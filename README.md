# ErdfeuchteSensor
WLAN-Sensor zur Bodenfeuchte-Messung

---

## 🔧 Hardware Setup

### 🌱 Sensor
- **DFRobot Gravity / AZ-Delivery Bodenfeuchte Sensor Module V1.2**
- Analogausgang: 0–3 V
- Versorgungsspannung: 3,3–5,5 V DC (5 mA)
- Transistor zum Ein-/Ausschalten

### 🧠 MCU
- **ESP32** – z.B. M5Stack M5Stamp C3 DevKit
- Versorgungsspannung: 5,0 V DC (500 mA)

### ⚡ Spannungsversorgung

#### Option A – Akku (USB-Laden)
- 🔋 1x 18650 Li-Ion Akku
- 🔌 Step-Up auf 5 V (MT3608)
- 100–470 µF zwischen 5V und GND
- 🔌 Ladegerät TP4056 (Laden per USB)

#### Option B – Solar (wartungsfrei, Außeneinsatz)
- ☀️ Solarpanel 0,5–1 W / 6 V
- 🔋 LiPo / 18650 (100–500 mAh reichen – Verbrauch ca. 0,07 Wh/Tag)
- 🔌 Solar-Laderegler **CN3791** (MPPT, ideal für kleine Panels)
  - alternativ: **BQ25504** für sehr kleine Panels / wenig Licht
- 🔌 Step-Up auf 5 V (MT3608)
- 100–470 µF zwischen 5V und GND

**Aufbau Solar-Kette:**
```
Solarpanel → CN3791 (MPPT) → LiPo → MT3608 (Step-Up 5V) → ESP32 + Sensor
```

> ⚠️ Ein normaler Elko reicht **nicht** zur Nachtüberbrückung (~160 J nötig, 10 mF Elko liefert nur ~0,1 J).
> Ein Supercap (>10 F) wäre theoretisch möglich, aber Solar + kleiner Akku ist die deutlich bessere Lösung.

### 🏠 Gehäuse
- ?? 3D-Druck ??

---

## 📋 TODO
- [ ] Prüfen, ob der DFRobot-Sensor auch mit 3,3 V betrieben werden kann (weniger Spannungswandler → weniger Verluste)

---

## 💻 Software

### 1. Bodenfeuchte messen
- DFRobot-Sensor per GPIO ein-/ausschalten
- Einmal pro Stunde: Sensor aktivieren → auslesen → deaktivieren
- WLAN einschalten, REST-API aufbauen, Verbindung zum Pi aufbauen, Werte senden, alles ausschalten
- DeepSleep bis zur nächsten vollen Stunde

### 2. Ladezustand messen
- 👉 Über Spannungsteiler an ADC
- → Damit lässt sich erkennen, wann der Akku leer wird
