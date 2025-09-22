#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接导入测试脚本 - 验证所有AstockQuant包已正确安装到Python库中

此脚本测试是否可以直接导入所有AstockQuant包，而不需要设置绝对路径。
"""

import sys
import importlib.util

print("===== 开始测试直接导入AstockQuant包 =====")
print(f"当前Python路径: {sys.prefix}")
print(f"Python版本: {sys.version}")
print("\n测试结果:")

# 要测试的包列表
test_packages = [
    'qdata',
    'qbackengine',
    'qindicator',
    'qplot',
    'qstrategy'
]

# 测试每个包的导入状态
success_count = 0
failure_count = 0

for package_name in test_packages:
    try:
        # 尝试直接导入包
        __import__(package_name)
        
        # 获取包对象
        pkg = sys.modules[package_name]
        
        # 尝试获取版本信息
        version = getattr(pkg, '__version__', '未知版本')
        
        # 获取包的安装路径
        pkg_path = getattr(pkg, '__file__', '未知路径')
        
        print(f"✓ 成功导入 {package_name} (版本: {version})")
        print(f"   安装路径: {pkg_path}")
        success_count += 1
    except ImportError as e:
        print(f"✗ 导入 {package_name} 失败: {str(e)}")
        failure_count += 1
    except Exception as e:
        print(f"✗ 导入 {package_name} 发生未知错误: {str(e)}")
        failure_count += 1

print("\n===== 导入测试汇总 =====")
print(f"总测试包数: {len(test_packages)}")
print(f"成功导入: {success_count}")
print(f"导入失败: {failure_count}")

if failure_count == 0:
    print("\n🎉 恭喜！所有AstockQuant包都已成功安装并可以直接导入。")
    print("现在您可以在任何Python脚本中直接使用 'import qdata', 'import qbackengine' 等语句导入这些包，无需设置绝对路径。")
else:
    print("\n❌ 有包导入失败，请检查安装是否正确。")

print("\n===== 测试完成 =====")