* # Hyperliquid Technical Architecture Overview

  Hyperliquid is a fully on-chain trading platform built on a custom Layer 1 (L1) that combines consensus, execution, and risk management into a unified framework. Its architecture is designed to deliver decentralization, capital efficiency, and high-performance execution, making it competitive with centralized exchanges while retaining blockchain trust guarantees. This document provides a detailed overview of its core components: **Consensus, Execution, Clearinghouse, Order Book, Staking, and Bridge**, along with PlantUML diagrams illustrating validator lifecycle, clearinghouse flow, and bridge process.

  ## Consensus: HyperBFT

  Hyperliquid secures its network using **HyperBFT**, a variant of the HotStuff consensus protocol.

  - **Proof-of-Stake**: Validators produce blocks proportional to the amount of **HYPE** delegated to them.
  - **Quorum Safety**: A quorum of more than two-thirds of stake ensures safety and liveness.
  - **Deterministic Ordering**: All transactions are finalized through consensus, ensuring consistent and trustless ordering without off-chain sequencers.

  ## Execution Model

  The Hyperliquid state is composed of two execution environments:

  - **HyperCore**: Specialized for trading, it contains the **margin engine** and **matching engine**. Crucially, HyperCore maintains a fully on-chain order book, avoiding reliance on off-chain systems.
  - **HyperEVM**: A general-purpose EVM-compatible environment, enabling programmability beyond trading use cases.

  This dual model balances trading-specific optimizations with general-purpose flexibility.

  ## Clearinghouse

  The **clearinghouse** is the backbone of Hyperliquid’s risk management, ensuring accurate accounting of user balances and positions.

  ### Perpetuals Clearinghouse

  - Maintains cross margin balances and open positions per address.
  - **Cross Margin**: Shared collateral across positions for capital efficiency.
  - **Isolated Margin**: Position-specific collateral to isolate liquidation risk.

  ### Spot Clearinghouse

  - Tracks token balances and order-related holds.
  - Ensures balances reflect both settled and pending orders.

  The clearinghouse guarantees consistency, transparency, and secure risk management across both markets.

  ## Order Book

  Each asset has a dedicated **order book**, fully maintained on-chain within HyperCore.

  - **Constraints**: Orders must conform to tick size (price granularity) and lot size (quantity granularity).
  - **Matching**: Operates on strict price-time priority.
  - **Clearinghouse Integration**: Margin checks are performed both at order placement and again at execution for the resting side, ensuring robustness under oracle price fluctuations.

  ### Consensus-Aware Ordering

  Transactions interacting with order books are semantically ordered by consensus:

  1. Non-order actions.
  2. Cancels.
  3. Order placements (GTC or IOC).

  This deterministic structure prevents manipulation and ensures fairness.

  ## Staking

  Staking is central to security and consensus, implemented directly in HyperCore under a **delegated proof-of-stake (DPoS)** model.

  ### Mechanics

  - **Delegations**: Users delegate HYPE to validators; delegation and staking are synonymous.
  - **Validator Activation**: Requires 10,000 HYPE self-delegation.
  - **Commissions**: Validators may charge delegators, with increases capped to ≤1%.
  - **Lockups**: Delegations require a 1-day lockup; undelegated balances are available in the staking account immediately.
  - **Unstaking Queue**: Transfers back to spot accounts incur a 7-day waiting period.

  ### Rewards

  - Funded by the future emissions reserve.
  - Annual reward rate is inversely proportional to √(total HYPE staked).
  - Rewards accrue every minute, distributed daily, and automatically compounded.

  ### Consensus Integration

  - **Quorum**: ≥⅔ stake honesty assumption underpins HyperBFT.
  - **Epochs**: Validator sets are fixed for epochs of ~100k rounds (~90 minutes).
  - **Jailing**: Underperforming validators may be jailed (halt rewards); malicious validators are subject to slashing in future iterations.

  ## Bridge

  The **bridge** connects Hyperliquid with EVM-compatible chains, enabling USDC transfers.

  ### Deposits

  - Credited once ≥⅔ of validator stake signs.

  ### Withdrawals

  - Immediately deducted from L1 balances.
  - Require ≥⅔ validator signatures before being submitted to the EVM bridge contract.
  - **Dispute Period**: Malicious withdrawals can lock the bridge; unlocking requires cold wallet signatures of ≥⅔ stake.
  - **Finalization**: After dispute resolution, USDC is distributed to destination addresses.

  ### Validator Set Management

  - Active validator set and stake weights are mirrored on the bridge contract.

  ### Fees

  - Users pay **1 USDC withdrawal fee** on Hyperliquid to cover Arbitrum gas costs—no external gas tokens are required.

  ### Security

  - Stake-weighted threshold signatures.
  - Dispute resolution safeguards.
  - Audited by **Zellic**.

  ## Performance Characteristics

  ### Latency

  - Median latency: ~0.2s (geographically co-located clients).
  - 99th percentile: ~0.9s.
  - Enables automated trading strategies and real-time UX.

  ### Throughput

  - Current mainnet capacity: ~200k orders/sec.
  - Consensus and networking scale to millions of orders/sec; current bottleneck is execution logic.

  ## 8. PlantUML Diagrams

  ### Validator Lifecycle

  @startuml

  start

  :User delegates HYPE;

  if (Self-delegation >= 10k?) then (yes)

    :Validator activated;

    :Produces blocks + earns rewards;

    if (Performance adequate?) then (yes)

  ​    :Validator remains active;

    else (no)

  ​    :Validator jailed;

  ​    :Stops producing rewards;

  ​    :Unjails after fixes + cooldown;

    endif

  else (no)

    :Validator inactive;

  endif

  stop

  @enduml

  ### Clearinghouse Flow

  @startuml

  start

  :User deposits funds;

  :Deposit credited to cross margin balance;

  if (Open position?) then (yes)

    :Margin check at order placement;

    if (Order matched?) then (yes)

  ​    :Margin re-check for resting side;

  ​    :Update balances and positions;

    else (no)

  ​    :Order remains in book;

    endif

  else (no)

    :Funds idle in balance;

  endif

  stop

  @enduml

  ### Bridge Process

  @startuml

  start

  :User initiates deposit/withdrawal;

  if (Deposit?) then (yes)

    :Validators sign deposit;

    if (≥2/3 stake signed) then (yes)

  ​    :Deposit credited to Hyperliquid;

    else (no)

  ​    :Deposit pending;

    endif

  else (Withdrawal)

    :Balance deducted immediately;

    :Validators sign withdrawal;

    if (≥2/3 stake signed) then (yes)

  ​    :Withdrawal request sent to EVM bridge;

  ​    :Dispute period begins;

  ​    if (No dispute) then (yes)

  ​      :Finalize + distribute USDC;

  ​    else (Dispute)

  ​      :Bridge locked;

  ​      :Cold wallet signatures required to unlock;

  ​    endif

    else (no)

  ​    :Withdrawal pending;

    endif

  endif

  stop

  @enduml

  ## 