# Offline end-to-end qlib run for the article "Microsoft qlib" (step 2 of 2).
# Run in a work folder holding qlib_data/ (built by prep.py + dump_bin.py), NOT inside a git repository:
# qlib's MLflow recorder stores `git diff` / `git status` of the current directory as run artifacts.
#   qlibdock py -n pipeline.py
# Data -> expressions -> Alpha158 -> LightGBM -> signal analysis -> TopkDropout backtest. MLflow runs in ./mlruns.
# Derived from ~/.claude/skills/qlib/scripts/offline_demo/pipeline.py, with the daily-return expression corrected
# and extra prints for every number the article quotes.
import numpy as np
import pandas as pd
import qlib
from qlib.constant import REG_US
from qlib.data import D
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, SigAnaRecord, PortAnaRecord

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)
qlib.init(provider_uri="/work/qlib_data", region=REG_US, exp_manager={
    "class": "MLflowExpManager", "module_path": "qlib.workflow.expm",
    "kwargs": {"uri": "file:/work/mlruns", "default_exp_name": "Experiment"}})

# 1. Data layer
cal = D.calendar()
print("CALENDAR", cal[0].date(), cal[-1].date(), len(cal), "days")
insts = D.list_instruments(D.instruments("all"), as_list=True)
print("INSTRUMENTS", len(insts), insts)

# 2. Expression engine: daily return, the inverted ratio, a 5-day mean and the default label
expr = ["$close", "$close/Ref($close, 1) - 1", "Ref($close, 1)/$close - 1", "Mean($close, 5)",
        "Ref($close, -2)/Ref($close, -1) - 1"]
print(D.features(["AAPL"], expr, start_time="2018-04-09", end_time="2018-04-11"))

# 3. Dataset: Alpha158 on DatasetH with three time segments
handler = {"class": "Alpha158", "module_path": "qlib.contrib.data.handler", "kwargs": {
    "start_time": "2010-01-01", "end_time": "2018-04-11", "fit_start_time": "2010-01-01",
    "fit_end_time": "2014-12-31", "instruments": "all"}}
dataset = init_instance_by_config({"class": "DatasetH", "module_path": "qlib.data.dataset", "kwargs": {
    "handler": handler, "segments": {"train": ("2010-01-01", "2014-12-31"),
    "valid": ("2015-01-01", "2016-06-30"), "test": ("2016-07-01", "2018-04-11")}}})
for seg in ("train", "valid", "test"):
    df = dataset.prepare(seg, col_set=["feature", "label"])
    print("SEGMENT", seg, "rows", len(df), "features", df["feature"].shape[1],
          "days", df.index.get_level_values("datetime").nunique())

# 4. Model + recorder + signal analysis + backtest
model = init_instance_by_config({"class": "LGBModel", "module_path": "qlib.contrib.model.gbdt",
    "kwargs": {"loss": "mse", "learning_rate": 0.05, "num_leaves": 31, "num_threads": 4, "seed": 0}})
port = {"strategy": {"class": "TopkDropoutStrategy", "module_path": "qlib.contrib.strategy",
                     "kwargs": {"signal": (model, dataset), "topk": 5, "n_drop": 1}},
        "backtest": {"start_time": "2016-07-01", "end_time": "2018-04-10", "account": 1_000_000,
                     "benchmark": "SPY", "exchange_kwargs": {"deal_price": "close", "open_cost": 0.0005,
                     "close_cost": 0.0015, "min_cost": 5}}}
with R.start(experiment_name="offline_test"):
    model.fit(dataset)
    rec = R.get_recorder()
    SignalRecord(model, dataset, rec).generate()
    SigAnaRecord(rec).generate()
    PortAnaRecord(rec, port, "day").generate()

    ic = rec.load_object("sig_analysis/ic.pkl")
    ric = rec.load_object("sig_analysis/ric.pkl")
    n = len(ic)
    print("IC days", n, "IC mean", round(float(ic.mean()), 4), "IC std", round(float(ic.std()), 4),
          "ICIR", round(float(ic.mean() / ic.std()), 4), "t", round(float(ic.mean() / ic.std() * np.sqrt(n)), 2),
          "share IC>0", round(float((ic > 0).mean()), 3))
    print("RankIC mean", round(float(ric.mean()), 4), "RankIC std", round(float(ric.std()), 4))

    ana = rec.load_object("portfolio_analysis/port_analysis_1day.pkl")
    print(ana)
    rep = rec.load_object("portfolio_analysis/report_normal_1day.pkl")
    print("BACKTEST days", len(rep), rep.index[0].date(), rep.index[-1].date())
    print("mean daily cost", float(rep["cost"].mean()), "mean daily turnover", float(rep["turnover"].mean()))
    print("sum return", float(rep["return"].sum()), "sum bench", float(rep["bench"].sum()),
          "sum cost", float(rep["cost"].sum()))
    ex = rep["return"] - rep["bench"] - rep["cost"]
    print("compounded excess with cost over the period", float((1 + ex).prod() - 1))

    # 5. Look-ahead demo: a "feature" that peeks at the label window, scored with no model at all
    pred = rec.load_object("pred.pkl")
    label = rec.load_object("label.pkl")
    idx = pred.index
    leak = D.features(insts, ["Ref($close, -2)/$close - 1"], start_time="2016-07-01", end_time="2018-04-11")
    leak = leak.swaplevel().sort_index().iloc[:, 0].reindex(idx)
    df = pd.DataFrame({"leak": leak, "label": label.iloc[:, 0]}).dropna()
    leak_ic = df.groupby(level="datetime").apply(lambda d: d["leak"].corr(d["label"]))
    print("LEAK IC mean", round(float(leak_ic.mean()), 4))
