#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShareProvider使用示例
展示如何直接使用AkShareProvider类以及通过qdata统一接口使用
"""
import pandas as pd
from qdata.backends.akshare_provider import AkShareProvider
import qdata

# 直接导入和使用
print("直接导入和使用")
ak_provider = AkShareProvider()
df = ak_provider.get_daily_data("512200", "2023-01-01", "2023-12-31")
print(df.head())
print(df.tail())

# 或使用qdata统一接口
print("或使用qdata统一接口")
df = qdata.get_daily_data("512200", "2023-01-01", "2023-12-31", backend='akshare')
print(df.head())
print(df.tail())

def direct_use_example():
    """直接使用AkShareProvider类示例"""
    print("\n=== 直接使用AkShareProvider类 ===")
    
    # 创建AkShareProvider实例
    ak_provider = AkShareProvider(retry_count=3)
    
    try:
        # 获取日线数据
        symbol = "512200"
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        print(f"获取ETF {symbol} 从 {start_date} 到 {end_date} 的日线数据...")
        df = ak_provider.get_daily_data(symbol, start_date, end_date)
        
        print(f"数据获取成功，共 {len(df)} 条记录")
        print("前5行数据:")
        print(df.head())
        
        # 获取股票列表
        print("\n获取股票列表...")
        stock_list = ak_provider.get_stock_list()
        print(f"股票列表获取成功，共 {len(stock_list)} 只股票")
        print("前5只股票:")
        print(stock_list.head())
        
    except Exception as e:
        print(f"错误: {e}")


def qdata_api_example():
    """使用qdata统一接口示例"""
    print("\n=== 使用qdata统一接口 ===")
    
    try:
        # 初始化qdata模块（这一步在首次调用接口时会自动执行，但显式调用可以确保初始化成功）
        qdata.init()
        
        # 使用默认后端获取数据
        symbol = "512200"
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        print(f"使用默认后端获取ETF {symbol} 从 {start_date} 到 {end_date} 的日线数据...")
        df = qdata.get_daily_data(symbol, start_date, end_date)
        
        print(f"数据获取成功，共 {len(df)} 条记录")
        print("前5行数据:")
        print(df.head())
        
        # 显式指定后端
        print("\n显式指定akshare后端获取数据...")
        df2 = qdata.get_daily_data(symbol, start_date, end_date, backend='akshare')
        print(f"数据获取成功，共 {len(df2)} 条记录")
        
    except Exception as e:
        print(f"错误: {e}")


def custom_config_example():
    """使用自定义配置创建AkShareProvider实例"""
    print("\n=== 使用自定义配置创建AkShareProvider实例 ===")
    
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
        
    except Exception as e:
        print(f"错误: {e}")


def main():
    """主函数"""
    print("=== AkShareProvider 使用示例 ===")
    
    # 示例1：直接使用AkShareProvider类
    direct_use_example()
    
    # 示例2：使用qdata统一接口
    qdata_api_example()
    
    # 示例3：使用自定义配置
    custom_config_example()
    
    print("\n=== 示例运行完毕 ===")


if __name__ == "__main__":
    main()