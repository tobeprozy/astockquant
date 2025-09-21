#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QStrategy 策略示例
展示如何使用不同的交易策略
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化 qindicator 和 qstrategy
import qindicator
import qstrategy

qindicator.init()
qstrategy.init()

def generate_sample_stock_data(start_date='2020-01-01', end_date='2023-12-31', price_level=100, volatility=0.02, trend_strength=0.001):
    """
    生成样本股票数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        price_level: 初始价格水平
        volatility: 日波动率
        trend_strength: 趋势强度
        
    Returns:
        pd.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价的DataFrame
    """
    # 生成日期范围
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # B表示工作日
    
    # 生成随机价格变动
    np.random.seed(42)  # 设置随机种子以确保结果可重复
    returns = np.random.normal(0, volatility, len(date_range))
    
    # 添加趋势
    trend = np.linspace(0, len(date_range) * trend_strength, len(date_range))
    returns = returns + trend / len(date_range)
    
    # 计算价格序列
    price = price_level * np.exp(np.cumsum(returns))
    
    # 生成开盘价、最高价、最低价
    open_price = price * (1 + np.random.normal(0, 0.01, len(date_range)))
    high_price = np.maximum(price, open_price) * (1 + np.random.uniform(0, 0.02, len(date_range)))
    low_price = np.minimum(price, open_price) * (1 - np.random.uniform(0, 0.02, len(date_range)))
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': open_price,
        'high': high_price,
        'low': low_price,
        'close': price
    }, index=date_range)
    
    # 添加成交量
    data['volume'] = np.random.randint(100000, 1000000, len(date_range))
    
    return data

def generate_pair_stock_data(start_date='2020-01-01', end_date='2023-12-31', price_level=100):
    """
    生成配对交易的两只股票数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        price_level: 初始价格水平
        
    Returns:
        tuple: (stock1_data, stock2_data)
    """
    # 生成日期范围
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # B表示工作日
    
    # 设置随机种子以确保结果可重复
    np.random.seed(43)
    
    # 生成共同趋势
    common_trend = np.cumsum(np.random.normal(0.001, 0.02, len(date_range)))
    
    # 生成股票1价格
    stock1_returns = np.random.normal(0, 0.02, len(date_range))
    stock1_price = price_level * np.exp(common_trend + stock1_returns)
    
    # 生成股票2价格（与股票1有相关性）
    stock2_returns = 0.7 * stock1_returns + 0.3 * np.random.normal(0, 0.02, len(date_range)) + 0.0005
    stock2_price = price_level * np.exp(common_trend + stock2_returns)
    
    # 创建股票1的DataFrame
    stock1_data = pd.DataFrame({
        'open': stock1_price * (1 + np.random.normal(0, 0.01, len(date_range))),
        'high': np.maximum(stock1_price, stock1_data['open']) * (1 + np.random.uniform(0, 0.02, len(date_range))),
        'low': np.minimum(stock1_price, stock1_data['open']) * (1 - np.random.uniform(0, 0.02, len(date_range))),
        'close': stock1_price,
        'volume': np.random.randint(100000, 1000000, len(date_range))
    }, index=date_range)
    
    # 修正股票1的high和low计算
    stock1_data['high'] = np.maximum(stock1_data['high'], stock1_data['open'], stock1_data['close'])
    stock1_data['low'] = np.minimum(stock1_data['low'], stock1_data['open'], stock1_data['close'])
    
    # 创建股票2的DataFrame
    stock2_data = pd.DataFrame({
        'open': stock2_price * (1 + np.random.normal(0, 0.01, len(date_range))),
        'high': np.maximum(stock2_price, stock2_data['open']) * (1 + np.random.uniform(0, 0.02, len(date_range))),
        'low': np.minimum(stock2_price, stock2_data['open']) * (1 - np.random.uniform(0, 0.02, len(date_range))),
        'close': stock2_price,
        'volume': np.random.randint(100000, 1000000, len(date_range))
    }, index=date_range)
    
    # 修正股票2的high和low计算
    stock2_data['high'] = np.maximum(stock2_data['high'], stock2_data['open'], stock2_data['close'])
    stock2_data['low'] = np.minimum(stock2_data['low'], stock2_data['open'], stock2_data['close'])
    
    return stock1_data, stock2_data

