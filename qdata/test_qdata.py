"""
测试qdata模块的基本功能
"""
import os
import sys
import logging
import pandas as pd

# 设置日志级别为DEBUG以查看详细信息
logging.basicConfig(level=logging.DEBUG)

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入qdata模块
import qdata


def test_module_initialization():
    """
    测试模块初始化
    """
    print("\n===== 测试模块初始化 =====")
    try:
        print(f"qdata版本: {qdata.__version__}")
        print(f"默认后端: {qdata.backends._default_backend}")
        print(f"已注册后端: {list(qdata.backends._registered_backends.keys())}")
        print("模块初始化成功!")
        return True
    except Exception as e:
        print(f"模块初始化失败: {e}")
        return False


def test_get_daily_data():
    """
    测试获取日线数据功能
    注意：此测试可能需要实际的网络连接
    """
    print("\n===== 测试获取日线数据 =====")
    try:
        # 使用一个常用的股票代码进行测试
        symbol = "000001"
        start_date = "2023-01-01"
        end_date = "2023-01-10"
        
        print(f"尝试获取股票 {symbol} 从 {start_date} 到 {end_date} 的日线数据...")
        df = qdata.get_daily_data(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            print(f"成功获取日线数据，共 {len(df)} 条记录")
            print("数据样例:")
            print(df.head())
            return True
        else:
            print("获取的日线数据为空")
            return False
    except Exception as e:
        print(f"获取日线数据失败: {e}")
        return False


def test_get_stock_list():
    """
    测试获取股票列表功能
    """
    print("\n===== 测试获取股票列表 =====")
    try:
        print("尝试获取股票列表...")
        df = qdata.get_stock_list()
        
        if df is not None and not df.empty:
            print(f"成功获取股票列表，共 {len(df)} 条记录")
            print("股票列表样例:")
            print(df.head())
            return True
        else:
            print("获取的股票列表为空")
            return False
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return False


def test_backend_switching():
    """
    测试切换后端功能
    """
    print("\n===== 测试切换后端 =====")
    try:
        # 尝试切换到csv后端（即使没有实际数据，至少测试切换功能）
        print("尝试切换到csv后端...")
        qdata.set_default_backend('csv')
        print(f"成功切换到默认后端: {qdata.backends._default_backend}")
        
        # 切回akshare后端
        print("尝试切换回akshare后端...")
        qdata.set_default_backend('akshare')
        print(f"成功切换到默认后端: {qdata.backends._default_backend}")
        
        return True
    except Exception as e:
        print(f"切换后端失败: {e}")
        return False


def test_create_provider():
    """
    测试创建特定后端的提供者实例
    """
    print("\n===== 测试创建提供者实例 =====")
    try:
        # 创建akshare提供者实例
        print("创建akshare提供者实例...")
        ak_provider = qdata.create_provider('akshare')
        print(f"成功创建akshare提供者实例: {ak_provider}")
        
        # 创建csv提供者实例，指定数据目录
        print("创建csv提供者实例...")
        csv_provider = qdata.create_provider('csv', data_dir='./test_data')
        print(f"成功创建csv提供者实例: {csv_provider}")
        
        return True
    except Exception as e:
        print(f"创建提供者实例失败: {e}")
        return False


def test_data_manager():
    """
    测试数据管理器功能
    """
    print("\n===== 测试数据管理器 =====")
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
        prepared_df = qdata.DataManager.prepare_data(df, 'daily')
        print("处理后的数据:")
        print(prepared_df)
        
        # 验证数据
        is_valid = qdata.DataManager.validate_data(prepared_df)
        print(f"数据验证结果: {'有效' if is_valid else '无效'}")
        
        return is_valid
    except Exception as e:
        print(f"数据管理器测试失败: {e}")
        return False


def main():
    """
    运行所有测试
    """
    print("开始测试qdata模块...")
    
    # 运行所有测试
    results = {
        "模块初始化": test_module_initialization(),
        "获取日线数据": test_get_daily_data(),
        "获取股票列表": test_get_stock_list(),
        "切换后端": test_backend_switching(),
        "创建提供者实例": test_create_provider(),
        "数据管理器": test_data_manager()
    }
    
    # 打印测试结果摘要
    print("\n===== 测试结果摘要 =====")
    success_count = 0
    for test_name, result in results.items():
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    # 计算通过率
    total_tests = len(results)
    pass_rate = (success_count / total_tests) * 100
    
    print(f"\n测试完成: {success_count}/{total_tests} 通过 ({pass_rate:.1f}%)")
    
    if pass_rate >= 80:
        print("qdata模块重构成功!")
    else:
        print("qdata模块重构需要进一步调整!")


if __name__ == "__main__":
    main()