"""
qindicator - 一个可扩展的股票指标计算插件系统

该系统设计用于统一不同指标计算库的访问接口，提供一致的指标计算功能。
"""

import logging
from typing import List, Optional, Any, Dict, Callable
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
_current_calculator = None
_initialized = False

# 导入必要的模块
from qindicator.calculator import IndicatorCalculator
from qindicator.factory import IndicatorCalculatorFactory
# 导入indicators模块以确保指标计算器注册
import qindicator.indicators

# 初始化函数
def init() -> None:
    """
    初始化qindicator插件
    自动使用ta-lib作为默认指标计算库
    """
    global _initialized, _current_calculator
    
    _initialized = True
    
    # 默认使用ta-lib作为指标计算库
    _current_calculator = IndicatorCalculatorFactory.create_calculator('talib')
    logger.info("已自动初始化talib指标计算库")

# 获取当前指标计算器
def get_calculator() -> IndicatorCalculator:
    """
    获取当前使用的指标计算器
    
    返回:
        当前指标计算器实例
    """
    global _current_calculator
    
    if _current_calculator is None:
        # 如果还没有初始化，则自动初始化
        if not _initialized:
            init()
    
    return _current_calculator

# 切换指标计算器
def set_current_calculator(calculator_name: str) -> IndicatorCalculator:
    """
    切换当前使用的指标计算器
    
    参数:
        calculator_name: 指标计算器名称
    
    返回:
        新的指标计算器实例
    """
    global _current_calculator
    
    _current_calculator = IndicatorCalculatorFactory.create_calculator(calculator_name)
    logger.info(f"已切换指标计算器至: {calculator_name}")
    
    return _current_calculator

# 动态代理函数，将计算器的方法暴露给模块级别
def __getattr__(name: str) -> Any:
    # 如果是内置属性或已定义属性，则直接返回
    if name.startswith('__') or name in globals():
        raise AttributeError(f"module 'qindicator' has no attribute '{name}'")
        
    # 确保计算器已初始化
    calculator = get_calculator()
    
    # 尝试从计算器获取方法
    if hasattr(calculator, name):
        method = getattr(calculator, name)
        
        # 确保获取的是可调用方法
        if callable(method):
            # 创建包装函数，保留原方法的文档和签名
            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                return method(*args, **kwargs)
            
            return wrapper
    
    raise AttributeError(f"module 'qindicator' has no attribute '{name}'")