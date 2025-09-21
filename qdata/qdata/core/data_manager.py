"""
数据管理模块
负责数据准备和管理，确保数据格式统一
"""
import pandas as pd
from typing import Optional, Union


class DataManager:
    """
    数据管理器
    负责数据准备、清洗和格式统一
    """
    
    @staticmethod
    def prepare_data(df: pd.DataFrame, data_type: str = 'daily') -> pd.DataFrame:
        """
        准备数据，确保数据格式统一
        
        Args:
            df: 原始数据DataFrame
            data_type: 数据类型，如'daily'或'minute'
            
        Returns:
            pd.DataFrame: 准备好的数据
        """
        # 复制原始数据，避免修改原数据
        prepared_df = df.copy()
        
        # 确保所有列名都是小写
        prepared_df.columns = [col.lower() for col in prepared_df.columns]
        
        # 确保日期索引
        if 'date' in prepared_df.columns:
            prepared_df['date'] = pd.to_datetime(prepared_df['date'])
            prepared_df = prepared_df.set_index('date')
        elif 'datetime' in prepared_df.columns:
            prepared_df['datetime'] = pd.to_datetime(prepared_df['datetime'])
            prepared_df = prepared_df.set_index('datetime')
        
        # 确保数据列存在
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        if not required_columns.issubset(prepared_df.columns):
            # 尝试进行列名映射
            column_mapping = {
                '开盘': 'open', '开盘价': 'open',
                '最高': 'high', '最高价': 'high',
                '最低': 'low', '最低价': 'low',
                '收盘': 'close', '收盘价': 'close',
                '成交量': 'volume', '成交额': 'volume'
            }
            
            # 检查并映射列名
            for old_col, new_col in column_mapping.items():
                if old_col.lower() in prepared_df.columns and new_col not in prepared_df.columns:
                    prepared_df[new_col] = prepared_df[old_col.lower()]
        
        # 确保数据类型正确
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in prepared_df.columns:
                prepared_df[col] = pd.to_numeric(prepared_df[col], errors='coerce')
        
        # 删除重复行
        prepared_df = prepared_df.drop_duplicates()
        
        # 按日期排序
        prepared_df = prepared_df.sort_index()
        
        return prepared_df
    
    @staticmethod
    def validate_data(df: pd.DataFrame, data_type: str = 'daily') -> bool:
        """
        验证数据是否有效
        
        Args:
            df: 要验证的数据DataFrame
            data_type: 数据类型，如'daily'或'minute'
            
        Returns:
            bool: 数据是否有效
        """
        # 检查是否为空
        if df.empty:
            return False
        
        # 检查必要的列
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        if not required_columns.issubset(df.columns):
            return False
        
        # 检查数据完整性
        if df[list(required_columns)].isnull().all().any():
            return False
        
        # 检查索引是否为日期类型
        if not isinstance(df.index, pd.DatetimeIndex):
            return False
        
        return True

__all__ = ['DataManager']