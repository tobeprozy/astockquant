"""
波动率突破策略实现
当价格突破近期波动率上限时买入，当价格跌破近期波动率下限时卖出
"""

import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, Any
from types import SimpleNamespace

import qindicator
from qstrategy.strategy import StrategyBase

class VolatilityBreakoutStrategy(StrategyBase):
    """
    波动率突破策略实现
    当价格突破近期波动率上限时买入，当价格跌破近期波动率下限时卖出
    """
    
    params = {
        'window': 20,          # 计算波动率的窗口
        'multiplier': 2.0,     # 波动率乘数
        'printlog': False,     # 是否打印日志
        'size': 100            # 交易数量（股）
    }
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
        """
        super().__init__()
        
        # 创建可通过点表示法访问的参数对象
        self._params = SimpleNamespace(**self.params)
        
        # 更新参数
        for key, value in kwargs.items():
            if key in self.params:
                setattr(self._params, key, value)
        
        self.volatility = None
        self.upper_band = None
        self.lower_band = None
        self.data = None
        self.signals = None
        
    def init_strategy(self, data: pd.DataFrame, **kwargs):
        """
        初始化策略数据和指标
        
        Args:
            data: 用于策略的数据
            **kwargs: 其他参数
        """
        self.data = data.copy()
        
        # 计算波动率（使用收盘价的标准差）
        self.volatility = self.data['close'].rolling(window=self._params.window).std()
        
        # 计算上下轨
        self.upper_band = self.data['close'] + self._params.multiplier * self.volatility
        self.lower_band = self.data['close'] - self._params.multiplier * self.volatility
        
        # 生成交易信号
        self.signals = self.generate_signals()
    
    def generate_signals(self, data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: 用于生成信号的数据，如果为None则使用初始化数据
            
        Returns:
            包含交易信号的字典
        """
        if data is None:
            data = self.data
            upper_band = self.upper_band
            lower_band = self.lower_band
        else:
            # 计算波动率
            volatility = data['close'].rolling(window=self._params.window).std()
            
            # 计算上下轨
            upper_band = data['close'] + self._params.multiplier * volatility
            lower_band = data['close'] - self._params.multiplier * volatility
        
        # 创建信号DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['close']
        signals['upper_band'] = upper_band
        signals['lower_band'] = lower_band
        
        # 当价格突破上轨时买入
        signals['buy_signal'] = (signals['price'].shift(1) < signals['upper_band'].shift(1)) & (signals['price'] > signals['upper_band'])
        # 当价格跌破下轨时卖出
        signals['sell_signal'] = (signals['price'].shift(1) > signals['lower_band'].shift(1)) & (signals['price'] < signals['lower_band'])
        
        return {
            'signals': signals,
            'buy_signals': signals[signals['buy_signal']].index,
            'sell_signals': signals[signals['sell_signal']].index
        }
        
    def execute_trade(self, signals: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行交易
        
        Args:
            signals: 交易信号，如果为None则使用生成的信号
            
        Returns:
            交易执行结果
        """
        if signals is None:
            signals = self.signals
        
        # 在实际应用中，这里会根据信号执行实际的交易
        # 这里我们只记录交易日志
        
        transactions = []
        
        for buy_date in signals['buy_signals']:
            price = self.data.loc[buy_date, 'close']
            transactions.append({
                'date': buy_date,
                'type': 'buy',
                'price': price,
                'reason': '价格突破波动率上轨'
            })
            if self._params.printlog:
                self.log(f'买入信号: {buy_date}, 价格: {price:.2f}')
        
        for sell_date in signals['sell_signals']:
            price = self.data.loc[sell_date, 'close']
            transactions.append({
                'date': sell_date,
                'type': 'sell',
                'price': price,
                'reason': '价格跌破波动率下轨'
            })
            if self._params.printlog:
                self.log(f'卖出信号: {sell_date}, 价格: {price:.2f}')
        
        return {
            'transactions': transactions,
            'total_buys': len(signals['buy_signals']),
            'total_sells': len(signals['sell_signals'])
        }
        
    def get_backtrader_strategy(self) -> type:
        """
        获取对应的backtrader策略类
        
        Returns:
            backtrader策略类
        """
        # 定义内部的backtrader策略类
        class BacktraderVolatilityBreakout(bt.Strategy):
            params = (
                ('window', self._params.window),
                ('multiplier', self._params.multiplier),
                ('printlog', self._params.printlog),
                ('size', self._params.size),  # 交易数量
            )
            
            def __init__(self):
                self.volatility = bt.indicators.StandardDeviation(
                    self.data.close, period=self.params.window
                )
                
                self.upper_band = self.data.close + self.params.multiplier * self.volatility
                self.lower_band = self.data.close - self.params.multiplier * self.volatility
                
            def next(self):
                # 检查是否已经持仓
                if not self.position:
                    # 价格突破上轨，买入
                    if self.data.close[0] > self.upper_band[0] and self.data.close[-1] <= self.upper_band[-1]:
                        # 计算所需资金
                        order_value = self.data.close[0] * self.params.size
                        # 检查可用资金是否足够买入指定数量的股票
                        if self.broker.getcash() >= order_value:
                            self.buy(size=self.params.size)
                            if self.params.printlog:
                                self.log(f'买入: 价格={self.data.close[0]:.2f}, 数量={self.params.size}')
                        else:
                            if self.params.printlog:
                                self.log(f'资金不足: 需要{order_value:.2f}, 可用{self.broker.getcash():.2f}')
                else:
                    # 价格跌破下轨，卖出
                    if self.data.close[0] < self.lower_band[0] and self.data.close[-1] >= self.lower_band[-1]:
                        self.sell(size=self.params.size)
                        if self.params.printlog:
                            self.log(f'卖出: 价格={self.data.close[0]:.2f}, 数量={self.params.size}')
                            
            def log(self, txt, dt=None):
                """日志函数，用于记录交易记录"""
                dt = dt or self.datas[0].datetime.date(0)
                # 计算持仓金额和剩余金额
                # 对于买入操作，计算买入后的持仓金额和剩余金额
                if '买入' in txt:
                    # 计算买入后的持仓数量
                    new_position_size = self.position.size + self.params.size
                    new_position_value = new_position_size * self.data.close[0]
                    new_remaining_cash = self.broker.getcash() - self.data.close[0] * self.params.size
                    print(f'{dt.isoformat()}, {txt}, 持仓金额={new_position_value:.2f}, 剩余金额={new_remaining_cash:.2f}')
                # 对于卖出操作，计算卖出后的持仓金额和剩余金额
                elif '卖出' in txt:
                    # 计算卖出后的持仓数量
                    sell_size = min(self.params.size, self.position.size if self.position else 0)
                    new_position_size = self.position.size - sell_size
                    new_position_value = new_position_size * self.data.close[0]
                    new_remaining_cash = self.broker.getcash() + self.data.close[0] * sell_size
                    print(f'{dt.isoformat()}, {txt}, 持仓金额={new_position_value:.2f}, 剩余金额={new_remaining_cash:.2f}')
                else:
                    # 其他情况，使用当前值
                    position_value = 0
                    if self.position:
                        position_value = self.position.size * self.data.close[0]
                    remaining_cash = self.broker.getcash()
                    print(f'{dt.isoformat()}, {txt}, 持仓金额={position_value:.2f}, 剩余金额={remaining_cash:.2f}')
        
        return BacktraderVolatilityBreakout