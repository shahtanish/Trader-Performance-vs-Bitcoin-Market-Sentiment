"""
visualization.py
-----------------
Plotly chart builders. Kept separate from app.py so charts can also be
reused in a plain script/notebook context (see notebooks/eda_analysis.py).
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


SENTIMENT_COLORS = {"Fear": "#E4572E", "Greed": "#2E9E4E", "Neutral": "#8C8C8C"}


def pnl_by_sentiment_bar(summary_df: pd.DataFrame, group_col: str = "sentiment_simple"):
    fig = px.bar(
        summary_df, x=group_col, y="total_pnl", color=group_col,
        color_discrete_map=SENTIMENT_COLORS,
        title="Total Closed PnL by Market Sentiment",
        labels={"total_pnl": "Total Closed PnL", group_col: "Sentiment"},
    )
    fig.update_layout(showlegend=False)
    return fig


def win_rate_by_sentiment_bar(summary_df: pd.DataFrame, group_col: str = "sentiment_simple"):
    fig = px.bar(
        summary_df, x=group_col, y="win_rate", color=group_col,
        color_discrete_map=SENTIMENT_COLORS,
        title="Win Rate by Market Sentiment",
        labels={"win_rate": "Win Rate", group_col: "Sentiment"},
    )
    fig.update_layout(yaxis_tickformat=".0%", showlegend=False)
    return fig


def daily_pnl_timeseries(daily_df: pd.DataFrame):
    fig = px.bar(
        daily_df, x="date", y="daily_pnl", color="sentiment_simple",
        color_discrete_map=SENTIMENT_COLORS,
        title="Daily Closed PnL Over Time, Colored by Sentiment",
        labels={"daily_pnl": "Daily PnL", "date": "Date", "sentiment_simple": "Sentiment"},
    )
    return fig


def leverage_by_sentiment_box(df: pd.DataFrame):
    fig = px.box(
        df, x="sentiment_simple", y="leverage", color="sentiment_simple",
        color_discrete_map=SENTIMENT_COLORS,
        title="Leverage Distribution by Sentiment",
        labels={"leverage": "Leverage", "sentiment_simple": "Sentiment"},
    )
    fig.update_layout(showlegend=False)
    return fig


def pnl_distribution_violin(df: pd.DataFrame):
    fig = px.violin(
        df, x="sentiment_simple", y="closed_pnl", color="sentiment_simple",
        color_discrete_map=SENTIMENT_COLORS, box=True, points=False,
        title="Closed PnL Distribution by Sentiment",
        labels={"closed_pnl": "Closed PnL", "sentiment_simple": "Sentiment"},
    )
    fig.update_layout(showlegend=False)
    return fig


def top_symbols_chart(top_symbols_df: pd.DataFrame):
    fig = px.bar(
        top_symbols_df, x="symbol", y="total_pnl", color="sentiment_simple",
        barmode="group", color_discrete_map=SENTIMENT_COLORS,
        title="Top Symbols by Total PnL, per Sentiment Regime",
        labels={"total_pnl": "Total PnL", "symbol": "Symbol", "sentiment_simple": "Sentiment"},
    )
    return fig


def correlation_heatmap(corr_df: pd.DataFrame):
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values, x=corr_df.columns, y=corr_df.columns,
        colorscale="RdBu", zmid=0, text=corr_df.round(2).values, texttemplate="%{text}",
    ))
    fig.update_layout(title="Correlation Matrix of Trade Features")
    return fig


def side_performance_chart(side_df: pd.DataFrame):
    fig = px.bar(
        side_df, x="sentiment_simple", y="avg_pnl", color="side", barmode="group",
        title="Average PnL by Trade Side (Long/Short) and Sentiment",
        labels={"avg_pnl": "Average PnL", "sentiment_simple": "Sentiment"},
    )
    return fig
