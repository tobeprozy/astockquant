from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Protocol


@dataclass
class Bar:
    date: Any
    open: float
    high: float
    low: float
    close: float
    volume: float


class DataProvider(ABC):
    @abstractmethod
    def fetch(self, symbol: str, start_date: str, end_date: str) -> "DataFrameLike":
        """Return OHLCV time series indexed by datetime for a symbol."""


class Strategy(Protocol):
    def on_bar(self, bar: Bar) -> Optional[Dict[str, Any]]:
        """Consume a bar and optionally return an order/signal payload."""


class BacktestEngine(ABC):
    @abstractmethod
    def run(self) -> Any:
        """Execute the backtest and return results object."""


class DataFrameLike(Protocol):
    def __iter__(self) -> Iterable[Any]:
        ...


