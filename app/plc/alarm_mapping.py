"""
PLC Alarm Mapping Management Module.

Manages definitions and metadata for PLC Boolean alarm bits:
- ByteAddress (int)
- BitAddress (int)
- PLCAddress (str, e.g. "DB101.DBX20.3")
- AlarmCode (str, e.g. "ALM-0203")
- AlarmDescription (str, e.g. "Hydraulic Pump Overload")
- Severity (str, e.g. "FAULT", "WARNING")
- IsEnabled (bool / int, 1 = active, 0 = suppressed)

Backed by SQLite (data/alarm_mappings.sqlite) so administrators can add or
modify alarm descriptions without code changes.
"""

from dataclasses import dataclass
import logging
from pathlib import Path
import sqlite3
import threading
from typing import Any

from app.config import Config, get_base_dir

logger = logging.getLogger("PLCDataCollector.AlarmMapping")


@dataclass
class AlarmDefinition:
    byte_address: int
    bit_address: int
    plc_address: str
    alarm_code: str
    alarm_description: str
    severity: str = "FAULT"
    is_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "byte_address": self.byte_address,
            "bit_address": self.bit_address,
            "plc_address": self.plc_address,
            "alarm_code": self.alarm_code,
            "alarm_description": self.alarm_description,
            "severity": self.severity,
            "is_enabled": self.is_enabled,
        }


# Default seed mappings for common known bits in DB101
DEFAULT_SEED_MAPPINGS = [
    (20, 3, "ALM-0203", "Hydraulic Pump Overload", "FAULT", 1),
    (5, 2, "ALM-0052", "FaultBit 1", "FAULT", 1),
    (5, 3, "ALM-0053", "FaultBit 2", "FAULT", 1),
    (5, 4, "ALM-0054", "FaultBit 3", "FAULT", 1),
    (5, 5, "ALM-0055", "FaultBit 4", "FAULT", 1),
    (5, 6, "ALM-0056", "FaultBit 5", "FAULT", 1),
    (5, 7, "ALM-0057", "FaultBit 6", "FAULT", 1),
    (6, 0, "ALM-0060", "P1 FAULT ONLY", "FAULT", 1),
    (6, 1, "ALM-0061", "P2 FAULT ONLY", "FAULT", 1),
    (6, 2, "ALM-0062", "P3 FAULT ONLY", "FAULT", 1),
    (6, 3, "ALM-0063", "FaultBit 10", "FAULT", 1),
]


