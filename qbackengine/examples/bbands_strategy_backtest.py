#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
布林带策略回测示例
展示如何使用qbackengine运行布林带策略的回测

注意：由于qbackengine的create_backtrader_engine函数与qstrategy的BBANDSStrategy不兼容，
本示例使用SimpleLoopEngine代替，SimpleLoopEngine是qbackengine提供的另一种回测引擎，
与qstrategy的策略设计更兼容。
"""

import qbackengine
import qdata
import qstrategy
import logging

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数：运行布林带策略回测"""
    print("===== 布林带策略回测示例 ====")
    
    try:
        # 获取数据
        data_provider = qdata.get_provider()
        df = data_provider.get_daily_data('600000', '2024-01-01', '2024-12-31')
        
        if df.empty:
            print("警告：获取数据为空，使用示例数据进行回测")
            # 生成示例数据用于测试
            import pandas as pd
            from datetime import datetime, timedelta
            
            # 生成日期序列
            dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(250)]
            
            # 创建示例数据
            import numpy as np
            np.random.seed(42)
            price = 100.0
            close_prices = []
            
            for i in range(250):
                # 添加一些趋势和随机波动
                trend = i * 0.1
                noise = np.random.normal(0, 2)
                price += trend + noise
                close_prices.append(price)
            
            df = pd.DataFrame({
                'date': dates,
                'open': [p * (1 + np.random.normal(0, 0.01)) for p in close_prices],
                'high': [max(o, p * (1 + np.random.normal(0, 0.02))) for o, p in zip(close_prices[:-1], close_prices[1:])],
                'low': [min(o, p * (1 - np.random.normal(0, 0.02))) for o, p in zip(close_prices[:-1], close_prices[1:])],
                'close': close_prices[1:],
                'volume': [int(np.random.normal(1000000, 500000)) for _ in range(249)]
            })
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # 获取策略实例
        strategy = qstrategy.get_strategy('bbands', 
            timeperiod=20, 
            nbdevup=2.0, 
            nbdevdn=2.0, 
            printlog=True
        )
        
        # 初始化策略数据
        strategy.init_data(df)
        
        # 创建SimpleLoopEngine回测引擎
        engine = qbackengine.SimpleLoopEngine(
            data_provider=data_provider,
            symbol='600000',
            start_date='2024-01-01',
            end_date='2024-12-31',
            strategy=strategy,
            starting_cash=100000.0
        )
        
        # 运行回测
        print("开始回测...")
        result = engine.run()
        
        # 打印回测结果
        print("\n回测结果摘要：")
        print(f"回测结果类型: {type(result)}")
        
        # 根据不同类型的结果进行适当处理
        if hasattr(result, '__dict__'):
            # 如果result是对象，检查其属性
            print(f"回测结果包含的属性: {dir(result)}")
            if hasattr(result, 'total_profit'):
                print(f"总利润: {result.total_profit:.2f}")
            if hasattr(result, 'num_trades'):
                print(f"交易次数: {result.num_trades}")
            if hasattr(result, 'final_equity'):
                print(f"最终权益: {result.final_equity:.2f}")
            
            # 安全地处理trades属性
            if hasattr(result, 'trades'):
                print(f"trades类型: {type(result.trades)}")
                if isinstance(result.trades, (list, tuple)) and result.trades:
                    print("\n部分交易详情：")
                    # 只显示前5个交易
                    for i, trade in enumerate(result.trades[:5]):
                        # 确保trade是字典类型
                        if isinstance(trade, dict):
                            date = trade.get('date', 'Unknown')
                            trade_type = trade.get('type', 'Unknown')
                            price = trade.get('price', 0)
                            print(f"交易{i+1}: {date} - {trade_type} @ {price:.2f}")
                        else:
                            print(f"交易{i+1}: {trade}")
        elif isinstance(result, dict):
            # 如果result是字典
            print(f"回测结果键: {list(result.keys())}")
            if 'total_profit' in result:
                print(f"总利润: {result['total_profit']:.2f}")
            if 'num_trades' in result:
                print(f"交易次数: {result['num_trades']}")
            if 'final_equity' in result:
                print(f"最终权益: {result['final_equity']:.2f}")
            
            # 安全地处理trades
            if 'trades' in result:
                print(f"trades类型: {type(result['trades'])}")
                if isinstance(result['trades'], (list, tuple)) and result['trades']:
                    print("\n部分交易详情：")
                    # 只显示前5个交易
                    for i, trade in enumerate(result['trades'][:5]):
                        if isinstance(trade, dict):
                            date = trade.get('date', 'Unknown')
                            trade_type = trade.get('type', 'Unknown')
                            price = trade.get('price', 0)
                            print(f"交易{i+1}: {date} - {trade_type} @ {price:.2f}")
                        else:
                            print(f"交易{i+1}: {trade}")
        else:
            # 其他类型的结果
            print(f"回测结果内容: {result}")
        
        print("\n布林带策略回测完成！")
        
    except Exception as e:
        logger.error(f"运行回测时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()