---
layout: post
title: "BIO Tokenomics - Supply, Unlocks, Demand and Value Capture of Bio Protocol's Token"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain defi finance
tags: defi desci token tokenomics governance staking
series: bio-protocol
description: "BIO tokenomics on 18 Sept 2026: 3.32 B fully minted, 2.15 B circulating, 0.91 B vesting on-chain, veBIO locks, unlock pace, and no revenue path to the token."
image: /assets/article/blockchain/defi/bio-protocol/2026-09-18-bio-tokenomics-mindmap.png
isMath: false
---

[Bio Protocol](https://www.bio.xyz/) is a decentralised-science (DeSci) launchpad that funds biotech research through token-governed communities, and `BIO` is its native token, live on Ethereum, Base, BNB Chain and Solana since the token generation event of 3 January 2025. The two previous articles in this series covered the protocol and its EVM contracts, and its Solana governance program. This one looks only at the token: how much exists, who holds the unvested part, how fast it unlocks, why anyone needs to hold it, and whether protocol activity reaches holders.

The analysis follows a fixed framework (supply, distribution, unlocks, demand, value capture, emissions, staking, sustainability, valuation) and ends with a snapshot, strengths, risks and the five metrics worth tracking. Figures are dated, sourced, and labelled as measured or estimated; where trackers disagree, the disagreement is shown rather than averaged away. Nothing here is a price forecast or a recommendation to buy or sell.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Method and data sources

All market data was collected on **18 September 2026 between 14:10 and 14:20 UTC**. Four kinds of source are used, in decreasing order of reliability:

- **On-chain reads** through public JSON-RPC endpoints: `totalSupply()` of the `BIO` contracts on the four chains, `BIO` balances held by the two `veBIO` staking contracts and by the two `vBIO` vesting contracts, and `totalSupply()` of the vesting contracts, which equals the amount committed to schedules and not yet released.
- **Official documentation** at docs.bio.xyz: allocation buckets, vesting terms, V2 mechanics (Ignition Sale, Liquidity Engine, staking, BioXP).
- **Aggregators**: CoinGecko for price, market cap, circulating supply and volume; DefiLlama's API for the protocol TVL; DropsTab and Tokenomist for unlock tracking.
- **Reporting** on governance decisions, chiefly the BIOPSY-22 vote that rescheduled the team unlock.

DefiLlama's token and unlock pages could not be fetched directly and its emissions endpoint is paid, so unlock figures come from DropsTab and Tokenomist, cross-checked against the documentation and the on-chain vesting balances. DefiLlama does not track fees or revenue for Bio Protocol, which matters for the valuation section.

## Tokenomics snapshot

| Metric | Value | Source, date | Type |
|--------|-------|--------------|------|
| Price | 0.0269 USD | CoinGecko, 2026-09-18 14:11 UTC | Measured |
| Market capitalisation | 57.7 M USD | CoinGecko | Measured |
| Fully diluted valuation (FDV) | 89.3 M USD | CoinGecko | Measured |
| MC / FDV | 0.65 | Computed | Derived |
| Circulating supply | 2,145,029,070 BIO (64.6 %) | CoinGecko, Tokenomist | Measured, methodology-dependent |
| Total = max supply | 3,320,000,000 BIO | Docs; on-chain sum across 4 chains | Measured |
| 24 h volume | 13.8 M USD (24 % of MC) | CoinGecko | Measured |
| All-time high | 0.889 USD on 2025-01-03 (TGE day); current price is 97 % below | CoinGecko | Measured |
| All-time low | 0.0158 USD on 2026-03-29 | CoinGecko | Measured |
| Last Genesis sale price | 0.066 USD (round 2.5, Nov 2024, 211 M USD pre-valuation) | ICO Drops | Reported |
| Total raised | 36.8 M USD in 4 rounds; Genesis rounds 33 M USD | ICO Drops; CoinGecko Learn | Reported |
| BIO locked in `veBIO` | 115.4 M BIO (59.7 M Ethereum + 55.7 M Base), 3.5 % of total, 5.4 % of circulating | On-chain, 2026-09-18 | Measured |
| BIO committed to `vBIO` vesting schedules | 909.1 M BIO (27.4 % of total) | On-chain, 2026-09-18 | Measured |
| Protocol TVL | 3.54 M USD (1.93 M Ethereum, 1.61 M Base) | DefiLlama API | Measured |
| MC / TVL | 16.3 | Computed | Derived |
| Protocol revenue | Not tracked by DefiLlama; no published figure | | Unknown |

## Supply

### Fully minted, and not growing

The documentation describes the 3.32 B supply as "uncapped", with the qualification that issuing more would require deploying a new token contract. The deployed `BioToken.sol` has an uncapped `MINTER_ROLE`, but the four on-chain supplies sum to the documented total:

| Chain | Contract | `totalSupply()` on 2026-09-18 |
|-------|----------|-------------------------------|
| Ethereum | `0xcb15…5ffa` | 2,944,057,731 |
| Base | `0x226A…7DD2` | 182,429,179 |
| Solana | `bioJ9…SvUJ` | 183,741,678 |
| BNB Chain | `0x226a…7dd2` | 9,769,564 |
| **Sum** | | **3,319,998,152** |

The sum matches 3.32 B to within two thousand tokens, which is bridge rounding. Two conclusions follow. The bridge is burn-and-mint, so the four balances are not double-counted. And the entire supply has been minted: there is no protocol inflation schedule, and no minting has occurred since the initial distribution beyond bridging. There is also no burn mechanism; the only burn in the V2 design is of *project* tokens forfeited by `veBIO` airdrop recipients who redeem early, not of `BIO`.

### Circulating versus unlocked versus vested

Three numbers are routinely confused, and the trackers disagree on them:

| Quantity | Value | Who says so |
|----------|-------|-------------|
| Circulating supply | 2.145 B (64.6 %) | CoinGecko, Tokenomist |
| Circulating supply | 2.48 B | CoinMarketCap (per Tokenomist's comparison) |
| Unlocked | 2.47 B, 77.2 % of a 3.2 B base | DropsTab |
| Locked in vesting schedules | 728 M (DropsTab) / 1.175 B (Tokenomist) | Trackers |
| Committed to on-chain vesting contracts, unreleased | 909.1 M | On-chain (`vBIO` master 881.0 M + subordinate 28.1 M) |

The spread comes from the 830 M **Ecosystem Incentives** bucket (25 % of supply), which the documentation lists with "no vesting" and DropsTab marks as unlocked at TGE. It sits in treasury control, so CoinGecko excludes most of it from circulation while DropsTab counts it as unlocked. The on-chain figure is the firm one: 909 M `BIO` are inside vesting contracts and not yet released, and the vesting contracts hold 921.5 M, the 12 M difference being surplus the admin can withdraw.

CoinGecko's non-circulating 1.175 B minus the 909 M in vesting leaves roughly 266 M that is neither vesting nor counted as circulating, which is consistent with treasury-held incentives (estimate).

## Distribution

The initial allocation, from the documentation, with the on-chain or tracker state where available:

| Bucket | Share | BIO | Vesting terms (docs) | Unlocked per DropsTab, 2026-09-18 |
|--------|-------|-----|----------------------|-----------------------------------|
| Ecosystem Incentives | 25.0 % | 830.0 M | None; spent by governance vote | 100 % (treasury) |
| Core Contributors | 21.2 % | 703.8 M | 1-year cliff, 6-year vest | 40.9 % |
| Community Auction | 20.0 % | 664.0 M | 50 % liquid, 50 % linear 1 year | 100 % (since Nov 2025) |
| Investors | 13.6 % | 451.5 M | 1-year cliff, 4-year vest | 62.3 % |
| Community Airdrop | 6.0 % | 199.2 M | Public part liquid; BioDAO and genesis members 1-year cliff, 6-year vest | 70.5 % |
| Molecule | 5.0 % | 166.0 M | 4-year vest | 82.8 % |
| Molecule Ecosystem Fund | 5.0 % | 166.0 M | 4-year vest (docs); at TGE (DropsTab) | 100 % per DropsTab |
| Advisors | 4.2 % | 139.4 M | 1-year cliff, 6-year vest | 41.0 % |

The documentation frames this as 56 % community and 44 % insiders. Reading it by control rather than by label gives a different picture:

- **Insider allocations** (team, investors, advisors, Molecule, Molecule fund) total **49 %** of supply.
- **Treasury-discretionary** supply (Ecosystem Incentives) is a further **25 %**, released by governance votes in which `BIO` and `vBIO` holders, so the same insiders while vesting, carry weight. One such vote, BIOPSY-5, allocated 133 M `BIO` (4 % of supply) to the bio/acc rewards programme; VitaDAO alone received 21 M in August 2024.
- **Sold or airdropped to the public**: the 20 % auction plus the liquid part of the 6 % airdrop, so at most **26 %**.

Ownership concentration by wallet was not measured for this article; the structural concentration above is the relevant fact for governance, since `vBIO` counts unvested team and investor tokens as voting balance.

## Unlocks

![BIO vesting Gantt from TGE in January 2025 to 2030: auction fully unlocked by November 2025, team tranche spread over November 2025 to May 2026 with the remainder linear to May 2030, investors and Molecule linear to 2028, advisors and DAO airdrop to 2030]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-vesting-schedule-gantt.png)

### The team schedule and BIOPSY-22

The team's vesting clock started before the TGE: the one-year cliff fell on **28 May 2025**, which places the vesting start at 28 May 2024. That cliff would have released one sixth of the team allocation, **117.3 M BIO**, in a single day. Governance proposal **BIOPSY-22** passed with 139.1 M tokens in favour across 33 votes and 143 % of quorum, and rescheduled that tranche to a linear release from **14 November 2025 to 14 May 2026**. The remaining five sixths, 586.5 M, continue linearly from 28 May 2025 to 28 May 2030, which is **117.3 M BIO per year, about 321,000 per day**.

The stated reason was to "limit volatility ahead of anticipated value-driving events" while the V2 launchpad and its revenue features were being built.

### Current pace

DropsTab reports the next daily unlock at **722,657 BIO**, about 19,400 USD or 0.02 % of total supply, across several allocations. A bottom-up estimate from the documentation's terms and DropsTab's per-bucket progress gives a similar figure:

| Bucket | Remaining (est.) | Ends (est.) | Per year (est.) |
|--------|------------------|-------------|-----------------|
| Core Contributors | 586.5 M less what has vested since May 2025 | May 2030 | 117.3 M |
| Investors | 170 M | mid-2028 | 101 M |
| Molecule | 28 M | Jan 2028 | 22 M |
| Advisors | 82 M | May 2030 | 22 M |
| Community Airdrop (DAO part) | 59 M | May 2030 | 16 M |
| Molecule Ecosystem Fund | 0 (DropsTab) or up to 41.5 M/year (docs) | | 0 to 41.5 M |
| **Total** | | | **278 M to 320 M per year** |

At the 18 September 2026 price, 278 M to 320 M `BIO` per year is **7.5 M to 8.6 M USD** of new supply, or **13 % to 15 % of the circulating supply**. Against the 13.8 M USD daily volume, the daily unlock of roughly 760,000 to 880,000 `BIO` is about 0.15 % of a day's trading. The unlock is therefore small relative to liquidity on any given day and material relative to float over a year. No single cliff remains: all buckets are now in linear release, so there is no scheduled one-day supply event ahead.

Two discrepancies to keep in mind. DropsTab's category totals use a 3.2 B base rather than 3.32 B, so its absolute figures run about 3.6 % low. And the Molecule Ecosystem Fund is shown as fully unlocked by DropsTab while the documentation says four-year vesting; the on-chain vesting balance of 909 M cannot settle it because the master contract aggregates all buckets.

## Demand

The documentation lists five uses of `BIO`. Each is assessed for whether it creates a reason to hold rather than to hold briefly:

- **Staking for `veBIO` and BioXP.** Locking `BIO` for 1 week to 2 years mints a decaying `veBIO` balance (`weeks_remaining / 104` per token) that accrues **BioXP** daily. BioXP is the priority weight in oversubscribed Ignition Sales and expires after 14 days. This is the strongest demand driver in the design: a launch participant who wants allocation priority needs a `veBIO` position that is continuously maintained. On-chain, **115.4 M `BIO`** are in the two `veBIO` contracts, 5.4 % of circulating supply. Public reporting at an unspecified later date cited "over 125 M" staked, after Ethereum staking opened in August 2025 had quadrupled the amount locked, so the locked amount has since been flat to slightly down.
- **Airdrops to `veBIO` holders.** Every token launched through an Ignition Sale airdrops a share of its supply to stakers pro rata, with 20 % redeemable at TGE and 80 % over six months. The reward is denominated in the new project's token, not in `BIO`.
- **Governance.** `BIO` and `vBIO` are the governance tokens today; `veBIO` is planned to take over "following a formal governance proposal". BIOPSY-22 shows the mechanism is used for supply decisions.
- **Pair asset and payments.** The documentation names `BIO` as "the primary pair asset for all project tokens" and as payment for BioAgent services. In the V2 Liquidity Engine as documented, however, the initial pool is `USDC`/project token; a `BIO`/token pool is added later if milestones are met. Sales settle in `USDC`, not `BIO`.
- **Instant BioXP mint.** Users may spend `BIO` to mint BioXP at 0.01 USD per point. Where the spent `BIO` goes (treasury, burn) is not documented.

The demand case therefore rests on the launch cadence: `veBIO` is worth holding in proportion to the number and quality of Ignition Sales and the size of their airdrops to stakers.

## Value capture

![Value flow in Bio V2: BIO locks into veBIO and BioXP for launch priority and project-token airdrops; USDC from Ignition Sales seeds AMM pools whose 1 % swap tax is split 70/30 between project and Bio treasuries; vesting contracts and ecosystem incentives release BIO to the market, and no buyback or burn path is documented]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-tokenomics-value-flow.png)

