# MultiAgentSystem — YouTube Medical Fact-Checker 🩺🔍

**Automated fact-checking of medical content from YouTube videos using LangGraph & LangServe.**

This pipeline fetches transcriptions, detects and deduplicates claims, selects a verification strategy (PubMed vs. Tavily), searches for sources, and generates an Evidence-Based Medicine (EBM) style report.

## 📦 Repository Contents

- **API (FastAPI + LangServe)**: Exposes the LangGraph workflow under the `/agent` endpoint.
- **GUI (Streamlit)**: A simple interface that streams agent progress step-by-step.
- **Tools**: Utilities for YouTube transcription, text chunking, clustering, and source retrieval.


## ✨ Key Features

- **LangGraph Workflow**: A deterministic agent graph with work distribution via subgraphs for multiple claims.
- **Gatekeeper**: A semantic filter that rejects non-medical videos.
- **Extractor (LLM)**: Extracts verifiable claims from transcript chunks.
- **Refiner (LLM + Clustering)**: Deduplicates claims and assigns verification tools (`PUBMED` or `TAVILY`).
- **Research (Tool)**: Source retrieval (via Tavily restricted to PubMed domains or general search) with an automatic fallback mechanism.
- **Judge (LLM)**: Issues a verdict (`True`, `False`, `Nuanced`, or `Unverified`) based on provided abstracts/content.
- **Reporter**: Generates a detailed Markdown report with claims, explanations, and citations.



## 🏗 Architecture

The main graph (global state: `AgentState`) executes the following nodes:

1.  **ingest**: Fetches metadata and transcript, chunks the text.
2.  **gatekeeper**: Validates if the content is medical.
3.  **extractor**: Extracts claims from chunks (map phase).
4.  **refiner**: Deduplicates, routes tools, and batches claims via clustering.
5.  **subgraph** (per claim): Handles research + judging.
6.  **reporter**: Compiles the final report.

### Workflow Visualization

![Schema](https://github.com/filipxcode/MultiAgentHealthFactChecker/blob/main/assets/schema.png?raw=true)

### Key Data Models

* `src/models/agent_state.py`: Global state (URL, chunks, claims, report).
* `src/models/claim.py`: Single claim with its source quote.
* `src/models/deduplicated_claims.py`: Deduplicated claims + assigned `verification_tool`.
* `src/models/judge.py`: `VerificationResult` (verdict, confidence, explanation, sources).



## 🚀 Quick Start

### 1. Requirements

* **Python 3.10+**
* (Optional) **Ollama** for local LLM execution.
* **API Keys**: `GROQ_API_KEY` and `TAVILY_API_KEY` (minimum required).

### 2. Installation

The repository uses standard pip installation. It is recommended to use a virtual environment.

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -U pip

# Install dependencies
pip install fastapi uvicorn streamlit python-dotenv pydantic pydantic-settings
pip install langserve langgraph langchain-core langchain-community langchain-text-splitters
pip install langchain-groq langchain-ollama
pip install tavily-python tenacity
pip install youtube-transcript-api yt-dlp
pip install semantic-router sentence-transformers scikit-learn numpy

# (Optional) Evaluation
pip install langsmith
```

> **Note:** If you encounter PyTorch issues during `sentence-transformers` installation, install the appropriate PyTorch version for your platform first from [pytorch.org](https://pytorch.org/).

### 3. Configuration (`.env`)

Create a `.env` file in the root directory:

```bash
# LLM (Groq)
GROQ_API_KEY=your_groq_key_here

# Search Engine
TAVILY_API_KEY=your_tavily_key_here

# (Optional) LangSmith tracing
LANGSMITH_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=youtube-fact-checker
``` 


## 💻 Usage

### Running the API (FastAPI + LangServe)

Start the backend server:

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

* **Swagger UI**: `http://localhost:8000/docs`
* **LangServe Endpoint**: `/agent`

### Running the GUI (Streamlit)

Ensure the API is running in a separate terminal, then run:

```bash
streamlit run src/gui/gui.py
```

### Data I/O

* **Input**: JSON object: `{ "video_url": "https://youtube.com/..." }`
* **Output**: Final Markdown report + intermediate states (`raw_claims`, `unique_claims`, `final_verdicts`).



## 🔍 Deep Dive: YouTube & Verification logic

### YouTube Transcription

* **Cache**: Transcripts are saved to `files/transcriptions.jsonl` to avoid redundant API calls.
* **Proxy**: By default, the code assumes a **Webshare** proxy configuration.
* *Don't have a proxy?* Set `web_proxy=False` inside `src/nodes/ingest.py`.
* *Have a proxy?* Ensure you configure it or place a `cookies.txt` file in the root if you hit rate limits.


### Verification Strategy

1. **PUBMED**: Uses Tavily restricted to `pubmed.ncbi.nlm.nih.gov` and `ncbi.nlm.nih.gov`.
2. **TAVILY**: Uses general web search.
3. **Fallback**: If PubMed search returns zero results, the system automatically triggers a general Tavily search to ensure coverage.

---

## 📂 Project Structure

```
src/
├── api/          # FastAPI + LangServe logic
├── graph/        # LangGraph definitions
├── nodes/        # Individual agent nodes (ingest, gatekeeper, etc.)
├── tools/        # Integrations (YouTube, Tavily, Clustering)
├── models/       # Pydantic models for state and results
├── settings/     # App configuration and LLM factories
└── gui/          # Streamlit user interface
files/            # Local cache for transcriptions
tests/            # Evaluation scripts
```



