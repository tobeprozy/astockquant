#!/usr/bin/env python3
import sys
import time
import random
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import pandas as pd
import numpy as np

# 生成模拟股票数据
def generate_sample_stock_data(symbol='AAPL', days=365):
    """生成模拟的股票OHLCV数据"""
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # 创建日期范围
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # B=工作日
    
    # 随机生成开盘价，基于某个基准值
    base_price = random.uniform(100, 200)
    returns = np.random.normal(0, 0.02, len(dates))
    
    # 计算价格序列
    close_prices = base_price * (1 + returns).cumprod()
    
    # 生成OHLC数据 - 使用numpy方法而不是pandas的shift
    open_prices = np.copy(close_prices)
    # 将第一个元素设置为base_price，其他元素使用前一天的收盘价
    open_prices[1:] = close_prices[:-1]
    open_prices[0] = base_price
    
    # 生成最高价和最低价
    high_prices = close_prices * (1 + np.random.uniform(0, 0.03, len(dates)))
    low_prices = close_prices * (1 - np.random.uniform(0, 0.03, len(dates)))
    
    # 生成成交量
    volumes = np.random.randint(1000000, 10000000, len(dates))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    })
    
    return df

# 预先生成一些股票的数据
sample_data = {
    'AAPL': generate_sample_stock_data('AAPL'),
    'MSFT': generate_sample_stock_data('MSFT'),
    'GOOG': generate_sample_stock_data('GOOG'),
    'TSLA': generate_sample_stock_data('TSLA'),
    'BABA': generate_sample_stock_data('BABA')
}

class UDFRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()
        
        # 处理不同的UDF API端点
        if parsed_path.path == '/config':
            # 返回配置信息
            config = {
                "supports_search": True,
                "supports_group_request": False,
                "supports_marks": False,
                "supports_timescale_marks": False,
                "supports_time": True,
                "exchanges": [
                    {"value": "", "name": "All Exchanges", "desc": ""},
                    {"value": "NASDAQ", "name": "NASDAQ", "desc": "NASDAQ"},
                    {"value": "NYSE", "name": "NYSE", "desc": "NYSE"}
                ],
                "symbols_types": [
                    {"name": "All types", "value": ""},
                    {"name": "Stock", "value": "stock"}
                ],
                "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"]
            }
            self.wfile.write(json.dumps(config).encode())
            
        elif parsed_path.path == '/search':
            # 处理搜索请求
            query = query_params.get('query', [''])[0].upper()
            limit = int(query_params.get('limit', [10])[0])
            
            # 过滤匹配的股票
            results = []
            for symbol in sample_data.keys():
                if query in symbol:
                    results.append({
                        "symbol": symbol,
                        "full_name": f"{symbol} Inc.",
                        "description": f"{symbol} - Technology",
                        "exchange": "NASDAQ",
                        "type": "stock"
                    })
                if len(results) >= limit:
                    break
            
            self.wfile.write(json.dumps(results).encode())
            
        elif parsed_path.path == '/symbols':
            # 处理获取股票信息请求
            symbol = query_params.get('symbol', [''])[0]
            
            if symbol in sample_data:
                symbol_info = {
                    "name": symbol,
                    "exchange-traded": "NASDAQ",
                    "exchange-listed": "NASDAQ",
                    "timezone": "America/New_York",
                    "minmov": 1,
                    "minmov2": 0,
                    "pointvalue": 1,
                    "session": "0930-1600",
                    "has_intraday": True,
                    "has_no_volume": False,
                    "description": f"{symbol} Inc.",
                    "pricescale": 100,
                    "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"]
                }
            else:
                symbol_info = {}
            
            self.wfile.write(json.dumps(symbol_info).encode())
            
        elif parsed_path.path == '/history':
            # 处理获取历史数据请求
            symbol = query_params.get('symbol', [''])[0]
            resolution = query_params.get('resolution', ['D'])[0]
            from_time = int(query_params.get('from', [0])[0])
            to_time = int(query_params.get('to', [0])[0])
            
            if symbol not in sample_data:
                self.wfile.write(json.dumps({"s": "no_data"}).encode())
                return
            
            df = sample_data[symbol].copy()
            
            # 转换日期为时间戳
            df['timestamp'] = df['Date'].apply(lambda x: int(x.timestamp()))
            
            # 过滤时间范围内的数据
            mask = (df['timestamp'] >= from_time) & (df['timestamp'] <= to_time)
            filtered_df = df.loc[mask]
            
            # 准备返回数据
            result = {
                "s": "ok",
                "t": filtered_df['timestamp'].tolist(),
                "o": filtered_df['Open'].round(2).tolist(),
                "h": filtered_df['High'].round(2).tolist(),
                "l": filtered_df['Low'].round(2).tolist(),
                "c": filtered_df['Close'].round(2).tolist(),
                "v": filtered_df['Volume'].tolist()
            }
            
            self.wfile.write(json.dumps(result).encode())
            
        elif parsed_path.path == '/time':
            # 返回当前时间戳
            self.wfile.write(json.dumps(int(time.time())).encode())
            
        else:
            # 未找到路径
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()

def run_server(port=8080):
    """启动UDF兼容的HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, UDFRequestHandler)
    print(f'Starting UDF server on port {port}...')
    print('Available symbols: ' + ', '.join(sample_data.keys()))
    print('API endpoints:')
    print('  /config          - 配置信息')
    print('  /search?query=   - 搜索股票')
    print('  /symbols?symbol= - 股票详情')
    print('  /history?symbol= - 历史数据')
    print('  /time            - 当前时间戳')
    print('To use with TradingView, set datafeed URL to http://localhost:8080')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)