Protocol revenue in V2 has one documented source: a **1 % fee on every buy and sell of a launched project token**, split **70 % to the project treasury and 30 % to the Bio Protocol treasury**. Two further mechanisms fund *projects* rather than the protocol: the `USDC` raised in a sale is paired into the project's liquidity pool, and limit-sell fundraising sells reserved project tokens at FDV milestones.

None of this touches `BIO` directly:

- The fee accrues to the treasury in the traded token pair, not in `BIO`.
- No **buyback**, **burn** or **fee distribution to stakers** is described in the documentation. Third-party summaries mention a "buyback and research-funding loop", but no official source, proposal or on-chain contract for a `BIO` buyback was found, and `BIO` supply has not decreased. This is treated here as unverified.
- Staking rewards are BioXP (off-chain points) and third-party tokens, so the protocol does not pay stakers from its own revenue in `BIO`.

Value capture for the token is therefore **indirect**: protocol success should raise demand for `veBIO` positions (more sales, larger airdrops) and grow a treasury that `BIO` governance controls, but no rule converts protocol revenue into `BIO` demand or supply reduction. Whether the 30 % treasury share is significant cannot be assessed: DefiLlama does not track Bio Protocol fees, and no revenue figure has been published.

## Emissions

There is no inflationary emission. The three supply-side flows are:

