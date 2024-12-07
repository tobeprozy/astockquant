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



import tushare as ts


def get_data_ts(token, stock_code, s_date, e_date):
    # 设置token
    ts.set_token(token)
    
    # 获取数据
    df = ts.get_k_data(code=stock_code, autype="qfq", start=s_date.strftime('%Y%m%d'), end=e_date.strftime('%Y%m%d'))
    
    # 调整列名以匹配pro.daily()的输出
    df.rename(columns={'date': 'trade_date', 'volume': 'vol'}, inplace=True)
    
    # 将trade_date列转换为datetime类型，并设置为索引
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    
    # 将数据类型转换为float，以匹配pro.daily()的输出
    df = df.astype('float')
    
    # 添加openinterest列，因为期货数据中会使用到，但在这里我们设为0
    df['openinterest'] = 0
    
    # 反转DataFrame，因为Backtrader期望数据是最新的在前
    df = df.iloc[::-1]
    
    # 由于trade_date已经是索引，不需要再次转换和删除
    # df.index = pd.to_datetime(df.trade_date)  # 这行代码是多余的，应该删除
    # df.drop('trade_date', axis=1, inplace=True)  # 这行代码也是多余的，应该删除
    
    # 列名调整已经在前面完成，这里不需要重复
    # df = df.astype('float')  # 重复的转换，可以删除
    # df.rename(columns={'vol': 'volume'}, inplace=True)  # 重复的重命名，可以删除
    # df['openinterest'] = 0  # 重复的添加，可以删除
    
    return df


s_date = datetime.datetime.now() - datetime.timedelta(days = 1165)
e_date = datetime.datetime.now()

# Create stock Data Feed
stock_index = '600633'
df = get_data_ts('你的token',stock_index, s_date, e_date)
data = bt.feeds.PandasData(dataname=df,fromdate=s_date,todate=e_date)




class TestStrategy(bt.Strategy):
    params = (('p1', 12), ('p2', 26), ('p3', 9))

    def __init__(self):
        self.order = None
        # 获取MACD柱
        self.macdhist = bt.ind.MACDHisto(self.data,
                                         period_me1=self.p.p1,
                                         period_me2=self.p.p2,
                                         period_signal=self.p.p3)

    def next(self):
        pos = self.getposition(data).size
    
        if not self.position:
            # 得到当前的账户价值
            total_value = self.broker.getcash()
            # 1手=100股，满仓买入
            size = int((total_value / 100) / self.datas[0].close[0]) * 100
            # 当MACD柱大于0（红柱）且无持仓时满仓买入
            if self.macdhist > 0:
                print('买入，macdhist->' + ',持仓数量->' + str(pos) + ',买入数量->' + str(size))
                self.order = self.buy(size=size)
        else:
            # 当MACD柱小于0（绿柱）且持仓时全部清仓
            if self.macdhist < 0:
                print('卖出，macdhist->' + ',持仓数量->' + str(pos))
                self.close()

    def log(self, txt, dt=None, doprint=False):
        if True or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price:.2f},\
                成本:{order.executed.value:.2f},\
                数量:{order.executed.size:.2f},\
                手续费:{order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price:.2f},\
                成本: {order.executed.value:.2f},\
                数量:{order.executed.size:.2f},\
                手续费{order.executed.comm:.2f}')
            self.bar_executed = len(self)
            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')




# 实例化大脑
cerebro = bt.Cerebro()
# 加入策略
cerebro.addstrategy(TestStrategy)
# cerebro.add_signal(bt.SIGNAL_LONG, MACDSignal)

cerebro.adddata(data=data)

startcash = 100000
cerebro.broker.setcash(startcash)
# 设置交易手续费为 0.1%
cerebro.broker.setcommission(commission=0.001)
print('组合期初资金: %.2f' % cerebro.broker.getvalue())
cerebro.run()
#获取回测结束后的总资金
print('组合期末资金: %.2f' % cerebro.broker.getvalue())

cerebro.plot()


# 画图并保存
fig = cerebro.plot()
fig.savefig('backtest_result.png', dpi=300, bbox_inches='tight')

print("回测结果图已保存为 'backtest_result.png'")
