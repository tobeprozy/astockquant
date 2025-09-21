#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 多面板图表示例

此示例展示如何使用 lightweight-charts 创建多面板图表。
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
    
    # 计算一些技术指标用于多面板显示
    logger.info("计算技术指标 (SMA5、SMA10 和成交量变化率)")
    # 计算5日移动平均线
    df['sma5'] = df['close'].rolling(window=5).mean()
    
    # 计算10日移动平均线
    df['sma10'] = df['close'].rolling(window=10).mean()
    
    # 计算成交量变化率
    df['volume_pct_change'] = df['volume'].pct_change() * 100
    logger.info("技术指标计算完成")
    
    # 创建主图表并设置数据
    logger.info("创建多面板图表并设置数据")
    chart = Chart(
        width=900, 
        height=600, 
        toolbox=True,
        title=f'{code} 多面板图表'
    )
    
    chart.set(df)
    
    # 添加移动平均线
    line5 = chart.create_line('sma5', color='#ff9800', width=1.5)
    line5.set(df[['date', 'sma5']])
    
    line10 = chart.create_line('sma10', color='#2196f3', width=1.5)
    line10.set(df[['date', 'sma10']])
    
    # 创建副图表（替代create_pane）
    volume_subchart = chart.create_subchart(height=100)
    volume_subchart.set(df)
    volume_line = volume_subchart.create_line('Volume', color='#26a69a')
    
    volume_change_subchart = chart.create_subchart(height=100)
    volume_change_subchart.set(df)
    volume_change_line = volume_change_subchart.create_line('Volume % Change', color='#e91e63')
    
    # 显示图表
    logger.info("显示多面板图表")
    chart.show(block=True)


if __name__ == "__main__":
    main()