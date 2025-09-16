import akshare as ak
def main() -> None:
    # stock_us_daily_df = ak.stock_us_daily(symbol="TSLL", adjust="")
    # print(stock_us_daily_df)
    # stock_us_famous_spot_em_df = ak.stock_us_famous_spot_em(symbol='汽车能源类')
    # # print(stock_us_famous_spot_em_df)
    # tesla_row = stock_us_famous_spot_em_df.query('名称 == "特斯拉"')
    # print(tesla_row)

    stock_us_spot_em_df = ak.stock_us_spot_em()
    tesla_row = stock_us_spot_em_df[stock_us_spot_em_df['代码'].str.contains('YANG', na=False)]
    print(tesla_row)

    stock_us_hist_min_em_df = ak.stock_us_hist_min_em(symbol="105.TSLL",start_date="2025-06-01 09:32:00",end_date="2025-09-10 09:32:00")
    print(stock_us_hist_min_em_df)
    stock_us_hist_min_em_df = ak.stock_us_hist_min_em(symbol="105.TSDD",start_date="2025-06-01 09:32:00",end_date="2025-09-10 09:32:00")
    print(stock_us_hist_min_em_df)

if __name__ == '__main__':
    main()


