"""
波动率突破策略使用示例
展示如何使用qstrategy中的波动率突破策略进行回测和信号生成

本示例基于qstrategy的新架构（core和backends模块）
"""

import pandas as pd
import qstrategy
from datetime import datetime, timedelta
import numpy as np

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
    
    # 创建示例数据 - 包含波动率特征
    base_price = 100
    trend = [i * 0.3 for i in range(days)]  # 上升趋势
    
    # 创建周期性变化的波动率
    volatility_period = 15
    volatility = [5 + 3 * np.sin(i / volatility_period * 2 * np.pi) for i in range(days)]
    
    # 生成价格序列
    close_prices = [base_price + trend[0]]
    for i in range(1, days):
        # 基于前一天的收盘价和当前波动率生成新价格
        daily_change = np.random.normal(0, volatility[i]/10)
        new_close = close_prices[i-1] * (1 + daily_change)
        close_prices.append(new_close)
    
    # 创建OHLC数据
    open_prices = [close * (1 + np.random.normal(0, 0.005)) for close in close_prices]
    high_prices = [max(o, c) * (1 + np.random.normal(0, 0.01)) for o, c in zip(open_prices, close_prices)]
    low_prices = [min(o, c) * (1 - np.random.normal(0, 0.01)) for o, c in zip(open_prices, close_prices)]
    volumes = [10000 + int(i*500 + np.random.normal(0, 5000)) for i in range(days)]
    
    data = {
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

def main():
    """
    运行波动率突破策略示例
    使用新架构的接口方式
    """
    print("===== 波动率突破策略使用示例 (新架构) =====")
    
    try:
        # 生成示例数据
        data = generate_sample_data()
        print("原始数据前5行：")
        print(data.head())
        
        # 创建策略实例
        try:
            strategy = qstrategy.get_strategy('volatility_breakout',
                                       volatility_window=10,
                                       breakout_factor=2.0,
                                       printlog=True)
            
            # 初始化策略数据
            strategy.init_data(data)
            
            # 生成交易信号
            signals = strategy.generate_signals()
        except ValueError:
            print(f"\n未找到 volatility_breakout 策略。使用 mean_reversion 策略作为替代进行演示。")
            strategy = qstrategy.get_strategy('mean_reversion',
                                       lookback_period=10,
                                       std_dev_threshold=2.0,
                                       printlog=True)
            
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
        
        # 策略评估
        if hasattr(strategy, 'evaluate_performance'):
            performance = strategy.evaluate_performance(results)
            print(f"\n策略性能评估：")
            print(f"收益率: {performance.get('return_rate', 0):.2%}")
            print(f"最大回撤: {performance.get('max_drawdown', 0):.2%}")
        
        print("\n===== 波动率突破策略示例运行完成 (新架构) =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()