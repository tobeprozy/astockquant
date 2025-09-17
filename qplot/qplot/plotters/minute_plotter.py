"""
分时图绘图器
"""

from qplot.plotter import Plotter
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import threading
import time

logger = logging.getLogger(__name__)

class MinutePlotter(Plotter):
    """
    分时图绘图器
    用于绘制股票的分时图，支持实时更新
    """
    
    def __init__(self):
        """
        初始化分时图绘图器
        """
        # 设置中文字体支持
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
        plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号
        
        # 实时更新相关属性
        self._update_thread = None
        self._stop_event = threading.Event()
        self._data_manager = None
    
    def plot(self, data: pd.DataFrame, **kwargs) -> None:
        """
        绘制分时图
        
        Args:
            data: 包含时间、价格等数据的DataFrame
            **kwargs: 其他绘图参数，包括：
                - title: 图表标题
                - figsize: 图表尺寸
                - line_color: 分时线颜色
                - save_path: 图表保存路径，None表示不保存
                - show_avg_line: 是否显示均线
                - avg_line_color: 均线颜色
        """
        if not self._validate_data(data):
            logger.warning("无效的数据，无法绘制分时图")
            return
        
        # 预处理数据
        df = self._preprocess_data(data)
        
        # 设置默认参数
        title = kwargs.get('title', f"{self._get_symbol_from_data(df)} 分时图")
        figsize = kwargs.get('figsize', (14, 6))
        line_color = kwargs.get('line_color', 'blue')
        save_path = kwargs.get('save_path', None)
        show_avg_line = kwargs.get('show_avg_line', True)
        avg_line_color = kwargs.get('avg_line_color', 'orange')
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制分时线
        ax.plot(df.index, df['price'], color=line_color, linewidth=2, label='价格')
        
        # 绘制均线
        if show_avg_line and 'avg_price' in df.columns:
            ax.plot(df.index, df['avg_price'], color=avg_line_color, linewidth=1.5, linestyle='--', label='均价')
        
        # 设置坐标轴格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 设置标题和标签
        ax.set_title(title)
        ax.set_ylabel('价格')
        ax.set_xlabel('时间')
        
        # 添加图例
        if show_avg_line and 'avg_price' in df.columns:
            ax.legend()
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"已将分时图保存到: {save_path}")
        
        # 显示图表
        plt.show(block=kwargs.get('block', True))
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理分时图数据
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 复制数据以避免修改原始数据
        df = data.copy()
        
        # 检查并转换列名
        column_mapping = {
            '时间': 'time',
            '价格': 'price',
            '均价': 'avg_price',
            '成交量': 'volume'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 确保包含必需的列
        if 'price' not in df.columns:
            raise ValueError("缺少必需的'price'列")
        
        # 确保时间列是日期时间类型
        if 'time' in df.columns:
            try:
                # 如果时间列只有时间部分，添加当前日期
                if not isinstance(df['time'].iloc[0], pd.Timestamp):
                    # 尝试将字符串转换为时间
                    if ':' in str(df['time'].iloc[0]):
                        # 假设时间格式为HH:MM或HH:MM:SS
                        current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                        df['time'] = pd.to_datetime(current_date + ' ' + df['time'].astype(str))
                    else:
                        df['time'] = pd.to_datetime(df['time'])
                df = df.set_index('time')
            except Exception as e:
                logger.warning(f"设置时间索引时出错: {e}")
        elif not isinstance(df.index, pd.DatetimeIndex):
            try:
                # 尝试将索引转换为日期时间
                df.index = pd.to_datetime(df.index)
            except Exception as e:
                logger.warning(f"将索引转换为日期时间时出错: {e}")
        
        # 排序数据
        df = df.sort_index()
        
        # 确保price列是数值类型
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # 如果没有均价列，计算均价
        if 'avg_price' not in df.columns and 'volume' in df.columns:
            try:
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
                # 简单计算均价（实际应该是加权平均）
                df['avg_price'] = df['price'].rolling(window=5, min_periods=1).mean()
            except Exception as e:
                logger.warning(f"计算均价时出错: {e}")
        
        # 删除包含NaN的行
        df = df.dropna(subset=['price'])
        
        return df
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """
        验证数据是否有效
        
        Args:
            data: 要验证的数据
        
        Returns:
            bool: 数据是否有效
        """
        if data is None or data.empty:
            logger.warning("数据为空")
            return False
        
        # 检查是否包含价格相关列
        price_columns = ['price', '价格', '收盘价', 'close']
        has_price_column = any(col in data.columns for col in price_columns)
        
        # 检查是否包含时间相关列
        time_columns = ['time', '时间', 'date', '日期']
        has_time_column = any(col in data.columns for col in time_columns) or isinstance(data.index, pd.DatetimeIndex)
        
        if not has_price_column:
            logger.warning(f"数据中不包含价格列，可用的列名: {price_columns}")
            return False
        
        if not has_time_column:
            logger.warning(f"数据中不包含时间列，可用的列名: {time_columns}")
            return False
        
        return True
    
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
    
    def start_realtime_plot(self, data_manager, update_interval: int = 10, **kwargs) -> None:
        """
        启动实时分时图绘制
        使用双线程：一个线程更新数据，一个线程更新图表
        
        Args:
            data_manager: 数据管理器实例，用于获取最新数据
            update_interval: 更新间隔（秒）
            **kwargs: 其他绘图参数
        """
        self._data_manager = data_manager
        self._stop_event.clear()
        
        # 创建图形
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (14, 6)))
        
        def update_plot():
            """更新图表函数"""
            while not self._stop_event.is_set():
                try:
                    # 获取最新数据
                    data = data_manager.get_data()
                    
                    if data is not None and not data.empty:
                        # 预处理数据
                        df = self._preprocess_data(data)
                        
                        # 清除当前图形
                        ax.clear()
                        
                        # 绘制分时线
                        line_color = kwargs.get('line_color', 'blue')
                        ax.plot(df.index, df['price'], color=line_color, linewidth=2, label='价格')
                        
                        # 绘制均线
                        show_avg_line = kwargs.get('show_avg_line', True)
                        if show_avg_line and 'avg_price' in df.columns:
                            avg_line_color = kwargs.get('avg_line_color', 'orange')
                            ax.plot(df.index, df['avg_price'], color=avg_line_color, linewidth=1.5, linestyle='--', label='均价')
                        
                        # 设置坐标轴格式
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                        plt.xticks(rotation=45)
                        
                        # 添加网格线
                        ax.grid(True, linestyle='--', alpha=0.7)
                        
                        # 设置标题和标签
                        title = kwargs.get('title', f"{self._get_symbol_from_data(df)} 实时分时图")
                        ax.set_title(f"{title} (更新时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')})")
                        ax.set_ylabel('价格')
                        ax.set_xlabel('时间')
                        
                        # 添加图例
                        if show_avg_line and 'avg_price' in df.columns:
                            ax.legend()
                        
                        # 调整布局
                        plt.tight_layout()
                        
                        # 更新图形
                        plt.draw()
                        plt.pause(0.1)  # 短暂暂停以允许图形更新
                except Exception as e:
                    logger.error(f"更新实时分时图时出错: {e}")
                    plt.pause(0.1)
                
                # 等待下一次更新
                time.sleep(update_interval)
        
        # 创建并启动绘图线程
        self._plot_thread = threading.Thread(target=update_plot)
        self._plot_thread.daemon = True  # 设置为守护线程，主线程结束时自动结束
        self._plot_thread.start()
        
        # 在主线程中显示图形
        plt.show()
        
    def stop_realtime_plot(self):
        """
        停止实时分时图绘制
        """
        self._stop_event.set()
        if hasattr(self, '_plot_thread') and self._plot_thread.is_alive():
            self._plot_thread.join(timeout=2.0)  # 等待线程结束，最多等待2秒
        plt.close('all')
        logger.info("已停止实时分时图绘制")