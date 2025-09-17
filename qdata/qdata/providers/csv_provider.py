import os
from typing import Optional
import pandas as pd

from qdata.provider import DataProvider


class CSVProvider(DataProvider):
    """
    CSV数据源提供者
    从本地CSV文件获取股票和ETF数据
    """
    
    def __init__(self, data_dir: str = './data', date_format: Optional[str] = '%Y-%m-%d'):
        """
        初始化CSVProvider
        
        Args:
            data_dir: CSV数据文件所在的目录，默认为'./data'
            date_format: 日期格式字符串
        """
        self.data_dir = data_dir
        self.date_format = date_format
        
        # 确保数据目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"创建CSV数据目录: {self.data_dir}")
    
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
        # 构建文件路径
        file_path = os.path.join(self.data_dir, f"{symbol}_daily.csv")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"日线数据文件不存在: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 格式化日期
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format=self.date_format)
        elif 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format=self.date_format)
            df = df.rename(columns={'Date': 'date'})
        else:
            raise ValueError(f"CSV文件中没有找到日期列: {file_path}")
        
        # 设置日期索引
        df = df.set_index('date')
        
        # 根据日期范围过滤数据
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        df = df.loc[(df.index >= start_datetime) & (df.index <= end_datetime)]
        
        # 格式化数据
        return self.format_data(df, data_type='daily')
    
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
        # 构建文件路径
        file_path = os.path.join(self.data_dir, f"{symbol}_{frequency}min.csv")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 尝试不带频率后缀的文件
            file_path = os.path.join(self.data_dir, f"{symbol}_minute.csv")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"分钟数据文件不存在: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 格式化日期时间
        if 'date' in df.columns:
            # 尝试解析为datetime，包括时间部分
            try:
                df['date'] = pd.to_datetime(df['date'])
            except ValueError:
                # 尝试使用指定的日期格式
                df['date'] = pd.to_datetime(df['date'], format=self.date_format)
        elif 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.rename(columns={'datetime': 'date'})
        else:
            raise ValueError(f"CSV文件中没有找到日期时间列: {file_path}")
        
        # 设置日期时间索引
        df = df.set_index('date')
        
        # 根据时间范围过滤数据
        start_datetime = pd.to_datetime(start_time)
        end_datetime = pd.to_datetime(end_time)
        df = df.loc[(df.index >= start_datetime) & (df.index <= end_datetime)]
        
        # 格式化数据
        return self.format_data(df, data_type='minute')
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            DataFrame: 包含股票代码、名称等信息的DataFrame
        """
        # 尝试读取股票列表文件
        stock_list_file = os.path.join(self.data_dir, "stock_list.csv")
        
        if not os.path.exists(stock_list_file):
            # 如果没有股票列表文件，尝试从数据目录中推断股票列表
            return self._infer_stock_list()
        
        # 读取股票列表文件
        df = pd.read_csv(stock_list_file)
        
        # 确保列名符合规范
        if 'code' not in df.columns or 'name' not in df.columns:
            # 尝试映射常见的列名
            column_mapping = {
                '股票代码': 'code',
                '代码': 'code',
                'stock_code': 'code',
                '股票名称': 'name',
                '名称': 'name',
                'stock_name': 'name'
            }
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # 检查是否有必要的列
            if 'code' not in df.columns or 'name' not in df.columns:
                raise ValueError(f"股票列表文件缺少必要的列: {stock_list_file}")
        
        return df[['code', 'name']]
    
    def get_etf_list(self) -> pd.DataFrame:
        """
        获取ETF列表
        
        Returns:
            DataFrame: 包含ETF代码、名称等信息的DataFrame
        """
        # 尝试读取ETF列表文件
        etf_list_file = os.path.join(self.data_dir, "etf_list.csv")
        
        if not os.path.exists(etf_list_file):
            # 如果没有ETF列表文件，尝试从数据目录中推断ETF列表
            return self._infer_etf_list()
        
        # 读取ETF列表文件
        df = pd.read_csv(etf_list_file)
        
        # 确保列名符合规范
        if 'code' not in df.columns or 'name' not in df.columns:
            # 尝试映射常见的列名
            column_mapping = {
                '基金代码': 'code',
                '代码': 'code',
                'etf_code': 'code',
                '基金名称': 'name',
                '名称': 'name',
                'etf_name': 'name'
            }
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # 检查是否有必要的列
            if 'code' not in df.columns or 'name' not in df.columns:
                raise ValueError(f"ETF列表文件缺少必要的列: {etf_list_file}")
        
        return df[['code', 'name']]
    
    def _infer_stock_list(self) -> pd.DataFrame:
        """
        从数据目录中推断股票列表
        
        Returns:
            DataFrame: 推断的股票列表
        """
        # 获取目录中的所有CSV文件
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        # 提取股票代码
        stocks = set()
        for f in csv_files:
            # 尝试从文件名中提取股票代码
            # 假设文件名格式为: {code}_daily.csv 或 {code}_minute.csv
            if '_daily.csv' in f:
                code = f.replace('_daily.csv', '')
                stocks.add(code)
            elif '_min' in f and '.csv' in f:
                # 匹配任何分钟数据文件格式
                code = f.split('_')[0]
                stocks.add(code)
        
        # 创建DataFrame
        df = pd.DataFrame({'code': list(stocks), 'name': ['未知'] * len(stocks)})
        return df[['code', 'name']]
    
    def _infer_etf_list(self) -> pd.DataFrame:
        """
        从数据目录中推断ETF列表
        
        Returns:
            DataFrame: 推断的ETF列表
        """
        # 对于CSV提供者，股票和ETF的推断逻辑可能相同
        # 这里简单地返回与股票列表相同的结果
        # 在实际应用中，可能需要更复杂的逻辑来区分股票和ETF
        return self._infer_stock_list()
    
    def format_data(self, df: pd.DataFrame, data_type: str = 'daily') -> pd.DataFrame:
        """
        格式化CSV数据为统一格式
        
        Args:
            df: 原始CSV数据
            data_type: 数据类型，'daily'或'minute'
            
        Returns:
            DataFrame: 格式化后的数据
        """
        # 定义列名映射
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume'
        }
        
        # 重命名列
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        # 检查并尝试填充缺失的列
        for col in required_columns:
            if col not in df.columns:
                # 对于缺失的列，可以尝试从其他列获取或设置默认值
                # 这里仅作提示，实际应用中可能需要更复杂的逻辑
                print(f"警告: 数据中缺少必要的列 '{col}'")
        
        # 只返回可用的必要列
        available_columns = [col for col in required_columns if col in df.columns]
        
        return df[available_columns]

# 注册到工厂
from ..factory import DataProviderFactory
DataProviderFactory.register('csv', CSVProvider)