- **Vesting unlocks**, 278 M to 320 M `BIO` per year (estimate above), to team, investors, advisors and Molecule. This is the structural component of sell pressure, as it goes to holders with a cost basis at or below the last Genesis price of 0.066 USD and mostly far below.
- **Ecosystem Incentives**, 830 M `BIO` under treasury control with no vesting; grants such as the 133 M bio/acc programme reach BioDAOs, which may hold or sell.
- **Airdrop claims** of the remaining DAO-member airdrop, 16 M per year (estimate).

Organic `BIO` demand sinks, by contrast, are lock-ups into `veBIO` (net flat over the past year at about 115 M) and the instant BioXP mint (unquantified). The measured imbalance is that annual scheduled supply of roughly 300 M exceeds the entire `veBIO` stock of 115 M by a factor of about 2.5.

## Staking

| Aspect | Finding |
|--------|---------|
| Reward source | BioXP (off-chain points, 14-day expiry) and pro-rata airdrops of newly launched tokens; no `BIO` rewards |
| Dilution | None: staking creates no new `BIO` |
| Lock-up | 1 week to 2 years, no early exit; `veBIO` decays linearly unless auto-renewed |
| Participation | 115.4 M `BIO` locked (Ethereum 59.7 M, Base 55.7 M), 5.4 % of circulating |
| Sustainability | Depends entirely on launch cadence; if no sales are oversubscribed, BioXP has no use and airdrops stop |

