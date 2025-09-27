#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
qindicator使用示例
简洁展示如何使用重构后的qindicator库计算各种股票指标
"""

import pandas as pd
import numpy as np
from qindicator import get_indicator_calculator
from qindicator import TalibIndicator

def main():
    # 使用方式1: 通过工厂函数获取指标计算器实例
    talib_calculator = get_indicator_calculator('talib')
    print("✅ 成功通过工厂函数获取talib指标计算器实例")
    
    # 使用方式2: 直接使用TalibIndicator类创建实例
    direct_calculator = TalibIndicator()
    print("✅ 成功直接使用TalibIndicator类创建指标计算器实例")

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

    # 使用直接创建的TalibIndicator实例计算指标
    print("\n=== 使用直接创建的TalibIndicator实例计算指标 ===")
    try:
        # 计算10日均线
        ma10_data = direct_calculator.calculate(df, 'ma', timeperiod=10)
        print("直接创建实例计算的10日均线数据:")
        # 修复：将MA改为MA10，因为计算的是10日均线
        print(ma10_data['MA10'].tail())
        
        # 将不支持的KDJ指标替换为支持的RSI指标
        rsi_data = direct_calculator.calculate(df, 'rsi', timeperiod=14)
        print("直接创建实例计算的RSI数据:")
        print(rsi_data['RSI'].tail())
        
        # 修复：将这部分代码移到try块内部，确保ma10_data已定义
        print("使用直接实例计算10日均线结果:")
        print(ma10_data[['close', 'MA10']].tail(5))
        print("\n")
    except Exception as e:
        print(f"直接创建实例计算指标时出错: {e}")
    
    
    print("qindicator使用示例完成!")

if __name__ == '__main__':
    main()