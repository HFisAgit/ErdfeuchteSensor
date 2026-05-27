#!/usr/bin/env python3
"""
ErdfeuchteSensor - Windows Test Receiver
=========================================
Empfaengt HTTP-POST-Messwerte vom ESP32 und gibt sie in der Konsole aus.

Erwartet JSON-Payload:  {"moisture": 42.5, "battery": 3.85}
Endpoint:               POST /api/moisture

Starten: python sensor-receiver.py
Beenden: Ctrl+C
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

HOST = "0.0.0.0"
PORT = 8080
ENDPOINT = "/api/moisture"


class SensorHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != ENDPOINT:
            self._send(404, b'{"error":"not found"}')
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._send(400, b'{"error":"invalid json"}')
            print(f"  [FEHLER] Ungueltige Daten: {e}  |  Body: {body!r}")
            return

        ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        moisture  = data.get("moisture", "?")
        battery   = data.get("battery",  "?")
        client_ip = self.client_address[0]

        # --- Ausgabe in der Konsole ---
        print(f"[{ts}]  Feuchte: {moisture:>5}%   Akku: {battery}V   (von {client_ip})")
        sys.stdout.flush()

        self._send(200, b'{"status":"ok"}')

    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Standard-Zugriffslog unterdruecken (saubere Ausgabe)
    def log_message(self, fmt, *args):
        pass


def main():
    print("=" * 50)
    print("  ErdfeuchteSensor - Test Receiver")
    print("=" * 50)
    print(f"  Lausche auf Port {PORT} ...")
    print(f"  Endpoint: http://<PC-IP>:{PORT}{ENDPOINT}")
    print("  Beenden mit Ctrl+C")
    print("-" * 50)
    print(f"  {'Zeitstempel':<20}  {'Feuchte':>8}   {'Akku':>8}")
    print("-" * 50)

    server = HTTPServer((HOST, PORT), SensorHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server beendet.")


if __name__ == "__main__":
    main()
