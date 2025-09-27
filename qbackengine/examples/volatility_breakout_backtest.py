#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
波动率突破策略回测示例
展示如何使用qbackengine运行波动率突破策略的回测
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
    """主函数：运行波动率突破策略回测"""
    print("===== 波动率突破策略回测示例 ====")
    
    # 创建波动率突破策略回测引擎
    engine = qbackengine.create_backtrader_engine(
        symbol='600000',  # 茅台股票代码
        start_date='2024-01-01',
        end_date='2024-12-31',
        strategy_name='volatility_breakout',  # 使用正确的策略名称
        starting_cash=100000.0,
        commission=0.00025, # 佣金
        strategy_kwargs={
            'window': 20,  # 波动率计算周期（与策略参数名一致）
            'multiplier': 2.0,  # 波动率乘数
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
    
    print("\n波动率突破策略回测完成！")

if __name__ == '__main__':
    main()