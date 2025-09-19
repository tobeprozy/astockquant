import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, Any
from types import SimpleNamespace

import backtrader as bt
from qstrategy.strategy import StrategyBase

class PairTradingStrategy(StrategyBase):
    """
    配对交易策略实现
    通过分析两只相关股票的价格差异来寻找交易机会
    """
    
    params = {
        'lookback_period': 60,    # 回看期长度
        'z_score_threshold': 2.0, # Z-score阈值
        'printlog': False,        # 是否打印日志
        'size': 100               # 交易数量（股）
    }
    
    def __init__(self, *args, **kwargs):
        """
        初始化策略
        
        Args:
            *args: 位置参数，用于backtrader框架传递的额外参数
            **kwargs: 策略参数
        """
        super().__init__(*args, **kwargs)
        
        # 创建可通过点表示法访问的参数对象
        self._params = SimpleNamespace(**self.params)
        
        # 更新参数
        for key, value in kwargs.items():
            if key in self.params:
                setattr(self._params, key, value)
        
        self.data_a = None  # 第一只股票数据
        self.data_b = None  # 第二只股票数据
        self.spread = None  # 价格差
        self.z_score = None  # Z-score
        self.signals = None  # 交易信号

    def init_strategy(self, data: Dict[str, pd.DataFrame], **kwargs):
        """
        初始化策略数据和指标
        
        Args:
            data: 包含两只股票数据的字典，键为'symbol_a'和'symbol_b'
            **kwargs: 其他参数
        """
        # 确保传入了两只股票的数据
        if 'symbol_a' not in data or 'symbol_b' not in data:
            raise ValueError("PairTradingStrategy需要'symbol_a'和'symbol_b'两只股票的数据")
        
        self.data_a = data['symbol_a'].copy()
        self.data_b = data['symbol_b'].copy()
        
        # 计算价格差
        self.spread = self.data_a['close'] - self.data_b['close']
        
        # 计算Z-score
        self._calculate_z_score()
        
        # 生成交易信号
        self.signals = self.generate_signals()
        
    def _calculate_z_score(self):
        """
        计算价格差的Z-score
        """
        # 计算移动平均线和标准差
        rolling_mean = self.spread.rolling(window=self._params.lookback_period).mean()
        rolling_std = self.spread.rolling(window=self._params.lookback_period).std()
        
        # 计算Z-score
        self.z_score = (self.spread - rolling_mean) / rolling_std
        
    def generate_signals(self, data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: 包含两只股票数据的字典，如果为None则使用初始化数据
            
        Returns:
            包含交易信号的字典
        """
        if data is not None:
            # 如果提供了新数据，重新计算价格差和Z-score
            if 'symbol_a' not in data or 'symbol_b' not in data:
                raise ValueError("PairTradingStrategy需要'symbol_a'和'symbol_b'两只股票的数据")
            
            data_a = data['symbol_a']
            data_b = data['symbol_b']
            spread = data_a['close'] - data_b['close']
            
            # 计算Z-score
            rolling_mean = spread.rolling(window=self._params.lookback_period).mean()
            rolling_std = spread.rolling(window=self._params.lookback_period).std()
            z_score = (spread - rolling_mean) / rolling_std
        else:
            z_score = self.z_score
        
        # 创建信号DataFrame
        signals = pd.DataFrame(index=z_score.index)
        signals['z_score'] = z_score
        
        # 买入信号：Z-score低于负阈值（做空价差）
        signals['buy_signal'] = (z_score < -self._params.z_score_threshold)
        # 卖出信号：Z-score高于正阈值（做多价差）
        signals['sell_signal'] = (z_score > self._params.z_score_threshold)
        # 平仓信号：Z-score回到0附近
        signals['close_position_signal'] = np.abs(z_score) < 0.5
        
        return {
            'signals': signals,
            'buy_signals': signals[signals['buy_signal']].index,
            'sell_signals': signals[signals['sell_signal']].index,
            'close_position_signals': signals[signals['close_position_signal']].index
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
        
        transactions = []
        
        # 买入信号：买入股票A，卖出股票B（做空价差）
        for buy_date in signals['buy_signals']:
            price_a = self.data_a.loc[buy_date, 'close'] if self.data_a is not None else None
            price_b = self.data_b.loc[buy_date, 'close'] if self.data_b is not None else None
            
            # 记录买入股票A的交易
            transactions.append({
                'date': buy_date,
                'symbol': 'symbol_a',
                'type': 'buy',
                'price': price_a,
                'reason': f'Z-score低于阈值: {self.z_score.loc[buy_date]:.2f}'
            })
            
            # 记录卖出股票B的交易
            transactions.append({
                'date': buy_date,
                'symbol': 'symbol_b',
                'type': 'sell',
                'price': price_b,
                'reason': f'Z-score低于阈值: {self.z_score.loc[buy_date]:.2f}'
            })
            
            if self._params.printlog:
                self.log(f'买入股票A，卖出股票B: {buy_date}, Z-score: {self.z_score.loc[buy_date]:.2f}')
        
        # 卖出信号：卖出股票A，买入股票B（做多价差）
        for sell_date in signals['sell_signals']:
            price_a = self.data_a.loc[sell_date, 'close'] if self.data_a is not None else None
            price_b = self.data_b.loc[sell_date, 'close'] if self.data_b is not None else None
            
            # 记录卖出股票A的交易
            transactions.append({
                'date': sell_date,
                'symbol': 'symbol_a',
                'type': 'sell',
                'price': price_a,
                'reason': f'Z-score高于阈值: {self.z_score.loc[sell_date]:.2f}'
            })
            
            # 记录买入股票B的交易
            transactions.append({
                'date': sell_date,
                'symbol': 'symbol_b',
                'type': 'buy',
                'price': price_b,
                'reason': f'Z-score高于阈值: {self.z_score.loc[sell_date]:.2f}'
            })
            
            if self._params.printlog:
                self.log(f'卖出股票A，买入股票B: {sell_date}, Z-score: {self.z_score.loc[sell_date]:.2f}')
        
        return {
            'transactions': transactions,
            'total_buys': len(signals['buy_signals']) * 2,  # 每个买入信号包含两个交易
            'total_sells': len(signals['sell_signals']) * 2  # 每个卖出信号包含两个交易
        }
        
    def get_backtrader_strategy(self) -> type:
        """
        获取对应的backtrader策略类
        
        Returns:
            backtrader策略类
        """
        # 定义内部的backtrader策略类
        class BacktraderPairTrading(bt.Strategy):
            params = (
                ('lookback_period', self._params.lookback_period),
                ('z_score_threshold', self._params.z_score_threshold),
                ('printlog', self._params.printlog),
                ('size', self._params.size),  # 交易数量
            )
            
            def __init__(self):
                # 确保有两只数据
                if len(self.datas) < 2:
                    raise ValueError("PairTrading策略需要两只数据")
                
                self.data_a = self.datas[0]
                self.data_b = self.datas[1]
                
                # 计算价差
                self.spread = self.data_a.close - self.data_b.close
                
                # 计算移动平均线和标准差
                self.spread_mean = bt.indicators.SimpleMovingAverage(
                    self.spread, period=self.params.lookback_period
                )
                self.spread_std = bt.indicators.StandardDeviation(
                    self.spread, period=self.params.lookback_period
                )
                
                # 计算Z-score
                self.z_score = (self.spread - self.spread_mean) / self.spread_std
                
            def next(self):
                # 获取价差和Z-score
                spread = self.spread[0]
                z_score = self.z_score[0]
                
                # Z-score低于负阈值，买入价差（买入资产1，卖出资产2）
                if z_score < -self.params.z_score_threshold:
                    # 计算所需资金（基于资产1的价格）
                    order_value_asset1 = self.datas[0].close[0] * self.params.size
                    
                    # 检查可用资金是否足够买入资产1
                    if self.broker.getcash() >= order_value_asset1:
                        self.buy(data=self.datas[0], size=self.params.size)
                        self.sell(data=self.datas[1], size=self.params.size)
                        if self.params.printlog:
                            self.log(f'买入价差: 价差={spread:.4f}, Z-score={z_score:.4f}, 数量={self.params.size}')
                    else:
                        if self.params.printlog:
                            self.log(f'资金不足: 需要{order_value_asset1:.2f}, 可用{self.broker.getcash():.2f}')
                # Z-score高于正阈值，卖出价差（卖出资产1，买入资产2）
                elif z_score > self.params.z_score_threshold:
                    # 确保有足够的资产1持仓用于卖出
                    asset1_position = self.getposition(self.datas[0]).size
                    sell_size = min(self.params.size, asset1_position)
                    
                    if sell_size > 0:
                        self.sell(data=self.datas[0], size=sell_size)
                        # 计算买入资产2所需资金
                        order_value_asset2 = self.datas[1].close[0] * sell_size
                        
                        if self.broker.getcash() >= order_value_asset2:
                            self.buy(data=self.datas[1], size=sell_size)
                            if self.params.printlog:
                                self.log(f'卖出价差: 价差={spread:.4f}, Z-score={z_score:.4f}, 数量={sell_size}')
                        else:
                            if self.params.printlog:
                                self.log(f'资金不足: 需要{order_value_asset2:.2f}, 可用{self.broker.getcash():.2f}')
                # Z-score回归到0附近，平仓
                elif abs(z_score) < 0.5:
                    # 平掉所有仓位
                    self.close(self.data_a)
                    self.close(self.data_b)
                    if self.params.printlog:
                        self.log(f'平仓: 价差={spread:.4f}, Z-score={z_score:.4f}')
            
            def log(self, txt, dt=None):
                """日志函数，用于记录交易记录，包含持仓金额和剩余金额"""
                dt = dt or self.datas[0].datetime.date(0)
                
                # 计算持仓金额和剩余金额
                remaining_cash = self.broker.getcash()
                position_value_asset1 = 0
                position_value_asset2 = 0
                
                # 根据交易类型计算持仓金额
                if '买入价差' in txt:
                    # 买入价差操作 - 使用当前持仓和价格计算持仓金额
                    size = int(txt.split('数量=')[1])
                    pos1 = self.getposition(self.datas[0])
                    pos2 = self.getposition(self.datas[1])
                    if pos1 and pos2:
                        position_value_asset1 = pos1.size * self.datas[0].close[0]
                        position_value_asset2 = pos2.size * self.datas[1].close[0]
                elif '卖出价差' in txt:
                    # 卖出价差操作 - 使用当前持仓和价格计算持仓金额
                    size = int(txt.split('数量=')[1])
                    pos1 = self.getposition(self.datas[0])
                    pos2 = self.getposition(self.datas[1])
                    if pos1 and pos2:
                        position_value_asset1 = pos1.size * self.datas[0].close[0]
                        position_value_asset2 = pos2.size * self.datas[1].close[0]
                elif '平仓' in txt:
                    # 平仓操作 - 持仓金额应为0
                    position_value_asset1 = 0
                    position_value_asset2 = 0
                else:
                    # 其他情况 - 使用当前价格计算持仓金额
                    if len(self.datas) > 0:
                        pos1 = self.getposition(self.datas[0])
                        if pos1:
                            position_value_asset1 = pos1.size * self.datas[0].close[0]
                    
                    if len(self.datas) > 1:
                        pos2 = self.getposition(self.datas[1])
                        if pos2:
                            position_value_asset2 = pos2.size * self.datas[1].close[0]
                
                total_position_value = position_value_asset1 + position_value_asset2
                
                # 打印带有持仓金额和剩余金额的日志
                print(f'{dt.isoformat()}, {txt}, 资产1持仓={position_value_asset1:.2f}, 资产2持仓={position_value_asset2:.2f}, 总持仓金额={total_position_value:.2f}, 剩余金额={remaining_cash:.2f}')
        
        return BacktraderPairTrading