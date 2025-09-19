"""
策略工厂模块
提供统一的策略创建接口
"""

from typing import Dict, Type, Optional
import logging

from qstrategy.strategy import StrategyBase

logger = logging.getLogger(__name__)

class StrategyFactory:
    """
    策略工厂类
    负责管理和创建不同的策略实例
    """
    # 存储已注册的策略类
    _registered_strategies: Dict[str, Type[StrategyBase]] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[StrategyBase]) -> None:
        """
        注册一个新的策略类
        
        Args:
            name: 策略名称，用于后续创建实例
            strategy_class: 策略类
        """
        if name in cls._registered_strategies:
            logger.warning(f"策略 '{name}' 已存在，将被覆盖")
        cls._registered_strategies[name] = strategy_class
        logger.info(f"已注册策略: {name}")
    
    # 添加register方法作为register_strategy的别名
    @classmethod
    def register(cls, name: str, strategy_class: Type[StrategyBase]) -> None:
        """
        register方法是register_strategy的别名
        
        Args:
            name: 策略名称，用于后续创建实例
            strategy_class: 策略类
        """
        cls.register_strategy(name, strategy_class)

    @classmethod
    def create_strategy(cls, name: str, **kwargs) -> StrategyBase:
        """
        创建指定名称的策略实例
        
        Args:
            name: 策略名称
            **kwargs: 传递给策略构造函数的参数
            
        Returns:
            策略实例
            
        Raises:
            ValueError: 当指定名称的策略未注册时
        """
        if name not in cls._registered_strategies:
            available = ', '.join(cls._registered_strategies.keys())
            raise ValueError(f"未找到名称为 '{name}' 的策略。可用的策略有: {available}")
        
        strategy_class = cls._registered_strategies[name]
        return strategy_class(**kwargs)

    @classmethod
    def get_available_strategies(cls) -> list:
        """
        获取所有可用的策略名称
        
        Returns:
            策略名称列表
        """
        return list(cls._registered_strategies.keys())

    @classmethod
    def get_strategy_class(cls, name: str) -> Optional[Type[StrategyBase]]:
        """
        获取指定名称的策略类
        
        Args:
            name: 策略名称
            
        Returns:
            策略类，如果不存在则返回None
        """
        return cls._registered_strategies.get(name)