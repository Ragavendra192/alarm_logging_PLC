"""
Alarm Analytics Repository.

Queries SQL Server (HydraulicMachineDB) for fault and alarm analytics:
- Filtering by date range, shift, press station, and search text
- Summary KPIs (Total, Today, Shift, Station breakdown)
- Timeline aggregation and Pareto top faults
- Drill-down snapshot data retrieval
- CSV export generation
"""

import csv
from datetime import datetime, timedelta
import io
import logging
from typing import Any

from app.config import Config, get_current_swift
from app.database.db_connection import get_db_cursor
from app.plc.plc_tags import PLC_ADDRESSES, PLC_TAGS
from app.plc.press_actual import ALL_PRESS_COLUMNS


logger = logging.getLogger("PLCDataCollector.AlarmAnalytics")


def classify_station(alarm_text: str | None) -> str:
    """Classify alarm text into Station (Press 1, Press 2, Press 3, Drive/MPCB, Common)."""
    if not alarm_text:
        return "Unknown"
    txt = alarm_text.upper()
    if "P1 " in txt or "P1_" in txt or "PRESS 1" in txt or txt.startswith("P1"):
        return "Press 1"
    if "P2 " in txt or "P2_" in txt or "PRESS 2" in txt or txt.startswith("P2"):
        return "Press 2"
    if "P3 " in txt or "P3_" in txt or "PRESS 3" in txt or txt.startswith("P3"):
        return "Press 3"
    if "SERVO" in txt or "DRIVE" in txt or "MPCB" in txt or "CB" in txt:
        return "Drive / MPCB"
    return "Common"


