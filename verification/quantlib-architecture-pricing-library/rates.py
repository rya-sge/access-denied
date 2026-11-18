"""Yield-curve bootstrap, vanilla swap, fixed-rate bond.

Claims checked in the article: the bootstrapped curve reprices its helpers,
a spot 5Y swap returns the 5Y quote when its conventions match the helper,
the convention-mismatch pitfall (Unadjusted fixed leg -> 3.39981 %), and the
bond clean/dirty/accrued/yield figures.
"""
import QuantLib as ql

today = ql.Date(15, ql.January, 2025)
ql.Settings.instance().evaluationDate = today
cal = ql.TARGET()
settlement = 2


def build_curve(fixed_convention):
    deposits = [("3M", 0.030), ("6M", 0.031)]
    swaps = [("2Y", 0.032), ("5Y", 0.034), ("10Y", 0.036)]
    helpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(x)), ql.Period(t), settlement, cal,
                                    ql.ModifiedFollowing, False, ql.Actual360()) for t, x in deposits]
    handle = ql.RelinkableYieldTermStructureHandle()
    euribor6m = ql.Euribor6M(handle)
    helpers += [ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(x)), ql.Period(t), cal, ql.Annual,
                                  fixed_convention, ql.Thirty360(ql.Thirty360.BondBasis), euribor6m)
                for t, x in swaps]
    curve = ql.PiecewiseLogCubicDiscount(settlement, cal, helpers, ql.Actual365Fixed())
    curve.enableExtrapolation()
    handle.linkTo(curve)
    curve.nodes()                     # force the lazy bootstrap
    err = max(abs(h.impliedQuote() - h.quote().value()) for h in helpers)
    return curve, handle, euribor6m, err


curve, handle, euribor6m, err = build_curve(ql.ModifiedFollowing)
print(f"QuantLib {ql.__version__}; curve reference date {curve.referenceDate()}; max helper error {err:.1e}")
for years in (1, 5, 10):
    d = curve.referenceDate() + ql.Period(years, ql.Years)
    print(f"  {years:>2}Y discount {curve.discount(d):.6f}  zero (cont.) "
          f"{curve.zeroRate(d, ql.Actual365Fixed(), ql.Continuous).rate():.5%}")

swap = ql.MakeVanillaSwap(ql.Period(5, ql.Years), euribor6m, 0.0)
print(f"5Y swap fair rate, matching conventions: {swap.fairRate():.5%}")
_, _, euribor_bad, err_bad = build_curve(ql.Unadjusted)
swap_bad = ql.MakeVanillaSwap(ql.Period(5, ql.Years), euribor_bad, 0.0)
print(f"5Y swap fair rate, curve bootstrapped with Unadjusted fixed leg: {swap_bad.fairRate():.5%} "
      f"(helpers still repriced to {err_bad:.1e})")
print(f"difference: {(swap.fairRate() - swap_bad.fairRate()) * 1e4:.4f} bp")

payer = ql.MakeVanillaSwap(ql.Period(5, ql.Years), euribor6m, 0.033, nominal=1_000_000)
print(f"payer 5Y at 3.30 %, notional 1,000,000: NPV {payer.NPV():,.2f}")

issue = ql.Date(15, ql.March, 2023)
sched = ql.Schedule(issue, issue + ql.Period(7, ql.Years), ql.Period(ql.Annual), cal,
                    ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, False)
isma = ql.ActualActual(ql.ActualActual.ISMA)
bond = ql.FixedRateBond(settlement, 100.0, sched, [0.04], isma)
bond.setPricingEngine(ql.DiscountingBondEngine(handle))
print(f"bond 4% 2030: clean {bond.cleanPrice():.4f} dirty {bond.dirtyPrice():.4f} "
      f"accrued {bond.accruedAmount():.4f} settlement {bond.settlementDate()}")
y = bond.bondYield(isma, ql.Compounded, ql.Annual)
rate = ql.InterestRate(y, isma, ql.Compounded, ql.Annual)
print(f"  yield {y:.4%}  modified duration {ql.BondFunctions.duration(bond, rate, ql.Duration.Modified):.4f}"
      f"  convexity {ql.BondFunctions.convexity(bond, rate):.4f}")
for cf in bond.cashflows():
    if cf.date() > today:
        print(f"    {cf.date()}  {cf.amount():.4f}")
