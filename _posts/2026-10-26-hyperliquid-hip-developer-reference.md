---
layout: post
title: "Building on Hyperliquid HIPs - A Developer Reference for Deployment and Integration"
date:   2026-10-26
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual api deployment integration prediction-market
series: hyperliquid
description: "Request payloads, info queries, asset-ID lookups, error cases, testnet steps and checklists for deploying and integrating Hyperliquid HIP-1 to HIP-4."
image: /assets/article/blockchain/hyperliquid/hyperliquid-hip-developer-reference.png
isMath: false
---

Hyperliquid's improvement proposals are not smart contracts: a HIP-1 token, a HIP-2 liquidity ladder, a HIP-3 perp DEX and a HIP-4 outcome market are all created by sending signed actions to the HyperCore exchange endpoint. How each mechanism works is covered in [The Hyperliquid Improvement Proposals - HIP-1 to HIP-4]({{site.url_complet}}/2026/09/02/hyperliquid-improvement-proposals-hip-1-to-hip-4/), and what can go wrong for users in [Hyperliquid HIPs in Practice - Risks, Failure Scenarios and Market Quality]({{site.url_complet}}/2026/10/26/hyperliquid-hip-risks-market-quality/).

This article is the reference a developer needs next to those two: the prerequisites for each deployment, the request body of every step, the info queries to run before and after each step, how to resolve asset IDs at runtime, the errors that come back and what they mean, a testnet procedure, and a checklist per HIP. The payloads follow the official API documentation as of 2026-10-26. Field values in the examples are illustrative, and the HIP-4 deployer flow and HIP-3\* venues are testnet-only at that date.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What you need to know first

The examples assume familiarity with the HIP mechanics and with a few API conventions:

- **Exchange and info endpoints.** Actions are `POST`ed to `/exchange` and must be signed; read queries are `POST`ed to `/info` and need no signature. Mainnet is `https://api.hyperliquid.xyz`, testnet `https://api.hyperliquid-testnet.xyz`.
- **L1 actions.** `spotDeploy`, `perpDeploy`, `outcomeDeploy` and `userOutcome` are L1 actions, signed with the L1 scheme (`sign_l1_action` in the Python SDK), not the user-signed scheme used for transfers.
- **Token index, spot index, asset ID.** Three different numbers. A token has a token index; a trading pair has a spot index; orders use an asset ID derived from the spot index, the perp index or the outcome encoding. They also differ between mainnet and testnet.
- **The five-step HIP-1 deployment.** `registerToken2`, `userGenesis`, `genesis`, `registerSpot`, `registerHyperliquidity`, in that order; only the first is gas-charged and time-sensitive.
- **Decimal strings.** Prices, sizes, amounts and fractions are passed as decimal strings without trailing zeros, because a trailing zero changes the signed payload.

## Prerequisites

| | HIP-1 and HIP-2 | HIP-3 | HIP-4 |
|---|---|---|---|
| **Network** | Mainnet and testnet | Mainnet and testnet; HIP-3\* testnet only | Deployer flow testnet only |
| **Account** | Activated HyperCore account with a deposit | Same | Same, using **Standard** account abstraction |
| **Funds** | HYPE to cover `maxGas` at the auction price; USDC for any seeded Hyperliquidity levels | HYPE for asset auctions beyond the first three; collateral token chosen for the DEX | No gas; capacity is capped per deployer |
| **Stake** | None | 500 000 HYPE staked, kept at least 183 days | The outcome-deployer staking requirement, which stacks with any HIP-3 stake |
| **Names** | Ticker up to 6 characters (not unique); optional deployer label of 2 to 4 lowercase letters | DEX name of 2 to 4 lowercase letters | Venue name of 2 to 4 lowercase letters, unique across venues and DEX names, reserved for good |
| **Rehearsal** | Exact deployment on testnet first | Same, including the oracle loop | Testnet is the only network |

Two account details cause most first-run failures. A new HyperCore account must receive a first transfer, which costs one unit of the quote token as an activation fee, before it can act. And an account that has never deposited gets `Must deposit before performing actions` on its first signed request, an error that also appears when a signature recovers the wrong address.

## The request envelope and signing

Every deployer action goes in the same envelope:

