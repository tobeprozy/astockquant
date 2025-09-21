# AkShareProvider 使用指南

## 导入说明

在qdata模块中，`AkShareProvider`类**不能**直接从qdata模块导入，而是需要从`qdata.backends.akshare_provider`模块导入。

### 正确的导入方式
```python
# 直接导入AkShareProvider类
from qdata.backends.akshare_provider import AkShareProvider

# 或者使用qdata提供的统一接口
import qdata
```

### 错误的导入方式（会导致ImportError）
```python
# 这是错误的导入方式
from qdata import AkShareProvider  # 这将失败
```

## 使用方法

### 方法1：直接使用AkShareProvider类
```python
from qdata.backends.akshare_provider import AkShareProvider

# 创建实例
ak_provider = AkShareProvider(retry_count=3)

# 获取数据
df = ak_provider.get_daily_data("512200", "2023-01-01", "2023-12-31")
```

### 方法2：使用qdata统一接口（推荐）
```python
import qdata

# 初始化（可选，首次调用接口时会自动执行）
qdata.init()

# 获取数据（默认使用akshare后端）
df = qdata.get_daily_data("512200", "2023-01-01", "2023-12-31")

# 显式指定后端
df = qdata.get_daily_data("512200", "2023-01-01", "2023-12-31", backend='akshare')
```

## 运行示例

您可以运行`akshare_provider_example.py`文件来查看完整的使用示例：

```bash
cd /Users/zzy/workspace/AstockQuant/qdata/examples
python akshare_provider_example.py
```

## 注意事项

1. 使用前请确保已安装必要的依赖包：`pandas`和`akshare`
2. `AkShareProvider`类支持自定义重试次数和延迟时间
3. qdata统一接口提供了更简洁的使用方式，并且会自动进行数据格式化处理

## 可用方法

AkShareProvider类提供以下主要方法：
- `get_daily_data`: 获取日线数据
- `get_minute_data`: 获取分时数据
- `get_stock_list`: 获取股票列表
- `get_etf_list`: 获取ETF列表