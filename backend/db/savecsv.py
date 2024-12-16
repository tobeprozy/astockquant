import sqlite3

import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root) 
from get_data.ak_data_fetch import FinancialDataFetcher
import datetime
import pandas as pd



def process_stocks(stocks, s_date, e_date):
    all_features = []
    all_labels = []
    for i,stock in enumerate(stocks):
        if i>=10:
            break
        stock_index = stock['基金代码']
        features, labels = load_and_process_stock_data(stock_index, s_date, e_date)
        all_features.append(features)
        all_labels.extend(labels)
    return all_features, all_labels

def get_fund_data(stock_index,s_date,e_date):
    # 创建数据获取器
    fetcher = FinancialDataFetcher()
    # 获取股票数据
    fetcher.fetch_fund_info(symbol=stock_index, start_date=s_date, end_date=e_date)
    fetcher.fund_rename()
    return fetcher.fund_info

import json
import time
import os
if not os.path.exists("./origin_data"):
    os.makedirs("./origin_data")

# 选择要保存的列
columns_to_save = ['date', 'open', 'close', 'high', 'low', 'vol']

# 保存到CSV文件


def preprocess_data():
    # 指定包含CSV文件的文件夹路径
    source_folder_path = './origin_data'  # 替换为包含CSV文件的文件夹路径
    new_folder_path = './ETF'  # 归一化后的数据将保存到这个新文件夹

    # 确保新文件夹存在，如果不存在则创建
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    csv_filenames=[]
    # 遍历文件夹中的所有CSV文件
    for filename in os.listdir(source_folder_path):
        df1=pd.DataFrame()
        if filename.endswith('.csv'):
            # 获取文件名（不包括扩展名）
            file_name_without_extension = os.path.splitext(filename)[0]
            # 添加到列表中
            csv_filenames.append(file_name_without_extension)
            
            # 构建完整的文件路径
            file_path = os.path.join(source_folder_path,filename)
            # 读取CSV文件
            df = pd.read_csv(file_path)
            # 确保列存在
            if all(col in df.columns for col in ['open', 'close', 'high', 'low', 'vol']):
                # 找到open, close, high, low的最大值
                max_value = df[['open', 'close', 'high', 'low']].max().max()
                # 归一化open, close, high, low列
                df1['date']=df['date']
                df1[['open', 'close', 'high', 'low']] = df[['open', 'close', 'high', 'low']] / max_value
                # 找到vol的最大值
                max_vol = df['vol'].max()
                # 归一化vol列
                df1['volume'] = df['vol'] / max_vol

                df1['dopen'] = df1['open'].diff()
                df1['dclose'] = df1['close'].diff()
                df1['dhigh'] = df1['high'].diff()
                df1['dlow'] = df1['low'].diff()
                df1['dvolume'] = df1['low'].diff()
                # 删除第一行，因为差值计算会导致第一行的值为NaN
                df1 = df1.iloc[1:]
                df=df.iloc[1:]
                df1['price']=df['close']
                # 指定新文件的路径
                new_file_path = os.path.join(new_folder_path, filename)
                
                print(df1.iloc[0].date)
                # 保存到新文件夹
                df1.to_csv(new_file_path, index=True)
                print(f"归一化后的DataFrame已保存到：{new_file_path}")
            else:
                print(f"CSV文件 {filename} 中缺少必要的列。")
        else:
            continue  # 如果不是CSV文件，则跳过
    # 将列表保存为JSON文件
    with open("fund_list2.json", 'w', encoding='utf-8') as json_file:
        json.dump(csv_filenames, json_file, ensure_ascii=False, indent=4)

    print(f"文件名列表已保存到JSON文件:fund_list2.json")
if __name__ == "__main__":
    # s_date = (datetime.datetime.now() - datetime.timedelta(days=5200)).strftime('%Y%m%d')
    s_date = "20120925"
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    fetcher = FinancialDataFetcher()
    fund_info=fetcher.fetch_fund_list()
    fetcher.save_fund_list("fund_list.json")

    with open("fund_list.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, item in enumerate(data):
        if i < 200:  # 只遍历前五个
            print(item['基金代码'])
            df=get_fund_data(item['基金代码'],s_date=s_date,e_date=e_date)
            # time.sleep(2)
            print(df)
            print(f"size:{df.index.size}")
            if df.index.size == 0:  # 如果DataFrame没有列，即为空
                continue  # 跳过当前迭代
            if pd.to_datetime(df.iloc[0].date).strftime('%Y%m%d') != s_date:
                print(f"date error:{s_date}")
                continue
            index=item['基金代码']
            save_path=os.path.join("./origin_data/",f"{index}.csv")
            df.to_csv(save_path, columns=columns_to_save, index=False)
            
        else:
            break 
    
    preprocess_data()