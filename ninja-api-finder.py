#!/usr/bin/env python3

"""
NinjaRMM API Region Finder

This script tests different NinjaRMM regional instances to find the correct one
for your credentials.
"""

import requests
import json

# Configuration
CLIENT_ID = 'FLFI6ANM2S7MG4AEOTA5'
CLIENT_SECRET = '47jn6gqcb6r402g48hmblcepcb642a5e553dempl'

# Different regional instances
REGIONS = [
    'https://app.ninjarmm.com',      # Global/US
    'https://us2.ninjarmm.com',      # US 2
    'https://eu.ninjarmm.com',       # Europe
    'https://ca.ninjarmm.com',       # Canada
    'https://oc.ninjarmm.com',       # Oceania
    'https://api.ninjarmm.com',      # Alternative API endpoint
]

def test_region(base_url):
    """Test authentication against a specific region"""
    print(f'Testing: {base_url}')

    token_url = f'{base_url}/ws/oauth/token'

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
        response = requests.post(
            token_url,
            data=payload,
            headers=headers,
            timeout=10
        )

        print(f'  Status: {response.status_code}')

        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                print(f'  ✅ SUCCESS! This is the correct region!')
                print(f'  Token Type: {token_data.get("token_type", "N/A")}')
                print(f'  Expires In: {token_data.get("expires_in", "N/A")} seconds')
                print(f'  Access Token: {token_data["access_token"][:30]}...')
                return base_url, token_data['access_token']
        else:
            try:
                error_data = response.json()
                print(f'  ❌ Failed: {error_data.get("resultCode", response.text)}')
            except:
                print(f'  ❌ Failed: {response.text[:100]}')

        print()
        return None, None

    except requests.exceptions.RequestException as e:
        print(f'  ❌ Connection error: {str(e)[:80]}')
        print()
        return None, None

def test_api_call(base_url, access_token):
    """Test an API call with the obtained token"""
    print(f'\n📡 Testing API call to: {base_url}/v2/organizations')

    api_url = f'{base_url}/v2/organizations'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print('✅ API call successful!')
            print('\nOrganizations Data:')
            print(json.dumps(data, indent=2))
        else:
            print(f'❌ API call failed with status {response.status_code}')
            print(f'Response: {response.text[:200]}')

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}')

def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║         NinjaRMM API Region Finder                             ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()
    print(f'Client ID: {CLIENT_ID}')
    print(f'Testing {len(REGIONS)} regional instances...\n')
    print('=' * 70 + '\n')

    for region in REGIONS:
        correct_region, access_token = test_region(region)

        if correct_region:
            print('\n' + '=' * 70)
            print(f'🎉 FOUND CORRECT REGION: {correct_region}')
            print('=' * 70 + '\n')

            # Test an API call
            test_api_call(correct_region, access_token)

            # Update configuration instructions
            print('\n' + '=' * 70)
            print('📝 Configuration:')
            print('=' * 70)
            print(f'\nUpdate your scripts to use:')
            print(f'  Base URL: {correct_region}')
            print(f'  Client ID: {CLIENT_ID}')
            print(f'  Client Secret: {CLIENT_SECRET}')
            return

    print('=' * 70)
    print('❌ Could not find the correct region for these credentials.')
    print('=' * 70)
    print('\nPossible reasons:')
    print('  1. The credentials are incorrect')
    print('  2. The client app has been deleted')
    print('  3. The region is not in the tested list')
    print('  4. Network connectivity issues')
    print('\nPlease verify your credentials in the NinjaRMM admin panel:')
    print('  Administration > Apps > API > Client App IDs')

if __name__ == '__main__':
    main()
