#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 使用日期格式绘制图表示例

此示例展示如何使用 lightweight-charts 绘制带有日期格式的图表。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
from lightweight_charts import Chart
import logging
from datetime import datetime, timedelta

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
    chart.show(block=True)


if __name__ == "__main__":
    main()