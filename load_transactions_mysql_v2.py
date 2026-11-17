"""
STEP 1 (v2) - reload the transactions into MySQL with a NEW live_ts column.

What changes compared with v1
  * No salary-day effect any more.
  * The load now has ordinary daily traffic PLUS random "load events" (sales, campaigns, rushes)
    that can start on ANY date and at ANY hour. Some build up slowly (20-100 min), some are sudden.
  * The same 1,000,000 real transactions are used; only WHEN they happen (live_ts) is generated.

Run from the capstone folder:   python load_transactions_mysql_v2.py
"""
import re
from pathlib import Path
import numpy as np
import pandas as pd

PASSWORD = "MY PASSWORD"
DATA_FILE = r"C:\Users\bhargavi\Downloads\capstone_project\capstone\data\transactions_inserts.sql"
START, DAYS, SEED = "2025-07-03", 150, 42


def _g(x, mu, sd):
    return np.exp(-0.5 * ((x - mu) / sd) ** 2)


def make_live_timestamps(n_tx, seed=SEED, start=START, days=DAYS, n_events=130, base_mean=3.3):
    """Return one new timestamp per transaction (same order as the input rows)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=days * 1440, freq="1min")
    N = len(idx)
    hour = idx.hour.values + idx.minute.values / 60

    # 1) ordinary traffic: quiet at night, peaks at ~10 AM and ~3 PM, weekends lower
    daily = 0.10 + 0.95 * _g(hour, 10.5, 1.8) + 0.80 * _g(hour, 15.5, 2.2) + 0.25 * _g(hour, 20, 2)
    dow = idx.dayofweek.values
    base = daily * np.where(dow < 5, 1.0, np.where(dow == 5, 0.55, 0.40))
    base = base * base_mean / base.mean()

    # 2) random load events at ANY date and time (adds extra transactions per minute)
    extra = np.zeros(N)
    for _ in range(n_events):
        sudden = rng.random() < 0.25                       # 25% appear almost instantly
        ramp = int(rng.integers(2, 7) if sudden else rng.integers(20, 101))
        hold = int(rng.integers(5, 21) if sudden else rng.integers(15, 91))
        fade = int(rng.integers(5, 21) if sudden else rng.integers(20, 61))
        amp = float(rng.uniform(14, 40) if sudden else rng.uniform(10, 32))
        s = int(rng.integers(0, N - ramp - hold - fade))
        shape = np.r_[np.linspace(0, amp, ramp, endpoint=False), np.full(hold, amp), np.linspace(amp, 0, fade)]
        extra[s:s + len(shape)] += shape

    lam = base + extra
    counts = rng.multinomial(n_tx, lam / lam.sum())        # how many transactions fall in each minute
    minute_of_txn = np.repeat(np.arange(N), counts)
    rng.shuffle(minute_of_txn)                             # random transaction -> minute mapping
    secs = rng.integers(0, 60, size=n_tx)
    return idx.values[minute_of_txn] + (secs * 1_000_000_000).astype("timedelta64[ns]")


def parse_transactions(path):
    pat = re.compile(r"VALUES \('([^']*)', '([^']*)', '([^']*)', '([^']*)', '([^']*)'\)")
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = pat.search(line)
            if m:
                rows.append(m.groups())
    df = pd.DataFrame(rows, columns=["transaction_id", "account_id", "merchant_id", "amount_usd", "transaction_date"])
    df["amount_usd"] = df["amount_usd"].astype(float)
    return df


if __name__ == "__main__":
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import URL

    engine = create_engine(URL.create("mysql+pymysql", username="root", password=PASSWORD,
                                      host="localhost", port=3306, database="bank_db"))
    print("Reading the insert file...")
    tx = parse_transactions(DATA_FILE)
    print(f"Read {len(tx):,} transactions")

    tx["live_ts"] = pd.to_datetime(make_live_timestamps(len(tx))).strftime("%Y-%m-%d %H:%M:%S")
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE transactions"))
    chunk = 10000
    for i in range(0, len(tx), chunk):
        tx.iloc[i:i + chunk].to_sql("transactions", engine, if_exists="append", index=False, method="multi")
        if (i // chunk) % 10 == 0:
            print(f"  loaded {min(i + chunk, len(tx)):,} rows")
    print("Done. Now open Capstone_v2.ipynb")
