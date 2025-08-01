#!/usr/bin/env python3
"""
Fetch metadata from Cube Cloud deployment and write to docs/META_CURRENT.md or docs/META_STAGING.md
Usage: python scripts/fetch_meta.py [--staging]
"""

import os
import jwt
import requests
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


def load_env_vars(use_staging: bool = False) -> Dict[str, str]:
    """Load environment variables from .env file if it exists"""
    env_vars = {}
    env_file = Path('.env')
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Override with actual environment variables
    api_url_key = 'STAGING_ENV_API_URL' if use_staging else 'API_URL'
    for key in ['API_SECRET', api_url_key]:
        if key in os.environ:
            env_vars[key] = os.environ[key]
    
    return env_vars


def generate_jwt_token(api_secret: str) -> str:
    """Generate JWT token using the API secret"""
    payload = {
        'iat': int(datetime.now(timezone.utc).timestamp())
    }
    
    token = jwt.encode(payload, api_secret, algorithm='HS256')
    return token


def fetch_metadata(api_url: str, token: str, extended: bool = True) -> Dict[str, Any]:
    """Fetch metadata from Cube Cloud /meta endpoint"""
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    # Ensure URL ends with /meta, add extended parameter if requested
    base_url = api_url.rstrip('/')
    meta_url = f"{base_url}/meta{'?extended' if extended else ''}"
    
    response = requests.get(meta_url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def format_metadata_as_markdown(metadata: Dict[str, Any], use_staging: bool = False) -> str:
    """Format metadata as markdown for documentation"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Extract cubes from metadata
    cubes = metadata.get('cubes', [])
    
    # Separate cubes and views
    cube_entities = [c for c in cubes if c.get('type') == 'cube']
    view_entities = [c for c in cubes if c.get('type') == 'view']
    
    env_label = "Staging" if use_staging else "Current"
    md_content = f"""# {env_label} Data Model Metadata

Generated on: {timestamp}
Environment: {'STAGING' if use_staging else 'PRODUCTION'}

## Overview

- **Total Entities**: {len(cubes)}
- **Cubes**: {len(cube_entities)}  
- **Views**: {len(view_entities)}

## Data Model Relationships

"""
    
    # Build relationship map
    relationship_map = {}
    for cube in cube_entities:
        cube_name = cube.get('name', 'Unknown')
        joins = cube.get('joins', [])
        if joins:
            relationship_map[cube_name] = []
            for join in joins:
                target = join.get('name', 'Unknown')
                relationship = join.get('relationship', 'Unknown')
                sql = join.get('sql', '')
                relationship_map[cube_name].append({
                    'target': target,
                    'relationship': relationship,
                    'sql': sql
                })
    
    # Display relationships
    if relationship_map:
        for cube_name, relationships in relationship_map.items():
            md_content += f"- **{cube_name}**:\n"
            for rel in relationships:
                rel_type = rel['relationship'].replace('belongsTo', 'many-to-one')
                md_content += f"  - {rel_type} → `{rel['target']}`\n"
        md_content += "\n"
    else:
        md_content += "No relationships found.\n\n"
    
    md_content += "## Cubes\n\n"
    
    for cube in cube_entities:
        cube_name = cube.get('name', 'Unknown')
        cube_title = cube.get('title', cube_name)
        file_name = cube.get('fileName', 'Unknown')
        
        md_content += f"### {cube_title} (`{cube_name}`)\n"
        md_content += f"*Source: {file_name}*\n\n"
        
        # Dimensions
        dimensions = cube.get('dimensions', [])
        key_dimensions = [d for d in dimensions if d.get('primaryKey', False)]
        regular_dimensions = [d for d in dimensions if not d.get('primaryKey', False)]
        
        if key_dimensions:
            md_content += "**Primary Keys:**\n"
            for dim in key_dimensions:
                dim_name = dim.get('shortTitle', dim.get('name', 'Unknown'))
                dim_type = dim.get('type', 'Unknown')
                md_content += f"- `{dim_name}` ({dim_type})\n"
            md_content += "\n"
        
        if regular_dimensions:
            md_content += "**Dimensions:**\n"
            for dim in regular_dimensions:
                dim_name = dim.get('shortTitle', dim.get('name', 'Unknown'))
                dim_type = dim.get('type', 'Unknown')
                md_content += f"- `{dim_name}` ({dim_type})\n"
            md_content += "\n"
        
        # Measures
        measures = cube.get('measures', [])
        if measures:
            md_content += "**Measures:**\n"
            for measure in measures:
                measure_name = measure.get('shortTitle', measure.get('name', 'Unknown'))
                agg_type = measure.get('aggType', measure.get('type', 'Unknown'))
                md_content += f"- `{measure_name}` ({agg_type})\n"
            md_content += "\n"
        
        # Joins
        joins = cube.get('joins', [])
        if joins:
            md_content += "**Joins:**\n"
            for join in joins:
                target = join.get('name', 'Unknown')
                relationship = join.get('relationship', 'Unknown').replace('belongsTo', 'many-to-one')  
                md_content += f"- {relationship} → `{target}`\n"
            md_content += "\n"
        
        # Pre-aggregations
        pre_aggs = cube.get('preAggregations', [])
        if pre_aggs:
            md_content += f"**Pre-aggregations:** {len(pre_aggs)} defined\n\n"
        
        md_content += "---\n\n"
    
    # Views section
    if view_entities:
        md_content += "## Views\n\n"
        
        for view in view_entities:
            view_name = view.get('name', 'Unknown')
            view_title = view.get('title', view_name)
            
            md_content += f"### {view_title} (`{view_name}`)\n"
            md_content += f"*Type: View*\n\n"
            
            # Measures
            measures = view.get('measures', [])
            if measures:
                md_content += "**Available Measures:**\n"
                for measure in measures:
                    measure_name = measure.get('shortTitle', measure.get('name', 'Unknown'))
                    agg_type = measure.get('aggType', measure.get('type', 'Unknown'))
                    md_content += f"- `{measure_name}` ({agg_type})\n"
                md_content += "\n"
            
            # Dimensions
            dimensions = view.get('dimensions', [])
            if dimensions:
                md_content += "**Available Dimensions:**\n"
                for dim in dimensions:
                    dim_name = dim.get('shortTitle', dim.get('name', 'Unknown'))
                    dim_type = dim.get('type', 'Unknown')
                    md_content += f"- `{dim_name}` ({dim_type})\n"
                md_content += "\n"
            
            md_content += "---\n\n"
    
    return md_content


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Fetch metadata from Cube Cloud deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/fetch_meta.py                # Fetch production metadata to META_CURRENT.md
  python scripts/fetch_meta.py --staging     # Fetch staging metadata to META_STAGING.md
        """
    )
    
    parser.add_argument('--staging', action='store_true', help='Use staging environment API URL and output to META_STAGING.md')
    
    args = parser.parse_args()
    
    try:
        # Load environment variables
        env_vars = load_env_vars(use_staging=args.staging)
        
        api_secret = env_vars.get('API_SECRET')
        
        if args.staging:
            api_url = env_vars.get('STAGING_ENV_API_URL')
            if not api_url:
                raise ValueError("STAGING_ENV_API_URL not found in environment variables or .env file")
            output_file = Path('docs/META_STAGING.md')
            env_label = "STAGING"
        else:
            api_url = env_vars.get('API_URL')
            if not api_url:
                raise ValueError("API_URL not found in environment variables or .env file")
            output_file = Path('docs/META_CURRENT.md')
            env_label = "PRODUCTION"
        
        if not api_secret:
            raise ValueError("API_SECRET not found in environment variables or .env file")
        
        print(f"Environment: {env_label}")
        print(f"Using API URL: {api_url}")
        print(f"Output file: {output_file}")
        
        # Generate JWT token
        print("Generating JWT token...")
        token = generate_jwt_token(api_secret)
        print(f"Token generated: {token[:20]}...")
        
        # Fetch metadata
        print("Fetching metadata from /meta endpoint...")
        metadata = fetch_metadata(api_url, token)
        print(f"Metadata fetched successfully. Found {len(metadata.get('cubes', []))} cubes.")
        
        # Format as markdown
        print("Formatting metadata as markdown...")
        markdown_content = format_metadata_as_markdown(metadata, use_staging=args.staging)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(markdown_content)
        
        print(f"Metadata written to {output_file}")
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())