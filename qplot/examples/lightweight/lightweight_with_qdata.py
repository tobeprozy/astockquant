"""lightweight-charts 简单使用示例
https://pypi.org/project/lightweight-charts/
https://lightweight-charts-python.readthedocs.io/en/latest/tutorials/getting_started.html

此示例展示如何使用 qdata 获取股票数据并使用 lightweight-charts 绘制图表。
使用前请确保已安装所需库：
pip install lightweight-charts qdata
"""

import qdata
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from lightweight_charts import Chart

# 初始化 qdata
def init_qdata():
    """初始化 qdata 包"""
    try:
        qdata.init()
        print("成功初始化 qdata 包")
        # 设置为 akshare 数据源（默认且免费）
        qdata.set_current_provider('akshare')
        print("已设置数据源为 akshare")
        return True
    except Exception as e:
        print(f"初始化 qdata 失败: {e}")
        return False

# 使用 qdata 获取数据并保存到 CSV
def get_data_and_save_to_csv(code="000001", start_date="20180701", end_date="20240510"):
    """使用 qdata 获取数据并保存到 CSV 文件"""
    print(f"正在获取股票 {code} 的数据...")
    
    try:
        # 使用 qdata 获取日线数据
        # 需要将日期格式从 'YYYYMMDD' 转换为 'YYYY-MM-DD'
        start_date_formatted = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_formatted = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        df = qdata.get_daily_data(code, start_date_formatted, end_date_formatted, backend='akshare')
        print(f"成功获取数据，数据量: {len(df)}行")
        
        # 处理数据格式
        if 'date' not in df.columns and df.index.name == 'date':
            df = df.reset_index()
        
        # 确保日期列正确
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        elif 'trade_date' in df.columns:
            df['date'] = pd.to_datetime(df['trade_date'])
        
        # 按日期排序
        df = df.sort_values(by="date", ascending=True)
        
        # 重命名列（如果需要）
        if 'vol' in df.columns and 'volume' not in df.columns:
            df.rename(columns={"vol": "volume"}, inplace=True)
        
        # 选择需要的列
        required_columns = [col for col in ["date", "open", "high", "low", "close", "volume"] if col in df.columns]
        df = df[required_columns]
        
        # 保存到 CSV
        csv_file = f"D_{code}.csv"
        df.to_csv(csv_file, index=False)
        print(f"数据已保存到 {csv_file}")
        
        return csv_file
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None

# 示例1：基本图表绘制
def basic_chart_example(csv_file):
    """示例1：基本图表绘制"""
    print("\n=== 示例1：基本图表绘制 ===")
    
    try:
        chart = Chart()
        df = pd.read_csv(csv_file)
        chart.set(df)
        chart.show(block=True)
    except Exception as e:
        print(f"绘制图表时出错: {e}")

# 示例2：逐步更新图表数据
def update_chart_example(csv_file):
    """示例2：逐步更新图表数据"""
    print("\n=== 示例2：逐步更新图表数据 ===")
    
    try:
        chart = Chart()
        df = pd.read_csv(csv_file)
        chart.set(df.iloc[:-10])
        chart.show(block=False)
        
        # 逐步更新最后10条数据
        for i, bar in df.iloc[-10:].iterrows():
            chart.update(bar)
            time.sleep(1)
        
        # 等待用户按键
        input("按Enter键继续...")
    except Exception as e:
        print(f"更新图表时出错: {e}")

# 示例3：使用日期格式绘制图表
def date_format_chart_example(csv_file):
    """示例3：使用日期格式绘制图表"""
    print("\n=== 示例3：使用日期格式绘制图表 ===")
    
    try:
        chart = Chart()
        df = pd.read_csv(csv_file, parse_dates=["date"])
        chart.set(df)
        chart.show(block=True)
    except Exception as e:
        print(f"绘制日期格式图表时出错: {e}")

# 示例4：模拟实时更新
def realtime_simulation_example(csv_file):
    """示例4：模拟实时更新"""
    print("\n=== 示例4：模拟实时更新 ===")
    
    try:
        chart = Chart()
        df = pd.read_csv(csv_file, parse_dates=["date"])
        chart.set(df)
        chart.show(block=False)
        
        # 获取最后一条数据的时间和价格
        last_time = df.iloc[-1]["date"] + timedelta(days=1)
        last_price = df.iloc[-1]["close"]
        
        print("开始模拟实时更新（按Ctrl+C停止）...")
        
        # 模拟实时更新
        try:
            while True:
                time.sleep(0.1)
                
                # 随机生成价格变化
                change_percent = 0.002
                change = last_price * random.uniform(-change_percent, change_percent)
                new_price = last_price + change
                new_time = pd.to_datetime(last_time) + timedelta(hours=1)
                
                # 创建新的tick数据
                tick = pd.Series({"time": new_time, "price": new_price})
                
                # 更新图表
                chart.update_from_tick(tick)
                
                # 更新最后价格和时间
                last_price = new_price
                last_time = new_time
        except KeyboardInterrupt:
            print("模拟实时更新已停止")
    except Exception as e:
        print(f"模拟实时更新时出错: {e}")

# 主函数
def main():
    """主函数"""
    print("===== lightweight-charts 简单使用示例 =====")
    
    # 初始化 qdata
    if not init_qdata():
        print("警告：qdata 初始化失败，示例可能无法正常运行")
    
    # 获取数据并保存到 CSV
    csv_file = get_data_and_save_to_csv(code="000001", start_date="20180701", end_date="20240510")
    
    if csv_file:
        # 运行各个示例
        basic_chart_example(csv_file)
        update_chart_example(csv_file)
        date_format_chart_example(csv_file)
        realtime_simulation_example(csv_file)
        
        print("\n所有示例运行完毕！")
    else:
        print("无法获取数据，示例无法运行")

if __name__ == "__main__":
    main()