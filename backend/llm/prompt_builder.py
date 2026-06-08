from __future__ import annotations

import json


def build_intent_prompt(user_prompt: str, dataset_metadata: list[dict], current_chart_state: dict | None) -> str:
    schema = {
        "action": "create_chart | modify_chart",
        "chart_type": "line | bar | scatter",
        "title": "string",
        "x_axis": "string (column name to use for x-axis)",
        "series": [{"dataset": "string (filename)", "column": "string (column name)"}],
        "filters": [{"column": "string", "operator": "> | >= | < | <= | == | !=", "value": "string | number"}],
        "transformations": [{"operation": "rolling_mean | pct_change | cumulative_sum", "column": "string", "window": "number (optional)"}],
    }

    return (
        "You are a chart intent parser. Return strict JSON only.\n"
        "Do not include markdown, explanation, or code fences.\n"
        "CRITICAL: Filter objects must use 'column' not 'field'.\n"
        "CRITICAL: Filter objects must include 'column', 'operator', and 'value' fields.\n"
        f"Schema: {json.dumps(schema, indent=2)}\n\n"
        f"Available datasets: {json.dumps(dataset_metadata, indent=2, default=str)}\n\n"
        f"Current chart state: {json.dumps(current_chart_state or {}, default=str)}\n\n"
        f"User request: {user_prompt}\n\n"
        "Return only the JSON object, nothing else."
    )