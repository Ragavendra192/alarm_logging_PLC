# 3-Station Hydraulic Machine Data Collector & Fault Analytics System

An industrial-grade telemetry and alarm logging system for 3-Station Hydraulic Press machines running Siemens S7 PLCs. Automatically captures PLC Boolean tags, machine pressures/positions, and fault alarms into Microsoft SQL Server, accompanied by a local web-based analytics dashboard and Windows background service.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Siemens S7 PLC (DB1000/   |
                      |   1001/101 & PE/PA IO)      |
                      +--------------+--------------+
                                     |
                       Snap7 Protocol (TCP/IP)
                                     v
+-------------------------------------------------------------------------+
| Windows Service: HydraulicDataCollectorService (windows_service.py)     |
|  - Real-time 100ms tag acquisition & edge buffer                        |
|  - Active alarm bit-level scanner (data/alarm_mappings.sqlite)          |
|  - Automatic reconnect & fault-only database throttling                 |
+------------------------------------+------------------------------------+
                                     |
                          ODBC Connection (pyodbc)
                                     v
                      +-----------------------------+
                      |    Microsoft SQL Server     |
                      |   (HydraulicMachineDB)      |
                      +--------------+--------------+
                                     |
                          ODBC Query & Aggregation
                                     v
+-------------------------------------------------------------------------+
| Web Analytics Dashboard: Flask Application (run_web.py : Port 5001)     |
|  - Live KPIs: Total Alarms, Shift Alarms, Station Breakdown             |
|  - Pareto distribution & hourly alarm timeline                          |
|  - Drill-down machine IO snapshot at the exact instant of alarm         |
|  - CSV Report Export & live PLC / SQL health monitor                    |
+-------------------------------------------------------------------------+
```

---

## Repository Structure

```
.
├── app/
│   ├── database/              # SQL Server repos & connection pooling
│   │   ├── alarm_analytics_repo.py
│   │   ├── db_connection.py
│   │   ├── db_initializer.py
│   │   └── io_repository.py
│   ├── plc/                   # Siemens S7 PLC client, tags & alarm scanner
│   │   ├── alarm_mapping.py
│   │   ├── alarm_monitor.py
│   │   ├── alarm_scanner.py
│   │   ├── client.py
│   │   ├── plc_tags.py
│   │   └── press_actual.py
│   ├── web/                   # Flask server, REST APIs, HTML/JS dashboard
│   │   ├── static/
│   │   ├── templates/
│   │   └── server.py
│   ├── workers/               # Asynchronous acquisition & logging threads
│   │   ├── data_log_worker.py
│   │   └── plc_worker.py
│   ├── config.py              # Configuration manager (.env parsing)
│   ├── logger.py              # Rotating file and console logger
│   └── main.py                # Standalone console entrypoint
├── data/
│   └── alarm_mappings.sqlite  # SQLite database storing bit-to-alarm definitions
├── installer/
│   └── setup.iss              # Inno Setup 6/7 compiler script
├── scripts/
│   ├── build_standalone.py    # PyInstaller multi-target build script
│   ├── install_service.bat    # Windows Service registration helper
│   ├── start_service.bat      # Windows Service start helper
│   ├── stop_service.bat       # Windows Service stop helper
│   └── uninstall_service.bat  # Windows Service removal helper
├── tests/                     # Unit test suites
│   ├── test_alarm_events.py
│   ├── test_sql_io.py
│   └── test_web_analytics.py
├── .env.example               # Configuration template
├── 3StationCollectorService.spec # PyInstaller spec for Windows Service
├── 3StationWebApp.spec        # PyInstaller spec for Web Application
├── build_installer.bat        # Automated batch build pipeline (PyInstaller + ISCC)
├── requirements.txt           # Python package dependencies
├── run.py                     # CLI launcher
├── run_web.py                 # Web app standalone launcher
└── windows_service.py         # Windows Service Controller entrypoint
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10+ (64-bit recommended)
- Siemens S7 PLC connected via Ethernet (`Snap7.dll` included or in PATH)
- Microsoft SQL Server with ODBC Driver 17 or 18 installed

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and adjust the settings to match your machine setup:
```env
# Machine Identification
MACHINE_ID=3_station
OPERATOR_NAME=Operator_1

# Siemens PLC Configuration
PLC_IP=192.168.40.11
PLC_RACK=0
PLC_SLOT=1
PLC_DB_NUMBER=1000
PLC_POLL_INTERVAL=0.1

# SQL Server Configuration
SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=HydraulicMachineDB
SQL_TABLE_NAME=MachineDataLog
SQL_TRUSTED_CONNECTION=true

# Web Dashboard Port
WEB_PORT=5001
```

---

## Running the Application

### Option A: Development Mode

- **Start Data Collector in Terminal:**
  ```bash
  python run.py
  ```

- **Start Web Analytics Dashboard:**
  ```bash
  python run_web.py
  ```
  Open your browser to `http://localhost:5001`.

### Option B: Windows Service (Production)

- **Install and Start Service:**
  ```cmd
  scripts\install_service.bat
  scripts\start_service.bat
  ```

- **Stop and Uninstall Service:**
  ```cmd
  scripts\stop_service.bat
  scripts\uninstall_service.bat
  ```

---

## Building Standalone Installer

To build a zero-dependency Windows setup executable (`.exe`) using PyInstaller and Inno Setup:
```cmd
build_installer.bat
```
The output installer will be generated in `installer_output/3StationMachine_Setup_v1.0.exe`.
