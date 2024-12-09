
import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from get_data.ak_data_fetch import FinancialDataFetcher
import pandas as pd
import backtrader as bt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class BackEngine:
    def __init__(self, stock_index, start_date, end_date, strategy):
        self.stock_index = stock_index
        self.start_date = start_date
        self.end_date = end_date
        self.strategy = strategy
        self.cerebro = bt.Cerebro()
        self.start_cash = 100000.0

    def fetch_data(self):
        # 创建数据获取器
        fetcher = FinancialDataFetcher()
        # 获取股票数据
        fetcher.fetch_fund_info(symbol=self.stock_index, start_date=self.start_date, end_date=self.end_date)
        fetcher.fund_rename()
        df = fetcher.fund_info.iloc[:, :6]
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df.set_index('date', inplace=True)
        return df

    def setup_cerebro(self, data):
        self.cerebro.adddata(data)
        self.cerebro.addstrategy(self.strategy)
        self.cerebro.broker.setcash(self.start_cash)
        self.cerebro.broker.setcommission(commission=0.00025)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    def run(self):
        data = bt.feeds.PandasData(dataname=self.fetch_data())
        self.setup_cerebro(data)
        # 打印初始资金
        logging.debug('初始投资组合市值: %.2f', self.cerebro.broker.getvalue())
        result = self.cerebro.run()
        # 打印回测完成后的资金
        logging.debug('最终投资组合市值: %.2f', self.cerebro.broker.getvalue())
        return result

    def print_results(self, result):
        strat = result[0]
        logging.debug('Final Portfolio Value: %.2f', self.cerebro.broker.getvalue())
        logging.debug('SR: %s', strat.analyzers.SharpeRatio.get_analysis()['sharperatio'])
        logging.debug('DW: %s', strat.analyzers.DW.get_analysis())
        port_value = self.cerebro.broker.getvalue()
        pnl = port_value - self.start_cash
        logging.debug("初始资金: %s", self.start_cash)
        logging.debug("回测期间：%s:%s", self.start_date, self.end_date)
        logging.info("总资金: %s", round(port_value, 2))
        logging.info("净收益: %s", round(pnl, 2))

        pyfoliozer = strat.analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
        logging.debug("returns: %s", returns)
        logging.debug("positions: %s", positions)
        logging.debug("transactions: %s", transactions)
        logging.debug("gross_lev: %s", gross_lev)

    def plot_results(self):
        self.cerebro.plot()

class MultiBackEngine(BackEngine):
    def __init__(self, stock_index, stock_index1, start_date, end_date, strategy):
        super().__init__(stock_index, start_date, end_date, strategy)
        self.stock_index1 = stock_index1

    def fetch_data(self):
        # 获取第一个数据源
        df = super().fetch_data()

        # print(df)
        # 获取第二个数据源
        fetcher1 = FinancialDataFetcher()
        fetcher1.fetch_fund_info(symbol=self.stock_index1, start_date=self.start_date, end_date=self.end_date)
        fetcher1.fund_rename()
        df1 = fetcher1.fund_info.iloc[:, :6]
        df1.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df1['date'] = pd.to_datetime(df1['date'], format='%Y-%m-%d')
        df1.set_index('date', inplace=True)
        # print(df1)
        return df, df1

    def setup_cerebro(self, data, data1):
        # 添加第一个数据源
        bt_data = bt.feeds.PandasData(dataname=data)
        self.cerebro.adddata(bt_data, name=self.stock_index)

        # 添加第二个数据源
        bt_data1 = bt.feeds.PandasData(dataname=data1)
        self.cerebro.adddata(bt_data1, name=self.stock_index1)

        self.cerebro.addstrategy(self.strategy)
        self.cerebro.broker.setcash(self.start_cash)
        self.cerebro.broker.setcommission(commission=0.00025)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')


    def run(self):
        data, data1 = self.fetch_data()
        self.setup_cerebro(data, data1)
        result = self.cerebro.run()
        return result