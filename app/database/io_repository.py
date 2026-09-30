"""
Repository module for high-frequency IO and 3-station press actual data logging.

Supports inserting and retrieving snapshots with:
- Timestamp
- OperatorName
- Swift
- 292 separate PLC Boolean address columns ([0.0] through [36.3]) showing 0 and 1
- 57 Real (float32) columns covering Press 1 (P1), Press 2 (P2), Press 3 (P3)
"""

from datetime import datetime
import logging
from typing import Any

from app.config import Config, get_current_swift
from app.database.db_connection import get_db_cursor
from app.plc.plc_tags import PLC_ADDRESSES
from app.plc.press_actual import ALL_PRESS_COLUMNS

logger = logging.getLogger("PLCDataCollector.Repository")

# Pre-constructed column names
_IO_COLS = [f"[{addr}]" for addr in PLC_ADDRESSES]
_PRESS_COLS = [f"[{col}]" for col in ALL_PRESS_COLUMNS]

_ALL_DATA_COLS = _IO_COLS + _PRESS_COLS
_ALL_DATA_COLS_SQL = ", ".join(_ALL_DATA_COLS)
_ALL_PLACEHOLDERS_SQL = ", ".join(["?"] * len(_ALL_DATA_COLS))


def build_insert_query(table_name: str) -> str:
    """Build parameterized INSERT statement for the target table."""
    return f"""
        INSERT INTO dbo.{table_name} (
            MachineNumber,
            [Timestamp],
            [Alarm],
            OperatorName,
            Swift,
            {_ALL_DATA_COLS_SQL},
            CreatedAt
        )
        VALUES (?, ?, ?, ?, ?, {_ALL_PLACEHOLDERS_SQL}, SYSDATETIME())
    """


def save_io_status(
    machine_number: str,
    timestamp: datetime | None,
    io_data: dict[str, int | bool],
    alarm: str | None = None,
    operator_name: str | None = None,
    swift: str | None = None,
    press_data: dict[str, float] | None = None,
    table_name: str | None = None,
    cursor: Any | None = None
) -> int:
    """
    Persist an IO and Press Actual snapshot into SQL Server with optional Alarm display string.

    Parameters:
        machine_number: Unique machine identifier
        timestamp: Snapshot timestamp (defaults to datetime.now())
        io_data: Dictionary mapping address (e.g. "0.0") to 0/1
        alarm: Optional active alarm / fault string (placed after Timestamp)
        operator_name: Operator name (defaults to Config.OPERATOR_NAME)
        swift: Shift name (defaults to Config.SWIFT or get_current_swift())
        press_data: Dictionary mapping press column (e.g. "P1 MAIN RAM POSITION") to float
        table_name: Destination table ("MachineDataLog", "IOStatus", or "AlarmResponse")
        cursor: Optional active pyodbc cursor for high-speed persistent reuse
    """
    tbl = table_name or Config.SQL_TABLE_NAME
    ts = timestamp if timestamp is not None else datetime.now()
    alarm_str = str(alarm).strip() if alarm else None
    if alarm_str and len(alarm_str) > 4000:
        alarm_str = alarm_str[:3997] + "..."
    op = operator_name if operator_name is not None else Config.OPERATOR_NAME
    sw = swift if swift is not None else (Config.SWIFT or get_current_swift())
    pdata = press_data or {}

    values: list[Any] = [machine_number, ts, alarm_str, op, sw]

    # 1. 292 Boolean values (0 or 1)
    for addr in PLC_ADDRESSES:
        val = io_data.get(addr, 0)
        values.append(1 if val else 0)

    # 2. 57 Press Real values (float)
    for col in ALL_PRESS_COLUMNS:
        fval = pdata.get(col, 0.0)
        values.append(float(fval))

    sql = build_insert_query(tbl)

    if cursor is not None:
        cursor.execute(sql, values)
        return cursor.rowcount

    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, values)
        return cur.rowcount


def save_alarm_snapshot(
    machine_number: str,
    timestamp: datetime | None,
    alarm: str,
    io_data: dict[str, int | bool],
    operator_name: str | None = None,
    swift: str | None = None,
    press_data: dict[str, float] | None = None,
    cursor: Any | None = None
) -> int:
    """
    Persist an Alarm triggered event snapshot into dbo.AlarmResponse with all 356 columns.
    """
    return save_io_status(
        machine_number=machine_number,
        timestamp=timestamp,
        io_data=io_data,
        alarm=alarm,
        operator_name=operator_name,
        swift=swift,
        press_data=press_data,
        table_name="AlarmResponse",
        cursor=cursor
    )


