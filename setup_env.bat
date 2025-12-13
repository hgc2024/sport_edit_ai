@echo off
echo Setting up virtual environment for SportsEdit-AI...

:: Create venv if it doesn't exist
if not exist "venv" (
    echo Creating venv...
    python -m venv venv
) else (
    echo venv already exists.
)

:: Activate venv
echo Activating venv...
call venv\Scripts\activate

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete. To run the app, verify Ollama is running and run 'streamlit run app.py'.
pause
