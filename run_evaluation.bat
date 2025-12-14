@echo off
if not exist "venv" (
    echo Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b
)

echo Starting SportsEdit-AI Benchmark...
echo Usage: run_evaluation.bat [--batch_size N] [--iterations N] [--type playoff/regular/all]
echo ----------------------------------------------------------------------------------------

call venv\Scripts\activate
python utils/evaluate_batch.py %*
pause
