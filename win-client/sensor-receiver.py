#!/usr/bin/env python3
"""
ErdfeuchteSensor - Windows Web Receiver
=========================================
Empfaengt HTTP-POST-Messwerte vom ESP32 und zeigt sie im Browser als Dashboard an.

Erwartet JSON-Payload:  {"moisture": 42.5, "battery": 3.85}
Endpoint:               POST /api/moisture
Dashboard:              http://localhost:8080/

Starten: python sensor-receiver.py
Beenden: Ctrl+C

Voraussetzung: pip install flask
"""

import sys
from collections import deque
from datetime import datetime

from flask import Flask, jsonify, render_template_string, request

HOST = "0.0.0.0"
PORT = 8080
MAX_MEASUREMENTS = 500

app = Flask(__name__)
measurements = deque(maxlen=MAX_MEASUREMENTS)

# ---------------------------------------------------------------------------
# HTML-Dashboard
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ErdfeuchteSensor – Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: "Segoe UI", Arial, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 24px;
    }

    h1 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #7dd3fc;
      margin-bottom: 24px;
      letter-spacing: 0.02em;
    }

    .cards {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 28px;
    }

    .card {
      background: #1e293b;
      border-radius: 12px;
      padding: 20px 28px;
      min-width: 160px;
      flex: 1;
    }

    .card-label {
      font-size: 0.78rem;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }

    .card-value {
      font-size: 2.4rem;
      font-weight: 700;
      line-height: 1;
    }

    .card-unit {
      font-size: 1rem;
      color: #94a3b8;
      margin-left: 4px;
    }

    #moistureValue { color: #38bdf8; }
    #batteryValue  { color: #4ade80; }

    .chart-wrapper {
      background: #1e293b;
      border-radius: 12px;
      padding: 20px;
      position: relative;
      height: 340px;
    }

    .footer {
      margin-top: 14px;
      font-size: 0.78rem;
      color: #475569;
      text-align: right;
    }

    #statusDot {
      display: inline-block;
      width: 8px; height: 8px;
      border-radius: 50%;
      background: #4ade80;
      margin-right: 6px;
      vertical-align: middle;
    }
    #statusDot.stale { background: #f87171; }
  </style>
</head>
<body>
  <h1>&#127807; ErdfeuchteSensor – Dashboard</h1>

  <div class="cards">
    <div class="card">
      <div class="card-label">Bodenfeuchte</div>
      <div class="card-value">
        <span id="moistureValue">–</span><span class="card-unit">%</span>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Akkuspannung</div>
      <div class="card-value">
        <span id="batteryValue">–</span><span class="card-unit">V</span>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Messungen gesamt</div>
      <div class="card-value" id="countValue" style="color:#a78bfa;">–</div>
    </div>
    <div class="card">
      <div class="card-label">Letzte Messung</div>
      <div class="card-value" id="lastTs" style="font-size:1rem; color:#e2e8f0; margin-top:8px;">–</div>
    </div>
  </div>

  <div class="chart-wrapper">
    <canvas id="chart"></canvas>
  </div>

  <div class="footer">
    <span id="statusDot"></span>
    <span id="refreshInfo">Warte auf Daten …</span>
  </div>

  <script>
    const ctx = document.getElementById("chart").getContext("2d");

    const chart = new Chart(ctx, {
      type: "line",
      data: {
        datasets: [
          {
            label: "Bodenfeuchte (%)",
            data: [],
            borderColor: "#38bdf8",
            backgroundColor: "rgba(56,189,248,0.10)",
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            fill: true,
            yAxisID: "yMoisture",
          },
          {
            label: "Akku (V)",
            data: [],
            borderColor: "#4ade80",
            backgroundColor: "rgba(74,222,128,0.06)",
            borderWidth: 2,
            pointRadius: 2,
            tension: 0.3,
            fill: false,
            yAxisID: "yBattery",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: {
            type: "time",
            time: { tooltipFormat: "HH:mm:ss", displayFormats: { second: "HH:mm:ss", minute: "HH:mm" } },
            ticks: { color: "#94a3b8", maxTicksLimit: 10 },
            grid:  { color: "#1e293b" },
          },
          yMoisture: {
            position: "left",
            min: 0, max: 100,
            ticks: { color: "#38bdf8", callback: v => v + " %" },
            grid:  { color: "#334155" },
            title: { display: true, text: "Feuchte (%)", color: "#38bdf8" },
          },
          yBattery: {
            position: "right",
            min: 3.0, max: 4.2,
            ticks: { color: "#4ade80", callback: v => v.toFixed(2) + " V" },
            grid:  { drawOnChartArea: false },
            title: { display: true, text: "Akku (V)", color: "#4ade80" },
          },
        },
        plugins: {
          legend: { labels: { color: "#e2e8f0" } },
        },
      },
    });

    let lastCount = 0;

    async function refresh() {
      try {
        const resp = await fetch("/api/data");
        const data = await resp.json();

        if (data.length === 0) return;

        // Nur neu laden wenn sich etwas geaendert hat
        if (data.length !== lastCount) {
          lastCount = data.length;

          chart.data.datasets[0].data = data.map(d => ({ x: d.ts, y: d.moisture }));
          chart.data.datasets[1].data = data.map(d => ({ x: d.ts, y: d.battery }));
          chart.update("none");

          const latest = data[data.length - 1];
          document.getElementById("moistureValue").textContent = latest.moisture.toFixed(1);
          document.getElementById("batteryValue").textContent  = latest.battery.toFixed(2);
          document.getElementById("countValue").textContent    = data.length;
          document.getElementById("lastTs").textContent        = new Date(latest.ts).toLocaleTimeString("de-DE");
        }

        const dot = document.getElementById("statusDot");
        dot.classList.remove("stale");
        document.getElementById("refreshInfo").textContent =
          "Aktualisiert: " + new Date().toLocaleTimeString("de-DE");
      } catch (e) {
        document.getElementById("statusDot").classList.add("stale");
        document.getElementById("refreshInfo").textContent = "Verbindungsfehler";
      }
    }

    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# API-Endpunkte
# ---------------------------------------------------------------------------

@app.route("/api/moisture", methods=["POST"])
def receive():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="invalid json"), 400

    if "moisture" not in data or "battery" not in data:
        return jsonify(error="missing fields"), 400

    entry = {
        "ts":       datetime.now().isoformat(),
        "moisture": float(data["moisture"]),
        "battery":  float(data["battery"]),
    }
    measurements.append(entry)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}]  Feuchte: {entry['moisture']:>5.1f}%   Akku: {entry['battery']:.2f}V")
    sys.stdout.flush()

    return jsonify(status="ok")


@app.route("/api/data")
def get_data():
    return jsonify(list(measurements))


@app.route("/")
def dashboard():
    return render_template_string(HTML)


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("  ErdfeuchteSensor - Web Dashboard")
    print("=" * 55)
    print(f"  Dashboard:  http://localhost:{PORT}/")
    print(f"  Endpoint:   http://<PC-IP>:{PORT}/api/moisture")
    print("  Beenden mit Ctrl+C")
    print("-" * 55)
    app.run(host=HOST, port=PORT, debug=False)
