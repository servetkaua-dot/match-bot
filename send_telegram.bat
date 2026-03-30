@echo off
cd /d %~dp0
call venv\Scripts\activate
python -m app.jobs.send_telegram
pause
