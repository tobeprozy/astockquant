"""
qplot - 一个可扩展的股票数据可视化插件系统

该系统设计用于统一不同数据源的数据可视化接口，提供一致的图表绘制功能。
支持实时日K线图和分时图的绘制。
"""

import logging
from typing import List, Optional, Any, Dict
import pandas as pd
from datetime import datetime
import threading
import time

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 版本信息
__version__ = "0.1.0"
__author__ = "AstockQuant Team"

# 全局变量
_initialized = False
_data_managers = {}
_plotters = {}
_update_threads = {}

# 导入必要的模块
from qplot.plotter import Plotter
from qplot.data_manager import DataManager
from qplot.plotters.candlestick_plotter import CandlestickPlotter
from qplot.plotters.minute_plotter import MinutePlotter

# 尝试导入pyecharts相关的绘图器
try:
    from qplot.plotters.pyecharts.candlestick_plotter import PyechartsCandlestickPlotter
    from qplot.plotters.pyecharts.minute_plotter import PyechartsMinutePlotter
    HAS_PYECHARTS = True
except ImportError:
    logger.info("未找到pyecharts库，如需使用pyecharts绘图功能，请安装: pip install qplot[pyecharts]")
    HAS_PYECHARTS = False

# 全局变量
default_plot_backend = 'matplotlib'  # 默认绘图后端

# 初始化函数
def init() -> None:
    """
    初始化qplot插件
    """
    global _initialized
    
    if not _initialized:
        _initialized = True
        logger.info("已初始化qplot插件")
        
        # 注册默认的绘图器
        register_plotter('candlestick', CandlestickPlotter)
        register_plotter('minute', MinutePlotter)
        
        # 如果pyecharts可用，注册pyecharts绘图器
        if HAS_PYECHARTS:
            register_plotter('pyecharts_candlestick', PyechartsCandlestickPlotter)
            register_plotter('pyecharts_minute', PyechartsMinutePlotter)

# 设置默认绘图后端
def set_default_plot_backend(backend: str) -> None:
    """
    设置默认的绘图后端
    
    Args:
        backend: 绘图后端名称，支持'matplotlib'或'pyecharts'
    
    Raises:
        ValueError: 如果指定的后端不支持
    """
    global default_plot_backend
    
    if backend not in ['matplotlib', 'pyecharts']:
        raise ValueError("不支持的绘图后端，仅支持'matplotlib'和'pyecharts'")
    
    if backend == 'pyecharts' and not HAS_PYECHARTS:
        raise ImportError("未找到pyecharts库，请先安装: pip install qplot[pyecharts]")
    
    default_plot_backend = backend
    logger.info(f"已设置默认绘图后端为: {backend}")

# 注册绘图器
def register_plotter(name: str, plotter_class: type) -> None:
    """
    注册一个绘图器
    
    Args:
        name: 绘图器名称
        plotter_class: 绘图器类
    """
    global _plotters
    _plotters[name] = plotter_class
    logger.info(f"已注册绘图器: {name}")

# 启动实时数据更新线程
def start_realtime_update(symbol: str, interval: int = 60, data_type: str = 'daily') -> None:
    """
    启动实时数据更新线程
    
    Args:
        symbol: 证券代码
        interval: 更新间隔（秒），默认为60秒
        data_type: 数据类型，'daily'或'minute'
    """
    global _data_managers, _update_threads
    
    key = f"{symbol}_{data_type}"
    
    if key not in _data_managers:
        _data_managers[key] = DataManager(symbol, data_type)
        
    if key not in _update_threads or not _update_threads[key].is_alive():
        def update_task():
            while True:
                try:
                    _data_managers[key].update_data()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"更新{symbol}的{data_type}数据时出错: {e}")
                    time.sleep(interval)  # 出错时也继续尝试
        
        thread = threading.Thread(target=update_task, daemon=True)
        _update_threads[key] = thread
        thread.start()
        logger.info(f"已启动{symbol}的{data_type}数据实时更新线程")

# 停止实时数据更新线程
def stop_realtime_update(symbol: str, data_type: str = 'daily') -> None:
    """
    停止实时数据更新线程
    
    Args:
        symbol: 证券代码
        data_type: 数据类型，'daily'或'minute'
    """
    global _update_threads
    
    key = f"{symbol}_{data_type}"
    
    if key in _update_threads:
        # 注意：Python的线程没有直接的终止方法，这里只是移除引用
        _update_threads[key] = None
        logger.info(f"已停止{symbol}的{data_type}数据实时更新线程")

