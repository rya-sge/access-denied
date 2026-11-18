"""European / American / barrier equity options with QuantLib-Python.

Claims checked in the article: analytic, finite-difference and Monte Carlo
prices of the same European call, Greeks, put-call parity, American >= European,
and the Observer behaviour (a quote change reprices, a new evaluation date reprices).
"""
import math
import QuantLib as ql

print("QuantLib", ql.__version__)
today = ql.Date(15, ql.January, 2025)
ql.Settings.instance().evaluationDate = today

dc = ql.Actual365Fixed()
cal = ql.TARGET()
spot = ql.SimpleQuote(100.0)
r = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.03, dc))
q = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.00, dc))
vol = ql.SimpleQuote(0.20)
v = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(today, cal, ql.QuoteHandle(vol), dc))
process = ql.BlackScholesMertonProcess(ql.QuoteHandle(spot), q, r, v)

maturity = today + ql.Period(1, ql.Years)
call = ql.VanillaOption(ql.PlainVanillaPayoff(ql.Option.Call, 100.0), ql.EuropeanExercise(maturity))

# 1. three engines on the same instrument
call.setPricingEngine(ql.AnalyticEuropeanEngine(process))
print(f"analytic      {call.NPV():.5f}")
print(f"delta {call.delta():.5f} gamma {call.gamma():.5f} vega/1% {call.vega()/100:.5f} "
      f"theta/day {call.theta()/365:.5f} rho/1% {call.rho()/100:.5f}")
analytic = call.NPV()
call.setPricingEngine(ql.FdBlackScholesVanillaEngine(process, 200, 400))
print(f"finite diff   {call.NPV():.5f}")
call.setPricingEngine(ql.MCEuropeanEngine(process, "pseudorandom", timeSteps=1,
                                          requiredSamples=200000, seed=42))
print(f"monte carlo   {call.NPV():.4f} +/- {call.errorEstimate():.4f}")

# 2. closed form by hand (Black-Scholes)
S, K, rr, s, T = 100.0, 100.0, 0.03, 0.20, dc.yearFraction(today, maturity)
d1 = (math.log(S / K) + (rr + s * s / 2) * T) / (s * math.sqrt(T))
d2 = d1 - s * math.sqrt(T)
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
print(f"closed form   {S*N(d1) - K*math.exp(-rr*T)*N(d2):.5f}  (T = {T})")

# 3. put-call parity
call.setPricingEngine(ql.AnalyticEuropeanEngine(process))
put = ql.VanillaOption(ql.PlainVanillaPayoff(ql.Option.Put, 100.0), ql.EuropeanExercise(maturity))
put.setPricingEngine(ql.AnalyticEuropeanEngine(process))
print(f"put {put.NPV():.5f}  C - P = {call.NPV()-put.NPV():.5f}  S - K e^-rT = {S-K*math.exp(-rr*T):.5f}")

# 4. American put on a binomial tree vs European put
amput = ql.VanillaOption(ql.PlainVanillaPayoff(ql.Option.Put, 100.0), ql.AmericanExercise(today, maturity))
amput.setPricingEngine(ql.BinomialVanillaEngine(process, "crr", 1000))
print(f"american put (CRR 1000) {amput.NPV():.5f} >= european put {put.NPV():.5f}")

# 5. Observer / LazyObject: change inputs, NPV follows
print(f"implied vol from analytic price {call.impliedVolatility(analytic, process):.6f}")
spot.setValue(105.0)
print(f"after spot -> 105      {call.NPV():.5f}")
spot.setValue(100.0)
vol.setValue(0.25)
print(f"after vol -> 25%       {call.NPV():.5f}")
vol.setValue(0.20)
ql.Settings.instance().evaluationDate = today + ql.Period(6, ql.Months)
print(f"evaluation date +6M    {call.NPV():.5f}")
ql.Settings.instance().evaluationDate = maturity + 1
print(f"after maturity         {call.NPV():.5f}  isExpired={call.isExpired()}")
ql.Settings.instance().evaluationDate = today
print(f"back to today          {call.NPV():.5f}")

# 6. up-and-out barrier call
barrier = ql.BarrierOption(ql.Barrier.UpOut, 120.0, 0.0,
                           ql.PlainVanillaPayoff(ql.Option.Call, 100.0), ql.EuropeanExercise(maturity))
barrier.setPricingEngine(ql.AnalyticBarrierEngine(process))
print(f"up-and-out call, barrier 120  {barrier.NPV():.5f}")
