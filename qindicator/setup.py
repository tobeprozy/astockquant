from setuptools import setup, find_packages
import codecs
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'AstockQuant指标计算插件'

# 需安装的依赖
INSTALL_REQUIRES = [
    'pandas>=1.0.0',
    'numpy>=1.18.0',
    'TA-Lib>=0.6.7',
]

# 确保所有子包都被包含
packages = find_packages(include=['qindicator', 'qindicator.*'])

setup(
    name="qindicator",
    version=VERSION,
    author="AstockQuant Team",
    author_email="team@astockquant.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/astockquant/qindicator',
    packages=packages,
    package_dir={
        'qindicator': 'qindicator'
    },
    include_package_data=True,
    package_data={
        'qindicator': ['*.py', 'backends/*.py', 'backends/*/*.py', 'core/*.py'],
    },
    install_requires=INSTALL_REQUIRES,
    keywords=['python', 'stock', 'indicators', 'trading', 'technical analysis'],
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