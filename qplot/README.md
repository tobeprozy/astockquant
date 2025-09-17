# qplot

qplot是一个可扩展的股票数据可视化插件系统，用于统一不同数据源的数据可视化接口，提供一致的图表绘制功能。支持多种绘图后端，包括matplotlib和pyecharts，可绘制专业的日K线图和分时图，并支持实时数据更新。

## 功能特性

- 📈 **日K线图绘制**：支持各种技术指标（如均线）和成交量显示
- ⏱️ **分时图绘制**：展示股票的日内走势和均价线
- 🔄 **实时数据更新**：通过双线程机制实现数据的实时获取和图表的动态更新
- 📊 **自定义样式**：支持自定义图表样式、颜色和尺寸
- 💾 **数据缓存**：内置数据缓存机制，提高数据访问效率
- 📱 **可安装性**：作为Python包可通过pip安装
- 🎨 **多绘图后端**：支持matplotlib和pyecharts两种绘图后端
- 🖱️ **交互式图表**：通过pyecharts支持可交互的图表，包括缩放、平移、悬停提示等功能
- 🌐 **HTML导出**：支持将图表导出为HTML文件，便于在浏览器中查看和分享

## 安装

### 基本安装

```bash
# 克隆仓库
cd d:/codespace/AstockQuant

# 安装qplot（开发模式）
cd qplot
pip install -e .
```

### 安装pyecharts支持

如果需要使用pyecharts绘图后端，可以安装可选依赖：

```bash
# 安装包含pyecharts支持的qplot
pip install -e .[pyecharts]

# 或者单独安装pyecharts
pip install pyecharts>=1.9.0
```

### 依赖项

qplot的核心依赖项：
- pandas>=1.0.0
- numpy>=1.18.0
- matplotlib>=3.3.0  # 默认绘图库
- mplfinance>=0.12.7a17  # 金融数据绘图专用库
- qdata>=0.1.0  # 依赖qdata插件获取数据

可选依赖项：
- pyecharts>=1.9.0  # 交互式图表库，用于生成可交互的HTML图表

这些依赖会在安装qplot时自动安装。

## 快速开始

以下是使用qplot绘制K线图和分时图的简单示例：

### 使用默认matplotlib后端

```python
import qplot
import qdata
from datetime import datetime, timedelta

# 获取股票数据
stock_code = "600519"
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
df = qdata.get_daily_data(stock_code, start_date, end_date)

# 绘制K线图
qplot.plot_kline(
    df,
    title=f"{stock_code} 日K线图",
    style='charles',
    volume=True,
    indicators=['ma5', 'ma10', 'ma20']
)

# 绘制分时图
# 注意：实际使用时请用真实的分时数据替代示例数据
sample_minute_data = qplot.examples.generate_sample_minute_data(stock_code)
qplot.plot_minute_chart(
    sample_minute_data,
    title=f"{stock_code} 分时图",
    line_color='blue',
    show_avg_line=True
)
```

### 使用pyecharts后端

```python
import qplot
import qdata
from datetime import datetime, timedelta

# 方法1: 设置全局默认绘图后端
qplot.set_default_plot_backend('pyecharts')

# 获取股票数据
stock_code = "600519"
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
df = qdata.get_daily_data(stock_code, start_date, end_date)

# 绘制K线图（将使用pyecharts后端）
qplot.plot_kline(
    df,
    title=f"{stock_code} 日K线图 - pyecharts",
    width=1200,  # pyecharts特有的参数
    height=600,  # pyecharts特有的参数
    volume=True,
    indicators=['ma5', 'ma10', 'ma20']
)

# 方法2: 在函数调用时指定绘图后端
# 绘制分时图（直接在调用时指定pyecharts后端）
sample_minute_data = qplot.examples.generate_sample_minute_data(stock_code)
qplot.plot_minute_chart(
    sample_minute_data,
    title=f"{stock_code} 分时图 - pyecharts",
    backend='pyecharts',  # 直接指定后端
    width=1200,
    height=500,
    show_avg_line=True,
    show_volume=True
)```

## 实时数据更新

qplot支持实时更新K线图和分时图，通过双线程机制实现。实时更新功能同时支持matplotlib和pyecharts后端：

### 使用matplotlib后端的实时更新

```python
import qplot

# 创建数据管理器
stock_code = "600519"
data_manager = qplot.DataManager(stock_code=stock_code, data_type='minute')

# 生成初始数据（实际应用中应使用真实数据）
initial_data = qplot.examples.generate_sample_minute_data(stock_code)
data_manager.update_data(initial_data)

# 启动实时更新
# 数据更新线程（每10秒更新一次）
data_manager.start_realtime_updates(interval=10)

# 绘制实时分时图
qplot.plot_minute_chart_realtime(data_manager, update_interval=10)

# 使用完毕后停止更新
data_manager.stop_realtime_updates()
```

### 使用pyecharts后端的实时更新

