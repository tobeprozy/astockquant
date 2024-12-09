
import backtrader as bt  # 升级到最新版，pip install matplotlib==3.2.2

class StrategyBase(bt.Strategy):
    def notify_order(self, order):
        # 未被处理的订单
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 已经处理的订单
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, ref:%.0f，Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                    (order.ref,  # 订单编号
                        order.executed.price,  # 成交价
                        order.executed.value,  # 成交额
                        order.executed.comm,  # 佣金
                        order.executed.size,  # 成交量
                        order.data._name))  # 股票名称
            else:  # Sell
                self.log('SELL EXECUTED, ref:%.0f, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                            (order.ref,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm,
                            order.executed.size,
                            order.data._name))

class MyStrategy(StrategyBase):
    # 定义我们自己写的这个 MyStrategy 类的专有属性
    def __init__(self):
        '''必选，策略中各类指标的批量计算或是批量生成交易信号都可以写在这里'''
        print(self.datas)
    # 构建交易函数: 策略交易的主体部分
    def next(self):
        '''必选，在这里根据交易信号进行买卖下单操作'''
        print(self.data.close[0])


        
class Strategy1(StrategyBase):
    """
    主策略程序
    """
    params = (
        ('printlog', True),
        ("maperiod", 5),
    )
    
    def __init__(self):
        """
        初始化函数
        """
        self.data_close = self.datas[0].close  # 指定价格序列
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        # 添加移动均线指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod
        )
    def log(self, txt, dt=None, doprint=False):
        """
        记录交易策略的执行过程
        """
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def next(self):
        """
        执行逻辑
        """
        if self.order:  # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        if not self.position:  # 没有持仓
            if self.data_close[0] > self.sma[0]:  # 执行买入条件判断：收盘价格上涨突破20日均线
                self.order = self.buy(size=50000)  # 执行买入
        else:
            if self.data_close[0] < self.sma[0]:  # 执行卖出条件判断：收盘价格跌破20日均线
                self.order = self.sell(size=50000)  # 执行卖出
        # 更新指令状态
        if self.order:
            self.buy_price = self.data_close[0]
            self.buy_comm = self.broker.getcommissioninfo(self.data).getcommission(self.buy_price, 100)
            self.order = None  # 在这里将订单设置为None，表示没有正在执行的订单
        else:
            self.buy_price = None
            self.buy_comm = None

class SmaCross(StrategyBase):
    # 这是一个简单的均值策略，当10日均线超过30日均线时买入，30日均线超过10日均线卖出。
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )
    def __init__(self):
        super().__init__()
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.order_target_size(target=1)  # enter long
                # self.buy()
        elif self.crossover < 0:  # in the market & cross to the downside
            self.order_target_size(target=0)  # close long position
            # self.close()

import backtrader.indicators as btind
class PairTradingStrategy(StrategyBase):
    # 很简单的策略，就是当zscore大于1的时候我们认为Y的估值相对X已经过高，考虑卖出Y买入X，当小于-1的时候相反。
    params = dict(
        period=10,
        qty1=0,
        qty2=0,
        printout=False,
        upper=1,
        lower=-1,
        up_medium=0.5,
        low_medium=-0.5,
        status=0,
    )
	# 这里说明一下；self.p.upper即可访问params里的参数，这是bt.Strategy里实现的
    # 所以这里params一般都是声明跟策略相关的变量，可以通过self.p的属性进行获取
    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None

    def __init__(self):
        # To control operation entries
        self.orderid = None
        self.qty1 = self.p.qty1
        self.qty2 = self.p.qty2
        self.upper_limit = self.p.upper
        self.lower_limit = self.p.lower
        self.up_medium = self.p.up_medium
        self.low_medium = self.p.low_medium
        self.status = self.p.status

        # Signals performed with PD.OLS :
        self.transform = btind.OLS_TransformationN(self.data0, self.data1,
                                                   period=self.p.period)
        self.zscore = self.transform.zscore

    def next(self):    
        if self.orderid:
            return  # if an order is active, no new orders are allowed

        if self.p.printout:
            print('Self  len:', len(self))
            print('Data0 len:', len(self.data0))
            print('Data1 len:', len(self.data1))
            print('Data0 len == Data1 len:',
                  len(self.data0) == len(self.data1))

            print('Data0 dt:', self.data0.datetime.datetime())
            print('Data1 dt:', self.data1.datetime.datetime())

            print('status is', self.status)
            print('zscore is', self.zscore[0])

        if (self.zscore[0] > self.upper_limit) and (self.status != 1):
            self.status = 1
            self.order_target_percent(self.data1,0) # data1 = y
            self.order_target_percent(self.data0,1) # data0 = x

        elif (self.zscore[0] < self.lower_limit) and (self.status != 2):
            self.order_target_percent(self.data0,0) # data0 = x
            self.order_target_percent(self.data1,1) # data1 = y
            self.status = 2 


    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')


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

if __name__ ==  "__main__":

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
    

