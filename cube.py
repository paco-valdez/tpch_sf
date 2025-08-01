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
 

@config('query_rewrite')
def query_rewrite(query: dict, ctx: dict) -> dict:
  context = ctx['securityContext']
  print(context)
  return query

@config('context_to_roles')
def context_to_roles(ctx: dict) -> list[str]:
  return ctx['securityContext'].get('roles', ['default'])
