#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
布林带策略实现
基于布林带指标的交易策略
"""

import pandas as pd
from typing import Dict, Any
import logging
import backtrader as bt  # 添加backtrader导入

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class BBANDSStrategy(Strategy):
    """
    布林带策略
    当价格触及下轨时买入，触及上轨时卖出
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                timeperiod: 计算周期，默认20
                nbdevup: 上轨标准差倍数，默认2
                nbdevdn: 下轨标准差倍数，默认2
                matype: 移动平均类型，默认0（简单移动平均）
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 设置默认参数
        default_params = {
            'timeperiod': 20,
            'nbdevup': 2,
            'nbdevdn': 2,
            'printlog': False,
            'size': 100
        }
        
        # 合并用户参数和默认参数
        default_params.update(kwargs)
        
        super().__init__(**default_params)
        
        # 初始化指标
        self._bb_upper = None
        self._bb_middle = None
        self._bb_lower = None
        self._indicators_data = None
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算布林带指标
        
        Returns:
            pd.DataFrame: 包含布林带指标的DataFrame
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 确保qindicator已初始化
        try:
            qindicator.init()
        except Exception as e:
            logger.warning(f"初始化qindicator失败，使用已有实例: {e}")
        
        # 获取参数
        timeperiod = self.params.get('timeperiod', 20)
        nbdevup = self.params.get('nbdevup', 2)
        nbdevdn = self.params.get('nbdevdn', 2)
        
        # 获取指标计算器实例
        try:
            calculator = qindicator.get_indicator_calculator('talib')
        except Exception as e:
            logger.error(f"获取指标计算器实例失败: {e}")
            raise ValueError(f"获取指标计算器实例失败: {e}")
        
        # 计算布林带
        bbands_result = calculator.calculate_bbands(
            self.data, 
            timeperiod=timeperiod,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn
        )
        
        # 保存结果
        self._indicators_data = bbands_result
        self._bb_upper = bbands_result['BB_UPPER']
        self._bb_middle = bbands_result['BB_MIDDLE']
        self._bb_lower = bbands_result['BB_LOWER']
        
        return bbands_result
    
    def generate_signals(self) -> Dict[str, Any]:
        """
        生成交易信号
        
        Returns:
            Dict[str, Any]: 包含买入信号和卖出信号的字典
        """
        if self._indicators_data is None:
            # 如果还没有计算指标，先计算
            self.calculate_indicators()
        
        # 生成布林带信号
        signals = {
            'buy_signals': [],  # 买入信号日期列表
            'sell_signals': [],  # 卖出信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找上下轨触及点
        for i in range(len(self.data)):
            date = self.data.index[i]
            close_price = self.data['close'].iloc[i]
            
            # 确保布林带值不为NaN
            if pd.notna(self._bb_upper.iloc[i]) and pd.notna(self._bb_lower.iloc[i]):
                # 检测下轨触及（买入信号）
                if close_price <= self._bb_lower.iloc[i]:
                    signals['buy_signals'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'buy',
                        'price': close_price,
                        'bb_upper': self._bb_upper.iloc[i],
                        'bb_middle': self._bb_middle.iloc[i],
                        'bb_lower': self._bb_lower.iloc[i]
                    })
                    if self.params.get('printlog', False):
                        self.log(f"布林带下轨触及信号: {date}, 价格: {close_price:.2f}")
                
                # 检测上轨触及（卖出信号）
                elif close_price >= self._bb_upper.iloc[i]:
                    signals['sell_signals'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'sell',
                        'price': close_price,
                        'bb_upper': self._bb_upper.iloc[i],
                        'bb_middle': self._bb_middle.iloc[i],
                        'bb_lower': self._bb_lower.iloc[i]
                    })
                    if self.params.get('printlog', False):
                        self.log(f"布林带上轨触及信号: {date}, 价格: {close_price:.2f}")
        
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
                    'bb_upper': signal['bb_upper'],
                    'bb_middle': signal['bb_middle'],
                    'bb_lower': signal['bb_lower']
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
                    'bb_upper': signal['bb_upper'],
                    'bb_middle': signal['bb_middle'],
                    'bb_lower': signal['bb_lower']
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
        # 获取当前策略的参数
        params = self.params.copy()
        
        # 定义backtrader策略类
        class BacktraderBBANDSStrategy(bt.Strategy):
            # 设置参数
            params = (
                ('timeperiod', params.get('timeperiod', 20)),
                ('nbdevup', params.get('nbdevup', 2)),
                ('nbdevdn', params.get('nbdevdn', 2)),
                ('printlog', params.get('printlog', False)),
                ('size', params.get('size', 100))
            )
            
            def __init__(self):
                # 初始化布林带指标
                self.bbands = bt.indicators.BollingerBands(
                    self.data.close,
                    period=self.p.timeperiod,
                    devfactor=self.p.nbdevup
                )
                
                # 跟踪交易状态
                self.order = None
                self.buyprice = None
                self.buycomm = None
            
            def log(self, txt, dt=None, doprint=False):
                """日志函数"""
                if self.p.printlog or doprint:
                    dt = dt or self.datas[0].datetime.date(0)
                    print(f'{dt.isoformat()} {txt}')
            
            def notify_order(self, order):
                """订单状态通知"""
                # ... 与MACDJKStrategy中的实现相同 ...
                if order.status in [order.Submitted, order.Accepted]:
                    return
                
                if order.status in [order.Completed]:
                    if order.isbuy():
                        self.log(f'买入: 价格={order.executed.price:.2f}, '
                                f'成本={order.executed.value:.2f}, '
                                f'佣金={order.executed.comm:.2f}')
                        self.buyprice = order.executed.price
                        self.buycomm = order.executed.comm
                    else:  # 卖出
                        self.log(f'卖出: 价格={order.executed.price:.2f}, '
                                f'收入={order.executed.value:.2f}, '
                                f'佣金={order.executed.comm:.2f}')
                    
                    self.bar_executed = len(self)
                    
                elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                    self.log('订单取消/保证金不足/拒绝')
                    
                self.order = None
            
            def notify_trade(self, trade):
                """交易状态通知"""
                # ... 与MACDJKStrategy中的实现相同 ...
                if not trade.isclosed:
                    return
                
                self.log(f'交易利润: 毛利润={trade.pnl:.2f}, 净利润={trade.pnlcomm:.2f}')
            
            def next(self):
                """每个交易周期执行一次"""
                # 检查是否有订单在处理中
                if self.order:
                    return
                
                # 买入信号: 价格触及下轨
                if self.data.close[0] <= self.bbands.lines.bot[0]:
                    self.log(f'买入信号: 价格={self.data.close[0]:.2f}, 下轨={self.bbands.lines.bot[0]:.2f}')
                    if not self.position:
                        self.order = self.buy(size=self.p.size)
                
                # 卖出信号: 价格触及上轨
                elif self.data.close[0] >= self.bbands.lines.top[0]:
                    self.log(f'卖出信号: 价格={self.data.close[0]:.2f}, 上轨={self.bbands.lines.top[0]:.2f}')
                    if self.position:
                        self.order = self.sell(size=self.p.size)
        
        return BacktraderBBANDSStrategy

# 注册策略
register_strategy('bbands', BBANDSStrategy)