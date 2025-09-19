#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略对比示例
展示如何同时运行多个策略并比较它们的表现
"""

from ctypes import sizeof
import qbackengine
import logging
import time
from datetime import datetime

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_strategy(strategy_name, strategy_kwargs=None):
    """
    运行单个策略并返回结果
    
    参数:
        strategy_name: 策略名称
        strategy_kwargs: 策略参数
        
    返回:
        包含策略名称、回测结果和运行时间的字典
    """
    start_time = time.time()
    
    print(f"\n正在运行 {strategy_name} 策略...")
    
    try:
        # 创建策略回测引擎
        engine = qbackengine.create_backtrader_engine(
            symbol='600000',  # 茅台股票代码
            start_date='2024-01-01',
            end_date='2024-12-31',
            strategy_name=strategy_name,
            starting_cash=100000.0,
            commission=0.00025,
            strategy_kwargs=strategy_kwargs or {}
        )
        
        # 运行回测
        result = engine.run()
        
        end_time = time.time()
        run_duration = end_time - start_time
        
        # 提取回测结果指标
        # 注意：backtrader引擎的run方法返回的是一个策略实例列表
        if result and len(result) > 0 and hasattr(result[0], 'broker'):
            final_value = result[0].broker.getvalue()
        else:
            final_value = 0
        
        initial_value = 100000.0
        net_profit = final_value - initial_value
        
        return {
            'name': strategy_name,
            'final_value': final_value,
            'initial_value': initial_value,
            'net_profit': net_profit,
            'profit_ratio': (net_profit / initial_value) * 100,
            'run_time': run_duration
        }
        
    except Exception as e:
        print(f"运行 {strategy_name} 策略出错: {e}")
        return None

def main():
    """主函数：运行多个策略并比较结果"""
    print("===== 策略对比示例 ====")
    
    # 定义要比较的策略和它们的参数
    strategies_to_compare = [
        {
            'name': 'MA_Cross',
            'kwargs': {'fast_period': 5, 'slow_period': 20, 'printlog': False,'size':10000}
        },
        {
            'name': 'MACD',
            'kwargs': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9, 'printlog': False,'size':10000}
        },
        {
            'name': 'RSI',
            'kwargs': {'period': 14, 'overbought': 70, 'oversold': 30, 'printlog': False,'size':10000}
        },
        {
            'name': 'BBands',
            'kwargs': {'period': 20, 'devfactor': 2.0, 'printlog': False,'size':10000}
        }
    ]
    
    # 运行所有策略
    results = []
    for strategy_info in strategies_to_compare:
        result = run_strategy(strategy_info['name'], strategy_info['kwargs'])
        if result:
            results.append(result)
    
    # 按净利润排序结果
    results.sort(key=lambda x: x['net_profit'], reverse=True)
    
    # 打印比较结果
    print("\n===== 策略比较结果 ====")
    print("排名 | 策略名称 | 初始资金 | 最终资金 | 净利润 | 收益率(%) | 运行时间(秒)")
    print("-----|---------|---------|---------|-------|----------|-----------")
    
    for i, result in enumerate(results, 1):
        print(f"{i:2d}   | {result['name']:8s} | {result['initial_value']:8.2f} | {result['final_value']:8.2f} | {result['net_profit']:6.2f} | {result['profit_ratio']:9.2f} | {result['run_time']:10.2f}")
    
    print("\n策略对比完成！")

if __name__ == '__main__':
    main()