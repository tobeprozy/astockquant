import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Grid


import pyecharts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import *


class StockIndicatorsVisualizer2:
    global returnList

    def __init__(self, df):
        self.df=df
        
    def get_Pyecharts_MA(self,n,index,itheme="light"):
            df = self.df
            colorlist = ["rgb(47,79,79)","rgb(255,140,0)","rgb(0,191,255)","rgb(187, 102, 255)"]
            icolor = colorlist[index-2]
            line = (
                Line(init_opts=opts.InitOpts(theme=itheme,animation_opts=opts.AnimationOpts(animation=False),))
                    # 添加x轴交易日期数据
                    .add_xaxis(df["date"].tolist())
                    .add_yaxis("MA{}".format(n),df["MA{}".format(n)].tolist(),xaxis_index=index,yaxis_index=index,
                            label_opts=opts.LabelOpts(is_show=False),
                            is_symbol_show=False, # 是否显示小圆点
                            itemstyle_opts=opts.ItemStyleOpts(color=icolor)) # 更改颜色
                    .set_global_opts(
                        xaxis_opts=opts.AxisOpts(is_show=False,grid_index=index),
                        yaxis_opts=opts.AxisOpts(is_show=False,grid_index=index),
                        legend_opts=opts.LegendOpts(is_show=True),  # 图例是否显示
                    )
                )
            return line
 
    # 绘制成交量均值线
    def get_Pyecharts_VolMA(self,n,index,itheme="light"):
        df = self.df
        colorlist = ["rgb(47,79,79)","rgb(255,140,0)"]
        icolor = colorlist[index-6]
        line = (
            Line(init_opts=opts.InitOpts(theme=itheme,animation_opts=opts.AnimationOpts(animation=False),))
                # 添加x轴交易日期数据
                .add_xaxis(df["date"].tolist())
                .add_yaxis("VolMA{}".format(n),df["VolMA{}".format(n)].tolist(),xaxis_index=index,yaxis_index=index,
                           label_opts=opts.LabelOpts(is_show=False),
                           is_symbol_show=False, # 是否显示小圆点
                           tooltip_opts=opts.TooltipOpts(is_show=False),
                           itemstyle_opts=opts.ItemStyleOpts(color=icolor)) # 更改颜色
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(is_show=False,grid_index=index),
                    yaxis_opts=opts.AxisOpts(is_show=False,grid_index=index),
                      # 图例是否显示
                )
            )
 
        return line
 
    # 绘制K线图,
    def get_Pyecharts_Kline(self,itheme="light"):
        tradeAction = [] # 交易输出记录
        df = self.df
        valueList = []
 
        for i in range(len(df)):
            valueList.append([df.loc[i, "open"], df.loc[i, "close"], df.loc[i, "high"], df.loc[i, "low"],(df.loc[i,"close"]-df.loc[i,"open"])/df.loc[i,"open"]  ])
        x = df["date"].tolist()
        y = valueList
        # 绘制K线图
        kline = (
            Kline(init_opts=opts.InitOpts(theme=itheme,animation_opts=opts.AnimationOpts(animation=True,animation_easing_update="backOut")))  # chalk
 
                # 添加x轴交易日期数据
                .add_xaxis(x)
                # 添加y轴成交价格数据
                .add_yaxis(series_name="Daily Trade Data", y_axis=y, itemstyle_opts=opts.ItemStyleOpts(  # 风格设置
                    color="red",color0="green",
                    border_color="#ef232a",border_color0="#14b143", # 边框色彩
                    ),
                )
 
                # 设置x、y轴显示信息
                .set_global_opts(xaxis_opts=opts.AxisOpts(name='交易时间'))
                # .set_global_opts(yaxis_opts=opts.AxisOpts(name='交易价格/元'))
                # 固定y轴的范围
                # .set_global_opts(yaxis_opts=opts.AxisOpts(min_=5, max_=10))
 
                .set_global_opts(title_opts=opts.TitleOpts(title="XXXX 标题"),  # 标题选项
 
                                 legend_opts=opts.LegendOpts(is_show=True),  # 图例选项
 
                                 datazoom_opts=[  # 缩放选项
                                     opts.DataZoomOpts(
                                         is_show=False,
                                         type_="inside",
                                         xaxis_index=[0,1],
                                         # 初始的框选范围
                                         range_start=80,
                                         range_end=100,
                                     ),
                                     opts.DataZoomOpts(
                                         is_show=True,
                                         xaxis_index=[0,1],
                                         type_="slider",
                                         pos_top="95%",
                                         range_start=80,
                                         range_end=100,
                                     )
                                 ],
 
                                 yaxis_opts=opts.AxisOpts(  # 坐标轴配置项
                                     is_scale=True,  # 是否显示y轴
                                     splitarea_opts=opts.SplitAreaOpts(  # 分割区域配置项
                                         is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
                                 ),
 
                                 # 控制x轴label
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter=JsCode(
                                     """
                                     function (x) {
                                     a = x.substring(0,4);
                                     b = x.substring(4,6);
                                     c = x.substring(6,8);
                                     return a+'年'+b+'月'+c+'日'; 
                                     }
                                     """)
                                )),
 
 
 
                                 tooltip_opts=opts.TooltipOpts(  # 提示框配置项
                                     trigger="axis",  # 触发类型默认
                                     axis_pointer_type="cross",  # 鼠标指针指示器
                                     background_color="rgba(245, 245, 245, 0.8)",  # 提示框漂浮层背景色
                                     border_width=1,  # 提示框漂浮层边框
                                     border_color="#ccc",
                                     textstyle_opts=opts.TextStyleOpts(color="#000"),  # 提示框文字选项
                                     formatter=JsCode(
                                         """
                                         function (x) {
                                         date = x[0].axisValue.substring(0,4)+ '年' + x[0].axisValue.substring(4,6)+ '月' +x[0].axisValue.substring(6,8)+ '日';
                                         open = x[0].data[1];
                                         close = x[0].data[2];
 
                                         
                                         return date + '<br>' + '开盘价：' + open + '<br>' +'收盘价：' + close + '<br>' +'涨跌幅：' + Math.round((close-open)/close*100*100)/100 + '%<br>'+ x[1].seriesName +'&nbsp;&nbsp;：'+ x[1].data[1] + '<br>' + x[2].seriesName +'：'+ x[2].data[1] + '<br>'+ x[3].seriesName +'：'+ x[3].data[1] + '<br>'+ x[4].seriesName +'：'+ x[4].data[1] + '<br>'; 
                                         }
                                         """)
                                 ),
 
                                 axispointer_opts=opts.AxisPointerOpts(  # 坐标轴指示器配置项
                                     is_show=True,
                                     label=opts.LabelOpts(background_color="#777"),
                                 ),
 
                                 brush_opts=opts.BrushOpts(  # 区域选择组建配置项
                                     x_axis_index="all",  # 指定哪些 xAxisIndex 可以被刷选
                                     brush_link="all",  # 不同系列间，选中的项可以联动。
                                     out_of_brush={"colorAlpha": 0.1},
                                     brush_type="lineX",
                                 ),
                                )
        )
        return kline
 
    # 绘制成交量图形
    def get_Pyecharts_Bar(self,itheme="light"):
        df = self.df
        valueList = []
        # 构建日交易金额数据list
        for i in range(len(df)):
            valueList.append([df.loc[i, "open"], df.loc[i, "close"], df.loc[i, "high"], df.loc[i, "low"]])
        # 绘制成交量柱状图
        bar = (
            Bar()
                .add_xaxis(xaxis_data=df["date"].tolist())
                .add_yaxis(series_name="Volume",y_axis=df["vol"].tolist(),label_opts=opts.LabelOpts(is_show=False),
                    # 设置多图联动
                    xaxis_index=1,
                    yaxis_index=1,
                    tooltip_opts=opts.TooltipOpts(is_show=False),)
 
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(
 
                        # 控制x轴label
                        axislabel_opts=opts.LabelOpts(formatter=JsCode(
                            """
                            function (x) {
                            a = x.substring(0,4);
                            b = x.substring(4,6);
                            c = x.substring(6,8);
                            return a+'年'+b+'月'+c+'日'; 
                            }
                            """)
                        ),
                        type_="category",
                        is_scale=True,
                        grid_index=1,
                        axisline_opts=opts.AxisLineOpts(is_on_zero=True),
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=False),
                        split_number=20,
                        min_="dataMin",
                        max_="dataMax",),
 
                    yaxis_opts=opts.AxisOpts(
                        grid_index=1,
                        is_scale=True,
                        split_number=2,
                        axislabel_opts=opts.LabelOpts(is_show=True),
                        axisline_opts=opts.AxisLineOpts(is_show=True),
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=False),),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )
        return bar
 
    # 绘制主图并输出页面
    def Print_Main_index(self,kline,bar_volumn,line_ma=None,line_ma2=None,line_ma3=None,line_ma4 = None,itheme="light"):
        bar = bar_volumn
 
        kline.overlap(line_ma)
        kline.overlap(line_ma2)
        kline.overlap(line_ma3)
        kline.overlap(line_ma4)
 
        grid_chart = Grid(
            init_opts=opts.InitOpts(
                width="1200px", height="580px",
                animation_opts=opts.AnimationOpts(animation=True,animation_easing="linear"),
                theme=itheme, page_title="Pyecharts_Demo",
            )
        )
        # 添加上图
        grid_chart.add(
            kline,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", height="60%"),
        )
        # 添加下图
        grid_chart.add(
            bar,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="75%", height="16%"),
        )

        import os
        # 确保目录存在
        output_dir = "./StockAnalysis/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            

        grid_chart.render(path = "./StockAnalysis/pyecharts-xx.html")
        
    def render_html(self):
        self.line_ma5 = self.get_Pyecharts_MA(5,2) # index由2开始
        self.line_ma10 = self.get_Pyecharts_MA(10,3)
        self.line_ma20 = self.get_Pyecharts_MA(20,4)
        self.line_ma50 = self.get_Pyecharts_MA(150,5)
        self.line_volma5 = self.get_Pyecharts_VolMA(5, 6)
        self.line_volma10 = self.get_Pyecharts_VolMA(10, 7)
        self.kline = self.get_Pyecharts_Kline()
        self.bar_volumn = self.get_Pyecharts_Bar().overlap(self.line_volma5).overlap(self.line_volma10)
        self.Print_Main_index(self.kline, self.bar_volumn, self.line_ma5, self.line_ma10, self.line_ma20, self.line_ma50)



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

    def plot_all(self,name="Stock_Indicators_Visualization.html"):
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

        # # 创建网格布局
        # grid = (
        #     Grid()
        #     .add(kline, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", height="40%"))
        #     .add(ma, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="40%", height="40%"))
        #     .add(rsi, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="80%", height="10%"))
        #     .add(macd, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="90%", height="10%"))
        #     .add(bbands, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="100%", height="10%"))
        # )

        # 渲染图表
        grid.render(name)
    





