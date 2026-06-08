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
        datasets_section = re.search(r'Datasets:\s*(\[.*?\])', prompt, re.DOTALL)
        datasets = []
        if datasets_section:
            try:
                datasets = json.loads(datasets_section.group(1))
            except json.JSONDecodeError:
                pass
        
        # Extract user request
        user_request_match = re.search(r'User request:\s*(.+)$', prompt, re.DOTALL)
        user_request = user_request_match.group(1).strip() if user_request_match else prompt
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
            x_column = available_columns[0]
        if not y_column and len(available_columns) > 1:
            y_column = available_columns[1]
        elif not y_column and available_columns:
            y_column = available_columns[0]

        # Look for filters (years, date ranges, etc.)
        filters = []

        # Check for year filtering
        year_match = re.search(r'\b(20\d{2})\b', user_request)
        if year_match:
            year_str = year_match.group(1)
            # Find a date/year column
            date_col = None
            for col in available_columns:
                if any(term in col.lower() for term in ['date', 'year', 'time']):
                    date_col = col
                    break

            if date_col:
                # Use a string match since dates are in YYYY-MM-DD format
                filters.append({
                    "column": date_col,
                    "operator": "==",
                    "value": f"{year_str}-01-01"  # Match the date format in the CSV
                })

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