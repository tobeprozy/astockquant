import matplotlib.pyplot as plt

def plot_data(data):
    # 示例绘图函数
    plt.figure(figsize=(10, 5))
    plt.plot(data['dates'], data['prices'], label='Price')
    plt.title('Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def plot_indicator(data, indicator):
    # 示例绘图函数，绘制指标
    plt.figure(figsize=(10, 5))
    plt.plot(data['dates'], indicator, label='Indicator')
    plt.title(f'{indicator} Over Time')
    plt.xlabel('Date')
    plt.ylabel(indicator)
    plt.legend()
    plt.show()
