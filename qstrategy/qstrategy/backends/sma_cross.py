#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
移动平均线交叉策略实现
当短期均线向上穿过长期均线时买入，当短期均线向下穿过长期均线时卖出
"""

import pandas as pd
from typing import Dict, Any
import logging

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class SMACrossStrategy(Strategy):
    """
    移动平均线交叉策略
    当短期均线向上穿过长期均线时买入，当短期均线向下穿过长期均线时卖出
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                fast_period: 短期均线周期，默认10
                slow_period: 长期均线周期，默认30
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 设置默认参数
        default_params = {
            'fast_period': 10,
            'slow_period': 30,
            'printlog': False,
            'size': 100
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._fast_ma = None
        self._slow_ma = None
        self._indicators_data = None
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算移动平均线指标
        
        Returns:
            pd.DataFrame: 包含移动平均线的DataFrame
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 获取参数
        fast_period = self.params.get('fast_period', 10)
        slow_period = self.params.get('slow_period', 30)
        
        # 获取指标计算器实例
        try:
            indicator_calculator = qindicator.get_indicator_calculator("talib")
            if indicator_calculator is None:
                raise ValueError("获取指标计算器失败")
        except Exception as e:
            logger.error(f"获取指标计算器失败: {e}")
            raise
        
        # 创建一个包含close列的DataFrame
        close_df = pd.DataFrame({'close': self.data['close']})
        
        # 计算快速移动平均线
        try:
            fast_ma_result = indicator_calculator.calculate_ma(
                close_df, 
                timeperiod=fast_period
            )
        except Exception as e:
            logger.error(f"计算快速移动平均线失败: {e}")
            raise
        
        # 计算慢速移动平均线
        try:
            slow_ma_result = indicator_calculator.calculate_ma(
                close_df, 
                timeperiod=slow_period
            )
        except Exception as e:
            logger.error(f"计算慢速移动平均线失败: {e}")
            raise
        
        # 合并结果
        indicators_data = pd.DataFrame({
            f'MA{fast_period}': fast_ma_result[f'MA{fast_period}'],
            f'MA{slow_period}': slow_ma_result[f'MA{slow_period}'],
            'close': self.data['close']
        })
        
        # 保存结果
        self._indicators_data = indicators_data
        self._fast_ma = indicators_data[f'MA{fast_period}']
        self._slow_ma = indicators_data[f'MA{slow_period}']
        
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
        fast_period = self.params.get('fast_period', 10)
        slow_period = self.params.get('slow_period', 30)
        
        # 生成金叉和死叉信号
        # 金叉：短期均线上穿长期均线
        # 死叉：短期均线下穿长期均线
        signals = {
            'buy_signals': [],  # 买入信号日期列表
            'sell_signals': [],  # 卖出信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找交叉点
        for i in range(1, len(self._fast_ma)):
            # 前一天的状态
            prev_fast_below_slow = self._fast_ma.iloc[i-1] < self._slow_ma.iloc[i-1]
            prev_fast_above_slow = self._fast_ma.iloc[i-1] > self._slow_ma.iloc[i-1]
            
            # 当前状态
            current_fast_below_slow = self._fast_ma.iloc[i] < self._slow_ma.iloc[i]
            current_fast_above_slow = self._fast_ma.iloc[i] > self._slow_ma.iloc[i]
            
            # 检测金叉（买入信号）
            if prev_fast_below_slow and current_fast_above_slow:
                date = self._fast_ma.index[i]
                signals['buy_signals'].append(date)
                signals['all_signals'].append({
                    'date': date,
                    'type': 'buy',
                    'price': self.data['close'].iloc[i]
                })
                if self.params.get('printlog', False):
                    self.log(f"金叉信号: {date}, 价格: {self.data['close'].iloc[i]:.2f}")
            
            # 检测死叉（卖出信号）
            elif prev_fast_above_slow and current_fast_below_slow:
                date = self._fast_ma.index[i]
                signals['sell_signals'].append(date)
                signals['all_signals'].append({
                    'date': date,
                    'type': 'sell',
                    'price': self.data['close'].iloc[i]
                })
                if self.params.get('printlog', False):
                    self.log(f"死叉信号: {date}, 价格: {self.data['close'].iloc[i]:.2f}")
        
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
        # 这里是简化的交易执行逻辑，实际应用中可能需要与交易接口对接
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
                    'position': position
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
                    'position': 0
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
register_strategy('sma_cross', SMACrossStrategy)