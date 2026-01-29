#!/usr/bin/env python3

"""
NinjaRMM API Integration Script

This script demonstrates how to:
1. Authenticate with NinjaRMM using OAuth 2.0 Client Credentials
2. Make API calls to retrieve organization and device data

Usage: python3 ninja-api.py
"""

import requests
import json
from typing import Optional, Dict, Any

# Configuration
CONFIG = {
    'client_id': 'J0CpD5xrF5WKV2qo50lxNbkUZ5k',
    'client_secret': 'VOwtkv-xVvO5HoZcIbncQxI-QIU4-OVC27DTFTHnZfJEGojG38lrbg',
    'base_url': 'https://comda.rmmservice.eu',
    'token_endpoint': '/ws/oauth/token',
    'api_endpoints': {
        'organizations': '/v2/organizations',
        'devices': '/v2/devices',
        'device_roles': '/v2/device-roles',
        'activities': '/v2/activities',
        'queries': '/v2/queries'
    }
}


def get_access_token() -> Optional[str]:
    """
    Get OAuth Access Token using Client Credentials flow

    Returns:
        Access token string or None if authentication fails
    """
    print('🔐 Requesting OAuth Access Token...')
    print(f'   Client ID: {CONFIG["client_id"]}')
    print(f'   Token URL: {CONFIG["base_url"]}{CONFIG["token_endpoint"]}\n')

    token_url = f'{CONFIG["base_url"]}{CONFIG["token_endpoint"]}'

    payload = {
        'grant_type': 'client_credentials',
        'client_id': CONFIG['client_id'],
        'client_secret': CONFIG['client_secret'],
        'scope': 'monitoring management'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(
            token_url,
            data=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                print('✅ Successfully obtained access token!')
                print(f'   Token Type: {token_data.get("token_type", "N/A")}')
                print(f'   Expires In: {token_data.get("expires_in", "N/A")} seconds')
                print(f'   Access Token: {token_data["access_token"][:20]}...')
                print()
                return token_data['access_token']

        print('❌ Failed to obtain access token')
        print(f'   Status Code: {response.status_code}')
        print(f'   Response: {response.text}')
        return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error during authentication: {str(e)}')
        return None


def call_api_endpoint(
    access_token: str,
    endpoint: str,
    endpoint_name: str
) -> Optional[Dict[Any, Any]]:
    """
    Call a NinjaRMM API endpoint

    Args:
        access_token: OAuth access token
        endpoint: API endpoint path
        endpoint_name: Human-readable name for logging

    Returns:
        JSON response data or None if request fails
    """
    print(f'📡 Calling API: {endpoint_name}')
    print(f'   Endpoint: {CONFIG["base_url"]}{endpoint}\n')

    api_url = f'{CONFIG["base_url"]}{endpoint}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            api_url,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            print(f'✅ {endpoint_name} - Success!')
            print(f'   Status: {response.status_code}')
            print('   Response:\n')
            data = response.json()
            print(json.dumps(data, indent=2))
            print('\n' + '=' * 80 + '\n')
            return data
        else:
            print(f'❌ {endpoint_name} - Failed')
            print(f'   Status Code: {response.status_code}')
            print(f'   Response: {response.text}')
            print()
            return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error calling {endpoint_name}: {str(e)}')
        return None


def main():
    """Main execution function"""
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║           NinjaRMM API Integration Script                      ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    try:
        # Step 1: Get Access Token
        access_token = get_access_token()

        if not access_token:
            print('\n❌ Failed to obtain access token. Exiting.')
            return

        # Step 2: Call API Endpoints
        call_api_endpoint(
            access_token,
            CONFIG['api_endpoints']['organizations'],
            'Get Organizations'
        )

        call_api_endpoint(
            access_token,
            CONFIG['api_endpoints']['devices'],
            'Get Devices'
        )

        call_api_endpoint(
            access_token,
            CONFIG['api_endpoints']['device_roles'],
            'Get Device Roles'
        )

        print('✅ All API calls completed successfully!')

    except Exception as e:
        print(f'\n❌ Script execution failed: {str(e)}')
        exit(1)


if __name__ == '__main__':
    main()
