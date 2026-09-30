; ==============================================================================
; Inno Setup 7 Script: 3-Station Machine Data Collector & Analytics Installer
; Fully automated installation for FRESH Windows systems (No Python / No Libs)
; Automatically installs and starts the Windows Service and places VBScript in startup
; ==============================================================================

#define MyAppName "3-Station Machine Data Collector"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Plant Automation"
#define MyAppExeName "3StationCollectorService.exe"
#define MyWebExeName "3StationWebApp.exe"

[Setup]
AppId={{D37E84B1-3E21-4F28-8B41-2A4B830198BC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\3StationMachineCollector
DefaultGroupName={#MyAppName}
OutputDir=..\installer_output
OutputBaseFilename=3StationMachine_Setup_v1.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UsedUserAreasWarning=no
ArchitecturesInstallIn64BitMode=x64compatible

DisableWelcomePage=no
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; All compiled application files and dependencies
Source: "..\dist\3StationPackage\app_files\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".env"

; Install .env only if it does not exist yet (preserves existing custom IP/machine config on updates)
Source: "..\dist\3StationPackage\app_files\.env"; DestDir: "{app}"; Flags: onlyifdoesntexist; Permissions: users-full

; VBScript startup launcher installed to App dir
Source: "..\dist\3StationPackage\app_files\start_web_app.vbs"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\data"; Permissions: users-full

[InstallDelete]
; Clean up any legacy duplicate startup entries from prior installations
Type: files; Name: "{userstartup}\3Station Web Dashboard.lnk"
Type: files; Name: "{userstartup}\start_web_app.vbs"
Type: files; Name: "{commonstartup}\start_web_app.vbs"

[Icons]
; Single Auto-Startup entry for all users on Windows boot
Name: "{commonstartup}\3Station Web Dashboard"; Filename: "wscript.exe"; Parameters: """{app}\start_web_app.vbs"""; WorkingDir: "{app}"

; Desktop shortcut
Name: "{autodesktop}\3-Station Machine Dashboard"; Filename: "wscript.exe"; Parameters: """{app}\start_web_app.vbs"""; WorkingDir: "{app}"


; Start Menu Shortcuts
Name: "{group}\3-Station Machine Dashboard"; Filename: "wscript.exe"; Parameters: """{app}\start_web_app.vbs"""; WorkingDir: "{app}"
Name: "{group}\Edit Configuration (.env)"; Filename: "notepad.exe"; Parameters: """{app}\.env"""
Name: "{group}\View System Logs"; Filename: "explorer.exe"; Parameters: """{app}\logs"""
Name: "{group}\Restart Background Service"; Filename: "cmd.exe"; Parameters: "/c net stop HydraulicDataCollectorService && net start HydraulicDataCollectorService"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
; 0. Grant standard Users full write access to configuration (.env)
Filename: "icacls.exe"; Parameters: """{app}\.env"" /grant *S-1-5-32-545:(M)"; Flags: runhidden; StatusMsg: "Configuring file permissions..."
Filename: "icacls.exe"; Parameters: """{app}"" /grant *S-1-5-32-545:(OI)(CI)M /T /Q"; Flags: runhidden; StatusMsg: "Configuring folder permissions..."

; 1. Install the Windows Service
Filename: "{app}\{#MyAppExeName}"; Parameters: "--startup auto install"; Flags: runhidden; StatusMsg: "Registering Windows Background Service..."

; 2. Configure Service to automatically start on Windows boot
Filename: "sc.exe"; Parameters: "config HydraulicDataCollectorService start= auto"; Flags: runhidden; StatusMsg: "Configuring boot startup..."

; 3. Configure Failure Recovery (Auto-restart service after 5s, 10s, 60s)
Filename: "sc.exe"; Parameters: "failure HydraulicDataCollectorService reset= 86400 actions= restart/5000/restart/10000/restart/60000"; Flags: runhidden; StatusMsg: "Configuring automatic failure recovery..."

; 4. Start the Windows Service immediately
Filename: "net.exe"; Parameters: "start HydraulicDataCollectorService"; Flags: runhidden; StatusMsg: "Starting Data Logging Service..."

; 5. Add Windows Firewall Rule for port 5001 (allows shop-floor tablet/network access)
Filename: "netsh.exe"; Parameters: "advfirewall firewall add rule name=""3Station Web Dashboard"" dir=in action=allow protocol=TCP localport=5001"; Flags: runhidden; StatusMsg: "Configuring Windows Firewall..."


; 6. Launch the Web Application Dashboard in browser on completion
Filename: "wscript.exe"; Parameters: """{app}\start_web_app.vbs"""; Flags: nowait postinstall skipifsilent; Description: "Launch 3-Station Web Analytics Dashboard now"

[UninstallRun]
; 1. Stop and remove the Windows Service
Filename: "net.exe"; Parameters: "stop HydraulicDataCollectorService"; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Parameters: "remove"; Flags: runhidden

; 2. Kill any running web server instance
Filename: "taskkill.exe"; Parameters: "/f /im {#MyWebExeName}"; Flags: runhidden

; 3. Remove Windows Firewall rule
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""3Station Web Dashboard"""; Flags: runhidden

[UninstallDelete]
Type: files; Name: "{userstartup}\3Station Web Dashboard.lnk"
Type: files; Name: "{userstartup}\start_web_app.vbs"
Type: files; Name: "{commonstartup}\3Station Web Dashboard.lnk"
Type: files; Name: "{commonstartup}\start_web_app.vbs"
Type: filesandordirs; Name: "{app}\__pycache__"


[Code]
// Verification of ODBC Driver on install
function InitializeSetup(): Boolean;
var
  OdbcInstalled: Boolean;
begin
  Result := True;
  OdbcInstalled := RegKeyExists(HKLM, 'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 17 for SQL Server') or
                   RegKeyExists(HKLM, 'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server') or
                   RegKeyExists(HKLM, 'SOFTWARE\ODBC\ODBCINST.INI\SQL Server Native Client 11.0');
                   
  if not OdbcInstalled then
  begin
    MsgBox('Notice: Microsoft ODBC Driver for SQL Server was not detected on this machine.' + #13#10 +
           'If SQL Server logging fails, please install "Microsoft ODBC Driver 17 for SQL Server".' + #13#10 +
           'The installer will proceed with installation.', mbInformation, MB_OK);
  end;
end;
