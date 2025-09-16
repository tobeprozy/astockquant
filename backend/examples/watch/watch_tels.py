import os
import time
import json
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional

import pandas as pd

import akshare as ak
import matplotlib.pyplot as plt


# ------------------------------
# Configuration
# ------------------------------
# Symbols to watch. For US ETFs/stocks via EastMoney API in akshare, the code format often is
# "105.TSLL" (NASDAQ) or "106.TSLA" etc. Adjust as needed.
SYMBOLS: List[str] = [
    "105.TSDD",
    "107.YANG",
]

# Email settings: hardcoded per your request (163 Mail, SSL on 465)
SMTP_HOST: str = "smtp.163.com"
SMTP_PORT: int = 465
SMTP_USER: str = "tobeprozy@163.com"
SMTP_PASS: str = "BHrMkpZZvm8frpWY"
EMAIL_FROM: str = "tobeprozy@163.com"
EMAIL_TO: str = "904762096@qq.com"  # comma-separated for multiple if needed

# Indicator parameters
MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9

BOLL_PERIOD: int = 20
BOLL_STD: float = 2.0

# State persistence
STATE_FILE: str = os.path.join(os.path.dirname(__file__), "watch_signals_state.json")
PLOT_DIR: str = os.path.join(os.path.dirname(__file__), "plots")

# runtime store for latest computed indicators per symbol
LATEST_DATA: Dict[str, pd.DataFrame] = {}


# ------------------------------
# Logging
# ------------------------------
logger = logging.getLogger("watch_signals")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state: Dict[str, Any]) -> None:
    tmp_file = STATE_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, STATE_FILE)


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Expect columns: 时间/收盘/开盘/最高/最低 or already-normalized with time index and close/open/high/low.
    df = df.copy()

    # Normalize column names if raw Chinese columns present
    if "时间" in df.columns:
        df.rename(columns={"时间": "time"}, inplace=True)
    if "收盘" in df.columns:
        df.rename(columns={"收盘": "close"}, inplace=True)
    if "开盘" in df.columns:
        df.rename(columns={"开盘": "open"}, inplace=True)
    if "最高" in df.columns:
        df.rename(columns={"最高": "high"}, inplace=True)
    if "最低" in df.columns:
        df.rename(columns={"最低": "low"}, inplace=True)

    # Ensure datetime index
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])  # type: ignore[index]
        df.sort_values("time", inplace=True)
        df.set_index("time", inplace=True)
    else:
        # If already time-indexed, keep as is; otherwise raise
        if not isinstance(df.index, pd.DatetimeIndex):
            raise KeyError("time")

    # MACD
    ema_fast = df["close"].ewm(span=MACD_FAST, adjust=False).mean()
    ema_slow = df["close"].ewm(span=MACD_SLOW, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=MACD_SIGNAL, adjust=False).mean()
    hist = macd_line - signal_line

    df["macd"] = macd_line
    df["signal"] = signal_line
    df["hist"] = hist

    # Bollinger Bands
    ma = df["close"].rolling(window=BOLL_PERIOD, min_periods=BOLL_PERIOD).mean()
    std = df["close"].rolling(window=BOLL_PERIOD, min_periods=BOLL_PERIOD).std(ddof=0)
    upper = ma + BOLL_STD * std
    lower = ma - BOLL_STD * std

    df["boll_mid"] = ma
    df["boll_upper"] = upper
    df["boll_lower"] = lower

    return df


