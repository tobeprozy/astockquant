#!/usr/bin/env python
"""
测试直接导入qplot中的类和函数
展示用户如何直接从qplot包导入和使用绘图类
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 直接导入qplot中的类和函数
print("===== 测试直接导入qplot类和函数 =====")
try:
    from qplot import (
        Plotter, 
        Chart, 
        RealTimePlotter,
        DataManager,
        MatplotlibChart,
        PyechartsChart,
        get_chart,
        plot_kline,
        plot_minute_chart,
        HAS_PYECHARTS
    )
    print("✅ 成功直接导入所有qplot类和函数")
except Exception as e:
    print(f"❌ 直接导入qplot类和函数失败: {e}")

# 测试工厂函数获取图表实例
def test_get_chart():
    """测试使用get_chart工厂函数获取图表实例"""
    print("\n===== 测试使用get_chart工厂函数获取图表实例 =====")
    try:
        # 生成简单的测试数据
        data = generate_sample_data()
        
        # 测试获取matplotlib的K线图
        kline_chart_mpl = get_chart('kline', backend='matplotlib', data=data)
        print("✅ 成功获取matplotlib K线图实例")
        
        # 测试获取matplotlib的分时图
        minute_chart_mpl = get_chart('minute', backend='matplotlib', data=data)
        print("✅ 成功获取matplotlib分时图实例")
        
        # 如果pyecharts可用，测试获取pyecharts的图表
        if HAS_PYECHARTS:
            kline_chart_echarts = get_chart('kline', backend='pyecharts', data=data)
            print("✅ 成功获取pyecharts K线图实例")
            
            minute_chart_echarts = get_chart('minute', backend='pyecharts', data=data)
            print("✅ 成功获取pyecharts分时图实例")
        else:
            print("ℹ️ pyecharts不可用，跳过pyecharts相关测试")
            
    except Exception as e:
        print(f"❌ 使用get_chart工厂函数失败: {e}")

# 测试直接使用导入的类
def test_direct_import_classes():
    """测试直接使用导入的绘图类"""
    print("\n===== 测试直接使用导入的绘图类 =====")
    try:
        # 生成简单的测试数据
        data = generate_sample_data()
        
        # 测试使用MatplotlibChart类
        try:
            mpl_chart = MatplotlibChart('kline', data=data)
            print("✅ 成功创建MatplotlibChart实例")
        except Exception as e:
            print(f"❌ 创建MatplotlibChart实例失败: {e}")
        
        # 如果pyecharts可用，测试使用PyechartsChart类
        if HAS_PYECHARTS:
            try:
                echarts_chart = PyechartsChart('kline', data=data)
                print("✅ 成功创建PyechartsChart实例")
            except Exception as e:
                print(f"❌ 创建PyechartsChart实例失败: {e}")
        else:
            print("ℹ️ pyecharts不可用，跳过PyechartsChart相关测试")
        
        # 测试使用DataManager类
        try:
            data_manager = DataManager('600519', 'daily')
            # 设置一些测试数据
            data_manager.update_data(data)
            print("✅ 成功创建和初始化DataManager实例")
        except Exception as e:
            print(f"❌ 创建或初始化DataManager实例失败: {e}")
            
    except Exception as e:
        print(f"❌ 测试直接使用导入的类失败: {e}")

# 测试快捷绘图函数
def test_shortcut_functions():
    """测试快捷绘图函数"""
    print("\n===== 测试快捷绘图函数 =====")
    try:
        # 生成简单的测试数据
        data = generate_sample_data()
        
        # 确保输出目录存在
        output_dir = './output'
        os.makedirs(output_dir, exist_ok=True)
        
        # 测试plot_kline函数
        print("1. 测试plot_kline函数")
        try:
            # 使用matplotlib后端
            chart1 = plot_kline(data=data, backend='matplotlib', title='测试K线图')
            print("✅ 成功使用plot_kline函数(matplotlib)")
            
            # 如果使用pyecharts后端并且可用，保存图表
            if HAS_PYECHARTS:
                chart2 = plot_kline(data=data, backend='pyecharts', title='测试K线图(Pyecharts)')
                output_path = os.path.join(output_dir, 'kline_example.html')
                chart2.save(output_path)  # 保存HTML文件
                print(f"✅ 成功使用plot_kline函数(pyecharts)并保存图表至: {output_path}")
        except Exception as e:
            print(f"❌ 使用plot_kline函数失败: {e}")
        
        # 测试plot_minute_chart函数
        print("\n2. 测试plot_minute_chart函数")
        try:
            # 使用matplotlib后端
            chart3 = plot_minute_chart(data=data, backend='matplotlib', title='测试分时图')
            print("✅ 成功使用plot_minute_chart函数(matplotlib)")
            
            # 如果使用pyecharts后端并且可用，保存图表
            if HAS_PYECHARTS:
                chart4 = plot_minute_chart(data=data, backend='pyecharts', title='测试分时图(Pyecharts)')
                output_path = os.path.join(output_dir, 'minute_chart_example.html')
                chart4.save(output_path)  # 保存HTML文件
                print(f"✅ 成功使用plot_minute_chart函数(pyecharts)并保存图表至: {output_path}")
        except Exception as e:
            print(f"❌ 使用plot_minute_chart函数失败: {e}")
            
    except Exception as e:
        print(f"❌ 测试快捷绘图函数失败: {e}")

# 生成测试数据
def generate_sample_data(days=100):
    """
    生成简单的测试数据
    """
    # 创建日期索引
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='B')
    
    # 生成随机价格数据
    np.random.seed(42)  # 设置随机种子，确保结果可重现
    base_price = 100
    returns = np.random.normal(0, 0.02, days)
    prices = base_price * (1 + returns).cumprod()
    
    # 生成开盘价、最高价、最低价和收盘价
    open_prices = prices * (1 + np.random.normal(0, 0.005, days))
    high_prices = np.maximum(prices, open_prices) * (1 + np.random.normal(0, 0.005, days))
    low_prices = np.minimum(prices, open_prices) * (1 - np.random.normal(0, 0.005, days))
    close_prices = prices
    
    # 生成成交量
    volume = np.random.randint(1000, 10000, days)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume
    }, index=dates)
    
    # 计算均线
    data['ma5'] = data['close'].rolling(window=5).mean()
    data['ma10'] = data['close'].rolling(window=10).mean()
    
    return data

# 运行所有测试
def main():
    """主函数"""
    print("=== qplot直接导入功能测试程序 ===")
    
    # 测试工厂函数获取图表实例
    test_get_chart()
    
    # 测试直接使用导入的类
    test_direct_import_classes()
    
    # 测试快捷绘图函数
    test_shortcut_functions()

if __name__ == "__main__":
    main()
    print("\n===== 测试完成 =====")