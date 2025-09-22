# -*- coding: utf-8 -*-
"""
测试qdata包的导入功能
这个脚本应该能够在任意位置运行，并正确导入qdata包
"""
import sys
import os

try:
    # 打印当前Python路径，帮助调试
    print("当前Python路径:")
    for path in sys.path:
        print(f"  - {path}")
    
    # 检查是否有多个qdata模块
    print("\n查找系统中的qdata模块:")
    # 尝试导入当前的qdata模块
    import qdata
    print(f"找到qdata模块，路径: {qdata.__file__ if hasattr(qdata, '__file__') else '未知'}")
    print(f"qdata模块内容: {dir(qdata)}")
    
    # 检查这是不是我们想要的模块
    success = True
    if hasattr(qdata, '__version__'):
        print(f"qdata版本: {qdata.__version__}")
    else:
        print("警告: 这个qdata模块没有__version__属性，可能是一个空占位符模块")
        success = False
        
        # 尝试找到正确的qdata模块
        print("\n尝试找到正确的qdata模块...")
        qdata_dir = os.path.join(os.path.dirname(__file__), 'qdata')
        print(f"项目中的qdata目录路径: {qdata_dir}")
        
        # 检查qdata目录是否在Python路径中
        if qdata_dir not in sys.path:
            print(f"当前Python路径中不包含qdata目录({qdata_dir})")
            print("临时添加qdata目录到Python路径...")
            sys.path.insert(0, qdata_dir)
            
            # 重新导入qdata模块
            print("重新导入qdata模块...")
            import importlib
            if 'qdata' in sys.modules:
                importlib.reload(sys.modules['qdata'])
            try:
                import qdata
                print(f"重新导入后qdata模块路径: {qdata.__file__ if hasattr(qdata, '__file__') else '未知'}")
                if hasattr(qdata, '__version__'):
                    print(f"成功！找到正确的qdata模块，版本: {qdata.__version__}")
                    success = True
                else:
                    print("仍然没有找到正确的qdata模块")
                    success = False
            except ImportError as e:
                print(f"重新导入失败: {e}")
                success = False
        else:
            print("qdata目录已经在Python路径中，但导入的模块不正确")
            success = False
    
    if success:
        # 测试qdata的基本功能
        print("\n测试qdata的基本功能:")
        # 检查是否可以访问qdata的主要函数
        if hasattr(qdata, 'get_daily_data'):
            print("  ✓ get_daily_data函数可用")
        else:
            print("  ✗ get_daily_data函数不可用")
        
        if hasattr(qdata, 'get_stock_list'):
            print("  ✓ get_stock_list函数可用")
        else:
            print("  ✗ get_stock_list函数不可用")
        
        if hasattr(qdata, 'set_default_backend'):
            print("  ✓ set_default_backend函数可用")
        else:
            print("  ✗ set_default_backend函数不可用")
        
        if hasattr(qdata, 'create_provider'):
            print("  ✓ create_provider函数可用")
        else:
            print("  ✗ create_provider函数不可用")
            
    print("\n=== 解决方案总结 ===")
    print("为了能够在任意位置导入qdata包，建议采用以下方法之一:")
    print("")
    print("方法1: 以开发模式安装qdata包（推荐）")
    print("  cd /Users/zzy/workspace/AstockQuant/qdata")
    print("  pip install -e .")
    print("这种方法会将qdata包安装到Python环境中，但保持与源代码的链接，修改源码后不需要重新安装。")
    
    print("")
    print("方法2: 临时添加qdata目录到Python路径")
    print(f"  export PYTHONPATH=\$PYTHONPATH:/Users/zzy/workspace/AstockQuant/qdata")
    print("这个方法只在当前终端会话中有效。")
    
    print("")
    print("方法3: 在脚本开头添加Python路径设置")
    print("  import sys")
    print("  import os")
    print(f"  sys.path.insert(0, os.path.abspath('/Users/zzy/workspace/AstockQuant/qdata'))")
    print("这种方法对单个脚本有效。")
    
    print("")
    print("方法4: 修复项目结构（长期解决方案）")
    print("1. 将qdata/qdata目录重命名为qdata/core")
    print("2. 修改qdata/__init__.py，从core导入所有公共API")
    print("3. 更新setup.py中的包配置")
    print("这种方法可以从根本上解决包结构问题。")
    
except ImportError as e:
    print(f"导入qdata包失败: {e}")
    print("\n请尝试以下解决方案:")
    print("1. 确保已修复qdata/setup.py文件")
    print("2. 使用开发模式安装qdata包:")
    print("   cd /Users/zzy/workspace/AstockQuant/qdata")
    print("   pip install -e .")
    print("3. 检查Python路径是否正确包含qdata包所在目录")
    print(f"   可以临时添加路径: export PYTHONPATH=\$PYTHONPATH:/Users/zzy/workspace/AstockQuant/qdata")