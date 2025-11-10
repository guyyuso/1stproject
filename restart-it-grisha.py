#!/usr/bin/env python3

"""
Force restart IT-GRISHA laptop via NinjaRMM API
"""

import requests
import json
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


def find_device(access_token: str, device_name: str) -> Optional[Dict[Any, Any]]:
    """Find device by name"""
    print(f'🔍 Searching for device: {device_name}...')

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

                if device_name.lower() in system_name or device_name.lower() in dns_name:
                    print(f'✅ Found device: {device.get("systemName")} (ID: {device.get("id")})')
                    print(f'   DNS Name: {device.get("dnsName", "N/A")}')
                    print(f'   Status: {"🟢 Online" if not device.get("offline") else "🔴 Offline"}')
                    print()
                    return device

            print(f'❌ No device found with name: {device_name}')
            return None

    except requests.exceptions.RequestException as e:
        print(f'❌ Error: {str(e)}')
        return None


def force_restart_device(access_token: str, device_id: int, device_name: str) -> bool:
    """Force restart device using NinjaRMM scripting"""
    print(f'🔄 Sending FORCE RESTART command to {device_name}...\n')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Try multiple restart methods
    methods = [
        # Method 1: Direct reboot endpoint
        {
            'url': f'{CONFIG["base_url"]}/v2/device/{device_id}/reboot',
            'method': 'POST',
            'payload': {'mode': 'FORCED'}
        },
        # Method 2: Script run with PowerShell restart
        {
            'url': f'{CONFIG["base_url"]}/v2/device/{device_id}/script/run',
            'method': 'POST',
            'payload': {
                'type': 'POWERSHELL',
                'script': 'Restart-Computer -Force'
            }
        },
        # Method 3: Windows command restart
        {
            'url': f'{CONFIG["base_url"]}/v2/device/{device_id}/script/run',
            'method': 'POST',
            'payload': {
                'type': 'COMMAND',
                'script': 'shutdown /r /f /t 0'
            }
        },
        # Method 4: Action endpoint
        {
            'url': f'{CONFIG["base_url"]}/v2/device/{device_id}/action/reboot',
            'method': 'POST',
            'payload': {}
        }
    ]

    for idx, method in enumerate(methods, 1):
        print(f'   [{idx}] Trying: {method["url"].split("/")[-1]}...')

        try:
            if method['method'] == 'POST':
                response = requests.post(
                    method['url'],
                    headers=headers,
                    json=method['payload'],
                    timeout=30
                )

            if response.status_code in [200, 201, 202, 204]:
                print(f'       ✅ SUCCESS! Status: {response.status_code}')
                if response.text:
                    try:
                        resp_data = response.json()
                        print(f'       Response: {json.dumps(resp_data, indent=2)}')
                    except:
                        print(f'       Response: {response.text[:200]}')
                return True
            elif response.status_code == 404:
                print(f'       ⚠️  Endpoint not found')
            else:
                print(f'       ❌ Failed with status: {response.status_code}')
                if response.text:
                    print(f'       Error: {response.text[:150]}')

        except requests.exceptions.RequestException as e:
            print(f'       ❌ Error: {str(e)[:100]}')

        print()

    # Try using maintenance endpoint
    print(f'   [5] Trying maintenance/reboot endpoint...')
    try:
        url = f'{CONFIG["base_url"]}/v2/device/{device_id}/maintenance/reboot'
        response = requests.post(url, headers=headers, json={'force': True}, timeout=30)

        if response.status_code in [200, 201, 202, 204]:
            print(f'       ✅ SUCCESS! Status: {response.status_code}')
            return True
        else:
            print(f'       ❌ Failed with status: {response.status_code}')
    except Exception as e:
        print(f'       ❌ Error: {str(e)[:100]}')

    return False


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║         Force Restart IT-GRISHA via NinjaRMM API               ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Step 1: Authenticate
    access_token = get_access_token()
    if not access_token:
        print('❌ Cannot proceed without authentication.')
        return

    # Step 2: Find device
    device = find_device(access_token, 'it-grisha')
    if not device:
        print('❌ Device not found. Exiting.')
        return

    device_id = device.get('id')
    system_name = device.get('systemName')

    if device.get('offline'):
        print('⚠️  WARNING: Device is currently OFFLINE.')
        print('   The restart command will be queued and executed when device comes online.')
        print()

    # Step 3: Send force restart command
    print('=' * 70)
    success = force_restart_device(access_token, device_id, system_name)
    print('=' * 70)
    print()

    if success:
        print('✅ FORCE RESTART COMMAND SENT SUCCESSFULLY!')
        print()
        print(f'   Device: {system_name}')
        print(f'   ID: {device_id}')
        print(f'   Action: Force Restart')
        print()
        print('   The computer will restart immediately.')
    else:
        print('❌ FORCE RESTART COMMAND FAILED!')
        print()
        print('Alternative options:')
        print('   1. Restart manually from NinjaRMM web interface')
        print(f'      URL: {CONFIG["base_url"]}/app/devices/{device_id}')
        print('   2. Contact the user to restart locally')
        print('   3. Use remote desktop to restart')


if __name__ == '__main__':
    main()
