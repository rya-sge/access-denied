import json, warnings, pandas as pd
warnings.filterwarnings("ignore")
from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
p = pd.read_csv("stock_prices.csv", parse_dates=True, index_col="date")
ef = EfficientFrontier(expected_returns.mean_historical_return(p), risk_models.CovarianceShrinkage(p).ledoit_wolf())
ef.max_sharpe(risk_free_rate=0.02); w = ef.clean_weights()
json.dump(w, open("/data/w.json", "w"))
a, _ = DiscreteAllocation(w, get_latest_prices(p), total_portfolio_value=10000).lp_portfolio()
json.dump({k: int(v) for k, v in a.items()}, open("/data/alloc.json", "w"))
da = DiscreteAllocation(w, get_latest_prices(p), total_portfolio_value=10000); da.greedy_portfolio(); b,_ = da.lp_portfolio()
json.dump({k: int(v) for k, v in b.items()}, open("/data/alloc_bad.json", "w"))
