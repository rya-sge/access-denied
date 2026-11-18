"""Fixed versus moving reference dates.

Claim checked in the article: a curve built with an explicit date keeps that
reference date, so moving Settings.evaluationDate does not shorten the option's
time to expiry; a curve built with settlement days follows the evaluation date.
"""
import QuantLib as ql

today = ql.Date(15, ql.January, 2025)
ql.Settings.instance().evaluationDate = today
dc, cal = ql.Actual365Fixed(), ql.TARGET()
maturity = today + ql.Period(1, ql.Years)


def price(moving):
    if moving:   # reference date = evaluation date (0 settlement days)
        r = ql.FlatForward(0, cal, 0.03, dc)
        q = ql.FlatForward(0, cal, 0.00, dc)
        v = ql.BlackConstantVol(0, cal, 0.20, dc)
    else:        # reference date pinned to 'today'
        r = ql.FlatForward(today, 0.03, dc)
        q = ql.FlatForward(today, 0.00, dc)
        v = ql.BlackConstantVol(today, cal, 0.20, dc)
    proc = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(100.0)),
                                        ql.YieldTermStructureHandle(q),
                                        ql.YieldTermStructureHandle(r),
                                        ql.BlackVolTermStructureHandle(v))
    opt = ql.VanillaOption(ql.PlainVanillaPayoff(ql.Option.Call, 100.0),
                           ql.EuropeanExercise(maturity))
    opt.setPricingEngine(ql.AnalyticEuropeanEngine(proc))
    return opt, r


for moving in (False, True):
    ql.Settings.instance().evaluationDate = today
    opt, curve = price(moving)
    a = opt.NPV()
    ql.Settings.instance().evaluationDate = today + ql.Period(6, ql.Months)
    b = opt.NPV()
    print(f"{'moving' if moving else 'fixed '} reference: today {a:.5f}  "
          f"+6M {b:.5f}  curve reference date {curve.referenceDate()}")

# closed form for the moving case: T = (maturity - (today + 6M)) / 365
import math
t = ql.Actual365Fixed().yearFraction(today + ql.Period(6, ql.Months), maturity)
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
d1 = (0.03 + 0.02) * t / (0.2 * math.sqrt(t)); d2 = d1 - 0.2 * math.sqrt(t)
print(f"closed form with T = {t:.6f}: {100*N(d1) - 100*math.exp(-0.03*t)*N(d2):.5f}")
