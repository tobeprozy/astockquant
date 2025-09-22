# -*- coding: utf-8 -*-
import sys
import os
import importlib.util

# 打印当前Python路径
def print_python_path():
    print("当前Python路径:")
    for path in sys.path:
        print(f"  - {path}")

# 检查qdata模块是否可以导入
def check_module(module_name):
    print(f"\n检查模块 {module_name}:")
    try:
        # 尝试直接导入
        __import__(module_name)
        print(f"  ✓ 直接导入成功")
        module = sys.modules[module_name]
        print(f"  ✓ 模块路径: {module.__file__ if hasattr(module, '__file__') else '未知'}")
        return module
    except ImportError as e:
        print(f"  ✗ 直接导入失败: {e}")
        
        # 尝试查找模块文件
        print("  尝试查找模块文件...")
        spec = importlib.util.find_spec(module_name)
        if spec:
            print(f"  ✓ 找到模块规范: {spec}")
            if spec.origin:
                print(f"  ✓ 模块文件: {spec.origin}")
        else:
            print(f"  ✗ 未找到模块规范")
        return None

# 打印当前工作目录
print(f"当前工作目录: {os.getcwd()}")

# 打印Python解释器信息
print(f"Python解释器: {sys.executable}")
print(f"Python版本: {sys.version}")

# 打印Python路径
print_python_path()

# 检查qdata模块
qdata_module = check_module('qdata')

if qdata_module:
    # 检查qdata.backends模块
    check_module('qdata.backends')
    check_module('qdata.backends.akshare_provider')

# 打印环境变量
print("\nPYTHONPATH环境变量:")
print(f"  {os.environ.get('PYTHONPATH', '未设置')}")

print("\n尝试使用绝对路径导入...")
qdata_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"qdata包目录: {qdata_dir}")

if qdata_dir not in sys.path:
    print(f"临时添加qdata包目录到Python路径: {qdata_dir}")
    sys.path.insert(0, qdata_dir)
    # 重新检查导入
    check_module('qdata')
else:
    print("qdata包目录已经在Python路径中")