"""
Database Initializer and Safe Migration Runner.

Performs idempotent database schema verification and migrations:
- Verifies/creates dbo.IOStatus and dbo.MachineDataLog with:
  * Timestamp
  * OperatorName
  * Swift
  * 292 PLC address BIT columns ([0.0] through [36.3]) showing 0 and 1
  * 57 Press Real columns ([P1 ...], [P2 ...], [P3 ...])
  * MachineNumber, Id, CreatedAt
- Uses ALTER TABLE for missing columns on existing tables to preserve data.
- Creates required performance indexes.
"""

import logging
from app.database.db_connection import get_db_cursor
from app.plc.plc_tags import PLC_ADDRESSES
from app.plc.press_actual import ALL_PRESS_COLUMNS

logger = logging.getLogger("PLCDataCollector.DBInitializer")


def ensure_columns_for_table(cursor, table_name: str) -> tuple[int, int]:
    """
    Ensure table exists with Id, MachineNumber, Timestamp, OperatorName, Swift,
    292 PLC address BIT columns, and 57 Press Real columns.
    Returns (address_column_count, press_column_count).
    """
    # 1. Check if table exists
    cursor.execute(f"SELECT OBJECT_ID('dbo.{table_name}', 'U')")
    table_exists = cursor.fetchone()[0] is not None

    if not table_exists:
        logger.info(f"dbo.{table_name} not found. Creating table...")
        io_defs = [f"[{addr}] BIT NULL" for addr in PLC_ADDRESSES]
        press_defs = [f"[{col}] REAL NULL" for col in ALL_PRESS_COLUMNS]
        all_cols_sql = ",\n    ".join(io_defs + press_defs)

        create_sql = f"""
        CREATE TABLE dbo.{table_name}
        (
            Id BIGINT IDENTITY(1,1) PRIMARY KEY,
            MachineNumber VARCHAR(50) NOT NULL,
            [Timestamp] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [Alarm] VARCHAR(500) NULL,
            OperatorName VARCHAR(200) NULL,
            Swift VARCHAR(100) NULL,
            {all_cols_sql},
            CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
        );
        """
        cursor.execute(create_sql)
        logger.info(f"Created dbo.{table_name} with [Alarm] column, 292 address columns and 57 press actual columns.")
    else:
        logger.info(f"dbo.{table_name} exists. Inspecting columns...")
        cursor.execute(f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}

        # Ensure Timestamp
        if "Timestamp" not in existing_columns:
            cursor.execute(f"ALTER TABLE dbo.{table_name} ADD [Timestamp] DATETIME2 NULL DEFAULT SYSDATETIME()")
            logger.info(f"Added [Timestamp] to dbo.{table_name}.")

        # Ensure Alarm column after Timestamp (use NVARCHAR(MAX) to prevent truncation when multiple alarms are active)
        if "Alarm" not in existing_columns:
            cursor.execute(f"ALTER TABLE dbo.{table_name} ADD [Alarm] NVARCHAR(MAX) NULL")
            logger.info(f"Added [Alarm] NVARCHAR(MAX) column to dbo.{table_name}.")
        else:
            try:
                cursor.execute(f"ALTER TABLE dbo.{table_name} ALTER COLUMN [Alarm] NVARCHAR(MAX) NULL")
            except Exception as alt_err:
                logger.debug(f"Ensuring NVARCHAR(MAX) on dbo.{table_name}.Alarm: {alt_err}")

        # In AlarmResponse, ensure legacy NOT NULL columns are relaxed to NULL
        if table_name == "AlarmResponse":
            try:
                cursor.execute("""
                    IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_AlarmResponse_Machine_Start' AND object_id = OBJECT_ID('dbo.AlarmResponse'))
                    BEGIN
                        DROP INDEX IX_AlarmResponse_Machine_Start ON dbo.AlarmResponse;
                    END
                """)
                cursor.execute("ALTER TABLE dbo.AlarmResponse ALTER COLUMN AlarmCode VARCHAR(100) NULL")
                cursor.execute("ALTER TABLE dbo.AlarmResponse ALTER COLUMN AlarmStartTime DATETIME2 NULL")
            except Exception as relax_err:
                logger.debug(f"Relaxing AlarmResponse column nullability: {relax_err}")


        # Ensure OperatorName & Swift

        if "OperatorName" not in existing_columns:
            cursor.execute(f"ALTER TABLE dbo.{table_name} ADD OperatorName VARCHAR(200) NULL")
            logger.info(f"Added OperatorName to dbo.{table_name}.")

        if "Swift" not in existing_columns:
            cursor.execute(f"ALTER TABLE dbo.{table_name} ADD Swift VARCHAR(100) NULL")
            logger.info(f"Added Swift to dbo.{table_name}.")

        # Ensure all 292 address columns
        missing_addresses = [addr for addr in PLC_ADDRESSES if addr not in existing_columns]
        if missing_addresses:
            logger.info(f"Adding {len(missing_addresses)} missing address columns to dbo.{table_name}...")
            for addr in missing_addresses:
                cursor.execute(f"ALTER TABLE dbo.{table_name} ADD [{addr}] BIT NULL")

        # Ensure all 57 press actual columns
        missing_press = [col for col in ALL_PRESS_COLUMNS if col not in existing_columns]
        if missing_press:
            logger.info(f"Adding {len(missing_press)} missing press actual columns to dbo.{table_name}...")
            for col in missing_press:
                cursor.execute(f"ALTER TABLE dbo.{table_name} ADD [{col}] REAL NULL")

    # 2. Ensure Index exists
    index_name = f"IX_{table_name}_Machine_Timestamp"
    cursor.execute(f"""
        IF NOT EXISTS (
            SELECT * FROM sys.indexes
            WHERE name = '{index_name}'
            AND object_id = OBJECT_ID('dbo.{table_name}')
        )
        BEGIN
            CREATE INDEX {index_name}
            ON dbo.{table_name}(MachineNumber, [Timestamp] DESC);
        END
    """)

    # 3. Verify counts
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        AND DATA_TYPE = 'bit'
        AND COLUMN_NAME LIKE '%.%'
    """)
    io_count = cursor.fetchone()[0]

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        AND DATA_TYPE = 'real'
        AND (COLUMN_NAME LIKE 'P1 %' OR COLUMN_NAME LIKE 'P2 %' OR COLUMN_NAME LIKE 'P3 %')
    """)
    press_count = cursor.fetchone()[0]

    return io_count, press_count


