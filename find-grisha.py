#!/usr/bin/env python3

"""
Find devices with 'grisha' in the name
"""

import requests
import json

# Configuration
CONFIG = {
    'client_id': 'H9E-VrYBPxfV1_zf17IExUgs_o4',
    'client_secret': 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
    'base_url': 'https://comda.rmmservice.eu',
    'token_endpoint': '/ws/oauth/token',
    'devices_endpoint': '/v2/devices'
}

def get_access_token():
    token_url = f'{CONFIG["base_url"]}{CONFIG["token_endpoint"]}'

    payload = {
        'grant_type': 'client_credentials',
        'client_id': CONFIG['client_id'],
        'client_secret': CONFIG['client_secret'],
        'scope': 'monitoring management'
    }

    response = requests.post(token_url, data=payload, timeout=30)

    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def find_grisha_devices(access_token):
    print('🔍 Searching for devices with "grisha" in name...\n')

    devices_url = f'{CONFIG["base_url"]}{CONFIG["devices_endpoint"]}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(devices_url, headers=headers, timeout=30)

    if response.status_code == 200:
        devices = response.json()

        matching = []
        for device in devices:
            system_name = device.get('systemName', '').lower()
            dns_name = device.get('dnsName', '').lower()

            if 'grisha' in system_name or 'grisha' in dns_name:
                matching.append(device)

        if matching:
            print(f'✅ Found {len(matching)} device(s):\n')
            for device in matching:
                print(f'Name: {device.get("systemName")}')
                print(f'DNS: {device.get("dnsName", "N/A")}')
                print(f'ID: {device.get("id")}')
                print(f'Status: {"🟢 Online" if not device.get("offline") else "🔴 Offline"}')
                print(f'Organization: {device.get("organizationId")}')
                print('-' * 60)
        else:
            print('❌ No devices found with "grisha" in name')
            print('\nSearching for similar names (grish, gris, etc.)...\n')

            for device in devices:
                system_name = device.get('systemName', '').lower()
                if 'gri' in system_name or 'gre' in system_name:
                    print(f'Possible match: {device.get("systemName")} (ID: {device.get("id")})')

if __name__ == '__main__':
    token = get_access_token()
    if token:
        find_grisha_devices(token)
