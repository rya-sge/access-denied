"""Prerequisites check: Black-Litterman posterior formula = bl_returns(), and with no views an
unconstrained optimiser at the same risk aversion returns the market weights (toy 3-asset example).
Run: pfodock py -n -r black_litterman_prior.py"""
import numpy as np, pandas as pd
from pypfopt import black_litterman, BlackLittermanModel, EfficientFrontier
t = ["A", "B", "C"]
S = pd.DataFrame([[0.04, 0.006, 0.01], [0.006, 0.09, 0.02], [0.01, 0.02, 0.0625]], index=t, columns=t)
mcaps = pd.Series({"A": 5e11, "B": 3e11, "C": 2e11}); wm = mcaps / mcaps.sum()
delta = 2.5
pi = black_litterman.market_implied_prior_returns(mcaps, delta, S)
print("Pi", pi.round(6).to_dict())
# no views: unconstrained quadratic utility with same delta returns w_mkt
w = np.linalg.solve(delta * S.values, pi.values); print("unconstrained w*", np.round(w, 6), "w_mkt", wm.values)
ef = EfficientFrontier(pi, S, weight_bounds=(None, None)); ef.max_quadratic_utility(risk_aversion=delta)
print("pypfopt max_quadratic_utility", {k: round(v, 6) for k, v in ef.clean_weights().items()})
# posterior formula vs bl_returns, one view
bl = BlackLittermanModel(S, pi=pi, absolute_views={"B": 0.10}, omega="default", tau=0.05)
P, Q, O, tau = bl.P, bl.Q, bl.omega, bl.tau
mu = pi.values.reshape(-1,1) + tau*S.values@P.T @ np.linalg.solve(P@(tau*S.values)@P.T + O, Q - P@pi.values.reshape(-1,1))
print("formula", np.round(mu.ravel(), 8), "bl_returns", np.round(bl.bl_returns().values, 8))
# Single absolute view on B: the posterior moves the fraction tau*s2/(tau*s2 + omega) of the gap Pi_B -> Q.
s2, om = S.loc["B", "B"], float(O[0, 0])
frac = tau * s2 / (tau * s2 + om)
print("fraction", round(frac, 6), "predicted mu_B", round(pi["B"] + frac * (0.10 - pi["B"]), 8), "bl_returns mu_B", round(bl.bl_returns()["B"], 8))
