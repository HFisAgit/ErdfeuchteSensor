# ErdfeuchteSensor
WLAN Sensor zur Bodenfeuchte Messung

Hardware setup

Sensor:
DFRobot Gravity 
Analog Ausgang  0 - 3V
Versorgungsspannung 3,3V - 5.5V DC (5mA)
Transistor zum ein/aus - Schalten

MCU
ESP32
z.B. M5Stack M5Stamp C3 DevKit
Versorgungsspannung 5.0V DC (500mA)

Spannungsversorgung:
🔋 1x 18650 Li-Ion Akku
🔌 Step-Up auf 5 V (MT3608 )
100–470 µF zwischen 5V und GND
+ Ladegerät TP4056 (Laden per USB)

Gehäuse:
?? 3D Druck ??

TODO:
Prüfen, ob man den DFRobot auch mit 3,3V betreiben kann. (weniger Spannungswandler - weniger Verluste)

Software:
1. Bodenfeuchte messen
DFRobot- Sensor per GPIO ein/aus schalten
Einmal pro Stunde Sensor aktivieren, Auslesen, wieder deaktivieren.
WLAN Einschalten, RestAPI Interface aufbauen, Verbindung zum Pi Aufbauen, Werte Senden, und wieder alles ausschalten
DeepSleep bis zur nächsten vollen Stunde.

2. Ladezustand messen
👉 über Spannungsteiler an ADC
→ dann weißt du, wann Akku leer wird
