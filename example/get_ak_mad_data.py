from datetime import datetime
import pandas as pd
import akshare as ak  # 使用 Akshare
import backtrader as bt  
import akshare as ak
import pandas as pd

# 获取沪深300指数的历史数据
index_code = "000300"
start_date = "2024-06-01"
end_date = "2024-12-06"
index_data = ak.index_zh_a_hist(symbol=index_code, period="daily", start_date=start_date, end_date=end_date)

# 数据预览
print(index_data.head())

import matplotlib.pyplot as plt
#下面这两行为了防止报错，如果没有问题可以不加
import matplotlib
matplotlib.use('TkAgg')

# 转换日期格式
index_data['date'] = pd.to_datetime(index_data['日期'])
index_data.set_index('date', inplace=True)

# 绘制收盘价趋势图
plt.figure(figsize=(12, 6))
plt.plot(index_data['收盘'], label='Close Price')
plt.title('hs300')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()
plt.show()


# 计算5日和20日移动平均线
index_data['MA5'] = index_data['收盘'].rolling(window=5).mean()
index_data['MA20'] = index_data['收盘'].rolling(window=20).mean()

# 策略：当MA5上穿MA20时买入，下穿时卖出
index_data['Signal'] = 0
index_data.loc[index_data['MA5'] > index_data['MA20'], 'Signal'] = 1
index_data.loc[index_data['MA5'] < index_data['MA20'], 'Signal'] = -1

# 绘制策略信号图
plt.figure(figsize=(12, 6))
plt.plot(index_data['收盘'], label='Close Price')
plt.plot(index_data['MA5'], label='MA5')
plt.plot(index_data['MA20'], label='MA20')
plt.title('Signal')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()