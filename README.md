# Trader Performance vs Bitcoin Market Sentiment

Analysis of how Hyperliquid trader behaviour (PnL, leverage, win rate, position
sizing) relates to Bitcoin Fear & Greed market sentiment. Built as a Primetrade.ai
data science hiring assignment submission.

## What's inside

```
.
├── app.py                      # Streamlit dashboard (main deliverable)
├── src/
│   ├── data_loader.py           # loads + normalizes both CSVs, merges on date
│   ├── analysis.py               # all metrics: PnL by sentiment, win rate,
│   │                              # leverage, t-test, correlations, top symbols
│   └── visualization.py          # Plotly chart builders
├── notebooks/
│   └── eda_analysis.py           # offline/non-interactive version -> saves
│                                  # a text report + HTML charts to outputs/
├── data/                          # put your two CSVs here (git-ignored)
├── outputs/                       # generated report + charts land here
├── requirements.txt
└── .gitignore
```

## 1. Get the data

Download the two files from the assignment links and save them as:

- `data/fear_greed_index.csv` — columns: `Date`, `Classification`
- `data/historical_data.csv` — Hyperliquid trades: `account`, `symbol`,
  `execution price`, `size`, `side`, `time`, `start position`, `event`,
  `closedPnL`, `leverage`, ...

The loader auto-normalizes column name variants (spacing/casing/underscores),
so slightly different headers from the export are fine.

## 2. Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Interactive dashboard
streamlit run app.py

# OR the offline script (writes outputs/summary_report.txt + HTML charts)
python notebooks/eda_analysis.py --fg data/fear_greed_index.csv --trades data/historical_data.csv
```

The Streamlit app also lets you **upload** the two CSVs directly in the
sidebar instead of relying on the `data/` folder — this is what you'd use
once it's deployed publicly, since you generally don't want to commit
someone's trading data to a public GitHub repo.

## 3. Push to GitHub

```bash
cd trader-sentiment-analysis     # or whatever you unzip this to
git init
git add .
git commit -m "Trader performance vs market sentiment analysis"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## 4. Deploy

### Streamlit Community Cloud (recommended, free, made for this)
1. Go to https://share.streamlit.io and sign in with GitHub.
2. **New app** → pick your repo/branch → main file path: `app.py` → **Deploy**.
3. You get a public URL in a couple of minutes. Since the app has file
   uploaders, you don't need to bundle any data in the repo at all.

### Render / Railway (alternative, also supports long-running Python apps)
Both can run a Streamlit app directly from a GitHub repo with a start
command like `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

### A note on Netlify
Netlify is built for static sites and small serverless functions — it can't
host a long-running Python/Streamlit process, so `app.py` won't run there
as-is. If a static, no-backend deliverable is specifically required, the
`notebooks/eda_analysis.py` script's HTML chart outputs (in `outputs/`) are
plain static files and **can** be dropped into a Netlify site (e.g. as a
simple `index.html` linking to each chart). For anything interactive
(filters, live upload), Streamlit Cloud/Render is the right target.

## Analysis approach

1. **Normalize & merge** — both CSVs are cleaned into a fixed schema and
   joined on trade date to that day's Fear/Greed reading.
2. **Sentiment buckets** — the 5-level classification (Extreme Fear →
   Extreme Greed) is kept as-is for detail, and simplified to
   Fear / Greed / Neutral for cleaner grouped comparisons.
3. **Core metrics per sentiment regime**: total & average closed PnL, win
   rate, PnL distribution, average/median leverage, trading volume.
4. **Behavioral cuts**: long vs short performance, per-symbol performance,
   per-account performance, all split by sentiment.
5. **Statistics**: Welch's t-test on mean closed PnL, Fear days vs Greed
   days, plus a correlation matrix across PnL/leverage/size/price.
6. **Takeaways** get surfaced directly in the dashboard's "Stats &
   Correlation" tab (e.g. whether the Fear/Greed PnL gap is statistically
   significant) rather than left for manual read-off.

## Notes for the reviewer

This repo is intentionally upload-first rather than shipping the raw
trading data, since (a) it's often large, and (b) it may not be meant for a
public repo. Everything needed to reproduce the analysis on the actual
assignment CSVs is here — just add the two files and run.
