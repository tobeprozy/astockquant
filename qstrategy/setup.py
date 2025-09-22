from setuptools import setup, find_packages
import codecs
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'AstockQuant策略插件系统'

# 需安装的依赖
INSTALL_REQUIRES = [
    'pandas>=1.0.0',
    'backtrader'
]

# 确保所有子包都被包含
packages = find_packages(include=['qstrategy', 'qstrategy.*'])

setup(
    name="qstrategy",
    version=VERSION,
    author="AstockQuant Team",
    author_email="team@astockquant.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/astockquant/qstrategy',
    packages=packages,
    package_dir={
        'qstrategy': 'qstrategy'
    },
    include_package_data=True,
    package_data={
        'qstrategy': ['*.py', 'backends/*.py', 'core/*.py'],
    },
    install_requires=INSTALL_REQUIRES,
    keywords=['python', 'stock', 'strategy', 'trading', 'backtesting'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.7',
)