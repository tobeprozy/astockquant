"""
移动平均线交叉策略使用示例
展示如何使用qstrategy中的移动平均线交叉策略进行回测和信号生成

本示例基于qstrategy的新架构（core和backends模块）
"""

import pandas as pd
from qstrategy.backends.sma_cross import SMACrossStrategy
from datetime import datetime, timedelta

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_data(days=100):
    """
    生成示例股票数据，确保包含金叉和死叉信号序列
    
    Args:
        days: 生成数据的天数
        
    Returns:
        DataFrame: 包含股票数据的DataFrame
    """
    # 生成日期序列
    dates = [datetime.now() - timedelta(days=i) for i in range(days-1, -1, -1)]
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    
    # 创建示例数据，设计明显的趋势变化以产生合理的交叉信号序列
    close_prices = []
    base_price = 100
    
    # 前20天：横盘整理（为后续趋势做准备）
    for i in range(20):
        close_prices.append(base_price + (i%7 - 3) * 0.8)
    
    # 接下来30天：缓慢上升趋势（会产生第一个金叉）
    for i in range(30):
        close_prices.append(close_prices[-1] + 0.8 + (i%5 - 2) * 0.5)
    
    # 接下来20天：快速下降趋势（会产生第一个死叉）
    for i in range(20):
        close_prices.append(close_prices[-1] - 1.2 + (i%4 - 1.5) * 0.6)
    
    # 接下来20天：再次上升趋势（会产生第二个金叉）
    for i in range(20):
        close_prices.append(close_prices[-1] + 1.0 + (i%6 - 2.5) * 0.7)
    
    # 最后10天：再次下降趋势（会产生第二个死叉）
    for i in range(10):
        close_prices.append(close_prices[-1] - 0.9 + (i%3 - 1) * 0.5)
    
    # 截取指定天数的数据
    close_prices = close_prices[:days]
    
    data = {
        'date': dates,
        'open': [price - 0.5 for price in close_prices],
        'high': [price + 1.0 for price in close_prices],
        'low': [price - 1.0 for price in close_prices],
        'close': close_prices,
        'volume': [10000 + (i%10)*2000 for i in range(days)]
    }
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

def main():
    """
    运行移动平均线交叉策略示例
    """
    print("===== 移动平均线交叉策略使用示例 =====")
    
    try:
        # 生成示例数据
        data = generate_sample_data()
        print("原始数据前5行：")
        print(data.head())
        
        # 创建策略实例
        strategy = SMACrossStrategy(
            fast_period=5, 
            slow_period=20, 
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
        
        print("\n===== 移动平均线交叉策略示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()