class AlarmMappingManager:
    """Thread-safe alarm definition manager with SQLite persistence and caching."""

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, db_path: str | Path | None = None):
        if getattr(self, "_initialized", False):
            return

        base_dir = get_base_dir()
        custom_path = db_path or Config.ALARM_MAPPINGS_DB
        self.db_file = Path(custom_path)
        if not self.db_file.is_absolute():
            self.db_file = base_dir / self.db_file

        self._lock = threading.Lock()
        self._cache: dict[tuple[int, int], AlarmDefinition] = {}

        self._init_sqlite()
        self.reload()
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_file), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self) -> None:
        """Create alarm_mappings table and populate defaults if empty."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alarm_mappings (
                        ByteAddress INTEGER NOT NULL,
                        BitAddress INTEGER NOT NULL,
                        PLCAddress TEXT NOT NULL,
                        AlarmCode TEXT NOT NULL,
                        AlarmText TEXT NOT NULL,
                        Severity TEXT DEFAULT 'FAULT',
                        IsEnabled INTEGER DEFAULT 1,
                        PRIMARY KEY (ByteAddress, BitAddress)
                    );
                """)
                cursor = conn.execute("SELECT COUNT(*) FROM alarm_mappings")
                count = cursor.fetchone()[0]

                if count == 0:
                    logger.info("Initializing alarm_mappings SQLite table with default seed records...")
                    db_num = Config.PLC_ALARM_DB
                    for byte_addr, bit_addr, code, text, sev, enabled in DEFAULT_SEED_MAPPINGS:
                        plc_addr = f"DB{db_num}.DBX{byte_addr}.{bit_addr}"
                        conn.execute("""
                            INSERT INTO alarm_mappings (
                                ByteAddress, BitAddress, PLCAddress, AlarmCode, AlarmText, Severity, IsEnabled
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (byte_addr, bit_addr, plc_addr, code, text, sev, enabled))
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize alarm_mappings SQLite database: {e}")

    def reload(self) -> None:
        """Reload all mappings into fast in-memory dictionary."""
        with self._lock:
            new_cache: dict[tuple[int, int], AlarmDefinition] = {}
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT ByteAddress, BitAddress, PLCAddress, AlarmCode, AlarmText, Severity, IsEnabled
                        FROM alarm_mappings
                    """)
                    for row in cursor.fetchall():
                        key = (int(row["ByteAddress"]), int(row["BitAddress"]))
                        new_cache[key] = AlarmDefinition(
                            byte_address=int(row["ByteAddress"]),
                            bit_address=int(row["BitAddress"]),
                            plc_address=str(row["PLCAddress"]),
                            alarm_code=str(row["AlarmCode"]),
                            alarm_description=str(row["AlarmText"]),
                            severity=str(row["Severity"] or "FAULT"),
                            is_enabled=bool(row["IsEnabled"]),
                        )
                self._cache = new_cache
                logger.debug(f"Loaded {len(self._cache)} alarm definitions into cache.")
            except Exception as e:
                logger.error(f"Error reading alarm_mappings SQLite database: {e}")

    def get_mapping(
        self,
        byte_index: int,
        bit_index: int,
        db_number: int | None = None
    ) -> AlarmDefinition | None:
        """
        Lookup alarm definition for given byte and bit.
        - If mapped and enabled: returns mapped AlarmDefinition.
        - If mapped and disabled (IsEnabled=0): returns None (suppressed).
        - If unmapped: returns auto-generated unmapped AlarmDefinition with severity FAULT.
        """
        db_num = db_number if db_number is not None else Config.PLC_ALARM_DB
        key = (byte_index, bit_index)

        with self._lock:
            defn = self._cache.get(key)

        if defn is not None:
            if not defn.is_enabled:
                return None  # Explicitly suppressed
            return defn

        # Unmapped alarm fallback: must still be detected and logged per requirement
        plc_address = f"DB{db_num}.DBX{byte_index}.{bit_index}"
        alarm_code = f"ALM-DB{db_num}-{byte_index:03d}{bit_index}"
        alarm_text = f"UNMAPPED ALARM {plc_address}"

        return AlarmDefinition(
            byte_address=byte_index,
            bit_address=bit_index,
            plc_address=plc_address,
            alarm_code=alarm_code,
            alarm_description=alarm_text,
            severity="FAULT",
            is_enabled=True,
        )

    def add_or_update_mapping(
        self,
        byte_address: int,
        bit_address: int,
        alarm_description: str,
        alarm_code: str | None = None,
        severity: str = "FAULT",
        is_enabled: bool = True,
        db_number: int | None = None
    ) -> AlarmDefinition:
        """Add or update an alarm definition dynamically in SQLite."""
        db_num = db_number if db_number is not None else Config.PLC_ALARM_DB
        plc_address = f"DB{db_num}.DBX{byte_address}.{bit_address}"
        code = alarm_code or f"ALM-DB{db_num}-{byte_address:03d}{bit_address}"

        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO alarm_mappings (
                        ByteAddress, BitAddress, PLCAddress, AlarmCode, AlarmText, Severity, IsEnabled
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(ByteAddress, BitAddress) DO UPDATE SET
                        PLCAddress = excluded.PLCAddress,
                        AlarmCode = excluded.AlarmCode,
                        AlarmText = excluded.AlarmText,
                        Severity = excluded.Severity,
                        IsEnabled = excluded.IsEnabled
                """, (byte_address, bit_address, plc_address, code, alarm_description, severity, int(is_enabled)))
                conn.commit()

            defn = AlarmDefinition(
                byte_address=byte_address,
                bit_address=bit_address,
                plc_address=plc_address,
                alarm_code=code,
                alarm_description=alarm_description,
                severity=severity,
                is_enabled=is_enabled,
            )
            self._cache[(byte_address, bit_address)] = defn
            logger.info(f"Updated alarm mapping for {plc_address}: {alarm_description} ({severity})")
            return defn

    def list_mappings(self) -> list[dict[str, Any]]:
        """Return all configured mappings sorted by address."""
        with self._lock:
            sorted_items = sorted(self._cache.values(), key=lambda d: (d.byte_address, d.bit_address))
            return [item.to_dict() for item in sorted_items]
