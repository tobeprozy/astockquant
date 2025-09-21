"""
MACD策略实现
"""

import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, Any
from types import SimpleNamespace

import qindicator
from qstrategy.core.strategy import Strategy

class MACDStrategy(Strategy):
    """
    MACD策略实现
    当MACD线从下向上穿过信号线时买入，当MACD线从上向下穿过信号线时卖出
    """
    
    params = {
        'fast_period': 12,      # 快线周期
        'slow_period': 26,      # 慢线周期
        'signal_period': 9,     # 信号线周期
        'printlog': False,      # 是否打印日志
        'size': 100             # 交易数量（股）
    }
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
        """
        super().__init__()
        
        # 创建可通过点表示法访问的参数对象
        self._params_ns = SimpleNamespace(**self.params)
        
        # 更新参数
        for key, value in kwargs.items():
            if key in self.params:
                setattr(self._params_ns, key, value)
        
        self.macd = None
        self.signal = None
        self.hist = None
        self.signals = None
    
    def init_strategy(self, data: pd.DataFrame, **kwargs):
        """
        初始化策略数据和指标
        
        Args:
            data: 用于策略的数据
            **kwargs: 其他参数
        """
        self.init_data(data)
        
        # 直接使用qindicator计算MACD指标
        # qindicator的calculate_macd需要完整的DataFrame
        # 确保DataFrame包含'open', 'high', 'low', 'close', 'volume'列
        # 为了兼容，我们创建一个包含必要列的DataFrame
        macd_df = qindicator.calculate_macd(
            pd.DataFrame({'close': data['close']}),
            fastperiod=self._params_ns.fast_period,
            slowperiod=self._params_ns.slow_period,
            signalperiod=self._params_ns.signal_period
        )
        
        self.macd = macd_df['MACD']
        self.signal = macd_df['MACD_SIGNAL']
        self.hist = macd_df['MACD_HIST']
        
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
            macd = self.macd
            signal = self.signal
            hist = self.hist
        else:
            # 直接使用qindicator计算MACD指标
            macd_df = qindicator.calculate_macd(
                pd.DataFrame({'close': data['close']}),
                fastperiod=self._params_ns.fast_period,
                slowperiod=self._params_ns.slow_period,
                signalperiod=self._params_ns.signal_period
            )
            macd = macd_df['MACD']
            signal = macd_df['MACD_SIGNAL']
            hist = macd_df['MACD_HIST']
        
        # 创建信号DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['close']
        signals['macd'] = macd
        signals['signal'] = signal
        signals['hist'] = hist
        
        # 计算交叉信号
        # 当MACD线从下向上穿过信号线时买入
        signals['buy_signal'] = ((signals['macd'] > signals['signal']) & 
                               (signals['macd'].shift(1) <= signals['signal'].shift(1)))
        
        # 当MACD线从上向下穿过信号线时卖出
        signals['sell_signal'] = ((signals['macd'] < signals['signal']) & 
                                (signals['macd'].shift(1) >= signals['signal'].shift(1)))
        
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
                'reason': 'MACD金叉信号：MACD线上穿信号线'
            })
            if self._params_ns.printlog:
                self.log(f'买入信号: {buy_date}, 价格: {price:.2f}')
        
        for sell_date in signals['sell_signals']:
            price = self.data.loc[sell_date, 'close']
            transactions.append({
                'date': sell_date,
                'type': 'sell',
                'price': price,
                'reason': 'MACD死叉信号：MACD线下穿信号线'
            })
            if self._params_ns.printlog:
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
        class BacktraderMACD(bt.Strategy):
            params = (
                ('fast_period', self._params_ns.fast_period),
                ('slow_period', self._params_ns.slow_period),
                ('signal_period', self._params_ns.signal_period),
                ('printlog', self._params_ns.printlog),
                ('size', self._params_ns.size)  # 使用外部传入的交易数量参数
            )

            def __init__(self):
                self.macd = bt.indicators.MACD(
                    self.data.close,
                    period_me1=self.params.fast_period,
                    period_me2=self.params.slow_period,
                    period_signal=self.params.signal_period
                )
                
                # 交叉信号
                self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

            def next(self):
                # 计算所需资金
                order_value = self.data.close[0] * self.params.size
                
                # 金叉信号 - 支持连续买入，但检查资金是否足够
                if self.crossover > 0:
                    # 检查可用资金是否足够买入指定数量的股票
                    if self.broker.getcash() >= order_value:
                        self.buy(size=self.params.size)
                        if self.params.printlog:
                            self.log(f'买入: 价格={self.data.close[0]:.2f}, 数量={self.params.size}')
                    else:
                        if self.params.printlog:
                            self.log(f'资金不足: 需要{order_value:.2f}, 可用{self.broker.getcash():.2f}')
                
                # 死叉信号 - 支持连续卖出，但不超过当前持仓量
                elif self.crossover < 0:
                    # 计算可以卖出的数量（不超过当前持仓量）
                    sell_size = min(self.params.size, self.position.size if self.position else 0)
                    if sell_size > 0:
                        self.sell(size=sell_size)
                        if self.params.printlog:
                            self.log(f'卖出: 价格={self.data.close[0]:.2f}, 数量={sell_size}')
                              
            def log(self, txt, dt=None):
                """日志函数，用于记录交易记录，包含持仓金额和剩余金额"""
                dt = dt or self.datas[0].datetime.date(0)
                
                # 计算持仓金额和剩余金额
                remaining_cash = self.broker.getcash()
                
                # 根据交易类型计算持仓金额
                if '买入' in txt:
                    # 买入操作 - 使用买入价格计算持仓金额
                    price = float(txt.split('价格=')[1].split(',')[0])
                    size = int(txt.split('数量=')[1])
                    position_value = price * size
                    remaining_cash = self.broker.getcash()
                elif '卖出' in txt:
                    # 卖出操作 - 使用卖出价格计算持仓金额
                    price = float(txt.split('价格=')[1].split(',')[0])
                    size = int(txt.split('数量=')[1])
                    # 计算卖出后的持仓金额
                    current_position = self.position.size - size if self.position else 0
                    position_value = current_position * price
                    # 计算卖出后的剩余现金
                    remaining_cash = self.broker.getcash() + (price * size)
                else:
                    # 其他情况 - 使用当前价格计算持仓金额
                    position_value = self.position.size * self.data.close[0] if self.position else 0
                
                # 打印带有持仓金额和剩余金额的日志
                print(f'{dt.isoformat()}, {txt}, 持仓金额={position_value:.2f}, 剩余金额={remaining_cash:.2f}')
            
        return BacktraderMACD