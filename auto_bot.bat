@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python -m app.init_db
python -m app.jobs.daily_predictions
python -m app.jobs.send_telegram
