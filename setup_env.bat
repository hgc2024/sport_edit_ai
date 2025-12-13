@echo off
echo Setting up SportsEdit-AI Environment...

:: 1. Python Venv
if not exist "venv" (
    echo Creating Python venv...
    python -m venv venv
)
echo Activating venv and installing Python deps...
call venv\Scripts\activate
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
