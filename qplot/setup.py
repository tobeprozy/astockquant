import os
from setuptools import setup, find_packages

# 读取项目目录下的README文件作为长描述
readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = '统一的股票数据可视化插件，支持实时日K线图和分时图绘制'

# 确保当前目录中有一个qplot目录
if not os.path.exists('qplot'):
    os.makedirs('qplot')
    with open('qplot/__init__.py', 'a'):
        pass

setup(
    name='qplot',
    version='0.1.0',
    description='统一的股票数据可视化插件，支持实时日K线图和分时图绘制',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AstockQuant Team',
    author_email='team@astockquant.com',
    url='https://github.com/astockquant/qplot',
    packages=['qplot', 'qplot.plotters'],
    package_dir={
        'qplot': 'qplot',
        'qplot.plotters': 'qplot/plotters'
    },
    include_package_data=True,
    package_data={
        'qplot': [
            'plotters/**/*',
            '*.py',
        ],
    },
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'matplotlib>=3.3.0',  # 绘图库
        'mplfinance>=0.12.7a17',  # 金融数据绘图专用库
        'qdata>=0.1.0',  # 依赖qdata插件获取数据
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'flake8>=3.8.0',
            'black>=20.8b1',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    keywords='股票可视化,图表绘制,K线图,分时图,量化交易',
    project_urls={
        'Documentation': 'https://github.com/astockquant/qplot/wiki',
        'Bug Reports': 'https://github.com/astockquant/qplot/issues',
        'Source': 'https://github.com/astockquant/qplot',
    },
)