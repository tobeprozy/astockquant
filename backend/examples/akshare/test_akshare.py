import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from adapters.akshare_provider import AkshareFundProvider


def main() -> None:
    provider = AkshareFundProvider()
    df = provider.fetch(symbol='512200', start_date='20220101', end_date='20240101')
    print(df.head())
    assert not df.empty


if __name__ == '__main__':
    main()


