#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MACD+KDJ策略回测示例
展示如何使用qbackengine运行MACD+KDJ策略的回测
"""

import qbackengine
import logging

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数：运行MACD+KDJ策略回测"""
    print("===== MACD+KDJ策略回测示例 ====")
    
    # 创建MACD+KDJ策略回测引擎
    engine = qbackengine.create_backtrader_engine(
        symbol='600000',  # 股票代码
        start_date='2025-06-01',
        end_date='2025-12-31',
        strategy_name='macd_kdj',  # 使用qstrategy中的MACD+KDJ策略
        starting_cash=100000.0,
        commission=0.00025,
        strategy_kwargs={
            'macd_fast_period': 12,    # MACD快线周期
            'macd_slow_period': 26,    # MACD慢线周期
            'macd_signal_period': 9,   # MACD信号线周期
            'kdj_period': 9,           # KDJ周期
            'kdj_slowing_period': 3,   # KDJ平滑周期
            'printlog': True,          # 打印交易日志
            'size': 5000               # 交易数量（股），可以根据需要调整这个值
        }
    )
    
    # 运行回测
    result = engine.run()
    
    # 打印回测结果
    print("\n回测结果摘要：")
    engine.print_results(result)
    
    # 绘制回测结果图表
    engine.plot()
    
    print("\nMACD+KDJ策略回测完成！")

if __name__ == '__main__':
    main()