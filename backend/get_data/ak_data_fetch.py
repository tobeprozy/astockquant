import akshare as ak

class AkDataFetcher:
    def __init__(self, start_date, end_date, interval='1d'):
        """
        初始化FinancialDataFetcher类。
        
        :param start_date: str, 开始日期，格式为'YYYY-MM-DD'。
        :param end_date: str, 结束日期，格式为'YYYY-MM-DD'。
        :param interval: str, 数据间隔，默认为日数据('1d')，可以设置为'1m'表示分钟数据。
        """
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
    def re_time(self):
        import re
        self.start_date=re.sub("-", "", self.start_date)
        self.end_date=re.sub("-", "", self.end_date)

    def get_data(self, symbol, data_type='stock'):
        """
        获取指定金融产品的数据。
        
        :param symbol: str, 股票或ETF代码。
        :param data_type: str, 数据类型，'stock' 或 'etf'。
        :return: DataFrame, 包含金融产品数据。
        """
        # 根据data_type选择不同的接口
        if data_type == 'stock':
            return self._get_stock_data(symbol)
        elif data_type == 'etf':
            return self._get_etf_data(symbol)
        else:
            raise ValueError("Unsupported data type. Choose 'stock' or 'etf'.")

    def _get_stock_data(self, symbol):
        """
        获取股票数据。
        
        :param symbol: str, 股票代码。
        :return: DataFrame, 包含股票数据。
        """
        if self.interval == '1d':
            self.re_time()
            return ak.stock_zh_a_hist(symbol, start_date=self.start_date, end_date=self.end_date)
        elif self.interval == '1m':
            return ak.stock_zh_a_hist_min(symbol, start_date=self.start_date, end_date=self.end_date)
        else:
            raise ValueError("Unsupported interval for stocks.")

    def _get_etf_data(self, symbol):
        """
        获取ETF数据。
        
        :param symbol: str, ETF代码。
        :return: DataFrame, 包含ETF数据。
        """
        if self.interval == '1d':
            self.re_time()
            return ak.fund_etf_hist_em(symbol, period="daily", adjust="qfq",start_date=self.start_date, end_date=self.end_date)
        elif self.interval == '1m':
            # 假设ETF分钟数据接口如下，实际使用时请替换为正确的接口
            return ak.fund_etf_hist_min_em(symbol, period="1", adjust="", start_date=self.start_date, end_date=self.end_date)
        else:
            raise ValueError("Unsupported interval for ETFs.")

# 示例用法
if __name__ == "__main__":
    # fund_name_em_df = ak.fund_name_em()
    # print(fund_name_em_df)

    fetcher = AkDataFetcher(start_date='2024-01-01', end_date='2024-12-07', interval='1d')
    stock_data = fetcher.get_data(symbol="600519", data_type='stock')
    etf_data = fetcher.get_data(symbol="511220", data_type='etf')

    print(stock_data)
    print(etf_data)