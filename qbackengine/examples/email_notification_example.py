#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
邮件通知功能示例
展示如何使用qbackengine的邮件通知功能在回测完成后发送结果邮件
"""

import qbackengine
import logging
from qbackengine.emailer import SmtpEmailer

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数：运行带邮件通知的回测"""
    print("===== 邮件通知功能示例 ====")
    
    # 创建邮件发送器（注意：需要配置SMTP环境变量）
    try:
        emailer = SmtpEmailer()
        print("邮件发送器初始化成功！")
        
        # 创建带邮件通知功能的回测引擎
        engine = qbackengine.create_backtrader_engine(
            symbol='600000',  # 茅台股票代码
            start_date='2024-01-01',
            end_date='2024-12-31',
            strategy_name='MA_Cross',  # 使用qstrategy中的MA_Cross策略
            starting_cash=100000.0,
            commission=0.00025,
            email_on_finish=True,
            emailer=emailer,
            strategy_kwargs={
                'fast_period': 5,
                'slow_period': 20,
                'printlog': True
            }
        )
        
        # 运行回测
        result = engine.run()
        
        # 打印回测结果
        print("\n回测结果摘要：")
        engine.print_results(result)
        
        # 绘制回测结果图表
        engine.plot()
        
        print("\n邮件通知功能示例完成！")
        print("注意：如果配置了正确的SMTP环境变量，回测结果邮件将已发送。")
        
    except Exception as e:
        print(f"初始化邮件发送器失败: {e}")
        print("请设置以下环境变量以使用邮件通知功能:")
        print("- SMTP_HOST: SMTP服务器地址")
        print("- SMTP_PORT: SMTP服务器端口")
        print("- SMTP_USER: 邮箱用户名")
        print("- SMTP_PASS: 邮箱密码/授权码")
        print("- SMTP_FROM: 发件人邮箱")
        print("- SMTP_TO: 收件人邮箱")
        print("\n或者可以使用以下方式直接配置邮件发送器:")
        print("emailer = SmtpEmailer(smtp_host='your_smtp_host', ...)")

if __name__ == '__main__':
    main()