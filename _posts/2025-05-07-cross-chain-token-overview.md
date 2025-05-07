---
layout: post
title: Cross-chain tokens Standard (ERC-7281, xERC20) - Overview
date:  2025-05-02
lang: en
locale: en-GB
categories: blockchain solidity ethereum
tags: cross-chain erc20 erc7281 erc7802
description: This article presents the different standards to represent cross-chain token on Ethereum and EVM blockchain, notably ERC-7281(xERC20) & ERC-7802
image: 
isMath: false
---

This article presents the different standards to represent cross-chain token on Ethereum and EVM blockchain.

[TOC]

## ERC-7281 (xERC20): Sovereign Bridged Tokens

> [ERC specification](https://eips.ethereum.org/EIPS/eip-7802), [Pull Request](https://github.com/ethereum/ERCs/pull/89)
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

`IERC7802` is intentionally lightweight, ensuring minimal overhead for implementation. Its modular design enables extensibility, allowing additional features—such as mint/burn limits, transfer fees, or bridge-specific access control mechanisms—to be layered on top without modifying the base interface.

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

