# GraphMind

**Turn CSV data and natural-language requests into interactive charts.** GraphMind is a local data-exploration workspace: upload datasets, ask for a visualization, then refine it through follow-up prompts.

## What the app does

1. Upload one or more CSV files and inspect their column metadata in the dataset sidebar.
2. Ask for a line, bar, or scatter chart, naming the dataset/columns when useful.
3. View an interactive Plotly chart alongside the conversation.
4. Apply supported filters and transformations, including rolling means, percentage changes and cumulative sums.

For example, with a CSV containing `date` and `sales`, try “Show sales over time as a line chart.” Prompt interpretation depends on whether Ollama or the limited rule-based fallback is active.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 18, TypeScript, Vite 7, Tailwind CSS 3 |
| Visualization | Plotly.js and react-plotly.js in the browser; Plotly in Python |
| Backend | Python, FastAPI, Uvicorn, pandas |
| Validation | Pydantic 2 chart-instruction schemas |
| Local AI | Ollama with `qwen2.5:3b` |
| Tests | Python unittest regression tests |

## How it works

```text
CSV uploads → pandas datasets + column metadata
Prompt + metadata + previous chart → Ollama (or rule-based fallback)
JSON instructions → Pydantic validation → Python chart generator → Plotly figure
```

The model interprets intent; it does not execute generated code or supply Plotly syntax. Chart construction and supported data transformations happen in Python. The fallback is a constrained local demo mode, not AI inference.

## Run locally

Requires Python 3.10+ and Node.js 22.12+. Ollama is optional.

On macOS/Linux, from the repository root:

```sh
./scripts_dev_up.sh
```

The script creates `.venv`, installs Python dependencies, starts FastAPI, and starts the Vite frontend. For manual setup:

```sh
# Terminal 1, repository root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
uvicorn backend.app:app --reload

# Terminal 2, repository root
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`; the frontend calls `http://localhost:8000`. On Windows, activate `.venv` with `.venv\Scripts\Activate.ps1` instead of the shell command above.

### Enable local AI

Install and start Ollama, then download the model:

```sh
ollama serve
# In another terminal:
ollama pull qwen2.5:3b
```

Start/restart the backend after Ollama is ready. `GET /llm-status` reports `ollama` or `mock`. `OLLAMA_BASE_URL` can override the default `http://localhost:11434`. There is no cloud API key requirement for this local model.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/llm-status` | Current intent-parser mode |
| POST | `/upload-csv` | Multipart CSV uploads (`files`); 10 MB maximum per file |
| POST | `/chat` | JSON `{ "prompt": "..." }`; returns instructions, chart and conversation state |

## Checks

```sh
python -m unittest discover -s backend/tests -v
cd frontend
npm run build
```

## Scope and next steps

This is a single-user local prototype. Uploaded data, chart state and history live in process memory and reset on restart. There is no per-user isolation or persistence; keep it local and use sample data when demonstrating it.

The next engineering priorities are configurable frontend API URLs, per-session state, stronger validation of requested columns/types, broader API/real-model tests, and a small sample dataset with reproducible example prompts.

## Source map

- `backend/app.py`: upload/chat routes and process-local state.
- `backend/llm/`: prompt construction, Ollama client and JSON parsing.
- `backend/charts/`: instruction schemas, filters, transformations and chart generation.
- `backend/data/`: dataset storage and metadata extraction.
- `frontend/src/`: chat, dataset sidebar, chart canvas and API client.
