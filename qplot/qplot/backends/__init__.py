"""
绘图后端模块
提供不同绘图库的实现
"""

from typing import Dict, Type, Optional
import importlib
import logging

from qplot.core.plotter import Chart

logger = logging.getLogger(__name__)

# 已注册的后端
_registered_backends: Dict[str, Type[Chart]] = {}

# 默认后端
_default_backend = 'matplotlib'

# 后端配置
_backend_config = {
    'matplotlib': {
        'required_package': 'matplotlib',
        'module_path': 'qplot.backends.matplotlib.chart',
        'class_name': 'MatplotlibChart'
    },
    'pyecharts': {
        'required_package': 'pyecharts',
        'module_path': 'qplot.backends.pyecharts.chart',
        'class_name': 'PyechartsChart'
    }
}

def register_backend(name: str, backend_class: Type[Chart]) -> None:
    """
    注册一个新的绘图后端
    
    Args:
        name: 后端名称
        backend_class: 后端类
    """
    if not issubclass(backend_class, Chart):
        raise TypeError(f"后端类必须是Chart的子类，当前类型: {type(backend_class)}")
    
    _registered_backends[name] = backend_class
    logger.info(f"已注册绘图后端: {name}")

def get_backend(name: str = None) -> Type[Chart]:
    """
    获取指定的后端类
    
    Args:
        name: 后端名称，如果为None则使用默认后端
    
    Returns:
        Type[Chart]: 后端类
    
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
    设置默认的绘图后端
    
    Args:
        name: 后端名称
    
    Raises:
        ValueError: 如果指定的后端不存在或无法加载
    """
    global _default_backend
    
    # 尝试加载后端以验证其可用性
    get_backend(name)
    
    _default_backend = name
    logger.info(f"已设置默认绘图后端为: {name}")

def create_chart(backend: str, chart_type: str, data_manager=None, data=None, **kwargs) -> Chart:
    """
    创建一个图表实例
    
    Args:
        backend: 绘图后端
        chart_type: 图表类型，'kline'或'minute'
        data_manager: 数据管理器实例
        data: 直接提供的数据（DataFrame）
        **kwargs: 传递给图表的配置参数
    
    Returns:
        Chart: 图表实例
    """
    backend_class = get_backend(backend)
    return backend_class(chart_type=chart_type, data_manager=data_manager, data=data, **kwargs)

# 初始化默认后端
try:
    get_backend('matplotlib')
except Exception as e:
    logger.warning(f"无法加载matplotlib后端: {e}")
    logger.info("尝试将pyecharts作为默认后端")
    try:
        get_backend('pyecharts')
        _default_backend = 'pyecharts'
    except Exception as e2:
        logger.warning(f"无法加载pyecharts后端: {e2}")
        logger.warning("请安装至少一个绘图库以使用qplot")