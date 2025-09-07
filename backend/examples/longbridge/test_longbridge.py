"""Longbridge connectivity test (placeholder).
Requires LONG_BRIDGE_* env vars if using official SDK.
"""
import os


def main() -> None:
    # Minimal env presence check to avoid accidental live calls
    has_token = any(os.getenv(k) for k in ['LB_ACCESS_TOKEN', 'LONGBRIDGE_APP_KEY'])
    if not has_token:
        print('Skip: Longbridge credentials not configured')
        return
    print('Longbridge env configured OK')


if __name__ == '__main__':
    main()


