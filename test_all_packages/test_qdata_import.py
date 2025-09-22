#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import importlib

print("===== 测试qdata包导入 =====")
print(f"当前Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path}\n")

# 尝试直接导入qdata
try:
    print("尝试直接导入qdata...")
    import qdata
    print(f"✓ 成功导入qdata (版本: {qdata.__version__})")
    print(f"  包路径: {qdata.__file__}")
    print(f"  包内容: {dir(qdata)[:10]}{'...' if len(dir(qdata)) > 10 else ''}")
except ImportError as e:
    print(f"✗ 直接导入qdata失败: {str(e)}")
    
    # 尝试手动添加qdata目录到Python路径
    print("\n尝试手动添加qdata目录到Python路径...")
    qdata_path = '/Users/zzy/workspace/AstockQuant/qdata'
    if os.path.exists(qdata_path):
        print(f"添加路径: {qdata_path}")
        sys.path.insert(0, qdata_path)
        
        # 再次尝试导入
        try:
            import qdata
            print(f"✓ 手动添加路径后成功导入qdata (版本: {qdata.__version__})")
            print(f"  包路径: {qdata.__file__}")
        except ImportError as e2:
            print(f"✗ 手动添加路径后仍无法导入qdata: {str(e2)}")
    else:
        print(f"路径不存在: {qdata_path}")

print("\n===== qdata导入测试完成 =====")