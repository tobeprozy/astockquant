import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from qdata.backends.akshare_provider import AkShareProvider


def main() -> None:
    provider = AkShareProvider()
    # 使用正确的日期格式和方法名
    df = provider.get_daily_data(symbol='512200', start_date='2022-01-01', end_date='2024-01-01')
    print(df.head())
    assert not df.empty


if __name__ == '__main__':
    main()


