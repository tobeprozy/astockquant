"""
基于pyecharts的图表实现 - 全新版本

设计说明：
1. 完全分离计算与绘图逻辑，所有指标数据通过参数传入
2. 每个绘图方法专注于绘制单一指标图
3. 通过drawAll方法实现灵活的图表布局组合
4. 支持多种图表类型和图片保存功能
"""

from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Gauge
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

class PyechartsChart_1(Chart):
    """基于pyecharts的图表实现 - 全新版本"""
    
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
    
    def _prepare_data(self):
        """准备绘图数据"""
        # 如果直接提供了数据，优先使用
        if self.data is not None:
            return self.data
        
        # 否则从数据管理器获取数据
        if self.data_manager is not None:
            try:
                return self.data_manager.get_data()
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
        
        self.chart = self.draw_klines(data)
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