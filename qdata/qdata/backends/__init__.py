"""
qdata.backends模块
提供不同数据源的实现，统一数据获取接口
"""
import importlib
import logging
from typing import Dict, Optional, Type

from qdata.provider import DataProvider

# 配置日志记录器
logger = logging.getLogger(__name__)

# 已注册的后端字典
_registered_backends: Dict[str, Type[DataProvider]] = {}

# 默认后端
_default_backend: str = 'akshare'

# 后端配置
_backend_config = {
    'akshare': {
        'enabled': True,
        'priority': 1,
    },
    'tushare': {
        'enabled': True,
        'priority': 2,
    },
    'csv': {
        'enabled': True,
        'priority': 3,
    }
}

def register_backend(name: str, backend_class: Type[DataProvider]) -> None:
    """
    注册一个新的数据源后端
    
    Args:
        name: 后端名称，用于标识后端
        backend_class: 后端类，必须是DataProvider的子类
    """
    if not issubclass(backend_class, DataProvider):
        raise TypeError(f"后端类必须是DataProvider的子类，而不是{type(backend_class)}")
    
    _registered_backends[name] = backend_class
    logger.info(f"已注册数据源后端: {name}")

def get_backend(name: Optional[str] = None) -> Type[DataProvider]:
    """
    获取指定的后端类
    
    Args:
        name: 后端名称，如果为None则返回默认后端
        
    Returns:
        Type[DataProvider]: 数据源后端类
        
    Raises:
        ValueError: 如果指定的后端不存在
    """
    if name is None:
        name = _default_backend
    
    if name not in _registered_backends:
        # 尝试动态加载后端
        try:
            module_name = f'qdata.backends.{name}_provider'
            importlib.import_module(module_name)
        except ImportError:
            pass
        
        if name not in _registered_backends:
            available = ', '.join(_registered_backends.keys())
            raise ValueError(f"不支持的数据源后端: {name}。可用的后端: {available}")
    
    return _registered_backends[name]

def set_default_backend(name: str) -> None:
    """
    设置默认的数据源后端
    
    Args:
        name: 后端名称
        
    Raises:
        ValueError: 如果指定的后端不存在
    """
    if name not in _registered_backends:
        # 尝试动态加载后端
        try:
            module_name = f'qdata.backends.{name}_provider'
            importlib.import_module(module_name)
        except ImportError:
            pass
        
        if name not in _registered_backends:
            available = ', '.join(_registered_backends.keys())
            raise ValueError(f"不支持的数据源后端: {name}。可用的后端: {available}")
    
    global _default_backend
    _default_backend = name
    logger.info(f"默认数据源后端已设置为: {name}")

def create_provider(name: Optional[str] = None, **kwargs) -> DataProvider:
    """
    创建一个数据源提供者实例
    
    Args:
        name: 后端名称，如果为None则使用默认后端
        **kwargs: 传递给后端构造函数的额外参数
        
    Returns:
        DataProvider: 数据源提供者实例
    """
    backend_class = get_backend(name)
    return backend_class(**kwargs)

def _auto_register_backends() -> None:
    """
    自动注册配置中的后端
    """
    for backend_name, config in _backend_config.items():
        if config.get('enabled', False):
            try:
                module_name = f'qdata.backends.{backend_name}_provider'
                importlib.import_module(module_name)
            except ImportError:
                logger.warning(f"无法加载后端模块: {module_name}")
            except Exception as e:
                logger.error(f"注册后端 {backend_name} 时出错: {e}")

# 自动注册后端
_auto_register_backends()

__all__ = [
    'register_backend',
    'get_backend',
    'set_default_backend',
    'create_provider',
]