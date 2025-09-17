import sys
import os
import time
from typing import Optional
import pandas as pd
import tushare as ts

from qdata.provider import DataProvider


class TuShareProvider(DataProvider):
    """
    TuShare数据源提供者
    使用tushare库获取股票和ETF数据
    """
    
    def __init__(self, token: Optional[str] = None, retry_count: int = 5, retry_delay: list = None):
        """
        初始化TuShareProvider
        
        Args:
            token: tushare的API令牌
            retry_count: 重试次数
            retry_delay: 重试延迟时间列表（秒）
        """
        self.retry_count = retry_count
        self.retry_delay = retry_delay or [1, 2, 4, 8, 10]
        
        # 设置tushare令牌
        if token:
            ts.set_token(token)
        else:
            # 尝试从环境变量获取
            token = os.environ.get('TUSHARE_TOKEN')
            if token:
                ts.set_token(token)
        
        # 初始化pro接口
        try:
            self.pro = ts.pro_api()
        except Exception:
            # 如果pro接口初始化失败，使用旧版接口
            self.pro = None
    
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
        last_err = None
        
        # 格式化日期为tushare所需的格式
        start_date_fmt = start_date.replace('-', '')
        end_date_fmt = end_date.replace('-', '')
        
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 尝试使用pro接口
                if self.pro:
                    try:
                        # 对于pro接口，需要添加市场后缀
                        if not (symbol.endswith('.SH') or symbol.endswith('.SZ') or \
                                symbol.endswith('.BJ')):
                            # 尝试自动判断市场
                            if symbol.startswith('6'):
                                ts_code = f"{symbol}.SH"
                            elif symbol.startswith('3') or symbol.startswith('0'):
                                ts_code = f"{symbol}.SZ"
                            elif symbol.startswith('8') or symbol.startswith('4'):
                                ts_code = f"{symbol}.BJ"
                            else:
                                ts_code = symbol  # 无法判断，保持原样
                        else:
                            ts_code = symbol
                        
                        df = self.pro.daily(ts_code=ts_code, start_date=start_date_fmt, end_date=end_date_fmt)
                        
                        if not df.empty:
                            return self._format_tushare_pro_data(df)
                    except Exception:
                        # 如果pro接口失败，尝试使用旧版接口
                        pass
                
                # 使用旧版接口
                df = ts.get_k_data(symbol, start=start_date, end=end_date, autype='qfq')
                
                if not df.empty:
                    return self._format_tushare_legacy_data(df)
                
            except Exception as e:
                last_err = e
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        # 如果所有重试都失败，抛出异常
        raise RuntimeError(
            f"获取数据失败: {symbol} (从 {start_date} 到 {end_date})"
        ) from last_err
    
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
        last_err = None
        
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 注意：tushare的分钟数据接口可能需要付费权限
                # 这里使用get_k_data并指定ktype参数来获取分钟数据
                ktype = f'{frequency}min'
                
                # 解析开始和结束时间
                start_date = start_time.split(' ')[0] if ' ' in start_time else start_time
                end_date = end_time.split(' ')[0] if ' ' in end_time else end_time
                
                df = ts.get_k_data(symbol, start=start_date, end=end_date, ktype=ktype)
                
                if not df.empty:
                    # 对于分钟数据，需要将date列解析为datetime
                    df['date'] = pd.to_datetime(df['date'])
                    return self._format_tushare_legacy_data(df)
                
            except Exception as e:
                last_err = e
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError(
            f"获取分钟数据失败: {symbol} (从 {start_time} 到 {end_time}, 频率: {frequency}分钟)"
        ) from last_err
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            DataFrame: 包含股票代码、名称等信息的DataFrame
        """
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 尝试使用pro接口
                if self.pro:
                    try:
                        # 获取A股列表
                        df = self.pro.stock_basic(exchange='', list_status='L', 
                                                 fields='ts_code,symbol,name,area,industry,list_date')
                        if not df.empty:
                            # 重命名列以符合统一格式
                            df = df.rename(columns={'symbol': 'code', 'name': 'name'})
                            return df[['code', 'name']]
                    except Exception:
                        # 如果pro接口失败，尝试其他方式
                        pass
                
                # 使用get_stock_basics（旧版接口）
                df = ts.get_stock_basics()
                if not df.empty:
                    # 旧版接口返回的DataFrame索引是股票代码
                    df = df.reset_index()
                    df = df.rename(columns={'index': 'code', 'name': 'name'})
                    return df[['code', 'name']]
                
            except Exception as e:
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError("获取股票列表失败")
    
    def get_etf_list(self) -> pd.DataFrame:
        """
        获取ETF列表
        
        Returns:
            DataFrame: 包含ETF代码、名称等信息的DataFrame
        """
        # 重试逻辑
        for i in range(self.retry_count):
            try:
                # 尝试使用pro接口获取ETF列表
                if self.pro:
                    try:
                        # 获取ETF列表
                        df = self.pro.fund_basic(market='E', 
                                                fields='ts_code,symbol,name,issue_date,fund_type')
                        if not df.empty:
                            # 重命名列以符合统一格式
                            df = df.rename(columns={'symbol': 'code', 'name': 'name'})
                            return df[['code', 'name']]
                    except Exception:
                        # 如果pro接口失败，尝试其他方式
                        pass
                
                # 使用get_k_data获取ETF数据（作为获取列表的一种方式）
                # 这里只是一个示例，实际使用时可能需要更精确的方法
                # 注意：tushare的ETF列表获取可能需要特定的接口或权限
                # 由于缺乏直接的ETF列表接口，这里返回一个空的DataFrame
                # 用户可能需要使用其他方式获取ETF列表
                
            except Exception as e:
                if i < self.retry_count - 1:
                    time.sleep(self.retry_delay[i] if i < len(self.retry_delay) else self.retry_delay[-1])
                continue
        
        raise RuntimeError("获取ETF列表失败")
    
    def _format_tushare_pro_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        格式化tushare pro接口返回的数据
        
        Args:
            df: tushare pro接口返回的原始数据
            
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
                pass
        
        # 只返回需要的列
        available_columns = [col for col in required_columns if col in df.columns]
        return df[available_columns]
    
    def _format_tushare_legacy_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        格式化tushare旧版接口返回的数据
        
        Args:
            df: tushare旧版接口返回的原始数据
            
        Returns:
            DataFrame: 格式化后的数据
        """
        # 定义列名映射
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
            # 对于旧版接口，date列可能已经是字符串格式
            if not pd.api.types.is_datetime64_any_dtype(df['date']):
                df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                # 尝试从其他可能的列名中获取或设置默认值
                pass
        
        # 只返回需要的列
        available_columns = [col for col in required_columns if col in df.columns]
        return df[available_columns]

# 注册到工厂
from ..factory import DataProviderFactory
DataProviderFactory.register('tushare', TuShareProvider)