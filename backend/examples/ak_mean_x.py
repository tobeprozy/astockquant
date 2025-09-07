import matplotlib.pyplot as plt
import os
import sys

# 获取当前文件的目录
cur_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root = os.path.abspath(os.path.join(cur_dir, '..'))
# 将项目根目录添加到 sys.path
if root not in sys.path:
    sys.path.append(root)


from adapters.akshare_provider import AkshareFundProvider


if __name__ == "__main__":
    provider = AkshareFundProvider()
    stock_data = provider.fetch(symbol="600519", start_date='20240101', end_date='20241207')
    etf_data = provider.fetch(symbol="511220", start_date='20240101', end_date='20241207')

    data = stock_data.reset_index()

    # caculate mean value of 1, 5, 10 days
    data['1'] = data['close']
    data['5'] = data['close'].rolling(5).mean()
    data['10'] = data['close'].rolling(10).mean()

    data['Signal'] = 0
    # 短期均线上穿长期均线，产生买入信号
    data.loc[data['5'] > data['10'], 'Signal'] = 1
    # 短期均线下穿长期均线，产生卖出信号
    data.loc[data['5'] < data['10'], 'Signal'] = -1

    data['Daily_Return'] = data['close'].pct_change()
    data['Strategy_Return'] = data['Daily_Return'] * data['Signal'].shift(1)
    data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod() - 1


    plt.figure(figsize=(10, 6))
    plt.plot(data['Cumulative_Return'], label='Strategy Return', color='b')
    plt.plot(data['close'] / data['close'].iloc[0], label='Stock', color='g')
    plt.title("Strategy Return vs. Stock")
    plt.xlabel("Date")
    plt.ylabel("Strategy Cumulative Return")
    plt.legend()

    # 保存图形到文件
    plt.savefig('strategy_vs_stock.png', bbox_inches='tight')
    plt.close()  # 关闭图形，避免内存浪费