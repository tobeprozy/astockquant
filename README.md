# AstockQuant

量化研究与回测仓库。此仓库正在进行结构优化，以提升解耦性与可扩展性（数据源/策略/引擎易于增量添加与替换）。

## 环境准备

```bash
conda create -n astockquant  -y python=3.10
conda activate astockquant
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple akshare pyfolio backtrader pyecharts TA-Lib
```

## 新的目录约定（逐步迁移中）

- `backend/core/`: 抽象基类与通用类型（DataProvider、Strategy、BacktestEngine）
- `backend/adapters/`: 适配层，将现有实现（如 Akshare 抓取器）包装为统一接口
- `backend/engines/`: 回测引擎实现（现支持 Backtrader 引擎）
- `backend/strategies/`: 策略实现（保留 Backtrader 策略）
- `backend/get_data/`: 旧的数据抓取cona实现，逐步迁移至 adapters

## 快速上手（新接口）

```python
from backend.adapters.akshare_provider import AkshareFundProvider
from backend.engines.backtrader_engine import BacktraderEngine
from backend.strategies.strategy import Strategy_MACD3

engine = BacktraderEngine(
    data_provider=AkshareFundProvider(),
    symbol='512200',
    start_date='20220101',
    end_date='20240101',
    strategy_cls=Strategy_MACD3,
)
results = engine.run()
engine.plot()
```

## 文档

- `docs/architecture.md`: 高层架构与模块职责
- `docs/user_guide.md`: 使用指南
- `docs/deployment.md`: 部署方案（本地 / Docker / Compose）

## FAQ

### Ta-lib 安装失败

获取源码并编译安装：

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -zxvf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make && sudo make install
pip install TA-Lib
```

