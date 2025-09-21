#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略核心模块
定义策略的抽象基类和基础功能
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional
import logging

class Strategy(ABC):
    """
    策略的抽象基类
    所有策略都需要实现这个接口
    """
    
    def __init__(self, **kwargs):
        """
        初始化策略
        
        Args:
            **kwargs: 策略参数
        """
        self._params = kwargs
        self._data = None
        self._signals = None
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @property
    def params(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        Returns:
            Dict[str, Any]: 策略参数字典
        """
        return self._params
    
    @params.setter
    def params(self, value: Dict[str, Any]) -> None:
        """
        设置策略参数
        
        Args:
            value: 策略参数字典
        """
        self._params.update(value)
    
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """
        获取策略数据
        
        Returns:
            Optional[pd.DataFrame]: 策略数据
        """
        return self._data
    
    @property
    def signals(self) -> Optional[Dict[str, Any]]:
        """
        获取策略信号
        
        Returns:
            Optional[Dict[str, Any]]: 策略信号
        """
        return self._signals
    
    @signals.setter
    def signals(self, value: Dict[str, Any]) -> None:
        """
        设置策略信号
        
        Args:
            value: 策略信号字典
        """
        self._signals = value
    
    def init_data(self, data: pd.DataFrame) -> None:
        """
        初始化策略数据
        
        Args:
            data: 包含股票数据的DataFrame
        """
        # 验证数据格式
        self._validate_data(data)
        self._data = data.copy()
    
    def _validate_data(self, data: pd.DataFrame) -> None:
        """
        验证数据格式
        
        Args:
            data: 待验证的DataFrame
        
        Raises:
            ValueError: 当数据格式不符合要求时
        """
        # 检查必要的列是否存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要的列: {col}")
        
        # 检查索引是否为时间类型
        if not isinstance(data.index, pd.DatetimeIndex):
            self._logger.warning("数据索引不是时间类型，可能会影响策略效果")
    
    def calculate_indicators(self) -> pd.DataFrame:
        """
        计算策略所需的指标
        
        Returns:
            pd.DataFrame: 包含计算结果的DataFrame
        """
        # 默认实现，在子类中可以覆盖
        if self._data is None:
            raise ValueError("数据尚未初始化，请先调用init_data()")
        return self._data.copy()
    
    @abstractmethod
    def generate_signals(self) -> Dict[str, Any]:
        """
        生成交易信号
        
        Returns:
            Dict[str, Any]: 包含交易信号的字典
        """
        pass
    
    @abstractmethod
    def execute_trade(self) -> Dict[str, Any]:
        """
        执行交易
        
        Returns:
            Dict[str, Any]: 交易执行结果
        """
        pass
    
    def log(self, message: str, level: int = logging.INFO) -> None:
        """
        记录策略日志
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        self._logger.log(level, message)

class DataManager:
    """
    数据管理类
    负责数据的预处理和管理
    """
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据，处理缺失值和异常值
        
        Args:
            data: 原始数据
        
        Returns:
            pd.DataFrame: 清洗后的数据
        """
        # 复制数据以避免修改原始数据
        cleaned_data = data.copy()
        
        # 处理缺失值
        cleaned_data = cleaned_data.dropna()
        
        # 处理异常值（可以根据具体需求扩展）
        # 例如：移除价格为0或负数的行
        cleaned_data = cleaned_data[cleaned_data['close'] > 0]
        
        # 确保索引是排序的
        if isinstance(cleaned_data.index, pd.DatetimeIndex):
            cleaned_data = cleaned_data.sort_index()
        
        return cleaned_data
    
    @staticmethod
    def resample_data(data: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
        """
        数据重采样
        
        Args:
            data: 原始数据
            freq: 重采样频率
        
        Returns:
            pd.DataFrame: 重采样后的数据
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("数据索引必须是时间类型才能进行重采样")
        
        # 使用ohlc方法重采样
        resampled = data.resample(freq).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        return resampled.dropna()