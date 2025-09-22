#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于pyecharts的图表实现 - 高级版本

设计说明：
1. 完全分离计算与绘图逻辑，所有指标数据通过参数传入
2. 每个绘图方法专注于绘制单一指标图
3. 通过drawAll方法实现灵活的图表布局组合
4. 支持多种图表类型和图片保存功能
"""

from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Gauge, Scatter
from pyecharts.commons.utils import JsCode
from pyecharts.render import make_snapshot
# 使用selenium来保存图片
from snapshot_selenium import snapshot as driver
import pandas as pd
import numpy as np
import os
import webbrowser
from qplot.core.plotter import Chart
import logging

logger = logging.getLogger(__name__)

class PyechartsChart_2(Chart):
    """基于pyecharts的图表实现 - 高级版本"""
    
    def __init__(self, chart_type, data_manager=None, data=None, **kwargs):
        """
        初始化图表
        
        Args:
            chart_type: 图表类型，'kline'、'line'、'bar'、'minute'等
            data_manager: 数据管理器实例
            data: 直接提供的数据（DataFrame）
            **kwargs: 其他配置参数
        """
        super().__init__(chart_type)
        self.chart = None
        self.is_realtime = kwargs.get('is_realtime', False)
        self.data_manager = data_manager  # 数据管理器
        self.data = data  # 存储直接传入的数据
        self.kwargs = kwargs  # 存储配置参数
        self.df = data  # 保留原始实现中的df变量，用于兼容
    
    def _prepare_data(self):
        """准备绘图数据"""
        # 如果直接提供了数据，优先使用
        if self.data is not None:
            return self.data
        
        # 否则从数据管理器获取数据
        if self.data_manager is not None:
            try:
                data = self.data_manager.get_data()
                self.df = data  # 更新df变量
                return data
            except Exception as e:
                logger.error(f"从数据管理器获取数据失败: {str(e)}")
                raise ValueError("无法从数据管理器获取数据")
        
        raise ValueError("未提供数据或数据管理器")
    
    def plot(self):
        """绘制图表"""
        if self.chart_type == 'gauge':
            # 仪表盘图表不需要数据，使用默认值或kwargs中的值
            value = self.kwargs.get('value', 90)
            title = self.kwargs.get('title', "电池电量仪表图")
            subtitle = self.kwargs.get('subtitle', "示例")
            self._plot_gauge(value, title, subtitle)
        else:
            data = self._prepare_data()
            
            if self.chart_type == 'kline':
                self._plot_kline(data)
            elif self.chart_type == 'minute':
                self._plot_minute(data)
            elif self.chart_type == 'line':
                self._plot_line(data)
            elif self.chart_type == 'bar':
                self._plot_bar(data)
        
        return self
    
    def _validate_data(self, data):
        """验证数据是否有效"""
        if data is None or data.empty:
            return False
        return True
    
    def _preprocess_data(self, data):
        """预处理数据"""
        # 复制数据以避免修改原始数据
        df = data.copy()
        # 确保索引是datetime类型
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except:
                # 如果无法转换为datetime类型，创建一个新的索引
                df.index = pd.RangeIndex(len(df))
        return df
    
    def _plot_kline(self, data):
        """绘制K线图"""
        # 如果data不是标准的OHLCV格式，尝试提取必要的列
        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            # 尝试从不同的列名中提取数据
            rename_map = {
                '开盘': 'open', 'open_price': 'open',
                '最高': 'high', 'high_price': 'high',
                '最低': 'low', 'low_price': 'low',
                '收盘': 'close', 'close_price': 'close'
            }
            data = data.rename(columns=rename_map)
        
        # 使用原始实现中的绘图方法
        self.chart = self.render_html()
        return self
    
    def _plot_line(self, data):
        """绘制折线图"""
        self.chart = self.draw_line(data)
        return self
    
    def _plot_bar(self, data):
        """绘制柱状图"""
        self.chart = self.draw_bar(data)
        return self
    
    def _plot_gauge(self, value=90, title="仪表图", subtitle="示例"):
        """绘制仪表盘图"""
        self.chart = self.draw_gauge(value, title, subtitle)
        return self
    
    def get_Pyecharts_MA(self, n, index, itheme="light"):
        """绘制均线"""
        df = self.df
        colorlist = ["rgb(47,79,79)","rgb(255,140,0)","rgb(0,191,255)","rgb(187, 102, 255)"]
        icolor = colorlist[index-2]
        line = (
            Line(init_opts=opts.InitOpts(theme=itheme,animation_opts=opts.AnimationOpts(animation=False),))
                # 添加x轴交易日期数据
                .add_xaxis(df["date"].tolist())
                .add_yaxis("MA{}".format(n), df["MA{}".format(n)].tolist(), xaxis_index=index, yaxis_index=index,
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
    
    def get_Pyecharts_VolMA(self, n, index, itheme="light"):
        """绘制成交量均值线"""
        df = self.df
        colorlist = ["rgb(47,79,79)","rgb(255,140,0)"]
        icolor = colorlist[index-6]
        line = (
            Line(init_opts=opts.InitOpts(theme=itheme,animation_opts=opts.AnimationOpts(animation=False),))
                # 添加x轴交易日期数据
                .add_xaxis(df["date"].tolist())
                .add_yaxis("VolMA{}".format(n), df["VolMA{}".format(n)].tolist(), xaxis_index=index, yaxis_index=index,
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
    
    def get_Pyecharts_Kline(self, itheme="light"):
        """绘制K线图"""
        tradeAction = [] # 交易输出记录
        df = self.df
        valueList = []
        
        for i in range(len(df)):
            valueList.append([df.loc[i, "open"], df.loc[i, "close"], df.loc[i, "high"], df.loc[i, "low"],(df.loc[i,"close"]-df.loc[i,"open"])/df.loc[i,"open"]  ])
        x = df["date"].tolist()
        y = valueList
        # 绘制K线图
        kline = (
            Kline(init_opts=opts.InitOpts(theme=itheme,animation_opts=opts.AnimationOpts(animation=True,animation_easing_update="backOut")))
                
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
                                     '''
                                     function (x) {
                                     a = x.substring(0,4);
                                     b = x.substring(4,6);
                                     c = x.substring(6,8);
                                     return a+'年'+b+'月'+c+'日'; 
                                     }
                                     ''')
                                )),
        
        
        
                                 tooltip_opts=opts.TooltipOpts(  # 提示框配置项
                                     trigger="axis",  # 触发类型默认
                                     axis_pointer_type="cross",  # 鼠标指针指示器
                                     background_color="rgba(245, 245, 245, 0.8)",  # 提示框漂浮层背景色
                                     border_width=1,  # 提示框漂浮层边框
                                     border_color="#ccc",
                                     textstyle_opts=opts.TextStyleOpts(color="#000"),  # 提示框文字选项
                                     formatter=JsCode(
                                         '''
                                         function (x) {
                                         date = x[0].axisValue.substring(0,4)+ '年' + x[0].axisValue.substring(4,6)+ '月' +x[0].axisValue.substring(6,8)+ '日';
                                         open = x[0].data[1];
                                         close = x[0].data[2];
                                         
                                          
                                         return date + '<br>' + '开盘价：' + open + '<br>' +'收盘价：' + close + '<br>' +'涨跌幅：' + Math.round((close-open)/close*100*100)/100 + '%<br>'+ x[1].seriesName +'&nbsp;&nbsp;：'+ x[1].data[1] + '<br>' + x[2].seriesName +'：'+ x[2].data[1] + '<br>'+ x[3].seriesName +'：'+ x[3].data[1] + '<br>'+ x[4].seriesName +'：'+ x[4].data[1] + '<br>'; 
                                         }
                                         '''
                                     )
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
    
    def get_Pyecharts_Bar(self, itheme="light"):
        """绘制成交量图形"""
        df = self.df
        valueList = []
        # 构建日交易金额数据list
        for i in range(len(df)):
            valueList.append([df.loc[i, "open"], df.loc[i, "close"], df.loc[i, "high"], df.loc[i, "low"]])
        # 绘制成交量柱状图
        bar = (
            Bar()
                .add_xaxis(xaxis_data=df["date"].tolist())
                .add_yaxis(series_name="Volume", y_axis=df["vol"].tolist(), label_opts=opts.LabelOpts(is_show=False),
                    # 设置多图联动
                    xaxis_index=1,
                    yaxis_index=1,
                    tooltip_opts=opts.TooltipOpts(is_show=False),)
        
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(
        
                        # 控制x轴label
                        axislabel_opts=opts.LabelOpts(formatter=JsCode(
                            '''
                            function (x) {
                            a = x.substring(0,4);
                            b = x.substring(4,6);
                            c = x.substring(6,8);
                            return a+'年'+b+'月'+c+'日'; 
                            }
                            '''
                        )),
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
    
    def mark_high_open(self, kline, df=None):
        """高开标记函数"""
        if df is None:
            df = self.df
        high_open_points = []  # 存储高开的标记点
        for i in range(1, len(df)):  # 从1开始，因为第一天没有前一天的收盘价
            if df.loc[i, "open"] > df.loc[i-1, "close"]:  # 开盘价高于前一天的收盘价，标记为高开
                high_open_points.append({
                    "coord": [df.loc[i, "date"], df.loc[i, "open"]],
                    "name": "高开"
                })
        kline.set_series_opts(
            markpoint_opts=opts.MarkPointOpts(
                data=high_open_points
            )
        )
    
    def Print_Main_index(self, kline, bar_volumn, line_ma=None, line_ma2=None, line_ma3=None, line_ma4=None, itheme="light", name=None):
        """绘制主图并输出页面"""
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
            

        # 调用高开标记函数
        self.mark_high_open(kline, self.df)
    
        grid_chart.render(path = name)
        return grid_chart
    
    def render_html(self, name="StockAnalysis/pyecharts-xx.html"):
        """渲染HTML"""
        self.line_ma5 = self.get_Pyecharts_MA(5, 2) # index由2开始
        self.line_ma10 = self.get_Pyecharts_MA(10, 3)
        self.line_ma20 = self.get_Pyecharts_MA(20, 4)
        self.line_ma50 = self.get_Pyecharts_MA(150, 5)
        self.line_volma5 = self.get_Pyecharts_VolMA(5, 6)
        self.line_volma10 = self.get_Pyecharts_VolMA(10, 7)
        self.kline = self.get_Pyecharts_Kline()
        self.bar_volumn = self.get_Pyecharts_Bar().overlap(self.line_volma5).overlap(self.line_volma10)
        return self.Print_Main_index(self.kline, self.bar_volumn, self.line_ma5, self.line_ma10, self.line_ma20, self.line_ma50, name=name)
    
    def plot_kline_1(self):
        """绘制K线图（简化版本）"""
        kline = (
            Kline()
            .add_xaxis(self.df["date"].tolist())
            .add_yaxis(
                series_name="Kline", 
                y_axis=[
                    [row['open'], row['close'], row['low'], row['high']]
                    for _, row in self.df.iterrows()
                    ],
                itemstyle_opts=opts.ItemStyleOpts(
                    color="#ef232a",
                    color0="#14b143",
                    border_color="#ef232a",
                    border_color0="#14b143",
                ),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="K线图"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                legend_opts=opts.LegendOpts(is_show=True),
                datazoom_opts=[
                    opts.DataZoomOpts(type_="inside"),
                    opts.DataZoomOpts(type_="slider"),
                ],
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                ),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, 
                        areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
            )
        )
        return kline
    
    def plot_ma5(self):
        """绘制MA5线"""
        # 检查数据是否有MA5列
        if "MA5" not in self.df.columns:
            logger.warning("数据中没有MA5列，使用收盘价代替")
            # 计算MA5
            self.df["MA5"] = self.df["close"].rolling(window=5).mean()
        
        # 创建MA5线
        ma5_line = Line()
        ma5_line.add_xaxis(self.df["date"].tolist())
        ma5_line.add_yaxis(
            series_name="MA5",
            y_axis=self.df["MA5"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(color="#14b143", width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        
        ma5_line.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_show=False),
            yaxis_opts=opts.AxisOpts(type_="value", is_show=False),
        )
        
        return ma5_line
    
    def plot_vol(self):
        """绘制成交量柱状图"""
        # 检查数据是否有vol列
        if "vol" not in self.df.columns:
            if "volume" in self.df.columns:
                self.df["vol"] = self.df["volume"]
            else:
                logger.warning("数据中没有成交量列")
                # 创建一个空的Bar图表
                return Bar()
        
        # 创建成交量柱状图
        volume_bar = Bar()
        volume_bar.add_xaxis(self.df["date"].tolist())
        volume_bar.add_yaxis(
            series_name="成交量",
            y_axis=self.df["vol"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    '''
                    function(params) {
                        var colorList;
                        if (params.data >= 0) {
                          colorList = '#ef232a';
                        } else {
                          colorList = '#14b143';
                        }
                        return colorList;
                    }
                    '''
                )
            )
        )
        
        volume_bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=1, axislabel_opts=opts.LabelOpts(is_show=True)),
            yaxis_opts=opts.AxisOpts(grid_index=1, is_scale=True),
            legend_opts=opts.LegendOpts(is_show=True),
        )
        
        return volume_bar
    
    def plot_macd_1(self):
        """绘制MACD柱状图"""
        # 检查数据是否有MACD相关列
        if not all(col in self.df.columns for col in ["DIF", "DEA", "MACD"]):
            logger.warning("数据中没有MACD相关列，使用收盘价计算")
            # 计算MACD
            close_array = self.df["close"].values
            # 计算短期EMA
            short_ema = np.zeros_like(close_array)
            short_ema[0] = close_array[0]
            multiplier = 2 / (12 + 1)
            for i in range(1, len(close_array)):
                short_ema[i] = close_array[i] * multiplier + short_ema[i-1] * (1 - multiplier)
            
            # 计算长期EMA
            long_ema = np.zeros_like(close_array)
            long_ema[0] = close_array[0]
            multiplier = 2 / (26 + 1)
            for i in range(1, len(close_array)):
                long_ema[i] = close_array[i] * multiplier + long_ema[i-1] * (1 - multiplier)
            
            # 计算DIF
            dif = short_ema - long_ema
            
            # 计算DEA
            dea = np.zeros_like(dif)
            dea[0] = dif[0]
            multiplier = 2 / (9 + 1)
            for i in range(1, len(dif)):
                dea[i] = dif[i] * multiplier + dea[i-1] * (1 - multiplier)
            
            # 计算MACD柱
            macd = (dif - dea) * 2
            
            # 保存到数据中
            self.df["DIF"] = dif
            self.df["DEA"] = dea
            self.df["MACD"] = macd
        
        # 创建MACD柱状图
        macd_bar = Bar()
        macd_bar.add_xaxis(self.df["date"].tolist())
        macd_bar.add_yaxis(
            series_name="MACD",
            y_axis=self.df["MACD"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    '''
                    function(params) {
                        var colorList;
                        if (params.data >= 0) {
                          colorList = '#D3403B';
                        } else {
                          colorList = '#66A578';
                        }
                        return colorList;
                    }
                    '''
                )
            )
        )
        
        macd_bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=2, axislabel_opts=opts.LabelOpts(is_show=True)),
            yaxis_opts=opts.AxisOpts(grid_index=2, is_scale=True),
            legend_opts=opts.LegendOpts(is_show=True),
        )
        
        return macd_bar
    
    def plot_dif_dea(self):
        """绘制DIF和DEA线"""
        # 检查数据是否有DIF和DEA列
        if not all(col in self.df.columns for col in ["DIF", "DEA"]):
            logger.warning("数据中没有DIF和DEA列")
            # 创建一个空的Line图表
            return Line()
        
        # 创建DIF和DEA线
        dif_dea_line = Line()
        dif_dea_line.add_xaxis(self.df["date"].tolist())
        dif_dea_line.add_yaxis(
            series_name="DIF",
            y_axis=self.df["DIF"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(color="#ef232a", width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        dif_dea_line.add_yaxis(
            series_name="DEA",
            y_axis=self.df["DEA"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(color="#14b143", width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        
        dif_dea_line.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=2, is_show=False),
            yaxis_opts=opts.AxisOpts(type_="value", grid_index=2, is_show=False),
        )
        
        return dif_dea_line
    
    def plot_cdl(self):
        """绘制CDL柱状图"""
        # 检查数据是否有CDLMORNINGSTAR列
        if "CDLMORNINGSTAR" not in self.df.columns:
            logger.warning("数据中没有CDLMORNINGSTAR列，创建默认值")
            # 创建默认的CDLMORNINGSTAR列
            self.df["CDLMORNINGSTAR"] = np.zeros(len(self.df))
        
        # 创建CDL柱状图
        cdl_bar = Bar()
        cdl_bar.add_xaxis(self.df["date"].tolist())
        cdl_bar.add_yaxis(
            series_name="CDLMORNINGSTAR",
            y_axis=self.df["CDLMORNINGSTAR"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        
        cdl_bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=3, axislabel_opts=opts.LabelOpts(is_show=True)),
            yaxis_opts=opts.AxisOpts(grid_index=3, is_scale=True),
            legend_opts=opts.LegendOpts(is_show=True),
        )
        
        return cdl_bar
    
    def mark_cdl(self):
        """标记CDL信号"""
        # 检查数据是否有CDLMORNINGSTAR列
        if "CDLMORNINGSTAR" not in self.df.columns:
            logger.warning("数据中没有CDLMORNINGSTAR列")
            # 返回一个空的Scatter图表
            return Scatter()
        
        # 检查数据是否有MA5列
        if "MA5" not in self.df.columns:
            logger.warning("数据中没有MA5列，使用收盘价代替")
            # 计算MA5
            self.df["MA5"] = self.df["close"].rolling(window=5).mean()
        
        # 找出CDLMORNINGSTAR大于50的索引
        high_indices = self.df[self.df["CDLMORNINGSTAR"] > 50].index.tolist()
        
        if not high_indices:
            logger.warning("没有找到CDL信号点")
            # 返回一个空的Scatter图表
            return Scatter()
        
        # 准备 x 轴和 y 轴数据
        x_data = self.df.loc[high_indices, "date"].tolist() if 'date' in self.df.columns else (
                self.df.index[high_indices].strftime('%Y-%m-%d').tolist() if hasattr(self.df.index, 'strftime') else self.df.index[high_indices].tolist())
        y_data = self.df.loc[high_indices, "MA5"].tolist()  # 使用 MA5 作为 y 轴的数据
        
        # 创建 Scatter 图表
        scatter = Scatter()
        scatter.add_xaxis(x_data)
        scatter.add_yaxis(
            series_name="CDLMORNINGSTAR > 50",
            y_axis=y_data,
            symbol='arrow',  # 使用向下箭头形状的标记
            symbol_size=10,  # 设置标记大小
            symbol_rotate=180,  # 箭头向下
            label_opts=opts.LabelOpts(is_show=False),  # 不显示标签
            itemstyle_opts=opts.ItemStyleOpts(
                color='rgba(0, 255, 0, 0.9)',  # 蓝色，80% 透明度
            )
        )
        
        # 设置 Scatter 图表的全局选项
        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title="CDLMORNINGSTAR Signal Marks on MA5"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(type_="value")
        )
        
        return scatter
    
    def render_html(self, output_path=None):
        kline=self.plot_kline_1()
        ma5_line=self.plot_ma5()
        macd_line=self.plot_macd_1()
        dif_dea_line=self.plot_dif_dea()
        overlap_kline_line = kline.overlap(ma5_line)
        vol_line=self.plot_vol()
        mark_cdl=self.mark_cdl()
        # 最下面的柱状图和折线图
        overlap_bar_line = macd_line.overlap(dif_dea_line)
        overlap_kline_line = overlap_kline_line.overlap(mark_cdl)
    
        # 最后的 Grid
        grid_chart = Grid()
    
        # 这个是为了把 data.datas 这个数据写入到 html 中,还没想到怎么跨 series 传值
        # demo 中的代码也是用全局变量传的
        grid_chart.add_js_funcs("var barData = {}".format(self.df["vol"].tolist()))
        

        # K线图和 MA5 的折线图
        grid_chart.add(
            overlap_kline_line,
            grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", height="60%"),
        )
        # Volumn 柱状图
        grid_chart.add(
            vol_line,
            grid_opts=opts.GridOpts(
                pos_left="3%", pos_right="1%", pos_top="71%", height="10%"
            ),
        )
        
        # MACD DIFS DEAS
        grid_chart.add(
            overlap_bar_line,
            grid_opts=opts.GridOpts(
                pos_left="3%", pos_right="1%", pos_top="82%", height="14%"
            ),
        )
        
        # 如果提供了输出路径，则渲染到指定路径
        if output_path:
            grid_chart.render(output_path)
        
        # 将网格布局设置为self.chart
        self.chart = grid_chart
        
        return grid_chart
    
    def draw_klines(self, data, ma_data=None, signal_points=None):
        """
        绘制单一的K线图，可选叠加已计算好的均线数据和买点卖点标记
        
        Args:
            data: 包含开盘价、最高价、最低价、收盘价等数据的DataFrame
            ma_data: 已计算好的均线数据字典，格式为 {"MA5": [...], "MA10": [...]} 或 None
            signal_points: 买点卖点标记数据，格式为 {"buy": [(date1, price1), (date2, price2), ...], "sell": [(date1, price1), (date2, price2), ...]} 或 None
        
        Returns:
            pyecharts.charts.Kline: K线图对象
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制K线图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 准备数据
        kline_data = df[['open', 'close', 'low', 'high']].values.tolist()  # 将pd转换为数组 股价
        dates = [str(idx.date()) for idx in df.index]  # 横坐标 日期
        
        # 创建K线图
        kline = Kline()
        kline.add_xaxis(xaxis_data=dates)
        kline.add_yaxis(
            series_name="股价",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(opacity=.8),
        )
        kline.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name='日期',
                is_scale=True,
            ),
            yaxis_opts=opts.AxisOpts(
                name='股价',
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True,
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.7)
                ),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0],
                    range_start=80,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    xaxis_index=[0],
                    pos_top="90%",
                    range_start=80,
                    range_end=100,
                ),
            ],
            title_opts=opts.TitleOpts(title="K线图"),
            tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
        )
        
        # 如果提供了均线数据，则叠加均线
        if ma_data:
            ma_line = Line()
            ma_line.add_xaxis(dates)
            
            for name, values in ma_data.items():
                ma_line.add_yaxis(
                    series_name=name,
                    y_axis=values,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
                    label_opts=opts.LabelOpts(is_show=False),
                )
            
            kline = kline.overlap(ma_line)
        
        # 如果提供了买点卖点标记，则添加标记
        if signal_points:
            # 创建买点标记
            if "buy" in signal_points:
                buy_line = Line()
                buy_dates = []
                buy_prices = []
                for date, price in signal_points["buy"]:
                    if date in dates:
                        buy_dates.append(date)
                        buy_prices.append(price)
                    else:
                        logger.warning(f"买点日期 {date} 不在数据范围内")
                
                if buy_dates:
                    buy_line.add_xaxis(xaxis_data=buy_dates)
                    buy_line.add_yaxis(
                        series_name="买入信号",
                        y_axis=buy_prices,
                        symbol="droplet",  # 水滴形状标记
                        symbol_size=20,  # 增大标记尺寸
                        itemstyle_opts=opts.ItemStyleOpts(
                            color="#14b143",  # 绿色买点
                            border_color="#0a7a0a",
                            border_width=2
                        ),
                        linestyle_opts=opts.LineStyleOpts(is_show=False),
                        label_opts=opts.LabelOpts(
                            is_show=True,  # 显示标签
                            position="top",  # 标签位置在上方
                            formatter="买入",
                            color="#14b143",
                            font_size=12,
                            font_weight="bold"
                        ),
                    )
                    kline = kline.overlap(buy_line)
            
            # 创建卖点标记
            if "sell" in signal_points:
                sell_line = Line()
                sell_dates = []
                sell_prices = []
                for date, price in signal_points["sell"]:
                    if date in dates:
                        sell_dates.append(date)
                        sell_prices.append(price)
                    else:
                        logger.warning(f"卖点日期 {date} 不在数据范围内")
                
                if sell_dates:
                    sell_line.add_xaxis(xaxis_data=sell_dates)
                    sell_line.add_yaxis(
                        series_name="卖出信号",
                        y_axis=sell_prices,
                        symbol="droplet",  # 水滴形状标记
                        symbol_size=20,  # 增大标记尺寸
                        itemstyle_opts=opts.ItemStyleOpts(
                            color="#ef232a",  # 红色卖点
                            border_color="#a81313",
                            border_width=2
                        ),
                        linestyle_opts=opts.LineStyleOpts(is_show=False),
                        label_opts=opts.LabelOpts(
                            is_show=True,  # 显示标签
                            position="bottom",  # 标签位置在下方
                            formatter="卖出",
                            color="#ef232a",
                            font_size=12,
                            font_weight="bold"
                        ),
                    )
                    kline = kline.overlap(sell_line)
        
        return kline
    
    def draw_macd(self, dates, dif, dea, macd):
        """
        绘制单一的MACD指标图
        
        Args:
            dates: 日期列表
            dif: 已计算好的DIF数据列表
            dea: 已计算好的DEA数据列表
            macd: 已计算好的MACD柱状图数据列表
        
        Returns:
            pyecharts.charts.Bar: 叠加了DIF和DEA线的MACD柱状图对象
        """
        # 创建MACD柱状图
        bar = Bar()
        bar.add_xaxis(dates)
        bar.add_yaxis(
            series_name="MACD",
            y_axis=macd,
            xaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            z=0,
            itemstyle_opts=opts.ItemStyleOpts(
                opacity=0.7,
                color=JsCode(
                    '''
                    function(params) {
                        var colorList;
                        if (params.data >= 0) {
                          colorList = '#D3403B';
                        } else {
                          colorList = '#66A578';
                        }
                        return colorList;
                    }
                    '''
                )
            )
        )
        
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=1,
                axislabel_opts=opts.LabelOpts(is_show=True),
                is_scale=True,
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                split_number=4,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            ),
            legend_opts=opts.LegendOpts(is_show=True),
        )
        
        # 创建DIF和DEA线
        line = Line()
        line.add_xaxis(dates)
        line.add_yaxis(
            series_name="DIF",
            y_axis=dif,
            xaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2),
        )
        line.add_yaxis(
            series_name="DEA",
            y_axis=dea,
            xaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2),
        )
        
        return bar.overlap(line)
    
    def draw_line(self, data, series_name='指标', y_column='value'):
        """
        绘制单一的折线图
        
        Args:
            data: 包含数据的DataFrame
            series_name: 系列名称
            y_column: Y轴数据列名
        
        Returns:
            pyecharts.charts.Line: 折线图对象
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制折线图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        dates = [str(idx.date()) for idx in df.index]
        
        line = Line()
        line.add_xaxis(dates)
        line.add_yaxis(
            series_name=series_name,
            y_axis=df[y_column].tolist(),
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        
        line.set_global_opts(
            title_opts=opts.TitleOpts(title=f"{series_name}折线图"),
            tooltip_opts=opts.TooltipOpts(trigger='axis'),
            xaxis_opts=opts.AxisOpts(name='日期', is_scale=True),
            yaxis_opts=opts.AxisOpts(name=series_name, is_scale=True),
        )
        
        return line
    
    def draw_bar(self, data, series_name='指标', y_column='value'):
        """
        绘制单一的柱状图
        
        Args:
            data: 包含数据的DataFrame
            series_name: 系列名称
            y_column: Y轴数据列名
        
        Returns:
            pyecharts.charts.Bar: 柱状图对象
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制柱状图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        dates = [str(idx.date()) for idx in df.index]
        
        bar = Bar()
        bar.add_xaxis(dates)
        bar.add_yaxis(
            series_name=series_name,
            y_axis=df[y_column].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
        
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title=f"{series_name}柱状图"),
            tooltip_opts=opts.TooltipOpts(trigger='axis'),
            xaxis_opts=opts.AxisOpts(name='日期', is_scale=True),
            yaxis_opts=opts.AxisOpts(name=series_name, is_scale=True),
        )
        
        return bar
    
    def draw_gauge(self, value=90, title="仪表图", subtitle="示例"):
        """
        绘制仪表盘图
        
        Args:
            value: 仪表显示的数值
            title: 图表标题
            subtitle: 图表副标题
        
        Returns:
            pyecharts.charts.Gauge: 仪表盘图对象
        """
        gauge = (
            Gauge()
            .add("", [("电量", value)], split_number=5)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
                legend_opts=opts.LegendOpts(is_show=False),
            )
            .set_series_opts(
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(
                        color=[[0.2, "#c23531"], [0.8, "#63869e"], [1, "#91c7ae"]],
                        width=30,
                    )
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True,
                    linestyle_opts=opts.LineStyleOpts(width=3, color="auto"),
                ),
            )
        )
        
        return gauge
    
    def draw_volume(self, dates, volume_data):
        """
        绘制单一的成交量柱状图
        
        Args:
            dates: 日期列表
            volume_data: 已计算好的成交量数据列表
        
        Returns:
            pyecharts.charts.Bar: 成交量柱状图对象
        """
        bar = Bar()
        bar.add_xaxis(dates)
        bar.add_yaxis(
            series_name="成交量",
            y_axis=volume_data,
            label_opts=opts.LabelOpts(is_show=False),
        )
        
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=1, axislabel_opts=opts.LabelOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(grid_index=1, is_scale=True),
            legend_opts=opts.LegendOpts(is_show=True),
        )
        
        return bar
    
    def drawAll(self, charts_with_layout):
        """
        灵活组合绘制多个图表
        
        Args:
            charts_with_layout: 图表及其布局配置的列表，每个元素为 (chart_object, layout_options) 元组
                               layout_options 包含 pos_left, pos_right, pos_top, height 等布局参数
        
        Returns:
            pyecharts.charts.Grid: 组合图表对象
        """
        grid_chart = Grid(init_opts=opts.InitOpts(width="2560px", height="800px"))
        
        for chart, layout in charts_with_layout:
            if chart:
                grid_chart.add(
                    chart,
                    grid_opts=opts.GridOpts(**layout)
                )
        
        return grid_chart
    
    def draw_kline_volume_signal(self, data, ma_data=None):
        """
        绘制带成交量和信号的K线图
        
        Args:
            data: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
            ma_data: 已计算好的均线数据字典，格式为 {"MA5": [...], "MA10": [...]} 或 None
        
        Returns:
            pyecharts.charts.Grid: 组合图表对象
        """
        if data is None or data.empty:
            logger.warning("无效的数据，无法绘制带成交量和信号的K线图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 检查必要的列
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            logger.warning("数据缺少必要的列，无法绘制完整的K线图")
            return None
        
        dates = [str(idx.date()) for idx in df.index]
        
        # 创建K线图，使用百分比宽度使其适应网页
        kline_chart = self.draw_klines(df, ma_data)
        
        # 创建成交量柱状图
        volume_chart = self.draw_volume(dates, df["volume"].tolist())
        
        # 使用drawAll方法组合图表
        grid_chart = self.drawAll([
            (kline_chart, {"pos_left": "10%", "pos_right": "10%", "height": "40%", "pos_top": "10%"}),
            (volume_chart, {"pos_left": "10%", "pos_right": "10%", "pos_top": "60%", "height": "20%"})
        ])
        
        # 添加JavaScript函数用于成交量颜色
        grid_chart.add_js_funcs("var barData={}".format(df[["open", "close"]].values.tolist()))
        
        return grid_chart
    
    def _plot_minute(self, data):
        """绘制分时图"""
        # 尝试从不同的列名中提取数据
        rename_map = {
            'price': 'close', '成交价': 'close',
            'avg_price': 'avg_price', '均价': 'avg_price',
            'volume': 'volume', '成交量': 'volume'
        }
        data = data.rename(columns=rename_map)
        
        # 创建折线图
        line = Line()
        time_list = data.index.strftime('%H:%M').tolist()
        
        # 获取自定义颜色
        colors = self.kwargs.get('colors', {})
        price_color = colors.get('price_color', '#ef232a')
        avg_color = colors.get('avg_color', '#14b143')
        
        # 添加价格线
        line.add_xaxis(time_list)
        line.add_yaxis(
            "价格",
            data['close'].tolist(),
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=2),
            itemstyle_opts=opts.ItemStyleOpts(color=price_color),
        )
        
        # 添加均价线
        if 'avg_price' in data.columns:
            line.add_yaxis(
                "均价",
                data['avg_price'].tolist(),
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=2),
                itemstyle_opts=opts.ItemStyleOpts(color=avg_color),
            )
        
        # 处理网格配置
        grid_config = self.kwargs.get('grid', {})
        grid_left = grid_config.get('left', '10%')
        grid_right = grid_config.get('right', '10%')
        
        # 创建成交量柱状图
        if self.kwargs.get('volume', False) and 'volume' in data.columns:
            bar = Bar()
            bar.add_xaxis(time_list)
            bar.add_yaxis(
                "成交量",
                data['volume'].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#82ca9d"),
            )
            
            # 创建网格布局
            grid_chart = Grid()
            grid_chart.add(line, grid_opts=opts.GridOpts(pos_left=grid_left, pos_right=grid_right, height="60%"))
            grid_chart.add(bar, grid_opts=opts.GridOpts(pos_left=grid_left, pos_right=grid_right, pos_top="70%", height="20%"))
            self.chart = grid_chart
        else:
            self.chart = line
        
        # 设置全局配置
        self.chart.set_global_opts(
            title_opts=opts.TitleOpts(title=self.kwargs.get('title', '分时图')),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(pos_top="3%"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True,
                    areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
        )
    
    def update(self):
        """更新图表数据"""
        # 重新准备数据，支持直接更新传入的数据
        data = self._prepare_data()
        
        # 重新绘制图表
        if self.chart_type == 'kline':
            self._plot_kline(data)
        elif self.chart_type == 'minute':
            self._plot_minute(data)
        elif self.chart_type == 'line':
            self._plot_line(data)
        elif self.chart_type == 'bar':
            self._plot_bar(data)
        
        return self
    
    def save(self, file_path='chart.html', **kwargs):
        """保存图表到文件
        
        Args:
            file_path: 文件保存路径
            **kwargs: 其他参数
                - type: 输出类型，如 'html' 或 'image'
                - image_format: 图片格式，如 'png', 'jpeg' 等
                - driver_type: 驱动类型，如 'chrome', 'firefox' 等，默认为 'chrome'
        """
        if self.chart is None:
            self.plot()
        
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 检查是否需要保存为图片
        output_type = kwargs.get('type', 'html')
        image_formats = ['.png', '.jpg', '.jpeg', '.svg']
        
        # 如果文件扩展名是图片格式，或者明确指定了type为image，则保存为图片
        if file_ext in image_formats or output_type.lower() == 'image':
            # 如果文件没有图片扩展名，则添加默认的.png扩展名
            if file_ext not in image_formats:
                file_path += '.png'
                file_ext = '.png'
            
            # 使用make_snapshot方法保存为图片
            try:
                # 先保存为临时HTML文件
                temp_html_path = file_path.replace(file_ext, '.html')
                self.chart.render(temp_html_path)
                
                # 然后使用make_snapshot将HTML转换为图片
                make_snapshot(driver, temp_html_path, file_path)
                logger.info(f"图表已成功保存为图片: {file_path}")
                
                # 可选：删除临时HTML文件
                if os.path.exists(temp_html_path):
                    os.remove(temp_html_path)
                    logger.debug(f"已删除临时HTML文件: {temp_html_path}")
            except ImportError:
                logger.error("未找到snapshot-selenium库，请使用pip install snapshot-selenium安装")
                # 尝试使用render方法的path参数保存为图片作为备选
                try:
                    self.chart.render(path=file_path, **kwargs)
                    logger.info(f"已使用render方法保存为图片: {file_path}")
                except Exception as e:
                    logger.error(f"保存图片失败: {str(e)}")
                    # 尝试保存为HTML作为备选
                    html_path = os.path.splitext(file_path)[0] + '.html'
                    self.chart.render(html_path, **kwargs)
                    logger.info(f"已作为备选保存为HTML: {html_path}")
            except Exception as e:
                logger.error(f"使用make_snapshot保存图片失败: {str(e)}")
                # 尝试使用render方法的path参数保存为图片作为备选
                try:
                    self.chart.render(path=file_path, **kwargs)
                    logger.info(f"已使用render方法保存为图片: {file_path}")
                except Exception as e:
                    logger.error(f"保存图片失败: {str(e)}")
                    # 尝试保存为HTML作为备选
                    html_path = os.path.splitext(file_path)[0] + '.html'
                    self.chart.render(html_path, **kwargs)
                    logger.info(f"已作为备选保存为HTML: {html_path}")
        else:
            # 保存为HTML
            if not file_ext:
                file_path += '.html'
            elif file_ext != '.html':
                file_path = os.path.splitext(file_path)[0] + '.html'
            
            self.chart.render(file_path, **kwargs)
            logger.info(f"图表已成功保存为HTML: {file_path}")
        
        return self
    
    def show(self, **kwargs):
        """显示图表"""
        if self.chart is None:
            self.plot()
            
        # 支持在不同环境中显示
        if kwargs.get('inline', True):
            # 在notebook中内联显示
            self.chart.render_notebook()
        else:
            # 在浏览器中打开
            self.chart.render('temp_chart.html', **kwargs)
            webbrowser.open('file://' + os.path.realpath('temp_chart.html'))
        
        return self


def example_draw_complete_chart():
    """
    示例函数：绘制一个完整的金融图表，包括K线、均线、成交量和MACD
    
    这个函数展示了如何使用PyechartsChart_2类创建一个完全相同的金融图表
    """
    # 导入必要的库
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import random
    
    # 生成示例数据
    def generate_sample_stock_data(days=100):
        """生成示例股票数据"""
        # 创建日期序列
        dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
        dates = [d.strftime('%Y%m%d') for d in dates]
        
        # 生成开盘价、最高价、最低价、收盘价和成交量
        start_price = 100
        open_prices = []
        close_prices = []
        high_prices = []
        low_prices = []
        volumes = []
        
        for i in range(days):
            # 生成随机价格变动
            change = random.uniform(-2, 2)
            
            # 确保价格不会变为负数
            if i == 0:
                open_price = start_price
            else:
                open_price = close_prices[i-1] + random.uniform(-1, 1)
            
            # 确保价格合理
            close_price = max(open_price + change, 1)
            high_price = max(open_price, close_price) + random.uniform(0, 1)
            low_price = min(open_price, close_price) - random.uniform(0, 1)
            volume = int(random.uniform(5000, 20000))
            
            open_prices.append(open_price)
            close_prices.append(close_price)
            high_prices.append(high_price)
            low_prices.append(low_price)
            volumes.append(volume)
        
        # 创建DataFrame
        df = pd.DataFrame({
            'date': dates,
            'open': open_prices,
            'close': close_prices,
            'high': high_prices,
            'low': low_prices,
            'vol': volumes
        })
        
        # 计算MA5
        df['MA5'] = df['close'].rolling(window=5).mean()
        
        # 计算MACD相关指标
        close_array = df['close'].values
        
        # 计算短期EMA
        short_ema = np.zeros_like(close_array)
        short_ema[0] = close_array[0]
        multiplier = 2 / (12 + 1)
        for i in range(1, len(close_array)):
            short_ema[i] = close_array[i] * multiplier + short_ema[i-1] * (1 - multiplier)
        
        # 计算长期EMA
        long_ema = np.zeros_like(close_array)
        long_ema[0] = close_array[0]
        multiplier = 2 / (26 + 1)
        for i in range(1, len(close_array)):
            long_ema[i] = close_array[i] * multiplier + long_ema[i-1] * (1 - multiplier)
        
        # 计算DIF
        dif = short_ema - long_ema
        
        # 计算DEA
        dea = np.zeros_like(dif)
        dea[0] = dif[0]
        multiplier = 2 / (9 + 1)
        for i in range(1, len(dif)):
            dea[i] = dif[i] * multiplier + dea[i-1] * (1 - multiplier)
        
        # 计算MACD柱
        macd = (dif - dea) * 2
        
        # 添加到DataFrame
        df['DIF'] = dif
        df['DEA'] = dea
        df['MACD'] = macd
        
        # 添加CDLMORNINGSTAR信号（随机生成一些信号点）
        df['CDLMORNINGSTAR'] = 0
        signal_indices = random.sample(range(10, days-10), 5)  # 随机选择5个位置作为信号点
        for idx in signal_indices:
            df.loc[idx, 'CDLMORNINGSTAR'] = 100  # 100表示强烈的买入信号
        
        return df
    
    # 生成示例数据
    df = generate_sample_stock_data(days=120)  # 生成120天的示例数据
    
    # 创建PyechartsChart_2实例
    chart = PyechartsChart_2(chart_type='kline', data=df)
    
    # 使用render_html方法绘制完整的图表
    # 这个方法会自动调用plot_kline_1, plot_ma5, plot_macd_1, plot_dif_dea, plot_vol等方法
    chart.render_html()
    
    # 保存图表为HTML文件
    chart.save('example_chart.html')
    
    # 在浏览器中显示图表
    chart.show(inline=False)
    
    print("图表已生成并保存为example_chart.html")
    print("图表也已在浏览器中打开")
    
    return chart


# 如果直接运行这个文件，则执行示例函数
if __name__ == "__main__":
    example_draw_complete_chart()

