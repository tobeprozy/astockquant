"""
配对交易策略使用示例
展示如何使用qstrategy中的配对交易策略进行回测和信号生成

本示例基于qstrategy的新架构（core和backends模块）
"""

import pandas as pd
from qstrategy.strategies.pair_trading_strategy import PairTradingStrategy
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
        dict: 包含两只配对股票数据的字典
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
    
    # 创建示例数据 - 股票B（与股票A有相关性但略有差异）
    data_b = {
        'date': dates,
        'open': [120 + i*0.48 for i in range(days)],
        'high': [121 + i*0.48 + i%5 for i in range(days)],
        'low': [119 + i*0.48 - i%3 for i in range(days)],
        'close': [120 + i*0.48 + (i%2 - 0.5)*2 + (i%7 - 3.5)*0.5 for i in range(days)],
        'volume': [12000 + i*1200 for i in range(days)]
    }
    
    df_a = pd.DataFrame(data_a)
    df_a['date'] = pd.to_datetime(df_a['date'])
    df_a.set_index('date', inplace=True)
    
    df_b = pd.DataFrame(data_b)
    df_b['date'] = pd.to_datetime(df_b['date'])
    df_b.set_index('date', inplace=True)
    
    return {'stock_a': df_a, 'stock_b': df_b}

def main():
    """
    运行配对交易策略示例
    """
    print("===== 配对交易策略使用示例 =====")
    
    try:
        # 生成示例数据
        pair_data = generate_sample_pair_data()
        print("股票A数据前5行：")
        print(pair_data['stock_a'].head())
        print("\n股票B数据前5行：")
        print(pair_data['stock_b'].head())
        
        # 创建策略实例
        strategy = PairTradingStrategy(
                                  lookback_period=30, 
                                  z_score_threshold=1.5, 
                                  printlog=True
        )
        
        # 初始化策略数据 - 注意PairTradingStrategy需要'symbol_a'和'symbol_b'键
        strategy.init_strategy({
            'symbol_a': pair_data['stock_a'],
            'symbol_b': pair_data['stock_b']
        })
        
        # 生成交易信号
        signals = strategy.generate_signals()
        print(f"\n生成的配对交易信号数量: {len(signals)}")
        
        # 显示部分信号
        if signals is not None:
            print("\n部分买入信号日期：")
            buy_signals = signals.get('buy_signals', [])
            if len(buy_signals) > 0:
                print(buy_signals[:3])
                
            print("\n部分卖出信号日期：")
            sell_signals = signals.get('sell_signals', [])
            if len(sell_signals) > 0:
                print(sell_signals[:3])
        
        # 执行交易
        results = strategy.execute_trade(signals)
        print(f"\n交易执行结果：")
        print(f"总买入交易次数: {results.get('total_buys', 0)}")
        print(f"总卖出交易次数: {results.get('total_sells', 0)}")
        print(f"总交易数量: {len(results.get('transactions', []))}")
        
        # 策略评估
        if hasattr(strategy, 'evaluate_performance'):
            performance = strategy.evaluate_performance(results)
            print(f"\n策略性能评估：")
            print(f"收益率: {performance.get('return_rate', 0):.2%}")
            print(f"最大回撤: {performance.get('max_drawdown', 0):.2%}")
        
        print("\n===== 配对交易策略示例运行完成 =====")
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()