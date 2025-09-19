#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配对交易策略回测示例
展示如何使用qbackengine运行配对交易策略的回测
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
    """主函数：运行配对交易策略回测"""
    print("===== 配对交易策略回测示例 ====")
    
    # 使用多标的回测引擎运行配对交易策略
    print("正在初始化多标的回测引擎...")
    multi_engine = qbackengine.create_multi_symbol_engine(
        symbol_a='600000',  # 茅台
        symbol_b='600170',  # 上海建工
        start_date='2024-01-01',
        end_date='2024-12-31',
        strategy_name='PairTrading',  # 使用qstrategy中的配对交易策略
        starting_cash=200000.0,
        commission=0.00025
    )
    
    print("正在运行回测...")
    result = multi_engine.run()
    
    # 打印回测结果
    print("\n回测结果摘要：")
    multi_engine.print_results(result)
    
    # 绘制回测结果图表
    multi_engine.plot()
    
    print("\n配对交易策略回测完成！")

if __name__ == '__main__':
    main()