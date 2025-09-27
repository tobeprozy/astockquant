#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qdata 包综合示例和测试

这个文件整合了 qdata 包的所有核心功能示例和测试，包括：
1. 模块初始化和基本信息
2. 数据获取功能（日线、分时数据）
3. 多数据源切换和自定义配置
4. 数据管理和验证
5. 异常处理
"""
import os
import sys
import logging
import pandas as pd
from qdata.backends.akshare_provider import AkShareProvider
import qdata

# 设置日志级别为INFO
logging.basicConfig(level=logging.INFO)


# =============== 模块信息和初始化 ===============

def show_module_info():
    """显示模块基本信息并初始化"""
    print("=== qdata 模块信息 ===")
    try:
        print(f"qdata版本: {getattr(qdata, '__version__', '未知')}")
        qdata.init()
        print(f"已注册后端: {list(getattr(qdata.backends, '_registered_backends', {}).keys())}")
        print("模块初始化成功!")
    except Exception as e:
        print(f"模块信息获取失败: {e}")
    print()


# =============== 数据获取功能示例 ===============

def get_daily_data_example():
    """日线数据获取示例"""
    print("=== 日线数据获取示例 ===")
    try:
        # 获取股票日线数据
        stock_df = qdata.get_daily_data('600000', '2023-01-01', '2023-06-30')
        print(f"获取到的股票日线数据形状: {stock_df.shape}")
        print("股票数据样例:")
        print(stock_df.head())
        
        # 获取ETF日线数据
        etf_df = qdata.get_daily_data('512200', '2023-01-01', '2023-12-31')
        print(f"获取到的ETF日线数据形状: {etf_df.shape}")
        print("ETF数据样例:")
        print(etf_df.head())
        
    except Exception as e:
        print(f"获取数据失败: {e}")
    print()


def get_minute_data_example():
    """分时数据获取示例"""
    print("=== 分时数据获取示例 ===")
    try:
        # 获取过去日期的分时数据，添加缺少的end_time参数
        minute_data = qdata.get_minute_data('600000', '2023-06-30', '2023-06-30', freq='1min')
        print(f"获取到的分时数据形状: {minute_data.shape}")
        print("分时数据样例:")
        print(minute_data.head())
    except Exception as e:
        print(f"获取分时数据失败: {e}")
    print()


def get_market_list_example():
    """获取市场列表示例"""
    print("=== 获取市场列表示例 ===")
    try:
        # 获取股票列表
        stock_list = qdata.get_stock_list()
        print(f"获取到的股票列表数量: {len(stock_list) if not stock_list.empty else 0}")
        if not stock_list.empty:
            print("股票列表样例:")
            print(stock_list.head())
        
        # 获取ETF列表
        try:
            etf_list = qdata.get_etf_list()
            print(f"获取到的ETF列表数量: {len(etf_list) if not etf_list.empty else 0}")
            if not etf_list.empty:
                print("ETF列表样例:")
                print(etf_list.head())
        except Exception as e:
            print(f"获取ETF列表失败: {e}")
            
    except Exception as e:
        print(f"获取列表数据失败: {e}")
    print()


# =============== 多数据源和自定义配置 ===============

def multi_backend_example():
    """多数据源切换示例"""
    print("=== 多数据源切换示例 ===")
    
    # 获取当前使用的数据源
    current_provider = qdata.get_provider()
    print(f"当前使用的数据源类型: {type(current_provider).__name__}")
    
    # 切换到csv后端
    try:
        qdata.set_default_backend('csv')
        csv_provider = qdata.get_provider()
        print(f"切换到CSV后端: {type(csv_provider).__name__}")
    except Exception as e:
        print(f"切换到CSV后端失败: {e}")
    
    # 切换到akshare后端
    try:
        qdata.set_default_backend('akshare')
        ak_provider = qdata.get_provider()
        print(f"切换到AkShare后端: {type(ak_provider).__name__}")
    except Exception as e:
        print(f"切换到AkShare后端失败: {e}")
    
    # 尝试切换到tushare后端（需要token）
    try:
        qdata.set_default_backend('tushare')
        tu_provider = qdata.get_provider()
        print(f"切换到TuShare后端: {type(tu_provider).__name__}")
        # 切回akshare后端
        qdata.set_default_backend('akshare')
    except Exception as e:
        print(f"使用TuShare数据源失败: {e}")
        print("请确保已设置TUSHARE_TOKEN环境变量")
    print()


def custom_akshare_provider_example():
    """自定义AkShareProvider配置示例"""
    print("=== 自定义AkShareProvider配置示例 ===")
    
    # 创建自定义配置的AkShareProvider实例
    custom_ak_provider = AkShareProvider(
        retry_count=5,  # 自定义重试次数
        retry_delay=[2, 4, 6, 8, 10]  # 自定义重试延迟时间列表
    )
    
    try:
        symbol = "512200"
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        print(f"使用自定义配置获取ETF {symbol} 的日线数据...")
        df = custom_ak_provider.get_daily_data(symbol, start_date, end_date)
        print(f"数据获取成功，共 {len(df)} 条记录")
        print("数据样例:")
        print(df.head())
        
    except Exception as e:
        print(f"错误: {e}")
    print()


def create_provider_example():
    """创建特定后端的提供者实例"""
    print("=== 创建提供者实例示例 ===")
    try:
        # 创建akshare提供者实例
        print("创建akshare提供者实例...")
        ak_provider = qdata.create_provider('akshare')
        print(f"成功创建akshare提供者实例: {ak_provider}")
        
        # 创建csv提供者实例，指定数据目录
        print("创建csv提供者实例...")
        csv_provider = qdata.create_provider('csv', data_dir='./test_data')
        print(f"成功创建csv提供者实例: {csv_provider}")
        
    except Exception as e:
        print(f"创建提供者实例失败: {e}")
    print()


# =============== CSV数据源使用 ===============

def csv_backend_usage_example():
    """CSV数据源使用示例"""
    print("=== CSV数据源使用示例 ===")
    
    try:
        # 准备数据目录和示例文件
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            # 创建一个示例CSV文件
            sample_data = pd.DataFrame({
                'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
                'open': [10.0, 10.2, 10.5],
                'high': [10.5, 10.7, 10.8],
                'low': [9.9, 10.1, 10.3],
                'close': [10.3, 10.5, 10.7],
                'volume': [1000000, 1200000, 1500000]
            })
            sample_data.to_csv(os.path.join(data_dir, '600000_daily.csv'), index=False)
            print(f"已创建示例CSV文件: {os.path.join(data_dir, '600000_daily.csv')}")
        
        # 使用CSV数据源
        qdata.set_default_backend('csv')
        
        # 从CSV文件获取数据
        csv_data = qdata.get_daily_data('600000', '2023-01-01', '2023-01-03')
        print("从CSV文件获取的数据:")
        print(csv_data)
        
    except Exception as e:
        print(f"使用CSV数据源失败: {e}")
    
    # 切换回默认数据源
    qdata.set_default_backend('akshare')
    print()


# =============== 数据管理和验证 ===============

def data_manager_example():
    """数据管理器功能示例"""
    print("=== 数据管理器示例 ===")
    try:
        # 创建测试数据
        test_data = {
            'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [103, 104, 105],
            'Volume': [1000, 2000, 3000]
        }
        
        df = pd.DataFrame(test_data)
        print("原始测试数据:")
        print(df)
        
        # 使用数据管理器处理数据
        if hasattr(qdata, 'DataManager'):
            prepared_df = qdata.DataManager.prepare_data(df, 'daily')
            print("处理后的数据:")
            print(prepared_df)
            
            # 验证数据
            is_valid = qdata.DataManager.validate_data(prepared_df)
            print(f"数据验证结果: {'有效' if is_valid else '无效'}")
        else:
            print("qdata模块中未找到DataManager类")
            
    except Exception as e:
        print(f"数据管理器测试失败: {e}")
    print()


# =============== 异常处理 ===============

def exception_handling_example():
    """异常处理示例"""
    print("=== 异常处理示例 ===")
    
    try:
        # 尝试获取不存在的股票数据
        df = qdata.get_daily_data('999999', '2023-01-01', '2023-06-30')
    except Exception as e:
        print(f"捕获到异常: {e}")
        
    # 尝试使用不存在的后端
    try:
        qdata.set_default_backend('non_existent_backend')
    except Exception as e:
        print(f"捕获到异常: {e}")
    print()


# =============== 主函数 ===============

def main():
    """主函数：运行所有示例"""
    print("=== qdata 包综合示例和测试 ===")
    print("这个文件整合了 qdata 包的核心功能示例和测试")
    print()
    
    # 运行各个示例
    show_module_info()
    get_daily_data_example()
    get_minute_data_example()
    get_market_list_example()
    multi_backend_example()
    custom_akshare_provider_example()
    create_provider_example()
    csv_backend_usage_example()
    data_manager_example()
    exception_handling_example()
    
    print("=== 示例运行完毕 ===")


if __name__ == "__main__":
    main()