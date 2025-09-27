#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略后端管理模块
提供策略的注册、获取和管理功能
"""

import logging
from typing import Dict, Type, Optional, Any

from qstrategy.core.strategy import Strategy

logger = logging.getLogger(__name__)

# 存储已注册的策略类
_registered_strategies: Dict[str, Type[Strategy]] = {}

# 默认策略配置
_default_strategy = None


def register_strategy(name: str, strategy_class: Type[Strategy]) -> None:
    """
    注册一个策略类
    
    Args:
        name: 策略名称，用于后续获取策略实例
        strategy_class: 策略类，必须继承自Strategy基类
    
    Raises:
        TypeError: 当策略类不是Strategy的子类时
    """
    if not issubclass(strategy_class, Strategy):
        raise TypeError(f"策略类必须是Strategy的子类，当前类型: {type(strategy_class)}")
    
    if name in _registered_strategies:
        logger.warning(f"策略 '{name}' 已存在，将被覆盖")
    
    _registered_strategies[name] = strategy_class
    logger.info(f"已注册策略: {name}")


def get_strategy(name: str, **kwargs) -> Strategy:
    """
    获取指定名称的策略实例
    
    Args:
        name: 策略名称
        **kwargs: 传递给策略构造函数的参数
    
    Returns:
        Strategy: 策略实例
    
    Raises:
        ValueError: 当指定名称的策略未注册时
    """
    if name not in _registered_strategies:
        available = ', '.join(_registered_strategies.keys())
        raise ValueError(f"未找到名称为 '{name}' 的策略。可用的策略有: {available}")
    
    strategy_class = _registered_strategies[name]
    try:
        strategy_instance = strategy_class(**kwargs)
        logger.info(f"已创建策略实例: {name}")
        return strategy_instance
    except Exception as e:
        logger.error(f"创建策略 '{name}' 实例失败: {e}")
        raise


def set_default_strategy(name: str) -> None:
    """
    设置默认策略
    
    Args:
        name: 策略名称
    
    Raises:
        ValueError: 当指定名称的策略未注册时
    """
    if name not in _registered_strategies:
        available = ', '.join(_registered_strategies.keys())
        raise ValueError(f"未找到名称为 '{name}' 的策略。可用的策略有: {available}")
    
    global _default_strategy
    _default_strategy = name
    logger.info(f"已设置默认策略: {name}")


def get_default_strategy(**kwargs) -> Optional[Strategy]:
    """
    获取默认策略实例
    
    Args:
        **kwargs: 传递给策略构造函数的参数
    
    Returns:
        Optional[Strategy]: 默认策略实例，如果没有设置默认策略则返回None
    """
    if _default_strategy is None:
        logger.warning("没有设置默认策略")
        return None
    
    return get_strategy(_default_strategy, **kwargs)


def get_available_strategies() -> list:
    """
    获取所有可用的策略名称
    
    Returns:
        list: 策略名称列表
    """
    return list(_registered_strategies.keys())


def is_strategy_registered(name: str) -> bool:
    """
    检查策略是否已注册
    
    Args:
        name: 策略名称
    
    Returns:
        bool: 如果策略已注册则返回True，否则返回False
    """
    return name in _registered_strategies


def create_strategy(name: str, **kwargs) -> Strategy:
    """
    创建策略实例的别名函数
    
    Args:
        name: 策略名称
        **kwargs: 传递给策略构造函数的参数
    
    Returns:
        Strategy: 策略实例
    """
    return get_strategy(name, **kwargs)

def get_strategy_class(name: str) -> Optional[Type[Strategy]]:
    """
    获取策略类
    
    Args:
        name: 策略名称
    
    Returns:
        Optional[Type[Strategy]]: 策略类，如果策略未注册则返回None
    """
    return _registered_strategies.get(name)


# 自动注册策略
# 当模块被导入时，尝试导入并注册所有可用的策略
# 这样用户在导入qstrategy模块时，就能自动使用所有已实现的策略

def _auto_register_strategies():
    """
    自动注册所有策略
    这个函数会在模块被导入时自动执行
    """
    try:
        # 导入内置策略
        from qstrategy.backends import sma_cross, macd, rsi, bbands, pair_trading, volatility_breakout
        from qstrategy.backends import mean_reversion
        from qstrategy.backends import macd_kdj
        from qstrategy.backends import turtle
        
        # 这里不需要显式注册，每个策略模块内部应该有自注册逻辑
        logger.info("已自动导入所有内置策略")
    except ImportError as e:
        logger.warning(f"自动注册策略失败: {e}")


# 当模块被导入时自动执行策略注册
# _auto_register_strategies()
# 注意：自动注册会在qstrategy.__init__.py中显式调用