"""
基于pyecharts的图表实现
"""

from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Timeline
from pyecharts.commons.utils import JsCode
import pandas as pd
import numpy as np
from qplot.core.plotter import Chart
import logging

logger = logging.getLogger(__name__)

# MACD指标常量定义
MACD_SHORT = 12
MACD_LONG = 26
MACD_SIGNAL = 9


def calculateMACD(closeArray, short_period=12, long_period=26, signal_period=9):
    """
    计算MACD指标
    
    Args:
        closeArray: 收盘价列表
        short_period: 短期EMA周期
        long_period: 长期EMA周期
        signal_period: 信号线EMA周期
        
    Returns:
        tuple: (DIF, DEA, MACD)
    """
    # 转换为numpy数组以便计算
    close_array = np.array(closeArray)
    
    # 计算短期EMA
    short_ema = np.zeros_like(close_array)
    short_ema[0] = close_array[0]
    multiplier = 2 / (short_period + 1)
    for i in range(1, len(close_array)):
        short_ema[i] = close_array[i] * multiplier + short_ema[i-1] * (1 - multiplier)
    
    # 计算长期EMA
    long_ema = np.zeros_like(close_array)
    long_ema[0] = close_array[0]
    multiplier = 2 / (long_period + 1)
    for i in range(1, len(close_array)):
        long_ema[i] = close_array[i] * multiplier + long_ema[i-1] * (1 - multiplier)
    
    # 计算DIF
    dif = short_ema - long_ema
    
    # 计算DEA
    dea = np.zeros_like(dif)
    dea[0] = dif[0]
    multiplier = 2 / (signal_period + 1)
    for i in range(1, len(dif)):
        dea[i] = dif[i] * multiplier + dea[i-1] * (1 - multiplier)
    
    # 计算MACD柱
    macd = (dif - dea) * 2
    
    return dif.tolist(), dea.tolist(), macd

