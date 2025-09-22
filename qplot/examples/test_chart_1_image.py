#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 PyechartsChart_1 的图片保存功能
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qplot.backends.pyecharts.chart_1 import PyechartsChart_1
import pandas as pd
import numpy as np

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

def main():
    """主函数：测试图片保存功能"""
    # 创建output目录（如果不存在）
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建目录: {output_dir}")
    
    # 生成示例数据
    df = generate_sample_data(days=50)
    ma_data = calculate_ma(df)
    
    # 创建PyechartsChart_1实例
    chart = PyechartsChart_1(chart_type='kline', data=df)
    
    print("\n=== 测试 K线图保存为图片 ===")
    # 绘制K线图
    chart.draw_klines(df, ma_data=ma_data)
    # 保存为图片
    img_path = os.path.join(output_dir, 'test_kline_image.png')
    result = chart.save(img_path)
    if result:
        print(f"成功保存K线图图片到: {img_path}")
    else:
        print(f"保存K线图图片失败")
    
    print("\n=== 测试 K线+成交量图保存为图片 ===")
    # 绘制K线+成交量图
    grid_chart = chart.draw_kline_volume_signal(df, ma_data=ma_data)
    if grid_chart:
        chart.chart = grid_chart
        # 保存为图片
        img_path = os.path.join(output_dir, 'test_kline_volume_image.png')
        result = chart.save(img_path)
        if result:
            print(f"成功保存K线+成交量图图片到: {img_path}")
        else:
            print(f"保存K线+成交量图图片失败")
    
    print("\n\n提示：\n")
    print("如需使用图片保存功能，请确保已安装必要依赖:")
    print("   pip install snapshot-selenium selenium")
    print("并安装对应的浏览器驱动")
    print("\n如果保存图片失败，程序会自动回退到保存HTML文件")

if __name__ == "__main__":
    main()