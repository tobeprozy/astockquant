#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import importlib.util
import importlib
from pathlib import Path

print("===== 深度诊断Python包导入问题 =====")
print(f"当前Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path}\n")

# 检查实际的文件系统路径
def check_actual_path(path_str):
    """检查实际文件系统中的路径(考虑大小写)"""
    try:
        # 在macOS上，我们可以通过遍历目录查找实际的大小写
        if sys.platform == 'darwin':  # macOS
            parts = Path(path_str).parts
            current = parts[0]  # 通常是根目录'/'
            
            for part in parts[1:]:
                found = False
                for item in os.listdir(current):
                    if item.lower() == part.lower():
                        current = os.path.join(current, item)
                        found = True
                        break
                if not found:
                    return None
            return current
        else:
            return path_str if os.path.exists(path_str) else None
    except Exception as e:
        print(f"检查路径时出错: {str(e)}")
        return None

# 测试包导入
def test_package_import(package_name, expected_path):
    print(f"\n=== 测试包: {package_name} ===")
    
    # 检查预期路径是否存在
    actual_path = check_actual_path(expected_path)
    print(f"预期路径: {expected_path}")
    print(f"实际路径: {actual_path}")
    print(f"路径存在: {os.path.exists(expected_path) if expected_path else False}")
    
    # 尝试直接导入
    try:
        print("\n尝试直接导入包...")
        module = __import__(package_name)
        print(f"✓ 成功导入 {package_name}")
        print(f"  版本: {getattr(module, '__version__', '未知版本')}")
        print(f"  文件路径: {module.__file__}")
        return True
    except ImportError as e:
        print(f"✗ 直接导入失败: {str(e)}")
        
        # 尝试通过路径导入
        if actual_path and os.path.isdir(actual_path):
            print("\n尝试通过实际路径导入...")
            try:
                # 查找__init__.py文件
                init_path = os.path.join(actual_path, '__init__.py')
                if os.path.exists(init_path):
                    spec = importlib.util.spec_from_file_location(package_name, init_path)
                    if spec:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[package_name] = module
                        spec.loader.exec_module(module)
                        print(f"✓ 通过路径成功导入 {package_name}")
                        print(f"  版本: {getattr(module, '__version__', '未知版本')}")
                        return True
            except Exception as e2:
                print(f"✗ 通过路径导入失败: {str(e2)}")
        
    return False

# 测试各个包
test_package_import('qdata', '/Users/zzy/workspace/AstockQuant/qdata/qdata')
test_package_import('qbackengine', '/Users/zzy/workspace/AstockQuant/qbackengine/qbackengine')
test_package_import('qindicator', '/Users/zzy/workspace/AstockQuant/qindicator/qindicator')
test_package_import('qplot', '/Users/zzy/workspace/AstockQuant/qplot/qplot')
test_package_import('qstrategy', '/Users/zzy/workspace/AstockQuant/qstrategy/qstrategy')

print("\n===== 深度诊断完成 =====")