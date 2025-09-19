"""
qbacktest - 量化交易回测插件

该插件提供简洁而强大的回测功能，支持不同的回测引擎和策略。
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# 读取README.md文件内容作为长描述
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='qbackengine',
    version='0.1.0',
    description='qbackengine - 一个简洁的量化交易回测引擎插件系统',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/qbacktest',
    author='AstockQuant Team',
    author_email='team@astockquant.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='quantitative trading backtest',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'qdata>=0.1.0',
        'qstrategy>=0.1.0',
        'backtrader'  # 如果使用backtrader引擎
    ],
    python_requires='>=3.7',
    package_data={
        'qbackengine': ['README.md'],
    },
    entry_points={
        'console_scripts': [
            # 可以添加命令行工具入口点
        ],
    },
)