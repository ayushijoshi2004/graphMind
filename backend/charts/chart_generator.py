from __future__ import annotations

import operator
from functools import reduce

import pandas as pd
import plotly.graph_objects as go

from backend.charts.chart_schema import ChartInstruction
from backend.data.dataset_store import DatasetStore

OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


class ChartGenerator:
    def build_figure(self, instruction: ChartInstruction, store: DatasetStore) -> go.Figure:
        fig = go.Figure()

        for series in instruction.series:
            record = store.get(series.dataset)
            frame = self._apply_filters(record.dataframe.copy(), instruction)
            frame = self._apply_transformations(frame, instruction)
            x = frame[instruction.x_axis]
            y = frame[series.column]
            name = f"{series.dataset}:{series.column}"

            if instruction.chart_type == "line":
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=name))
            elif instruction.chart_type == "scatter":
                fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name=name))
            elif instruction.chart_type == "bar":
                fig.add_trace(go.Bar(x=x, y=y, name=name))

        fig.update_layout(title=instruction.title, template="plotly_white")
        return fig

    def _apply_filters(self, frame: pd.DataFrame, instruction: ChartInstruction) -> pd.DataFrame:
        masks = []
        for filter_spec in instruction.filters:
            comparator = OPS[filter_spec.operator]
            masks.append(comparator(frame[filter_spec.column], filter_spec.value))

        if masks:
            frame = frame[reduce(operator.and_, masks)]
        return frame

    def _apply_transformations(self, frame: pd.DataFrame, instruction: ChartInstruction) -> pd.DataFrame:
        for transform in instruction.transformations:
            col = transform.column
            if transform.operation == "rolling_mean":
                window = transform.window or 3
                frame[col] = frame[col].rolling(window=window).mean()
            elif transform.operation == "pct_change":
                frame[col] = frame[col].pct_change()
            elif transform.operation == "cumulative_sum":
                frame[col] = frame[col].cumsum()
        return frame
