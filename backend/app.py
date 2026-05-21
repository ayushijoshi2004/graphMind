from __future__ import annotations

import io
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.charts.chart_generator import ChartGenerator
from backend.data.dataset_store import DatasetStore
from backend.llm.ollama_client import OllamaClient
from backend.llm.parser import parse_instruction
from backend.llm.prompt_builder import build_intent_prompt

app = FastAPI(title="GraphMind API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = DatasetStore()
llm = OllamaClient()
chart_generator = ChartGenerator()
current_chart_state: dict[str, Any] | None = None
conversation_history: list[dict[str, str]] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-csv")
async def upload_csv(files: list[UploadFile] = File(...)) -> dict:
    uploaded = []
    for file in files:
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        content = await file.read()
        dataframe = pd.read_csv(io.BytesIO(content))
        record = store.add_csv(file.filename, dataframe)
        uploaded.append(record.metadata)

    return {"uploaded": uploaded, "all_datasets": store.list_metadata()}


@app.post("/chat")
def chat(payload: dict[str, str]) -> dict:
    global current_chart_state

    prompt = payload.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")
    if not store.has_data():
        raise HTTPException(status_code=400, detail="Upload at least one CSV first.")

    composed_prompt = build_intent_prompt(prompt, store.list_metadata(), current_chart_state)
    raw_response = llm.generate(composed_prompt)
    instruction = parse_instruction(raw_response)

    figure = chart_generator.build_figure(instruction, store)
    current_chart_state = instruction.model_dump()
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history.append({"role": "assistant", "content": raw_response})

    return {
        "instruction": current_chart_state,
        "figure": figure.to_plotly_json(),
        "conversation_history": conversation_history,
        "datasets": store.list_metadata(),
    }
