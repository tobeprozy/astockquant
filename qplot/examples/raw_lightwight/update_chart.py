#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 逐步更新图表数据示例

此示例展示如何使用 lightweight-charts 逐步更新图表数据。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
import time
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
    
    # 创建图表并设置初始数据
    logger.info("创建图表并设置初始数据")
    chart = Chart()
    chart.set(df.iloc[:-10])
    chart.show(block=False)
    
    # 逐步更新最后10条数据
    logger.info("开始逐步更新最后10条数据")
    for bar in df.iloc[-10:].itertuples(index=False):
        # 将命名元组转换为字典
        bar_dict = bar._asdict()
        # 为update_from_tick方法添加price字段，使用close价格
        bar_dict['price'] = bar_dict.get('close', bar_dict.get('close_price'))
        # 将字典转换为pandas Series对象
        tick_series = pd.Series(bar_dict)
        chart.update_from_tick(tick_series)
        time.sleep(1)  # 每秒更新一条数据
    logger.info("数据更新完成")
    
    # 等待用户输入，防止程序立即退出
    input("按Enter键继续...")


if __name__ == "__main__":
    main()