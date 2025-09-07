from __future__ import annotations

import backtrader as bt
import matplotlib.pyplot as plt

from typing import Any, Type

from core.base import BacktestEngine, DataProvider
from utils.emailer import SmtpEmailer


class BacktraderEngine(BacktestEngine):
    def __init__(
        self,
        data_provider: DataProvider,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_cls: Type[bt.Strategy],
        starting_cash: float = 100000.0,
        commission: float = 0.00025,
        email_on_finish: bool = False,
        emailer: SmtpEmailer | None = None,
        strategy_kwargs: dict | None = None,
    ) -> None:
        self.data_provider = data_provider
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.strategy_cls = strategy_cls
        self.starting_cash = starting_cash
        self.commission = commission
        self.cerebro = bt.Cerebro()
        self.email_on_finish = email_on_finish
        self.emailer = emailer or SmtpEmailer()
        self.strategy_kwargs = strategy_kwargs or {}

    def run(self) -> Any:
        df = self.data_provider.fetch(self.symbol, self.start_date, self.end_date)
        data = bt.feeds.PandasData(dataname=df)
        self.cerebro.adddata(data, name=self.symbol)
        if self.strategy_kwargs:
            self.cerebro.addstrategy(self.strategy_cls, **self.strategy_kwargs)
        else:
            self.cerebro.addstrategy(self.strategy_cls)
        self.cerebro.broker.setcash(self.starting_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        result = self.cerebro.run()
        if self.email_on_finish:
            print(self.emailer)
            try:
                print(self.strategy_kwargs)
                port_value = self.cerebro.broker.getvalue()
                pnl = port_value - self.starting_cash
                self.emailer.send(
                    subject=f"Backtest finished: {self.symbol}",
                    body=f"Final Value: {port_value:.2f}\nPnL: {pnl:.2f}\nPeriod: {self.start_date} - {self.end_date}",
                )
                print(f"Email sent: {self.symbol}")
            except Exception:
                print(f"Email sent failed: {self.symbol}")
                pass
        return result

    def plot(self) -> None:
        self.cerebro.plot()

    def print_results(self, result: Any) -> None:
        strat = result[0]
        port_value = self.cerebro.broker.getvalue()
        pnl = port_value - self.starting_cash
        try:
            sr = strat.analyzers.SharpeRatio.get_analysis().get('sharperatio')
        except Exception:
            sr = None
        print('Final Portfolio Value: %.2f' % port_value)
        print('PNL: %.2f' % pnl)
        print('Sharpe:', sr)


class MultiSymbolBacktraderEngine(BacktestEngine):
    def __init__(
        self,
        data_provider: DataProvider,
        symbol_a: str,
        symbol_b: str,
        start_date: str,
        end_date: str,
        strategy_cls: Type[bt.Strategy],
        starting_cash: float = 100000.0,
        commission: float = 0.00025,
    ) -> None:
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
        df_a = self.data_provider.fetch(self.symbol_a, self.start_date, self.end_date)
        df_b = self.data_provider.fetch(self.symbol_b, self.start_date, self.end_date)
        data_a = bt.feeds.PandasData(dataname=df_a)
        data_b = bt.feeds.PandasData(dataname=df_b)
        self.cerebro.adddata(data_a, name=self.symbol_a)
        self.cerebro.adddata(data_b, name=self.symbol_b)
        self.cerebro.addstrategy(self.strategy_cls)
        self.cerebro.broker.setcash(self.starting_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        return self.cerebro.run()

    def plot(self) -> None:
        self.cerebro.plot()



