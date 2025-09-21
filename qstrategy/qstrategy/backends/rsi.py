#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RSI策略实现
基于相对强弱指标的交易策略
"""

import pandas as pd
from typing import Dict, Any
import logging

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class RSIStrategy(Strategy):
    """
    RSI策略
    当RSI低于超卖阈值时买入，高于超买阈值时卖出
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                timeperiod: RSI计算周期，默认14
                oversold: 超卖阈值，默认30
                overbought: 超买阈值，默认70
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 设置默认参数
        default_params = {
            'timeperiod': 14,
            'oversold': 30,
            'overbought': 70,
            'printlog': False,
            'size': 100
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._rsi = None
        self._indicators_data = None
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算RSI指标
        
        Returns:
            pd.DataFrame: 包含RSI指标的DataFrame
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 确保qindicator已初始化
        try:
            qindicator.init()
        except Exception as e:
            logger.warning(f"初始化qindicator失败，使用已有实例: {e}")
        
        # 获取参数
        timeperiod = self.params.get('timeperiod', 14)
        
        # 计算RSI
        rsi_result = qindicator.calculate_rsi(
            self.data, 
            timeperiod=timeperiod
        )
        
        # 保存结果
        self._indicators_data = rsi_result
        self._rsi = rsi_result['RSI']
        
        return rsi_result
    
    def generate_signals(self) -> Dict[str, Any]:
        """
        生成交易信号
        
        Returns:
            Dict[str, Any]: 包含买入信号和卖出信号的字典
        """
        if self._indicators_data is None:
            # 如果还没有计算指标，先计算
            self.calculate_indicators()
        
        # 获取参数
        oversold = self.params.get('oversold', 30)
        overbought = self.params.get('overbought', 70)
        
        # 生成RSI信号
        signals = {
            'buy_signals': [],  # 买入信号日期列表
            'sell_signals': [],  # 卖出信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找超买超卖点
        for i in range(len(self._rsi)):
            rsi_value = self._rsi.iloc[i]
            date = self._rsi.index[i]
            
            # 检测超卖（买入信号）
            if rsi_value < oversold:
                signals['buy_signals'].append(date)
                signals['all_signals'].append({
                    'date': date,
                    'type': 'buy',
                    'price': self.data['close'].iloc[i],
                    'rsi_value': rsi_value
                })
                if self.params.get('printlog', False):
                    self.log(f"RSI超卖信号: {date}, RSI={rsi_value:.2f}, 价格: {self.data['close'].iloc[i]:.2f}")
            
            # 检测超买（卖出信号）
            elif rsi_value > overbought:
                signals['sell_signals'].append(date)
                signals['all_signals'].append({
                    'date': date,
                    'type': 'sell',
                    'price': self.data['close'].iloc[i],
                    'rsi_value': rsi_value
                })
                if self.params.get('printlog', False):
                    self.log(f"RSI超买信号: {date}, RSI={rsi_value:.2f}, 价格: {self.data['close'].iloc[i]:.2f}")
        
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
                    'rsi_value': signal['rsi_value']
                }
                trades.append(trade)
                if self.params.get('printlog', False):
                    self.log(f"买入: 价格={signal['price']:.2f}, 数量={size}, RSI={signal['rsi_value']:.2f}")
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
                    'rsi_value': signal['rsi_value']
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
register_strategy('rsi', RSIStrategy)