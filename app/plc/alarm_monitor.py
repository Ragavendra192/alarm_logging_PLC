"""
PLC Alarm Monitor Module.

Decodes alarm and fault statuses from Siemens PLC DBALARM (DB 101 / DB 1011):
- FaultBit 1 to 6 (Offsets 5.2 to 5.7)
- P1 FAULT ONLY, P2 FAULT ONLY, P3 FAULT ONLY (Offsets 6.0 to 6.2)
- FaultBit 10 (Offset 6.3)
- FAULTWORD1 through FAULTWORD9 (Offsets 8.0 to 24.0)
- COMMONFAULTWORD (Offset 26.0)
- WARNINGWORD1 through WARNINGWORD3 (Offsets 28.0 to 32.0)

Provides:
- parse_alarm_bytes(): Decodes 34-byte raw buffer into active alarms and display string
- read_plc_alarms(): Safe PLC reader attempting DB 101 then DB 1011
"""

import logging
import struct
from typing import Any

logger = logging.getLogger("PLCDataCollector.AlarmMonitor")

# Named Boolean fault bits: (byte_index, bit_index, label)
FAULT_BITS = [
    (5, 2, "FaultBit 1"),
    (5, 3, "FaultBit 2"),
    (5, 4, "FaultBit 3"),
    (5, 5, "FaultBit 4"),
    (5, 6, "FaultBit 5"),
    (5, 7, "FaultBit 6"),
    (6, 0, "P1 FAULT ONLY"),
    (6, 1, "P2 FAULT ONLY"),
    (6, 2, "P3 FAULT ONLY"),
    (6, 3, "FaultBit 10"),
]

# Named 16-bit fault words: (byte_offset, label)
FAULT_WORDS = [
    (8, "FAULTWORD1"),
    (10, "FAULTWORD2"),
    (12, "FAULTWORD3"),
    (14, "FAULTWORD4"),
    (16, "FAULTWORD5"),
    (18, "FAULTWORD6"),
    (20, "FAULTWORD7"),
    (22, "FAULTWORD8"),
    (24, "FAULTWORD9"),
    (26, "COMMONFAULTWORD"),
]

# Warning words: (byte_offset, label)
WARNING_WORDS = [
    (28, "WARNINGWORD1"),
    (30, "WARNINGWORD2"),
    (32, "WARNINGWORD3"),
]


def parse_alarm_bytes(data: bytes | bytearray) -> tuple[bool, str, dict[str, Any]]:
    """
    Parse a 34-byte DBALARM buffer.

    Returns:
        (is_fault_active, alarm_display_str, details_dict)
        - is_fault_active: True if any fault bit or fault word is non-zero
        - alarm_display_str: Human-readable alarm text for the [Alarm] column
        - details_dict: Complete map of all bit and word values
    """
    if len(data) < 34:
        return False, "", {}

    active_alarms: list[str] = []
    details: dict[str, Any] = {}

    # 1. Check Boolean Fault Bits
    for byte_idx, bit_idx, label in FAULT_BITS:
        val = bool(data[byte_idx] & (1 << bit_idx))
        details[label] = val
        if val:
            active_alarms.append(label)

    # 2. Check 16-bit Fault Words (Big-Endian UInt16)
    for byte_offset, label in FAULT_WORDS:
        word_val = struct.unpack_from(">H", data, byte_offset)[0]
        details[label] = word_val
        if word_val != 0:
            active_alarms.append(f"{label}:0x{word_val:04X}")

    # 3. Check Warning Words
    for byte_offset, label in WARNING_WORDS:
        word_val = struct.unpack_from(">H", data, byte_offset)[0]
        details[label] = word_val

    is_active = len(active_alarms) > 0
    alarm_display = ", ".join(active_alarms) if active_alarms else ""

    return is_active, alarm_display, details


def read_plc_alarms(
    client: Any,
    db_primary: int = 101,
    db_fallback: int = 1011
) -> tuple[bool, str, dict[str, Any]]:
    """
    Attempt to read 34 bytes of alarm data from Siemens PLC.
    First tries db_primary (DB 101); if optimized (0x05) or missing, tries db_fallback (DB 1011).
    Gracefully handles errors.
    """
    if client is None:
        return False, "", {}

    # Try Primary Alarm DB
    try:
        data = client.db_read(db_primary, 0, 34)
        return parse_alarm_bytes(data)
    except Exception as e:
        logger.debug(f"Primary alarm DB {db_primary} read failed ({e}); attempting fallback DB {db_fallback}")

    # Try Fallback Alarm DB
    try:
        data = client.db_read(db_fallback, 0, 34)
        return parse_alarm_bytes(data)
    except Exception as e2:
        logger.debug(f"Fallback alarm DB {db_fallback} read failed ({e2})")

    return False, "", {}
