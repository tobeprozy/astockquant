"""
qstrategy - 一个可扩展的股票策略插件系统

该系统设计用于统一不同策略的管理和执行接口，提供一致的策略使用体验。
"""

import logging
from typing import List, Optional, Any, Dict, Callable, Type
import pandas as pd
from datetime import datetime
import inspect
import functools

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 版本信息
__version__ = "0.1.0"
__author__ = "AstockQuant Team"

# 全局变量
_current_strategy = None
_initialized = False
_current_engine = None

# 导入必要的模块
from qstrategy.core.strategy import Strategy
from qstrategy.backends import (
    register_strategy as _register_strategy,
    get_strategy as _get_strategy,
    get_available_strategies as _get_available_strategies,
    _auto_register_strategies
)

# 策略通过backends模块的注册机制进行管理
# 用户可以通过get_strategy()函数获取策略实例

# 自动注册内置策略
_auto_register_strategies()

# 初始化函数
def init(engine_type: str = 'simple') -> None:
    """
    初始化qstrategy插件
    
    参数:
        engine_type: 回测引擎类型，默认为'simple'
    """
    global _initialized, _current_engine
    
    _initialized = True
    
    # 创建并设置默认回测引擎
    if engine_type == 'backtrader':
        _current_engine = create_backtrader_engine()
    else:
        _current_engine = None
        
    logger.info(f"已初始化qstrategy插件，引擎类型: {engine_type}")
    logger.info(f"可用策略: {', '.join(_get_available_strategies())}")

# 获取当前策略
def get_strategy(name: str = None, **kwargs) -> Strategy:
    """
    获取指定名称的策略实例或当前策略
    
    参数:
        name: 策略名称，如果为None则返回当前策略
        **kwargs: 传递给策略构造函数的参数
        
    返回:
        策略实例
    """
    global _current_strategy
    
    if name is not None:
        # 创建并设置指定名称的策略
        _current_strategy = _get_strategy(name, **kwargs)
        logger.info(f"已切换至策略: {name}")
    elif _current_strategy is None:
        # 如果还没有初始化策略，则初始化默认策略
        if not _initialized:
            init()
        
        # 获取可用的第一个策略
        available_strategies = _get_available_strategies()
        if available_strategies:
            _current_strategy = _get_strategy(available_strategies[0])
            logger.info(f"已自动选择默认策略: {available_strategies[0]}")
        else:
            logger.warning("没有可用的策略")
    
    return _current_strategy

# 注册自定义策略
def register_strategy(name: str, strategy_class: Type[Strategy]) -> None:
    """
    注册自定义策略
    
    参数:
        name: 策略名称
        strategy_class: 策略类
    """
    _register_strategy(name, strategy_class)

# 创建backtrader回测引擎
def create_backtrader_engine() -> Any:
    """
    创建backtrader回测引擎
    
    返回:
        backtrader.Cerebro实例
    """
    try:
        import backtrader as bt
        return bt.Cerebro()
    except ImportError:
        logger.error("无法导入backtrader模块，请先安装: pip install backtrader")
        raise

# 添加数据到回测引擎
def add_data_to_engine(engine: Any, df: pd.DataFrame, name: str = 'stock') -> None:
    """
    添加数据到回测引擎
    
    参数:
        engine: 回测引擎实例
        df: 包含股票数据的DataFrame
        name: 数据名称
    """
    try:
        import backtrader as bt
        # 创建backtrader数据源
        data_feed = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为时间
            open=0, high=1, low=2, close=3, volume=4, openinterest=-1
        )
        data_feed._name = name
        engine.adddata(data_feed)
    except Exception as e:
        logger.error(f"添加数据到引擎时出错: {e}")
        raise

# 添加策略到回测引擎
def add_strategy_to_engine(engine: Any, strategy_name: str, **kwargs) -> None:
    """
    添加策略到回测引擎
    
    参数:
        engine: 回测引擎实例
        strategy_name: 策略名称
        **kwargs: 传递给策略的参数
    """
    try:
        from qstrategy.backends import get_strategy_class
        strategy_class = get_strategy_class(strategy_name)
        if strategy_class:
            engine.addstrategy(strategy_class, **kwargs)
        else:
            raise ValueError(f"未找到名称为 '{strategy_name}' 的策略")
    except Exception as e:
        logger.error(f"添加策略到引擎时出错: {e}")
        raise

# 获取当前回测引擎
def get_engine() -> Any:
    """
    获取当前回测引擎实例
    
    返回:
        回测引擎实例
    """
    global _current_engine
    
    if _current_engine is None:
        # 如果还没有初始化引擎，则自动初始化
        if not _initialized:
            init()
    
    return _current_engine

# 动态代理函数，将常用方法暴露给模块级别
def __getattr__(name: str) -> Any:
    # 如果是内置属性或已定义属性，则直接返回
    if name.startswith('__') or name in globals():
        raise AttributeError(f"module 'qstrategy' has no attribute '{name}'")
        
    # 确保策略已初始化
    strategy = get_strategy()
    
    # 尝试从策略获取方法
    if hasattr(strategy, name):
        method = getattr(strategy, name)
        
        # 确保获取的是可调用方法
        if callable(method):
            # 创建包装函数，保留原方法的文档和签名
            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                return method(*args, **kwargs)
            
            return wrapper
    
    raise AttributeError(f"module 'qstrategy' has no attribute '{name}'")