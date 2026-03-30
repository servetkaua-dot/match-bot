@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo Match Predictor - Full Cycle (TheSportsDB)

echo [1/6] Checking virtual environment...
if not exist venv (
    py -3.12 -m venv venv
    if errorlevel 1 py -3 -m venv venv
)

call venv\\Scripts\\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [2/6] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/6] Checking .env...
if not exist .env (
    copy .env.example .env >nul
    echo .env was created from .env.example
)

echo [4/6] Initializing database...
python -m app.init_db
if errorlevel 1 (
    echo Failed to initialize database.
    pause
    exit /b 1
)

echo [5/6] Collecting predictions for tomorrow...
python -m app.jobs.daily_predictions
if errorlevel 1 (
    echo Failed to generate predictions.
    pause
    exit /b 1
)

echo [6/6] Sending predictions to Telegram...
python -m app.jobs.send_telegram
if errorlevel 1 (
    echo Telegram sending failed or was skipped.
)

echo Checking finished matches and updating stats...
python -m app.jobs.resolve_predictions
if errorlevel 1 (
    echo Results resolve failed or nothing to resolve.
)

echo.
echo Done.
echo Health:              http://127.0.0.1:8000/health
echo Predictions:         http://127.0.0.1:8000/predictions/tomorrow
echo Stats summary:       http://127.0.0.1:8000/stats/summary
echo.
pause
endlocal
