"""
indicator模块 - 定义指标计算的抽象基类
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional

class Indicator(ABC):
    """
    指标计算的抽象基类
    所有具体的指标计算器都需要实现这个接口
    """
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        计算指标
        
        Args:
            data: 要计算的数据，通常是pandas DataFrame
            **kwargs: 其他计算参数
        
        Returns:
            pd.DataFrame: 包含计算结果的DataFrame
        """
        pass
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """
        验证数据是否有效
        
        Args:
            data: 要验证的数据
        
        Returns:
            bool: 数据是否有效
        """
        # 默认检查数据是否为空以及是否包含必要的列
        if data is None or data.empty:
            return False
        
        # 检查是否包含至少'close'列
        required_columns = ['close']
        for col in required_columns:
            if col not in data.columns:
                return False
                
        return True

class DataManager:
    """
    数据管理器类
    负责准备和管理指标计算所需的数据
    """
    
    def __init__(self):
        """
        初始化数据管理器
        """
        self.data = None
    
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备数据以用于指标计算
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 准备好的数据
        """
        # 确保列名是小写的
        data = data.copy()
        data.columns = [col.lower() for col in data.columns]
        
        # 确保索引是日期类型
        if not pd.api.types.is_datetime64_any_dtype(data.index):
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data = data.set_index('date')
        
        return data