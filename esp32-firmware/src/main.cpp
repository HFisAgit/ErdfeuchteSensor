#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/gpio.h>
#include "config.h"

void sendData(float moisture, float batteryVoltage);

void setup()
{
    Serial.begin(115200);
    Serial.println("Hello World");

    // WiFi explizit deaktivieren vor der Messung (ADC2 Ressourcenkonflikt)
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    delay(100);

    // Sensor einschalten
    pinMode(PIN_SENSOR_POWER, OUTPUT);
    digitalWrite(PIN_SENSOR_POWER, HIGH);
    analogSetPinAttenuation(PIN_SENSOR_ADC, ADC_11db);
    delay(SENSOR_WARMUP_MS);

    // Bodenfeuchtigkeit messen (GPIO13 = ADC2_CH4)
    int rawMoisture = analogRead(PIN_SENSOR_ADC);
    Serial.printf("FeuchteRaw: %d\n", rawMoisture);  // debug: roher ADC-Wert (0-4095) ausgeben
    // Kalibrierung: trocken=4095 (0%), nass/Wasser=2150 (100%)
    float moisture = constrain((4095 - rawMoisture) * (100.0 / (4095 - 2150)), 0.0, 100.0);

    // Akkuspannung messen (über Spannungsteiler)
    // int rawBattery = analogRead(PIN_BATTERY_ADC);
    // float batteryVoltage = rawBattery * (3.3 / 4095.0) * BATTERY_DIVIDER_FACTOR;

    // Sensor ausschalten
    digitalWrite(PIN_SENSOR_POWER, LOW);

    // GPIO13 sauber deaktivieren bevor WiFi gestartet wird
    pinMode(PIN_SENSOR_ADC, INPUT);
    gpio_reset_pin((gpio_num_t)PIN_SENSOR_ADC);

    // Serial.printf("Feuchte: %.1f%%, Akku: %.2fV\n", moisture, batteryVoltage);
    Serial.printf("Feuchte: %.1f%%\n", moisture);

    // WiFi verbinden und Daten senden
    sendData(moisture, 0.0);

    // DeepSleep bis zur nächsten vollen Stunde
    uint64_t sleepTime = SLEEP_DURATION_US;
    Serial.printf("Schlafe fuer %llu Sekunden...\n", sleepTime / 1000000ULL);
    esp_deep_sleep(sleepTime);
}

void loop()
{
    // Wird nie erreicht (DeepSleep startet in setup() neu)
}

void sendData(float moisture, float batteryVoltage)
{
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long startAttempt = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < WIFI_TIMEOUT_MS)
    {
        delay(100);
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        HTTPClient http;
        http.begin(API_ENDPOINT);
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"moisture\":" + String(moisture, 1) +
                         ",\"battery\":" + String(batteryVoltage, 2) + "}";

        int httpCode = http.POST(payload);
        Serial.printf("HTTP Response: %d\n", httpCode);
        http.end();
    }
    else
    {
        Serial.println("WiFi Verbindung fehlgeschlagen!");
    }

    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
}
