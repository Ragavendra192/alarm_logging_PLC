"""
Automated Test Suite for Automatic PLC Alarm Detection (DB 101) -> SQL Server (dbo.AlarmEvent).

Validates:
1. Generic bit scanner for DB101.
2. Unmapped alarm handling and naming.
3. Mapped alarm metadata resolution.
4. Rising edge detection (0 -> 1): exactly 1 event created.
5. Holding state (1 -> 1): 0 duplicate events.
6. Falling edge detection (1 -> 0): open event closed, duration calculated.
7. Multiple alarms active simultaneously and tracked independently.
8. Full machine snapshot capture (292 IO bit columns + 57 Press Real columns).
9. Active alarms query (AlarmEndTime IS NULL) and active count.
10. DataLogWorker asynchronous queueing and resilient batch flushing.
"""

from datetime import datetime, timedelta
import time
import unittest

from app.config import Config
from app.database.db_connection import get_db_cursor, test_sql_connection
from app.database.db_initializer import initialize_database
from app.database.io_repository import (
    close_alarm_event,
    get_active_alarm_count,
    get_active_alarm_events,
    save_alarm_event_start,
)
from app.plc.alarm_mapping import AlarmMappingManager
from app.plc.alarm_scanner import AlarmScanner
from app.plc.plc_tags import PLC_ADDRESSES
from app.plc.press_actual import ALL_PRESS_COLUMNS
from app.workers.data_log_worker import DataLogWorker


