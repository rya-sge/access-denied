# Understanding Gas in Ethereum

[TOC]

## What is Gas?

In the Ethereum network, "gas" refers to the unit that measures the amount of computational effort required to execute operations such as transactions and smart contracts. Essentially, gas is the fuel that allows the Ethereum Virtual Machine (EVM) to operate.

- **Purpose of Gas**: Gas helps to keep the Ethereum network secure and functional. By requiring a fee for every computational step, it prevents malicious actors from spamming the network with frivolous or computationally expensive tasks.
- **Gas Price and Gas Limit**: Each operation on Ethereum requires a certain amount of gas. 
  - The "gas price" (usually measured in Gwei, a subunit of Ether) is the amount of Ether a user is willing to pay per unit of gas. 
  - The "gas limit" is the maximum amount of gas a user is willing to spend on a transaction.

### How Gas Works

1. **Transaction Submission**: When a user submits a transaction, they specify a gas limit and a gas price.
2. **Transaction Processing**: Miners process transactions, prioritizing those with higher gas prices since they earn more from those transactions.
3. **Gas Usage**: If the transaction requires more gas than the gas limit, it fails but the gas used up to that point is consumed. If it requires less, the remainder is refunded to the user.

### Historical Changes in Ethereum Gas Mechanism

1. **Initial Gas Model**: When Ethereum was first launched in July 2015, the gas model was relatively simple. Gas prices were set by the users, and miners would prioritize transactions with higher gas prices.
2. **Spurious Dragon (2016)**: The Spurious Dragon hard fork included changes from EIP-150 and EIP-160, which adjusted gas costs and introduced measures to clear out unnecessary state entries. **EIP-150 and EIP-160 (2016)**: These were among the first significant changes, increasing the gas costs for certain operations to mitigate potential denial-of-service attacks.
3. **Constantinople and St. Petersburg (2019)**: These upgrades included EIP-1283, which initially aimed to reduce gas costs for certain storage operations. However, due to a vulnerability, it was not immediately implemented.
4. **Istanbul (2019)**: This hard fork introduced several EIPs (e.g., EIP-2028, EIP-1884) that adjusted gas costs for different operations to improve network efficiency and security.
5. **Berlin (2021)**: EIP-2929 and other proposals were included in this upgrade, further increasing gas costs for certain operations to prevent potential exploits.
6. **London (2021)**: The London hard fork brought one of the most significant changes with EIP-1559, overhauling the fee market by introducing a base fee and burning mechanism, which helped stabilize transaction fees and provided a deflationary aspect to Ether.

## Relevant Ethereum Improvement Proposals (EIPs) Regarding Gas

Several EIPs have been introduced to modify how gas works in the Ethereum network:

Generally, the main function of gas costs of opcodes is to be an estimate of the time needed to process that opcode, the goal being for the gas limit to correspond to a limit on the time needed to process a block. 

### EIP-150 (2016 / Byzantium hard *fork*)

**EIP-150 (Gas Cost Changes for IO-heavy Operations)**

This proposal aimed to mitigate denial-of-service attacks by adjusting gas costs for certain operations to better reflect their actual computational costs.

### Abstract

Recent denial-of-service attacks have shown that opcodes that read the state tree are under-priced relative to other opcodes. 

- Such opcodes will be by a substantial margin the easiest known mechanism to degrade network performance via transaction spam. 
- The concern arises because it takes a long time to read from disk, and is additionally a risk to future sharding proposals as the "attack transactions" that have so far been most successful in degrading network performance would also require tens of megabytes to provide Merkle proofs for. 
- This EIP increases the cost of storage reading opcodes to address this concern. 

Change summary:

- Increase the gas cost of EXTCODESIZE to 700 (from 20).
- Increase the base gas cost of EXTCODECOPY to 700 (from 20).
- Increase the gas cost of BALANCE to 400 (from 20).
- Increase the gas cost of SLOAD to 200 (from 50).
- Increase the gas cost of CALL, DELEGATECALL, CALLCODE to 700 (from 40).
- Increase the gas cost of SELFDESTRUCT to 5000 (from 0).

