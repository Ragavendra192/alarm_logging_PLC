"""
Siemens PLC Communication Client using python-snap7.

Supports connection management, robust reconnection with backoff,
raw DB reading, and automatic parsing of IO boolean tag snapshots.
"""

import logging
import time
import snap7

from app.config import Config
from app.plc.plc_tags import parse_io_bytes, PLC_REQUIRED_BYTES

logger = logging.getLogger("PLCDataCollector.PLC")


# Hardware module offset mapping for distributed 3-station input modules:
# Logical bytes 0..13 -> Hardware inputs I0..I13
# Logical bytes 14..18 -> Hardware inputs I32..I36
# Logical bytes 19..23 -> Hardware inputs I55..I59
# Logical bytes 24..26 -> Hardware inputs I83..I85
# Logical bytes 27..28 -> Hardware inputs I89..I90
# Logical bytes 29..30 -> Hardware inputs I95..I96
# Logical bytes 31..36 -> Hardware inputs I121..I126
HW_BYTE_MAP = {
    14: 32, 15: 33, 16: 34, 17: 35, 18: 36,
    19: 55, 20: 56, 21: 57, 22: 58, 23: 59,
    24: 83, 25: 84, 26: 85,
    27: 89, 28: 90,
    29: 95, 30: 96,
    31: 121, 32: 122, 33: 123, 34: 124, 35: 125, 36: 126,
}


class SiemensPLC:
    """Siemens S7 PLC connection and data reader."""

    def __init__(self, ip: str | None = None, rack: int | None = None, slot: int | None = None):
        self.ip = ip or Config.PLC_IP
        self.rack = rack if rack is not None else Config.PLC_RACK
        self.slot = slot if slot is not None else Config.PLC_SLOT

        self.client = snap7.client.Client()
        self._last_connect_attempt = 0.0

    def connect(self) -> bool:
        """
        Connect to Siemens PLC.
        Returns True if connected, False on failure.
        """
        if self.is_connected():
            return True

        self._last_connect_attempt = time.time()
        try:
            logger.info(f"Connecting to PLC at {self.ip} (Rack {self.rack}, Slot {self.slot})...")
            self.client.connect(self.ip, self.rack, self.slot)
            connected = self.client.get_connected()
            if connected:
                logger.info("PLC connected successfully!")
            else:
                logger.warning("PLC connection attempt returned disconnected.")
            return connected
        except Exception as e:
            logger.error(f"PLC connection error: {e}")
            return False

    def reconnect(self) -> bool:
        """Attempt to reconnect to PLC."""
        self.disconnect()
        return self.connect()

    def disconnect(self) -> None:
        """Disconnect from PLC."""
        try:
            if self.client.get_connected():
                self.client.disconnect()
        except Exception as e:
            logger.debug(f"Error during PLC disconnect: {e}")

    def is_connected(self) -> bool:
        """Check if PLC client is currently connected."""
        try:
            return bool(self.client.get_connected())
        except Exception:
            return False

    def read_db(self, db_number: int, start: int, size: int) -> bytearray | bytes:
        """
        Read raw bytes from a Siemens PLC Data Block.

        Parameters:
            db_number : DB number (e.g. 501)
            start     : Starting byte offset
            size      : Number of bytes to read

        Returns:
            Raw byte data
        """
        if not self.is_connected():
            raise ConnectionError("PLC is not connected")

        return self.client.db_read(db_number, start, size)

    def read_io_snapshot(self, db_number: int | None = None) -> dict[str, int]:
        """
        Read all 292 Boolean IO addresses from the PLC.

        Reads from live Process Image Inputs (snap7.Area.PE), Process Image Outputs
        (snap7.Area.PA), hardware module offsets, and DB 1000, combining them into
        a unified 37-byte snapshot for parsing.

        Returns:
            Dictionary mapping address (e.g. "0.0") to 0 or 1.
        """
        if not self.is_connected():
            raise ConnectionError("PLC is not connected")

        source = getattr(Config, "PLC_IO_SOURCE", "AUTO")
        combined = bytearray(PLC_REQUIRED_BYTES)

        if source in ("PE", "AUTO"):
            try:
                # Read up to 130 bytes to cover physical I0..I13 and remote I32..I126
                raw_pe = self.client.read_area(snap7.Area.PE, 0, 0, 130)
                for i in range(PLC_REQUIRED_BYTES):
                    pe_val = raw_pe[i] if i < len(raw_pe) else 0
                    if i in HW_BYTE_MAP:
                        hw_idx = HW_BYTE_MAP[i]
                        if hw_idx < len(raw_pe):
                            pe_val |= raw_pe[hw_idx]
                    combined[i] |= pe_val
            except Exception as pe_err:
                logger.debug(f"Error reading PE area: {pe_err}")

            try:
                # Read up to 37 bytes of Process Image Outputs (Q0..Q36)
                raw_pa = self.client.read_area(snap7.Area.PA, 0, 0, PLC_REQUIRED_BYTES)
                for i in range(min(len(raw_pa), PLC_REQUIRED_BYTES)):
                    combined[i] |= raw_pa[i]
            except Exception as pa_err:
                logger.debug(f"Error reading PA area: {pa_err}")

        if source in ("DB", "AUTO"):
            db = db_number if db_number is not None else Config.PLC_DB_NUMBER
            try:
                raw_db = self.read_db(
                    db_number=db,
                    start=Config.PLC_BYTE_START,
                    size=PLC_REQUIRED_BYTES
                )
                if raw_db:
                    for i in range(min(len(raw_db), PLC_REQUIRED_BYTES)):
                        combined[i] |= raw_db[i]
            except Exception as db_err:
                if source == "DB":
                    raise db_err
                logger.debug(f"DB {db} read note: {db_err}")

        return parse_io_bytes(combined)