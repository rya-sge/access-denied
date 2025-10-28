## **Traditional Futures vs. Perpetual Futures: A Technical Comparison**

### **Abstract**

Futures contracts are cornerstone instruments in both traditional and digital asset markets, enabling traders to speculate on or hedge against the future price of an underlying asset. While **traditional futures** have long been used in commodities, equities, and FX markets, the rise of cryptocurrency derivatives has popularized a novel contract type — the **perpetual futures** (or **perpetual swaps**). Despite similar payoff structures, the two instruments differ fundamentally in settlement mechanisms, price anchoring, and funding dynamics. This article provides a technical analysis of these differences and their implications for market structure, liquidity, and pricing efficiency.



****

If the contract is initiated at t < T, 

- we will write F (t, T) for the forward price 
- the payoffs will be:
  - S (T) − F(t, T) (long position) 
  - F (t, T) − S (T) (short position). 

As no payment is made at the beginning of the forward contract, the main problem is to find the forward price F (0, T) such that both parties are willing to enter into such agreement. 

One possible approach would be to compute the present value, which we know that is zero, by discounting the expected payoff of the contract. That is, 0 = V (0) = e −rTE [S (T) − F (0, T)] , 
$$
0 = V (0) = e {− rT}E [S (T) − F (0, T)] ,
$$
 which yields F (0, T) = E [S (T)]. 

Note that F (0, T) would depend on the distribution of S (T), hence, we would only have translated the problem to agree on which distribution use. • The solution comes from the fact that we can also invest in the money market and there exists only one value for F (0, T) such avoid arbitrages. • The price obtained does not depend on the distribution of S(T). Rules 1. Buy and hold strategy • Borrow S (0) NOK, to buy the asset at time zero • Hold it until time T. • At time T, the amount S(0) e rT to be paid to settle the loan is a natural candidate for F (0, T). Theorem 6.1 The forward price F (0, T) is given by F (0, T) = S (0) e rT , (6.1) where r is the constant risk free interest rate under continuous compounding. If the contract is initiated at time t ≤ T, then F (t, T) = S (t) e r(T −t) . (6.2) Remark 1. The formula in the previous theorem applies as long as the underlying asset does not generate an income (dividends) or a cost (storage and insurance costs for commodities). In this lecture we will, many times, be implicitly assuming that the underlying is a stock which does not pay dividends. Remark 2. In the case considered here we always have F (t, T) = S (t) e r(T −t) > S (t). Moreover, the difference F (t, T) − S (t), called the basis, converges to 0 as t converges to T.

------

### Contract Structure

> A forward contract is an agreement to buy or sell an asset on a fixed date in the future, called the delivery time, for a price specified in advance, called the forward price.

A **traditional futures contract** is a standardized agreement to buy or sell an underlying asset at a specified future date and price. Each contract is characterized by:

- A **defined expiration date** (e.g., monthly, quarterly) called delivery time, 
- **Settlement terms** — either *physical* (delivery of the underlying) or *cash-settled* (payment based on price difference).

A **perpetual futures contract**, in contrast, has **no expiration date**. Traders can hold positions indefinitely, subject to margin maintenance. This structure was pioneered in cryptocurrency markets (notably by BitMEX in 2016) to facilitate continuous leveraged trading without periodic contract rollovers.

Formally, if `P_t` is the perpetual futures price and `S_t` is the spot price, the contract’s price dynamics are anchored through a **funding rate mechanism** rather than time-based convergence.



## 



The forward price `F (0, T)` is given by 
$$
F (0, T) = S (0)e^{rt}
$$
where r is the constant risk free interest rate under continuous compounding. If the contract is initiated at time t ≤ T, then 
$$
F (t, T) = S(t)e^{r(T −t)}.
$$
Remark 1. The formula in the previous theorem applies as long as the underlying asset does not generate an income (dividends) or a cost (storage and insurance costs for commodities). In this lecture we will, many times, be implicitly assuming that the underlying is a stock which does not pay dividends.

https://www.uio.no/studier/emner/matnat/math/STK-MAT3700/h22/lecture-notes/lecture6__7_forvard_future_contract_option.pdf

------

### Price Convergence and Anchoring Mechanisms

#### Traditional Futures

Traditional futures prices are determined by the **cost-of-carry model**:

$$
Ft=S_t×e^{(r+c−y)(T−t)}
$$
Where:

- F_t = futures price at time ttt
- S_t = spot price
- r = risk-free interest rate
- c = storage or carrying cost
- y convenience yield
- T = time to maturity