def get_latest_io_status(
    machine_number: str,
    table_name: str | None = None
) -> dict[str, Any] | None:
    """
    Retrieve the latest snapshot from SQL Server for a given machine.
    Returns dictionary with all 292 address bits, 57 press actuals,
    Alarm, OperatorName, Swift, and Timestamp.
    """
    tbl = table_name or Config.SQL_TABLE_NAME
    query = f"""
        SELECT TOP 1 *
        FROM dbo.{tbl}
        WHERE MachineNumber = ?
        ORDER BY [Timestamp] DESC
    """

    with get_db_cursor(commit=False) as cursor:
        cursor.execute(query, (machine_number,))
        row = cursor.fetchone()
        if not row:
            return None

        col_names = [col[0] for col in cursor.description]
        row_dict = dict(zip(col_names, row))

        result: dict[str, Any] = {
            "MachineNumber": row_dict.get("MachineNumber"),
            "Timestamp": row_dict.get("Timestamp"),
            "Alarm": row_dict.get("Alarm"),
            "OperatorName": row_dict.get("OperatorName"),
            "Swift": row_dict.get("Swift"),
        }

        # Extract 292 address columns
        for addr in PLC_ADDRESSES:
            if addr in row_dict:
                val = row_dict[addr]
                result[addr] = 1 if val else 0

        # Extract 57 press actual columns
        for col in ALL_PRESS_COLUMNS:
            if col in row_dict:
                val = row_dict[col]
                result[col] = float(val) if val is not None else 0.0

        return result


def build_alarm_event_insert_query() -> str:
    """Build parameterized INSERT statement for dbo.AlarmEvent."""
    return f"""
        INSERT INTO dbo.AlarmEvent (
            MachineNumber,
            PLCAddress,
            DBNumber,
            ByteAddress,
            BitAddress,
            AlarmCode,
            AlarmDescription,
            [Alarm],
            Severity,
            AlarmStartTime,
            AlarmEndTime,
            AlarmDurationSeconds,
            OperatorName,
            Swift,
            RecipeName,
            MachineRunning,
            CycleRunning,
            MachineMode,
            PLCConnected,
            [Timestamp],
            {_ALL_DATA_COLS_SQL},
            CreatedAt
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, {_ALL_PLACEHOLDERS_SQL}, SYSDATETIME())
    """


def save_alarm_event_start(
    event_data: dict[str, Any],
    cursor: Any | None = None
) -> int:
    """
    Persist an ALARM_START event snapshot into dbo.AlarmEvent.
    Captures complete machine state (all 292 IO bits + 57 press actuals).
    """
    machine_number = event_data.get("machine_number") or Config.MACHINE_ID
    plc_address = str(event_data.get("plc_address", "UNKNOWN"))
    db_number = event_data.get("db_number", Config.PLC_ALARM_DB)
    byte_address = event_data.get("byte_address", 0)
    bit_address = event_data.get("bit_address", 0)
    alarm_code = event_data.get("alarm_code") or f"ALM-DB{db_number}-{byte_address:03d}{bit_address}"
    alarm_desc = str(event_data.get("alarm_description") or f"UNMAPPED ALARM {plc_address}")
    if len(alarm_desc) > 4000:
        alarm_desc = alarm_desc[:3997] + "..."
    severity = str(event_data.get("severity") or "FAULT")
    start_time = event_data.get("start_time") or datetime.now()
    operator_name = event_data.get("operator_name") or Config.OPERATOR_NAME
    swift = event_data.get("swift") or (Config.SWIFT or get_current_swift())
    recipe_name = event_data.get("recipe_name") or Config.RECIPE_NAME
    machine_running = 1 if event_data.get("machine_running", True) else 0
    cycle_running = 1 if event_data.get("cycle_running", False) else 0
    machine_mode = event_data.get("machine_mode") or Config.MACHINE_MODE
    plc_connected = 1 if event_data.get("plc_connected", True) else 0
    timestamp = event_data.get("timestamp") or start_time

    io_data = event_data.get("io_data") or {}
    press_data = event_data.get("press_data") or {}

    values: list[Any] = [
        machine_number,
        plc_address,
        db_number,
        byte_address,
        bit_address,
        alarm_code,
        alarm_desc,
        alarm_desc,
        severity,
        start_time,
        operator_name,
        swift,
        recipe_name,
        machine_running,
        cycle_running,
        machine_mode,
        plc_connected,
        timestamp,
    ]

    # 292 Boolean columns
    for addr in PLC_ADDRESSES:
        val = io_data.get(addr, 0)
        values.append(1 if val else 0)

    # 57 Press Real columns
    for col in ALL_PRESS_COLUMNS:
        fval = press_data.get(col, 0.0)
        values.append(float(fval))

    sql = build_alarm_event_insert_query()

    if cursor is not None:
        cursor.execute(sql, values)
        # Also persist to legacy AlarmResponse if present
        try:
            save_alarm_snapshot(
                machine_number=machine_number,
                timestamp=timestamp,
                alarm=f"{alarm_desc} ({plc_address})",
                io_data=io_data,
                operator_name=operator_name,
                swift=swift,
                press_data=press_data,
                cursor=cursor
            )
        except Exception as leg_err:
            logger.debug(f"Legacy AlarmResponse sync: {leg_err}")
        return cursor.rowcount

    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, values)
        try:
            save_alarm_snapshot(
                machine_number=machine_number,
                timestamp=timestamp,
                alarm=f"{alarm_desc} ({plc_address})",
                io_data=io_data,
                operator_name=operator_name,
                swift=swift,
                press_data=press_data,
                cursor=cur
            )
        except Exception:
            pass
        return cur.rowcount


