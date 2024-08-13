---
layout: post
title:  Code4Arena Contest - Dyad Stablecoin Liquidation 
date:   2024-05-02
lang: en
locale: en-GB
categories: blockchain ethereum security defi
tags: ethereum solidity interview security gas
description: This article presents the liquidation function from the Dyad Stablecoin made during the code4Arena contest
image: /assets/article/blockchain/audit/dyad-vaultManagerV2.png
isMath: false
---

This article presents the liquidation function from the `Dyad Stablecoin`.

This analyse has been done for the [Code4Arena](https://github.com/code-423n4/2024-04-dyad) contest..

Since I have a limited time, I found that it could be interesting to focus only in one function in the `VaultManagerV2`, [liquidate](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L205) instead of the whole code.

Prior to the contest, the code has also been audited by [huntersec](https://www.huntersec.co/portfolio/audit/dyad-kerosene-vaults/full-report)

## Overview

DYAD is a decentralized stablecoin. Traditionally, two costs make stablecoins inefficient: surplus collateral and DEX liquidity. 

DYAD minimizes both of these costs through Kerosene, a token that lowers the individual cost to mint DYAD.

- [Website](https://dyadstable.notion.site/DYAD-design-outline-v6-3fa96f99425e458abbe574f67b795145)
- [Code4Arena Dyad](https://github.com/code-423n4/2024-04-dyad)
- [Documentation](https://dyadstable.notion.site/DYAD-design-outline-v6-3fa96f99425e458abbe574f67b795145)
- [DYAD V2 - Kerosene - Code4rena Audit](https://www.youtube.com/watch?v=ok4CBaqEajM)

![dyad-vaultManagerV2]({{site.url_complet}}/assets/article/blockchain/audit/dyad-vaultManagerV2.png)

### Notes

Notes are ERC-721 NFTs into which holders deposit approved ERC-20 tokens. These tokens are currently wETH and wstETH, and will soon include LSTs and LRTs, other types of yield-bearing collateral, as well as Kerosene. 

=> Note holders can then mint DYAD against the combined USD value of tokens they deposit at a 150% minimum collateralization ratio.

**Summary:**

A user can deposit wETH and wstETH to receive ERC-721 NFTs (Note) called `dNFT`

With these NFTs, holder can then mint DYAD, the stablecoin against 150% minimum CR.

### Kerosene (ERC20)

Each DYAD stablecoin is backed by at least $1.50 of exogenous collateral. This surplus absorbs the collateral’s volatility, keeping DYAD fully backed in all conditions. 

=> Kerosene is a token that lets you mint DYAD against this collateral surplus. Kerosene can be deposited in Notes just like other collateral to increase the Note’s DYAD minting capacity.



### Introduction

The liquidation process is described as follows:

> If a Note’s collateral value in USD drops below 150% of its DYAD minted balance, it faces liquidation. The liquidator burns a quantity of DYAD equal to the target Note’s DYAD minted balance, and in return receives an equivalent value plus a 20% bonus of the target Note’s backing colateral, which the liquidator can direct to any other Note, usually their own. The target keeps the remainder of their collateral, if any.
> Users may also burn DYAD stablecoins that they hold, which reduces their DYAD minted balance and allows them to withdraw more collateral or avoid liquidation.

### Term

- **Notes** 

Notes are ERC-721 NFTs into which holders deposit approved ERC-20 tokens. These tokens are currently wETH and wstETH, and will soon include LSTs and LRTs, other types of yield-bearing collateral, as well as Kerosene. 

Note holders can then mint DYAD against the combined USD value of tokens they deposit at a 150% minimum collateralization ratio.

- DNft — "A dNFT gives you the right to mint DYAD"


- Dyad — "Stablecoin backed by ETH"




## Code

The code for the function `liquidate`, inside the contract `VaultManagerV2` is the following:

```solidity
uint public constant MIN_COLLATERIZATION_RATIO = 1.5e18; // 150%
uint public constant LIQUIDATION_REWARD        = 0.2e18; //  20%
  /// @inheritdoc IVaultManager
  function liquidate(
    uint id,
    uint to
  ) 
    external 
      isValidDNft(id)
      isValidDNft(to)
    {
      uint cr = collatRatio(id);
      if (cr >= MIN_COLLATERIZATION_RATIO) revert CrTooHigh();
      dyad.burn(id, msg.sender, dyad.mintedDyad(address(this), id));

      uint cappedCr               = cr < 1e18 ? 1e18 : cr;
      uint liquidationEquityShare = (cappedCr - 1e18).mulWadDown(LIQUIDATION_REWARD);
      uint liquidationAssetShare  = (liquidationEquityShare + 1e18).divWadDown(cappedCr);

      uint numberOfVaults = vaults[id].length();
      for (uint i = 0; i < numberOfVaults; i++) {
          Vault vault      = Vault(vaults[id].at(i));
          uint  collateral = vault.id2asset(id).mulWadUp(liquidationAssetShare);
          vault.move(id, to, collateral);
      }
      emit Liquidate(id, msg.sender, to);
  }
```



### Constants

Two constants are important for the function `liquidate`

The first variable defines the minimal value of the CR before liquidiation and the second value defines the liquidation reward.

```solidity
uint public constant MIN_COLLATERIZATION_RATIO = 1.5e18; // 150%
uint public constant LIQUIDATION_REWARD        = 0.2e18; //  20%
```

Reference: [github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L25](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L25)

### Vault

#### Move function

The function `move` transfers amount of `from`to `to`.

It is used during liquidation to move funds from the liquidated account to the liquidator.

`from`and `to`are integers representing a Note(NFT). 

This function is restricted to the role ` onlyVaultManager`

```solidity
function move(
    uint from,
    uint to,
    uint amount
    )
    external
    onlyVaultManager
    {
    id2asset[from] -= amount;
    id2asset[to]   += amount;
    emit Move(from, to, amount);
}
```

Info: `uint256`could be used instead of `uint`for clarity. 

Code Reference: [github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/src/core/Vault.sol#L66](https://github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/src/core/Vault.sol#L66)

#### Dyad

##### **mintedDyad**

```solidity
// vault manager => (dNFT ID => dyad)
mapping (address => mapping (uint => uint)) public mintedDyad; 
```

Code reference: [github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/src/core/Dyad.sol#L12](https://github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/src/core/Dyad.sol#L12)

##### burn

The function `burn`is restricted to the role `licensedVaultManager `.

It reduces the `from` s balance   with `amount`

Then it reduces also `amount`of dyad for the corresponding vault manager, which is the contract sender.

```solidity
  /// @inheritdoc IDyad
  /**
  * @notice Burns amount of DYAD through a dNFT and licensed vault manager
  *         from a specified address.
  * @dev The caller must be a licensed vault manager. Vault manager get
  *      licensed by the 'sll'.
  * @param id ID of the dNFT.
  * @param from The address of the recipient who the tokens will be burnt
  *        from.
  * @param amount The amount of tokens to be burned.
  */
  function burn(
      uint    id, 
      address from,
      uint    amount
  ) external 
      licensedVaultManager 
    {
      _burn(from, amount);
      mintedDyad[msg.sender][id] -= amount;
  }
```



### Others functions

#### collatRatio

This function compute the collateral ratio.

First, it gets the number of dyad minted, the stablecoin

If this number is different from zero, calls the function ` getTotalUsdValue`.

The value is rounded `down`, therefore the collateral value is reduces in favor of the protocol, which is safer.

```solidity
  function collatRatio(
    uint id
  )
    public 
    view
    returns (uint) {
      uint _dyad = dyad.mintedDyad(address(this), id);
      if (_dyad == 0) return type(uint).max;
      return getTotalUsdValue(id).divWadDown(_dyad);
  }
```

Code reference: [github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L230](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L230)

#### getTotalUsdValue

```solidity
  function getTotalUsdValue(
    uint id
  ) 
    public 
    view
    returns (uint) {
      return getNonKeroseneValue(id) + getKeroseneValue(id);
  }
```

Code reference: [github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L241](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L241)

#### getKeroseneValue / getNonKeroseneValue

These two functions are very similar, but the first one uses the array `vaults` and the second one uses the array `vaultsKerosene`.

```solidity
  function getNonKeroseneValue(
    uint id
  ) 
    public 
    view
    returns (uint) {
      uint totalUsdValue;
      uint numberOfVaults = vaults[id].length(); 
      for (uint i = 0; i < numberOfVaults; i++) {
        Vault vault = Vault(vaults[id].at(i));
        uint usdValue;
        if (vaultLicenser.isLicensed(address(vault))) {
          usdValue = vault.getUsdValue(id);        
        }
        totalUsdValue += usdValue;
      }
      return totalUsdValue;
  }

  function getKeroseneValue(
    uint id
  ) 
    public 
    view
    returns (uint) {
      uint totalUsdValue;
      uint numberOfVaults = vaultsKerosene[id].length(); 
      for (uint i = 0; i < numberOfVaults; i++) {
        Vault vault = Vault(vaultsKerosene[id].at(i));
        uint usdValue;
        if (keroseneManager.isLicensed(address(vault))) {
          usdValue = vault.getUsdValue(id);        
        }
        totalUsdValue += usdValue;
      }
      return totalUsdValue;
  }
```

Code reference: [https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L250](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L250)

**Info:**

- An important point is that the vaults have to be licensed inside the contract `keroseneManager`, otherwise the collateral assets put in the vault are not taken into consideration.

- These two functions are very similar, and probably a large part of the code could be moved to a generic function `getUSDValue` which takes the vault array as supplementary argument.

This would avoid having the same code logic twice and reduces the contract bytecode size too.

- `uint256`could be used instead of `uint`for clarity. 
- `++i`could be used instead of `i++`for [gas optimization](https://rya-sge.github.io/access-denied/2023/09/26/gas-optimization/)



### Math

To perform computation, the protocol uses the library `solmate`, which provides  an arithmetic library with operations for fixed-point numbers.

Code reference: [github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/lib/solmate/src/utils/FixedPointMathLib.sol#L20](https://github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/lib/solmate/src/utils/FixedPointMathLib.sol#L20)

```solidity
uint256 internal constant WAD = 1e18; // The scalar of ETH and most ERC20s.

    function mulWadDown(uint256 x, uint256 y) internal pure returns (uint256) {
        return mulDivDown(x, y, WAD); // Equivalent to (x * y) / WAD rounded down.
    }

    function mulWadUp(uint256 x, uint256 y) internal pure returns (uint256) {
        return mulDivUp(x, y, WAD); // Equivalent to (x * y) / WAD rounded up.
    }

    function divWadDown(uint256 x, uint256 y) internal pure returns (uint256) {
        return mulDivDown(x, WAD, y); // Equivalent to (x * WAD) / y rounded down.
    }

    function divWadUp(uint256 x, uint256 y) internal pure returns (uint256) {
        return mulDivUp(x, WAD, y); // Equivalent to (x * WAD) / y rounded up.
    }
```





## Function explanation

### Steps

Code available [line 205](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L205)

1) Get the Collateral Ratio

2) Check if the collateral value is higher than the minimum required

3) The function burn the corresponding dyad from the liquidator (sender): `vault manager => (dNFT ID => dyad)`

4. For each Vault (for loop), the contract

   1. Get the collateral Id

   2. Compute the collateral value by using the [fix notation library](https://github.com/code-423n4/2024-04-dyad/blob/4a987e536576139793a1c04690336d06c93fca90/lib/solmate/src/utils/FixedPointMathLib.sol#L20) with `mulWadUp`. 
      The collateral moved is rounded `Up`meaning that this is in favor of the liquidator.

      ```solidity
       uint  collateral = vault.id2asset(id).mulWadUp(liquidationAssetShare);
      ```

      

   $$
   Amount = Asset * liquidationAssetShare / 1e18
   $$

   

   3. Move `amount`of collateral from `id` to `to` with the function `move`

5) Emit the event `liquidate`

### Comparison with the documentation

> If a Note’s collateral value in USD drops below 150% of its DYAD minted balance, it faces liquidation. 

The following code check the CR and revert if the collateral value is > 150%

```solidity
 if (cr >= MIN_COLLATERIZATION_RATIO) revert CrTooHigh();
```

> The liquidator burns a quantity of DYAD equal to the target Note’s DYAD minted balance

```solidity
 dyad.burn(id, msg.sender, dyad.mintedDyad(address(this), id));              
```

Here the liquidator, specifies with `msg.sender` burn its own DYAD to repay the debt.

The quantity to burn is retrieved in the map  `mintedDyad` which corresponds to the target Note’s DYAD minted balance. The target is specify with the parameter `id`.

> and in return receives an equivalent value plus a 20% bonus of the target Note’s backing colateral, which the liquidator can direct to any other Note, usually their own. 

> ```solidity
>   uint liquidationEquityShare = (cappedCr - 1e18).mulWadDown(LIQUIDATION_REWARD);
> ```

$$

$$

$$
liquidationEquityShare = (cappedCr - 1) * 0.2
$$

If the CR is < 1, then the CR used is `1`. Otherwise it use the current value of CR, which is smaller than 1.5% due to the previous calculation.

```solidity
liquidationAssetShare  = (liquidationEquityShare + 1e18).divWadDown(cappedCr);
```


$$
liquidationAssetShare  = (liquidationEquityShare + 1) / cappedCR
$$


> The target keeps the remainder of their collateral, if any.

If we look on the two functions computing the liquidated assets share, we can see that `cappedCr`is used to compute the liquidation part.

Therefore,

```solidity
  uint liquidationEquityShare = (cappedCr - 1e18).mulWadDown(LIQUIDATION_REWARD);
  uint liquidationAssetShare  = (liquidationEquityShare + 1e18).divWadDown(cappedCr);
```

He only takes what is necessary to repay the debt


> Users may also burn DYAD stablecoins that they hold, which reduces their DYAD minted balance and allows them to withdraw more collateral or avoid liquidation.

A user can just call himself the function to do this.



## Conclusion

During the analyze of the liquidation function, I didn't find particular vulnerabilities. 

It would be interesting to see how the different vaults work and are configured to be sure that the value of the collateral returned is correct.