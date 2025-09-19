"""
MACD+KDJ战法策略实现
结合MACD和KDJ指标生成交易信号
"""

import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, Any
from types import SimpleNamespace

import qindicator
from qstrategy.strategy import StrategyBase

class MACDKDJStrategy(StrategyBase):
    """
    MACD+KDJ战法策略实现
    结合MACD和KDJ指标生成交易信号
    """
    
    params = {
        'macd_fast_period': 12,    # MACD快线周期
        'macd_slow_period': 26,    # MACD慢线周期
        'macd_signal_period': 9,   # MACD信号线周期
        'kdj_period': 9,           # KDJ周期
        'kdj_slowing_period': 3,   # KDJ平滑周期
        'printlog': False,         # 是否打印日志
        'size': 100                # 交易数量（股）
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
        
        self.macd = None
        self.signal = None
        self.hist = None
        self.k = None
        self.d = None
        self.j = None
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
        
        # 计算MACD指标
        macd_df = qindicator.calculate_macd(
            pd.DataFrame({'close': data['close']}),
            fastperiod=self._params.macd_fast_period,
            slowperiod=self._params.macd_slow_period,
            signalperiod=self._params.macd_signal_period
        )
        
        self.macd = macd_df['MACD']
        self.signal = macd_df['MACD_SIGNAL']
        self.hist = macd_df['MACD_HIST']
        
        # 计算KDJ指标
        kdj_df = self._calculate_kdj(data)
        self.k = kdj_df['K']
        self.d = kdj_df['D']
        self.j = kdj_df['J']
        
        # 生成交易信号
        self.signals = self.generate_signals()
    
    def _calculate_kdj(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算KDJ指标
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含KDJ指标的DataFrame
        """
        df = data.copy()
        
        # 计算RSV值（未成熟随机值）
        low_min = df['low'].rolling(window=self._params.kdj_period).min()
        high_max = df['high'].rolling(window=self._params.kdj_period).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        
        # 计算K值
        df['K'] = rsv.ewm(alpha=1/self._params.kdj_slowing_period, adjust=False).mean()
        
        # 计算D值
        df['D'] = df['K'].ewm(alpha=1/self._params.kdj_slowing_period, adjust=False).mean()
        
        # 计算J值
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        return df
    
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
            k = self.k
            d = self.d
            j = self.j
        else:
            # 计算MACD指标
            macd_df = qindicator.calculate_macd(
                pd.DataFrame({'close': data['close']}),
                fastperiod=self._params.macd_fast_period,
                slowperiod=self._params.macd_slow_period,
                signalperiod=self._params.macd_signal_period
            )
            macd = macd_df['MACD']
            signal = macd_df['MACD_SIGNAL']
            hist = macd_df['MACD_HIST']
            
            # 计算KDJ指标
            kdj_df = self._calculate_kdj(data)
            k = kdj_df['K']
            d = kdj_df['D']
            j = kdj_df['J']
        
        # 创建信号DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['close']
        signals['macd'] = macd
        signals['signal'] = signal
        signals['hist'] = hist
        signals['K'] = k
        signals['D'] = d
        signals['J'] = j
        
        # 计算MACD交叉信号
        signals['macd_buy_signal'] = ((signals['macd'] > signals['signal']) & 
                                    (signals['macd'].shift(1) <= signals['signal'].shift(1)))
        
        signals['macd_sell_signal'] = ((signals['macd'] < signals['signal']) & 
                                     (signals['macd'].shift(1) >= signals['signal'].shift(1)))
        
        # 计算KDJ超买超卖信号
        signals['kdj_buy_signal'] = (signals['K'] < 20) & (signals['J'] < 0)
        signals['kdj_sell_signal'] = (signals['K'] > 80) & (signals['J'] > 100)
        
        # 计算KDJ金叉信号
        signals['kdj_gold_cross'] = ((signals['K'] > signals['D']) & 
                                   (signals['K'].shift(1) <= signals['D'].shift(1)))
        
        # 计算KDJ死叉信号
        signals['kdj_death_cross'] = ((signals['K'] < signals['D']) & 
                                    (signals['K'].shift(1) >= signals['D'].shift(1)))
        
        # 组合MACD和KDJ信号生成买入信号
        # 买入信号：MACD金叉 或者 (KDJ金叉且KDJ处于超卖区域)
        signals['buy_signal'] = signals['macd_buy_signal'] | \
                               (signals['kdj_gold_cross'] & signals['kdj_buy_signal'])
        
        # 卖出信号：MACD死叉 或者 (KDJ死叉且KDJ处于超买区域)
        signals['sell_signal'] = signals['macd_sell_signal'] | \
                                (signals['kdj_death_cross'] & signals['kdj_sell_signal'])
        
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
                'reason': 'MACD+KDJ买入信号'
            })
            if self._params.printlog:
                self.log(f'买入信号: {buy_date}, 价格: {price:.2f}')
        
        for sell_date in signals['sell_signals']:
            price = self.data.loc[sell_date, 'close']
            transactions.append({
                'date': sell_date,
                'type': 'sell',
                'price': price,
                'reason': 'MACD+KDJ卖出信号'
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
        class BacktraderMACDKDJ(bt.Strategy):
            params = (
                ('macd_fast_period', self._params.macd_fast_period),
                ('macd_slow_period', self._params.macd_slow_period),
                ('macd_signal_period', self._params.macd_signal_period),
                ('kdj_period', self._params.kdj_period),
                ('kdj_slowing_period', self._params.kdj_slowing_period),
                ('printlog', self._params.printlog),
                ('size', self._params.size)  # 使用外部传入的交易数量参数
            )

            def __init__(self):
                # 计算MACD指标
                self.macd = bt.indicators.MACD(
                    self.data.close,
                    period_me1=self.params.macd_fast_period,
                    period_me2=self.params.macd_slow_period,
                    period_signal=self.params.macd_signal_period
                )
                
                # 计算KDJ指标
                # 首先计算RSV值
                self.low_min = bt.indicators.Lowest(
                    self.data.low, period=self.params.kdj_period
                )
                self.high_max = bt.indicators.Highest(
                    self.data.high, period=self.params.kdj_period
                )
                self.rsv = (self.data.close - self.low_min) / \
                          (self.high_max - self.low_min) * 100
                
                # 计算K值
                self.k = bt.indicators.EMA(
                    self.rsv, period=self.params.kdj_slowing_period
                )
                
                # 计算D值
                self.d = bt.indicators.EMA(
                    self.k, period=self.params.kdj_slowing_period
                )
                
                # 计算J值
                self.j = 3 * self.k - 2 * self.d
                
                # MACD交叉信号
                self.macd_crossover = bt.indicators.CrossOver(
                    self.macd.macd, self.macd.signal
                )
                
                # KDJ交叉信号
                self.kdj_crossover = bt.indicators.CrossOver(self.k, self.d)

            def next(self):
                # 计算所需资金
                order_value = self.data.close[0] * self.params.size
                
                # 买入信号
                # 条件1: MACD金叉
                # 或者
                # 条件2: KDJ金叉且K值小于20且J值小于0
                if (self.macd_crossover > 0) or \
                   (self.kdj_crossover > 0 and self.k[0] < 20 and self.j[0] < 0):
                    # 检查可用资金是否足够买入指定数量的股票
                    if self.broker.getcash() >= order_value:
                        self.buy(size=self.params.size)
                        if self.params.printlog:
                            self.log(f'买入: 价格={self.data.close[0]:.2f}, 数量={self.params.size}')
                    else:
                        if self.params.printlog:
                            self.log(f'资金不足: 需要{order_value:.2f}, 可用{self.broker.getcash():.2f}')
                
                # 卖出信号
                # 条件1: MACD死叉
                # 或者
                # 条件2: KDJ死叉且K值大于80且J值大于100
                elif (self.macd_crossover < 0) or \
                     (self.kdj_crossover < 0 and self.k[0] > 80 and self.j[0] > 100):
                    # 计算可以卖出的数量（不超过当前持仓量）
                    sell_size = min(self.params.size, self.position.size if self.position else 0)
                    if sell_size > 0:
                        self.sell(size=sell_size)
                        if self.params.printlog:
                            self.log(f'卖出: 价格={self.data.close[0]:.2f}, 数量={sell_size}')
                              
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
                    position_value = self.position.size * self.data.close[0] if self.position else 0
                    remaining_cash = self.broker.getcash()
                    print(f'{dt.isoformat()}, {txt}, 持仓金额={position_value:.2f}, 剩余金额={remaining_cash:.2f}')
        
        return BacktraderMACDKDJ