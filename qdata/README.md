# qdata - 统一的股票数据获取插件

qdata是一个可扩展的股票数据获取插件系统，设计用于统一不同数据源的访问接口，提供一致的数据格式。

## 功能特点

- 支持多种数据源：akshare、tushare、CSV文件
- 提供统一的API接口，简化数据获取流程
- 自动数据格式转换，确保数据结构一致性
- 灵活的数据源切换机制
- 支持自动初始化和配置

## 安装

### 从源码安装

```bash
cd qdata
pip install -e .
```

### 依赖项

- pandas>=1.0.0
- numpy>=1.18.0
- akshare>=1.8.0 (用于akshare数据源)
- tushare>=1.2.80 (用于tushare数据源)
- requests>=2.24.0

## 基本使用

### 自动初始化（默认使用akshare数据源）

```python
import qdata

# 获取日线数据
df = qdata.get_daily_data('600000', '2023-01-01', '2023-06-30')
print(df.head())

# 获取股票列表
stock_list = qdata.get_stock_list()
print(f"获取到{len(stock_list)}支股票")

# 获取ETF列表
etf_list = qdata.get_etf_list()
print(f"获取到{len(etf_list)}支ETF")
```

### 手动初始化和配置

```python
import qdata

# 配置字典
config = {
    'default_provider': 'akshare',
    'akshare_config': {
        'retry_count': 3,
        'retry_delay': [1, 2, 3]
    },
    'tushare_config': {
        'token': 'your_token_here'
    }
}

# 手动初始化
qdata.init(config)

# 切换数据源
qdata.set_current_provider('tushare')

# 获取数据
df = qdata.get_daily_data('600000', '2023-01-01', '2023-06-30')
```

### 使用CSV数据源

```python
import qdata
import os

# 设置CSV数据目录
csv_config = {
    'data_dir': os.path.join(os.path.dirname(__file__), 'data')
}

# 切换到CSV数据源
qdata.set_current_provider('csv', csv_config)

# 获取数据
df = qdata.get_daily_data('600000', '2023-01-01', '2023-06-30')
```

### 获取分时数据

```python
import qdata

# 获取1分钟级别的分时数据
minute_data = qdata.get_minute_data('600000', '2023-06-30', freq='1min')
print(minute_data.head())
```

## 目录结构

```
qdata/
├── __init__.py         # 外层包初始化文件
├── setup.py            # 安装配置文件
├── README.md           # 项目说明文档
├── examples/           # 示例代码
│   └── usage_example.py # 使用示例
├── tests/              # 测试文件
│   └── test_qdata_api.py # API测试
└── qdata/              # 内部包目录
    ├── __init__.py     # 包初始化文件，包含主要API接口
    ├── provider.py     # 抽象基类定义
    ├── factory.py      # 数据源工厂类
    └── providers/      # 数据源适配器
        ├── __init__.py # 数据源注册
        ├── akshare_provider.py # AkShare数据源实现
        ├── tushare_provider.py # TuShare数据源实现
        └── csv_provider.py     # CSV文件数据源实现
```

## API参考

### 初始化函数

- `qdata.init(config=None)`: 初始化qdata插件
  - `config`: 配置字典，可选

### 数据源管理

- `qdata.get_provider()`: 获取当前使用的数据源
- `qdata.set_current_provider(provider_name, provider_config=None)`: 切换数据源
  - `provider_name`: 数据源名称，如'akshare'、'tushare'、'csv'
  - `provider_config`: 数据源配置，可选

### 数据获取函数

- `qdata.get_daily_data(symbol, start_date, end_date, **kwargs)`: 获取日线数据
  - `symbol`: 股票代码
  - `start_date`: 开始日期，格式为'YYYY-MM-DD'
  - `end_date`: 结束日期，格式为'YYYY-MM-DD'

- `qdata.get_minute_data(symbol, start_time=None, end_time=None, freq='1min', **kwargs)`: 获取分时数据
  - `symbol`: 股票代码
  - `start_time`: 开始时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
  - `end_time`: 结束时间，格式为'YYYY-MM-DD HH:MM:SS'或'YYYY-MM-DD'
  - `freq`: 时间频率，默认为'1min'

- `qdata.get_stock_list(**kwargs)`: 获取股票列表
- `qdata.get_etf_list(**kwargs)`: 获取ETF列表

## 示例

更多示例请查看`examples`目录下的`usage_example.py`文件。

## 测试

可以通过运行测试文件来验证qdata包的功能：

```bash
cd qdata/tests
python -m unittest test_qdata_api.py
```

也可以使用项目根目录下的`test_qdata_import.py`脚本快速验证包的导入和基本功能：

```bash
python test_qdata_import.py
```

## 扩展开发

要添加新的数据源，需要：

1. 创建一个新的数据源适配器类，继承自`DataProvider`基类
2. 实现所有抽象方法：`get_daily_data`, `get_minute_data`, `get_stock_list`, `get_etf_list`
3. 在`providers/__init__.py`文件中注册新的数据源

## 许可证

MIT License