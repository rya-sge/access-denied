# About Hyperliquid

### **What is Hyperliquid?**

Hyperliquid is a performant L1 optimized from the ground up. The vision is a fully onchain open financial system with user built applications interfacing with performant native components, all without compromising end user experience. 

The Hyperliquid L1 is performant enough to operate an entire ecosystem of permissionless financial applications – every order, cancel, trade, and liquidation happens transparently on-chain with block latency <1 second. The chain currently supports 100k orders / second.

The Hyperliquid L1 uses a custom consensus algorithm called HyperBFT which is heavily inspired by Hotstuff and its successors. Both the algorithm and networking stack are optimized from the ground up to support the L1. 

The flagship native application is a fully onchain order book perpetuals exchange, the Hyperliquid DEX. 

Hyperliquid Labs is a core contributor supporting the growth of Hyperliquid, led by [Jeff](https://twitter.com/chameleon_jeff) and iliensinc, who are classmates from Harvard. Other members of the team are from Caltech and MIT and previously worked at Airtable, Citadel, Hudson River Trading, and Nuro. Hyperliquid Labs is self-funded and has not taken any external capital, which allows the team to focus on building a product they believe in without external pressure.

## L1 Overview

### Introduction

The Hyperliquid L1 is custom built around a performant derivatives exchange as the flagship native component. A perpetuals order book exchange was chosen for the following key reasons:

1. It is a realistic real-world application with more infrastructure demands than any existing L1 can handle.
2. It is the most valuable vertical in defi upon from which most user built applications would benefit.
3. It drives real users to interact with the underlying L1 infrastructure.  

The Hyperliquid L1 is continually pushed by the flagship native perps DEX, leading to crucial optimizations that general purpose chains miss in their design.

Note that the L1 state includes all margin and matching engine states. Importantly, Hyperliquid does not rely on the crutch of off-chain order books. A core design principle is full decentralization with one consistent order of transactions achieved through BFT consensus. 

### Latency

Consensus currently uses an optimized consensus algorithm called **HyperBFT**, which is optimized for end-to-end latency. End-to-end latency is measured as duration between sending request to receiving committed response. 

For an order placed from a geographically co-located client, end-to-end latency has a median 0.2 seconds and 99th percentile 0.9 seconds. This performance allows users to port over automated strategies from other crypto venues with minimal changes and gives retail users instant feedback through the UI.

### Throughput

Mainnet currently supports approximately 100k orders/sec. The current bottleneck is execution. The consensus algorithm and networking stack can scale to millions of orders per second once the execution can keep up. There are plans to further optimize the execution logic once the need arises. 

# HyperEVM

(Testnet-only)

Hyperliquid L1 features a general purpose EVM as part of the blockchain state. Importantly, the HyperEVM is not a separate chain, but rather secured by the same HyperBFT consensus as the rest of the L1. This lets the EVM interact directly with the native components of the L1, such as spot and perp order books.

For example, ERC20 tokens are fungible with their linked native spot asset. Users can trade a project token with minimal fees and deep liquidity on the native spot order book, and seamlessly use the same asset on applications built on the EVM.

The HyperEVM and its interactions with the L1 are under active development. For the latest technical developments, see[https://app.gitbook.com/o/9IEyz6nVB2XCF7KcJ16H/s/yUdp569E6w18GdfqlGvJ/~/changes/484/for-developers/evm](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/evm)

### Bridge

Hyperliquid runs with an EVM bridge that is secured by the same validator set as the Hyperliquid L1. 

Deposits to the bridge are signed by validators on the L1 and are credited when more than 2/3 of the staking power has signed the deposit.

Withdrawals from the L1 are immediately escrowed on the L1, and validators sign the withdrawal as separate L1 transactions. When 2/3 of the staking power has signed the L1 withdrawal, an EVM transaction can be sent to the bridge to request the withdrawal. 

After a withdrawal is requested, there is a dispute period during which the bridge can be locked for a malicious withdrawal that does not match the L1. Cold wallet signatures of 2/3 of the stake-weighted validator set are required to unlock the bridge.  

After the dispute period, finalization transactions are sent, which distribute the USDC to the corresponding destination addresses.

There is a similar mechanism to maintain the set of active validators and their corresponding stake on the bridge contract. 

Withdrawals do not require any Arbitrum ETH from the user. Instead, a withdrawal fee of 1 USDC is paid by the user on the L1 to cover the Arbitrum gas costs of the validators.  

The bridge and its logic in relation to the L1 staking have been audited by Zellic. See the Hyperliquid github repository for the full bridge code, and the [Audits](https://hyperliquid.gitbook.io/hyperliquid-docs/audits) section for the audit reports.

# API servers

The API servers are permissionless, other than the validating nodes allowing direct connectivity via RPC. Essentially the API servers act as non-validating proxies to the network. The design allows anyone with access to a node RPC (which will ultimately be public) to spin up arbitrary sets of API servers with their own properties for load balancing.

A single API server is simple in design. It listens to block updates and maintains a processed version of the blockchain state to serve to clients. On requests, it forwards those to the nodes and relays the response back to the client. 

The API server’s in-memory representation of the blockchain state allows Hyperliquid to serve an API that is familiar to automated traders on centralized exchanges. Furthermore, the permissionless API server model solves the issue of load balancing and DDOS protection much like sentry nodes in other network designs.

### REST vs WS

The API serves two sources of data, REST and Websocket. Under the hood, orders and cancels are relayed to the consensus RPC, which gossips the transactions to all the nodes and respond to the original request once it's included in the block and that block is committed. 

Websocket is maintained by a replica state that runs parallel to consensus and pushes updates when the blocks are created. Both systems handle load differently, since the consensus is running as a separate process on each node machine, but the websocket process is running in the same process as the state machine updates. Therefore it's not guaranteed that the timestamps from interleaving the two sources will be consistent.

# Clearinghouse

Key term:

"margin balance",

"isolat margin"

"cross margin balance"

The perps clearinghouse is the core component of the exchange state on the Hyperliquid L1. It manages the perps margin state for each address, which includes balance and positions. 

Deposits are first credited to an address's cross margin balance. Positions by default are also opened in cross margin mode. 

Isolated margin is also supported, which allows users to allocate margin towards a specific position, disassociating the liquidation risk of that position with all other positions.

The spot clearinghouse analogously manages spot user state for each address, including token balances and holds.

# Oracle

The validators are responsible for publishing spot oracle prices for each perp asset every 3 seconds. The oracle prices are used to compute funding rates. They are also a component in the `mark price` which is used for margining, liquidations, and triggering TP/SL orders.

The spot oracle prices are computed by each validator as the weighted median of Binance, OKX, Bybit, Kraken, Kucoin, Gate IO, MEXC, and Hyperliquid spot prices for each asset, with weights 3, 2, 2, 1, 1, 1, 1, 1 respectively. Perps on assets which have primary spot liquidity on Hyperliquid spot do not incorporate external sources until sufficient liquidity is met.

The final oracle price used by the clearinghouse is the weighted median of each validator's submitted oracle prices, where the validators are weighted by their stake.

# Order book

key term: order book, tick size, price-time priority

Hyperliquid L1 state includes an order book for each asset. The order book works in essentially the same way as all centralized exchanges. Orders are added where price is an integer multiple of the tick size, and size is an integer multiple of lot size. The orders are matched in price-time priority. 

Operations on the order book take a reference to the clearinghouse, as all positions and margin checks are handled there. Margin checks happen on the opening of a new order, and again for the resting side at the matching of each order. This ensures that the margining system is consistent despite oracle price fluctuations after the resting order is placed.

# Multi-Sig

Advanced Feature (Testnet-only)

The Hyperliquid L1 supports native multi-sig actions in addition to normal L1 actions. This allows multiple private keys to control a single account for additional security. Unlike other chains, multi-sig is available as a built-in primitive on the L1 as opposed to relying on smart contracts. 

The multi-sig workflow is described below:

- To convert a user to a multi-sig user, the user sends a `ConvertToMultiSigUser` action with the authorized users and the minimum required number of authorized users required to sign an action. Authorized users must be existing users on the L1. Once a user has been converted into a multi-sig user, all its actions must be sent via multi-sig. 
- To send an action, each authorized user must sign a payload to produce a signature. A `MultiSig` action wraps around any normal action and includes a list of signatures from authorized users. 
- The `MutiSig`payload also contains the target multi-sig user and the authorized user who will ultimately send the `MultiSig` action to the L1. The sender of the final action is also known as the `leader `of the multi-sig action.
  - When a multi-sig action is sent, only the nonce set of the authorized user who sent the transaction is validated against and updated.
  - Similarly to normal actions, the leader address can also be an API wallet of an authorized user. In this case, the nonce of the API wallet is checked and updated. 
- A multi-sig user's set of authorized users and/or the threshold may be updated by sending a `MultiSig` action wrapping a`ConvertToMultiSigUser` action describing the new state.
- A multi-sig user can be converted back to a normal user by sending a `ConvertToMultiSigUser` via multi-sig. In this case, the set of authorized users can be set to empty and conversion to normal user will be performed.
- Misc notes: A user can be a multi-sig user and an authorized user for another multi-sig user at the same time. A user may be an authorized user for multiple multi-sig users. The maximum allowed number of authorized users for a given multi-sig user is 10. 

See the Python SDK for code example