class Strategy_MACD(StrategyBase):
    '''#平滑异同移动平均线MACD
        DIF(蓝线): 计算12天平均和26天平均的差，公式：EMA(C,12)-EMA(c,26)
       Signal(DEM或DEA或MACD) (红线): 计算macd9天均值，公式：Signal(DEM或DEA或MACD)：EMA(MACD,9)
        Histogram (柱): 计算macd与signal的差值，公式：Histogram：MACD-Signal

        period_me1=12
        period_me2=26
        period_signal=9
        
        macd = ema(data, me1_period) - ema(data, me2_period)
        signal = ema(macd, signal_period)
        histo = macd - signal
    '''
    
    params = (
        ('printlog', True),
        ('ema_short', 8),
        ('ema_long', 21),
        ('macd_period', 5),
        ('sma_short', 21),
        ('sma_long', 55),
    )
    
    
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s: %s' % (dt.isoformat(), txt))
            with open('log.txt', 'a') as file:
                file.write('%s: %s \n' % (dt.isoformat(), txt))
        
    
    def __init__(self):
        
        # Keep a reference to the 'close' line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # Add MACD indicator
        # self.macdhisto =  bt.talib.MACD(self.datas[0])
        # bt.talib.MACD.macdhist=2*bt.talib.MACD.macdhist
        # self.MACD = bt.talib.MACD
        self.MACD = bt.talib.MACDFIX(self.datas[0], fastperiod=self.params.ema_short, slowperiod=self.params.ema_long, signalperiod=self.params.macd_period)
        self.dif = self.MACD.macd
        self.dea = self.MACD.macdsignal
        self.signal = self.MACD.macdhist

        # self.macdhisto =  bt.indicators.MACDHisto(self.datas[0],self.params.ema_short, self.params.ema_long, self.params.macd_period)
        # 双均线
        self.sma1 = bt.ind.SMA(period=self.params.sma_short)  # 短期均线
        self.sma2 = bt.ind.SMA(period=self.params.sma_long)  # 长期均线
        # self.crossover = bt.ind.CrossOver(sma1, sma2)  # 交叉信号
        self.crossover55 = bt.ind.CrossOver(self.datas[0].high, self.sma2)   # 价格穿过55日线
        self.crossover21 = bt.ind.CrossOver(self.datas[0].low, self.sma1)  # 价格穿过21日线
        self.order = None
        # bt.indicators.BollingerBands(self.datas[0], period=25)

        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                self.log('BUY EXECUTED, Price: %.2f, Lot:%i, Cash: %i, Value: %i' %
                         (order.executed.price,
                          order.executed.size,
                          self.broker.get_cash(),
                          self.broker.get_value()))
            else:  # Sell
                print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
                self.log('SELL EXECUTED, Price: %.2f, Lot:%i, Cash: %i, Value: %i' %
                        (order.executed.price,
                          -order.executed.size,
                          self.broker.get_cash(),
                          self.broker.get_value()))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        #self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    # def notify_trade(self, trade):
    #     if trade.isclosed:
    #         if trade.history[0].event == 'buy':
    #             print('买入时间：{}, 买入价：{:.2f}, 买入数量：{}, 卖出时间：{}, 卖出价：{:.2f}, 盈亏：{:.2f}'.format(
    #                 bt.num2date(
    #                     trade.history[0].dt), trade.history[0].price, trade.history[0].size,
    #                 bt.num2date(trade.history[-1].dt), trade.history[-1].price, trade.history[-1].price - trade.history[0].price))
    #         else:
    #             print('卖出时间：{}, 卖出价：{:.2f}, 卖出数量：{}, 买入时间：{}, 买入价：{:.2f}, 盈亏：{:.2f}'.format(
    #                 bt.num2date(
    #                     trade.history[0].dt), trade.history[0].price, trade.history[0].size,
    #                 bt.num2date(trade.history[-1].dt), trade.history[-1].price, trade.history[0].price - trade.history[-1].price))
        
 
    def next(self):
        
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        #if self.order:
        #    return
           
        # # MACD Buy Signal
        # if self.macdhisto.histo[0] > 0 and self.macdhisto.histo[-1] < 0:
        #     self.log('BUY CREATE, Price: %.2f, Lots: %i, Current Position: %i' % (self.dataclose[0], 
        #                                                                                  100, self.getposition(self.data).size))
        #     self.buy(size = 100)
                   
        # # MACD Sell Singal
        # elif self.macdhisto.histo[0] < 0 and self.macdhisto.histo[-1] > 0:
        #         if self.getposition(self.data).size > 0:
        #             self.log('SELL CREATE (Close), Price: %.2f, Lots: %i' % (self.dataclose[0], 
        #                                                                                     self.getposition(self.data).size))
        #             self.close()
        if not self.position:
            if self.crossover55 > 0 and self.sma1[0] <self.sma2[0] :
                self.buy(size=10000/self.dataclose-200)  # 买入
        elif self.crossover21 < 0:
            self.close()  # 卖出


                    
        # Keep track of the created order to avoid a 2nd order
        #self.order = self.sell(size = self.getposition(data).size - opt_position)