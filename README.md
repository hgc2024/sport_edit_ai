# SportsEdit-AI: Agentic Sports Editorial Pipeline

A local, AI-powered newsroom that generates, verifies, and publishes sports recaps using `Ollama` (Llama 3.2 & Mistral), `LangGraph`, `FastAPI`, and `React`.

## 🚀 Features

*   **Agentic Writing:** Generates excitement-filled recaps (Writer Agent).
*   **Automated Fact-Checking:** Verifies stats against ground truth (Judge Agent).
*   **Self-Correction:** Automatically revises drafts if errors are found.
*   **Local & Cost-Efficient:** Runs 100% locally on NVIDIA RTX 4050 (Cost: $0.00).
*   **Modern UI:** Premium React frontend with Dark Mode and real-time status updates.
*   **Robust Backend:** FastAPI server handling agent orchestration.

## 🛠 Prerequisites

1.  **Python 3.10+**
2.  **Node.js v18+** (Required for React Client)
3.  **Ollama**: Install from [ollama.com](https://ollama.com).
4.  **Models**: Pull the required models:
    ```bash
    ollama pull llama3.2
    ollama pull mistral
    ```
5.  **Dataset**: Ensure Kaggle NBA dataset is in `../data/archive/`.

## ⚡ Quick Start

1.  **Setup Environment**:
    Double-click `setup_env.bat` to install both Python and Node dependencies.
    *   Creates/activates Python `venv`.
    *   Installs pip requirements (`fastapi`, `langgraph`, etc.).
    *   Installs npm packages in `client/`.

2.  **Run the System**:
    Double-click `start_app.bat` to launch both servers:
    *   **Backend (FastAPI)**: `http://localhost:8000`
    *   **Frontend (React)**: `http://localhost:5173`

3.  **Use**:
    *   Open `http://localhost:5173`.
    *   Enter a Game ID (e.g., `22200477`).
    *   Click "Draft Article" and verify the ROI calculations!

## 📂 Project Structure

*   `agents/`: Processing logic for Writer and Judge agents.
*   `api.py`: FastAPI backend entry point (serves logic to frontend).
*   `client/`: React/Vite Frontend source code.
*   `graph.py`: LangGraph orchestration loop.
*   `utils/`: Data processing helpers.
*   `setup_env.bat` / `start_app.bat`: Automation scripts.

## 📊 Logic Flow

1.  **Frontend**: User requests a draft via React UI.
2.  **API**: FastAPI Endpoint triggers Graph.
3.  **Writer**: Generates draft using Llama 3.2.
4.  **Judge**: Verifies stats using Mistral.
5.  **Loop**: If FAIL, Writer retries with feedback.
6.  **Response**: Final text + Verification Log + Execution Stats returned to UI.