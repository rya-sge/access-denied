---
layout: post
title: Fungible Tokens across blockchains
date:   2024-07-12
lang: en
locale: en-GB
categories: blockchain ethereum defi
tags: erc20 fungible token
description: Representation of fungible tokens in the various existing blockchains. On Ethereum, its largest representative is the ERC-20 standard.
image: /assets/article/blockchain/defi/money-2180330_640.jpg
isMath: false
---

**ERC-20** tokens are widely used in the Ethereum ecosystem. But why?

ERC-20 is a standard to describe a **fungible token**. Fungibility describes a commodity, security, or other good that is mostly interchangeable with other units of the same kind. For example, as a real-world analogy, a 10 USD bill can be interchanged with another 10 USD bill. They have the same value.

If you have 1 unit of an ERC-20, e.g. 1 USDC,  this unit is strictly equal to another unit of USDC owned by someone else.

Since fungibility implies equal value between the assets, it simplified the exchange and trade processes.

Each blockchain has its own way to represent a fungible token:

A) By providing a common interface or standard, like Ethereum with the well-known ERC-20. 

B) or by incorporated into the blockchain a fungible token implementation.

In the first case, the standard is a common interface that the fungible token must follow and enables **interoperability** between the difference application build on the blockchain, for example a decentralized exchange. This offers great flexibility in terms of implementation, but this is a source of vulnerabilities if the interface is not fully respected by the developers.

With the second case, the choice is more restricted but it is easier to launch a token respecting blockchain standards

Some blockchains, like Stellar, choose to offer a common interface (A) as well as an implementation incorporated into the blockchain (B) to have the best of both worlds.

Finally, I decided to create a specific category for **Bitcoin**, which its development is not managed by a foundation and where the different way to represent fungible tokens on Bitcoin are more proposals from various persons and projects rather than a common standard incorporated into the network.

