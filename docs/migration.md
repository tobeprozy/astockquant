## Migration Guide

本文指导如何从旧目录迁移到新的分层结构。

### 旧 -> 新

- `backend/get_data/*` -> 保持不变，但通过 `backend/adapters/*` 以 `DataProvider` 接口接入。
- `backend/backEngine/*` -> 使用 `backend/engines/backtrader_engine.py` 代替。
- `backend/main.py` -> 新入口示例 `backend/main_v2.py`（旧文件保留）。

### 新增数据源

实现 `DataProvider` 子类，例如：

```python
from core.base import DataProvider
class MyProvider(DataProvider):
    def fetch(self, symbol, start_date, end_date):
        ... # 返回标准化 OHLCV DataFrame
```

### 新增策略

继续使用 Backtrader 策略（`bt.Strategy`），或实现统一 `Strategy` 协议后接入自研引擎。


