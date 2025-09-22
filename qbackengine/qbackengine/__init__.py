"""
qbackengine - 一个简洁的量化交易回测引擎插件系统

该系统设计用于提供简洁而强大的回测功能，支持不同的回测引擎和策略。
"""

import logging
from typing import Any, Dict, Optional, Type
import pandas as pd
from datetime import datetime

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 版本信息
__version__ = "0.1.0"
__author__ = "AstockQuant Team"

# 导入数据源和策略插件
from qdata import get_provider
import qstrategy

# 导入回测引擎实现
from .engine import BacktraderEngine, MultiSymbolBacktraderEngine, SimpleLoopEngine, SimpleResult

# 全局变量
_current_engine = None
_initialized = False

# 初始化函数
def init(engine_type: str = 'backtrader') -> None:
    """
    初始化qbackengine插件
    
    参数:
        engine_type: 回测引擎类型，默认为'backtrader'
    """
    global _initialized
    
    _initialized = True
    logger.info(f"已初始化{engine_type}回测引擎")

# 策略名称映射字典，将示例中使用的名称映射到实际注册的名称
STRATEGY_NAME_MAPPING = {
    'MA_Cross': 'sma_cross',
    'MACD': 'macd',
    'RSI': 'rsi',
    'BBands': 'bbands'
}

# 创建回测引擎
def create_backtrader_engine(
    symbol: str,
    start_date: str,
    end_date: str,
    strategy_name: str = 'MA_Cross',
    starting_cash: float = 100000.0,
    commission: float = 0.00025,
    email_on_finish: bool = False,
    strategy_kwargs: dict = None
) -> BacktraderEngine:
    """
    创建backtrader回测引擎
    
    参数:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        strategy_name: 策略名称
        starting_cash: 初始资金
        commission: 佣金比例
        email_on_finish: 回测完成后发送邮件
        strategy_kwargs: 策略参数
    
    返回:
        回测引擎实例
    """
    # 获取数据提供者
    data_provider = get_provider()
    
    # 获取策略类
    # 应用策略名称映射
    mapped_strategy_name = STRATEGY_NAME_MAPPING.get(strategy_name, strategy_name)
    
    try:
        # 获取策略实例
        strategy = qstrategy.get_strategy(mapped_strategy_name, **(strategy_kwargs or {}))
        # 对于backtrader引擎，我们需要策略类而不是实例
        strategy_cls = strategy.__class__
    except Exception as e:
        # 策略未找到时的默认处理
        logger.warning(f"未找到策略 '{mapped_strategy_name}'，使用默认的SmaCrossStrategy")
        from qstrategy.strategies.sma_cross import SmaCrossStrategy
        strategy_cls = SmaCrossStrategy
    
    # 创建回测引擎
    engine = BacktraderEngine(
        data_provider=data_provider,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_cls=strategy_cls,
        starting_cash=starting_cash,
        commission=commission,
        email_on_finish=email_on_finish,
        strategy_kwargs=strategy_kwargs
    )
    
    return engine

# 创建多标的回测引擎
def create_multi_symbol_engine(
    symbol_a: str,
    symbol_b: str,
    start_date: str,
    end_date: str,
    strategy_name: str = 'PairTrading',
    starting_cash: float = 100000.0,
    commission: float = 0.00025
) -> MultiSymbolBacktraderEngine:
    """
    创建多标的回测引擎
    
    参数:
        symbol_a: 第一个股票代码
        symbol_b: 第二个股票代码
        start_date: 开始日期
        end_date: 结束日期
        strategy_name: 策略名称
        starting_cash: 初始资金
        commission: 佣金比例
    
    返回:
        回测引擎实例
    """
    # 获取数据提供者
    data_provider = get_provider()
    
    # 获取策略类
    # 应用策略名称映射
    mapped_strategy_name = STRATEGY_NAME_MAPPING.get(strategy_name, strategy_name)
    
    try:
        # 获取策略实例
        strategy = qstrategy.get_strategy(mapped_strategy_name)
        # 对于多标的策略，我们需要获取backtrader策略类
        bt_strategy_cls = strategy.get_backtrader_strategy()
    except Exception as e:
        # PairTrading策略未找到时的默认处理
        logger.warning(f"未找到策略 '{mapped_strategy_name}'，使用默认的SmaCrossStrategy")
        from qstrategy.strategies.sma_cross import SmaCrossStrategy
        strategy = SmaCrossStrategy()
        bt_strategy_cls = strategy.get_backtrader_strategy()
    
    # 创建回测引擎
    engine = MultiSymbolBacktraderEngine(
        data_provider=data_provider,
        symbol_a=symbol_a,
        symbol_b=symbol_b,
        start_date=start_date,
        end_date=end_date,
        strategy_cls=bt_strategy_cls,
        starting_cash=starting_cash,
        commission=commission
    )
    
    return engine

# 运行回测
def run(
    symbol: str,
    start_date: str,
    end_date: str,
    strategy_name: str = 'MA_Cross',
    starting_cash: float = 100000.0,
    commission: float = 0.00025,
    engine_type: str = 'backtrader',
    strategy_kwargs: dict = None
) -> Any:
    """
    运行回测
    
    参数:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        strategy_name: 策略名称
        starting_cash: 初始资金
        commission: 佣金比例
        engine_type: 回测引擎类型
        strategy_kwargs: 策略参数
    
    返回:
        回测结果
    """
    # 如果还没有初始化，则自动初始化
    if not _initialized:
        init()
    
    # 创建回测引擎
    if engine_type == 'backtrader':
        engine = create_backtrader_engine(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy_name=strategy_name,
            starting_cash=starting_cash,
            commission=commission,
            strategy_kwargs=strategy_kwargs
        )
    else:
        # 使用简单回测引擎
        data_provider = get_provider()
        
        # 应用策略名称映射
        mapped_strategy_name = STRATEGY_NAME_MAPPING.get(strategy_name, strategy_name)
        
        try:
            strategy = qstrategy.get_strategy(mapped_strategy_name, **(strategy_kwargs or {}))
        except Exception as e:
            # 策略未找到时的默认处理
            logger.warning(f"未找到策略 '{mapped_strategy_name}'，使用默认的SmaCrossStrategy")
            from qstrategy.strategies.sma_cross import SmaCrossStrategy
            strategy = SmaCrossStrategy(**(strategy_kwargs or {}))

        engine = SimpleLoopEngine(
            data_provider=data_provider,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy=strategy,
            starting_cash=starting_cash
        )
    
    # 运行回测
    result = engine.run()
    
    return result

# 自动初始化
if not _initialized:
    try:
        init()
    except Exception as e:
        logger.warning(f"自动初始化失败: {e}")
        logger.info("请手动调用qbackengine.init()进行初始化")

__all__ = ['BacktraderEngine', 'MultiSymbolBacktraderEngine', 'SimpleLoopEngine', 'run', 'init', 'create_backtrader_engine', 'create_multi_symbol_engine']