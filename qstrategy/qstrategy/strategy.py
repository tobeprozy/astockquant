from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional
import logging

# 直接导入qindicator插件
import qindicator

class StrategyBase(ABC):
    """
    策略的抽象基类
    所有策略都需要实现这个接口
    """
    
    # 策略参数
    params = ()
    
    def __init__(self, *args):
        """
        初始化策略
        
        Args:
            *args: 位置参数（用于兼容backtrader框架）
        """
        self._emailer = None
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
        # 初始化qindicator插件
        try:
            qindicator.init()
            logging.info("成功初始化qindicator插件")
        except Exception as e:
            logging.error(f"初始化qindicator插件失败: {e}")
            raise
    
    def get_indicator_adapter(self):
        """
        获取指标适配器实例
        
        Returns:
            指标适配器实例
        """
        # 直接返回qindicator模块作为替代
        return qindicator
    
    @abstractmethod
    def init_strategy(self, data: pd.DataFrame) -> None:
        """
        初始化策略参数和指标
        
        参数:
            data: 包含股票数据的DataFrame
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        参数:
            data: 包含股票数据的DataFrame
            
        返回:
            包含交易信号的DataFrame
        """
        pass
    
    @abstractmethod
    def execute_trade(self, signals: pd.DataFrame) -> Dict[str, Any]:
        """
        执行交易
        
        参数:
            signals: 包含交易信号的DataFrame
            
        返回:
            交易执行结果
        """
        pass
    
    def log(self, txt: str, dt: Optional[pd.Timestamp] = None, doprint: bool = None) -> None:
        """
        记录策略执行过程
        
        参数:
            txt: 日志文本
            dt: 日期时间
            doprint: 是否打印日志，如果为None则根据self._params.printlog决定
        """
        # 如果没有指定doprint，则检查是否有printlog参数并使用
        should_print = doprint
        if should_print is None and hasattr(self, '_params') and hasattr(self._params, 'printlog'):
            should_print = self._params.printlog
        elif should_print is None and hasattr(self, '_params') and isinstance(self._params, dict) and 'printlog' in self._params:
            should_print = self._params['printlog']
        
        if should_print:
            if dt:
                print(f"{dt.isoformat()}, {txt}")
            else:
                print(txt)
    
    def notify_order(self, order: Any) -> None:
        """
        订单状态通知处理
        
        参数:
            order: 订单对象
        """
        pass
    
    def notify_trade(self, trade: Any) -> None:
        """
        交易结果通知处理
        
        参数:
            trade: 交易对象
        """
        pass