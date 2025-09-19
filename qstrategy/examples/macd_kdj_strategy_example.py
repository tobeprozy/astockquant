"""
MACD+KDJ策略使用示例
展示如何使用qstrategy中的MACD+KDJ策略进行回测和信号生成
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
    
    # 创建示例数据，包含一些波动以更好地展示指标
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
    运行MACD+KDJ策略示例
    """
    print("===== MACD+KDJ策略使用示例 =====")
    
    try:
        # 初始化qstrategy
        qstrategy.init()
        
        # 生成示例数据
        data = generate_sample_data()
        print("原始数据前5行：")
        print(data.head())
        
        # 创建并初始化策略
        # 参数说明：
        # macd_fast_period: MACD快线周期
        # macd_slow_period: MACD慢线周期
        # macd_signal_period: MACD信号线周期
        # kdj_period: KDJ周期
        # kdj_slowing_period: KDJ平滑周期
        strategy = qstrategy.get_strategy(
            'macd_kdj', 
            macd_fast_period=12, 
            macd_slow_period=26, 
            macd_signal_period=9, 
            kdj_period=9, 
            kdj_slowing_period=3,
            printlog=True
        )
        strategy.init_strategy(data)
        
        # 生成交易信号
        signals = strategy.generate_signals()
        print(f"\n生成的买入信号数量: {len(signals['buy_signals'])}")
        print(f"生成的卖出信号数量: {len(signals['sell_signals'])}")
        
        # 显示部分信号
        if len(signals['buy_signals']) > 0:
            print("\n部分买入信号日期：")
            print(signals['buy_signals'][:3])
        
        if len(signals['sell_signals']) > 0:
            print("\n部分卖出信号日期：")
            print(signals['sell_signals'][:3])
        
        # 执行交易
        results = strategy.execute_trade(signals)
        print(f"\n交易执行结果：")
        print(f"总买入次数: {results['total_buys']}")
        print(f"总卖出次数: {results['total_sells']}")
        
        # 打印一些交易详情
        if results['transactions']:
            print("\n部分交易详情：")
            for i, tx in enumerate(results['transactions'][:3]):
                print(f"交易{i+1}: {tx['date']} - {tx['type']} @ {tx['price']:.2f} - {tx['reason']}")
        
        print("\n===== MACD+KDJ策略示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()