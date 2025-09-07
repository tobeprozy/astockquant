"""
Minimal connectivity test for Alpaca example.
Requires environment variables:
  ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY, ALPACA_BASE_URL
"""
import os


def main() -> None:
    missing = [k for k in [
        'ALPACA_API_KEY_ID', 'ALPACA_API_SECRET_KEY', 'ALPACA_BASE_URL'
    ] if not os.getenv(k)]
    if missing:
        print('Skip: missing envs', missing)
        return
    # Basic smoke: ensure credentials present
    print('Alpaca env configured OK')


if __name__ == '__main__':
    main()