class TestAlarmEvents(unittest.TestCase):
    """Unit and integration test suite for DB101 alarm detection and SQL Server persistence."""

    @classmethod
    def setUpClass(cls):
        initialize_database()
        cls.test_machine = "TEST_ALARM_SUITE_MCH"

    @classmethod
    def tearDownClass(cls):
        with get_db_cursor(commit=True) as cur:
            cur.execute("DELETE FROM dbo.AlarmEvent WHERE MachineNumber = ?", (cls.test_machine,))
            cur.execute("DELETE FROM dbo.AlarmResponse WHERE MachineNumber = ?", (cls.test_machine,))

    def setUp(self):
        with get_db_cursor(commit=True) as cur:
            cur.execute("DELETE FROM dbo.AlarmEvent WHERE MachineNumber = ?", (self.test_machine,))
            cur.execute("DELETE FROM dbo.AlarmResponse WHERE MachineNumber = ?", (self.test_machine,))

    def test_01_alarm_mapping_mapped_and_unmapped(self):
        """Verify mapping manager returns mapped seed descriptions and unmapped fallback."""
        manager = AlarmMappingManager()

        # Seed mapping: Byte 20, Bit 3 -> Hydraulic Pump Overload
        mapped = manager.get_mapping(20, 3, db_number=101)
        self.assertIsNotNone(mapped)
        self.assertEqual(mapped.plc_address, "DB101.DBX20.3")
        self.assertEqual(mapped.alarm_code, "ALM-0203")
        self.assertEqual(mapped.alarm_description, "Hydraulic Pump Overload")
        self.assertEqual(mapped.severity, "FAULT")

        # Unmapped bit: Byte 30, Bit 2
        unmapped = manager.get_mapping(30, 2, db_number=101)
        self.assertIsNotNone(unmapped)
        self.assertEqual(unmapped.plc_address, "DB101.DBX30.2")
        self.assertIn("UNMAPPED ALARM", unmapped.alarm_description)
        self.assertEqual(unmapped.severity, "FAULT")

    def test_02_alarm_scanner_transitions_single_alarm(self):
        """Verify edge detection: 0->1 generates start, 1->1 generates nothing, 1->0 generates end."""
        scanner = AlarmScanner(db_number=101, byte_count=64)
        buf = bytearray(64)

        # Baseline scan (0 -> 0)
        active, starts, ends, txt = scanner.scan_bytes(buf)
        self.assertEqual(len(active), 0)
        self.assertEqual(len(starts), 0)
        self.assertEqual(len(ends), 0)

        # Rising edge: turn on DB101.DBX20.3 (0 -> 1)
        buf[20] |= (1 << 3)
        active, starts, ends, txt = scanner.scan_bytes(buf)
        self.assertEqual(len(active), 1)
        self.assertEqual(len(starts), 1)
        self.assertEqual(len(ends), 0)
        self.assertEqual(starts[0]["plc_address"], "DB101.DBX20.3")
        self.assertEqual(starts[0]["alarm_description"], "Hydraulic Pump Overload")

        # Holding state: keep on DB101.DBX20.3 (1 -> 1)
        active, starts, ends, txt = scanner.scan_bytes(buf)
        self.assertEqual(len(active), 1)
        self.assertEqual(len(starts), 0, "Holding active alarm must not generate duplicate start event")
        self.assertEqual(len(ends), 0)

        # Falling edge: turn off DB101.DBX20.3 (1 -> 0)
        buf[20] &= ~(1 << 3)
        active, starts, ends, txt = scanner.scan_bytes(buf)
        self.assertEqual(len(active), 0)
        self.assertEqual(len(starts), 0)
        self.assertEqual(len(ends), 1)
        self.assertEqual(ends[0]["plc_address"], "DB101.DBX20.3")

    def test_03_sql_persistence_db101_dbx20_3_lifecycle(self):
        """Test full lifecycle in SQL Server for primary test alarm DB101.DBX20.3."""
        plc_addr = "DB101.DBX20.3"
        start_time = datetime.now() - timedelta(seconds=25)

        io_snap = {addr: 0 for addr in PLC_ADDRESSES}
        io_snap["0.0"] = 1
        io_snap["36.3"] = 1

        press_snap = {col: 0.0 for col in ALL_PRESS_COLUMNS}
        press_snap["P1 MAIN RAM POSITION"] = 350.5
        press_snap["P2 MAIN RAM POSITION"] = 180.2

        # 1. Rising edge start
        event_payload = {
            "machine_number": self.test_machine,
            "plc_address": plc_addr,
            "db_number": 101,
            "byte_address": 20,
            "bit_address": 3,
            "alarm_code": "ALM-0203",
            "alarm_description": "Hydraulic Pump Overload",
            "severity": "FAULT",
            "start_time": start_time,
            "operator_name": "Test_Operator",
            "swift": "Shift 1",
            "recipe_name": "Recipe_Alpha",
            "machine_running": True,
            "cycle_running": False,
            "machine_mode": "AUTO",
            "plc_connected": True,
            "io_data": io_snap,
            "press_data": press_snap,
        }
        rows = save_alarm_event_start(event_payload)
        self.assertEqual(rows, 1, "save_alarm_event_start must insert exactly 1 row")

        # 2. Verify active in SQL
        active_list = get_active_alarm_events(self.test_machine)
        self.assertEqual(len(active_list), 1)
        self.assertEqual(active_list[0]["PLCAddress"], plc_addr)
        self.assertEqual(active_list[0]["AlarmCode"], "ALM-0203")
        self.assertEqual(active_list[0]["AlarmDescription"], "Hydraulic Pump Overload")

        count = get_active_alarm_count(self.test_machine)
        self.assertEqual(count, 1)

        # 3. Falling edge end
        end_time = datetime.now()
        closed = close_alarm_event(self.test_machine, plc_addr, end_time=end_time)
        self.assertEqual(closed, 1)

        # 4. Verify closed in SQL
        active_after = get_active_alarm_events(self.test_machine)
        self.assertEqual(len(active_after), 0)

        with get_db_cursor(commit=False) as cur:
            cur.execute("""
                SELECT AlarmStartTime, AlarmEndTime, AlarmDurationSeconds, [0.0], [36.3], [P1 MAIN RAM POSITION]
                FROM dbo.AlarmEvent
                WHERE MachineNumber = ? AND PLCAddress = ?
            """, (self.test_machine, plc_addr))
            row = cur.fetchone()

        self.assertIsNotNone(row)
        self.assertIsNotNone(row[1], "AlarmEndTime must be populated")
        self.assertGreaterEqual(row[2], 24, "AlarmDurationSeconds must be ~25 seconds")
        self.assertEqual(row[3], 1, "IO bit [0.0] must be preserved")
        self.assertEqual(row[4], 1, "IO bit [36.3] must be preserved")
        self.assertAlmostEqual(row[5], 350.5, places=1, msg="Press actual metric must be preserved")

    def test_04_multiple_concurrent_alarms(self):
        """Verify multiple alarms active simultaneously: DB101.DBX20.3, DB101.DBX21.3, DB101.DBX22.3."""
        addrs = ["DB101.DBX20.3", "DB101.DBX21.3", "DB101.DBX22.3"]
        now = datetime.now()

        for idx, addr in enumerate(addrs):
            save_alarm_event_start({
                "machine_number": self.test_machine,
                "plc_address": addr,
                "db_number": 101,
                "byte_address": 20 + idx,
                "bit_address": 3,
                "alarm_code": f"ALM-02{idx}3",
                "alarm_description": f"Fault on {addr}",
                "severity": "FAULT",
                "start_time": now - timedelta(seconds=10 * (idx + 1)),
                "io_data": {},
                "press_data": {},
            })

        # Verify 3 active alarms
        self.assertEqual(get_active_alarm_count(self.test_machine), 3)

        # Clear only the middle one: DB101.DBX21.3
        close_alarm_event(self.test_machine, "DB101.DBX21.3", end_time=datetime.now())

        # Verify 2 active alarms remain
        active_list = get_active_alarm_events(self.test_machine)
        active_addrs = {r["PLCAddress"] for r in active_list}
        self.assertEqual(len(active_addrs), 2)
        self.assertIn("DB101.DBX20.3", active_addrs)
        self.assertIn("DB101.DBX22.3", active_addrs)
        self.assertNotIn("DB101.DBX21.3", active_addrs)

        # Clear remaining
        close_alarm_event(self.test_machine, "DB101.DBX20.3", end_time=datetime.now())
        close_alarm_event(self.test_machine, "DB101.DBX22.3", end_time=datetime.now())
        self.assertEqual(get_active_alarm_count(self.test_machine), 0)

    def test_05_unmapped_alarm_logging(self):
        """Verify unmapped alarm bit is automatically named and persisted."""
        unmapped_addr = "DB101.DBX45.7"
        now = datetime.now()

        save_alarm_event_start({
            "machine_number": self.test_machine,
            "plc_address": unmapped_addr,
            "db_number": 101,
            "byte_address": 45,
            "bit_address": 7,
            "alarm_code": "ALM-DB101-0457",
            "alarm_description": f"UNMAPPED ALARM {unmapped_addr}",
            "severity": "FAULT",
            "start_time": now,
            "io_data": {},
            "press_data": {},
        })

        active = get_active_alarm_events(self.test_machine)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["PLCAddress"], unmapped_addr)
        self.assertEqual(active[0]["AlarmDescription"], f"UNMAPPED ALARM {unmapped_addr}")

        close_alarm_event(self.test_machine, unmapped_addr, end_time=now + timedelta(seconds=5))
        self.assertEqual(get_active_alarm_count(self.test_machine), 0)

    def test_06_datalogworker_queue_and_resilient_flush(self):
        """Verify DataLogWorker receives ALARM_START and ALARM_END via queue and flushes safely."""
        worker = DataLogWorker(machine_id=self.test_machine)
        worker.start()

        try:
            plc_addr = "DB101.DBX20.3"
            start_ts = datetime.now()

            # Enqueue start
            worker.enqueue_alarm_start(
                alarm_data={
                    "plc_address": plc_addr,
                    "db_number": 101,
                    "byte_address": 20,
                    "bit_address": 3,
                    "alarm_code": "ALM-0203",
                    "alarm_description": "Hydraulic Pump Overload",
                    "severity": "FAULT",
                    "start_time": start_ts,
                },
                io_data={PLC_ADDRESSES[0]: 1},
                press_data={ALL_PRESS_COLUMNS[0]: 99.9}
            )

            # Wait for worker loop to drain and commit
            time.sleep(0.3)
            active = get_active_alarm_events(self.test_machine)
            self.assertEqual(len(active), 1, "DataLogWorker must persist ALARM_START to SQL Server")
            self.assertEqual(active[0]["PLCAddress"], plc_addr)

            # Enqueue end
            worker.enqueue_alarm_end(
                plc_address=plc_addr,
                end_time=datetime.now(),
                machine_number=self.test_machine
            )

            time.sleep(0.3)
            active_after = get_active_alarm_events(self.test_machine)
            self.assertEqual(len(active_after), 0, "DataLogWorker must close ALARM_END in SQL Server")

        finally:
            worker.stop()
            worker.join(timeout=2.0)

    def test_11_alarm_trigger_inserts_row_to_machine_data_log(self):
        """Verify that on alarm trigger, a snapshot row is inserted into MachineDataLog with current parameters."""
        worker = DataLogWorker(machine_id=self.test_machine)
        worker.start()

        try:
            test_ts = datetime.now()
            alarm_desc = "DB101.DBX18.0 - OIL LEVEL LOW TEST"
            test_io = {PLC_ADDRESSES[0]: 1, PLC_ADDRESSES[1]: 0}
            test_press = {ALL_PRESS_COLUMNS[0]: 123.45}

            # Enqueue snapshot for MachineDataLog on alarm trigger
            success = worker.enqueue_io_snapshot(
                io_data=test_io,
                timestamp=test_ts,
                alarm=alarm_desc,
                operator_name="TestOperator",
                swift="Shift A",
                press_data=test_press,
                table_name="MachineDataLog"
            )
            self.assertTrue(success)

            # Wait for worker loop to drain and commit
            time.sleep(0.4)

            with get_db_cursor(commit=False) as cur:
                cur.execute(f"""
                    SELECT TOP 1 [Alarm], OperatorName, Swift, [0.0], [{ALL_PRESS_COLUMNS[0]}]
                    FROM dbo.MachineDataLog
                    WHERE MachineNumber = ?
                    ORDER BY Id DESC
                """, (self.test_machine,))
                row = cur.fetchone()

            self.assertIsNotNone(row, "MachineDataLog must have a newly inserted row on alarm trigger")
            self.assertEqual(row[0], alarm_desc)
            self.assertEqual(row[1], "TestOperator")
            self.assertEqual(row[2], "Shift A")
            self.assertEqual(row[3], 1)
            self.assertAlmostEqual(float(row[4]), 123.45, places=2)

        finally:
            worker.stop()
            worker.join(timeout=2.0)
            with get_db_cursor(commit=True) as cur:
                cur.execute("DELETE FROM dbo.MachineDataLog WHERE MachineNumber = ?", (self.test_machine,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
