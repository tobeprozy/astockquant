#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
qdata 插件示例运行器
用于执行 qdata/examples 目录下所有的 Python 示例脚本
"""
import os
import sys
import subprocess
import argparse
import glob


def run_python_script(script_path):
    """
    运行单个 Python 脚本
    """
    print(f"\n{'='*50}")
    print(f"正在运行: {script_path}")
    print(f"{'='*50}")
    
    try:
        # 获取脚本所在目录作为工作目录
        script_dir = os.path.dirname(script_path)
        
        # 运行脚本并捕获输出
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=script_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        # 输出脚本的标准输出和标准错误
        if result.stdout:
            print(f"\n标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"\n标准错误:\n{result.stderr}")
        
        # 检查脚本是否成功运行
        if result.returncode == 0:
            print(f"\n脚本运行成功: {script_path}")
            return True
        else:
            print(f"\n脚本运行失败: {script_path}, 退出码: {result.returncode}")
            return False
    except Exception as e:
        print(f"\n执行脚本时出错: {script_path}, 错误: {str(e)}")
        return False


def run_all_examples(examples_dir):
    """
    运行目录下所有的 Python 示例脚本
    """
    # 查找所有的 Python 文件，但排除 __init__.py
    python_files = []
    
    # 递归查找所有 .py 文件
    for root, _, files in os.walk(examples_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print(f"在 {examples_dir} 目录下没有找到 Python 示例脚本")
        return 0, 0
    
    print(f"找到 {len(python_files)} 个 Python 示例脚本\n")
    
    # 运行每个脚本并统计结果
    success_count = 0
    fail_count = 0
    
    for script_path in python_files:
        if run_python_script(script_path):
            success_count += 1
        else:
            fail_count += 1
    
    return success_count, fail_count


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='运行 qdata 插件的所有示例脚本')
    parser.add_argument('--dir', type=str, default='examples', 
                      help='示例脚本所在的目录 (默认: examples)')
    
    args = parser.parse_args()
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建示例目录的绝对路径
    examples_dir = os.path.join(current_dir, args.dir)
    
    # 检查示例目录是否存在
    if not os.path.isdir(examples_dir):
        print(f"错误: 示例目录 {examples_dir} 不存在")
        sys.exit(1)
    
    print(f"开始运行 qdata 插件的所有示例脚本\n")
    
    # 运行所有示例
    success_count, fail_count = run_all_examples(examples_dir)
    
    # 打印总结
    print(f"\n{'='*50}")
    print(f"示例运行总结:")
    print(f"总脚本数: {success_count + fail_count}")
    print(f"成功运行: {success_count}")
    print(f"运行失败: {fail_count}")
    print(f"{'='*50}")
    
    # 如果有脚本运行失败，返回非零退出码
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == '__main__':
    main()