@echo off
REM Auto-refresh: pull the latest LIVE data, then rebuild the shareable/published files.
REM Runs with no pause so Windows Task Scheduler can call it unattended.
cd /d "%~dp0"
echo [%date% %time%] Refreshing live data...
python fetch_data.py
echo [%date% %time%] Rebuilding shareable file...
python bundle.py
echo [%date% %time%] Done.
