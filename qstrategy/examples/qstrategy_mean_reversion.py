"""
均值回归策略使用示例
展示如何使用qstrategy中的均值回归策略进行回测和信号生成

本示例基于qstrategy的新架构（core和backends模块）
"""

import pandas as pd
from qstrategy.backends.mean_reversion import MeanReversionStrategy
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
        # 生成示例数据
        data = generate_sample_data()
        print("原始数据前5行：")
        print(data.head())
        
        # 创建策略实例
        strategy = MeanReversionStrategy(
            lookback_period=10, 
            std_dev_threshold=1.5, 
            printlog=True
        )
        
        # 初始化策略数据
        strategy.init_data(data)
        
        # 生成交易信号
        signals = strategy.generate_signals()
        print(f"\n生成的买入信号数量: {len(signals['buy_signals'])}")
        print(f"生成的卖出信号数量: {len(signals['sell_signals'])}")
        
        # 显示部分信号
        if len(signals['buy_signals']) > 0:
            print("\n部分买入信号日期：")
            print(signals['buy_signals'][:3])
        
        # 执行交易
        results = strategy.execute_trade()
        print(f"\n交易执行结果：")
        print(f"总交易次数: {results['num_trades']}")
        print(f"总利润: {results['total_profit']:.2f}")
        print(f"最终持仓: {'有持仓' if results['final_position'] > 0 else '空仓'}")
        
        # 策略评估
        if hasattr(strategy, 'evaluate_performance'):
            performance = strategy.evaluate_performance(results)
            print(f"\n策略性能评估：")
            print(f"收益率: {performance.get('return_rate', 0):.2%}")
            print(f"最大回撤: {performance.get('max_drawdown', 0):.2%}")
        
        print("\n===== 均值回归策略示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()