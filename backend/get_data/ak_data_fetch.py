import akshare as ak
import json
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


import akshare as ak
import pandas as pd

class FinancialDataFetcher:
    def __init__(self):
        self.stock_list = None
        self.fund_list = None
    
    def fetch_stock_list(self):
        """获取所有股票列表"""
        self.stock_list = ak.stock_zh_a_spot_em()
        print("Stock List:")
        print(self.stock_list)
    
    def fetch_fund_list(self):
        """获取所有基金列表"""
        self.fund_list = ak.fund_name_em()
        print("Fund List:")
        print(self.fund_list)
    
    def fetch_stock_info(self, symbol, start_date=None, end_date=None):
        """根据股票代码获取股票信息，支持可选的日期范围"""
        if start_date is None or end_date is None:
            # 默认获取所有历史数据
            stock_info = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="19900101", end_date="20240101", adjust="qfq")
        else:
            stock_info = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        return stock_info
    
    def fetch_fund_info(self, symbol, start_date=None, end_date=None):
        """根据基金代码获取基金信息，支持可选的日期范围"""
        if start_date is None or end_date is None:
            # 默认获取所有历史数据
            fund_info = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date="19900101", end_date="20240101", adjust="qfq")
        else:
            fund_info = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        return fund_info
    
    def filter_funds_by_name(self,df,name):
        filtered_df = df[df['基金简称'].str.contains(name, na=False)]
        return filtered_df

    # def save_stock_list(self,name):
    #     self.stock_list[['代码', '名称']].to_json(name, orient='records')
    
    # def save_fund_list(self,name):
    #     self.fund_list[['基金代码', '基金简称']].to_json(name, orient='records')

    def save_fund_list(self, name):
        # 将基金列表保存为格式化的JSON文件，确保中文字符不被转义
        data = self.fund_list[['基金代码', '基金简称']].to_dict(orient='records')
        with open(name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def save_stock_list(self, name):
        # 将股票列表保存为格式化的JSON文件，确保中文字符不被转义
        data = self.stock_list[['代码', '名称']].to_dict(orient='records')
        with open(name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


# 示例用法
if __name__ == "__main__":
    # fund_name_em_df = ak.fund_name_em()
    # print(fund_name_em_df)

    # fetcher = AkDataFetcher(start_date='2024-01-01', end_date='2024-12-07', interval='1d')
    # stock_data = fetcher.get_data(symbol="600519", data_type='stock')
    # etf_data = fetcher.get_data(symbol="511220", data_type='etf')

    # print(stock_data)
    # print(etf_data)
    # 使用示例
    fetcher = FinancialDataFetcher()
    # stock_info=fetcher.fetch_stock_list()
    # fund_info=fetcher.fetch_fund_list()
    # print(fetcher.filter_funds_by_name(fetcher.fund_list,"医药"))
    
    # fetcher.save_stock_list("stock_list.json")
    # fetcher.save_fund_list("fund_list.json")

    with open("fund_list.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, item in enumerate(data):
        if i < 5:  # 只遍历前五个
            print(item)
            print(fetcher.fetch_fund_info(symbol=item['基金代码']))
            
        else:
            break  # 到达第五个后停止循环





    # # 获取特定股票的所有历史信息
    # specific_stock_info = fetcher.fetch_stock_info("600519")
    # print("Specific Stock Info:")
    # print(specific_stock_info)

    # # 获取特定基金的所有历史信息
    # specific_fund_info = fetcher.fetch_fund_info("510300")
    # print("Specific Fund Info:")
    # print(specific_fund_info)

    # # 根据股票类别筛选股票信息，例如筛选科技类股票
    # tech_stock_info = fetcher.filter_stocks_by_category("科技")
    # print("Tech Stock Info:")
    # print(tech_stock_info)