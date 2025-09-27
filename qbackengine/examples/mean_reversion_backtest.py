#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
均值回归策略回测示例
展示如何使用qbackengine运行均值回归策略的回测
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
    """主函数：运行均值回归策略回测"""
    print("===== 均值回归策略回测示例 ====")
    
    # 创建均值回归策略回测引擎
    engine = qbackengine.create_backtrader_engine(
        symbol='600000',  # 股票代码
        start_date='2024-01-01',
        end_date='2024-12-31',
        strategy_name='mean_reversion',  # 使用正确的策略名称（小写字母加下划线）
        starting_cash=100000.0,
        commission=0.00025,
        strategy_kwargs={
            'period': 20,  # 均值计算周期
            'z_score_threshold': 2.0,  # Z-score交易阈值
            'printlog': True,  # 打印交易日志
            'size': 1000  # 交易数量（股）
        }
    )
    
    # 运行回测
    result = engine.run()
    
    # 打印回测结果
    print("\n回测结果摘要：")
    engine.print_results(result)
    
    # 绘制回测结果图表
    engine.plot()
    
    print("\n均值回归策略回测完成！")

if __name__ == '__main__':
    main()