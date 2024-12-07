import akshare as ak
import datetime
import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import backtrader as bt
import backtrader.feeds as btfeed
from backtrader.indicators import EMA
import datetime
import numpy as np 


# 设置字体
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # 替换为你的字体路径
prop = fm.FontProperties(fname=font_path)

# 从akshare获取数据的方法
def get_data_akshare(stock_code, s_date, e_date):
    df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=s_date, end_date=e_date, adjust="qfq")
    return df

# 设置日期范围
s_date = (datetime.datetime.now() - datetime.timedelta(days=100)).strftime('%Y%m%d')
e_date = datetime.datetime.now().strftime('%Y%m%d')

# 获取股票数据
stock_index = '600733'
stock_hfq_df = get_data_akshare(stock_index, s_date, e_date).iloc[:, :7]

# 删除不需要的列
del stock_hfq_df['股票代码']

# 处理字段命名，以符合 Backtrader 的要求
stock_hfq_df.columns = [
    'date',
    'open',
    'close',
    'high',
    'low',
    'volume',
]

# 把 date 作为日期索引，以符合 Backtrader 的要求
stock_hfq_df.index = pd.to_datetime(stock_hfq_df['date'])
stock_hfq_df['openinterest'] = 0  # 添加 openinterest 列

# 定义Backtrader数据源
class PandasData(bt.feeds.PandasData):
    lines = ('open', 'high', 'low', 'close', 'volume', 'openinterest')
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', 'openinterest'),
    )

# 创建 Backtrader 数据源
data = PandasData(dataname=stock_hfq_df, fromdate=pd.to_datetime(s_date), todate=pd.to_datetime(e_date))
class MACDStrategy(bt.Strategy):
    # 参数
    params = (
        ('maperiod', 15),
    )

    def log(self,txt,dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume

        self.order = None
        self.buyprice = None
        self.buycomm = None

        me1 = EMA(self.data, period=12)
        me2 = EMA(self.data, period=26)

        ## DIF = EMA(12) - EMA(26)
        self.macd = me1 - me2

        ## DEA = EMA(DIF,9)
        self.signal = EMA(self.macd,period=9)

        ## HIS = DIF - DEA
        self.macdhis = self.macd - self.signal

        ## MACD Histogram
        bt.indicators.MACDHisto(self.data)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '买入 价格:%.2f, 金额:%.2f, 手续费:%.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm)
                )

                self.buyprice=order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.dataclose[0]
            else:
                self.log(
                    '卖出 价格:%.2f, 金额:%.2f, 手续费:%.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm)                   
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('取消订单/合并订单/拒绝订单')

        self.order = None

    def next(self):
        # 如果还有订单在执行中，就不做新的仓位调整
        if self.order:
            return

        #买入信号：当 DIF 上穿 DEA，可能表示上升趋势的开始。
        #卖出信号：当 DIF 下穿 DEA，可能表示下降趋势的开始。
        if not self.position:
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]

            if self.macdhis[-1] < 0 and self.macdhis[0] > 0:
                condition3 = 1
            elif self.macdhis[-1] > 0 and self.macdhis[0] < 0:
                condition3 = -1
            else:
                condition3 = 0

            if condition1 < 0 and condition2 > 0 and condition3 == 1:
                self.log('买入: %.2f' % self.dataclose[0])
                self.order = self.buy()

        else:
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]
            if self.macdhis[-1] < 0 and self.macdhis[0] > 0:
                condition3 = 1
            elif self.macdhis[-1] > 0 and self.macdhis[0] < 0:
                condition3 = -1
            else:
                condition3 = 0

            if condition1 > 0 and condition2 < 0 and condition3 == -1:
                self.log('卖出: %.2f' % self.dataclose[0])
                self.order = self.sell()

class MACDSignal(bt.Indicator):
    lines = ('signal',)

    params = dict(
        short_period = 9,
        median_period = 12,
        long_period = 26
    )

    def __init__(self):
        #- **买入信号**：当 DIF 上穿 DEA，且 MACD Histogram 由负转正，可能表示上升趋势的开始。
        #- **卖出信号**：当 DIF 下穿 DEA，且 MACD Histogram 由正转负，可能表示下降趋势的开始。

        me1 = EMA(self.data, period=self.p.median_period)
        me2 = EMA(self.data, period=self.p.long_period)

        ## DIF = EMA(12) - EMA(26)
        self.dif = me1 - me2
        ## DEA = EMA(DIF,9)
        self.dea = EMA(self.dif,period=self.p.short_period)
        ## MACD Histogram 
        self.macd_hist = self.dif - self.dea

        # DIF 上穿 DEA，取值为1；反之，DIF 下穿 DEA，取值为-1
        self.signal1 = bt.ind.CrossOver(self.dif,self.dea)

        # MACD Histogram 由负转正 1 或 由正转负 -1
        ## MACD Histogram 由负转正, 取值为1；反之，取值为0
        self.signal2 = bt.And(self.macd_hist(-1) < 0, self.macd_hist > 0)

        ## MACD Histogram 由正转负 -1, 取值为1；反之，取值为0
        self.signal3 = bt.And(self.macd_hist(-1) > 0, self.macd_hist < 0)

        # 买入、卖出信号
        ## 买入信号
        self.buy_signal = bt.If((self.signal1 + self.signal2) == 2, 1, 0)
        ## 卖出信号
        self.sell_signal = bt.If((self.signal1 + self.signal3) == 0, -1, 0)

        ## 将 买入信号 和 卖出信号 进行合并
        self.lines.signal = bt.Sum(self.buy_signal,self.sell_signal)

        ## MACD Histogram
        bt.indicators.MACDHisto(self.macd_hist)

# 实例化大脑
cerebro = bt.Cerebro()
# 加入策略
cerebro.addstrategy(MACDStrategy)
# cerebro.add_signal(bt.SIGNAL_LONG, MACDSignal)

cerebro.adddata(data=data)
## 设置初始金额、手续费等
### 初始资金 1,000,000
cerebro.broker.setcash(1000000.0)

### 佣金各0.0003
cerebro.broker.setcommission(commission=0.0003)

### 每次固定交易100股
cerebro.addsizer(bt.sizers.FixedSize, stake=100)
## 
result = cerebro.run()

print(result)

# 画图并保存
fig = cerebro.plot(style='candlestick')[0][0]
fig.savefig('backtest_result.png', dpi=300, bbox_inches='tight')

print("回测结果图已保存为 'backtest_result.png'")
