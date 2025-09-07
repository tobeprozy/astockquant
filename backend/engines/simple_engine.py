from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd

from core.base import BacktestEngine, DataProvider, Bar


@dataclass
class SimpleResult:
    equity_curve: pd.Series
    trades: int


class SimpleLoopEngine(BacktestEngine):
    """A minimal event-loop backtest engine using the core Strategy protocol.

    Strategy should return optional dict signals like {"action": "buy"|"sell", "size": float}.
    Position is managed in units; execution price is bar.close; no commission/slippage.
    """

    def __init__(
        self,
        data_provider: DataProvider,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy: Any,
        starting_cash: float = 100000.0,
    ) -> None:
        self.data_provider = data_provider
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.strategy = strategy
        self.starting_cash = starting_cash

    def run(self) -> SimpleResult:
        df = self.data_provider.fetch(self.symbol, self.start_date, self.end_date)
        cash = self.starting_cash
        position = 0.0
        equity = []
        index = []
        trades = 0
        for ts, row in df.iterrows():
            bar = Bar(date=ts, open=float(row["open"]), high=float(row["high"]), low=float(row["low"]), close=float(row["close"]), volume=float(row["volume"]))
            signal: Optional[Dict[str, Any]] = self.strategy.on_bar(bar)
            price = bar.close
            if signal and signal.get("action") == "buy":
                size = float(signal.get("size", 0))
                if size > 0:
                    cost = size * price
                    if cost <= cash:
                        cash -= cost
                        position += size
                        trades += 1
            elif signal and signal.get("action") == "sell":
                size = float(signal.get("size", 0))
                if size > 0 and position >= size:
                    cash += size * price
                    position -= size
                    trades += 1
            # mark-to-market equity
            index.append(ts)
            equity.append(cash + position * price)
        equity_curve = pd.Series(equity, index=index, name="equity")
        return SimpleResult(equity_curve=equity_curve, trades=trades)


