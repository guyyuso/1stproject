#!/usr/bin/env python3

"""
Check HIDUSHIM3 PC and Exchange Server Connection
"""

import requests
import json
from datetime import datetime

CONFIG = {
    'client_id': 'H9E-VrYBPxfV1_zf17IExUgs_o4',
    'client_secret': 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
    'base_url': 'https://comda.rmmservice.eu',
}

print('╔════════════════════════════════════════════════════════════════╗')
print('║     HIDUSHIM3 - Exchange Server Connection Report              ║')
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

# Search for HIDUSHIM3
print('🔍 Searching for HIDUSHIM3...')
devices_url = f'{CONFIG["base_url"]}/v2/devices'
response = requests.get(devices_url, headers=headers, timeout=30)

if response.status_code != 200:
    print(f'❌ Failed to get devices: {response.status_code}')
    exit(1)

devices = response.json()
device = None

for d in devices:
    system_name = d.get('systemName', '').lower()
    dns_name = d.get('dnsName', '').lower()

    if 'hidushim3' in system_name or 'hidushim3' in dns_name:
        device = d
        break

if not device:
    print('❌ Device HIDUSHIM3 not found')
    print('\nSearching for similar names (hidush, hidu)...')

    for d in devices:
        system_name = d.get('systemName', '').lower()
        if 'hidush' in system_name or 'hidu' in system_name:
            print(f'   Found: {d.get("systemName")} (ID: {d.get("id")})')
    exit(1)

print(f'✅ Found: {device.get("systemName")} (ID: {device.get("id")})\n')

# Get detailed device information
device_id = device.get('id')
print(f'📋 Getting detailed information for device {device_id}...\n')

device_detail_url = f'{CONFIG["base_url"]}/v2/device/{device_id}'
response = requests.get(device_detail_url, headers=headers, timeout=30)

if response.status_code == 200:
    device_detail = response.json()
else:
    device_detail = device

print('=' * 70)
print('DEVICE INFORMATION')
print('=' * 70)
print()

# Basic info
print(f'System Name:      {device_detail.get("systemName", "N/A")}')
print(f'DNS Name:         {device_detail.get("dnsName", "N/A")}')
print(f'Device ID:        {device_detail.get("id")}')
print(f'Organization ID:  {device_detail.get("organizationId", "N/A")}')
print(f'Location ID:      {device_detail.get("locationId", "N/A")}')
print()

# Status
offline = device_detail.get('offline', True)
print(f'Status:           {"🟢 ONLINE" if not offline else "🔴 OFFLINE"}')

if device_detail.get('lastContact'):
    last_contact = datetime.fromtimestamp(device_detail.get('lastContact'))
    print(f'Last Contact:     {last_contact.strftime("%Y-%m-%d %H:%M:%S")}')

print()

# OS Information
os_info = device_detail.get('os', {})
if isinstance(os_info, dict):
    print(f'Operating System: {os_info.get("name", "N/A")}')
    print(f'OS Version:       {os_info.get("version", "N/A")}')
print()

# Network Information
print('Network Information:')
public_ip = device_detail.get('publicIP', 'N/A')
print(f'  Public IP:      {public_ip}')

ip_addresses = device_detail.get('ipAddresses', [])
if ip_addresses:
    print(f'  IP Addresses:   {", ".join(ip_addresses)}')

dns_name = device_detail.get('dnsName', 'N/A')
print(f'  DNS Name:       {dns_name}')
print()

# Node class
print(f'Node Class:       {device_detail.get("nodeClass", "N/A")}')
print(f'Node Role ID:     {device_detail.get("nodeRoleId", "N/A")}')
print()

print('=' * 70)
print('EXCHANGE SERVER CONNECTION CHECK')
print('=' * 70)
print()

if offline:
    print('⚠️  WARNING: Device is OFFLINE')
    print('   Cannot check Exchange connection while device is offline')
    print()
else:
    print('✅ Device is ONLINE - Checking Exchange connectivity...')
    print()

# Try to get network/connectivity information
print('📡 Network Connectivity Status:')
print()

# Check if we can get more detailed network info
network_url = f'{CONFIG["base_url"]}/v2/device/{device_id}/network'
response = requests.get(network_url, headers=headers, timeout=30)

if response.status_code == 200:
    network_info = response.json()
    print('   Network details available:')
    print(json.dumps(network_info, indent=2)[:500])
else:
    print(f'   ⚠️  Network details endpoint not available (Status: {response.status_code})')

print()

# Check for Exchange-related information
print('📧 Exchange Server Information:')
print()

# Try to get installed software/services
software_url = f'{CONFIG["base_url"]}/v2/device/{device_id}/software'
response = requests.get(software_url, headers=headers, timeout=30)

if response.status_code == 200:
    software_list = response.json()

    # Look for Outlook/Exchange related software
    exchange_software = []
    for sw in software_list:
        name = sw.get('name', '').lower()
        if 'outlook' in name or 'exchange' in name or 'office' in name:
            exchange_software.append(sw.get('name'))

    if exchange_software:
        print('   ✅ Exchange-related software found:')
        for sw in exchange_software[:10]:
            print(f'      - {sw}')
    else:
        print('   ⚠️  No Exchange/Outlook software detected in inventory')
else:
    print(f'   ℹ️  Software inventory not available (Status: {response.status_code})')

print()

# Summary and recommendations
print('=' * 70)
print('SUMMARY & RECOMMENDATIONS')
print('=' * 70)
print()

if offline:
    print('❌ CRITICAL: Device is OFFLINE')
    print()
    print('   Immediate Actions Required:')
    print('   1. Check if the computer is powered on')
    print('   2. Verify network connectivity (cable/WiFi)')
    print('   3. Check if NinjaRMM agent is running')
    print('   4. Contact user to confirm device status')
    print()
else:
    print('✅ Device Status: ONLINE')
    print()
    print('   Exchange Connection Check:')
    print('   • Device is reachable via NinjaRMM')
    print('   • Network connectivity is functional')
    print()
    print('   To verify Exchange server connection:')
    print('   1. Check Outlook is connected (from user perspective)')
    print('   2. Test email send/receive')
    print('   3. Verify Exchange server reachability:')
    print('      - Check DNS resolution to Exchange server')
    print('      - Verify port 443/80/587 connectivity')
    print('   4. Review Outlook connection status logs')
    print()

print('   Additional Checks Available via Web Interface:')
print(f'   → https://comda.rmmservice.eu/app/devices/{device_id}')
print('   • View real-time device status')
print('   • Check installed software')
print('   • Review event logs')
print('   • Run remote diagnostics')
print()

print('=' * 70)

# Export report
report_data = {
    'device': device_detail,
    'status': 'online' if not offline else 'offline',
    'timestamp': datetime.now().isoformat(),
    'check_type': 'exchange_connectivity'
}

with open('hidushim3_exchange_report.json', 'w') as f:
    json.dump(report_data, f, indent=2)

print()
print('📄 Full report exported to: hidushim3_exchange_report.json')
print()
