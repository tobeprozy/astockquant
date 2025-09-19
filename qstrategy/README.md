# qstrategy

AstockQuant策略插件系统，提供统一的策略管理和执行接口。

## 功能特点

- 统一的策略接口设计
- 基于工厂模式的策略管理
- 支持多种回测框架（默认backtrader）
- 易于扩展的插件架构
- 丰富的内置策略实现

## 安装

```bash
cd /Users/zzy/workspace/AstockQuant/qstrategy
pip install -e .
```

## 使用示例

```python
import qstrategy
import pandas as pd

# 初始化qstrategy
qstrategy.init()

# 获取数据
# ... 假设这里获取了股票数据df ...

# 创建回测引擎
cerebro = qstrategy.create_backtrader_engine()

# 添加数据
cerebro.adddata(df)

# 添加策略
cerebro.addstrategy('sma_cross')

# 运行回测
result = cerebro.run()

# 查看结果
cerebro.plot()
```

## 支持的策略

- SMA Cross Strategy（均线交叉策略）
- MACD Strategy（MACD指标策略）
- RSI Strategy（RSI指标策略）
- Turtle Strategy（海龟交易策略）
- Pair Trading Strategy（配对交易策略）

## 扩展指南

要添加自定义策略，请继承`qstrategy.StrategyBase`基类并实现必要的方法，然后通过`qstrategy.register_strategy`方法注册您的策略。