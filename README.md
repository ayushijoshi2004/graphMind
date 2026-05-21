# GraphMind

GraphMind is a local AI-powered data visualization workspace.

## MVP stack

- Frontend: React + TypeScript + TailwindCSS
- Backend: FastAPI + pandas + Plotly
- LLM: Ollama (`qwen2.5:3b`) for intent parsing only

## Architecture principle

The LLM never executes code and never emits Plotly syntax. It only returns strict JSON chart instructions. The backend validates instructions and safely generates charts.

## Run backend

```bash
pip install fastapi uvicorn pandas plotly pydantic requests python-multipart
uvicorn backend.app:app --reload
```

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
