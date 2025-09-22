#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仪表盘图表功能示例

这个示例展示如何使用 PyechartsChart_1 类来创建仪表盘图表并将其保存为图片
"""

import os
from qplot.backends.pyecharts.chart_1 import PyechartsChart_1


def main():
    """主函数"""
    print("开始测试仪表盘图表功能...")
    
    # 创建output目录（如果不存在）
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建仪表盘图表
    gauge_chart = PyechartsChart_1('gauge', value=85, title="电池电量仪表图", subtitle="测试示例")
    gauge_chart.plot()
    
    # 保存为HTML
    html_path = os.path.join(output_dir, 'gauge_chart.html')
    gauge_chart.save(html_path)
    print(f"已生成HTML文件: {html_path}")
    
    # 保存为图片
    image_path = os.path.join(output_dir, 'gauge_chart.png')
    gauge_chart.save(image_path)
    
    # 判断图片是否保存成功
    if os.path.isfile(image_path):
        print(f"✅ 成功生成图片: {os.path.abspath(image_path)}")
    else:
        print("❌ 图片保存失败")
    
    print("\n提示：\n")
    print("如需保存图片功能，请确保已安装必要依赖:")
    print("   pip install snapshot-selenium selenium")
    print("并安装对应的浏览器驱动")
    

if __name__ == '__main__':
    main()