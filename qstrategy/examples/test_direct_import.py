#!/usr/bin/env python
"""
测试直接导入策略类的功能
展示用户如何直接从qstrategy包导入和使用策略类
"""

# 测试方法1: 直接导入策略类
print("===== 测试直接导入策略类 =====")
try:
    from qstrategy import BBandsStrategy, MACDStrategy, RSIStrategy
    from qstrategy import MACDKDJStrategy, MeanReversionStrategy
    from qstrategy import VolatilityBreakoutStrategy, PairTradingStrategy
    
    print("✅ 成功导入所有策略类")
    print(f"布林带策略类: {BBandsStrategy}")
    print(f"MACD策略类: {MACDStrategy}")
    print(f"RSI策略类: {RSIStrategy}")
except Exception as e:
    print(f"❌ 直接导入策略类失败: {e}")

# 测试方法2: 通过包访问策略类
print("\n===== 测试通过包访问策略类 =====")
try:
    import qstrategy
    
    # 创建策略实例
    bbands_strategy = qstrategy.BBandsStrategy(period=20, devfactor=2.0)
    macd_strategy = qstrategy.MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    
    print("✅ 成功通过包访问策略类")
    print(f"创建的布林带策略实例: {bbands_strategy}")
    print(f"创建的MACD策略实例: {macd_strategy}")
except Exception as e:
    print(f"❌ 通过包访问策略类失败: {e}")

# 测试方法3: 使用策略类的方法
print("\n===== 测试使用策略类的方法 =====")
try:
    # 创建样本数据进行简单测试
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # 生成简单的测试数据
    dates = [datetime.now() - timedelta(days=i) for i in range(100-1, -1, -1)]
    data = pd.DataFrame({
        'date': dates,
        'open': [100 + i*0.5 for i in range(100)],
        'high': [101 + i*0.5 + i%5 for i in range(100)],
        'low': [99 + i*0.5 - i%3 for i in range(100)],
        'close': [100 + i*0.5 + (i%2 - 0.5)*2 for i in range(100)],
        'volume': [10000 + i*1000 for i in range(100)]
    })
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    
    # 使用策略类
    strategy = qstrategy.BBandsStrategy(period=20, devfactor=2.0)
    strategy.init_strategy(data)
    
    print("✅ 成功初始化策略并处理数据")
    print(f"策略参数: 周期={strategy.params['period']}, 标准差倍数={strategy.params['devfactor']}")
except Exception as e:
    print(f"❌ 使用策略类的方法失败: {e}")

print("\n===== 测试完成 =====")