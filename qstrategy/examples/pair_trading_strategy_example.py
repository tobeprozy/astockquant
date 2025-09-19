"""
配对交易策略使用示例
展示如何使用qstrategy中的配对交易策略进行回测和信号生成
"""

import pandas as pd
import qstrategy
from datetime import datetime, timedelta

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_pair_data(days=100):
    """
    生成示例配对股票数据
    
    Args:
        days: 生成数据的天数
        
    Returns:
        tuple: 包含两只相关股票数据的DataFrame元组
    """
    # 生成日期序列
    dates = [datetime.now() - timedelta(days=i) for i in range(days-1, -1, -1)]
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    
    # 创建示例数据 - 股票A
    data_a = {
        'date': dates,
        'open': [100 + i*0.5 for i in range(days)],
        'high': [101 + i*0.5 + i%5 for i in range(days)],
        'low': [99 + i*0.5 - i%3 for i in range(days)],
        'close': [100 + i*0.5 + (i%2 - 0.5)*2 for i in range(days)],
        'volume': [10000 + i*1000 for i in range(days)]
    }
    
    # 创建示例数据 - 股票B (与股票A相关但有一些差异)
    data_b = {
        'date': dates,
        'open': [120 + i*0.55 for i in range(days)],
        'high': [121 + i*0.55 + i%5 for i in range(days)],
        'low': [119 + i*0.55 - i%3 for i in range(days)],
        'close': [120 + i*0.55 + (i%2 - 0.5)*1.8 + (i%7 - 3.5)*0.3 for i in range(days)],
        'volume': [12000 + i*1200 for i in range(days)]
    }
    
    df_a = pd.DataFrame(data_a)
    df_a['date'] = pd.to_datetime(df_a['date'])
    df_a.set_index('date', inplace=True)
    
    df_b = pd.DataFrame(data_b)
    df_b['date'] = pd.to_datetime(df_b['date'])
    df_b.set_index('date', inplace=True)
    
    return df_a, df_b

def main():
    """
    运行配对交易策略示例
    """
    print("===== 配对交易策略使用示例 =====")
    
    try:
        # 初始化qstrategy
        qstrategy.init()
        
        # 生成示例配对数据
        data_a, data_b = generate_sample_pair_data()
        print("股票A数据前5行：")
        print(data_a.head())
        print("\n股票B数据前5行：")
        print(data_b.head())
        
        # 创建并初始化策略
        # 参数说明：
        # window: 计算配对关系的窗口大小
        # zscore_threshold: Z-score阈值，超过时产生交易信号
        strategy = qstrategy.get_strategy('pair_trading', window=30, zscore_threshold=2.0, printlog=True)
        
        # 注意：配对交易需要两只股票的数据，作为元组传入
        strategy.init_strategy((data_a, data_b))
        
        # 生成交易信号
        signals = strategy.generate_signals()
        print(f"\n生成的买入信号数量: {len(signals['buy_signals'])}")
        print(f"生成的卖出信号数量: {len(signals['sell_signals'])}")
        
        # 显示部分信号
        if len(signals['buy_signals']) > 0:
            print("\n部分买入信号日期：")
            print(signals['buy_signals'][:3])
        
        # 执行交易
        results = strategy.execute_trade(signals)
        print(f"\n交易执行结果：")
        print(f"总买入次数: {results['total_buys']}")
        print(f"总卖出次数: {results['total_sells']}")
        
        print("\n===== 配对交易策略示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()