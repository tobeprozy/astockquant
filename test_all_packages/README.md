
## 如何在任意位置导入qdata包

为了解决从任意位置导入qdata包的问题，我们提供了以下几种方法：

### 方法1: 以开发模式安装qdata包（推荐）

这种方法是最推荐的，它会将qdata包安装到Python环境中，但保持与源代码的链接，修改源码后不需要重新安装。

```bash
cd qdata
pip install -e .
```

### 方法2: 临时添加qdata目录到Python路径

这个方法只在当前终端会话中有效。

```bash
export PYTHONPATH=$PYTHONPATH:./astockquant/qdata
```

### 方法3: 在脚本开头添加Python路径设置

这种方法对单个脚本有效，不需要修改系统环境。

```python
import sys
import os
sys.path.insert(0, os.path.abspath('./astockquant/qdata'))
```

### 方法4: 修复项目结构（长期解决方案）

如果您希望从根本上解决包结构问题，可以考虑以下步骤：

1. 将qdata/qdata目录重命名为qdata/core
2. 修改qdata/__init__.py，从core导入所有公共API
3. 更新setup.py中的包配置

## 测试导入功能

我们提供了一个测试脚本，可以验证qdata包的导入功能：

```bash
python3 test_package_import.py
```

该脚本会检查qdata包的导入状态，并提供详细的错误信息和解决方案。