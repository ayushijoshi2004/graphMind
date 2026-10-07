import json
import unittest
import pandas as pd
from backend.llm.ollama_client import OllamaClient
from backend.llm.prompt_builder import build_intent_prompt
from backend.llm.parser import parse_instruction
from backend.charts.chart_generator import ChartGenerator
from backend.data.dataset_store import DatasetStore

class MockChartTests(unittest.TestCase):
    def test_nested_metadata_and_full_year(self):
        store = DatasetStore()
        store.add_csv('sales.csv', pd.DataFrame({'date': ['2025-01-01', '2025-06-01', '2026-01-01'], 'revenue': [1, 2, 3]}))
        prompt = build_intent_prompt('show revenue over time for 2025', store.list_metadata(), None)
        client = object.__new__(OllamaClient)
        instruction = parse_instruction(client._mock_generate(prompt))
        self.assertEqual(instruction.series[0].dataset, 'sales.csv')
        self.assertEqual(instruction.series[0].column, 'revenue')
        self.assertEqual(instruction.x_axis, 'date')
        figure = ChartGenerator().build_figure(instruction, store)
        self.assertEqual(list(figure.data[0].y), [1, 2])

    def test_missing_metadata_is_clear_error(self):
        with self.assertRaisesRegex(ValueError, 'metadata'):
            object.__new__(OllamaClient)._mock_generate('User request: line chart')
