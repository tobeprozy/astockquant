#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pyecharts K线图和MACD示例

展示如何使用qplot的重构后API绘制包含MACD指标的K线图
"""

import pandas as pd
import numpy as np
import logging
import os
from qplot import DataManager, plot_kline

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_data(start_date='2023-01-01', days=100):
    """
    生成示例股票数据
    
    Args:
        start_date: 起始日期
        days: 数据天数
        
    Returns:
        pd.DataFrame: 包含开盘价、最高价、最低价、收盘价的数据
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
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, days)
    }, index=dates)
    
    # 添加股票代码属性
    data.attrs['symbol'] = '600519'
    data.attrs['name'] = '贵州茅台'
    
    return data

def main():
    """主函数"""
    try:
        # 生成示例数据
        logger.info("正在生成示例股票数据...")
        data = generate_sample_data()
        logger.info(f"生成了{len(data)}行数据")
        
        # 绘制包含MACD的K线图（直接传递数据）
        logger.info("正在绘制包含MACD指标的K线图...")
        chart = plot_kline(
            data=data,  # 直接传递数据
            backend='pyecharts',  # 指定使用pyecharts后端
            show_volume=True,     # 显示成交量
            show_macd=True,       # 启用MACD指标显示
            title='贵州茅台K线图与MACD指标'
        )
        
        # 创建output目录（如果不存在）
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存图表到output目录
        output_path = os.path.join(output_dir, 'pyecharts_kline_macd_example.html')
        chart.save(output_path)
        logger.info(f"图表已保存到: {output_path}")
        
        # 显示图表（可选）
        # chart.show()
        
    except Exception as e:
        logger.error(f"绘制图表时出错: {e}")
        raise

if __name__ == '__main__':
    main()