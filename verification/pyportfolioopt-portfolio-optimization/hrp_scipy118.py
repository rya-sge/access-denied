"""HRPOpt.optimize() with SciPy 1.18 (run with network for the pip install):
    pfodock sh -r -- sh -c 'pip install --user "scipy>=1.18,<1.19"; python3 hrp_scipy118.py'
Output on 2026-11-18: scipy 1.18.1 / AttributeError ... no attribute '_LINKAGE_METHODS'
"""
import scipy, pandas as pd
from pypfopt import HRPOpt, expected_returns
print("scipy", scipy.__version__)
p = pd.read_csv("stock_prices.csv", parse_dates=True, index_col="date")
try:
    HRPOpt(expected_returns.returns_from_prices(p)).optimize()
    print("HRP ok")
except Exception as e:
    print(type(e).__name__, e)
