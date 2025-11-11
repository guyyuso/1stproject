#!/usr/bin/env python3

"""
Find all machines with 'zeev' in their name from NinjaRMM
"""

import requests
import json
from typing import Optional, List, Dict, Any

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
        device_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')

        if search_term.lower() in device_name.lower():
            filtered.append(device)

    return filtered


def generate_report(devices: List[Dict[Any, Any]], search_term: str):
    """Generate a formatted report of matching machines"""
    print('=' * 100)
    print(f'  MACHINES CONTAINING "{search_term.upper()}" IN NAME')
    print('=' * 100)
    print()

    if not devices:
        print(f'❌ No machines found with "{search_term}" in their name.')
        print()
        return

    print(f'✅ Found {len(devices)} machine(s):\n')

    # Summary table
    print(f'{"#":<5} {"System Name":<35} {"Status":<10} {"DNS Name":<40}')
    print('-' * 100)

    for idx, device in enumerate(devices, 1):
        system_name = device.get('systemName', 'N/A')[:33]
        online = not device.get('offline', True)
        status = "🟢 Online" if online else "🔴 Offline"
        dns_name = device.get('dnsName', 'N/A')[:38]

        print(f'{idx:<5} {system_name:<35} {status:<10} {dns_name:<40}')

    print()
    print('=' * 100)
    print(f'\nTotal: {len(devices)} machines')
    print('=' * 100)

    # Detailed info
    print('\n📋 DETAILED INFORMATION:\n')

    for idx, device in enumerate(devices, 1):
        print(f'[{idx}] {device.get("systemName", "N/A")}')
        print(f'    Device ID: {device.get("id")}')
        print(f'    DNS Name: {device.get("dnsName", "N/A")}')
        print(f'    Status: {"🟢 Online" if not device.get("offline") else "🔴 Offline"}')
        print(f'    Organization ID: {device.get("organizationId", "N/A")}')
        print(f'    Node Class: {device.get("nodeClass", "N/A")}')

        # Last contact
        last_contact = device.get('lastContact', 0)
        if last_contact:
            from datetime import datetime
            try:
                dt = datetime.fromtimestamp(last_contact)
                print(f'    Last Contact: {dt.strftime("%Y-%m-%d %H:%M:%S")}')
            except:
                print(f'    Last Contact: {last_contact}')

        print()

    # Export to JSON
    output_file = f'{search_term.lower()}_machines_report.json'
    with open(output_file, 'w') as f:
        json.dump(devices, f, indent=2)

    print(f'📄 Full details exported to: {output_file}')
    print()


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║     NinjaRMM Machine Report - Filter by "ZEEV"                 ║')
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

    # Step 3: Filter devices containing "zeev"
    search_term = 'zeev'
    matching_devices = filter_devices_by_name(all_devices, search_term)

    # Step 4: Generate report
    generate_report(matching_devices, search_term)


if __name__ == '__main__':
    main()
