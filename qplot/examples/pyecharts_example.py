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

# 示例1: 使用pyecharts后端绘制K线图
def example_1_pyecharts_kline():
    """使用pyecharts后端绘制K线图"""
    print("\n=== 示例1: 使用pyecharts后端绘制K线图 ===")
    
    try:
        # 设置默认绘图后端为pyecharts
        qplot.set_default_plot_backend('pyecharts')
        print("已设置默认绘图后端为pyecharts")
        
        # 绘制K线图，使用pyecharts后端
        symbol = '000001.SZ'  # 平安银行
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        print(f"绘制{symbol}从{start_date}到{end_date}的K线图")
        
        # 使用pyecharts后端绘制K线图
        qplot.plot_kline(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            title=f'{symbol} 日K线图 - pyecharts',
            # 可以添加pyecharts特有的参数
            width=1200,
            height=600,
            volume=True,  # 显示成交量
            indicators=['ma5', 'ma10', 'ma20']  # 显示均线指标
        )
        
        print("K线图绘制完成")
    except Exception as e:
        print(f"绘制K线图时出错: {e}")

# 示例2: 在函数调用时指定pyecharts后端
def example_2_specify_backend():
    """在函数调用时指定pyecharts后端"""
    print("\n=== 示例2: 在函数调用时指定pyecharts后端 ===")
    
    try:
        symbol = '000002.SZ'  # 万科A
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # 在调用时通过backend参数指定使用pyecharts后端
        qplot.plot_kline(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            backend='pyecharts',  # 直接在调用时指定后端
            title=f'{symbol} 日K线图 - 调用时指定pyecharts',
            volume=True,
            indicators=['ma5', 'ma10', 'ma20']
        )
        
        print("K线图绘制完成")
    except Exception as e:
        print(f"绘制K线图时出错: {e}")

# 示例3: 使用pyecharts绘制分时图
def example_3_pyecharts_minute():
    """使用pyecharts绘制分时图"""
    print("\n=== 示例3: 使用pyecharts绘制分时图 ===")
    
    try:
        symbol = '000001.SZ'  # 平安银行
        
        # 设置默认绘图后端为pyecharts
        qplot.set_default_plot_backend('pyecharts')
        
        # 绘制分时图
        print(f"绘制{symbol}的分时图")
        
        qplot.plot_minute_chart(
            symbol=symbol,
            title=f'{symbol} 分时图 - pyecharts',
            width=1200,
            height=500,
            show_avg_line=True,  # 显示均价线
            show_volume=True  # 显示成交量
        )
        
        print("分时图绘制完成")
    except Exception as e:
        print(f"绘制分时图时出错: {e}")

# 示例4: 保存pyecharts图表到HTML文件
def example_4_save_to_html():
    """保存pyecharts图表到HTML文件"""
    print("\n=== 示例4: 保存pyecharts图表到HTML文件 ===")
    
    try:
        symbol = '000001.SZ'  # 平安银行
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 绘制并保存K线图到HTML文件
        kline_save_path = f'./{symbol}_kline_pyecharts.html'
        print(f"绘制并保存{symbol}的K线图到: {kline_save_path}")
        
        qplot.plot_kline(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            backend='pyecharts',
            save_path=kline_save_path,
            volume=True
        )
        
        # 绘制并保存分时图到HTML文件
        minute_save_path = f'./{symbol}_minute_pyecharts.html'
        print(f"绘制并保存{symbol}的分时图到: {minute_save_path}")
        
        qplot.plot_minute_chart(
            symbol=symbol,
            backend='pyecharts',
            save_path=minute_save_path,
            show_avg_line=True,
            show_volume=True
        )
        
        print("图表保存完成")
    except Exception as e:
        print(f"保存图表时出错: {e}")

# 示例5: 恢复默认matplotlib后端
def example_5_restore_matplotlib():
    """恢复默认matplotlib后端"""
    print("\n=== 示例5: 恢复默认matplotlib后端 ===")
    
    try:
        # 恢复默认绘图后端为matplotlib
        qplot.set_default_plot_backend('matplotlib')
        print("已恢复默认绘图后端为matplotlib")
        
        symbol = '000001.SZ'  # 平安银行
        
        # 获取当前日期和30天前的日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 使用matplotlib后端绘制K线图
        qplot.plot_kline(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            title=f'{symbol} 日K线图 - matplotlib',
            volume=True
        )
        
        print("K线图绘制完成")
    except Exception as e:
        print(f"绘制K线图时出错: {e}")

# 主函数
def main():
    # 设置日志
    setup_logging()
    
    print("\nqplot pyecharts绘图后端示例")
    print("============================")
    
    try:
        # 检查pyecharts是否可用
        try:
            import pyecharts
            print(f"已找到pyecharts库，版本: {pyecharts.__version__}")
        except ImportError:
            print("未找到pyecharts库，请先安装: pip install qplot[pyecharts]")
            return
        
        # 运行各个示例
        example_1_pyecharts_kline()
        example_2_specify_backend()
        example_3_pyecharts_minute()
        example_4_save_to_html()
        example_5_restore_matplotlib()
        
    except Exception as e:
        print(f"运行示例时出错: {e}")

if __name__ == '__main__':
    main()