def close_alarm_event(
    machine_number: str,
    plc_address: str,
    end_time: datetime | None = None,
    cursor: Any | None = None
) -> int:
    """
    Close an active alarm event in dbo.AlarmEvent (and dbo.AlarmResponse)
    by updating AlarmEndTime and calculating AlarmDurationSeconds.
    """
    ts_end = end_time if end_time is not None else datetime.now()

    def _execute_close(cur) -> int:
        cur.execute("""
            SELECT TOP 1 Id, AlarmStartTime
            FROM dbo.AlarmEvent
            WHERE MachineNumber = ?
              AND PLCAddress = ?
              AND AlarmEndTime IS NULL
            ORDER BY AlarmStartTime DESC
        """, (machine_number, plc_address))
        row = cur.fetchone()
        if not row:
            return 0

        event_id = row[0]
        cur.execute("""
            UPDATE dbo.AlarmEvent
            SET AlarmEndTime = ?,
                AlarmDurationSeconds = DATEDIFF(SECOND, AlarmStartTime, ?)
            WHERE Id = ?
        """, (ts_end, ts_end, event_id))

        # Also close corresponding open row in dbo.AlarmResponse if present
        try:
            cur.execute("""
                SELECT TOP 1 Id
                FROM dbo.AlarmResponse
                WHERE MachineNumber = ?
                  AND (AlarmCode = ? OR [Alarm] LIKE ? OR AlarmDescription LIKE ?)
                  AND AlarmEndTime IS NULL
                ORDER BY AlarmStartTime DESC
            """, (machine_number, plc_address, f"%{plc_address}%", f"%{plc_address}%"))
            resp_row = cur.fetchone()
            if resp_row:
                cur.execute("""
                    UPDATE dbo.AlarmResponse
                    SET AlarmEndTime = ?,
                        AlarmDurationSeconds = DATEDIFF(SECOND, AlarmStartTime, ?)
                    WHERE Id = ?
                """, (ts_end, ts_end, resp_row[0]))
        except Exception:
            pass

        return 1

    if cursor is not None:
        return _execute_close(cursor)

    with get_db_cursor(commit=True) as cur:
        return _execute_close(cur)


def get_active_alarm_events(
    machine_number: str | None = None,
    limit: int = 100,
    cursor: Any | None = None
) -> list[dict[str, Any]]:
    """Retrieve currently active (un-cleared) alarm events from dbo.AlarmEvent."""
    query = """
        SELECT TOP (?)
            Id, MachineNumber, PLCAddress, DBNumber, ByteAddress, BitAddress,
            AlarmCode, AlarmDescription, Severity, AlarmStartTime,
            OperatorName, Swift, RecipeName, MachineRunning, CycleRunning, MachineMode,
            PLCConnected, [Timestamp]
        FROM dbo.AlarmEvent
        WHERE AlarmEndTime IS NULL
    """
    params: list[Any] = [limit]
    if machine_number:
        query += " AND MachineNumber = ?"
        params.append(machine_number)
    query += " ORDER BY AlarmStartTime DESC"

    def _fetch(cur):
        cur.execute(query, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    if cursor is not None:
        return _fetch(cursor)
    with get_db_cursor(commit=False) as cur:
        return _fetch(cur)


def get_active_alarm_count(
    machine_number: str | None = None,
    cursor: Any | None = None
) -> int:
    """Return count of currently open active alarm events."""
    query = "SELECT COUNT(*) FROM dbo.AlarmEvent WHERE AlarmEndTime IS NULL"
    params: list[Any] = []
    if machine_number:
        query += " AND MachineNumber = ?"
        params.append(machine_number)

    def _count(cur):
        cur.execute(query, params)
        return cur.fetchone()[0]

    if cursor is not None:
        return _count(cursor)
    with get_db_cursor(commit=False) as cur:
        return _count(cur)

