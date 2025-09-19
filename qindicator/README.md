# qindicator

AstockQuant指标计算插件，提供统一的股票技术指标计算接口。

## 功能特性

- 统一的技术指标计算接口
- 支持多种指标计算库（默认支持TA-Lib）
- 可扩展的插件架构
- 支持常用技术指标：MA、EMA、RSI、MACD、布林带等

## 安装

```bash
cd qindicator
pip install -e .
```

## 使用示例

```python
import pandas as pd
import qindicator

# 初始化qindicator（自动使用ta-lib作为默认指标计算库）
qindicator.init()

# 准备数据（DataFrame需要包含'open', 'high', 'low', 'close', 'volume'列）
# 这里假设您已经有了股票数据data

data = pd.DataFrame({
    'open': [100, 102, 101, 103, 104],
    'high': [105, 104, 106, 107, 108],
    'low': [98, 100, 100, 102, 103],
    'close': [103, 101, 105, 106, 107],
    'volume': [10000, 12000, 15000, 13000, 14000]
})

# 计算MA5
ma_data = qindicator.calculate_ma(data, timeperiod=5)
print(ma_data)

# 计算MACD
macd_data = qindicator.calculate_macd(data)
print(macd_data)

# 计算RSI
rsi_data = qindicator.calculate_rsi(data)
print(rsi_data)

# 计算布林带
bbands_data = qindicator.calculate_bbands(data)
print(bbands_data)
```

## 插件架构

qindicator采用工厂模式和适配器模式，支持轻松扩展新的指标计算库：

1. 创建新的指标计算器类，继承自`IndicatorCalculator`抽象基类
2. 实现所有抽象方法
3. 使用`IndicatorCalculatorFactory.register()`注册新的指标计算器

## 支持的指标

- 移动平均线（MA）
- 指数移动平均线（EMA）
- 相对强弱指数（RSI）
- 平滑异同移动平均线（MACD）
- 布林带（Bollinger Bands）

## 开发计划

- 支持更多技术指标
- 增加更多指标计算库的支持
- 提供更丰富的参数配置