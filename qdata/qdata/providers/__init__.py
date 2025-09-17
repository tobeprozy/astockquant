"""
qdata.providers模块
包含所有可用的数据源适配器
"""

# 导入各个数据源适配器
from qdata.providers.akshare_provider import AkShareProvider
from qdata.providers.tushare_provider import TuShareProvider
from qdata.providers.csv_provider import CSVProvider
from qdata.factory import DataProviderFactory

# 注册所有数据源适配器
data_providers = {
    'akshare': AkShareProvider,
    'tushare': TuShareProvider,
    'csv': CSVProvider
}

# 注册到工厂类
for name, provider_class in data_providers.items():
    DataProviderFactory.register(name, provider_class)

__all__ = ['AkShareProvider', 'TuShareProvider', 'CSVProvider', 'data_providers']