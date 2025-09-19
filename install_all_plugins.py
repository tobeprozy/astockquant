#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AstockQuant 一键安装所有插件脚本
版本: 1.0
作者: AstockQuant Team
功能: 自动安装qdata、qindicator和qplot插件及其依赖
"""

import os
import sys
import subprocess
import platform
import time
from typing import List

# 颜色定义
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

# 日志函数
def log_info(message: str) -> None:
    """打印信息日志"""
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")

def log_success(message: str) -> None:
    """打印成功日志"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")

def log_warning(message: str) -> None:
    """打印警告日志"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {message}")

def log_error(message: str) -> None:
    """打印错误日志"""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}")

# 执行命令并返回结果
def run_command(command: List[str], description: str = "") -> bool:
    """执行命令并返回成功与否"""
    if description:
        log_info(description)
    
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            log_error(f"命令执行失败: {' '.join(command)}")
            log_error(f"错误输出: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        log_error(f"执行命令时发生异常: {str(e)}")
        return False

# 检查Python环境
def check_python_env() -> bool:
    """检查Python环境是否满足要求"""
    log_info("检查Python环境...")
    
    # 检查Python版本
    python_version = platform.python_version()
    log_info(f"当前Python版本: {python_version}")
    
    # 检查pip
    pip_installed = run_command([sys.executable, '-m', 'pip', '--version'], "")
    if not pip_installed:
        log_error("pip 未安装，请先安装pip。")
        return False
    
    # 确保pip是最新版本
    log_info("确保pip是最新版本...")
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], "更新pip...")
    
    return True

# 安装TA-Lib依赖提示
def install_talib_hint() -> None:
    """提供TA-Lib依赖安装提示"""
    log_info("\n--- TA-Lib 安装提示 ---")
    log_info("qindicator插件依赖TA-Lib库进行技术指标计算")
    log_info("请根据您的操作系统安装相应的依赖：")
    
    system = platform.system()
    if system == "Darwin":  # macOS
        log_info("macOS系统:")
        log_info("  1. 使用Homebrew安装: brew install ta-lib")
    elif system == "Linux":
        log_info("Linux系统:")
        log_info("  Ubuntu/Debian: sudo apt-get install libta-lib0")
        log_info("  CentOS/RHEL: sudo yum install ta-lib-devel")
    elif system == "Windows":
        log_info("Windows系统:")
        log_info("  1. 下载预编译的TA-Lib二进制文件")
        log_info("  2. 或参考相关教程安装")
    
    log_info("安装完系统依赖后，Python的TA-Lib包会自动安装")
    log_info("--- TA-Lib 安装提示结束 ---")
    
    # 等待用户确认
    input("按Enter键继续安装...")

# 安装插件
def install_plugin(plugin_path: str, plugin_name: str) -> bool:
    """安装单个插件"""
    log_info(f"开始安装 {plugin_name} 插件...")
    
    # 检查插件目录是否存在
    if not os.path.exists(plugin_path):
        log_error(f"插件目录不存在: {plugin_path}")
        return False
    
    # 检查setup.py是否存在
    setup_path = os.path.join(plugin_path, "setup.py")
    if not os.path.exists(setup_path):
        log_error(f"插件setup.py文件不存在: {setup_path}")
        return False
    
    # 使用pip安装插件（开发模式）
    install_command = [sys.executable, '-m', 'pip', 'install', '-e', plugin_path]
    success = run_command(install_command, f"安装 {plugin_name} 插件...")
    
    if success:
        log_success(f"{plugin_name} 插件安装成功！")
    else:
        log_error(f"{plugin_name} 插件安装失败！")
    
    return success

# 安装所有插件
def install_all_plugins() -> bool:
    """安装所有AstockQuant插件"""
    # 获取项目根目录（脚本所在目录）
    project_root = os.path.dirname(os.path.abspath(__file__))
    log_info(f"项目根目录: {project_root}")
    
    # 定义插件列表和安装顺序（按依赖关系排序）
    plugins = [
        (os.path.join(project_root, "qdata"), "qdata"),
        (os.path.join(project_root, "qindicator"), "qindicator"),
        (os.path.join(project_root, "qplot"), "qplot")
    ]
    
    # 安装基础依赖
    log_info("安装基础依赖包...")
    basic_deps = ["pandas>=1.0.0", "numpy>=1.18.0", "matplotlib>=3.3.0"]
    for dep in basic_deps:
        run_command([sys.executable, '-m', 'pip', 'install', dep], f"安装 {dep}...")
    
    # 提供TA-Lib安装提示
    install_talib_hint()
    
    # 依次安装每个插件
    for plugin_path, plugin_name in plugins:
        if not install_plugin(plugin_path, plugin_name):
            log_error(f"{plugin_name} 插件安装失败，停止安装后续插件")
            return False
        
    log_success("所有插件安装完成！")
    return True

# 显示使用示例
def show_usage_examples() -> None:
    """显示插件使用示例"""
    log_info("\n=== 使用示例 ===")
    log_info("1. qdata 插件示例:")
    log_info("   import qdata")
    log_info("   qdata.init()")
    log_info("   # 获取股票日线数据")
    log_info("   df = qdata.get_daily_data('600000', start_date='2023-01-01', end_date='2023-12-31')")
    
    log_info("\n2. qindicator 插件示例:")
    log_info("   import qindicator")
    log_info("   # 计算均线指标")
    log_info("   df_with_indicators = qindicator.calculate_ma(df, [5, 10, 20])")
    
    log_info("\n3. qplot 插件示例:")
    log_info("   import qplot")
    log_info("   # 绘制K线图")
    log_info("   qplot.plot_kline(df_with_indicators)")
    
    log_info("\n更多示例请查看各插件目录下的examples文件夹")

# 主函数
def main() -> None:
    """主函数"""
    print(f"{Colors.GREEN}=== AstockQuant 一键安装脚本 ==={Colors.ENDC}")
    print(f"{Colors.GREEN}版本: 1.0{Colors.ENDC}")
    print(f"{Colors.GREEN}作者: AstockQuant Team{Colors.ENDC}\n")
    
    # 检查Python环境
    if not check_python_env():
        log_error("Python环境检查失败，无法继续安装")
        sys.exit(1)
    
    # 安装所有插件
    start_time = time.time()
    success = install_all_plugins()
    end_time = time.time()
    
    # 显示安装结果和用时
    duration = end_time - start_time
    log_info(f"\n总安装用时: {duration:.2f} 秒")
    
    if success:
        show_usage_examples()
        log_success("\n🎉 安装完成！您现在可以使用AstockQuant的所有插件了。")
    else:
        log_error("\n❌ 安装过程中遇到错误，请查看上面的错误信息并尝试解决问题。")
        log_error("如果问题持续存在，您可以尝试手动安装每个插件。")
        sys.exit(1)

if __name__ == "__main__":
    main()