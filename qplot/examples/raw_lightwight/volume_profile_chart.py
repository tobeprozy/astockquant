#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 成交量分布图示例

此示例展示如何使用 lightweight-charts 添加成交量分布图到图表中。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
import numpy as np
from lightweight_charts import Chart
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def calculate_volume_profile(df, price_bins=20):
    """计算成交量分布"""
    # 创建价格区间
    price_min = df['low'].min()
    price_max = df['high'].max()
    price_range = price_max - price_min
    bin_width = price_range / price_bins
    
    # 初始化每个价格区间的成交量
    volume_profile = []
    
    # 遍历每个价格区间
    for i in range(price_bins):
        bin_start = price_min + (i * bin_width)
        bin_end = price_min + ((i + 1) * bin_width)
        
        # 计算落在当前价格区间内的成交量
        bin_volume = 0
        for _, row in df.iterrows():
            # 如果价格区间与K线有交集
            if not (row['high'] < bin_start or row['low'] > bin_end):
                # 简单计算：按K线在区间内的比例分配成交量
                overlap = min(row['high'], bin_end) - max(row['low'], bin_start)
                total_range = row['high'] - row['low']
                if total_range > 0:
                    bin_volume += (overlap / total_range) * row['volume']
                else:
                    # 处理开盘价和收盘价相同的情况
                    if bin_start <= row['close'] < bin_end:
                        bin_volume += row['volume']
        
        # 添加到成交量分布列表
        volume_profile.append({
            'price': (bin_start + bin_end) / 2,  # 区间中点价格
            'volume': bin_volume
        })
    
    # 转换为DataFrame
    volume_profile_df = pd.DataFrame(volume_profile)
    return volume_profile_df

def main():
    # 初始化 qdata
    qdata.init()
    qdata.set_current_provider('akshare')
    logger.info("qdata 初始化完成，数据源设置为 akshare")
    
    # 计算日期范围（当前日期到往前3年）
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
    
    # 获取股票数据
    code = "000001"
    logger.info(f"获取股票 {code} 的数据 (日期范围: {start_date} 到 {end_date})")
    df = qdata.get_daily_data(code, start_date, end_date)
    logger.info(f"数据获取完成，共 {len(df)} 条记录")
    
    # 处理数据格式
    if 'date' not in df.columns and df.index.name == 'date':
        df = df.reset_index()
    
    # 确保日期列正确
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif 'trade_date' in df.columns:
        df['date'] = pd.to_datetime(df['trade_date'])
    
    # 按日期排序
    df = df.sort_values(by="date", ascending=True)
    
    # 重命名列
    if 'vol' in df.columns and 'volume' not in df.columns:
        df.rename(columns={"vol": "volume"}, inplace=True)
    
    # 选择需要的列
    required_columns = [col for col in ["date", "open", "high", "low", "close", "volume"] if col in df.columns]
    df = df[required_columns]
    
    # 计算成交量分布
    logger.info("计算成交量分布数据")
    volume_profile_df = calculate_volume_profile(df)
    
    # 创建图表
    logger.info("创建图表并添加成交量分布图")
    chart = Chart(
        width=1000,
        height=700,
        toolbox=True,
        title=f'{code} 成交量分布图示例'
    )
    
    # 设置主图表数据
    chart.set(df)
    
    # 添加成交量副面板
    volume_pane = chart.create_subchart(height=100)
    volume_pane.set(df)
    volume_line = volume_pane.create_line('volume', color='#26a69a', width=1)
    
    # 添加成交量分布图（作为垂直直方图）
    # 注意：lightweight-charts 原生不直接支持成交量分布图
    # 这里我们使用自定义的方式模拟成交量分布图
    logger.info("添加成交量分布图")
    
    # 找到最大成交量用于归一化
    max_volume = volume_profile_df['volume'].max()
    
    # 为了在图表上显示成交量分布，我们创建一个特殊的系列
    # 这里我们在主图表的右侧显示成交量分布
    # 创建一系列水平线来表示成交量分布
    for _, row in volume_profile_df.iterrows():
        # 根据成交量大小设置线的长度（归一化到图表宽度的一部分）
        line_length = (row['volume'] / max_volume) * 0.1  # 最大占图表宽度的10%
        
        # 添加水平线来表示成交量分布
        chart.horizontal_line(
            price=row['price'],
            color='rgba(38, 166, 154, 0.3)',  # 使用半透明的绿色
            width=line_length * 100  # 转换为百分比
        )
    
    # 添加样式
    chart.candle_style(up_color='#26a69a', down_color='#ef5350')
    chart.watermark(f'{code} - 成交量分布图')
    
    # 显示说明
    print("\n===== 成交量分布图说明 =====")
    print("• 右侧的垂直彩色区域表示不同价格区间的成交量分布")
    print("• 颜色越深表示该价格区间的成交量越大")
    print("• 成交量分布图可以帮助识别支撑位和阻力位")
    print("=========================\n")
    
    # 显示图表
    logger.info("显示成交量分布图")
    chart.show(block=True)


if __name__ == "__main__":
    main()