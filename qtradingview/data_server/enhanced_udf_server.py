#!/usr/bin/env python3
"""
Enhanced UDF (Universal Data Feed) Server for TradingView
支持更真实的股票数据模拟，包括技术指标和市场行为模拟
"""

import sys
import time
import random
import datetime
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class StockConfig:
    """股票配置类"""
    symbol: str
    name: str
    base_price: float
    volatility: float  # 波动率
    trend: float      # 趋势 (正数上涨，负数下跌)
    sector: str

# 预定义的股票配置
STOCK_CONFIGS = {
    'AAPL': StockConfig('AAPL', 'Apple Inc.', 150.0, 0.02, 0.0005, 'Technology'),
    'MSFT': StockConfig('MSFT', 'Microsoft Corporation', 300.0, 0.018, 0.0003, 'Technology'),
    'GOOG': StockConfig('GOOG', 'Alphabet Inc.', 2500.0, 0.025, 0.0002, 'Technology'),
    'TSLA': StockConfig('TSLA', 'Tesla Inc.', 800.0, 0.035, 0.001, 'Automotive'),
    'BABA': StockConfig('BABA', 'Alibaba Group', 200.0, 0.03, -0.0002, 'E-commerce'),
    'AMZN': StockConfig('AMZN', 'Amazon.com Inc.', 3200.0, 0.022, 0.0004, 'E-commerce'),
    'NVDA': StockConfig('NVDA', 'NVIDIA Corporation', 400.0, 0.04, 0.002, 'Technology'),
    'META': StockConfig('META', 'Meta Platforms Inc.', 250.0, 0.028, 0.0001, 'Technology'),
    'NFLX': StockConfig('NFLX', 'Netflix Inc.', 400.0, 0.03, 0.0003, 'Entertainment'),
    'DIS': StockConfig('DIS', 'The Walt Disney Company', 120.0, 0.025, 0.0001, 'Entertainment')
}

