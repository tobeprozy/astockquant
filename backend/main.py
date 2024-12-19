

import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

    
from get_data.ak_data_fetch import FinancialDataFetcher
import datetime
import pandas as pd
import pyfolio as pf
import matplotlib.pyplot as plt
import backtrader as bt  # 升级到最新版，pip install matplotlib==3.2.2

from strategies.strategy import Strategy1,SmaCross,PairTradingStrategy,Strategy_MACD,Strategy_MCACD2,Strategy_MACD3

from backEngine.backEngine import BackEngine,MultiBackEngine
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ ==  "__main__":

    stock_index = '512480' # 半导体ETF
    stock_index = '512200' # 房地产ETF
    stock_index = '159607' # 互联网ETF
    # stock_index = '159892' # 医药ETF
    # stock_index = '512690' # 白酒ETF

    s_date = (datetime.datetime.now() - datetime.timedelta(days=240)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    engine = BackEngine(stock_index, s_date, e_date, Strategy_MACD3)
    result = engine.run()
    engine.print_results(result)
    engine.plot_results()
    
    

def get_fund_data(stock_index,s_date,e_date):
    # 创建数据获取器
    fetcher = FinancialDataFetcher()
    # 获取股票数据
    fetcher.fetch_fund_info(symbol=stock_index, start_date=s_date, end_date=e_date)
    fetcher.fund_rename()
    return fetcher.fund_info

if __name__ ==  "__main6__":

    stock_index = '512200'

    s_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    df=get_fund_data(stock_index,s_date,e_date)
    print(df)
    # 计算开盘幅度，即今天的开盘价与昨天的收盘价之间的变化
    df['OpenAmplitude'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1) * 100
    # 计算开盘幅度，即今天的开盘价与昨天的收盘价之间的变化
    df['CloseAmplitude'] = (df['close'] - df['close'].shift(1)) / df['close'].shift(1) * 100

    # 打印结果
    print("**********************所有结果*************************")
    print(df[['date', 'OpenAmplitude']])
    
    # 打印所有大于0的开盘幅度
    print("**********************大于0的开盘幅度*************************")
    print(df[df['OpenAmplitude'] > 0])
    # 确定开盘幅度大于0的天数
    positive_open_amplitude_count = df[df['OpenAmplitude'] > 0].shape[0]
    # 计算总天数（排除第一天，因为它没有前一天的收盘价）
    total_days = df.shape[0] - 1
    # 计算占比
    positive_open_amplitude_ratio = positive_open_amplitude_count / total_days
    # 打印结果
    
    print(f"开盘幅度大于0的占比是: {positive_open_amplitude_ratio:.2f}")
    
    print("**********************大于0的，上一天*************************")
    # 将'OpenAmplitude'列向上移动一行
    df['NextOpenAmplitude'] = df['OpenAmplitude'].shift(-1)
    # 打印高开的前一天的情况
    print(df[df['NextOpenAmplitude'] > 0])
    
    ## 统计下一天高开时候，当天下跌的概率
    total_days = df[df['NextOpenAmplitude'] > 0][0] - 1

    df.to_csv(f'{stock_index}.csv')
    
    
    
    
if __name__ ==  "__main5__":

    stock_index = '159607'

    s_date = (datetime.datetime.now() - datetime.timedelta(days=120)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    engine = BackEngine(stock_index, s_date, e_date, Strategy_MCACD2)
    result = engine.run()
    engine.print_results(result)
    engine.plot_results()


if __name__ ==  "__main4__":


    stock_index = '512200'
    stock_index1 = '159819'
    s_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    engine = MultiBackEngine(stock_index, stock_index1, s_date, e_date, PairTradingStrategy)
    result = engine.run()
    engine.print_results(result)
    engine.plot_results()


if __name__ ==  "__main3__":

    stock_index = '512200'

    s_date = (datetime.datetime.now() - datetime.timedelta(days=100)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    engine = BackEngine(stock_index, s_date, e_date, Strategy1)
    result = engine.run()
    engine.print_results(result)
    engine.plot_results()

    
if __name__ ==  "__main2__":

    stock_index = '512200'

    s_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    # 创建数据获取器
    fetcher = FinancialDataFetcher()
    # 获取股票数据
    fetcher.fetch_fund_info(symbol=stock_index, start_date=s_date, end_date=e_date)
    fetcher.fund_rename()
    df=fetcher.fund_info.iloc[:,:6]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume'] # 字段必须相同，不然会报错Axis limits cannot be NaN or Inf
    print(df)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')  # 使用正确的格式
    df.set_index('date', inplace=True)  # 将 'date' 列设置为索引

    # 创建 Backtrader 数据源
    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.adddata(data)  # 将数据传入回测系统   
    cerebro.addstrategy(Strategy1)

    # 加入pyfolio分析者
    start_cash=100000.0
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=0.00025)
    result = cerebro.run()  # 运行回测系统


    port_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
    pnl = port_value - start_cash  # 盈亏统计

    print(f"初始资金: {start_cash}\n回测期间：{s_date}:{e_date}")
    print(f"总资金: {round(port_value, 2)}")
    print(f"净收益: {round(pnl, 2)}")



    cerebro.plot()  # 画图
    plt.savefig('backtrader_plot.png')  # 保存绘图结果为 PNG 文件

    cerebro.broker.getvalue()

    strat = result[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    print("returns:", returns)
    print("positions:", positions)
    print("transactions:", transactions)
    print("gross_lev:", gross_lev)
    

if __name__ ==  "__main1__":

    stock_index = '512200'

    s_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    # 创建数据获取器
    fetcher = FinancialDataFetcher()
    # 获取股票数据
    fetcher.fetch_fund_info(symbol=stock_index, start_date=s_date, end_date=e_date)
    fetcher.fund_rename()
    df=fetcher.fund_info.iloc[:,:6]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume'] # 字段必须相同，不然会报错Axis limits cannot be NaN or Inf
    print(df)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')  # 使用正确的格式
    df.set_index('date', inplace=True)  # 将 'date' 列设置为索引

    # 创建 Backtrader 数据源
    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.adddata(data)  # 将数据传入回测系统   
    cerebro.addstrategy(Strategy1)

    start_cash=100000.0
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name = 'SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    # 添加 Pyfolio 分析器
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=0.00025)
    result = cerebro.run()  # 运行回测系统




    strat = result[0]
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('SR:', strat.analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('DW:', strat.analyzers.DW.get_analysis())
    

    port_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
    pnl = port_value - start_cash  # 盈亏统计

    print(f"初始资金: {start_cash}\n回测期间：{s_date}:{e_date}")
    print(f"总资金: {round(port_value, 2)}")
    print(f"净收益: {round(pnl, 2)}")


    cerebro.plot()  # 画图
    plt.savefig('backtrader_plot.png')  # 保存绘图结果为 PNG 文件


    pyfoliozer = strat.analyzers.getbyname('pyfolio')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    print("returns:", returns)
    print("positions:", positions)
    print("transactions:", transactions)
    print("gross_lev:", gross_lev)

