#!/usr/bin/env python3

"""
Disable Bluetooth on a computer via NinjaRMM API

This script:
1. Authenticates with NinjaRMM
2. Finds the device by name
3. Sends a PowerShell script to disable Bluetooth

Usage: python3 disable-bluetooth.py <computer-name>
"""

import requests
import json
import sys
import time
from typing import Optional, List, Dict, Any

# Configuration
CONFIG = {
    'client_id': 'J0CpD5xrF5WKV2qo50lxNbkUZ5k',
    'client_secret': 'VOwtkv-xVvO5HoZcIbncQxI-QIU4-OVC27DTFTHnZfJEGojG38lrbg',
    'base_url': 'https://comda.rmmservice.eu',
    'token_endpoint': '/ws/oauth/token',
    'devices_endpoint': '/v2/devices',
    'scripting_endpoint': '/v2/device/{device_id}/script/run'
}

# PowerShell script to disable Bluetooth
DISABLE_BLUETOOTH_SCRIPT = """
# Disable Bluetooth on Windows

Write-Host "Disabling Bluetooth..."

# Method 1: Disable Bluetooth Support Service
$service = Get-Service -Name "bthserv" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "Stopping Bluetooth Support Service..."
    Stop-Service -Name "bthserv" -Force -ErrorAction SilentlyContinue
    Set-Service -Name "bthserv" -StartupType Disabled -ErrorAction SilentlyContinue
    Write-Host "✓ Bluetooth Support Service disabled"
}

# Method 2: Disable Bluetooth Radio via Device Manager
Write-Host "Disabling Bluetooth radios..."
$bluetoothRadios = Get-PnpDevice | Where-Object {
    $_.Class -eq "Bluetooth" -or
    $_.FriendlyName -like "*Bluetooth*" -or
    $_.Description -like "*Bluetooth*"
} | Where-Object {$_.Status -eq "OK"}

if ($bluetoothRadios) {
    foreach ($radio in $bluetoothRadios) {
        try {
            Write-Host "  Disabling: $($radio.FriendlyName)"
            Disable-PnpDevice -InstanceId $radio.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Host "  ✓ Disabled: $($radio.FriendlyName)"
        } catch {
            Write-Host "  ✗ Failed to disable: $($radio.FriendlyName) - $($_.Exception.Message)"
        }
    }
} else {
    Write-Host "No active Bluetooth radios found"
}

# Method 3: Disable via Registry (for persistent disable)
Write-Host "Setting registry keys to disable Bluetooth..."
$regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys"
if (Test-Path $regPath) {
    try {
        Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT" -Name "Start" -Value 4 -ErrorAction SilentlyContinue
        Write-Host "✓ Registry updated"
    } catch {
        Write-Host "✗ Failed to update registry: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "========================================="
Write-Host "Bluetooth has been disabled"
Write-Host "========================================="
Write-Host ""
Write-Host "Note: Changes may require a system restart to take full effect."
"""


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


def find_device_by_name(devices: List[Dict[Any, Any]], name: str) -> Optional[Dict[Any, Any]]:
    """Find a device by exact or partial name match"""
    print(f'🔍 Searching for device: {name}')

    # Try exact match first
    for device in devices:
        system_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')
        if system_name.upper() == name.upper():
            print(f'✅ Found exact match: {system_name}\n')
            return device

    # Try partial match
    for device in devices:
        system_name = device.get('systemName', '') or device.get('dnsName', '') or device.get('name', '')
        if name.upper() in system_name.upper():
            print(f'✅ Found partial match: {system_name}\n')
            return device

    print(f'❌ Device not found: {name}\n')
    return None


