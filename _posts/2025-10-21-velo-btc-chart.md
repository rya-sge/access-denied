---
layout: post
title: Velo - BTC chart Overview
date:   2025-10-21
lang: en
locale: en-GB
categories: blockchain
tags: bitcoin btc
description: BTC chart statistic by Velo
image:
isMath: 
---

Here is the list of data related to BTC price available here: [Velo - Futures - BTC](https://velo.xyz/futures/BTC) with a summary made with ChatGPT.

[TOC]

## Futures

- BTC 24h Volume
- BTC Open Interest Snapshot
- BTC funding Rare (APR)
- BTC Open Interest
- BTC Price
- BTC CVD Dollars
- BTC Liquidations
  BTC 3 month Annualized Basis
- BTC Volume
- BTC 1m Average Return By Hour (UTC)
- BTC 1m Average Return By Day (UTC)
- BTC Cumulative Return By Session 

### BTC 24h Volume

The total dollar value of all BTC traded across all major exchanges in the past 24 hours.

- **Why it matters**: High volume = high interest/activity. It can indicate strong momentum or market participation.

------

### BTC Open Interest Snapshot

The total number of outstanding BTC futures or options contracts at a given time (a "snapshot").

- **Why it matters**: It shows how much money is locked into derivatives. Rising OI means traders are opening more positions.

------

### BTC Funding Rate (APR)

The interest paid between long and short traders on perpetual futures, shown annualized.

- **Why it matters**:
  - **Positive rate** = Longs paying shorts → Bullish bias
  - **Negative rate** = Shorts paying longs → Bearish bias
  - **APR** means this rate is scaled to a yearly equivalent.

------

### BTC Open Interest

Same as above, but often shown as a trend over time.

- **Why it matters**: Helps spot leverage build-up or unwind (e.g., if OI drops sharply = possible liquidations).

------

### BTC Price

Current spot price of Bitcoin.

- **Why it matters**: The most fundamental stat, obviously. Everything else revolves around this.

------

### BTC CVD (Cumulative Volume Delta) - Dollars

The net difference between market buys and sells, in dollar terms.

- **Why it matters**:
  - Positive CVD = More aggressive buying
  - Negative CVD = More aggressive selling
  - It helps you see "who’s in control" of the tape.

See also [tradingview.com - Cumulative Volume Delta](https://www.tradingview.com/support/solutions/43000725058-cumulative-volume-delta/)

------

### BTC Liquidations

Total value of forced closures of leveraged positions (longs or shorts).

- **Why it matters**: High liquidations = High volatility and potential reversals (e.g., long squeeze → price drops fast).

------

### BTC 3-Month Annualized Basis

The premium of 3-month BTC futures over the spot price, shown as annualized %.

- **Why it matters**:
  - Positive basis = Bullish bias (futures trade above spot)
  - Zero/negative = Bearish or cautious sentiment

------

### BTC Volume

Similar to 24h volume but can refer to a specific timeframe (hourly/daily/etc.).

- **Why it matters**: Helps assess market activity strength during specific windows.

------

### BTC 1m Average Return By Hour (UTC)

Average return per minute, grouped by each hour of the day (UTC timezone).

- **Why it matters**: Shows what hours tend to be most bullish or bearish based on historical 1-min returns.

------

### BTC 1m Average Return By Day (UTC)

Average return per minute, grouped by each day of the week.

- **Why it matters**: Helps you spot "day of the week" trends — maybe BTC tends to be bullish on Mondays, for instance.

------

### BTC Cumulative Return By Session

Total return over time, grouped by sessions (e.g., Asia, Europe, US trading hours).

- **Why it matters**: Lets you see which trading session is driving the market. For example, maybe Asia is mostly selling and US is buying.

------

## Option

- BTC implied Volatility Term structure
- BTC 24h Top Volume options
- BTC ATM Implied Volatility
- BTC 25 delta Skew
- BTC Spot-Vol Correlation
- BTC Implied Volatility Term Structure Slope

### BTC Implied Volatility Term Structure

A curve showing *implied volatility (IV)* for BTC options across different expirations (e.g. 7d, 30d, 90d, 180d, etc.).

------

### BTC 24h Top Volume Options

The most actively traded BTC option contracts in the last 24 hours (by volume).

- Example: BTC-29NOV24-70000-C means a call option expiring Nov 29, 2024, with a strike of $70,000.

- **Why it matters**:
  - Shows where traders are speculating or hedging most.
  - High volume near a specific strike/expiry = “hot zone” for market expectations.

------

### BTC ATM Implied Volatility

The implied volatility of “At-The-Money” (ATM) options — where strike ≈ current BTC price.

- **Why it matters**:
  - It’s the market’s best estimate of expected short-term volatility.
  - Often used as the baseline for comparing other options (like the VIX for BTC).

See also [Corporate Finance Institute - At The Money (ATM)](https://corporatefinanceinstitute.com/resources/derivatives/at-the-money-atm/)

------

### BTC 25-Delta Skew

The difference in implied volatility between **25-delta call options** and **25-delta put options**. Typically expressed as: `IV(call 25d) – IV(put 25d)`

- **Why it matters**:
  - Measures **sentiment bias**.
  - **Negative skew** → puts (downside protection) more expensive → fear / bearish sentiment.
  - **Positive skew** → calls more expensive → bullish sentiment.
  - It’s a key “fear vs greed” indicator in options markets.

See also [marketchameleon - Option Volatility Skew](https://marketchameleon.com/Learn/Skew)

------

### BTC Spot-Vol Correlation

The statistical correlation between **BTC price changes (spot)** and **implied volatility changes**.

- **Why it matters**:
  - **Negative correlation** (usual case): when BTC falls, IV rises → traders buy options for protection.
  - **Positive correlation**: when BTC rallies, IV also rises → traders chasing upside exposure.

------

### BTC Implied Volatility Term Structure Slope

A quantitative measure of the *steepness* of the IV term structure curve (difference between long- and short-dated IV).

- **Why it matters**:
  - **Steep positive slope** → market expects more long-term uncertainty or potential big moves later.
  - **Flat or inverted slope** → near-term event risk or calm longer-term outlook.
  - Useful for timing trades — e.g., buying short-term options ahead of volatility spikes.