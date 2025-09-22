#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 模拟实时更新示例

此示例展示如何使用 lightweight-charts 模拟实时更新股票数据。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from lightweight_charts import Chart
import logging

logger = logging.getLogger(__name__)

def main():
    # 初始化 qdata
    qdata.init()
    logger.info("qdata 初始化完成")
    
    # 计算日期范围（当前日期到往前3年）
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
    
    # 获取股票数据
    code = "000001"
    logger.info(f"获取股票 {code} 的数据 (日期范围: {start_date} 到 {end_date})" )
    df = qdata.get_daily_data(code, start_date, end_date, backend='akshare')
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
    
    # 创建图表并设置样式
    logger.info("创建图表并设置样式")
    chart = Chart()
    chart.watermark(code)
    chart.candle_style(up_color='#26a69a', down_color='#ef5350')
    chart.set(df)
    chart.show(block=False)
    
    # 获取最后一条数据的时间和价格
    last_time = df.iloc[-1]["date"] + timedelta(days=1)
    last_price = df.iloc[-1]["close"]
    
    # 开始模拟实时更新
    logger.info("开始模拟实时更新（按Ctrl+C停止）...")
    
    try:
        while True:
            time.sleep(0.1)  # 每0.1秒更新一次
            
            # 随机生成价格变化
            change_percent = 0.002
            change = last_price * random.uniform(-change_percent, change_percent)
            new_price = last_price + change
            new_time = pd.to_datetime(last_time) + timedelta(hours=1)
            
            # 创建新的tick数据
            tick = pd.Series({"time": new_time, "price": new_price})
            
            # 更新图表
            chart.update_from_tick(tick)
            
            # 更新最后价格和时间
            last_price = new_price
            last_time = new_time
    except KeyboardInterrupt:
        logger.info("模拟实时更新已停止")
    
    input("按回车键关闭图表...")


if __name__ == "__main__":
    main()