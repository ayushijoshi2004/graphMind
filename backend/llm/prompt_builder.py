from __future__ import annotations

import json


def build_intent_prompt(user_prompt: str, dataset_metadata: list[dict], current_chart_state: dict | None) -> str:
    schema = {
        "action": "create_chart | modify_chart",
        "chart_type": "line | bar | scatter",
        "title": "string",
        "x_axis": "string",
        "series": [{"dataset": "string", "column": "string"}],
        "filters": [],
        "transformations": [],
    }

    return (
        "You are a chart intent parser. Return strict JSON only.\n"
        "Do not include markdown and do not include explanation.\n"
        f"Schema: {json.dumps(schema)}\n"
        f"Current chart state: {json.dumps(current_chart_state or {}, default=str)}\n"
        f"Datasets: {json.dumps(dataset_metadata, default=str)}\n"
        f"User request: {user_prompt}\n"
    )
