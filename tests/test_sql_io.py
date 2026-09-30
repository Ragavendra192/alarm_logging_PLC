"""
Automated Verification and Test Suite for SQL Server Data Logging,
IOStatus, and 3-Station Press Actual Real Metrics.
"""

from datetime import datetime
import struct
import time
import unittest

from app.config import Config
from app.database.db_connection import get_db_cursor, test_sql_connection
from app.database.db_initializer import initialize_database
from app.database.io_repository import get_latest_io_status, save_alarm_snapshot, save_io_status
from app.plc.alarm_monitor import parse_alarm_bytes
from app.plc.client import SiemensPLC
from app.plc.plc_tags import PLC_ADDRESSES, parse_io_bytes
from app.plc.press_actual import ALL_PRESS_COLUMNS, P1_TAGS, read_all_press_actuals
from app.workers.data_log_worker import DataLogWorker


class TestSQLDataLogging(unittest.TestCase):
    """Test suite for SQL Server integration."""

    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_01_sql_connection(self):
        """Verify SQL Server connectivity."""
        ok, msg = test_sql_connection()
        self.assertTrue(ok, f"SQL Server connection failed: {msg}")

    def test_02_database_schema_356_columns(self):
        """Verify MachineDataLog has Timestamp, Alarm, Operator, Swift, 292 IO bits, and 57 Press Reals."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'MachineDataLog'
            """)
            rows = cursor.fetchall()
            col_map = {r[0]: r[1] for r in rows}

        self.assertIn("Id", col_map)
        self.assertIn("MachineNumber", col_map)
        self.assertIn("Timestamp", col_map)
        self.assertIn("Alarm", col_map)
        self.assertIn("OperatorName", col_map)
        self.assertIn("Swift", col_map)
        self.assertIn("CreatedAt", col_map)

        # 292 IO bits
        for addr in PLC_ADDRESSES:
            self.assertIn(addr, col_map)
            self.assertEqual(col_map[addr].lower(), "bit")

        # 57 Press Real columns
        for col in ALL_PRESS_COLUMNS:
            self.assertIn(col, col_map)
            self.assertEqual(col_map[col].lower(), "real")

        self.assertEqual(len(col_map), 356)

    def test_03_io_bytes_parsing(self):
        """Verify parsing 37 raw PLC bytes into 292 bit values (0 and 1)."""
        raw = bytearray(37)
        raw[0] = 0b00000101   # 0.0=1, 0.2=1
        raw[36] = 0b00001001  # 36.0=1, 36.3=1

        parsed = parse_io_bytes(raw)
        self.assertEqual(len(parsed), 292)
        self.assertEqual(parsed["0.0"], 1)
        self.assertEqual(parsed["0.1"], 0)
        self.assertEqual(parsed["0.2"], 1)
        self.assertEqual(parsed["36.0"], 1)
        self.assertEqual(parsed["36.3"], 1)

    def test_04_save_and_read_io_with_press_actuals_and_alarm(self):
        """Insert a test snapshot with Alarm, OperatorName, Swift, IO, and Press Actuals."""
        test_machine = "TEST_PRESS_100MS"
        test_op = "Operator_Beta"
        test_swift = "Shift 1"
        test_alarm = "P1 FAULT ONLY, FAULTWORD1:0x800B"
        test_io = {addr: 0 for addr in PLC_ADDRESSES}
        test_io["0.0"] = 1
        test_io["36.3"] = 1

        test_press = {col: 0.0 for col in ALL_PRESS_COLUMNS}
        test_press["P1 MAIN RAM POSITION"] = 396.0
        test_press["P1 CYCLE TIME"] = 12.484
        test_press["P2 MAIN RAM POSITION"] = 235.0
        test_press["P3 MAIN RAM POSITION"] = 194.0

        test_ts = datetime.now()

        # Insert
        saved = save_io_status(
            machine_number=test_machine,
            timestamp=test_ts,
            io_data=test_io,
            alarm=test_alarm,
            operator_name=test_op,
            swift=test_swift,
            press_data=test_press
        )
        self.assertEqual(saved, 1, "save_io_status should insert 1 row")

        # Query latest
        latest = get_latest_io_status(test_machine)
        self.assertIsNotNone(latest, "get_latest_io_status returned None")
        self.assertEqual(latest["OperatorName"], test_op)
        self.assertEqual(latest["Swift"], test_swift)
        self.assertEqual(latest["Alarm"], test_alarm)
        self.assertEqual(latest["0.0"], 1)
        self.assertEqual(latest["36.3"], 1)
        self.assertAlmostEqual(latest["P1 MAIN RAM POSITION"], 396.0, places=2)
        self.assertAlmostEqual(latest["P1 CYCLE TIME"], 12.484, places=2)
        self.assertAlmostEqual(latest["P2 MAIN RAM POSITION"], 235.0, places=2)
        self.assertAlmostEqual(latest["P3 MAIN RAM POSITION"], 194.0, places=2)

        # Cleanup test row
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(f"DELETE FROM dbo.{Config.SQL_TABLE_NAME} WHERE MachineNumber = ?", (test_machine,))

    def test_05_read_live_plc_db1_actuals(self):
        """Verify reading DB 1 live from connected PLC."""
        plc = SiemensPLC()
        if not plc.connect():
            self.skipTest("PLC not currently connected; skipping live PLC read test")

        try:
            actuals = read_all_press_actuals(plc.client)
            self.assertEqual(len(actuals), 57)
            self.assertIn("P1 MAIN RAM POSITION", actuals)
        finally:
            plc.disconnect()

    def test_06_alarm_bytes_parsing(self):
        """Verify parsing DBALARM 34-byte buffer matching TIA Portal snapshot."""
        buf = bytearray(34)
        buf[5] = (1 << 2) | (1 << 3)  # FaultBit 1, FaultBit 2
        buf[6] = (1 << 0)             # P1 FAULT ONLY
        struct.pack_into(">H", buf, 8, 0x800B)  # FAULTWORD1

        is_active, display, details = parse_alarm_bytes(buf)
        self.assertTrue(is_active)
        self.assertIn("FaultBit 1", display)
        self.assertIn("FaultBit 2", display)
        self.assertIn("P1 FAULT ONLY", display)
        self.assertIn("FAULTWORD1:0x800B", display)

    def test_07_save_alarm_snapshot_to_alarm_response(self):
        """Verify saving full 356-column fault snapshot into dbo.AlarmResponse."""
        test_machine = "TEST_ALARM_CAPTURE"
        test_alarm = "P1 FAULT ONLY"
        test_io = {addr: 1 for addr in PLC_ADDRESSES}
        test_press = {col: 100.5 for col in ALL_PRESS_COLUMNS}
        test_ts = datetime.now()

        saved = save_alarm_snapshot(
            machine_number=test_machine,
            timestamp=test_ts,
            alarm=test_alarm,
            io_data=test_io,
            operator_name="Test_Op",
            swift="Shift 1",
            press_data=test_press
        )
        self.assertEqual(saved, 1, "save_alarm_snapshot should insert 1 row into AlarmResponse")

        # Verify record in AlarmResponse
        with get_db_cursor(commit=False) as cur:
            cur.execute("""
                SELECT TOP 1 MachineNumber, [Alarm], [0.0], [P1 MAIN RAM POSITION]
                FROM dbo.AlarmResponse
                WHERE MachineNumber = ?
                ORDER BY [Timestamp] DESC
            """, (test_machine,))
            row = cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], test_machine)
        self.assertEqual(row[1], test_alarm)
        self.assertEqual(row[2], True)
        self.assertAlmostEqual(row[3], 100.5, places=1)

        # Cleanup
        with get_db_cursor(commit=True) as cur:
            cur.execute("DELETE FROM dbo.AlarmResponse WHERE MachineNumber = ?", (test_machine,))


if __name__ == "__main__":
    unittest.main(verbosity=2)

