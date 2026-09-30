@echo off
echo ==========================================================
echo  Installing Hydraulic Machine Data Collector Service
echo ==========================================================
cd /d "%~dp0\.."

REM 1. Install service via python with auto-startup
python windows_service.py --startup auto install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install service. Run this script as Administrator.
    pause
    exit /b %ERRORLEVEL%
)

REM 2. Configure Service to Auto Start on Windows boot
echo Configuring service to auto-start...
sc.exe config HydraulicDataCollectorService start= auto

REM 3. Configure Failure Recovery (Auto-Restart after 5s, 10s, 60s)
echo Configuring automatic failure recovery...
sc.exe failure HydraulicDataCollectorService reset= 86400 actions= restart/5000/restart/10000/restart/60000

echo.
echo Service installed successfully!
echo To start the service now, run: scripts\start_service.bat
pause
