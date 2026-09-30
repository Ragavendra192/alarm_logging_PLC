"""
Press Actual Values Extraction Module.

Reads 32-bit floating point (IEEE 754 Real) metrics from Siemens PLC Data Blocks:
- Press 1 (P1): DB 1 (Offsets 0.0 to 72.0)
- Press 2 (P2): DB 2 (Offsets 0.0 to 72.0)
- Press 3 (P3): DB 3 (Offsets 0.0 to 72.0)
"""

import logging
import snap7.util

logger = logging.getLogger("PLCDataCollector.PressActual")

# Press 1 (DB 1) Tags and Offsets
P1_TAGS = [
    ("MAIN RAM PRESSURE", 0),
    ("MAIN RAM POSITION", 4),
    ("DIECUSHION PRESSURE", 8),
    ("DIECUSHION POSITION", 12),
    ("DAMPUR PRESSURE", 16),
    ("OIL LVEL LOW", 20),
    ("OIL TEMP HIGH", 24),
    ("CYCLE TIME", 28),
    ("DWELL TIME", 32),
    ("PRV.CYCLE TIME", 36),
    ("SHIFT COUNT", 40),
    ("CUMM COUNT", 44),
    ("MACHINE LIFE COUNT", 48),
    ("MAIN RAM TONNAGE", 52),
    ("DC TONNAGE", 56),
    ("PUMP 1 PRESSURE TRANSDUCER", 60),
    ("PUMP 2 PRESSURE TRANSDUCER", 64),
    ("PUMP 3 PRESSURE TRANSDUCER", 68),
    ("MAIN RAM B-LINE PRESSURE TRANSDUCER", 72),
]

# Press 2 (DB 2) Tags and Offsets
P2_TAGS = [
    ("MAIN RAM PRESSURE", 0),
    ("MAIN RAM POSITION", 4),
    ("DIECUSHION PRESSURE", 8),
    ("DIECUSHION POSITION", 12),
    ("DAMPUR PRESSURE", 16),
    ("OIL LVEL LOW", 20),
    ("OIL TEMP HIGH", 24),
    ("CYCLE TIME", 28),
    ("DWELL TIME", 32),
    ("PRV.CYCLE TIME", 36),
    ("SHIFT COUNT", 40),
    ("CUMM COUNT", 44),
    ("MACHINE LIFE COUNT", 48),
    ("MAIN RAM TONNAGE", 52),
    ("DC TONNAGE", 56),
    ("PUMP 4 PRESSURE TRANSDUCER", 60),
    ("PUMP 5 PRESSURE TRANSDUCER", 64),
    ("PUMP 6 PRESSURE TRANSDUCER", 68),
    ("MAIN RAM B-LINE PRESSURE TRANSDUCER", 72),
]

# Press 3 (DB 3) Tags and Offsets
P3_TAGS = [
    ("MAIN RAM PRESSURE", 0),
    ("MAIN RAM POSITION", 4),
    ("DIECUSHION PRESSURE", 8),
    ("DIECUSHION POSITION", 12),
    ("DAMPUR PRESSURE", 16),
    ("OIL LVEL LOW", 20),
    ("OIL TEMP HIGH", 24),
    ("CYCLE TIME", 28),
    ("DWELL TIME", 32),
    ("PRV.CYCLE TIME", 36),
    ("SHIFT COUNT", 40),
    ("CUMM COUNT", 44),
    ("MACHINE LIFE COUNT", 48),
    ("MAIN RAM TONNAGE", 52),
    ("DC TONNAGE", 56),
    ("PUMP 7 PRESSURE TRANSDUCER", 60),
    ("PUMP 8 PRESSURE TRANSDUCER", 64),
    ("PUMP 9 PRESSURE TRANSDUCER", 68),
    ("MAIN RAM B-LINE PRESSURE TRANSDUCER", 72),
]

# Mapping of press identifier to default DB number and tag definition
PRESS_CONFIG = {
    "P1": {"db": 1000, "start_byte": 200, "fallback_db": 1, "tags": P1_TAGS},
    "P2": {"db": 1001, "start_byte": 228, "fallback_db": 2, "tags": P2_TAGS},
    "P3": {"db": 1001, "start_byte": 268, "fallback_db": 3, "tags": P3_TAGS},
}

