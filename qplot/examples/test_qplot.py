#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试重构后的qplot库功能"""

import pandas as pd
import numpy as np
import qplot
from qplot import DataManager


def generate_test_kline_data():
    """生成测试用的K线数据"""
    # 创建一个简单的交易日序列
    dates = pd.date_range('2023-01-01', periods=50, freq='B')
    
    # 随机生成开盘价、收盘价、最高价、最低价
    np.random.seed(42)  # 固定随机数种子，确保结果可重现
    base_price = 100.0
    open_prices = base_price + np.random.randn(50).cumsum()
    close_prices = open_prices + np.random.randn(50) * 2
    high_prices = np.maximum(open_prices, close_prices) + np.random.rand(50) * 3
    low_prices = np.minimum(open_prices, close_prices) - np.random.rand(50) * 3
    volumes = np.random.randint(10000, 100000, 50)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': open_prices,
        'close': close_prices,
        'high': high_prices,
        'low': low_prices,
        'volume': volumes
    }, index=dates)
    
    return data


def generate_test_minute_data():
    """生成测试用的分时图数据"""
    # 创建一个交易日内的分钟序列
    start_date = '2023-01-01 09:30:00'
    end_date = '2023-01-01 15:00:00'
    dates = pd.date_range(start_date, end_date, freq='min')
    
    # 随机生成价格和成交量
    np.random.seed(42)
    base_price = 100.0
    prices = base_price + np.random.randn(len(dates)).cumsum() / 5
    volumes = np.random.randint(1000, 10000, len(dates))
    
    # 计算均价
    avg_prices = []
    cumulative_price_volume = 0
    cumulative_volume = 0
    
    for price, volume in zip(prices, volumes):
        cumulative_price_volume += price * volume
        cumulative_volume += volume
        avg_price = cumulative_price_volume / cumulative_volume if cumulative_volume > 0 else price
        avg_prices.append(avg_price)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'price': prices,
        'avg_price': avg_prices,
        'volume': volumes
    }, index=dates)
    
    return data


def test_basic_kline_chart():
    """测试基本的K线图绘制"""
    print("测试基本的K线图绘制...")
    
    # 生成测试数据
    data = generate_test_kline_data()
    
    # 使用plot_kline函数绘制K线图
    chart = qplot.plot_kline(
        data=data,
        title="测试K线图",
        figsize=(12, 6),
        volume=True,
        ma=[5, 10, 20]
    )
    
    return chart


def test_basic_minute_chart():
    """测试基本的分时图绘制"""
    print("测试基本的分时图绘制...")
    
    # 生成测试数据
    data = generate_test_minute_data()
    
    # 使用plot_minute_chart函数绘制分时图
    chart = qplot.plot_minute_chart(
        data=data,
        title="测试分时图",
        figsize=(12, 6),
        volume=True
    )
    
    return chart


def test_data_manager():
    """测试DataManager的功能"""
    print("测试DataManager的功能...")
    
    # 创建数据管理器
    dm = DataManager()
    
    # 生成并添加数据
    kline_data = generate_test_kline_data()
    minute_data = generate_test_minute_data()
    
    dm.set_kline_data(kline_data)
    dm.set_minute_data(minute_data)
    
    # 使用统一的plot_chart接口绘制图表
    kline_chart = qplot.plot_chart(
        data_manager=dm,
        chart_type='kline',
        title="使用DataManager的K线图",
        volume=True,
        ma=[5, 10, 20]
    )
    
    minute_chart = qplot.plot_chart(
        data_manager=dm,
        chart_type='minute',
        title="使用DataManager的分时图",
        volume=True
    )
    
    return kline_chart, minute_chart


def test_backend_switching():
    """测试后端切换功能"""
    print("测试后端切换功能...")
    
    # 生成测试数据
    kline_data = generate_test_kline_data()
    
    try:
        # 切换到pyecharts后端
        qplot.set_default_backend('pyecharts')
        
        # 绘制K线图
        chart = qplot.plot_kline(
            data=kline_data,
            title="使用pyecharts后端的K线图",
            volume=True
        )
        
        # 切回matplotlib后端
        qplot.set_default_backend('matplotlib')
        
        return chart
    except ImportError:
        print("警告: pyecharts后端依赖未安装，跳过此测试")
        return None


def test_chart_configuration():
    """测试图表配置功能"""
    print("测试图表配置功能...")
    
    # 生成测试数据
    data = generate_test_kline_data()
    
    # 自定义配置
    config = {
        'figsize': (14, 8),
        'title': {
            'text': '自定义配置的K线图',
            'fontsize': 16,
            'fontweight': 'bold'
        },
        'colors': {
            'up_color': 'red',
            'down_color': 'green'
        },
        'grid': {
            'left': '0.05',
            'right': '0.05',
            'bottom': '0.1'
        }
    }
    
    # 绘制图表
    chart = qplot.plot_kline(
        data=data,
        **config
    )
    
    return chart


if __name__ == "__main__":
    print("开始测试qplot库...")
    
    # 测试基本功能
    kline_chart = test_basic_kline_chart()
    minute_chart = test_basic_minute_chart()
    
    # 测试数据管理器
    kline_dm_chart, minute_dm_chart = test_data_manager()
    
    # 测试后端切换
    pyecharts_chart = test_backend_switching()
    
    # 测试图表配置
    config_chart = test_chart_configuration()
    
    print("所有测试完成。请查看生成的图表。")
    
    # 显示matplotlib图表
    if kline_chart:
        kline_chart.show()