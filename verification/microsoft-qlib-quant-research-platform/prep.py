# Offline qlib demo (step 1 of 2): per-symbol OHLCV CSVs from PyPortfolioOpt's sample prices
# (copy stock_prices.csv and spy_prices.csv from PyPortfolioOpt's tests/resources/ into the work folder,
#  and create an empty csv/ folder next to them).
# Synthetic OHLC = close and constant volume: enough to exercise the pipeline, NOT realistic data.
import pandas as pd
px = pd.read_csv("stock_prices.csv", parse_dates=["date"], index_col="date")
spy = pd.read_csv("spy_prices.csv", parse_dates=["date"], index_col="date")
px["SPY"] = spy.iloc[:, 0]
px = px.loc["2008-01-01":]
for sym in px:
    s = px[sym].dropna()
    if len(s) < 500: continue
    pd.DataFrame({"date": s.index.strftime("%Y-%m-%d"), "symbol": sym, "open": s.values, "high": s.values,
                  "low": s.values, "close": s.values, "volume": 1e6, "vwap": s.values, "factor": 1.0}
                 ).to_csv(f"csv/{sym}.csv", index=False)
print(sorted(f for f in __import__("os").listdir("csv")))
