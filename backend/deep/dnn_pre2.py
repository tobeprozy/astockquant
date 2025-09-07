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
    # 保持与旧逻辑兼容
    df = df.reset_index()
    df = df[['date','open','close','high','low','volume']]
    df.columns = [
        'Date',
        'Open',
        'Close',
        'High',
        'Low',
        'Vol',
    ]
    return df


# 定义模型
class ModelDNN(nn.Module):
    def __init__(self, input_size):
        super(ModelDNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)  # 输出一个值，表示上涨的概率

    def forward(self, x):
        # 展平输入张量
        x = x.view(x.size(0), -1)  # 将 (batch_size, 30, 5) 转换为 (batch_size, 150)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)  # 直接输出
        return x

if __name__ == "__main__":
    # 设置日期范围
    s_date = (datetime.datetime.now() - datetime.timedelta(days=3000)).strftime('%Y-%m-%d')
    e_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # 获取数据
    provider = AkshareFundProvider()
    df_raw = provider.fetch(symbol="159892", start_date=s_date.replace('-', ''), end_date=e_date.replace('-', ''))
    df = adapt_backtrader(df_raw)
    print(df.shape)

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

    # 准备输入特征和标签
    X = []
    y = []

    # 只关注当前日的特征和下一日的涨跌情况
    for i in range(14, len(df_normalized) - 1):  # -1 是为了确保可以取到未来一天的数据
        X.append(df_normalized.iloc[i-14:i, 1:6].values)  # 输入数据为过去30天的Open, Close, High, Low, Vol
        # 标签数据为下一天的涨跌情况
        if df_normalized.iloc[i + 1, 4] > df_normalized.iloc[i, 4]:  # 比较下一天的收盘价
            y.append(1)  # 涨
        else:
            y.append(0)  # 跌

    X = torch.tensor(X, dtype=torch.float)
    y = torch.tensor(y, dtype=torch.float).view(-1, 1)  # 变为列向量
    print(X.shape)
    print(y.shape)

    # 划分训练集和测试集
    N = -200  # 取最后200个样本作为测试集
    X_train, X_test = X[:N], X[N:]
    y_train, y_test = y[:N], y[N:]
    trainloader = DataLoader(TensorDataset(X_train, y_train), batch_size=64, shuffle=True)
    print(X_train.shape, X_test.shape)

    # 初始化模型、损失函数和优化器
    modelDNN = ModelDNN(input_size=14 * 5)  # 输入大小应为 30 * 5
    optimizer = optim.Adam(modelDNN.parameters(), lr=0.001)
    criterion = nn.BCEWithLogitsLoss()  # 使用适合二分类的损失函数

    # 训练模型
    for i in tqdm(range(100)):  # 训练100轮
        modelDNN.train()  # 设置模型为训练模式
        for X_batch, y_batch in trainloader:
            y_pred = modelDNN(X_batch)
            loss = criterion(y_pred, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        # 每10个epoch输出一次训练和测试损失
        if (i + 1) % 10 == 0:
            with torch.no_grad():
                train_pred = modelDNN(X_train)
                train_mse = criterion(train_pred, y_train)
                test_pred = modelDNN(X_test)
                test_mse = criterion(test_pred, y_test)
                print(f'Epoch {i + 1}, Train Loss: {train_mse.item():.4f}, Test Loss: {test_mse.item():.4f}')


    # 检查长度
    print(f"Length of X: {len(X)}, Length of y: {len(y)}")

    # 进行预测，从第30天开始
    modelDNN.eval()
    with torch.no_grad():
        all_predictions = []
        for i in range(len(X)):
            pred = modelDNN(X[i].unsqueeze(0))  # 添加一个批次维度
            all_predictions.append(torch.sigmoid(pred).item())

   # 确保预测结果的长度与日期长度一致
    start_index = 14  # 从第30天开始
    predicted_df = pd.DataFrame({
        'Date': df_normalized['Date'].iloc[start_index:len(all_predictions) + start_index].values,  # 从第30天开始的日期
        'Predicted': all_predictions
    })

    # 计算实际涨跌情况
    df_normalized['Price Change'] = df_normalized['Close'].diff()
    df_normalized['Actual Direction'] = (df_normalized['Price Change'] > 0).astype(int)  # 1:上涨, 0:下跌

    # 确保实际方向的长度与预测方向的长度一致
    predicted_df['Actual Direction'] = df_normalized['Actual Direction'].iloc[start_index:start_index + len(all_predictions)].values

    # 计算预测的方向
    predicted_df['Predicted Direction'] = (predicted_df['Predicted'] > 0.5).astype(int)  # 1:上涨, 0:下跌

    # 计算准确率
    correct_predictions = (predicted_df['Predicted Direction'].values == predicted_df['Actual Direction'].values)
    accuracy = correct_predictions.mean()

    # 打印准确率
    print(f'Prediction Accuracy: {accuracy * 100:.2f}%')

    # 绘制结果
    plt.figure(figsize=(14, 7))
    plt.plot(df_normalized['Date'], df_normalized['Close'], label='Actual Close Price', color='blue', alpha=0.5)
    plt.plot(predicted_df['Date'], predicted_df['Predicted'], label='Predicted Price', color='orange', alpha=0.7)

    # 添加图例和标题
    plt.title(f'Stock Price Prediction (Accuracy: {accuracy * 100:.2f}%)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 保存图像
    plt.savefig('stock_price_prediction_accuracy.png')  # 保存为 PNG 文件