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
            raise ValueError("无法导入qindicator模块")
        
        # 初始化指标属性
        self.macd = None
        self.macd_signal = None
        self.macd_hist = None
        self.k = None
        self.d = None
        self.j = None
    
    def _calculate_kdj(self) -> Dict[str, pd.Series]:
        """
        计算KDJ指标
        
        Returns:
            包含K、D、J线的字典
        """
        try:
            if self.data is None:
                raise ValueError("策略数据未初始化，请先调用init_data方法")
                
            # 获取KDJ周期参数
            kdj_period = self.params.get('kdj_period')
            
            # 计算RSV值
            low_min = self.data['low'].rolling(window=kdj_period).min()
            high_max = self.data['high'].rolling(window=kdj_period).max()
            rsv = (self.data['close'] - low_min) / (high_max - low_min) * 100
            
            # 计算K值
            k = pd.Series(0.0, index=self.data.index)
            k.iloc[kdj_period - 1] = 50.0  # 初始值
            for i in range(kdj_period, len(self.data)):
                k.iloc[i] = (2/3) * k.iloc[i-1] + (1/3) * rsv.iloc[i]
            
            # 计算D值
            d = pd.Series(0.0, index=self.data.index)
            d.iloc[kdj_period - 1] = 50.0  # 初始值
            for i in range(kdj_period, len(self.data)):
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
            raise ValueError(f"计算KDJ指标失败: {str(e)}")
    
    def calculate_indicators(self) -> Dict[str, Any]:
        """
        计算MACD+KDJ策略的指标
        
        Returns:
            包含指标计算结果的字典
        """
        try:
            if self.data is None:
                raise ValueError("策略数据未初始化，请先调用init_data方法")
                
            # 计算MACD指标
            macd_df = self.qindicator.calculate_macd(
                self.data, 
                fastperiod=self.params.get('macd_fast_period'), 
                slowperiod=self.params.get('macd_slow_period'),
                signalperiod=self.params.get('macd_signal_period')
            )
            
            self.macd = macd_df['MACD']
            self.macd_signal = macd_df['MACD_SIGNAL']
            self.macd_hist = macd_df['MACD_HIST']
            
            # 计算KDJ指标
            kdj_result = self._calculate_kdj()
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
            raise ValueError(f"计算指标失败: {str(e)}")
    
    def generate_signals(self) -> Dict[str, Any]:
        """
        基于MACD+KDJ生成交易信号
        
        Returns:
            包含交易信号的字典
        """
        try:
            if self.data is None:
                raise ValueError("策略数据未初始化，请先调用init_data方法")
                
            # 计算指标
            indicators = self.calculate_indicators()
            
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            k = indicators['k']
            d = indicators['d']
            j = indicators['j']
            
            # 创建信号DataFrame
            signals = pd.DataFrame(index=self.data.index)
            signals['price'] = self.data['close']
            signals['macd'] = macd
            signals['macd_signal'] = macd_signal
            signals['k'] = k
            signals['d'] = d
            signals['j'] = j
            
            # MACD交叉信号
            signals['macd_buy_cross'] = (macd.shift(1) <= macd_signal.shift(1)) & (macd > macd_signal)
            signals['macd_sell_cross'] = (macd.shift(1) >= macd_signal.shift(1)) & (macd < macd_signal)
            
            # 获取KDJ参数
            kdj_oversold = self.params.get('kdj_oversold')
            kdj_overbought = self.params.get('kdj_overbought')
            
            # KDJ超买超卖信号
            signals['kdj_oversold'] = (k < kdj_oversold) & (d < kdj_oversold) & (j < kdj_oversold)
            signals['kdj_overbought'] = (k > kdj_overbought) & (d > kdj_overbought) & (j > kdj_overbought)
            
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
            
            if self.params.get('printlog'):
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
        try:
            if self.data is None:
                raise ValueError("策略数据未初始化，请先调用init_data方法")
                
            # 如果还没有生成信号，先生成
            if self._signals is None:
                self.generate_signals()
                
            transactions = []
            total_profit = 0.0
            position = 0  # 0表示空仓，大于0表示持仓
            buy_price = 0.0
            
            # 获取交易参数
            size = self.params.get('size')
            printlog = self.params.get('printlog')
            
            # 遍历所有交易日
            for date in self.data.index:
                # 执行买入信号
                if date in self._signals['buy_signals'] and position == 0:
                    price = self.data.loc[date, 'close']
                    transactions.append({
                        'date': date,
                        'type': 'buy',
                        'price': price,
                        'size': size,
                        'cost': price * size,
                        'position': size,
                        'reason': 'MACD金叉且KDJ超卖或金叉'
                    })
                    position = size
                    buy_price = price
                    
                    if printlog:
                        logger.info(f"买入信号: {date}, 价格: {price:.2f}")
                
                # 执行卖出信号
                elif date in self._signals['sell_signals'] and position > 0:
                    price = self.data.loc[date, 'close']
                    profit = (price - buy_price) * size
                    profit_percent = (profit / (buy_price * size)) * 100 if buy_price > 0 else 0
                    total_profit += profit
                    
                    transactions.append({
                        'date': date,
                        'type': 'sell',
                        'price': price,
                        'size': size,
                        'revenue': price * size,
                        'profit': profit,
                        'profit_percent': profit_percent,
                        'position': 0,
                        'reason': 'MACD死叉且KDJ超买或死叉'
                    })
                    position = 0
                    
                    if printlog:
                        logger.info(f"卖出信号: {date}, 价格: {price:.2f}, 利润: {profit:.2f} ({profit_percent:.2f}%)")
            
            # 返回交易结果
            result = {
                'transactions': transactions,
                'total_buys': len(self._signals['buy_signals']),
                'total_sells': len(self._signals['sell_signals']),
                'total_profit': total_profit,
                'final_position': position,
                'num_trades': len(transactions)
            }
            
            if printlog:
                logger.info(f"交易结果: 总利润={total_profit:.2f}, 交易次数={len(transactions)}")
                
            return result
        except Exception as e:
            logger.error(f"执行交易失败: {str(e)}")
            raise ValueError(f"执行交易失败: {str(e)}")

# 注册策略
register_strategy('macd_kdj', MACDKDJStrategy)