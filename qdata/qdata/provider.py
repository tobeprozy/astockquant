from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Protocol, Union
import pandas as pd
from abc import ABC, abstractmethod


class DataFrameLike(Protocol):
    def __iter__(self) -> List:
        ...


class DataProvider(ABC):
    """
    数据源提供者的抽象基类
    所有数据源适配器都需要实现这个接口
    """
    
    @abstractmethod
    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取日线数据
        
        Args:
            symbol: 证券代码
            start_date: 开始日期，格式为'YYYY-MM-DD'
            end_date: 结束日期，格式为'YYYY-MM-DD'
            
        Returns:
            DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
        """
        pass
    
    @abstractmethod
    def get_minute_data(self, symbol: str, start_time: str, end_time: str, frequency: str = '1') -> pd.DataFrame:
        """
        获取分时数据
        
        Args:
            symbol: 证券代码
            start_time: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
            end_time: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
            frequency: 时间频率，例如'1'表示1分钟，'5'表示5分钟等
            
        Returns:
            DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
        """
        pass
    
    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            DataFrame: 包含股票代码、名称等信息的DataFrame
        """
        pass
    
    @abstractmethod
    def get_etf_list(self) -> pd.DataFrame:
        """
        获取ETF列表
        
        Returns:
            DataFrame: 包含ETF代码、名称等信息的DataFrame
        """
        pass
    
    def format_data(self, df: pd.DataFrame, data_type: str = 'daily') -> pd.DataFrame:
        """
        格式化数据为统一格式
        
        Args:
            df: 原始数据DataFrame
            data_type: 数据类型，'daily'或'minute'
            
        Returns:
            DataFrame: 格式化后的DataFrame
        """
        # 这里实现统一的数据格式化逻辑
        # 确保返回的DataFrame包含以下列：date, open, high, low, close, volume
        # 并设置date列为索引
        
        # 默认实现，子类可以覆盖
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        
        # 确保列名符合规范
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        if not required_columns.issubset(df.columns):
            # 尝试进行列名映射，子类应该根据具体数据源实现更精确的映射
            pass
        
        return df
