#!/usr/bin/env python3
"""
测试增强UDF服务器的功能
Test script for the enhanced UDF server
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_server(base_url="http://localhost:8080"):
    """测试服务器的各个端点"""
    
    print("🧪 Testing Enhanced UDF Server")
    print("=" * 50)
    
    # 测试配置端点
    print("\n1. Testing /config endpoint...")
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Config endpoint working")
            print(f"   📊 Supported resolutions: {config['supported_resolutions']}")
            print(f"   🏢 Exchanges: {len(config['exchanges'])}")
        else:
            print(f"❌ Config endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Config endpoint error: {e}")
    
    # 测试搜索端点
    print("\n2. Testing /search endpoint...")
    try:
        response = requests.get(f"{base_url}/search?query=APP&limit=5")
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search endpoint working")
            print(f"   🔍 Found {len(results)} results for 'APP'")
            for result in results:
                print(f"      📈 {result['symbol']}: {result['full_name']}")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
    
    # 测试股票信息端点
    print("\n3. Testing /symbols endpoint...")
    test_symbols = ['AAPL', 'TSLA', 'INVALID']
    
    for symbol in test_symbols:
        try:
            response = requests.get(f"{base_url}/symbols?symbol={symbol}")
            if response.status_code == 200:
                symbol_info = response.json()
                if symbol_info.get('name'):
                    print(f"✅ Symbol {symbol} found")
                    print(f"      📊 Description: {symbol_info.get('description', 'N/A')}")
                    print(f"      🏢 Exchange: {symbol_info.get('exchange-traded', 'N/A')}")
                else:
                    print(f"❌ Symbol {symbol} not found")
            else:
                print(f"❌ Symbols endpoint failed for {symbol}: {response.status_code}")
        except Exception as e:
            print(f"❌ Symbols endpoint error for {symbol}: {e}")
    
    # 测试历史数据端点
    print("\n4. Testing /history endpoint...")
    
    # 计算时间范围 (最近30天)
    end_time = int(time.time())
    start_time = end_time - (30 * 24 * 60 * 60)
    
    try:
        url = f"{base_url}/history?symbol=AAPL&resolution=D&from={start_time}&to={end_time}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('s') == 'ok':
                print(f"✅ History endpoint working")
                print(f"   📊 Retrieved {len(data['t'])} data points for AAPL")
                
                if data['t']:
                    # 显示最后几个数据点
                    print(f"   📈 Latest data points:")
                    for i in range(min(3, len(data['t']))):
                        idx = -(i+1)
                        date = datetime.fromtimestamp(data['t'][idx]).strftime('%Y-%m-%d')
                        print(f"      {date}: O={data['o'][idx]}, H={data['h'][idx]}, L={data['l'][idx]}, C={data['c'][idx]}, V={data['v'][idx]}")
            else:
                print(f"❌ History endpoint returned no data: {data.get('s')}")
        else:
            print(f"❌ History endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ History endpoint error: {e}")
    
    # 测试时间端点
    print("\n5. Testing /time endpoint...")
    try:
        response = requests.get(f"{base_url}/time")
        if response.status_code == 200:
            server_time = response.json()
            current_time = int(time.time())
            time_diff = abs(server_time - current_time)
            
            print(f"✅ Time endpoint working")
            print(f"   ⏰ Server time: {datetime.fromtimestamp(server_time).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   ⏰ Local time:  {datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   ⚡ Time difference: {time_diff} seconds")
        else:
            print(f"❌ Time endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Time endpoint error: {e}")
    
    # 测试数据质量
    print("\n6. Testing data quality...")
    try:
        url = f"{base_url}/history?symbol=TSLA&resolution=D&from={start_time}&to={end_time}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('s') == 'ok' and data['t']:
                # 检查数据的一致性
                prices_valid = all(
                    data['l'][i] <= data['o'][i] <= data['h'][i] and
                    data['l'][i] <= data['c'][i] <= data['h'][i]
                    for i in range(len(data['t']))
                )
                
                volumes_valid = all(v > 0 for v in data['v'])
                
                print(f"✅ Data quality check completed")
                print(f"   📊 Price consistency: {'✅ Valid' if prices_valid else '❌ Invalid'}")
                print(f"   📈 Volume validity: {'✅ Valid' if volumes_valid else '❌ Invalid'}")
                
                # 计算一些统计信息
                if len(data['c']) > 1:
                    returns = [(data['c'][i] - data['c'][i-1]) / data['c'][i-1] for i in range(1, len(data['c']))]
                    avg_return = sum(returns) / len(returns)
                    volatility = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
                    
                    print(f"   📊 Average daily return: {avg_return:.4f} ({avg_return*100:.2f}%)")
                    print(f"   📊 Daily volatility: {volatility:.4f} ({volatility*100:.2f}%)")
            else:
                print(f"❌ No data available for quality check")
        else:
            print(f"❌ Data quality check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Data quality check error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("\n💡 If all tests pass, the server is ready for TradingView integration.")
    print("🚀 Start your Vue application and navigate to the chart component.")

def test_performance(base_url="http://localhost:8080", num_requests=10):
    """测试服务器性能"""
    print(f"\n⚡ Performance Test ({num_requests} requests)")
    print("-" * 30)
    
    end_time = int(time.time())
    start_time = end_time - (365 * 24 * 60 * 60)  # 1年数据
    
    import time as time_module
    
    start_perf = time_module.time()
    
    for i in range(num_requests):
        try:
            response = requests.get(
                f"{base_url}/history?symbol=AAPL&resolution=D&from={start_time}&to={end_time}",
                timeout=5
            )
            if response.status_code != 200:
                print(f"❌ Request {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Request {i+1} error: {e}")
    
    end_perf = time_module.time()
    total_time = end_perf - start_perf
    avg_time = total_time / num_requests
    
    print(f"📊 Total time: {total_time:.2f} seconds")
    print(f"📊 Average per request: {avg_time:.3f} seconds")
    print(f"📊 Requests per second: {num_requests/total_time:.1f}")

if __name__ == "__main__":
    print("🚀 Enhanced UDF Server Test Suite")
    print("Make sure the server is running: python tests/enhanced_udf_server.py")
    print()
    
    # 基本功能测试
    test_server()
    
    # 性能测试
    try:
        test_performance()
    except KeyboardInterrupt:
        print("\n⏹️ Performance test interrupted")
    except Exception as e:
        print(f"\n❌ Performance test error: {e}")