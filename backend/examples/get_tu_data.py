from datetime import datetime

import numpy as np
import pandas as pd
import tushare as ts
import backtrader as bt  
import akshare as ak
# 如果要使用旧版tushare，需要指定pip包
# pip install numpy==1.23.5 pandas==1.5.3 -i https://pypi.tuna.tsinghua.edu.cn/simple

def get_data(code, start="2024-08-01", end="2024-09-30"):
    df = ts.get_k_data(code, autype="qfq", start=start, end=end)
    #df = ts.pro_bar(ts_code=code, adj='qfq', start_date=start, end_date=end)
    df.index = pd.to_datetime(df.date)
    df["openinterest"] = 0
    df = df[["open", "high", "low", "close", "volume", "openinterest"]]
    return df

if __name__ == "__main__":

    start = datetime(2024, 12, 1)
    end = datetime(2024, 12, 6)
    dataframe = get_data("159892", start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=start, todate=end)
    print(dataframe)

    df=ak.fund_etf_hist_em(symbol="159892", period="daily", start_date=start, end_date=end, adjust="qfq")
    print(df)
    df = ts.get_k_data("159892", autype="qfq", start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    print(df)

    