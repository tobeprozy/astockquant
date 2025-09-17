from typing import Dict, Type
from .provider import DataProvider


class DataProviderFactory:
    """
    数据提供者工厂类
    用于创建和管理不同的数据源适配器
    """
    
    _providers: Dict[str, Type[DataProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[DataProvider]) -> None:
        """
        注册一个数据源提供者
        
        Args:
            name: 数据源名称，用于标识提供者
            provider_class: 数据源提供者类
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str) -> DataProvider:
        """
        创建一个数据源提供者实例
        
        Args:
            name: 数据源名称
            
        Returns:
            DataProvider: 数据源提供者实例
            
        Raises:
            ValueError: 如果指定的数据源名称未注册
        """
        if name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(f"不支持的数据源: {name}. 可用的数据源: {available}")
        
        return cls._providers[name]()
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        获取所有可用的数据源提供者名称
        
        Returns:
            list: 可用的数据源提供者名称列表
        """
        return list(cls._providers.keys())