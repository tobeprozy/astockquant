"""qstock connectivity test.
Requires `qstock` package available.
"""
try:
    import qstock as qs  # type: ignore
except Exception:
    qs = None


def main() -> None:
    if qs is None:
        print('Skip: qstock not installed')
        return
    try:
        df = qs.realtime()
        print(df.head())
    except Exception as exc:
        print('qstock call failed:', exc)


if __name__ == '__main__':
    main()