def plot_strategy_results(data, strategy_name, indicators_data=None, signals=None, trades=None):
    """
    可视化策略结果
    
    Args:
        data: 价格数据
        strategy_name: 策略名称
        indicators_data: 指标数据
        signals: 信号数据
        trades: 交易数据
    """
    plt.figure(figsize=(14, 8))
    
    # 绘制价格
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['close'], label='收盘价')
    
    # 绘制指标
    if indicators_data is not None:
        if 'ma_short' in indicators_data and 'ma_long' in indicators_data:
            plt.plot(indicators_data.index, indicators_data['ma_short'], label='短期均线')
            plt.plot(indicators_data.index, indicators_data['ma_long'], label='长期均线')
        if 'upper_band' in indicators_data and 'lower_band' in indicators_data:
            plt.plot(indicators_data.index, indicators_data['upper_band'], '--', label='上轨')
            plt.plot(indicators_data.index, indicators_data['lower_band'], '--', label='下轨')
            if 'middle_band' in indicators_data:
                plt.plot(indicators_data.index, indicators_data['middle_band'], label='中轨')
        if 'macd' in indicators_data and 'signal' in indicators_data:
            plt.subplot(2, 1, 2)
            plt.plot(indicators_data.index, indicators_data['macd'], label='MACD')
            plt.plot(indicators_data.index, indicators_data['signal'], label='信号线')
            plt.bar(indicators_data.index, indicators_data.get('hist', np.zeros_like(indicators_data['macd'])), label='MACD柱状线')
    
    # 绘制RSI指标
    if indicators_data is not None and 'rsi' in indicators_data:
        if 'macd' not in indicators_data:
            plt.subplot(2, 1, 2)
        plt.plot(indicators_data.index, indicators_data['rsi'], label='RSI')
        plt.axhline(y=70, color='r', linestyle='--', alpha=0.3)
        plt.axhline(y=30, color='g', linestyle='--', alpha=0.3)
    
    # 绘制信号
    if signals is not None:
        for buy_date in signals.get('buy_signals', []):
            if buy_date in data.index:
                price = data.loc[buy_date, 'close']
                plt.subplot(2, 1, 1)
                plt.scatter(buy_date, price, marker='^', color='g', s=100, label='买入信号' if '买入信号' not in plt.gca().get_legend_handles_labels()[1] else "")
        
        for sell_date in signals.get('sell_signals', []):
            if sell_date in data.index:
                price = data.loc[sell_date, 'close']
                plt.subplot(2, 1, 1)
                plt.scatter(sell_date, price, marker='v', color='r', s=100, label='卖出信号' if '卖出信号' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # 设置图表属性
    plt.subplot(2, 1, 1)
    plt.title(f'{strategy_name} 策略结果')
    plt.xlabel('日期')
    plt.ylabel('价格')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if indicators_data is not None and ('rsi' in indicators_data or 'macd' in indicators_data):
        plt.subplot(2, 1, 2)
        plt.xlabel('日期')
        if 'rsi' in indicators_data:
            plt.ylabel('RSI')
        elif 'macd' in indicators_data:
            plt.ylabel('MACD')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def run_strategy_example(strategy_name, data, plot_results=True, **kwargs):
    """
    运行策略示例
    
    Args:
        strategy_name: 策略名称
        data: 价格数据
        plot_results: 是否绘制结果
        **kwargs: 策略参数
        
    Returns:
        tuple: (indicators_data, signals, result)
    """
    try:
        print(f"\n=== 运行 {strategy_name} 策略 ===")
        
        # 获取策略
        strategy = qstrategy.get_strategy(strategy_name, **kwargs)
        
        # 初始化数据
        strategy.init_data(data)
        
        # 计算指标
        indicators_data = strategy.calculate_indicators()
        
        # 生成信号
        signals = strategy.generate_signals()
        
        # 执行交易
        result = strategy.execute_trade()
        
        # 打印结果摘要
        print(f"策略: {strategy_name}")
        print(f"交易次数: {result.get('num_trades', 0)}")
        print(f"总利润: {result.get('total_profit', 0):.2f}")
        print(f"最终持仓: {result.get('final_position', 0)}")
        if 'final_portfolio_value' in result:
            print(f"最终组合价值: {result.get('final_portfolio_value', 0):.2f}")
        
        # 可视化结果
        if plot_results:
            plot_strategy_results(data, strategy_name, indicators_data, signals, result.get('trades'))
        
        return indicators_data, signals, result
        
    except Exception as e:
        print(f"运行 {strategy_name} 策略时出错: {e}")
        return None, None, None

def run_pair_trading_example(data1, data2, plot_results=True, **kwargs):
    """
    运行配对交易策略示例
    
    Args:
        data1: 第一只股票数据
        data2: 第二只股票数据
        plot_results: 是否绘制结果
        **kwargs: 策略参数
        
    Returns:
        tuple: (indicators_data, signals, result)
    """
    try:
        print(f"\n=== 运行 PairTrading 策略 ===")
        
        # 获取配对交易策略
        strategy = qstrategy.get_strategy('PairTrading', **kwargs)
        
        # 初始化数据（配对交易需要两只股票的数据）
        strategy.init_data(data1, data2)
        
        # 计算指标
        indicators_data = strategy.calculate_indicators()
        
        # 生成信号
        signals = strategy.generate_signals()
        
        # 执行交易
        result = strategy.execute_trade()
        
        # 打印结果摘要
        print(f"策略: PairTrading")
        print(f"交易次数: {result.get('num_trades', 0)}")
        print(f"总利润: {result.get('total_profit', 0):.2f}")
        print(f"最终持仓: {result.get('final_position', 0)}")
        
        # 可视化结果
        if plot_results:
            plt.figure(figsize=(14, 10))
            
            # 绘制两只股票的价格
            plt.subplot(3, 1, 1)
            plt.plot(data1.index, data1['close'], label='股票1')
            plt.plot(data2.index, data2['close'], label='股票2')
            plt.title('配对交易 - 股票价格')
            plt.ylabel('价格')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 绘制价差
            plt.subplot(3, 1, 2)
            if indicators_data is not None and 'spread' in indicators_data:
                plt.plot(indicators_data.index, indicators_data['spread'], label='价差')
                if 'mean_spread' in indicators_data:
                    plt.plot(indicators_data.index, indicators_data['mean_spread'], '--', label='平均价差')
            plt.title('配对交易 - 价差')
            plt.ylabel('价差')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 绘制Z-score
            plt.subplot(3, 1, 3)
            if indicators_data is not None and 'zscore' in indicators_data:
                plt.plot(indicators_data.index, indicators_data['zscore'], label='Z-score')
                plt.axhline(y=2, color='r', linestyle='--', alpha=0.3)
                plt.axhline(y=1, color='r', linestyle=':', alpha=0.3)
                plt.axhline(y=-1, color='g', linestyle=':', alpha=0.3)
                plt.axhline(y=-2, color='g', linestyle='--', alpha=0.3)
            plt.title('配对交易 - Z-score')
            plt.xlabel('日期')
            plt.ylabel('Z-score')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
        
        return indicators_data, signals, result
        
    except Exception as e:
        print(f"运行 PairTrading 策略时出错: {e}")
        return None, None, None

def main():
    """
    主函数，运行所有策略示例
    """
    print("===== QStrategy 策略示例 =====")
    
    # 生成样本数据
    print("生成样本股票数据...")
    stock_data = generate_sample_stock_data()
    
    # 生成配对交易数据
    print("生成配对交易样本数据...")
    stock1_data, stock2_data = generate_pair_stock_data()
    
    # 运行 SMA交叉策略
    run_strategy_example('sma_cross', stock_data, ma_short=5, ma_long=20)
    
    # 运行 MACD策略
    run_strategy_example('macd', stock_data, fastperiod=12, slowperiod=26, signalperiod=9)
    
    # 运行 RSI策略
    run_strategy_example('rsi', stock_data, period=14, overbought=70, oversold=30)
    
    # 运行 布林带策略
    run_strategy_example('bbands', stock_data, period=20, nbdevup=2, nbdevdn=2)
    
    # 运行 均值回归策略
    run_strategy_example('mean_reversion', stock_data, lookback_period=20, std_dev_threshold=2)
    
    # 运行 海龟交易策略
    run_strategy_example('turtle', stock_data, entry_period=20, exit_period=10, risk_percent=1)
    
    # 运行 配对交易策略
    run_pair_trading_example(stock1_data, stock2_data, lookback_period=30, zscore_threshold=2)
    
    print("\n===== 所有策略示例运行完成 =====")


if __name__ == '__main__':
    main()