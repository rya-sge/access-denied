---
layout: post
title: Cross-chain tokens Standard (ERC-7281, xERC20) - Overview
date:  2025-05-07
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: blockchain solidity ethereum
tags: cross-chain erc20 erc7281 erc7802
description: This article presents the different standards to represent cross-chain token on Ethereum and EVM blockchain, notably ERC-7281(xERC20) & ERC-7802
image: /assets/article/blockchain/ethereum/cross-chain-token/2025-05-07-cross-chain-token-overview-mindmap.png
isMath: false
---

This article presents the different standards to represent cross-chain token on Ethereum and EVM blockchain.

[TOC]

## What you need to know first

The three standards below assume a few bridge and EVM mechanisms that the article uses without explaining them.

- **Lock-and-mint and burn-and-mint bridges**: a lock-and-mint bridge locks the original tokens on the source chain and mints a representation on the destination chain. A burn-and-mint bridge destroys the tokens on the source chain and mints the same amount on the destination chain, which is the model all three standards expose through their `mint`/`burn` functions; see [Cross-Chain Bridge Threat Model - Assets, Trust Boundaries, STRIDE and Threat Register]({{site.url_complet}}/2026/07/31/cross-chain-bridge-threat-model/).
- **Bridged token fragmentation**: when each bridge issues its own wrapped version of a token, the destination chain ends up with several representations that are not interchangeable. This is the fungibility problem that ERC-7281 sets out to fix.
- **Mint and burn access control**: a token that lets outside contracts call `mint` and `burn` must restrict who may call them. Here the token issuer keeps an allowlist of bridges, and a compromised bridge can only mint up to the limit it was given.
- **Rate limit**: a cap on how much can be minted or burned over time. In ERC-7281 the current limit of a bridge refills at `ratePerSecond` up to its `maxLimit`, so a burst of minting drains it and waiting restores it.
- **ERC-165 interface detection**: a contract implementing ERC-165 exposes `supportsInterface(bytes4)`, which tells callers whether it implements a given interface. `IERC7802` extends `IERC165`, so a bridge can check that a token supports `crosschainMint` and `crosschainBurn` before calling them.
- **OP Stack predeploys and the Superchain**: the Superchain is the set of chains built on Optimism's OP Stack. Predeploys are system contracts placed at fixed addresses starting with `0x4200...` on every OP Stack chain, which is why `SuperchainTokenBridge` has the same address everywhere.
- **Same-address deployment**: `CREATE2` computes a contract address from the deployer, a salt and the hash of the init code, so the same deployment gives the same address on every EVM chain. SuperchainERC20 relies on this, because its bridge mints on the destination chain at the token's own address; see [Nonce Management and CREATE2 in ERC-4337 Smart Wallets]({{site.url_complet}}/2026/02/17/nonce-management-create2-smart-wallets-erc4337/).

## ERC-7281 (xERC20): Sovereign Bridged Tokens

