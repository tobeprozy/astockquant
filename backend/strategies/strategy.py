
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
        
        
class TurtleStrategy(bt.Strategy):
    #默认参数
    params = (
        ('H_period', 20),   # 唐奇安通道上轨周期
        ('L_period', 10),   # 唐奇安通道下轨周期
        ('ATRPeriod', 14),  # 平均真实波幅ATR周期
    )

    #交易记录日志（默认打印结果）
    def log(self, txt, dt=None, doprint=False):
        if doprint:
            dt = dt or self.datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def __init__(self):
        # 初始化
        self.order = None  # 未决订单
        self.buyprice = 0  # 买单执行价格
        self.buycomm = 0  # 订单执行佣金
        self.buy_size = 0  # 买单数量
        self.buy_count = 0  # 买入次数计数

        # 海龟交易法则中的唐奇安通道和平均真实波幅ATR
        self.H_line = bt.indicators.Highest(
            self.data.high(-1), period=self.p.H_period)
        self.L_line = bt.indicators.Lowest(
            self.data.low(-1), period=self.p.L_period)
        self.ATR = bt.indicators.AverageTrueRange(
            self.data, period=self.p.ATRPeriod)

        # 价格与上下轨线的交叉
        self.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.sell_signal = bt.ind.CrossDown(self.data.close(0), self.L_line)

    def next(self):
        if self.order:
            return

        #入场：价格突破上轨线且空仓时
        if self.buy_signal and self.buy_count == 0:
             # 计算买入数量
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR 
            self.buy_size = int(self.buy_size / 100) * 100 

            self.buy_count += 1  # 买入次数计数
            self.log('创建买单')
            self.order = self.buy(size=self.buy_size)

        #加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] \
                and self.buy_count > 0 and self.buy_count <= 4:
             # 计算买入数量
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR 
            self.buy_size = int(self.buy_size / 100) * 100  

            self.log('创建买单')
            self.order = self.buy(size=self.buy_size)
            self.buy_count += 1  # 买入次数计数

        #离场：价格跌破下轨线且持仓时
        elif self.position:
            if self.sell_signal or self.data.close < (
                    self.buyprice - 2 * self.ATR[0]):
                self.log('创建卖单')
                self.order = self.close()  # 清仓
                self.buy_count = 0

    #记录交易执行情况（默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败%s' % order.getstatusname())
        self.order = None

    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(
            f'(组合线：{self.p.H_period},{self.p.L_period})；\
        期末总资金: {self.broker.getvalue():.2f}',
            doprint=True)
        
        
# 定义Observer
class OrderObserver(bt.observer.Observer):
    lines = ('created', 'expired',)
    # 做图参数设置
    plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)
    # 创建工单 * 标识，过期工单 方块 标识
    plotlines = dict(
        created=dict(marker='*', markersize=8.0, color='lime', fillstyle='full'),
        expired=dict(marker='s', markersize=8.0, color='red', fillstyle='full')
    )

    # 处理 Lines
    def next(self):
        for order in self._owner._orderspending:
            if order.data is not self.data:
                continue

            if not order.isbuy():
                continue

            # Only interested in "buy" orders, because the sell orders
            # in the strategy are Market orders and will be immediately
            # executed

            if order.status in [bt.Order.Accepted, bt.Order.Submitted]:
                self.lines.created[0] = order.created.price

            elif order.status in [bt.Order.Expired]:
                self.lines.expired[0] = order.created.price

