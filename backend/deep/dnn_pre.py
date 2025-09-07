import matplotlib.pyplot as plt
import os
import sys

# from sklearn.preprocessing import MinMaxScaler
import torch
import datetime
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
from tqdm import tqdm
import torch.optim as optim


# 获取当前文件的目录
cur_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root = os.path.abspath(os.path.join(cur_dir, '..'))
# 将项目根目录添加到 sys.path
if root not in sys.path:
    sys.path.append(root)


from adapters.akshare_provider import AkshareFundProvider


def adapt_backtrader(df):
    # 利用 AKShare 获取股票的后复权数据，这里只获取前 6 列
    df = df.iloc[:, :6]
    # 删除 `股票代码` 列
    # del df['股票代码']
    # 处理字段命名，以符合 Backtrader 的要求
    df.columns = [
        'Date',
        'Open',
        'Close',
        'High',
        'Low',
        'Vol',
    ]
    return df




class MinMaxScaler:
    def __init__(self):
        self.min_val = None
        self.max_val = None

    def fit(self, data):
        # data应该是一个torch.tensor
        self.min_val = data.min(dim=0)[0]
        self.max_val = data.max(dim=0)[0]

    def transform(self, data):
        # 归一化公式：(x - min) / (max - min)
        return (data - self.min_val) / (self.max_val - self.min_val)

    def inverse_transform(self, data):
        # 反归一化公式：(x * (max - min)) + min
        return (data * (self.max_val - self.min_val)) + self.min_val

class ModelDNN(nn.Module):
    def __init__(self, input_size, hiddens=[64, 32, 8]):
        super().__init__()
        self.hiddens = hiddens
        self.net = nn.Sequential(nn.Flatten())
        for pre, nxt in zip([input_size]+hiddens[:-1], hiddens):
            self.net.append(nn.Linear(pre, nxt))
            self.net.append(nn.ReLU())
        self.net.append(nn.Linear(hiddens[-1], 1))
        
    def forward(self, x):
        return self.net(x)


if __name__ == "__main__":

    # 设置日期范围
    s_date = (datetime.datetime.now() - datetime.timedelta(days=3000)).strftime('%Y-%m-%d')
    e_date = datetime.datetime.now().strftime('%Y-%m-%d')

    provider = AkshareFundProvider()
    df = provider.fetch(symbol="159892", start_date=s_date.replace('-', ''), end_date=e_date.replace('-', ''))
    df = df.reset_index()
    df = df[['date','open','close','high','low','volume']]
    df.columns = ['Date','Open','Close','High','Low','Vol']
    print(df.shape)

    # ms = MinMaxScaler()
    # mms.fit(df.iloc[:-800][["Open", "High", "Low", "Close", "Vol"]])
    # df[["Open", "High", "Low", "Close", "Vol"]] = mms.transform(df[["Open", "High", "Low", "Close", "Vol"]])
    # 假设df是一个Pandas DataFrame，我们首先将其转换为torch.tensor
    
    # 将Pandas DataFrame转换为PyTorch张量，排除日期列
    data_tensor = torch.tensor(df.iloc[:, 1:].values, dtype=torch.float)

    # 计算每个特征的最大值和最小值
    min_vals = data_tensor.min(dim=0)[0]
    max_vals = data_tensor.max(dim=0)[0]

    # 应用归一化公式
    df_normalized_tensor = (data_tensor - min_vals) / (max_vals - min_vals + 1e-8)  # 加上一个小的值防止除以零

    # 将归一化后的张量转换回NumPy数组，以便与Pandas DataFrame合并
    df_normalized = pd.DataFrame(df_normalized_tensor.numpy(), columns=df.columns[1:], index=df.index)

    # 将日期列重新添加到归一化后的DataFrame中
    df_normalized.insert(0, 'Date', df['Date'])

    print(df_normalized)

    X = []
    y = []
    for i in range(30, len(df)):
        X.append(df_normalized.iloc[i-30:i, 1:6].values)  # 输入数据未取到i时刻
        y.append(df_normalized.iloc[i, 4])  # 标签数据为i时刻
    X=torch.tensor(X,dtype=torch.float)
    y = torch.tensor(y, dtype=torch.float).view(-1, 1)
    print(X.shape)
    print(y.shape)

    N = -200
    X_train, X_test = X[:N], X[N:]
    y_train, y_test = y[:N], y[N:]
    trainloader = DataLoader(TensorDataset(X_train, y_train), 64, True)
    print(X_train.shape,X_test.shape)

    modelDNN = ModelDNN(30*5)
    optimizer = optim.Adam(modelDNN.parameters())
    criterion = nn.MSELoss()

   # 存储预测值和实际值
train_preds = []
test_preds = []
y_train_actual = y_train.clone().numpy()
y_test_actual = y_test.clone().numpy()
# 初始化模型、损失函数和优化器
modelDNN = ModelDNN(input_size=30*5)
optimizer = optim.Adam(modelDNN.parameters())
criterion = nn.MSELoss()

# 训练模型
for i in tqdm(range(100)):
    for X, y in trainloader:
        y_pred = modelDNN(X)
        loss = criterion(y_pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    if (i+1) % 10 == 0:
        with torch.no_grad():
            train_pred = modelDNN(X_train)
            train_mse = criterion(train_pred, y_train)
            test_pred = modelDNN(X_test)
            test_mse = criterion(test_pred, y_test)
            print(i, train_mse.item(), test_mse.item())

# 使用模型进行最终预测
with torch.no_grad():
    final_train_pred = modelDNN(X_train)
    final_test_pred = modelDNN(X_test)

# 将预测值和实际值转换为一维数组，以便绘图
final_train_pred = final_train_pred.view(-1).numpy()
final_test_pred = final_test_pred.view(-1).numpy()
y_train_actual = y_train.view(-1).numpy()
y_test_actual = y_test.view(-1).numpy()

# 绘制训练集和测试集的预测曲线与实际曲线
plt.figure(figsize=(14, 7))

# 绘制训练集预测曲线和实际曲线
plt.subplot(1, 2, 1)
plt.plot(y_train_actual, label='Actual Train', color='blue')
plt.plot(final_train_pred, label='Predicted Train', color='red')
plt.xlabel('Sample index')
plt.ylabel('Value')
plt.title('Train Prediction vs Actual')
plt.legend()

# 绘制测试集预测曲线和实际曲线
plt.subplot(1, 2, 2)
plt.plot(y_test_actual, label='Actual Test', color='blue')
plt.plot(final_test_pred, label='Predicted Test', color='red')
plt.xlabel('Sample index')
plt.ylabel('Value')
plt.title('Test Prediction vs Actual')
plt.legend()

plt.tight_layout()
plt.savefig('final_prediction_vs_actual.png')