# data/

Put your two source CSVs here if you want the Streamlit app's
"Use bundled files from data/" option to work, and if you want to run
`notebooks/eda_analysis.py` without passing `--fg` / `--trades` flags:

- `fear_greed_index.csv`   — columns: Date, Classification
- `historical_data.csv`    — Hyperliquid trader data: account, symbol,
  execution price, size, side, time, start position, event, closedPnL,
  leverage, etc.

These CSVs are git-ignored by default (see `.gitignore`) so you don't
accidentally commit large data files or leak trading data to a public repo.
If you'd rather keep the data in the repo (e.g. private repo, or the
dataset is small and meant to be reproducible), just remove the
`data/*.csv` line from `.gitignore`.

Download links from the assignment:
- Historical trader data: (Google Drive link provided by Primetrade.ai)
- Fear & Greed index: (Google Drive link provided by Primetrade.ai)
