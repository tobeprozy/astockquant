"""
qplot插件使用示例
展示如何使用qplot绘制日K线图和分时图
"""

import qplot
import qdata
import pandas as pd
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_1_kline_plot():
    """
    示例1: 绘制日K线图
    """
    print("\n=== 示例1: 绘制日K线图 ===")
    
    try:
        # 使用qdata获取股票的日线数据
        # 这里使用贵州茅台(600519)的日线数据作为示例
        stock_code = "600519"
        
        # 使用生成的示例数据（实际应用中可以使用真实数据）
        print(f"正在生成{stock_code}的示例日线数据...")
        df = generate_sample_daily_data(stock_code)
        
        if df is not None and not df.empty:
            print(f"成功生成数据，数据量: {len(df)}行")
            print("数据前5行:\n", df.head())
            
            # 验证数据格式
            if ('date' in df.columns and 'open' in df.columns and 'high' in df.columns and 
                'low' in df.columns and 'close' in df.columns):
                print("数据格式验证通过")
            else:
                print("警告：数据缺少必要的列")
                print("当前列名:", df.columns.tolist())
            
            # 创建数据管理器
            data_manager = qplot.DataManager(symbol=stock_code, data_type='daily')
            data_manager.update_data(df)
            
            # 使用qplot绘制K线图
            print("正在绘制K线图...")
            qplot.plot_kline(
                stock_code,
                title=f"{stock_code} 日K线图",
                style='charles',
                volume=True,
                indicators=['ma5', 'ma10', 'ma20'],
                figsize=(14, 8)
            )
        else:
            print("未能生成数据或数据为空")
    except Exception as e:
        logger.error(f"绘制K线图时出错: {e}")

def example_2_minute_plot():
    """
    示例2: 绘制分时图
    """
    print("\n=== 示例2: 绘制分时图 ===")
    
    try:
        # 使用qdata获取股票的分钟数据
        stock_code = "600519"
        
        print(f"正在获取{stock_code}的分时数据...")
        # 注意：这里为了演示，我们使用生成的模拟数据，因为实际的分钟数据可能需要特殊权限或付费服务
        df = generate_sample_minute_data(stock_code)
        
        if df is not None and not df.empty:
            print(f"成功获取数据，数据量: {len(df)}行")
            print("数据前5行:\n", df.head())
            
            # 使用qplot绘制分时图
            print("正在绘制分时图...")
            qplot.plot_minute_chart(
                df,
                title=f"{stock_code} 分时图",
                line_color='blue',
                show_avg_line=True,
                avg_line_color='orange',
                figsize=(14, 6)
            )
        else:
            print("未能获取数据或数据为空")
    except Exception as e:
        logger.error(f"绘制分时图时出错: {e}")

def example_3_realtime_kline():
    """
    示例3: 绘制实时更新的K线图
    """
    print("\n=== 示例3: 绘制实时更新的K线图 ===")
    print("注意：此示例使用模拟数据进行实时更新演示")
    
    try:
        # 创建数据管理器
        stock_code = "600519"
        data_manager = qplot.DataManager(stock_code=stock_code, data_type='daily')
        
        # 生成初始数据
        initial_data = generate_sample_daily_data(stock_code)
        data_manager.update_data(initial_data)
        
        print("正在启动实时K线图...")
        print("按Ctrl+C或关闭窗口以停止实时更新")
        
        # 启动实时更新线程
        data_manager.start_realtime_updates(interval=30)  # 每30秒更新一次
        
        # 绘制实时K线图
        qplot.plot_kline_realtime(data_manager, update_interval=30)
    except KeyboardInterrupt:
        print("\n已停止实时K线图")
    except Exception as e:
        logger.error(f"绘制实时K线图时出错: {e}")
    finally:
        # 确保停止数据更新线程
        data_manager.stop_realtime_updates()

