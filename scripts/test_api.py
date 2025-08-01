#!/usr/bin/env python3
"""
Test script for Cube.js API
Usage: python scripts/test_api.py '{"measures":["lineitem.count"]}'
       python scripts/test_api.py --staging '{"measures":["lineitem.count"]}'
"""

import sys
import json
import os
import requests
import argparse
from urllib.parse import urlencode
from dotenv import load_dotenv

def load_env_vars(use_staging=False):
    """Load environment variables from .env file"""
    load_dotenv()
    
    api_secret = os.getenv('API_SECRET')
    
    if use_staging:
        api_url = os.getenv('STAGING_ENV_API_URL')
        if not api_url:
            print("Error: STAGING_ENV_API_URL must be set in .env file for staging environment")
            sys.exit(1)
    else:
        api_url = os.getenv('API_URL')
        if not api_url:
            print("Error: API_URL must be set in .env file")
            sys.exit(1)
    
    if not api_secret:
        print("Error: API_SECRET must be set in .env file")
        sys.exit(1)
    
    return api_secret, api_url

def create_auth_token(api_secret):
    """Create JWT token for API authentication"""
    import jwt
    import time
    
    payload = {
        'iat': int(time.time())
    }
    return jwt.encode(payload, api_secret, algorithm='HS256')

def test_cube_api(query_json, api_secret, api_url, use_staging=False):
    """Test the Cube API with the given query"""
    try:
        # Parse the query JSON
        query = json.loads(query_json)
        
        # Create auth token
        token = create_auth_token(api_secret)
        
        # Prepare the request
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        # Make the API request
        params = {'query': json.dumps(query)}
        url = f"{api_url.rstrip('/')}/load"
        
        env_label = "STAGING" if use_staging else "PRODUCTION"
        print(f"Environment: {env_label}")
        print(f"Making request to: {url}")
        print(f"Query: {json.dumps(query, indent=2)}")
        print("-" * 50)
        
        response = requests.get(url, headers=headers, params=params)
        
        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON query: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Test Cube.js API with custom queries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_api.py '{"measures":["lineitem.count"]}'
  python scripts/test_api.py --staging '{"measures":["lineitem.count"]}'
  python scripts/test_api.py '{"measures":["lineitem.supplier_sales_contribution"],"dimensions":["supplier.supplier_name"],"limit":5}'
  python scripts/test_api.py --staging '{"measures":["partsupp.total_supply_cost","partsupp.total_inventory_value"],"dimensions":["part.part_type"],"limit":10}'
        """
    )
    
    parser.add_argument('query', help='JSON query string for the Cube API')
    parser.add_argument('--staging', action='store_true', help='Use staging environment API URL')
    
    args = parser.parse_args()
    
    api_secret, api_url = load_env_vars(use_staging=args.staging)
    test_cube_api(args.query, api_secret, api_url, use_staging=args.staging)

if __name__ == "__main__":
    main()