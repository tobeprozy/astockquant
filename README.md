pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package

pip freeze > requirements.txt


# FAQ

## Ta-lib安装是失败：

### 获取源码库
sudo wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz

### 解压进入目录
tar -zxvf ta-lib-0.4.0-src.tar.gz
cd ta-lib/

### 编译安装
sudo ./configure --prefix=/usr  
sudo make
sudo make install

### 重新安装python的TA-Lib库
pip install TA-Lib
