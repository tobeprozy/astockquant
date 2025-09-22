#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qplot 插件 - chart_1.py 示例

此示例展示如何使用 chart_1.py 插件直接获取数据、绘图并保存为图片
"""

import pandas as pd
import numpy as np
import os
from qplot.backends.pyecharts.chart_1 import PyechartsChart_1


def generate_sample_data(days=60):
    """生成示例K线数据"""
    # 生成随机日期
    dates = pd.date_range(start='2023-01-01', periods=days, freq='B')
    
    # 生成随机价格数据
    np.random.seed(42)  # 设置随机种子以确保结果可重现
    base_price = 100
    price_changes = np.random.normal(0, 2, days)
    close_prices = base_price + np.cumsum(price_changes)
    
    # 生成开盘价、最高价和最低价
    open_prices = close_prices[:-1] * (1 + np.random.normal(0, 0.01, days-1))
    # 为第一天添加一个随机开盘价
    open_prices = np.insert(open_prices, 0, close_prices[0] * (1 + np.random.normal(0, 0.01)))
    
    # 最高价和最低价
    high_prices = np.maximum(open_prices, close_prices) * (1 + np.random.uniform(0, 0.02, days))
    low_prices = np.minimum(open_prices, close_prices) * (1 - np.random.uniform(0, 0.02, days))
    
    # 生成成交量数据
    volumes = np.random.randint(100000, 1000000, days)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    return df


def calculate_ma(df, periods=[5, 10, 20]):
    """计算均线数据"""
    ma_data = {}
    for period in periods:
        ma_column = f'MA{period}'
        df[ma_column] = df['close'].rolling(window=period).mean()
        ma_data[ma_column] = df[ma_column].tolist()
    return ma_data


def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """计算MACD指标"""
    # 计算快线和慢线
    df['EMA12'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    # 计算DIF
    df['DIF'] = df['EMA12'] - df['EMA26']
    
    # 计算DEA
    df['DEA'] = df['DIF'].ewm(span=signal_period, adjust=False).mean()
    
    # 计算MACD柱状图
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    
    # 转换为日期和数据列表
    dates = [str(idx.date()) for idx in df.index]
    dif = df['DIF'].tolist()
    dea = df['DEA'].tolist()
    macd = df['MACD'].tolist()
    
    return dates, dif, dea, macd


def main():
    """主函数：获取数据、绘图并保存"""
    # 创建output目录（如果不存在）
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建目录: {output_dir}")
    
    print("开始生成示例数据...")
    
    # 1. 生成示例数据
    df = generate_sample_data(days=100)
    print(f"生成了{len(df)}条K线数据")
    
    # 2. 计算技术指标
    ma_data = calculate_ma(df)
    dates, dif, dea, macd = calculate_macd(df)
    
    # 3. 创建PyechartsChart_1实例
    chart = PyechartsChart_1(chart_type='kline', data=df)
    
        # 4. 绘制单一K线图并保存为HTML
    chart.draw_klines(df, ma_data=ma_data)
    chart.save(os.path.join(output_dir, 'kline_chart.html'))
    print(f"K线图已保存为 {os.path.join(output_dir, 'kline_chart.html')}")
    
    # 5. 绘制组合图表（K线+成交量）并保存为图片
    grid_chart = chart.draw_kline_volume_signal(df, ma_data=ma_data)
    if grid_chart:
        chart.chart = grid_chart
        chart.save(os.path.join(output_dir, 'kline_volume_chart.png'))
        print(f"K线+成交量图已保存为 {os.path.join(output_dir, 'kline_volume_chart.png')}")
    
    # 6. 使用drawAll方法自定义组合图表（K线+MACD）
    # 创建K线图
    kline_obj = chart.draw_klines(df, ma_data=ma_data)
    # 创建MACD图
    macd_obj = chart.draw_macd(dates, dif, dea, macd)
    # 组合图表
    custom_grid = chart.drawAll([
        (kline_obj, {"pos_left": "10%", "pos_right": "10%", "height": "40%", "pos_top": "10%"}),
        (macd_obj, {"pos_left": "10%", "pos_right": "10%", "pos_top": "60%", "height": "20%"})
    ])
    # 保存为图片
    chart.chart = custom_grid
    chart.save(os.path.join(output_dir, 'kline_macd_chart.png'))
    print(f"K线+MACD图已保存为 {os.path.join(output_dir, 'kline_macd_chart.png')}")
    
    print("\n提示：\n")
    print("如需保存图片功能，请确保已安装必要依赖:")
    print("   pip install snapshot-selenium selenium")
    print("并安装对应的浏览器驱动")


if __name__ == "__main__":
    main()