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
*   **The Editor-in-Chief (Mistral)**: Enforces journalistic standards and narrative stakes.
*   **The Bias Watchdog (Mistral)**: Checks for unfair framing against losing teams.
**Logic**: If ANY agent fails, the draft is rejected (Unanimous Consent). Editor provides qualitative feedback.

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

## 🧠 Advanced Methodology (NeurIPS 2025 Inspired)

### 1. The Media Enterprise Jury (Expanded Architecture)
We have evolved the single "Judge" into a sophisticated **6-Agent Media Enterprise** organized into three functional divisions:

#### A. The Standards Division (Gatekeepers)
*   **Fact Checker (Mistral)**: Strict numeric verification against box scores. **(Veto Power)**
*   **Brand Safety Officer (Mistral)**: Protects ad revenue by flagging toxicity, harsh sentiment, or controversy. **(Veto Power)**
*   **Bias Watchdog (Mistral)**: Checks for unfair framing against losing teams. **(Veto Power)**

#### B. The Editorial Division (Quality)
*   **Editor-in-Chief (Mistral)**: "The Voice". Assigns a **Quality Score (1-10)** based on narrative flow, context, and proper team naming. **(Fail if Score < 6)**.

#### C. The Growth Division (Optimization)
*   **SEO Strategist (Mistral)**: Maximizes search traffic. Checks keywords and entity linking. Assigns **SEO Score (0-100)**.
*   **Engagement Editor (Mistral)**: Maximizes "Time on Page". Checks hooks and readability. Assigns **Engagement Score (1-10)**.

### 2. SOTA Evaluation Metrics
The "Evaluation Lab" now measures:
*   **Avg Quality Score**: Editorial grade (e.g., 8.5/10).
*   **Hallucination Rate**: Specific % of Fact/Entity errors.
*   **SEO & Engagement Scores**: Growth metrics for every article.
*   **Safety Rate**: % of drafts passing all "Gatekeeper" checks.
*   **Detailed Logging**: Captures full decision trees (JSON) for all 6 agents.

### 3. Deep Context RAG (New!)
The system is no longer "amnesiac". We have implemented a **Temporal Context Engine** that replays the entire 20-year history of the NBA to build state-aware context for every game.

On the first run, the system will automatically:
1.  Run `utils/build_context.py` (ETL Pipeline).
2.  Generate thousands of "Context Snapshots" (JSON) in `context_cache/`.
3.  Inject **Season Records**, **Winning Streaks**, and **Series History** into the Writer's prompt.

This allows the AI to write sentences like *"The Suns snapped a 3-game losing streak..."* based on actual historical data.

## 💻 CLI Benchmark Suite (Robust Testing)
For automated, overnight testing, use the included batch script. This runs the evaluation in "Headless Mode" and generates a `benchmark_results_report.md`.

> **Graceful Shutdown**: You can press `Ctrl+C` at any time. The script will catch the interrupt, save all results processed so far, and generate the final report before exiting.

```bash
# Run a large-scale SOTA benchmark (Recmmended for Overnight)
run_evaluation.bat --batch_size 100 --iterations 3 --red_team --recall
```

### Arguments:
*   `--batch_size`: Number of distinct games to test.
*   `--iterations`: How many times to re-run the *same* game (tests consistency/variance).
*   `--red_team`: Enables **Adversarial Data Poisoning** (Score Swapping, Star Inflation) to test Jury resilience.
*   `--recall`: Enables **Semantic Fact Verification** using a secondary Analyst agent (Mistral).completeness checking.
*   **Output**: Generates a professional `benchmark_results_report.md` with grades and failure analysis.

## 📊 Logic Flow

1.  **Input**: Box Score Data.
2.  **Writer**: Generates draft (Llama 3.2).
3.  **Jury**: Parallel execution of 6 specialized agents (Standards, Editorial, Growth).
4.  **Consensus**: Complex voting logic (Vetoes + Quality Gates).
5.  **Output**: Verified Article + Jury Feedback.