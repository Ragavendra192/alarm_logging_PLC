"""
Generic PLC Alarm Scanner Module.

Performs high-speed block scanning of Siemens PLC DB101 (or configured DB):
- Reads configured block once per cycle: client.db_read(db_number, start, size)
- Scans all bytes and bits generically: data[byte_idx] & (1 << bit_idx)
- Resolves alarm metadata via AlarmMappingManager (with unmapped fallback)
- Performs rising-edge (0 -> 1) and falling-edge (1 -> 0) detection per bit
- Safe startup handling to prevent false alarm bursts on restart
"""

from datetime import datetime
import logging
import threading
from typing import Any

from app.config import Config
from app.plc.alarm_mapping import AlarmMappingManager

logger = logging.getLogger("PLCDataCollector.AlarmScanner")


def swap_bytes(data: bytes | bytearray) -> bytearray:
    """
    Swap adjacent bytes in the datablock (word byte-order swap: 0<->1, 2<->3, ...).
    Aligns byte indexes when PLC datablocks use Siemens word-swapped bit layout.
    """
    swapped = bytearray(data)
    for i in range(0, len(swapped) - 1, 2):
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
    return swapped


class AlarmScanner:
    """Generic bit-level PLC alarm scanner with edge detection."""

    def __init__(
        self,
        db_number: int | None = None,
        start_byte: int | None = None,
        byte_count: int | None = None,
        db_fallback: int | None = None,
        byte_swap: bool | None = None,
        mapping_manager: AlarmMappingManager | None = None,
    ):
        self.db_number = db_number if db_number is not None else Config.PLC_ALARM_DB
        self.start_byte = start_byte if start_byte is not None else Config.PLC_ALARM_START_BYTE
        self.byte_count = byte_count if byte_count is not None else Config.PLC_ALARM_BYTE_COUNT
        self.db_fallback = db_fallback if db_fallback is not None else Config.PLC_ALARM_DB_FALLBACK
        self.byte_swap = byte_swap if byte_swap is not None else Config.PLC_ALARM_BYTE_SWAP
        self.mapping_manager = mapping_manager or AlarmMappingManager()

        self._prev_states: dict[str, bool] = {}
        self._active_start_times: dict[str, datetime] = {}
        self._initialized = False
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Reset edge tracking states."""
        with self._lock:
            self._prev_states.clear()
            self._active_start_times.clear()
            self._initialized = False

    def scan_bytes(
        self,
        raw_bytes: bytes | bytearray,
        db_number: int | None = None,
        scan_time: datetime | None = None
    ) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], str]:
        """
        Scan a raw byte buffer for active alarm bits and detect state transitions.

        Returns:
            (active_alarms, alarm_starts, alarm_ends, alarm_display_str)
            - active_alarms: dict of currently active alarms keyed by plc_address
            - alarm_starts: list of newly triggered alarms (rising edge 0 -> 1)
            - alarm_ends: list of newly cleared alarms (falling edge 1 -> 0)
            - alarm_display_str: comma-separated text of all active alarms
        """
        db_num = db_number if db_number is not None else self.db_number
        ts = scan_time or datetime.now()
        data_to_scan = swap_bytes(raw_bytes) if self.byte_swap else raw_bytes
        total_len = len(data_to_scan)

        current_active: dict[str, dict[str, Any]] = {}
        alarm_starts: list[dict[str, Any]] = []
        alarm_ends: list[dict[str, Any]] = []

        with self._lock:
            for byte_idx in range(total_len):
                byte_val = data_to_scan[byte_idx]
                # If entire byte is zero, skip bit testing for speed
                if byte_val == 0:
                    for bit_idx in range(8):
                        plc_addr = f"DB{db_num}.DBX{byte_idx}.{bit_idx}"
                        prev = self._prev_states.get(plc_addr, False)
                        if prev:
                            # Alarm just cleared: 1 -> 0
                            start_time = self._active_start_times.pop(plc_addr, ts)
                            duration = max(0, int((ts - start_time).total_seconds()))
                            defn = self.mapping_manager.get_mapping(byte_idx, bit_idx, db_num)
                            alarm_ends.append({
                                "plc_address": plc_addr,
                                "db_number": db_num,
                                "byte_address": byte_idx,
                                "bit_address": bit_idx,
                                "alarm_code": defn.alarm_code if defn else "",
                                "alarm_description": defn.alarm_description if defn else f"UNMAPPED ALARM {plc_addr}",
                                "severity": defn.severity if defn else "FAULT",
                                "start_time": start_time,
                                "end_time": ts,
                                "duration_seconds": duration,
                            })
                            self._prev_states[plc_addr] = False
                    continue

                for bit_idx in range(8):
                    is_bit_set = bool(byte_val & (1 << bit_idx))
                    plc_addr = f"DB{db_num}.DBX{byte_idx}.{bit_idx}"
                    defn = self.mapping_manager.get_mapping(byte_idx, bit_idx, db_num)

                    # If definition is None, it was explicitly disabled
                    if defn is None:
                        is_bit_set = False

                    prev = self._prev_states.get(plc_addr, False)

                    if is_bit_set:
                        alarm_info = {
                            "plc_address": plc_addr,
                            "db_number": db_num,
                            "byte_address": byte_idx,
                            "bit_address": bit_idx,
                            "alarm_code": defn.alarm_code,
                            "alarm_description": defn.alarm_description,
                            "severity": defn.severity,
                        }
                        current_active[plc_addr] = alarm_info

                        if not prev:
                            # Rising edge: 0 -> 1 (including initial active alarms on startup)
                            self._active_start_times[plc_addr] = ts
                            alarm_starts.append({
                                **alarm_info,
                                "start_time": ts,
                            })

                        self._prev_states[plc_addr] = True

                    else:
                        if prev:
                            # Falling edge: 1 -> 0
                            start_time = self._active_start_times.pop(plc_addr, ts)
                            duration = max(0, int((ts - start_time).total_seconds()))
                            alarm_ends.append({
                                "plc_address": plc_addr,
                                "db_number": db_num,
                                "byte_address": byte_idx,
                                "bit_address": bit_idx,
                                "alarm_code": defn.alarm_code if defn else "",
                                "alarm_description": defn.alarm_description if defn else f"UNMAPPED ALARM {plc_addr}",
                                "severity": defn.severity if defn else "FAULT",
                                "start_time": start_time,
                                "end_time": ts,
                                "duration_seconds": duration,
                            })
                        self._prev_states[plc_addr] = False

            self._initialized = True

        display_parts = [
            f"{info['alarm_description']} ({addr})"
            for addr, info in current_active.items()
        ]
        alarm_display_str = ", ".join(display_parts) if display_parts else ""

        return current_active, alarm_starts, alarm_ends, alarm_display_str

    def scan_plc(
        self,
        client: Any,
        scan_time: datetime | None = None
    ) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], str]:
        """
        Read DB block once from PLC and perform full scan.
        Gracefully attempts smaller reads if PLC DB size is shorter than configured.
        Tries primary DB, then fallback DB on failure.
        """
        if client is None:
            return {}, [], [], ""

        raw_bytes = None
        used_db = self.db_number

        # Build descending candidate sizes to adapt to actual DB size
        candidate_sizes: list[int] = [self.byte_count]
        for s in (102, 64, 48, 34, 32, 16, 8, 4):
            if s not in candidate_sizes:
                candidate_sizes.append(s)

        # 1. Try Primary DB
        for size in candidate_sizes:
            try:
                raw_bytes = client.db_read(self.db_number, self.start_byte, size)
                break
            except Exception as e1:
                logger.debug(f"Primary alarm DB {self.db_number} size {size} read attempt failed: {e1}")

        # 2. Try Fallback DB if primary failed
        if raw_bytes is None and self.db_fallback:
            for size in candidate_sizes:
                try:
                    raw_bytes = client.db_read(self.db_fallback, self.start_byte, size)
                    used_db = self.db_fallback
                    break
                except Exception as e2:
                    logger.debug(f"Fallback alarm DB {self.db_fallback} size {size} read attempt failed: {e2}")

        if raw_bytes is None:
            return {}, [], [], ""

        return self.scan_bytes(raw_bytes, db_number=used_db, scan_time=scan_time)
