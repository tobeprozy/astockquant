"""
指标计算器工厂模块
提供统一的指标计算器创建接口
"""

from typing import Dict, Type, Optional
import logging

from qindicator.calculator import IndicatorCalculator

logger = logging.getLogger(__name__)

class IndicatorCalculatorFactory:
    """
    指标计算器工厂类
    负责管理和创建不同的指标计算器实例
    """
    # 存储已注册的计算器类
    _registered_calculators: Dict[str, Type[IndicatorCalculator]] = {}

    @classmethod
    def register_calculator(cls, name: str, calculator_class: Type[IndicatorCalculator]) -> None:
        """
        注册一个新的指标计算器类
        
        Args:
            name: 计算器名称，用于后续创建实例
            calculator_class: 计算器类
        """
        if name in cls._registered_calculators:
            logger.warning(f"指标计算器 '{name}' 已存在，将被覆盖")
        cls._registered_calculators[name] = calculator_class
        logger.info(f"已注册指标计算器: {name}")
    
    # 添加register方法作为register_calculator的别名
    @classmethod
    def register(cls, name: str, calculator_class: Type[IndicatorCalculator]) -> None:
        """
        register方法是register_calculator的别名
        
        Args:
            name: 计算器名称，用于后续创建实例
            calculator_class: 计算器类
        """
        cls.register_calculator(name, calculator_class)

    @classmethod
    def create_calculator(cls, name: str, **kwargs) -> IndicatorCalculator:
        """
        创建指定名称的指标计算器实例
        
        Args:
            name: 计算器名称
            **kwargs: 传递给计算器构造函数的参数
            
        Returns:
            指标计算器实例
            
        Raises:
            ValueError: 当指定名称的计算器未注册时
        """
        if name not in cls._registered_calculators:
            available = ', '.join(cls._registered_calculators.keys())
            raise ValueError(f"未找到名称为 '{name}' 的指标计算器。可用的计算器有: {available}")
        
        calculator_class = cls._registered_calculators[name]
        return calculator_class(**kwargs)

    @classmethod
    def get_available_calculators(cls) -> list:
        """
        获取所有可用的指标计算器名称
        
        Returns:
            计算器名称列表
        """
        return list(cls._registered_calculators.keys())

    @classmethod
    def get_calculator_class(cls, name: str) -> Optional[Type[IndicatorCalculator]]:
        """
        获取指定名称的指标计算器类
        
        Args:
            name: 计算器名称
            
        Returns:
            计算器类，如果不存在则返回None
        """
        return cls._registered_calculators.get(name)