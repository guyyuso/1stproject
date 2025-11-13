#!/usr/bin/env python3

import requests
import json
from datetime import datetime

CONFIG = {
    'client_id': 'H9E-VrYBPxfV1_zf17IExUgs_o4',
    'client_secret': 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
    'base_url': 'https://comda.rmmservice.eu',
}

DEVICE_ID = 537

# Get token
token_url = f'{CONFIG["base_url"]}/ws/oauth/token'
payload = {
    'grant_type': 'client_credentials',
    'client_id': CONFIG['client_id'],
    'client_secret': CONFIG['client_secret'],
    'scope': 'monitoring management'
}
response = requests.post(token_url, data=payload, timeout=30)
token = response.json().get('access_token')

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print('╔════════════════════════════════════════════════════════════════╗')
print('║          HIDUSH3 - Exchange Server Connection Report           ║')
print('╚════════════════════════════════════════════════════════════════╝')
print()

# Get device details
device_url = f'{CONFIG["base_url"]}/v2/device/{DEVICE_ID}'
response = requests.get(device_url, headers=headers, timeout=30)

device = response.json()

print('=' * 70)
print('DEVICE INFORMATION')
print('=' * 70)
print()

print(f'System Name:      {device.get("systemName", "N/A")}')
print(f'DNS Name:         {device.get("dnsName", "N/A")}')
print(f'Device ID:        {device.get("id")}')
print(f'Organization ID:  {device.get("organizationId", "N/A")}')
print(f'Location ID:      {device.get("locationId", "N/A")}')
print(f'Node Class:       {device.get("nodeClass", "N/A")}')
print()

# Status
offline = device.get('offline', True)
status_icon = "🟢 ONLINE" if not offline else "🔴 OFFLINE"
print(f'Status:           {status_icon}')

if device.get('lastContact'):
    try:
        last_contact = datetime.fromtimestamp(device.get('lastContact'))
        print(f'Last Contact:     {last_contact.strftime("%Y-%m-%d %H:%M:%S")}')
    except:
        print(f'Last Contact:     {device.get("lastContact")}')

print()

# OS Information
os_info = device.get('os', {})
if isinstance(os_info, dict):
    print(f'Operating System: {os_info.get("name", "N/A")}')
print()

# Network Information
print('Network Information:')
public_ip = device.get('publicIP', 'N/A')
print(f'  Public IP:      {public_ip}')

ip_addresses = device.get('ipAddresses', [])
if ip_addresses:
    print(f'  IP Addresses:   {", ".join(ip_addresses)}')

print()

print('=' * 70)
print('EXCHANGE SERVER CONNECTION STATUS')
print('=' * 70)
print()

if offline:
    print('❌ CRITICAL: Device is OFFLINE')
    print()
    print('   Cannot verify Exchange connection while device is offline.')
    print()
    if device.get('lastContact'):
        try:
            last_seen = datetime.fromtimestamp(device.get('lastContact')).strftime("%Y-%m-%d %H:%M:%S")
            print(f'   Last seen: {last_seen}')
        except:
            pass
    print()
    print('   Immediate Actions Required:')
    print('   1. ⚡ Verify device is powered on')
    print('   2. 🔌 Check network cable/WiFi connection')
    print('   3. 🖥️  Check NinjaRMM agent is running')
    print('   4. 👤 Contact user to confirm device status')
else:
    print('✅ Device Status: ONLINE')
    print()
    print('   Network connectivity is functional.')
    print()
    print('   Exchange Connection Verification:')
    print('   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print()
    print('   1. 📧 Outlook Connection:')
    print('      • Check if Outlook is running')
    print('      • Verify "Connected to Microsoft Exchange" status')
    print()
    print('   2. 🔍 DNS & Network:')
    print('      • Verify Exchange server DNS resolves')
    print('      • Test ports 443 (HTTPS) and 587 (SMTP)')
    print()
    print('   3. 🔐 Authentication:')
    print('      • Verify user credentials')
    print('      • Check autodiscover')
    print()

print('=' * 70)
print('RECOMMENDATIONS')
print('=' * 70)
print()

if offline:
    print('🔴 PRIORITY: Restore device connectivity first')
else:
    print('✅ Device is reachable')
    print()
    print('   To check Exchange connection:')
    print(f'   → https://comda.rmmservice.eu/app/devices/{DEVICE_ID}')
    print()
    print('   Ask user to:')
    print('      • Open Outlook > File > Account Settings')
    print('      • Click "Test Account Settings"')
    print('      • Send/receive test email')

print()
print('=' * 70)

# Save report
report = {
    'device_name': device.get('systemName'),
    'device_id': DEVICE_ID,
    'status': 'online' if not offline else 'offline',
    'dns_name': device.get('dnsName'),
    'public_ip': device.get('publicIP'),
    'last_contact': device.get('lastContact'),
    'organization_id': device.get('organizationId'),
    'timestamp': datetime.now().isoformat()
}

with open('hidush3_exchange_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print()
print('📄 Report saved to: hidush3_exchange_report.json')
