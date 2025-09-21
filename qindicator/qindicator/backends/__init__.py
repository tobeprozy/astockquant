"""
指标计算后端模块
提供不同指标计算库的实现
"""

from typing import Dict, Type, Optional
import importlib
import logging

from qindicator.core.indicator import Indicator

logger = logging.getLogger(__name__)

# 已注册的后端
_registered_backends: Dict[str, Type[Indicator]] = {}

# 默认后端
_default_backend = 'talib'

# 后端配置
_backend_config = {
    'talib': {
        'required_package': 'talib',
        'module_path': 'qindicator.backends.talib.indicator',
        'class_name': 'TalibIndicator'
    }
}

def register_backend(name: str, backend_class: Type[Indicator]) -> None:
    """
    注册一个新的指标计算后端
    
    Args:
        name: 后端名称
        backend_class: 后端类
    """
    if not issubclass(backend_class, Indicator):
        raise TypeError(f"后端类必须是Indicator的子类，当前类型: {type(backend_class)}")
    
    _registered_backends[name] = backend_class
    logger.info(f"已注册指标计算后端: {name}")

def get_backend(name: str = None) -> Type[Indicator]:
    """
    获取指定的后端类
    
    Args:
        name: 后端名称，如果为None则使用默认后端
    
    Returns:
        Type[Indicator]: 后端类
    
    Raises:
        ValueError: 如果指定的后端不存在
    """
    backend_name = name or _default_backend
    
    # 如果后端已注册，直接返回
    if backend_name in _registered_backends:
        return _registered_backends[backend_name]
    
    # 尝试动态加载后端
    if backend_name in _backend_config:
        config = _backend_config[backend_name]
        
        try:
            # 检查是否安装了必要的包
            importlib.import_module(config['required_package'])
            
            # 导入后端模块
            module = importlib.import_module(config['module_path'])
            backend_class = getattr(module, config['class_name'])
            
            # 注册后端
            register_backend(backend_name, backend_class)
            return backend_class
        except ImportError as e:
            logger.error(f"加载后端{backend_name}时出错: {e}")
            raise ImportError(f"请安装必要的包以使用{backend_name}后端: {config['required_package']}")
    
    raise ValueError(f"未找到指定的后端: {backend_name}")

def set_default_backend(name: str) -> None:
    """
    设置默认的指标计算后端
    
    Args:
        name: 后端名称
    
    Raises:
        ValueError: 如果指定的后端不存在或无法加载
    """
    global _default_backend
    
    # 尝试加载后端以验证其可用性
    get_backend(name)
    _default_backend = name
    logger.info(f"已设置默认指标计算后端为: {name}")

def create_indicator(backend_name: str = None, **kwargs) -> Indicator:
    """
    创建指标计算实例
    
    Args:
        backend_name: 后端名称，如果为None则使用默认后端
        **kwargs: 传递给后端构造函数的参数
    
    Returns:
        Indicator: 指标计算实例
    """
    backend_class = get_backend(backend_name)
    return backend_class(**kwargs)

# 自动注册配置中的后端
def _auto_register_backends():
    """
    自动注册配置中的后端
    """
    for name in _backend_config:
        try:
            get_backend(name)
        except ImportError:
            logger.info(f"后端 {name} 的依赖包未安装，暂不注册")
        except Exception as e:
            logger.error(f"注册后端 {name} 时出错: {e}")

# 自动注册后端
_auto_register_backends()