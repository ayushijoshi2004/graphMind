# GraphMind

GraphMind is a local AI-powered data visualization workspace.

## What you need

- Python 3.10+
- Node.js 22.12+
- (Optional) Ollama for real local LLM intent parsing

If Ollama is not installed/running, GraphMind now falls back to a built-in **mock intent mode** so you can still run and test the full flow.

## Quick start (one command)

```bash
./scripts_dev_up.sh
```

This creates a Python virtualenv (if missing), installs backend deps, starts FastAPI, installs frontend deps (if missing), and starts Vite.

## MVP stack

- Frontend: React + TypeScript + TailwindCSS
- Backend: FastAPI + pandas + Plotly
- LLM: Ollama (`qwen2.5:3b`) for intent parsing only

## Architecture principle

The LLM never executes code and never emits Plotly syntax. It only returns strict JSON chart instructions. The backend validates instructions and safely generates charts.

## Run backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

Backend runs on `http://127.0.0.1:8000`.

Useful endpoints:

- `GET /health`
- `GET /llm-status` (`ollama` or `mock` mode)
- `POST /upload-csv`
- `POST /chat`

## 2) Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173` and talks to backend at `http://localhost:8000`.

## 3) Optional: enable real Ollama mode

Install Ollama, then:

```bash
ollama serve
ollama pull qwen2.5:3b
```

Once available, `/chat` will use Ollama automatically.

## IntelliJ setup

Yes, this works in IntelliJ.

- Open project root in IntelliJ.
- Configure Python interpreter for backend.
- Create Python run config:
  - Module: `uvicorn`
  - Args: `backend.app:app --reload`
  - Working directory: project root
- Open `frontend/` as Node project and run `npm run dev` in terminal (or npm run config).

## Architecture principle

The LLM never executes code and never emits Plotly syntax. It only returns strict JSON chart instructions. The backend validates instructions and safely generates charts.
## API endpoints

- `POST /upload-csv` uploads one or more CSV files and stores metadata in memory.
- `POST /chat` parses natural-language intent and returns a Plotly figure JSON payload.
- `GET /health` basic healthcheck.

## Suggested frontend wiring

The frontend scaffold under `frontend/` includes:

- chat panel
- dataset sidebar
- prompt input
- graph canvas

and API helpers to call the backend endpoints.

## Scope and verification

This is a single-user local prototype: datasets and chat state are held in memory and reset on restart. Use public/sample CSV data when demonstrating it. Ollama is optional; mock mode uses dataset metadata and simple prompt rules rather than AI inference.

Run backend regression checks with `python -m unittest discover -s backend/tests -v`. Build the frontend with `npm run build` from `frontend/`. Dependencies are installed locally and are not part of source control.
