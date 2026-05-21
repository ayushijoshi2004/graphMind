from __future__ import annotations

import os

import requests


class OllamaClient:
    def __init__(self, model: str = "qwen2.5:3b") -> None:
        self.model = model
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("response", "")


def mock_generate(prompt: str) -> str:
    lower = prompt.lower()
    chart_type = "line"
    if "scatter" in lower:
        chart_type = "scatter"
    elif "bar" in lower:
        chart_type = "bar"

    return (
        '{"action":"create_chart","chart_type":"'
        + chart_type
        + '","title":"Generated Chart","x_axis":"Date","series":[{"dataset":"demo.csv","column":"Value"}],"filters":[],"transformations":[]}'
    )
