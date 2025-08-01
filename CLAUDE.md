# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Cube.js Python API project implementing a TPC-H SF100 data model. It defines OLAP cubes and views for analytical queries on the TPC-H benchmark dataset using Snowflake as the data source.

## Architecture

The project follows Cube.js Python API conventions:

- **`cube.py`**: Main configuration file with Python decorators for query rewriting and security context
- **`model/cubes/`**: YAML cube definitions for TPC-H entities (customer, lineitem, nation, orders, part, partsupp, region, supplier)
- **`model/views/`**: Analytical views that combine multiple cubes via join paths
- **`scripts/`**: Utility scripts for data loading and testing the Cube API. (All scripts use the env variables defined in `.env` and support staging environment parameters)

### Datasource Data Model Structure

Read `docs/DATA_MODEL.md` for detailed database data model structure and relationships. Don't update this file for data model changes, update `docs/DATA_MODEL.md` instead.

### Datasource Data Model Structure

Read `docs/META_CURRENT.md` for detailed cube data model structure and relationships. Don't update this file for cube data model changes, run `python scripts/fetch_meta.py` to regenerate this file after the user has pushed the changes to Cube Cloud.

## Development Commands

This project uses Python and Cube Cloud, so no commands can be run locally.
We can only use REST API to interact with the Cube.js server.

### Running Scripts

All scripts in the `scripts/` directory support both production and staging environment parameters:
- **Production**: Scripts use environment variables from `.env` by default
- **Staging**: Add `--staging` flag to use staging environment variables (e.g., `python scripts/fetch_meta.py --staging`)

Example REST API call to fetch data from the Cube.js server:

```bash
curl \
  -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTM5OTcwMTN9.-sm1MpPrJDqkxLEYf1LOhMS44O3Ik6pzJgNQMa8VY08" \
  -G \
  --data-urlencode 'query={"measures":["customer.count"]}' \
  https://coral-silkworm.aws-us-east-1.cubecloudapp.dev/cubejs-api/v1/load
```

## API Reference

Read `docs/REST_API_REFERENCE.md` for detailed API endpoints and usage examples ONLY WHEN NECESSARY.

## Development Workflow
- Cube Cloud has staging envirionments, before testing a change you need to commit and push your changes to the branch defined in the `.env` file as `STAGING_ENV_BRANCH`. The branch should be created in the Cube Cloud UI. 
- NEVER create a branch or commit in the master or main branch, always use the `STAGING_ENV_BRANCH` defined in the `.env` file.
- ALWAYS check which branch you are working on before making changes. You can use the `git branch` command to see the current branch.
- When you are in the staging environment branch, the URL for the CUBE API will be defined in the env variable `STAGING_ENV_API_URL`. Use this URL to make API calls.


## Notes
- Empty requirements.txt suggests dependencies are managed elsewhere or project is minimal
- No tests directory found - testing approach unclear
- Git repository includes .cubestore, node_modules, and .env in .gitignore
- DO NOT modify the `.env` file directly; use `.env-example` as a template for environment variables
- when creating or adding members to views, there can be only one measure called count. Actually all measures and names should be unique in a views. You can use the `prefix: true` option to avoid conflicts.