The summary tab is also available as a gist on my Github: [click here](https://gist.github.com/rya-sge/b5e41176fd66a7b999e729bfb09037e2)

Reference: [What Are Fungible Goods? Meaning, Examples, and How to Trade](https://www.investopedia.com/terms/f/fungibles.asp), [Robinhood learn - What is Fungibility?](https://learn.robinhood.com/articles/6euYOzP4ARB6WZPwZWu358/what-is-fungibility/)

[TOC]

## Summary

| Blockchain                                 | Standards                                                    |
| ------------------------------------------ | ------------------------------------------------------------ |
| Aleo                                       | [ARC-20](https://aleo.up.railway.app/p/2bf1586d-b8de-419d-afac-f94f48a5de34) (draft) |
| Algorand                                   | [Algorand Standard Assets (ASAs)](https://developer.algorand.org/docs/get-details/asa/) |
| Arbitrum<br />(Ethereum Layer2)            | Same as Ethereum                                             |
| Aptos                                      | [Fungible Asset Standard](https://aptos.dev/en/build/smart-contracts/fungible-asset) |
| Avalanche                                  | Same as Ethereum                                             |
| Aztec                                      | -                                                            |
| Base<br />(Ethereum Layer2)                | Same as Ethereum                                             |
| Bitcoin                                    | [BRC-20](https://domo-2.gitbook.io/brc-20-experiment), [SRC-20](https://github.com/stampchain-io/stamps_sdk/blob/main/docs/src20specs.md), [Runes](https://docs.ordinals.com/runes.html) |
| Canton Network                             | [Asset Model](https://docs.daml.com/daml-finance/concepts/asset-model.html) |
| Cardano                                    | [Native tokens](https://docs.cardano.org/developer-resources/native-tokens/) |
| Cosmos                                     | CosmWasm: [CW20](https://github.com/CosmWasm/cw-plus/blob/main/packages/cw20/README.md)<br />IBC: [ICS-20](https://github.com/cosmos/ibc/blob/main/spec/app/ics-020-fungible-token-transfer/README.md) |
| Cronos                                     | Same as Ethereum, see [docs.cronos.org - ERC-20](https://docs.cronos.org/cronos-play/getting-started_unreal/quick-start/erc20) |
| Ethereum                                   | [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [ERC-777](https://eips.ethereum.org/EIPS/eip-777) |
| Binance Smart Chain <br />(EVM compatible) | [BEP-20](https://github.com/bnb-chain/BEPs/blob/master/BEPs/BEP20.md) |
| Filecoin                                   | -Same as Ethereum, see <br />[docs.filecoin.io - erc-20-quickstart](https://docs.filecoin.io/smart-contracts/fundamentals/erc-20-quickstart)<br />-[FRC-0046 [draft]](https://github.com/filecoin-project/FIPs/blob/master/FRCs/frc-0046.md) |
| Hedera                                     | Same as Ethereum, see<br /> [docs.hedera.com - ERC-20 (Fungible Tokens)](https://docs.hedera.com/hedera/core-concepts/smart-contracts/tokens-managed-by-smart-contracts/erc-20-fungible-tokens) |
| Hyperliquid                                | [HIP-1](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard) |
| ICP                                        | [ICRC-1](https://github.com/dfinity/ICRC-1/blob/main/standards/ICRC-1/README.md) |
| Mina                                       | [RFC-14](https://github.com/o1-labs/rfcs/blob/main/0014-fungible-token-standard.md) |
| Near                                       | [NEP-141](https://github.com/near/NEPs/blob/master/neps/nep-0141.md) |
| Neo                                        | [NEP-5](https://docs.neo.org/v2/docs/en-us/sc/write/nep5.html) |
| Optimism<br />(Ethereum Layer2)            | Same as Ethereum                                             |
| Polkadot                                   | [PSP-22](https://github.com/w3f/PSPs/blob/master/PSPs/psp-22.md) |
| Polygon PoS<br />(Ethereum Layer2)         | Same as Ethereum                                             |
| Scroll<br />(Ethereum Layer2)              | Same as Ethereum                                             |
| Sei                                        | ERC-20, CW20<br />See [docs.sei.io - dev-token-standards](https://www.docs.sei.io/dev-token-standards) |
| StarkNet<br />(Ethereum Layer2)            | Same as Ethereum,<br />but written in Cairo.<br />See [Cairo by example](https://cairo-by-example.com/examples/erc20/) |
| Solana                                     | [SPL token](https://spl.solana.com/token)                    |
| Stacks <br />( Bitcoin Layer2)             | [SIP10](https://github.com/stacksgov/sips/blob/main/sips/sip-010/sip-010-fungible-token-standard.md) |
| Sui                                        | [Coin Standard](https://docs.sui.io/standards/coin), [Close-Loop token](https://docs.sui.io/standards/closed-loop-token) |
| Stellar                                    | [CAP: 0046-06](https://github.com/stellar/stellar-protocol/blob/master/core/cap-0046-06.md) (native contract implementation for classic tokens)<br />[SEP: 0041](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0041.md) (Soroban Token Interface) |
| Tezos                                      | [FA1.2 (TZIP-7)](https://tzip.tezosagora.org/proposal/tzip-7/), [FA2 (TZIP-12)](https://tzip.tezosagora.org/proposal/tzip-12/) |
| TON                                        | [Jettons (TEP-74)](https://github.com/ton-blockchain/TEPs/blob/master/text/0074-jettons-standard.md) |
| Tron <br />(EVM compatible)                | [TRC-20](https://developers.tron.network/docs/trc20-protocol-interface) |
| XRP Ledger                                 | [Fungible Tokens](https://xrpl.org/docs/concepts/tokens/fungible-tokens/) |
| ZCash                                      | [ZIP 220 / Zcash Shielded Assets](https://github.com/zcash/zcash/issues/830) (draft) <br /><br />See [A Proposal for Shielded Assets (ZSA/UDA) for DeFi on Zcash](https://forum.zcashcommunity.com/t/a-proposal-for-shielded-assets-zsa-uda-for-defi-on-zcash/40520) |
| ZKSync<br />(Ethereum Layer2)              | Same as Ethereum, <br />see [docs.zksync - Create an ERC20 token](https://docs.zksync.io/build/quick-start/erc20-token) |



## Standard interface

### EVM Chain

#### Ethereum (ERC-20, ERC-233, ERC-777)

##### ERC-20

Specification: [ERC-20](https://eips.ethereum.org/EIPS/eip-20)

The main standard to represent fungible token in Ethereum and EVM-chain is the standard ERC-20. This standard offers the following methods to:

- Transfer tokens from one account to another
- Get the current token balance of an account
- Get the total supply of the token available on the network
- Approve whether an amount of token from an account can be spent by a third-party account

```solidity
function name() public view returns (string)
function symbol() public view returns (string)
function decimals() public view returns (uint8)
function totalSupply() public view returns (uint256)
function balanceOf(address _owner) public view returns (uint256 balance)
function transfer(address _to, uint256 _value) public returns (bool success)
function transferFrom(address _from, address _to, uint256 _value) public returns (bool success)
function approve(address _spender, uint256 _value) public returns (bool success)
function allowance(address _owner, address _spender) public view returns (uint256 remaining)
```

Other reference: [ethereum.org - ERC-20 Token Standard](https://ethereum.org/en/developers/docs/standards/tokens/erc-20/)

##### ERC-223

Specification: [ERC-223](https://eips.ethereum.org/EIPS/eip-223)

The following describes an interface and logic for fungible tokens that supports a `tokenReceived` callback to notify contract recipients when tokens are received. This makes tokens behave identical to ether.

```solidity
function totalSupply() view returns (uint256)
function name() view returns (string memory)
function symbol() view returns (string memory)
function decimals() view returns (uint8)
function balanceOf(address _owner) view returns (uint256)
function transfer(address _to, uint _value) returns (bool)
function transfer(address _to, uint _value, bytes calldata _data) returns (bool)
```

And also a token receiver method

A function for handling token transfers, which is called from the token contract, when a token holder sends tokens.

```solidity
function tokenReceived(address _from, uint _value, bytes calldata _data) returns (bytes4)

```

##### ERC-777

Specification: [ERC-777](https://eips.ethereum.org/EIPS/eip-777)

This standard tries to improve the [ERC-20](https://eips.ethereum.org/EIPS/eip-20) token standard. The main advantages of this standard are:

1. Uses the same philosophy as Ether in that tokens are sent with `send(dest, value, data)`.
2. Both contracts and regular addresses can control and reject which token they send by registering a `tokensToSend` hook. (Rejection is done by `revert`ing in the hook function.)
3. Both contracts and regular addresses can control and reject which token they receive by registering a `tokensReceived` hook. (Rejection is done by `revert`ing in the hook function.)
4. The `tokensReceived` hook allows to send tokens to a contract and notify it in a single transaction, unlike [ERC-20](https://eips.ethereum.org/EIPS/eip-20) which requires a double call (`approve`/`transferFrom`) to achieve this.
5. The holder can “authorize” and “revoke” operators which can send tokens on their behalf. These operators are intended to be verified contracts such as an exchange, a cheque processor or an automatic charging system.
6. Every token transaction contains `data` and `operatorData` bytes fields to be used freely to pass data from the holder and the operator, respectively.
7. It is backward compatible with wallets that do not contain the `tokensReceived` hook function by deploying a proxy contract implementing the `tokensReceived` hook for the wallet.



####  Binance Smart Chain (BEP-20)

Specification: [github.com/bnb-chain - BEP20.md](https://github.com/bnb-chain/BEPs/blob/master/BEPs/BEP20.md)

> The BNB Smart Chain supports EVM-compatible smart contracts and protocols.

Binance Smart Chain’s standard that extends Ethereum’s ERC-20. 

BEP-20 is compatible with ERC-20

The standard is interoperable with BEP-2 (Binance Chain) and similar functionality to ERC-20.

**Method**

```solidity
function name() public view returns (string)
function symbol() public view returns (string)
function decimals() public view returns (uint8)
function totalSupply() public view returns (uint256)
function balanceOf(address _owner) public view returns (uint256 balance)
unction transfer(address _to, uint256 _value) public returns (bool success)
function transfer(address _to, uint256 _value) public returns (bool success)
function transferFrom(address _from, address _to, uint256 _value) public returns (bool success)
function approve(address _spender, uint256 _value) public returns (bool success)
function allowance(address _owner, address _spender) public view returns (uint256 remaining)
```

There is also an extension `getOwner` which is required to flow across the BNB Beacon Chain and BNB Smart Chain.

```solidity
function getOwner() external view returns (address);
```

Reference: [Binance Academy - BEP-20](https://academy.binance.com/en/glossary/bep-20), [bnb chain doc - Introduction](https://docs.bnbchain.org/bnb-smart-chain/developers/overview/), https://www.ledger.com/academy/glossary/bep-20

#### Tron (TRC-20)

Specification: [developers.tron.network - trc20-protocol-interface](https://developers.tron.network/docs/trc20-protocol-interface)

> TRON is compatible with Ethereum, which means that you can migrate smart contracts on Ethereum to TRON generally directly or with minor modification
>
> The difference can be found here: [Differences between TVM and EVM](https://developers.tron.network/docs/tvm#differences-from-evm)

[TRC-20](https://developers.tron.network/docs/trc20-protocol-interface) is the standard to represent fungible token on the Tron blockchain.

The concept is also very similar to the standard ERC-20 from Ethereum, with almost the same functions.

```javascript
function totalSupply() constant returns (uint theTotalSupply);
function balanceOf(address _owner) constant returns (uint balance);
function transfer(address _to, uint _value) returns (bool success);
function transferFrom(address _from, address _to, uint _value) returns (bool success);
function approve(address _spender, uint _value) returns (bool success);
function allowance(address _owner, address _spender) constant returns (uint remaining);
event Transfer(address indexed _from, address indexed _to, uint _value);
event Approval(address indexed _owner, address indexed _spender, uint _value);
```

Reference: [https://developers.tron.network/docs/getting-start](https://developers.tron.network/docs/getting-start)

### Cosmos

#### CW20

Specification: [CW2](https://github.com/CosmWasm/cw-plus/blob/main/packages/cw20/README.md)

CW20 is a specification for fungible tokens based on CosmWasm. The name and design is loosely based on Ethereum's ERC20 standard, but many changes have been made, for example to manage the allowance and additional information related to the token (metadata).

##### Base

Messages:

- Transfer{recipient, amount}
- Send{contract, amount, msg}
- Burn{amount}

Queries:

- Balance{address}
- TokenInfo{}

##### Allowances

Message:

- IncreaseAllowance{spender, amount, expires}
- DecreaseAllowance{spender, amount, expires}
- TransferFrom{owner, recipient, amount}
- SendFrom{owner, contract, amount, msg}
- BurnFrom{owner, amount}

Queries:

- Allowance{owner, spender}

##### Other functionalities

Mintable: allows another contract to mint new tokens, possibly with a cap

Enumerable:  allows  to get lists of results with pagination.

Marketing: allows to attach more metadata on the token to help with displaying the token in wallets.

#### IBC - ICS-20

Specification: [github.com/cosmos/ibc/blob/main/spec/app/ics-020-fungible-token-transfer/README.md](https://github.com/cosmos/ibc/blob/main/spec/app/ics-020-fungible-token-transfer/README.md).

This standard document specifies packet data structure, state machine handling logic, and encoding details for the transfer of fungible tokens over an IBC channel between two modules on separate chains.

This standard is not strictly speaking a standard for defining a fungible token but rather a standard to define the way of transferring them.

Further reading: [tutorials.cosmos.network - IBC Token Transfer](https://tutorials.cosmos.network/academy/3-ibc/7-token-transfer.html)



### ICP (ICRC-1)

Specification: [github.com/dfinity/ICRC-1 - ICRC-1](https://github.com/dfinity/ICRC-1/blob/main/standards/ICRC-1/README.md), [internetcomputer.org/docs - 4.2-icrc-tokens](https://internetcomputer.org/docs/current/tutorials/developer-journey/level-4/4.2-icrc-tokens)

The ICRC-1 is a standard for Fungible Tokens on the [Internet Computer](https://internetcomputer.org).

Available method: 

- `icrc1_name, `
- `icrc1_symbol , `
- `icrc1_decimals, `
- `icrc1_fee, `
- `icrc1_metadata, `
- `crc1_total_supply, `
- `icrc1_minting_account, `
- `icrc1_balance_of, `
- `crc1_transfer`.

In short, the standard has three supplementary methods compared to the ERC-20 standard.

- icrc1_minting_account

Returns the [minting account](https://github.com/dfinity/ICRC-1/blob/main/standards/ICRC-1/README.md#minting_account) if this ledger supports minting and burning tokens.

```haskell
icrc1_minting_account : () -> (opt Account) query;
```

- icrc1_metadata 

Returns the list of metadata entries for this ledger. See the "Metadata" section below.

```haskell
type Value = variant { Nat : nat; Int : int; Text : text; Blob : blob };
icrc1_metadata : () -> (vec record { text; Value }) query;
```

- crc1_fee 

Returns the default transfer fee.

```haskell
icrc1_fee : () -> (nat) query;
```

### NEO (NEP-5)

Specification: [docs.neo.org/v2/docs/en-us/sc/write/nep5.html](https://docs.neo.org/v2/docs/en-us/sc/write/nep5.html)

NEO’s standard for creating tokens, similar to Ethereum’s ERC-20.

- Different from UTXO, the NEP5 assets are recorded in the contract storage area, through updating account balance in the storage area, to complete the transaction.
- The interface is similar to ERC-20 and provides the following functions: totalSupply, name, symbol, decimals, balanceOf, transfer and a Transfer Event.



### TON (Jettons)

Specification: [github.com/ton-blockchain - 0074-jettons-standard.md](https://github.com/ton-blockchain/TEPs/blob/master/text/0074-jettons-standard.md)

[TEP-74](https://github.com/ton-blockchain/TEPs/blob/master/text/0074-jettons-standard.md) is the TON Enhancement Proposals which defines a fungible token for the TON blockchain.

Before describing the standard, here the nomenclature:

- "Jetton" with capital `J` as designation for entirety of tokens of the same type
-  "jetton" with `j` as designation of amount of tokens of some type.

TEP-74 standard describes:

- The way of jetton transfers.
- The way of retrieving common information (name, circulating supply, etc) about given Jetton asset.

Jettons are organized as follows: 

Each Jetton has a master smart contract which is used to mint new jettons, account for circulating supply and provide common information.

Example: if you release a Jetton with circulating supply of 200 jetton which are owned by 3 people, then you will deploy 4 contracts: 1 Jetton-master and 3 jetton-wallets.

### NEAR (NEP-148)

Specification: 

- [nomicon.io/Standards/Tokens/FungibleToken/Core](https://nomicon.io/Standards/Tokens/FungibleToken/Core)
- [nomicon.io/Standards/Tokens/FungibleToken/](https://nomicon.io/Standards/Tokens/FungibleToken/)

> NEAR Protocol uses an asynchronous, sharded runtime. This means the following:
>
> - Storage for different contracts and accounts can be located on different shards.
> - Two contracts can be executed at the same time in different shards.

A standard interface for fungible tokens that allows for a normal transfer as well as a transfer and method call in a single transaction. 

- The [storage standard](https://nomicon.io/Standards/StorageManagement) addresses the needs (and security) of storage staking. 
- The [fungible token metadata standard](https://nomicon.io/Standards/Tokens/FungibleToken/Metadata) provides the fields needed for ergonomics across dApps and marketplaces.

Main functionalities

- **Total supply**: the total number of tokens in circulation.
- **Balance owner**: an account ID that owns some amount of tokens.
- **Balance**: an amount of tokens.
- **Transfer**: an action that moves some amount from one account to another account, either an externally owned account or a contract account.
- **Transfer and call**: an action that moves some amount from one account to a contract account where the receiver calls a method. This is a concept similar to what is done in the standard [ERC-777](https://eips.ethereum.org/EIPS/eip-777).
- **Storage amount**: the amount of storage used for an account to be "registered" in the fungible token. This amount is denominated in Ⓝ, not bytes, and represents the [storage staked](https://docs.near.org/concepts/storage/storage-staking).

Interface

```rust
function ft_transfer(
    receiver_id: string,
    amount: string,
    memo: string|null
): void {}

function ft_transfer_call(
   receiver_id: string,
   amount: string,
   memo: string|null,
   msg: string
): Promise {}

/****************************************/
/* CHANGE METHODS on receiving contract */
/****************************************/

function ft_on_transfer(
    sender_id: string,
    amount: string,
    msg: string
): string {}

/****************/
/* VIEW METHODS */
/****************/

// Returns the total supply of fungible tokens as a string representing the value as an unsigned 128-bit integer.
function ft_total_supply(): string {}

// Returns the balance of an account in string form representing a value as an unsigned 128-bit integer. If the account doesn't exist must returns `"0"`.
function ft_balance_of(
    account_id: string
): string {}
```



### Polkadot (PSP-22)

Specification: [github.com/w3f/PSPs/blob/master/PSPs/psp-22.md](https://github.com/w3f/PSPs/blob/master/PSPs/psp-22.md)

A Polkadot Smart Contract Proposal (PSP) describes standards for smart contracts in the Polkadot ecosystem.

PSP-22 is the standard proposal for a fungible token interface for WebAssembly smart contracts which run on Substrate's [`contracts` pallet](https://github.com/paritytech/substrate/tree/master/frame/contracts).

**Interface**

```rust
total_supply() ➔ Balance
balance_of(owner: AccountId) ➔ Balance
allowance(owner: AccountId, spender: AccountId) ➔ Balance
transfer(to: AccountId, value: Balance, data: [u8]) ➔ Result<(), PSP22Error>
transfer_from(from: AccountId, to: AccountId, value: Balance, data: [u8]) ➔ Result<(), PSP22Error>
approve(spender: AccountId, value: Balance) ➔ Result<(), PSP22Error>
increase_allowance(spender: AccountId, delta_value: Balance) ➔ Result<(), PSP22Error>
decrease_allowance(spender: AccountId, delta_value: Balance) ➔ Result<(), PSP22Error>
token_name() ➔ Option
token_symbol() ➔ Option
token_decimals() ➔ u8
```

The interface is very similar to the ERC-20 interface but adds two functions: `increase_allowance` and `decrease_allowance` which are a good improvement to avoid the [approval front-running](https://scsfg.io/hackers/approvals/) risk.

Reference implementation: [github.com/Brushfam/openbrush-contracts - psp22/psp22.rs](https://github.com/Brushfam/openbrush-contracts/blob/main/contracts/src/token/psp22/psp22.rs)

### Stacks (SIP-010)

Specification: [github.com/stacksgov/sips/blob/main/sips/sip-010/sip-010-fungible-token-standard.md](https://github.com/stacksgov/sips/blob/main/sips/sip-010/sip-010-fungible-token-standard.md)

> Stacks is a Bitcoin L2, bringing smart contract functionality to Bitcoin, without modifying Bitcoin itself.

SIP-010 is the standard proposal for a fungible token interface for Stacks, in Clarity, the smart contract language used by Stacks.

The interface is defined as a *trait*, a trait defines a group of functions to which a specific contract can choose to conform to. They are used to ensure compatibility of smart contracts with a given standard implementation.

Available method: 

- `transfer `
- `get-name, `
- `get-symbol, `
- `get-decimals, `
- `get-balance, `
- `get-total-supply, `
- `get-token-uri, `

Implementation example:

```rust
(define-trait sip-010-trait
  (
    ;; Transfer from the caller to a new principal
    (transfer (uint principal principal (optional (buff 34))) (response bool uint))

    ;; the human readable name of the token
    (get-name () (response (string-ascii 32) uint))

    ;; the ticker symbol, or empty if none
    (get-symbol () (response (string-ascii 32) uint))

    ;; the number of decimals used, e.g. 6 would mean 1_000_000 represents 1 token
    (get-decimals () (response uint uint))

    ;; the balance of the passed principal
    (get-balance (principal) (response uint uint))

    ;; the current total supply (which does not need to be a constant)
    (get-total-supply () (response uint uint))

    ;; an optional URI that represents metadata of this token
    (get-token-uri () (response (optional (string-utf8 256)) uint))
  )
)
```

Further reading: [learnweb3 - SIP-010 Fungible Tokens & Traits](https://learnweb3.io/lessons/sip-010-fungible-tokens-and-traits/)

### Stellar (SEP: 0041)

This proposal defines a standard contract interface for tokens. The interface is a subset of the Stellar Asset contract, and compatible with its descriptive and token interfaces defined in [CAP-46-6](https://github.com/stellar/stellar-protocol/blob/master/core/CAP-0046-06.md).

```rust
pub trait TokenInterface {
    /// Returns the allowance for `spender` to transfer from `from`.
    fn allowance(env: Env, from: Address, spender: Address) -> i128;

    /// Set the allowance by `amount` for `spender` to transfer/burn from
    /// `from`.
    fn approve(env: Env, from: Address, spender: Address, amount: i128, live_until_ledger: u32);

    /// Returns the balance of `id`.
    fn balance(env: Env, id: Address) -> i128;

    /// Transfer `amount` from `from` to `to`.
    fn transfer(env: Env, from: Address, to: Address, amount: i128);

    /// Transfer `amount` from `from` to `to`, consuming the allowance of
    /// `spender`. Authorized by spender (`spender.require_auth()`).
    fn transfer_from(env: Env, spender: Address, from: Address, to: Address, amount: i128);

    /// Burn `amount` from `from`.
    fn burn(env: Env, from: Address, amount: i128);

    /// Burn `amount` from `from`, consuming the allowance of `spender`.
    fn burn_from(env: Env, spender: Address, from: Address, amount: i128);

    /// Returns the number of decimals used to represent amounts of this token.
    fn decimals(env: Env) -> u32;

    /// Returns the name for this token.
    fn name(env: Env) -> String;

    /// Returns the symbol for this token.
    fn symbol(env: Env) -> String;
}
```



### Tezos (FA1.2/FA2)

#### FA1.2

The FA1.2 standard (standing for *Financial Application 1.2*) refers to the fungible token standard for Tezos.

- This standard describes a smart contract which implements a ledger that maps identities to balances.
- This ledger implements token transfer operations, as well as approval for spending tokens from other accounts which is a similar concept to what is done with ERC-20.

The FA1.2 specification is described in detail in [TZIP-7](https://tzip.tezosagora.org/proposal/tzip-7/)

A contract which implements this standard must have the following entrypoints:

```lisp
(address :from, (address :to, nat :value)) %transfer
(address :spender, nat :value) %approve
(view (address :owner, address :spender) nat) %getAllowance
(view (address :owner) nat) %getBalance
(view unit nat) %getTotalSupply
```

References: [opentezos.com/defi/token-standards/#fa12](https://opentezos.com/defi/token-standards/#fa12)

#### FA2

Specification: [tzip.tezosagora.org/proposal/tzip-12/](https://tzip.tezosagora.org/proposal/tzip-12/)

Fungible token can also be represented with the standard TZIP-012, which proposes a standard for a unified token contract interface.

This standard supports a wide range of token types, in addition to the fungible tokens, and implementations: non-fungible ([ERC-721](https://ethereum.org/en/developers/docs/standards/tokens/) on Ethereum),non-transferable ([ERC-1238](https://ethereum.org/en/developers/docs/standards/tokens/) on Ethereum) and also multi-asset contracts [ERC-1155](https://ethereum.org/en/developers/docs/standards/tokens/) on Ethereum).

A variety of transfer permission policies can also be defined to control who can perform a transfer or receiver tokens.

A token contract can be designed to support a single token type or multiple token types to optimize batch transfers and atomic swaps. An FA2 implementation may also  include hybrid implementations where multiple token kinds (fungible, non-fungible, non-transferable, etc) can co-exist (e.g. in a fractionalized NFT contract).

The FA2 has been designed to be the successor to [FA1.2](https://opentezos.com/defi/token-standards#references) but the latter is still very present in the industry

For example, here the description of the transfer function:

Each transfer in the batch is specified between one source (`from_`) address and a list of destinations. Each `transfer_destination` specifies token type and the amount to be transferred from the source address to the destination (`to_`) address.

```lisp
transfer
(list %transfer
  (pair
    (address %from_)
    (list %txs
      (pair
        (address %to_)
        (pair
          (nat %token_id)
          (nat %amount)
        )
      )
    )
  )
```

Reference: [opentezos.com/defi/token-standards/#fa12, https://opentezos.com/defi/token-standards/](https://opentezos.com/defi/token-standards/#fa12, https://opentezos.com/defi/token-standards/)

## Integrated program

### Algorand (ASAs)

Specification: [developer.algorand - Algorand Standard Assets (ASAs)](https://developer.algorand.org/docs/get-details/asa/)

The implementation on Algorand of Fungible tokens is made of two main points:

- They are implemented as Algorand Standard  Assets (ASAs). 
- They do not need to write smart contract code. 

This is the same principle for the implementation of NFT.

You just need to specify:

- A few parameters to identify it as an FT  (e.g. total count is greater than 1) 
- Attach metadata so that  potential owners have the information they need to validate the integrity of the asset. 

The implementation defines also eight immutable parameters:

- [Creator](https://developer.algorand.org/docs/get-details/transactions/transactions#creator) (*required*)
- [AssetName](https://developer.algorand.org/docs/get-details/transactions/transactions#assetname) (*optional, but recommended*)
- [UnitName](https://developer.algorand.org/docs/get-details/transactions/transactions#unitname) (*optional, but recommended*)
- [Total](https://developer.algorand.org/docs/get-details/transactions/transactions#total) (*required*)
- [Decimals](https://developer.algorand.org/docs/get-details/transactions/transactions#decimals) (*required*)
- [DefaultFrozen](https://developer.algorand.org/docs/get-details/transactions/transactions#defaultfrozen) (*required*)
- [URL](https://developer.algorand.org/docs/get-details/transactions/transactions#url) (*optional*)
- [MetaDataHash](https://developer.algorand.org/docs/get-details/transactions/transactions#metadatahash) (*optional*)

Others references:

- [developer.algorand.org - Create a fungible token](https://developer.algorand.org/docs/get-started/tokenization/ft/)
- [Algorand Request for Comments for standards](https://developer.algorand.org/docs/get-details/asa/)  
- The asset creation transaction can be created using any of [Algorands SDKs](https://developer.algorand.org/docs/sdks/). 
- Code demonstrating creating an Asset is available in the [ASA documentation](https://developer.algorand.org/docs/get-details/asa/#creating-an-asset).

### Aptos (Fungible Asset Standard)

Specification: [aptos.dev/standards/fungible-asset](https://aptos.dev/standards/fungible-asset)

In Aptos, fungibles tokens are represented by the Aptos Fungible Asset Standard (Fungible Asset or FA).

The standard is built upon [Aptos object model](https://aptos.dev/standards/aptos-object), so all the resources defined here are included in the object resource group and stored inside objects. 

The FA standard uses two Move Obkects:

- `Object<Metadata>`: include information about the FA, such as name, symbol, and decimals.
- `Object<FungibleStore>`: store a specific amount of FA units. 
  - FAs are units that are interchangeable with others of the same metadata. 
  - They can be stored in objects that contain a  FungibleStore resource. 
  - These store objects can be freely created, and FAs can be moved, split, and combined between them easily.

The standard also supports minting new units and burning existing units with appropriate controls.

The different objects involved - `Object<Metadata>` and `Object<FungibleStore>` objects, and their relationships to accounts are shown in the diagram below:

- **Metadata object**

```rust
#[resource_group_member(group = aptos_framework::object::ObjectGroup)]
struct Metadata has key {
    supply: Option<Supply>,
    /// Name of the fungible metadata, i.e., "USDT".
    name: String,
    /// Symbol of the fungible metadata
    symbol: String,
    /// Number of decimals used for display purposes.
    decimals: u8,
}
```

- Fungible asset

```rust
struct FungibleAsset {
    metadata: Object<Metadata>,
    amount: u64,
}
```

### Canton Network (Asset Model)

Specification: [docs.daml.com/daml-finance/concepts/asset-model.html](https://docs.daml.com/daml-finance/concepts/asset-model.html)

The integration of a fungible token in Canton is quite different compared to others blockchains. In the case of Canton, there is a strong motivation to be as close as possible to the definition and the use in the financial sector.

A fungible token is defined in the library Asset Model, which defines also NFTs. The difference between a fungible and a non-fungible token is done by precising the holding standard for the token, in the case of a fungible token, it is the standard holding *Fungible*.

The term used is an instrument, which describes the economic terms (rights and obligations) of one unit of a financial contract.

- It can be an ISIN code referencing some real-world (off-ledger) security, or it can encode specific on-ledger lifecycling logic.

- Every instrument must have an `issuer` party and a `depository` party, which are both signatories of the contract. On the ledger, the `depository` acts as a trusted party that prevents the `issuer` from potentially acting maliciously.

- Instruments are keyed by an [InstrumentKey](https://docs.daml.com/daml-finance/reference/code-documentation/daml-finance-rst/Daml-Finance-Interface-Types-Common-Types.html#constr-daml-finance-interface-types-common-types-instrumentkey-32970), which comprises:

  - the instrument `issuer`

  - the instrument `depository`

  - a textual `id`

  - a textual `version`

  - the instrument’s `holdingStandard`

- A holding contract represents the ownership of a certain amount of an instrument by an owner at a custodian.

- The library distinguishes four types of holdings, referred to as [Holding Standard](https://docs.daml.com/daml-finance/reference/code-documentation/daml-finance-rst/Daml-Finance-Interface-Types-Common-Types.html#type-daml-finance-interface-types-common-types-holdingstandard-38061)s, namely:

  - Fungible: Holdings that are fungible only.
  - Transferable: Holdings that are transferable only.
  - TransferableFungible: Holdings that are both transferable and fungible.
  - BaseHolding: Holdings that are neither transferable nor fungible.

### Hyperliquid (HIP-1)

Specification: [hyperliquid.gitbook.io - HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard)

> Hyperliquid is a  L1 optimized to operate an ecosystem of permissionless financial applications – every order, cancel, trade, and liquidation happens transparently on-chain..
>
> The main native application is a fully onchain order book perpetuals exchange, the Hyperliquid DEX. 

HIP-1 is a capped supply fungible token standard. It also features onchain spot order books between pairs of HIP-1 tokens.

The sender of the token genesis transaction will specify the following:

1. `name`: human readable, maximum 6 characters, no uniqueness constraints.
2. `weiDecimals`: the conversion rate from the minimal integer unit of the token to a human-interpretable float. For example, ETH on EVM networks has `weiDecimals = 18` and BTC on Bitcoin network has `weiDecimals = 8`.
3. `szDecimals`: the minimum tradable number of decimals on spot order books.
4. `maxSupply`: the maximum and initial supply. The supply may decrease over time due to spot order book fees or future burn mechanisms.
5. `initialWei`: optional genesis balances specified by the sender of the transaction. This could include a multisig treasury, an initial bridge mint, etc.
6. `anchorTokenWei` the sender of the transaction can specify existing HIP-1 tokens to proportionally receieve genesis balances.
7. `hyperliquidityInit`: parameters for initializing the Hyperliquidity for the USDC spot pair. See HIP-2 section for more details.

The deployment transaction of the token will generate a globally unique hash by which the L1 will index the token.

References: [hyperliquid.gitbook.io - About Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs)

###  Solana (SPL token)

Specification: [spl.solana.com/token](https://spl.solana.com/token)

Solana Program Library's token standard used for creating fungible tokens on the Solana blockchain.

The `spl-token` command-line utility can be used to experiment with SPL tokens. You can find more information in my article [Introduction to Solana and the spl-token command line](https://rya-sge.github.io/access-denied/2022/08/06/solana-spl-token/).

This section will cover the basics of how tokens are represented on Solana. These are referred to as SPL ([Solana Program Library](https://github.com/solana-labs/solana-program-library)) Tokens.

To represent a token, there are tree main entities: 

- The [Token Program](https://solana.com/docs/core/tokens#token-program) contains all the instruction logic for interacting with tokens on the network (both fungible and non-fungible).
- A [Mint Account](https://solana.com/docs/core/tokens#mint-account) represents a specific type of token and stores global metadata about the token such as the total supply and mint authority, which is the address authorized to create new units of a token.
- A [Token Account](https://solana.com/docs/core/tokens#token-account) keeps track of individual ownership of how many units of a specific type of token (mint account) are owned by a specific address.

There is also a new version of the Token Program *The Token Extensions Program which includes additional features while maintaining the same core functionalities.

This program comes with several different instructions included: 

- [`InitializeMint`](https://github.com/solana-labs/solana-program-library/blob/b1c44c171bc95e6ee74af12365cb9cbab68be76c/token/program/src/processor.rs#L29): Create a new mint account to represent a new type of token.
- [`InitializeAccount`](https://github.com/solana-labs/solana-program-library/blob/b1c44c171bc95e6ee74af12365cb9cbab68be76c/token/program/src/processor.rs#L84): Create a new token account to hold units of a specific type of token (mint).
- [`MintTo`](https://github.com/solana-labs/solana-program-library/blob/b1c44c171bc95e6ee74af12365cb9cbab68be76c/token/program/src/processor.rs#L522): Create new units of a specific type of token and add them to a token account. This increases the supply of the token and can only be done by the mint authority of the mint account.
- [`Transfer`](https://github.com/solana-labs/solana-program-library/blob/b1c44c171bc95e6ee74af12365cb9cbab68be76c/token/program/src/processor.rs#L228): Transfer units of a specific type of token from one token account to another.

Reference: [solana.com/docs/core/tokens](https://solana.com/docs/core/tokens)

### Stellar (cap-0046-06)

Specification: [github.com/stellar - cap-0046-06.md](https://github.com/stellar/stellar-protocol/blob/master/core/cap-0046-06.md), [developers.stellar.org - stellar-asset-contract](https://developers.stellar.org/docs/tokens/stellar-asset-contract)

Tokens exist in two forms on Stellar:

1. Assets issued by Stellar accounts (`G...` addresses) and their built-in [Stellar Asset Contract (SAC)](https://developers.stellar.org/docs/tokens/stellar-asset-contract) implementation, and
2. [Custom tokens](https://developers.stellar.org/docs/tokens/token-interface) issued by a deployed WASM contract (`C...` addresses).

This proposal introduces a native contract implementation for classic tokens. The interface tries to follow an ERC-20 model but adds several functions not available in the ERC-20 standard such as `burn`, `burn_from` and `authorized`.

#### Token interface

The token interface provides capabilities analogous to those of ERC-20 tokens.

```rust
/// Returns the allowance for `spender` to transfer from `from`.
fn allowance(e: &Host, from: Address, spender: Address) -> Result<i128, HostError>;

/// Set the allowance by `amount` for `spender` to transfer/burn from
/// `from`.
fn approve(
        e: &Host,
        from: Address,
        spender: Address,
        amount: i128,
        expiration_ledger: u32,
    ) -> Result<(), HostError>;

/// Returns the balance of `id`.
fn balance(env: Env, id: Address) -> i128;

/// Returns true if `id` is authorized to use its balance.
fn authorized(env: Env, id: Address) -> bool;

/// Transfer `amount` from `from` to `to`.
fn transfer(env: Env, from: Address, to: Address, amount: i128);

/// Transfer `amount` from `from` to `to`, consuming the allowance of
/// `spender`. Authorized by spender (`spender.require_auth()`).
fn transfer_from(env: Env, spender: Address, from: Address, to: Address, amount: i128);

/// Burn `amount` from `from`.
fn burn(env: Env, from: Address, amount: i128);

/// Burn `amount` from `from`, consuming the allowance of `spender`.
fn burn_from(env: Env, spender: Address, from: Address, amount: i128)
```

#### Admin interface

The admin interface provides the ability to control supply and some simple compliance functionality.

```rust
/// Sets the administrator to the specified address `new_admin`.
fn set_admin(env: Env, new_admin: Address);

/// Returns the admin of the contract.
fn admin(env: Env) -> Address;

/// Sets whether the account is authorized to use its balance. If
/// `authorized` is true, `id` should be able to use its balance.
fn set_authorized(env: Env, id: Address, authorize: bool);

/// Mints `amount` to `to`.
fn mint(env: Env, to: Address, amount: i128);

/// Clawback `amount` from `from` account. `amount` is burned in the
/// clawback process.
fn clawback(env: Env, from: Address, amount: i128);
```

#### Deployment

Deploying a contract that allows interacting with Stellar classic assets

```rust
// Creates the instance of Stellar Asset Contract corresponding to the provided asset. `asset`
fn create_asset_contract(asset: Object) -> Result<Object, Error>;

// init_asset will initialize a contract that can interact with a classic asset
// (Native, AlphaNum4, or AlphaNum12). 
fn init_asset(asset_bytes: Bytes) -> Result<(), Error>;
```



### Sui (Coin Standard)

>  Sui is a Layer 1 protocol blockchain with its own consensus and validation for transaction blocks 
>
>  Smart contracts and applications are written in Move.

Specification: [MystenLab - sui-framework/coin.md](https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/docs/sui-framework/coin.md)

#### Coin standard

Reference: [docs.sui.io/standards/coin](https://docs.sui.io/standards/coin)

The Coin standard is the technical standard used for smart contracts on  Sui for creating coins on the Sui blockchain. The Coin standard on Sui is equivalent to the ERC-20 technical standard on Ethereum.

The [Coin standard](https://docs.sui.io/standards/coin) works in an open-loop system - coins are free-flowing, [wrappable](https://docs.sui.io/concepts/object-ownership/wrapped), [freely transferable](https://docs.sui.io/concepts/transfers/custom-rules#the-store-ability-and-transfer-rules) and you can store them in any application. 

These types of tokens are represented with a specific type Coin `<T>`:

- Coins are denominated by their type parameter, `T`, which is also associated with metadata (like name, symbol, decimal precision). That applies to all instances of `Coin<T>`. 

- The `sui::coin` module exposes an interface over `Coin<T>` that treats it as fungible, meaning that a unit of `T` held in one instance of `Coin<T>` is interchangeable with any other unit of `T`

- You can create a coin using the `coin::create_currency` function. The publisher of the smart contract that creates the coin receives a `TreasuryCap` object which is required to mint new coins or to burn current ones. 

- `TreasuryCap`, short for "treasury capability", is required  to mint new coin supply. The `TreasuryCap` can be transferred to a different address of a trusted third party, or it can be destroyed. Destroying a `TreasuryCap` is similar to renouncing ownership in an ERC-20 contract

Example from the article by Mysten Labs: [How to Create a Token: ERC-20 Standard Versus Sui Coin](https://blog.sui.io/create-token-erc-20-versus-coin/)

```rust
use sui::coin::{Self, TreasuryCap};

public struct MY_COIN has drop {}

fun init(witness: MY_COIN, ctx: &mut TxContext) {
        let (treasury, metadata) = coin::create_currency(witness, 6, b"MY_COIN", b"", b"", option::none(), ctx);
        transfer::public_freeze_object(metadata);
        transfer::public_transfer(treasury, ctx.sender())
    }
```

Further reading: [Creating a Fungible Token on Sui: A Step-by-Step Guide](https://medium.com/@ksdumont/creating-a-fungible-token-on-sui-a-step-by-step-guide-d5484b4a77ee)

#### Closed-Loop Token

Specification: [Sui - Closed-Loop Token](https://docs.sui.io/standards/closed-loop-token)

An alternative to create fungible token is the **Closed-Loop  standard**. With this standard, you can limit the applications that can use the token  and set up custom policies for transfers, spends, and conversions. The [`sui::token` module](https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/docs/sui-framework/token.md) in the Sui framework defines the standard.

### XRP

Specification: [XRP Ledger - Fungible tokens](https://xrpl.org/docs/concepts/tokens/fungible-tokens/)

Fungible tokens on the XRP Ledger (XRPL) works and are implemented differently than in EVM fungible. They have similar properties:

- These tokens are fungible: all units of that token are interchangeable and indistinguishable. 
- Tokens can be used for [cross-currency payments](https://xrpl.org/docs/concepts/payment-types/cross-currency-payments/) and can be traded in the [decentralized exchange](https://xrpl.org/docs/concepts/tokens/decentralized-exchange/).

 To create fungible tokens, you 

- Set up a *trust line*, a form of accounting relationship, between two accounts
- Then send payments between them. 

Interesting fact: 

- With their concept of trust lines, You can not transfer a token to someone who don't want these tokens, which is not the case in Ethereum.

- It exists alos the concept of ["rippling"](https://xrpl.org/docs/concepts/tokens/fungible-tokens/rippling/), describes a process of atomic net settlement between multiple connected parties who have [trust lines](https://xrpl.org/docs/concepts/tokens/fungible-tokens/) for the same token. This is similar to the concept of [channel liquidity](https://rya-sge.github.io/access-denied/2023/12/21/lightning-network/#channel-liquidity) in Lightning Network

Here an [example](https://github.com/XRPLF/xrpl-dev-portal/blob/master/_code-samples/issue-a-token/js/issue-a-token.js) of a trust lines in Typescript, between an account and an issuer

```typescript
const currency_code = "FOO"
  const trust_set_tx = {
    "TransactionType": "TrustSet",
    "Account": hot_wallet.address,
    "LimitAmount": {
      "currency": currency_code,
      "issuer": cold_wallet.address,
      "value": "10000000000" // arbitrarily chosen
    }
  }
```

And here the example to send the transaction:

```typescript
 const send_token_tx = {
    "TransactionType": "Payment",
    "Account": cold_wallet.address,
    "Amount": {
      "currency": currency_code,
      "value": issue_quantity,
      "issuer": cold_wallet.address
    },
    "Destination": hot_wallet.address,
    "DestinationTag": 1 
  }

```

References: 

- [xrpl - Fungible Tokens](https://xrpl.org/docs/concepts/tokens/fungible-tokens/)
- [Ripple CTO Clarifies XRP Ledger's Token Naming and Fungibility](https://www.binance.com/en-NG/square/post/2024-06-20-ripple-cto-clarifies-xrp-ledger-s-token-naming-and-fungibility-9715949986545)
- [XRP Ledger](https://xrpl.org/docs/tutorials/how-tos/use-tokens/issue-a-fungible-token/)



## Bitcoin (BRC-20, SRC-20, Runes)

Finally, I decided to create a specific category for Bitcoin, which its development is not managed by a foundation.

Moreover, the different way to represent fungible tokens on Bitcoin are propositions from various persons and projects rather than a common standard incorporated into the network.

https://blockspace.media/insight/how-bitcoins-runes-actually-work/



### BRC-20

Specification: [domo-2.gitbook.io/brc-20-experiment](https://domo-2.gitbook.io/brc-20-experiment), [layer1 foundation - brc-20](https://layer1.gitbook.io/layer1-foundation/protocols/brc-20)

BRC-20 tokens use the Bitcoin Ordinals protocol, which stores  information in the witness data.  

It is important to note that this witness data can be pruned by a node.

As for Ordinal, Json is required for traceability.

There are three main operations:

- Create a brc-20 with the deploy function
- Mint an amount of brc-20's with the mint function
- Transfer an amount of brc-20's with the transfer function. 

**Deploy**

```json
{ 
  "p": "brc-20",
  "op": "deploy",
  "tick": "ordi",
  "max": "21000000",
  "lim": "1000"
}
```

**mint**

```json
{ 
  "p": "brc-20",
  "op": "mint",
  "tick": "ordi",
  "amt": "1000"
}
```

**Transfer BRC-20**

```json
{ 
  "p": "brc-20",
  "op": "transfer",
  "tick": "ordi",
  "amt": "100"
}
```

Further reading: [academy.binance.com - SRC-20 Tokens](https://academy.binance.com/ph/glossary/src-20-tokens)



### SRC-20

Specification: [github.com - src20specs.md](https://github.com/stampchain-io/stamps_sdk/blob/main/docs/src20specs.md)

Initially, SRC-20 were created through the [Counterparty protocol](https://www.counterparty.io/), but this is no longer the case and SRC-20 transactions are now created directly on BTC .

SRC-20 token data are stored on UTXOs. Therefore, they can not be pruned,  which ensures permanence.

SRC-20 transaction must be signed and broadcast onto BTC by the address that holds the SRC-20 token balance as it acts as a means to authenticate ownership. Both the source and destination addresses are embedded into the BTC transaction which is created by the users wallet. 

**Deploy**

```json
{
  "p": "src-20",
  "op": "deploy",
  "tick": "STAMP",
  "max": "100000",
  "lim": "100",
  "dec": "18" // [optional]
}
```

**Mint**

```json
{
  "p": "src-20",
  "op": "mint",
  "tick": "STAMP",
  "amt": "100"
}
```

**Transfer**

```json
{
  "p": "src-20",
  "op": "transfer",
  "tick": "STAMP",
  "amt": "100"
}
```

Further reading: [academy.binance.com - SRC-20 Tokens](https://academy.binance.com/ph/glossary/src-20-tokens), [docs.openstamp.io - src20-protocol](https://docs.openstamp.io/introduction/src20-protocol)

### Runes

Specification:  [docs.ordinals.com/runes.html](https://docs.ordinals.com/runes.html)

Runes allow Bitcoin transactions to etch, mint, and transfer Bitcoin-native digital commodities.

Rune protocol messages, called runestones, are stored in Bitcoin transaction outputs.

Runes uses the opcode OP_RETURN to include information, up to 80 bytes, about the fungible token (token ID, name, symbol,...).

The message in OP_RETURN does 1 of 3 things: 

- creates a Rune ticker
- “mints” a Rune ticker, 
- Sends/Transfers a Rune ticker.

Runes are identified by IDs, which consist of the block in which a rune was etched and the index of the etching transaction within that block, represented in text as `BLOCK:TX`. 

For example, the ID of the rune etched in the 20th transaction of the 500th block is `500:20`.

**Difference with BRC-20**

- Runes utilizes Bitcoin’s UTXO model to store Bitcoin and Runes balances  efficiently. 
- Through the use of the opcode OP_RETURN, Runes data are stored on Bitcoin’s UTXO output itself, contrary to BRC-20 assets which are stored on the witness data of a Bitcoin block. 

**Example:**

[ordinals.com - BASED•ON•CRYPTOGRAPHIC•PROOF](https://ordinals.com/rune/BASED%E2%80%A2ON%E2%80%A2CRYPTOGRAPHIC%E2%80%A2PROOF)

```

number
    86580
timestamp
    2024-07-03 03:11:38 UTC
id
    850474:2601
etching block
    850474
etching transaction
    2601
mint
    no
supply
    2100000000000000 💰
mint progress
    100%
premine
    2100000000000000 💰
premine percentage
    100%
burned
    0 💰
divisibility
    0
symbol
    💰
turbo
    false
etching
    26144f35c616901ed4f3f0f30b5e2f26931688e0617710468e2401abb1acf3d9 
```



References. [ledger - OP_Return](https://www.ledger.com/academy/glossary/op_return),  [Zulu Research - Runes protocol](https://medium.com/@zulu_network/zulu-research-runes-protocol-444b40d8bf39),