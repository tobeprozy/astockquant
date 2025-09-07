import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from adapters.akshare_provider import AkshareFundProvider
from engines.backtrader_engine import BacktraderEngine
from strategies.strategy import Strategy_MACD3


def main() -> None:
    engine = BacktraderEngine(
        data_provider=AkshareFundProvider(),
        symbol='512200',
        start_date='20220101',
        end_date='20240101',
        strategy_cls=Strategy_MACD3,
    )
    res = engine.run()
    engine.print_results(res)


if __name__ == '__main__':
    main()


