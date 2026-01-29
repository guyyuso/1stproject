# Disable Bluetooth on Windows
# This script can be run locally on IT-GREGORYR or via NinjaRMM web interface

Write-Host "========================================="
Write-Host "Disabling Bluetooth on Windows"
Write-Host "========================================="
Write-Host ""

# Method 1: Stop and Disable Bluetooth Support Service
Write-Host "[1/3] Stopping Bluetooth Support Service..."
$service = Get-Service -Name "bthserv" -ErrorAction SilentlyContinue
if ($service) {
    try {
        Stop-Service -Name "bthserv" -Force -ErrorAction Stop
        Write-Host "  ✓ Service stopped"

        Set-Service -Name "bthserv" -StartupType Disabled -ErrorAction Stop
        Write-Host "  ✓ Service disabled (startup type: Disabled)"
    } catch {
        Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "  ⚠ Bluetooth Support Service not found"
}

Write-Host ""

# Method 2: Disable Bluetooth Radios via Device Manager
Write-Host "[2/3] Disabling Bluetooth radios in Device Manager..."
$bluetoothRadios = Get-PnpDevice | Where-Object {
    ($_.Class -eq "Bluetooth") -or
    ($_.FriendlyName -like "*Bluetooth*") -or
    ($_.Description -like "*Bluetooth*")
} | Where-Object {$_.Status -eq "OK"}

if ($bluetoothRadios) {
    $count = 0
    foreach ($radio in $bluetoothRadios) {
        try {
            Write-Host "  Disabling: $($radio.FriendlyName)"
            Disable-PnpDevice -InstanceId $radio.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Host "    ✓ Disabled successfully" -ForegroundColor Green
            $count++
        } catch {
            Write-Host "    ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "  ✓ Disabled $count Bluetooth radio(s)"
} else {
    Write-Host "  ⚠ No active Bluetooth radios found"
}

Write-Host ""

# Method 3: Disable via Registry (persistent disable)
Write-Host "[3/3] Updating registry to prevent Bluetooth auto-start..."
try {
    # Disable BTHPORT service via registry
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Services\BTHPORT"
    if (Test-Path $regPath) {
        Set-ItemProperty -Path $regPath -Name "Start" -Value 4 -ErrorAction Stop
        Write-Host "  ✓ BTHPORT registry updated (Start=4, Disabled)"
    }

    # Disable BthServ service via registry
    $regPath2 = "HKLM:\SYSTEM\CurrentControlSet\Services\bthserv"
    if (Test-Path $regPath2) {
        Set-ItemProperty -Path $regPath2 -Name "Start" -Value 4 -ErrorAction Stop
        Write-Host "  ✓ BthServ registry updated (Start=4, Disabled)"
    }

    Write-Host "  ✓ Registry keys updated successfully"
} catch {
    Write-Host "  ✗ Failed to update registry: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================="
Write-Host "Bluetooth Disable Complete!"
Write-Host "========================================="
Write-Host ""
Write-Host "Summary:"
Write-Host "  - Bluetooth Support Service: Stopped and Disabled"
Write-Host "  - Bluetooth Radios: Disabled in Device Manager"
Write-Host "  - Registry Keys: Updated to prevent auto-start"
Write-Host ""
Write-Host "⚠ IMPORTANT: A system restart is recommended"
Write-Host "   for all changes to take full effect."
Write-Host ""

# Optional: Ask user if they want to restart now
$restart = Read-Host "Restart computer now? (y/n)"
if ($restart -eq 'y' -or $restart -eq 'Y') {
    Write-Host ""
    Write-Host "Restarting computer in 10 seconds..."
    Write-Host "Press Ctrl+C to cancel"
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host ""
    Write-Host "Please restart manually when convenient."
}
