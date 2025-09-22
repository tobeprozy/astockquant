#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试pyecharts图表后端功能
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from qplot import plot_chart, plot_kline, plot_minute_chart, DataManager
import os

# 生成测试数据
def generate_test_data(days=30):
    """生成测试用的K线数据"""
    # 生成K线数据
    dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
    
    # 生成随机价格数据，模拟股票价格走势
    np.random.seed(42)  # 固定随机种子，使结果可复现
    base_price = 100
    volatility = 2
    
    open_prices = [base_price]
    close_prices = []
    high_prices = []
    low_prices = []
    volumes = []
    
    for i in range(1, days):
        # 随机波动
        change = np.random.normal(0, volatility)
        open_price = close_prices[-1] if i > 1 else base_price
        close_price = open_price + change
        high_price = max(open_price, close_price) + np.random.uniform(0, volatility/2)
        low_price = min(open_price, close_price) - np.random.uniform(0, volatility/2)
        volume = np.random.randint(1000, 10000)
        
        open_prices.append(open_price)
        close_prices.append(close_price)
        high_prices.append(high_price)
        low_prices.append(low_price)
        volumes.append(volume)
    
    # 添加第一天的收盘价等数据
    close_prices.insert(0, base_price + np.random.normal(0, volatility))
    high_prices.insert(0, max(open_prices[0], close_prices[0]) + np.random.uniform(0, volatility/2))
    low_prices.insert(0, min(open_prices[0], close_prices[0]) - np.random.uniform(0, volatility/2))
    volumes.insert(0, np.random.randint(1000, 10000))
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=pd.DatetimeIndex(dates))
    
    return data

# 创建测试用的数据管理器
def create_test_data_manager():
    """创建测试用的数据管理器"""
    # 生成测试数据
    data = generate_test_data()
    
    # 创建数据管理器
    data_manager = DataManager(symbol='TEST', data_type='kline')
    
    # 更新数据
    data_manager.update_data(data)
    
    return data_manager

# 测试函数
def test_pyecharts_chart():
    """测试pyecharts图表后端功能"""
    print("开始测试pyecharts图表后端功能...")
    
    # 测试K线图
    print("测试K线图...")
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)

    # 1. 通过data_manager绘制K线图
    print("1. 通过data_manager绘制K线图")
    kline_data_manager = create_test_data_manager()
    chart1 = plot_kline(data_manager=kline_data_manager, title="测试K线图（通过data_manager）", backend='pyecharts', \
                       volume=True, colors={'up_color': '#ff4d4f', 'down_color': '#52c41a'})
    chart1.save(os.path.join(output_dir, 'test_kline_by_data_manager.html'))
    print("  K线图已保存为 test_kline_by_data_manager.html")
    
    # 2. 通过直接传入data绘制K线图
    print("2. 通过直接传入data绘制K线图")
    kline_data = generate_test_data()
    chart2 = plot_kline(data=kline_data, title="测试K线图（通过data参数）", backend='pyecharts', \
                       volume=True, colors={'up_color': '#f5222d', 'down_color': '#73d13d'})
    chart2.save(os.path.join(output_dir, 'test_kline_by_data.html'))
    print("  K线图已保存为 test_kline_by_data.html")
    
    # 3. 使用通用接口plot_chart绘制K线图
    print("3. 使用通用接口plot_chart绘制K线图")
    chart3 = plot_chart(chart_type='kline', data=kline_data, title="测试K线图（通用接口）", backend='pyecharts', \
                       volume=True, grid={'left': '8%', 'right': '8%'})
    chart3.save(os.path.join(output_dir, 'test_kline_by_plot_chart.html'))
    print("  K线图已保存为 test_kline_by_plot_chart.html")
    

    
    # 测试图表更新功能
    print("测试图表更新功能...")
    
    # 生成新数据
    new_kline_data = generate_test_data(days=20)
    
    # 更新图表数据
    chart2.data = new_kline_data  # 更新直接传入的数据
    chart2.update()
    chart2.save(os.path.join(output_dir, 'test_kline_updated.html'))
    print("  更新后的K线图已保存为 test_kline_updated.html")
    
    print("pyecharts图表后端功能测试完成！")

if __name__ == '__main__':
    test_pyecharts_chart()