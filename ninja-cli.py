#!/usr/bin/env python3

"""
NinjaRMM CLI - Command Line Interface for NinjaRMM Management

A unified CLI tool for managing computers via NinjaRMM API.

Usage:
    ninja-cli.py search <name>           - Search for computers by name
    ninja-cli.py restart <name>          - Restart a computer
    ninja-cli.py list                    - List all computers
    ninja-cli.py list-guy                - List computers with 'guy' in name
    ninja-cli.py info <name>             - Get detailed info about a computer
    ninja-cli.py --help                  - Show this help message

Examples:
    ninja-cli.py search "IT-GREGORYR"
    ninja-cli.py restart "IT-GREGORYR"
    ninja-cli.py list-guy
    ninja-cli.py info "daniel 2019"
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
    'devices_endpoint': '/v2/devices',
    'reboot_endpoint': '/v2/device/{device_id}/reboot'
}


class NinjaAPI:
    """NinjaRMM API Client"""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.access_token = None

    def authenticate(self) -> bool:
        """Authenticate with NinjaRMM and get access token"""
        print('🔐 Authenticating with NinjaRMM...')

        token_url = f'{self.config["base_url"]}{self.config["token_endpoint"]}'

        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
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
                    self.access_token = token_data['access_token']
                    print('✅ Authentication successful!\n')
                    return True

            print(f'❌ Authentication failed: {response.status_code}')
            print(f'Response: {response.text}\n')
            return False

        except requests.exceptions.RequestException as e:
            print(f'❌ Error: {str(e)}\n')
            return False

    def get_devices(self) -> Optional[List[Dict[Any, Any]]]:
        """Get all devices from NinjaRMM"""
        if not self.access_token:
            print('❌ Not authenticated. Call authenticate() first.')
            return None

        print('📡 Fetching devices from NinjaRMM...')

        devices_url = f'{self.config["base_url"]}{self.config["devices_endpoint"]}'

        headers = {
            'Authorization': f'Bearer {self.access_token}',
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

    def search_devices(self, devices: List[Dict[Any, Any]], search_term: str) -> List[Dict[Any, Any]]:
        """Search for devices by name"""
        results = []
        for device in devices:
            system_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')
            if search_term.lower() in system_name.lower():
                results.append(device)
        return results

    def reboot_device(self, device_id: int, device_name: str) -> bool:
        """Send reboot command to a device"""
        if not self.access_token:
            print('❌ Not authenticated.')
            return False

        print(f'🔄 Sending reboot command to: {device_name} (ID: {device_id})')

        reboot_url = f'{self.config["base_url"]}{self.config["reboot_endpoint"]}'.format(device_id=device_id)

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(reboot_url, headers=headers, json={}, timeout=30)

            if response.status_code in [200, 201, 202, 204]:
                print(f'✅ Reboot command sent successfully!')
                print(f'   Status Code: {response.status_code}\n')
                return True
            else:
                print(f'❌ Reboot failed: {response.status_code}')
                print(f'   Response: {response.text}\n')
                return False

        except requests.exceptions.RequestException as e:
            print(f'❌ Error: {str(e)}\n')
            return False


def print_device_summary(device: Dict[Any, Any], index: int = None):
    """Print device summary in one line"""
    system_name = device.get('systemName', 'N/A')
    device_id = device.get('id', 'N/A')
    online = device.get('online', False)
    status = "🟢" if online else "🔴"

    if index:
        print(f'  [{index}] {status} {system_name:<40} ID: {device_id}')
    else:
        print(f'  {status} {system_name:<40} ID: {device_id}')


def print_device_details(device: Dict[Any, Any]):
    """Print detailed device information"""
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


def cmd_search(api: NinjaAPI, search_term: str):
    """Search for computers by name"""
    print(f'🔍 Searching for: "{search_term}"\n')

    devices = api.get_devices()
    if not devices:
        return 1

    results = api.search_devices(devices, search_term)

    if not results:
        print(f'❌ No devices found matching "{search_term}"\n')
        return 1

    print(f'✅ Found {len(results)} device(s):\n')
    for idx, device in enumerate(results, 1):
        print_device_summary(device, idx)

    print()
    return 0


def cmd_restart(api: NinjaAPI, computer_name: str):
    """Restart a computer by name"""
    print(f'🎯 Target: {computer_name}\n')

    devices = api.get_devices()
    if not devices:
        return 1

    results = api.search_devices(devices, computer_name)

    if not results:
        print(f'❌ Computer "{computer_name}" not found.\n')
        return 1

    if len(results) > 1:
        print(f'⚠️  Multiple computers found matching "{computer_name}":\n')
        for idx, device in enumerate(results, 1):
            print_device_summary(device, idx)
        print('\n❌ Please be more specific.\n')
        return 1

    device = results[0]
    device_id = device.get('id')
    system_name = device.get('systemName', 'N/A')

    print_device_summary(device)
    print()

    success = api.reboot_device(device_id, system_name)
    return 0 if success else 1


def cmd_list(api: NinjaAPI):
    """List all computers"""
    devices = api.get_devices()
    if not devices:
        return 1

    print(f'📋 All Computers ({len(devices)} total):\n')
    for idx, device in enumerate(devices, 1):
        print_device_summary(device, idx)

    print()
    return 0


def cmd_list_guy(api: NinjaAPI):
    """List computers with 'guy' in name"""
    devices = api.get_devices()
    if not devices:
        return 1

    results = api.search_devices(devices, 'guy')

    if not results:
        print('❌ No computers found with "guy" in name.\n')
        return 1

    print(f'📋 Computers with "guy" in name ({len(results)} found):\n')
    for idx, device in enumerate(results, 1):
        print_device_summary(device, idx)

    print()
    return 0


def cmd_info(api: NinjaAPI, computer_name: str):
    """Get detailed information about a computer"""
    print(f'🔍 Getting info for: "{computer_name}"\n')

    devices = api.get_devices()
    if not devices:
        return 1

    results = api.search_devices(devices, computer_name)

    if not results:
        print(f'❌ Computer "{computer_name}" not found.\n')
        return 1

    for idx, device in enumerate(results, 1):
        if len(results) > 1:
            print(f'\n[{idx}] ')
        print_device_details(device)
        print()

    return 0


def print_help():
    """Print help message"""
    print(__doc__)


def main():
    """Main CLI entry point"""
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║                    NinjaRMM CLI Tool                           ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        return 0

    command = sys.argv[1].lower()

    # Initialize API client
    api = NinjaAPI(CONFIG)

    # Authenticate
    if not api.authenticate():
        print('❌ Authentication failed. Please check your credentials.\n')
        return 1

    # Execute command
    if command == 'search':
        if len(sys.argv) < 3:
            print('❌ Usage: ninja-cli.py search <name>\n')
            return 1
        search_term = ' '.join(sys.argv[2:])
        return cmd_search(api, search_term)

    elif command == 'restart':
        if len(sys.argv) < 3:
            print('❌ Usage: ninja-cli.py restart <name>\n')
            return 1
        computer_name = ' '.join(sys.argv[2:])
        return cmd_restart(api, computer_name)

    elif command == 'list':
        return cmd_list(api)

    elif command == 'list-guy':
        return cmd_list_guy(api)

    elif command == 'info':
        if len(sys.argv) < 3:
            print('❌ Usage: ninja-cli.py info <name>\n')
            return 1
        computer_name = ' '.join(sys.argv[2:])
        return cmd_info(api, computer_name)

    else:
        print(f'❌ Unknown command: {command}\n')
        print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
