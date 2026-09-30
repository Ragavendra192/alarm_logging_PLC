"""
Script to split composite/concatenated alarm rows in dbo.AlarmResponse
into individual, separate rows in dbo.AlarmEvent.
"""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import re
from datetime import datetime
from app.database.db_connection import get_db_cursor
from app.plc.plc_tags import PLC_ADDRESSES
from app.plc.press_actual import ALL_PRESS_COLUMNS
from app.database.io_repository import save_alarm_event_start

def split_composite_alarm_response(row_id: int):
    with get_db_cursor(commit=True) as cur:
        cur.execute(f"SELECT * FROM dbo.AlarmResponse WHERE ID = {row_id}")
        col_names = [c[0] for c in cur.description]
        row = cur.fetchone()
        if not row:
            print(f"Row {row_id} not found in dbo.AlarmResponse")
            return

        data = dict(zip(col_names, row))
        raw_alarm = data.get("Alarm") or ""
        items = [a.strip() for a in raw_alarm.split(",") if a.strip()]
        print(f"Splitting Row {row_id} with {len(items)} composite alarms...")

        pattern = re.compile(r"^(.*?)\s*\((DB101\.DBX(\d+)\.(\d+))\)$")

        # Extract I/O and press actual data
        io_data = {}
        for addr in PLC_ADDRESSES:
            if addr in data:
                io_data[addr] = 1 if data[addr] else 0

        press_data = {}
        for col in ALL_PRESS_COLUMNS:
            if col in data and data[col] is not None:
                press_data[col] = float(data[col])

        ts = data.get("Timestamp") or datetime.now()
        op_name = data.get("OperatorName") or "Operator_1"
        swift = data.get("Swift") or "Shift 1"
        machine_num = data.get("MachineNumber") or "3_station"

        inserted = 0
        for item in items:
            m = pattern.match(item)
            if m:
                desc = m.group(1).strip()
                addr = m.group(2)
                byte_a = int(m.group(3))
                bit_a = int(m.group(4))
            else:
                desc = item
                addr = "DB101"
                byte_a = 0
                bit_a = 0

            alarm_payload = {
                "machine_number": machine_num,
                "plc_address": addr,
                "db_number": 101,
                "byte_address": byte_a,
                "bit_address": bit_a,
                "alarm_code": f"ALM-DB101-{byte_a:03d}{bit_a}",
                "alarm_description": desc,
                "severity": "FAULT",
                "start_time": ts,
                "operator_name": op_name,
                "swift": swift,
                "recipe_name": "DEFAULT",
                "machine_running": True,
                "cycle_running": False,
                "machine_mode": "AUTO",
                "plc_connected": True,
                "timestamp": ts,
                "io_data": io_data,
                "press_data": press_data,
            }

            save_alarm_event_start(alarm_payload, cursor=cur)
            inserted += 1

        print(f"Successfully inserted {inserted} individual records into dbo.AlarmEvent!")

        # Now delete the giant composite row from dbo.AlarmResponse
        cur.execute(f"DELETE FROM dbo.AlarmResponse WHERE ID = {row_id}")
        print(f"Deleted composite row {row_id} from dbo.AlarmResponse.")

if __name__ == "__main__":
    split_composite_alarm_response(93)
