import backtrader as bt
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

class StockScreener(bt.Strategy):
    params = (
        ('period', 20),
    )

    def __init__(self):
        # 使用列表推导式（List Comprehension）来创建一个列表
        # for d in self.datas：这是一个循环，遍历 self.datas 列表中的每一个数据源 d。
        # self.datas 通常包含多个数据源，每个数据源代表一个股票或资产的历史数据。
        # 对于每一个数据源 d，创建一个简单移动平均线指标。d.close 表示该数据源的收盘价数据，
        self.smas = [bt.indicators.SimpleMovingAverage(d.close, period=self.params.period) for d in self.datas]
        self.selected_stocks = set()
        self.crossovers = [bt.ind.CrossOver(d.close, self.smas[i]) for i, d in enumerate(self.datas)]  # crossover signals

    def next(self):
        # 使用 enumerate 函数来遍历 self.datas 列表，并为每个元素提供一个索引 i 和对应的值 d。
        # self.datas 是一个包含多个数据源的列表，每个数据源代表一个股票或资产的历史数据。
        for i, d in enumerate(self.datas):
            if self.crossovers[i] > 0:
                print('加入: ', d._name)
                self.selected_stocks.add(d._name)
            elif self.crossovers[i] < 0:
                print('移除: ', d._name)
                self.selected_stocks.discard(d._name)
# ========获取300代码===============================
def get_hs300_stocks():
    # 获取沪深300指数的成分股
    hs300_df = ak.index_stock_cons(symbol="000300")
    hs300_stocks = hs300_df['品种代码'] # .tolist()
    hs300_stocks=hs300_stocks.tolist()
    print('完成获取300股票代码')
    return hs300_stocks

# ========数据清洗=====================================
def fetch_data(stock_code, start_date, end_date):
    stock_data = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
    stock_data.index = pd.to_datetime(stock_data['日期'])
    stock_data = stock_data[['开盘', '最高', '最低', '收盘', '成交量']]
    stock_data.columns = ['open', 'high', 'low', 'close', 'volume']
    return stock_data
# ========遍历300个股票,分别策略分析==========
def run_screener(stock_codes, start_date, end_date):
    cerebro = bt.Cerebro()
    print('加入数据源')
    for stock_code in stock_codes:
        data = fetch_data(stock_code, start_date, end_date)
        
        if len(data) < 20:
            print(f"Warning: Data for {stock_code} is too short. Skipping.")
            continue
        data = bt.feeds.PandasData(dataname=data)
        
        cerebro.adddata(data, name=stock_code)
    cerebro.addstrategy(StockScreener)
    results = cerebro.run()
    print(results)
    
    return results[0].selected_stocks

# ========回测天数,返回开始日期和今天==========
def get_date_range(days_before):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_before)
    
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    return start_date_str, end_date_str

# ======================================================================================
# ======================================================================================
if __name__ == '__main__':
    stock_codes = get_hs300_stocks()
    
    start_date, end_date = get_date_range(50)
    
    selected_stocks = run_screener(stock_codes, start_date, end_date)
    print("Selected Stocks:", selected_stocks)
