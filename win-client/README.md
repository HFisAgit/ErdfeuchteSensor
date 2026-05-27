# Windows Test-Client für ErdfeuchteSensor

Empfängt Messwerte vom ESP32 über ein WLAN-Hotspot auf dem Windows-PC.

## Voraussetzungen
- Windows 10/11
- Python 3.x ([python.org](https://www.python.org/downloads/)) – beim Installieren **"Add Python to PATH"** aktivieren
- USB-WLAN-Adapter, der **Hosted Network** unterstützt (die meisten tun das)

---

## Schritt-für-Schritt

### 1. Hotspot einrichten (einmalig)

PowerShell **als Administrator** öffnen und ausführen:

```powershell
.\setup-hotspot.ps1
```

Das Skript gibt am Ende die genauen Werte aus, die du in `secrets.h` eintragen musst, z.B.:

```cpp
#define WIFI_SSID      "ErdfeuchteSensor"
#define WIFI_PASSWORD  "sensor1234"
#define API_ENDPOINT   "http://192.168.137.1:8080/api/moisture"
```

> **Hinweis:** Der PC bekommt im Hosted Network immer die IP `192.168.137.1`.

### 2. ESP32 flashen

`esp32-firmware\include\secrets.h` mit den Werten aus Schritt 1 anlegen/aktualisieren, dann flashen.

### 3. Receiver starten

```cmd
start-receiver.bat
```

oder direkt:

```cmd
python sensor-receiver.py
```

### 4. Konsolenausgabe

```
==================================================
  ErdfeuchteSensor - Test Receiver
==================================================
  Lausche auf Port 8080 ...
  Endpoint: http://<PC-IP>:8080/api/moisture
  Beenden mit Ctrl+C
--------------------------------------------------
  Zeitstempel           Feuchte      Akku
--------------------------------------------------
[2026-05-27 14:32:01]  Feuchte:  42.5%   Akku: 3.85V   (von 192.168.137.42)
```

---

## Windows Firewall

Beim ersten Start fragt Windows, ob Python den Port öffnen darf → **"Zugriff zulassen"** klicken.

Falls der ESP32 trotzdem keine Verbindung bekommt, Firewall-Regel manuell anlegen:

```powershell
# Als Administrator:
New-NetFirewallRule -DisplayName "ESP32 Sensor Receiver" `
    -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

---

## Hotspot beenden

```powershell
netsh wlan stop hostednetwork
```
