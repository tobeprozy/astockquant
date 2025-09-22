#!/usr/bin/env python
"""
测试直接导入指标计算器类的功能
展示用户如何直接从qindicator包导入和使用指标计算器类
"""

import sys
import os

# 直接导入指标计算器类
try:
    from qindicator import TalibIndicatorCalculator
    from qindicator import get_indicator_calculator
    print("✅ 成功直接导入指标计算器类和工厂函数")
except Exception as e:
    print(f"❌ 直接导入指标计算器类失败: {e}")

# 测试方法1: 使用工厂函数获取指标计算器
def test_get_indicator_calculator():
    """测试使用get_indicator_calculator函数获取指标计算器实例"""
    print("===== 测试使用get_indicator_calculator获取指标计算器实例 =====")
    try:
        import qindicator
        
        # 测试获取talib指标计算器
        talib_calculator = qindicator.get_indicator_calculator('talib')
        print("✅ 成功获取talib指标计算器实例")
        
        # 显示可用的计算器类型
        print("\n可用的指标计算器: talib")
        
    except Exception as e:
        print(f"❌ 获取指标计算器实例失败: {e}")

# 测试方法2: 使用指标计算器实例的方法
def test_indicator_methods():
    """测试指标计算器实例的主要方法"""
    print("\n===== 测试指标计算器实例的主要方法 =====")
    try:
        import qindicator
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # 生成简单的测试数据
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)  # 设置随机种子，保证结果可复现
        prices = 100 + np.cumsum(np.random.normal(0, 2, 100))

        data = {
            'open': prices * (1 + np.random.normal(0, 0.01, 100)),
            'high': prices * (1 + np.random.normal(0, 0.02, 100)),
            'low': prices * (1 - np.random.normal(0, 0.02, 100)),
            'close': prices,
            'volume': np.random.randint(1000, 100000, 100)
        }
        df = pd.DataFrame(data, index=dates)
        
        # 显示示例数据的前5行
        print("示例数据的前5行:")
        print(df.head())
        print("\n")
        
        # 创建并使用指标计算器
        talib_calculator = qindicator.get_indicator_calculator('talib')
        
        # 测试计算MA指标
        ma_data = talib_calculator.calculate_ma(df, timeperiod=5)
        print("✅ 成功计算5日均线")
        print(ma_data[['close', 'MA5']].tail(5))
        print("\n")
        
        # 测试计算RSI指标
        rsi_data = talib_calculator.calculate_rsi(df, timeperiod=14)
        print("✅ 成功计算RSI指标")
        print(rsi_data[['close', 'RSI']].tail(5))
        print("\n")
        
        # 测试计算MACD指标
        macd_data = talib_calculator.calculate_macd(df, fastperiod=12, slowperiod=26, signalperiod=9)
        print("✅ 成功计算MACD指标")
        print(macd_data[['close', 'MACD', 'MACD_SIGNAL', 'MACD_HIST']].tail(5))
        print("\n")
        
        # 测试计算布林带指标
        bbands_data = talib_calculator.calculate_bbands(df, timeperiod=20, nbdevup=2, nbdevdn=2)
        print("✅ 成功计算布林带指标")
        print(bbands_data[['close', 'BB_UPPER', 'BB_MIDDLE', 'BB_LOWER']].tail(5))
        print("\n")
        
    except Exception as e:
        print(f"❌ 测试指标方法失败: {e}")

# 测试方法3: 直接使用导入的指标计算器类
def test_direct_import_indicator():
    """测试直接使用导入的指标计算器类"""
    print("\n===== 测试直接使用导入的指标计算器类 =====")
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # 生成简单的测试数据
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)  # 设置随机种子，保证结果可复现
        prices = 100 + np.cumsum(np.random.normal(0, 2, 100))

        data = {
            'open': prices * (1 + np.random.normal(0, 0.01, 100)),
            'high': prices * (1 + np.random.normal(0, 0.02, 100)),
            'low': prices * (1 - np.random.normal(0, 0.02, 100)),
            'close': prices,
            'volume': np.random.randint(1000, 100000, 100)
        }
        df = pd.DataFrame(data, index=dates)
        
        # 测试直接使用TalibIndicatorCalculator类
        try:
            talib_calc = TalibIndicatorCalculator()
            ma_data = talib_calc.calculate_ma(df, timeperiod=5)
            rsi_data = talib_calc.calculate_rsi(df, timeperiod=14)
            print(f"✅ 成功使用TalibIndicatorCalculator类: 计算了MA5和RSI14指标")
        except Exception as e:
            print(f"❌ 使用TalibIndicatorCalculator类失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试直接导入指标计算器类失败: {e}")

# 运行所有测试
if __name__ == "__main__":
    test_get_indicator_calculator()
    test_indicator_methods()
    test_direct_import_indicator()

print("\n===== 测试完成 =====")