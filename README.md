# SportsEdit-AI: Agentic Sports Editorial Pipeline

A local, AI-powered newsroom that generates, verifies, and publishes sports recaps using `Ollama` (Llama 3.2 & Mistral), `LangGraph`, and `Streamlit`.

## 🚀 Features

*   **Agentic Writing:** Generates excitement-filled recaps (Writer Agent).
*   **Automated Fact-Checking:** Verifies stats against ground truth (Judge Agent).
*   **Self-Correction:** Automatically revises drafts if errors are found.
*   **Cost-Efficiency:** runs 100% locally on NVIDIA RTX 4050 (Cost: $0.00).

## 🛠 Prerequisites

1.  **Python 3.10+**
2.  **Ollama**: Install from [ollama.com](https://ollama.com).
3.  **Models**: Pull the required models:
    ```bash
    ollama pull llama3.2
    ollama pull mistral
    ```
4.  **Dataset**: Ensure Kaggle NBA dataset is in `../data/archive/`.

## ⚡ Quick Start

1.  **Setup Environment**:
    Double-click `setup_env.bat` OR run:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

3.  **Use**:
    *   Enter a Game ID (e.g., `22200477`) in the sidebar.
    *   Click "Draft Article".
    *   Watch the agents collaborate!

## 📂 Project Structure

*   `agents/`: processing logic for Writer and Judge.
*   `utils/`: Data processing helpers.
*   `graph.py`: LangGraph orchestration loop.
*   `app.py`: Streamlit frontend.

## 📊 Logic Flow

1.  **Input**: Box Score Data.
2.  **Writer**: Generates draft.
3.  **Judge**: Compares draft numbers vs. CSV numbers.
4.  **Loop**: If FAIL, Writer retries with feedback.
5.  **Output**: Verified Article.