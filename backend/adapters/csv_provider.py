from __future__ import annotations

from typing import Optional

import pandas as pd

from core.base import DataProvider, DataFrameLike


class CsvOHLCVProvider(DataProvider):
    """Load OHLCV data from a CSV file with columns: date, open, high, low, close, volume."""

    def __init__(self, csv_path: str, date_col: str = 'date', date_format: Optional[str] = '%Y-%m-%d') -> None:
        self.csv_path = csv_path
        self.date_col = date_col
        self.date_format = date_format

    def fetch(self, symbol: str, start_date: str, end_date: str) -> DataFrameLike:
        df = pd.read_csv(self.csv_path)
        if self.date_format:
            df[self.date_col] = pd.to_datetime(df[self.date_col], format=self.date_format)
        else:
            df[self.date_col] = pd.to_datetime(df[self.date_col])
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
        df.set_index('date', inplace=True)
        # Filtering by date boundaries if present in index
        df = df.loc[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]
        return df