[https://github.com/ethereum/EIPs/blob/master/EIPS/eip-150.md](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-150.md)

https://www.rareskills.io/post/eip-150-and-the-63-64-rule-for-gas

### EIP-1559 (2021 / London Hard fork )

#### Summary  (Fee Market Change for ETH 1.0 Chain)

Introduced in the London hard fork, EIP-1559 reformed the transaction fee mechanism. Instead of a simple auction, it implemented a base fee that gets burned (removed from circulation) and an optional tip (priority fee) to incentivize miners.

#### Abstract

Introduce a new [EIP-2718](https://eips.ethereum.org/EIPS/eip-2718) transaction type, with the format `0x02 || rlp([chain_id, nonce, max_priority_fee_per_gas, max_fee_per_gas,  gas_limit, destination, amount, data, access_list, signature_y_parity,  signature_r, signature_s])`.

- There is a base fee per gas in protocol, which can move up or down each  block according to a formula which is a function of gas used in parent  block and gas target (block gas limit divided by elasticity multiplier)  of parent block. 
- The algorithm results in the base fee per gas increasing when blocks are above the gas target, and decreasing when blocks are below the gas target. 
- The base fee per gas is burned.
- Priority fee : Transactions specify the maximum fee per gas they are willing to give to miners to incentivize them to include their transaction (aka: priority  fee).
- Maximum fee: Transactions also specify the maximum fee per gas they are willing to  pay total (aka: max fee), which covers both the priority fee and the  block’s network fee per gas (aka: base fee).
- Senders will always pay, except if the total exceeds transaction’s maximum fee per gas:
  - The base fee per gas of the block their  transaction was included in,
  - The priority fee per gas  set in the transaction

#### Motivation                

Ethereum historically priced transaction fees using a simple auction  mechanism, where users send transactions with bids (“gasprices”) and  miners choose transactions with the highest bids, and transactions that  get included pay the bid that they specify. This leads to several large  sources of inefficiency:

- Mismatch between volatility of transaction fee levels and social cost of transactions*
- Needless delays for users
- Inefficiencies of first price auctions 
- Instability of blockchains with no block reward
- and so on...

[eips.ethereum.org/EIPS/eip-1559](https://eips.ethereum.org/EIPS/eip-1559)

[consensys.io/blog/what-is-eip-1559-how-will-it-change-ethereum](https://consensys.io/blog/what-is-eip-1559-how-will-it-change-ethereum)

### EIP-2929 (2021 / Berlin Hard fork)

#### Summary (Gas Cost Increases for State Access OpCodes)

Introduced to increase gas costs for certain state access operations, helping to mitigate potential attack vectors that could exploit these lower costs.

####  Abstract

- Increase the gas cost of `SLOAD` (`0x54`) to 2100,
- Increase the `*CALL` opcode family (`0xf1`, `f2`, `f4`, `fA`), `BALANCE` `0x31` and the `EXT*` opcode family (`0x3b`, `0x3c`, `0x3f`) to 2600. 
- Exempts (i) precompiles, and (ii) addresses and storage slots that have already been accessed in the same transaction, which get a decreased gas cost. 
- Additionally reforms `SSTORE` metering and `SELFDESTRUCT` to ensure “de-facto storage loads” inherent in those opcodes are priced correctly.

#### Motivation

Storage-accessing opcodes (`SLOAD`, as well as the `*CALL`, `BALANCE` and `EXT*` opcodes) have historically been underpriced. 

In the 2016 Shanghai DoS attacks, once the most serious client bugs were fixed, one of the more durably successful strategies used by the attacker was to simply send transactions that access or call a large number of accounts.

Gas costs were increased to mitigate this, but a research paper suggested they were not increased enough. Quoting [arxiv.org/pdf/1909.07220.pdf](https://arxiv.org/pdf/1909.07220.pdf):

> Although by itself, this issue might seem benign, `EXTCODESIZE` forces the client to search the contract ondisk, resulting in IO heavy transactions. While replaying the Ethereum history on our hardware, the malicious transactions took around 20 to 80 seconds to execute, compared to a few milliseconds for the average transactions

This proposed EIP increases the costs of these opcodes by a factor of ~3, reducing the worst-case processing time to ~7-27 seconds. 

A secondary benefit of this EIP is that it also performs most of the work needed to make [stateless witness sizes](https://ethereum-magicians.org/t/protocol-changes-to-bound-witness-size/3885) in Ethereum acceptable. Assuming [a switch to binary tries](https://ethresear.ch/t/binary-trie-format/7621), the theoretical maximum witness size not including code size (hence “most of the work” and not “all”) would decrease from `(12500000 gas limit) / (700 gas per BALANCE) * (800 witness bytes per BALANCE) ~= 14.3M bytes` to `12500000 / 2600 * 800 ~= 3.85M bytes`. Pricing for code access could be changed when code merklization is implemented. There are similar benefits in the case of SNARK/STARK witnesses. 

While the EIP only increases the gas cost of the *first* access per transaction, the Subsequent accesses are  however made cheaper (100 gas in all cases). Additionally, calls to precompiles always cost 100 gas including the first call. This has some excellent positive consequences:

- Any use case of SLOAD followed by SSTORE (or SSTORE followed by SLOAD) of the same slot becomes cheaper. This is because the first storage read or write pays for accessing the storage slot, so it is already "warm" and the second read or write is cheaper; instead of a cost of 800 + 5000, we get a cost of 2100 + 2900 (approximately), a reduction of ~800. 
- Self-calling becomes cheaper
- Calls to precompiles become cheaper

[eips.ethereum.org/EIPS/eip-2929](https://eips.ethereum.org/EIPS/eip-2929)

[www.reddit.com/r/ethereum/comments/mrl5wg/a_quick_explanation_of_what_the_point_of_the_eip/](https://www.reddit.com/r/ethereum/comments/mrl5wg/a_quick_explanation_of_what_the_point_of_the_eip/)

### EIP-3198

**EIP-3198 (BASEFEE opcode)**: 

This proposal introduced an opcode to get the value of the base fee in the current block, enabling smart contracts to access the base fee information introduced by EIP-1559.

### Summary

Gas in Ethereum serves as a critical mechanism to ensure the network's security and efficiency by requiring users to pay for computational resources. Over time, various EIPs have been proposed and implemented to refine gas costs and transaction fee mechanisms, addressing both economic and security concerns. Notably, EIP-1559 introduced a transformative change, significantly impacting how transaction fees are calculated and managed within the network. Understanding these changes helps users and developers navigate and optimize their interactions with the Ethereum blockchain.

ChatGtp with the input:

- I would like an article to explain the concept of gas in Ethereum and the different relevant EIP regarding gas. I would like also an history of the different change in Ethereum regarding gas"