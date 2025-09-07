## 使用指南

### 环境准备

```bash
conda create -n astockquant -c conda-forge -y python=3.10
conda activate astockquant
pip install -r backend/requirements.txt
```

### 快速开始（新架构）

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
engine.run()
engine.plot()
```

### 邮件通知

配置环境变量（示例）：

```bash
set SMTP_HOST=smtp.example.com
set SMTP_PORT=587
set SMTP_USER=your_user@example.com
set SMTP_PASS=your_password
set SMTP_FROM=your_user@example.com
set SMTP_TO=notify_to@example.com
```

回测结束发信：

```python
from backend.utils.emailer import SmtpEmailer
engine = BacktraderEngine(
    data_provider=AkshareFundProvider(),
    symbol='512200',
    start_date='20220101',
    end_date='20240101',
    strategy_cls=Strategy_MACD3,
    email_on_finish=True,
    emailer=SmtpEmailer(),
)
```

买卖信号发信（策略）：

```python
from backend.utils.emailer import SmtpEmailer
email = SmtpEmailer()
strat = Strategy_MACD3
engine = BacktraderEngine(...)
# 在 Backtrader 中可通过策略参数或在策略实例化钩子中注入 emailer（此仓库提供 set_emailer 接口）。
```

### 目录说明（精简）

- `backend/core/` 抽象接口
- `backend/adapters/` 数据源适配
- `backend/engines/` 回测引擎
- `backend/examples/` 示例
- `backend/utils/` 指标与可视化


