"""qbackengine - 回测引擎模块

该模块包含qbackengine插件的回测引擎实现，负责执行回测逻辑。
"""

import pandas as pd
import backtrader as bt
from typing import Dict, Any, Optional
from dataclasses import dataclass

class BacktraderEngine:
    """
    基于backtrader的回测引擎
    """
    
    def __init__(
        self,
        data_provider,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_cls,
        starting_cash: float = 100000.0,
        commission: float = 0.00025,
        email_on_finish: bool = False,
        emailer=None,
        strategy_kwargs: dict = None
    ):
        """
        初始化backtrader回测引擎
        
        参数:
            data_provider: 数据提供者
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategy_cls: 策略类
            starting_cash: 初始资金
            commission: 佣金比例
            email_on_finish: 回测完成后发送邮件
            emailer: 邮件发送器
            strategy_kwargs: 策略参数
        """
        self.data_provider = data_provider
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.strategy_cls = strategy_cls
        self.starting_cash = starting_cash
        self.commission = commission
        self.cerebro = bt.Cerebro()
        self.email_on_finish = email_on_finish
        self.emailer = emailer
        self.strategy_kwargs = strategy_kwargs or {}
    
    def run(self) -> Any:
        """
        运行回测
        
        返回:
            回测结果
        """
        # 获取数据
        df = self.data_provider.get_daily_data(self.symbol, self.start_date, self.end_date)
        
        # 将数据转换为backtrader可用格式
        data = bt.feeds.PandasData(dataname=df)
        self.cerebro.adddata(data, name=self.symbol)
        
        # 添加策略
        # 检查策略类是否有get_backtrader_strategy方法
        if hasattr(self.strategy_cls, 'get_backtrader_strategy'):
            # 创建策略实例以访问实例方法
            strategy_instance = self.strategy_cls(**self.strategy_kwargs)
            # 获取真正的backtrader策略类
            bt_strategy_cls = strategy_instance.get_backtrader_strategy()
            # 添加策略到cerebro
            self.cerebro.addstrategy(bt_strategy_cls)
        else:
            # 直接添加策略（适用于已继承bt.Strategy的策略）
            if self.strategy_kwargs:
                self.cerebro.addstrategy(self.strategy_cls, **self.strategy_kwargs)
            else:
                self.cerebro.addstrategy(self.strategy_cls)
        
        # 设置初始资金和佣金
        self.cerebro.broker.setcash(self.starting_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # 添加分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        
        # 运行回测
        result = self.cerebro.run()
        
        # 发送邮件通知
        if self.email_on_finish and self.emailer:
            try:
                port_value = self.cerebro.broker.getvalue()
                pnl = port_value - self.starting_cash
                self.emailer.send(
                    subject=f"回测完成: {self.symbol}",
                    body=f"最终市值: {port_value:.2f}\n盈亏: {pnl:.2f}\n周期: {self.start_date} - {self.end_date}",
                )
            except Exception as e:
                print(f"邮件发送失败: {self.symbol}, 错误: {e}")
                pass
        
        return result
        
    def print_results(self, result: Any) -> None:
        """
        打印回测结果
        
        参数:
            result: 回测结果
        """
        strat = result[0]
        port_value = self.cerebro.broker.getvalue()
        pnl = port_value - self.starting_cash
        try:
            sr = strat.analyzers.SharpeRatio.get_analysis().get('sharperatio')
        except Exception:
            sr = None
        print('最终投资组合价值: %.2f' % port_value)
        print('盈亏: %.2f' % pnl)
        print('夏普比率:', sr)
        
        try:
            drawdown = strat.analyzers.DW.get_analysis()
            print('最大回撤: %.2f%%' % (drawdown.max.drawdown * 100))
            print('回撤持续时间: %d' % drawdown.max.len)
        except Exception:
            pass
            
    def plot(self) -> None:
        """
        绘制回测结果图表
        """
        self.cerebro.plot()

class MultiSymbolBacktraderEngine:
    """
    多标的backtrader回测引擎
    """
    
    def __init__(
        self,
        data_provider,
        symbol_a: str,
        symbol_b: str,
        start_date: str,
        end_date: str,
        strategy_cls,
        starting_cash: float = 100000.0,
        commission: float = 0.00025
    ):
        """
        初始化多标的回测引擎
        
        参数:
            data_provider: 数据提供者
            symbol_a: 第一个股票代码
            symbol_b: 第二个股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategy_cls: 策略类
            starting_cash: 初始资金
            commission: 佣金比例
        """
        self.data_provider = data_provider
        self.symbol_a = symbol_a
        self.symbol_b = symbol_b
        self.start_date = start_date
        self.end_date = end_date
        self.strategy_cls = strategy_cls
        self.starting_cash = starting_cash
        self.commission = commission
        self.cerebro = bt.Cerebro()
    
    def run(self) -> Any:
        """
        运行多标的回测
        
        返回:
            回测结果
        """
        # 获取两个标的的数据
        df_a = self.data_provider.get_daily_data(self.symbol_a, self.start_date, self.end_date)
        df_b = self.data_provider.get_daily_data(self.symbol_b, self.start_date, self.end_date)
        
        # 转换为backtrader数据格式
        data_a = bt.feeds.PandasData(dataname=df_a)
        data_b = bt.feeds.PandasData(dataname=df_b)
        
        # 添加数据到回测引擎
        self.cerebro.adddata(data_a, name=self.symbol_a)
        self.cerebro.adddata(data_b, name=self.symbol_b)
        
        # 添加策略
        self.cerebro.addstrategy(self.strategy_cls)
        
        # 设置初始资金和佣金
        self.cerebro.broker.setcash(self.starting_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # 添加分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        
        # 运行回测
        return self.cerebro.run()
        
    def print_results(self, result: Any) -> None:
        """
        打印多标的回测结果
        
        参数:
            result: 回测结果
        """
        strat = result[0]
        port_value = self.cerebro.broker.getvalue()
        pnl = port_value - self.starting_cash
        try:
            sr = strat.analyzers.SharpeRatio.get_analysis().get('sharperatio')
        except Exception:
            sr = None
        print('最终投资组合价值: %.2f' % port_value)
        print('盈亏: %.2f' % pnl)
        print('夏普比率:', sr)
        
        try:
            drawdown = strat.analyzers.DW.get_analysis()
            print('最大回撤: %.2f%%' % (drawdown.max.drawdown * 100))
            print('回撤持续时间: %d' % drawdown.max.len)
        except Exception:
            pass
            
    def plot(self) -> None:
        """
        绘制多标的回测结果图表
        """
        self.cerebro.plot()

@dataclass
class SimpleResult:
    equity_curve: pd.Series
    trades: int


class SimpleLoopEngine:
    """
    简单事件循环回测引擎
    """
    
    def __init__(
        self,
        data_provider,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy,
        starting_cash: float = 100000.0
    ):
        """
        初始化简单事件循环回测引擎
        
        参数:
            data_provider: 数据提供者
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategy: 策略实例
            starting_cash: 初始资金
        """
        self.data_provider = data_provider
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.strategy = strategy
        self.starting_cash = starting_cash
    
    def run(self) -> SimpleResult:
        """
        运行简单事件循环回测
        
        返回:
            SimpleResult对象，包含权益曲线和交易次数
        """
        # 获取数据
        df = self.data_provider.get_daily_data(self.symbol, self.start_date, self.end_date)
        
        # 初始化回测变量
        cash = self.starting_cash
        position = 0.0
        equity = []
        index = []
        trades = 0
        
        # 检查策略类型并初始化
        if hasattr(self.strategy, 'init_strategy'):
            # 对于QStrategy类型的策略，先初始化
            self.strategy.init_strategy(df)
            # 预先生成所有信号
            signals = self.strategy.generate_signals()
        elif not hasattr(self.strategy, 'on_bar'):
            # 如果策略既没有on_bar方法也没有init_strategy方法，抛出异常
            raise AttributeError(f'策略对象{self.strategy.__class__.__name__}没有on_bar或init_strategy方法')
        
        # 逐bar回测
        for ts, row in df.iterrows():
            # 构建Bar数据
            bar_data = {
                'date': ts,
                'open': float(row["open"]),
                'high': float(row["high"]),
                'low': float(row["low"]),
                'close': float(row["close"]),
                'volume': float(row["volume"])
            }
            
            # 获取策略信号
            signal = None
            if hasattr(self.strategy, 'on_bar'):
                # 对于有on_bar方法的策略
                signal = self.strategy.on_bar(bar_data)
            elif hasattr(self.strategy, 'generate_signals'):
                # 对于使用generate_signals方法的策略
                # 检查当前日期是否在买入或卖出信号中
                if ts in signals['buy_signals']:
                    signal = {'action': 'buy', 'size': cash / bar_data['close']}
                elif ts in signals['sell_signals']:
                    signal = {'action': 'sell', 'size': position}
            
            price = bar_data['close']
            
            # 执行买入操作
            if signal and signal.get("action") == "buy":
                size = float(signal.get("size", 0))
                if size > 0:
                    cost = size * price
                    if cost <= cash:
                        cash -= cost
                        position += size
                        trades += 1
            # 执行卖出操作
            elif signal and signal.get("action") == "sell":
                size = float(signal.get("size", 0))
                if size > 0 and position >= size:
                    cash += size * price
                    position -= size
                    trades += 1
            
            # 计算当前权益
            index.append(ts)
            equity.append(cash + position * price)
        
        # 创建权益曲线
        equity_curve = pd.Series(equity, index=index, name="equity")
        
        return SimpleResult(equity_curve=equity_curve, trades=trades)
    
    def print_result(self, result: SimpleResult) -> None:
        """
        打印简单回测引擎的结果
        
        参数:
            result: SimpleResult对象
        """
        final_equity = result.equity_curve.iloc[-1]
        pnl = final_equity - self.starting_cash
        print(f'最终权益: {final_equity:.2f}')
        print(f'盈亏: {pnl:.2f}')
        print(f'交易次数: {result.trades}')
        # 计算简单收益率
        return_rate = (final_equity / self.starting_cash - 1) * 100
        print(f'收益率: {return_rate:.2f}%')
        
    def plot(self, result: SimpleResult) -> None:
        """
        绘制回测结果图表
        由于SimpleLoopEngine是简单事件循环引擎，目前仅支持基本的结果打印。
        
        参数:
            result: SimpleResult对象
        """
        try:
            import matplotlib.pyplot as plt
            # 简单的权益曲线绘制
            plt.figure(figsize=(10, 6))
            plt.plot(result.equity_curve.index, result.equity_curve.values)
            plt.title('权益曲线')
            plt.xlabel('日期')
            plt.ylabel('权益')
            plt.grid(True)
            plt.show()
        except ImportError:
            print("无法绘制图表，请安装matplotlib库: pip install matplotlib")
        except Exception as e:
            print(f"绘制图表时出错: {str(e)}")