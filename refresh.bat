@echo off
REM Daily auto-refresh: pull the latest LIVE data (incl. daily WTI & Henry Hub spot
REM prices), rebuild the shareable file, and push to GitHub so the shared copy stays
REM current. Runs unattended (no pause) for Windows Task Scheduler.
cd /d "%~dp0"
set PATH=%PATH%;C:\Program Files\GitHub CLI;C:\Program Files\Git\cmd

echo [%date% %time%] Refreshing live data...
python fetch_data.py
echo [%date% %time%] Rebuilding shareable file...
python bundle.py

echo [%date% %time%] Pushing to GitHub...
git add -A
git commit -m "Daily data refresh (auto)"
git push

echo [%date% %time%] Done.
