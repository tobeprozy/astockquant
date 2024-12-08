import akshare as ak

# get realtime all fund list
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
print(stock_zh_a_spot_em_df)


stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="")
print(stock_zh_a_hist_df)

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="qfq")
print(stock_zh_a_hist_df)

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="hfq")
print(stock_zh_a_hist_df)


stock_zh_kcb_daily_df = ak.stock_zh_kcb_daily(symbol="sh688399", adjust="hfq")
print(stock_zh_kcb_daily_df)


# 注意：该接口返回的数据只有最近一个交易日的有开盘价，其他日期开盘价为 0
stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", start_date="2024-03-20 09:30:00", end_date="2024-03-20 15:00:00", period="1", adjust="")
print(stock_zh_a_hist_min_em_df)

stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", start_date="2024-03-20 09:30:00", end_date="2024-03-20 15:00:00", period="5", adjust="hfq")
print(stock_zh_a_hist_min_em_df)




# get fund list
fund_name_em_df = ak.fund_name_em()
print(fund_name_em_df)

fund_name_em_df=fund_lof_spot_em()
print(fund_name_em_df)

# history
fund_etf_hist_em_df = ak.fund_etf_hist_em(symbol="513500", period="daily", start_date="20000101", end_date="20230201", adjust="")
print(fund_etf_hist_em_df)

fund_etf_hist_em_df = ak.fund_etf_hist_em(symbol="513500", period="daily", start_date="20000101", end_date="20230201", adjust="qfq")
print(fund_etf_hist_em_df)

fund_etf_hist_em_df = ak.fund_etf_hist_em(symbol="513500", period="daily", start_date="20000101", end_date="20230201", adjust="hfq")
print(fund_etf_hist_em_df)

fund_lof_hist_em_df = ak.fund_lof_hist_em(symbol="166009", period="daily", start_date="20000101", end_date="20230703", adjust="")
print(fund_lof_hist_em_df)

fund_lof_hist_em_df = ak.fund_lof_hist_em(symbol="166009", period="daily", start_date="20000101", end_date="20230703", adjust="qfq")
print(fund_lof_hist_em_df)

fund_lof_hist_em_df = ak.fund_lof_hist_em(symbol="166009", period="daily", start_date="20000101", end_date="20230703", adjust="hfq")
print(fund_lof_hist_em_df)