---
layout: post
title:  RareSkills Solidity Interview Answers - Medium
date:   2024-02-14
lang: en
locale: en-GB
categories: blockhain blockchainBestOf ethereum solidity
tags: ethereum solidity interview security gas
description: Solidity Interview questions - Medium, answers from the article - Solidity Interview Questions- by RareSkills.
image: /assets/article/blockchain/ethereum/solidity/solidity_logo.svg
isMath: true
---

This article presents the list of medium questions with their answers related to the article [Solidity Interview Questions](https://www.rareskills.io/post/solidity-interview-questions) by RareSkills.

For the levels Hard and Advanced, you can see [my second](https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/) and [third](https://rya-sge.github.io/access-denied/2024/05/06/solidity-interview-question-rareskills-advanced/) articles.

According to the article, all questions can be answered in three sentences or less.

The answers here are more complete tha

[TOC]

n necessary in order to explain in details the topics.



## DeFi

### What is a bonding curve ?

--- A bonding curve is a mathematical function connecting the supply of a digital asset with its value.

In summary, the price of a token change regarding the token supply

[What Is a Bonding Curve and How Does It Affect Token Price?](https://hackernoon.com/what-is-a-bonding-curve-and-how-does-it-affect-token-price)

### AMM price assets

>  How does an AMM price assets?

An *AMM* used different algorithm and mathematical formula to automatically price assets.

The historical formula, used by Uniswap V1 and V2, is the constant product formula:

```
x * y = k
```

where

x: number of token 1 in the pool

y: number of token 2 in the pool

k: constant that stays constant during trades but recalculated when liquidity is provided / withdrawn

See [Uniswap V2 - How Uniswap work](https://docs.uniswap.org/contracts/v2/concepts/protocol-overview/how-uniswap-works), [Back to the Basics: Uniswap, Balancer, Curve](https://medium.com/@kinaumov/back-to-the-basics-uniswap-balancer-curve-e930c3ad9046)

### Compound Finance 

>  How does Compound Finance calculate utilization?

The formula for producing the utilization is:

```
Utilization = TotalBorrows / TotalSupply
```

Ref: [docs.compound.finance/interest-rates/#get-utilization](https://docs.compound.finance/interest-rates/#get-utilization)

### What is TWAP?

--- A TWAP (Time Volume Weighted Average Price) is an oracle which returns the average price of an asset over a specific period.

To compute the average price, it will perform a sum up of each price for a certain amount of block and divide it by the number of blocks used. The formula can be summarized thus: 

![](https://static.wixstatic.com/media/935a00_cdd0c97f14834dfdbfb812597b8a34c3~mv2.png)

The goal of this oracle is to make more costly a flashhloan attack / price manipulation since a flashloan attack modifies the price of an asset inside the same block.

A attacker has to manipulate the price during a long period instead that just one block.

**Advantage**

- Generally, more robust again short-term manipulation (typically flashloan)


**Disadvantage**

- You can not use a TWAP to obtain prices of an asset over a small period of time since it will reduce the cost of a price manipulation attack.
- Moreover, TWAP oracles can not use the price of an assets on an exchange to compute the price.

Reference: [Halborn - WHAT ARE TWAP ORACLES?](https://www.halborn.com/blog/post/what-are-twap-oracles), [Halborn - Why TWAP Oracles Are Key to DeFi Security](https://www.halborn.com/blog/post/why-twap-oracles-are-key-to-defi-security), [TWAP Oracles vs. Chainlink Price Feeds: A Comparative Analysis](https://smartcontentpublication.medium.com/twap-oracles-vs-chainlink-price-feeds-a-comparative-analysis-8155a3483cbd), [How the TWAP Oracle in Uniswap v2 Works](https://www.rareskills.io/post/twap-uniswap-v2)

###  Slippage parameter

> What is a slippage parameter useful for?

--- Slippage refers to the difference between the expected price of a trade and the actual executed price due to market volatility or liquidity issues.

It can p.ex happens on a DEX with a large order or if the transaction is targeted by a sandwich attack.

A slippage parameter in a function allows to indicate the minimum amount of tokens that you want to be returned from a swap or another operation.

Reference: [What are Slippage Attacks in Decentralized Exchanges (DEXs)?](https://www.immunebytes.com/blog/what-are-slippage-attacks-in-decentralized-exchanges-dexs/)

## Gas

### Loop

> How do you write a gas-efficient for loop in Solidity?

1) Cache storage variable in a local variable
2) Use `++i`instead of `i++`
3) Eventually*: use `unchecked` to update the counter `i`

**Solution**

```solidity
// Store the storage variable inside a local variable
uint256 limit = storageVariableUint256;
for (uint256 i; i <= limit; ) {
    // deactivate check overflow
    unchecked {
    	// ++i instead of i++
        ++i;
    }
}
```

You find more optimizations in my other articles on gas optimization: [Gas Optimization](https://rya-sge.github.io/access-denied/2023/09/26/gas-optimization/)

**Exception**

*The solidity version [0.8.22](https://soliditylang.org/blog/2023/10/25/solidity-0.8.22-release-announcement) introduces an overflow check optimization that automatically generates an unchecked arithmetic increment of the counter of for loops.  As a result, it is not useful to use `unchecked` if the loop meets the criteria (see the release doc). 

This native optimization works only for the comparaison `<`and not with `<=`

**Example**

```solidity
// Store the storage variable inside a local variable
uint256 limit = storageVariableUint256;
for (uint256 i; i < limit; ++i) {
	// Body
}
```

See [Solidity 0.8.22 Release Announcement](https://soliditylang.org/blog/2023/10/25/solidity-0.8.22-release-announcement)

Reference:

[RareSkills Book of Solidity Gas Optimization](https://www.rareskills.io/post/gas-optimization#viewer-8rekj)

### Gas griefing

> What is gas griefing?

**Solution**

A gas griefing is a scenario when a transaction fails maliciously due to a lack of gas.

- It can happen when a user sends a transaction to a relayer or another smart contract with no enough gas to perform the different subcalls contains in the transaction.

- It can happen if the smart contract entrypoint (e.g. a relayer) does not check if there is enough gas to execute the transaction and do not check the return value of the external call.

Reference:

- [SWC-126/](https://swcregistry.io/docs/SWC-126/)
- [Smart contract gas griefing attack - The hidden danger](https://www.getsecureworld.com/blog/smart-contract-gas-griefing-attack-the-hidden-danger/)

### Function payable

> What is the effect on gas of making a function payable?

--- It will reduce the contract bytecode size and the amount of gas required to execute the function since the compiler does not check if ethers have been send with the call (call value).

It is possible to use this trick to save gas with the constructor and admin function, but not for all functions since these specifics functions will not be called by end-user, reducing the risk to send ethers by error.

It  is general not recommended to make all functions payable since it can generate unexpected behavior and it reduces the readability of the code.

Reference:

- [5. The RareSkills Book of Solidity Gas Optimization: 80+ Tips](https://www.rareskills.io/post/gas-optimization#viewer-aqto5)

### Types of storage 

> Describe the three types of storage gas costs.

Calldata =>  temporary data storage, read-only, the cheapest

memory => temporary data storage, read and write,  gas cost between calldata and storage

storage => permanent data storage on the blockchain, read and write, most costly type of storage

- **calldata**

The cheapest storage location since it is a read-only temporary data storage used to contain the function arguments passed from an external call. Therefore, It is not possible to modify the data inside a function or to use it with an internal function.

- **memory**

`memory` is a temporary data storage location that can be modified by a function, while `calldata` is a read-only temporary data storage location used to hold function arguments passed in from an external caller.

As for calldata, it is a temporary data storage, but it is writable and therefore cost most than the calldata storage. The opcode use is `mload.`

- **Storage** 

The most costly type of storage since the data are stored permanently on the blockchain. The opcode use is `sload`.

Reference: [When to use Storage vs. Memory vs. Calldata in Solidity](https://docs.alchemy.com/docs/when-to-use-storage-vs-memory-vs-calldata-in-solidity#:~:text=The%20key%20difference%20between%20memory,in%20from%20an%20external%20caller.)

### Multiplying and dividing

>  What is a gas efficient alternative to multiplying and dividing by a multiple of two?

We can use binary shift to do this because the shift right (`shr`) and shift left (`shl`) opcodes are cheaper than the opcodes used for the multiplication and division.
Respectively, the binary shift opcodes cost 3 against 5 for the `mul` and `div` opcode.
$$
10 * 2 = 10 << 1
$$


$$
10 \div 2 = 10 >> 1
$$

Reference: [The RareSkills Book of Solidity Gas Optimization: 80+ Tips](https://www.rareskills.io/post/gas-optimization#viewer-cvebl)

### EIP-1559-BASEFEE 

> How does Ethereum determine the BASEFEE in EIP-1559?

--- The base fee depends of the network activity / congestion according to a fomula. 

For example, if `x`, the % of the block filling

x == 50% full => unchanged

x == 100% full => increase by the maxium (12.5%)

50 < x < 100% => increase by less than 12.5%

x == 0% full (empty block) => decrease by less than 12.5%

Reference: [blocknative.com - A Definitive Guide to Ethereum EIP-1559 Gas Fee Calculations: Base Fee, Priority Fee, Max Fee](https://www.blocknative.com/blog/eip-1559-fees)

### Cold and warm read

>  What is the difference between a cold read and a warm read?

This two terms appear inside the [yellow paper](https://ethereum.github.io/yellowpaper/paper.pdf) regarding the gas cost.

The first time a storage variable is read is called a *cold* access and the second time, it is a *warm* access and it is cheaper.

In any case, the most cheapest solution if you have to read several time a storage variable is to cache the variable in memory, which will be cheaper than a *warm read*.

References:

- [Cold access VS Warm access - Gas Cost Question](https://ethereum.stackexchange.com/questions/149658/cold-access-vs-warm-access-gas-cost-question)
- [coinsbench.com - Comprehensive Guide: Tips and Tricks for Gas Optimization in Solidity](https://coinsbench.com/comprehensive-guide-tips-and-tricks-for-gas-optimization-in-solidity-5380db734404)

### Packed variable

>  How large a uint can be packed with an address in one slot?

A slot contains 32 bytes and an address already takes 20 bytes. Thus there are 12 bytes (= 96 bits) which are still free in this slot.

You can pack an `uint96` with an address in the same slot.

### Gas refund

> Which operations give a partial refund of gas

--- With [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529), `SSTORE` is the only operation that potentially provides a gas refund.

The refund is given (added into refund counter) when the storage value is set to zero from non-zero.

Reference: [Appendix - Dynamic Gas Costs](https://github.com/wolflo/evm-opcodes/blob/main/gas.md#a0-3-gas-refunds), [How to clear storage and get incentivized by Ethereum Blockchain ?](https://www.zaryabs.com/clear-storage-and-get-incentivized-by-ethereum-blockchain/)

Remark:

Initially, the operation self-destruct offered a refund of gas but this is no longer the case since the introduction of [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529)(London fork) which has removed this refund.

## Proxy

If you want to build a contract for a proxy architecture, I made a summary of the most important points to think about: [Programming proxy contracts with OpenZeppelin - Summary](https://rya-sge.github.io/access-denied/2022/10/31/proxy-contract-summary/)

### Storage collision 

>  What is a storage collision in a proxy contract?

- Storage collision between the proxy and the implementation contract

--- A storage collision happens when a proxy and its implementation use the same slot to store a value. As a result, when the implementation contract writes to update its variable, it will overwrite in reality the variable used by the proxy.

A solution, used by OpenZeppelin, is to "randomize" slot positions in the proxy’s storage

See [openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies)

- Storage collision between two implementations

In this case, a new implementation overwrites a variable from the previous implementation when an upgrade is performed

See [docs.openzeppelin.com/upgrades-plugins/1.x/proxies#storage-collisions-between-implementation-versions](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#storage-collisions-between-implementation-versions)

### Function selector clash 

> What is a function selector clash in a proxy and how does it happen?

A function selector clash happens when two functions have the same 4-byte identifiers.

This identifier depends on the name and arity of the function,

--- In the case of a proxy, and plus particularly of a transparent proxy, a same function with the same arguments can be defined in the proxy and its implementation resulting in a function clash.

In this scenario, we have to know if the sender tries to call the function defined in the proxy or the function defines in its implementation.

The solution implemented by the OpenZeppelin team is to use a proxy admin to control the proxy. 

- If the admin calls the proxy, the call is not delegate and the function called is the function defined in the proxy. 
- If the call came not from the admin, the call will be delegate to the implementation contract.

See [docs.openzeppelin.com/upgrades-plugins/1.x/proxies#transparent-proxies-and-function-clashes](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#transparent-proxies-and-function-clashes)

### Upgradeable contracts constructor

>  Why shouldn’t upgradeable contracts use the constructor?

If variables are initialied inside the constructor, the proxy has no way to see these values since :

- The constructor is not stored in the runtime bytecode, but only in the creation bytecode.
- The implementation contract is not deployed in the context of the proxy.

The solution is to use a public `initialize` function to initialize the proxy with the different values for each variable.

One exception to this is for immutable variable. Since this value is stored in the contract bytecode instead of the contract storage, you can use and initialize an immutable inside the constructor of the implementation contract

See [docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat)

### UUPS and the Transparent Upgradeable Proxy

> What is the difference between UUPS and the Transparent Upgradeable Proxy pattern?

Contrary to the `Diamond` or the `Beacon` proxy, these two interfaces use the same system to delegate call and know the implementation.

But they have a big difference in the method to upgrade the implementation.

With the `Transparent` Proxy, the function to perform the upgrade is contained in the proxy, not the implementation.

While in the UUPS, the function is contained in the implementation contract. 

This architecture makes the proxy cheaper, but can be more riskier because :

- If you upgrade your proxy with a new implementation where the upgrade function does not exist, the proxy can not longer be upgraded.
-  Several vulnerabilities have targeted UUPS proxy where a `self destruct` function was available but not protected in the implementation contract...With the next Ethereum upgrade Dencun (2024) self destruct can no longer destroy a contract but the risk remains if others critical functions are present, see [Wormhole Uninitialized Proxy Bugfix Review](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a).

Reference:  [Proxy Patterns For Upgradeability Of Solidity Contracts: Transparent vs UUPS Proxies](https://mirror.xyz/0xB38709B8198d147cc9Ff9C133838a044d78B064B/M7oTptQkBGXxox-tk9VJjL66E1V8BUF0GF79MMK4YG0)

### Delegatecall

 **Self Destructed**

> a) If a contract delegatecalls an empty address or an implementation that was previously self-destructed, what happens? 
> b) What if it is a regular call instead of a delegatecall?

**Question A**

--- If a contract delegatecalls to a self-destructed implementation, **the delegatecall will return a success**.

The reason is because the address still exists,  even if the storage and the funds/balance have been cleared.

If it is the zero address, I am not totally sure, but I think it returns also a success, see this [question on stackoverflow](https://stackoverflow.com/questions/70178516/why-assembly-delegatecall-returns-1-instead-of-0-when-calling-zero-0x000).

If the call is performed to an External Owned Account (EOA),  since this is not a contract, there is no code and the call will returne `True`

For information, `DELEGATECALL`pushes 1 on the stack in case of success, and pushes 0 on the stack in case of an error.

Reference:

- [Understanding Contract Delegation in Solidity: Handling Selfdestruct Scenarios](https://medium.com/@solidity101/understanding-contract-delegation-in-solidity-handling-selfdestruct-scenarios-%EF%B8%8F-37fe2f4198ee)
- [OpenZeppelin - Proxy.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/192e873fcb5b1f6b4b9efc177be231926e2280d2/contracts/proxy/Proxy.sol#L31)
- [Why is delegatecall returning 0 and erroring?](https://ethereum.stackexchange.com/questions/107591/why-is-delegatecall-returning-0-and-erroring)
- [Understanding delegatecall And How to Use It Safely](https://eip2535diamonds.substack.com/p/understanding-delegatecall-and-how)

**Question B**

For a call with `call`, if it is the address 0, the call will return a success. You can test this behavior with Foundry.

```solidity
address _address = address(0);
(bool success, bytes memory data) = _address.call{
gas: 5000
}(abi.encodeWithSignature("foo(string,uint256)", "call foo", 123));
assertEq(success, true);
```

For a self destructed contract, the call will also return `true` but will not do anything since the code has been removed.

Reference:

- [Solidity by Example - Call](https://solidity-by-example.org/call/)
- [Solidity: A Small Test of the Self-Destruct Operation](https://betterprogramming.pub/solidity-what-happens-with-selfdestruct-f337fcaa58a7)

**Balance**

> If a proxy makes a delegatecall to A, and A does address(this).balance, whose balance is returned, the proxy's or A?

The returned balance is the proxy balance since the call is executed in the context of the proxy.

**Revert**

> If a delegatecall is made to a function that reverts, what does the delegatecall do?

Delegatecall will return false, it does not revert.

You have to manage this case in your contract. For example, [OpenZeppelin](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/192e873fcb5b1f6b4b9efc177be231926e2280d2/contracts/proxy/Proxy.sol#L31) for their proxy contract reverts in case of an error

```solidity
switch result
	// delegatecall returns 0 on error.
	case 0 {
		revert(0, returndatasize())
	}
```

References: [OpenZeppelin - Proxy](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/192e873fcb5b1f6b4b9efc177be231926e2280d2/contracts/proxy/Proxy.sol#L31), [Preventing unwanted delegate call](https://dev.to/moyedx3/preventing-unwanted-delegate-call-1dj9)

**Immutable variable**

> If a delegatecall is made to a function that reads from an immutable variable, what will the value be?

An immutable variable is stored in the bytecode of the implementation contract and it is this value which will be read.

With a proxy, you can change/upgrade the value of an immutable variable by upgrading to a new implementation.

## Token 

### Rebasing token

>  What is a rebasing token?

A rebase, or elastic, token, is a token where the supply and the user's balance is adjusted periodically

Use case :

- Algorithmic stablecoin to maintain a peg to another asset. The number of token in circulation are adjusted through the rebase mechanism depending of the token price related to the asset peg. 

Example: [Ampleforth (AMPL)](https://www.coindesk.com/tech/2021/04/21/ampleforth-is-giving-governance-tokens-to-every-wallet-that-ever-held-ampl/)

- Liquid staking Token (LST) : the user's balance is rebased to represent the revenue issue from the staking.

Example: [Lido (stETH)](https://docs.lido.fi/contracts/lido/)

On UniswapV2, this type of token is a problem because the uniswap router contract does not know when a rebasing happen and it makes the pair balance unbalanced, see [uniswap docs](https://docs.uniswap.org/contracts/v2/reference/smart-contracts/common-errors#rebasing-tokens). As a result, rebasing tokens will succeed in pool creation and swapping, but liquidity providers will bear the loss of a negative rebase when their position becomes active, with no way to recover the loss, see [uniswap docs](https://docs.uniswap.org/concepts/protocol/integration-issues#rebasing-tokens)

Global reference: [What Is a Rebase/Elastic Token?](https://www.coindesk.com/learn/what-is-a-rebaseelastic-token/https://www.coindesk.com/learn/what-is-a-rebaseelastic-token/)

### fee-on-transfer

> What is a fee-on-transfer token?

---A "Fee on Transfer" token is a token that  takes a percentage of internal commission upon transfer or trade. In other words, every time the token is transfered, a portion of the transfer amount is taken, e.g. to burn or sent to another address as a fee.

Reference: [1inch - What is a Fee on Transfer token?](https://help.1inch.io/en/articles/5651059-what-is-a-fee-on-transfer-token)

On UniswapV2, to swap this type of token, you have to call a specific function which takes in consideration this fee to compute the invariant, see [uniswap docs](https://docs.uniswap.org/contracts/v2/reference/smart-contracts/common-errors#fee-on-transfer-tokens).



### Token standard

#### ERC-777 

>  What danger do ERC-777 tokens pose?

[EIP reference](https://eips.ethereum.org/EIPS/eip-777)

--ERC-777 allows a sender of a transaction specified a contract to call, which can be used to perform reentrancy attack.

*From the EIP:* 

- The holder can “authorize” and “revoke” operators which can send tokens on their behalf
- When sending tokens, the token contract MUST call the `tokensToSend` hook of the *holder* if the *holder* registers an `ERC777TokensSender` implementation via [ERC-1820](https://eips.ethereum.org/EIPS/eip-1820).
- The token contract MUST call the `tokensReceived` hook of the *recipient* if the *recipient* registers an `ERC777TokensRecipient` implementation via [ERC-1820](https://eips.ethereum.org/EIPS/eip-1820).

This contract is determined through a registry.

*What are the possible attacks/danger ?*

- An attacker can perform a reentrancy attack by setting a malicious contract as a hook when the attacker sends or receives tokens. For example to re-enter a `withdraw`function, which will send tokens to the attacker address. The token ERC-777 has to protect against it by adding a nonReentrant` modifier` to callbacks: `_callTokensToSend ` and `_callTokensReceived`. See [ERC-777 callback issue](https://consensys.io/diligence/audits/2020/01/skale-token/#erc-777-callback-issue)
- If a target contract allows making arbitrary calls to any address with any data, an attacker can leverage this to set a malicious contract to call each time the target contract receives or send tokens (see [One more problem with ERC-777](https://mixbytes.io/blog/one-more-problem-with-erc777)). The attacker can choose for example to revert each time resulting in an attack dos.

Reference: [A Dive With ERC-777 And Risk Mitigations](https://medium.com/coinmonks/a-dive-with-erc-777-and-risk-mitigations-9f3ffcac0f78), [ERC777 implementation and security clarifications](https://github.com/OpenZeppelin/openzeppelin-contracts/issues/1749), [ERC-777 callback issue](https://consensys.io/diligence/audits/2020/01/skale-token/#erc-777-callback-issue)

#### ERC-721

> How does safeMint differ from mint in the OpenZeppelin ERC721 implementation? 

[EIP reference](https://eips.ethereum.org/EIPS/eip-721)

The safeMint function will check if the destination contract can support ERC-721 token. If not, the call will revert

#### ERC-721A

> What does ERC-721A do to reduce mint costs? What is the tradeoff?

[Offical website](https://www.erc721a.org/)

Enable minting multiple NFTs for essentially the same cost of minting a single NFT.

- Optimization 1 - Removing duplicate storage from OpenZeppelin’s (OZ) ERC721Enumerable
- Optimization 2 - updating the owner’s balance once per batch mint request, instead of per minted NFT
- Optimization 3 - updating the owner data once per batch mint request, instead of per minted NFT

Reference: [www.erc721a.org](https://www.erc721a.org), [www.azuki.com/erc721a](https://www.azuki.com/erc721a)

We can see these difference by comparing the function mint from OpenZeppelin and the function mint from ERC-721A. We can see for ERC-721A there is no `tokenId` and a new parameter `quantity` has been added in the parameters of the function.

- [ERC-721 OpenZeppelin](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol)

```solidity
 function _mint(address to, uint256 tokenId) internal {
```

- [ERC-721A](https://github.com/chiru-labs/ERC721A/blob/main/contracts/ERC721A.sol#L751C4-L805C6)

```solidity
function _mint(address to, uint256 quantity) internal virtual
```

## Security

### Transfer and send

> What is the difference between transfer and send? Why should they not be used?

- **transfer**

The receiving smart contract should have a **fallback** function defined or else the transfer call will throw an **error**. There is a gas limit of **2300 gas**, which is enough to complete the transfer operation. Initially, this gas limit was put in place to prevent **reentrancy attacks** since there is no enough gas to perform this attack.

- **send** 

 It works in a similar way as to transfer call and has also a gas limit of **2300 gas** . But contrary to `transfer`, It returns the status as a **boolean**.

**Recommendation**

According to [immunebytes.com](https://www.immunebytes.com/blog/transfer-in-solidity-why-you-should-stop-using-it/), it is not recommended to use the function `transfer` since the modifier `.gas()` has been added and this function takes a hard dependency on gas costs by forwarding a fixed amount of gas i.e., 2300. 

[Consensys](https://consensys.io/diligence/blog/2019/09/stop-using-soliditys-transfer-now/) recommends also to avoid `transfer`, and also `send`, for the same reasons and to use `call`instead.

`Call` will forward all gas (if not set) and returns a boolean. It is necessary to protect the call against re-entrancy attack

Example from [Solidity by Example](https://solidity-by-example.org/sending-ether/)

```solidity
 function sendViaCall(address payable _to) public payable {
        // Call returns a boolean value indicating success or failure.
        // This is the current recommended method to use.
        (bool sent, bytes memory data) = _to.call{value: msg.value}("");
        require(sent, "Failed to send Ether");
    }
```

**References:**

1. [coinmonks - Solidity — transfer vs send vs call function](https://medium.com/coinmonks/solidity-transfer-vs-send-vs-call-function-64c92cfc878a)

2. [immunebytes.com - Transfer in Solidity: Why you should STOP using it?](https://www.immunebytes.com/blog/transfer-in-solidity-why-you-should-stop-using-it/)

3. [Stop Using Solidity's transfer() Now](https://consensys.io/diligence/blog/2019/09/stop-using-soliditys-transfer-now/)

4. [Solidity by Example - Sending Ether](https://solidity-by-example.org/sending-ether/)

   

### Front-running

**Definition**

> What is frontrunning?

--- A front-run happens when an attacker sends and validates by the nodes a transaction before a target transaction, for example by paying a higher gas fee.

When a transaction is waiting in the mempool to be valided, an "attacker" use the information contained in this transaction to makes its own transaction beneficial to him and pays a higher gas fee in order to validate its transaction before the first one. 

Reference:

- [Front-Running Attacks in Blockchain: The Complete Guide](https://www.immunebytes.com/blog/front-running-attacks-in-blockchain-the-complete-guide/)
- [Front Running and Sandwich Attack Explained - QuillAudits](https://quillaudits.medium.com/front-running-and-sandwich-attack-explained-quillaudits-de1e8ff3356d)

**Sandwich attack**

> What is a sandwich attack?

--- A sandwich attack happens when an attacker, generally a bot, sends a transaction before and after a target transaction.

In general the goal is to take advantage of price movements to make a profit to the detriment of the issuer of the target transaction.

For example, if the target transaction is a buy order of a token C. The attacker will buy tokens before the transaction, making the price to move up, then selling the bought tokens after the target transaction. Thus we have this sequence:

1) Attacker buys token X, prices moves up
2) Target buy tokens to an higher price than expected
3) Attacker makes a profit by selling the tokens

There are two mains methods to protect against a sandwich attack

- The slippage parameter to define a range of price 
- Use [flashbot](https://www.flashbots.net/) to avoid the mempool.

References:

[CharlesWangP - Thread](https://twitter.com/CharlesWangP/status/1743658885926228152), [Lecture 13.7: Sandwich Attacks](https://www.youtube.com/watch?v=Om6Fqf7lRKQ&list=PLS01nW3RtgopsMpAceFwuyLKH42VW0Nw9&index=7), [Modern MEV sandwich attacks on Ethereum routers](https://mirror.xyz/totlsota.eth/9JaNkZ1XQfQD6Y79aLYHC_kb_dSBoJ2JYiag5BuGGM8)



###  abi.encodePacked - Vulnerability

>  Under what circumstances could abi.encodePacked create a vulnerability?

For different arguments passed, abi.encodePacked will return the same value.

The [solidity documentation](https://docs.soliditylang.org/en/v0.8.24/abi-spec.html#non-standard-packed-mode) provides the following example: 

```solidity
abi.encodePacked("a", "bc") == abi.encodePacked("ab", "c")
```

If this return value is hashed to verify a signature or to check the arguments contents, an attacker can change the order of the arguments and still have valid data or signature associated.

In this example form, from this [1.article](https://scsfg.io/hackers/abi-hash-collisions/), an attacker present as a regular user can put its address in the privileged array.

```solidity
    function claimRewards(address[] calldata privileged, address[] calldata regular) external {
        bytes32 payoutKey = keccak256(abi.encodePacked(privileged, regular));
        require(allowedPayouts[payoutKey], "Unauthorized claim");
        allowedPayouts[payoutKey] = false;
        _payout(privileged, premiumPayout);
        _payout(regular, regularPayout);
    }
```

In this another example from this [2. article](https://medium.com/@0xkaden/new-smart-contract-weakness-hash-collisions-with-multiple-variable-length-arguments-dc7b9c84e493) , if a valid signature already exists in a transaction on the blockchain, a `regularUser` can call again the function with the same signature, but by putting its address in the array `admins`.

```solidity
 function addUsers(
        address[] calldata admins,
        address[] calldata regularUsers,
        bytes calldata signature
    )
        external
    {
        if (!isAdmin[msg.sender]) {
            // Allow calls to be relayed with an admin's signature.
            bytes32 hash = keccak256(abi.encodePacked(admins, regularUsers));
            address signer = hash.toEthSignedMessageHash().recover(signature);
            require(isAdmin[signer], "Only admins can add users.");
        }
        for (uint256 i = 0; i < admins.length; i++) {
            isAdmin[admins[i]] = true;
        }
        for (uint256 i = 0; i < regularUsers.length; i++) {
            isRegularUser[regularUsers[i]] = true;
        }
    }
```

Reference:

- [1. New Smart Contract Weakness: Hash Collisions With Multiple Variable Length Arguments3](https://medium.com/@0xkaden/new-smart-contract-weakness-hash-collisions-with-multiple-variable-length-arguments-dc7b9c84e493)
- [2. scsfg.io - ABI Hash Collisions](https://scsfg.io/hackers/abi-hash-collisions/)

### Signature replay attack

> What is a signature replay attack?

A signature replay attack happens when a valid signature is used several times.

Generally, it happens because the smart contract does not verify if a signature has already been used.

See [solidity-by-example.org - signature-replay](https://solidity-by-example.org/hacks/signature-replay/)

### Commit-reveal scheme

> What is a commit-reveal scheme and when would you use it?

In a commitment scheme, the actors involved post (= commit) a value on the blockchain.  This value has the following propreties :

- It is not readable from others (hidden)
- It can be revealed later
- No one can change its value once commited.

This scheme is implemented through cryptographic algorithm and has two phases:

- A commit phase in which a value is chosen and specified;
- A reveal phase in which the value is revealed and checked.

This schema can be used to bid amounts or to play a game like Rock-paper-scissors (see next question) to keep the player's choice secret from others players.

Example of a commit struct, where `solutionHash`is compute off-chain by the sender as hash(msg.sender + solution + secret)

```solidity
struct Commit {
        bytes32 solutionHash;
        uint commitTime;
        bool revealed;
}
```

References:

- [Solidity by example - Front Running](https://solidity-by-example.org/hacks/front-running/)
- [Transaction Order Dependence (Front-running)](https://github.com/obheda12/Solidity-Security-Compendium/blob/main/days/day1.md)

### Rock-paper-scissors

> How would you design a game of rock-paper-scissors in a smart contract such that players cannot cheat?

--- You can use the *commit-reveal scheme* (see previous question).

Each player commit its choice under the form `hash(choice, salt)`

Once the two players have commit their choice, the two players call the function `reveal`with their salt.

The smart contract computes the hash with the salt, and can compare the choice of the two players to determine which players won.

References: [obheda12 - Transaction Order Dependence (Front-running)](https://github.com/obheda12/Solidity-Security-Compendium/blob/main/days/day1.md), [BCAM - Commit Reveal](https://blockchain-academy.hs-mittweida.de/courses/solidity-coding-beginners-to-intermediate/lessons/solidity-11-coding-patterns/topic/commit-reveal/)



## Solidity Misc

###  ERC-165

> What is ERC-165 used for?

--- It is used to specify and retrieve a standard ERC. It is useful to know if a contract implements an interface.

For example, it is required by the standard [ERC-721](https://eips.ethereum.org/EIPS/eip-721) but not by [ERC-20](https://eips.ethereum.org/EIPS/eip-20).

See [eip-165](https://eips.ethereum.org/EIPS/eip-165)

### Measure time in Solidity

> What keywords are provided in Solidity to measure time?

--- Suffixes like `seconds`, `minutes`, `hours`, `days` and `weeks` after literal numbers can be used to specify units of **time** where seconds are the base unit.

- `block.timestamp` (`uint`): current block **time**stamp as seconds since unix epoch

The current block **time**stamp must be strictly larger than the timestamp of the last block. 

According to the documentation, the only guarantee is that it will be somewhere between the timestamps of two consecutive blocks in the canonical chain. Nevertheless, I think this point concerned Ethereum before the merge (see next question).

References: [docs.soliditylang.org - time Units](https://docs.soliditylang.org/en/v0.8.23/units-and-global-variables.html#time-units), [rareskills.io - Solidity Coding Standards](https://www.rareskills.io/post/solidity-style-guide)

> What changed with block.timestamp before and after proof of stake? 

--- The post-Merge consensus on valid blocks is pre-determined timestamps that are not modifiable.

Each slot has an expected timestamp, and a block without that exact  timestamp is not valid. The block after the beacon chain genesis is  expected to have a timestamp exactly 12 seconds after the genesis block. The block after it 12 seconds after, and so forth. See the [spec](https://github.com/ethereum/consensus-specs/blob/9839ed49346a85f95af4f8b0cb9c4d98b2308af8/configs/mainnet.yaml#L60) 

Reference: [Miner-modifiability of block timestamp after the Merge](https://ethereum.stackexchange.com/questions/135445/miner-modifiability-of-block-timestamp-after-the-merge)

### Floating point arithmetic

> Why doesn't Solidity support floating point arithmetic?

Ethereum blockchain is deterministic which ensures that smart contracts always produce the same output for the same input.

--- With floating point number, you can have a loss of precision and a difference between node computation which is not compatible with the deterministic nature of Ethereum.

References: [stackoverflow - Usage of Float Numbers in Smart contract](https://ethereum.stackexchange.com/questions/52962/usage-of-float-numbers-in-smart-contract), [stackoverflow - Why are there no decimal numbers in Solidity?](https://stackoverflow.com/questions/72623122/why-are-there-no-decimal-numbers-in-solidity)



### Abi.encode and abi.encodePacked?

> What is the difference between abi.encode and abi.encodePacked?

**abi.encode**

`abi.encode(...) returns (bytes memory)`

[ABI](https://docs.soliditylang.org/en/v0.8.24/abi-spec.html#abi)-encodes the given arguments. 

- The arguments will be passed as specified in the ABI specification
- Useful to perform a call to a contract

**abi.encodePacked**

`abi.encodePacked(...) returns (bytes memory)`

Perform [packed encoding](https://docs.soliditylang.org/en/v0.8.24/abi-spec.html#abi-packed-mode) of the given arguments. Note that this encoding can be ambiguous!

The rules are the following

- types shorter than 32 bytes are concatenated directly, without padding or sign extension (contrary to `abi.encode`)
- dynamic types are encoded in-place and without the length.
- array elements are padded, but still encoded in-place

Furthermore, structs as well as nested arrays are not supported.

In some cases, using `abi.encodePacked` can be dangerous (see section security / abi.encodePacked - vulnerability)

Reference: [solidity doc - ABI Encoding and Decoding Functions](https://docs.soliditylang.org/en/v0.8.24/cheatsheet.html#abi-encoding-and-decoding-functions), [Why are there two methods encoding arguments? "abi.encode" and "abi.encodePacked"](https://ethereum.stackexchange.com/questions/91826/why-are-there-two-methods-encoding-arguments-abi-encode-and-abi-encodepacked)

### Uint

> uint8, uint32, uint64, uint128, uint256 are all valid uint sizes. Are there others?

Yes, all`uint8` to `uint256` in steps of `8` (unsigned of 8 up to 256 bits)

For example, there is also uint16, uint24, uint40...

Reference: [www.velvetshark.com - Max values for each uint in Solidity, from uint8 to uint256](https://www.velvetshark.com/max-int-values-in-solidity), [docs.soliditylang.org - integers](https://docs.soliditylang.org/en/latest/types.html#integers)

### Interface - Function modifiers

> What function modifiers are valid for interfaces?

 valid function modifiers for interfaces are 

`pure, view, external, override, payable`

- It is not possible to use the modifiers *internal* or `private`. A function interface has to be `external`. The visibility restriction can be perform on the implementation.
- It is not possible to use the modifier `nonpayable` too
- You can use the `pure` or `view` keyword, in this case, the function implementation has to be `view` or `pure`. Same behavior with `payable`.

Reference: [twitter.com/RareSkills_io/status/1638556209828737025](https://twitter.com/RareSkills_io/status/1638556209828737025) + tested with Visual Studio Code.

###  Function - memory and calldata

> What is the difference between memory and calldata in a function argument?

See Section `Gas-Type of storage`

`memory` is a temporary data storage location that can be modified by a function, while `calldata` is a read-only temporary data storage location used to hold function arguments passed in from an external caller. A `calldata`argument can not be used by an `internal` function. 

### Free memory pointer

> What is the free memory pointer and where is it stored?

It is stored in the slot `0x40`. This pointer contains the emplacement in memory which is free. Initially, it points to the address `0x80`

See [docs.soliditylang - Layout in Memory](https://docs.soliditylang.org/en/latest/internals/layout_in_memory.html) && [0xpranay - Solidity Internals](https://0xpranay.github.io/solidity-notes/Internals.html)

### Solidity style Guide

#### Functions ordered

> According to the solidity style guide, how should functions be ordered?$

Functions should be grouped according to their visibility and ordered:

- constructor
- receive function (if exists)
- fallback function (if exists)
- external
- public
- internal
- private

Within a grouping, place the `view` and `pure` functions last.

Example from the documentation

```solidity
// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;
contract A {
    constructor() {
        // ...
    }

    receive() external payable {
        // ...
    }

    fallback() external {
        // ...
    }

    // External functions
    // ...

    // External functions that are view
    // ...

    // External functions that are pure
    // ...

    // Public functions
    // ...

    // Internal functions
    // ...

    // Private functions
    // ...
}
```

Reference: [docs.soliditylang.org - order-of-functions](https://docs.soliditylang.org/en/latest/style-guide.html#order-of-functions)

#### Modifiers ordered

> According to the solidity style guide, how should function modifiers be ordered?

The modifier order for a function should be:

1. Visibility
2. Mutability
3. Virtual
4. Override
5. Custom modifiers

Example:

```solidity
function balance(uint from) public view override returns (uint)  {
    return balanceOf[from];
}

function shutdown() public onlyOwner {
    selfdestruct(owner);
}
```

Reference: [docs.soliditylang.org - function-declaration](https://docs.soliditylang.org/en/latest/style-guide.html#function-declaration)

## Further reading

You can find different answers to these questions in the following resources

- [github.com/typicalHuman/solidity-interview-questions?tab=readme-ov-file#medium](https://github.com/typicalHuman/solidity-interview-questions?tab=readme-ov-file#medium)

