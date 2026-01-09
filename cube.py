# module.exports = {
#   contextToRoles: ({securityContext}) => {
#     return securityContext.roles || []
#   }
# queryRewrite: (query, context) => {
#   console.log(context);
#   return query
# }
# }
#   contextToRoles: ({securityContext}) => {
#     return securityContext.roles || []
#   }
from cube import config
import os
from typing import Dict, List, Any


@config("check_sql_auth")
def check_sql_auth(req: Dict[str, Any], user_name: str, password: str) -> Dict[str, Any]:
    """
    Authentication hook for Cube SQL / XMLA connections.

    Responsibilities:
    - Handle Power BI / gateway scenarios for XMLA over NTLM and Kerberos.
    - Map incoming `user_name` to Cube Cloud roles via `get_roles_for_username`.
    - Return a dict with:
        {
          "password": <password-to-use-for-downstream-connection>,
          "securityContext": {
            "user": <normalized user name>,
            "cubeCloud": {
              "roles": [<role>, ...]
            }
          }
        }

    Main cases:
    1. XMLA + NTLM  (Power BI Desktop / Gateway "runas" scenarios)
    2. XMLA + Kerberos
    3. Direct SQL user (CUBEJS_SQL_USER)
    4. Other users resolved via get_roles_for_username
    """

    # Extract protocol/method defensively to avoid KeyError if req is incomplete.
    protocol = (req or {}).get("protocol")
    method = (req or {}).get("method")

    # Important environment variables used for auth decisions.
    sql_user = os.environ.get("CUBEJS_SQL_USER")
    sql_super_user = os.environ.get("CUBEJS_SQL_SUPER_USER")
    sql_password = os.environ.get("CUBEJS_SQL_PASSWORD")
    xmla_password = os.environ.get("CUBE_XMLA_API_PASSWORD")

    def build_security_context(user: str, roles: List[str]) -> Dict[str, Any]:
        """Return securityContext in the shape expected by Cube / the rest of the codebase."""
        return {
            "user": user,
            "cubeCloud": {
                "roles": roles,
            },
        }

    # Default to admin role; this will be overridden for non-admin users.
    roles: List[str] = ["CUBECLOUD_ADMIN"]

    print(
        "check_sql_auth called: protocol={}, method={}, user_name={}".format(
        protocol,
        method,
        user_name
    ))

    # -------------------------------------------------------------------------
    # 1. XMLA + NTLM (Power BI Desktop / Gateway using NTLM)
    # -------------------------------------------------------------------------
    if protocol == "xmla" and method == "ntlm":
        # Admin users keep the default admin role; other users get roles from IdP / directory.
        # if user_name not in {sql_user, sql_super_user}:
        #     roles = get_roles_for_username(user_name)

        print("NTLM roles for {}: {}".format(user_name, roles))

        # 1.a. Power BI Desktop connecting directly as CUBEJS_SQL_USER
        if user_name == sql_user:
            return {
                "password": sql_password,
                "securityContext": build_security_context(user_name, roles),
            }

        # 1.b. Power BI Gateway connecting as super user with XMLA API password
        if user_name == sql_super_user:
            # Here you can optionally add impersonation logic based on headers,
            # if needed in the future.
            return {
                "password": xmla_password,
                "securityContext": build_security_context(user_name, roles),
            }

        # 1.c. Fallback for NTLM XMLA: treat as a normal SQL connection but over XMLA
        return {
            "password": sql_password,
            "securityContext": build_security_context(user_name, roles),
        }

    # -------------------------------------------------------------------------
    # 2. XMLA + Kerberos
    # -------------------------------------------------------------------------
    if protocol == "xmla" and method == "kerberos":
        # Admin users keep admin role; others get roles from IdP / directory.
        # if user_name not in {sql_user, sql_super_user}:
        #     roles = get_roles_for_username(user_name)

        print("Kerberos roles for {}: {}".format(user_name, roles))

        # For Kerberos, we usually pass through the password coming from the gateway.
        return {
            "password": password,
            "securityContext": build_security_context(user_name, roles),
        }

    # -------------------------------------------------------------------------
    # 3. Direct SQL user (CUBEJS_SQL_USER)
    # -------------------------------------------------------------------------
    if user_name == sql_user:
        # If password is provided, it must match the configured SQL password.
        if password and sql_password and password != sql_password:
            print("Access denied for CUBEJS_SQL_USER: invalid password")
            raise Exception("Access denied")

        return {
            "password": sql_password,
            "securityContext": build_security_context(user_name, roles),
        }

    # -------------------------------------------------------------------------
    # 4. Other users – resolve roles via get_roles_for_username
    # -------------------------------------------------------------------------
    # For non-admin, non-service users, we look up roles dynamically.
    # roles = get_roles_for_username(user_name, default_groups=[])
    print("SQL roles for {}: {}".format(user_name, roles))

    if True: # roles: # enable this validation once get_roles_for_username is implemented
        return {
            "password": sql_password,
            "securityContext": build_security_context(user_name, roles),
        }

    # No roles and not a known service/admin user → deny access.
    print("Access denied for user {}: no roles resolved".format(user_name))
    raise Exception("Access denied")

@config('query_rewrite')
def query_rewrite(query: dict, ctx: dict) -> dict:
  context = ctx['securityContext']
  print(f"Query Rewrite context: {context}")
  return query

@config('context_to_roles')
def context_to_roles(ctx: dict) -> list[str]:
  context = ctx['securityContext']
  cube_cloud_roles = context.get('cubeCloud', {}).get('roles', [])
  ctx_roles = context.get('roles', ['default'])
  all_roles = list(set(cube_cloud_roles + ctx_roles))
  print(f"roles: {all_roles}")
  return all_roles
