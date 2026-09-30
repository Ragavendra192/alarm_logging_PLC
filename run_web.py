"""
Launcher script for Fault & Alarm Analytics Web Dashboard.

Usage:
    python run_web.py
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import Config
from app.web.server import app

if __name__ == "__main__":
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "5001"))


    print("=" * 60)
    print("  Hydraulic Machine Fault & Alarm Analytics Web Dashboard")
    print("=" * 60)
    print(f"Machine ID      : {Config.MACHINE_ID}")
    print(f"SQL Server      : {Config.SQL_SERVER}")
    print(f"SQL Database    : {Config.SQL_DATABASE}")
    print(f"Dashboard URL   : http://127.0.0.1:{port}")
    print(f"Network URL     : http://localhost:{port}")
    print("-" * 60)
    print("Press CTRL+C to stop the web server.")
    print("=" * 60)

    app.run(host=host, port=port, debug=False)
