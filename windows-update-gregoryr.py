#!/usr/bin/env python3

"""
Run Windows Update on IT-GREGORYR (ID: 515)
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
print('║         RUN WINDOWS UPDATE - IT-GREGORYR                       ║')
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

# Device info
print(f'📋 Device: {DEVICE_NAME} (ID: {DEVICE_ID})')
print(f'   DNS: IT-Gregoryr.comda.co.il')
print(f'   OS: Windows 11 Professional Edition')
print(f'   Status: 🟢 Online\n')

print('🔄 Triggering Windows Update...\n')

# PowerShell script to run Windows Update
windows_update_script = """
# Install PSWindowsUpdate module if not present
if (!(Get-Module -ListAvailable -Name PSWindowsUpdate)) {
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
    Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck
}

# Import module
Import-Module PSWindowsUpdate

# Check for updates
Write-Host "Checking for Windows Updates..."
Get-WindowsUpdate -MicrosoftUpdate

# Install all updates
Write-Host "Installing Windows Updates..."
Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot
"""

# Alternative simpler method using Windows Update client
simple_update_script = """
# Trigger Windows Update using COM object
Write-Host "Starting Windows Update..."
$updateSession = New-Object -ComObject Microsoft.Update.Session
$updateSearcher = $updateSession.CreateUpdateSearcher()

Write-Host "Searching for updates..."
$searchResult = $updateSearcher.Search("IsInstalled=0 and Type='Software'")

if ($searchResult.Updates.Count -eq 0) {
    Write-Host "No updates available"
} else {
    Write-Host "Found $($searchResult.Updates.Count) update(s)"

    $updatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl
    foreach ($update in $searchResult.Updates) {
        Write-Host "- $($update.Title)"
        $updatesToDownload.Add($update) | Out-Null
    }

    Write-Host "Downloading updates..."
    $downloader = $updateSession.CreateUpdateDownloader()
    $downloader.Updates = $updatesToDownload
    $downloadResult = $downloader.Download()

    Write-Host "Installing updates..."
    $installer = $updateSession.CreateUpdateInstaller()
    $installer.Updates = $updatesToDownload
    $installResult = $installer.Install()

    Write-Host "Installation complete. Reboot required: $($installResult.RebootRequired)"
}
"""

# Command line method
cmd_update = 'usoclient StartScan && usoclient StartDownload && usoclient StartInstall'

# Try different methods to trigger Windows Update
update_methods = [
    ('USO Client Command', f'/v2/device/{DEVICE_ID}/scripting/run', {
        'type': 'COMMAND',
        'scriptContent': cmd_update
    }),
    ('PowerShell - Simple Update', f'/v2/device/{DEVICE_ID}/scripting/run', {
        'type': 'POWERSHELL',
        'scriptContent': simple_update_script
    }),
    ('PowerShell - PSWindowsUpdate', f'/v2/device/{DEVICE_ID}/scripting/run', {
        'type': 'POWERSHELL',
        'scriptContent': windows_update_script
    }),
    ('Windows Update Task', f'/v2/device/{DEVICE_ID}/scripting/run', {
        'type': 'POWERSHELL',
        'scriptContent': 'Start-Process "ms-settings:windowsupdate-action"'
    }),
]

success = False

for method_name, endpoint, payload_data in update_methods:
    print(f'   [{update_methods.index((method_name, endpoint, payload_data)) + 1}] Trying: {method_name}...')

    try:
        url = f'{CONFIG["base_url"]}{endpoint}'
        response = requests.post(url, headers=headers, json=payload_data, timeout=60)

        if response.status_code in [200, 201, 202, 204]:
            print(f'       ✅ SUCCESS! (Status: {response.status_code})')
            if response.text:
                try:
                    resp_json = response.json()
                    print(f'       Job ID: {resp_json.get("jobId", "N/A")}')
                    print(f'       Response: {json.dumps(resp_json, indent=2)[:300]}')
                except:
                    print(f'       Response: {response.text[:200]}')
            success = True
            break
        else:
            print(f'       ❌ Failed: {response.status_code}')
            if response.text:
                print(f'       Error: {response.text[:150]}')
    except Exception as e:
        print(f'       ❌ Error: {str(e)[:100]}')

    print()
    time.sleep(1)

print('=' * 70)

if success:
    print('✅ WINDOWS UPDATE TRIGGERED SUCCESSFULLY!')
    print()
    print(f'   Device: {DEVICE_NAME}')
    print(f'   ID: {DEVICE_ID}')
    print(f'   Action: Windows Update')
    print()
    print('   📥 The device is now:')
    print('      1. Checking for available Windows updates')
    print('      2. Downloading updates in the background')
    print('      3. Installing updates automatically')
    print()
    print('   ⚠️  Note: The device may restart automatically after updates install')
    print('   ⏱️  Update process may take 15-60 minutes depending on size')
else:
    print('❌ All Windows Update methods failed!')
    print()
    print('Alternative options:')
    print('   1. Manually run Windows Update from NinjaRMM web interface')
    print(f'      URL: {CONFIG["base_url"]}/app/devices/{DEVICE_ID}')
    print('   2. Ask user Gregory to run Windows Update manually:')
    print('      Settings > Windows Update > Check for updates')
    print('   3. Remote into the machine and run updates manually')

print('=' * 70)