The design avoids the usual staking failure mode, paying stakers with inflation, at the cost of making staking rewards a function of launchpad activity that the token does not control. The `veBIO` decay and BioXP expiry are deliberate anti-hoarding features; they also mean a staker's position requires ongoing attention.

## Sustainability assessment

The model does not rely on inflation: supply is fixed and fully minted, and no rewards are paid in new `BIO`. It relies moderately on incentives, in the form of a large treasury allocation whose release is discretionary, and it relies on launchpad activity for every source of token demand.

Three structural observations:

- **Supply is front-loaded.** 46 % of supply was scheduled for year one (Tokenomist), and the auction bucket completed in November 2025. The price fell 97 % from its TGE-day high and 85 % over the last twelve months, over a period in which unlocks were the dominant supply flow and the V2 launchpad was still being built.
- **Revenue and token are decoupled.** The protocol earns in `USDC` and project tokens; the token earns nothing in its own unit. This is not unusual for a launchpad, but it means `BIO` is a governance and access token, not a claim on cash flow.
- **Governance is exercised, and it is exercised over supply.** BIOPSY-22 postponed an insider unlock by vote of a `BIO`/`vBIO` electorate that includes the insiders whose tokens were postponed. The decision reduced near-term supply; the concentration that enabled it is the same one noted under Distribution.

