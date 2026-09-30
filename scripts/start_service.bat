@echo off
echo Starting HydraulicDataCollectorService...
sc.exe start HydraulicDataCollectorService
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start service. Make sure it is installed and you have Administrator privileges.
) else (
    echo Service started successfully!
)
pause