As expiration approaches (T→t), the futures price F_t  converges to the spot price S_t. This **natural convergence** ensures pricing integrity and arbitrage alignment between spot and futures markets.

#### Perpetual Futures

Perpetual contracts lack a maturity date, so there is no time-based convergence. Instead, exchanges employ a **funding rate** mechanism — a recurring payment between long and short positions — designed to maintain price parity between the perpetual and spot markets.

If the perpetual price trades above the spot (P_t>S_t), the **funding rate** (f) becomes **positive**, requiring longs to pay shorts. 

Conversely, if P_t<S_t, the rate turns **negative**, and shorts pay longs.

The funding payment per interval is typically calculated as:

$$
Funding~ Payment=Position~Size×f
$$
This dynamic incentivizes traders to arbitrage discrepancies, thus stabilizing the perpetual contract around the spot price.

**Closing Your Position**

There are two main ways a position can be closed:

1. **Voluntary Closure:** You can choose to **close your position** at any time. When you do this, you either:
   - Claim your accumulated **profit**.
   - Realize your accumulated **loss**. Any losses incurred are **paid directly from the collateral** you deposited.
2. **Forced Closure (Liquidation)**: You can keep your position open *as long as* your deposited **collateral is sufficient to cover your current unrealized losses**. However, if the price moves significantly against you and your **losses grow to be very close to the total value of your deposited collateral**, the platform (like GMX) will automatically and **forcefully close your position**. This process is known as **liquidation**. When liquidated, your accumulated losses are paid using your collateral, meaning you effectively lose the collateral that was securing that specific position.
3. Auto-delevelearng

Reference

------

### Margining and Liquidation Mechanics

Both instruments are **margin-traded**, but their risk and liquidation processes differ.

- **Traditional Futures:** Margins are typically settled daily via **mark-to-market (MTM)**. Profits and losses are realized each day, and margin calls occur if account equity falls below maintenance requirements.
- **Perpetual Futures:** Margining is continuous, often updated every few seconds, and coupled with funding payments. Liquidations are automated and immediate if the trader’s equity falls below the liquidation threshold.

This real-time system, combined with high leverage (often up to 100×), makes perpetuals more sensitive to short-term volatility.

------

### Market Behavior and Use Cases

| Feature                  | **Traditional Futures**            | **Perpetual Futures**                  |
| ------------------------ | ---------------------------------- | -------------------------------------- |
| **Participants**         | Institutional traders, hedgers     | Retail and professional crypto traders |
| **Trading Horizon**      | Defined, periodic                  | Continuous                             |
| **Primary Function**     | Hedging, portfolio diversification | Speculation, liquidity provision       |
| **Rollover Requirement** | Yes                                | No                                     |
| **Funding Cost**         | None                               | Dynamic funding rate                   |

Traditional futures are favored in regulated environments (e.g., CME, ICE) for risk management and hedging. Perpetuals, being non-expiring, offer unparalleled liquidity and convenience for speculative trading but introduce **funding cost volatility** as a new dimension of risk.

------

### Practical Example

Suppose Bitcoin trades at **$60,000** on the spot market.

- **Traditional Futures (Quarterly)** might trade at **$61,200**, reflecting a 2% annualized premium due to cost-of-carry.
- **Perpetual Futures** might oscillate between **$59,950** and **$60,050**, staying near spot due to funding rate arbitrage.

If the perpetual premium persists above spot, the funding rate becomes positive — say f=0.01%f = 0.01\%f=0.01% every 8 hours — and long traders pay shorts to maintain balance.

------

### Conclusion

While **traditional futures** and **perpetual futures** share core derivative properties — leverage, margining, and directional exposure — they differ in structural design and market behavior.

- Traditional futures rely on **time-based convergence**.
- Perpetual futures rely on **funding-based price anchoring**.

The perpetual model’s flexibility and continuous liquidity make it ideal for crypto markets, though it introduces unique risks related to funding volatility and perpetual leverage exposure.

As perpetual contracts continue to evolve beyond digital assets into broader financial products, understanding these structural mechanics is essential for both traders and risk managers navigating hybrid derivative ecosystems.

------

Reference

https://financial.math.ncsu.edu/glossary-f/futures-contract/

[uio.no - Forward and Future contract. Option.](https://www.uio.no/studier/emner/matnat/math/STK-MAT3700/h22/lecture-notes/lecture6__7_forvard_future_contract_option.pdf)

ChatCPT witht he following input "what are the difference between traditional futures and perpetual futures ?"