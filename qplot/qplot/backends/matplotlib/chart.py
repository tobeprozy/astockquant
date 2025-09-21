"""
基于matplotlib的图表实现
"""

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from qplot.core.plotter import Chart
import os

class MatplotlibChart(Chart):
    """基于matplotlib的图表实现"""
    
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
        self.fig, self.ax = plt.subplots(figsize=kwargs.get('figsize', (12, 8)))
        self.is_realtime = kwargs.get('is_realtime', False)
        self.data_manager = data_manager
        self.data = data  # 存储直接传入的数据
        self.kwargs = kwargs
        
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
        
        plt.tight_layout()
        return self
    
    def _plot_kline(self, data):
        """绘制K线图"""
        # 设置中文显示
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
        
        # 确保数据格式正确
        if not isinstance(data, pd.DataFrame):
            raise TypeError("数据必须是pandas DataFrame类型")
        
        # 处理数据格式
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
        
        # 设置绘图参数（在External Axes Mode中有效的参数）
        kwargs = {
            'type': 'candle',
            'style': 'charles',
            'ylabel': '价格',
        }
        
        # 处理标题（在External Axes Mode中需要单独设置）
        title = self.kwargs.get('title', 'K线图')
        if title and hasattr(self, 'fig') and self.fig:
            self.fig.suptitle(title, fontsize=16)
        
        # 添加技术指标
        ma = self.kwargs.get('ma', [])
        if ma and isinstance(ma, list):
            kwargs['mav'] = ma
        
        # 处理自定义颜色
        if 'colors' in self.kwargs:
            colors = self.kwargs['colors']
            if 'up_color' in colors or 'down_color' in colors:
                # 自定义蜡烛图颜色
                up_color = colors.get('up_color', 'red')
                down_color = colors.get('down_color', 'green')
                my_style = mpf.make_mpf_style(
                    base_mpf_style='charles',
                    marketcolors=mpf.make_marketcolors(
                        up=up_color,
                        down=down_color
                    )
                )
                kwargs['style'] = my_style
        
        # 检查是否显示成交量
        show_volume = self.kwargs.get('volume', False) or self.kwargs.get('show_volume', False)
        
        # 绘制K线图，根据是否显示成交量选择不同的绘图方式
        if show_volume and 'volume' in data.columns:
            # 如果要显示成交量，创建一个包含两个子图的布局
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.kwargs.get('figsize', (12, 10)), gridspec_kw={'height_ratios': [3, 1]})
            
            # 绘制K线图到第一个子图
            mpf.plot(data, **kwargs, ax=ax1)
            
            # 绘制成交量到第二个子图
            ax2.bar(data.index, data['volume'], color=['red' if data['close'].iloc[i] >= data['open'].iloc[i] else 'green' for i in range(len(data))])
            ax2.set_ylabel('成交量')
            ax2.grid(True, alpha=0.3)
            
            # 设置为图表的fig和ax属性
            self.fig = fig
            self.ax = ax1
        else:
            # 只绘制K线图
            mpf.plot(data, **kwargs, ax=self.ax)
    
    def _plot_minute(self, data):
        """绘制分时图"""
        # 设置中文显示
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
        
        # 创建双Y轴
        ax1 = self.ax
        ax2 = ax1.twinx()
        
        # 尝试从不同的列名中提取数据
        rename_map = {
            'price': 'close', '成交价': 'close',
            'avg_price': 'avg_price', '均价': 'avg_price',
            'volume': 'volume', '成交量': 'volume'
        }
        data = data.rename(columns=rename_map)
        
        # 绘制价格线和均价线
        ax1.plot(data.index, data['close'], 'b-', label='价格')
        if 'avg_price' in data.columns:
            ax1.plot(data.index, data['avg_price'], 'g-', label='均价')
        
        # 绘制成交量柱状图
        if self.kwargs.get('volume', False) and 'volume' in data.columns:
            ax2.bar(data.index, data['volume'], alpha=0.3, color='r', label='成交量')
        
        # 设置标签和标题
        ax1.set_xlabel('时间')
        ax1.set_ylabel('价格')
        if 'volume' in data.columns:
            ax2.set_ylabel('成交量')
        ax1.set_title(self.kwargs.get('title', '分时图'))
        
        # 添加图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # 格式化X轴日期标签
        plt.xticks(rotation=45)
    
    def update(self):
        """更新图表数据"""
        if not self.is_realtime:
            raise RuntimeError("非实时图表不支持更新")
        
        # 清除当前图表
        self.ax.clear()
        
        # 重新绘制
        self.plot()
        
        # 如果是实时模式，更新显示
        if hasattr(self, 'plt'):
            plt.pause(0.1)
    
    def save(self, file_path='chart.png', **kwargs):
        """保存图表到文件
        
        Args:
            file_path: 保存的文件路径，默认是'chart.png'
            **kwargs: 其他保存参数
        """
        if self.fig is None:
            raise RuntimeError("图表尚未绘制")
        
        # 检查文件格式
        file_ext = file_path.split('.')[-1].lower()
        supported_formats = ['eps', 'jpeg', 'jpg', 'pdf', 'pgf', 'png', 'ps', 'raw', 'rgba', 'svg', 'svgz', 'tif', 'tiff', 'webp']
        
        if file_ext == 'html':
            # 警告用户Matplotlib不支持直接保存为HTML格式
            import warnings
            warnings.warn("Matplotlib不支持直接保存为HTML格式。请使用png、pdf、svg等格式。")
            # 自动将扩展名改为png
            new_file_path = file_path.rsplit('.', 1)[0] + '.png'
            warnings.warn(f"已将文件保存为: {new_file_path}")
            file_path = new_file_path
        elif file_ext not in supported_formats:
            # 警告用户使用了不支持的格式
            import warnings
            warnings.warn(f"不支持的文件格式 '{file_ext}'。请使用以下格式之一: {', '.join(supported_formats)}")
            # 自动将扩展名改为png
            new_file_path = file_path.rsplit('.', 1)[0] + '.png'
            warnings.warn(f"已将文件保存为: {new_file_path}")
            file_path = new_file_path
        
        # 保存图表
        self.fig.savefig(file_path, **kwargs)
        return self
    
    def show(self):
        """显示图表"""
        plt.show()
        return self