## Architecture

目标：实现数据源、策略、回测引擎三者解耦，具备可插拔能力。

### 分层

- Core（`backend/core`）: 抽象接口与通用类型。
  - `DataProvider.fetch(symbol, start_date, end_date)` 返回标准化 OHLCV。
  - `BacktestEngine.run()` 执行回测并返回结果。
  - `Strategy` 协议：面向通用引擎的事件接口（保留 Backtrader 策略作为具体实现）。

- Adapters（`backend/adapters`）: 将现有数据抓取封装为 `DataProvider`。

- Engines（`backend/engines`）: 各类回测引擎实现，目前提供 Backtrader 引擎封装。

- Strategies（`backend/strategies`）: 具体策略实现，沿用 Backtrader 风格。

### 数据流

`DataProvider` -> 标准化 DataFrame -> `Engine` -> 调用具体策略并产出结果。

### 迁移策略

不破坏现有示例，新增代码优先走 `core/adapters/engines` 路线；旧目录逐步淡出。

