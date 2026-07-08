# Trader Performance vs Bitcoin Market Sentiment

[![Live App](https://img.shields.io/badge/Live-Streamlit_App-red)](https://trader-performance-vs-bitcoin-market-sentiment-hrafihztyftywnz.streamlit.app)

## Project Overview

This project provides an in-depth data science analysis of how Hyperliquid trader behavior (including PnL, leverage, win rate, and position sizing) correlates with the Bitcoin Fear & Greed market sentiment index. 

The goal of this project is to uncover actionable insights into whether market sentiment drives trader profitability and risk appetite, visualizing these relationships through an interactive data dashboard.

You can view the interactive dashboard for this analysis here:
**[Live Website / Streamlit App](https://trader-performance-vs-bitcoin-market-sentiment-hrafihztyftywnz.streamlit.app)**

## Analysis Approach

1. **Normalize & merge**: Datasets are cleaned into a fixed schema and joined on trade date to that day's Fear/Greed reading.
2. **Sentiment buckets**: The 5-level classification (Extreme Fear → Extreme Greed) is analyzed for granular details, and also simplified to Fear / Greed / Neutral for cleaner grouped comparisons.
3. **Core metrics per sentiment regime**: Evaluates total & average closed PnL, win rate, PnL distribution, average/median leverage, and trading volume.
4. **Behavioral cuts**: Analyzes long vs short performance, per-symbol performance, and per-account performance, all split by sentiment.
5. **Statistics**: Utilizes Welch's t-test on mean closed PnL (Fear days vs Greed days), plus a correlation matrix across PnL/leverage/size/price to test statistical significance.
6. **Actionable Takeaways**: Surfaces insights directly in the dashboard's "Stats & Correlation" tab, providing immediate answers rather than raw data dumps.

## Project Structure

```
.
├── app.py                      # Streamlit dashboard (Main application entry point)
├── src/
│   ├── data_loader.py           # Loads, normalizes, and merges CSV datasets
│   ├── analysis.py               # Core analytics: PnL, win rate, leverage, t-tests
│   └── visualization.py          # Plotly chart builders for interactive visuals
├── notebooks/
│   └── eda_analysis.py           # Offline/non-interactive version for generating static reports
├── data/                          # Directory for input CSVs (git-ignored)
├── outputs/                       # Generated textual reports and HTML charts
└── requirements.txt             # Python dependencies
```

## Running Locally

To run the dashboard on your local machine, follow these steps:

1. Clone the repository and navigate to the project folder.
2. (Optional) Place your `fear_greed_index.csv` and `historical_data.csv` in the `data/` directory. Alternatively, you can use the web app's built-in file upload feature once it's running.
3. Set up your virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. Run the interactive Streamlit dashboard:

```bash
streamlit run app.py
```

*Alternatively, to run the offline script and generate a static HTML/text report in the `outputs/` folder:*

```bash
python notebooks/eda_analysis.py --fg data/fear_greed_index.csv --trades data/historical_data.csv
```
