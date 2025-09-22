"""
qplot - 一个可扩展的股票数据可视化插件系统

该系统设计用于统一不同数据源的数据可视化接口，提供一致的图表绘制功能。
支持绘制K线图和分时图，支持多种绘图后端。
"""

import logging

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 版本信息
__version__ = "0.1.0"
__author__ = "AstockQuant Team"

# 直接导入核心类和绘图器
from qplot.core.plotter import Plotter, Chart, RealTimePlotter
from qplot.core.data_manager import DataManager
from qplot.backends.matplotlib.chart import MatplotlibChart
from qplot.backends.pyecharts.chart import PyechartsChart

# 尝试导入pyecharts相关的绘图器
try:
    # 这里仅做可用性检查，具体的pyecharts功能在PyechartsChart中实现
    import pyecharts
    HAS_PYECHARTS = True
except ImportError:
    logger.info("未找到pyecharts库，如需使用pyecharts绘图功能，请安装: pip install qplot[pyecharts]")
    HAS_PYECHARTS = False

# 获取图表实例的工厂函数
def get_chart(chart_type='kline', backend='matplotlib', data_manager=None, data=None, **kwargs):
    """
    获取图表实例
    
    Args:
        chart_type: 图表类型，'kline'或'minute'
        backend: 绘图后端，'matplotlib'或'pyecharts'
        data_manager: 数据管理器实例
        data: 直接提供的数据（DataFrame）
        **kwargs: 其他配置参数
    
    Returns:
        Chart: 图表实例
    """
    if backend == 'pyecharts':
        if not HAS_PYECHARTS:
            raise ImportError("未找到pyecharts库，请先安装: pip install qplot[pyecharts]")
        return PyechartsChart(chart_type, data_manager=data_manager, data=data, **kwargs)
    else:
        # 默认使用matplotlib后端
        return MatplotlibChart(chart_type, data_manager=data_manager, data=data, **kwargs)

# 绘制K线图的快捷函数
def plot_kline(data=None, data_manager=None, backend='matplotlib', **kwargs):
    """
    绘制K线图的快捷函数
    
    Args:
        data: 直接提供的数据（DataFrame）
        data_manager: 数据管理器实例
        backend: 绘图后端，'matplotlib'或'pyecharts'
        **kwargs: 其他配置参数
    
    Returns:
        Chart: 图表实例
    """
    chart = get_chart('kline', backend=backend, data_manager=data_manager, data=data, **kwargs)
    return chart.plot()

# 绘制分时图的快捷函数
def plot_minute_chart(data=None, data_manager=None, backend='matplotlib', **kwargs):
    """
    绘制分时图的快捷函数
    
    Args:
        data: 直接提供的数据（DataFrame）
        data_manager: 数据管理器实例
        backend: 绘图后端，'matplotlib'或'pyecharts'
        **kwargs: 其他配置参数
    
    Returns:
        Chart: 图表实例
    """
    chart = get_chart('minute', backend=backend, data_manager=data_manager, data=data, **kwargs)
    return chart.plot()

# 通用绘图接口
def plot_chart(chart_type='kline', data=None, data_manager=None, backend='matplotlib', **kwargs):
    """
    通用绘图接口函数，可绘制不同类型的图表
    
    Args:
        chart_type: 图表类型，'kline'或'minute'
        data: 直接提供的数据（DataFrame）
        data_manager: 数据管理器实例
        backend: 绘图后端，'matplotlib'或'pyecharts'
        **kwargs: 其他配置参数
    
    Returns:
        Chart: 图表实例
    """
    chart = get_chart(chart_type, backend=backend, data_manager=data_manager, data=data, **kwargs)
    return chart.plot()

# 模块导出列表
__all__ = [
    'Plotter',
    'Chart',
    'RealTimePlotter',
    'DataManager',
    'MatplotlibChart',
    'PyechartsChart',
    'get_chart',
    'plot_chart',
    'plot_kline',
    'plot_minute_chart',
    'HAS_PYECHARTS'
]