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

:: Pruefen ob Flask installiert ist
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask wird installiert...
    pip install flask
)

echo Dashboard oeffnet sich unter: http://localhost:8080/
echo.
python sensor-receiver.py
pause
