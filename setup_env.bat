@echo off
echo Setting up SportsEdit-AI Environment...

:: 1. Python Venv Configuration
set PYTHON_PATH="C:\Users\henry-cao-local\AppData\Local\Programs\Python\Python310\python.exe"

if not exist %PYTHON_PATH% (
    echo Error: Python 3.10 not found at %PYTHON_PATH%
    echo Please install Python 3.10 or update the path in setup_env.bat
    pause
    exit /b
)

:: Clean old venv if needed (Simple check: if venv exists, ask user to recreate or just recreate if we want to force 3.10)
:: For now, we assume if venv exists, we might want to nuking it to be safe, but let's just try to create it if missing.
if exist "venv" (
    echo [INFO] Found existing venv. Checking version...
    venv\Scripts\python --version | findstr "3.10" >nul
    if errorlevel 1 (
        echo [WARNING] Existing venv is not Python 3.10. Deleting...
        rmdir /s /q venv
    )
)

if not exist "venv" (
    echo Creating Python 3.10 venv...
    %PYTHON_PATH% -m venv venv
)

echo Activating venv and updating pip...
call venv\Scripts\activate
python -m pip install --upgrade pip
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

:: 2. Node Modules
if exist "client" (
    echo Installing Node dependencies in client/ ...
    cd client
    call npm install
    cd ..
) else (
    echo Error: client/ directory not found.
)

echo Setup Complete!
pause
