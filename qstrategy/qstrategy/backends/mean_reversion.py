#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
均值回归策略实现
基于价格围绕均值波动的交易策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class MeanReversionStrategy(Strategy):
    """
    均值回归策略
    当价格偏离均值超过一定阈值时，预期价格会回归均值，从而产生交易信号
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                lookback_period: 回溯期，默认20
                std_dev_threshold: 标准差阈值，默认2
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 设置默认参数
        default_params = {
            'lookback_period': 20,
            'std_dev_threshold': 2,
            'printlog': False,
            'size': 100
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._rolling_mean = None
        self._rolling_std = None
        self._zscore = None
        self._upper_band = None
        self._lower_band = None
        self._indicators_data = None
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算均值回归所需的指标
        
        Returns:
            pd.DataFrame: 包含计算结果的DataFrame
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 确保qindicator已初始化
        try:
            qindicator.init()
        except Exception as e:
            logger.warning(f"初始化qindicator失败，使用已有实例: {e}")
        
        # 获取参数
        lookback_period = self.params.get('lookback_period', 20)
        std_dev_threshold = self.params.get('std_dev_threshold', 2)
        
        # 计算滚动均值和标准差
        rolling_mean = self.data['close'].rolling(window=lookback_period).mean()
        rolling_std = self.data['close'].rolling(window=lookback_period).std()
        
        # 计算Z-score
        zscore = (self.data['close'] - rolling_mean) / rolling_std
        
        # 计算上下边界
        upper_band = rolling_mean + (rolling_std * std_dev_threshold)
        lower_band = rolling_mean - (rolling_std * std_dev_threshold)
        
        # 创建指标DataFrame
        indicators_data = pd.DataFrame({
            'close': self.data['close'],
            'rolling_mean': rolling_mean,
            'rolling_std': rolling_std,
            'zscore': zscore,
            'upper_band': upper_band,
            'lower_band': lower_band
        })
        
        # 保存结果
        self._indicators_data = indicators_data
        self._rolling_mean = rolling_mean
        self._rolling_std = rolling_std
        self._zscore = zscore
        self._upper_band = upper_band
        self._lower_band = lower_band
        
        return indicators_data
    
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
        std_dev_threshold = self.params.get('std_dev_threshold', 2)
        
        # 生成均值回归信号
        signals = {
            'buy_signals': [],  # 买入信号日期列表
            'sell_signals': [],  # 卖出信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找交易机会
        for i in range(len(self._zscore)):
            zscore_value = self._zscore.iloc[i]
            date = self._zscore.index[i]
            close_price = self.data['close'].iloc[i]
            
            # 确保Z-score值不为NaN
            if pd.notna(zscore_value):
                # 当Z-score低于负阈值时，买入（预期价格会回归均值）
                if zscore_value < -std_dev_threshold:
                    signals['buy_signals'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'buy',
                        'price': close_price,
                        'zscore': zscore_value
                    })
                    if self.params.get('printlog', False):
                        self.log(f"均值回归买入信号: {date}, Z-score={zscore_value:.2f}, 价格: {close_price:.2f}")
                
                # 当Z-score高于正阈值时，卖出（预期价格会回归均值）
                elif zscore_value > std_dev_threshold:
                    signals['sell_signals'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'sell',
                        'price': close_price,
                        'zscore': zscore_value
                    })
                    if self.params.get('printlog', False):
                        self.log(f"均值回归卖出信号: {date}, Z-score={zscore_value:.2f}, 价格: {close_price:.2f}")
        
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
                    'zscore': signal['zscore']
                }
                trades.append(trade)
                if self.params.get('printlog', False):
                    self.log(f"买入: 价格={signal['price']:.2f}, 数量={size}, Z-score={signal['zscore']:.2f}")
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
                    'zscore': signal['zscore']
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
register_strategy('mean_reversion', MeanReversionStrategy)