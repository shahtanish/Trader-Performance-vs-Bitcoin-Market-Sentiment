"""
eda_analysis.py
----------------
Standalone, non-interactive version of the analysis for anyone who wants a
plain script/notebook deliverable instead of (or in addition to) the
Streamlit app. Produces:
  - outputs/summary_report.txt   (all key numbers, human-readable)
  - outputs/*.html               (interactive Plotly charts, open in any browser)

Usage:
    python notebooks/eda_analysis.py --fg data/fear_greed_index.csv --trades data/historical_data.csv
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_fear_greed, load_trader_data, merge_datasets
from src import analysis as an
from src import visualization as viz


def main(fg_path: str, trades_path: str, out_dir: str = "outputs"):
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading sentiment data from {fg_path} ...")
    fg = load_fear_greed(fg_path)
    print(f"Loading trader data from {trades_path} ...")
    trades = load_trader_data(trades_path)
    merged = merge_datasets(trades, fg)
    merged["sentiment_simple"] = merged["sentiment_simple"].fillna("Neutral")

    lines = []
    lines.append("=" * 70)
    lines.append("TRADER PERFORMANCE vs BITCOIN MARKET SENTIMENT — SUMMARY REPORT")
    lines.append("=" * 70)
    lines.append(f"Total trades: {len(trades):,}")
    lines.append(f"Date range: {trades['date'].min()} to {trades['date'].max()}")
    lines.append("")

    summary = an.performance_by_sentiment(merged)
    lines.append("--- Performance by Sentiment ---")
    lines.append(summary.to_string(index=False))
    lines.append("")

    lev = an.leverage_vs_sentiment(merged)
    if not lev.empty:
        lines.append("--- Leverage by Sentiment ---")
        lines.append(lev.to_string(index=False))
        lines.append("")

    side = an.win_rate_by_side_and_sentiment(merged)
    if not side.empty:
        lines.append("--- Win Rate by Side & Sentiment ---")
        lines.append(side.to_string(index=False))
        lines.append("")

    ttest = an.statistical_test_fear_vs_greed(merged)
    lines.append("--- Statistical Test: Fear vs Greed mean PnL (Welch's t-test) ---")
    for k, v in ttest.items():
        lines.append(f"{k}: {v}")
    lines.append("")

    top_syms = an.top_symbols_by_sentiment(merged)
    if not top_syms.empty:
        lines.append("--- Top Symbols by Sentiment ---")
        lines.append(top_syms.to_string(index=False))
        lines.append("")

    corr = an.correlation_matrix(merged)
    if not corr.empty:
        lines.append("--- Correlation Matrix ---")
        lines.append(corr.to_string())
        lines.append("")

    report_path = os.path.join(out_dir, "summary_report.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved report -> {report_path}")

    # Save interactive charts as standalone HTML files
    charts = {
        "pnl_by_sentiment": viz.pnl_by_sentiment_bar(summary),
        "win_rate_by_sentiment": viz.win_rate_by_sentiment_bar(summary),
        "daily_pnl_timeseries": viz.daily_pnl_timeseries(an.daily_pnl_series(merged)),
        "pnl_distribution": viz.pnl_distribution_violin(merged),
    }
    if not lev.empty:
        charts["leverage_by_sentiment"] = viz.leverage_by_sentiment_box(merged)
    if not top_syms.empty:
        charts["top_symbols"] = viz.top_symbols_chart(top_syms)
    if not corr.empty:
        charts["correlation_heatmap"] = viz.correlation_heatmap(corr)

    for name, fig in charts.items():
        path = os.path.join(out_dir, f"{name}.html")
        fig.write_html(path)
        print(f"Saved chart -> {path}")

    print("\nDone. Open the .html files in a browser, or read summary_report.txt.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run offline EDA on trader vs sentiment data.")
    parser.add_argument("--fg", default="data/fear_greed_index.csv", help="Path to Fear/Greed CSV")
    parser.add_argument("--trades", default="data/historical_data.csv", help="Path to Hyperliquid trades CSV")
    parser.add_argument("--out", default="outputs", help="Output directory")
    args = parser.parse_args()
    main(args.fg, args.trades, args.out)
