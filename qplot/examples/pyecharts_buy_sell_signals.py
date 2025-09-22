#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试K线图上添加买点和卖点标记功能

本示例将随机生成一组股票数据，然后添加几个随机的买点和卖点标记，最后绘制并保存图表。
"""

import sys
import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qplot.backends.pyecharts.chart_1 import PyechartsChart_1

# 设置中文字体支持
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


def generate_random_stock_data(start_date, days=100):
    """
    生成随机股票数据
    
    Args:
        start_date: 开始日期
        days: 数据天数
        
    Returns:
        pandas.DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量的DataFrame
    """
    # 生成日期序列
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # 随机生成收盘价数据（使用随机游走模型）
    np.random.seed(42)  # 设置随机种子，保证结果可重复
    base_price = 100
    returns = np.random.normal(0, 1, days) / 100  # 日收益率
    close_prices = base_price * np.exp(np.cumsum(returns))
    
    # 根据收盘价生成开盘价、最高价、最低价
    open_prices = close_prices[:-1] * (1 + np.random.uniform(-0.02, 0.02, days-1))
    open_prices = np.insert(open_prices, 0, close_prices[0] * (1 + np.random.uniform(-0.02, 0.02)))
    
    high_prices = np.maximum(open_prices, close_prices) * (1 + np.random.uniform(0, 0.03, days))
    low_prices = np.minimum(open_prices, close_prices) * (1 - np.random.uniform(0, 0.03, days))
    
    # 生成成交量数据
    volumes = np.random.randint(100000, 10000000, days)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    return df

def calculate_ma(df, periods=[5, 10]):
    """
    计算均线数据
    
    Args:
        df: 包含收盘价的DataFrame
        periods: 均线周期列表
        
    Returns:
        dict: 均线数据字典
    """
    ma_data = {}
    for period in periods:
        ma_data[f'MA{period}'] = df['close'].rolling(window=period).mean().tolist()
    return ma_data

def generate_random_signals(df, num_buy=3, num_sell=3):
    """
    生成随机的买点和卖点
    
    Args:
        df: 股票数据DataFrame
        num_buy: 买点数量
        num_sell: 卖点数量
        
    Returns:
        dict: 包含买点和卖点的字典
    """
    # 选择随机日期作为信号点
    all_dates = [str(date.date()) for date in df.index]
    
    # 随机选择买点日期
    buy_dates_indices = sorted(random.sample(range(10, len(all_dates)-10), num_buy))
    buy_dates = [all_dates[i] for i in buy_dates_indices]
    buy_prices = [df.iloc[i]['low'] * (1 - 0.01) for i in buy_dates_indices]  # 买点稍微低于当日最低价
    
    # 随机选择卖点日期
    # 确保卖点日期与买点日期不完全重叠
    available_indices = [i for i in range(10, len(all_dates)-10) if i not in buy_dates_indices]
    if len(available_indices) < num_sell:
        # 如果可用日期不够，就使用任意日期
        sell_dates_indices = sorted(random.sample(range(len(all_dates)), num_sell))
    else:
        sell_dates_indices = sorted(random.sample(available_indices, num_sell))
    
    sell_dates = [all_dates[i] for i in sell_dates_indices]
    sell_prices = [df.iloc[i]['high'] * (1 + 0.01) for i in sell_dates_indices]  # 卖点稍微高于当日最高价
    
    # 创建信号点字典
    signals = {
        'buy': list(zip(buy_dates, buy_prices)),
        'sell': list(zip(sell_dates, sell_prices))
    }
    
    return signals

def main():
    """主函数"""
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成随机股票数据
    start_date = datetime(2023, 1, 1)
    df = generate_random_stock_data(start_date, days=100)
    
    # 计算均线数据
    ma_data = calculate_ma(df, periods=[5, 10])
    
    # 生成随机买点和卖点
    signal_points = generate_random_signals(df, num_buy=4, num_sell=3)
    
    print("生成的买点：")
    for date, price in signal_points['buy']:
        print(f"  日期: {date}, 价格: {price:.2f}")
    
    print("生成的卖点：")
    for date, price in signal_points['sell']:
        print(f"  日期: {date}, 价格: {price:.2f}")
    
    # 创建K线图对象
    chart = PyechartsChart_1(
        chart_type='kline', 
        data=df,
        title='随机生成的股票K线图（带买卖点标记）'
    )
    
    # 使用自定义的draw_klines方法添加均线和买卖点标记
    # 注意：这里我们需要直接调用draw_klines方法而不是plot方法，因为plot方法不支持传递signal_points参数
    chart.chart = chart.draw_klines(df, ma_data=ma_data, signal_points=signal_points)
    
    # 保存为HTML文件
    html_file = os.path.join(output_dir, 'kline_with_signals.html')
    chart.save(html_file)
    print(f"图表已保存为HTML：{html_file}")
    
    # 保存为图片文件
    # 注意：保存图片需要安装snapshot-selenium和selenium，并配置浏览器驱动
    # try:
    #     image_file = os.path.join(output_dir, 'kline_with_signals.png')
    #     chart.save(image_file, type='image')
    #     print(f"图表已保存为图片：{image_file}")
    # except Exception as e:
    #     print(f"保存图片失败：{str(e)}")
    #     print("请确保已安装snapshot-selenium和selenium，并配置了正确的浏览器驱动")
    #     print("安装命令：pip install snapshot-selenium selenium")
    #     print("Chrome驱动下载地址：https://chromedriver.chromium.org/downloads")


if __name__ == '__main__':
    main()