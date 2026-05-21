from __future__ import annotations

import io
import json
import os
from typing import Any

import pandas as pd
import requests
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


@app.get("/llm-status")
def llm_status() -> dict[str, str]:
    try:
        requests.get(f"{llm.base_url}/api/tags", timeout=3).raise_for_status()
        return {"status": "ok", "mode": "ollama"}
    except requests.RequestException:
        return {"status": "degraded", "mode": "mock", "message": "Ollama unavailable. Using mock mode."}


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


def _build_mock_instruction(user_prompt: str) -> str:
    metadata = store.list_metadata()[0]
    dataset = metadata["filename"]
    x_axis = metadata["columns"][0]
    series_column = metadata.get("numeric_columns", [])
    y_axis = series_column[0] if series_column else metadata["columns"][1]

    lower = user_prompt.lower()
    chart_type = "line"
    if "scatter" in lower:
        chart_type = "scatter"
    elif "bar" in lower:
        chart_type = "bar"

    payload = {
        "action": "create_chart" if current_chart_state is None else "modify_chart",
        "chart_type": chart_type,
        "title": f"{y_axis} vs {x_axis}",
        "x_axis": x_axis,
        "series": [{"dataset": dataset, "column": y_axis}],
        "filters": [],
        "transformations": [],
    }
    return json.dumps(payload)


@app.post("/chat")
def chat(payload: dict[str, str]) -> dict:
    global current_chart_state

    prompt = payload.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")
    if not store.has_data():
        raise HTTPException(status_code=400, detail="Upload at least one CSV first.")

    composed_prompt = build_intent_prompt(prompt, store.list_metadata(), current_chart_state)

    try:
        raw_response = llm.generate(composed_prompt)
        llm_mode = "ollama"
    except requests.RequestException:
        raw_response = _build_mock_instruction(prompt)
        llm_mode = "mock"

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
        "llm_mode": llm_mode,
    }