def ensure_alarm_event_table(cursor) -> None:
    """
    Ensure dbo.AlarmEvent table exists with required columns, indexes,
    all 292 Boolean IO address columns, and 57 Press Real columns.
    """
    cursor.execute("SELECT OBJECT_ID('dbo.AlarmEvent', 'U')")
    table_exists = cursor.fetchone()[0] is not None

    io_defs = [f"[{addr}] BIT NULL" for addr in PLC_ADDRESSES]
    press_defs = [f"[{col}] REAL NULL" for col in ALL_PRESS_COLUMNS]
    all_snapshot_cols_sql = ",\n        ".join(io_defs + press_defs)

    if not table_exists:
        logger.info("dbo.AlarmEvent not found. Creating table...")
        create_sql = f"""
        CREATE TABLE dbo.AlarmEvent
        (
            Id BIGINT IDENTITY(1,1) PRIMARY KEY,
            MachineNumber VARCHAR(50) NOT NULL,
            PLCAddress VARCHAR(100) NOT NULL,
            DBNumber INT NULL,
            ByteAddress INT NULL,
            BitAddress INT NULL,
            AlarmCode VARCHAR(100) NULL,
            AlarmDescription NVARCHAR(MAX) NOT NULL,
            [Alarm] NVARCHAR(MAX) NULL,
            Severity VARCHAR(50) NULL DEFAULT 'FAULT',
            AlarmStartTime DATETIME2 NOT NULL,
            AlarmEndTime DATETIME2 NULL,
            AlarmDurationSeconds INT NULL,
            OperatorName VARCHAR(200) NULL,
            Swift VARCHAR(100) NULL,
            RecipeName VARCHAR(200) NULL,
            MachineRunning BIT NULL,
            CycleRunning BIT NULL,
            MachineMode VARCHAR(50) NULL,
            PLCConnected BIT NULL DEFAULT 1,
            OperatorAction NVARCHAR(1000) NULL,
            Resolution NVARCHAR(1000) NULL,
            [Timestamp] DATETIME2 NULL DEFAULT SYSDATETIME(),
            {all_snapshot_cols_sql},
            CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
        );
        """
        cursor.execute(create_sql)
        logger.info("Created dbo.AlarmEvent with all metadata and machine snapshot columns.")
    else:
        logger.info("dbo.AlarmEvent exists. Verifying columns...")
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'AlarmEvent'
        """)
        existing_cols = {row[0] for row in cursor.fetchall()}

        base_fields = [
            ("PLCAddress", "VARCHAR(100) NULL"),
            ("DBNumber", "INT NULL"),
            ("ByteAddress", "INT NULL"),
            ("BitAddress", "INT NULL"),
            ("AlarmCode", "VARCHAR(100) NULL"),
            ("AlarmDescription", "VARCHAR(500) NULL"),
            ("Alarm", "VARCHAR(500) NULL"),
            ("Severity", "VARCHAR(50) NULL DEFAULT 'FAULT'"),
            ("AlarmStartTime", "DATETIME2 NULL"),
            ("AlarmEndTime", "DATETIME2 NULL"),
            ("AlarmDurationSeconds", "INT NULL"),
            ("OperatorName", "VARCHAR(200) NULL"),
            ("Swift", "VARCHAR(100) NULL"),
            ("RecipeName", "VARCHAR(200) NULL"),
            ("MachineRunning", "BIT NULL"),
            ("CycleRunning", "BIT NULL"),
            ("MachineMode", "VARCHAR(50) NULL"),
            ("PLCConnected", "BIT NULL DEFAULT 1"),
            ("OperatorAction", "NVARCHAR(1000) NULL"),
            ("Resolution", "NVARCHAR(1000) NULL"),
            ("Timestamp", "DATETIME2 NULL DEFAULT SYSDATETIME()"),
        ]

        for col_name, col_type in base_fields:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE dbo.AlarmEvent ADD [{col_name}] {col_type}")
                logger.info(f"Added [{col_name}] to dbo.AlarmEvent.")

        # Ensure all 292 IO bits
        missing_addresses = [addr for addr in PLC_ADDRESSES if addr not in existing_cols]
        if missing_addresses:
            logger.info(f"Adding {len(missing_addresses)} missing address columns to dbo.AlarmEvent...")
            for addr in missing_addresses:
                cursor.execute(f"ALTER TABLE dbo.AlarmEvent ADD [{addr}] BIT NULL")

        # Ensure all 57 Press Reals
        missing_press = [col for col in ALL_PRESS_COLUMNS if col not in existing_cols]
        if missing_press:
            logger.info(f"Adding {len(missing_press)} missing press columns to dbo.AlarmEvent...")
            for col in missing_press:
                cursor.execute(f"ALTER TABLE dbo.AlarmEvent ADD [{col}] REAL NULL")

    # Ensure required indexes
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.indexes
            WHERE name = 'IX_AlarmEvent_Machine_Address_Start'
            AND object_id = OBJECT_ID('dbo.AlarmEvent')
        )
        BEGIN
            CREATE INDEX IX_AlarmEvent_Machine_Address_Start
            ON dbo.AlarmEvent (MachineNumber, PLCAddress, AlarmStartTime DESC);
        END
    """)

    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.indexes
            WHERE name = 'IX_AlarmEvent_Active'
            AND object_id = OBJECT_ID('dbo.AlarmEvent')
        )
        BEGIN
            CREATE INDEX IX_AlarmEvent_Active
            ON dbo.AlarmEvent (AlarmEndTime)
            INCLUDE (MachineNumber, PLCAddress, AlarmStartTime);
        END
    """)


def initialize_database() -> bool:
    """
    Run complete safe initialization of SQL Server database for
    IOStatus, MachineDataLog, AlarmResponse, and AlarmEvent tables.
    """
    try:
        logger.info("Starting database initialization...")
        with get_db_cursor(commit=True) as cursor:
            io_cnt, p_cnt = ensure_columns_for_table(cursor, "MachineDataLog")
            ensure_columns_for_table(cursor, "IOStatus")
            ensure_columns_for_table(cursor, "AlarmResponse")
            ensure_alarm_event_table(cursor)

        logger.info(
            f"Database initialization completed successfully! "
            f"IO Address columns: {io_cnt}, Press Actual columns: {p_cnt}"
        )
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    from app.logger import setup_logger
    setup_logger()
    success = initialize_database()
    print("Database initialization result:", success)
