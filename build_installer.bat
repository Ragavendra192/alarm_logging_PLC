@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo   3-Station Machine Deployment Builder (PyInstaller + Inno Setup)
echo ==============================================================================
cd /d "%~dp0"

REM 1. Find Inno Setup Compiler (ISCC.exe)
set "ISCC_PATH="
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 7\ISCC.exe" (
    set "ISCC_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 7\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    for /f "delims=" %%i in ('where iscc.exe 2^>nul') do set "ISCC_PATH=%%i"
)

if not defined ISCC_PATH (
    echo [ERROR] Inno Setup compiler (ISCC.exe) not found!
    echo Please ensure Inno Setup is installed.
    pause
    exit /b 1
)

echo [INFO] Found Inno Setup Compiler: "!ISCC_PATH!"

REM 2. Run PyInstaller Standalone Package Builder
echo.
echo [STEP 1/2] Building Standalone PyInstaller Package...
python scripts\build_standalone.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

REM 3. Compile Inno Setup Installer
echo.
echo [STEP 2/2] Compiling Inno Setup Installer...
"!ISCC_PATH!" installer\setup.iss
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Inno Setup compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [SUCCESS] INSTALLER BUILT SUCCESSFULLY!
echo Installer File: installer_output\3StationMachine_Setup_v1.0.exe
echo.
echo TO DEPLOY ON FRESH MACHINE:
echo 1. Copy 'installer_output\3StationMachine_Setup_v1.0.exe' to the machine.
echo 2. Right-click and select "Run as Administrator".
echo 3. The installer will automatically:
echo    - Install all files to Program Files (no Python/libs required).
echo    - Register and start 'HydraulicDataCollectorService' on boot with auto-recovery.
echo    - Place 'start_web_app.vbs' in shell:startup for silent background auto-boot.
echo    - Open port 5001 in Windows Firewall.
echo    - Launch the live Web Analytics dashboard in the browser!

echo ==============================================================================
pause
