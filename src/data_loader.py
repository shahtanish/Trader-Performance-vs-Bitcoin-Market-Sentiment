"""
data_loader.py
--------------
Loads and normalizes the two source datasets:
  1. Bitcoin Fear/Greed sentiment data      (Date, Classification)
  2. Hyperliquid historical trader data      (account, symbol, execution price,
                                               size, side, time, start position,
                                               event, closedPnL, leverage, ...)

Real-world exports often have inconsistent column names/casing/spacing
(e.g. "Closed PnL" vs "closedPnL" vs "closed_pnl"). This module normalizes
column names so the rest of the pipeline can rely on a fixed schema.
"""

from __future__ import annotations
import re
import pandas as pd
import numpy as np


def _normalize_col(col: str) -> str:
    """Turn any messy header into snake_case."""
    col = str(col).strip()
    col = re.sub(r"[^\w\s]", "", col)          # drop punctuation
    col = re.sub(r"\s+", "_", col)              # spaces -> underscore
    return col.lower()


# Maps many possible raw-header variants -> our canonical column name
CANONICAL_MAP = {
    "account": "account",
    "coin": "symbol",
    "symbol": "symbol",
    "execution_price": "execution_price",
    "price": "execution_price",
    "size": "size",
    "size_tokens": "size",
    "size_usd": "size_usd",
    "side": "side",
    "direction": "side",
    "timestamp": "time",
    "time": "time",
    "start_position": "start_position",
    "event": "event",
    "closedpnl": "closed_pnl",
    "closed_pnl": "closed_pnl",
    "leverage": "leverage",
    "date": "date",
    "classification": "classification",
    "fee": "fee",
    "trade_id": "trade_id",
}


def _apply_canonical_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_normalize_col(c) for c in df.columns]
    rename = {c: CANONICAL_MAP[c] for c in df.columns if c in CANONICAL_MAP}
    df = df.rename(columns=rename)
    return df


def load_fear_greed(path_or_buffer) -> pd.DataFrame:
    """Load the Fear/Greed sentiment CSV and return columns: date, classification."""
    df = pd.read_csv(path_or_buffer)
    df = _apply_canonical_names(df)

    if "date" not in df.columns:
        raise ValueError("Fear/Greed file must contain a 'Date' column.")
    if "classification" not in df.columns:
        raise ValueError("Fear/Greed file must contain a 'Classification' column.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["classification"] = df["classification"].astype(str).str.strip().str.title()

    # Collapse to a simplified 2-way sentiment as well, useful for cleaner grouping
    def simplify(label: str) -> str:
        label = label.lower()
        if "greed" in label:
            return "Greed"
        if "fear" in label:
            return "Fear"
        return "Neutral"

    df["sentiment_simple"] = df["classification"].apply(simplify)
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"])
    return df[["date", "classification", "sentiment_simple"]].sort_values("date")


def load_trader_data(path_or_buffer) -> pd.DataFrame:
    """Load the Hyperliquid historical trades CSV and normalize schema."""
    df = pd.read_csv(path_or_buffer)
    df = _apply_canonical_names(df)

    required = ["time"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Trader data must contain a '{col}' column.")

    # Parse time -> datetime, handle both unix (s/ms) and string timestamps
    def parse_time(series: pd.Series) -> pd.Series:
        if pd.api.types.is_numeric_dtype(series):
            # Guess ms vs s by magnitude
            sample = series.dropna().astype(float)
            if len(sample) and sample.median() > 1e12:
                return pd.to_datetime(series, unit="ms", errors="coerce")
            return pd.to_datetime(series, unit="s", errors="coerce")
        return pd.to_datetime(series, errors="coerce")

    df["time"] = parse_time(df["time"])
    df["date"] = df["time"].dt.date

    # Ensure numeric fields are numeric
    for col in ["execution_price", "size", "size_usd", "closed_pnl", "leverage", "start_position", "fee"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "closed_pnl" not in df.columns:
        df["closed_pnl"] = np.nan

    if "side" in df.columns:
        df["side"] = df["side"].astype(str).str.strip().str.upper()

    df = df.dropna(subset=["date"])
    return df


def merge_datasets(trades: pd.DataFrame, sentiment: pd.DataFrame) -> pd.DataFrame:
    """Left-join trades with the sentiment reading for that day."""
    merged = trades.merge(sentiment, on="date", how="left")
    return merged
