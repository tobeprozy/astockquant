"""
基于pyecharts的K线图绘图器
"""

from qplot.plotter import Plotter
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PyechartsCandlestickPlotter(Plotter):
    """
    基于pyecharts的K线图绘图器
    使用pyecharts库绘制交互式K线图
    """
    
    def __init__(self):
        """
        初始化pyecharts K线图绘图器
        """
        super().__init__()
    
    def plot(self, data: pd.DataFrame, **kwargs) -> Any:
        """
        绘制K线图
        
        Args:
            data: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
            **kwargs: 其他绘图参数，包括：
                - title: 图表标题
                - width: 图表宽度
                - height: 图表高度
                - volume: 是否显示成交量
                - indicators: 要显示的指标列表，如['ma5', 'ma10', 'ma20']
                - save_path: 图表保存路径，None表示不保存
                - is_horizontal: 是否水平布局
        
        Returns:
            pyecharts.charts.Grid: 图表对象
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制K线图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 设置默认参数
        title = kwargs.get('title', f"{self._get_symbol_from_data(df)} 日K线图")
        width = kwargs.get('width', 1200)
        height = kwargs.get('height', 600)
        volume = kwargs.get('volume', True)
        indicators = kwargs.get('indicators', ['ma5', 'ma10', 'ma20'])
        save_path = kwargs.get('save_path', None)
        is_horizontal = kwargs.get('is_horizontal', False)
        
        # 准备K线数据
        kline_data = []
        dates = []
        
        for idx, row in df.iterrows():
            dates.append(str(idx.date()))
            kline_data.append([row['open'], row['close'], row['low'], row['high']])
        
        # 创建K线图
        kline = Kline(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px", theme=kwargs.get('theme', 'white')))
        kline.add_xaxis(xaxis_data=dates)
        kline.add_yaxis(
            series_name="K线",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",  # 阳线颜色
                color0="#14b143",  # 阴线颜色
                border_color="#ef232a",
                border_color0="#14b143"
            )
        )
        
        kline.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=0.1))
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", xaxis_index=[0, 1], range_start=0, range_end=100),
                opts.DataZoomOpts(type_="slider", xaxis_index=[0, 1], range_start=0, range_end=100)
            ],
            legend_opts=opts.LegendOpts(is_show=True)
        )
        
        # 创建网格布局
        grid = Grid(
            init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px", theme=kwargs.get('theme', 'white'))
        )
        
        # 计算布局高度比例
        if volume:
            kline_height = 0.7
            volume_height = 0.3
        else:
            kline_height = 1.0
            volume_height = 0.0
        
        # 添加K线图到网格
        grid.add(kline, grid_opts=opts.GridOpts(height=f"{kline_height * 100}%", top="5%"))
        
        # 添加成交量
        if volume:
            bar = Bar()
            bar.add_xaxis(xaxis_data=dates)
            bar.add_yaxis(
                series_name="成交量",
                y_axis=df['volume'].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color={"type": "color", "value": "#3370FF"})
            )
            bar.set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
                yaxis_opts=opts.AxisOpts(is_scale=True)
            )
            grid.add(bar, grid_opts=opts.GridOpts(height=f"{volume_height * 100}%", top=f"{5 + kline_height * 100}%"))
        
        # 添加指标
        if indicators:
            ma_data = self._calculate_indicators(df, indicators)
            for ma_name, ma_values in ma_data.items():
                line = Line()
                line.add_xaxis(xaxis_data=dates)
                line.add_yaxis(
                    series_name=ma_name,
                    y_axis=ma_values,
                    is_smooth=True,
                    is_symbol_show=False,
                    line_style_opts=opts.LineStyleOpts(width=1)
                )
                # 将指标线叠加到K线图上
                kline.overlap(line)
        
        # 保存图表
        if save_path:
            try:
                grid.render(save_path)
                logger.info(f"已将K线图保存到: {save_path}")
            except Exception as e:
                logger.error(f"保存K线图时出错: {e}")
        
        # 显示图表
        return grid
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        df = super()._preprocess_data(data)
        
        # 确保数据按时间排序
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df.columns:
                # 如果缺少必要的列，尝试从其他可能的列名中获取
                if col == 'open' and '开盘价' in df.columns:
                    df['open'] = df['开盘价']
                elif col == 'high' and '最高价' in df.columns:
                    df['high'] = df['最高价']
                elif col == 'low' and '最低价' in df.columns:
                    df['low'] = df['最低价']
                elif col == 'close' and '收盘价' in df.columns:
                    df['close'] = df['收盘价']
                else:
                    raise ValueError(f"数据缺少必要的列: {col}")
        
        # 确保volume列存在
        if 'volume' not in df.columns:
            if '成交量' in df.columns:
                df['volume'] = df['成交量']
            else:
                # 如果实在没有成交量数据，用0填充
                df['volume'] = 0
        
        return df
    
    def _calculate_indicators(self, data: pd.DataFrame, indicators: List[str]) -> Dict[str, List[float]]:
        """
        计算技术指标
        
        Args:
            data: 数据
            indicators: 要计算的指标列表
        
        Returns:
            Dict[str, List[float]]: 指标名称到指标值的映射
        """
        result = {}
        
        for indicator in indicators:
            if indicator.startswith('ma'):
                try:
                    period = int(indicator[2:])
                    ma_values = data['close'].rolling(window=period).mean().tolist()
                    result[indicator] = ma_values
                except Exception as e:
                    logger.warning(f"计算均线指标{indicator}时出错: {e}")
        
        return result
    
    def _get_symbol_from_data(self, data: pd.DataFrame) -> str:
        """
        从数据中获取股票代码
        
        Args:
            data: 数据
        
        Returns:
            str: 股票代码
        """
        # 尝试从数据中获取股票代码
        if hasattr(data, 'attrs') and 'symbol' in data.attrs:
            return data.attrs['symbol']
        elif 'symbol' in data.columns:
            return data['symbol'].iloc[0]
        elif 'code' in data.columns:
            return data['code'].iloc[0]
        else:
            return '未知'