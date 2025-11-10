#!/usr/bin/env python3

"""
Get all machines with 'guy' in their name from NinjaRMM
"""

import requests
import json
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
    print('📡 Fetching all devices from NinjaRMM...')

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


def filter_devices_by_name(devices: List[Dict[Any, Any]], search_term: str) -> List[Dict[Any, Any]]:
    """Filter devices that contain the search term in their name"""
    filtered = []

    for device in devices:
        # Check various name fields that might exist
        device_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')

        if search_term.lower() in device_name.lower():
            filtered.append(device)

    return filtered


def generate_report(devices: List[Dict[Any, Any]], search_term: str):
    """Generate a formatted report of matching machines"""
    print('=' * 80)
    print(f'  MACHINES CONTAINING "{search_term.upper()}" IN NAME')
    print('=' * 80)
    print()

    if not devices:
        print(f'❌ No machines found with "{search_term}" in their name.')
        print()
        return

    print(f'✅ Found {len(devices)} machine(s):\n')

    for idx, device in enumerate(devices, 1):
        print(f'[{idx}] DEVICE INFORMATION')
        print('-' * 60)

        # Extract common fields
        system_name = device.get('systemName', 'N/A')
        dns_name = device.get('dnsName', 'N/A')
        device_id = device.get('id', 'N/A')
        node_class = device.get('nodeClass', 'N/A')
        online = device.get('online', False)
        last_contact = device.get('lastContact', 'N/A')

        # Organization info
        org_id = device.get('organizationId', 'N/A')
        org_name = device.get('organizationName', 'N/A')

        # System info
        os = device.get('os', {})
        os_name = os.get('name', 'N/A') if isinstance(os, dict) else 'N/A'

        # IP addresses
        public_ip = device.get('publicIP', 'N/A')
        ip_addresses = device.get('ipAddresses', [])

        print(f'  System Name:    {system_name}')
        print(f'  DNS Name:       {dns_name}')
        print(f'  Device ID:      {device_id}')
        print(f'  Node Class:     {node_class}')
        print(f'  Status:         {"🟢 Online" if online else "🔴 Offline"}')
        print(f'  Last Contact:   {last_contact}')
        print(f'  Organization:   {org_name} (ID: {org_id})')
        print(f'  Operating System: {os_name}')
        print(f'  Public IP:      {public_ip}')

        if ip_addresses:
            print(f'  IP Addresses:   {", ".join(ip_addresses)}')

        print()

    # Summary table
    print('=' * 80)
    print('SUMMARY TABLE')
    print('=' * 80)
    print()
    print(f'{"#":<5} {"System Name":<30} {"Status":<10} {"OS":<20}')
    print('-' * 80)

    for idx, device in enumerate(devices, 1):
        system_name = device.get('systemName', 'N/A')[:28]
        online = device.get('online', False)
        status = "Online" if online else "Offline"
        os = device.get('os', {})
        os_name = (os.get('name', 'N/A') if isinstance(os, dict) else 'N/A')[:18]

        print(f'{idx:<5} {system_name:<30} {status:<10} {os_name:<20}')

    print()
    print('=' * 80)

    # Export to JSON
    output_file = 'guy_machines_report.json'
    with open(output_file, 'w') as f:
        json.dump(devices, f, indent=2)

    print(f'📄 Full details exported to: {output_file}')
    print()


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║     NinjaRMM Machine Report - Filter by "guy"                  ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Step 1: Authenticate
    access_token = get_access_token()
    if not access_token:
        print('❌ Cannot proceed without authentication.')
        return

    # Step 2: Get all devices
    all_devices = get_all_devices(access_token)
    if not all_devices:
        print('❌ Cannot retrieve devices.')
        return

    # Step 3: Filter devices containing "guy"
    search_term = 'guy'
    matching_devices = filter_devices_by_name(all_devices, search_term)

    # Step 4: Generate report
    generate_report(matching_devices, search_term)


if __name__ == '__main__':
    main()
