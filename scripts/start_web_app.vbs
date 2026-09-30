' ==============================================================================
' 3-Station Machine Analytics Web Dashboard Auto-Launcher (VBScript)
' Launches 3StationWebApp.exe completely silent/hidden in background (no console window)
' and opens default browser to http://localhost:5001 (guaranteed single browser window)
' ==============================================================================

Option Explicit

Dim WshShell, FSO, WMI, ProcessList
Dim AppDir, WebExe, IsRunning, BrowserUrl
Dim TempDir, LockFile, ShouldOpenBrowser, FileObj

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get directory where this script is installed or check standard Program Files install
AppDir = FSO.GetParentFolderName(WScript.ScriptFullName)
If Not FSO.FileExists(AppDir & "\3StationWebApp.exe") Then
    If FSO.FileExists("C:\Program Files\3StationMachineCollector\3StationWebApp.exe") Then
        AppDir = "C:\Program Files\3StationMachineCollector"
    End If
End If
WebExe = AppDir & "\3StationWebApp.exe"
BrowserUrl = "http://localhost:5001"

' Fallback check: if running from dev environment where exe doesn't exist yet, run via python
Dim UsePython, PyLauncher
UsePython = False
If Not FSO.FileExists(WebExe) Then
    If FSO.FileExists(AppDir & "\run_web.py") Then
        UsePython = True
        PyLauncher = "python """ & AppDir & "\run_web.py"""
    End If
End If

' 1. Check if 3StationWebApp is already running to avoid duplicate instances
IsRunning = False
On Error Resume Next
Set WMI = GetObject("winmgmts:\\.\root\cimv2")
Set ProcessList = WMI.ExecQuery("SELECT * FROM Win32_Process WHERE Name = '3StationWebApp.exe'")
If ProcessList.Count > 0 Then
    IsRunning = True
End If
On Error GoTo 0

' 2. Launch web server if not already active
If Not IsRunning Then
    WshShell.CurrentDirectory = AppDir
    If UsePython Then
        ' Hidden window style 0 = completely hidden, no black CMD window
        WshShell.Run PyLauncher, 0, False
    ElseIf FSO.FileExists(WebExe) Then
        WshShell.Run """" & WebExe & """", 0, False
    End If
    ' Wait 2 seconds for Flask web server to bind to port 5001
    WScript.Sleep 2000
End If

' 3. Prevent opening duplicate browser windows within 15 seconds (debounce guard)
TempDir = WshShell.ExpandEnvironmentStrings("%TEMP%")
LockFile = TempDir & "\3station_web_open.lock"
ShouldOpenBrowser = True

If FSO.FileExists(LockFile) Then
    On Error Resume Next
    Set FileObj = FSO.GetFile(LockFile)
    ' If opened less than 15 seconds ago, skip opening another duplicate browser tab
    If DateDiff("s", FileObj.DateLastModified, Now) < 15 Then
        ShouldOpenBrowser = False
    End If
    On Error GoTo 0
End If

If ShouldOpenBrowser Then
    On Error Resume Next
    Dim LockStream
    Set LockStream = FSO.CreateTextFile(LockFile, True)
    LockStream.WriteLine CStr(Now)
    LockStream.Close
    On Error GoTo 0

    ' Open Web Dashboard in default browser
    WshShell.Run BrowserUrl, 1, False
End If

Set WshShell = Nothing
Set FSO = Nothing
Set WMI = Nothing
Set ProcessList = Nothing