Whether the model works long-term therefore turns on one empirical question the current data cannot answer: whether Ignition Sales generate enough demand for `veBIO` positions, and enough 30 % fee revenue to the treasury, to absorb roughly 300 M `BIO` a year of insider unlocks through 2028 and 117 M a year through 2030.

## Valuation

| Ratio | Value | Note |
|-------|-------|------|
| MC / FDV | 0.65 | 35 % of supply not circulating |
| FDV / MC | 1.55 | Full dilution would add about 31.6 M USD at current price |
| MC / TVL | 16.3 | TVL 3.54 M USD, DefiLlama "Launchpad" category |
| FDV / TVL | 25.2 | |
| Volume / MC (24 h) | 24 % | High turnover for the size |
| MC / Revenue, FDV / Revenue | Not computable | No revenue data |
| Price vs last private price | 0.41x | 0.0269 vs 0.066 USD (round 2.5) |
| Price vs ATH | 0.03x | 0.0269 vs 0.889 USD |

The TVL figure needs care: for a launchpad, DefiLlama's TVL reflects assets in the protocol's pools and contracts, not `BIO` staked, so MC/TVL compares the token's market value with the capital the launchpad currently holds. A ratio of 16 says the market values the token at sixteen times the assets under its contracts, which is a statement about expectations, not about cash flows.

## Key strengths

- **Fixed, fully minted supply** across four chains, verified on-chain, with no inflation and no staking dilution.
- **Vesting is enforced by open-source contracts** (`TokenVesting`, audited by Pashov in 2023), and the vesting balance is publicly readable: 909 M `BIO` committed on 18 September 2026.
- **No cliff events remain**; every bucket is in linear release, and the largest one was deliberately smoothed by BIOPSY-22.
- **Staking has a concrete use** (launch allocation priority, airdrops) that does not depend on paying stakers in `BIO`.
- **Governance is live** and has been used for a supply decision.

## Key risks

