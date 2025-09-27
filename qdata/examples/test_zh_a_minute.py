"""
测试A股分时数据获取功能
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from qdata.backends.akshare_provider import AkShareProvider


def test_get_zh_a_minute_data():
    """
    测试获取A股分时数据
    """
    # 创建AkShareProvider实例
    provider = AkShareProvider()
    
    try:
        # 测试获取sh600751股票的1分钟分时数据，使用前复权
        print("正在获取sh600751股票的1分钟分时数据(前复权)...")
        df = provider.get_zh_a_minute_data(symbol='sh600751', period='1', adjust="qfq")
        
        # 打印数据信息
        print(f"获取数据成功! 数据形状: {df.shape}")
        print("数据样例:")
        print(df.head())
        print("\n数据列:", df.columns.tolist())
        print("\n数据索引:", df.index[:5])
        
        # 测试不同的复权类型
        print("\n测试其他复权类型:")
        # 后复权
        print("\n正在获取sh600751股票的1分钟分时数据(后复权)...")
        df_hfq = provider.get_zh_a_minute_data(symbol='sh600751', period='1', adjust="hfq")
        print(f"后复权数据形状: {df_hfq.shape}")
        
        # 不复权
        print("\n正在获取sh600751股票的1分钟分时数据(不复权)...")
        df_no_adjust = provider.get_zh_a_minute_data(symbol='sh600751', period='1', adjust="")
        print(f"不复权数据形状: {df_no_adjust.shape}")
        
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_get_zh_a_minute_data()