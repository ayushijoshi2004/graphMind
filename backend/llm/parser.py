from __future__ import annotations

import json

from backend.charts.chart_schema import ChartInstruction


def parse_instruction(raw: str) -> ChartInstruction:
    data = json.loads(raw)
    return ChartInstruction.model_validate(data)
