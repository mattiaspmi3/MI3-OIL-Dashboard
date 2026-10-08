@echo off
REM Manual/local full data refresh. To run this unattended, register it separately
REM in Windows Task Scheduler. The hosted dashboard uses GitHub Actions instead.
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
