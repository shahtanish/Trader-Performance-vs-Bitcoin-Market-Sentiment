"""
analysis.py
-----------
Computes the core metrics that link trader performance to market sentiment.
Every function takes the merged (trades + sentiment) dataframe produced by
data_loader.merge_datasets and returns a tidy summary dataframe, so results
can be reused by both the Streamlit app and any offline script/notebook.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from scipy import stats


def performance_by_sentiment(df: pd.DataFrame, group_col: str = "sentiment_simple") -> pd.DataFrame:
    """Aggregate PnL / win-rate / volume / leverage stats per sentiment bucket."""
    g = df.groupby(group_col, dropna=True)

    out = g.agg(
        total_trades=("closed_pnl", "count"),
        total_pnl=("closed_pnl", "sum"),
        avg_pnl=("closed_pnl", "mean"),
        median_pnl=("closed_pnl", "median"),
        pnl_std=("closed_pnl", "std"),
        win_rate=("closed_pnl", lambda s: (s > 0).mean()),
        avg_leverage=("leverage", "mean") if "leverage" in df.columns else ("closed_pnl", "size"),
    ).reset_index()

    if "size_usd" in df.columns:
        vol = g["size_usd"].sum().rename("total_volume_usd")
        out = out.merge(vol, on=group_col, how="left")
    elif "size" in df.columns:
        vol = g["size"].sum().rename("total_volume")
        out = out.merge(vol, on=group_col, how="left")

    return out.sort_values("total_pnl", ascending=False)


def daily_pnl_series(df: pd.DataFrame) -> pd.DataFrame:
    """Daily aggregated PnL joined with that day's sentiment classification."""
    daily = (
        df.groupby(["date", "classification", "sentiment_simple"], dropna=False)
        .agg(daily_pnl=("closed_pnl", "sum"),
             trades=("closed_pnl", "count"),
             win_rate=("closed_pnl", lambda s: (s > 0).mean()))
        .reset_index()
        .sort_values("date")
    )
    return daily


def top_symbols_by_sentiment(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Best performing symbols within each sentiment regime."""
    if "symbol" not in df.columns:
        return pd.DataFrame()

    g = (
        df.groupby(["sentiment_simple", "symbol"])
        .agg(total_pnl=("closed_pnl", "sum"), trades=("closed_pnl", "count"))
        .reset_index()
    )
    g = g.sort_values(["sentiment_simple", "total_pnl"], ascending=[True, False])
    return g.groupby("sentiment_simple").head(top_n)


def leverage_vs_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Average leverage & risk-taking behaviour by sentiment."""
    if "leverage" not in df.columns:
        return pd.DataFrame()
    g = df.groupby("sentiment_simple").agg(
        avg_leverage=("leverage", "mean"),
        max_leverage=("leverage", "max"),
        median_leverage=("leverage", "median"),
    ).reset_index()
    return g


def statistical_test_fear_vs_greed(df: pd.DataFrame) -> dict:
    """
    Independent two-sample t-test: is average PnL significantly different
    between Fear days and Greed days?
    """
    fear = df.loc[df["sentiment_simple"] == "Fear", "closed_pnl"].dropna()
    greed = df.loc[df["sentiment_simple"] == "Greed", "closed_pnl"].dropna()

    if len(fear) < 2 or len(greed) < 2:
        return {"error": "Not enough data in one of the groups to run a t-test."}

    t_stat, p_value = stats.ttest_ind(fear, greed, equal_var=False, nan_policy="omit")
    return {
        "fear_mean_pnl": float(fear.mean()),
        "greed_mean_pnl": float(greed.mean()),
        "fear_n": int(len(fear)),
        "greed_n": int(len(greed)),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "significant_at_0.05": bool(p_value < 0.05),
    }


def win_rate_by_side_and_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Do long vs short trades perform differently across sentiment regimes?"""
    if "side" not in df.columns:
        return pd.DataFrame()
    g = (
        df.groupby(["sentiment_simple", "side"])
        .agg(trades=("closed_pnl", "count"),
             win_rate=("closed_pnl", lambda s: (s > 0).mean()),
             avg_pnl=("closed_pnl", "mean"))
        .reset_index()
    )
    return g


def account_level_summary(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Per-account totals, useful for spotting consistently strong/weak traders."""
    if "account" not in df.columns:
        return pd.DataFrame()
    g = (
        df.groupby("account")
        .agg(total_pnl=("closed_pnl", "sum"),
             trades=("closed_pnl", "count"),
             win_rate=("closed_pnl", lambda s: (s > 0).mean()),
             avg_leverage=("leverage", "mean") if "leverage" in df.columns else ("closed_pnl", "count"))
        .reset_index()
        .sort_values("total_pnl", ascending=False)
    )
    return pd.concat([g.head(top_n), g.tail(top_n)]).drop_duplicates()


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Correlate numeric trade features (helps spot hidden relationships)."""
    numeric_cols = [c for c in ["closed_pnl", "leverage", "size", "size_usd",
                                 "execution_price", "start_position"] if c in df.columns]
    if len(numeric_cols) < 2:
        return pd.DataFrame()
    return df[numeric_cols].corr()
