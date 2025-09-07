from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, Optional

from core.base import Strategy, Bar


class SMACrossStrategy(Strategy):
    def __init__(self, fast: int = 5, slow: int = 20, unit: float = 1.0) -> None:
        self.fast = fast
        self.slow = slow
        self.unit = unit
        self.fast_window: Deque[float] = deque(maxlen=fast)
        self.slow_window: Deque[float] = deque(maxlen=slow)
        self.in_position: bool = False

    def on_bar(self, bar: Bar) -> Optional[Dict[str, Any]]:
        self.fast_window.append(bar.close)
        self.slow_window.append(bar.close)
        if len(self.slow_window) < self.slow:
            return None
        fast_ma = sum(self.fast_window) / len(self.fast_window)
        slow_ma = sum(self.slow_window) / len(self.slow_window)
        if not self.in_position and fast_ma > slow_ma:
            self.in_position = True
            return {"action": "buy", "size": self.unit}
        if self.in_position and fast_ma < slow_ma:
            self.in_position = False
            return {"action": "sell", "size": self.unit}
        return None