- **Insider-heavy remaining supply**: of the 909 M `BIO` still vesting, essentially all belongs to team, investors, advisors and Molecule; 278 M to 320 M `BIO` a year reaches holders with a low cost basis.
- **Treasury-discretionary 25 %**: 830 M `BIO` with no vesting, released by votes in which insiders carry weight through `vBIO`.
- **No value-capture rule for the token**: revenue is in `USDC` and project tokens; buybacks, burns and fee sharing are undocumented.
- **Demand is a derivative of launch cadence**: `veBIO` locks are 5.4 % of circulating supply and have not grown over the last year.
- **No revenue disclosure**: the 30 % fee share cannot be sized, so MC/Revenue cannot be computed.
- **Price history**: 97 % below the TGE-day high and 85 % down over twelve months; whatever the cause, this sets the market context in which further unlocks land.

## The five metrics to track

1. **`BIO` locked in `veBIO`** (on-chain, both chains): 115.4 M on 2026-09-18. Growth here is the only direct measure that the staking use-case is working.
2. **Committed vesting balance** (`vBIO` master `totalSupply()`): 881.0 M on 2026-09-18. Its rate of decrease is the realised unlock pace, independent of tracker methodology.
3. **Annual unlocks as a share of circulating supply**: 13 % to 15 % today, falling to about 5 % after mid-2028 when investors and Molecule complete, then to zero in May 2030.
4. **Bio treasury fee income** from the 1 % swap tax: currently unpublished; any disclosure would make MC/Revenue computable and would show whether the launchpad generates meaningful cash.
5. **Ecosystem Incentives spent**: the portion of the 830 M released by governance, and to whom, since this bucket can add more supply than all vesting combined.

## Conclusion

`BIO` is a fixed-supply governance and access token whose remaining unlocks are almost entirely insider-held, and whose demand is a function of the launchpad it governs.

- **Supply**: 3.32 B fully minted across Ethereum, Base, Solana and BNB Chain, verified on-chain; 2.15 B circulating per CoinGecko; 909 M committed to vesting contracts; no inflation, no burn.
- **Distribution**: 49 % to insiders, 25 % treasury-discretionary, at most 26 % sold or airdropped to the public.
- **Unlocks**: 278 M to 320 M per year (estimate), all linear, investors and Molecule ending around 2028, team and advisors in May 2030; the one-day team cliff was replaced by a six-month release through BIOPSY-22.
- **Demand**: `veBIO` for launch priority and project-token airdrops; 115.4 M `BIO` locked, flat over a year.
- **Value capture**: 30 % of a 1 % swap tax to the treasury, in the traded pair; no documented path from revenue to `BIO`.
- **Valuation**: 57.7 M USD market cap, 89.3 M USD FDV, MC/TVL 16.3, no revenue ratio computable.

![Mindmap of BIO tokenomics covering supply, distribution, unlocks, demand, value capture and valuation as of September 2026]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/2026-09-18-bio-tokenomics-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Circulating supply** | Tokens an aggregator counts as freely tradeable; differs by methodology, chiefly on whether treasury-held tokens are included. |
| **Fully diluted valuation (FDV)** | Price multiplied by total supply; the market cap if every token were circulating. |
| **Unlock** | The moment vested tokens become claimable by their beneficiary under a vesting schedule. |
| **Cliff** | A period at the start of a vesting schedule during which nothing vests; at its end a first tranche becomes claimable. |
| **`vBIO`** | The vesting representation of `BIO`: a non-transferable ERC-20 balance equal to a holder's unreleased vested amount, usable in governance. |
| **`veBIO`** | Vote-escrowed `BIO`: a decaying, non-transferable balance minted by locking `BIO` for 1 week to 2 years. |
| **BioXP** | Off-chain points earned by staking, expiring after 14 days, that set allocation priority in oversubscribed Ignition Sales. |
| **Ignition Sale** | Bio's fixed-price, `USDC`-denominated project launch sale. |
| **Liquidity Engine** | The post-sale mechanism pairing raised `USDC` with the project token and collecting a 1 % fee on every swap. |
| **BIOPSY** | Prefix of Bio Protocol governance proposals; BIOPSY-22 rescheduled the team unlock, BIOPSY-5 funded bio/acc rewards. |

