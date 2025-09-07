import sqlite3

import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root) 
from adapters.akshare_provider import AkshareFundProvider
import datetime
import pandas as pd



def create_table_from_df(df, conn, table_name):
    # 构建创建表的 SQL 语句
    columns = []
    for column_name, dtype in zip(df.columns, df.dtypes):
        dtype = 'TEXT' if dtype == object else 'REAL'
        columns.append(f"{column_name} {dtype}")
    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
    conn.execute(sql)

def insert_data_from_df(df, conn, table_name):
    placeholders = ', '.join(['?'] * len(df.columns))
    columns = ', '.join(df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    for row in df.itertuples(index=False, name=None):
        conn.execute(sql, row)
    conn.commit()


def save_db(db_name,df):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_name)
    # 创建表
    create_table_from_df(df, conn, "fund_data")

    # 插入数据
    insert_data_from_df(df, conn, "fund_data")

    # 关闭Connection:
    conn.close()


def get_fund_data(stock_index,s_date,e_date):
    provider = AkshareFundProvider()
    df = provider.fetch(symbol=stock_index, start_date=s_date, end_date=e_date)
    # provider 返回标准英文列并以日期索引；保存前恢复为列并匹配原列名
    df = df.reset_index().rename(columns={'date':'date','open':'open','high':'high','low':'low','close':'close','volume':'vol'})
    return df
    

def load_db_to_dataframe(db_name):
    # 连接到 SQLite 数据库文件
    conn = sqlite3.connect(db_name)
    # 编写 SQL 查询语句
    query = "SELECT * FROM fund_data"

    # 使用 Pandas 的 read_sql_query 函数加载数据
    df = pd.read_sql_query(query, conn)

    # 显示 DataFrame
    print(df)


if __name__ ==  "__main__":

    stock_index = '512200'

    s_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y%m%d')
    e_date = datetime.datetime.now().strftime('%Y%m%d')

    df=get_fund_data(stock_index,s_date,e_date)
    
    print(df)

    save_db(f"{stock_index}.db",df)

    load_db_to_dataframe(f"{stock_index}.db")




    