"""
qdata模块
可扩展的股票数据获取插件系统
统一不同数据源的访问接口
"""
import logging
import pandas as pd
from typing import Dict, List, Optional, Union, Any

# 版本信息
__version__ = "0.1.0"

# 配置日志记录器
logger = logging.getLogger(__name__)

# 导入核心模块
from qdata.provider import DataProvider
from qdata.core.data_manager import DataManager

# 导入后端管理函数
from qdata.backends import (
    register_backend,
    get_backend,
    set_default_backend,
    create_provider
)

# 全局变量
_data_provider = None


def init():
    """
    初始化模块，设置默认后端并创建数据提供者实例
    """
    global _data_provider
    
    try:
        # 设置默认后端为akshare
        set_default_backend('akshare')
        # 创建数据提供者实例
        _data_provider = create_provider()
        logger.info("qdata模块初始化成功")
    except Exception as e:
        logger.error(f"qdata模块初始化失败: {e}")
        _data_provider = None


def get_provider() -> DataProvider:
    """
    获取数据提供者实例（单例模式）
    
    Returns:
        DataProvider: 数据提供者实例
    """
    global _data_provider
    
    if _data_provider is None:
        init()
        
    if _data_provider is None:
        raise RuntimeError("数据提供者未初始化")
        
    return _data_provider


def get_daily_data(
    symbol: str, 
    start_date: str, 
    end_date: str, 
    backend: Optional[str] = None, 
    **kwargs
) -> pd.DataFrame:
    """
    获取股票日线数据
    
    Args:
        symbol: 证券代码
        start_date: 开始日期，格式为'YYYY-MM-DD'
        end_date: 结束日期，格式为'YYYY-MM-DD'
        backend: 数据源后端名称，如果为None则使用默认后端
        **kwargs: 传递给后端的额外参数
        
    Returns:
        DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
    """
    if backend is None:
        provider = get_provider()
    else:
        provider = create_provider(backend, **kwargs)
    
    try:
        df = provider.get_daily_data(symbol, start_date, end_date, **kwargs)
        # 使用数据管理器准备数据
        return DataManager.prepare_data(df, 'daily')
    except Exception as e:
        logger.error(f"获取日线数据失败: {e}")
        raise


def get_minute_data(
    symbol: str, 
    start_time: str, 
    end_time: str, 
    frequency: str = '1', 
    backend: Optional[str] = None, 
    **kwargs
) -> pd.DataFrame:
    """
    获取股票分时数据
    
    Args:
        symbol: 证券代码
        start_time: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
        end_time: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
        frequency: 时间频率，例如'1'表示1分钟，'5'表示5分钟等
        backend: 数据源后端名称，如果为None则使用默认后端
        **kwargs: 传递给后端的额外参数
        
    Returns:
        DataFrame: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
    """
    if backend is None:
        provider = get_provider()
    else:
        provider = create_provider(backend, **kwargs)
    
    try:
        df = provider.get_minute_data(symbol, start_time, end_time, frequency, **kwargs)
        # 使用数据管理器准备数据
        return DataManager.prepare_data(df, 'minute')
    except Exception as e:
        logger.error(f"获取分时数据失败: {e}")
        raise


def get_stock_list(
    backend: Optional[str] = None, 
    **kwargs
) -> pd.DataFrame:
    """
    获取股票列表
    
    Args:
        backend: 数据源后端名称，如果为None则使用默认后端
        **kwargs: 传递给后端的额外参数
        
    Returns:
        DataFrame: 包含股票代码、名称等信息的DataFrame
    """
    if backend is None:
        provider = get_provider()
    else:
        provider = create_provider(backend, **kwargs)
    
    try:
        return provider.get_stock_list(**kwargs)
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise


def get_etf_list(
    backend: Optional[str] = None, 
    **kwargs
) -> pd.DataFrame:
    """
    获取ETF列表
    
    Args:
        backend: 数据源后端名称，如果为None则使用默认后端
        **kwargs: 传递给后端的额外参数
        
    Returns:
        DataFrame: 包含ETF代码、名称等信息的DataFrame
    """
    if backend is None:
        provider = get_provider()
    else:
        provider = create_provider(backend, **kwargs)
    
    try:
        return provider.get_etf_list(**kwargs)
    except Exception as e:
        logger.error(f"获取ETF列表失败: {e}")
        raise

# 自动初始化
init()

__all__ = [
    "get_daily_data",
    "get_minute_data",
    "get_stock_list",
    "get_etf_list",
    "set_default_backend",
    "create_provider",
    "register_backend",
    "get_backend",
    "DataProvider",
    "DataManager"
]
