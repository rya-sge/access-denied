# Counts the Alpha158 columns that carry no information on the synthetic data of the article
# (open = high = low = close = vwap, constant volume). Run like pipeline.py:
#   qlibdock py -n feature_check.py
import qlib
from qlib.constant import REG_US
from qlib.utils import init_instance_by_config

qlib.init(provider_uri="/work/qlib_data", region=REG_US)
handler = init_instance_by_config({"class": "Alpha158", "module_path": "qlib.contrib.data.handler", "kwargs": {
    "start_time": "2010-01-01", "end_time": "2014-12-31", "fit_start_time": "2010-01-01",
    "fit_end_time": "2014-12-31", "instruments": "all"}})
feat = handler.fetch(col_set="feature")
all_nan = [c for c in feat.columns if feat[c].isna().all()]
const = [c for c in feat.columns if c not in all_nan and feat[c].nunique(dropna=True) <= 1]
print("columns", feat.shape[1])
print("all NaN", len(all_nan), all_nan)
print("constant", len(const), const)
print("uninformative", len(all_nan) + len(const))
