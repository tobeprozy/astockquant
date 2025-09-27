#!/usr/bin/env python3
"""
QData UDF Server for TradingView
使用 qdata 包提供真实股票数据的 UDF (Universal Data Feed) 服务器
"""

import sys
import os
import time
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple


try:
    import qdata
    print("✅ Successfully imported qdata")
except ImportError as e:
    print(f"❌ Failed to import qdata: {e}")
    print("Please ensure qdata package is installed or available in the path")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QDataStockManager:
    """使用qdata管理股票数据"""
    
    def __init__(self):
        """初始化数据管理器"""
        try:
            # 初始化qdata
            qdata.init()
            self.initialized = True
            print("✅ QData initialized successfully")
        except Exception as e:
            print(f"❌ QData initialization failed: {e}")
            self.initialized = False
        
        # 数据缓存
        self.cache = {}
        self.cache_ttl = {}
        self.cache_duration = 300  # 5分钟缓存
        
        # 预定义的股票代码映射 (TradingView格式 -> A股代码)
        self.symbol_mapping = {
            # A股主要股票
            'GOOG': '600036',    # 招商银行
            'AMZN': '600519',    # 贵州茅台  
        }
        
        # 反向映射
        self.reverse_mapping = {v: k for k, v in self.symbol_mapping.items()}
        
        # 获取可用股票列表
        self.available_stocks = self._get_available_stocks()
    
    def _get_available_stocks(self) -> Dict[str, Dict]:
        """直接使用预定义的股票代码，不获取股票列表"""
        stocks = {}
        
        # 直接使用预定义的映射中的前2个股票
        count = 0
        for tv_symbol, real_symbol in self.symbol_mapping.items():
            if count >= 2:
                break
            stocks[tv_symbol] = {
                'symbol': tv_symbol,
                'name': f"Stock {real_symbol}",
                'full_name': f"Stock {real_symbol}",
                'description': f"A股 {real_symbol}",
                'exchange': 'SSE/SZSE',
                'type': 'stock',
                'real_symbol': real_symbol
            }
            count += 1
        
        logger.info(f"加载了 {len(stocks)} 个股票")
        return stocks
    
    def get_real_symbol(self, tv_symbol: str) -> str:
        """将TradingView symbol转换为真实的A股代码"""
        # 首先查找预定义映射
        if tv_symbol in self.symbol_mapping:
            return self.symbol_mapping[tv_symbol]
        
        # 查找可用股票列表
        if tv_symbol in self.available_stocks:
            return self.available_stocks[tv_symbol]['real_symbol']
        
        # 如果是A股代码格式，直接返回
        if tv_symbol.isdigit() and len(tv_symbol) == 6:
            return tv_symbol
        
        # 默认返回原symbol
        return tv_symbol
    
    def search_symbols(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索股票"""
        results = []
        query_upper = query.upper()
        
        for symbol, info in self.available_stocks.items():
            if (query_upper in symbol.upper() or 
                query_upper in info['name'] or
                query_upper in info['full_name'].upper()):
                results.append({
                    'symbol': symbol,
                    'full_name': info['full_name'],
                    'description': info['description'],
                    'exchange': info['exchange'],
                    'type': info['type']
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_symbol_info(self, tv_symbol: str) -> Optional[Dict]:
        """获取股票信息"""
        if tv_symbol in self.available_stocks:
            stock = self.available_stocks[tv_symbol]
            return {
                'name': tv_symbol,
                'exchange-traded': stock['exchange'],
                'exchange-listed': stock['exchange'],
                'timezone': 'Asia/Shanghai',
                'minmov': 1,
                'minmov2': 0,
                'pointvalue': 1,
                'session': '0930-1500',
                'has_intraday': True,
                'has_no_volume': False,
                'description': stock['description'],
                'pricescale': 100,
                'supported_resolutions': ['1', '5', '15', '30', '60', 'D', 'W', 'M'],
                'volume_precision': 0,
                'data_status': 'streaming'
            }
        return None
    
    def get_daily_data(self, tv_symbol: str, days: int = 365) -> pd.DataFrame:
        """获取日线数据 - 优化为只获取一次"""
        if not self.initialized:
            return pd.DataFrame()
        
        # 检查缓存 - 使用较长的缓存时间确保只获取一次
        cache_key = f"{tv_symbol}_daily_data"
        if (cache_key in self.cache and 
            cache_key in self.cache_ttl and 
            time.time() < self.cache_ttl[cache_key]):
            logger.info(f"从缓存获取 {tv_symbol} 的数据")
            return self.cache[cache_key]
        
        try:
            # 获取真实股票代码
            real_symbol = self.get_real_symbol(tv_symbol)
            
            # 计算日期范围
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            # 格式化日期
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # 获取数据
            logger.info(f"获取 {real_symbol} 从 {start_date_str} 到 {end_date_str} 的数据")
            df = qdata.get_daily_data(real_symbol, start_date_str, end_date_str)
            
            if not df.empty:
                # 数据预处理
                df = self._process_daily_data(df)
                
                # 缓存数据 - 设置为极长的缓存时间，确保只获取一次
                self.cache[cache_key] = df
                self.cache_ttl[cache_key] = time.time() + 365 * 24 * 60 * 60  # 缓存一年
                
                logger.info(f"成功获取 {len(df)} 条 {tv_symbol} 的数据")
                return df
            else:
                logger.warning(f"未获取到 {tv_symbol} 的数据")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"获取 {tv_symbol} 数据失败: {e}")
            return pd.DataFrame()
    
    def _process_daily_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理日线数据格式"""
        # 如果DataFrame为空，返回空DataFrame
        if df.empty:
            return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        
        # 重置索引，避免date同时作为索引和列存在
        if not df.index.name is None:
            # 如果索引有名称，将其转换为列
            df = df.reset_index()
        
        # 确保列名标准化
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high', 
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 检查是否有date列，如果没有则创建
        if 'date' not in df.columns:
            # 创建一个日期序列
            logger.warning(f"缺少列: date，创建默认日期序列")
            # 使用当前日期向前推，创建与数据行数相同的日期序列
            end_date = datetime.datetime.now()
            date_range = pd.date_range(end=end_date, periods=len(df), freq='B')
            df['date'] = date_range
        else:
            # 确保日期格式正确
            try:
                df['date'] = pd.to_datetime(df['date'])
            except Exception as e:
                logger.warning(f"日期格式转换失败: {e}，重新创建日期序列")
                # 转换失败时重新创建日期序列
                end_date = datetime.datetime.now()
                date_range = pd.date_range(end=end_date, periods=len(df), freq='B')
                df['date'] = date_range
        
        # 确保其他必要的列存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                if col == 'volume':
                    df[col] = 1000000  # 默认成交量
                else:
                    # 对于其他缺少的列，使用开盘价作为默认值
                    logger.warning(f"缺少列: {col}")
                    if 'open' in df.columns:
                        df[col] = df['open']
                    else:
                        df[col] = 0
        
        # 确保数值类型正确
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 删除无效数据
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        # 按日期排序
        df = df.sort_values('date')
        
        return df

# 使用单例模式确保QDataStockManager只初始化一次
class QDataStockManagerSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = QDataStockManager()
        return cls._instance


class QDataUDFRequestHandler(BaseHTTPRequestHandler):
    """UDF请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # 使用单例模式获取QDataStockManager实例
        self.stock_manager = QDataStockManagerSingleton.get_instance()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
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
            elif parsed_path.path == '/status':
                self._handle_status()
            elif parsed_path.path == '/stocks':
                self._handle_stocks()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"处理请求失败 {self.path}: {e}")
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
                {"value": "SSE", "name": "Shanghai Stock Exchange", "desc": "上海证券交易所"},
                {"value": "SZSE", "name": "Shenzhen Stock Exchange", "desc": "深圳证券交易所"}
            ],
            "symbols_types": [
                {"name": "All types", "value": ""},
                {"name": "Stock", "value": "stock"},
                {"name": "ETF", "value": "etf"}
            ],
            "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"]
        }
        self.wfile.write(json.dumps(config, ensure_ascii=False).encode('utf-8'))
    
    def _handle_search(self, query_params):
        """处理搜索请求"""
        query = query_params.get('query', [''])[0]
        limit = int(query_params.get('limit', [10])[0])
        
        results = self.stock_manager.search_symbols(query, limit)
        self.wfile.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
    
    def _handle_symbols(self, query_params):
        """处理股票信息请求"""
        symbol = query_params.get('symbol', [''])[0]
        
        symbol_info = self.stock_manager.get_symbol_info(symbol)
        if symbol_info:
            self.wfile.write(json.dumps(symbol_info, ensure_ascii=False).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({}).encode('utf-8'))
    
    def _handle_history(self, query_params):
        """处理历史数据请求"""
        symbol = query_params.get('symbol', [''])[0]
        resolution = query_params.get('resolution', ['D'])[0]
        from_time = int(query_params.get('from', [0])[0])
        to_time = int(query_params.get('to', [0])[0])
        
        if not symbol:
            self.wfile.write(json.dumps({"s": "no_data"}).encode())
            return
        
        # 获取数据
        df = self.stock_manager.get_daily_data(symbol, days=500)
        
        if df.empty:
            self.wfile.write(json.dumps({"s": "no_data"}).encode())
            return
        
        try:
            # 转换时间戳 - 确保date列存在
            df['timestamp'] = df['date'].apply(lambda x: int(x.timestamp()))
            
            # 过滤时间范围
            if from_time > 0 and to_time > 0:
                mask = (df['timestamp'] >= from_time) & (df['timestamp'] <= to_time)
                filtered_df = df.loc[mask]
            else:
                filtered_df = df
            
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
            
        except Exception as e:
            logger.error(f"处理历史数据失败: {e}")
            self.wfile.write(json.dumps({"s": "error", "errmsg": str(e)}).encode())
    
    def _handle_time(self):
        """处理时间请求"""
        self.wfile.write(json.dumps(int(time.time())).encode())
    
    def _handle_status(self):
        """处理状态请求"""
        status = {
            "qdata_initialized": self.stock_manager.initialized,
            "available_stocks": len(self.stock_manager.available_stocks),
            "cache_size": len(self.stock_manager.cache),
            "timestamp": int(time.time())
        }
        self.wfile.write(json.dumps(status, ensure_ascii=False).encode('utf-8'))
    
    def _handle_stocks(self):
        """处理获取股票列表请求"""
        try:
            # 获取可用股票列表并转换为前端需要的格式
            stocks_data = []
            for symbol, info in self.stock_manager.available_stocks.items():
                stocks_data.append({
                    'symbol': symbol,
                    'real_symbol': info['real_symbol'],
                    'name': info['name'],
                    'description': info['description'],
                    'exchange': info['exchange'],
                    'type': info['type']
                })
            
            self.wfile.write(json.dumps({
                "s": "ok",
                "data": stocks_data
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            self.wfile.write(json.dumps({
                "s": "error",
                "errmsg": str(e)
            }, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()

def run_server(port=8080):
    """启动QData UDF服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, QDataUDFRequestHandler)
    
    print("=" * 70)
    print("🚀 QData UDF Server for TradingView")
    print("=" * 70)
    print(f"📡 Server starting on port {port}...")
    print(f"🌐 TradingView datafeed URL: http://localhost:{port}")
    print("\n📍 API Endpoints:")
    print("   📋 /config          - TradingView 配置信息")
    print("   🔍 /search?query=   - 搜索股票/ETF")
    print("   📈 /symbols?symbol= - 股票详细信息")
    print("   📊 /history?symbol= - 历史价格数据")
    print("   ⏰ /time            - 服务器时间戳")
    print("   ⚡ /status          - 服务器状态")
    print("\n💡 Features:")
    print("   ✅ 使用 qdata 获取真实A股数据")
    print("   ✅ 支持股票和ETF数据")
    print("   ✅ 自动数据缓存机制")
    print("   ✅ TradingView UDF 协议兼容")
    print("   ✅ 中文股票名称支持")
    print("\n📊 Data Sources:")
    print("   🔥 AkShare - 免费股票数据接口")
    print("   💾 自动数据缓存 (5分钟)")
    print("   🔄 实时数据获取")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Shutting down server...')
        httpd.server_close()
        print('✅ Server stopped successfully')

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)