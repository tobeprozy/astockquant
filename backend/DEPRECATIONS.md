## Deprecations

- `backEngine/`: superseded by `engines/backtrader_engine.py`. Existing code is kept for compatibility.
- Direct usage of `get_data/*` in engines: prefer `adapters/*` via `DataProvider`.


