@echo off
cd /d %~dp0
if not exist venv (
    py -3.12 -m venv venv
    if errorlevel 1 py -3 -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements
if not exist .env (
    copy .env.example .env
)
python -m app.init_db
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
