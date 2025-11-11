#!/usr/bin/env python3

"""
Search for a computer by name in NinjaRMM
"""

import requests
import json
import sys
from typing import Optional, List, Dict, Any

# Configuration
CONFIG = {
    'client_id': 'FLFI6ANM2S7MG4AEOTA5',
    'client_secret': '47jn6gqcb6r402g48hmblcepcb642a5e553dempl',
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


def search_devices(devices: List[Dict[Any, Any]], search_term: str) -> List[Dict[Any, Any]]:
    """Search for devices by name"""
    results = []

    for device in devices:
        system_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')

        if search_term.lower() in system_name.lower():
            results.append(device)

    return results


def display_device_info(device: Dict[Any, Any], index: int = 1):
    """Display detailed device information"""
    print(f'[{index}] DEVICE FOUND')
    print('=' * 80)

    # Basic info
    system_name = device.get('systemName', 'N/A')
    dns_name = device.get('dnsName', 'N/A')
    device_id = device.get('id', 'N/A')
    node_class = device.get('nodeClass', 'N/A')
    online = device.get('online', False)
    last_contact = device.get('lastContact', 'N/A')

    # Organization
    org_id = device.get('organizationId', 'N/A')
    org_name = device.get('organizationName', 'N/A')

    # System
    os = device.get('os', {})
    os_name = os.get('name', 'N/A') if isinstance(os, dict) else 'N/A'

    # Network
    public_ip = device.get('publicIP', 'N/A')
    ip_addresses = device.get('ipAddresses', [])

    # Hardware
    system = device.get('system', {})
    manufacturer = system.get('manufacturer', 'N/A') if isinstance(system, dict) else 'N/A'
    model = system.get('model', 'N/A') if isinstance(system, dict) else 'N/A'

    print(f'System Name:      {system_name}')
    print(f'DNS Name:         {dns_name}')
    print(f'Device ID:        {device_id}')
    print(f'Node Class:       {node_class}')
    print(f'Status:           {"🟢 Online" if online else "🔴 Offline"}')
    print(f'Last Contact:     {last_contact}')
    print()
    print(f'Organization:     {org_name} (ID: {org_id})')
    print(f'Operating System: {os_name}')
    print()
    print(f'Public IP:        {public_ip}')
    if ip_addresses:
        print(f'IP Addresses:     {", ".join(ip_addresses)}')
    print()
    print(f'Manufacturer:     {manufacturer}')
    print(f'Model:            {model}')
    print('=' * 80)
    print()


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║           NinjaRMM Computer Search                             ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Get search term
    if len(sys.argv) < 2:
        search_term = input('Enter computer name to search: ')
    else:
        search_term = ' '.join(sys.argv[1:])

    print(f'Searching for: "{search_term}"\n')

    # Authenticate
    access_token = get_access_token()
    if not access_token:
        print('❌ Cannot proceed without authentication.')
        sys.exit(1)

    # Get all devices
    all_devices = get_all_devices(access_token)
    if not all_devices:
        print('❌ Cannot retrieve devices.')
        sys.exit(1)

    # Search for devices
    matching_devices = search_devices(all_devices, search_term)

    if not matching_devices:
        print(f'❌ No devices found matching "{search_term}"\n')
        print('Try searching with a different name or partial name.')
        sys.exit(1)

    print(f'✅ Found {len(matching_devices)} device(s) matching "{search_term}":\n')

    # Display all matching devices
    for idx, device in enumerate(matching_devices, 1):
        display_device_info(device, idx)

    # Summary of IDs
    print('SUMMARY - All Device IDs:')
    print('─' * 80)
    for idx, device in enumerate(matching_devices, 1):
        device_id = device.get('id', 'N/A')
        system_name = device.get('systemName', 'N/A')
        print(f'  [{idx}] ID: {device_id} - {system_name}')
    print()


if __name__ == '__main__':
    main()
