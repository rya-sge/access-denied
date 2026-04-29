---
layout: post
title: Integrating Pyth Network Price Feeds — A Security-Focused Guide
date: 2026-03-13
lang: en
locale: en-GB
categories: blockchain defi security solidity solana
tags: pyth oracle price-feed defi solidity solana anchor security audit
description: Learn how to integrate Pyth Network pull oracle price feeds in Solidity and Solana programs, with a deep focus on security pitfalls — staleness, confidence intervals, fixed-point math, and adversarial selection.
image: /assets/article/blockchain/oracle/pyth-network-security.png
isMath: true
---

Pyth Network is a first-party oracle protocol that aggregates real-time price data from major financial institutions and market makers. Unlike traditional push oracles (e.g., Chainlink), Pyth uses a **pull model**: prices are published on a dedicated blockchain (Pythnet) and must be explicitly fetched and posted on the target chain by the caller. This architectural choice delivers sub-second latency and broader asset coverage, but it also introduces unique integration patterns and a specific set of security considerations that every developer must understand before going to production.

This article covers how Pyth works internally, how to integrate it correctly on EVM and Solana, and — most importantly — which vulnerabilities arise when the integration is incomplete or misunderstood.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills.

[TOC]

---

## How Pyth Works

### Architecture Overview

Pyth operates across three layers:

