#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple引擎回测示例
展示如何使用qbackengine的simple回测引擎运行策略
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
    """主函数：使用simple引擎运行回测"""
    print("===== Simple引擎回测示例 ====")
    print("Simple引擎是一个轻量级的事件循环回测引擎，适合简单策略的快速回测")
    
    # 创建simple引擎
    engine = qbackengine.run(
        symbol='600000',  # 茅台股票代码
        start_date='2024-01-01',
        end_date='2024-12-31',
        strategy_name='MACD',  # 使用qstrategy中的MACD策略
        starting_cash=100000.0,
        commission=0.00025,
        engine_type='simple',  # 使用simple引擎
        strategy_kwargs={
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'printlog': True
        }
    )
    
    # 注意：对于simple引擎，run函数直接返回结果对象
    result = engine
    
    # 打印回测结果
    print("\n回测结果摘要：")
    if hasattr(result, 'final_value'):
        print(f"最终总资产: {result.final_value:.2f}")
        print(f"初始资金: 100000.00")
        print(f"净收益: {(result.final_value - 100000.00):.2f}")
        if hasattr(result, 'trade_count'):
            print(f"交易次数: {result.trade_count}")
    else:
        print(f"回测结果: {result}")
    
    # 由于simple引擎返回的是结果对象而不是引擎实例，无法直接调用plot方法
    # 如果需要为simple引擎添加绘图功能，需要修改qbackengine模块的实现
    
    print("\nSimple引擎回测完成！")

if __name__ == '__main__':
    main()