> [ERC specification (draft in the closed pull request)](https://github.com/ethereum/ERCs/blob/052a0c89d98d6042617874caef323f415327f1ee/ERCS/erc-7281.md), [Pull Request](https://github.com/ethereum/ERCs/pull/89)
>
> Status: Draft
>
> [ethereum magicians](https://ethereum-magicians.org/t/erc-7281-sovereign-bridged-tokens/14979)
>
> Implementation: [defi-wonderland - crosschainERC20](https://github.com/defi-wonderland/crosschainERC20)

EIP-7281 (aka xERC20) proposes a minimal extension to ERC-20 to fix problems with token sovereignty, fungibility, and security across domains.

The proposal introduces:

1. A burn/mint interface to the token callable by bridges allowlisted by the token issuer.
2. Configurable rate limits for the above
3. A “Lockbox”: a simple wrapper contract that consolidates home chain token liquidity and provides a straightforward adoption path for existing ERC20s.

### Interface

```solidity
interface IXERC20 {
  /**
   * @notice Emits when a lockbox is set
   *
   * @param _lockbox The address of the lockbox
   */

  event LockboxSet(address _lockbox);

  /**
   * @notice Emits when a limit is set
   *
   * @param _mintingLimit The updated minting limit we are setting to the bridge
   * @param _burningLimit The updated burning limit we are setting to the bridge
   * @param _bridge The address of the bridge we are setting the limit too
   */

  event BridgeLimitsSet(uint256 _mintingLimit, uint256 _burningLimit, address indexed _bridge);

  /**
   * @notice Reverts when a user with too low of a limit tries to call mint/burn
   */

  error IXERC20_NotHighEnoughLimits();

  struct Bridge {
    BridgeParameters minterParams;
    BridgeParameters burnerParams;
  }

  struct BridgeParameters {
    uint256 timestamp;
    uint256 ratePerSecond;
    uint256 maxLimit;
    uint256 currentLimit;
  }

  /**
   * @notice Sets the lockbox address
   *
   * @param _lockbox The address of the lockbox (0x0 if no lockbox)
   */

  function setLockbox(address _lockbox) external;

  /**
   * @notice Updates the limits of any bridge
   * @dev Can only be called by the owner
   * @param _mintingLimit The updated minting limit we are setting to the bridge
   * @param _burningLimit The updated burning limit we are setting to the bridge
   * @param _bridge The address of the bridge we are setting the limits too
   */
  function setLimits(address _bridge, uint256 _mintingLimit, uint256 _burningLimit) external;

  /**
   * @notice Returns the max limit of a bridge
   *
   * @param _bridge The bridge we are viewing the limits of
   *  @return _limit The limit the bridge has
   */
  function mintingMaxLimitOf(address _bridge) external view returns (uint256 _limit);

  /**
   * @notice Returns the max limit of a bridge
   *
   * @param _bridge the bridge we are viewing the limits of
   * @return _limit The limit the bridge has
   */

  function burningMaxLimitOf(address _bridge) external view returns (uint256 _limit);

  /**
   * @notice Returns the current limit of a bridge
   *
   * @param _bridge The bridge we are viewing the limits of
   * @return _limit The limit the bridge has
   */

  function mintingCurrentLimitOf(address _bridge) external view returns (uint256 _limit);

  /**
   * @notice Returns the current limit of a bridge
   *
   * @param _bridge the bridge we are viewing the limits of
   * @return _limit The limit the bridge has
   */

  function burningCurrentLimitOf(address _bridge) external view returns (uint256 _limit);

  /**
   * @notice Mints tokens for a user
   * @dev Can only be called by a bridge
   * @param _user The address of the user who needs tokens minted
   * @param _amount The amount of tokens being minted
   */

  function mint(address _user, uint256 _amount) external;

  /**
   * @notice Burns tokens for a user
   * @dev Can only be called by a bridge
   * @param _user The address of the user who needs tokens burned
   * @param _amount The amount of tokens being burned
   */

  function burn(address _user, uint256 _amount) external;
}
```

## ERC-7802: Token With Mint/Burn Access Across Chains

> [ERC specification](https://eips.ethereum.org/EIPS/eip-7802)
>
> Status: Draft
>
> [ethereum magicians](https://ethereum-magicians.org/t/erc-7802-crosschain-token-interface/21508)
>
> Implementation: [defi-wonderland - crosschainERC20](https://github.com/defi-wonderland/crosschainERC20)

This standard introduces a minimal and extensible interface, `IERC7802`, for tokens to enable standardized crosschain communication. The interface consists of two functions, `crosschainMint` and `crosschainBurn`, which allow authorized bridge contracts to mint and burn token representations during crosschain transfers. 

These functions serve as the entry points for bridge logic, enabling consistent handling of token supply across chains.

The interface also defines two standardized events, `CrosschainMint` and `CrosschainBurn`, which emit metadata, including the target address, token amount, and caller. 

These events facilitate deterministic indexing and monitoring of crosschain activities by off-chain agents, such as indexers, analytics tools, and auditors.

`IERC7802` is intentionally small, so it adds little implementation overhead. Additional features can be layered on top without modifying the base interface, for example mint and burn limits, transfer fees, or bridge-specific access control.

### Optimism superchain ERC20

The [`SuperchainERC20`](https://github.com/ethereum-optimism/optimism/blob/develop/packages/contracts-bedrock/src/L2/SuperchainERC20.sol) contract implements [ERC-7802](https://ethereum-magicians.org/t/erc-7802-crosschain-token-interface/21508) to enable asset interoperability within the Superchain.

Application developers must complete two steps to make their tokens compatible with `SuperchainERC20`. 

Setting this up in advance ensures tokens will benefit from interop when it becomes available.

- Grant permission to `SuperchainTokenBridge` (address `0x4200000000000000000000000000000000000028`) to call `crosschainMint` and `crosschainBurn`. 
  - If you are using [`SuperchainERC20`](https://github.com/ethereum-optimism/optimism/blob/develop/packages/contracts-bedrock/src/L2/SuperchainERC20.sol) this is already done for you.
- Deploy the `SuperchainERC20` at the same address on every chain in the Superchain where you want your token to be available. If you do not deploy the contract to a specific destination chain, users will be unable to successfully move their tokens to that chain.

See [Optimism superchain ERC20](https://docs.optimism.io/interop/superchain-erc20)

### Interfaces

```solidity
interface IERC7802 is IERC165 {
    /// @notice Emitted when a crosschain transfer mints tokens.
    /// @param to       Address of the account tokens are being minted for.
    /// @param amount   Amount of tokens minted.
    /// @param sender   Address of the caller (msg.sender) who invoked crosschainMint.
    event CrosschainMint(address indexed to, uint256 amount, address indexed sender);

    /// @notice Emitted when a crosschain transfer burns tokens.
    /// @param from     Address of the account tokens are being burned from.
    /// @param amount   Amount of tokens burned.
    /// @param sender   Address of the caller (msg.sender) who invoked crosschainBurn.
    event CrosschainBurn(address indexed from, uint256 amount, address indexed sender);

    /// @notice Mint tokens through a crosschain transfer.
    /// @param _to     Address to mint tokens to.
    /// @param _amount Amount of tokens to mint.
    function crosschainMint(address _to, uint256 _amount) external;

    /// @notice Burn tokens through a crosschain transfer.
    /// @param _from   Address to burn tokens from.
    /// @param _amount Amount of tokens to burn.
    function crosschainBurn(address _from, uint256 _amount) external;
}
```

## ERC-7905 (minimal xERC20)

> Status: draft
>
> [GitHub PR](https://github.com/ethereum/ERCs/pull/961/)

The related ERC-7281 (XERC20) proposal encompasses Lockbox wrappers, structs, and extensive configuration functions, exceeding the minimal requirements for core interoperability. 

This ERC presents a streamlined, focused approach, providing the essential functionality for 'xERC20 native' fungible token interoperability.

```solidity
interface IERC7905 {
    /**
     * @notice Reverts when a bridge with too low of a limit tries to call mint/burn
     */
    error IXERC20_NotHighEnoughLimits();
    /**
     * @notice Returns the max limit of a minter
     *
     * @param _bridge The bridge we are viewing the limits of
     * @return _limit The limit the bridge has
     */
    function mintingMaxLimitOf(address _bridge) external view returns (uint256 _limit);
    /**
     * @notice Returns the max limit of a bridge
     *
     * @param _bridge the bridge we are viewing the limits of
     * @return _limit The limit the bridge has
     */
    function burningMaxLimitOf(address _bridge) external view returns (uint256 _limit);
    /**
     * @notice Returns the current limit of a minter
     *
     * @param _bridge The bridge we are viewing the limits of
     * @return _limit The limit the minter has
     */
    function mintingCurrentLimitOf(address _bridge) external view returns (uint256 _limit);
    /**
     * @notice Returns the current limit of a bridge
     *
     * @param _bridge the bridge we are viewing the limits of
     * @return _limit The limit the bridge has
     */
    function burningCurrentLimitOf(address _bridge) external view returns (uint256 _limit);
    /**
     * @notice Mints tokens for a user
     * @param _user The address of the user who needs tokens minted
     * @param _amount The amount of tokens being minted
     */
    function mint(address _user, uint256 _amount) external;
    /**
     * @notice Burns tokens for a user
     * @param _user The address of the user who needs tokens burned
     * @param _amount The amount of tokens being burned
     */
    function burn(address _user, uint256 _amount) external;
}
```

## Conclusion

The three standards address cross-chain token representation at different levels of scope. ERC-7281 (xERC20) gives the token issuer sovereignty over which bridges can mint or burn, with per-bridge rate limits and an optional Lockbox to wrap an existing ERC-20. ERC-7802 reduces the surface to a minimal `crosschainMint` / `crosschainBurn` interface intended as a common entry point for bridge logic, and is the basis for Optimism's `SuperchainERC20`. ERC-7905 keeps the xERC20 limit model but drops the Lockbox and configuration functions for a smaller footprint. All three are still at Draft status.

![Cross-chain token standards mindmap]({{site.url_complet}}/assets/article/blockchain/ethereum/cross-chain-token/2025-05-07-cross-chain-token-overview-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Cross-chain token** | A token whose supply can move between several chains while staying one asset for its holders. |
| **Bridge** | The contract that carries a token transfer from one chain to another, here by burning on the source chain and minting on the destination chain. |
| **Token sovereignty** | The issuer's control over which bridges may mint and burn its token, instead of each bridge deciding on its own representation. |
| **xERC20** | The name of the ERC-7281 token: an ERC-20 extended with a mint/burn interface for allowlisted bridges and per-bridge limits. |
| **Lockbox** | The ERC-7281 wrapper contract that holds the home-chain liquidity of an existing ERC-20 and issues the xERC20 against it. |
| **Home chain** | The chain where the original ERC-20 lives and where the Lockbox holds its liquidity. |
| **Minting limit / burning limit** | The amount a given bridge may mint or burn, set by the issuer with `setLimits` and read with `mintingMaxLimitOf` and `burningMaxLimitOf`. |
| **Current limit** | The amount a bridge can still mint or burn at a given moment, which refills over time at `ratePerSecond` up to the max limit. |
| **ERC-7802** | A minimal interface with only `crosschainMint`, `crosschainBurn` and their two events, as standard entry points for authorized bridges. |
| **`CrosschainMint` / `CrosschainBurn`** | The ERC-7802 events that record the target address, the amount and the caller, so off-chain indexers can follow cross-chain supply. |
| **SuperchainERC20** | Optimism's ERC-20 implementation of ERC-7802 for token transfers between Superchain chains. |
| **SuperchainTokenBridge** | The Optimism bridge at `0x4200000000000000000000000000000000000028` that must be allowed to call `crosschainMint` and `crosschainBurn`. |
| **ERC-7905** | A minimal xERC20 that keeps only `mint`, `burn` and the limit views, and drops the Lockbox and configuration functions of ERC-7281. |

## Frequently Asked Questions

**Q: What core problem does ERC-7281 (xERC20) try to solve?**

It addresses token sovereignty, fungibility, and security across chains. Rather than each bridge issuing its own incompatible wrapped representation, xERC20 lets the token issuer keep a single canonical token and allowlist which bridges may mint or burn it, each with configurable rate limits. This caps the damage a single compromised bridge can do.

**Q: What is the Lockbox in ERC-7281, and why is it useful?**

The Lockbox is a wrapper contract that holds the home-chain liquidity of an existing ERC-20 and issues the xERC20 representation against it. It gives already-deployed tokens an adoption path to xERC20 without having to migrate holders to a new token contract.

**Q: How does ERC-7802 differ from ERC-7281?**

ERC-7802 is deliberately minimal: it defines only `crosschainMint` and `crosschainBurn` (plus matching events) as standardized entry points for authorized bridges, and leaves features such as rate limits or fees to be layered on top. ERC-7281 is broader, bundling the Lockbox, rate-limit structs, and configuration functions into the standard itself.

**Q: What two steps make a token compatible with Optimism's SuperchainERC20?**

First, grant the `SuperchainTokenBridge` (at `0x4200000000000000000000000000000000000028`) permission to call `crosschainMint` and `crosschainBurn`. Second, deploy the `SuperchainERC20` contract at the same address on every Superchain chain where the token should be available; chains where it is not deployed cannot receive the token.

**Q: Why does ERC-7905 exist if ERC-7281 already covers xERC20?**

ERC-7281 carries Lockbox wrappers, structs, and extensive configuration functions that exceed the minimum needed for core interoperability. ERC-7905 keeps only the xERC20-native functions: mint, burn and the limit views. Tokens that do not need the rest of ERC-7281 get a smaller interface.

## References

- [ERC-7281: Sovereign Bridged Tokens (Ethereum Magicians)](https://ethereum-magicians.org/t/erc-7281-sovereign-bridged-tokens/14979)
- [ERC-7802: Crosschain Token Interface (Ethereum Magicians)](https://ethereum-magicians.org/t/erc-7802-crosschain-token-interface/21508)
- [ERC-7905: minimal xERC20 (Ethereum ERCs PR #961)](https://github.com/ethereum/ERCs/pull/961/)
- [defi-wonderland — crosschainERC20 implementation](https://github.com/defi-wonderland/crosschainERC20)
- [Optimism Docs — SuperchainERC20](https://docs.optimism.io/interop/superchain-erc20)

### Related articles

- [USD₮0 - Omnichain Fungible Token]({{site.url_complet}}/2025/11/07/usdt0-Omnichain-fungible-token/)
- [Cross-Chain Bridge Hacks - Ten Incidents, Five Failure Classes]({{site.url_complet}}/2026/07/31/cross-chain-bridge-hacks/)
