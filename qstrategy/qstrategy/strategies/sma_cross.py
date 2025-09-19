"""
移动平均线交叉策略
"""

import backtrader as bt
import pandas as pd
from typing import Dict, Any

from qstrategy.strategy import StrategyBase
import qindicator

class SmaCrossStrategy(StrategyBase):
    """
    移动平均线交叉策略
    当短期均线向上穿过长期均线时买入，当短期均线向下穿过长期均线时卖出
    """
    
    params = {
        'fast_period': 10,   # 短期均线周期
        'slow_period': 30,   # 长期均线周期
        'printlog': False,   # 是否打印日志
        'size': 100          # 交易数量（股）
    }
    
    def __init__(self, *args, **kwargs):
        """
        初始化策略
        
        Args:
            *args: 位置参数（用于兼容backtrader框架）
            **kwargs: 策略参数
        """
        super().__init__(*args)
        # 更新参数（处理params为字典的情况）
        self._params = self.params.copy()  # 创建实例参数副本
        for key, value in kwargs.items():
            if key in self._params:
                self._params[key] = value
        
        self.fast_ma = None
        self.slow_ma = None
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
        
        # 使用指标适配器获取移动平均线计算结果
        # 创建一个包含close列的DataFrame，因为qindicator需要DataFrame作为输入
        close_df = pd.DataFrame({'close': data['close']})
        
        # 计算快速移动平均线
        fast_ma_result = qindicator.calculate_ma(
            close_df, 
            timeperiod=self._params['fast_period']
        )
        # 从结果中提取快速均线列（列名为'MA<period>'）
        self.fast_ma = fast_ma_result[f'MA{self._params["fast_period"]}']
        
        # 计算慢速移动平均线
        slow_ma_result = qindicator.calculate_ma(
            close_df, 
            timeperiod=self._params['slow_period']
        )
        # 从结果中提取慢速均线列
        self.slow_ma = slow_ma_result[f'MA{self._params["slow_period"]}']
        
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
            fast_ma = self.fast_ma
            slow_ma = self.slow_ma
        else:
            # 使用指标适配器获取移动平均线计算结果
            # 创建一个包含close列的DataFrame
            close_df = pd.DataFrame({'close': data['close']})
            
            # 计算快速移动平均线
            fast_ma_result = qindicator.calculate_ma(
                close_df, 
                timeperiod=self._params['fast_period']
            )
            # 从结果中提取快速均线列
            self.fast_ma = fast_ma_result[f'MA{self._params["fast_period"]}']
            
            # 计算慢速移动平均线
            slow_ma_result = qindicator.calculate_ma(
                close_df, 
                timeperiod=self._params['slow_period']
            )
            # 从结果中提取慢速均线列
            self.slow_ma = slow_ma_result[f'MA{self._params["slow_period"]}']
            
            fast_ma = self.fast_ma
            slow_ma = self.slow_ma
        
        # 创建信号DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['close']
        signals['fast_ma'] = fast_ma
        signals['slow_ma'] = slow_ma
        
        # 金叉信号：短期均线上穿长期均线
        signals['buy_signal'] = (fast_ma.shift(1) < slow_ma.shift(1)) & (fast_ma > slow_ma)
        # 死叉信号：短期均线下穿长期均线
        signals['sell_signal'] = (fast_ma.shift(1) > slow_ma.shift(1)) & (fast_ma < slow_ma)
        
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
                'reason': '金叉信号：短期均线上穿长期均线'
            })
            if self._params['printlog']:
                self.log(f'买入信号: {buy_date}, 价格: {price:.2f}')
        
        for sell_date in signals['sell_signals']:
            price = self.data.loc[sell_date, 'close']
            transactions.append({
                'date': sell_date,
                'type': 'sell',
                'price': price,
                'reason': '死叉信号：短期均线下穿长期均线'
            })
            if self._params['printlog']:
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
        class BacktraderSmaCross(bt.Strategy):
            params = (
                ('fast_period', self.params['fast_period']),
                ('slow_period', self.params['slow_period']),
                ('printlog', self.params['printlog']),
                ('size', self.params['size']),  # 交易数量
            )
            
            def __init__(self):
                self.fast_ma = bt.indicators.SimpleMovingAverage(
                    self.data.close, period=self.params.fast_period)
                self.slow_ma = bt.indicators.SimpleMovingAverage(
                    self.data.close, period=self.params.slow_period)
                
                # 交叉信号
                self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
                
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
        
        return BacktraderSmaCross