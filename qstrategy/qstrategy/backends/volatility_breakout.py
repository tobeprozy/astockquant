# 修改导入部分
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
import backtrader as bt
from typing import Dict, Any
from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class VolatilityBreakoutStrategy(Strategy):
    """
    波动率突破策略实现
    当价格突破近期波动率上限时买入，当价格跌破近期波动率下限时卖出
    """
    
    # 直接在类级别定义默认参数
    default_params = {
        'window': 20,
        'multiplier': 2.0,
        'printlog': False,
        'size': 100
    }
    
    def __init__(self, **kwargs):
        """
        初始化波动率突破策略
        
        Args:
            window: 计算波动率的窗口，默认20
            multiplier: 波动率乘数，默认2.0
            printlog: 是否打印日志，默认False
            size: 交易数量，默认100
        """
        # 合并用户参数和默认参数
        params = self.default_params.copy()
        params.update(kwargs)
        
        # 调用父类初始化
        super().__init__(**params)
        
        # 初始化指标属性
        self.volatility = None
        self.upper_band = None
        self.lower_band = None
    
    def get_backtrader_strategy(self):
        """
        获取兼容backtrader的策略类
        使策略能在BacktraderEngine中运行
        """
        # 定义backtrader策略类
        class BacktraderVolatilityBreakoutStrategy(bt.Strategy):
            # 使用类级别默认参数
            params = tuple((k, v) for k, v in VolatilityBreakoutStrategy.default_params.items())
            
            def __init__(self):
                # 初始化交易状态
                self.order = None
                self.buyprice = None
                self.buycomm = None
                
                # 计算波动率（使用标准差）
                self.volatility = bt.indicators.StandardDeviation(
                    self.data.close, period=self.p.window
                )
                
                # 计算上下轨
                self.upper_band = self.data.close + self.p.multiplier * self.volatility
                self.lower_band = self.data.close - self.p.multiplier * self.volatility
            
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
                
                # 当价格突破上轨且当前没有持仓时买入
                if self.data.close[0] > self.upper_band[0] and not self.position:
                    self.log(f'买入信号: 价格={self.data.close[0]:.2f}, 上轨={self.upper_band[0]:.2f}')
                    self.order = self.buy(size=self.p.size)
                
                # 当价格跌破下轨且当前有持仓时卖出
                elif self.data.close[0] < self.lower_band[0] and self.position:
                    self.log(f'卖出信号: 价格={self.data.close[0]:.2f}, 下轨={self.lower_band[0]:.2f}')
                    self.order = self.sell(size=self.p.size)
        
        return BacktraderVolatilityBreakoutStrategy
    
    def calculate_indicators(self) -> Dict[str, Any]:
        """
        计算波动率突破策略的指标
        
        Returns:
            包含指标计算结果的字典
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
            
        try:
            # 计算波动率（使用收盘价的标准差）
            self.volatility = self.data['close'].rolling(window=self.params.window).std()
            
            # 计算上下轨
            self.upper_band = self.data['close'] + self.params.multiplier * self.volatility
            self.lower_band = self.data['close'] - self.params.multiplier * self.volatility
            
            return {
                'volatility': self.volatility,
                'upper_band': self.upper_band,
                'lower_band': self.lower_band
            }
        except Exception as e:
            logger.error(f"计算指标失败: {str(e)}")
            raise ValueError(f"计算指标失败: {str(e)}")
    
    def generate_signals(self) -> Dict[str, Any]:
        """
        基于波动率突破生成交易信号
        
        Returns:
            包含交易信号的字典
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
            
        try:
            # 计算指标
            indicators = self.calculate_indicators()
            
            upper_band = indicators['upper_band']
            lower_band = indicators['lower_band']
            
            # 创建信号DataFrame
            signals = pd.DataFrame(index=self.data.index)
            signals['price'] = self.data['close']
            signals['upper_band'] = upper_band
            signals['lower_band'] = lower_band
            
            # 当价格突破上轨时买入
            signals['buy_signal'] = (signals['price'].shift(1) < signals['upper_band'].shift(1)) & \
                                  (signals['price'] > signals['upper_band'])
            # 当价格跌破下轨时卖出
            signals['sell_signal'] = (signals['price'].shift(1) > signals['lower_band'].shift(1)) & \
                                   (signals['price'] < signals['lower_band'])
            
            # 记录买入和卖出信号的日期
            buy_signals = signals[signals['buy_signal']].index
            sell_signals = signals[signals['sell_signal']].index
            
            if self.params.printlog:
                logger.info(f"生成信号: 买入信号{len(buy_signals)}个, 卖出信号{len(sell_signals)}个")
                
            # 保存信号
            self._signals = {
                'signals': signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals
            }
            
            return self._signals
        except Exception as e:
            logger.error(f"生成信号失败: {str(e)}")
            raise ValueError(f"生成信号失败: {str(e)}")
    
    def execute_trade(self) -> Dict[str, Any]:
        """
        执行交易
        
        Returns:
            交易结果
        """
        if self.data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
            
        try:
            # 如果没有生成信号，则先生成
            if self._signals is None:
                self.generate_signals()
                
            transactions = []
            total_profit = 0.0
            position = False
            buy_price = 0.0
            
            # 遍历所有交易日
            for date in self.data.index:
                # 执行买入信号
                if date in self._signals['buy_signals'] and not position:
                    price = self.data.loc[date, 'close']
                    transactions.append({
                        'date': date,
                        'type': 'buy',
                        'price': price,
                        'size': self.params.size,
                        'reason': '价格突破波动率上轨'
                    })
                    position = True
                    buy_price = price
                    
                    if self.params.printlog:
                        logger.info(f"买入信号: {date}, 价格: {price:.2f}")
                
                # 执行卖出信号
                elif date in self._signals['sell_signals'] and position:
                    price = self.data.loc[date, 'close']
                    profit = (price - buy_price) * self.params.size
                    total_profit += profit
                    
                    transactions.append({
                        'date': date,
                        'type': 'sell',
                        'price': price,
                        'size': self.params.size,
                        'profit': profit,
                        'reason': '价格跌破波动率下轨'
                    })
                    position = False
                    
                    if self.params.printlog:
                        logger.info(f"卖出信号: {date}, 价格: {price:.2f}, 利润: {profit:.2f}")
            
            # 返回交易结果
            result = {
                'transactions': transactions,
                'total_buys': len(self._signals['buy_signals']),
                'total_sells': len(self._signals['sell_signals']),
                'total_profit': total_profit,
                'final_position': 'holding' if position else 'cash'
            }
            
            return result
        except Exception as e:
            logger.error(f"执行交易失败: {str(e)}")
            raise ValueError(f"执行交易失败: {str(e)}")

# 注册策略
register_strategy('volatility_breakout', VolatilityBreakoutStrategy)