# 绘制日K线图
def plot_kline(symbol: str, start_date: str = None, end_date: str = None, realtime: bool = False, interval: int = 60, **kwargs) -> None:
    """
    绘制日K线图
    
    Args:
        symbol: 证券代码
        start_date: 开始日期，格式为'YYYY-MM-DD'
        end_date: 结束日期，格式为'YYYY-MM-DD'
        realtime: 是否启用实时更新
        interval: 实时更新间隔（秒）
        **kwargs: 其他绘图参数
        - backend: 可选，指定绘图后端，'matplotlib'或'pyecharts'
    """
    # 初始化qplot
    if not _initialized:
        init()
    
    # 获取或创建数据管理器
    key = f"{symbol}_daily"
    if key not in _data_managers:
        _data_managers[key] = DataManager(symbol, 'daily')
    
    # 更新数据
    if start_date and end_date:
        _data_managers[key].fetch_history_data(start_date, end_date)
    else:
        _data_managers[key].update_data()
    
    # 选择绘图器
    backend = kwargs.pop('backend', default_plot_backend)
    
    if backend == 'pyecharts':
        if HAS_PYECHARTS and 'pyecharts_candlestick' in _plotters:
            plotter = _plotters['pyecharts_candlestick']()
            chart = plotter.plot(_data_managers[key].get_data(), **kwargs)
            # 如果是Jupyter环境，可以直接显示图表
            try:
                from IPython.display import display
                display(chart)
            except ImportError:
                # 非Jupyter环境，直接返回图表对象
                pass
        else:
            logger.warning("pyecharts绘图器不可用，使用默认的matplotlib绘图器")
            if 'candlestick' in _plotters:
                plotter = _plotters['candlestick']()
                plotter.plot(_data_managers[key].get_data(), **kwargs)
            else:
                raise ValueError("未找到candlestick绘图器")
    else:
        # 使用默认的matplotlib绘图器
        if 'candlestick' in _plotters:
            plotter = _plotters['candlestick']()
            plotter.plot(_data_managers[key].get_data(), **kwargs)
        else:
            raise ValueError("未找到candlestick绘图器")
    
    # 如果启用了实时更新
    if realtime:
        start_realtime_update(symbol, interval, 'daily')

# 绘制分时图
def plot_minute_chart(symbol: str, start_time: str = None, end_time: str = None, realtime: bool = False, interval: int = 60, **kwargs) -> None:
    """
    绘制分时图
    
    Args:
        symbol: 证券代码
        start_time: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
        end_time: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
        realtime: 是否启用实时更新
        interval: 实时更新间隔（秒）
        **kwargs: 其他绘图参数
        - backend: 可选，指定绘图后端，'matplotlib'或'pyecharts'
    """
    # 初始化qplot
    if not _initialized:
        init()
    
    # 获取或创建数据管理器
    key = f"{symbol}_minute"
    if key not in _data_managers:
        _data_managers[key] = DataManager(symbol, 'minute')
    
    # 更新数据
    if start_time and end_time:
        _data_managers[key].fetch_history_data(start_time, end_time)
    else:
        _data_managers[key].update_data()
    
    # 选择绘图器
    backend = kwargs.pop('backend', default_plot_backend)
    
    if backend == 'pyecharts':
        if HAS_PYECHARTS and 'pyecharts_minute' in _plotters:
            plotter = _plotters['pyecharts_minute']()
            chart = plotter.plot(_data_managers[key].get_data(), **kwargs)
            # 如果是Jupyter环境，可以直接显示图表
            try:
                from IPython.display import display
                display(chart)
            except ImportError:
                # 非Jupyter环境，直接返回图表对象
                pass
        else:
            logger.warning("pyecharts绘图器不可用，使用默认的matplotlib绘图器")
            if 'minute' in _plotters:
                plotter = _plotters['minute']()
                plotter.plot(_data_managers[key].get_data(), **kwargs)
            else:
                raise ValueError("未找到minute绘图器")
    else:
        # 使用默认的matplotlib绘图器
        if 'minute' in _plotters:
            plotter = _plotters['minute']()
            plotter.plot(_data_managers[key].get_data(), **kwargs)
        else:
            raise ValueError("未找到minute绘图器")
    
    # 如果启用了实时更新
    if realtime:
        start_realtime_update(symbol, interval, 'minute')

# 获取数据管理器
def get_data_manager(symbol: str, data_type: str = 'daily') -> DataManager:
    """
    获取数据管理器实例
    
    Args:
        symbol: 证券代码
        data_type: 数据类型，'daily'或'minute'
    
    Returns:
        DataManager: 数据管理器实例
    """
    global _data_managers
    
    key = f"{symbol}_{data_type}"
    
    if key not in _data_managers:
        _data_managers[key] = DataManager(symbol, data_type)
    
    return _data_managers[key]

# 获取绘图器
def get_plotter(name: str) -> Plotter:
    """
    获取绘图器实例
    
    Args:
        name: 绘图器名称
    
    Returns:
        Plotter: 绘图器实例
    """
    if name not in _plotters:
        raise ValueError(f"未找到绘图器: {name}")
    
    return _plotters[name]()

# 清理资源
def cleanup():
    """
    清理资源，停止所有更新线程
    """
    global _update_threads
    
    for key in list(_update_threads.keys()):
        stop_realtime_update(key.split('_')[0], key.split('_')[1])
    
    logger.info("已清理qplot资源")