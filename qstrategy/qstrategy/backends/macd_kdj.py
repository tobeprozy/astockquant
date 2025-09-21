import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
from qstrategy.core.strategy import Strategy
from qstrategy.backends import register_strategy

logger = logging.getLogger(__name__)

class MACDKDJStrategy(Strategy):
    """
    MACD+KDJ策略实现
    结合MACD和KDJ指标生成交易信号
    """
    
    def __init__(self, **kwargs):
        """
        初始化MACD+KDJ策略
        
        Args:
            macd_fast_period: MACD快线周期，默认12
            macd_slow_period: MACD慢线周期，默认26
            macd_signal_period: MACD信号线周期，默认9
            kdj_period: KDJ周期，默认9
            kdj_slow_period: KDJ慢速K周期，默认3
            kdj_overbought: KDJ超买阈值，默认80
            kdj_oversold: KDJ超卖阈值，默认20
            printlog: 是否打印日志，默认False
            size: 交易数量，默认100
        """
        # 设置默认参数
        default_params = {
            'macd_fast_period': 12,
            'macd_slow_period': 26,
            'macd_signal_period': 9,
            'kdj_period': 9,
            'kdj_slow_period': 3,
            'kdj_overbought': 80,
            'kdj_oversold': 20,
            'printlog': False,
            'size': 100
        }
        
        # 更新默认参数
        default_params.update(kwargs)
        
        # 调用父类初始化
        super().__init__(**default_params)
        
        # 导入qindicator
        try:
            import qindicator
            self.qindicator = qindicator
        except ImportError:
            logger.error("无法导入qindicator模块")
            raise StrategyError("无法导入qindicator模块")
        
        # 初始化指标属性
        self.macd = None
        self.macd_signal = None
        self.macd_hist = None
        self.k = None
        self.d = None
        self.j = None
    
    def _calculate_kdj(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算KDJ指标
        
        Args:
            data: 用于计算KDJ指标的数据
        
        Returns:
            包含K、D、J线的字典
        """
        try:
            # 计算RSV值
            low_min = data['low'].rolling(window=self.params.kdj_period).min()
            high_max = data['high'].rolling(window=self.params.kdj_period).max()
            rsv = (data['close'] - low_min) / (high_max - low_min) * 100
            
            # 计算K值
            k = pd.Series(0.0, index=data.index)
            k.iloc[self.params.kdj_period - 1] = 50.0  # 初始值
            for i in range(self.params.kdj_period, len(data)):
                k.iloc[i] = (2/3) * k.iloc[i-1] + (1/3) * rsv.iloc[i]
            
            # 计算D值
            d = pd.Series(0.0, index=data.index)
            d.iloc[self.params.kdj_period - 1] = 50.0  # 初始值
            for i in range(self.params.kdj_period, len(data)):
                d.iloc[i] = (2/3) * d.iloc[i-1] + (1/3) * k.iloc[i]
            
            # 计算J值
            j = 3 * k - 2 * d
            
            return {
                'k': k,
                'd': d,
                'j': j
            }
        except Exception as e:
            logger.error(f"计算KDJ指标失败: {str(e)}")
            raise StrategyError(f"计算KDJ指标失败: {str(e)}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算MACD+KDJ策略的指标
        
        Args:
            data: 用于计算指标的数据
        
        Returns:
            包含指标计算结果的字典
        """
        try:
            # 计算MACD指标
            macd_df = self.qindicator.calculate_macd(
                data, 
                fast_period=self.params.macd_fast_period, 
                slow_period=self.params.macd_slow_period,
                signal_period=self.params.macd_signal_period
            )
            
            self.macd = macd_df['MACD']
            self.macd_signal = macd_df['Signal']
            self.macd_hist = macd_df['Histogram']
            
            # 计算KDJ指标
            kdj_result = self._calculate_kdj(data)
            self.k = kdj_result['k']
            self.d = kdj_result['d']
            self.j = kdj_result['j']
            
            return {
                'macd': self.macd,
                'macd_signal': self.macd_signal,
                'macd_hist': self.macd_hist,
                'k': self.k,
                'd': self.d,
                'j': self.j
            }
        except Exception as e:
            logger.error(f"计算指标失败: {str(e)}")
            raise StrategyError(f"计算指标失败: {str(e)}")
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        基于MACD+KDJ生成交易信号
        
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
                
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            k = indicators['k']
            d = indicators['d']
            j = indicators['j']
            
            # 创建信号DataFrame
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['close']
            signals['macd'] = macd
            signals['macd_signal'] = macd_signal
            signals['k'] = k
            signals['d'] = d
            signals['j'] = j
            
            # MACD交叉信号
            signals['macd_buy_cross'] = (macd.shift(1) <= macd_signal.shift(1)) & (macd > macd_signal)
            signals['macd_sell_cross'] = (macd.shift(1) >= macd_signal.shift(1)) & (macd < macd_signal)
            
            # KDJ超买超卖信号
            signals['kdj_oversold'] = (k < self.params.kdj_oversold) & (d < self.params.kdj_oversold) & (j < self.params.kdj_oversold)
            signals['kdj_overbought'] = (k > self.params.kdj_overbought) & (d > self.params.kdj_overbought) & (j > self.params.kdj_overbought)
            
            # KDJ交叉信号
            signals['kdj_buy_cross'] = (k.shift(1) <= d.shift(1)) & (k > d)
            signals['kdj_sell_cross'] = (k.shift(1) >= d.shift(1)) & (k < d)
            
            # 组合信号：MACD金叉且KDJ超卖或金叉
            signals['buy_signal'] = signals['macd_buy_cross'] & (signals['kdj_oversold'] | signals['kdj_buy_cross'])
            
            # 组合信号：MACD死叉且KDJ超买或死叉
            signals['sell_signal'] = signals['macd_sell_cross'] & (signals['kdj_overbought'] | signals['kdj_sell_cross'])
            
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
                        'reason': 'MACD金叉且KDJ超卖或金叉'
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
                        'reason': 'MACD死叉且KDJ超买或死叉'
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
signals = register_strategy('macd_kdj', MACDKDJStrategy)