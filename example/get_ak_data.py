from datetime import datetime
import pandas as pd
import akshare as ak  # 使用 Akshare
import backtrader as bt  

# def get_data(code, start="2017-03-01", end="2023-10-22"):
#     # 使用 Akshare 获取股票历史数据
#     df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start.replace("-", ""), end_date=end.replace("-", ""), adjust="")
    
#     # 打印返回的数据结构以进行调试
#     print("获取的数据：")
#     print(df.head())  # 打印前几行数据
#     print("数据列名：", df.columns)  # 打印列名

#     # 确保索引为日期类型
#     if '日期' in df.columns:  # 根据 Akshare 返回的列名调整
#         df.index = pd.to_datetime(df['日期'])  # 使用 '日期' 列作为索引
#     else:
#         print("警告：数据中没有 '日期' 列，使用默认索引。")
#         df.index = pd.to_datetime(df.index)  # 如果没有 '日期' 列，使用默认索引
    
#     df["openinterest"] = 0  # 添加 openinterest 列
#     df = df[["开盘", "最高", "最低", "收盘", "成交量", "openinterest"]]  # 选择需要的列
#     return df

# if __name__ == "__main__":
#     start = "2024-12-01"
#     end = "2024-12-06"
#     # 注意：这里的代码需要是 Akshare 支持的股票代码格式，例如 "000001"
#     dataframe = get_data("159892", start=start, end=end)
#     # 将数据转换为 Backtrader 数据格式
#     data = bt.feeds.PandasData(dataname=dataframe, fromdate=pd.to_datetime(start), todate=pd.to_datetime(end))
#     print(dataframe)



# def get_etf_data(symbol, start_date, end_date):
#     # 使用 Akshare 获取ETF的历史分钟数据
#     df = ak.fund_etf_hist_min_em(symbol=symbol, period="1", adjust="", start_date=start_date, end_date=end_date)
    
#     # 打印返回的数据结构以进行调试
#     print("获取的数据：")
#     print(df.head())  # 打印前几行数据
#     print("数据列名：", df.columns)  # 打印列名

#     # 确保索引为日期时间类型
#     if '时间' in df.columns:  # 根据 Akshare 返回的列名调整
#         df['时间'] = pd.to_datetime(df['时间'])  # 将 '时间' 列转换为日期时间格式
#         df.set_index('时间', inplace=True)  # 将 '时间' 列设置为索引
#     else:
#         print("警告：数据中没有 '时间' 列，无法设置索引。")
    
#     df["openinterest"] = 0  # 添加 openinterest 列
#     # 选择需要的列，假设需要的列为开盘、最高、最低、收盘、成交量
#     df = df[["开盘", "最高", "最低", "收盘", "成交量", "openinterest"]]  # 根据实际列名选择
#     return df

# if __name__ == "__main__":
#     symbol = "159892"  # ETF代码
#     start_date = "2024-12-01 09:32:00"  # 开始时间
#     end_date = "2024-12-06 15:40:00"  # 结束时间
    
#     dataframe = get_etf_data(symbol, start_date, end_date)
    
#     # 将数据转换为 Backtrader 数据格式
#     data = bt.feeds.PandasData(dataname=dataframe, fromdate=pd.to_datetime(start_date), todate=pd.to_datetime(end_date))
#     print(dataframe)


def get_etf_data(symbol, start_date, end_date):
    # 使用 Akshare 获取ETF的历史数据
    df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="")
    
    # 打印返回的数据结构以进行调试
    print("获取的数据：")
    print(df.head())  # 打印前几行数据
    print("数据列名：", df.columns)  # 打印列名

    # 确保索引为日期类型
    if '日期' in df.columns:  # 根据 Akshare 返回的列名调整
        df['日期'] = pd.to_datetime(df['日期'])  # 将 '日期' 列转换为日期时间格式
        df.set_index('日期', inplace=True)  # 将 '日期' 列设置为索引
    else:
        print("警告：数据中没有 '日期' 列，无法设置索引。")
    
    df["openinterest"] = 0  # 添加 openinterest 列
    # 选择需要的列，假设需要的列为开盘、收盘、最高、最低、成交量
    df = df[["开盘", "收盘", "最高", "最低", "成交量", "openinterest"]]  # 根据实际列名选择
    return df

if __name__ == "__main__":
    symbol = "159892"  # ETF代码
    start_date = "20241201"  # 开始时间
    end_date = "20241206"  # 结束时间
    
    dataframe = get_etf_data(symbol, start_date, end_date)
    
    # 将数据转换为 Backtrader 数据格式
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=pd.to_datetime(start_date), todate=pd.to_datetime(end_date))
    print(dataframe)