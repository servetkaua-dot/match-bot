@echo off
cd /d %~dp0
if not exist venv (
    py -3.12 -m venv venv
    if errorlevel 1 py -3 -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements >nul 2>&1
if not exist .env (
    copy .env.example .env >nul
)
python -m app.init_db
python -m app.jobs.daily_predictions
python -m app.jobs.send_telegram
python -m app.jobs.resolve_predictions
