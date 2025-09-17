"""
日K线图绘图器
"""

from qplot.plotter import Plotter
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import logging

logger = logging.getLogger(__name__)

class CandlestickPlotter(Plotter):
    """
    日K线图绘图器
    使用mplfinance库绘制专业的K线图
    """
    
    def __init__(self):
        """
        初始化K线图绘图器
        """
        # 设置中文字体支持
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
        plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号
    
    def plot(self, data: pd.DataFrame, **kwargs) -> None:
        """
        绘制K线图
        
        Args:
            data: 包含开盘价、最高价、最低价、收盘价、成交量等数据的DataFrame
            **kwargs: 其他绘图参数，包括：
                - title: 图表标题
                - style: 图表风格
                - figsize: 图表尺寸
                - volume: 是否显示成交量
                - indicators: 要显示的指标列表，如['ma5', 'ma10', 'ma20']
                - save_path: 图表保存路径，None表示不保存
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制K线图")
            return
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 设置默认参数
        title = kwargs.get('title', f"{self._get_symbol_from_data(df)} 日K线图")
        style = kwargs.get('style', 'charles')
        figsize = kwargs.get('figsize', (14, 8))
        volume = kwargs.get('volume', True)
        indicators = kwargs.get('indicators', ['ma5', 'ma10', 'ma20'])
        save_path = kwargs.get('save_path', None)
        
        # 准备绘图参数
        plot_kwargs = {
            'type': 'candle',
            'style': style,
            'title': title,
            'figsize': figsize,
            'volume': volume,
            'ylabel': '价格',
            'ylabel_lower': '成交量',
            'show_nontrading': False
        }
        
        # 准备添加的指标
        addplot = []
        
        # 添加均线指标
        if indicators:
            ma_colors = {'ma5': 'blue', 'ma10': 'orange', 'ma20': 'green', 'ma60': 'red'}
            
            for ma in indicators:
                if ma.startswith('ma'):
                    try:
                        period = int(ma[2:])
                        df[ma] = df['close'].rolling(window=period).mean()
                        color = ma_colors.get(ma, 'gray')
                        ap = mpf.make_addplot(df[ma], color=color, width=1)
                        addplot.append(ap)
                    except Exception as e:
                        logger.warning(f"添加均线指标{ma}时出错: {e}")
        
        # 绘制K线图
        try:
            if addplot:
                plot_kwargs['addplot'] = addplot
            
            mpf.plot(df, **plot_kwargs)
            
            # 保存图表
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"已将K线图保存到: {save_path}")
            
            plt.show(block=kwargs.get('block', True))
        except Exception as e:
            logger.error(f"绘制K线图时出错: {e}")
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理K线图数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 复制数据以避免修改原始数据
        df = data.copy()
        
        # 确保列名符合mplfinance的要求
        required_columns = ['open', 'high', 'low', 'close']
        
        # 检查并转换列名
        column_mapping = {
            '开盘价': 'open',
            '最高价': 'high', 
            '最低价': 'low',
            '收盘价': 'close',
            '成交量': 'volume'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 检查是否包含必需的列
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"缺少必需的列: {col}")
        
        # 确保索引是日期时间类型
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                else:
                    # 尝试将索引转换为日期时间
                    df.index = pd.to_datetime(df.index)
            except Exception as e:
                logger.warning(f"设置日期索引时出错: {e}")
        
        # 排序数据
        df = df.sort_index()
        
        # 确保数值列是数值类型
        numeric_columns = ['open', 'high', 'low', 'close']
        if 'volume' in df.columns:
            numeric_columns.append('volume')
            
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 删除包含NaN的行
        df = df.dropna(subset=required_columns)
        
        return df
    
    def _get_symbol_from_data(self, data: pd.DataFrame) -> str:
        """
        从数据中获取证券代码
        
        Args:
            data: 数据
        
        Returns:
            str: 证券代码或默认字符串
        """
        # 这里简化处理，实际应用中可能需要从数据或其他地方获取证券代码
        return "未知股票"
    
    def plot_with_indicators(self, data: pd.DataFrame, indicators: list = None, **kwargs) -> None:
        """
        绘制带有技术指标的K线图
        
        Args:
            data: K线数据
            indicators: 要显示的指标列表
            **kwargs: 其他绘图参数
        """
        if indicators is None:
            indicators = ['ma5', 'ma10', 'ma20']
        
        kwargs['indicators'] = indicators
        self.plot(data, **kwargs)
    
    def plot_realtime(self, data_manager, update_interval: int = 60, **kwargs) -> None:
        """
        绘制实时更新的K线图
        
        Args:
            data_manager: 数据管理器实例
            update_interval: 更新间隔（秒）
            **kwargs: 其他绘图参数
        """
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        
        # 创建图形和坐标轴
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (14, 8)))
        
        def update(frame):
            """更新函数，用于动画"""
            try:
                # 清除当前图形
                ax.clear()
                
                # 获取最新数据
                data = data_manager.get_data()
                
                if data is not None and not data.empty:
                    # 预处理数据
                    df = self._preprocess_data(data)
                    
                    # 绘制K线图
                    mpf.plot(df, type='candle', ax=ax, style=kwargs.get('style', 'charles'))
                    
                    # 设置标题
                    title = kwargs.get('title', f"{self._get_symbol_from_data(df)} 实时K线图")
                    ax.set_title(f"{title} (更新时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')})")
            except Exception as e:
                logger.error(f"更新实时K线图时出错: {e}")
        
        # 创建动画
        ani = FuncAnimation(fig, update, interval=update_interval * 1000)  # 转换为毫秒
        
        # 显示图形
        plt.tight_layout()
        plt.show()