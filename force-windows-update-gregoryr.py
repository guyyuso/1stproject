#!/usr/bin/env python3

"""
Force Windows Update on IT-GREGORYR (ID: 515) - All Methods
"""

import requests
import json
import time

CONFIG = {
    'client_id': 'H9E-VrYBPxfV1_zf17IExUgs_o4',
    'client_secret': 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
    'base_url': 'https://comda.rmmservice.eu',
}

DEVICE_ID = 515
DEVICE_NAME = 'IT-GREGORYR'

print('╔════════════════════════════════════════════════════════════════╗')
print('║     FORCE WINDOWS UPDATE - IT-GREGORYR (ALL METHODS)           ║')
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

print(f'📋 Device: {DEVICE_NAME} (ID: {DEVICE_ID})')
print(f'   DNS: IT-Gregoryr.comda.co.il')
print(f'   OS: Windows 11 Professional Edition')
print(f'   Status: 🟢 Online\n')

print('🔄 Attempting to FORCE Windows Update using all available methods...\n')
print('=' * 70)

# First, let's check what endpoints are available
print('\n📡 Step 1: Checking available device endpoints...\n')

test_endpoints = [
    '/v2/device/{id}/scripting',
    '/v2/device/{id}/script',
    '/v2/device/{id}/tasks',
    '/v2/device/{id}/jobs',
    '/v2/device/{id}/software-patch-management',
    '/v2/device/{id}/windows-updates',
    '/v2/device/{id}/policies',
    '/v2/device/{id}/actions',
]

available_endpoints = []

for endpoint_template in test_endpoints:
    endpoint = endpoint_template.replace('{id}', str(DEVICE_ID))
    url = f'{CONFIG["base_url"]}{endpoint}'

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 404:
            print(f'   ✅ Available: {endpoint} (Status: {response.status_code})')
            available_endpoints.append(endpoint)
        else:
            print(f'   ❌ Not found: {endpoint}')
    except Exception as e:
        print(f'   ⚠️  Error checking {endpoint}: {str(e)[:50]}')

print('\n' + '=' * 70)
print(f'\n📊 Found {len(available_endpoints)} available endpoint(s)\n')
print('=' * 70)

# Now try comprehensive Windows Update methods
print('\n🔄 Step 2: Attempting Windows Update execution...\n')

update_attempts = [
    # Method 1: Jobs/Tasks endpoints
    ('Create Windows Update Job', f'/v2/device/{DEVICE_ID}/jobs', 'POST', {
        'type': 'WINDOWS_UPDATE',
        'name': 'Force Windows Update',
        'runNow': True
    }),

    # Method 2: Tasks endpoint
    ('Create Update Task', f'/v2/device/{DEVICE_ID}/tasks', 'POST', {
        'name': 'Windows Update',
        'type': 'WINDOWS_UPDATE',
        'schedule': 'immediate'
    }),

    # Method 3: Actions endpoint
    ('Trigger Update Action', f'/v2/device/{DEVICE_ID}/actions', 'POST', {
        'action': 'WINDOWS_UPDATE',
        'force': True
    }),

    # Method 4: Software patch management
    ('Software Patch Scan', f'/v2/device/{DEVICE_ID}/software-patch-management/scan', 'POST', {}),

    ('Software Patch Install', f'/v2/device/{DEVICE_ID}/software-patch-management/install', 'POST', {
        'installAll': True,
        'rebootIfRequired': True
    }),

    # Method 5: Windows Updates specific
    ('Windows Update Scan', f'/v2/device/{DEVICE_ID}/windows-updates', 'POST', {
        'action': 'scan'
    }),

    ('Windows Update Install All', f'/v2/device/{DEVICE_ID}/windows-updates', 'POST', {
        'action': 'install',
        'updateIds': 'all',
        'rebootIfRequired': True
    }),

    # Method 6: Scripting/run endpoints
    ('Run Script - USO Client', f'/v2/device/{DEVICE_ID}/scripting', 'POST', {
        'language': 'cmd',
        'script': 'usoclient StartScan && usoclient StartDownload && usoclient StartInstall'
    }),

    ('Run Script - PowerShell', f'/v2/device/{DEVICE_ID}/script', 'POST', {
        'type': 'powershell',
        'content': 'Start-Process "ms-settings:windowsupdate" && (New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search("IsInstalled=0").Updates | ForEach-Object { $_.Install() }'
    }),

    # Method 7: Policy enforcement
    ('Enforce Update Policy', f'/v2/device/{DEVICE_ID}/policies/enforce', 'POST', {
        'policyType': 'WINDOWS_UPDATE',
        'force': True
    }),
]

success = False
successful_method = None

for idx, (method_name, endpoint, http_method, payload_data) in enumerate(update_attempts, 1):
    print(f'[{idx}/{len(update_attempts)}] {method_name}')
    print(f'    Endpoint: {endpoint}')

    try:
        url = f'{CONFIG["base_url"]}{endpoint}'

        if http_method == 'POST':
            response = requests.post(url, headers=headers, json=payload_data, timeout=30)
        elif http_method == 'PUT':
            response = requests.put(url, headers=headers, json=payload_data, timeout=30)

        print(f'    Status: {response.status_code}')

        if response.status_code in [200, 201, 202, 204]:
            print(f'    ✅ SUCCESS!')
            if response.text:
                try:
                    resp_json = response.json()
                    print(f'    Response: {json.dumps(resp_json, indent=4)[:400]}')
                except:
                    print(f'    Response: {response.text[:200]}')
            success = True
            successful_method = method_name
            break
        elif response.status_code == 404:
            print(f'    ❌ Endpoint not found')
        elif response.status_code == 403:
            print(f'    ❌ Permission denied')
        else:
            print(f'    ❌ Failed')
            if response.text:
                print(f'    Error: {response.text[:150]}')

    except Exception as e:
        print(f'    ❌ Exception: {str(e)[:100]}')

    print()
    time.sleep(0.5)

print('=' * 70)

if success:
    print('\n✅ ✅ ✅  WINDOWS UPDATE INITIATED SUCCESSFULLY! ✅ ✅ ✅\n')
    print(f'   Method Used: {successful_method}')
    print(f'   Device: {DEVICE_NAME} (ID: {DEVICE_ID})')
    print(f'   Action: Force Windows Update')
    print()
    print('   📥 What happens next:')
    print('      1. Device will check for Windows updates')
    print('      2. Updates will download automatically')
    print('      3. Updates will install automatically')
    print('      4. Device may restart if required')
    print()
    print('   ⏱️  Expected duration: 15-60 minutes')
    print('   🔄 Monitor progress in NinjaRMM dashboard')
else:
    print('\n❌ ALL WINDOWS UPDATE METHODS FAILED\n')
    print('   The API does not support remote Windows Update execution')
    print('   with the current OAuth permissions and endpoint availability.')
    print()
    print('   📋 Manual alternatives:')
    print()
    print('   Option 1: NinjaRMM Web Interface')
    print(f'      → https://comda.rmmservice.eu/app/devices/{DEVICE_ID}')
    print('      → Click Actions → Windows Update / Patch Management')
    print()
    print('   Option 2: Contact User Gregory')
    print('      → Ask to open: Settings → Windows Update')
    print('      → Click "Check for updates"')
    print()
    print('   Option 3: Remote Desktop')
    print('      → RDP to IT-Gregoryr.comda.co.il')
    print('      → Manually run Windows Update')

print('=' * 70)
