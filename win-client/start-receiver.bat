@echo off
:: start-receiver.bat
:: Startet den ESP32-Sensor-Receiver. Python muss installiert sein.

echo Starte ErdfeuchteSensor Receiver...
echo.

:: Pruefen ob Python vorhanden ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    echo Bitte Python installieren: https://www.python.org/downloads/
    echo Beim Installieren "Add Python to PATH" aktivieren!
    pause
    exit /b 1
)

python sensor-receiver.py
pause