import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
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


# 定义一个字典，将中文列标题映射到英文列标题
columns_mapping2 = {
    '日期': 'date',
    '开盘': 'open',
    '收盘': 'close',
    '最高': 'high',
    '最低': 'low',
    '成交量': 'vol',
    '成交额': 'Turnover',
    '振幅': 'Amplitude',
    '涨跌幅': 'ChangePercent',
    '涨跌额': 'ChangeAmount',
    '换手率': 'TurnoverRate'
}


from utils.indictor import StockIndicatorsCalculator
from utils.indictor import StockTAIndicatorsCalculator
import datetime

if __name__ == "__main__":

    fetcher = FinancialDataFetcher()
    # 设置日期范围
    s_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')


    df=fetcher.fetch_fund_info(symbol="512200", start_date=s_date, end_date=e_date)

    df.rename(columns=columns_mapping2, inplace=True)
    # 假设df是包含股票数据的DataFrame
    # calculator = StockIndicatorsCalculator(df)
    # calculator.calculate_ma(5)
    # calculator.calculate_ema(5)
    # calculator.calculate_rsi(14)
    # calculator.calculate_bbands(5)
    # calculator.calculate_macd(12, 26, 9)

    # plotter = StockIndicatorsVisualizer(calculator.data)
    # plotter.plot_all("Stock_Indicators_Visualization.html")
    

    calculator = StockTAIndicatorsCalculator(df)
    calculator.cal_cdlupsidegap2crows()
    calculator.cal_cdlseparatinglines()
    # calculator.calculate_all_indicators()

    calculator = StockIndicatorsCalculator(df)
    calculator.get_MA(5)
    calculator.get_MA(10)
    calculator.get_MA(20)
    calculator.get_MA(150)
    calculator.get_Vol_MA(5)
    calculator.get_Vol_MA(10)

    plotter = StockIndicatorsVisualizer2(calculator.data)
    plotter.render_html()