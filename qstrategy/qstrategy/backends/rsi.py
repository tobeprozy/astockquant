#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RSI策略实现
基于相对强弱指标的交易策略
"""

import pandas as pd
from typing import Dict, Any
import logging
import backtrader as bt  # 添加backtrader导入

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class RSIStrategy(Strategy):
    """
    RSI策略
    当RSI低于超卖阈值时买入，高于超买阈值时卖出
    """
    
    # 直接在类级别定义默认参数
    default_params = {
        'timeperiod': 14,
        'oversold': 30,
        'overbought': 70,
        'printlog': False,
        'size': 100
    }
    
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
        # 合并用户参数和默认参数
        params = self.default_params.copy()
        params.update(kwargs)
        
        super().__init__(**params)
        
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
        
        # 获取参数
        timeperiod = self.params.get('timeperiod', 14)
        
        # 获取指标计算器实例并计算RSI
        calculator = qindicator.get_indicator_calculator('talib')
        if calculator is None:
            raise ValueError("无法获取指标计算器实例")
        
        rsi_result = calculator.calculate_rsi(
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
        
    def get_backtrader_strategy(self):
        """
        获取兼容backtrader的策略类
        该方法使策略能够在BacktraderEngine中运行
        """
        # 解决参数作用域问题的方法：创建一个封装函数
        def make_backtrader_strategy(params_dict):
            class BacktraderRSIStrategy(bt.Strategy):
                # 设置参数
                params = (
                    ('timeperiod', params_dict.get('timeperiod', 14)),
                    ('oversold', params_dict.get('oversold', 30)),
                    ('overbought', params_dict.get('overbought', 70)),
                    ('printlog', params_dict.get('printlog', False)),
                    ('size', params_dict.get('size', 100))
                )
                
                def __init__(self):
                    # 初始化RSI指标
                    self.rsi = bt.indicators.RSI_SMA(
                        self.data.close, 
                        period=self.p.timeperiod
                    )
                    
                    # 初始化交易状态
                    self.order = None
                    self.buyprice = None
                    self.buycomm = None
                
                def log(self, txt, dt=None, doprint=False):
                    """日志函数，用于记录交易信息"""
                    if self.p.printlog or doprint:
                        dt = dt or self.datas[0].datetime.date(0)
                        print(f'{dt.isoformat()}, {txt}')
                
                def notify_order(self, order):
                    """订单状态变化回调"""
                    if order.status in [order.Submitted, order.Accepted]:
                        # 订单已提交或已接受，无需处理
                        return
                    
                    # 检查订单是否完成
                    if order.status in [order.Completed]:
                        if order.isbuy():  # 买入订单
                            self.log(f'买入执行: 价格={order.executed.price:.2f}, '\
                                    f'成本={order.executed.value:.2f}, 佣金={order.executed.comm:.2f}')
                            self.buyprice = order.executed.price
                            self.buycomm = order.executed.comm
                        else:  # 卖出订单
                            self.log(f'卖出执行: 价格={order.executed.price:.2f}, '\
                                    f'收入={order.executed.value:.2f}, 佣金={order.executed.comm:.2f}')
                    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                        self.log('订单 取消/保证金不足/拒绝')
                    
                    # 重置订单标志
                    self.order = None
                
                def notify_trade(self, trade):
                    """交易状态变化回调"""
                    if not trade.isclosed:
                        return
                    
                    self.log(f'交易利润: 毛利润={trade.pnl:.2f}, 净利润={trade.pnlcomm:.2f}')
                
                def next(self):
                    """每个数据点执行一次的逻辑"""
                    # 检查是否有未完成的订单
                    if self.order:
                        return
                    
                    # 检查是否已持仓
                    if not self.position:
                        # 未持仓，检查买入信号
                        if self.rsi[0] < self.p.oversold:
                            # RSI低于超卖阈值，买入
                            self.log(f'买入信号: RSI={self.rsi[0]:.2f} < {self.p.oversold}')
                            self.order = self.buy(size=self.p.size)
                    else:
                        # 已持仓，检查卖出信号
                        if self.rsi[0] > self.p.overbought:
                            # RSI高于超买阈值，卖出
                            self.log(f'卖出信号: RSI={self.rsi[0]:.2f} > {self.p.overbought}')
                            self.order = self.sell(size=self.p.size)
            
            return BacktraderRSIStrategy
        
        # 使用封装函数创建并返回策略类
        return make_backtrader_strategy(self.params)


# 注册策略
register_strategy('rsi', RSIStrategy)