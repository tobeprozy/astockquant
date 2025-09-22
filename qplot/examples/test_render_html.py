#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 render_html 方法的示例程序
此示例展示如何使用更新后的 render_html 方法创建完整的K线+MA5+MACD+成交量图表
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from qplot.backends.pyecharts.chart_2 import PyechartsChart_2


def generate_sample_stock_data(days=120):
    """
    生成示例股票数据，包含K线、成交量、MA5、MACD等指标
    
    参数:
        days: 生成的交易日数量
    
    返回:
        DataFrame: 包含股票数据的DataFrame
    """
    # 生成日期序列
    dates = pd.date_range(start='2023-01-01', periods=days, freq='B')
    
    # 初始化价格列表
    np.random.seed(42)  # 设置随机种子以确保结果可重现
    close_prices = [100.0]  # 起始价格
    open_prices = [100.0]
    high_prices = [100.0]
    low_prices = [100.0]
    volumes = [10000]
    
    # 生成随机价格数据
    for i in range(1, days):
        # 基于前一天的收盘价生成当天的价格变化
        change = np.random.normal(0, 2)
        if i > 0:
            open_price = close_prices[i-1] + np.random.uniform(-1, 1)
        else:
            open_price = 100.0
        
        # 确保价格合理
        close_price = max(open_price + change, 1)
        high_price = max(open_price, close_price) + np.random.uniform(0, 1)
        low_price = min(open_price, close_price) - np.random.uniform(0, 1)
        volume = int(np.random.uniform(5000, 20000))
        
        open_prices.append(open_price)
        close_prices.append(close_price)
        high_prices.append(high_price)
        low_prices.append(low_price)
        volumes.append(volume)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'close': close_prices,
        'high': high_prices,
        'low': low_prices,
        'vol': volumes
    })
    
    # 计算MA5
    df['MA5'] = df['close'].rolling(window=5).mean()
    
    # 计算MACD相关指标
    close_array = df['close'].values
    
    # 计算短期EMA
    short_ema = np.zeros_like(close_array)
    short_ema[0] = close_array[0]
    multiplier = 2 / (12 + 1)
    for i in range(1, len(close_array)):
        short_ema[i] = close_array[i] * multiplier + short_ema[i-1] * (1 - multiplier)
    
    # 计算长期EMA
    long_ema = np.zeros_like(close_array)
    long_ema[0] = close_array[0]
    multiplier = 2 / (26 + 1)
    for i in range(1, len(close_array)):
        long_ema[i] = close_array[i] * multiplier + long_ema[i-1] * (1 - multiplier)
    
    # 计算DIF
    dif = short_ema - long_ema
    
    # 计算DEA
    dea = np.zeros_like(dif)
    dea[0] = dif[0]
    multiplier = 2 / (9 + 1)
    for i in range(1, len(dif)):
        dea[i] = dif[i] * multiplier + dea[i-1] * (1 - multiplier)
    
    # 计算MACD柱
    macd = (dif - dea) * 2
    
    # 添加到DataFrame
    df['DIF'] = dif
    df['DEA'] = dea
    df['MACD'] = macd
    
    # 添加CDLMORNINGSTAR信号（随机生成一些信号点）
    df['CDLMORNINGSTAR'] = 0
    signal_indices = np.random.choice(range(10, days-10), 5, replace=False)  # 随机选择5个位置作为信号点
    for idx in signal_indices:
        df.loc[idx, 'CDLMORNINGSTAR'] = 100  # 100表示强烈的买入信号
    
    return df


def main():
    """
    主函数：测试更新后的 render_html 方法
    """
    # 创建output目录（如果不存在）
    output_dir = os.path.join(os.getcwd(), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建目录: {output_dir}")
    
    # 生成示例数据
    df = generate_sample_stock_data(days=120)  # 生成120天的示例数据
    
    print("=== 测试更新后的 render_html 方法 ===")
    try:
        # 创建PyechartsChart_2实例
        chart = PyechartsChart_2(chart_type='kline', data=df)
        
        # 定义输出文件路径
        html_path = os.path.join(output_dir, 'example_render_html.html')
        
        # 使用render_html方法绘制完整的图表
        # 这个方法会自动调用plot_kline_1, plot_ma5, plot_macd_1, plot_dif_dea, plot_vol等方法
        
        # 方法1: 使用render_html的output_path参数直接指定输出路径
        chart.render_html(output_path=html_path)
        
        # 方法2: 先调用render_html，再调用save方法（与之前兼容的方式）
        # chart.render_html()
        # chart.save(html_path)
        
        if os.path.exists(html_path):
            print(f"成功保存图表到: {html_path}")
        else:
            print(f"保存图表失败")
        
        # 在浏览器中显示图表（可选）
        # chart.show(inline=False)
        
        print("\n图表说明:")
        print("- 顶部区域: K线图 + MA5均线")
        print("- 中间区域: 成交量柱状图")
        print("- 底部区域: MACD指标图")
        print("- 图表布局已优化，确保各区域不重叠")
        
    except Exception as e:
        print(f"创建图表时出错: {str(e)}")


if __name__ == '__main__':
    main()