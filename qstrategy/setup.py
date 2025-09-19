from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'AstockQuant策略插件系统'

# 需安装的依赖
INSTALL_REQUIRES = [
    'pandas>=1.0.0',
    'numpy>=1.18.0',
    'backtrader'
]

setup(
    name="qstrategy",
    version=VERSION,
    author="AstockQuant Team",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    keywords=['python', 'stock', 'strategy', 'trading', 'backtesting'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)