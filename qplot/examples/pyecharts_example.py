"""
qplot pyecharts绘图后端示例

此示例展示如何使用qplot的pyecharts绘图后端来绘制交互式的K线图和分时图

使用前请确保已安装pyecharts: pip install qplot[pyecharts]
"""

import qplot
import logging
from datetime import datetime, timedelta

# 配置日志
def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

def example_1_pyecharts_kline():
    """
    示例1: 使用pyecharts后端绘制K线图
    """
    print("\n=== 示例1: 使用pyecharts后端绘制K线图 ===")
    
    try:
        # 设置默认绘图后端为pyecharts
        qplot.set_default_plot_backend('pyecharts')
        print("已设置默认绘图后端为pyecharts")
        
        # 绘制K线图，使用pyecharts后端
        stock_code = "600519"  # 与usage_example.py保持一致的股票代码
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        print(f"绘制{stock_code}从{start_date}到{end_date}的K线图")
        
        # 使用pyecharts后端绘制K线图
        # 注意：避免传递可能导致GridOpts错误的参数
        qplot.plot_kline(
            symbol=stock_code,
            start_date=start_date,
            end_date=end_date,
            title=f'{stock_code} 日K线图 - pyecharts',
            volume=True,  # 显示成交量
            indicators=['ma5', 'ma10', 'ma20']  # 显示均线指标
        )
        
        print("K线图绘制完成")
    except Exception as e:
        logger.error(f"绘制K线图时出错: {e}")

def example_2_specify_backend():
    """
    示例2: 在函数调用时指定pyecharts后端
    """
    print("\n=== 示例2: 在函数调用时指定pyecharts后端 ===")
    
    try:
        stock_code = "600519"  # 与usage_example.py保持一致的股票代码
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # 在调用时通过backend参数指定使用pyecharts后端
        # 注意：避免传递可能导致GridOpts错误的参数
        qplot.plot_kline(
            symbol=stock_code,
            start_date=start_date,
            end_date=end_date,
            backend='pyecharts',  # 直接在调用时指定后端
            title=f'{stock_code} 日K线图 - 调用时指定pyecharts',
            volume=True,
            indicators=['ma5', 'ma10', 'ma20']
        )
        
        print("K线图绘制完成")
    except Exception as e:
        logger.error(f"绘制K线图时出错: {e}")

def example_3_pyecharts_minute():
    """
    示例3: 使用pyecharts绘制分时图
    """
    print("\n=== 示例3: 使用pyecharts绘制分时图 ===")
    
    try:
        stock_code = "600519"  # 与usage_example.py保持一致的股票代码
        
        # 设置默认绘图后端为pyecharts
        qplot.set_default_plot_backend('pyecharts')
        
        # 绘制分时图
        print(f"绘制{stock_code}的分时图")
        
        # 注意：show_avg_line作为函数参数正确传递
        qplot.plot_minute_chart(
            symbol=stock_code,
            title=f'{stock_code} 分时图 - pyecharts',
            show_avg_line=True,  # 显示均价线
            show_volume=True  # 显示成交量
        )
        
        print("分时图绘制完成")
    except Exception as e:
        logger.error(f"绘制分时图时出错: {e}")

def example_4_save_to_html():
    """
    示例4: 保存pyecharts图表到HTML文件
    """
    print("\n=== 示例4: 保存pyecharts图表到HTML文件 ===")
    
    try:
        stock_code = "600519"  # 与usage_example.py保持一致的股票代码
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 绘制并保存K线图到HTML文件
        kline_save_path = f'./{stock_code}_kline_pyecharts.html'
        print(f"绘制并保存{stock_code}的K线图到: {kline_save_path}")
        
        # 注意：避免传递可能导致GridOpts错误的参数
        qplot.plot_kline(
            symbol=stock_code,
            start_date=start_date,
            end_date=end_date,
            backend='pyecharts',
            save_path=kline_save_path,
            volume=True
        )
        
        # 绘制并保存分时图到HTML文件
        minute_save_path = f'./{stock_code}_minute_pyecharts.html'
        print(f"绘制并保存{stock_code}的分时图到: {minute_save_path}")
        
        qplot.plot_minute_chart(
            symbol=stock_code,
            backend='pyecharts',
            save_path=minute_save_path,
            show_avg_line=True,
            show_volume=True
        )
        
        print("图表保存完成")
    except Exception as e:
        logger.error(f"保存图表时出错: {e}")

def main():
    """
    主函数，运行所有pyecharts后端示例
    """
    # 设置日志
    setup_logging()
    
    print("========== qplot pyecharts绘图后端示例 ==========")
    
    try:
        # 检查pyecharts是否可用
        try:
            import pyecharts
            print(f"已找到pyecharts库，版本: {pyecharts.__version__}")
        except ImportError:
            print("未找到pyecharts库，请先安装: pip install qplot[pyecharts]")
            return
        
        # 示例1: 使用pyecharts后端绘制K线图
        example_1_pyecharts_kline()
        
        # 示例2: 在函数调用时指定pyecharts后端
        example_2_specify_backend()
        
        # 示例3: 使用pyecharts绘制分时图
        example_3_pyecharts_minute()
        
        # 示例4: 保存pyecharts图表到HTML文件
        example_4_save_to_html()
        
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
    
    print("\n========== 所有示例运行完毕 ==========")

if __name__ == "__main__":
    main()