# 定义策略
class MACD_KDJStrategy(bt.Strategy):
    # 策略参数
    params = (
        ('highperiod', 9),
        ('lowperiod', 9),
        ('kperiod', 3),
        ('dperiod', 3),
        ('me1period', 12),
        ('me2period', 26),
        ('signalperiod', 9),
        ('limitperc', 1.0), # 限价比例 ，下跌1个百分点才买入，目的可以展示Observer的过期单
        ('valid', 7), # 限价周期
        ('print', False),
        ('counter', 0),  # 计数器
    )

    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        if self.params.print:
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # 初始化全局变量，备用
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.volume = self.datas[0].volume

        self.order = None
        self.buyprice = None
        self.buycomm = None

        # N个交易日内最高价
        self.highest = bt.indicators.Highest(self.data.high, period=self.p.highperiod)
        # N个交易日内最低价
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.p.lowperiod)

        # 计算rsv值 RSV=(CLOSE- LOW) / (HIGH-LOW) * 100
        # 如果被除数0 ，为None
        self.rsv = 100 * bt.DivByZero(
            self.data_close - self.lowest, self.highest - self.lowest, zero=None
        )

        # 计算rsv的N个周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=self.p.kperiod, plot=False)
        # D值=K值 的N个周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=self.p.dperiod, plot=False)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D

        # MACD策略参数
        me1 = bt.indicators.EMA(self.data, period=self.p.me1period, plot=True)
        me2 = bt.indicators.EMA(self.data, period=self.p.me2period, plot=True)

        self.macd = me1 - me2
        self.signal = bt.indicators.EMA(self.macd, period=self.p.signalperiod)
        bt.indicators.MACDHisto(self.data)

    # 订单通知处理
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.dataclose[0]
            else:
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    # 交易通知处理
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    # 策略执行
    def next(self):
        self.log("Close, %.2f" % self.dataclose[0])
        if self.order:
            return

        # 空仓中，开仓买入
        if not self.position:
            # 买入基于MACD策略
            condition1 = self.macd[-1] - self.signal[-1] # 昨天低于signal
            condition2 = self.macd[0] - self.signal[0] # 今天高于signal
            # 买入基于KDJ策略 K值大于D值，K线向上突破D线时，为买进信号。下跌趋势中，K值小于D值，K线向下跌破D线时，为卖出信号。
            condition3 = self.K[-1] - self.D[-1] # 昨天J低于D
            condition4 = self.K[0] - self.D[0]   # 今天J高于D

            if condition1 < 0 and condition2 > 0 and condition3 < 0 and condition4 > 0 :
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                plimit = self.data.close[0] * (1.0 - self.p.limitperc / 100.0)
                valid = self.data.datetime.date(0) + datetime.timedelta(days=self.p.valid)
                self.log('BUY CREATE, %.2f' % plimit)
                # 限价购买
                self.buy(exectype=bt.Order.Limit, price=plimit, valid=valid)


        else:
            # 卖出基于MACD策略
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]
            # 卖出基于KDJ策略
            condition3 = self.K[-1] - self.D[-1]
            condition4 = self.D[0] - self.D[0]

            if condition1 > 0 and condition2 < 0 and (condition3 > 0 or condition4 < 0):
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.order = self.sell()

    def start(self):
        # 从0 开始
        # self.params.counter += 1
        self.log('Strategy start %s' % self.params.counter)

    def nextstart(self):
        self.params.counter += 1
        self.log('Strategy nextstart %s' % self.params.counter)

    def prenext(self):
        self.params.counter += 1
        self.log('Strategy prenext  %s' % self.params.counter)

    def stop(self):
        self.params.counter += 1
        self.log('Strategy stop  %s' % self.params.counter)
        self.log('Ending Value %.2f' % ( self.broker.getvalue()))

    # 例子，没地方放，先当着
    # if __name__ == "__main__":
    #     tframes = dict(
    #         days=bt.TimeFrame.Days,
    #         weeks=bt.TimeFrame.Weeks,
    #         months=bt.TimeFrame.Months,
    #         years=bt.TimeFrame.Years)

    #     #1.实例初始化
    #     cerebro = bt.Cerebro()

    #     # 2.加载数据 Data feeds
    #     # 加载数据到模型中，由dataframe 到 Lines 数据类型，查询10年数据到dataframe
    #     stock_df = common.get_data('000858.SZ','2010-01-01','2021-01-01')
    #     # 加载5年数据进行分析
    #     start_date = datetime.datetime(2016, 1, 1)  # 回测开始时间
    #     end_date = datetime.datetime(2020, 12, 31)  # 回测结束时间
    #     # bt数据转换
    #     data = bt.feeds.PandasData(dataname=stock_df, fromdate=start_date, todate=end_date)
    #     # bt加载数据
    #     cerebro.adddata(data)

    #     #3.加载策略 Strategy
    #     cerebro.addstrategy(MACD_KDJStrategy)

    #     #4.加载分析器 Analyzers
    #     cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    #     cerebro.addanalyzer(bt.analyzers.DrawDown,_name = 'mydrawdown')
    #     cerebro.addanalyzer(bt.analyzers.AnnualReturn,_name = 'myannualreturn')

    #     #5.加载观察者 Observers
    #     cerebro.addobserver(OrderObserver)

    #     #6.设置仓位管理 Sizers
    #     cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    #     #7.设置佣金管理 Commission
    #     cerebro.broker.setcommission(commission=0.002)

    #     #8.设置初始资金
    #     cerebro.broker.setcash(100000)
    #     print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    #     #9.启动回测
    #     checkstrats = cerebro.run()
    #     #数据源0 返回值处理
    #     checkstrat = checkstrats[0]

    #     #10.回测结果
    #     print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    #     print('夏普率:')
    #     for k, v in checkstrat.analyzers.mysharpe.get_analysis().items():
    #         print(k, ':', v)

    #     print('最大回测:')
    #     for k, v in checkstrat.analyzers.mydrawdown.get_analysis()['max'].items():
    #         print('max ', k, ':', v)

    #     print('年化收益率:')
    #     for year, ann_ret in checkstrat.analyzers.myannualreturn.get_analysis().items():
    #         print(year, ':', ann_ret)

    #     #11.回测图示
    #     cerebro.plot()