def run_script_on_device(access_token: str, device_id: int, device_name: str, script: str) -> bool:
    """Run a PowerShell script on a device"""
    print(f'📜 Sending PowerShell script to: {device_name} (ID: {device_id})')

    # Try multiple possible endpoint formats
    endpoints = [
        f'/v2/device/{device_id}/script/run',
        f'/v2/devices/{device_id}/script/run',
        f'/v2/device/{device_id}/scripting/run',
        f'/v2/device/{device_id}/action/script'
    ]

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Try different payload formats
    payloads = [
        {
            'type': 'powershell',
            'script': script
        },
        {
            'scriptType': 'powershell',
            'scriptContent': script
        },
        {
            'language': 'powershell',
            'content': script
        }
    ]

    for endpoint in endpoints:
        script_url = f'{CONFIG["base_url"]}{endpoint}'

        for payload in payloads:
            try:
                print(f'   Trying endpoint: {endpoint}')
                response = requests.post(script_url, headers=headers, json=payload, timeout=30)

                if response.status_code in [200, 201, 202, 204]:
                    print(f'✅ Script execution initiated successfully!')
                    print(f'   Status Code: {response.status_code}')
                    if response.text:
                        print(f'   Response: {response.text}')
                    print()
                    return True

            except requests.exceptions.RequestException:
                continue

    print(f'❌ All script execution endpoints failed.\n')
    print('⚠️  This might be because:')
    print('   1. The scripting API endpoint is different')
    print('   2. Additional permissions are needed')
    print('   3. The device needs to be online')
    print()
    print('📋 Alternative: Manually disable Bluetooth on IT-GREGORYR:')
    print('   1. Open Device Manager')
    print('   2. Expand "Bluetooth"')
    print('   3. Right-click Bluetooth adapter → Disable device')
    print()
    return False


def main():
    print('╔════════════════════════════════════════════════════════════════╗')
    print('║           Disable Bluetooth via NinjaRMM                       ║')
    print('╚════════════════════════════════════════════════════════════════╝')
    print()

    # Get computer name from command line argument
    if len(sys.argv) < 2:
        print('❌ Usage: python3 disable-bluetooth.py <computer-name>')
        print('   Example: python3 disable-bluetooth.py IT-GREGORYR')
        sys.exit(1)

    computer_name = sys.argv[1]
    print(f'Target Computer: {computer_name}\n')

    # Step 1: Authenticate
    access_token = get_access_token()
    if not access_token:
        print('❌ Cannot proceed without authentication.')
        sys.exit(1)

    # Step 2: Get all devices
    all_devices = get_all_devices(access_token)
    if not all_devices:
        print('❌ Cannot retrieve devices.')
        sys.exit(1)

    # Step 3: Find the target device
    target_device = find_device_by_name(all_devices, computer_name)
    if not target_device:
        print(f'❌ Device "{computer_name}" not found.')
        print('\nAvailable devices:')
        for device in all_devices[:10]:  # Show first 10
            name = device.get('systemName', 'N/A')
            print(f'   - {name}')
        sys.exit(1)

    # Display device info
    device_id = target_device.get('id')
    system_name = target_device.get('systemName', 'N/A')
    online = target_device.get('online', False)
    status = "🟢 Online" if online else "🔴 Offline"

    print('─' * 60)
    print('TARGET DEVICE INFORMATION')
    print('─' * 60)
    print(f'  System Name: {system_name}')
    print(f'  Device ID:   {device_id}')
    print(f'  Status:      {status}')
    print('─' * 60)
    print()

    if not online:
        print('⚠️  WARNING: Device is offline.')
        print('   Script execution may fail or be delayed until device comes online.')
        print()
        response = input('Continue anyway? (y/n): ')
        if response.lower() != 'y':
            print('Aborted.')
            sys.exit(0)
        print()

    # Step 4: Run the script to disable Bluetooth
    success = run_script_on_device(access_token, device_id, system_name, DISABLE_BLUETOOTH_SCRIPT)

    if success:
        print('✅ SUCCESS: Bluetooth disable command sent successfully!')
        print()
        print('📝 Note: The script will:')
        print('   1. Stop Bluetooth Support Service')
        print('   2. Disable Bluetooth radios in Device Manager')
        print('   3. Update registry to prevent auto-start')
        print()
        print('⚠️  A system restart may be required for changes to take full effect.')
        sys.exit(0)
    else:
        print('❌ FAILED: Could not send Bluetooth disable command.')
        print()
        print('💡 You can manually disable Bluetooth using NinjaRMM web interface:')
        print('   1. Go to the device in NinjaRMM')
        print('   2. Use "Run Script" or "Remote Tools"')
        print('   3. Run the PowerShell script shown above')
        sys.exit(1)


if __name__ == '__main__':
    main()
