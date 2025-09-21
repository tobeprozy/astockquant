"""Tushare connectivity test.
Requires env var: TUSHARE_TOKEN
"""
import os


def main() -> None:
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print('Skip: set TUSHARE_TOKEN to run tushare test')
        return
    try:
        import tushare as ts  # type: ignore
        pro = ts.pro_api(token)
        # Fetch a tiny slice to validate connectivity
        df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240110')
        print(df.head())
        assert df is not None
    except Exception as exc:
        print('tushare call failed:', exc)


if __name__ == '__main__':
    main()


