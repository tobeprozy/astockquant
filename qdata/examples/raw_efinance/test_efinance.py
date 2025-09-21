"""Simple efinance connectivity test.
Requires `efinance` installed in current environment.
"""
try:
    import efinance as ef  # type: ignore
except Exception as e:
    ef = None


def main() -> None:
    if ef is None:
        print('Skip: efinance not installed')
        return
    try:
        df = ef.stock.get_realtime_quotes()
        print(df.head())
    except Exception as exc:
        print('efinance call failed:', exc)


if __name__ == '__main__':
    main()


