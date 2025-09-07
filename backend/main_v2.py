import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '.'))
if root not in sys.path:
    sys.path.append(root)

from adapters.akshare_provider import AkshareFundProvider
from engines.backtrader_engine import BacktraderEngine
from strategies.strategy import Strategy_MACD3


def run(symbol: str = '512200', start_date: str = '20230101', end_date: str = '20240101') -> None:
    engine = BacktraderEngine(
        data_provider=AkshareFundProvider(),
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_cls=Strategy_MACD3,
    )
    engine.run()
    engine.plot()


if __name__ == '__main__':
    run()


