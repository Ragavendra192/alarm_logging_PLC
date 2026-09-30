import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_base_dir() -> Path:
    """Return the application root directory (handles frozen PyInstaller runtime)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _load_env_file():
    """Load key-value pairs from .env file into os.environ if present."""
    base_dir = get_base_dir()
    env_file = base_dir / ".env"

    if env_file.is_file():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass

    # Optional config.json fallback
    config_json = base_dir / "config.json"
    if config_json.is_file():
        try:
            with open(config_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    if k not in os.environ:
                        os.environ[k] = str(v)
        except Exception:
            pass


_load_env_file()


def get_current_swift() -> str:
    """
    Determine current machine shift / swift.
    If configured explicitly via SWIFT environment variable, return it.
    Otherwise calculate standard 3-shift industrial cycle:
        Shift 1 (Morning)   : 06:00 to 14:00
        Shift 2 (Evening)   : 14:00 to 22:00
        Shift 3 (Night)     : 22:00 to 06:00
    """
    configured = os.getenv("SWIFT")
    if configured:
        return configured

    hour = datetime.now().hour
    if 6 <= hour < 14:
        return "Shift 1"
    elif 14 <= hour < 22:
        return "Shift 2"
    else:
        return "Shift 3"


class Config:
    """Application and Data Collector Configuration."""

    # Machine Identification
    MACHINE_ID = os.getenv("MACHINE_ID", "3_station")
    OPERATOR_NAME = os.getenv("OPERATOR_NAME", "Operator_1")
    SWIFT = os.getenv("SWIFT", "")

    # Siemens PLC Configuration
    PLC_IP = os.getenv("PLC_IP", "192.168.50.11")
    PLC_RACK = int(os.getenv("PLC_RACK", "0"))
    PLC_SLOT = int(os.getenv("PLC_SLOT", "1"))
    PLC_DB_NUMBER = int(os.getenv("PLC_DB_NUMBER", "1000"))
    PLC_BYTE_START = int(os.getenv("PLC_BYTE_START", "0"))
    PLC_BYTE_SIZE = int(os.getenv("PLC_BYTE_SIZE", "37"))

    # Polling & Logging Intervals - set to 100ms (0.1s)
    PLC_POLL_INTERVAL = float(os.getenv("PLC_POLL_INTERVAL", "0.1"))
    PLC_RECONNECT_DELAY = float(os.getenv("PLC_RECONNECT_DELAY", "3.0"))

    # Backwards compatibility
    POLL_INTERVAL = PLC_POLL_INTERVAL

    # SQL Server / SSMS
    SQL_SERVER = os.getenv("SQL_SERVER", r"localhost\SQLEXPRESS")
    SQL_DATABASE = os.getenv("SQL_DATABASE", "HydraulicMachineDB")
    SQL_TABLE_NAME = os.getenv("SQL_TABLE_NAME", "MachineDataLog")
    SQL_TRUSTED_CONNECTION = os.getenv("SQL_TRUSTED_CONNECTION", "true").lower() in ("true", "1", "yes")
    SQL_USER = os.getenv("SQL_USER", "")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
    SQL_TIMEOUT = int(os.getenv("SQL_TIMEOUT", "5"))

    # Data Logging Interval - 100ms (0.1s)
    SQL_IO_LOG_INTERVAL = float(os.getenv("SQL_IO_LOG_INTERVAL", "0.1"))
    SQL_BUFFER_MAX_SIZE = int(os.getenv("SQL_BUFFER_MAX_SIZE", "50000"))

    # PLC Alarm DB Configuration (DBALARM DB 101, fallback DB 1011)
    PLC_ALARM_DB = int(os.getenv("PLC_ALARM_DB", "101"))
    PLC_ALARM_DB_FALLBACK = int(os.getenv("PLC_ALARM_DB_FALLBACK", "1011"))
    PLC_ALARM_START_BYTE = int(os.getenv("PLC_ALARM_START_BYTE", "0"))
    PLC_ALARM_BYTE_COUNT = int(os.getenv("PLC_ALARM_BYTE_COUNT", "64"))
    PLC_ALARM_BYTE_SWAP = os.getenv("PLC_ALARM_BYTE_SWAP", "false").lower() in ("true", "1", "yes")
    ALARM_MAPPINGS_DB = os.getenv("ALARM_MAPPINGS_DB", str(get_base_dir() / "data" / "alarm_mappings.sqlite"))

    # Production State Defaults
    RECIPE_NAME = os.getenv("RECIPE_NAME", "Standard_Recipe")
    MACHINE_MODE = os.getenv("MACHINE_MODE", "AUTO")

    # Logging Mode: Insert row into SSMS only when an alarm is triggered (True by default)
    LOG_ON_ALARM_ONLY = os.getenv("LOG_ON_ALARM_ONLY", "true").lower() in ("true", "1", "yes")
    LOG_ONLY_ON_FAULT = os.getenv("LOG_ONLY_ON_FAULT", "true").lower() in ("true", "1", "yes")

    # Press Actual Metrics DB Configuration
    P1_DB = int(os.getenv("P1_DB", "1000"))
    P1_START_BYTE = int(os.getenv("P1_START_BYTE", "200"))
    P2_DB = int(os.getenv("P2_DB", "1001"))
    P2_START_BYTE = int(os.getenv("P2_START_BYTE", "228"))
    P3_DB = int(os.getenv("P3_DB", "1001"))
    P3_START_BYTE = int(os.getenv("P3_START_BYTE", "268"))

    # IO Acquisition Source: AUTO (reads PE process inputs, PA process outputs, HW offsets, and DB 1000)
    PLC_IO_SOURCE = os.getenv("PLC_IO_SOURCE", "AUTO").upper()

    # Web Dashboard Port
    WEB_PORT = int(os.getenv("WEB_PORT", "5001"))


def reload_config() -> None:
    """Reload .env file and update Config class attributes dynamically."""
    _load_env_file()
    Config.WEB_PORT = int(os.getenv("WEB_PORT", "5001"))
    Config.MACHINE_ID = os.getenv("MACHINE_ID", "3_station")
    Config.OPERATOR_NAME = os.getenv("OPERATOR_NAME", "Operator_1")

    Config.SWIFT = os.getenv("SWIFT", "")
    Config.PLC_IP = os.getenv("PLC_IP", "192.168.50.11")
    Config.PLC_RACK = int(os.getenv("PLC_RACK", "0"))
    Config.PLC_SLOT = int(os.getenv("PLC_SLOT", "1"))
    Config.PLC_DB_NUMBER = int(os.getenv("PLC_DB_NUMBER", "1000"))
    Config.PLC_BYTE_START = int(os.getenv("PLC_BYTE_START", "0"))
    Config.PLC_BYTE_SIZE = int(os.getenv("PLC_BYTE_SIZE", "37"))
    Config.PLC_POLL_INTERVAL = float(os.getenv("PLC_POLL_INTERVAL", "0.1"))
    Config.PLC_RECONNECT_DELAY = float(os.getenv("PLC_RECONNECT_DELAY", "3.0"))
    Config.POLL_INTERVAL = Config.PLC_POLL_INTERVAL
    Config.SQL_SERVER = os.getenv("SQL_SERVER", r"localhost\SQLEXPRESS")
    Config.SQL_DATABASE = os.getenv("SQL_DATABASE", "HydraulicMachineDB")
    Config.SQL_TABLE_NAME = os.getenv("SQL_TABLE_NAME", "MachineDataLog")
    Config.SQL_TRUSTED_CONNECTION = os.getenv("SQL_TRUSTED_CONNECTION", "true").lower() in ("true", "1", "yes")
    Config.SQL_USER = os.getenv("SQL_USER", "")
    Config.SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
    Config.SQL_TIMEOUT = int(os.getenv("SQL_TIMEOUT", "5"))
    Config.SQL_IO_LOG_INTERVAL = float(os.getenv("SQL_IO_LOG_INTERVAL", "0.1"))
    Config.SQL_BUFFER_MAX_SIZE = int(os.getenv("SQL_BUFFER_MAX_SIZE", "50000"))
    Config.PLC_ALARM_DB = int(os.getenv("PLC_ALARM_DB", "101"))
    Config.PLC_ALARM_DB_FALLBACK = int(os.getenv("PLC_ALARM_DB_FALLBACK", "1011"))
    Config.PLC_ALARM_START_BYTE = int(os.getenv("PLC_ALARM_START_BYTE", "0"))
    Config.PLC_ALARM_BYTE_COUNT = int(os.getenv("PLC_ALARM_BYTE_COUNT", "64"))
    Config.PLC_ALARM_BYTE_SWAP = os.getenv("PLC_ALARM_BYTE_SWAP", "false").lower() in ("true", "1", "yes")
    Config.ALARM_MAPPINGS_DB = os.getenv("ALARM_MAPPINGS_DB", str(get_base_dir() / "data" / "alarm_mappings.sqlite"))
    Config.RECIPE_NAME = os.getenv("RECIPE_NAME", "Standard_Recipe")
    Config.MACHINE_MODE = os.getenv("MACHINE_MODE", "AUTO")
    Config.LOG_ON_ALARM_ONLY = os.getenv("LOG_ON_ALARM_ONLY", "true").lower() in ("true", "1", "yes")
    Config.LOG_ONLY_ON_FAULT = os.getenv("LOG_ONLY_ON_FAULT", "true").lower() in ("true", "1", "yes")
    Config.P1_DB = int(os.getenv("P1_DB", "1000"))
    Config.P1_START_BYTE = int(os.getenv("P1_START_BYTE", "200"))
    Config.P2_DB = int(os.getenv("P2_DB", "1001"))
    Config.P2_START_BYTE = int(os.getenv("P2_START_BYTE", "228"))
    Config.P3_DB = int(os.getenv("P3_DB", "1001"))
    Config.P3_START_BYTE = int(os.getenv("P3_START_BYTE", "268"))
    Config.PLC_IO_SOURCE = os.getenv("PLC_IO_SOURCE", "AUTO").upper()


def ensure_env_file_permissions() -> None:
    """Ensure standard Users (S-1-5-32-545) have write/modify access to .env in Windows."""
    if sys.platform != "win32":
        return
    try:
        env_file = get_base_dir() / ".env"
        if env_file.exists():
            import stat
            import subprocess
            try:
                os.chmod(env_file, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
            # Grant BUILTIN\\Users (well-known SID *S-1-5-32-545) Modify access silently
            subprocess.run(
                ["icacls", str(env_file), "/grant", "*S-1-5-32-545:(M)"],
                capture_output=True,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
    except Exception:
        pass


def update_env_file(updates: dict[str, str]) -> tuple[bool, str]:
    """Update or insert key-value pairs into .env file while preserving comments and order."""
    base_dir = get_base_dir()
    env_file = base_dir / ".env"

    lines = []
    keys_updated = set()

    if env_file.is_file():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        key, _ = stripped.split("=", 1)
                        key = key.strip()
                        if key in updates:
                            val = updates[key]
                            lines.append(f"{key}={val}\n")
                            keys_updated.add(key)
                            os.environ[key] = str(val)
                            continue
                    lines.append(line if line.endswith("\n") else line + "\n")
        except Exception as e:
            return False, f"Failed to read existing .env file: {e}"

    # Append any keys that were not in the file
    for k, v in updates.items():
        if k not in keys_updated:
            lines.append(f"{k}={v}\n")
            os.environ[k] = str(v)

    try:
        import stat
        if env_file.exists():
            try:
                os.chmod(env_file, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass

        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except PermissionError as pe:
        return False, f"Permission denied writing to '{env_file}'. Administrator privileges or folder write permissions required ({pe})."
    except Exception as e:
        return False, f"Failed to write configuration file ({e})"

    try:
        reload_config()
    except Exception as e:
        return False, f"Configuration written, but reloading failed ({e})"

    return True, "Configuration successfully saved to .env!"


def get_config_dict() -> dict:
    """Return dictionary of current settings for the web dashboard."""
    return {
        "machine_id": Config.MACHINE_ID,
        "operator_name": Config.OPERATOR_NAME,
        "plc_ip": Config.PLC_IP,
        "plc_rack": Config.PLC_RACK,
        "plc_slot": Config.PLC_SLOT,
        "plc_db_number": Config.PLC_DB_NUMBER,
        "plc_alarm_db": Config.PLC_ALARM_DB,
        "sql_server": Config.SQL_SERVER,
        "sql_database": Config.SQL_DATABASE,
        "sql_trusted_connection": Config.SQL_TRUSTED_CONNECTION,
        "sql_user": Config.SQL_USER,
        "sql_password": Config.SQL_PASSWORD,
        "sql_timeout": Config.SQL_TIMEOUT,
        "sql_io_log_interval": Config.SQL_IO_LOG_INTERVAL,
        "log_on_alarm_only": Config.LOG_ON_ALARM_ONLY,
        "plc_poll_interval": Config.PLC_POLL_INTERVAL,
        "web_port": Config.WEB_PORT
    }


