# -*- coding: utf-8 -*-
"""
qplot库示例
展示如何使用qplot库进行股票数据可视化
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging
from qplot import DataManager, plot_kline, plot_minute_chart, plot_chart

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 创建示例K线数据
def create_sample_kline_data():
    """创建示例K线数据"""
    # 生成日期序列
    end_date = datetime.now()
    start_date = end_date - timedelta(days=100)
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    
    # 生成随机价格数据
    np.random.seed(42)
    base_price = 100
    close_prices = [base_price]
    
    for _ in range(1, len(dates)):
        change = np.random.normal(0, 2)
        new_price = close_prices[-1] + change
        close_prices.append(new_price)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': [p + np.random.normal(0, 1) for p in close_prices],
        'high': [p + np.random.uniform(0, 3) for p in close_prices],
        'low': [p - np.random.uniform(0, 3) for p in close_prices],
        'close': close_prices,
        'volume': [int(np.random.uniform(1000, 10000)) for _ in close_prices]
    })
    
    # 设置日期为索引
    data.set_index('date', inplace=True)
    return data


# 创建示例分时数据
def create_sample_minute_data():
    """创建示例分时数据"""
    # 生成一天内的时间序列
    date_str = datetime.now().strftime('%Y-%m-%d')
    start_time = f'{date_str} 09:30:00'
    end_time = f'{date_str} 15:00:00'
    times = pd.date_range(start=start_time, end=end_time, freq='1min')
    
    # 生成随机价格数据
    np.random.seed(42)
    base_price = 100
    prices = [base_price]
    
    for _ in range(1, len(times)):
        change = np.random.normal(0, 0.1)
        new_price = prices[-1] + change
        prices.append(new_price)
    
    # 生成均价和成交量
    avg_prices = [p + np.random.normal(0, 0.05) for p in prices]
    volumes = [int(np.random.uniform(100, 1000)) for _ in prices]
    
    # 创建DataFrame
    data = pd.DataFrame({
        'time': times,
        'price': prices,
        'avg_price': avg_prices,
        'volume': volumes
    })
    
    # 设置时间为索引
    data.set_index('time', inplace=True)
    return data


def example_basic_charts():
    """基础图表绘制示例"""
    print("=== 基础图表绘制示例 ===")
    
    # 创建数据管理器
    kline_manager = DataManager('600000')
    kline_manager.update_data(create_sample_kline_data())
    
    # 绘制K线图
    print("绘制K线图...")
    kline_chart = plot_kline(data_manager=kline_manager, show_volume=True)
    
    # 创建分时图数据管理器
    minute_manager = DataManager('600000', data_type='minute')
    minute_manager.update_data(create_sample_minute_data())
    
    # 绘制分时图
    print("绘制分时图...")
    minute_chart = plot_minute_chart(data_manager=minute_manager, show_avg_line=True)
    
    # 保存图表
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    kline_chart.save(os.path.join(output_dir, 'kline_example.png'))
    print(f"K线图已保存至: {os.path.join(output_dir, 'kline_example.png')}")
    
    minute_chart.save(os.path.join(output_dir, 'minute_example.png'))
    print(f"分时图已保存至: {os.path.join(output_dir, 'minute_example.png')}")


def example_with_real_data():
    """使用真实数据绘制图表示例"""
    print("\n=== 使用真实数据绘制图表示例 ===")
    
    try:
        # 创建数据管理器
        kline_manager = DataManager('600000')
        
        # 获取最近30天的历史数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        kline_manager.fetch_history_data(start_date, end_date)
        
        if kline_manager.data is not None and not kline_manager.data.empty:
            print(f"成功获取数据，数据量: {len(kline_manager.data)}行")
            
            # 绘制K线图
            kline_chart = plot_kline(
                data_manager=kline_manager,
                title=f'600000 日K线图 ({start_date} - {end_date})',
                show_volume=True,
                indicators=['ma5', 'ma10', 'ma20']
            )
            
            # 保存图表
            output_dir = './output'
            os.makedirs(output_dir, exist_ok=True)
            
            kline_chart.save(os.path.join(output_dir, 'real_kline_example.png'))
            print(f"真实数据K线图已保存至: {os.path.join(output_dir, 'real_kline_example.png')}")
        else:
            print("未能获取到真实数据，可能是qdata配置问题或网络问题")
            print("请确保已正确配置qdata库，或使用set_data方法传入自定义数据")
            
    except Exception as e:
        logger.error(f"使用真实数据绘制图表时出错: {e}")
        print(f"获取真实数据时出错: {e}")
        print("请确保已正确安装和配置qdata库")


def example_multi_charts():
    """多图表绘制示例"""
    print("\n=== 多图表绘制示例 ===")
    
    # 创建数据管理器
    kline_manager = DataManager('600000')
    kline_manager.update_data(create_sample_kline_data())
    
    # 绘制多个图表
    print("绘制多个图表...")
    charts = []
    
    # 基本K线图
    charts.append(plot_kline(data_manager=kline_manager, title="基本K线图"))
    
    # 带成交量的K线图
    charts.append(plot_kline(data_manager=kline_manager, title="带成交量的K线图", show_volume=True))
    
    # 带指标的K线图
    charts.append(plot_kline(
        data_manager=kline_manager, 
        title="带均线指标的K线图", 
        indicators=['ma5', 'ma10', 'ma20']
    ))
    
    # 保存所有图表
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    for i, chart in enumerate(charts):
        chart.save(os.path.join(output_dir, f'multi_chart_{i+1}.png'))
        print(f"多图表{i+1}已保存至: {os.path.join(output_dir, f'multi_chart_{i+1}.png')}")


def main():
    """主函数"""
    print("========== qplot库示例 ==========")
    
    # 示例1: 基础图表绘制
    example_basic_charts()
    
    # 示例2: 使用真实数据绘制图表
    example_with_real_data()
    
    # 示例3: 多图表绘制
    example_multi_charts()
    
    print("\n========== 所有示例运行完毕 ==========")


if __name__ == "__main__":
    main()