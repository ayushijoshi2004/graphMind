from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .metadata_extractor import extract_metadata


@dataclass
class DatasetRecord:
    name: str
    dataframe: pd.DataFrame
    metadata: dict


class DatasetStore:
    def __init__(self) -> None:
        self._datasets: dict[str, DatasetRecord] = {}

    def add_csv(self, filename: str, dataframe: pd.DataFrame) -> DatasetRecord:
        metadata = extract_metadata(filename, dataframe)
        record = DatasetRecord(name=filename, dataframe=dataframe, metadata=metadata)
        self._datasets[filename] = record
        return record

    def get(self, name: str) -> DatasetRecord:
        return self._datasets[name]

    def list_metadata(self) -> list[dict]:
        return [record.metadata for record in self._datasets.values()]

    def has_data(self) -> bool:
        return bool(self._datasets)
