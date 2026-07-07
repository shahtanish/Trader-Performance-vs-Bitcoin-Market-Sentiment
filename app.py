"""
app.py
------
Streamlit dashboard: Trader Performance vs Bitcoin Market Sentiment.

Run locally:
    streamlit run app.py

Deploy free on Streamlit Community Cloud:
    1. Push this repo to GitHub.
    2. Go to https://share.streamlit.io -> New app -> pick the repo -> main file: app.py
    3. Done — you get a public URL in ~2 minutes.
"""

import streamlit as st
import pandas as pd

from src.data_loader import load_fear_greed, load_trader_data, merge_datasets
from src import analysis as an
from src import visualization as viz

st.set_page_config(
    page_title="Trader Performance vs Market Sentiment",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Trader Performance vs Bitcoin Market Sentiment")
st.caption(
    "Explores how Hyperliquid trader behaviour (PnL, leverage, win rate, volume) "
    "shifts with Bitcoin Fear & Greed sentiment."
)

# ---------------------------------------------------------------------------
# 1. Data ingestion
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1. Load Data")
    st.write("Upload the two source CSVs, or drop them in `data/` before deploying "
             "and toggle 'Use bundled sample paths' below.")

    fg_file = st.file_uploader("Fear & Greed CSV (Date, Classification)", type="csv", key="fg")
    trades_file = st.file_uploader(
        "Hyperliquid Historical Trader CSV (account, symbol, execution price, "
        "size, side, time, closedPnL, leverage, ...)",
        type="csv", key="trades",
    )

    use_bundled = st.checkbox("Use bundled files from data/ instead", value=False)
    st.markdown("---")
    st.caption("Tip: for a public deployment, uploading each session is simplest — "
               "no data ever needs to live in the GitHub repo.")


@st.cache_data(show_spinner=True)
def _load(fg_source, trades_source):
    fg = load_fear_greed(fg_source)
    trades = load_trader_data(trades_source)
    merged = merge_datasets(trades, fg)
    return fg, trades, merged


fg_source, trades_source = None, None
if use_bundled:
    fg_source = "data/fear_greed_index.csv"
    trades_source = "data/historical_data.csv"
elif fg_file is not None and trades_file is not None:
    fg_source = fg_file
    trades_source = trades_file

if fg_source is None or trades_source is None:
    st.info("⬅️ Upload both CSV files in the sidebar to begin (or check 'Use bundled files').")
    st.stop()

try:
    fg_df, trades_df, merged_df = _load(fg_source, trades_source)
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

merged_df["sentiment_simple"] = merged_df["sentiment_simple"].fillna("Neutral")

# ---------------------------------------------------------------------------
# 2. Filters
# ---------------------------------------------------------------------------
st.sidebar.header("2. Filters")
date_min, date_max = merged_df["date"].min(), merged_df["date"].max()
date_range = st.sidebar.date_input("Date range", (date_min, date_max), min_value=date_min, max_value=date_max)

symbols = sorted(merged_df["symbol"].dropna().unique()) if "symbol" in merged_df.columns else []
selected_symbols = st.sidebar.multiselect("Symbols (blank = all)", symbols, default=[])

filtered = merged_df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = filtered[(filtered["date"] >= date_range[0]) & (filtered["date"] <= date_range[1])]
if selected_symbols:
    filtered = filtered[filtered["symbol"].isin(selected_symbols)]

st.success(f"Loaded {len(trades_df):,} trades across {trades_df['date'].nunique():,} days. "
           f"{len(filtered):,} trades match current filters.")

# ---------------------------------------------------------------------------
# 3. KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Closed PnL", f"{filtered['closed_pnl'].sum():,.2f}")
k2.metric("Overall Win Rate", f"{(filtered['closed_pnl'] > 0).mean():.1%}")
k3.metric("Avg Leverage", f"{filtered['leverage'].mean():.2f}x" if "leverage" in filtered.columns else "N/A")
k4.metric("Trades", f"{len(filtered):,}")

st.markdown("---")

# ---------------------------------------------------------------------------
# 4. Core visuals
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Sentiment Overview", "Time Series", "Risk (Leverage)", "Symbols & Accounts", "Stats & Correlation"]
)

with tab1:
    summary = an.performance_by_sentiment(filtered)
    st.plotly_chart(viz.pnl_by_sentiment_bar(summary), use_container_width=True)
    st.plotly_chart(viz.win_rate_by_sentiment_bar(summary), use_container_width=True)
    st.plotly_chart(viz.pnl_distribution_violin(filtered), use_container_width=True)
    st.dataframe(summary, use_container_width=True)

with tab2:
    daily = an.daily_pnl_series(filtered)
    st.plotly_chart(viz.daily_pnl_timeseries(daily), use_container_width=True)
    st.dataframe(daily, use_container_width=True)

with tab3:
    if "leverage" in filtered.columns:
        st.plotly_chart(viz.leverage_by_sentiment_box(filtered), use_container_width=True)
        st.dataframe(an.leverage_vs_sentiment(filtered), use_container_width=True)
    else:
        st.warning("No 'leverage' column found in the uploaded trader data.")

    side_df = an.win_rate_by_side_and_sentiment(filtered)
    if not side_df.empty:
        st.plotly_chart(viz.side_performance_chart(side_df), use_container_width=True)
        st.dataframe(side_df, use_container_width=True)

with tab4:
    top_syms = an.top_symbols_by_sentiment(filtered)
    if not top_syms.empty:
        st.plotly_chart(viz.top_symbols_chart(top_syms), use_container_width=True)

    acct = an.account_level_summary(filtered)
    if not acct.empty:
        st.subheader("Top / Bottom Accounts by Total PnL")
        st.dataframe(acct, use_container_width=True)

with tab5:
    result = an.statistical_test_fear_vs_greed(filtered)
    st.subheader("Fear vs Greed — Two-Sample t-test on Closed PnL")
    st.json(result)
    if "p_value" in result:
        if result["significant_at_0.05"]:
            st.success("The difference in mean PnL between Fear and Greed days is "
                        "statistically significant (p < 0.05).")
        else:
            st.info("No statistically significant difference in mean PnL was found "
                     "between Fear and Greed days at the 5% level.")

    corr = an.correlation_matrix(filtered)
    if not corr.empty:
        st.plotly_chart(viz.correlation_heatmap(corr), use_container_width=True)

st.markdown("---")
st.caption("Built for the Primetrade.ai data science hiring assignment — "
           "trader performance vs Bitcoin market sentiment analysis.")