```json
{
  "action": { "type": "spotDeploy", "registerToken2": { "...": "..." } },
  "nonce": 1793030400000,
  "signature": { "r": "0x...", "s": "0x...", "v": 27 }
}
```

The nonce is the current time in milliseconds. The documentation strongly recommends signing through an official SDK rather than reimplementing the scheme, and lists the usual mistakes:

- using the user-signed scheme for an L1 action, or the reverse;
- changing the order of fields, which matters because the action is msgpack-encoded before hashing;
- trailing zeros on numbers;
- upper-case characters in addresses (lowercase every address before signing);
- trusting a local signer recovery, whose payload may not match what the node reconstructs.

The [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) (`hyperliquid/utils/signing.py`) shows what an L1 action signature actually covers, which explains why these mistakes break it:

1. The action is msgpack-encoded as given, so field order is part of the hash.
2. The nonce is appended as 8 big-endian bytes, then one byte `0x00` when there is no vault address, or `0x01` followed by the 20-byte vault or sub-account address.
3. When an `expiresAfter` timestamp is used, a `0x00` byte and the timestamp as 8 big-endian bytes follow.
4. The keccak-256 of these bytes becomes the `connectionId` of a "phantom agent" `{source, connectionId}`, where `source` is `"a"` on mainnet and `"b"` on testnet.
5. The phantom agent is signed as EIP-712 typed data with domain name `Exchange`, version `1`, `chainId` 1337 and a zero verifying contract.

Numbers go on the wire as strings with at most 8 decimals and no trailing zeros (`float_to_wire`), which is why `"5000.0"` and `"5000"` sign differently. Because the network is part of the phantom agent rather than the domain, a testnet signature never replays on mainnet, and a correct signature for the wrong network recovers an unknown address.

For `perpDeploy` and `outcomeDeploy`, every list of tuples (prices by asset, keyword values, margin modes) must be **sorted lexicographically** before signing. An unsorted list produces a different hash and a signature that recovers some other address.

A wrong signature does not say what is wrong. It shows up as `L1 error: User or API Wallet 0x... does not exist.` or `Must deposit before performing actions`, naming an address that is not yours.

## HIP-1 and HIP-2: deploying a token

The example deploys LUME with one billion units, half in a Hyperliquidity ladder, on testnet.

### Before step 1: read the auction

```json
{ "type": "spotDeployState", "user": "0xdeployer..." }
```

The response contains `gasAuction` with `startTimeSeconds`, `durationSeconds` (111 600, which is 31 hours), `startGas`, `currentGas` and `endGas`, plus a `states` array describing any deployment this address has in progress: token, spec, spots, `maxSupply`, `hyperliquidityGenesisBalance`, `totalGenesisBalanceWei`, and the genesis balances recorded so far. That array is how a deployer resumes an interrupted deployment.

### Step 1: `registerToken2`

```json
{
  "type": "spotDeploy",
  "registerToken2": {
    "spec": { "name": "LUME", "szDecimals": 2, "weiDecimals": 8 },
    "maxGas": 130000000000,
    "fullName": "Lume Token"
  }
}
```