## Frequently Asked Questions

**Q: Is the BIO supply capped?**

By code, no: the deployed `BioToken` has a `MINTER_ROLE` with no cap, and the documentation calls the supply "uncapped". In fact, yes: the sum of `totalSupply()` on Ethereum, Base, Solana and BNB Chain on 18 September 2026 equals the documented 3.32 B to within two thousand tokens, so everything has been minted and nothing has been added since.

The documentation states that issuing more would require a new token contract, which suggests the minter role is not intended to be used.

**Q: Why do CoinGecko, CoinMarketCap and DropsTab give different circulating or unlocked figures?**

They treat the 830 M Ecosystem Incentives bucket differently. It has no vesting, so DropsTab counts it as unlocked at TGE, giving 77 % unlocked; CoinGecko excludes most treasury-held tokens, giving 2.15 B circulating; CoinMarketCap sits in between at 2.48 B. The on-chain number that does not depend on methodology is the 909 M `BIO` committed to vesting contracts and not yet released.

**Q: What did BIOPSY-22 change, and what did it not change?**

It changed the timing of one tranche: the 117.3 M `BIO` that the team's 28 May 2025 cliff would have released in a day was spread linearly over 14 November 2025 to 14 May 2026. It did not change the total, the remaining five sixths (586.5 M, linear to 28 May 2030), or the vesting maturity date. The vote had 139.1 M tokens in favour across 33 votes.

**Q: Does protocol revenue reach BIO holders?**

Not by any documented rule. The 1 % swap fee on launched tokens sends 30 % to the Bio treasury in the traded pair, and `BIO` governance controls that treasury, but there is no buyback, burn or fee distribution to `veBIO` stakers. Stakers are paid in BioXP and in airdrops of new project tokens. Third-party references to a "buyback loop" could not be traced to an official source.

**Q: How large are annual unlocks relative to the market?**

Roughly 278 M to 320 M `BIO` per year (estimate). Put against the other quantities:

- 13 % to 15 % of circulating supply;
- 7.5 M to 8.6 M USD at the 18 September 2026 price;
- about 2.5 times the total amount currently locked in `veBIO`;
- per day, about 0.15 % of the reported 24-hour volume.

Relative to daily liquidity the flow is small; relative to the float it is significant, and it continues at this pace until mid-2028 before dropping to about 117 M per year.

**Q: Combining the distribution and the governance model, who decides how the 830 M Ecosystem Incentives are spent?**

Holders of `BIO` and `vBIO`, by proposal vote. Because `vBIO` counts unreleased vested tokens, team, investor and advisor allocations that are still vesting carry voting weight. The same electorate passed BIOPSY-22 and BIOPSY-5. `veBIO` is intended to take over governance after a future proposal, which would shift weight toward those who lock liquid `BIO`.

**Q: What is the single on-chain number to watch?**

`totalSupply()` of the `vBIO` master contract at `0x0d2ADB4Af57cdac02d553e7601456739857D2eF4`: 880,962,478 `BIO` on 18 September 2026. It is the committed, unreleased vesting balance across all schedules it aggregates, and its rate of decrease is the realised unlock pace without any tracker assumptions.

## References

### On-chain sources (read 2026-09-18)

