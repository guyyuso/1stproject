#!/usr/bin/env python3

"""
NinjaRMM API Test Script for comda.rmmservice.eu
"""

import requests
import json

# Configuration for your specific instance
CLIENT_ID = 'H9E-VrYBPxfV1_zf17IExUgs_o4'
CLIENT_SECRET = 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg'
BASE_URL = 'https://comda.rmmservice.eu'

def get_access_token():
    """Get OAuth Access Token"""
    print('🔐 Requesting OAuth Access Token...')
    print(f'   Client ID: {CLIENT_ID}')
    print(f'   Base URL: {BASE_URL}')
    print(f'   Token URL: {BASE_URL}/ws/oauth/token\n')

    token_url = f'{BASE_URL}/ws/oauth/token'

    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'monitoring management'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(token_url, data=payload, headers=headers, timeout=30)

        print(f'Response Status: {response.status_code}')

        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                print('✅ Successfully obtained access token!')
                print(f'   Token Type: {token_data.get("token_type", "N/A")}')
                print(f'   Expires In: {token_data.get("expires_in", "N/A")} seconds')
                print(f'   Access Token: {token_data["access_token"][:30]}...')
                print()
                return token_data['access_token']

        print('❌ Failed to obtain access token')
        print(f'   Response: {response.text}')
        return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}')
        return None

def call_api(access_token, endpoint, name):
    """Call API endpoint"""
    print(f'📡 Calling: {name}')
    print(f'   URL: {BASE_URL}{endpoint}')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(f'{BASE_URL}{endpoint}', headers=headers, timeout=30)
        print(f'   Status: {response.status_code}\n')

        if response.status_code == 200:
            data = response.json()
            print(f'✅ {name} - Success!')
            print(json.dumps(data, indent=2))
            print('\n' + '=' * 80 + '\n')
            return data
        else:
            print(f'❌ Failed: {response.text}\n')
            return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}\n')
        return None

def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║      NinjaRMM API Test - comda.rmmservice.eu                   ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Get access token
    access_token = get_access_token()

    if not access_token:
        print('❌ Could not authenticate. Exiting.')
        return

    # Test various endpoints
    endpoints = [
        ('/v2/organizations', 'Organizations'),
        ('/v2/devices', 'Devices'),
        ('/v2/device-roles', 'Device Roles'),
        ('/v2/activities', 'Activities'),
    ]

    for endpoint, name in endpoints:
        call_api(access_token, endpoint, name)

    print('✅ Testing complete!')

if __name__ == '__main__':
    main()
