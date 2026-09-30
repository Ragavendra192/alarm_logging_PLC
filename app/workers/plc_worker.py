"""
PLC Polling Worker Thread.

Continuously polls the Siemens PLC at 100ms intervals:
- Decodes 292-bit Boolean IO snapshot from DB 1000
- Decodes 57 Real (float32) actuals from Press 1 (DB1), Press 2 (DB2), Press 3 (DB3)
- Dispatches synchronized data snapshots to DataLogWorker.
"""

from datetime import datetime
import logging
import threading
import time
from typing import Any

from app.config import Config, get_current_swift
from app.plc.alarm_monitor import read_plc_alarms
from app.plc.alarm_scanner import AlarmScanner
from app.plc.client import SiemensPLC
from app.plc.press_actual import read_all_press_actuals
from app.workers.data_log_worker import DataLogWorker

logger = logging.getLogger("PLCDataCollector.PLCWorker")


class PLCWorker(threading.Thread):
    """Worker thread dedicated to high-frequency (100ms) PLC communication."""

    def __init__(self, data_log_worker: DataLogWorker | None = None):
        super().__init__(name="PLCWorker", daemon=True)
        self.plc = SiemensPLC()
        self.data_log_worker = data_log_worker
        self.alarm_scanner = AlarmScanner(
            db_number=Config.PLC_ALARM_DB,
            start_byte=Config.PLC_ALARM_START_BYTE,
            byte_count=Config.PLC_ALARM_BYTE_COUNT,
            db_fallback=Config.PLC_ALARM_DB_FALLBACK
        )

        self._running = threading.Event()
        self._running.set()

        self.plc_connected = False
        self._latest_io_snapshot: dict[str, int] = {}
        self._latest_press_actuals: dict[str, float] = {}
        self._latest_alarm_text: str = ""
        self._latest_alarm_active: bool = False
        self._latest_active_alarms: dict[str, dict[str, Any]] = {}
        self._prev_alarm_active: bool = False
        self._snapshot_lock = threading.Lock()
        self._last_log_time = 0.0

    def get_latest_snapshot(self) -> dict[str, int]:
        """Return a copy of the most recently read IO snapshot."""
        with self._snapshot_lock:
            return dict(self._latest_io_snapshot)

    def get_latest_press_actuals(self) -> dict[str, float]:
        """Return a copy of the most recently read 3-station press actual values."""
        with self._snapshot_lock:
            return dict(self._latest_press_actuals)

    def get_latest_alarm(self) -> tuple[bool, str]:
        """Return active alarm state and alarm text."""
        with self._snapshot_lock:
            return self._latest_alarm_active, self._latest_alarm_text

    def get_active_alarms(self) -> dict[str, dict[str, Any]]:
        """Return a copy of currently active alarms mapped by PLC address."""
        with self._snapshot_lock:
            return dict(self._latest_active_alarms)

    def run(self) -> None:
        """Main polling loop running at 100ms."""
        logger.info(f"PLCWorker thread started (Poll interval: {Config.PLC_POLL_INTERVAL*1000:.0f}ms).")

        while self._running.is_set():
            loop_start = time.perf_counter()
            try:
                # 1. Ensure connected
                if not self.plc.is_connected():
                    if self.plc_connected:
                        logger.warning("PLC disconnected! Attempting to reconnect...")
                        self.plc_connected = False

                    if not self.plc.connect():
                        time.sleep(Config.PLC_RECONNECT_DELAY)
                        continue

                    self.plc_connected = True
                    logger.info("PLC reconnected successfully!")

                # 2. Read 292-bit Boolean IO snapshot from DB 1000
                io_snapshot: dict[str, int] = {}
                try:
                    io_snapshot = self.plc.read_io_snapshot(Config.PLC_DB_NUMBER)
                except Exception as read_err:
                    logger.warning(f"Error reading PLC IO Data Block {Config.PLC_DB_NUMBER}: {read_err}")
                    self.plc_connected = False
                    self.plc.disconnect()
                    continue

                # 3. Read Press 1, 2, 3 actual Real values (DB 1, 2, 3)
                press_actuals: dict[str, float] = {}
                try:
                    press_actuals = read_all_press_actuals(self.plc.client)
                except Exception as press_err:
                    logger.debug(f"Error reading press actuals: {press_err}")

                # 4. Scan DB 101 Alarms via generic AlarmScanner
                active_alarms: dict[str, dict[str, Any]] = {}
                alarm_starts: list[dict[str, Any]] = []
                alarm_ends: list[dict[str, Any]] = []
                alarm_display = ""
                try:
                    active_alarms, alarm_starts, alarm_ends, alarm_display = self.alarm_scanner.scan_plc(self.plc.client)
                except Exception as alarm_err:
                    logger.debug(f"Error scanning alarms via AlarmScanner: {alarm_err}")

                # Fallback check to legacy alarm monitor if scanner found nothing
                if not active_alarms:
                    try:
                        legacy_active, legacy_text, _ = read_plc_alarms(
                            self.plc.client,
                            db_primary=Config.PLC_ALARM_DB,
                            db_fallback=Config.PLC_ALARM_DB_FALLBACK
                        )
                        if legacy_active and not alarm_display:
                            alarm_display = legacy_text
                    except Exception:
                        pass

                is_alarm_active = len(active_alarms) > 0 or bool(alarm_display)

                with self._snapshot_lock:
                    self._latest_io_snapshot = io_snapshot
                    self._latest_press_actuals = press_actuals
                    self._latest_alarm_active = is_alarm_active
                    self._latest_alarm_text = alarm_display
                    self._latest_active_alarms = active_alarms

                # 5. Handle Alarm Starts (Rising Edge: 0 -> 1)
                # When an alarm is triggered, immediately insert the new snapshot row with current parameters
                for start in alarm_starts:
                    alarm_text = f"{start['plc_address']} - {start['alarm_description']}"
                    logger.warning(f"🚨 ALARM TRIGGERED: {alarm_text}")
                    if self.data_log_worker:
                        # Record event in dbo.AlarmEvent
                        self.data_log_worker.enqueue_alarm_start(
                            alarm_data=start,
                            io_data=io_snapshot,
                            press_data=press_actuals,
                            timestamp=start.get("start_time"),
                            operator_name=Config.OPERATOR_NAME,
                            swift=Config.SWIFT or get_current_swift(),
                            recipe_name=Config.RECIPE_NAME,
                            machine_running=True,
                            cycle_running=False,
                            machine_mode=Config.MACHINE_MODE,
                            plc_connected=True,
                        )
                        # Record snapshot row with current parameter values to dbo.MachineDataLog
                        self.data_log_worker.enqueue_io_snapshot(
                            io_data=io_snapshot,
                            timestamp=start.get("start_time") or datetime.now(),
                            alarm=alarm_text,
                            operator_name=Config.OPERATOR_NAME,
                            swift=Config.SWIFT or get_current_swift(),
                            press_data=press_actuals,
                            table_name=Config.SQL_TABLE_NAME
                        )

                # 6. Handle Alarm Ends (Falling Edge: 1 -> 0)
                for end in alarm_ends:
                    logger.info(f"✅ ALARM CLEARED: {end['plc_address']} - {end['alarm_description']} (Duration: {end.get('duration_seconds', 0)}s)")
                    if self.data_log_worker:
                        self.data_log_worker.enqueue_alarm_end(
                            plc_address=end["plc_address"],
                            end_time=end.get("end_time"),
                            machine_number=self.data_log_worker.machine_id,
                        )

                # 7. Fallback rising edge trigger (if alarm became active without alarm_starts)
                if is_alarm_active and not self._prev_alarm_active:
                    if self.data_log_worker and not alarm_starts:
                        now_ts = datetime.now()
                        logger.warning(f"🚨 ALARM TRIGGERED (Fallback): Logging individual active alarms")
                        if active_alarms:
                            for addr, info in active_alarms.items():
                                self.data_log_worker.enqueue_alarm_start(
                                    alarm_data=info,
                                    io_data=io_snapshot,
                                    press_data=press_actuals,
                                    timestamp=now_ts,
                                    operator_name=Config.OPERATOR_NAME,
                                    swift=Config.SWIFT or get_current_swift(),
                                    recipe_name=Config.RECIPE_NAME,
                                    machine_running=True,
                                    cycle_running=False,
                                    machine_mode=Config.MACHINE_MODE,
                                    plc_connected=True,
                                )
                        elif alarm_display:
                            # Split legacy comma-separated display and log each alarm individually
                            parts = [p.strip() for p in alarm_display.split(",") if p.strip()]
                            for p in parts:
                                pseudo_info = {
                                    "plc_address": "DB101",
                                    "alarm_code": "ALM-FALLBACK",
                                    "alarm_description": p,
                                    "severity": "FAULT",
                                    "start_time": now_ts,
                                }
                                self.data_log_worker.enqueue_alarm_start(
                                    alarm_data=pseudo_info,
                                    io_data=io_snapshot,
                                    press_data=press_actuals,
                                    timestamp=now_ts,
                                    operator_name=Config.OPERATOR_NAME,
                                    swift=Config.SWIFT or get_current_swift(),
                                    recipe_name=Config.RECIPE_NAME,
                                    machine_running=True,
                                    cycle_running=False,
                                    machine_mode=Config.MACHINE_MODE,
                                    plc_connected=True,
                                )
                self._prev_alarm_active = is_alarm_active

                # 8. Dispatch periodic logging ONLY if continuous logging is explicitly enabled (disabled by default)
                if not Config.LOG_ON_ALARM_ONLY:
                    now = time.time()
                    if (now - self._last_log_time) >= Config.SQL_IO_LOG_INTERVAL:
                        self._last_log_time = now
                        if self.data_log_worker:
                            # Log if continuous mode OR if fault alarm is currently active
                            if not Config.LOG_ONLY_ON_FAULT or is_alarm_active:
                                self.data_log_worker.enqueue_io_snapshot(
                                    io_data=io_snapshot,
                                    timestamp=datetime.now(),
                                    alarm=alarm_display if is_alarm_active else None,
                                    operator_name=Config.OPERATOR_NAME,
                                    swift=Config.SWIFT or get_current_swift(),
                                    press_data=press_actuals
                                )

            except Exception as e:
                logger.error(f"Unexpected error in PLCWorker loop: {e}")

            # Precise sleep for remaining interval
            elapsed = time.perf_counter() - loop_start
            sleep_time = max(0.0, Config.PLC_POLL_INTERVAL - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Cleanup on stop
        self.plc.disconnect()
        logger.info("PLCWorker stopped.")

    def stop(self) -> None:
        """Signal worker thread to stop."""
        self._running.clear()
