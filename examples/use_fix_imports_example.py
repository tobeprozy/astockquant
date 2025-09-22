#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用fix_imports.py修复AstockQuant包导入问题的示例

这个示例展示了如何在你的Python脚本中使用fix_imports.py工具，
以解决macOS上由于文件系统大小写敏感性导致的包导入问题。
"""

# 第一步：添加项目根目录到Python路径
import sys
project_root = '/Users/zzy/workspace/AstockQuant'
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"已添加项目根目录到Python路径: {project_root}")

# 第二步：导入并使用fix_imports工具
from fix_imports import fix_all_imports
print("\n开始修复所有包的导入问题...")
results = fix_all_imports()

# 第三步：正常导入所有AstockQuant包
print("\n开始导入AstockQuant包...")

# 导入qdata包并使用
try:
    import qdata
    print(f"✓ 成功导入qdata包 (版本: {getattr(qdata, '__version__', '未知版本')})")
    # 简单使用qdata的示例
    if hasattr(qdata, 'get_provider'):
        print("  qdata包包含get_provider函数")
except ImportError as e:
    print(f"✗ 导入qdata包失败: {str(e)}")

# 导入qbackengine包并使用
try:
    import qbackengine
    print(f"✓ 成功导入qbackengine包 (版本: {getattr(qbackengine, '__version__', '未知版本')})")
    # 简单使用qbackengine的示例
    if hasattr(qbackengine, 'init'):
        print("  qbackengine包包含init函数")
except ImportError as e:
    print(f"✗ 导入qbackengine包失败: {str(e)}")

# 导入qindicator包并使用
try:
    import qindicator
    print(f"✓ 成功导入qindicator包 (版本: {getattr(qindicator, '__version__', '未知版本')})")
    # 简单使用qindicator的示例
    if hasattr(qindicator, 'get_indicator_calculator'):
        print("  qindicator包包含get_indicator_calculator函数")
except ImportError as e:
    print(f"✗ 导入qindicator包失败: {str(e)}")

# 导入qplot包并使用
try:
    import qplot
    print(f"✓ 成功导入qplot包 (版本: {getattr(qplot, '__version__', '未知版本')})")
    # 简单使用qplot的示例
    if hasattr(qplot, 'get_chart'):
        print("  qplot包包含get_chart函数")
except ImportError as e:
    print(f"✗ 导入qplot包失败: {str(e)}")

# 导入qstrategy包并使用
try:
    import qstrategy
    print(f"✓ 成功导入qstrategy包 (版本: {getattr(qstrategy, '__version__', '未知版本')})")
    # 简单使用qstrategy的示例
    if hasattr(qstrategy, 'Strategy'):
        print("  qstrategy包包含Strategy类")
except ImportError as e:
    print(f"✗ 导入qstrategy包失败: {str(e)}")

print("\n===== 示例运行完成 =====")