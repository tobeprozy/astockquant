#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配对交易策略实现
基于两只相关性高的股票之间价格差异的交易策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import logging
import backtrader as bt  # 添加backtrader导入

from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy
import qindicator

logger = logging.getLogger(__name__)

class PairTradingStrategy(Strategy):
    """
    配对交易策略
    当两只相关性高的股票之间的价格差异超过阈值时进行交易
    """
    
    # 直接在类级别定义默认参数
    default_params = {
        'lookback_period': 60,
        'zscore_threshold': 2,
        'printlog': False,
        'size': 100
    }
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
                lookback_period: 回溯期，默认60
                zscore_threshold: Z-score阈值，默认2
                printlog: 是否打印日志，默认False
                size: 交易数量（股），默认100
        """
        # 合并用户参数和默认参数
        merged_params = PairTradingStrategy.default_params.copy()
        merged_params.update(kwargs)
        
        super().__init__(**merged_params)
        
        # 初始化指标
        self._stock1_data = None
        self._stock2_data = None
        self._spread = None
        self._zscore = None
        self._indicators_data = None
    
    def get_backtrader_strategy(self):
        """
        获取兼容backtrader的策略类
        使策略能在BacktraderEngine中运行
        """
        class BacktraderPairTradingStrategy(bt.Strategy):
            # 使用类级别默认参数
            params = tuple((k, v) for k, v in PairTradingStrategy.default_params.items())
            
            def __init__(self):
                # 初始化交易状态
                self.order = None
                self.buyprice = None
                self.buycomm = None
                
                # 获取两只股票的数据源
                self.stock1 = self.datas[0]
                self.stock2 = self.datas[1]
                
                # 计算价差
                self.spread = self.stock1.close - self.stock2.close
                
                # 计算滚动均值和标准差用于Z-score计算
                self.lookback_period = self.p.lookback_period
                
                # 用于存储历史价差数据
                self.spread_history = []
                
                # 交易状态跟踪
                self.in_position = False
            
            def log(self, txt, dt=None):
                """记录交易日志"""
                dt = dt or self.datas[0].datetime.date(0)
                print(f'{dt.isoformat()} {txt}')
            
            def notify_order(self, order):
                """订单状态变化通知"""
                if order.status in [order.Submitted, order.Accepted]:
                    # 订单已提交或已接受，无需操作
                    return
                
                # 检查订单是否完成
                if order.status in [order.Completed]:
                    if order.isbuy():  # 买入订单完成
                        self.log(f'买入: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
                        self.buyprice = order.executed.price
                        self.buycomm = order.executed.comm
                    else:  # 卖出订单完成
                        self.log(f'卖出: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
                elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                    self.log('订单 取消/保证金不足/拒绝')
                
                # 重置订单状态
                self.order = None
            
            def notify_trade(self, trade):
                """交易状态变化通知"""
                if not trade.isclosed:
                    return
                
                self.log(f'交易利润: 毛利润={trade.pnl:.2f}, 净利润={trade.pnlcomm:.2f}')
            
            def next(self):
                """每个交易日执行的逻辑"""
                # 检查是否有挂单
                if self.order:
                    return
                
                # 添加当前价差到历史记录
                current_spread = self.spread[0]
                self.spread_history.append(current_spread)
                
                # 确保有足够的历史数据计算Z-score
                if len(self.spread_history) < self.p.lookback_period:
                    return
                
                # 计算Z-score
                recent_spreads = self.spread_history[-self.p.lookback_period:]
                mean = np.mean(recent_spreads)
                std = np.std(recent_spreads)
                
                # 避免除零错误
                if std == 0:
                    zscore = 0
                else:
                    zscore = (current_spread - mean) / std
                
                # 交易逻辑
                if not self.in_position:
                    # 当Z-score低于负阈值时，买入股票1卖出股票2
                    if zscore < -self.p.zscore_threshold:
                        if self.p.printlog:
                            self.log(f"买入股票1卖出股票2信号: Z-score={zscore:.2f}")
                        # 买入股票1
                        self.buy(data=self.stock1, size=self.p.size)
                        # 卖出股票2
                        self.sell(data=self.stock2, size=self.p.size)
                        self.in_position = True
                else:
                    # 当Z-score高于正阈值时，卖出股票1买入股票2（平仓）
                    if zscore > self.p.zscore_threshold:
                        if self.p.printlog:
                            self.log(f"卖出股票1买入股票2信号: Z-score={zscore:.2f}")
                        # 卖出股票1
                        self.sell(data=self.stock1, size=self.p.size)
                        # 买入股票2
                        self.buy(data=self.stock2, size=self.p.size)
                        self.in_position = False
        
        return BacktraderPairTradingStrategy
    
    def init_data(self, data: Dict[str, pd.DataFrame]) -> None:
        """
        初始化策略数据
        
        Args:
            data: 包含两只股票数据的字典，格式为{'stock1': df1, 'stock2': df2}
        
        Raises:
            ValueError: 当数据格式不符合要求时
        """
        # 验证数据格式
        if not isinstance(data, dict) or len(data) != 2:
            raise ValueError("配对交易策略需要两只股票的数据，格式为{'stock1': df1, 'stock2': df2}")
        
        # 提取两只股票的数据
        stock_keys = list(data.keys())
        self._stock1_data = data[stock_keys[0]].copy()
        self._stock2_data = data[stock_keys[1]].copy()
        
        # 验证数据完整性
        self._validate_data(self._stock1_data)
        self._validate_data(self._stock2_data)
        
        # 确保两只股票的日期范围一致
        common_dates = self._stock1_data.index.intersection(self._stock2_data.index)
        self._stock1_data = self._stock1_data.loc[common_dates]
        self._stock2_data = self._stock2_data.loc[common_dates]
        
        # 保存数据
        self._data = data
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算配对交易所需的指标（价差和Z-score）
        
        Returns:
            pd.DataFrame: 包含计算结果的DataFrame
        """
        if self._stock1_data is None or self._stock2_data is None:
            raise ValueError("策略数据未初始化，请先调用init_data方法")
        
        # 获取参数
        lookback_period = self.params.get('lookback_period', 60)
        
        # 计算两只股票的价格比率
        price_ratio = self._stock1_data['close'] / self._stock2_data['close']
        
        # 计算价差
        spread = self._stock1_data['close'] - self._stock2_data['close']
        
        # 计算Z-score
        zscore = []
        for i in range(len(spread)):
            if i < lookback_period:
                zscore.append(np.nan)
            else:
                mean = spread.iloc[i-lookback_period:i].mean()
                std = spread.iloc[i-lookback_period:i].std()
                if std == 0:
                    zscore.append(0)
                else:
                    zscore.append((spread.iloc[i] - mean) / std)
        
        zscore = pd.Series(zscore, index=spread.index)
        
        # 创建指标DataFrame
        indicators_data = pd.DataFrame({
            'stock1_close': self._stock1_data['close'],
            'stock2_close': self._stock2_data['close'],
            'price_ratio': price_ratio,
            'spread': spread,
            'zscore': zscore
        })
        
        # 保存结果
        self._indicators_data = indicators_data
        self._spread = spread
        self._zscore = zscore
        
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
        zscore_threshold = self.params.get('zscore_threshold', 2)
        
        # 生成配对交易信号
        signals = {
            'buy_stock1_sell_stock2': [],  # 买入股票1卖出股票2的信号日期列表
            'sell_stock1_buy_stock2': [],  # 卖出股票1买入股票2的信号日期列表
            'all_signals': []  # 所有信号日期和类型
        }
        
        # 遍历数据，寻找交易机会
        for i in range(len(self._zscore)):
            zscore_value = self._zscore.iloc[i]
            date = self._zscore.index[i]
            
            # 确保Z-score值不为NaN
            if pd.notna(zscore_value):
                # 当Z-score低于负阈值时，买入股票1卖出股票2
                if zscore_value < -zscore_threshold:
                    signals['buy_stock1_sell_stock2'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'buy_stock1_sell_stock2',
                        'stock1_price': self._stock1_data['close'].iloc[i],
                        'stock2_price': self._stock2_data['close'].iloc[i],
                        'zscore': zscore_value
                    })
                    if self.params.get('printlog', False):
                        self.log(f"买入股票1卖出股票2信号: {date}, Z-score={zscore_value:.2f}")
                
                # 当Z-score高于正阈值时，卖出股票1买入股票2
                elif zscore_value > zscore_threshold:
                    signals['sell_stock1_buy_stock2'].append(date)
                    signals['all_signals'].append({
                        'date': date,
                        'type': 'sell_stock1_buy_stock2',
                        'stock1_price': self._stock1_data['close'].iloc[i],
                        'stock2_price': self._stock2_data['close'].iloc[i],
                        'zscore': zscore_value
                    })
                    if self.params.get('printlog', False):
                        self.log(f"卖出股票1买入股票2信号: {date}, Z-score={zscore_value:.2f}")
        
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
        position = {'stock1': 0, 'stock2': 0}  # 当前持仓
        
        # 按照日期排序所有信号
        all_signals_sorted = sorted(self._signals['all_signals'], key=lambda x: x['date'])
        
        for signal in all_signals_sorted:
            if signal['type'] == 'buy_stock1_sell_stock2' and position['stock1'] == 0 and position['stock2'] == 0:
                # 买入股票1，卖出股票2
                position['stock1'] = size
                position['stock2'] = -size
                
                trade = {
                    'date': signal['date'],
                    'type': 'buy_stock1_sell_stock2',
                    'stock1_price': signal['stock1_price'],
                    'stock2_price': signal['stock2_price'],
                    'size': size,
                    'position': position.copy(),
                    'zscore': signal['zscore']
                }
                trades.append(trade)
                
                if self.params.get('printlog', False):
                    self.log(f"买入股票1卖出股票2: 股票1价格={signal['stock1_price']:.2f}, 股票2价格={signal['stock2_price']:.2f}, 数量={size}")
            elif signal['type'] == 'sell_stock1_buy_stock2' and position['stock1'] != 0 and position['stock2'] != 0:
                # 卖出股票1，买入股票2（平仓）
                # 计算利润
                last_trade = next(t for t in reversed(trades) if t['type'] == 'buy_stock1_sell_stock2')
                profit = (signal['stock1_price'] - last_trade['stock1_price']) * size + \
                        (last_trade['stock2_price'] - signal['stock2_price']) * size
                
                trade = {
                    'date': signal['date'],
                    'type': 'sell_stock1_buy_stock2',
                    'stock1_price': signal['stock1_price'],
                    'stock2_price': signal['stock2_price'],
                    'size': size,
                    'profit': profit,
                    'position': {'stock1': 0, 'stock2': 0},
                    'zscore': signal['zscore']
                }
                trades.append(trade)
                
                # 更新持仓
                position['stock1'] = 0
                position['stock2'] = 0
                
                if self.params.get('printlog', False):
                    self.log(f"卖出股票1买入股票2: 股票1价格={signal['stock1_price']:.2f}, 股票2价格={signal['stock2_price']:.2f}, 数量={size}, 利润={profit:.2f}")
        
        # 计算总收益
        total_profit = sum(trade['profit'] for trade in trades if 'profit' in trade)
        
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
register_strategy('PairTrading', PairTradingStrategy)