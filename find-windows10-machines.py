#!/usr/bin/env python3

"""
Find all machines running Windows 10 from NinjaRMM
"""

import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

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


def get_device_details(access_token: str, device_id: int) -> Optional[Dict[Any, Any]]:
    """Get detailed information for a specific device"""
    device_url = f'{CONFIG["base_url"]}/v2/device/{device_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(device_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        return None

    except requests.exceptions.RequestException:
        return None


def filter_windows10_devices(devices: List[Dict[Any, Any]], access_token: str) -> List[Dict[Any, Any]]:
    """Filter devices running Windows 10"""
    print('🔍 Analyzing OS versions...\n')

    windows10_devices = []

    for idx, device in enumerate(devices, 1):
        if idx % 50 == 0:
            print(f'   Processed {idx}/{len(devices)} devices...')

        system_name = device.get('systemName', 'N/A')

        # Check OS info in basic device data
        os_info = device.get('os', {})
        os_name = ''

        if isinstance(os_info, dict):
            os_name = os_info.get('name', '')

        # If no OS info in basic data, try to get detailed info
        if not os_name and device.get('nodeClass') in ['WINDOWS_WORKSTATION', 'WINDOWS_SERVER']:
            device_id = device.get('id')
            details = get_device_details(access_token, device_id)
            if details and 'os' in details:
                os_info = details.get('os', {})
                if isinstance(os_info, dict):
                    os_name = os_info.get('name', '')

        # Check if Windows 10
        if 'windows 10' in os_name.lower() or 'win 10' in os_name.lower():
            device['os_name'] = os_name
            windows10_devices.append(device)

    print(f'✅ Analysis complete!\n')
    return windows10_devices


def generate_report(devices: List[Dict[Any, Any]]):
    """Generate a formatted report of Windows 10 machines"""
    print('=' * 100)
    print('  MACHINES RUNNING WINDOWS 10')
    print('=' * 100)
    print()

    if not devices:
        print('✅ Good news! No machines found running Windows 10.')
        print('   All systems appear to be on Windows 11 or other OS versions.')
        print()
        return

    print(f'⚠️  Found {len(devices)} machine(s) still running Windows 10:\n')

    # Count by status
    online_count = sum(1 for d in devices if not d.get('offline', True))
    offline_count = len(devices) - online_count

    print(f'📊 Summary:')
    print(f'   Total: {len(devices)}')
    print(f'   Online: {online_count}')
    print(f'   Offline: {offline_count}')
    print()

    # Detailed table
    print(f'{"#":<5} {"System Name":<35} {"Status":<10} {"OS Version":<30} {"Last Contact":<15}')
    print('-' * 100)

    for idx, device in enumerate(devices, 1):
        system_name = device.get('systemName', 'N/A')[:33]
        online = not device.get('offline', True)
        status = "🟢 Online" if online else "🔴 Offline"
        os_name = device.get('os_name', 'Windows 10')[:28]

        # Format last contact
        last_contact = device.get('lastContact', 0)
        if last_contact:
            try:
                dt = datetime.fromtimestamp(last_contact)
                last_contact_str = dt.strftime('%Y-%m-%d')[:13]
            except:
                last_contact_str = 'N/A'
        else:
            last_contact_str = 'N/A'

        print(f'{idx:<5} {system_name:<35} {status:<10} {os_name:<30} {last_contact_str:<15}')

    print()
    print('=' * 100)

    # Group by organization
    print('\n📂 By Organization:')
    print('-' * 50)

    org_counts = {}
    for device in devices:
        org_id = device.get('organizationId', 'Unknown')
        org_counts[org_id] = org_counts.get(org_id, 0) + 1

    for org_id, count in sorted(org_counts.items(), key=lambda x: x[1], reverse=True):
        print(f'   Organization {org_id}: {count} machine(s)')

    print()
    print('=' * 100)

    # Support end-of-life warning
    print('\n⚠️  IMPORTANT: Windows 10 Support Status')
    print('-' * 50)
    print('   Windows 10 support ends: October 14, 2025')
    print('   After this date, Windows 10 will no longer receive:')
    print('   • Security updates')
    print('   • Bug fixes')
    print('   • Technical support')
    print()
    print('   ⚡ Action Required: Plan upgrades to Windows 11')
    print('=' * 100)

    # Export to JSON
    output_file = 'windows10_machines_report.json'
    with open(output_file, 'w') as f:
        json.dump(devices, f, indent=2)

    print(f'\n📄 Full details exported to: {output_file}')
    print()


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║     NinjaRMM Windows 10 Detection Report                       ║')
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

    # Step 3: Filter Windows 10 devices
    windows10_devices = filter_windows10_devices(all_devices, access_token)

    # Step 4: Generate report
    generate_report(windows10_devices)


if __name__ == '__main__':
    main()
