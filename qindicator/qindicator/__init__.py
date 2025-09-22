"""
qindicator - 一个可扩展的股票指标计算插件系统

该系统设计用于统一不同指标计算库的访问接口，提供一致的指标计算功能。
"""

import logging
from typing import Optional
import pandas as pd

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 版本信息
__version__ = "0.1.0"
__author__ = "AstockQuant Team"

# 导入实际存在的模块
from qindicator.backends.talib.indicator import TalibIndicator as TalibIndicatorCalculator

# 快捷工厂函数，用于获取指标计算器实例
def get_indicator_calculator(calculator_type: str = "talib") -> Optional[TalibIndicatorCalculator]:
    """
    获取指标计算器实例
    
    参数:
        calculator_type: 计算器类型，当前仅支持"talib"
        
    返回:
        指标计算器实例
    """
    if calculator_type.lower() == "talib":
        return TalibIndicatorCalculator()
    else:
        logger.error(f"不支持的计算器类型: {calculator_type}")
        return None


# 定义模块导出列表
__all__ = [
    'TalibIndicatorCalculator',
    'get_indicator_calculator'
]