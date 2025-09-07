import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from typing import Any
import time

try:
    import requests
    RequestsError = requests.exceptions.RequestException
except Exception:  # requests not strictly required at import time
    class RequestsError(Exception):
        pass

import pandas as pd

from core.base import DataProvider, DataFrameLike


class AkshareFundProvider(DataProvider):
    """Wrap existing FinancialDataFetcher to core DataProvider interface."""

    def fetch(self, symbol: str, start_date: str, end_date: str) -> DataFrameLike:
        from get_data.ak_data_fetch import FinancialDataFetcher  # lazy import

        backoff_seconds = [1, 2, 4, 8, 10]
        last_err: Exception | None = None
        for delay in backoff_seconds:
            try:
                fetcher = FinancialDataFetcher()
                fetcher.fetch_fund_info(symbol=symbol, start_date=start_date, end_date=end_date)
                fetcher.fund_rename()
                df = fetcher.fund_info.iloc[:, :6].copy()
                df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                df.set_index('date', inplace=True)
                return df
            except (RequestsError, TimeoutError) as e:  # network timeouts
                last_err = e
                time.sleep(delay)
            except Exception as e:
                last_err = e
                time.sleep(delay)
        # If all retries failed, raise with hint
        raise RuntimeError(
            f"AkshareFundProvider fetch failed after retries for {symbol}. "
            f"Consider setting HTTP_PROXY/HTTPS_PROXY envs or using CsvOHLCVProvider."
        ) from last_err


