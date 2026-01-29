#!/usr/bin/env python3

"""
Restart a computer via NinjaRMM API

This script:
1. Authenticates with NinjaRMM
2. Finds the device by name
3. Sends a reboot command

Usage: python3 restart-computer.py <computer-name>
"""

import requests
import json
import sys
from typing import Optional, List, Dict, Any

# Configuration
CONFIG = {
    'client_id': 'J0CpD5xrF5WKV2qo50lxNbkUZ5k',
    'client_secret': 'VOwtkv-xVvO5HoZcIbncQxI-QIU4-OVC27DTFTHnZfJEGojG38lrbg',
    'base_url': 'https://comda.rmmservice.eu',
    'token_endpoint': '/ws/oauth/token',
    'devices_endpoint': '/v2/devices',
    'reboot_endpoint': '/v2/device/{device_id}/reboot'
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


def get_all_devices(access_token: str) -> Optional[List[Dict[Any, Any]]]:
    """Get all devices from NinjaRMM"""
    print('📡 Fetching devices from NinjaRMM...')

    devices_url = f'{CONFIG["base_url"]}{CONFIG["devices_endpoint"]}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(devices_url, headers=headers, timeout=30)

        if response.status_code == 200:
            devices = response.json()
            print(f'✅ Retrieved {len(devices)} devices\n')
            return devices
        else:
            print(f'❌ Failed to get devices: {response.status_code}')
            print(f'Response: {response.text}\n')
            return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}\n')
        return None


def find_device_by_name(devices: List[Dict[Any, Any]], name: str) -> Optional[Dict[Any, Any]]:
    """Find a device by exact or partial name match"""
    print(f'🔍 Searching for device: {name}')

    # Try exact match first
    for device in devices:
        system_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')
        if system_name.upper() == name.upper():
            print(f'✅ Found exact match: {system_name}\n')
            return device

    # Try partial match
    for device in devices:
        system_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')
        if name.upper() in system_name.upper():
            print(f'✅ Found partial match: {system_name}\n')
            return device

    print(f'❌ Device not found: {name}\n')
    return None


def reboot_device(access_token: str, device_id: int, device_name: str) -> bool:
    """Send reboot command to a device"""
    print(f'🔄 Sending reboot command to: {device_name} (ID: {device_id})')

    reboot_url = f'{CONFIG["base_url"]}{CONFIG["reboot_endpoint"]}'.format(device_id=device_id)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Try POST method first (most common for actions)
    try:
        response = requests.post(reboot_url, headers=headers, json={}, timeout=30)

        if response.status_code in [200, 201, 202, 204]:
            print(f'✅ Reboot command sent successfully!')
            print(f'   Status Code: {response.status_code}')
            if response.text:
                print(f'   Response: {response.text}')
            print()
            return True
        elif response.status_code == 404:
            # Try alternative endpoint format
            print('⚠️  Primary endpoint returned 404, trying alternative method...')
            return reboot_device_alternative(access_token, device_id, device_name)
        else:
            print(f'❌ Reboot failed: {response.status_code}')
            print(f'   Response: {response.text}\n')
            return False

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}\n')
        return False


def reboot_device_alternative(access_token: str, device_id: int, device_name: str) -> bool:
    """Try alternative reboot endpoint"""
    # Alternative endpoints to try
    alternative_endpoints = [
        f'/v2/device/{device_id}/action/reboot',
        f'/v2/device/{device_id}/actions/reboot',
        f'/v2/devices/{device_id}/reboot',
        f'/v2/devices/{device_id}/action/reboot'
    ]

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    for endpoint in alternative_endpoints:
        print(f'   Trying: {endpoint}')
        url = f'{CONFIG["base_url"]}{endpoint}'

        try:
            response = requests.post(url, headers=headers, json={}, timeout=30)

            if response.status_code in [200, 201, 202, 204]:
                print(f'✅ Reboot command sent successfully!')
                print(f'   Endpoint: {endpoint}')
                print(f'   Status Code: {response.status_code}')
                if response.text:
                    print(f'   Response: {response.text}')
                print()
                return True

        except requests.exceptions.RequestException:
            continue

    print(f'❌ All reboot endpoints failed for device {device_name}\n')
    return False


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║           NinjaRMM Computer Restart Script                     ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Get computer name from command line argument
    if len(sys.argv) < 2:
        print('❌ Usage: python3 restart-computer.py <computer-name>')
        print('   Example: python3 restart-computer.py IT-GREGORYR')
        sys.exit(1)

    computer_name = sys.argv[1]
    print(f'Target Computer: {computer_name}\n')

    # Step 1: Authenticate
    access_token = get_access_token()
    if not access_token:
        print('❌ Cannot proceed without authentication.')
        sys.exit(1)

    # Step 2: Get all devices
    all_devices = get_all_devices(access_token)
    if not all_devices:
        print('❌ Cannot retrieve devices.')
        sys.exit(1)

    # Step 3: Find the target device
    target_device = find_device_by_name(all_devices, computer_name)
    if not target_device:
        print(f'❌ Device "{computer_name}" not found.')
        print('\nAvailable devices:')
        for device in all_devices[:10]:  # Show first 10
            name = device.get('systemName', 'N/A')
            print(f'   - {name}')
        sys.exit(1)

    # Display device info
    device_id = target_device.get('id')
    system_name = target_device.get('systemName', 'N/A')
    online = target_device.get('online', False)
    status = "🟢 Online" if online else "🔴 Offline"

    print('─' * 60)
    print('TARGET DEVICE INFORMATION')
    print('─' * 60)
    print(f'  System Name: {system_name}')
    print(f'  Device ID:   {device_id}')
    print(f'  Status:      {status}')
    print('─' * 60)
    print()

    # Step 4: Reboot the device
    success = reboot_device(access_token, device_id, system_name)

    if success:
        print('✅ SUCCESS: Reboot command completed successfully!')
        sys.exit(0)
    else:
        print('❌ FAILED: Could not send reboot command.')
        sys.exit(1)


if __name__ == '__main__':
    main()
