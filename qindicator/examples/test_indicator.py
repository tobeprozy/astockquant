#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
qindicator使用示例
简洁展示如何使用重构后的qindicator库计算各种股票指标
"""

import pandas as pd
import numpy as np
from qindicator import get_indicator_calculator
from qindicator import TalibIndicatorCalculator

def main():
    # 使用方式1: 通过工厂函数获取指标计算器实例
    talib_calculator = get_indicator_calculator('talib')
    print("✅ 成功通过工厂函数获取talib指标计算器实例")
    
    # 使用方式2: 直接使用TalibIndicatorCalculator类创建实例
    # talib_calculator = TalibIndicatorCalculator()
    # print("✅ 成功直接使用类创建指标计算器实例")

    # 生成示例股票数据
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

    # 计算5日均线
    ma_data = talib_calculator.calculate_ma(df, timeperiod=5)
    print("计算5日均线结果:")
    print(ma_data[['close', 'MA5']].tail(5))
    print("\n")

    # 计算RSI指标
    rsi_data = talib_calculator.calculate_rsi(df)
    print("计算RSI结果:")
    print(rsi_data[['close', 'RSI']].tail(5))
    print("\n")

    # 计算MACD指标
    macd_data = talib_calculator.calculate_macd(df)
    print("计算MACD结果:")
    print(macd_data[['close', 'MACD', 'MACD_SIGNAL', 'MACD_HIST']].tail(5))
    print("\n")

    # 计算布林带指标
    bbands_data = talib_calculator.calculate_bbands(df, timeperiod=20)
    print("计算布林带结果:")
    print(bbands_data[['close', 'BB_UPPER', 'BB_MIDDLE', 'BB_LOWER']].tail(5))
    print("\n")

    # 使用统一接口计算指标
    atr_data = talib_calculator.calculate(df, 'atr')
    print("使用统一接口计算ATR指标结果:")
    print(atr_data[['close', 'ATR']].tail(5))
    print("\n")

    print("qindicator使用示例完成!")

if __name__ == '__main__':
    main()