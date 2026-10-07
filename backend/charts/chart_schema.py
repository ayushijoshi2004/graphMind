from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


ChartType = Literal["line", "bar", "scatter"]
ActionType = Literal["create_chart", "modify_chart"]


class SeriesSpec(BaseModel):
    dataset: str = Field(..., min_length=1)
    column: str = Field(..., min_length=1)


class FilterSpec(BaseModel):
    column: str
    operator: Literal[">", ">=", "<", "<=", "==", "!="]
    value: str | int | float


class TransformationSpec(BaseModel):
    operation: Literal["rolling_mean", "pct_change", "cumulative_sum"]
    column: str
    window: int | None = Field(default=None, gt=0)


class ChartInstruction(BaseModel):
    action: ActionType
    chart_type: ChartType
    title: str
    x_axis: str
    series: List[SeriesSpec] = Field(..., min_length=1)
    filters: List[FilterSpec] = Field(default_factory=list)
    transformations: List[TransformationSpec] = Field(default_factory=list)
