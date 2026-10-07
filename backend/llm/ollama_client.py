from __future__ import annotations

import json
import os
import re

import requests


class OllamaClient:
    def __init__(self, model: str = "qwen2.5:3b") -> None:
        self.model = model
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.mode = "unknown"
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Ollama is available, otherwise fall back to mock mode."""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=2)
            if response.ok:
                self.mode = "ollama"
            else:
                self.mode = "mock"
        except (requests.ConnectionError, requests.Timeout):
            self.mode = "mock"

    def _mock_generate(self, prompt: str) -> str:
        """Generate a mock chart instruction based on the prompt."""
        # Extract dataset metadata from the prompt
        datasets = []
        marker = "Available datasets: "
        if marker in prompt:
            try:
                datasets, _ = json.JSONDecoder().raw_decode(prompt.split(marker, 1)[1])
            except (json.JSONDecodeError, TypeError):
                pass
        if not datasets:
            raise ValueError("No dataset metadata is available for chart generation.")

        user_request = prompt.split("User request: ", 1)[-1].split("\n\nReturn only", 1)[0].strip()
        user_request_lower = user_request.lower()

        # Determine chart type
        chart_type = "bar"  # Default to bar for comparisons
        if "line" in user_request_lower or "trend" in user_request_lower or "over time" in user_request_lower:
            chart_type = "line"
        elif "scatter" in user_request_lower or "point" in user_request_lower:
            chart_type = "scatter"

        # Get dataset info
        dataset_name = datasets[0]["filename"] if datasets else "data.csv"
        available_columns = datasets[0]["columns"] if datasets else []

        # Try to intelligently find columns based on the request
        x_column = None
        y_column = None

        # Look for "X vs Y" pattern
        vs_match = re.search(r'(\w+)\s+vs\s+(\w+)', user_request_lower)
        if vs_match:
            potential_x = vs_match.group(1).lower()
            potential_y = vs_match.group(2).lower()

            for col in available_columns:
                if potential_x in col.lower() and not x_column:
                    x_column = col
                if potential_y in col.lower() and not y_column:
                    y_column = col

        # If not found, try matching individual column names
        if not x_column or not y_column:
            for col in available_columns:
                if col.lower() in user_request_lower:
                    if not x_column:
                        x_column = col
                    elif not y_column:
                        y_column = col

        # Default fallback if we couldn't find columns
        if not x_column and available_columns:
            x_column = next(iter(datasets[0].get("datetime_columns", [])), available_columns[0])
        if not y_column and len(available_columns) > 1:
            y_column = next((col for col in datasets[0].get("numeric_columns", []) if col != x_column), available_columns[1])
        elif not y_column and available_columns:
            y_column = available_columns[0]

        if x_column == y_column and datasets[0].get("datetime_columns"):
            x_column = datasets[0]["datetime_columns"][0]

        # Look for filters (years, date ranges, etc.)
        filters = []

        # Match the entire requested year, not just January 1.
        year_match = re.search(r"\b(20\d{2})\b", user_request)
        if year_match:
            date_col = next((col for col in available_columns if "date" in col.lower()), None)
            year_col = next((col for col in available_columns if col.lower() == "year"), None)
            if date_col:
                year = int(year_match.group(1))
                filters.extend([
                    {"column": date_col, "operator": ">=", "value": f"{year}-01-01"},
                    {"column": date_col, "operator": "<", "value": f"{year + 1}-01-01"},
                ])
            elif year_col:
                numeric = year_col in datasets[0].get("numeric_columns", [])
                filters.append({"column": year_col, "operator": "==",
                                "value": int(year_match.group(1)) if numeric else year_match.group(1)})

        # Generate a descriptive title
        title_parts = []
        if y_column:
            title_parts.append(y_column)
        if x_column and x_column != y_column:
            title_parts.append(f"by {x_column}")
        if year_match:
            title_parts.append(f"({year_match.group(1)})")

        title = " ".join(title_parts) if title_parts else f"{chart_type.title()} Chart"

        # Create instruction
        instruction = {
            "action": "create_chart",
            "chart_type": chart_type,
            "title": title,
            "x_axis": x_column or "index",
            "series": [
                {
                    "dataset": dataset_name,
                    "column": y_column or "value"
                }
            ],
            "filters": filters,
            "transformations": []
        }

        return json.dumps(instruction)

    def generate(self, prompt: str) -> str:
        if self.mode == "mock":
            return self._mock_generate(prompt)

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("response", "")
        except (requests.ConnectionError, requests.Timeout) as e:
            # Fall back to mock mode if Ollama becomes unavailable
            self.mode = "mock"
            return self._mock_generate(prompt)

    def get_mode(self) -> str:
        """Return the current mode (ollama or mock)."""
        return self.mode