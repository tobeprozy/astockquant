"""
plotter模块 - 定义绘图器的抽象基类
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional

class Plotter(ABC):
    """
    绘图器的抽象基类
    所有具体的绘图器都需要实现这个接口
    """
    
    @abstractmethod
    def plot(self, data: pd.DataFrame, **kwargs) -> Any:
        """
        绘制图表
        
        Args:
            data: 要绘制的数据，通常是pandas DataFrame
            **kwargs: 其他绘图参数
        
        Returns:
            Any: 图表对象（根据不同绘图库返回不同类型）
        """
        pass
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 默认不做处理，直接返回
        return data
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """
        验证数据是否有效
        
        Args:
            data: 要验证的数据
        
        Returns:
            bool: 数据是否有效
        """
        # 默认检查数据是否为空
        if data is None or data.empty:
            return False
        return True

class RealTimePlotter(Plotter):
    """
    实时绘图器的抽象基类
    支持实时数据更新的绘图器需要继承这个类
    """
    
    def __init__(self):
        """
        初始化实时绘图器
        """
        self.figure = None
        self.axes = None
        self.is_initialized = False
        
    @abstractmethod
    def update_plot(self, data: pd.DataFrame, **kwargs) -> None:
        """
        更新图表
        
        Args:
            data: 新的数据
            **kwargs: 其他更新参数
        """
        pass
    
    def setup_realtime_updates(self, update_callback, interval: int = 60) -> None:
        """
        设置实时更新
        
        Args:
            update_callback: 更新回调函数
            interval: 更新间隔（秒）
        """
        import threading
        import time
        
        def update_task():
            while True:
                try:
                    data = update_callback()
                    if data is not None and not data.empty:
                        self.update_plot(data)
                except Exception as e:
                    import logging
                    logging.error(f"更新图表时出错: {e}")
                time.sleep(interval)
        
        thread = threading.Thread(target=update_task, daemon=True)
        thread.start()

class Chart(Plotter):
    """
    通用图表类
    统一处理不同类型的图表（K线图、分时图等）
    """
    
    CHART_TYPE_KLINE = 'kline'
    CHART_TYPE_MINUTE = 'minute'
    
    def __init__(self, chart_type: str = CHART_TYPE_KLINE):
        """
        初始化通用图表
        
        Args:
            chart_type: 图表类型，'kline'或'minute'
        """
        self.chart_type = chart_type
    
    def plot(self, data: pd.DataFrame, **kwargs) -> Any:
        """
        根据图表类型绘制相应的图表
        
        Args:
            data: 要绘制的数据
            **kwargs: 绘图参数
        
        Returns:
            Any: 图表对象
        """
        if not self._validate_data(data):
            import logging
            logging.warning("无效的数据，无法绘制图表")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 根据图表类型调用不同的绘图方法
        if self.chart_type == self.CHART_TYPE_KLINE:
            return self._plot_kline(df, **kwargs)
        elif self.chart_type == self.CHART_TYPE_MINUTE:
            return self._plot_minute(df, **kwargs)
        else:
            raise ValueError(f"不支持的图表类型: {self.chart_type}")
    
    @abstractmethod
    def _plot_kline(self, data: pd.DataFrame, **kwargs) -> Any:
        """
        绘制K线图
        
        Args:
            data: 预处理后的数据
            **kwargs: 绘图参数
        
        Returns:
            Any: 图表对象
        """
        pass
    
    @abstractmethod
    def _plot_minute(self, data: pd.DataFrame, **kwargs) -> Any:
        """
        绘制分时图
        
        Args:
            data: 预处理后的数据
            **kwargs: 绘图参数
        
        Returns:
            Any: 图表对象
        """
        pass
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        根据图表类型预处理数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 复制数据以避免修改原始数据
        df = data.copy()
        
        if self.chart_type == self.CHART_TYPE_KLINE:
            return self._preprocess_kline_data(df)
        elif self.chart_type == self.CHART_TYPE_MINUTE:
            return self._preprocess_minute_data(df)
        else:
            return df
    
    def _preprocess_kline_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理K线图数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 默认实现，子类可以覆盖
        # 确保列名符合要求
        column_mapping = {
            '开盘价': 'open',
            '最高价': 'high', 
            '最低价': 'low',
            '收盘价': 'close',
            '成交量': 'volume'
        }
        
        # 重命名列
        df = data.rename(columns=column_mapping)
        
        # 确保索引是日期时间类型
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                else:
                    # 尝试将索引转换为日期时间
                    df.index = pd.to_datetime(df.index)
            except Exception as e:
                import logging
                logging.warning(f"设置日期索引时出错: {e}")
        
        # 排序数据
        df = df.sort_index()
        
        return df
    
    def _preprocess_minute_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理分时图数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 默认实现，子类可以覆盖
        # 确保列名符合要求
        column_mapping = {
            '时间': 'time',
            '价格': 'price',
            '均价': 'avg_price',
            '成交量': 'volume'
        }
        
        # 重命名列
        df = data.rename(columns=column_mapping)
        
        # 确保索引是日期时间类型
        if 'time' in df.columns:
            try:
                df['time'] = pd.to_datetime(df['time'])
                df = df.set_index('time')
            except Exception as e:
                import logging
                logging.warning(f"设置时间索引时出错: {e}")
        elif not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception as e:
                import logging
                logging.warning(f"将索引转换为日期时间时出错: {e}")
        
        # 排序数据
        df = df.sort_index()
        
        return df