def example_4_realtime_minute_chart():
    """
    示例4: 绘制实时更新的分时图
    """
    print("\n=== 示例4: 绘制实时更新的分时图 ===")
    print("注意：此示例使用模拟数据进行实时更新演示")
    
    try:
        # 创建数据管理器
        stock_code = "600519"
        data_manager = qplot.DataManager(stock_code=stock_code, data_type='minute')
        
        # 生成初始数据
        initial_data = generate_sample_minute_data(stock_code)
        data_manager.update_data(initial_data)
        
        print("正在启动实时分时图...")
        print("按Ctrl+C或关闭窗口以停止实时更新")
        
        # 启动实时更新线程
        data_manager.start_realtime_updates(interval=10)  # 每10秒更新一次
        
        # 绘制实时分时图
        qplot.plot_minute_chart_realtime(data_manager, update_interval=10)
    except KeyboardInterrupt:
        print("\n已停止实时分时图")
    except Exception as e:
        logger.error(f"绘制实时分时图时出错: {e}")
    finally:
        # 确保停止数据更新线程
        data_manager.stop_realtime_updates()

def generate_sample_daily_data(stock_code: str) -> pd.DataFrame:
    """
    生成示例日线数据
    实际应用中应使用qdata.get_daily_data获取真实数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        pd.DataFrame: 示例日线数据
    """
    # 生成日期序列
    dates = pd.date_range(end=datetime.now(), periods=60)
    
    # 生成随机价格数据
    base_price = 1700.0
    price_changes = pd.Series(0.0, index=dates)
    
    # 生成随机波动
    import numpy as np
    np.random.seed(42)  # 设置随机种子以确保结果可复现
    
    for i in range(1, len(dates)):
        # 生成-1%到+1%之间的随机变化
        change_percent = np.random.uniform(-1, 1) / 100
        price_changes.iloc[i] = price_changes.iloc[i-1] * (1 + change_percent)
    
    # 计算开盘价、最高价、最低价、收盘价
    close_prices = base_price + price_changes
    open_prices = close_prices.shift(1).fillna(base_price)  # 开盘价基于前一天的收盘价
    
    # 生成最高价和最低价
    high_prices = open_prices + np.random.uniform(0, 50, len(dates))
    low_prices = open_prices - np.random.uniform(0, 50, len(dates))
    
    # 确保最高价不低于收盘价，最低价不高于收盘价
    high_prices = np.maximum(high_prices, close_prices)
    low_prices = np.minimum(low_prices, close_prices)
    
    # 生成成交量
    volumes = np.random.randint(1000000, 10000000, len(dates))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    
    return df

def generate_sample_minute_data(stock_code: str) -> pd.DataFrame:
    """
    生成示例分时数据
    实际应用中应使用qdata.get_minute_data获取真实数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        pd.DataFrame: 示例分时数据
    """
    # 创建当天的时间序列（9:30-15:00）
    today = datetime.now().date()
    start_time = datetime.combine(today, datetime.min.time()).replace(hour=9, minute=30)
    end_time = datetime.combine(today, datetime.min.time()).replace(hour=15, minute=0)
    
    # 生成1分钟间隔的时间点
    times = pd.date_range(start=start_time, end=end_time, freq='1T')
    
    # 排除午休时间（11:30-13:00）
    times = times[(times.hour < 11) | 
                  ((times.hour == 11) & (times.minute <= 30)) | 
                  (times.hour > 13) | 
                  ((times.hour == 13) & (times.minute >= 0))]
    
    # 生成随机价格数据
    base_price = 1750.0
    import numpy as np
    np.random.seed(42)  # 设置随机种子以确保结果可复现
    
    # 生成随机波动
    price_changes = np.random.normal(0, 0.5, len(times))
    cumulative_changes = np.cumsum(price_changes)
    prices = base_price + cumulative_changes
    
    # 计算均价（这里简化处理）
    avg_prices = pd.Series(prices).rolling(window=5, min_periods=1).mean().values
    
    # 生成成交量
    volumes = np.random.randint(100000, 1000000, len(times))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'time': times,
        'price': prices,
        'avg_price': avg_prices,
        'volume': volumes
    })
    
    return df

def main():
    """
    主函数，运行所有示例
    """
    print("========== qplot插件使用示例 ==========")
    
    # 示例1: 绘制日K线图
    example_1_kline_plot()
    
    # 示例2: 绘制分时图
    example_2_minute_plot()
    
    # 示例3: 绘制实时更新的K线图（可选运行）
    # 取消下面的注释以运行实时K线图示例
    # example_3_realtime_kline()
    
    # 示例4: 绘制实时更新的分时图（可选运行）
    # 取消下面的注释以运行实时分时图示例
    # example_4_realtime_minute_chart()
    
    print("\n========== 所有示例运行完毕 ==========")

if __name__ == "__main__":
    main()