@echo off
if not exist "venv" (
    echo Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b
)

echo Running Deep Data Analysis...
call venv\Scripts\activate
python utils/analyze_join.py
pause
