"""
CSV数据源后端
从CSV文件读取股票和ETF数据
"""
import os
import pandas as pd
from typing import Optional, Dict, List

from qdata.provider import DataProvider
from qdata.backends import register_backend


class CSVProvider(DataProvider):
    """
    CSV数据源提供者
    从CSV文件读取股票和ETF数据
    """
    
    def __init__(self, data_dir: str = './data', file_pattern: str = '{symbol}.csv'):
        """
        初始化CSVProvider
        
        Args:
            data_dir: CSV数据文件存放目录
            file_pattern: 文件名模式，使用{symbol}作为占位符
        """
        self.data_dir = data_dir
        self.file_pattern = file_pattern
        
        # 确保数据目录存在
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_daily_data(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        从CSV文件获取日线数据
        
        Args:
            symbol: 证券代码
            start_date: 开始日期，格式为'YYYY-MM-DD'
            end_date: 结束日期，格式为'YYYY-MM-DD'
            **kwargs: 额外参数
            
        Returns:
            DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
        """
        # 构建文件路径
        file_path = os.path.join(self.data_dir, self.file_pattern.format(symbol=symbol))
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到数据文件: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 格式化数据
        df = self._format_csv_data(df)
        
        # 筛选日期范围
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            df = df.set_index('date')
        elif isinstance(df.index, pd.DatetimeIndex):
            df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
    
    def get_minute_data(self, symbol: str, start_time: str, end_time: str, frequency: str = '1', **kwargs) -> pd.DataFrame:
        """
        从CSV文件获取分时数据
        
        Args:
            symbol: 证券代码
            start_time: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
            end_time: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
            frequency: 时间频率，例如'1'表示1分钟，'5'表示5分钟等
            **kwargs: 额外参数
            
        Returns:
            DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
        """
        # 构建文件路径（分钟数据使用不同的文件模式）
        minute_file_pattern = kwargs.get('minute_file_pattern', '{}_min{}.csv')
        file_path = os.path.join(self.data_dir, minute_file_pattern.format(symbol, frequency))
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 尝试使用默认模式
            file_path = os.path.join(self.data_dir, f'{symbol}_min{frequency}.csv')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"找不到分钟数据文件: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 格式化数据
        df = self._format_csv_data(df)
        
        # 筛选时间范围
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= start_time) & (df['date'] <= end_time)]
            df = df.set_index('date')
        elif isinstance(df.index, pd.DatetimeIndex):
            df = df[(df.index >= start_time) & (df.index <= end_time)]
        
        return df
    
    def get_stock_list(self, **kwargs) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            DataFrame: 包含股票代码、名称等信息的DataFrame
        """
        # 尝试从stock_list.csv文件读取股票列表
        file_path = os.path.join(self.data_dir, 'stock_list.csv')
        
        if not os.path.exists(file_path):
            # 如果没有股票列表文件，尝试从数据目录中获取所有CSV文件
            stock_files = [f for f in os.listdir(self.data_dir) 
                          if f.endswith('.csv') and not f.endswith('_min.csv') and not f.startswith('stock_list')]
            
            # 提取股票代码
            stocks = []
            for file in stock_files:
                # 从文件名中提取股票代码
                symbol = file.split('.')[0]
                # 如果文件名符合模式，尝试提取股票代码
                try:
                    if '{symbol}' in self.file_pattern:
                        # 这是一个简单的提取方法，可能需要根据实际的file_pattern进行调整
                        symbol = file.replace('.csv', '')
                except:
                    pass
                
                stocks.append({'code': symbol, 'name': symbol})  # 没有名称信息，使用代码作为名称
            
            if stocks:
                return pd.DataFrame(stocks)
            else:
                raise FileNotFoundError("找不到股票列表文件，且数据目录中没有CSV文件")
        
        # 读取股票列表文件
        df = pd.read_csv(file_path)
        
        # 确保列名符合统一接口
        if 'code' not in df.columns and '股票代码' in df.columns:
            df = df.rename(columns={'股票代码': 'code'})
        
        if 'name' not in df.columns and '股票名称' in df.columns:
            df = df.rename(columns={'股票名称': 'name'})
        
        # 确保至少包含code和name列
        if 'code' in df.columns:
            if 'name' not in df.columns:
                df['name'] = df['code']
            return df[['code', 'name']]
        
        raise ValueError("股票列表文件必须包含code列")
    
    def get_etf_list(self, **kwargs) -> pd.DataFrame:
        """
        获取ETF列表
        
        Returns:
            DataFrame: 包含ETF代码、名称等信息的DataFrame
        """
        # 尝试从etf_list.csv文件读取ETF列表
        file_path = os.path.join(self.data_dir, 'etf_list.csv')
        
        if not os.path.exists(file_path):
            # 如果没有ETF列表文件，返回空DataFrame或尝试从股票列表中筛选
            # 这里简单地返回空DataFrame
            return pd.DataFrame(columns=['code', 'name'])
        
        # 读取ETF列表文件
        df = pd.read_csv(file_path)
        
        # 确保列名符合统一接口
        if 'code' not in df.columns and '基金代码' in df.columns:
            df = df.rename(columns={'基金代码': 'code'})
        
        if 'name' not in df.columns and '基金名称' in df.columns:
            df = df.rename(columns={'基金名称': 'name'})
        
        # 确保至少包含code和name列
        if 'code' in df.columns:
            if 'name' not in df.columns:
                df['name'] = df['code']
            return df[['code', 'name']]
        
        raise ValueError("ETF列表文件必须包含code列")
    
    def _format_csv_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        格式化CSV文件中的数据为统一格式
        
        Args:
            df: 从CSV文件读取的原始数据
            
        Returns:
            DataFrame: 格式化后的数据
        """
        # 定义列名映射
        column_mapping = {
            'date': 'date',
            'datetime': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'vol': 'volume',
            'amount': 'amount'
        }
        
        # 转换列名为小写，以便统一处理
        df.columns = [col.lower() for col in df.columns]
        
        # 重命名列
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # 确保'date'列为datetime类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                # 如果缺少必要的列，尝试设置默认值
                if col == 'volume':
                    df[col] = 0
                else:
                    # 对于价格相关的列，使用close列的值
                    if 'close' in df.columns:
                        df[col] = df['close']
                    else:
                        df[col] = 0
        
        # 按日期排序
        if 'date' in df.columns:
            df = df.sort_values('date')
        
        return df

# 注册后端
register_backend('csv', CSVProvider)

__all__ = ['CSVProvider']