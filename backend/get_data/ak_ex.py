import akshare as ak


stock_info_a_code_name_df = ak.stock_info_a_code_name()
print(stock_info_a_code_name_df)

stock_info_sh_name_code_df = ak.stock_info_sh_name_code(symbol="主板A股")
print(stock_info_sh_name_code_df)

stock_info_sz_name_code_df = ak.stock_info_sz_name_code(symbol="A股列表")
print(stock_info_sz_name_code_df)

# get realtime all fund list
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
print(stock_zh_a_spot_em_df)

stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
print(stock_sh_a_spot_em_df)

stock_sz_a_spot_em_df = ak.stock_sz_a_spot_em()
print(stock_sz_a_spot_em_df)

stock_bj_a_spot_em_df = ak.stock_bj_a_spot_em()
print(stock_bj_a_spot_em_df)

stock_new_a_spot_em_df = ak.stock_new_a_spot_em()
print(stock_new_a_spot_em_df)

stock_cy_a_spot_em_df = ak.stock_cy_a_spot_em()
print(stock_cy_a_spot_em_df)

stock_kc_a_spot_em_df = ak.stock_kc_a_spot_em()
print(stock_kc_a_spot_em_df)

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="")
print(stock_zh_a_hist_df)

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="qfq")
print(stock_zh_a_hist_df)

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="hfq")
print(stock_zh_a_hist_df)

stock_zh_a_cdr_daily_df = ak.stock_zh_a_cdr_daily(symbol='sh689009', start_date='20201103', end_date='20201116')
print(stock_zh_a_cdr_daily_df)




# 注意：该接口返回的数据只有最近一个交易日的有开盘价，其他日期开盘价为 0
stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", start_date="2024-03-20 09:30:00", end_date="2024-03-20 15:00:00", period="1", adjust="")
print(stock_zh_a_hist_min_em_df)

stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", start_date="2024-03-20 09:30:00", end_date="2024-03-20 15:00:00", period="5", adjust="hfq")
print(stock_zh_a_hist_min_em_df)

stock_intraday_em_df = ak.stock_intraday_em(symbol="000001")
print(stock_intraday_em_df)



# get fund list
fund_name_em_df = ak.fund_name_em()
print(fund_name_em_df)

fund_info_index_em_df = ak.fund_info_index_em(symbol="沪深指数", indicator="增强指数型")
print(fund_info_index_em_df)

# get realtime all fund list
fund_lof_spot_em_df = ak.fund_lof_spot_em()
print(fund_lof_spot_em_df)

fund_etf_hist_min_em_df = ak.fund_etf_hist_min_em(symbol="511220", period="1", adjust="", start_date="2024-03-20 09:30:00", end_date="2024-03-20 17:40:00")
print(fund_etf_hist_min_em_df)

fund_etf_hist_min_em_df = ak.fund_etf_hist_min_em(symbol="513500", period="5", adjust="hfq", start_date="2023-12-11 09:32:00", end_date="2023-12-11 17:40:00")
print(fund_etf_hist_min_em_df)

fund_lof_hist_min_em_df = ak.fund_lof_hist_min_em(symbol="166009", period="1", adjust="", start_date="2024-03-20 09:30:00", end_date="2024-03-20 14:40:00")
print(fund_lof_hist_min_em_df)

fund_lof_hist_min_em_df = ak.fund_lof_hist_min_em(symbol="166009", period="5", adjust="hfq", start_date="2023-07-01 09:32:00", end_date="2023-07-04 14:40:00")
print(fund_lof_hist_min_em_df)

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