class Strategy_MCACD2(bt.Strategy):
    #记录函数
    def log(self,txt,dt=None):
        dt=dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    #初始化数据,私有类
    def __init__(self):
        self.dataclose=self.datas[0].close
        self.dataopen=self.datas[0].open
        self.datalow=self.datas[0].low
        self.datahigh=self.datas[0].high
        self.ma5=bt.indicators.MovingAverageSimple(self.dataclose,period=5)
        self.ma10=bt.indicators.MovingAverageSimple(self.dataclose,period=10)
        self.ma20=bt.indicators.MovingAverageSimple(self.dataclose,period=20)
        self.MACD=bt.indicators.MACD(self.datas[0])
        self.macd=self.MACD.macd
        self.signal=self.MACD.signal
        self.rsi=bt.indicators.RSI(self.datas[0])
        self.boll=bt.indicators.BollingerBands(self.datas[0])
        self.atr=bt.indicators.ATR(self.datas[0])
        self.order=None
        self.buyprice=None
        self.comm=None
        self.buy_size=10000
    #交易状态检测
    def notify_order(self,order):
        if order.status in [order.Submitted,order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买进的价格 %.2f,账户值；%.2f,交易费用：%.2f' % (order.executed.price,order.executed.value,order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            if order.issell():
                self.log('卖出的价格 %.2f,账户值；%.2f,交易费用：%.2f' % (order.executed.price,order.executed.value,order.executed.comm))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易取消,资金不足，交易拒接')
    #交易完统计
    def notify_trade(self,trade):
        if not trade.isclosed:
            return
        self.log('利润：%.2f,总利润: %.2f' %(trade.pnl,trade.pnlcomm))
    #交易函数
    def next(self):
        #低位金叉买入
        if self.macd[-1]<self.signal[-1]:
            if self.macd[0]>self.signal[0]:
                if self.macd[0]<0:
                    self.buy(size=self.buy_size)
                    self.log('MACD低位金叉买入价格:%.2f' % self.dataclose[0])
                    return 
        #正常金叉买价
        if self.macd[-1]<self.signal[-1]:
            if self.macd[0]>self.signal[0]:
                if self.macd[0]==0:
                    self.buy(size=self.buy_size)
                    self.log('MACD正常金叉买入价格:%.2f' % self.dataclose[0])
                    return 
        # #高位金叉买价，高位金叉有加速上升的作用
        # if self.macd[-1]<self.signal[-1]:
        #     if self.macd[0]>self.signal[0]:
        #         if self.macd[0]>0:
        #             self.buy(size=self.buy_size)
        #             self.log('MACD高位金叉买入价格:%.2f' % self.dataclose[0])
        #             return 
        # #高位死叉卖出
        # if self .macd[-1]>self.signal[-1]:
        #     if self.macd[0]<self.signal[-1]:
        #         if self.macd[0]>=0:
        #             self.sell(size=self.buy_size*0.4)
        #             self.log('MACD高位死叉卖出价格:%.2f' % self.dataclose[0])
        #             return
        #低位死叉卖出，和死叉减创
        if self.macd[-1]<self.signal[-1]:
            if self.macd[0]>self.signal[0]:
                if self.macd[0]<0:
                    self.buy(size=self.buy_size)
                    self.log('MACD低位金叉卖出价格:%.2f' % self.dataclose[0])
                    return
        # #低位死叉，加速下降卖出
        # if self .macd[-1]>self.signal[-1]:
        #     if self.macd[0]<self.signal[-1]:
        #         if self.macd[0]<0:
        #             self.sell(size=self.buy_size*0.4)
        #             self.log('MACD低位死叉卖出价格:%.2f' % self.dataclose[0])
        #             return
        # #macd下降趋势卖出
        # if (self.macd[-1]-self.signal[-1])>(self.macd[0]-self.signal[0]):
        #     if self.signal[0]>self.macd[0]:
        #         self.buy(size=self.buy_size*0.2)
        #         self.log('MACD下降趋势卖出价格:%.2f' % self.dataclose[0])
        #         return
        # #macd上涨趋势买入
        # if (self.macd[-1]-self.signal[-1])<(self.macd[0]-self.signal[0]):
        #     if self.signal[0]<self.macd[0]:
        #         self.buy(size=self.buy_size*0.2)
        #         self.log('MACD上升趋势买入价格:%.2f' % self.dataclose[0])
        #         return
        # #光头光脚大阳线买入
        # if self.dataopen[0]==self.datalow[0] and self.dataclose[0]==self.datahigh[0] and self.dataclose[0]>self.dataopen[0]:
        #     self.buy(size=self.buy_size)
        #     self.log('光头光脚阳线买入，价格 %.2f' % self.dataclose[0])
        #     return
        # #光头光脚大阴线卖出
        # if self.dataopen[0]==self.datahigh[0] and self.dataclose[0]==self.datalow[0] and self.dataopen[0]>self.dataclose[0]:
        #     self.sell(size=self.buy_size)
        #     self.log('光头光脚大阴线卖出，价格 %.2f' % self.dataclose[0])
        #     return 
