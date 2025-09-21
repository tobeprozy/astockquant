#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
海龟交易策略实现
基于突破和资金管理的经典交易策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class TurtleStrategy(Strategy):
    """
    海龟交易策略
    基于唐奇安通道突破和固定比例资金管理的交易策略
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                entry_period: 入场突破周期，默认20
                exit_period: 出场突破周期，默认10
                risk_percent: 单笔交易风险百分比，默认1
                printlog: 是否打印日志，默认False
                position_size_multiplier: 头寸规模乘数，默认2
        """
        # 设置默认参数
        default_params = {
            'entry_period': 20,
            'exit_period': 10,
            'risk_percent': 1,
            'printlog': False,
            'position_size_multiplier': 2
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._upper_band = None  # 上突破通道
        self._lower_band = None  # 下突破通道
        self._exit_upper_band = None  # 出场上通道
        self._exit_lower_band = None  # 出场下通道
        self._atr = None  # 平均真实波动幅度
        self._indicators_data = None
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算海龟交易策略所需的指标
        
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
        entry_period = self.params.get('entry_period', 20)
        exit_period = self.params.get('exit_period', 10)
        
        # 计算唐奇安通道（入场通道）
        upper_band = self.data['high'].rolling(window=entry_period).max()
        lower_band = self.data['low'].rolling(window=entry_period).min()
        
        # 计算出场通道
        exit_upper_band = self.data['high'].rolling(window=exit_period).max()
        exit_lower_band = self.data['low'].rolling(window=exit_period).min()
        
        # 计算ATR指标
        high = self.data['high']
        low = self.data['low']
        close = self.data['close']
        
        # 计算真实波动幅度
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
        
        # 计算ATR
        atr = tr.rolling(window=14).mean()
        
        # 创建指标DataFrame
        indicators_data = pd.DataFrame({
            'close': self.data['close'],
            'upper_band': upper_band,
            'lower_band': lower_band,
            'exit_upper_band': exit_upper_band,
            'exit_lower_band': exit_lower_band,
            'atr': atr
        })
        
        # 保存结果
        self._indicators_data = indicators_data
        self._upper_band = upper_band
        self._lower_band = lower_band
        self._exit_upper_band = exit_upper_band
        self._exit_lower_band = exit_lower_band
        self._atr = atr
        
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
        
        # 生成海龟交易信号
        signals = {
            'buy_signals': [],  # 买入信号日期列表
            'sell_signals': [],  # 卖出信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找交易机会
        for i in range(len(self.data)):
            date = self.data.index[i]
            close_price = self.data['close'].iloc[i]
            
            # 确保指标值不为NaN
            if (pd.notna(self._upper_band.iloc[i]) and 
                pd.notna(self._lower_band.iloc[i]) and 
                pd.notna(self._exit_upper_band.iloc[i]) and 
                pd.notna(self._exit_lower_band.iloc[i])):
                
                # 上突破买入信号
                if close_price > self._upper_band.iloc[i]:
                    signals['buy_signals'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'buy',
                        'price': close_price
                    })
                    if self.params.get('printlog', False):
                        self.log(f"海龟买入信号: {date}, 价格: {close_price:.2f}")
                
                # 下突破卖出信号
                elif close_price < self._lower_band.iloc[i]:
                    signals['sell_signals'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'sell',
                        'price': close_price
                    })
                    if self.params.get('printlog', False):
                        self.log(f"海龟卖出信号: {date}, 价格: {close_price:.2f}")
        
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
        risk_percent = self.params.get('risk_percent', 1) / 100
        position_size_multiplier = self.params.get('position_size_multiplier', 2)
        
        # 执行交易逻辑
        trades = []
        position = 0  # 当前持仓
        portfolio_value = 100000  # 假设初始资金为10万元
        
        # 按照日期排序所有信号
        all_signals_sorted = sorted(self._signals['all_signals'], key=lambda x: x['date'])
        
        for signal in all_signals_sorted:
            date_idx = self.data.index.get_loc(signal['date'])
            
            if date_idx >= 14:  # 确保ATR数据可用
                atr_value = self._atr.iloc[date_idx]
                
                if atr_value > 0:
                    # 计算头寸规模（根据海龟交易法则的资金管理规则）
                    account_risk = portfolio_value * risk_percent
                    dollar_per_point = account_risk / 2  # 假设2倍ATR作为止损位
                    position_size = int((dollar_per_point / atr_value) * position_size_multiplier)
                    
                    if position_size < 1:
                        position_size = 1  # 最小交易单位
                    
                    if signal['type'] == 'buy' and position <= 0:
                        # 买入
                        position = position_size
                        cost = signal['price'] * position_size
                        
                        trade = {
                            'date': signal['date'],
                            'type': 'buy',
                            'price': signal['price'],
                            'size': position_size,
                            'cost': cost,
                            'position': position,
                            'atr': atr_value,
                            'stop_loss': signal['price'] - (2 * atr_value)  # 2倍ATR作为止损
                        }
                        trades.append(trade)
                        
                        if self.params.get('printlog', False):
                            self.log(f"买入: 价格={signal['price']:.2f}, 数量={position_size}, ATR={atr_value:.2f}")
                            self.log(f"    止损价={trade['stop_loss']:.2f}, 成本={cost:.2f}")
                    elif signal['type'] == 'sell' and position > 0:
                        # 卖出
                        revenue = signal['price'] * position_size
                        profit = revenue - cost
                        profit_percent = (profit / cost) * 100
                        
                        trade = {
                            'date': signal['date'],
                            'type': 'sell',
                            'price': signal['price'],
                            'size': position_size,
                            'revenue': revenue,
                            'profit': profit,
                            'profit_percent': profit_percent,
                            'position': 0,
                            'atr': atr_value
                        }
                        trades.append(trade)
                        position = 0
                        
                        # 更新组合价值
                        portfolio_value += profit
                        
                        if self.params.get('printlog', False):
                            self.log(f"卖出: 价格={signal['price']:.2f}, 数量={position_size}")
                            self.log(f"    收入={revenue:.2f}, 利润={profit:.2f} ({profit_percent:.2f}%)")
                            self.log(f"    组合价值={portfolio_value:.2f}")
        
        # 计算总收益
        total_profit = sum(trade['profit'] for trade in trades if trade['type'] == 'sell')
        
        result = {
            'trades': trades,
            'total_profit': total_profit,
            'num_trades': len(trades),
            'final_position': position,
            'final_portfolio_value': portfolio_value
        }
        
        if self.params.get('printlog', False):
            self.log(f"交易结果: 总利润={total_profit:.2f}, 交易次数={len(trades)}, 最终组合价值={portfolio_value:.2f}")
        
        return result


# 注册策略
register_strategy('turtle', TurtleStrategy)