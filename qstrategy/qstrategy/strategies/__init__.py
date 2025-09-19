"""
策略实现模块
包含各种具体的交易策略实现
"""

from .sma_cross import SmaCrossStrategy
from .macd_strategy import MACDStrategy
from .rsi_strategy import RSIStrategy
from .bbands_strategy import BBandsStrategy
from .pair_trading_strategy import PairTradingStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .volatility_breakout_strategy import VolatilityBreakoutStrategy
from .macd_kdj_strategy import MACDKDJStrategy

# 注册策略到工厂
from qstrategy.factory import StrategyFactory

# 自动注册所有已实现的策略
StrategyFactory.register('sma_cross', SmaCrossStrategy)
StrategyFactory.register('macd', MACDStrategy)
StrategyFactory.register('rsi', RSIStrategy)
StrategyFactory.register('bbands', BBandsStrategy)
StrategyFactory.register('PairTrading', PairTradingStrategy)
StrategyFactory.register('mean_reversion', MeanReversionStrategy)
StrategyFactory.register('volatility_breakout', VolatilityBreakoutStrategy)
StrategyFactory.register('macd_kdj', MACDKDJStrategy)

__all__ = [
    'SmaCrossStrategy',
    'MACDStrategy',
    'RSIStrategy',
    'BBandsStrategy',
    'PairTradingStrategy',
    'MeanReversionStrategy',
    'VolatilityBreakoutStrategy',
    'MACDKDJStrategy'
]