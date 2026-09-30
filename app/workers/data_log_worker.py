"""
High-Speed Asynchronous Data Log Worker Thread.

Supports 100ms high-frequency logging into SQL Server for both
292 Boolean IO addresses and 57 3-station press actual Real metrics.
"""

from collections import deque
from datetime import datetime
import logging
import queue
import threading
import time
from typing import Any

from app.config import Config, get_current_swift
from app.database.db_connection import get_sql_connection
from app.database.io_repository import save_io_status, save_alarm_event_start, close_alarm_event

logger = logging.getLogger("PLCDataCollector.DataLogWorker")


class DataLogWorker(threading.Thread):
    """High-speed asynchronous SQL Server data logging thread."""

    def __init__(self, machine_id: str | None = None):
        super().__init__(name="DataLogWorker", daemon=True)
        self.machine_id = machine_id or Config.MACHINE_ID

        # Input queue for high-frequency snapshots
        self.queue: queue.Queue = queue.Queue(maxsize=5000)

        # Buffer for records queued during SQL Server downtime
        self.buffer: deque = deque(maxlen=Config.SQL_BUFFER_MAX_SIZE)

        self._running = threading.Event()
        self._running.set()

        self.sql_connected = False
        self._conn = None
        self._cursor = None
        self._last_reconnect_attempt = 0.0
        self._reconnect_interval = 3.0

    def enqueue_io_snapshot(
        self,
        io_data: dict[str, int],
        timestamp: datetime | None = None,
        alarm: str | None = None,
        operator_name: str | None = None,
        swift: str | None = None,
        press_data: dict[str, float] | None = None,
        table_name: str | None = None
    ) -> bool:
        """
        Non-blocking enqueue of an IO snapshot and press actuals from the 100ms PLC loop.
        Includes optional Alarm string for the new [Alarm] column following Timestamp.
        """
        item = {
            "event_type": "CONTINUOUS_IO",
            "machine_number": self.machine_id,
            "timestamp": timestamp or datetime.now(),
            "alarm": alarm or None,
            "operator_name": operator_name or Config.OPERATOR_NAME,
            "swift": swift or (Config.SWIFT or get_current_swift()),
            "data": io_data,
            "press_data": press_data or {},
            "table_name": table_name or None,
        }
        return self._put_queue(item)

    def enqueue_alarm_start(
        self,
        alarm_data: dict[str, Any],
        io_data: dict[str, int],
        press_data: dict[str, float] | None = None,
        timestamp: datetime | None = None,
        operator_name: str | None = None,
        swift: str | None = None,
        recipe_name: str | None = None,
        machine_running: bool = True,
        cycle_running: bool = False,
        machine_mode: str | None = None,
        plc_connected: bool = True,
    ) -> bool:
        """
        Enqueue an ALARM_START (rising edge 0 -> 1) event with full machine snapshot.
        Targeted for dbo.AlarmEvent.
        """
        ts = timestamp or datetime.now()
        event_payload = {
            "machine_number": self.machine_id,
            "plc_address": alarm_data.get("plc_address", "UNKNOWN"),
            "db_number": alarm_data.get("db_number", Config.PLC_ALARM_DB),
            "byte_address": alarm_data.get("byte_address", 0),
            "bit_address": alarm_data.get("bit_address", 0),
            "alarm_code": alarm_data.get("alarm_code"),
            "alarm_description": alarm_data.get("alarm_description"),
            "severity": alarm_data.get("severity", "FAULT"),
            "start_time": alarm_data.get("start_time") or ts,
            "operator_name": operator_name or Config.OPERATOR_NAME,
            "swift": swift or (Config.SWIFT or get_current_swift()),
            "recipe_name": recipe_name or Config.RECIPE_NAME,
            "machine_running": machine_running,
            "cycle_running": cycle_running,
            "machine_mode": machine_mode or Config.MACHINE_MODE,
            "plc_connected": plc_connected,
            "timestamp": ts,
            "io_data": dict(io_data),
            "press_data": dict(press_data or {}),
        }
        item = {
            "event_type": "ALARM_START",
            "event_data": event_payload,
        }
        logger.info(f"Queued ALARM_START event: {event_payload['plc_address']} - {event_payload['alarm_description']}")
        return self._put_queue(item)

    def enqueue_alarm_end(
        self,
        plc_address: str,
        end_time: datetime | None = None,
        machine_number: str | None = None
    ) -> bool:
        """
        Enqueue an ALARM_END (falling edge 1 -> 0) event.
        Targeted to update dbo.AlarmEvent with duration.
        """
        ts_end = end_time or datetime.now()
        item = {
            "event_type": "ALARM_END",
            "machine_number": machine_number or self.machine_id,
            "plc_address": plc_address,
            "end_time": ts_end,
        }
        logger.info(f"Queued ALARM_END event: {plc_address} at {ts_end}")
        return self._put_queue(item)

    def _put_queue(self, item: dict[str, Any]) -> bool:
        try:
            self.queue.put_nowait(item)
            return True
        except queue.Full:
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(item)
                return True
            except Exception:
                return False

    def enqueue_alarm_snapshot(
        self,
        alarm: str,
        io_data: dict[str, int],
        timestamp: datetime | None = None,
        operator_name: str | None = None,
        swift: str | None = None,
        press_data: dict[str, float] | None = None
    ) -> bool:
        """Enqueue dedicated fault alarm event snapshot for legacy dbo.AlarmResponse."""
        return self.enqueue_io_snapshot(
            io_data=io_data,
            timestamp=timestamp,
            alarm=alarm,
            operator_name=operator_name,
            swift=swift,
            press_data=press_data,
            table_name="AlarmResponse"
        )


    def run(self) -> None:
        """Main worker loop handling 100ms logging."""
        logger.info("DataLogWorker thread started (100ms logging pipeline).")

        self._ensure_connection()

        while self._running.is_set():
            try:
                # 1. Drain pending queue items into buffer
                items_drained = 0
                while items_drained < 50:
                    try:
                        item = self.queue.get_nowait()
                        self.buffer.append(item)
                        self.queue.task_done()
                        items_drained += 1
                    except queue.Empty:
                        break

                # 2. If nothing to process, wait briefly
                if not self.buffer:
                    time.sleep(0.02)
                    continue

                # 3. Ensure DB connection is active
                if not self._ensure_connection():
                    time.sleep(0.1)
                    continue

                # 4. Flush buffer using persistent connection
                self._flush_buffer()

            except Exception as e:
                logger.error(f"Error in DataLogWorker execution: {e}")
                self._close_connection()
                time.sleep(0.1)

        # Shutdown flush
        self._close_connection()
        logger.info("DataLogWorker stopped.")

    def stop(self) -> None:
        """Signal thread to stop."""
        self._running.clear()

    def _ensure_connection(self) -> bool:
        """Establish or maintain persistent connection to SQL Server."""
        if self._conn is not None and self._cursor is not None:
            return True

        now = time.time()
        if now - self._last_reconnect_attempt < self._reconnect_interval:
            return False

        self._last_reconnect_attempt = now
        try:
            self._conn = get_sql_connection()
            self._cursor = self._conn.cursor()
            if not self.sql_connected:
                logger.info("SQL Server status: CONNECTED")
                self.sql_connected = True
            return True
        except Exception as e:
            if self.sql_connected:
                logger.warning(f"SQL Server disconnected: {e}")
                self.sql_connected = False
            self._close_connection()
            return False

    def _close_connection(self) -> None:
        """Safely close active cursor and connection."""
        if self._cursor:
            try:
                self._cursor.close()
            except Exception:
                pass
            self._cursor = None
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _flush_buffer(self) -> None:
        """Insert buffered records in batch, handling both continuous data and alarm events."""
        if not self.buffer or not self._cursor or not self._conn:
            return

        batch_count = 0
        try:
            while self.buffer and batch_count < 100:
                item = self.buffer[0]
                event_type = item.get("event_type", "CONTINUOUS_IO")

                if event_type == "ALARM_START":
                    save_alarm_event_start(
                        event_data=item["event_data"],
                        cursor=self._cursor
                    )
                elif event_type == "ALARM_END":
                    close_alarm_event(
                        machine_number=item["machine_number"],
                        plc_address=item["plc_address"],
                        end_time=item.get("end_time"),
                        cursor=self._cursor
                    )
                else:
                    # CONTINUOUS_IO or legacy ALARM_SNAPSHOT
                    save_io_status(
                        machine_number=item["machine_number"],
                        timestamp=item["timestamp"],
                        io_data=item["data"],
                        alarm=item.get("alarm"),
                        operator_name=item["operator_name"],
                        swift=item["swift"],
                        press_data=item["press_data"],
                        table_name=item.get("table_name"),
                        cursor=self._cursor
                    )

                self.buffer.popleft()
                batch_count += 1

            # Commit batch
            self._conn.commit()

        except Exception as e:
            logger.warning(f"SQL insert batch error: {e}")
            self.sql_connected = False
            self._close_connection()