```python
import qplot

# 设置为pyecharts后端
qplot.set_default_plot_backend('pyecharts')

# 创建数据管理器
stock_code = "600519"
data_manager = qplot.DataManager(stock_code=stock_code, data_type='minute')

# 生成初始数据（实际应用中应使用真实数据）
initial_data = qplot.examples.generate_sample_minute_data(stock_code)
data_manager.update_data(initial_data)

# 启动实时更新
# 数据更新线程（每10秒更新一次）
data_manager.start_realtime_updates(interval=10)

# 绘制实时分时图（pyecharts后端）
# 注意：pyecharts后端的实时更新在Jupyter环境中体验更佳
qplot.plot_minute_chart_realtime(data_manager, update_interval=10)

# 使用完毕后停止更新
data_manager.stop_realtime_updates()

# 恢复默认matplotlib后端
qplot.set_default_plot_backend('matplotlib')
```

## 示例

qplot提供了完整的使用示例，您可以在`examples`目录下找到：

### 基本使用示例

```bash
cd examples
python usage_example.py
```

`usage_example.py`包含以下内容：
1. 绘制基本的日K线图
2. 绘制基本的分时图
3. 绘制实时更新的日K线图
4. 绘制实时更新的分时图

### pyecharts后端使用示例

```bash
cd examples
python pyecharts_example.py
```

`pyecharts_example.py`包含以下pyecharts后端特有的示例：
1. 设置全局默认绘图后端为pyecharts
2. 在函数调用时指定使用pyecharts后端
3. 绘制交互式K线图并自定义参数
4. 绘制交互式分时图并保存为HTML文件
5. 实现matplotlib与pyecharts后端的切换

## 核心模块说明

### 1. 绘图器（Plotters）

qplot采用可扩展的插件架构，支持多种绘图后端：

**Matplotlib后端**：
- **CandlestickPlotter**：基于matplotlib的日K线图绘图器，支持各种技术指标
- **MinutePlotter**：基于matplotlib的分时图绘图器，支持实时更新

**Pyecharts后端**（可选）：
- **PyechartsCandlestickPlotter**：基于pyecharts的交互式日K线图绘图器
- **PyechartsMinutePlotter**：基于pyecharts的交互式分时图绘图器

绘图器会根据设置的默认后端或函数调用时指定的后端自动选择。

### 2. 数据管理（DataManager）

- 负责从qdata获取数据、缓存数据、管理实时数据更新
- 支持数据库存储（可选）

### 3. API接口

qplot提供了统一的绘图接口，支持根据后端自动适配不同的绘图行为：

- `plot_kline(df, title='K线图', backend=None, style='charles', volume=True, indicators=None, width=10, height=6)`：
  绘制日K线图，支持选择绘图后端。`backend`参数可设置为'matplotlib'或'pyecharts'，若不指定则使用默认后端。

- `plot_minute_chart(df, title='分时图', backend=None, line_color='blue', show_avg_line=True, show_volume=False, width=10, height=4)`：
  绘制分时图，支持选择绘图后端。`backend`参数可设置为'matplotlib'或'pyecharts'，若不指定则使用默认后端。

- `plot_kline_realtime(data_manager, update_interval=10, backend=None)`：
  绘制实时更新的日K线图，支持选择绘图后端。

- `plot_minute_chart_realtime(data_manager, update_interval=10, backend=None)`：
  绘制实时更新的分时图，支持选择绘图后端。

- `set_default_plot_backend(backend)`：
  设置全局默认的绘图后端，参数可设置为'matplotlib'（默认）或'pyecharts'。在Jupyter环境中使用pyecharts后端时，图表会直接嵌入到Notebook中显示。

## 配置选项

### 绘图配置

qplot支持丰富的配置选项，不同的绘图后端有各自特定的配置参数：

**通用配置**：
- **标题**：设置图表标题
- **样式**：选择图表样式（主要适用于K线图）
- **颜色**：自定义线条颜色
- **尺寸**：设置图表尺寸（matplotlib使用英寸，pyecharts使用像素）
- **技术指标**：添加均线等技术指标（适用于K线图）
- **成交量**：显示/隐藏成交量
- **后端选择**：通过`backend`参数指定使用的绘图后端

**Pyecharts特有配置**：
- **HTML保存**：支持将图表保存为HTML文件（通过`render()`方法或在绘图函数中指定保存路径）
- **交互功能**：支持缩放、平移、悬停提示等交互功能
- **主题选择**：支持多种图表主题
- **图表组件**：可添加工具箱、标题、图例等组件

### 实时更新配置

- **更新间隔**：设置数据更新和图表刷新的时间间隔
- **数据源**：选择数据来源
- **数据库存储**：配置是否使用数据库存储数据

## 注意事项

1. 使用实时功能时，请确保有可靠的数据来源
2. 实时数据更新会占用较多系统资源，请根据实际情况调整更新间隔
3. 本插件仅用于数据可视化，不构成投资建议
4. 使用前请确保已正确安装qdata插件

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交问题和改进建议！如有任何问题，请在GitHub仓库中提交issue。