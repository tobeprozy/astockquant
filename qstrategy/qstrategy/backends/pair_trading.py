#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配对交易策略实现
基于两只相关性高的股票之间价格差异的交易策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import logging

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class PairTradingStrategy(Strategy):
    """
    配对交易策略
    当两只相关性高的股票之间的价格差异超过阈值时进行交易
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                lookback_period: 回溯期，默认60
                zscore_threshold: Z-score阈值，默认2
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 设置默认参数
        default_params = {
            'lookback_period': 60,
            'zscore_threshold': 2,
            'printlog': False,
            'size': 100
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._stock1_data = None
        self._stock2_data = None
        self._spread = None
        self._zscore = None
        self._indicators_data = None
    
    def init_data(self, data: Dict[str, pd.DataFrame]) -> None:
        """
        初始化策略数据
        
        Args:
            data: 包含两只股票数据的字典，格式为{'stock1': df1, 'stock2': df2}
        
        Raises:
            ValueError: 当数据格式不符合要求时
        """
        # 验证数据格式
        if not isinstance(data, dict) or len(data) != 2:
            raise ValueError("配对交易策略需要两只股票的数据，格式为{'stock1': df1, 'stock2': df2}")
        
        # 提取两只股票的数据
        stock_keys = list(data.keys())
        self._stock1_data = data[stock_keys[0]].copy()
        self._stock2_data = data[stock_keys[1]].copy()
        
        # 验证数据完整性
        self._validate_data(self._stock1_data)
        self._validate_data(self._stock2_data)
        
        # 确保两只股票的日期范围一致
        common_dates = self._stock1_data.index.intersection(self._stock2_data.index)
        self._stock1_data = self._stock1_data.loc[common_dates]
        self._stock2_data = self._stock2_data.loc[common_dates]
        
        # 保存数据
        self._data = data
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算配对交易所需的指标（价差和Z-score）
        
        Returns:
            pd.DataFrame: 包含计算结果的DataFrame
        """
        if self._stock1_data is None or self._stock2_data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 获取参数
        lookback_period = self.params.get('lookback_period', 60)
        
        # 计算两只股票的价格比率
        price_ratio = self._stock1_data['close'] / self._stock2_data['close']
        
        # 计算价差
        spread = self._stock1_data['close'] - self._stock2_data['close']
        
        # 计算Z-score
        zscore = []
        for i in range(len(spread)):
            if i < lookback_period:
                zscore.append(np.nan)
            else:
                mean = spread.iloc[i-lookback_period:i].mean()
                std = spread.iloc[i-lookback_period:i].std()
                if std == 0:
                    zscore.append(0)
                else:
                    zscore.append((spread.iloc[i] - mean) / std)
        
        zscore = pd.Series(zscore, index=spread.index)
        
        # 创建指标DataFrame
        indicators_data = pd.DataFrame({
            'stock1_close': self._stock1_data['close'],
            'stock2_close': self._stock2_data['close'],
            'price_ratio': price_ratio,
            'spread': spread,
            'zscore': zscore
        })
        
        # 保存结果
        self._indicators_data = indicators_data
        self._spread = spread
        self._zscore = zscore
        
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
        zscore_threshold = self.params.get('zscore_threshold', 2)
        
        # 生成配对交易信号
        signals = {
            'buy_stock1_sell_stock2': [],  # 买入股票1卖出股票2的信号日期列表
            'sell_stock1_buy_stock2': [],  # 卖出股票1买入股票2的信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找交易机会
        for i in range(len(self._zscore)):
            zscore_value = self._zscore.iloc[i]
            date = self._zscore.index[i]
            
            # 确保Z-score值不为NaN
            if pd.notna(zscore_value):
                # 当Z-score低于负阈值时，买入股票1卖出股票2
                if zscore_value < -zscore_threshold:
                    signals['buy_stock1_sell_stock2'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'buy_stock1_sell_stock2',
                        'stock1_price': self._stock1_data['close'].iloc[i],
                        'stock2_price': self._stock2_data['close'].iloc[i],
                        'zscore': zscore_value
                    })
                    if self.params.get('printlog', False):
                        self.log(f"买入股票1卖出股票2信号: {date}, Z-score={zscore_value:.2f}")
                
                # 当Z-score高于正阈值时，卖出股票1买入股票2
                elif zscore_value > zscore_threshold:
                    signals['sell_stock1_buy_stock2'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'sell_stock1_buy_stock2',
                        'stock1_price': self._stock1_data['close'].iloc[i],
                        'stock2_price': self._stock2_data['close'].iloc[i],
                        'zscore': zscore_value
                    })
                    if self.params.get('printlog', False):
                        self.log(f"卖出股票1买入股票2信号: {date}, Z-score={zscore_value:.2f}")
        
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
        position = {'stock1': 0, 'stock2': 0}  # 当前持仓
        
        # 按照日期排序所有信号
        all_signals_sorted = sorted(self._signals['all_signals'], key=lambda x: x['date'])
        
        for signal in all_signals_sorted:
            if signal['type'] == 'buy_stock1_sell_stock2' and position['stock1'] == 0 and position['stock2'] == 0:
                # 买入股票1，卖出股票2
                position['stock1'] = size
                position['stock2'] = -size
                
                trade = {
                    'date': signal['date'],
                    'type': 'buy_stock1_sell_stock2',
                    'stock1_price': signal['stock1_price'],
                    'stock2_price': signal['stock2_price'],
                    'size': size,
                    'position': position.copy(),
                    'zscore': signal['zscore']
                }
                trades.append(trade)
                
                if self.params.get('printlog', False):
                    self.log(f"买入股票1卖出股票2: 股票1价格={signal['stock1_price']:.2f}, 股票2价格={signal['stock2_price']:.2f}, 数量={size}")
            elif signal['type'] == 'sell_stock1_buy_stock2' and position['stock1'] != 0 and position['stock2'] != 0:
                # 卖出股票1，买入股票2（平仓）
                # 计算利润
                last_trade = next(t for t in reversed(trades) if t['type'] == 'buy_stock1_sell_stock2')
                profit = (signal['stock1_price'] - last_trade['stock1_price']) * size + \
                        (last_trade['stock2_price'] - signal['stock2_price']) * size
                
                trade = {
                    'date': signal['date'],
                    'type': 'sell_stock1_buy_stock2',
                    'stock1_price': signal['stock1_price'],
                    'stock2_price': signal['stock2_price'],
                    'size': size,
                    'profit': profit,
                    'position': {'stock1': 0, 'stock2': 0},
                    'zscore': signal['zscore']
                }
                trades.append(trade)
                
                # 更新持仓
                position['stock1'] = 0
                position['stock2'] = 0
                
                if self.params.get('printlog', False):
                    self.log(f"卖出股票1买入股票2: 股票1价格={signal['stock1_price']:.2f}, 股票2价格={signal['stock2_price']:.2f}, 数量={size}, 利润={profit:.2f}")
        
        # 计算总收益
        total_profit = sum(trade['profit'] for trade in trades if 'profit' in trade)
        
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
register_strategy('PairTrading', PairTradingStrategy)