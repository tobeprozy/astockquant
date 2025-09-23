#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票分析与交易信号通知系统
功能：使用qdata获取股票数据，qstrategy计算买卖信号，qplot绘制K线图并标记信号，最后发送邮件通知
"""

import os
import sys
import logging

# 导入必要的模块
import qdata
import qstrategy
import qplot
import pandas as pd
from datetime import datetime, timedelta
from qbackengine.emailer import SmtpEmailer
# 导入 PyechartsChart_1 类
from qplot.backends.pyecharts.chart_1 import PyechartsChart_1

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stock_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self, stock_code, start_date, end_date, strategy_name='sma_cross', 
                 strategy_params=None, email_config=None):
        """
        初始化股票分析器
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategy_name: 策略名称
            strategy_params: 策略参数
            email_config: 邮件配置
        """
        self.stock_code = stock_code
        self.start_date = start_date
        self.end_date = end_date
        self.strategy_name = strategy_name
        self.strategy_params = strategy_params or {'fast_period': 5, 'slow_period': 20}
        self.email_config = email_config or {
            'smtp_host': 'smtp.163.com',
            'smtp_port': 465,
            'username': 'tobeprozy@163.com',
            'password': 'BHrMkpZZvm8frpWY',
            'from_addr': 'tobeprozy@163.com',
            'to_addrs': '904762096@qq.com'
        }
        
        # 初始化各模块
        qdata.init()
        # qdata.set_current_provider('akshare') - 这个函数不存在，qdata.init()已经设置了默认数据源为akshare
        logger.info("qdata 初始化完成，数据源设置为 akshare")
        # qstrategy.init()
        
        # 创建输出目录
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 存储结果
        self.data = None
        self.signals = None
        self.plot_file = None
    
    def fetch_data(self):
        """获取股票数据"""
        logger.info(f"正在获取股票 {self.stock_code} 从 {self.start_date} 到 {self.end_date} 的数据...")
        try:
            # 使用qdata获取日线数据
            self.data = qdata.get_daily_data(self.stock_code, self.start_date, self.end_date)
            
            if self.data is None or self.data.empty:
                logger.error(f"未获取到股票 {self.stock_code} 的数据")
                return False
            
            logger.info(f"成功获取数据，数据量: {len(self.data)}行")
            logger.debug(f"数据前5行:\n{self.data.head()}")
            return True
        except Exception as e:
            logger.error(f"获取数据时出错: {e}")
            return False
    
    def generate_signals(self):
        """生成交易信号"""
        if self.data is None or self.data.empty:
            logger.error("请先获取数据")
            return False
        
        logger.info(f"正在使用 {self.strategy_name} 策略生成交易信号...")
        try:
            # 创建并初始化策略
            strategy = qstrategy.get_strategy(
                self.strategy_name, 
                **self.strategy_params, 
                printlog=True
            )
            
            # 初始化策略数据 - 修正方法名：init_data 而不是 init_strategy
            strategy.init_data(self.data)
            
            # 生成交易信号
            self.signals = strategy.generate_signals()
            
            logger.info(f"生成的买入信号数量: {len(self.signals['buy_signals'])}")
            logger.info(f"生成的卖出信号数量: {len(self.signals['sell_signals'])}")
            
            # 打印所有买入信号时间
            if len(self.signals['buy_signals']) > 0:
                logger.info(f"买入信号时间列表：")
                for signal_date in self.signals['buy_signals']:
                    logger.info(f"  - {signal_date}")
                logger.debug(f"部分买入信号日期：{self.signals['buy_signals'][:3]}")
            
            # 打印所有卖出信号时间
            if len(self.signals['sell_signals']) > 0:
                logger.info(f"卖出信号时间列表：")
                for signal_date in self.signals['sell_signals']:
                    logger.info(f"  - {signal_date}")
                logger.debug(f"部分卖出信号日期：{self.signals['sell_signals'][:3]}")
            
            return True
        except Exception as e:
            logger.error(f"生成交易信号时出错: {e}")
            return False
    
    def plot_and_save(self):
        """绘制K线图并保存"""
        if self.data is None or self.data.empty:
            logger.error("请先获取数据")
            return False
        
        if self.signals is None:
            logger.error("请先生成交易信号")
            return False
        
        logger.info(f"正在绘制股票 {self.stock_code} 的K线图并标记交易信号...")
        try:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d')
            self.plot_file = os.path.join(self.output_dir, f"{self.stock_code}_{timestamp}_kline.png")
            
            # 计算均线数据
            def calculate_ma(df, periods=[5, 10, 20]):
                ma_data = {}
                for period in periods:
                    ma_column = f'MA{period}'
                    df[ma_column] = df['close'].rolling(window=period).mean()
                    ma_data[ma_column] = df[ma_column].tolist()
                return ma_data
            
            ma_data = calculate_ma(self.data)
            
            # 格式化买卖信号数据
            # 从 self.signals 中提取买点和卖点
            signal_points = {'buy': [], 'sell': []}
            
            # 格式化日期并添加买点
            for buy_date in self.signals['buy_signals']:
                # 将日期转换为字符串格式
                date_str = str(pd.to_datetime(buy_date).date())
                # 查找该日期在数据中的位置
                if date_str in [str(idx.date()) for idx in self.data.index]:
                    # 获取该日期的最低价并稍微降低作为买点标记位置
                    date_idx = self.data.index.get_loc(pd.to_datetime(buy_date))
                    buy_price = self.data.iloc[date_idx]['low'] * 0.99
                    signal_points['buy'].append((date_str, buy_price))
            
            # 格式化日期并添加卖点
            for sell_date in self.signals['sell_signals']:
                # 将日期转换为字符串格式
                date_str = str(pd.to_datetime(sell_date).date())
                # 查找该日期在数据中的位置
                if date_str in [str(idx.date()) for idx in self.data.index]:
                    # 获取该日期的最高价并稍微提高作为卖点标记位置
                    date_idx = self.data.index.get_loc(pd.to_datetime(sell_date))
                    sell_price = self.data.iloc[date_idx]['high'] * 1.01
                    signal_points['sell'].append((date_str, sell_price))
            
            # 创建PyechartsChart_1实例
            chart = PyechartsChart_1(
                chart_type='kline',
                data=self.data,
                title=f"{self.stock_code} 日K线图 (买卖信号标记)"
            )
            
            # 绘制K线图并标记买卖信号
            chart.chart = chart.draw_klines(
                self.data,
                ma_data=ma_data,
                signal_points=signal_points
            )
            
            # 保存为图片
            result = chart.save(self.plot_file)
            
            if os.path.exists(self.plot_file):
                logger.info(f"K线图已保存至: {self.plot_file}")
                return True
            else:
                logger.error("保存图片失败")
                return False
        except Exception as e:
            logger.error(f"绘制K线图时出错: {e}")
            return False
    
    def send_email(self):
        """发送邮件（注意：当前SmtpEmailer不支持附件）"""
        if self.plot_file is None or not os.path.exists(self.plot_file):
            logger.warning("K线图文件不存在，将只发送邮件内容")
            
        logger.info("正在发送邮件...")
        try:
            # 创建邮件发送器
            emailer = SmtpEmailer(
                smtp_host=self.email_config['smtp_host'],
                smtp_port=self.email_config['smtp_port'],
                username=self.email_config['username'],
                password=self.email_config['password'],
                from_addr=self.email_config['from_addr'],
                to_addrs=self.email_config['to_addrs']
            )
            
            # 准备邮件内容
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subject = f"股票分析报告 - {self.stock_code} - {current_time}"
            
            # 构建邮件正文
            body = f"""股票分析报告\n\n"""
            body += f"股票代码: {self.stock_code}\n"
            body += f"分析区间: {self.start_date} 至 {self.end_date}\n"
            body += f"使用策略: {self.strategy_name}\n"
            body += f"策略参数: {self.strategy_params}\n\n"
            body += f"买入信号数量: {len(self.signals['buy_signals'])}\n"
            body += f"卖出信号数量: {len(self.signals['sell_signals'])}\n\n"
            if self.plot_file and os.path.exists(self.plot_file):
                body += f"K线图已保存至本地: {self.plot_file}\n\n"
            body += f"报告生成时间: {current_time}\n"
            
            # 发送邮件（不包含附件，因为当前SmtpEmailer不支持）
            emailer.send(
                subject=subject,
                body=body
            )
            
            logger.info(f"邮件已成功发送至: {self.email_config['to_addrs']}")
            return True
        except Exception as e:
            logger.error(f"发送邮件时出错: {e}")
            return False
    
    def run(self):
        """运行完整流程"""
        logger.info(f"开始股票分析流程 - 股票代码: {self.stock_code}")
        
        # 1. 获取数据
        if not self.fetch_data():
            return False
        
        # 2. 生成交易信号
        if not self.generate_signals():
            return False
        
        # 3. 绘制并保存K线图
        if not self.plot_and_save():
            return False
        
        # 4. 发送邮件
        if not self.send_email():
            return False
        
        logger.info("股票分析流程已成功完成")
        return True

def main():
    """主函数"""
    # 设置默认参数
    stock_code = "600519"  # 贵州茅台
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 初始化分析器
    analyzer = StockAnalyzer(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        strategy_name='sma_cross',
        strategy_params={'fast_period': 5, 'slow_period': 20}
    )
    
    # 运行分析流程
    analyzer.run()

if __name__ == '__main__':
    main()