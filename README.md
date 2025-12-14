# SportsEdit-AI: Agentic Sports Editorial Pipeline

A local, AI-powered newsroom that generates, verifies, and publishes sports recaps using `Ollama` (Llama 3.2 & Mistral), `LangGraph`, `FastAPI`, and `React`.

## 🚀 Features

*   **Agentic Writing:** Generates excitement-filled recaps (Writer Agent).
*   **Pluralistic Jury:** A 3-agent panel (Fact, Style, Bias) verifies every draft.
*   **Evaluation Lab:** Run batch benchmarks to measure ROI, Consistency, and Safety.
*   **Local & Cost-Efficient:** Runs 100% locally on NVIDIA RTX 4050 (Cost: $0.00).

## 🧠 Methodology (NeurIPS 2025 Alignment)

### 1. The Jury System (Pluralistic Alignment)
Based on *Gordon & Shen (2025)*, we replaced the single Judge with a **Pluralistic Jury**:
*   **The Fact Checker (Mistral)**: Strict numeric verification.
*   **The Style Critic (Llama 3.2)**: Ensures high-energy sports journalism.
*   **The Bias Watchdog (Mistral)**: Checks for unfair framing against losing teams.
**Logic**: If Fact OR Bias fails, the draft is rejected (Veto Power). Style provides feedback.

### 2. Batch Evaluation & ROI
The new **Evaluation Lab** dashboard allows running random batches (e.g., 3 games x 1 iteration) to measure:
*   **Safety Rate**: % of drafts requiring zero human intervention.
*   **Throughput**: Articles generated per minute.
*   **ROI Multiplier**: Human Cost ($15.00) vs. Agent Cost (~$0.05).

## 🛠 Prerequisites

1.  **Python 3.10+** & **Node.js v18+**
2.  **Ollama**: Install & Pull Models:
    ```bash
    ollama pull llama3.2
    ollama pull mistral
    ```
3.  **Dataset**: Ensure Kaggle NBA dataset is in `../data/archive/`.

## ⚡ Quick Start

1.  **Setup Environment**:
    Double-click `setup_env.bat` to install dependencies (Python & Node).

2.  **Run the System**:
    Double-click `start_app.bat` to launch backend (8000) and frontend (5173).

3.  **Operating Modes**:
    *   **Newsroom**: Enter a Game ID -> Click "Draft Article".
    *   **Evaluation Lab**: Click the toggle in the header -> Click "Run Benchmark" to run a random batch test.

## 📈 CLI Benchmarking (Headless Mode)

For long-running quality assurance tests, use the command-line interface:

```bash
run_evaluation.bat --batch_size 10 --iterations 3 --type playoff
```

**Parameters:**
*   `--batch_size`: Number of unique games to sample.
*   `--iterations`: Number of times to run *each* game (tests consistency).
*   `--type`: `playoff` | `regular` | `all`.
*   `--output`: Output JSON file (default: `benchmark_results.json`).

## 📊 Logic Flow

1.  **Input**: Box Score Data.
2.  **Writer**: Generates draft (Llama 3.2).
3.  **Jury**: Parallel execution of Fact, Style, and Bias agents.
4.  **Consensus**: Votes aggregated. Revisions triggered if necessary.
5.  **Output**: Verified Article + Jury Feedback.