import pandas as pd
import numpy as np
import logging
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
    
    def __init__(self, **kwargs):
        """
        初始化波动率突破策略
        
        Args:
            window: 计算波动率的窗口，默认20
            multiplier: 波动率乘数，默认2.0
            printlog: 是否打印日志，默认False
            size: 交易数量，默认100
        """
        # 设置默认参数
        default_params = {
            'window': 20,
            'multiplier': 2.0,
            'printlog': False,
            'size': 100
        }
        
        # 更新默认参数
        default_params.update(kwargs)
        
        # 调用父类初始化
        super().__init__(**default_params)
        
        # 初始化指标属性
        self.volatility = None
        self.upper_band = None
        self.lower_band = None
        
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算波动率突破策略的指标
        
        Args:
            data: 用于计算指标的数据
        
        Returns:
            包含指标计算结果的字典
        """
        try:
            # 计算波动率（使用收盘价的标准差）
            self.volatility = data['close'].rolling(window=self.params.window).std()
            
            # 计算上下轨
            self.upper_band = data['close'] + self.params.multiplier * self.volatility
            self.lower_band = data['close'] - self.params.multiplier * self.volatility
            
            return {
                'volatility': self.volatility,
                'upper_band': self.upper_band,
                'lower_band': self.lower_band
            }
        except Exception as e:
            logger.error(f"计算指标失败: {str(e)}")
            raise StrategyError(f"计算指标失败: {str(e)}")
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        基于波动率突破生成交易信号
        
        Args:
            data: 用于生成信号的数据
            indicators: 已计算的指标，如果为None则重新计算
        
        Returns:
            包含交易信号的字典
        """
        try:
            # 如果没有提供指标，则计算
            if indicators is None:
                indicators = self.calculate_indicators(data)
                
            upper_band = indicators['upper_band']
            lower_band = indicators['lower_band']
            
            # 创建信号DataFrame
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['close']
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
                
            return {
                'signals': signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals
            }
        except Exception as e:
            logger.error(f"生成信号失败: {str(e)}")
            raise StrategyError(f"生成信号失败: {str(e)}")
    
    def execute_trade(self, data: pd.DataFrame, signals: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行交易
        
        Args:
            data: 交易数据
            signals: 交易信号，如果为None则重新生成
        
        Returns:
            交易结果
        """
        try:
            # 如果没有提供信号，则生成
            if signals is None:
                signals = self.generate_signals(data)
                
            transactions = []
            total_profit = 0.0
            position = False
            buy_price = 0.0
            
            # 遍历所有交易日
            for date in data.index:
                # 执行买入信号
                if date in signals['buy_signals'] and not position:
                    price = data.loc[date, 'close']
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
                elif date in signals['sell_signals'] and position:
                    price = data.loc[date, 'close']
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
            return {
                'transactions': transactions,
                'total_buys': len(signals['buy_signals']),
                'total_sells': len(signals['sell_signals']),
                'total_profit': total_profit,
                'final_position': 'holding' if position else 'cash'
            }
        except Exception as e:
            logger.error(f"执行交易失败: {str(e)}")
            raise StrategyError(f"执行交易失败: {str(e)}")

# 注册策略
signals = register_strategy('volatility_breakout', VolatilityBreakoutStrategy)