class PyechartsChart(Chart):
    """基于pyecharts的图表实现"""
    
    def __init__(self, chart_type, data_manager=None, data=None, **kwargs):
        """
        初始化图表
        
        Args:
            chart_type: 图表类型，'kline' 或 'minute'
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
    
    def _prepare_data(self):
        """准备绘图数据"""
        # 如果直接提供了数据，优先使用
        if self.data is not None:
            return self.data
        
        # 否则从数据管理器获取数据
        if self.data_manager is not None:
            # 适配当前的DataManager实现
            try:
                # 尝试直接获取数据
                return self.data_manager.get_data()
            except Exception:
                # 兼容不同数据类型
                if self.chart_type == 'kline':
                    # 假设数据管理器包含K线数据
                    if hasattr(self.data_manager, 'get_kline_data'):
                        return self.data_manager.get_kline_data()
                    else:
                        return self.data_manager.get_data()
                elif self.chart_type == 'minute':
                    # 假设数据管理器包含分时数据
                    if hasattr(self.data_manager, 'get_minute_data'):
                        return self.data_manager.get_minute_data()
                    else:
                        return self.data_manager.get_data()
        
        raise ValueError("未提供数据或数据管理器")
    
    def plot(self):
        """绘制图表"""
        data = self._prepare_data()
        
        if self.chart_type == 'kline':
            self._plot_kline(data)
        elif self.chart_type == 'minute':
            self._plot_minute(data)
        
        return self
    
    def _validate_data(self, data):
        """验证数据是否有效"""
        if data is None or data.empty:
            return False
        required_columns = ['open', 'high', 'low', 'close']
        return all(col in data.columns for col in required_columns)
    
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
    
    def calculate_MA(self, closeArray, fast_period=5, slow_period=10):
        """计算均线"""
        # 转换为numpy数组以便计算
        close_array = np.array(closeArray)
        
        # 计算短期EMA
        fast_ma = np.zeros_like(close_array)
        fast_ma[fast_period-1:] = np.convolve(close_array, np.ones(fast_period)/fast_period, mode='valid')
        
        # 计算长期EMA
        slow_ma = np.zeros_like(close_array)
        slow_ma[slow_period-1:] = np.convolve(close_array, np.ones(slow_period)/slow_period, mode='valid')
        
        return fast_ma.tolist(), slow_ma.tolist()
    
    def _plot_kline(self, data):
        """绘制K线图"""
        # 如果data不是标准的OHLCV格式，尝试提取必要的列
        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            # 尝试从不同的列名中提取数据
            rename_map = {
                '开盘': 'open', 'open_price': 'open',
                '最高': 'high', 'high_price': 'high',
                '最低': 'low', 'low_price': 'low',
                '收盘': 'close', 'close_price': 'close',
                '成交量': 'volume', 'vol': 'volume'
            }
            data = data.rename(columns=rename_map)
        
        # 检查是否需要使用带成交量和信号的K线图
        if self.kwargs.get('show_volume_signal', False):
            self.chart = self.draw_kline_volume_signal(data)
        else:
            # 使用draw_klines和drawMACD方法来绘制图表
            overlap_kline_ma = self.draw_klines(data)
            if overlap_kline_ma:
                # 如果需要显示MACD
                if self.kwargs.get('show_macd', False):
                    overlap_bar_line = self.drawMACD(data)
                    if overlap_bar_line:
                        self.chart = self.drawAll(overlap_kline_ma, overlap_bar_line)
                    else:
                        self.chart = overlap_kline_ma
                else:
                    self.chart = overlap_kline_ma
        
        return self
    
    def draw_klines(self, data, self_param=None):
        """
        绘制K线图
        
        Args:
            data: 包含开盘价、最高价、最低价、收盘价等数据的DataFrame
            self_param: 保留参数，用于兼容调用方式
            
        Returns:
            pyecharts.charts.Kline: 叠加了均线的K线图对象
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制K线图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 准备数据
        klineData = df[['open', 'close', 'low', 'high']].values.tolist()  # 将pd转换为数组 股价
        dates = [str(idx.date()) for idx in df.index]  # 横坐标 日期
        
        # 创建K线图
        kline = Kline()
        kline.add_xaxis(xaxis_data=dates)
        kline.add_yaxis(
            series_name="股价/港币",
            y_axis=klineData,
            itemstyle_opts=opts.ItemStyleOpts(opacity=.8),
        )
        kline.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name='日期',
                is_scale=True,
            ),
            yaxis_opts=opts.AxisOpts(
                name='股价/港币',
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
                    xaxis_index=[0, 1],
                    range_start=80,
                    range_end=100,
                ),
                # xaxis_index=[0, 0]设置第一幅图为内部缩放
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    xaxis_index=[0, 1],
                    pos_top="95%",
                    range_start=80,
                    range_end=100,
                ),
                # xaxis_index=[0, 1]连接第二幅图的axis
            ],
            title_opts=opts.TitleOpts(title="股价k线图"),
            tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
        )
        
        # 创建均线图
        maLine = Line()
        maLine.add_xaxis(dates)
        closeArray = df['close'].values.tolist()
        fast_MA, slow_MA = self.calculate_MA(closeArray, 5, 10)  # 计算均线
        
        maLine.add_yaxis(
            series_name="MA5",
            y_axis=fast_MA,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
            label_opts=opts.LabelOpts(is_show=False),  # 不显示具体数值
            z=3,  # ma在最顶层
        )
        
        maLine.add_yaxis(
            series_name="MA10",
            y_axis=slow_MA,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
            label_opts=opts.LabelOpts(is_show=False),
            z=4,
        )
        
        KlineWithMA = kline.overlap(maLine)  # MA画在k线上
        return KlineWithMA
        
    def drawMACD(self, data):
        """
        绘制MACD指标图
        
        Args:
            data: 包含收盘价数据的DataFrame
            
        Returns:
            pyecharts.charts.Bar: 叠加了DIF和DEA线的MACD柱状图
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制MACD图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 准备数据
        closeArray = df['close'].values.tolist()
        DIF, DEA, MACD = calculateMACD(closeArray, MACD_SHORT, MACD_LONG, MACD_SIGNAL)
        dates = [str(idx.date()) for idx in df.index]
        
        # 创建MACD柱状图
        bar_2 = Bar()
        bar_2.add_xaxis(dates)
        bar_2.add_yaxis(
            series_name="MACD",
            y_axis=MACD.tolist(),
            xaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            z=0,
            itemstyle_opts=opts.ItemStyleOpts(
                opacity=0.7,
                color=JsCode(
                    # 就是这么神奇，要写在注释中,但是的确是生效的,通过浏览器进行解析
                    """
                                        function(params) {
                                            var colorList;
                                            if (params.data >= 0) {
                                              colorList = '#D3403B';
                                            } else {
                                              colorList = '#66A578';
                                            }
                                            return colorList;
                                        }
                                        """
                )
            )
        )
        
        bar_2.set_global_opts(
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
            
            legend_opts=opts.LegendOpts(is_show=True, pos_top='70%'),  # 图例
        )
        
        # 创建DIF和DEA线
        line_2 = Line()
        line_2.add_xaxis(dates)
        line_2.add_yaxis(
            series_name="DIF",
            y_axis=DIF,
            xaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2),
        )
        line_2.add_yaxis(
            series_name="DEA",
            y_axis=DEA,
            xaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2),
        )
        
        overlap_bar_line = bar_2.overlap(line_2)
        return overlap_bar_line
        
    def drawAll(self, overlap_kline_ma, overlap_bar_line):
        """
        组合绘制K线图和MACD图
        
        Args:
            overlap_kline_ma: 叠加了均线的K线图对象
            overlap_bar_line: 叠加了DIF和DEA线的MACD柱状图对象
            
        Returns:
            pyecharts.charts.Grid: 组合图表对象
        """
        grid_chart = Grid(init_opts=opts.InitOpts(width="2560px", height="800px"))
        # K线图和 MA 的折线图
        grid_chart.add(
            overlap_kline_ma,
            grid_opts=opts.GridOpts(pos_left="3%", pos_right="3%", height="60%"),
        )
        # MACD DIFS DEAS
        grid_chart.add(
            overlap_bar_line,
            grid_opts=opts.GridOpts( pos_left="3%", pos_right="3%", pos_top="72%", height="20%"),
        )
        return grid_chart
    
    def draw_kline_volume_signal(self, data):
        """
        绘制带成交量和信号的K线图
        
        Args:
            data: 包含开盘价、最高价、最低价、收盘价、成交量、均线等数据的DataFrame
            
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
        
        # 创建K线图，使用百分比宽度使其适应网页
        kline = (
            Kline(init_opts=opts.InitOpts(width="100%", height="1000px"))
            .add_xaxis(xaxis_data=[str(idx.date()) for idx in df.index])
            .add_yaxis(
                series_name="klines",
                y_axis=df[["open", "close", "low", "high"]].values.tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=self.kwargs.get('title', 'K线图'), pos_top="1%", pos_left="center"),
                legend_opts=opts.LegendOpts(is_show=True, pos_top="3%", pos_left="center"),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=False,
                        type_="inside",
                        xaxis_index=[0,1],
                        range_start=98,
                        range_end=100,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=[0,1],
                        type_="slider",
                        pos_top="85%",
                        range_start=98,
                        range_end=100,
                    ),
                ],
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=False,
                    dimension=2,
                    series_index=5,
                    is_piecewise=True,
                    pieces=[
                        {"value": 1, "color": "#00da3c"},
                        {"value": -1, "color": "#ec0000"},
                    ],
                ),
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                brush_opts=opts.BrushOpts(
                    x_axis_index="all",
                    brush_link="all",
                    out_of_brush={"colorAlpha": 0.1},
                    brush_type="lineX",
                ),
            )
        )

        # 创建成交量柱状图
        bar = (
            Bar()
            .add_xaxis(xaxis_data=[str(idx.date()) for idx in df.index])
            .add_yaxis(
                series_name="volume",
                y_axis=df["volume"].tolist(),
                xaxis_index=1,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                    function(params) {
                        var colorList;
                        if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
                            colorList = '#ef232a';
                        } else {
                            colorList = '#14b143';
                        }
                        return colorList;
                    }
                    """
                    )
                ),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=1,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )
        
        # 创建均线图
        line=(Line()
            .add_xaxis(xaxis_data=[str(idx.date()) for idx in df.index])
        )
        
        # 添加可用的均线
        for ma_period in ['ma5', 'ma10', 'ma20']:
            if ma_period in df.columns:
                line.add_yaxis(
                    series_name=ma_period,
                    y_axis=df[ma_period].tolist(),
                    xaxis_index=1,
                    yaxis_index=1,
                    label_opts=opts.LabelOpts(is_show=False),
                )
        
        # 创建网格布局，使用百分比宽度使其适应网页
        grid_chart = Grid(
            init_opts=opts.InitOpts(
                width="100%",
                height="1000px",
                animation_opts=opts.AnimationOpts(animation=False),
            )
        )

        # 添加JavaScript函数
        grid_chart.add_js_funcs("var barData={}".format(df[["open", "close"]].values.tolist()))
        
        # 叠加K线图和均线图
        overlap_kline_line = kline.overlap(line)
        
        # 添加图表到网格，调整布局使其居中
        grid_chart.add(
            overlap_kline_line,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", height="40%", pos_top="10%"),
        )
        grid_chart.add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="10%", pos_top="60%", height="20%"
            ),
        )
        
        return grid_chart
    
    def _draw_macd(self, data, macd_color_pos=None, macd_color_neg=None, dif_color=None, dea_color=None):
        """保留此方法作为兼容性支持，内部调用新的 drawMACD 方法"""
        return self.drawMACD(data)
    
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
            line_opts=opts.LineStyleOpts(width=2),
            itemstyle_opts=opts.ItemStyleOpts(color=price_color),
        )
        
        # 添加均价线
        if 'avg_price' in data.columns:
            line.add_yaxis(
                "均价",
                data['avg_price'].tolist(),
                is_smooth=True,
                line_opts=opts.LineStyleOpts(width=2),
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
        
        return self
    
    def save(self, file_path='chart.html', **kwargs):
        """保存图表到文件"""
        if self.chart is None:
            self.plot()
        
        # 支持保存为不同格式（pyecharts主要支持HTML）
        output_type = kwargs.get('type', 'html')
        if output_type.lower() == 'html':
            if file_path.endswith('.html'):
                self.chart.render(file_path, **kwargs)
            else:
                self.chart.render(file_path + '.html', **kwargs)
        else:
            # 发出警告，pyecharts主要支持HTML格式
            import warnings
            warnings.warn("pyecharts主要支持HTML格式，其他格式可能不被支持")
            if file_path.endswith('.html'):
                self.chart.render(file_path, **kwargs)
            else:
                self.chart.render(file_path + '.html', **kwargs)
        
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
            import webbrowser
            import os
            webbrowser.open('file://' + os.path.realpath('temp_chart.html'))
        
        return self