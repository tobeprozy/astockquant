import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from adapters.csv_provider import CsvOHLCVProvider
from engines.simple_engine import SimpleLoopEngine
from strategies.simple_sma import SMACrossStrategy


def main() -> None:
    provider = CsvOHLCVProvider(csv_path=os.path.join(root, '512200.csv'))
    strategy = SMACrossStrategy(fast=5, slow=20, unit=10)
    engine = SimpleLoopEngine(
        data_provider=provider,
        symbol='512200',
        start_date='2020-01-01',
        end_date='2030-01-01',
        strategy=strategy,
        starting_cash=100000.0,
    )
    result = engine.run()
    print('Trades:', result.trades)
    print('Final equity:', float(result.equity_curve.iloc[-1]))


if __name__ == '__main__':
    main()


