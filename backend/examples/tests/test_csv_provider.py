import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from adapters.csv_provider import CsvOHLCVProvider


def main() -> None:
    csv_path = os.path.join(root, '512200.csv')
    if not os.path.exists(csv_path):
        print('CSV not found, skipping:', csv_path)
        return
    provider = CsvOHLCVProvider(csv_path=csv_path)
    df = provider.fetch(symbol='512200', start_date='2020-01-01', end_date='2030-01-01')
    print(df.head())
    assert not df.empty


if __name__ == '__main__':
    main()


