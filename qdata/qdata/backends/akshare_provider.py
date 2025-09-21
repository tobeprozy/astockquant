"""
AkShare数据源后端
使用akshare库获取股票和ETF数据
"""
import sys
import time
from typing import Optional
import pandas as pd
import akshare as ak

from qdata.provider import DataProvider
from qdata.backends import register_backend


class AkShareProvider(DataProvider):
    """
    AkShare数据源提供者
    使用akshare库获取股票和ETF数据
    """
    
    def __init__(self, retry_count: int = 5, retry_delay: list = None):
        """
        初始化AkShareProvider
        
        Args:
            retry_count: 重试次数
            retry_delay: 重试延迟时间列表（秒）
        """
        self.retry_count = retry_count
        self.retry_delay = retry_delay or [1, 2, 4, 8, 10]
    
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
        
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 尝试获取ETF数据
                try:
                    # 格式化日期为akshare所需的格式
                    start_date_fmt = start_date.replace('-', '')
                    end_date_fmt = end_date.replace('-', '')
                    
                    df = ak.fund_etf_hist_em(
                        symbol=symbol,
                        period="daily",
                        start_date=start_date_fmt,
                        end_date=end_date_fmt,
                        adjust="qfq"
                    )
                    
                    # 检查数据是否有效
                    if not df.empty:
                        return self._format_akshare_data(df, data_type='fund')
                except Exception:
                    # 如果ETF数据获取失败，尝试获取股票数据
                    df = ak.stock_zh_a_hist(
                        symbol=symbol,
                        period="daily",
                        start_date=start_date_fmt,
                        end_date=end_date_fmt,
                        adjust="qfq"
                    )
                    
                    if not df.empty:
                        return self._format_akshare_data(df, data_type='stock')
                
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
                # 尝试获取ETF分钟数据
                try:
                    df = ak.fund_etf_hist_min_em(
                        symbol=symbol,
                        period=frequency,
                        start_date=start_time,
                        end_date=end_time,
                        adjust=""
                    )
                    
                    if not df.empty:
                        return self._format_akshare_data(df, data_type='fund_minute')
                except Exception:
                    # 如果ETF分钟数据获取失败，尝试获取股票分钟数据
                    df = ak.stock_zh_a_hist_min_em(
                        symbol=symbol,
                        period=frequency,
                        start_date=start_time,
                        end_date=end_time,
                        adjust=""
                    )
                    
                    if not df.empty:
                        return self._format_akshare_data(df, data_type='stock_minute')
                
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
                df = ak.stock_zh_a_spot_em()
                # 选择主要列并标准化列名
                if not df.empty:
                    # 确保列名正确
                    if '代码' in df.columns and '名称' in df.columns:
                        df = df.rename(columns={'代码': 'code', '名称': 'name'})
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
                df = ak.fund_name_em()
                # 选择主要列并标准化列名
                if not df.empty:
                    # 确保列名正确
                    if '基金代码' in df.columns and '基金简称' in df.columns:
                        df = df.rename(columns={'基金代码': 'code', '基金简称': 'name'})
                        return df[['code', 'name']]
                    return df
            except Exception as e:
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError("获取ETF列表失败")
    
    def _format_akshare_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        格式化akshare返回的数据为统一格式
        
        Args:
            df: akshare返回的原始数据
            data_type: 数据类型，如'stock', 'fund', 'stock_minute', 'fund_minute'
            
        Returns:
            DataFrame: 格式化后的数据
        """
        # 定义列名映射
        column_mapping = {
            '日期': 'date',
            '时间': 'date',  # 分钟数据使用'时间'列作为日期
            '开盘': 'open',
            '开盘价': 'open',
            '最高': 'high',
            '最高价': 'high',
            '最低': 'low',
            '最低价': 'low',
            '收盘': 'close',
            '收盘价': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        
        # 重命名列
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # 确保'date'列为datetime类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                # 尝试从其他可能的列名中获取或设置默认值
                # 这里可以根据实际情况添加更多的逻辑
                pass
        
        # 只返回需要的列
        available_columns = [col for col in required_columns if col in df.columns]
        return df[available_columns]

# 注册后端
register_backend('akshare', AkShareProvider)

__all__ = ['AkShareProvider']