def normalize_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw dataframe to time-indexed OHLC DataFrame without indicators."""
    df = df.copy()
    if "时间" in df.columns:
        df.rename(columns={"时间": "time"}, inplace=True)
    if "收盘" in df.columns:
        df.rename(columns={"收盘": "close"}, inplace=True)
    if "开盘" in df.columns:
        df.rename(columns={"开盘": "open"}, inplace=True)
    if "最高" in df.columns:
        df.rename(columns={"最高": "high"}, inplace=True)
    if "最低" in df.columns:
        df.rename(columns={"最低": "low"}, inplace=True)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])  # type: ignore[index]
        df.sort_values("time", inplace=True)
        df.set_index("time", inplace=True)
    return df

def detect_cross(prev_macd: float, prev_signal: float, curr_macd: float, curr_signal: float) -> Optional[str]:
    # Golden cross: macd crosses up through signal
    if prev_macd <= prev_signal and curr_macd > curr_signal:
        return "golden"
    # Death cross: macd crosses down through signal
    if prev_macd >= prev_signal and curr_macd < curr_signal:
        return "death"
    return None


def send_email(subject: str, body: str) -> None:
    if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS and EMAIL_FROM and EMAIL_TO):
        return  # Missing config; silently skip to avoid crashes

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    to_list = [addr.strip() for addr in EMAIL_TO.split(",") if addr.strip()]

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    try:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, to_list, msg.as_string())
    finally:
        server.quit()


def send_email_with_attachments(subject: str, body: str, attachment_paths: List[str]) -> None:
    if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS and EMAIL_FROM and EMAIL_TO):
        return

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(body, "plain", "utf-8"))

    for path in attachment_paths:
        try:
            with open(path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)
        except Exception:
            logger.exception("attach file failed: %s", path)

    # Use SSL for 163 (port 465)
    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, [addr.strip() for addr in EMAIL_TO.split(',') if addr.strip()], msg.as_string())
    finally:
        try:
            server.quit()
        except Exception:
            pass


def fetch_last_5_trading_days(symbol: str) -> pd.DataFrame:
    # Eastmoney intraday API requires start and end timestamps.
    # We'll set start as now - 10 days to be safe; the API returns market days only.
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=5)
    df = ak.stock_us_hist_min_em(
        symbol=symbol
    )
    if df is not None and not df.empty:
        try:
            logger.info("fetched %s rows for %s", len(df), symbol)
            logger.info("latest fetched rows for %s: %s", symbol, df.tail(3).to_dict(orient="records"))
        except Exception:
            logger.info("fetched %s rows for %s (tail log failed)", len(df), symbol)
    return df


def process_symbol(symbol: str, state: Dict[str, Any]) -> None:
    """Incrementally update symbol data and compute alerts only on new bars."""
    try:
        raw_df = fetch_last_5_trading_days(symbol)
        if raw_df is None or raw_df.empty:
            logger.warning("no data fetched for %s", symbol)
            return
        # Normalize first
        price_df = normalize_prices(raw_df)
    except Exception:
        logger.exception("failed to fetch/normalize for %s", symbol)
        return

    # Merge to cache and compute indicators only for a small tail window
    cached = LATEST_DATA.get(symbol)
    if cached is not None and not cached.empty:
        # Append only rows that do not exist in history (dedup by timestamp)
        new_idx = price_df.index.difference(cached.index)
        append_df = price_df.loc[new_idx]
        if append_df.empty:
            logger.info("no new bars for %s (all fetched bars already cached)", symbol)
            return
        base = cached.drop(columns=[c for c in ["macd","signal","hist","boll_mid","boll_upper","boll_lower"] if c in cached.columns])
        merged = pd.concat([base, append_df])
        merged.sort_index(inplace=True)
    else:
        # first load: compute full indicators
        merged = price_df

    # To avoid recomputing the entire history, recompute indicators on a tail window
    # but MACD/BOLL need prior context; take a warmup window
    warmup = max(MACD_SLOW + MACD_SIGNAL, BOLL_PERIOD) + 5
    tail_start = max(0, len(merged) - (warmup + 500))  # cap to recent 500 bars plus warmup
    head_df = merged.iloc[:tail_start]
    tail_df = merged.iloc[tail_start:]
    tail_with_ind = compute_indicators(tail_df)
    if head_df.empty:
        df = tail_with_ind
    else:
        # ensure no duplicate columns
        df = pd.concat([head_df, tail_with_ind])

    # Determine new rows compared to previous processed timestamp
    symbol_state: Dict[str, Any] = state.get(symbol, {})
    last_processed_iso: Optional[str] = symbol_state.get("last_processed_time")
    last_signal: Optional[str] = symbol_state.get("last_signal")

    LATEST_DATA[symbol] = df

    if last_processed_iso:
        last_dt = pd.to_datetime(last_processed_iso)
        new_df = df[df.index > last_dt]
    else:
        new_df = df.tail(1)

    if new_df.empty:
        logger.info("no new bars for %s since %s", symbol, last_processed_iso)
        return

    new_df = new_df.sort_index()
    prev_row = df.loc[: new_df.index[0]].iloc[-2] if len(df.loc[: new_df.index[0]]) >= 2 else None

    for idx, row in new_df.iterrows():
        if prev_row is None:
            prev_row = row
            continue

        try:
            logger.info(
                "bar %s %s | close=%.4f macd=%.6f signal=%.6f boll(mid=%.4f,up=%.4f,low=%.4f)",
                symbol,
                idx,
                float(row.get("close", float("nan"))),
                float(row.get("macd", float("nan"))),
                float(row.get("signal", float("nan"))),
                float(row.get("boll_mid", float("nan"))),
                float(row.get("boll_upper", float("nan"))),
                float(row.get("boll_lower", float("nan"))),
            )
        except Exception:
            pass

        cross = detect_cross(
            float(prev_row["macd"]),
            float(prev_row["signal"]),
            float(row["macd"]),
            float(row["signal"]),
        )

        if cross == "golden" and last_signal != "buy":
            logger.info("%s GOLDEN CROSS at %s -> BUY alert", symbol, idx)
            subject = f"{symbol} MACD 金叉 信号 - 买入"
            body = (
                f"Symbol: {symbol}\nTime: {idx}\n"
                f"Close: {row['close']:.4f}\nMACD: {row['macd']:.6f}, Signal: {row['signal']:.6f}\n"
                f"BOLL Mid: {row.get('boll_mid', float('nan')):.4f}, Upper: {row.get('boll_upper', float('nan')):.4f}, Lower: {row.get('boll_lower', float('nan')):.4f}"
            )
            send_email_with_attachments(subject, body,[])
            last_signal = "buy"

        if cross == "death" and last_signal != "sell":
            logger.info("%s DEATH CROSS at %s -> SELL alert", symbol, idx)
            subject = f"{symbol} MACD 死叉 信号 - 卖出"
            body = (
                f"Symbol: {symbol}\nTime: {idx}\n"
                f"Close: {row['close']:.4f}\nMACD: {row['macd']:.6f}, Signal: {row['signal']:.6f}\n"
                f"BOLL Mid: {row.get('boll_mid', float('nan')):.4f}, Upper: {row.get('boll_upper', float('nan')):.4f}, Lower: {row.get('boll_lower', float('nan')):.4f}"
            )
            send_email_with_attachments(subject, body,[])
            last_signal = "sell"

        prev_row = row

    state[symbol] = {
        "last_processed_time": new_df.index[-1].isoformat(),
        "last_signal": last_signal,
    }
    logger.info("state updated for %s -> last_time=%s last_signal=%s", symbol, state[symbol]["last_processed_time"], last_signal)

    LATEST_DATA[symbol] = df


def plot_symbol(symbol: str, df: pd.DataFrame, window_minutes: Optional[int] = None, out_path: Optional[str] = None) -> None:
    try:
        os.makedirs(PLOT_DIR, exist_ok=True)
        # window slice for recent minutes if specified
        dfp = df
        try:
            end_ts = None
            start_ts = None
            if window_minutes is not None and not df.empty:
                end_ts = df.index.max()
                start_ts = end_ts - timedelta(minutes=window_minutes)
                dfp = df[df.index >= start_ts]
                if dfp.empty:
                    dfp = df.tail(60)
        except Exception:
            dfp = df

        fig, (ax_price, ax_macd) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

        ax_price.plot(dfp.index, dfp['close'], label='Close', color='black', linewidth=1)
        if 'boll_mid' in dfp.columns:
            ax_price.plot(dfp.index, dfp['boll_mid'], label='BOLL Mid', color='blue', linewidth=1)
        if 'boll_upper' in dfp.columns:
            ax_price.plot(dfp.index, dfp['boll_upper'], label='BOLL Upper', color='green', linewidth=0.8)
        if 'boll_lower' in dfp.columns:
            ax_price.plot(dfp.index, dfp['boll_lower'], label='BOLL Lower', color='red', linewidth=0.8)
        title_suffix = f" (last {window_minutes}m)" if window_minutes else ""
        ax_price.set_title(f"{symbol} Price with Bollinger Bands{title_suffix}")
        ax_price.legend(loc='upper left')
        ax_price.grid(True, linestyle='--', alpha=0.3)

        ax_macd.plot(dfp.index, dfp['macd'], label='MACD', color='purple', linewidth=1)
        ax_macd.plot(dfp.index, dfp['signal'], label='Signal', color='orange', linewidth=1)
        ax_macd.bar(dfp.index, dfp['hist'], label='Hist', color=['#2ca02c' if h >= 0 else '#d62728' for h in dfp['hist']], width=0.8)
        ax_macd.set_title("MACD")
        ax_macd.legend(loc='upper left')
        ax_macd.grid(True, linestyle='--', alpha=0.3)

        # Ensure x-axis only shows the requested time window when provided
        if window_minutes is not None and start_ts is not None and end_ts is not None:
            try:
                ax_price.set_xlim(start_ts, end_ts)
                ax_macd.set_xlim(start_ts, end_ts)
            except Exception:
                pass

        plt.tight_layout()
        final_path = out_path or os.path.join(PLOT_DIR, f"{symbol.replace('.', '_')}.png")
        fig.savefig(final_path, dpi=150)
        plt.close(fig)
        logger.info("plot saved: %s", final_path)
    except Exception:
        logger.exception("plot failed for %s", symbol)


def run_once() -> None:
    state = load_state()
    for sym in SYMBOLS:
        process_symbol(sym, state)
    save_state(state)


def sleep_until_next_minute() -> None:
    now = datetime.now()
    next_min = (now.replace(second=0, microsecond=0) + timedelta(minutes=1))
    to_sleep = (next_min - now).total_seconds()
    if to_sleep > 0:
        time.sleep(to_sleep)


def main() -> None:
    try:
        last_plot_email_ts = datetime.min
        while True:
            run_once()
            # every 10 minutes, generate plots and email
            now = datetime.now()
            if (now - last_plot_email_ts).total_seconds() >= 4800 and LATEST_DATA:
                paths: List[str] = []
                for sym, df in LATEST_DATA.items():
                    # draw only last 30 minutes for email
                    email_path = os.path.join(PLOT_DIR, f"{sym.replace('.', '_')}_30m.png")
                    plot_symbol(sym, df, window_minutes=60, out_path=email_path)
                    paths.append(email_path)
                try:
                    send_email_with_attachments(
                        subject=f"近60分钟图表 {now.strftime('%Y-%m-%d %H:%M')}",
                        body="附件为各标的近60分钟价格+布林+MACD图。",
                        attachment_paths=paths,
                    )
                    logger.info("emailed plots (%d attachments)", len(paths))
                except Exception:
                    logger.exception("email plots failed")
                last_plot_email_ts = now
            sleep_until_next_minute()
    except KeyboardInterrupt:
        logger.info("received KeyboardInterrupt, generating plots before exit...")
    except Exception:
        logger.exception("unexpected error, generating plots before exit...")
    finally:
        # Generate plots on exit
        if not LATEST_DATA:
            logger.info("no data to plot on exit")
            return
        for sym, df in LATEST_DATA.items():
            plot_symbol(sym, df)


if __name__ == "__main__":
    main()


