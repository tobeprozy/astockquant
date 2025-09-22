#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Longbridge API示例
注意：运行此示例需要安装longport模块和配置API密钥
安装命令: pip install longport
配置信息: 请替换下面的app_key、app_secret和access_token
"""

import sys
import time

try:
    from longport.openapi import TradeContext, QuoteContext, Config, SubType, PushQuote
except ImportError:
    print("错误: 缺少必要的依赖包。")
    print("请运行: pip install longport")
    sys.exit(1)


def main():
    # 配置信息（需要替换为实际的API密钥）
    config = Config(app_key="xx", app_secret="xx", 
                    access_token="xx")

    try:
        # 创建交易上下文并获取账户余额
        ctx = TradeContext(config)
        resp = ctx.account_balance()
        print("账户余额信息:")
        print(resp)

        # 定义行情回调函数
        def on_quote(symbol: str, quote: PushQuote):
            print(f"\n收到{symbol}行情:")
            print(quote)
        
        # 创建行情上下文并订阅行情
        quote_ctx = QuoteContext(config)
        quote_ctx.set_on_quote(on_quote)
        symbols = ["700.HK"]  # 腾讯控股
        print(f"\n订阅{symbols}行情...")
        quote_ctx.subscribe(symbols, [SubType.Quote], True)
        
        # 等待接收行情数据
        print("等待30秒接收行情数据...")
        time.sleep(30)
        
    except Exception as e:
        print(f"错误: {e}")
        print("请确保您的API密钥正确配置并且网络连接正常。")


if __name__ == "__main__":
    print("=== Longbridge API示例开始 ===")
    main()
    print("=== Longbridge API示例结束 ===")