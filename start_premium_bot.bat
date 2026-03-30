@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python -m app.jobs.bot_loop
pause
