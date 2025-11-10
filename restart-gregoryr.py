#!/usr/bin/env python3

"""
Force restart IT-GREGORYR (ID: 515)
"""

import requests
import json

CONFIG = {
    'client_id': 'H9E-VrYBPxfV1_zf17IExUgs_o4',
    'client_secret': 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
    'base_url': 'https://comda.rmmservice.eu',
}

DEVICE_ID = 515
DEVICE_NAME = 'IT-GREGORYR'

print('╔════════════════════════════════════════════════════════════════╗')
print('║         FORCE RESTART IT-GREGORYR                              ║')
print('╚════════════════════════════════════════════════════════════════╝')
print()

# Get token
print('🔐 Authenticating...')
token_url = f'{CONFIG["base_url"]}/ws/oauth/token'
payload = {
    'grant_type': 'client_credentials',
    'client_id': CONFIG['client_id'],
    'client_secret': CONFIG['client_secret'],
    'scope': 'monitoring management'
}
response = requests.post(token_url, data=payload, timeout=30)

if response.status_code != 200:
    print(f'❌ Authentication failed: {response.status_code}')
    exit(1)

token = response.json().get('access_token')
print('✅ Authenticated!\n')

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Verify device status
print(f'📋 Device: {DEVICE_NAME} (ID: {DEVICE_ID})')
print(f'   DNS: IT-Gregoryr.comda.co.il')
print(f'   Status: 🟢 Online\n')

print('🔄 Sending FORCE RESTART command...\n')

# Try multiple restart methods
restart_methods = [
    ('Script - PowerShell', f'/v2/device/{DEVICE_ID}/scripting/run', {
        'type': 'POWERSHELL',
        'scriptContent': 'Restart-Computer -Force'
    }),
    ('Script - CMD', f'/v2/device/{DEVICE_ID}/scripting/run', {
        'type': 'COMMAND',
        'scriptContent': 'shutdown /r /f /t 0'
    }),
    ('Direct Reboot', f'/v2/device/{DEVICE_ID}/reboot', {
        'force': True
    }),
    ('Action Reboot', f'/v2/device/{DEVICE_ID}/actions/reboot', {}),
]

success = False

for method_name, endpoint, payload in restart_methods:
    print(f'   Trying: {method_name}...')

    try:
        url = f'{CONFIG["base_url"]}{endpoint}'
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code in [200, 201, 202, 204]:
            print(f'   ✅ SUCCESS! (Status: {response.status_code})')
            if response.text:
                try:
                    print(f'   Response: {json.dumps(response.json(), indent=2)}')
                except:
                    print(f'   Response: {response.text[:200]}')
            success = True
            break
        else:
            print(f'   ❌ Failed: {response.status_code}')
            if response.text:
                print(f'   Error: {response.text[:150]}')
    except Exception as e:
        print(f'   ❌ Error: {str(e)[:100]}')

    print()

print('=' * 70)

if success:
    print('✅ FORCE RESTART COMMAND SENT SUCCESSFULLY!')
    print()
    print(f'   Device: {DEVICE_NAME}')
    print(f'   ID: {DEVICE_ID}')
    print(f'   Action: Force Restart')
    print()
    print('   ⚡ The computer will restart immediately.')
else:
    print('❌ All restart methods failed!')
    print()
    print('Alternative options:')
    print(f'   1. Restart from NinjaRMM web: {CONFIG["base_url"]}/app/devices/{DEVICE_ID}')
    print('   2. Contact user Gregory to restart manually')
    print('   3. Use remote desktop if available')

print('=' * 70)
