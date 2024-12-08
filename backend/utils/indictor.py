import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Grid
from pyecharts.commons.utils import JsCode
import numpy as np
import pandas as pd

class StockTAIndicatorsCalculator:
    def __init__(self, df):
        """
        初始化StockTAIndicatorsCalculator类。
        
        参数:
        df -- 包含股票数据的pandas.DataFrame对象，必须包含'High', 'Low', 'Close', 'Volume'列。
        """
        self.df = df.copy()
        self.calculate_all_indicators()

    def calculate_all_indicators(self):
        """
        计算所有技术指标。
        """
        self.calculate_ma(5)
        self.calculate_ema(5)
        self.calculate_rsi(14)
        self.calculate_bbands(5, 2, 2)
        self.calculate_macd(12, 26, 9)

    def calculate_ma(self, timeperiod=5):
        """
        计算移动平均线（MA）。
        
        参数:
        timeperiod -- MA的周期，默认为5。
        """
        self.df['MA{}'.format(timeperiod)] = talib.MA(self.df['Close'], timeperiod=timeperiod)

    def calculate_ema(self, timeperiod=5):
        """
        计算指数移动平均线（EMA）。
        
        参数:
        timeperiod -- EMA的周期，默认为5。
        """
        self.df['EMA{}'.format(timeperiod)] = talib.EMA(self.df['Close'], timeperiod=timeperiod)

    def calculate_rsi(self, timeperiod=14):
        """
        计算相对强弱指数（RSI）。
        
        参数:
        timeperiod -- RSI的周期，默认为14。
        """
        self.df['RSI'] = talib.RSI(self.df['Close'], timeperiod=timeperiod)

    def calculate_bbands(self, timeperiod=5, nbdevup=2, nbdevdn=2):
        """
        计算布林带（Bollinger Bands）。
        
        参数:
        timeperiod -- 布林带的周期，默认为5。
        nbdevup -- 上轨偏差，默认为2。
        nbdevdn -- 下轨偏差，默认为2。
        """
        self.df['UPPER_BAND'], self.df['BB_MIDDLE'], self.df['UPPER_BAND'] = talib.BBANDS(self.df['Close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)

    def calculate_macd(self, fastperiod=12, slowperiod=26, signalperiod=9):
        """
        计算MACD。
        
        参数:
        fastperiod -- MACD的快速EMA周期，默认为12。
        slowperiod -- MACD的慢速EMA周期，默认为26。
        signalperiod -- MACD信号线的周期，默认为9。
        """
        macd, macd_signal, macd_hist = talib.MACD(self.df['Close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        self.df['MACD'] = macd
        self.df['MACD_SIGNAL'] = macd_signal
        self.df['MACD_HIST'] = macd_hist

    def get_data(self):
        """
        返回计算结果的DataFrame。
        """
        return self.df


class StockIndicatorsCalculator:
    def __init__(self, data):
        """
        初始化StockIndicatorsCalculator类。
        
        参数:
        data -- 包含股票数据的pandas.DataFrame对象，必须包含'Open', 'High', 'Low', 'Close', 'Volume'列。
        """
        self.data = data.copy()

    def calculate_ma(self, timeperiod=5):
        """计算移动平均线（MA）。"""
        self.data['MA{}'.format(timeperiod)] = self.data['Close'].rolling(window=timeperiod).mean()

    def calculate_ema(self, timeperiod=5):
        """计算指数移动平均线（EMA）。"""
        self.data['EMA{}'.format(timeperiod)] = self.data['Close'].ewm(span=timeperiod, adjust=False).mean()

    def calculate_rsi(self, timeperiod=14):
        """计算相对强弱指数（RSI）。"""
        delta = self.data['Close'].diff(1)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        rsi = 100 - (100 / (1 + up.rolling(window=timeperiod).mean() / down.rolling(window=timeperiod).mean()))
        self.data['RSI'] = rsi

    def calculate_bbands(self, timeperiod=5, nbdevup=2, nbdevdn=2, median_period=20):
        """计算布林带（Bollinger Bands）。"""
        self.data['MA{}'.format(median_period)] = self.data['Close'].rolling(window=median_period).mean()
        self.data['STDDEV{}'.format(timeperiod)] = self.data['Close'].rolling(window=timeperiod).std()
        self.data['UPPER_BAND'] = self.data['MA{}'.format(median_period)] + (self.data['STDDEV{}'.format(timeperiod)] * nbdevup)
        self.data['LOWER_BAND'] = self.data['MA{}'.format(median_period)] - (self.data['STDDEV{}'.format(timeperiod)] * nbdevdn)
        self.data['MIDDLE_BAND'] = self.data['MA{}'.format(median_period)]

    def calculate_macd(self, fastperiod=12, slowperiod=26, signalperiod=9):
        """计算MACD。"""
        self.data['EMA{}'.format(fastperiod)] = self.data['Close'].ewm(span=fastperiod, adjust=False).mean()
        self.data['EMA{}'.format(slowperiod)] = self.data['Close'].ewm(span=slowperiod, adjust=False).mean()
        self.data['MACD'] = self.data['EMA{}'.format(fastperiod)] - self.data['EMA{}'.format(slowperiod)]
        self.data['Signal_Line'] = self.data['MACD'].ewm(span=signalperiod, adjust=False).mean()
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['Signal_Line']


class StockIndicatorsVisualizer:
    def __init__(self, data):
        """
        初始化StockIndicatorsVisualizer类。
        
        参数:
        data -- 包含股票数据的pandas.DataFrame对象，必须包含'Open', 'High', 'Low', 'Close', 'Volume'列。
        """
        self.data = data.copy()
        # 确保将日期列转换为日期时间格式
        self.data['Date'] = pd.to_datetime(self.data['Date'])

    def plot_kline(self):
        """绘制K线图。"""
        kline = (
            Kline()
            .add_xaxis(self.data['Date'].dt.strftime('%Y-%m-%d').tolist())
            .add_yaxis("Kline", [
                [row['Open'], row['Close'], row['Low'], row['High']]
                for _, row in self.data.iterrows()
            ])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Kline Chart"),

                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(is_scale=True),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                tooltip_opts=opts.TooltipOpts(trigger="axis")
            )
        )
        return kline

    def plot_ma(self):
        """绘制移动平均线和EMA。"""
        line = (
            Line()
            .add_xaxis(self.data['Date'].dt.strftime('%Y-%m-%d').tolist())
            .add_yaxis("MA5", self.data['MA5'].tolist())
            .add_yaxis("EMA5", self.data['EMA5'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="MA and EMA"),
                yaxis_opts=opts.AxisOpts(is_scale=True,is_show=False),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                tooltip_opts=opts.TooltipOpts(trigger="axis")
            )
        )
        return line

    def plot_rsi(self):
        """绘制RSI。"""
        rsi_line = (
            Line()
            .add_xaxis(self.data['Date'].dt.strftime('%Y-%m-%d').tolist())
            .add_yaxis("RSI", self.data['RSI'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="RSI"),
                yaxis_opts=opts.AxisOpts(is_scale=True, min_=0, max_=100),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                tooltip_opts=opts.TooltipOpts(trigger="axis")
            )
        )
        return rsi_line

    def plot_macd(self):
        """绘制MACD。"""
        macd_line = (
            Line()
            .add_xaxis(self.data['Date'].dt.strftime('%Y-%m-%d').tolist())
            .add_yaxis("MACD", self.data['MACD'].tolist())
            .add_yaxis("Signal Line", self.data['Signal_Line'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="MACD"),
                yaxis_opts=opts.AxisOpts(is_scale=True),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                tooltip_opts=opts.TooltipOpts(trigger="axis")
            )
        )
        return macd_line

    def plot_bbands(self):
        """绘制布林带。"""
        bbands_line = (
            Line()
            .add_xaxis(self.data['Date'].dt.strftime('%Y-%m-%d').tolist())
            .add_yaxis("Upper Band", self.data['UPPER_BAND'].tolist())
            .add_yaxis("Middle Band", self.data['MIDDLE_BAND'].tolist())
            .add_yaxis("Lower Band", self.data['LOWER_BAND'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Bollinger Bands"),
                yaxis_opts=opts.AxisOpts(is_scale=True),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                tooltip_opts=opts.TooltipOpts(trigger="axis")
            )
        )
        return bbands_line

    def plot_all(self):
        """绘制所有指标图表。"""
        kline = self.plot_kline()
        ma = self.plot_ma()
        rsi = self.plot_rsi()
        macd = self.plot_macd()
        bbands = self.plot_bbands()

        # 创建网格布局
        grid = (
            Grid()
            .add(kline, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", height="40%"))
            .add(ma, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="45%", height="10%"))
            .add(rsi, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="55%", height="10%"))
            .add(macd, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="65%", height="10%"))
            .add(bbands, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="75%", height="10%"))
        )

        # 渲染图表
        grid.render("Stock_Indicators_Visualization.html")

import matplotlib.pyplot as plt
import os
import sys
import json
# 获取当前文件的目录
cur_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root = os.path.abspath(os.path.join(cur_dir, '..'))
# 将项目根目录添加到 sys.path
if root not in sys.path:
    sys.path.append(root)


from get_data.ak_data_fetch import FinancialDataFetcher

# 定义一个字典，将中文列标题映射到英文列标题
columns_mapping = {
    '日期': 'Date',
    '开盘': 'Open',
    '收盘': 'Close',
    '最高': 'High',
    '最低': 'Low',
    '成交量': 'Volume',
    '成交额': 'Turnover',
    '振幅': 'Amplitude',
    '涨跌幅': 'ChangePercent',
    '涨跌额': 'ChangeAmount',
    '换手率': 'TurnoverRate'
}



if __name__ == "__main__":

    fetcher = FinancialDataFetcher()
    df=fetcher.fetch_fund_info(symbol="600733")

    df.rename(columns=columns_mapping, inplace=True)
    # 假设df是包含股票数据的DataFrame
    calculator = StockIndicatorsCalculator(df)
    calculator.calculate_ma(5)
    calculator.calculate_ema(5)
    calculator.calculate_rsi(14)
    calculator.calculate_bbands(5)
    calculator.calculate_macd(12, 26, 9)

    plotter = StockIndicatorsVisualizer(calculator.data)
    plotter.plot_all()
