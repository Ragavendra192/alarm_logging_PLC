"""
Build script to compile 3StationCollector and 3StationWebApp using PyInstaller
into a completely self-contained distribution folder (dist/3StationPackage).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
PACKAGE_DIR = DIST_DIR / "3StationPackage"


def run_cmd(cmd, desc):
    print(f"\n[BUILD] {desc}...")
    print("Command:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print(f"[ERROR] {desc} failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    print(f"[SUCCESS] {desc} completed.")


def main():
    print("=" * 70)
    print("  Building 3-Station Machine Deployment Package (PyInstaller)")
    print("=" * 70)

    # Clean previous builds
    build_temp = ROOT_DIR / "build"
    if build_temp.exists():
        shutil.rmtree(build_temp, ignore_errors=True)
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR, ignore_errors=True)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Compile 3StationCollectorService.exe
    cmd_service = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--name", "3StationCollectorService",
        "--hidden-import", "win32timezone",
        "--hidden-import", "win32service",
        "--hidden-import", "win32serviceutil",
        "--hidden-import", "servicemanager",
        "--hidden-import", "pywintypes",
        "--hidden-import", "win32event",
        "--hidden-import", "pyodbc",
        "--hidden-import", "snap7",
        "--collect-all", "snap7",
        "--distpath", str(PACKAGE_DIR / "service_dist"),
        "windows_service.py"
    ]
    run_cmd(cmd_service, "Compiling Windows Service executable")

    # 2. Compile 3StationWebApp.exe
    cmd_web = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--name", "3StationWebApp",
        "--hidden-import", "pyodbc",
        "--hidden-import", "flask",
        "--hidden-import", "jinja2",
        "--distpath", str(PACKAGE_DIR / "web_dist"),
        "run_web.py"
    ]
    run_cmd(cmd_web, "Compiling Web Application executable")

    # 3. Assemble unified package
    print("\n[ASSEMBLY] Assembling unified distribution folder...")
    final_dir = PACKAGE_DIR / "app_files"
    final_dir.mkdir(parents=True, exist_ok=True)

    # Copy files from service_dist/3StationCollectorService to final_dir
    svc_source = PACKAGE_DIR / "service_dist" / "3StationCollectorService"
    for item in svc_source.iterdir():
        dest = final_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # Copy 3StationWebApp.exe and its dependencies from web_dist/3StationWebApp
    web_source = PACKAGE_DIR / "web_dist" / "3StationWebApp"
    for item in web_source.iterdir():
        dest = final_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            if not dest.exists():
                shutil.copy2(item, dest)

    # Copy required runtime data files
    data_dest = final_dir / "data"
    data_dest.mkdir(parents=True, exist_ok=True)
    if (ROOT_DIR / "data" / "alarm_mappings.sqlite").exists():
        shutil.copy2(ROOT_DIR / "data" / "alarm_mappings.sqlite", data_dest / "alarm_mappings.sqlite")

    # Copy web templates and static assets
    web_dest = final_dir / "app" / "web"
    web_dest.mkdir(parents=True, exist_ok=True)
    if (ROOT_DIR / "app" / "web" / "templates").exists():
        shutil.copytree(ROOT_DIR / "app" / "web" / "templates", web_dest / "templates", dirs_exist_ok=True)
        if (final_dir / "_internal").exists():
            shutil.copytree(ROOT_DIR / "app" / "web" / "templates", final_dir / "_internal" / "app" / "web" / "templates", dirs_exist_ok=True)
            shutil.copytree(ROOT_DIR / "app" / "web" / "templates", final_dir / "_internal" / "templates", dirs_exist_ok=True)

    if (ROOT_DIR / "app" / "web" / "static").exists():
        shutil.copytree(ROOT_DIR / "app" / "web" / "static", web_dest / "static", dirs_exist_ok=True)
        if (final_dir / "_internal").exists():
            shutil.copytree(ROOT_DIR / "app" / "web" / "static", final_dir / "_internal" / "app" / "web" / "static", dirs_exist_ok=True)
            shutil.copytree(ROOT_DIR / "app" / "web" / "static", final_dir / "_internal" / "static", dirs_exist_ok=True)


    # Copy config and launcher scripts
    shutil.copy2(ROOT_DIR / ".env", final_dir / ".env")
    shutil.copy2(ROOT_DIR / ".env.example", final_dir / ".env.example")
    shutil.copy2(ROOT_DIR / "scripts" / "start_web_app.vbs", final_dir / "start_web_app.vbs")

    # Create logs directory
    (final_dir / "logs").mkdir(parents=True, exist_ok=True)

    # Clean intermediate dist folders
    shutil.rmtree(PACKAGE_DIR / "service_dist", ignore_errors=True)
    shutil.rmtree(PACKAGE_DIR / "web_dist", ignore_errors=True)

    print("=" * 70)
    print(f"[SUCCESS] Standalone Package successfully created at:\n  {final_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
