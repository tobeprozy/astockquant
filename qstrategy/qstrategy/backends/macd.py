#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MACD策略实现
基于MACD指标的交易策略
"""

import pandas as pd
from typing import Dict, Any
import logging

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class MACDStrategy(Strategy):
    """
    MACD策略
    当MACD线穿过信号线时产生交易信号
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                fast_period: 快线周期，默认12
                slow_period: 慢线周期，默认26
                signal_period: 信号线周期，默认9
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 设置默认参数
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'printlog': False,
            'size': 100
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._macd = None
        self._macd_signal = None
        self._macd_hist = None
        self._indicators_data = None
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算MACD指标
        
        Returns:
            pd.DataFrame: 包含MACD指标的DataFrame
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 获取指标计算器实例
        try:
            calculator = qindicator.get_indicator_calculator('talib')
        except Exception as e:
            logger.error(f"获取指标计算器实例失败: {e}")
            raise ValueError(f"获取指标计算器实例失败: {e}")
        
        # 获取参数
        fast_period = self.params.get('fast_period', 12)
        slow_period = self.params.get('slow_period', 26)
        signal_period = self.params.get('signal_period', 9)
        
        # 计算MACD
        macd_result = calculator.calculate_macd(
            self.data, 
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        
        # 保存结果
        self._indicators_data = macd_result
        self._macd = macd_result['MACD']
        self._macd_signal = macd_result['MACD_SIGNAL']
        self._macd_hist = macd_result['MACD_HIST']
        
        return macd_result
    
    def generate_signals(self) -> Dict[str, Any]:
        """
        生成交易信号
        
        Returns:
            Dict[str, Any]: 包含买入信号和卖出信号的字典
        """
        if self._indicators_data is None:
            # 如果还没有计算指标，先计算
            self.calculate_indicators()
        
        # 生成MACD交叉信号
        signals = {
            'buy_signals': [],  # 买入信号日期列表
            'sell_signals': [],  # 卖出信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找交叉点
        for i in range(1, len(self._macd)):
            # 前一天的状态
            prev_macd_below_signal = self._macd.iloc[i-1] < self._macd_signal.iloc[i-1]
            prev_macd_above_signal = self._macd.iloc[i-1] > self._macd_signal.iloc[i-1]
            
            # 当前状态
            current_macd_below_signal = self._macd.iloc[i] < self._macd_signal.iloc[i]
            current_macd_above_signal = self._macd.iloc[i] > self._macd_signal.iloc[i]
            
            # 检测金叉（买入信号）
            if prev_macd_below_signal and current_macd_above_signal:
                date = self._macd.index[i]
                signals['buy_signals'].append(date)
                signals['all_signals'].append({
                    'date': date,
                    'type': 'buy',
                    'price': self.data['close'].iloc[i],
                    'macd_value': self._macd.iloc[i],
                    'signal_value': self._macd_signal.iloc[i],
                    'hist_value': self._macd_hist.iloc[i]
                })
                if self.params.get('printlog', False):
                    self.log(f"MACD金叉信号: {date}, 价格: {self.data['close'].iloc[i]:.2f}")
            
            # 检测死叉（卖出信号）
            elif prev_macd_above_signal and current_macd_below_signal:
                date = self._macd.index[i]
                signals['sell_signals'].append(date)
                signals['all_signals'].append({
                    'date': date,
                    'type': 'sell',
                    'price': self.data['close'].iloc[i],
                    'macd_value': self._macd.iloc[i],
                    'signal_value': self._macd_signal.iloc[i],
                    'hist_value': self._macd_hist.iloc[i]
                })
                if self.params.get('printlog', False):
                    self.log(f"MACD死叉信号: {date}, 价格: {self.data['close'].iloc[i]:.2f}")
        
        # 保存信号
        self._signals = signals
        
        return signals
    
    def execute_trade(self) -> Dict[str, Any]:
        """
        执行交易
        
        Returns:
            Dict[str, Any]: 交易执行结果
        """
        if self._signals is None:
            # 如果还没有生成信号，先生成
            self.generate_signals()
        
        # 获取参数
        size = self.params.get('size', 100)
        
        # 执行交易逻辑
        trades = []
        position = 0  # 当前持仓
        
        # 按照日期排序所有信号
        all_signals_sorted = sorted(self._signals['all_signals'], key=lambda x: x['date'])
        
        for signal in all_signals_sorted:
            if signal['type'] == 'buy' and position == 0:
                # 买入
                position = size
                trade = {
                    'date': signal['date'],
                    'type': 'buy',
                    'price': signal['price'],
                    'size': size,
                    'cost': signal['price'] * size,
                    'position': position,
                    'macd_value': signal['macd_value'],
                    'signal_value': signal['signal_value']
                }
                trades.append(trade)
                if self.params.get('printlog', False):
                    self.log(f"买入: 价格={signal['price']:.2f}, 数量={size}")
            elif signal['type'] == 'sell' and position > 0:
                # 卖出
                profit = (signal['price'] - trades[-1]['price']) * size if trades else 0
                profit_percent = (profit / (trades[-1]['price'] * size) * 100) if trades else 0
                
                trade = {
                    'date': signal['date'],
                    'type': 'sell',
                    'price': signal['price'],
                    'size': size,
                    'revenue': signal['price'] * size,
                    'profit': profit,
                    'profit_percent': profit_percent,
                    'position': 0,
                    'macd_value': signal['macd_value'],
                    'signal_value': signal['signal_value']
                }
                trades.append(trade)
                position = 0
                if self.params.get('printlog', False):
                    self.log(f"卖出: 价格={signal['price']:.2f}, 数量={size}, 利润={profit:.2f} ({profit_percent:.2f}%)")
        
        # 计算总收益
        total_profit = sum(trade['profit'] for trade in trades if trade['type'] == 'sell')
        
        result = {
            'trades': trades,
            'total_profit': total_profit,
            'num_trades': len(trades),
            'final_position': position
        }
        
        if self.params.get('printlog', False):
            self.log(f"交易结果: 总利润={total_profit:.2f}, 交易次数={len(trades)}")
        
        return result


# 注册策略
register_strategy('macd', MACDStrategy)