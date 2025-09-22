#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import importlib.util
import os

# 要测试的包列表
packages_to_test = [
    'qdata',
    'qbackengine',
    'qindicator',
    'qplot',
    'qstrategy'
]

print("===== 开始测试所有包的导入 =====")
print(f"当前Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path}\n")

# 测试每个包的导入
for package in packages_to_test:
    try:
        print(f"\n测试导入包: {package}")
        
        # 尝试导入包
        module = __import__(package)
        
        # 打印包的版本信息（如果有）
        version = getattr(module, '__version__', '未知版本')
        print(f"✓ 成功导入 {package} (版本: {version})")
        
        # 打印包的路径
        print(f"  包路径: {module.__file__ if hasattr(module, '__file__') else '未知路径'}")
        
        # 打印包的主要内容（公共接口）
        public_attrs = [attr for attr in dir(module) if not attr.startswith('_')]
        print(f"  公共接口: {public_attrs[:10]}{'...' if len(public_attrs) > 10 else ''}")
        
    except ImportError as e:
        print(f"✗ 导入 {package} 失败: {str(e)}")
        
        # 尝试提供一些诊断信息
        if hasattr(e, 'name'):
            print(f"  无法导入的模块: {e.name}")
        
        # 检查Python路径中是否有相关目录
        for path in sys.path:
            if os.path.exists(os.path.join(path, package)):
                print(f"  在Python路径中找到包目录: {os.path.join(path, package)}")
                break
        else:
            print(f"  未在Python路径中找到包目录: {package}")
    
    except Exception as e:
        print(f"✗ 导入 {package} 时发生未知错误: {str(e)}")

print("\n===== 所有包导入测试完成 =====")