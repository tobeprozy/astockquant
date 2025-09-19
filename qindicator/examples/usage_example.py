"""
qindicator使用示例
"""

import pandas as pd
import qindicator
from datetime import datetime, timedelta

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_sample_data(days=30):
    """
    生成示例股票数据
    
    Args:
        days: 生成数据的天数
        
    Returns:
        DataFrame: 包含股票数据的DataFrame
    """
    # 生成日期序列
    dates = [datetime.now() - timedelta(days=i) for i in range(days-1, -1, -1)]
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    
    # 创建示例数据
    data = {
        'date': dates,
        'open': [100 + i*0.5 for i in range(days)],
        'high': [101 + i*0.5 + i%5 for i in range(days)],
        'low': [99 + i*0.5 - i%3 for i in range(days)],
        'close': [100 + i*0.5 + (i%2 - 0.5)*2 for i in range(days)],
        'volume': [10000 + i*1000 for i in range(days)]
    }
    
    return pd.DataFrame(data)


def example_1_basic_indicators():
    """
    示例1：计算基本技术指标
    """
    print("\n=== 示例1：计算基本技术指标 ===")
    
    # 初始化qindicator
    qindicator.init()
    
    # 生成示例数据
    data = generate_sample_data()
    print("原始数据前5行：")
    print(data.head())
    
    # 计算MA5和MA10
    ma_data = qindicator.calculate_ma(data, timeperiod=5)
    ma_data = qindicator.calculate_ma(ma_data, timeperiod=10)
    print("\n计算MA后的前10行数据：")
    print(ma_data[['date', 'close', 'MA5', 'MA10']].head(10))
    
    # 计算MACD
    macd_data = qindicator.calculate_macd(data)
    print("\n计算MACD后的前5行数据：")
    print(macd_data[['date', 'close', 'MACD', 'MACD_SIGNAL', 'MACD_HIST']].head())
    
    # 计算RSI
    rsi_data = qindicator.calculate_rsi(data)
    print("\n计算RSI后的前5行数据：")
    print(rsi_data[['date', 'close', 'RSI']].head())
    
    # 计算布林带
    bbands_data = qindicator.calculate_bbands(data)
    print("\n计算布林带后的前5行数据：")
    print(bbands_data[['date', 'close', 'BB_UPPER', 'BB_MIDDLE', 'BB_LOWER']].head())

    # 归一化波动幅度均值
    kline_data = qindicator.calculate_natr(data)
    print("\n计算归一化波动幅度均值后的前5行数据：")
    print(kline_data[['date', 'close', 'NATR']].head())
    


def example_2_multi_indicators():
    """
    示例2：一次计算多个指标
    """
    print("\n=== 示例2：一次计算多个指标 ===")
    
    # 初始化qindicator
    qindicator.init()
    
    # 生成示例数据
    data = generate_sample_data()
    
    # 一次计算多个指标
    indicator_data = data.copy()
    indicator_data = qindicator.calculate_ma(indicator_data, timeperiod=5)
    indicator_data = qindicator.calculate_ma(indicator_data, timeperiod=10)
    indicator_data = qindicator.calculate_ema(indicator_data, timeperiod=5)
    indicator_data = qindicator.calculate_macd(indicator_data)
    indicator_data = qindicator.calculate_rsi(indicator_data)
    indicator_data = qindicator.calculate_bbands(indicator_data)
    
    print("计算多个指标后的前10行数据：")
    columns = ['date', 'close', 'MA5', 'MA10', 'EMA5', 'MACD', 'RSI', 'BB_MIDDLE']
    print(indicator_data[columns].head(10))


def main():
    """
    运行所有示例
    """
    print("===== qindicator使用示例 =====")
    
    try:
        # 示例1：计算基本技术指标
        example_1_basic_indicators()
        
        # 示例2：一次计算多个指标
        example_2_multi_indicators()
        
        print("\n===== 所有示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()