- [BIO on Ethereum `0xcb1592591996765Ec0eFc1f92599A19767ee5ffA`](https://etherscan.io/token/0xcb1592591996765Ec0eFc1f92599A19767ee5ffA) — `totalSupply`, `transfersEnabled`, balances of the `veBIO` and vesting contracts
- [BIO on Base `0x226A2FA2556C48245E57cd1cbA4C6c9e67077DD2`](https://basescan.org/token/0x226A2FA2556C48245E57cd1cbA4C6c9e67077DD2)
- [BIO on Solana `bioJ9JTqW62MLz7UKHU69gtKhPpGi1BQhccj2kmSvUJ`](https://solscan.io/token/bioJ9JTqW62MLz7UKHU69gtKhPpGi1BQhccj2kmSvUJ)
- [BIO on BNB Chain `0x226a2fa2556c48245e57cd1cba4c6c9e67077dd2`](https://bscscan.com/token/0x226a2fa2556c48245e57cd1cba4c6c9e67077dd2)
- [veBIO Ethereum `0xF91a12742Aa609d41513a137d3c36b749F56f40C`](https://etherscan.io/address/0xF91a12742Aa609d41513a137d3c36b749F56f40C) and [veBIO Base `0xE1B48C0279Cd95D984f1290293116c45D049A3bD`](https://basescan.org/address/0xE1B48C0279Cd95D984f1290293116c45D049A3bD)
- [vBIO, BIO Vesting Master `0x0d2ADB4Af57cdac02d553e7601456739857D2eF4`](https://etherscan.io/address/0x0d2ADB4Af57cdac02d553e7601456739857D2eF4) and [BIO Vesting Token `0x2141B47A1C7De6df073d23ff94F04d9fd2aaA9b3`](https://etherscan.io/address/0x2141B47A1C7De6df073d23ff94F04d9fd2aaA9b3)

### Market data and trackers

- [CoinGecko — Bio Protocol](https://www.coingecko.com/en/coins/bio-protocol) — price, market cap, FDV, circulating supply, volume, ATH/ATL (API read 2026-09-18 14:11 UTC)
- [DefiLlama — Bio Protocol](https://defillama.com/protocol/bio-protocol) — TVL by chain (API `api.llama.fi/protocol/bio-protocol`, 2026-09-18); [DefiLlama token page](https://defillama.com/token/BIO) and [unlocks](https://defillama.com/unlocks) were not fetchable at the time of writing
- [DropsTab — BIO Protocol vesting](https://dropstab.com/coins/bio-protocol/vesting) — per-bucket unlocked percentages, next unlock
- [Tokenomist — Bio Protocol](https://tokenomist.ai/bio-protocol) — unlocked share, year-one emission share
- [ICO Drops — BIO Protocol](https://icodrops.com/bio-protocol/) — Genesis round 2.5 price and valuation, total raised, TGE date

### Documentation

- [Basic Token Information](https://docs.bio.xyz/bio/introduction/bio-token/basic-token-information) — allocation buckets, vesting terms, contract addresses
- [bio/acc Rewards](https://docs.bio.xyz/bio/introduction/bio-token/bio-acc-rewards)
- [Launcher](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/launcher), [Liquidity Engine](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/liquidity-engine), [Staking BIO](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/staking-and-vebio/staking-bio), [BioXP](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/staking-and-vebio/bioxp), [veBIO Rewards](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/staking-and-vebio/vebio-rewards)

### Reporting

- [Bio Protocol Approves Phased Unlock Of Team Tokens Beginning In November — Metaverse Post](https://mpost.io/bio-protocol-approves-phased-unlock-of-team-tokens-beginning-in-november/) — BIOPSY-22 figures
- [Bio Protocol core team postponed the unlocking of tokens — PANews](https://www.panewslab.com/en/articles/51zhrywq)
- [What Is BIO Protocol: A Binance Labs-Backed DeSci Project — CoinGecko Learn](https://www.coingecko.com/learn/what-is-bio-protocol-crypto-desci) — Genesis raise, BIOPSY-5, BioDAO figures
- [Binance Labs makes first foray into DeSci sector with investment in BIO Protocol — The Block](https://www.theblock.co/post/325185/binance-labs-desci-investment-bio-protocol)

### Related articles

- [Solana Staking - Overview]({{site.url_complet}}/2025/11/07/solana-staking-overview/)
- [Virtual Protocol, create co-ownership AI agents]({{site.url_complet}}/2024/12/05/virtual-protocol-architecture/)
- [Issuing a Token Under MiCA — The Crypto-Asset White Paper and Its Exemptions (Title II)]({{site.url_complet}}/2026/09/17/mica-crypto-asset-white-paper-token-issuers/)
