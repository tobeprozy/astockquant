#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightweight-charts 交互式股票筛选器示例

此示例展示如何创建一个简单的股票筛选器，并使用 lightweight-charts 查看筛选结果。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
import numpy as np
from lightweight_charts import Chart
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class StockScreener:
    """股票筛选器类"""
    def __init__(self):
        # 初始化 qdata
        qdata.init()
        qdata.set_current_provider('akshare')
        logger.info("qdata 初始化完成，数据源设置为 akshare")
        
        # 计算日期范围
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 存储股票数据
        self.stock_data = {}
        
        # 预定义一些股票代码用于演示
        self.sample_stocks = [
            "000001", "000002", "000858", "002594", "300750", 
            "600000", "600519", "601318", "601899", "603288"
        ]
    
    def fetch_stock_data(self, code):
        """获取单个股票的数据"""
        if code in self.stock_data:
            return self.stock_data[code]
        
        try:
            logger.info(f"获取股票 {code} 的数据")
            df = qdata.get_daily_data(code, self.start_date, self.end_date)
            
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
            
            # 计算一些基本指标用于筛选
            if len(df) > 20:
                df['ma20'] = df['close'].rolling(window=20).mean()
                df['return_1m'] = df['close'].pct_change(20) * 100  # 1个月回报率
                df['volatility'] = df['close'].pct_change().rolling(window=20).std() * 100 * np.sqrt(252)  # 年化波动率
            
            self.stock_data[code] = df
            return df
        except Exception as e:
            logger.error(f"获取股票 {code} 数据失败: {e}")
            return None
    
    def screen_stocks(self, min_return=None, max_volatility=None, above_ma20=False):
        """根据条件筛选股票"""
        results = []
        
        for code in self.sample_stocks:
            df = self.fetch_stock_data(code)
            if df is None or len(df) < 20:
                continue
            
            # 获取最新数据
            latest = df.iloc[-1]
            
            # 应用筛选条件
            match = True
            
            if min_return is not None and latest['return_1m'] < min_return:
                match = False
            
            if max_volatility is not None and latest['volatility'] > max_volatility:
                match = False
            
            if above_ma20 and latest['close'] < latest['ma20']:
                match = False
            
            if match:
                results.append({
                    'code': code,
                    'close': latest['close'],
                    'return_1m': latest['return_1m'],
                    'volatility': latest['volatility'],
                    'above_ma20': latest['close'] > latest['ma20']
                })
        
        # 按1个月回报率排序
        results.sort(key=lambda x: x['return_1m'], reverse=True)
        return results

def show_stock_chart(screener, code):
    """显示股票图表"""
    df = screener.fetch_stock_data(code)
    if df is None:
        print(f"无法获取股票 {code} 的数据")
        return
    
    # 创建图表
    chart = Chart(
        width=1000,
        height=700,
        toolbox=True,
        title=f'{code} 日线图'
    )
    
    # 设置主图表数据
    chart.set(df)
    
    # 添加20日均线
    if 'ma20' in df.columns:
        ma20_line = chart.create_line('ma20', color='#FF9800')
    
    # 添加成交量副面板
    volume_pane = chart.create_subchart(height=100)
    volume_pane.set(df)
    volume_line = volume_pane.create_line('volume', color='#26a69a', width=1)
    
    # 添加样式
    chart.candle_style(up_color='#26a69a', down_color='#ef5350', border_width=1)
    chart.watermark(f'{code} - {screener.start_date} 至 {screener.end_date}')
    
    # 显示图表
    chart.show(block=True)

def main():
    # 创建股票筛选器实例
    screener = StockScreener()
    
    print("\n===== 交互式股票筛选器 =====")
    print(f"当前筛选日期范围: {screener.start_date} 至 {screener.end_date}")
    
    while True:
        print("\n请选择筛选条件:")
        print("1. 按1个月回报率筛选")
        print("2. 按波动率筛选")
        print("3. 仅显示价格在20日均线上方的股票")
        print("4. 综合条件筛选")
        print("5. 退出")
        
        choice = input("请输入选项 (1-5): ")
        
        if choice == '5':
            break
        
        min_return = None
        max_volatility = None
        above_ma20 = False
        
        if choice == '1':
            try:
                min_return = float(input("请输入最小1个月回报率 (%): "))
            except ValueError:
                print("输入无效，请重试")
                continue
        elif choice == '2':
            try:
                max_volatility = float(input("请输入最大波动率 (%): "))
            except ValueError:
                print("输入无效，请重试")
                continue
        elif choice == '3':
            above_ma20 = True
        elif choice == '4':
            try:
                min_return_input = input("请输入最小1个月回报率 (%，留空跳过): ")
                if min_return_input:
                    min_return = float(min_return_input)
                
                max_volatility_input = input("请输入最大波动率 (%，留空跳过): ")
                if max_volatility_input:
                    max_volatility = float(max_volatility_input)
                
                above_ma20_input = input("仅显示价格在20日均线上方的股票? (y/n，留空跳过): ")
                if above_ma20_input.lower() == 'y':
                    above_ma20 = True
            except ValueError:
                print("输入无效，请重试")
                continue
        else:
            print("无效选项，请重试")
            continue
        
        # 执行筛选
        logger.info(f"执行股票筛选 (min_return={min_return}, max_volatility={max_volatility}, above_ma20={above_ma20})")
        results = screener.screen_stocks(min_return, max_volatility, above_ma20)
        
        if not results:
            print("没有找到符合条件的股票")
            continue
        
        # 显示筛选结果
        print("\n===== 筛选结果 =====")
        print(f"找到 {len(results)} 只符合条件的股票:")
        print("{:<8} {:<10} {:<12} {:<12} {:<15}".format(
            "股票代码", "收盘价", "1月回报率(%)", "波动率(%)", "在20日均线上方"))
        
        for stock in results:
            print("{:<8} {:<10.2f} {:<12.2f} {:<12.2f} {:<15}".format(
                stock['code'], 
                stock['close'], 
                stock['return_1m'], 
                stock['volatility'], 
                "是" if stock['above_ma20'] else "否"))
        
        # 询问用户是否要查看某只股票的图表
        while True:
            view_chart = input("\n请输入要查看图表的股票代码 (输入'q'返回筛选菜单): ")
            if view_chart.lower() == 'q':
                break
            
            if view_chart in [stock['code'] for stock in results]:
                show_stock_chart(screener, view_chart)
            else:
                print("无效的股票代码，请从筛选结果中选择")


if __name__ == "__main__":
    main()