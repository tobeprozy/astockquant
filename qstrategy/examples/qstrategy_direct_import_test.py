#!/usr/bin/env python
"""
测试直接导入策略类的功能
展示用户如何直接从qstrategy包导入和使用策略类
"""

import sys
import os

# 直接导入策略类
try:
    from qstrategy.backends.bbands import BBANDSStrategy
    from qstrategy.backends.macd import MACDStrategy
    from qstrategy.backends.rsi import RSIStrategy
    from qstrategy.backends.macd_kdj import MACDKDJStrategy
    from qstrategy.backends.sma_cross import SMACrossStrategy
    from qstrategy.backends.mean_reversion import MeanReversionStrategy
    print("✅ 成功直接导入所有策略类")
except Exception as e:
    print(f"❌ 直接导入策略类失败: {e}")

# 测试方法1: 获取策略实例
def test_get_strategy():
    """测试使用get_strategy函数获取策略实例"""
    print("===== 测试使用get_strategy获取策略实例 =====")
    try:
        import qstrategy
        
        # 测试获取布林带策略
        bbands_strategy = qstrategy.get_strategy('bbands', period=20, devfactor=2.0)
        print("✅ 成功获取布林带策略实例")
        
        # 测试获取MACD策略
        macd_strategy = qstrategy.get_strategy('macd', fastperiod=12, slowperiod=26, signalperiod=9)
        print("✅ 成功获取MACD策略实例")
        
        # 测试获取RSI策略
        rsi_strategy = qstrategy.get_strategy('rsi', period=14, overbought=70, oversold=30)
        print("✅ 成功获取RSI策略实例")
        
        # 测试获取MACD+KDJ策略
        macd_kdj_strategy = qstrategy.get_strategy('macd_kdj', macd_fast_period=12, macd_slow_period=26, macd_signal_period=9, kdj_period=9)
        print("✅ 成功获取MACD+KDJ策略实例")
        
        # 在实际使用中，可以通过策略后端模块获取可用策略列表
        # 这里为了简单起见，我们手动列出已知策略
        print("\n已知策略列表: sma_cross, macd, rsi, bbands, PairTrading, mean_reversion, macd_kdj")
        
    except Exception as e:
        print(f"❌ 获取策略实例失败: {e}")

# 测试方法2: 使用策略实例的方法
def test_strategy_methods():
    """测试策略实例的主要方法"""
    print("\n===== 测试策略实例的主要方法 =====")
    try:
        import qstrategy
        import pandas as pd
        from datetime import datetime, timedelta
        
        # 生成简单的测试数据
        dates = [datetime.now() - timedelta(days=i) for i in range(100-1, -1, -1)]
        data = pd.DataFrame({
            'date': dates,
            'open': [100 + i*0.5 for i in range(100)],
            'high': [101 + i*0.5 + i%5 for i in range(100)],
            'low': [99 + i*0.5 - i%3 for i in range(100)],
            'close': [100 + i*0.5 + (i%2 - 0.5)*2 for i in range(100)],
            'volume': [10000 + i*1000 for i in range(100)]
        })
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # 创建并初始化布林带策略
        bbands_strategy = qstrategy.get_strategy('bbands', period=20, devfactor=2.0)
        bbands_strategy.init_data(data)
        
        print("✅ 成功初始化布林带策略数据")
        print(f"布林带策略参数: 周期={bbands_strategy.params['period']}, 标准差倍数={bbands_strategy.params['devfactor']}")
        
        # 测试生成布林带信号
        bbands_signals = bbands_strategy.generate_signals()
        print(f"✅ 成功生成布林带交易信号: {len(bbands_signals['buy_signals'])}个买入信号, {len(bbands_signals['sell_signals'])}个卖出信号")
        
        # 测试执行布林带交易
        bbands_results = bbands_strategy.execute_trade()
        print(f"✅ 成功执行布林带交易: {bbands_results.get('num_trades', 0)}次交易, 利润: {bbands_results.get('total_profit', 0):.2f}")
        
        # 创建并初始化MACD+KDJ策略
        macd_kdj_strategy = qstrategy.get_strategy('macd_kdj', macd_fast_period=12, macd_slow_period=26, macd_signal_period=9, kdj_period=9)
        macd_kdj_strategy.init_data(data)
        
        print("\n✅ 成功初始化MACD+KDJ策略数据")
        print(f"MACD+KDJ策略参数: MACD周期={macd_kdj_strategy.params['macd_fast_period']}/{macd_kdj_strategy.params['macd_slow_period']}/{macd_kdj_strategy.params['macd_signal_period']}, KDJ周期={macd_kdj_strategy.params['kdj_period']}")
        
        # 测试生成MACD+KDJ信号
        macd_kdj_signals = macd_kdj_strategy.generate_signals()
        print(f"✅ 成功生成MACD+KDJ交易信号: {len(macd_kdj_signals['buy_signals'])}个买入信号, {len(macd_kdj_signals['sell_signals'])}个卖出信号")
        
        # 测试执行MACD+KDJ交易
        macd_kdj_results = macd_kdj_strategy.execute_trade()
        print(f"✅ 成功执行MACD+KDJ交易: {macd_kdj_results.get('num_trades', 0)}次交易, 利润: {macd_kdj_results.get('total_profit', 0):.2f}")
        
    except Exception as e:
        print(f"❌ 测试策略方法失败: {e}")

# 测试方法3: 直接使用导入的策略类
def test_direct_import_strategy():
    """测试直接使用导入的策略类"""
    print("\n===== 测试直接使用导入的策略类 =====")
    try:
        import pandas as pd
        from datetime import datetime, timedelta
        
        # 生成简单的测试数据
        dates = [datetime.now() - timedelta(days=i) for i in range(100-1, -1, -1)]
        data = pd.DataFrame({
            'date': dates,
            'open': [100 + i*0.5 for i in range(100)],
            'high': [101 + i*0.5 + i%5 for i in range(100)],
            'low': [99 + i*0.5 - i%3 for i in range(100)],
            'close': [100 + i*0.5 + (i%2 - 0.5)*2 for i in range(100)],
            'volume': [10000 + i*1000 for i in range(100)]
        })
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # 测试直接使用布林带策略类
        try:
            bbands = BBANDSStrategy(period=20, devfactor=2.0)
            bbands.init_data(data)
            bbands_signals = bbands.generate_signals()
            print(f"✅ 成功使用BBANDSStrategy类: {len(bbands_signals['buy_signals'])}个买入信号, {len(bbands_signals['sell_signals'])}个卖出信号")
        except Exception as e:
            print(f"❌ 使用BBANDSStrategy类失败: {e}")
        
        # 测试直接使用MACD+KDJ策略类
        try:
            macd_kdj = MACDKDJStrategy(macd_fast_period=12, macd_slow_period=26, macd_signal_period=9, kdj_period=9)
            macd_kdj.init_data(data)
            macd_kdj_signals = macd_kdj.generate_signals()
            print(f"✅ 成功使用MACDKDJStrategy类: {len(macd_kdj_signals['buy_signals'])}个买入信号, {len(macd_kdj_signals['sell_signals'])}个卖出信号")
        except Exception as e:
            print(f"❌ 使用MACDKDJStrategy类失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试直接导入策略类失败: {e}")

# 运行所有测试
if __name__ == "__main__":
    test_get_strategy()
    test_strategy_methods()
    test_direct_import_strategy()

print("\n===== 测试完成 =====")