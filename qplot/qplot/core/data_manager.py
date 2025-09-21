"""
数据管理器模块
负责从qdata获取数据、缓存数据、提供数据更新接口等
"""

import qdata
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """
    数据管理器类
    负责管理股票数据的获取、缓存和更新
    """
    
    def __init__(self, symbol: str, data_type: str = 'daily'):
        """
        初始化数据管理器
        
        Args:
            symbol: 证券代码
            data_type: 数据类型，'daily'或'minute'
        """
        self.symbol = symbol
        self.data_type = data_type
        self.data = None
        self.last_update_time = None
        self.lock = threading.RLock()  # 使用可重入锁保护数据访问
        
        # 尝试初始化qdata，但避免因qdata模块问题导致程序崩溃
        try:
            if not hasattr(qdata, '_initialized') or not getattr(qdata, '_initialized', False):
                if hasattr(qdata, 'init'):
                    qdata.init()
        except Exception as e:
            logger.warning(f"尝试初始化qdata时出错: {e}")
    
    def update_data(self, data=None) -> None:
        """
        更新数据
        获取最新数据或使用传入的数据更新现有数据
        
        Args:
            data: 可选，直接传入的数据，若为None则从qdata获取数据
        """
        with self.lock:
            try:
                # 如果传入了数据，直接使用
                if data is not None:
                    self.data = data
                    self.last_update_time = datetime.now()
                    logger.info(f"已使用传入数据更新{self.symbol}的{self.data_type}数据")
                    return
                
                # 根据数据类型获取最新数据
                if self.data_type == 'daily':
                    # 获取最近一个月的数据
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    new_data = qdata.get_daily_data(self.symbol, start_date, end_date)
                elif self.data_type == 'minute':
                    # 获取当天的分时数据
                    today = datetime.now().strftime('%Y-%m-%d')
                    new_data = qdata.get_minute_data(self.symbol, today, today, freq='1min')
                else:
                    raise ValueError(f"不支持的数据类型: {self.data_type}")
                
                # 更新数据
                if new_data is not None and not new_data.empty:
                    self.data = new_data
                    self.last_update_time = datetime.now()
                    logger.info(f"已更新{self.symbol}的{self.data_type}数据，最新时间: {self.last_update_time}")
            except Exception as e:
                logger.error(f"更新{self.symbol}的{self.data_type}数据时出错: {e}")
    
    def fetch_history_data(self, start_date: str, end_date: str) -> None:
        """
        获取历史数据
        
        Args:
            start_date: 开始日期，格式为'YYYY-MM-DD'
            end_date: 结束日期，格式为'YYYY-MM-DD'
        """
        with self.lock:
            try:
                if self.data_type == 'daily':
                    self.data = qdata.get_daily_data(self.symbol, start_date, end_date)
                elif self.data_type == 'minute':
                    self.data = qdata.get_minute_data(self.symbol, start_date, end_date, freq='1min')
                else:
                    raise ValueError(f"不支持的数据类型: {self.data_type}")
                
                self.last_update_time = datetime.now()
                logger.info(f"已获取{self.symbol}从{start_date}到{end_date}的{self.data_type}历史数据")
            except Exception as e:
                logger.error(f"获取{self.symbol}的历史{self.data_type}数据时出错: {e}")
    
    def get_data(self):
        """
        获取存储的数据
        
        Returns:
            pd.DataFrame: 存储的数据，如果没有数据则返回None
        """
        with self.lock:
            return self.data
    
    def get_latest_data(self, n: int = 1) -> pd.DataFrame:
        """
        获取最新的n条数据
        
        Args:
            n: 要获取的最新数据条数
        
        Returns:
            pd.DataFrame: 最新的n条数据
        """
        with self.lock:
            if self.data is None or self.data.empty:
                return pd.DataFrame()
            # 确保索引是日期时间类型
            if not isinstance(self.data.index, pd.DatetimeIndex):
                try:
                    if 'date' in self.data.columns:
                        self.data['date'] = pd.to_datetime(self.data['date'])
                        self.data = self.data.set_index('date')
                except Exception as e:
                    logger.warning(f"设置日期索引时出错: {e}")
            # 按日期排序并获取最新的n条数据
            sorted_data = self.data.sort_index()
            return sorted_data.tail(n)
    
    def is_data_stale(self, max_age_seconds: int = 60) -> bool:
        """
        检查数据是否过期
        
        Args:
            max_age_seconds: 数据的最大有效时间（秒）
        
        Returns:
            bool: 数据是否过期
        """
        if self.last_update_time is None:
            return True
        elapsed = (datetime.now() - self.last_update_time).total_seconds()
        return elapsed > max_age_seconds
    
    def clear_data(self) -> None:
        """
        清除缓存的数据
        """
        with self.lock:
            self.data = None
            self.last_update_time = None
            logger.info(f"已清除{self.symbol}的{self.data_type}缓存数据")

class DatabaseDataManager(DataManager):
    """
    数据库数据管理器
    扩展基本数据管理器，增加数据库存储功能
    """
    
    def __init__(self, symbol: str, data_type: str = 'daily', db_path: str = None):
        """
        初始化数据库数据管理器
        
        Args:
            symbol: 证券代码
            data_type: 数据类型，'daily'或'minute'
            db_path: 数据库路径，默认为None
        """
        super().__init__(symbol, data_type)
        self.db_path = db_path if db_path else f'./data/{symbol}_{data_type}.db'
        self._init_database()
    
    def _init_database(self):
        """
        初始化数据库
        """
        try:
            # 确保目录存在
            import os
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # 尝试连接数据库
            self._connect_db()
            logger.info(f"已初始化数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"初始化数据库时出错: {e}")
    
    def _connect_db(self):
        """
        连接数据库（子类实现具体逻辑）
        """
        # 由具体的子类实现
        pass
    
    def save_to_db(self):
        """
        将数据保存到数据库（子类实现具体逻辑）
        """
        # 由具体的子类实现
        pass
    
    def load_from_db(self):
        """
        从数据库加载数据（子类实现具体逻辑）
        """
        # 由具体的子类实现
        pass