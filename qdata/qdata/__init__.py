"""
qdata - 一个可扩展的股票数据获取插件系统

该系统设计用于统一不同数据源的访问接口，提供一致的数据格式。
"""

import logging
from typing import List, Optional, Any, Dict
import pandas as pd
from datetime import datetime

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
_current_provider = None
_initialized = False

# 导入必要的模块
from qdata.provider import DataProvider
from qdata.factory import DataProviderFactory
# 导入providers模块以确保数据源注册
import qdata.providers

# 初始化函数
def init() -> None:
    """
    初始化qdata插件
    自动使用akshare作为默认数据源
    """
    global _initialized, _current_provider
    
    _initialized = True
    
    # 默认使用akshare作为数据源
    _current_provider = DataProviderFactory.create_provider('akshare')
    logger.info("已自动初始化akshare数据源")

# 获取当前数据源
def get_provider() -> DataProvider:
    """
    获取当前使用的数据源
    
    返回:
        当前数据源实例
    """
    global _current_provider
    
    if _current_provider is None:
        # 如果还没有初始化，则自动初始化
        if not _initialized:
            init()
    
    return _current_provider

# 切换数据源
def set_current_provider(provider_name: str) -> DataProvider:
    """
    切换当前使用的数据源
    
    参数:
        provider_name: 数据源名称
    
    返回:
        新的数据源实例
    """
    global _current_provider
    
    _current_provider = DataProviderFactory.create_provider(provider_name)
    logger.info(f"已切换数据源至: {provider_name}")
    
    return _current_provider

# 获取股票日线数据
def get_daily_data(symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
    """
    获取股票的日线数据
    
    参数:
        symbol: 股票代码
        start_date: 开始日期，格式为'YYYY-MM-DD'
        end_date: 结束日期，格式为'YYYY-MM-DD'
        **kwargs: 其他参数
    
    返回:
        包含日线数据的DataFrame
    """
    provider = get_provider()
    return provider.get_daily_data(symbol, start_date, end_date, **kwargs)

# 获取股票分时数据
def get_minute_data(symbol: str, start_time: str = None, end_time: str = None, freq: str = '1min', **kwargs) -> pd.DataFrame:
    """
    获取股票的分时数据
    
    参数:
        symbol: 股票代码
        start_time: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
        end_time: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
        freq: 时间频率，默认为'1min'
        **kwargs: 其他参数
    
    返回:
        包含分时数据的DataFrame
    """
    provider = get_provider()
    return provider.get_minute_data(symbol, start_time, end_time, freq, **kwargs)

# 获取股票列表
def get_stock_list(**kwargs) -> List[Dict[str, Any]]:
    """
    获取股票列表
    
    参数:
        **kwargs: 其他参数
    
    返回:
        股票列表
    """
    provider = get_provider()
    return provider.get_stock_list(**kwargs)

# 获取ETF列表
def get_etf_list(**kwargs) -> List[Dict[str, Any]]:
    """
    获取ETF列表
    
    参数:
        **kwargs: 其他参数
    
    返回:
        ETF列表
    """
    provider = get_provider()
    return provider.get_etf_list(**kwargs)

# 自动初始化
if not _initialized:
    try:
        init()
    except Exception as e:
        logger.warning(f"自动初始化失败: {e}")
        logger.info("请手动调用qdata.init()进行初始化")
