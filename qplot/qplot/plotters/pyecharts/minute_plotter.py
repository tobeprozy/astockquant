"""
基于pyecharts的分时图绘图器
"""

from qplot.plotter import Plotter
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Grid
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PyechartsMinutePlotter(Plotter):
    """
    基于pyecharts的分时图绘图器
    使用pyecharts库绘制交互式分时图
    """
    
    def __init__(self):
        """
        初始化pyecharts分时图绘图器
        """
        super().__init__()
    
    def plot(self, data: pd.DataFrame, **kwargs) -> Any:
        """
        绘制分时图
        
        Args:
            data: 包含时间、价格等数据的DataFrame
            **kwargs: 其他绘图参数，包括：
                - title: 图表标题
                - width: 图表宽度
                - height: 图表高度
                - line_color: 分时线颜色
                - show_avg_line: 是否显示均线
                - avg_line_color: 均线颜色
                - show_volume: 是否显示成交量
                - volume_color: 成交量颜色
                - save_path: 图表保存路径，None表示不保存
        
        Returns:
            pyecharts.charts.Grid: 图表对象
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制分时图")
            return None
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 设置默认参数
        title = kwargs.get('title', f"{self._get_symbol_from_data(df)} 分时图")
        width = kwargs.get('width', 1200)
        height = kwargs.get('height', 600)
        line_color = kwargs.get('line_color', '#ef232a')  # 默认红色
        show_avg_line = kwargs.get('show_avg_line', True)
        avg_line_color = kwargs.get('avg_line_color', '#14b143')  # 默认绿色
        show_volume = kwargs.get('show_volume', True)
        volume_color = kwargs.get('volume_color', '#3370FF')  # 默认蓝色
        save_path = kwargs.get('save_path', None)
        
        # 准备数据
        time_points = []
        prices = []
        avg_prices = []
        volumes = []
        
        for idx, row in df.iterrows():
            # 格式化时间显示
            if hasattr(idx, 'hour'):
                time_point = f"{idx.hour:02d}:{idx.minute:02d}"
            else:
                # 如果索引不是datetime类型，尝试转换
                try:
                    dt = pd.to_datetime(idx)
                    time_point = f"{dt.hour:02d}:{dt.minute:02d}"
                except:
                    time_point = str(idx)
            
            time_points.append(time_point)
            prices.append(row['price'])
            
            if 'avg_price' in row:
                avg_prices.append(row['avg_price'])
            elif show_avg_line:
                avg_prices.append(None)  # 如果没有均价数据，用None填充
            
            if 'volume' in row:
                volumes.append(row['volume'])
            elif show_volume:
                volumes.append(0)  # 如果没有成交量数据，用0填充
        
        # 创建图表
        grid = Grid(
            init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px", theme=kwargs.get('theme', 'white'))
        )
        
        # 计算布局比例
        if show_volume:
            price_height = 0.7
            volume_height = 0.3
        else:
            price_height = 1.0
            volume_height = 0.0
        
        # 创建价格线图表
        price_chart = Line()
        price_chart.add_xaxis(xaxis_data=time_points)
        
        # 添加价格线
        price_chart.add_yaxis(
            series_name="价格",
            y_axis=prices,
            is_smooth=True,
            is_symbol_show=False,
            line_style_opts=opts.LineStyleOpts(color=line_color, width=2)
        )
        
        # 添加均价线
        if show_avg_line and avg_prices:
            price_chart.add_yaxis(
                series_name="均价",
                y_axis=avg_prices,
                is_smooth=True,
                is_symbol_show=False,
                line_style_opts=opts.LineStyleOpts(color=avg_line_color, width=1.5, type_="dashed")
            )
        
        # 设置全局配置
        price_chart.set_global_opts(
            title_opts=opts.TitleOpts(title=title, pos_top="5%"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(is_show=True, pos_top="10%"),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", xaxis_index=[0, 1]),
                opts.DataZoomOpts(type_="slider", xaxis_index=[0, 1], pos_top="95%")
            ],
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                axislabel_opts=opts.LabelOpts(formatter="{value:.2f}"),
                splitline_opts=opts.SplitLineOpts(is_show=True)
            )
        )
        
        # 添加价格图表到网格
        grid.add(price_chart, grid_opts=opts.GridOpts(
            pos_top="15%",
            pos_bottom=f"{volume_height * 100 + 15}%",
            height=f"{price_height * 100}%"
        ))
        
        # 添加成交量图表
        if show_volume and volumes:
            volume_chart = Bar()
            volume_chart.add_xaxis(xaxis_data=time_points)
            volume_chart.add_yaxis(
                series_name="成交量",
                y_axis=volumes,
                itemstyle_opts=opts.ItemStyleOpts(color=volume_color)
            )
            volume_chart.set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
                yaxis_opts=opts.AxisOpts(is_scale=True)
            )
            
            grid.add(volume_chart, grid_opts=opts.GridOpts(
                pos_top=f"{15 + price_height * 100}%",
                pos_bottom="15%",
                height=f"{volume_height * 100}%"
            ))
        
        # 保存图表
        if save_path:
            try:
                grid.render(save_path)
                logger.info(f"已将分时图保存到: {save_path}")
            except Exception as e:
                logger.error(f"保存分时图时出错: {e}")
        
        # 返回图表对象
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
        required_columns = ['price']
        for col in required_columns:
            if col not in df.columns:
                # 如果缺少必要的列，尝试从其他可能的列名中获取
                if col == 'price' and 'close' in df.columns:
                    df['price'] = df['close']
                elif col == 'price' and '收盘价' in df.columns:
                    df['price'] = df['收盘价']
                else:
                    raise ValueError(f"数据缺少必要的列: {col}")
        
        # 创建Grid布局
        grid = Grid(
            init_opts=opts.InitOpts(width="100%", height="100%", theme=theme)
        )
        
        # 添加主图（价格线和均价线）
        grid.add(
            main_chart, 
            grid_opts=opts.GridOpts(
                pos_left="10%", 
                pos_right="10%", 
                height="60%"
            )
        )
        
        # 添加成交量图
        if volume_chart is not None:
            grid.add(
                volume_chart, 
                grid_opts=opts.GridOpts(
                    pos_left="10%", 
                    pos_right="10%", 
                    pos_top="75%", 
                    height="16%"
                )
            )
        
        return df
    
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