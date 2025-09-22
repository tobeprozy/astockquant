#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AstockQuant 项目示例运行器
用于执行所有插件的示例脚本
"""
import os
import sys
import subprocess
import argparse

# 定义项目中的所有插件目录
PLUGINS = [
    'qdata',
    'qbackengine',
    'qindicator',
    'qstrategy',
    'qplot'
]


def run_plugin_examples(plugin_name):
    """
    运行指定插件的示例脚本
    """
    print(f"\n{'='*60}")
    print(f"开始运行 {plugin_name} 插件的示例脚本")
    print(f"{'='*60}")
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建插件目录的绝对路径
    plugin_dir = os.path.join(current_dir, plugin_name)
    
    # 检查插件目录是否存在
    if not os.path.isdir(plugin_dir):
        print(f"警告: 插件目录 {plugin_dir} 不存在，跳过")
        return False
    
    # 构建示例运行脚本的绝对路径
    run_script = os.path.join(plugin_dir, 'run_examples.py')
    
    # 检查运行脚本是否存在
    if not os.path.isfile(run_script):
        print(f"警告: 插件 {plugin_name} 的示例运行脚本不存在，跳过")
        return False
    
    try:
        # 确保脚本有可执行权限
        os.chmod(run_script, 0o755)
        
        # 运行示例脚本
        result = subprocess.run(
            [sys.executable, run_script],
            cwd=plugin_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        # 输出脚本的标准输出和标准错误
        if result.stdout:
            print(f"\n{plugin_name} 标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"\n{plugin_name} 标准错误:\n{result.stderr}")
        
        # 检查脚本是否成功运行
        if result.returncode == 0:
            print(f"\n{plugin_name} 插件的示例脚本全部运行成功")
            return True
        else:
            print(f"\n{plugin_name} 插件的示例脚本运行失败，退出码: {result.returncode}")
            return False
    except Exception as e:
        print(f"\n运行 {plugin_name} 插件的示例脚本时出错: {str(e)}")
        return False


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='运行 AstockQuant 项目所有插件的示例脚本')
    parser.add_argument('--plugins', type=str, nargs='+', choices=PLUGINS, 
                      help='指定要运行的插件示例脚本 (默认: 所有插件)')
    
    args = parser.parse_args()
    
    # 确定要运行的插件
    plugins_to_run = args.plugins if args.plugins else PLUGINS
    
    print(f"开始运行 AstockQuant 项目的示例脚本\n")
    print(f"将要运行的插件: {', '.join(plugins_to_run)}")
    
    # 运行指定的插件示例
    success_count = 0
    fail_count = 0
    
    for plugin in plugins_to_run:
        if run_plugin_examples(plugin):
            success_count += 1
        else:
            fail_count += 1
    
    # 打印总结
    print(f"\n{'='*60}")
    print(f"AstockQuant 项目示例运行总结:")
    print(f"总插件数: {success_count + fail_count}")
    print(f"成功运行的插件: {success_count}")
    print(f"运行失败的插件: {fail_count}")
    print(f"{'='*60}")
    
    # 如果有插件运行失败，返回非零退出码
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == '__main__':
    main()