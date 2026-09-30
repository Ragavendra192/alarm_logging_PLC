"""
SQL Server Database Connection Management.

Provides thread-safe connection generation, ODBC driver auto-detection,
connection testing, and context management for pyodbc cursors.
"""

from contextlib import contextmanager
import logging
import pyodbc

from app.config import Config

logger = logging.getLogger("PLCDataCollector.Database")

# Cached working driver name
_CACHED_DRIVER: str | None = None


def get_available_odbc_driver() -> str:
    """Detect and return the preferred installed SQL Server ODBC driver."""
    global _CACHED_DRIVER
    if _CACHED_DRIVER:
        return _CACHED_DRIVER

    available_drivers = pyodbc.drivers()

    # Preferred order of drivers
    preferred = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "SQL Server"
    ]

    for drv in preferred:
        if drv in available_drivers:
            _CACHED_DRIVER = drv
            logger.debug(f"Selected ODBC Driver: {drv}")
            return drv

    # Fallback to any SQL Server driver
    for drv in available_drivers:
        if "sql server" in drv.lower():
            _CACHED_DRIVER = drv
            logger.debug(f"Selected fallback ODBC Driver: {drv}")
            return drv

    # Default if none explicitly matched
    _CACHED_DRIVER = "ODBC Driver 17 for SQL Server"
    return _CACHED_DRIVER


def build_connection_string(
    server: str | None = None,
    database: str | None = None,
    trusted_connection: bool | None = None,
    user: str | None = None,
    password: str | None = None,
    timeout: int | None = None
) -> str:
    """Construct a pyodbc connection string based on parameters or application configuration."""
    driver = get_available_odbc_driver()
    srv = server or Config.SQL_SERVER
    db = database or Config.SQL_DATABASE
    is_trusted = Config.SQL_TRUSTED_CONNECTION if trusted_connection is None else trusted_connection
    u = Config.SQL_USER if user is None else user
    p = Config.SQL_PASSWORD if password is None else password
    t = Config.SQL_TIMEOUT if timeout is None else timeout

    parts = [
        f"Driver={{{driver}}}",
        f"Server={srv}",
        f"Database={db}",
    ]

    if is_trusted:
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={u}")
        parts.append(f"PWD={p}")

    if "ODBC Driver 18" in driver:
        parts.append("TrustServerCertificate=yes")

    parts.append(f"LoginTimeout={t}")

    return ";".join(parts) + ";"


def get_sql_connection(
    server: str | None = None,
    database: str | None = None,
    trusted_connection: bool | None = None,
    user: str | None = None,
    password: str | None = None,
    timeout: int | None = None
) -> pyodbc.Connection:
    """
    Establish and return a new pyodbc Connection.
    Raises pyodbc.Error on failure.
    """
    conn_str = build_connection_string(server, database, trusted_connection, user, password, timeout)
    t = Config.SQL_TIMEOUT if timeout is None else timeout
    return pyodbc.connect(conn_str, timeout=t)


def test_sql_connection(
    server: str | None = None,
    database: str | None = None,
    trusted_connection: bool | None = None,
    user: str | None = None,
    password: str | None = None,
    timeout: int | None = None
) -> tuple[bool, str]:
    """
    Test connectivity to SQL Server.
    Returns (True, "Connected (<version>)") or (False, error_message).
    """
    try:
        conn = get_sql_connection(server, database, trusted_connection, user, password, timeout)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        version = row[0].split("\n")[0] if row else "SQL Server"
        conn.close()
        return True, f"Connected ({version})"
    except Exception as e:
        return False, str(e)



@contextmanager
def get_db_cursor(commit: bool = True):
    """
    Context manager that yields a cursor and safely commits or rolls back transactions.
    Automatically closes cursor and connection.
    """
    conn = None
    cursor = None
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        if conn and commit:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
