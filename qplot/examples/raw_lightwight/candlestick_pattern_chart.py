#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 蜡烛图形态识别示例

此示例展示如何使用 lightweight-charts 识别和标记常见的蜡烛图形态。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
from lightweight_charts import Chart
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def identify_candlestick_patterns(df):
    """识别常见的蜡烛图形态并添加标记"""
    # 创建用于存储标记的数据框
    markers = []
    
    # 遍历数据，识别蜡烛图形态
    for i in range(2, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        prev_prev = df.iloc[i-2]
        
        # 1. 锤子线 (Hammer) 和上吊线 (Hanging Man)
        # 锤子线：出现在下降趋势中，实体小，下影线长
        # 上吊线：出现在上升趋势中，实体小，下影线长
        body_size = abs(current['open'] - current['close'])
        lower_shadow = min(current['open'], current['close']) - current['low']
        upper_shadow = current['high'] - max(current['open'], current['close'])
        
        if lower_shadow > 2 * body_size and upper_shadow < body_size:
            # 判断是上升趋势还是下降趋势（简单判断：比较当前价格和5天前的价格）
            if i > 5:
                trend = current['close'] > df.iloc[i-5]['close']
                if trend:
                    # 上吊线
                    markers.append({
                        'date': current['date'],
                        'position': 'below',
                        'shape': 'arrow_up',
                        'color': '#f44336',
                        'text': 'H'
                    })
                else:
                    # 锤子线
                    markers.append({
                        'date': current['date'],
                        'position': 'above',
                        'shape': 'arrow_down',
                        'color': '#4caf50',
                        'text': 'Hm'
                    })
        
        # 2. 吞没形态 (Engulfing Pattern)
        # 看涨吞没：在下降趋势中，第二根蜡烛的实体完全吞没第一根蜡烛的实体
        # 看跌吞没：在上升趋势中，第二根蜡烛的实体完全吞没第一根蜡烛的实体
        if (prev['open'] > prev['close'] and current['open'] < current['close'] and 
            current['open'] < prev['close'] and current['close'] > prev['open']):
            # 看涨吞没
            if i > 5 and current['close'] < df.iloc[i-5]['close']:
                markers.append({
                    'date': current['date'],
                    'position': 'above',
                    'shape': 'arrow_down',
                    'color': '#4caf50',
                    'text': 'CE'
                })
        elif (prev['open'] < prev['close'] and current['open'] > current['close'] and 
              current['open'] > prev['close'] and current['close'] < prev['open']):
            # 看跌吞没
            if i > 5 and current['close'] > df.iloc[i-5]['close']:
                markers.append({
                    'date': current['date'],
                    'position': 'below',
                    'shape': 'arrow_up',
                    'color': '#f44336',
                    'text': 'BE'
                })
        
        # 3. 十字星 (Doji)
        # 实体很小，开盘价和收盘价接近
        if body_size < (current['high'] - current['low']) * 0.1:
            markers.append({
                'date': current['date'],
                'position': 'above',
                'shape': 'circle',
                'color': '#ff9800',
                'text': 'D'
            })
    
    # 将标记转换为DataFrame
    if markers:
        markers_df = pd.DataFrame(markers)
        return markers_df
    else:
        return None

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
    
    # 识别蜡烛图形态
    logger.info("识别常见的蜡烛图形态")
    patterns_df = identify_candlestick_patterns(df)
    
    # 创建图表
    logger.info("创建图表并标记蜡烛图形态")
    chart = Chart(
        width=1000,
        height=600,
        toolbox=True,
        title=f'{code} 蜡烛图形态识别示例'
    )
    
    # 设置图表数据
    chart.set(df)
    
    # 添加样式
    chart.candle_style(up_color='#26a69a', down_color='#ef5350')
    chart.watermark(f'{code} - 蜡烛图形态识别')
    
    # 添加蜡烛图形态标记
    if patterns_df is not None:
        logger.info(f"识别到 {len(patterns_df)} 个蜡烛图形态")
        
        # 逐个添加标记
        for _, marker in patterns_df.iterrows():
            chart.marker(
                time=marker['date'],
                position=marker['position'],
                shape=marker['shape'],
                color=marker['color'],
                text=marker['text']
            )
        
        # 显示形态说明
        print("\n===== 蜡烛图形态标记说明 =====")
        print("• Hm: 锤子线 (Hammer) - 可能的底部反转信号")
        print("• H: 上吊线 (Hanging Man) - 可能的顶部反转信号")
        print("• CE: 看涨吞没 (Bullish Engulfing) - 可能的上涨信号")
        print("• BE: 看跌吞没 (Bearish Engulfing) - 可能的下跌信号")
        print("• D: 十字星 (Doji) - 可能的反转信号")
        print("=============================\n")
    else:
        logger.info("未识别到明显的蜡烛图形态")
    
    # 显示图表
    logger.info("显示蜡烛图形态识别图表")
    chart.show(block=True)


if __name__ == "__main__":
    main()