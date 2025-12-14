@echo off
if not exist "venv" (
    echo Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b
)

echo Starting SportsEdit-AI Benchmark...
echo Usage: run_evaluation.bat [--batch_size N] [--iterations N] [--type playoff/regular/all] [--red_team] [--recall]
echo ----------------------------------------------------------------------------------------

call venv\Scripts\activate

if not exist "context_cache" (
    echo [System] Context Cache not found. Building deep context... (This happens once)
    python utils/build_context.py
)

python utils/evaluate_batch.py %*
pause