def get_alarm_logs(
    date_from: str | None = None,
    date_to: str | None = None,
    shift: str | None = None,
    station: str | None = None,
    search: str | None = None,
    source_table: str = "AlarmResponse",
    limit: int = 100,
    offset: int = 0
) -> tuple[list[dict[str, Any]], int]:
    """
    Retrieve filterable, paginated alarm records from SQL Server dbo.AlarmResponse.
    Returns (records, total_count).
    """
    conditions = ["Alarm IS NOT NULL", "LTRIM(RTRIM(Alarm)) != ''"]
    params: list[Any] = []

    if date_from:
        conditions.append("[Timestamp] >= ?")
        params.append(date_from)

    if date_to:
        conditions.append("[Timestamp] <= ?")
        params.append(date_to)

    if shift and shift.lower() != "all":
        conditions.append("Swift = ?")
        params.append(shift)

    if search and search.strip():
        term = f"%{search.strip()}%"
        conditions.append("(Alarm LIKE ? OR OperatorName LIKE ? OR MachineNumber LIKE ?)")
        params.extend([term, term, term])

    where_clause = " AND ".join(conditions)

    # Query target table(s): AlarmEvent, AlarmResponse, MachineDataLog, or all
    if source_table == "AlarmEvent":
        base_query = f"""
            FROM (
                SELECT 
                    Id, 'AlarmEvent' AS SourceTable, MachineNumber, 
                    ISNULL(AlarmStartTime, [Timestamp]) AS [Timestamp], 
                    ISNULL(AlarmDescription, [Alarm]) AS [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.AlarmEvent
                WHERE (AlarmDescription IS NOT NULL AND LTRIM(RTRIM(AlarmDescription)) != '')
                   OR (Alarm IS NOT NULL AND LTRIM(RTRIM(Alarm)) != '')
            ) AS CombinedAlarms
        """
        union_params = []
    elif source_table == "all":
        base_query = f"""
            FROM (
                SELECT 
                    Id, 'AlarmEvent' AS SourceTable, MachineNumber, 
                    ISNULL(AlarmStartTime, [Timestamp]) AS [Timestamp], 
                    ISNULL(AlarmDescription, [Alarm]) AS [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.AlarmEvent
                WHERE (AlarmDescription IS NOT NULL AND LTRIM(RTRIM(AlarmDescription)) != '')
                   OR (Alarm IS NOT NULL AND LTRIM(RTRIM(Alarm)) != '')

                UNION ALL

                SELECT 
                    Id, 'AlarmResponse' AS SourceTable, MachineNumber, [Timestamp], [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.AlarmResponse
                WHERE {where_clause}

                UNION ALL

                SELECT 
                    Id, 'MachineDataLog' AS SourceTable, MachineNumber, [Timestamp], [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.MachineDataLog
                WHERE {where_clause}
            ) AS CombinedAlarms
        """
        union_params = params + params
    elif source_table == "MachineDataLog":
        base_query = f"""
            FROM (
                SELECT 
                    Id, 'MachineDataLog' AS SourceTable, MachineNumber, [Timestamp], [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.MachineDataLog
                WHERE {where_clause}
            ) AS CombinedAlarms
        """
        union_params = list(params)
    else:
        # Default: dbo.AlarmResponse or dbo.AlarmEvent fallback
        base_query = f"""
            FROM (
                SELECT 
                    Id, 'AlarmEvent' AS SourceTable, MachineNumber, 
                    ISNULL(AlarmStartTime, [Timestamp]) AS [Timestamp], 
                    ISNULL(AlarmDescription, [Alarm]) AS [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.AlarmEvent
                WHERE (AlarmDescription IS NOT NULL AND LTRIM(RTRIM(AlarmDescription)) != '')
                   OR (Alarm IS NOT NULL AND LTRIM(RTRIM(Alarm)) != '')

                UNION ALL

                SELECT 
                    Id, 'AlarmResponse' AS SourceTable, MachineNumber, [Timestamp], [Alarm], 
                    OperatorName, Swift, CreatedAt
                FROM dbo.AlarmResponse
                WHERE {where_clause}
            ) AS CombinedAlarms
        """
        union_params = list(params)

    # Filter station in memory or via outer where if needed
    outer_conditions = []
    outer_params: list[Any] = []
    if station and station.lower() != "all":
        if station == "Press 1":
            outer_conditions.append("(Alarm LIKE '%P1%' OR Alarm LIKE '%PRESS 1%')")
        elif station == "Press 2":
            outer_conditions.append("(Alarm LIKE '%P2%' OR Alarm LIKE '%PRESS 2%')")
        elif station == "Press 3":
            outer_conditions.append("(Alarm LIKE '%P3%' OR Alarm LIKE '%PRESS 3%')")
        elif station == "Drive / MPCB":
            outer_conditions.append("(Alarm LIKE '%SERVO%' OR Alarm LIKE '%DRIVE%' OR Alarm LIKE '%MPCB%')")
        elif station == "Common":
            outer_conditions.append("(Alarm NOT LIKE '%P1%' AND Alarm NOT LIKE '%P2%' AND Alarm NOT LIKE '%P3%' AND Alarm NOT LIKE '%SERVO%')")

    final_where = f"WHERE {' AND '.join(outer_conditions)}" if outer_conditions else ""

    try:
        with get_db_cursor(commit=False) as cursor:
            # 1. Total Count
            count_sql = f"SELECT COUNT(*) {base_query} {final_where}"
            cursor.execute(count_sql, union_params + outer_params)
            total_count = cursor.fetchone()[0]

            # 2. Paginated rows
            data_sql = f"""
                SELECT Id, SourceTable, MachineNumber, [Timestamp], [Alarm], OperatorName, Swift, CreatedAt
                {base_query}
                {final_where}
                ORDER BY [Timestamp] DESC
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            exec_params = union_params + outer_params + [offset, limit]
            cursor.execute(data_sql, exec_params)
            rows = cursor.fetchall()

            records = []
            for r in rows:
                alarm_txt = r[4] or ""
                ts_str = r[3].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if isinstance(r[3], datetime) else str(r[3])
                records.append({
                    "id": r[0],
                    "source_table": r[1],
                    "machine_number": r[2],
                    "timestamp": ts_str,
                    "alarm": alarm_txt,
                    "station": classify_station(alarm_txt),
                    "operator_name": r[5] or "N/A",
                    "shift": r[6] or "N/A",
                })

            return records, total_count
    except Exception as e:
        logger.warning(f"Unable to query alarm logs from database: {e}")
        return [], 0


def get_alarm_stats(
    date_from: str | None = None,
    date_to: str | None = None,
    shift: str | None = None
) -> dict[str, Any]:
    """
    Compute key analytics metrics:
    - Total alarms
    - Alarms today
    - Current shift alarms
    - Station breakdown (P1, P2, P3, Drive, Common)
    - Shift breakdown (Shift 1, Shift 2, Shift 3)
    - Top 5 frequent alarms
    - Timeline points for frequency chart
    """
    records, total_count = get_alarm_logs(
        date_from=date_from,
        date_to=date_to,
        shift=shift,
        limit=2000,
        offset=0
    )

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_shift = Config.SWIFT or get_current_swift()

    today_count = 0
    current_shift_count = 0
    station_counts: dict[str, int] = {
        "Press 1": 0,
        "Press 2": 0,
        "Press 3": 0,
        "Drive / MPCB": 0,
        "Common": 0,
    }
    shift_counts: dict[str, int] = {
        "Shift 1": 0,
        "Shift 2": 0,
        "Shift 3": 0,
    }
    alarm_frequency: dict[str, int] = {}
    timeline_map: dict[str, int] = {}

    for rec in records:
        ts = rec["timestamp"]
        alarm = rec["alarm"]
        station = rec["station"]
        rec_shift = rec["shift"]

        # Today check
        if ts.startswith(today_str):
            today_count += 1

        # Current shift check
        if rec_shift == current_shift and ts.startswith(today_str):
            current_shift_count += 1

        # Station distribution
        if station in station_counts:
            station_counts[station] += 1
        else:
            station_counts["Common"] += 1

        # Shift distribution
        if rec_shift in shift_counts:
            shift_counts[rec_shift] += 1

        # Specific alarm frequency (split multiple comma-separated alarms)
        for individual in [a.strip() for a in alarm.split(",") if a.strip()]:
            alarm_frequency[individual] = alarm_frequency.get(individual, 0) + 1

        # Timeline (by hour or date: YYYY-MM-DD HH:00)
        hour_key = ts[:13] + ":00" if len(ts) >= 13 else ts
        timeline_map[hour_key] = timeline_map.get(hour_key, 0) + 1

    # Sort top alarms
    top_alarms = sorted(
        [{"alarm": k, "count": v} for k, v in alarm_frequency.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]

    # Most affected station
    sorted_stations = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)
    top_station = sorted_stations[0][0] if (sorted_stations and sorted_stations[0][1] > 0) else "None"

    # Timeline list sorted chronologically
    timeline = [{"time": k, "count": v} for k, v in sorted(timeline_map.items())][-24:]

    return {
        "total_alarms": total_count,
        "today_alarms": today_count,
        "current_shift_alarms": current_shift_count,
        "current_shift": current_shift,
        "top_station": top_station,
        "station_distribution": station_counts,
        "shift_distribution": shift_counts,
        "top_alarms": top_alarms,
        "timeline": timeline,
    }


def get_alarm_detail(alarm_id: int, source_table: str = "AlarmResponse") -> dict[str, Any] | None:
    """
    Retrieve full machine freeze-frame snapshot for a given alarm event:
    Returns timestamp, alarm, operator, shift, 57 press actuals, and active tripped IO tags.
    """
    valid_tables = {"AlarmEvent", "AlarmResponse", "MachineDataLog"}
    tbl = source_table if source_table in valid_tables else "AlarmResponse"
    query = f"SELECT TOP 1 * FROM dbo.{tbl} WHERE Id = ?"

    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, (alarm_id,))
            row = cursor.fetchone()
            if not row:
                return None

            col_names = [col[0] for col in cursor.description]
            row_dict = dict(zip(col_names, row))

            ts = row_dict.get("AlarmStartTime") or row_dict.get("Timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if isinstance(ts, datetime) else str(ts)
            alarm_txt = row_dict.get("AlarmDescription") or row_dict.get("Alarm") or ""

            # Extract press actual metrics
            press_metrics: dict[str, dict[str, float]] = {"P1": {}, "P2": {}, "P3": {}}
            for col in ALL_PRESS_COLUMNS:
                if col in row_dict and row_dict[col] is not None:
                    val = float(row_dict[col])
                    if col.startswith("P1 "):
                        press_metrics["P1"][col[3:]] = val
                    elif col.startswith("P2 "):
                        press_metrics["P2"][col[3:]] = val
                    elif col.startswith("P3 "):
                        press_metrics["P3"][col[3:]] = val

            # Extract all 292 I/O tag statuses
            io_list: list[dict[str, Any]] = []
            active_trips: list[str] = []
            active_io_count = 0
            for addr in PLC_ADDRESSES:
                bit_val = 1 if row_dict.get(addr) else 0
                if bit_val:
                    active_io_count += 1
                    active_trips.append(addr)
                tag_meta = PLC_TAGS.get(addr, {})
                io_list.append({
                    "address": addr,
                    "name": tag_meta.get("name", f"Tag_{addr}"),
                    "comment": tag_meta.get("comment", ""),
                    "status": bit_val
                })

            return {
                "id": row_dict.get("Id"),
                "table": tbl,
                "machine_number": row_dict.get("MachineNumber"),
                "timestamp": ts_str,
                "alarm": alarm_txt,
                "station": classify_station(alarm_txt),
                "operator_name": row_dict.get("OperatorName") or "N/A",
                "swift": row_dict.get("Swift") or "N/A",
                "press_actuals": press_metrics,
                "active_io_trips": active_trips,
                "active_io_count": active_io_count,
                "total_io_count": len(PLC_ADDRESSES),
                "io_status": io_list,
            }
    except Exception as e:
        logger.warning(f"Unable to query alarm detail for ID {alarm_id} from database: {e}")
        return None


def get_latest_machine_io() -> dict[str, Any] | None:
    """Retrieve the latest IO status snapshot from SQL Server."""
    try:
        with get_db_cursor(commit=False) as cursor:
            row = None
            for tbl in ["MachineDataLog", "AlarmResponse", "IOStatus"]:
                cursor.execute(f"SELECT TOP 1 * FROM dbo.{tbl} ORDER BY [Timestamp] DESC")
                row = cursor.fetchone()
                if row:
                    break
            if not row:
                return None

            col_names = [col[0] for col in cursor.description]
            row_dict = dict(zip(col_names, row))
            ts = row_dict.get("Timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if isinstance(ts, datetime) else str(ts)

            io_list: list[dict[str, Any]] = []
            active_count = 0
            for addr in PLC_ADDRESSES:
                bit_val = 1 if row_dict.get(addr) else 0
                if bit_val:
                    active_count += 1
                tag_meta = PLC_TAGS.get(addr, {})
                io_list.append({
                    "address": addr,
                    "name": tag_meta.get("name", f"Tag_{addr}"),
                    "comment": tag_meta.get("comment", ""),
                    "status": bit_val
                })

            return {
                "timestamp": ts_str,
                "machine_number": row_dict.get("MachineNumber"),
                "operator_name": row_dict.get("OperatorName") or "N/A",
                "swift": row_dict.get("Swift") or "N/A",
                "alarm": row_dict.get("Alarm"),
                "active_count": active_count,
                "total_count": len(PLC_ADDRESSES),
                "io_status": io_list
            }
    except Exception as e:
        logger.warning(f"Unable to query latest machine IO from database: {e}")
        return None




def export_alarm_csv(
    date_from: str | None = None,
    date_to: str | None = None,
    shift: str | None = None,
    station: str | None = None,
    search: str | None = None
) -> str:
    """Generate CSV string of filtered alarms."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Timestamp", "Station", "Alarm / Fault Description",
        "Operator", "Shift", "Machine Number"
    ])

    try:
        records, total = get_alarm_logs(
            date_from=date_from,
            date_to=date_to,
            shift=shift,
            station=station,
            search=search,
            limit=5000,
            offset=0
        )

        for r in records:
            writer.writerow([
                r["id"],
                r["timestamp"],
                r["station"],
                r["alarm"],
                r["operator_name"],
                r["shift"],
                r["machine_number"],
            ])

        if total == 0:
            writer.writerow([
                "-",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Notice",
                "No alarm records found or SQL Server is currently disconnected. Check Settings tab.",
                Config.OPERATOR_NAME,
                Config.SWIFT or get_current_swift(),
                Config.MACHINE_ID
            ])

    except Exception as e:
        logger.error(f"Error generating alarm CSV export: {e}")
        writer.writerow([
            "-",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error",
            f"Error generating export: {e}",
            Config.OPERATOR_NAME,
            "-",
            Config.MACHINE_ID
        ])

    return output.getvalue()


