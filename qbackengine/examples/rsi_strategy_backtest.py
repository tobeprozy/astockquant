#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RSI策略回测示例
展示如何使用qbackengine运行RSI策略的回测
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
    """主函数：运行RSI策略回测"""
    print("===== RSI策略回测示例 ====")
    
    # 创建RSI策略回测引擎
    engine = qbackengine.create_backtrader_engine(
        symbol='600000',  # 茅台股票代码
        start_date='2024-01-01',
        end_date='2024-12-31',
        strategy_name='RSI',  # 使用qstrategy中的RSI策略
        starting_cash=100000.0,
        commission=0.00025,
        strategy_kwargs={
            'period': 14,  # RSI计算周期
            'overbought': 70,  # 超买阈值
            'oversold': 30,  # 超卖阈值
            'printlog': True  # 打印交易日志
        }
    )
    
    # 运行回测
    result = engine.run()
    
    # 打印回测结果
    print("\n回测结果摘要：")
    engine.print_results(result)
    
    # 绘制回测结果图表
    engine.plot()
    
    print("\nRSI策略回测完成！")

if __name__ == '__main__':
    main()