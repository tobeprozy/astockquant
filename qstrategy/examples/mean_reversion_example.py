"""
均值回归策略使用示例
展示如何使用qstrategy中的均值回归策略进行回测和信号生成
"""

import pandas as pd
import qstrategy
from datetime import datetime, timedelta

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_data(days=100):
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
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

def main():
    """
    运行均值回归策略示例
    """
    print("===== 均值回归策略使用示例 =====")
    
    try:
        # 初始化qstrategy
        qstrategy.init()
        
        # 生成示例数据
        data = generate_sample_data()
        print("原始数据前5行：")
        print(data.head())
        
        # 创建并初始化策略
        # 参数说明：
        # window: 计算均值和标准差的窗口大小
        # std_dev_threshold: 标准差阈值，价格低于均值多少倍标准差时买入
        strategy = qstrategy.get_strategy('mean_reversion', window=10, std_dev_threshold=1.5, printlog=True)
        strategy.init_strategy(data)
        
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
        
        print("\n===== 均值回归策略示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()