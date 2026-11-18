# Verification: Microsoft qlib, offline end-to-end run

Code behind the worked example of `_posts/2026-11-18-microsoft-qlib-quant-research-platform.md`.

## What is tested

An offline run of qlib 0.9.8 (built from commit `54355232463878d2eebb91fe0ee5fa7fa1f5976c`, tag `v0.9.8`)
through every layer the article describes:

1. `prep.py` turns two CSV files of daily adjusted closes into one CSV per symbol (20 US stocks and SPY,
   2008-01-02 to 2018-04-11).
2. qlib's `scripts/dump_bin.py` converts them into qlib's binary layout, and `scripts/check_data_health.py`
   checks it.
3. `pipeline.py` queries the expression engine, builds `Alpha158` on a `DatasetH` with train / valid / test
   segments, trains `LGBModel`, records the signal (`SignalRecord`), analyses it (`SigAnaRecord`: IC, rank IC),
   runs a `TopkDropoutStrategy` backtest against SPY with costs (`PortAnaRecord`), and scores a deliberately
   leaked expression to show what look-ahead does to the IC.

`expected-output.txt` holds the numbers the article quotes, from a real run.

**The data is synthetic.** The source files contain closing prices only, so `prep.py` sets
open = high = low = close = vwap and a constant volume of 1,000,000. Half of Alpha158's factors (candle shape,
volume) are therefore constant. The run tests qlib's machinery; its returns are not a strategy result.

## Article claims that depend on it

- The binary layout and the expression examples (daily return, inverted ratio, the default label and its
  two trailing `NaN`).
- Alpha158 yields 158 features; segment sizes.
- IC mean 0.0632, rank IC 0.0239, ICIR 0.15, and the t-statistics derived from them.
- Excess return 13.0 %/yr without cost and 3.6 %/yr with cost (information ratio 0.86 and 0.24), the benchmark
  figures, the mean daily cost and turnover.
- Leaked feature IC 0.68.

## How to run

The `qlib` Claude skill provides `qlibdock`, a wrapper that runs a Docker image built from the reviewed qlib
source (non-root, only the current folder mounted at `/work`). Any Python 3.12 environment with qlib 0.9.8
built from the same commit and lightgbm installed should behave the same.

Run it **outside any git repository**: qlib's MLflow recorder saves `git diff`, `git status` and
`git diff --cached` of the current directory as run artifacts (`qlib/workflow/recorder.py`).

```bash
W=$(mktemp -d); mkdir -p "$W/csv"; cd "$W"
cp <PyPortfolioOpt>/tests/resources/{stock_prices,spy_prices}.csv .
cp <this folder>/prep.py <this folder>/pipeline.py .
qlibdock py -n prep.py
qlibdock sh -n -- python /usr/src/qlib/scripts/dump_bin.py dump_all --data_path csv --qlib_dir qlib_data \
   --freq day --date_field_name date --symbol_field_name symbol \
   --include_fields open,high,low,close,volume,vwap,factor
qlibdock sh -n -r -- python /usr/src/qlib/scripts/check_data_health.py check_data --qlib_dir /work/qlib_data
qlibdock py -n pipeline.py
```

`-n` runs without network. The whole pipeline takes about 15 seconds. The input CSV files come from
[PyPortfolioOpt's test resources](https://github.com/PyPortfolio/PyPortfolioOpt/tree/a6638d2e06dae6f444fd022cfd4b3c528902a85b/tests/resources)
(commit `a6638d2e06dae6f444fd022cfd4b3c528902a85b`).
`get_data.py` (qlib's dataset download) is not used: it fetches an unchecksummed archive.
