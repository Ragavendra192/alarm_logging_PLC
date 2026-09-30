@echo off
echo ==========================================================
echo  Uninstalling Hydraulic Machine Data Collector Service
echo ==========================================================
cd /d "%~dp0\.."

echo Stopping service if running...
sc.exe stop HydraulicDataCollectorService >nul 2>&1

echo Removing service...
python windows_service.py remove
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to remove service. Run as Administrator.
) else (
    echo Service removed successfully.
)
pause
