import matplotlib.pyplot as plt
import os
import sys
import json
# 获取当前文件的目录
cur_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root = os.path.abspath(os.path.join(cur_dir, '..'))
# 将项目根目录添加到 sys.path
if root not in sys.path:
    sys.path.append(root)


from get_data.ak_data_fetch import FinancialDataFetcher

# 定义一个字典，将中文列标题映射到英文列标题
columns_mapping = {
    '日期': 'Date',
    '开盘': 'Open',
    '收盘': 'Close',
    '最高': 'High',
    '最低': 'Low',
    '成交量': 'Volume',
    '成交额': 'Turnover',
    '振幅': 'Amplitude',
    '涨跌幅': 'ChangePercent',
    '涨跌额': 'ChangeAmount',
    '换手率': 'TurnoverRate'
}



if __name__ == "__main__":

    fetcher = FinancialDataFetcher()
    # stock_info=fetcher.fetch_stock_list()
    # fund_info=fetcher.fetch_fund_list()
    # print(fetcher.filter_funds_by_name(fetcher.fund_list,"医药"))
    
    # fetcher.save_stock_list("stock_list.json")
    # fetcher.save_fund_list("fund_list.json")

    with open("fund_list.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df=[]
    for i, item in enumerate(data):
        if i < 1:  # 只遍历前五个
            print(item)
            df=fetcher.fetch_fund_info(symbol=item['基金代码'])
            print(df)

        else:
            break

    # 使用rename方法更新列标题
    df.rename(columns=columns_mapping, inplace=True)
    import pandas as pd
    # 确保 Date 列是 datetime 类型
    df['Date'] = pd.to_datetime(df['Date'])

    import pandas as pd
    from pyecharts import options as opts
    from pyecharts.charts import Kline
    # 准备 K线图数据
    kline_data = [
        [row['Open'], row['Close'], row['Low'], row['High']]
        for _, row in df.iterrows()
    ]

    # 创建 K线图
    c = (
        Kline()
        .add_xaxis(df['Date'].dt.strftime('%Y/%m/%d').tolist())  # 格式化日期
        .add_yaxis("Kline", kline_data)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
            title_opts=opts.TitleOpts(title="Kline Chart Example"),
        )
        .render("Kline_Chart.html")  # 输出到 HTML 文件
    )

    print("K线图已生成并保存为 Kline_Chart.html")