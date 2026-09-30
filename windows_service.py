"""
Windows Service for Continuous and Automatic Data Logging.

Runs the Hydraulic Machine Data Collector as a background Windows Service
that automatically starts on boot and restarts on failure.
"""

import os
import sys
from pathlib import Path
import servicemanager
import win32event
import win32service
import win32serviceutil

# Ensure workspace root is in sys.path and cwd is application directory
if getattr(sys, "frozen", False):
    workspace_dir = str(Path(sys.executable).resolve().parent)
else:
    workspace_dir = str(Path(__file__).resolve().parent)

try:
    os.chdir(workspace_dir)
except Exception:
    pass

if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from app.config import ensure_env_file_permissions
from app.logger import setup_logger
from app.main import CollectorApplication


class HydraulicDataCollectorService(win32serviceutil.ServiceFramework):
    """Windows Service for Hydraulic Machine Data Collector."""

    _svc_name_ = "HydraulicDataCollectorService"
    _svc_display_name_ = "Hydraulic Machine Data Collector Service"
    _svc_description_ = (
        "Continuous automated data logger collecting 292 PLC Boolean tags "
        "and machine metrics into SQL Server (dbo.IOStatus)."
    )

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = setup_logger()
        self.app = CollectorApplication()

    def SvcStop(self):
        """Called when the Windows Service Controller requests stop."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.logger.info("Windows Service stop signal received.")
        self.app.stop()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Main service execution."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        self.logger.info("=== Windows Service Started ===")

        try:
            ensure_env_file_permissions()
            self.app.start()

            # Wait for stop event or run periodic check every 1000ms
            while True:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            self.logger.exception(f"Fatal error in Windows Service execution: {e}")
            servicemanager.LogErrorMsg(f"Service encountered fatal error: {e}")

        finally:
            self.app.stop()
            self.logger.info("=== Windows Service Stopped ===")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, "")
            )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Started by Windows Service Control Manager (no command-line args)
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(HydraulicDataCollectorService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception:
            win32serviceutil.HandleCommandLine(HydraulicDataCollectorService)
    else:
        # Command line management: install, remove, start, stop, restart, debug
        win32serviceutil.HandleCommandLine(HydraulicDataCollectorService)

