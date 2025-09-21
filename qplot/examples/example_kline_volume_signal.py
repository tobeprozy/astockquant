#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""使用pyecharts绘制带成交量和信号的K线图示例"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from qplot import plot_kline, DataManager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_sample_data(start_date='2023-01-01', days=100):
    """
    生成示例股票数据，包含开盘价、最高价、最低价、收盘价、成交量和均线
    
    Args:
        start_date: 起始日期
        days: 数据天数
        
    Returns:
        pd.DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量和均线的数据
    """
    # 创建日期索引
    dates = pd.date_range(start=start_date, periods=days, freq='B')
    
    # 生成随机价格数据
    np.random.seed(42)  # 设置随机种子，确保结果可重现
    base_price = 100
    returns = np.random.normal(0, 0.02, days)
    prices = base_price * (1 + returns).cumprod()
    
    # 生成开盘价、最高价、最低价和收盘价
    open_prices = prices * (1 + np.random.normal(0, 0.005, days))
    high_prices = np.maximum(prices, open_prices) * (1 + np.random.normal(0, 0.005, days))
    low_prices = np.minimum(prices, open_prices) * (1 - np.random.normal(0, 0.005, days))
    close_prices = prices
    
    # 生成成交量
    volume = np.random.randint(1000, 10000, days)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume
    }, index=dates)
    
    # 计算均线
    data['ma5'] = data['close'].rolling(window=5).mean()
    data['ma10'] = data['close'].rolling(window=10).mean()
    data['ma20'] = data['close'].rolling(window=20).mean()
    
    # 添加股票代码和名称属性
    data.attrs['symbol'] = '600519'
    data.attrs['name'] = '贵州茅台'
    
    return data


def example_with_sample_data():
    """使用样本数据绘制带成交量和信号的K线图示例"""
    print("\n=== 使用样本数据绘制带成交量和信号的K线图示例 ===")
    
    try:
        # 生成示例数据
        data = generate_sample_data(days=120)
        print(f"生成示例数据成功，数据量: {len(data)}行")
        print(f"数据列: {list(data.columns)}")
        
        # 创建数据管理器
        kline_manager = DataManager('600519', data_type='kline')
        kline_manager.update_data(data)
        
        # 确保输出目录存在
        output_dir = './output'
        os.makedirs(output_dir, exist_ok=True)
        
        # 示例1: 使用数据管理器和show_volume_signal参数绘制带成交量和信号的K线图
        print("\n1. 使用数据管理器绘制带成交量和信号的K线图")
        kline_chart = plot_kline(
            data_manager=kline_manager,
            title='600519 贵州茅台 带成交量和信号的K线图',
            show_volume_signal=True,
            backend='pyecharts'
        )
        
        # 保存图表
        output_path = os.path.join(output_dir, 'kline_volume_signal_example.html')
        kline_chart.save(output_path)
        print(f"图表已保存至: {output_path}")
        
        # 示例2: 直接传入数据绘制带成交量和信号的K线图
        print("\n2. 直接传入数据绘制带成交量和信号的K线图")
        kline_chart2 = plot_kline(
            data=data,
            title='600519 贵州茅台 带成交量和信号的K线图（直接传入数据）',
            show_volume_signal=True,
            backend='pyecharts'
        )
        
        # 保存图表
        output_path2 = os.path.join(output_dir, 'kline_volume_signal_example_direct.html')
        kline_chart2.save(output_path2)
        print(f"图表已保存至: {output_path2}")
        
        # 示例3: 使用通用plot_chart接口绘制带成交量和信号的K线图
        print("\n3. 使用通用plot_chart接口绘制带成交量和信号的K线图")
        from qplot import plot_chart
        
        kline_chart3 = plot_chart(
            chart_type='kline',
            data=data,
            title='600519 贵州茅台 带成交量和信号的K线图（通用接口）',
            show_volume_signal=True,
            backend='pyecharts'
        )
        
        # 保存图表
        output_path3 = os.path.join(output_dir, 'kline_volume_signal_example_general.html')
        kline_chart3.save(output_path3)
        print(f"图表已保存至: {output_path3}")
        
        print("\n所有示例图表已生成完成！")
        print(f"请查看 {output_dir} 目录下的HTML文件")
        
    except Exception as e:
        logger.error(f"绘制图表时出错: {e}")
        print(f"绘制图表时出错: {e}")


def main():
    """主函数"""
    print("=== 带成交量和信号的K线图示例程序 ===")
    
    # 使用样本数据绘制图表示例
    example_with_sample_data()


if __name__ == "__main__":
    main()