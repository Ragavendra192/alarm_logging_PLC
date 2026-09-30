"""
Flask Web Application Server for Fault & Alarm Analytics.

Serves the minimal, clean, industrial analytics web page and REST APIs:
- GET /: Dashboard interface
- GET /api/alarms: Filtered & paginated alarm log entries
- GET /api/alarms/stats: Summary KPIs and distribution metrics
- GET /api/alarms/<id>: Drill-down machine snapshot
- GET /api/alarms/export: CSV download
- GET /api/health: Live connection status
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, Response, jsonify, render_template, request

from app.config import Config, get_current_swift
from app.database.alarm_analytics_repo import (
    export_alarm_csv,
    get_active_alarm_logs,
    get_alarm_detail,
    get_alarm_logs,
    get_alarm_stats,
    get_latest_machine_io,
)
from app.database.db_connection import test_sql_connection

logger = logging.getLogger("PLCDataCollector.Web")

def _resolve_asset_dirs():
    """Find templates and static directories whether running in dev or frozen."""
    candidates = []
    if getattr(sys, "frozen", False):
        # When packaged with PyInstaller:
        candidates.append(Path(sys.executable).resolve().parent)
        candidates.append(Path(sys.executable).resolve().parent / "_internal")

    # Relative to this file
    this_dir = Path(__file__).resolve().parent
    candidates.append(this_dir)
    candidates.append(this_dir.parent.parent)

    tpl_path = None
    st_path = None

    for c in candidates:
        t = c / "app" / "web" / "templates"
        if not t.is_dir():
            t = c / "templates"
        if t.is_dir() and (t / "index.html").is_file():
            tpl_path = str(t)
            break

    for c in candidates:
        s = c / "app" / "web" / "static"
        if not s.is_dir():
            s = c / "static"
        if s.is_dir():
            st_path = str(s)
            break

    if not tpl_path:
        tpl_path = str(this_dir / "templates")
    if not st_path:
        st_path = str(this_dir / "static")

    return tpl_path, st_path


template_dir, static_dir = _resolve_asset_dirs()

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



@app.route("/")
def index():
    """Render the fault & alarm analytics dashboard."""
    return render_template(
        "index.html",
        machine_id=Config.MACHINE_ID,
        sql_server=Config.SQL_SERVER,
        sql_database=Config.SQL_DATABASE
    )


@app.route("/api/alarms")
def api_alarms():
    """Retrieve paginated and filtered historical alarm records."""
    try:
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        shift = request.args.get("shift") or None
        station = request.args.get("station") or None
        search = request.args.get("search") or None
        table = request.args.get("table", "AlarmResponse")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        records, total = get_alarm_logs(
            date_from=date_from,
            date_to=date_to,
            shift=shift,
            station=station,
            search=search,
            source_table=table,
            limit=min(limit, 500),
            offset=offset
        )

        return jsonify({
            "success": True,
            "total": total,
            "offset": offset,
            "limit": limit,
            "records": records
        })
    except Exception as e:
        logger.error(f"Error in api_alarms: {e}")
        return jsonify({
            "success": True,
            "total": 0,
            "offset": 0,
            "limit": 50,
            "records": []
        })


@app.route("/api/alarms/active")
def api_active_alarms():
    """Retrieve currently active un-cleared alarms."""
    try:
        machine_id = request.args.get("machine_id") or None
        records = get_active_alarm_logs(machine_number=machine_id)
        return jsonify({
            "success": True,
            "total": len(records),
            "records": records
        })
    except Exception as e:
        logger.error(f"Error in api_active_alarms: {e}")
        return jsonify({
            "success": True,
            "total": 0,
            "records": []
        })


@app.route("/api/alarms/stats")
def api_stats():
    """Retrieve summary analytics and KPI metrics."""
    try:
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        shift = request.args.get("shift") or None

        stats = get_alarm_stats(
            date_from=date_from,
            date_to=date_to,
            shift=shift
        )

        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error in api_stats: {e}")
        return jsonify({
            "success": True,
            "stats": {
                "total_alarms": 0,
                "today_alarms": 0,
                "current_shift_alarms": 0,
                "current_shift": Config.SWIFT or get_current_swift(),
                "top_station": "None",
                "station_distribution": {"Press 1": 0, "Press 2": 0, "Press 3": 0, "Drive / MPCB": 0, "Common": 0},
                "shift_distribution": {"Shift 1": 0, "Shift 2": 0, "Shift 3": 0},
                "top_alarms": [],
                "timeline": []
            }
        })


@app.route("/api/alarms/<int:alarm_id>")
def api_alarm_detail(alarm_id: int):
    """Retrieve full freeze-frame snapshot details for an alarm event."""
    try:
        table = request.args.get("table", "AlarmResponse")
        detail = get_alarm_detail(alarm_id, source_table=table)
        if not detail:
            return jsonify({"success": False, "error": "Alarm record not found"}), 404

        return jsonify({
            "success": True,
            "detail": detail
        })
    except Exception as e:
        logger.error(f"Error in api_alarm_detail: {e}")
        return jsonify({"success": False, "error": f"Error retrieving alarm detail: {e}"}), 500


@app.route("/api/io/latest")
def api_io_latest():
    """Retrieve the latest complete 292 I/O status snapshot."""
    try:
        data = get_latest_machine_io()
        if not data:
            return jsonify({"success": False, "error": "No I/O records found or SQL Server offline"}), 404
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        logger.error(f"Error in api_io_latest: {e}")
        return jsonify({"success": False, "error": f"Error reading I/O status: {e}"}), 500



@app.route("/api/alarms/export")
def api_export():
    """Download filtered alarm records as a CSV file."""
    try:
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        shift = request.args.get("shift") or None
        station = request.args.get("station") or None
        search = request.args.get("search") or None

        csv_data = export_alarm_csv(
            date_from=date_from,
            date_to=date_to,
            shift=shift,
            station=station,
            search=search
        )

        filename = f"alarms_export_{Config.MACHINE_ID}.csv"
        return Response(
            csv_data,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except Exception as e:
        logger.error(f"Error in api_export: {e}", exc_info=True)
        err_csv = (
            "ID,Timestamp,Station,Alarm / Fault Description,Operator,Shift,Machine Number\n"
            f"-,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},Error,Failed to generate export: {e},{Config.OPERATOR_NAME},-,{Config.MACHINE_ID}\n"
        )
        return Response(
            err_csv,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=alarms_export_error.csv"}
        )


def test_plc_socket(ip: str, port: int = 102, timeout: float = 0.6) -> tuple[bool, str]:
    """Fast non-blocking check if Siemens S7 TCP port 102 is reachable."""
    if not ip:
        return False, "Empty PLC IP address"
    try:
        import socket
        with socket.create_connection((ip, port), timeout=timeout):
            return True, "Reachable"
    except Exception as e:
        return False, str(e)


@app.route("/api/health")
def api_health():
    """Check database connection, PLC connection, and system status."""
    sql_ok, sql_msg = test_sql_connection()
    plc_ok, plc_msg = test_plc_socket(Config.PLC_IP, timeout=0.6)
    return jsonify({
        "machine_id": Config.MACHINE_ID,
        "sql_connected": sql_ok,
        "sql_message": sql_msg,
        "sql_server": Config.SQL_SERVER,
        "sql_database": Config.SQL_DATABASE,
        "plc_connected": plc_ok,
        "plc_message": plc_msg,
        "plc_ip": Config.PLC_IP,
        "plc_rack": Config.PLC_RACK,
        "plc_slot": Config.PLC_SLOT,
    })


@app.route("/api/config", methods=["GET"])
def api_get_config():
    """Return the current active configuration."""
    from app.config import get_config_dict
    return jsonify({
        "success": True,
        "config": get_config_dict()
    })


@app.route("/api/config", methods=["POST"])
def api_save_config():
    """Save updated connection and machine configuration to .env."""
    from app.config import get_config_dict, update_env_file

    data = request.get_json() or {}
    updates = {}

    if "plc_ip" in data and str(data["plc_ip"]).strip():
        updates["PLC_IP"] = str(data["plc_ip"]).strip()
    if "plc_rack" in data:
        updates["PLC_RACK"] = str(data["plc_rack"]).strip()
    if "plc_slot" in data:
        updates["PLC_SLOT"] = str(data["plc_slot"]).strip()
    if "plc_db_number" in data:
        updates["PLC_DB_NUMBER"] = str(data["plc_db_number"]).strip()
    if "plc_alarm_db" in data:
        updates["PLC_ALARM_DB"] = str(data["plc_alarm_db"]).strip()

    if "sql_server" in data and str(data["sql_server"]).strip():
        updates["SQL_SERVER"] = str(data["sql_server"]).strip()
    if "sql_database" in data and str(data["sql_database"]).strip():
        updates["SQL_DATABASE"] = str(data["sql_database"]).strip()
    if "sql_trusted_connection" in data:
        updates["SQL_TRUSTED_CONNECTION"] = "true" if data["sql_trusted_connection"] else "false"
    if "sql_user" in data:
        updates["SQL_USER"] = str(data["sql_user"]).strip()
    if "sql_password" in data:
        updates["SQL_PASSWORD"] = str(data["sql_password"]).strip()

    if "machine_id" in data and str(data["machine_id"]).strip():
        updates["MACHINE_ID"] = str(data["machine_id"]).strip()
    if "operator_name" in data and str(data["operator_name"]).strip():
        updates["OPERATOR_NAME"] = str(data["operator_name"]).strip()
    if "web_port" in data and str(data["web_port"]).strip():
        updates["WEB_PORT"] = str(data["web_port"]).strip()
    if "log_on_alarm_only" in data:
        updates["LOG_ON_ALARM_ONLY"] = "true" if data["log_on_alarm_only"] else "false"

    success, msg = update_env_file(updates)

    if not success:
        return jsonify({"success": False, "error": msg or "Failed to write configuration to .env file"}), 500

    return jsonify({
        "success": True,
        "message": msg or "Configuration successfully saved to .env!",
        "config": get_config_dict()
    })


@app.route("/api/config/test-plc", methods=["POST"])
def api_test_plc():
    """Test connection to Siemens PLC with given IP, Rack, and Slot."""
    import time
    import snap7

    data = request.get_json() or {}
    ip = str(data.get("plc_ip", Config.PLC_IP)).strip()
    rack = int(data.get("plc_rack", Config.PLC_RACK))
    slot = int(data.get("plc_slot", Config.PLC_SLOT))

    if not ip:
        return jsonify({"success": False, "error": "PLC IP address cannot be empty"}), 400

    client = snap7.client.Client()
    t0 = time.time()
    try:
        client.connect(ip, rack, slot)
        connected = client.get_connected()
        latency_ms = round((time.time() - t0) * 1000, 1)
        client.disconnect()

        if connected:
            return jsonify({
                "success": True,
                "message": f"Connected to Siemens PLC ({ip}:102, Rack {rack}, Slot {slot}) in {latency_ms} ms",
                "latency_ms": latency_ms
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to connect to PLC at {ip}:102 (Rack {rack}, Slot {slot})"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"PLC Connection Error: {str(e)}"
        }), 400
    finally:
        try:
            client.destroy()
        except Exception:
            pass


@app.route("/api/config/test-sql", methods=["POST"])
def api_test_sql():
    """Test connectivity to SQL Server / SSMS with given parameters."""
    data = request.get_json() or {}
    server = str(data.get("sql_server", Config.SQL_SERVER)).strip()
    database = str(data.get("sql_database", Config.SQL_DATABASE)).strip()
    trusted = data.get("sql_trusted_connection", Config.SQL_TRUSTED_CONNECTION)
    user = str(data.get("sql_user", Config.SQL_USER)).strip()
    password = str(data.get("sql_password", Config.SQL_PASSWORD)).strip()

    if not server:
        return jsonify({"success": False, "error": "SQL Server host name cannot be empty"}), 400

    ok, msg = test_sql_connection(
        server=server,
        database=database,
        trusted_connection=trusted,
        user=user,
        password=password,
        timeout=4
    )
    if ok:
        return jsonify({
            "success": True,
            "message": f"SQL Server connected successfully! {msg}"
        })
    else:
        return jsonify({
            "success": False,
            "error": f"SQL Connection Error: {msg}"
        }), 400


@app.route("/api/config/restart-service", methods=["POST"])
def api_restart_service():
    """Restart HydraulicDataCollectorService so new settings take effect."""
    import subprocess

    service_name = "HydraulicDataCollectorService"
    try:
        stop_res = subprocess.run(["net", "stop", service_name], capture_output=True, text=True, timeout=12)
        start_res = subprocess.run(["net", "start", service_name], capture_output=True, text=True, timeout=12)

        if start_res.returncode == 0:
            return jsonify({
                "success": True,
                "message": f"Windows Service '{service_name}' successfully restarted! New IP and SQL host are active."
            })
        else:
            err_msg = start_res.stderr or start_res.stdout or stop_res.stderr or "Service restart did not return 0"
            return jsonify({
                "success": False,
                "error": f"Service restart notice: {err_msg.strip()}. You can restart it manually via services.msc."
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Could not restart service automatically ({str(e)}). Please restart '{service_name}' in services.msc."
        }), 400


def create_app():
    return app


if __name__ == "__main__":
    port = int(os.getenv("WEB_PORT", 5001))
    print(f"Starting Alarm Analytics Web Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


