"""
qdata 包使用示例

这个示例展示了如何使用 qdata 包获取股票数据、ETF数据、股票列表等信息。
"""

import qdata
import pandas as pd

# 示例1：基本使用（自动初始化，使用默认的akshare数据源）
# print("示例1：基本使用")
# df = qdata.get_daily_data('600000', '2023-01-01', '2023-06-30')
# print(f"获取到的日线数据形状: {df.shape}")
# print(df.head())
# print()

# 示例2：手动初始化
print("示例2：手动初始化")
qdata.init()

# 获取股票列表
hs300_stocks = qdata.get_stock_list()
print(f"获取到的股票列表数量: {len(hs300_stocks)}")
if not hs300_stocks.empty:
    print(f"部分股票列表:")
    print(hs300_stocks.head())
print()

# 示例3：使用TuShare数据源（需要token）
print("示例3：使用TuShare数据源")
try:
    # 假设已经设置了环境变量 TUSHARE_TOKEN
    qdata.set_default_backend('tushare')
    
    # 获取ETF列表
    etf_list = qdata.get_etf_list()
    print(f"获取到的ETF列表数量: {len(etf_list)}")
    if not etf_list.empty:
        print(f"部分ETF列表:")
        print(etf_list.head())
except Exception as e:
    print(f"使用TuShare数据源失败: {e}")
    print("请确保已设置TUSHARE_TOKEN环境变量")
print()

# 示例4：获取分时数据
print("示例4：获取分时数据")
qdata.set_default_backend('akshare')  # 切换回akshare

try:
    minute_data = qdata.get_minute_data('600000', '2023-06-30', freq='1min')
    print(f"获取到的分时数据形状: {minute_data.shape}")
    print(minute_data.head())
except Exception as e:
    print(f"获取分时数据失败: {e}")
print()

# 示例5：处理数据获取异常
print("示例5：处理数据获取异常")
try:
    # 尝试获取不存在的股票数据
    df = qdata.get_daily_data('999999', '2023-01-01', '2023-06-30')
except Exception as e:
    print(f"捕获到异常: {e}")
print()

# 示例6：使用CSV数据源
print("示例6：使用CSV数据源")
try:
    # 假设当前目录下有一个data子目录，包含CSV数据文件
    import os
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # 如果data目录不存在，创建它
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        # 创建一个示例CSV文件
        sample_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'open': [10.0, 10.2, 10.5],
            'high': [10.5, 10.7, 10.8],
            'low': [9.9, 10.1, 10.3],
            'close': [10.3, 10.5, 10.7],
            'volume': [1000000, 1200000, 1500000]
        })
        sample_data.to_csv(os.path.join(data_dir, '600000_daily.csv'), index=False)
        print(f"已创建示例CSV文件: {os.path.join(data_dir, '600000_daily.csv')}")
    
    # 使用CSV数据源
    qdata.set_default_backend('csv')
    
    # 从CSV文件获取数据
    csv_data = qdata.get_daily_data('600000', '2023-01-01', '2023-01-03')
    print("从CSV文件获取的数据:")
    print(csv_data)
except Exception as e:
    print(f"使用CSV数据源失败: {e}")
print()

# 示例7：获取当前使用的数据源
print("示例7：获取当前使用的数据源")
current_provider = qdata.get_provider()
print(f"当前使用的数据源类型: {type(current_provider).__name__}")