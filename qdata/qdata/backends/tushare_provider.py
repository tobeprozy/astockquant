"""
TuShare数据源后端
使用tushare库获取股票和ETF数据
"""
import time
from typing import Optional
import pandas as pd
import tushare as ts

from qdata.provider import DataProvider
from qdata.backends import register_backend


class TuShareProvider(DataProvider):
    """
    TuShare数据源提供者
    使用tushare库获取股票和ETF数据
    """
    
    def __init__(self, token: str = None, retry_count: int = 3, retry_delay: list = None):
        """
        初始化TuShareProvider
        
        Args:
            token: TuShare API token
            retry_count: 重试次数
            retry_delay: 重试延迟时间列表（秒）
        """
        self.retry_count = retry_count
        self.retry_delay = retry_delay or [1, 2, 3]
        
        # 初始化tushare
        if token:
            ts.set_token(token)
        
        # 初始化pro接口
        self.pro = ts.pro_api()
    
    def get_daily_data(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取日线数据
        
        Args:
            symbol: 证券代码
            start_date: 开始日期，格式为'YYYY-MM-DD'
            end_date: 结束日期，格式为'YYYY-MM-DD'
            **kwargs: 额外参数
            
        Returns:
            DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
        """
        # 尝试获取股票或ETF数据
        last_err = None
        
        # 格式化日期
        start_date_fmt = start_date.replace('-', '')
        end_date_fmt = end_date.replace('-', '')
        
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 尝试获取股票数据
                df = ts.pro_bar(ts_code=symbol, adj='qfq', 
                                start_date=start_date_fmt, end_date=end_date_fmt)
                
                if not df.empty:
                    # 检查是否是ETF数据
                    if df['ts_code'].str.startswith(('51', '58', '15', '16')).any():
                        # ETF数据处理
                        return self._format_tushare_data(df, data_type='fund')
                    else:
                        # 股票数据处理
                        return self._format_tushare_data(df, data_type='stock')
                
            except Exception as e:
                last_err = e
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        # 如果所有重试都失败，抛出异常
        raise RuntimeError(
            f"获取数据失败: {symbol} (从 {start_date} 到 {end_date})"
        ) from last_err
    
    def get_minute_data(self, symbol: str, start_time: str, end_time: str, frequency: str = '1', **kwargs) -> pd.DataFrame:
        """
        获取分时数据
        
        Args:
            symbol: 证券代码
            start_time: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
            end_time: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
            frequency: 时间频率，例如'1'表示1分钟，'5'表示5分钟等
            **kwargs: 额外参数
            
        Returns:
            DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
        """
        last_err = None
        
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 使用tushare的get_k_data获取分钟数据
                df = ts.get_k_data(symbol, start=start_time, end=end_time, ktype=frequency)
                
                if not df.empty:
                    return self._format_tushare_data(df, data_type='minute')
                
            except Exception as e:
                last_err = e
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError(
            f"获取分钟数据失败: {symbol} (从 {start_time} 到 {end_time}, 频率: {frequency}分钟)"
        ) from last_err
    
    def get_stock_list(self, **kwargs) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            DataFrame: 包含股票代码、名称等信息的DataFrame
        """
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 获取A股列表
                df = self.pro.stock_basic(exchange='', list_status='L', 
                                         fields='ts_code,symbol,name,area,industry,list_date')
                
                if not df.empty:
                    # 重命名列，确保符合统一接口
                    if 'ts_code' in df.columns and 'name' in df.columns:
                        df = df.rename(columns={'ts_code': 'code'})
                        return df[['code', 'name']]
                    return df
                
            except Exception as e:
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError("获取股票列表失败")
    
    def get_etf_list(self, **kwargs) -> pd.DataFrame:
        """
        获取ETF列表
        
        Returns:
            DataFrame: 包含ETF代码、名称等信息的DataFrame
        """
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 获取ETF列表
                df = self.pro.fund_basic(market='E', 
                                        fields='ts_code,name,fund_type,issue_date,list_date')
                
                if not df.empty:
                    # 重命名列，确保符合统一接口
                    if 'ts_code' in df.columns and 'name' in df.columns:
                        df = df.rename(columns={'ts_code': 'code'})
                        return df[['code', 'name']]
                    return df
                
            except Exception as e:
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError("获取ETF列表失败")
    
    def _format_tushare_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        格式化tushare返回的数据为统一格式
        
        Args:
            df: tushare返回的原始数据
            data_type: 数据类型，如'stock', 'fund', 'minute'
            
        Returns:
            DataFrame: 格式化后的数据
        """
        # 定义列名映射
        column_mapping = {
            'trade_date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'amount': 'amount'
        }
        
        # 对于分钟数据，列名可能不同
        if data_type == 'minute':
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
        
        # 重命名列
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # 确保'date'列为datetime类型
        if 'date' in df.columns:
            # 处理tushare的日期格式
            if data_type != 'minute' and isinstance(df['date'].iloc[0], str) and len(df['date'].iloc[0]) == 8:
                # 如果是YYYYMMDD格式
                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            else:
                df['date'] = pd.to_datetime(df['date'])
            
            df = df.set_index('date')
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                # 尝试从其他可能的列名中获取或设置默认值
                pass
        
        # 对于tushare的数据，需要按日期排序
        if not df.empty:
            df = df.sort_index()
        
        # 只返回需要的列
        available_columns = [col for col in required_columns if col in df.columns]
        return df[available_columns]

# 注册后端
register_backend('tushare', TuShareProvider)

__all__ = ['TuShareProvider']