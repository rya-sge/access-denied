# Hyperliquid in Five Minutes

**An L1 where the order book is part of consensus**

Ryan Sauge · v1.0 · 2026-10-01

Talk length: about 5 minutes (11 slides, 20 to 35 seconds each)

Source: [The Hyperliquid Protocol - HyperCore, HyperEVM and Onchain Perpetual Mechanics](https://rya-sge.github.io/access-denied/2026/09/02/hyperliquid-protocol-architecture/) and the [Hyperliquid documentation](https://hyperliquid.gitbook.io/hyperliquid-docs)

---

## 1. What is Hyperliquid

- A decentralised exchange for perpetual futures and spot, running on its own proof-of-stake chain.
- Many DEXs keep the order book off-chain, or replace it with an AMM. Hyperliquid puts the order book, margin and liquidations into the chain state that validators agree on.
- The question for this talk: what does an exchange look like when it is the chain itself?

```mermaid
flowchart LR
    subgraph OTHER["Other DEX designs"]
        direction TB
        A1["Order book off-chain,<br/>settlement onchain"]
        A2["AMM pool<br/>instead of a book"]
    end
    subgraph HL["Hyperliquid"]
        direction TB
        H1["Order book, margin<br/>and liquidation onchain"]
    end
    A1 -->|"book moves onchain"| H1
    A2 -->|"pool replaced by a book"| H1

    style OTHER fill:#F0F2F5,stroke:#78909C
    style HL fill:#E8F5E9,stroke:#2E7D32
    style A1 fill:#F0F2F5,stroke:#78909C
    style A2 fill:#F0F2F5,stroke:#78909C
    style H1 fill:#E8F5E9,stroke:#2E7D32
```

> **Speaker notes (25 s):** Most people know Hyperliquid as a perp exchange. The design choice behind it is that the matching engine is not an app deployed on a chain. Every validator runs it.

---

## 2. Architecture: one consensus, two execution states

- **HyperBFT**: a HotStuff variant. A block is committed when validators holding more than two thirds of the staked HYPE sign it.
- **HyperCore**: order books, perp and spot clearinghouses, the oracle, staking.
- **HyperEVM**: a regular EVM (chain ID 999). Same consensus, same history, no bridge to HyperCore.

```mermaid
flowchart TB
    VAL["Validators<br/>HyperBFT, staked HYPE"] --> CORE
    VAL --> EVM
    subgraph L1["Hyperliquid L1"]
        direction LR
        CORE["HyperCore<br/>order books, clearinghouses,<br/>oracle, staking"]
        EVM["HyperEVM<br/>smart contracts"]
    end

    style VAL fill:#E8EEF9,stroke:#3A5FA0
    style L1 fill:#F0F2F5,stroke:#78909C
    style CORE fill:#E8F5E9,stroke:#2E7D32
    style EVM fill:#F0F2F5,stroke:#78909C
```

> **Speaker notes (30 s):** For a co-located client, the median time from sending an order to a committed answer is 0.2 seconds. Mainnet handles about 200 000 orders per second, and the documentation says execution is the bottleneck, not consensus.

---

## 3. The life of an order

```mermaid
flowchart LR
    C["Client<br/>signed order"] --> API["API server<br/>holds the request open"]
    API --> NODE["Validator node<br/>HyperBFT round"]
    NODE --> BOOK["Order book<br/>price-time priority"]
    BOOK --> RES["Fill confirmation<br/>sent back to the client"]

    style C fill:#E8EEF9,stroke:#3A5FA0
    style API fill:#F0F2F5,stroke:#78909C
    style NODE fill:#F0F2F5,stroke:#78909C
    style BOOK fill:#E8F5E9,stroke:#2E7D32
    style RES fill:#F0F2F5,stroke:#78909C
```

Inside a block, actions run in three groups:

1. Orders that take no liquidity (post-only)
2. Cancels
3. Orders that take liquidity (GTC, IOC)

> **Speaker notes (35 s):** A market maker who cancels and a trader who hits the same quote in the same block: the cancel wins. That removes a form of front-running that a first-come, first-served block allows. Margin is checked when the order is placed, and again for the resting order at each match, because the price may have moved between the two.

---

## 4. Prices: oracle and mark

- **Oracle price**: every ~3 s, each validator takes a weighted median of 8 spot exchanges; the chain takes the stake-weighted median of the validators. Used for funding.
- **Mark price**: median of three indices (oracle + basis, local book, external perps). Used for margin and liquidation.

```mermaid
flowchart LR
    EXT["8 spot exchanges"] --> ORA["Oracle price<br/>two medians"]
    ORA --> FUND["Funding<br/>paid hourly"]
    ORA --> MARK["Mark price<br/>median of 3"]
    MARK --> LIQ["Margin and<br/>liquidation"]

    style EXT fill:#E8EEF9,stroke:#3A5FA0
    style ORA fill:#E8F5E9,stroke:#2E7D32
    style MARK fill:#E8F5E9,stroke:#2E7D32
    style FUND fill:#F0F2F5,stroke:#78909C
    style LIQ fill:#F0F2F5,stroke:#78909C
```

> **Speaker notes (30 s):** One consequence: a position can be liquidated with no trade on Hyperliquid at that price, because the mark price also reads external markets. The oracle has its own deck if someone wants the details.

---

## 5. Liquidation: on the order book

```mermaid
flowchart LR
    START["Equity below<br/>maintenance margin"] --> BOOK["Step 1<br/>market orders sent to the book"]
    BOOK --> Q{"Margin restored?"}
    Q -->|"restored"| OK["Trader keeps the<br/>remaining collateral"]
    Q -->|"equity below 2/3<br/>of maintenance"| NEXT["Step 2<br/>next slide"]

    style START fill:#F0F2F5,stroke:#78909C
    style BOOK fill:#E8F5E9,stroke:#2E7D32
    style Q fill:#F0F2F5,stroke:#78909C
    style OK fill:#F0F2F5,stroke:#78909C
    style NEXT fill:#FDEEEE,stroke:#B54A4A
```

- Anyone can take the other side of the liquidation orders.
- Positions above 100 000 USDC: 20% at a time, then a 30-second cooldown.

> **Speaker notes (20 s):** Maintenance margin is half the initial margin at maximum leverage, so between 1.25% and 16.7% depending on the asset. Most liquidations end at this step.

---

## 6. Liquidation: backstop and auto-deleveraging

```mermaid
flowchart LR
    IN["Equity below 2/3<br/>of maintenance"] --> HLP["Step 2<br/>HLP vault takes<br/>the position"]
    HLP --> Q2{"Account value<br/>negative?"}
    Q2 -->|"no"| END["Done"]
    Q2 -->|"negative"| ADL["Step 3<br/>auto-deleveraging"]

    style IN fill:#F0F2F5,stroke:#78909C
    style HLP fill:#E8F5E9,stroke:#2E7D32
    style Q2 fill:#F0F2F5,stroke:#78909C
    style END fill:#F0F2F5,stroke:#78909C
    style ADL fill:#FDEEEE,stroke:#B54A4A
```

- Auto-deleveraging closes the most profitable and most levered opposite positions first.
- A user with no open position never pays for platform losses.

> **Speaker notes (20 s):** The trader does not get the maintenance margin back at step 2: HLP keeps it so that backstop liquidations are profitable on average.

---

## 7. HyperEVM and HyperCore

```mermaid
flowchart LR
    SC["HyperEVM contract"] -->|"read precompiles<br/>0x...0800 and up"| CORE["HyperCore state<br/>positions, balances, prices"]
    SC -->|"CoreWriter<br/>0x3333...3333"| ACT["HyperCore action<br/>order, transfer, staking"]

    style SC fill:#F0F2F5,stroke:#78909C
    style CORE fill:#E8F5E9,stroke:#2E7D32
    style ACT fill:#E8F5E9,stroke:#2E7D32
```

- **Read**: values match HyperCore at the moment the EVM block was built.
- **Write**: orders sent through CoreWriter are delayed by a few seconds, so the EVM cannot be used to jump ahead of the L1 queue.
- Two block types: small blocks every second (3M gas), big blocks every minute (30M gas).

> **Speaker notes (30 s):** This is how a lending protocol or a vault on the HyperEVM can trade on the order book and price its collateral with the same number the clearinghouse uses.

---

## 8. The HIP standards

```mermaid
flowchart LR
    H1["HIP-1<br/>native tokens<br/>and spot books"] --> H2["HIP-2<br/>Hyperliquidity:<br/>built-in market making"]
    H3["HIP-3<br/>builder-deployed perps<br/>500 000 HYPE staked"]
    H4["HIP-4<br/>outcome markets<br/>no leverage"]

    style H1 fill:#E8F5E9,stroke:#2E7D32
    style H2 fill:#E8F5E9,stroke:#2E7D32
    style H3 fill:#E8EEF9,stroke:#3A5FA0
    style H4 fill:#E8EEF9,stroke:#3A5FA0
```

| Standard | What it adds |
|---|---|
| HIP-1 | Anyone can deploy a token and its spot market (Dutch auction, 500 HYPE floor) |
| HIP-2 | An onchain strategy that keeps a 0.3% spread, refreshed every 3 s |
| HIP-3 | Anyone can run a perp exchange; the deployer publishes the oracle and can be slashed |
| HIP-4 | Fully collateralised markets with a fixed settlement range, e.g. prediction markets |

> **Speaker notes (30 s):** Green: spot tokens and their liquidity. Blue: new market types, perps and outcomes. HIP-2 attaches to a HIP-1 token at deployment, which is why those two are linked.

---

## 9. Where the fees go

```mermaid
flowchart LR
    FEES["Trading fees"] --> HLP["HLP<br/>protocol vault"]
    FEES --> DEP["HIP-1 and HIP-3<br/>deployers"]
    FEES --> AF["Assistance Fund<br/>buys HYPE and burns it"]

    style FEES fill:#F0F2F5,stroke:#78909C
    style HLP fill:#E8F5E9,stroke:#2E7D32
    style DEP fill:#E8EEF9,stroke:#3A5FA0
    style AF fill:#E8F5E9,stroke:#2E7D32
```

- Base perp fees: 0.045% taker, 0.015% maker. Staking HYPE gives up to 40% off.
- No operator takes a cut. HLP also runs the backstop liquidations.
- Staking: rewards of about 2.37% per year at 400M HYPE staked.

> **Speaker notes (25 s):** HLP is the vault from slide 6. Anyone can deposit into it, with a four-day lock-up after each deposit.

---

## 10. Limitations

| Limitation (by design) | What it means for a user |
|---|---|
| Validators with two thirds of the stake can change any state | The order book, the oracle and every validator vote share one trust assumption |
| Validator votes decide offchain questions | Delistings, HIP-3 slashing and quote-asset status are judgement calls by stake |
| HIP-3 oracle is one deployer | Slashed stake is burned; users are not compensated |
| HyperEVM token links are not verified | A linked contract can hold arbitrary code; integrators must check it |
| No automatic slashing of validators | Misbehaving validators can be jailed by vote, not slashed |

> **Speaker notes (30 s):** None of this is hidden; the documentation states each point. The trust model reduces to how HYPE stake is distributed across validators.

---

## 11. Conclusion

```mermaid
flowchart LR
    C1["HyperBFT<br/>consensus"] --> C2["HyperCore<br/>order book in the state"]
    C2 --> C3["HyperEVM<br/>contracts on the same state"]
    C3 --> C4["HIP standards<br/>third parties build on top"]

    style C1 fill:#E8EEF9,stroke:#3A5FA0
    style C2 fill:#E8F5E9,stroke:#2E7D32
    style C3 fill:#F0F2F5,stroke:#78909C
    style C4 fill:#F0F2F5,stroke:#78909C
```

- On Hyperliquid, the exchange is the chain's state machine.
- That lets the chain order cancels before takers, check margin at each match, and close losses through a fixed liquidation sequence.
- The cost is one trust assumption for everything: two thirds of the staked HYPE.

> **Speaker notes (25 s):** Back to the opening question. An exchange that is the chain gets a central-exchange order book with onchain settlement, and puts all its trust in the validator set.
