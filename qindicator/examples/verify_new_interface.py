#!/usr/bin/env python
"""
验证qindicator库的新接口是否正常工作
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试导入新接口
try:
    from qindicator import TalibIndicatorCalculator
    from qindicator import get_indicator_calculator
    print("✅ 成功导入新接口")
except Exception as e:
    print(f"❌ 导入新接口失败: {e}")
    sys.exit(1)

# 测试创建指标计算器实例
try:
    # 使用工厂函数
    calc1 = get_indicator_calculator('talib')
    print("✅ 成功使用工厂函数创建指标计算器实例")
    
    # 直接使用类
    calc2 = TalibIndicatorCalculator()
    print("✅ 成功直接使用类创建指标计算器实例")
except Exception as e:
    print(f"❌ 创建指标计算器实例失败: {e}")
    sys.exit(1)

# 测试指标计算功能
try:
    # 生成测试数据
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.normal(0, 1, 30))
    
    data = {
        'open': prices * (1 + np.random.normal(0, 0.01, 30)),
        'high': prices * (1 + np.random.normal(0, 0.02, 30)),
        'low': prices * (1 - np.random.normal(0, 0.02, 30)),
        'close': prices,
        'volume': np.random.randint(1000, 100000, 30)
    }
    
    df = pd.DataFrame(data, index=dates)
    
    # 测试计算MA指标
    ma_result = calc1.calculate_ma(df, timeperiod=5)
    print(f"✅ 成功计算MA指标，结果形状: {ma_result.shape}")
    
    # 测试计算RSI指标
    rsi_result = calc1.calculate_rsi(df, timeperiod=14)
    print(f"✅ 成功计算RSI指标，结果形状: {rsi_result.shape}")
    
    # 测试计算MACD指标
    macd_result = calc2.calculate_macd(df)
    print(f"✅ 成功计算MACD指标，结果形状: {macd_result.shape}")
    
    # 测试计算布林带指标
    bbands_result = calc2.calculate_bbands(df, timeperiod=20)
    print(f"✅ 成功计算布林带指标，结果形状: {bbands_result.shape}")
    
    # 验证指标计算结果
    if ('MA5' in ma_result.columns and 
        'RSI' in rsi_result.columns and 
        'MACD' in macd_result.columns and 
        'BB_UPPER' in bbands_result.columns):
        print("✅ 所有指标计算结果验证通过")
    else:
        print("❌ 指标计算结果验证失败")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ 指标计算功能测试失败: {e}")
    sys.exit(1)

print("\n===== 新接口验证测试全部通过! =====")