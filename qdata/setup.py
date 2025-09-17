from setuptools import setup
import os

# 读取项目目录下的README文件作为长描述
readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = '统一的股票数据获取插件，支持多种数据源'

# 确保当前目录中有一个qdata目录
if not os.path.exists('qdata'):
    os.makedirs('qdata')
    with open('qdata/__init__.py', 'a'):
        pass

setup(
    name='qdata',
    version='0.1.0',
    description='统一的股票数据获取插件，支持多种数据源',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AstockQuant Team',
    author_email='team@astockquant.com',
    url='https://github.com/astockquant/qdata',
    packages=['qdata', 'qdata.providers'],
    package_dir={
        'qdata': 'qdata',
        'qdata.providers': 'qdata/providers'
    },
    include_package_data=True,
    package_data={
        'qdata': [
            'providers/**/*',
            '*.py',
        ],
    },
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'akshare>=1.8.0',  # akshare数据源依赖
        'tushare>=1.2.80',  # tushare数据源依赖
        'requests>=2.24.0',  # 网络请求依赖
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
    keywords='股票数据,akshare,tushare,量化交易,数据获取',
    project_urls={
        'Documentation': 'https://github.com/astockquant/qdata/wiki',
        'Bug Reports': 'https://github.com/astockquant/qdata/issues',
        'Source': 'https://github.com/astockquant/qdata',
    },
)