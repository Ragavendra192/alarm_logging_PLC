# PowerShell Service Manager for Hydraulic Machine Data Collector
Param(
    [Parameter(Position=0)]
    [ValidateSet("status", "start", "stop", "restart", "install", "uninstall", "logs")]
    [string]$Action = "status"
)

$ServiceName = "HydraulicDataCollectorService"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectDir = Split-Path -Parent $ScriptDir
$LogFile = Join-Path $ProjectDir "logs\collector.log"

function Check-Service {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "Service '$ServiceName': $($service.Status) (StartType: $($service.StartType))" -ForegroundColor Cyan
    } else {
        Write-Host "Service '$ServiceName' is NOT installed." -ForegroundColor Yellow
    }
    return $service
}

switch ($Action) {
    "status" {
        Check-Service
    }
    "start" {
        Write-Host "Starting $ServiceName..." -ForegroundColor Green
        Start-Service -Name $ServiceName
        Check-Service
    }
    "stop" {
        Write-Host "Stopping $ServiceName..." -ForegroundColor Yellow
        Stop-Service -Name $ServiceName
        Check-Service
    }
    "restart" {
        Write-Host "Restarting $ServiceName..." -ForegroundColor Cyan
        Restart-Service -Name $ServiceName
        Check-Service
    }
    "install" {
        Write-Host "Installing $ServiceName..." -ForegroundColor Green
        Set-Location $ProjectDir
        python windows_service.py --startup auto install
        sc.exe config $ServiceName start= auto
        sc.exe failure $ServiceName reset= 86400 actions= restart/5000/restart/10000/restart/60000
        Check-Service
    }
    "uninstall" {
        Write-Host "Uninstalling $ServiceName..." -ForegroundColor Yellow
        Set-Location $ProjectDir
        Stop-Service -Name $ServiceName -ErrorAction SilentlyContinue
        python windows_service.py remove
        Check-Service
    }
    "logs" {
        if (Test-Path $LogFile) {
            Write-Host "Tailing logs from $LogFile (Ctrl+C to exit)..." -ForegroundColor Cyan
            Get-Content -Path $LogFile -Tail 30 -Wait
        } else {
            Write-Host "Log file $LogFile not found." -ForegroundColor Red
        }
    }
}
