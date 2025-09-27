#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
移动平均线交叉策略实现
当短期均线向上穿过长期均线时买入，当短期均线向下穿过长期均线时卖出
"""

import pandas as pd
from typing import Dict, Any
import logging
import backtrader as bt

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class SMACrossStrategy(Strategy):
    """
    移动平均线交叉策略
    当短期均线向上穿过长期均线时买入，当短期均线向下穿过长期均线时卖出
    """
    
    # 直接在类级别定义默认参数
    default_params = {
        'fast_period': 10,
        'slow_period': 30,
        'printlog': False,
        'size': 100
    }
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
        """
        # 合并用户参数和默认参数
        params = self.default_params.copy()
        params.update(kwargs)
        
        super().__init__(**params)
        
        # 初始化指标
        self._fast_ma = None
        self._slow_ma = None
        self._indicators_data = None
    
    def get_backtrader_strategy(self):
        """
        获取兼容backtrader的策略类
        使策略能在BacktraderEngine中运行
        """
        # 定义backtrader策略类
        class BacktraderSMACrossStrategy(bt.Strategy):
            # 使用类级别默认参数
            params = tuple((k, v) for k, v in SMACrossStrategy.default_params.items())
            
            def __init__(self):
                # 初始化交易状态
                self.order = None
                self.buyprice = None
                self.buycomm = None
                
                # 计算移动平均线
                self.fast_ma = bt.indicators.SimpleMovingAverage(
                    self.data.close, period=self.p.fast_period
                )
                self.slow_ma = bt.indicators.SimpleMovingAverage(
                    self.data.close, period=self.p.slow_period
                )
                
                # 用于判断交叉
                self.crossover = bt.indicators.CrossOver(
                    self.fast_ma, self.slow_ma
                )
            
            def log(self, txt, dt=None):
                """日志函数，用于记录交易执行情况"""
                if self.p.printlog:
                    dt = dt or self.data.datetime.date(0)
                    print(f'{dt.isoformat()}, {txt}')
            
            def notify_order(self, order):
                """订单状态通知"""
                if order.status in [order.Submitted, order.Accepted]:
                    # 订单已提交或已接受，不需要操作
                    return
                
                # 检查订单是否完成
                if order.status in [order.Completed]:
                    if order.isbuy():  # 买入订单
                        self.log(f'买入: 价格={order.executed.price:.2f}, 成本={order.executed.value:.2f}, 佣金={order.executed.comm:.2f}')
                        self.buyprice = order.executed.price
                        self.buycomm = order.executed.comm
                    else:  # 卖出订单
                        self.log(f'卖出: 价格={order.executed.price:.2f}, 收入={order.executed.value:.2f}, 佣金={order.executed.comm:.2f}')
                    # 记录交易执行的价格和佣金
                    
                elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                    self.log('订单: 已取消/保证金不足/被拒绝')
                
                # 重置订单状态
                self.order = None
            
            def notify_trade(self, trade):
                """交易状态通知"""
                if not trade.isclosed:
                    return
                
                self.log(f'交易结果: 毛利润={trade.pnl:.2f}, 净利润={trade.pnlcomm:.2f}')
            
            def next(self):
                """每个时间点的交易逻辑"""
                # 检查是否有未完成的订单
                if self.order:
                    return
                
                # 金叉信号：短期均线上穿长期均线
                if self.crossover > 0 and not self.position:
                    # 买入
                    self.log(f'买入信号: 价格={self.data.close[0]:.2f}')
                    self.order = self.buy(size=self.p.size)
                
                # 死叉信号：短期均线下穿长期均线
                elif self.crossover < 0 and self.position:
                    # 卖出
                    self.log(f'卖出信号: 价格={self.data.close[0]:.2f}')
                    self.order = self.sell(size=self.p.size)
        
        return BacktraderSMACrossStrategy
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算移动平均线指标
        
        Returns:
            pd.DataFrame: 包含移动平均线的DataFrame
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 确保qindicator已初始化
        try:
            qindicator.init()
        except Exception as e:
            logger.warning(f"初始化qindicator失败，使用已有实例: {e}")
        
        # 创建一个包含close列的DataFrame
        close_df = pd.DataFrame({'close': self.data['close']})
        
        # 获取参数
        fast_period = self.params.get('fast_period', 10)
        slow_period = self.params.get('slow_period', 30)
        
        # 计算快速移动平均线
        fast_ma_result = qindicator.calculate_ma(
            close_df, 
            timeperiod=fast_period
        )
        
        # 计算慢速移动平均线
        slow_ma_result = qindicator.calculate_ma(
            close_df, 
            timeperiod=slow_period
        )
        
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