`maxGas` caps what the deployer accepts to pay, in units of 10^-8 HYPE (the SDK's deployment example states that `1000000000000` is 10 000 HYPE, so `130000000000` here is 1 300 HYPE), so the transaction fails rather than overpays if the auction price is higher than expected. After this step the token index is assigned (read it from `spotDeployState`), the name and decimals are final, and the gas is spent.

### Step 2: `userGenesis` (repeatable)

```json
{
  "type": "spotDeploy",
  "userGenesis": {
    "token": 1234,
    "userAndWei": [
      ["0xteam...", "20000000000000000"],
      ["0xtreasury...", "30000000000000000"],
      ["0xffffffffffffffffffffffffffffffffffffffff", "50000000000000000"]
    ],
    "existingTokenAndWei": []
  }
}
```

Amounts are in wei of the new token: with `weiDecimals = 8`, 200 million LUME is 2 followed by 16 zeros. The third entry is the Hyperliquidity allocation: the SDK's deployment example credits the ladder's inventory to the address `0xffff…ffff` through `userGenesis`, like any other balance. The API documentation does not name that address, so take it from the SDK. `existingTokenAndWei` distributes a total amount to holders of an existing token in proportion to their balances, excluding holders below 0.0001% of that token's max supply. Large distributions can be split across several calls, and `blacklistUsers` sets or clears a blacklist flag per address.

### Step 3: `genesis`

```json
{
  "type": "spotDeploy",
  "genesis": { "token": 1234, "maxSupply": "100000000000000000" }
}
```

`maxSupply` is in wei and is a checksum over everything before it: the SDK's example says it "needs to match the total allocation above from user genesis". Here it is one billion LUME in wei: 200 and 300 million for the team and treasury, plus 500 million credited to the Hyperliquidity address for the ladder (1 000 levels of 500 000). If the numbers do not add up, the call fails, and the deployer corrects the earlier steps. For a bridged token that will not use Hyperliquidity, add `"noHyperliquidity": true` and put the supply at the token's system address in step 2.

### Step 4: `registerSpot`

```json
{ "type": "spotDeploy", "registerSpot": { "tokens": [1234, 0] } }
```

The pair is `[base, quote]`, with USDC as token 0. The new pair gets a **spot index**, distinct from the token index; read it from `spotMeta` or `spotDeployState` before step 5. The same action creates a pair between two existing tokens, under a separate auction whose status comes from `{"type": "spotPairDeployAuctionStatus"}`.

### Step 5: `registerHyperliquidity`

```json
{
  "type": "spotDeploy",
  "registerHyperliquidity": {
    "spot": 987,
    "startPx": "0.01",
    "orderSz": "500000",
    "nOrders": 1000,
    "nSeededLevels": 0
  }
}
```

`spot` is the spot index from step 4. `orderSz` is in tokens, not wei. With `noHyperliquidity` set at genesis, `nOrders` must be 0. Each seeded level costs `px * sz` in USDC, held by the deployer at this point.

### Optional actions

```json
{ "type": "spotDeploy", "setDeployerTradingFeeShare": { "token": 1234, "share": "50%" } }
{ "type": "spotDeploy", "setTokenAnnotation": { "token": 1234, "annotation": {
    "category": "utility", "description": "Example token.", "displayName": null, "keywords": ["example"] } } }
{ "type": "spotDeploy", "setDeployerLabel": { "label": "lume" } }
{ "type": "spotDeploy", "enableFreezePrivilege": { "token": 1234 } }
{ "type": "spotDeploy", "freezeUser": { "token": 1234, "user": "0xuser...", "freeze": true } }
{ "type": "spotDeploy", "revokeFreezePrivilege": { "token": 1234 } }
{ "type": "spotDeploy", "enableQuoteToken": { "token": 1234 } }
```

The fee share starts at 100%, can only decrease, and moves in steps of 0.001%. The annotation can change at most once a day, and the label can be set once per deployer. `enableQuoteToken` requires the fee share to be zero and the token to be allowed as a quote token.

The freeze actions come from the SDK, not from the deployment page of the documentation. After `enableFreezePrivilege` (shown in the SDK example right after `userGenesis`), the deployer can freeze an address, which then cannot trade, send or receive the token, and unfreeze it again. `revokeFreezePrivilege` gives the power up. Integrators should treat a token whose deployer still holds the privilege as one whose balances the deployer can lock.

### After deployment: verify

`{"type": "tokenDetails", "tokenId": "0x..."}` returns the deployed token as others will see it: `maxSupply`, `totalSupply`, `circulatingSupply`, decimals, prices, the genesis balances, the deployer, the gas paid and `seededUsdc`. Compare it field by field against the deployment plan before announcing the token.

## HIP-3: deploying and operating a perp DEX

### Before deploying: auction and limits

```json
{ "type": "perpDeployAuctionStatus" }
```

The response has the same shape as the spot auction (`startTimeSeconds`, `durationSeconds`, `startGas`, `currentGas`, `endGas`). The first three assets of a DEX need no auction.

### Creating the DEX with its first asset: `registerAsset2`

```json
{
  "type": "perpDeploy",
  "registerAsset2": {
    "dex": "idx",
    "assetRequest": {
      "coin": "idx:IDX",
      "szDecimals": 3,
      "oraclePx": "5000",
      "marginTableId": 1,
      "marginMode": "noCross"
    },
    "schema": {
      "fullName": "Index perps",
      "collateralToken": 0,
      "oracleUpdater": "0xupdater..."
    }
  }
}
```

The `schema` field creates the DEX; later assets are registered without it. `marginMode` is `strictIsolated` (isolated margin cannot be withdrawn from open positions), `noCross` or `normal`. The legacy `registerAsset` takes a boolean `onlyIsolated` instead. The coin name carries the DEX prefix (`idx:IDX`), as in the SDK's `perp_deploy.py`. At commit `2fdb18f` (2026-06-04) the SDK's `perp_deploy_register_asset` still sends the legacy `registerAsset` and its schema has no `isStar`, so `registerAsset2`, `marginMode` and HIP-3\* need a hand-built action signed with `sign_l1_action`. On testnet, `"isStar": true` in the schema creates a HIP-3\* venue; this choice is made once, at creation.

Two traps sit in `maxGas`. Leaving it out pays the current auction price. Setting it to **0 uses a reserve deployment, whether or not the auction has completed**, so the documentation advises querying the auction status first.

`szDecimals` interacts with the open-interest caps. The size cap is a constant one billion units per asset, and the documentation recommends a minimum size increment worth roughly 1 to 10 USDC at the initial price, which implies the cap counts minimum increments. For IDX at 5 000, `szDecimals = 3` gives an increment of 0.001 contracts worth 5 USDC, inside the recommended range, and a size cap around 5 billion USDC of notional. `szDecimals = 6` would give an increment worth half a cent and cap the market near 5 million USDC, whatever notional cap the deployer sets.

### The oracle loop: `setOracle`

```json
{
  "type": "perpDeploy",
  "setOracle": {
    "dex": "idx",
    "oraclePxs": [["idx:IDX", "5001.5"]],
    "markPxs": [[["idx:IDX", "5001.2"]]],
    "externalPerpPxs": [["idx:IDX", "5001.0"]]
  }
}
```

The constraints the documentation sets on this action define the operator's main job:

- calls must be at least **2.5 seconds** apart, and the deployer is expected to call every 3 seconds even when nothing changes;
- after **10 seconds** without an update, the mark falls back to the local book mark, a behaviour the documentation says not to rely on;
- each update moves the mark by at most **1%**, and all prices are clamped to **10 times** the start-of-day value;
- the mark cannot be updated so that open interest would exceed 10 times the cap;
- `externalPerpPxs` must include every asset of the DEX.

`markPxs` can hold zero, one or two inner lists. The new mark is the median of those inputs and the local mark. With two inputs, the deployer's values decide the median; with none, the book does.

### Risk and fee settings

```json
{ "type": "perpDeploy", "setOpenInterestCaps": [["idx:IDX", 1000000000]] }
{ "type": "perpDeploy", "setMarginModes": [["idx:IDX", "noCross"]] }
{ "type": "perpDeploy", "setFundingMultipliers": [["idx:IDX", "1"]] }
{ "type": "perpDeploy", "setDeployerFees": [["idx:IDX", { "scale": "0.5", "growthMode": false }]] }
```

Open-interest caps are integer notionals; the documentation sets the minimum at the larger of 1 000 000 (which it describes as one size unit of the collateral asset) and half the current open interest, and `null` removes a custom cap. The scale of that integer is not spelled out, so confirm it on testnet by reading the cap back from `perpDexs`. Funding multipliers lie between 0 and 10, interest rates between -0.01 and 0.01 per 8 hours, and clamps between 0 and 0.01. A margin table holds at most three tiers, with leverage from 1 to 50. The fee `scale` lies in [0, 3], or [0, 10) in growth mode, and can change at most once per 30 days on mainnet. Enabling cross margin on an asset cannot be undone.

### Settling and recycling an asset: `haltTrading`

```json
{ "type": "perpDeploy", "haltTrading": { "coin": "idx:IDX", "isHalted": true } }
```

Halting cancels every order and settles every position at the current mark. Sending `isHalted: false` resumes trading on the same slot, which is how a dated contract can be relisted without a new auction.

### Delegating: `setSubDeployers`

```json
{
  "type": "perpDeploy",
  "setSubDeployers": {
    "dex": "idx",
    "subDeployers": [{ "variant": "setOracle", "user": "0xbot...", "allowed": true }]
  }
}
```

Each grant covers one action variant. Keep the oracle bot's key separate from the deployer key, and grant it nothing else.

## HIP-4: deploying outcome markets (testnet)

### Activation

```json
{ "type": "activateOutcomeDeployer", "activate": { "venueName": "ab" } }
```

Deactivation (`"deactivate": null`) requires the 183-day minimum staking duration to have elapsed and no active outcomes, and it is permanent: the account cannot activate again and the venue name stays reserved.

### Finding a template

```json
{ "type": "outcomeTemplates" }
```

Each template has an ID, a role (standalone outcome, question, or question outcome), display text with `{keyword}` placeholders, typed hints per keyword and a `semanticRestriction`. A market that contradicts the restriction is slashable, so the restriction is the first field to read.

### Deploying a standalone outcome

```json
{
  "type": "outcomeDeploy",
  "venue": "ab",
  "operation": {
    "registerStandaloneOutcomeFromTemplate": {
      "id": "abc",
      "keywordToValue": [["expiry", "20261101-0600"], ["target", "100"], ["underlying", "ABC"]],
      "deployerFeeScale": "1"
    }
  }
}
```

Keyword values must match their hint types: `dateTime` as `YYYYMMDD-HHMM` in UTC within the next year, `uDecimal` without sign, exponent or leading and trailing zeros, `hlPerp` as the name of an existing perp. The onchain name becomes `template:abc` and the description `expiry:20261101-0600|target:100|underlying:ABC`. Questions use `registerQuestionFromTemplate`, which registers the question, its named outcomes and an automatic fallback in one action.

### Settling

```json
{
  "type": "outcomeDeploy",
  "venue": "ab",
  "operation": {
    "settleOutcome": {
      "outcome": 7,
      "settleFraction": "1",
      "details": "",
      "nameAndDescription": ["template:abc", "expiry:20261101-0600|target:100|underlying:ABC"],
      "sideNames": ["template:Over", "template:Under"]
    }
  }
}
```

`nameAndDescription` and `sideNames` must match the outcome exactly, which protects against settling the wrong outcome index. Standalone outcomes accept any fraction in [0, 1]; question outcomes accept only 0 or 1, settle sequentially, and can all be settled at once with `settleQuestion2` (the original `settleQuestion` is discontinued). Settled outcomes can be read back with `{"type": "settledOutcome", "outcome": 7}`.

### User operations on outcomes

```json
{ "type": "userOutcome", "splitOutcome":  { "outcome": 7, "amount": "100" } }
{ "type": "userOutcome", "mergeOutcome":  { "outcome": 7, "amount": null } }
{ "type": "userOutcome", "mergeQuestion": { "question": 3, "amount": "50" } }
{ "type": "userOutcome", "negateOutcome": { "question": 3, "outcome": 11, "amount": "25" } }
```

`null` as the merge amount means the maximum available. The same operations are available to HyperEVM contracts through CoreWriter's `Outcome operation`, where any field the operation does not use must be zero or the action is dropped.

### Limits

On testnet a deployer can have at most 10 active outcomes and deploy 50 per day. A question with N named outcomes registers N + 1, the fallback included, and a question holds at most 100 outcomes.

## Asset IDs: resolving them at runtime

Hard-coded IDs break between networks and as markets are added. The lookups below resolve them from the info endpoint each time:

```python
import requests

INFO = "https://api.hyperliquid-testnet.xyz/info"

def info(body):
    return requests.post(INFO, json=body, timeout=10).json()

def spot_asset_id(base_token, quote_token=0):
    for pair in info({"type": "spotMeta"})["universe"]:
        if pair["tokens"] == [base_token, quote_token]:
            return 10000 + pair["index"]
    raise KeyError((base_token, quote_token))

def hip3_asset_id(dex, coin):
    dexs = info({"type": "perpDexs"})          # entry 0 is null: the validator-operated DEX
    dex_index = next(i for i, d in enumerate(dexs) if d and d["name"] == dex)
    universe = info({"type": "meta", "dex": dex})["universe"]
    index_in_meta = next(i for i, a in enumerate(universe) if a["name"] == f"{dex}:{coin}")
    return 100000 + dex_index * 10000 + index_in_meta

def outcome_asset_id(outcome, side):
    assert side in (0, 1)                      # side indexes sideSpecs in outcomeMeta
    return 100_000_000 + 10 * outcome + side
```

The documentation's own example of why: HYPE is token 150 and spot 107 on mainnet, but token 1105 and spot 1035 on testnet.

## Error cases

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `L1 error: User or API Wallet 0x... does not exist.` naming an unknown address | Signature recovers the wrong signer: field order, trailing zeros, upper-case address, unsorted tuples, wrong scheme | Sign through the SDK; lowercase addresses; sort tuple lists; strip trailing zeros |
| `Must deposit before performing actions` | Account never funded, or the same signature problem | Fund and activate the account; then check the signature |
| `Post only order would have immediately matched` (`BadAloPx`) | An ALO order crosses the book | Expected for Hyperliquidity levels; for bots, reprice from the current best bid and offer |
| `Order would increase open interest while open interest is capped` | Notional or size OI cap reached | Read caps in `perpDexs` and `perpDexLimits`; raise the cap or revisit `szDecimals` |
| `Order must have minimum value of 10 {quote_token}` | Spot order below the minimum notional | Increase size; account for it when sizing tests |
| `Deployer fee scale cannot be negative or greater than 10.` | HIP-4 `deployerFeeScale` out of range | Use a decimal string in [0, 10] |
| `genesis` rejected | `maxSupply` checksum does not match genesis balances plus Hyperliquidity | Recompute from `spotDeployState`; fix `userGenesis` or the ladder parameters |
| Deployment stuck after `registerToken2` | Incompatible supply and Hyperliquidity parameters | No refund; continue with corrected later steps if a valid combination exists |
| Reserve deployment consumed unexpectedly | `maxGas: 0` on `registerAsset2` | Query `perpDeployAuctionStatus` first; pass an explicit `maxGas` |
| Mark price drifts to the book | `setOracle` not called for 10 s, or calls under 2.5 s apart being rejected | Run the oracle loop every 3 s with monitoring and alerting |
| CoreWriter outcome action has no effect | Unused fields non-zero | Zero every field the operation ignores |
| Venue or DEX name refused | Name taken by a venue, a DEX, `spot`, or a deactivated venue | Pick another name; reserved names never free up |

## Testnet procedure

The documentation is explicit that the exact deployment should be rehearsed on testnet, and for HIP-4 testnet is the only option. A useful sequence:

1. **Fund and activate** a fresh testnet account, and record its address in lower case.
2. **Read every state** first: `spotDeployState`, `perpDeployAuctionStatus`, `perpDexs`, `outcomeTemplates`.
3. **Run the full sequence with production parameters**: same decimals, same supply split, same ladder, same margin table, same template keywords. A deployment rehearsed with round test values does not test the checksum or the ladder that will run in production.
4. **Read the result back** with `tokenDetails`, `spotMeta`, `meta` with `dex`, `perpDexLimits` and `outcomeMeta`, and compare it to the plan.
5. **Exercise the failure paths**: stop the oracle loop and watch the 10-second fallback, send an unsorted tuple list, settle an outcome with a mismatched description, place an ALO order that crosses.
6. **Trade against the market** with a second account, including a liquidation on HIP-3 and a split, merge and settlement on HIP-4.
7. **Resolve asset IDs again on mainnet** at deployment time; none of the testnet IDs carry over.

## Checklists

### HIP-1 and HIP-2 deployer

- [ ] Decimals satisfy `szDecimals + 5 <= weiDecimals` and the frontend ranges.
- [ ] Ticker checked against existing tokens, knowing it will not be unique.
- [ ] Genesis split, ladder size and seeded levels add up to `maxSupply`.
- [ ] `maxGas` set to the highest price you accept, auction status read just before sending.
- [ ] Spot index (not token index) used in `registerHyperliquidity`.
- [ ] Fee share chosen knowing it can only decrease.
- [ ] Bridged asset: supply at the system address, `noHyperliquidity` set, EVM link tested.
- [ ] Full rehearsal on testnet with production parameters.

### HIP-3 deployer

- [ ] Stake in place for at least 183 days, and its source (self or LST) disclosed.
- [ ] Oracle source reliable, external, hard to manipulate; oracle bot calling every 3 s with alerting.
- [ ] Separate `oracleUpdater` and sub-deployer keys, each with the minimum grant.
- [ ] `szDecimals` chosen so the minimum increment is worth 1 to 10 USDC.
- [ ] Margin table and OI caps sized for the underlying's liquidity.
- [ ] Cross margin enabled only on assets that meet the eligibility standards, knowing it is irreversible.
- [ ] Fee scale and growth-mode eligibility checked, with the 30-day change limit in mind.
- [ ] `maxGas` explicit on every `registerAsset2`.

### HIP-4 deployer

- [ ] Standard account abstraction; staking requirement met on top of any HIP-3 stake.
- [ ] Venue name chosen for good.
- [ ] Template's `semanticRestriction` read and every keyword value checked against its hint.
- [ ] Settlement source and procedure written down, including who sends `settleOutcome` and when.
- [ ] Sub-deployers granted only the variants they need.
- [ ] Active-outcome and daily caps planned for.

### Integrator (wallet, frontend, bot)

- [ ] Tokens keyed on token index or token ID, never on the ticker.
- [ ] Asset IDs resolved at runtime per network.
- [ ] HIP-3 markets shown with their deployer, `oracleUpdater`, margin mode and OI headroom.
- [ ] Oracle staleness and 1%-step drift monitored on HIP-3 markets used for liquidation-sensitive flows.
- [ ] HIP-4 markets shown with their template, settlement rule and who settles them.
- [ ] Historical orders on HIP-4 reconciled against the merged book (one order can return two records).

## Conclusion

Deploying on Hyperliquid is a sequence of signed actions rather than a contract deployment, and most of the work lies around the actions rather than in them:

- **Reading state comes first.** `spotDeployState`, the auction status queries and `outcomeTemplates` decide what the next action should contain, and reading back after each step catches mistakes before they become permanent.
- **A few steps are one-way.** `registerToken2`, enabling cross margin, the DEX schema (including HIP-3\*), the venue name and HIP-4 deactivation cannot be undone, and the checklists mark them.
- **Operation is ongoing for HIP-3 and HIP-4.** The oracle loop and settlement are services the deployer runs for as long as the market exists, under rate limits and clamps that shape how they must be built.
- **IDs are looked up, never stored.** Token, spot, perp and outcome IDs differ by scheme and by network.

![Mindmap of the Hyperliquid HIP developer reference covering prerequisites, signing, the HIP-1 to HIP-4 deployment walkthroughs, asset-ID lookups, error cases and checklists]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-hip-developer-reference.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **L1 action** | An action signed with Hyperliquid's L1 scheme and executed by HyperCore; all deployer actions are L1 actions. |
| **Token index / spot index** | The number assigned to a token at `registerToken2`, and the number assigned to a pair at `registerSpot`; spot asset IDs derive from the second. |
| **Reserve deployment** | A HIP-3 asset deployment at the current auction price that bypasses the auction timer, used when `maxGas` is 0. |
| **`oracleUpdater`** | The address permitted to call `setOracle` for a HIP-3 DEX, the deployer by default. |
| **Venue** | A HIP-4 deployer's namespace, named once and reserved permanently. |
| **System address** | The HyperCore address linked to a token's HyperEVM contract; transfers to it move balances between the two states. |

## Frequently Asked Questions

**Q: Why does `registerHyperliquidity` fail with the token index but succeed with another number?**

It expects the spot index of the pair created by `registerSpot`, not the token index from `registerToken2`. The two are assigned independently. Read the spot index from `spotMeta` or `spotDeployState` after step 4.

**Q: A HIP-3 deployer sends `registerAsset2` with `maxGas: 0` while the auction is still running. What happens?**

A reserve deployment is consumed at the current auction price. The documentation warns that a reserve deployment is used whether or not the auction has completed, so a deployer who meant to wait for the price to fall has used one of their reserve slots instead.

**Q: Why might a correct-looking signature produce `User or API Wallet ... does not exist`?**

Because the node recovered a different signer. The usual causes are a trailing zero in a number, an upper-case address, fields in a different order, an unsorted list of tuples in a `perpDeploy` or `outcomeDeploy` action, or the wrong signing scheme. Any of these changes the hash, and the recovered address changes with it.

**Q: How often must a HIP-3 oracle bot send `setOracle`, and what happens if it stops?**

The documentation expects a call every 3 seconds, with at least 2.5 seconds between calls. If no update arrives for 10 seconds, the mark price falls back to the local book mark, which the documentation says not to rely on.

**Q: Which HIP-4 settlement fields guard against settling the wrong market?**

`nameAndDescription` and `sideNames` must exactly match the outcome being settled. An outcome index typed wrong will not match the description of the intended market, and the action is rejected rather than settling an unrelated outcome.

**Q: Combine the HIP-1 and asset-ID sections: what three numbers does a LUME/USDC buy order involve, and which one goes in the order?**

The LUME token index (from `registerToken2`), the LUME/USDC spot index (from `registerSpot`), and the asset ID, which is 10 000 plus the spot index. Only the asset ID goes in the order; the token index identifies the token in balances and transfers.

## Gaps

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| Full response bodies for several info requests | Field names above come from the documentation's examples, which do not show every field | Query testnet and log the raw responses |
| The HIP-4 staking amount | The deployer documentation states that a requirement exists, not its size | HIP-4 deployer actions; testnet activation error messages |
| Status of the freeze actions | They appear in the SDK but not in the deployment page of the documentation, so whether they are enabled on mainnet is not stated | `spotDeploy` responses on testnet; future documentation updates |
| The Hyperliquidity genesis address | `0xffff…ffff` comes from the SDK example only | SDK `examples/spot_deploy.py`; `tokenDetails` after a testnet genesis |
| SDK support for HIP-3 `registerAsset2` and HIP-4 | The SDK at `2fdb18f` has no `registerAsset2`, `isStar`, `outcomeDeploy` or `userOutcome` helpers | Newer SDK releases; the TypeScript definitions in the documentation |
| Scale of HIP-3 open-interest cap integers | The documentation does not say whether the integer is whole collateral units or a smaller unit, so the example value is not a recommendation | Read a cap back from `perpDexs` after setting it on testnet |
| Error strings for deployer actions | The error page lists order errors; deployer action errors are learnt from responses | Testnet responses during rehearsal |

## References

### Hyperliquid API documentation

- [Deploying HIP-1 and HIP-2 assets](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets) — the `spotDeploy` action types
- [HIP-3 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions) — the `perpDeploy` action types, `setOracle` constraints, fee rules, HIP-3\*
- [HIP-4 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions) — activation, templates, deployment, settlement, limits
- [Exchange endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint) — the envelope and the `userOutcome` operations
- [Info endpoint, Spot](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot) — `spotDeployState`, `spotPairDeployAuctionStatus`, `tokenDetails`, `outcomeMeta`, `outcomeTemplates`, `settledOutcome`
- [Info endpoint, Perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals) — `perpDexs`, `meta`, `metaAndAssetCtxs`, `perpDeployAuctionStatus`, `perpDexLimits`, `perpDexStatus`
- [Asset IDs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/asset-ids) — the perp, HIP-3, spot and outcome encodings
- [Signing](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/signing) — the two schemes and common mistakes
- [Error responses](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/error-responses) — order and cancel errors
- [Activation gas fee](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/activation-gas-fee) — first-transfer fee for new accounts
- [Tick and lot size](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size) — price and size precision rules

### SDK

- [hyperliquid-python-sdk](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) — the reference implementation of both signing schemes (commit `2fdb18f`, 2026-06-04)
- [SDK `examples/spot_deploy.py`](https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/master/examples/spot_deploy.py) — HIP-1 and HIP-2 deployment end to end: units of `maxGas` and `maxSupply`, the Hyperliquidity address, freeze privilege, fee share rules
- [SDK `examples/perp_deploy.py`](https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/master/examples/perp_deploy.py) — HIP-3 asset registration and `setOracle`
- [SDK `hyperliquid/utils/signing.py`](https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/master/hyperliquid/utils/signing.py) — action hash, phantom agent and EIP-712 domain

### Related articles

- [Hyperliquid's Onchain Order Book - Matching, Ordering, and How It Differs from a CEX and from GMX]({{site.url_complet}}/2026/09/02/hyperliquid-order-book-matching-engine/)
- [Gnosis Conditional Tokens — Combinatorial Prediction Markets on ERC-1155]({{site.url_complet}}/2026/07/28/gnosis-conditional-tokens-framework/)
- [Hyperliquid HIP-1 to HIP-4 in Twelve Cards — The Definitions to Memorise]({{site.url_complet}}/2026/10/26/hyperliquid-hip-flashcards/)
