# AI Financial Assistant

A multi-agent financial assistant that delivers spoken market briefs and answers queries about your stock portfolio.

## Project Overview

This project is a sophisticated financial tool designed to provide users with real-time market insights, portfolio analysis, and earnings surprise highlights. It leverages a multi-agent architecture where different specialized agents collaborate to:

* Fetch market data for a user-defined stock portfolio.
* Scrape relevant financial news from online sources.
* Retrieve the most pertinent information using a vector store (RAG).
* Analyze the collected data for risk exposure and sentiment.
* Generate a natural language summary using a Large Language Model (LLM).
* Provide both text and spoken output via a Streamlit web application.

The system is orchestrated by a FastAPI backend, ensuring a modular and scalable design.

## Key Features

* **Dynamic Portfolio Analysis:** Define your stock portfolio in a simple JSON file.
* **Real-time Data:** Utilizes APIs (like Yahoo Finance) for up-to-date market information.
* **News Scraping & RAG:** Scrapes financial news and uses Retrieval-Augmented Generation to find the most relevant snippets for your queries.
* **Stateful Analysis:** Tracks portfolio changes from the previous day (via a daily log).
* **Confidence Scoring:** The retrieval system can identify when it doesn't have a good match for a query and ask for clarification.
* **Intent Routing:** Can differentiate between financial queries and general conversation.
* **Voice Interaction:** Supports both voice input (Speech-to-Text) and spoken output (Text-to-Speech).
* **Web Interface:** A user-friendly Streamlit application for interaction.

## Tech Stack

* **Backend Orchestration:** FastAPI, LangGraph
* **Frontend UI:** Streamlit
* **Language Model (LLM):** Google Gemini API (for core reasoning)
* **Voice I/O:**
    * Speech-to-Text (STT): OpenAI Whisper API
    * Text-to-Speech (TTS): OpenAI TTS API
* **Data Retrieval:**
    * `yfinance` (for market data)
    * `feedparser` (for RSS news scraping)
    * `sentence-transformers` (for embeddings)
    * `faiss-cpu` (for vector storage)
* **Core Libraries:** `requests`, `pydantic`, `python-dotenv`
* **Package Management & Runner:** `uv`

## Project Structure
```
project_root/
├── agents/             # Contains all specialized agents (API, scraper, retriever, etc.)
├── orchestrator/       # FastAPI microservice and LangGraph workflow
│   ├── main.py         # FastAPI app
│   └── graph.py        # LangGraph definition
├── streamlit_app/      # Streamlit frontend application
│   └── app.py
├── portfolio.json      # User-defined portfolio configuration
├── daily_log.json      # Stores previous day's portfolio for change analysis (auto-generated)
├── .env                # API keys (GOOGLE_API_KEY, OPENAI_API_KEY)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone git@github.com:ashutosh-utsav/finance-assistance.git
    cd finance-assistance
    ```

2.  **Install Dependencies:**
    This project uses `uv` for package management. Ensure `uv` is installed.
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Set Up API Keys:**
    * Create a `.env` file in the project root.
    * Add your API keys:
        ```env
        GOOGLE_API_KEY="google_gemini_api_key"
        OPENAI_API_KEY="openai_api_key"
        ```

4.  **Configure Your Portfolio:**
    * Edit the `portfolio.json` file in the project root to list the stocks you want to track and their allocations. Example:
        ```json
        {
          "portfolio": {
            "AAPL": { "allocation": 0.30, "region": "US", "lang": "en-US" },
            "MSFT": { "allocation": 0.30, "region": "US", "lang": "en-US" },
            "2330.TW": { "allocation": 0.40, "region": "TW", "lang": "zh-Hant" }
          }
        }
        ```

5.  **Install `ffmpeg` (for Voice Output):**
    The text-to-speech feature requires `ffmpeg` (specifically `ffplay`) to stream audio.
    * **macOS (Homebrew):** `brew install ffmpeg`
    * **Debian/Ubuntu:** `sudo apt-get update && sudo apt-get install ffmpeg`
    * **Windows:** Download from the official ffmpeg website and add `ffmpeg/bin` to your system's PATH.

## How to Run

You need to run two separate processes in two different terminals from the **project root directory**.

1.  **Terminal 1: Start the Backend Orchestrator (FastAPI):**
    ```bash
    uv run uvicorn orchestrator.main:app --reload
    ```
    This will typically run on `http://127.0.0.1:8000`.

2.  **Terminal 2: Start the Frontend UI (Streamlit):**
    ```bash
    uv run streamlit run streamlit_app/app.py
    ```
    This will typically open the app in your browser at `http://localhost:8501`.

Now you can interact with the AI Financial Assistant through the Streamlit web interface using text or voice.