# Complete list of 57 column names formatted for SQL Server
ALL_PRESS_COLUMNS: list[str] = []
for press, cfg in PRESS_CONFIG.items():
    for name, _ in cfg["tags"]:
        ALL_PRESS_COLUMNS.append(f"{press} {name}")

# Total bytes required to read offset 0 through 75 (76 bytes)
PRESS_REQUIRED_BYTES = 76


def read_press_db(
    client,
    db_number: int,
    tags: list[tuple[str, int]],
    prefix: str,
    start_byte: int = 0,
    fallback_db: int | None = None,
    fallback_start_byte: int = 0
) -> dict[str, float]:
    """
    Read Real (float32) values from a single press DB.
    Supports start_byte offset and automatic fallback DB/offset if primary fails.
    Returns dict mapping '{prefix} {name}' -> float value.
    """
    results: dict[str, float] = {}
    data = None

    # 1. Attempt primary DB read
    try:
        data = client.db_read(db_number, start_byte, PRESS_REQUIRED_BYTES)
    except Exception as primary_err:
        logger.debug(f"Primary DB {db_number} (offset {start_byte}) read failed for {prefix}: {primary_err}")
        # 2. Attempt fallback DB read if specified
        if fallback_db is not None and fallback_db != db_number:
            try:
                data = client.db_read(fallback_db, fallback_start_byte, PRESS_REQUIRED_BYTES)
                logger.info(f"Fallback to DB {fallback_db} offset {fallback_start_byte} succeeded for {prefix}")
            except Exception as fb_err:
                logger.debug(f"Fallback DB {fallback_db} read failed for {prefix}: {fb_err}")

    if data:
        for name, offset in tags:
            try:
                val = snap7.util.get_real(data, offset)
                # Filter NaNs or infinities
                if val != val or abs(val) > 1e12:
                    val = 0.0
                results[f"{prefix} {name}"] = round(float(val), 4)
            except Exception:
                results[f"{prefix} {name}"] = 0.0
    else:
        # Default all tags to 0.0 if DB read fails
        for name, _ in tags:
            results[f"{prefix} {name}"] = 0.0

    return results


def read_all_press_actuals(client) -> dict[str, float]:
    """
    Read actual values for all 3 presses.
    Uses configured DBs and offsets from Config with automatic fallback:
    - P1: Config.P1_DB (default 1000, start 200), fallback DB 1 (start 0)
    - P2: Config.P2_DB (default 1001, start 228), fallback DB 2 (start 0)
    - P3: Config.P3_DB (default 1001, start 268), fallback DB 3 (start 0)
    Returns combined dictionary of all 57 values.
    """
    try:
        from app.config import Config
        p1_db = getattr(Config, "P1_DB", 1000)
        p1_start = getattr(Config, "P1_START_BYTE", 200)

        p2_db = getattr(Config, "P2_DB", 1001)
        p2_start = getattr(Config, "P2_START_BYTE", 228)

        p3_db = getattr(Config, "P3_DB", 1001)
        p3_start = getattr(Config, "P3_START_BYTE", 268)
    except Exception:
        p1_db, p1_start = 1000, 200
        p2_db, p2_start = 1001, 228
        p3_db, p3_start = 1001, 268

    combined: dict[str, float] = {}

    # Read P1
    p1_vals = read_press_db(
        client=client,
        db_number=p1_db,
        tags=P1_TAGS,
        prefix="P1",
        start_byte=p1_start,
        fallback_db=1 if p1_db != 1 else 1000,
        fallback_start_byte=0 if p1_db != 1 else 200
    )
    combined.update(p1_vals)

    # Read P2
    p2_vals = read_press_db(
        client=client,
        db_number=p2_db,
        tags=P2_TAGS,
        prefix="P2",
        start_byte=p2_start,
        fallback_db=2 if p2_db != 2 else 1001,
        fallback_start_byte=0 if p2_db != 2 else 228
    )
    combined.update(p2_vals)

    # Read P3
    p3_vals = read_press_db(
        client=client,
        db_number=p3_db,
        tags=P3_TAGS,
        prefix="P3",
        start_byte=p3_start,
        fallback_db=3 if p3_db != 3 else 1001,
        fallback_start_byte=0 if p3_db != 3 else 268
    )
    combined.update(p3_vals)

    return combined