class EnhancedStockDataGenerator:
    """增强的股票数据生成器"""
    
    def __init__(self, config: StockConfig):
        self.config = config
        
    def generate_intraday_data(self, date: datetime.datetime, intervals_per_day: int = 390) -> pd.DataFrame:
        """生成单日内的分钟级数据"""
        # 创建交易时间 (9:30 AM - 4:00 PM EST)
        start_time = date.replace(hour=9, minute=30, second=0, microsecond=0)
        time_intervals = []
        
        for i in range(intervals_per_day):
            time_intervals.append(start_time + datetime.timedelta(minutes=i))
        
        # 生成价格走势 - 模拟日内交易模式
        returns = self._generate_intraday_returns(intervals_per_day)
        
        # 计算价格
        base_price = self.config.base_price * (1 + random.uniform(-0.02, 0.02))
        close_prices = base_price * (1 + returns).cumprod()
        
        # 生成OHLC
        data = []
        for i, time_point in enumerate(time_intervals):
            if i == 0:
                open_price = base_price
            else:
                open_price = data[i-1]['close']
            
            close_price = close_prices[i]
            
            # 生成高低价 - 考虑真实的价格波动
            high_factor = random.uniform(1.0, 1 + self.config.volatility * 0.5)
            low_factor = random.uniform(1 - self.config.volatility * 0.5, 1.0)
            
            high_price = max(open_price, close_price) * high_factor
            low_price = min(open_price, close_price) * low_factor
            
            # 生成成交量 - 模拟真实的交易量模式
            volume = self._generate_realistic_volume(i, intervals_per_day)
            
            data.append({
                'datetime': time_point,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def generate_daily_data(self, days: int = 365) -> pd.DataFrame:
        """生成日线数据"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # 创建工作日日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        # 生成日线数据
        returns = self._generate_daily_returns(len(dates))
        
        # 加入季节性和趋势
        seasonal_factor = [1 + 0.01 * math.sin(2 * math.pi * i / 252) for i in range(len(dates))]
        trend_factor = [(1 + self.config.trend) ** i for i in range(len(dates))]
        
        # 计算价格序列
        base_prices = [self.config.base_price * seasonal_factor[i] * trend_factor[i] for i in range(len(dates))]
        close_prices = np.array(base_prices) * (1 + returns).cumprod()
        
        # 生成OHLC数据
        data = []
        for i, date in enumerate(dates):
            if i == 0:
                open_price = self.config.base_price
            else:
                open_price = data[i-1]['close']
            
            close_price = close_prices[i]
            
            # 生成高低价
            daily_range = abs(close_price - open_price) * random.uniform(1.5, 3.0)
            high_price = max(open_price, close_price) + daily_range * random.uniform(0, 0.7)
            low_price = min(open_price, close_price) - daily_range * random.uniform(0, 0.7)
            
            # 生成成交量
            base_volume = random.randint(1000000, 5000000)
            volume_multiplier = 1 + abs(close_price - open_price) / open_price * 10  # 波动大时成交量大
            volume = int(base_volume * volume_multiplier)
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def _generate_daily_returns(self, length: int) -> np.ndarray:
        """生成日收益率序列"""
        # 基础随机收益
        returns = np.random.normal(0, self.config.volatility, length)
        
        # 添加聚类波动性 (GARCH效应)
        for i in range(1, length):
            if abs(returns[i-1]) > self.config.volatility:
                returns[i] *= 1.5  # 增加后续波动
        
        # 添加均值回归
        cumulative_return = np.cumsum(returns)
        mean_reversion = -0.001 * cumulative_return
        returns += mean_reversion
        
        return returns
    
    def _generate_intraday_returns(self, length: int) -> np.ndarray:
        """生成日内收益率序列"""
        # 创建日内模式 - 开盘和收盘时波动较大
        time_weights = []
        for i in range(length):
            # 开盘30分钟和收盘30分钟波动较大
            if i < 30 or i > length - 30:
                weight = 1.5
            elif 60 < i < 150:  # 午盘相对平静
                weight = 0.7
            else:
                weight = 1.0
            time_weights.append(weight)
        
        # 生成基础收益
        base_returns = np.random.normal(0, self.config.volatility / 20, length)  # 日内波动较小
        
        # 应用时间权重
        returns = base_returns * np.array(time_weights)
        
        return returns
    
    def _generate_realistic_volume(self, interval_index: int, total_intervals: int) -> int:
        """生成真实的成交量模式"""
        base_volume = random.randint(10000, 50000)
        
        # 开盘和收盘成交量较大
        if interval_index < 30 or interval_index > total_intervals - 30:
            multiplier = random.uniform(2.0, 4.0)
        elif 60 < interval_index < 150:  # 午盘成交量较小
            multiplier = random.uniform(0.3, 0.7)
        else:
            multiplier = random.uniform(0.8, 1.5)
        
        return int(base_volume * multiplier)

class EnhancedUDFServer:
    """增强的UDF服务器"""
    
    def __init__(self):
        self.generators = {symbol: EnhancedStockDataGenerator(config) 
                          for symbol, config in STOCK_CONFIGS.items()}
        self.cache = {}
        self.cache_ttl = {}
        
    def get_daily_data(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """获取日线数据（带缓存）"""
        cache_key = f"{symbol}_daily_{days}"
        
        # 检查缓存
        if (cache_key in self.cache and 
            cache_key in self.cache_ttl and 
            time.time() < self.cache_ttl[cache_key]):
            return self.cache[cache_key]
        
        # 生成新数据
        if symbol in self.generators:
            data = self.generators[symbol].generate_daily_data(days)
            
            # 缓存数据（缓存1小时）
            self.cache[cache_key] = data
            self.cache_ttl[cache_key] = time.time() + 3600
            
            return data
        
        return pd.DataFrame()

class UDFRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.server_instance = EnhancedUDFServer()
        super().__init__(*args, **kwargs)
    
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
        
        try:
            if parsed_path.path == '/config':
                self._handle_config()
            elif parsed_path.path == '/search':
                self._handle_search(query_params)
            elif parsed_path.path == '/symbols':
                self._handle_symbols(query_params)
            elif parsed_path.path == '/history':
                self._handle_history(query_params)
            elif parsed_path.path == '/time':
                self._handle_time()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Error handling request {self.path}: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _handle_config(self):
        """处理配置请求"""
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
    
    def _handle_search(self, query_params):
        """处理搜索请求"""
        query = query_params.get('query', [''])[0].upper()
        limit = int(query_params.get('limit', [10])[0])
        
        results = []
        for symbol, config in STOCK_CONFIGS.items():
            if query in symbol or query in config.name.upper():
                results.append({
                    "symbol": symbol,
                    "full_name": config.name,
                    "description": f"{config.name} - {config.sector}",
                    "exchange": "NASDAQ",
                    "type": "stock"
                })
            if len(results) >= limit:
                break
        
        self.wfile.write(json.dumps(results).encode())
    
    def _handle_symbols(self, query_params):
        """处理股票信息请求"""
        symbol = query_params.get('symbol', [''])[0]
        
        if symbol in STOCK_CONFIGS:
            config = STOCK_CONFIGS[symbol]
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
                "description": config.name,
                "pricescale": 100,
                "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"],
                "volume_precision": 0,
                "data_status": "streaming"
            }
        else:
            symbol_info = {}
        
        self.wfile.write(json.dumps(symbol_info).encode())
    
    def _handle_history(self, query_params):
        """处理历史数据请求"""
        symbol = query_params.get('symbol', [''])[0]
        resolution = query_params.get('resolution', ['D'])[0]
        from_time = int(query_params.get('from', [0])[0])
        to_time = int(query_params.get('to', [0])[0])
        
        if symbol not in STOCK_CONFIGS:
            self.wfile.write(json.dumps({"s": "no_data"}).encode())
            return
        
        # 获取数据
        df = self.server_instance.get_daily_data(symbol, days=500)
        
        if df.empty:
            self.wfile.write(json.dumps({"s": "no_data"}).encode())
            return
        
        # 转换时间戳
        df['timestamp'] = df['date'].apply(lambda x: int(x.timestamp()))
        
        # 过滤时间范围
        mask = (df['timestamp'] >= from_time) & (df['timestamp'] <= to_time)
        filtered_df = df.loc[mask]
        
        if filtered_df.empty:
            self.wfile.write(json.dumps({"s": "no_data"}).encode())
            return
        
        # 准备返回数据
        result = {
            "s": "ok",
            "t": filtered_df['timestamp'].tolist(),
            "o": filtered_df['open'].tolist(),
            "h": filtered_df['high'].tolist(),
            "l": filtered_df['low'].tolist(),
            "c": filtered_df['close'].tolist(),
            "v": filtered_df['volume'].tolist()
        }
        
        self.wfile.write(json.dumps(result).encode())
    
    def _handle_time(self):
        """处理时间请求"""
        self.wfile.write(json.dumps(int(time.time())).encode())
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()

def run_server(port=8080):
    """启动增强的UDF服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, UDFRequestHandler)
    
    print(f'🚀 Enhanced UDF Server starting on port {port}...')
    print(f'📊 Available symbols: {", ".join(STOCK_CONFIGS.keys())}')
    print('\n📍 API Endpoints:')
    print('  📋 /config          - 配置信息')
    print('  🔍 /search?query=   - 搜索股票')
    print('  📈 /symbols?symbol= - 股票详情')
    print('  📊 /history?symbol= - 历史数据')
    print('  ⏰ /time            - 当前时间戳')
    print(f'\n🌐 TradingView datafeed URL: http://localhost:{port}')
    print('\n💡 Features:')
    print('  ✅ Realistic OHLCV data generation')
    print('  ✅ Multiple stock symbols with different characteristics')
    print('  ✅ Volume patterns simulation')
    print('  ✅ Trend and seasonality effects')
    print('  ✅ Data caching for better performance')
    print('\n🔄 Data regenerates with realistic market behavior patterns')
    print('⏹️  Press Ctrl+C to stop the server\n')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Shutting down server...')
        httpd.server_close()
        print('✅ Server stopped successfully')

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)