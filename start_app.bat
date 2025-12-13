@echo off
echo Starting SportsEdit-AI System...

:: Check environment
if not exist "venv" (
    echo Venv missing. Run setup_env.bat.
    pause
    exit /b
)
if not exist "client\node_modules" (
    echo Node modules missing. Run setup_env.bat.
    pause
    exit /b
)

:: Activate Python
call venv\Scripts\activate

:: Start Backend (FastAPI) in a new window
echo Starting Backend (FastAPI)...
start "SportsEdit-AI Backend" cmd /k "venv\Scripts\activate && uvicorn api:app --reload --port 8000"

:: Start Frontend (Vite) in a new window
echo Starting Frontend (React)...
cd client
start "SportsEdit-AI Frontend" cmd /k "npm run dev"

echo System Started.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
