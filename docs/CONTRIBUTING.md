## Contributing

### 代码结构

- 新增数据源：在 `backend/adapters/` 内实现 `DataProvider` 子类。
- 新增回测引擎：在 `backend/engines/` 内实现 `BacktestEngine` 子类。
- 策略：维持 `backend/strategies/`，或提供统一 `Strategy` 协议实现。

### 规范

- 遵守类型注解与清晰命名。
- 避免跨层直接耦合（策略不直接依赖具体数据抓取实现）。


