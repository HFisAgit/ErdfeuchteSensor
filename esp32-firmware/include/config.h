#pragma once

// Sensible Daten (WiFi, API-URL) sind in secrets.h ausgelagert.
// Diese Datei ist NICHT im Git-Repo enthalten.
// Kopiere secrets.h.example -> secrets.h und trage deine Daten ein.
#include "secrets.h"

// ===== WiFi Konfiguration =====
#define WIFI_TIMEOUT_MS 10000

// ===== Pin-Belegung =====
#define PIN_SENSOR_POWER 2 // GPIO zum Schalten des Sensors (Transistor)
#define PIN_SENSOR_ADC 0   // ADC-Eingang Bodenfeuchtesensor
#define PIN_BATTERY_ADC 1  // ADC-Eingang Akkuspannung (Spannungsteiler)

// ===== Sensor Konfiguration =====
#define SENSOR_WARMUP_MS 500 // Aufwärmzeit Sensor nach Einschalten (ms)

// ===== Batterie Spannungsteiler =====
// Faktor = (R1 + R2) / R2  (z.B. 100k + 100k -> Faktor 2.0)
#define BATTERY_DIVIDER_FACTOR 2.0

// ===== Sleep Konfiguration =====
#define SLEEP_DURATION_US 3600000000ULL // 1 Stunde in Mikrosekunden
