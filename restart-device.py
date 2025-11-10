#!/usr/bin/env python3

"""
Restart a device by name using NinjaRMM API
"""

import requests
import json
import sys
from typing import Optional, Dict, Any

# Configuration
CONFIG = {
    'client_id': 'H9E-VrYBPxfV1_zf17IExUgs_o4',
    'client_secret': 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
    'base_url': 'https://comda.rmmservice.eu',
    'token_endpoint': '/ws/oauth/token',
    'devices_endpoint': '/v2/devices'
}


def get_access_token() -> Optional[str]:
    """Get OAuth Access Token"""
    print('🔐 Authenticating with NinjaRMM...')

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
        response = requests.post(token_url, data=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                print('✅ Authentication successful!\n')
                return token_data['access_token']

        print(f'❌ Authentication failed: {response.status_code}')
        print(f'Response: {response.text}\n')
        return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}\n')
        return None


def find_device_by_name(access_token: str, search_name: str) -> Optional[Dict[Any, Any]]:
    """Find a device by name"""
    print(f'🔍 Searching for device: {search_name}...')

    devices_url = f'{CONFIG["base_url"]}{CONFIG["devices_endpoint"]}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(devices_url, headers=headers, timeout=30)

        if response.status_code == 200:
            devices = response.json()

            for device in devices:
                system_name = device.get('systemName', '').lower()
                dns_name = device.get('dnsName', '').lower()

                if search_name.lower() in system_name or search_name.lower() in dns_name:
                    print(f'✅ Found device: {device.get("systemName")} (ID: {device.get("id")})')
                    print(f'   DNS Name: {device.get("dnsName", "N/A")}')
                    print(f'   Status: {"🟢 Online" if not device.get("offline") else "🔴 Offline"}')
                    print()
                    return device

            print(f'❌ No device found with name containing "{search_name}"')
            return None
        else:
            print(f'❌ Failed to get devices: {response.status_code}')
            print(f'Response: {response.text}')
            return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}')
        return None


def restart_device(access_token: str, device_id: int, device_name: str) -> bool:
    """Send restart command to device"""
    print(f'🔄 Sending restart command to {device_name}...')

    # Try different possible restart endpoints
    restart_endpoints = [
        f'/v2/device/{device_id}/reboot',
        f'/v2/device/{device_id}/restart',
        f'/v2/device/{device_id}/actions/reboot',
        f'/v2/devices/{device_id}/reboot',
        f'/v2/devices/{device_id}/scripting/run/action/reboot',
    ]

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    for endpoint in restart_endpoints:
        url = f'{CONFIG["base_url"]}{endpoint}'
        print(f'   Trying: {endpoint}')

        try:
            # Try POST
            response = requests.post(url, headers=headers, json={}, timeout=30)

            if response.status_code in [200, 201, 202, 204]:
                print(f'✅ Restart command sent successfully!')
                print(f'   Status Code: {response.status_code}')
                if response.text:
                    print(f'   Response: {response.text}')
                return True
            elif response.status_code == 404:
                continue
            else:
                print(f'   ❌ Failed: {response.status_code}')
                print(f'   Response: {response.text[:200]}')

        except requests.exceptions.RequestException as e:
            print(f'   ❌ Error: {str(e)}')
            continue

    # If all endpoints failed, try scripting approach
    print('\n   Trying scripting/run endpoint...')
    script_url = f'{CONFIG["base_url"]}/v2/device/{device_id}/scripting/run'

    # Windows restart command
    script_payload = {
        "type": "ACTION",
        "actionId": "restart-device",
        "parameters": {}
    }

    try:
        response = requests.post(script_url, headers=headers, json=script_payload, timeout=30)

        if response.status_code in [200, 201, 202, 204]:
            print(f'✅ Restart command sent via scripting!')
            print(f'   Status Code: {response.status_code}')
            if response.text:
                print(f'   Response: {response.text}')
            return True
        else:
            print(f'   ❌ Failed: {response.status_code}')
            print(f'   Response: {response.text[:500]}')

    except requests.exceptions.RequestException as e:
        print(f'   ❌ Error: {str(e)}')

    print('\n❌ Could not find working restart endpoint.')
    print('   The device may need to be restarted manually or through the NinjaRMM web interface.')
    return False


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 restart-device.py <device_name>')
        print('Example: python3 restart-device.py it-grisha')
        sys.exit(1)

    device_name = sys.argv[1]

    print('╔════════════════════════════════════════════════════════════════╗')
    print('║          NinjaRMM Device Restart Tool                          ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Step 1: Authenticate
    access_token = get_access_token()
    if not access_token:
        print('❌ Cannot proceed without authentication.')
        sys.exit(1)

    # Step 2: Find device
    device = find_device_by_name(access_token, device_name)
    if not device:
        sys.exit(1)

    device_id = device.get('id')
    system_name = device.get('systemName')

    if device.get('offline'):
        print('⚠️  WARNING: Device is currently offline.')
        print('   Restart command may not be executed until device comes online.')
        print()

    # Step 3: Send restart command
    success = restart_device(access_token, device_id, system_name)

    if success:
        print('\n' + '=' * 70)
        print('✅ Restart command completed!')
        print('   The device should restart shortly.')
        print('=' * 70)
    else:
        print('\n' + '=' * 70)
        print('❌ Restart command failed.')
        print('   Please restart the device manually from the NinjaRMM web interface:')
        print(f'   https://comda.rmmservice.eu/app/devices/{device_id}')
        print('=' * 70)


if __name__ == '__main__':
    main()