1. **Publishers** — exchanges, market makers, and institutional data providers that publish their observed prices and confidence intervals to Pythnet.
2. **Pythnet** — an application-specific blockchain operated by Pyth's data providers, built on Solana's validator software. Price aggregation occurs on-chain at every slot (approximately every 400 ms, matching Solana's slot duration).
3. **Wormhole / Hermes** — At each Pythnet slot, validators send the Merkle root of all price updates to the Wormhole contract. Wormhole guardians observe this message and produce a signed VAA (Verifiable Action Approval) attesting the Merkle root. Hermes, a web service run by the Pyth Data Association (and optionally by anyone), listens to both Pythnet and Wormhole, stores each price message with its Merkle proof and the corresponding signed VAA, and exposes REST/WebSocket APIs for retrieving the latest update.

This architecture means that **prices live on Pythnet, not on your target chain**. To use a price on Ethereum, Solana, or any other supported network, the caller must retrieve the latest update message from Hermes (which bundles the signed Merkle root VAA and the Merkle proof of the specific price) and submit it to the local Pyth contract, which verifies the Wormhole signatures and Merkle proof before storing the price on-chain.

### Price Aggregation

At each slot, Pyth aggregates individual publisher submissions using a robust two-step algorithm:

1. Each publisher submits a price `p_i` and a confidence interval `c_i`. Pyth gives each publisher three votes: one at `p_i`, one at `p_i - c_i`, and one at `p_i + c_i`. The **aggregate price** `μ` is the median of all votes.
2. The **aggregate confidence** `σ` is the larger of the distances from `μ` to the 25th and 75th percentiles of the votes.

This design is robust to outliers: a single rogue publisher cannot shift the aggregate price beyond the range of the 25th–75th percentiles of all publishers.

Pyth also computes an **EMA price** (`ema_price`) — a slot-weighted, inverse-confidence-weighted exponential moving average over approximately 1 hour. It is useful for settling contracts and smoothing volatility spikes, but it lags the spot price.

### Fixed-Point Representation

All Pyth prices use a fixed-point encoding:

$$
\begin{aligned}
\text{actual price} = \text{price} \times 10^{\text{exponent}}
\end{aligned}
$$

For example, with `exponent = -8`, a raw price of `7160106530699` corresponds to `$71,601.065`.
Both `price` and `conf` share the same `exponent`.

| Field       | Type    | Description                                      |
|-------------|---------|--------------------------------------------------|
| `price`     | `int64` | Integer representation of the price             |
| `conf`      | `uint64`| Confidence interval (half-width, same exponent) |
| `exponent`  | `int32` | Negative integer (typically −8 for crypto)      |
| `publishTime`| `uint` | Unix timestamp of the price update               |

This representation must be **correctly decoded** before any arithmetic. Failing to apply the exponent is one of the most common integration bugs.

---

## Integration on EVM (Solidity)

### The Pull Flow

Every EVM function that needs a Pyth price must follow this three-step sequence:

```
1. Off-chain: fetch signed VAA bytes from Hermes
2. On-chain:  pyth.updatePriceFeeds{ value: fee }(priceUpdate)
3. On-chain:  pyth.getPriceNoOlderThan(priceFeedId, maxAge)
```

The key interface is `IPyth` from `@pythnetwork/pyth-sdk-solidity`:

```solidity
interface IPyth {
    // Post a signed price update (VAA) on-chain. Requires paying a fee.
    function updatePriceFeeds(bytes[] calldata updateData) external payable;

    // Returns the fee required for the given update data.
    function getUpdateFee(bytes[] calldata updateData)
        external view returns (uint feeAmount);

    // Returns the current price if it is no older than `age` seconds.
    // Reverts with StalePrice (0x19abf40e) otherwise.
    function getPriceNoOlderThan(bytes32 id, uint age)
        external view returns (PythStructs.Price memory price);

    // Returns the price WITHOUT any staleness check. DANGEROUS.
    function getPrice(bytes32 id)
        external view returns (PythStructs.Price memory price);

    // Parses a price update for a specific timestamp range.
    // Used for delayed settlement / commit-reveal patterns.
    function parsePriceFeedUpdates(
        bytes[] calldata updateData,
        bytes32[] calldata priceIds,
        uint64 minPublishTime,
        uint64 maxPublishTime
    ) external payable returns (PythStructs.PriceFeed[] memory priceFeeds);
}
```

### Minimal Correct Integration

```solidity
pragma solidity ^0.8.0;

import "@pythnetwork/pyth-sdk-solidity/IPyth.sol";
import "@pythnetwork/pyth-sdk-solidity/PythStructs.sol";

contract PythConsumer {
    IPyth public immutable pyth;
    bytes32 public constant ETH_USD_FEED =
        0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace;

    uint256 public constant MAX_PRICE_AGE   = 60;   // seconds
    uint256 public constant MAX_CONF_BPS    = 200;  // 2% of price

    constructor(address pythContract) {
        pyth = IPyth(pythContract);
    }

    function executeWithPrice(bytes[] calldata priceUpdate) external payable {
        // 1. Update the on-chain price, paying the required fee.
        uint256 fee = pyth.getUpdateFee(priceUpdate);
        require(msg.value >= fee, "Insufficient fee");
        pyth.updatePriceFeeds{ value: fee }(priceUpdate);

        // 2. Read the price, enforcing a 60-second staleness window.
        PythStructs.Price memory p = pyth.getPriceNoOlderThan(ETH_USD_FEED, MAX_PRICE_AGE);

        // 3. Validate that the price is positive before any arithmetic.
        require(p.price > 0, "Non-positive price");

        // 4. Validate confidence interval.
        uint256 confBps = (uint256(p.conf) * 10_000) / uint256(uint64(p.price));
        require(confBps <= MAX_CONF_BPS, "Price confidence too wide");

        // 5. Scale to 18 decimals. p.exponent is typically -8.
        //    18 + exponent = 18 + (-8) = 10  →  multiply by 10^10
        uint256 priceScaled = _scalePrice(p.price, p.exponent, 18);

        // ... use priceScaled
    }

    function _scalePrice(int64 price, int32 expo, uint8 targetDecimals)
        internal pure returns (uint256)
    {
        require(price > 0, "Negative price");
        uint256 absPrice = uint256(uint64(price));
        int32 delta = int32(int8(targetDecimals)) + expo; // targetDecimals + exponent
        if (delta >= 0) {
            return absPrice * (10 ** uint32(delta));
        } else {
            return absPrice / (10 ** uint32(-delta));
        }
    }
}
```

### Delayed Settlement (Commit-Reveal)

High-frequency derivative protocols should not use the latest price at execution time, as adversaries can select a stale-but-still-valid VAA from just before a price move. Instead, pin the price to the **order submission timestamp** using `parsePriceFeedUpdates`:

```solidity
// At order submission (block.timestamp == orderTime):
// Store orderTime in the order struct.

// At execution (later block):
// Fetch from Hermes: GET /v2/updates/price/{orderTime}?ids[]=...
PythStructs.PriceFeed[] memory feeds = pyth.parsePriceFeedUpdates{
    value: pyth.getUpdateFee(priceUpdate)
}(
    priceUpdate,
    priceFeedIds,
    uint64(orderTime),       // minPublishTime
    uint64(orderTime + 5)    // maxPublishTime (±5s window)
);
```

This ensures the price used is from *when the user committed*, not from when they choose to execute.

---

## Integration on Solana (Anchor / Rust)

### The Pull Flow

On Solana, prices are posted into **price update accounts** (ephemeral, closeable) or **price feed accounts** (persistent PDAs, maintained by the Pyth Data Association). Both conform to the `PriceUpdateV2` struct from `pyth-solana-receiver-sdk`.

```
Off-chain:
  1. Fetch VAA bytes from Hermes
  2. Call transactionBuilder.addPostPriceUpdates(priceUpdateData)
     → posts price update accounts on Solana

On-chain:
  3. Pass price_update: Account<'info, PriceUpdateV2> to instruction
  4. Call price_update.get_price_no_older_than(&clock, max_age, &feed_id)
```

### Minimal Correct Integration (Anchor)

```rust
use anchor_lang::prelude::*;
use pyth_solana_receiver_sdk::price_update::{get_feed_id_from_hex, PriceUpdateV2};

declare_id!("...");

const MAX_AGE_SECONDS: u64 = 30;
const BTC_USD_FEED_HEX: &str =
    "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43";
const MAX_CONF_BPS: u64 = 200; // 2%

#[program]
pub mod pyth_consumer {
    use super::*;

    pub fn execute(ctx: Context<Execute>) -> Result<()> {
        let price_update = &ctx.accounts.price_update;

        // Validate feed ID AND staleness in one call.
        // Errors: PriceTooOld (10000) or MismatchedFeedId (10002)
        let feed_id = get_feed_id_from_hex(BTC_USD_FEED_HEX)?;
        let price = price_update
            .get_price_no_older_than(&Clock::get()?, MAX_AGE_SECONDS, &feed_id)?;

        // Validate confidence interval (price is i64, conf is u64).
        let conf_bps = price.conf
            .checked_mul(10_000)
            .and_then(|v| v.checked_div(price.price.unsigned_abs()))
            .ok_or(ErrorCode::ArithmeticError)?;
        require!(conf_bps <= MAX_CONF_BPS, ErrorCode::PriceUncertain);

        // Scale to 6-decimal USD (exponent typically -8).
        // target_decimals=6, exponent=-8 → shift = 6+(-8) = -2 → divide by 100
        let price_scaled = scale_price(price.price, price.exponent, 6)?;

        msg!("BTC/USD = {}", price_scaled);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Execute<'info> {
    pub payer: Signer<'info>,
    // Anchor automatically checks that this account is owned
    // by the Pyth Solana Receiver program.
    pub price_update: Account<'info, PriceUpdateV2>,
}

fn scale_price(price: i64, exponent: i32, target_decimals: i32) -> Result<u64> {
    require!(price > 0, ErrorCode::NegativePrice);
    let shift = target_decimals + exponent; // e.g. 6 + (-8) = -2
    let abs_price = price.unsigned_abs();
    if shift >= 0 {
        abs_price
            .checked_mul(10u64.pow(shift as u32))
            .ok_or(ErrorCode::ArithmeticError.into())
    } else {
        Ok(abs_price / 10u64.pow((-shift) as u32))
    }
}

#[error_code]
pub enum ErrorCode {
    ArithmeticError,
    PriceUncertain,
    NegativePrice,
}
```

---

## Security Vulnerabilities and Best Practices

The following sections catalogue the most impactful integration mistakes. Each is described with its root cause, concrete attack scenario, and remediation.

### 1. Using `getPrice()` / Reading Without Staleness Check (Critical)

**Root cause**: `getPrice()` (EVM) and reading `price_update.price_message` directly (Solana) return the stored price with no age validation. A price stored days ago is returned as if it were current.

**Attack scenario**: The attacker monitors the chain. They find that no price update has been submitted for 10 minutes (e.g., during a network hiccup). They interact with the protocol, which reads the 10-minute-old price. If the asset has moved 5%, they profit from the discrepancy.

**Remediation**:
- EVM: always use `getPriceNoOlderThan(feedId, maxAge)`.
- Solana: always use `get_price_no_older_than(&clock, maxAge, &feedId)`.
- Set `maxAge` conservatively: ≤ 60 s for volatile assets, ≤ 120 s for stablecoins.

### 2. Ignoring the Confidence Interval (High)

**Root cause**: The `conf` field of a Pyth price is not a mere footnote — it is the oracle's quantified uncertainty. Using `price.price` as a single point when `conf/price > 1%` means the protocol acts on a potentially misleading signal.

**Attack scenario (lending protocol)**: During a brief market dislocation, the confidence interval widens to 3% of the price. An attacker deposits collateral valued at `price + conf` while the protocol values it at `price`. They borrow the maximum allowed, then the price corrects, leaving the protocol undercollateralized.

**Best practice**:

$$
\begin{aligned}
\text{collateral value} &= \text{price} - \text{conf} \\
\text{loan value} &= \text{price} + \text{conf}
\end{aligned}
$$

Add a circuit breaker: if `conf / price > threshold`, revert or pause new positions.

```solidity
// Conservative collateral valuation
int256 conservativePrice = p.price - int256(uint256(p.conf));
require(conservativePrice > 0, "Price too uncertain");
```

### 3. Adversarial Price Selection (High)

**Root cause**: The pull model allows the caller to choose *which* VAA to submit. Any VAA that satisfies the staleness constraint is accepted. An attacker can use a VAA from 55 seconds ago (with a 60-second window) if it represents a more favorable price.

**Attack scenario**: Asset price drops 3% in the last 30 seconds. Attacker holds a VAA from 55 seconds ago (still within the 60-second window). They submit a sell order using this stale-but-valid price, profiting from the price that no longer exists.

**Mitigations**:
- Reduce `maxAge` to 5–10 seconds for highly sensitive protocols.
- Use delayed settlement with `parsePriceFeedUpdates` to pin the price to the order timestamp.
- Enforce a minimum holding period between opening and closing positions.

### 4. Same-Block Exploitation (Critical for Derivative Protocols)

**Root cause**: If a protocol allows positions to be opened and closed in the same block (or even the same transaction), an adversary can combine a flash loan with a stale price to extract profit with zero inventory risk.

**Attack scenario**:
1. Flash-borrow asset A to provide collateral.
2. Submit a stale VAA showing asset A at a **lower** price than the current market (or a **higher** price if shorting).
3. Open a **long** position at the stale low price (or a short at the stale high price).
4. Submit the current price update and close the position at the now-higher market price, capturing the spread.
5. Repay the flash loan and keep the profit — zero inventory risk, single atomic transaction.

**Remediation**: Separate commitment from execution. Require at least 1–2 blocks between position open and close. Use commit-reveal schemes.

### 5. Fixed-Point Exponent Not Applied (High)

**Root cause**: Developers treat `price.price` as a human-readable dollar amount. In reality, it is a large integer that must be multiplied (or divided) by `10^exponent` to obtain the real value.

**Attack scenario**: A contract computes a user's position value as:
```solidity
uint256 value = uint256(int256(price.price)) * collateralAmount;
```
With `price.price = 7160106530699` (BTC ~$71,601) and `exponent = -8`, this produces a value `10^8` times larger than intended, allowing the user to borrow an astronomically large amount.

**Remediation**: Always apply the exponent before any arithmetic. Write and test a dedicated `scalePrice` utility that handles both positive and negative exponents without overflow.

### 6. Missing Account Owner Check on Solana (Critical)

**Root cause**: The `PriceUpdateV2` struct is publicly documented. Without an ownership check, an attacker can create an account with the same layout but arbitrary price data.

**Attack scenario**: Attacker creates a fake account with `price = MAX_I64` for BTC/USD. They pass it to a lending instruction. The protocol reads an astronomically high BTC price and allows the attacker to borrow all protocol funds.

**Remediation**: In Anchor, always declare price accounts as `Account<'info, PriceUpdateV2>`. Anchor automatically verifies the account is owned by `pyth_solana_receiver_sdk::ID`. Without Anchor, add a manual check:

```rust
// Native Solana (no Anchor): check owner before deserialising
if ctx.accounts.price_update.owner != &pyth_solana_receiver_sdk::ID {
    return Err(ProgramError::InvalidAccountOwner);
}
```

### 7. Feed ID Not Validated (Critical)

**Root cause**: `PriceUpdateV2` stores a price for *some* feed. If the on-chain program does not verify *which* feed is in the account, an attacker can pass a price update for a cheaper asset where an expensive one is expected.

**Attack scenario**: A protocol accepts USDC as collateral and expects the USDC/USD feed (≈ $1). An attacker passes a price update account for ETH/USD (≈ $3,000) instead. The protocol values 1 USDC of collateral at $3,000 and allows the attacker to borrow far more than they should. The inverse scenario is equally dangerous: if the protocol expects ETH/USD but the attacker substitutes a low-price feed, they can borrow against artificially inflated collateral and drain the protocol.

**Remediation**: Always pass the expected `feed_id` to `get_price_no_older_than`. This validates the feed atomically with the staleness check (error `10002 MismatchedFeedId`).

### 8. Partial Verification (High on Solana)

**Root cause**: Using `addPostPartiallyVerifiedPriceUpdates` reduces the number of Wormhole guardian signatures verified, enabling single-transaction posting at the cost of a weaker trust assumption.

**Attack scenario**: With fewer required signatures, a subset of compromised guardian nodes could submit a fraudulent price update that passes the partial verification threshold.

**Remediation**: Use full verification (`addPostPriceUpdates`) for all high-value operations. Reserve partial verification for low-stakes, latency-critical use cases where the security trade-off is explicitly accepted and documented.

### 9. Market Hours and Price Availability (Medium)

**Root cause**: Pyth follows traditional market hours for equities, commodities, and FX pairs. Outside these hours, the oracle will not publish new prices, and the last published price will quickly become stale.

**Attack scenario**: A protocol accepts AAPL/USD as collateral. After NYSE market close, no new prices are published. The staleness check correctly causes a revert — but if the protocol silently falls back to the last known price, it exposes itself to gap risk when markets reopen.

**Remediation**: Ensure the staleness revert is surfaced to users. Pause new position openings when a feed is unavailable. For futures-based assets (commodities, volatility indices), apply a weighted-average strategy across contract maturities to avoid negative-price scenarios.

### 10. EMA vs Spot Price Confusion (Medium)

**Root cause**: `getEmaPrice()` returns an exponential moving average over ~1 hour — it lags spot by design. Using it for real-time collateral valuation means a sudden price crash is not immediately reflected.

**Attack scenario**: BTC drops 15% in 2 minutes. The EMA still shows a price close to the pre-crash level. An attacker borrows against BTC collateral at the EMA-inflated value before the average catches up, then lets the position be liquidated with insufficient collateral.

**Remediation**: Use EMA only for settlement and smoothing, not for real-time collateral/liquidation checks. Use `getPriceNoOlderThan` / `get_price_no_older_than` (spot) for margin calculations.

---

## Summary of Security Checks

| Vulnerability | Severity | EVM | Solana |
|---|---|---|---|
| `getPrice()` without staleness | Critical | ✓ | — |
| No owner check on `PriceUpdateV2` | Critical | — | ✓ |
| Feed ID not validated | Critical | Medium risk | Critical risk |
| Same-block open/close exploit | Critical | ✓ | ✓ |
| Confidence interval ignored | High | ✓ | ✓ |
| Adversarial VAA selection | High | ✓ | ✓ |
| Fixed-point exponent not applied | High | ✓ | ✓ |
| Partial verification | High | — | ✓ |
| `updatePriceFeeds` skippable | High | ✓ | — |
| Market hours not handled | Medium | ✓ | ✓ |
| EMA used for spot valuation | Medium | ✓ | ✓ |
| Admin can swap Pyth address | Medium | ✓ | — |

---

## Conclusion

Pyth Network's pull oracle model delivers high-frequency, aggregated prices with quantified uncertainty — but it places more responsibility on the integrator than a traditional push oracle. The key rules are:

- **Always update before reading**: `updatePriceFeeds` is not optional.
- **Always use `getPriceNoOlderThan`** / `get_price_no_older_than`: never bypass the staleness check.
- **Always validate the confidence interval**: use price bounds, not a single point.
- **Always validate the feed ID**: do not trust the caller to pass the correct price account.
- **Always apply the exponent**: `price.price` is a raw integer, not a dollar value.
- **For derivative protocols**: prevent same-block exploitation and adversarial VAA selection through delayed settlement, commit-reveal, or minimum holding periods.

Following these principles converts Pyth from a latency risk into a genuine competitive advantage — accurate, fresh, and manipulation-resistant price data with sub-second granularity.

![pyth-network-security]({{site.url_complet}}/assets/article/blockchain/oracle/pyth-network-security.png)

```
@startmindmap
* Pyth Integration Security
** Architecture
*** Pull oracle model
*** Pythnet aggregation
*** Wormhole VAA / Hermes
*** Fixed-point (price × 10^exponent)
** EVM Integration
*** updatePriceFeeds (required)
*** getUpdateFee (pay correctly)
*** getPriceNoOlderThan (not getPrice)
*** parsePriceFeedUpdates (delayed settlement)
** Solana Integration
*** PriceUpdateV2 account
*** Account owner check (Anchor auto)
*** get_price_no_older_than
*** Full vs Partial verification
** Critical Vulnerabilities
*** No staleness check
*** Feed ID not validated
*** No owner check (Solana)
*** Same-block open/close
** High Vulnerabilities
*** Confidence interval ignored
*** Adversarial VAA selection
*** Exponent not applied
*** updatePriceFeeds skippable
** Medium Vulnerabilities
*** EMA used for spot
*** Market hours not handled
*** Admin can swap oracle address
** Best Practices
*** Conservative price bounds (price ± conf)
*** Circuit breaker on wide confidence
*** Commit-reveal / delayed settlement
*** Minimum holding period
*** Immutable Pyth contract address
@endmindmap
```

---

## Reference

- [Claude Code](https://claude.com/product/claude-code)
- [Pyth Network Documentation](https://docs.pyth.network/price-feeds)
- [Pyth Best Practices](https://docs.pyth.network/price-feeds/core/best-practices)
- [Pyth EVM Pull Integration](https://docs.pyth.network/price-feeds/core/use-real-time-data/pull-integration/evm)
- [Pyth Solana Pull Integration](https://docs.pyth.network/price-feeds/core/use-real-time-data/pull-integration/solana)
- [Pyth Price Aggregation](https://docs.pyth.network/price-feeds/core/how-pyth-works/price-aggregation)
- [Pyth EMA Price Aggregation](https://docs.pyth.network/price-feeds/core/how-pyth-works/ema-price-aggregation)
- [Pyth EVM Error Codes](https://docs.pyth.network/price-feeds/core/error-codes/evm)
- [Pyth SVM Error Codes](https://docs.pyth.network/price-feeds/core/error-codes/svm)
- [pyth-sdk-solidity (GitHub)](https://github.com/pyth-network/pyth-crosschain/tree/main/target_chains/ethereum/sdk/solidity)
- [pyth-solana-receiver-sdk (GitHub)](https://github.com/pyth-network/pyth-crosschain/tree/main/target_chains/solana/pyth_solana_receiver_sdk)
