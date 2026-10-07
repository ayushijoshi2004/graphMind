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
    return {"mode": llm.get_mode()}


@app.post("/upload-csv")
async def upload_csv(files: list[UploadFile] = File(...)) -> dict:
    uploaded = []
    for file in files:
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        content = await file.read(10 * 1024 * 1024 + 1)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="CSV files must be at most 10 MB.")
        try:
            dataframe = pd.read_csv(io.BytesIO(content))
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Upload a non-empty, valid UTF-8 CSV file.") from None
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

    try:
        # Step 1: Build the prompt
        composed_prompt = build_intent_prompt(prompt, store.list_metadata(), current_chart_state)
        print(f"[DEBUG] Composed prompt length: {len(composed_prompt)}")
        
        # Step 2: Generate LLM response
        raw_response = llm.generate(composed_prompt)
        print(f"[DEBUG] Raw LLM response: {raw_response[:200]}...")
        
        # Step 3: Parse the instruction
        try:
            instruction = parse_instruction(raw_response)
            print(f"[DEBUG] Parsed instruction: {instruction.model_dump()}")
        except Exception as e:
            print(f"[ERROR] Failed to parse instruction: {e}")
            print(f"[ERROR] Raw response was: {raw_response}")
            raise HTTPException(
                status_code=500, 
                detail="Unable to interpret this chart request. Try specifying the dataset and columns."
            )
        
        # Step 4: Build the figure
        try:
            figure = chart_generator.build_figure(instruction, store)
            print(f"[DEBUG] Figure generated successfully")
        except Exception as e:
            print(f"[ERROR] Failed to build figure: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate the requested chart. Check the columns and transformations."
            )
        
        # Step 5: Convert figure to JSON (with numpy handling)
        try:
            import json
            import numpy as np
            
            # Custom JSON encoder to handle numpy types
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, np.integer):
                        return int(obj)
                    if isinstance(obj, np.floating):
                        return float(obj)
                    if isinstance(obj, np.ndarray):
                        return obj.tolist()
                    return super().default(obj)
            
            figure_dict = json.loads(json.dumps(figure.to_plotly_json(), cls=NumpyEncoder))
            print(f"[DEBUG] Figure serialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to serialize figure: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to return the generated chart."
            )
        
        # Step 6: Save state and return
        current_chart_state = instruction.model_dump()
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": raw_response})

        return {
            "instruction": current_chart_state,
            "figure": figure_dict,
            "conversation_history": conversation_history,
            "datasets": store.list_metadata(),
            "llm_mode": llm.get_mode(),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to process this chart request.")
