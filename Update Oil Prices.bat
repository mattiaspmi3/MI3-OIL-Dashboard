@echo off
REM Double-click this file to download the latest oil prices.
cd /d "%~dp0"
python fetch_data.py
echo.
echo ---------------------------------------------
echo Done. You can close this window now.
echo Open index.html to see the updated chart.
echo ---------------------------------------------
pause
