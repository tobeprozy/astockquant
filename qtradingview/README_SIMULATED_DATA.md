# 使用本地模拟股票数据

本文档介绍如何使用本地UDF服务器提供模拟股票数据给TradingView图表组件。

## 工作原理

TradingView图表通过UDF（Universal Data Feed）协议从服务器获取数据。我们创建了一个简单的Python服务器，实现了UDF协议的基本功能，可以生成模拟的股票OHLCV（开盘价、最高价、最低价、收盘价、成交量）数据。

## 步骤说明

### 1. 运行本地UDF服务器

首先，确保您的系统已安装Python 3以及所需的依赖库：

```bash
cd /Users/zzy/workspace/AstockQuant/qtradingview
pip install pandas numpy
```

然后运行UDF服务器：

```bash
python simple_udf_server.py
```

默认情况下，服务器将在端口8080上运行。如果需要使用其他端口，可以指定端口号：

```bash
python simple_udf_server.py 8888
```

服务器启动后，将显示可用的股票代码（AAPL、MSFT、GOOG、TSLA、BABA）和API端点信息。

### 2. 启动前端应用

在另一个终端窗口中，启动Vue应用：

```bash
cd /Users/zzy/workspace/AstockQuant/qtradingview
npm install
npm run dev
```

### 3. 查看效果

打开浏览器，访问Vue应用提供的本地地址（通常是http://localhost:5173/），您应该能看到TradingView图表组件加载了来自本地UDF服务器的模拟股票数据。

## 注意事项

1. 如果您修改了服务器端口，需要相应地更新`TradingViewChart.vue`文件中的数据馈送URL。

2. 当前实现提供了5只股票的模拟数据，数据是随机生成的，但保持了合理的股票价格波动模式。

3. 服务器支持UDF协议的基本功能，包括：
   - 配置信息（/config）
   - 股票搜索（/search）
   - 股票详情（/symbols）
   - 历史数据（/history）
   - 时间同步（/time）

4. 模拟数据基于当前日期生成过去365个工作日的数据。

## 扩展建议

1. 要添加更多股票数据，可以修改`simple_udf_server.py`文件中的`sample_data`字典。

2. 可以调整数据生成逻辑，使其更符合特定股票的波动特性。

3. 对于更复杂的需求，可以考虑从CSV文件或数据库加载历史数据。