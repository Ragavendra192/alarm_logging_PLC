"""
Application Entry Point - Hydraulic Machine Data Collector.

Coordinates configuration loading, database initialization, PLC communication,
and asynchronous data logging workers.
"""

import logging
import signal
import sys
import time

from app.config import Config
from app.database.db_connection import test_sql_connection
from app.database.db_initializer import initialize_database
from app.logger import setup_logger
from app.workers.data_log_worker import DataLogWorker
from app.workers.plc_worker import PLCWorker

logger = setup_logger()


class CollectorApplication:
    """Controller for PLC communication and SQL Server data logging."""

    def __init__(self):
        self._running = True
        self.data_log_worker: DataLogWorker | None = None
        self.plc_worker: PLCWorker | None = None

    def start(self) -> None:
        """Start collector application and worker pipelines."""
        logger.info("==================================================")
        logger.info("  Hydraulic Machine Data Collector Service        ")
        logger.info("==================================================")
        logger.info(f"Machine ID          : {Config.MACHINE_ID}")
        logger.info(f"PLC IP              : {Config.PLC_IP} (Rack {Config.PLC_RACK}, Slot {Config.PLC_SLOT})")
        logger.info(f"PLC DB Number       : {Config.PLC_DB_NUMBER} (Bytes 0 to 36, 292 tags)")
        logger.info(f"PLC Poll Interval   : {Config.PLC_POLL_INTERVAL}s")
        logger.info(f"SQL Server          : {Config.SQL_SERVER}")
        logger.info(f"SQL Database        : {Config.SQL_DATABASE}")
        logger.info(f"SQL IO Log Interval : {Config.SQL_IO_LOG_INTERVAL}s")
        logger.info("--------------------------------------------------")

        # 1. Test SQL Server & Run Safe Migrations
        logger.info("Checking SQL Server connection...")
        sql_ok, sql_msg = test_sql_connection()
        if sql_ok:
            logger.info("SQL Server connection: CONNECTED")
            logger.info("Verifying database schema and dbo.IOStatus table...")
            init_ok = initialize_database()
            if not init_ok:
                logger.warning("Database initialization had warnings, but continuing...")
        else:
            logger.warning(f"SQL Server connection: DISCONNECTED ({sql_msg})")
            logger.warning("Application will proceed; DataLogWorker will buffer records and auto-reconnect.")

        # 2. Start Asynchronous Workers
        logger.info("Starting DataLogWorker...")
        self.data_log_worker = DataLogWorker(machine_id=Config.MACHINE_ID)
        self.data_log_worker.start()

        logger.info("Starting PLCWorker...")
        self.plc_worker = PLCWorker(data_log_worker=self.data_log_worker)
        self.plc_worker.start()

        logger.info("All worker threads launched successfully.")

    def run(self) -> None:
        """Main loop monitoring workers and logging periodic health status."""
        last_status_time = 0.0
        status_interval = 10.0  # Log summary every 10 seconds

        while self._running:
            try:
                now = time.time()
                if now - last_status_time >= status_interval:
                    last_status_time = now
                    plc_status = "CONNECTED" if (self.plc_worker and self.plc_worker.plc_connected) else "DISCONNECTED"
                    sql_status = "CONNECTED" if (self.data_log_worker and self.data_log_worker.sql_connected) else "DISCONNECTED"
                    buffer_count = len(self.data_log_worker.buffer) if self.data_log_worker else 0
                    alarm_active, alarm_txt = self.plc_worker.get_latest_alarm() if self.plc_worker else (False, "")
                    alarm_display = f"ALARM: {alarm_txt}" if alarm_active else "NO ALARM"

                    logger.info(
                        f"[Health] PLC: {plc_status} | SQL: {sql_status} | Status: {alarm_display} | Buffer: {buffer_count} items"
                    )


                time.sleep(1.0)

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received, stopping...")
                break
            except Exception as e:
                logger.error(f"Error in main supervisor loop: {e}")
                time.sleep(1.0)

        self.stop()

    def stop(self) -> None:
        """Stop all workers and cleanup resources."""
        self._running = False
        logger.info("Stopping application and workers...")

        if self.plc_worker:
            self.plc_worker.stop()
            self.plc_worker.join(timeout=3.0)

        if self.data_log_worker:
            self.data_log_worker.stop()
            self.data_log_worker.join(timeout=3.0)

        logger.info("Collector application stopped successfully.")


def main():
    app = CollectorApplication()

    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} received, shutting down...")
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app.start()
    app.run()


if __name__ == "__main__":
    main()