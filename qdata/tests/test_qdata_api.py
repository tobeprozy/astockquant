"""
测试qdata包的主要接口功能
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime

# 导入qdata包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qdata


class TestQDataAPI(unittest.TestCase):
    """
    测试qdata包的主要接口功能
    """
    
    def setUp(self):
        """测试前的设置"""
        # 创建一个模拟的DataProvider对象
        self.mock_provider = MagicMock()
        
        # 设置模拟的返回数据
        self.mock_daily_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'open': [10.0, 10.2, 10.5],
            'high': [10.5, 10.7, 10.8],
            'low': [9.9, 10.1, 10.3],
            'close': [10.3, 10.5, 10.7],
            'volume': [1000000, 1200000, 1500000]
        })
        
        self.mock_minute_data = pd.DataFrame({
            'datetime': ['2023-06-30 10:00:00', '2023-06-30 10:01:00', '2023-06-30 10:02:00'],
            'open': [10.3, 10.4, 10.5],
            'high': [10.4, 10.5, 10.6],
            'low': [10.2, 10.3, 10.4],
            'close': [10.4, 10.5, 10.6],
            'volume': [100000, 120000, 150000]
        })
        
        self.mock_stock_list = [
            {'code': '600000', 'name': '浦发银行'},
            {'code': '600001', 'name': '邯郸钢铁'},
            {'code': '600002', 'name': '齐鲁石化'}
        ]
        
        self.mock_etf_list = [
            {'code': '512200', 'name': '南方中证500ETF'},
            {'code': '510300', 'name': '沪深300ETF'},
            {'code': '159915', 'name': '创业板ETF'}
        ]
    
    def tearDown(self):
        """测试后的清理"""
        # 重置qdata的全局变量，确保测试之间的独立性
        qdata._current_provider = None
        qdata._provider_config = {}
        qdata._initialized = False
    
    @patch('qdata.DataProviderFactory')
    def test_init(self, mock_factory):
        """测试init函数"""
        # 配置模拟对象
        mock_factory.create_provider.return_value = self.mock_provider
        
        # 测试初始化配置
        config = {
            'default_provider': 'akshare',
            'akshare_config': {
                'retry_count': 3,
                'retry_delay': [1, 2, 3]
            }
        }
        qdata.init(config)
        
        # 验证
        mock_factory.create_provider.assert_called_once_with('akshare', config['akshare_config'])
        self.assertEqual(qdata._provider_config, config)
        self.assertTrue(qdata._initialized)
        self.assertEqual(qdata._current_provider, self.mock_provider)
    
    @patch('qdata.DataProviderFactory')
    def test_get_provider(self, mock_factory):
        """测试get_provider函数"""
        # 配置模拟对象
        mock_factory.create_provider.return_value = self.mock_provider
        
        # 测试获取提供程序（应该自动初始化）
        provider = qdata.get_provider()
        
        # 验证
        mock_factory.create_provider.assert_called_once_with('akshare')
        self.assertEqual(provider, self.mock_provider)
    
    @patch('qdata.DataProviderFactory')
    def test_set_current_provider(self, mock_factory):
        """测试set_current_provider函数"""
        # 配置模拟对象
        mock_factory.create_provider.return_value = self.mock_provider
        
        # 测试设置提供程序
        provider = qdata.set_current_provider('tushare', {'token': 'test_token'})
        
        # 验证
        mock_factory.create_provider.assert_called_once_with('tushare', {'token': 'test_token'})
        self.assertEqual(provider, self.mock_provider)
        self.assertEqual(qdata._current_provider, self.mock_provider)
    
    def test_get_daily_data(self):
        """测试get_daily_data函数"""
        # 设置模拟对象的返回值
        self.mock_provider.get_daily_data.return_value = self.mock_daily_data
        
        # 设置当前提供程序
        qdata._current_provider = self.mock_provider
        
        # 测试获取日线数据
        result = qdata.get_daily_data('600000', '2023-01-01', '2023-01-03')
        
        # 验证
        self.mock_provider.get_daily_data.assert_called_once_with('600000', '2023-01-01', '2023-01-03')
        pd.testing.assert_frame_equal(result, self.mock_daily_data)
    
    def test_get_minute_data(self):
        """测试get_minute_data函数"""
        # 设置模拟对象的返回值
        self.mock_provider.get_minute_data.return_value = self.mock_minute_data
        
        # 设置当前提供程序
        qdata._current_provider = self.mock_provider
        
        # 测试获取分时数据
        result = qdata.get_minute_data('600000', '2023-06-30', freq='1min')
        
        # 验证
        self.mock_provider.get_minute_data.assert_called_once_with('600000', '2023-06-30', None, '1min')
        pd.testing.assert_frame_equal(result, self.mock_minute_data)
    
    def test_get_stock_list(self):
        """测试get_stock_list函数"""
        # 设置模拟对象的返回值
        self.mock_provider.get_stock_list.return_value = self.mock_stock_list
        
        # 设置当前提供程序
        qdata._current_provider = self.mock_provider
        
        # 测试获取股票列表
        result = qdata.get_stock_list()
        
        # 验证
        self.mock_provider.get_stock_list.assert_called_once()
        self.assertEqual(result, self.mock_stock_list)
    
    def test_get_etf_list(self):
        """测试get_etf_list函数"""
        # 设置模拟对象的返回值
        self.mock_provider.get_etf_list.return_value = self.mock_etf_list
        
        # 设置当前提供程序
        qdata._current_provider = self.mock_provider
        
        # 测试获取ETF列表
        result = qdata.get_etf_list()
        
        # 验证
        self.mock_provider.get_etf_list.assert_called_once()
        self.assertEqual(result, self.mock_etf_list)


if __name__ == '__main__':
    unittest.main()