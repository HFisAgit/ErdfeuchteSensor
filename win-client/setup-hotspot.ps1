# setup-hotspot.ps1
# Richtet einen WLAN-Hotspot (Hosted Network) fuer den ESP32-Sensor ein.
# Muss als Administrator ausgefuehrt werden!
#
# Verwendung:
#   .\setup-hotspot.ps1
#   .\setup-hotspot.ps1 -SSID "MeinNetz" -Password "GeheimPW"

param(
    [string]$SSID = "ErdfeuchteSensor",
    [string]$Password = "sensor1234"
)

# --- Admin-Check ---
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Bitte dieses Skript als Administrator ausfuehren!"
    Write-Host "Rechtsklick auf PowerShell > 'Als Administrator ausfuehren'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ESP32 Sensor - WLAN Hotspot Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SSID    : $SSID"
Write-Host "  Passwort: $Password"
Write-Host ""

# --- Hosted Network konfigurieren und starten ---
Write-Host "[1/2] Konfiguriere Hosted Network..." -ForegroundColor Yellow
netsh wlan set hostednetwork mode=allow ssid="$SSID" key="$Password" | Out-Null

Write-Host "[2/2] Starte Hosted Network..." -ForegroundColor Yellow
$result = netsh wlan start hostednetwork
Write-Host $result

if ($LASTEXITCODE -ne 0 -and $result -notmatch "started") {
    Write-Host ""
    Write-Host "FEHLER: Hosted Network konnte nicht gestartet werden." -ForegroundColor Red
    Write-Host ""
    Write-Host "Moegliche Ursachen:" -ForegroundColor Yellow
    Write-Host "  - USB-WLAN-Adapter unterstuetzt kein Hosted Network"
    Write-Host "  - Treiber aktualisieren oder anderen Adapter verwenden"
    Write-Host ""
    Write-Host "Alternative: Windows Mobile Hotspot (manuell)" -ForegroundColor Cyan
    Write-Host "  Einstellungen > Netzwerk und Internet > Mobile Hotspot"
    Write-Host "  SSID und Passwort dort manuell eintragen."
    Write-Host "  IP des PCs ist dann ebenfalls 192.168.137.1"
    pause
    exit 1
}

# --- IP-Adresse ermitteln ---
# Windows vergibt dem Hosted-Network-Interface standardmaessig 192.168.137.1
Start-Sleep -Seconds 2
$hostedIp = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like "192.168.137.*" } |
    Select-Object -First 1).IPAddress

if (-not $hostedIp) {
    $hostedIp = "192.168.137.1"
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Hotspot laeuft! IP des PCs: $hostedIp" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Trage folgende Werte in" -ForegroundColor Cyan
Write-Host "  esp32-firmware\include\secrets.h  ein:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  #define WIFI_SSID      `"$SSID`"" -ForegroundColor White
Write-Host "  #define WIFI_PASSWORD  `"$Password`"" -ForegroundColor White
Write-Host "  #define API_ENDPOINT   `"http://${hostedIp}:8080/api/moisture`"" -ForegroundColor White
Write-Host ""
Write-Host "Dann den Receiver starten:" -ForegroundColor Cyan
Write-Host "  python sensor-receiver.py" -ForegroundColor White
Write-Host "  -- oder --" -ForegroundColor Gray
Write-Host "  start-receiver.bat" -ForegroundColor White
Write-Host ""
