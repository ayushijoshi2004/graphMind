from __future__ import annotations

import pandas as pd


def extract_metadata(filename: str, dataframe: pd.DataFrame) -> dict:
    dtypes = {col: str(dtype) for col, dtype in dataframe.dtypes.items()}
    numeric_columns = dataframe.select_dtypes(include=["number"]).columns.tolist()
    datetime_columns = dataframe.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    if not datetime_columns:
        for column in dataframe.columns:
            if "date" in column.lower() or "time" in column.lower():
                datetime_columns.append(column)

    return {
        "filename": filename,
        "columns": dataframe.columns.tolist(),
        "data_types": dtypes,
        "sample_rows": dataframe.head(5).fillna("").to_dict(orient="records"),
        "numeric_columns": numeric_columns,
        "datetime_columns": list(dict.fromkeys(datetime_columns)),
    }
