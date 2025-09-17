"""
plotter模块 - 定义绘图器的抽象基类
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class Plotter(ABC):
    """
    绘图器的抽象基类
    所有具体的绘图器都需要实现这个接口
    """
    
    @abstractmethod
    def plot(self, data: pd.DataFrame, **kwargs) -> None:
        """
        绘制图表
        
        Args:
            data: 要绘制的数据，通常是pandas DataFrame
            **kwargs: 其他绘图参数
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