def get_active_alarm_logs(machine_number: str | None = None) -> list[dict[str, Any]]:
    """Retrieve all currently active (open) alarm events from dbo.AlarmEvent."""
    try:
        with get_db_cursor(commit=False) as cursor:
            query = """
                SELECT
                    Id, MachineNumber, PLCAddress, DBNumber, ByteAddress, BitAddress,
                    AlarmCode, AlarmDescription, Severity, AlarmStartTime,
                    OperatorName, Swift, RecipeName, MachineRunning, CycleRunning, MachineMode,
                    PLCConnected, [Timestamp]
                FROM dbo.AlarmEvent
                WHERE AlarmEndTime IS NULL
            """
            params: list[Any] = []
            if machine_number:
                query += " AND MachineNumber = ?"
                params.append(machine_number)
            query += " ORDER BY AlarmStartTime DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                st = r[9]
                st_str = st.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if isinstance(st, datetime) else str(st)
                results.append({
                    "id": r[0],
                    "machine_number": r[1],
                    "plc_address": r[2],
                    "db_number": r[3],
                    "byte_address": r[4],
                    "bit_address": r[5],
                    "alarm_code": r[6],
                    "alarm_description": r[7],
                    "severity": r[8],
                    "alarm_start_time": st_str,
                    "operator_name": r[10] or "N/A",
                    "shift": r[11] or "N/A",
                    "recipe_name": r[12] or "N/A",
                    "machine_running": bool(r[13]),
                    "cycle_running": bool(r[14]),
                    "machine_mode": r[15] or "AUTO",
                    "plc_connected": bool(r[16]),
                })
            return results
    except Exception as e:
        logger.warning(f"Unable to query active alarm logs from database: {e}")
        return []
