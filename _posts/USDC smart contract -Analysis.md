# USDC smart contract -Analysis

This article presents a deepe dive into USDC smart contract on Ethereum mainet



[TOC]



https://etherscan.io/address/0x43506849d7c04f9138d1a2050bbf3a0c054402dd#code

![usdc-mainet-uml](/home/ryan/Downloads/me/access-denied/assets/article/blockchain/ethereum/usdc-mainet-uml.svg)



## V1

### Blacklistable

```solidity
/**
 * SPDX-License-Identifier: Apache-2.0
 *
 * Copyright (c) 2023, Circle Internet Financial, LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

pragma solidity 0.6.12;

import { Ownable } from "./Ownable.sol";

/**
 * @title Blacklistable Token
 * @dev Allows accounts to be blacklisted by a "blacklister" role
 */
abstract contract Blacklistable is Ownable {
    address public blacklister;
    mapping(address => bool) internal _deprecatedBlacklisted;

    event Blacklisted(address indexed _account);
    event UnBlacklisted(address indexed _account);
    event BlacklisterChanged(address indexed newBlacklister);

    /**
     * @dev Throws if called by any account other than the blacklister.
     */
    modifier onlyBlacklister() {
        require(
            msg.sender == blacklister,
            "Blacklistable: caller is not the blacklister"
        );
        _;
    }

    /**
     * @dev Throws if argument account is blacklisted.
     * @param _account The address to check.
     */
    modifier notBlacklisted(address _account) {
        require(
            !_isBlacklisted(_account),
            "Blacklistable: account is blacklisted"
        );
        _;
    }

    /**
     * @notice Checks if account is blacklisted.
     * @param _account The address to check.
     * @return True if the account is blacklisted, false if the account is not blacklisted.
     */
    function isBlacklisted(address _account) external view returns (bool) {
        return _isBlacklisted(_account);
    }

    /**
     * @notice Adds account to blacklist.
     * @param _account The address to blacklist.
     */
    function blacklist(address _account) external onlyBlacklister {
        _blacklist(_account);
        emit Blacklisted(_account);
    }

    /**
     * @notice Removes account from blacklist.
     * @param _account The address to remove from the blacklist.
     */
    function unBlacklist(address _account) external onlyBlacklister {
        _unBlacklist(_account);
        emit UnBlacklisted(_account);
    }

    /**
     * @notice Updates the blacklister address.
     * @param _newBlacklister The address of the new blacklister.
     */
    function updateBlacklister(address _newBlacklister) external onlyOwner {
        require(
            _newBlacklister != address(0),
            "Blacklistable: new blacklister is the zero address"
        );
        blacklister = _newBlacklister;
        emit BlacklisterChanged(blacklister);
    }

    /**
     * @dev Checks if account is blacklisted.
     * @param _account The address to check.
     * @return true if the account is blacklisted, false otherwise.
     */
    function _isBlacklisted(address _account)
        internal
        virtual
        view
        returns (bool);

    /**
     * @dev Helper method that blacklists an account.
     * @param _account The address to blacklist.
     */
    function _blacklist(address _account) internal virtual;

    /**
     * @dev Helper method that unblacklists an account.
     * @param _account The address to unblacklist.
     */
    function _unBlacklist(address _account) internal virtual;
}

```



The `Blacklistable` contract is an **abstract access-control module** that enables a `blacklister` role to manage a blacklist of accounts. It is designed to be inherited by token contracts (such as `FiatTokenV1`, `FiatTokenV2_2`, etc.) to enforce regulatory or compliance restrictions.

Here’s a breakdown of its structure, purpose, and how it ties into the broader token implementation:

------

#### Key Components

#### Roles

- **`blacklister`**: A privileged role (separate from `owner`) that can add/remove accounts from the blacklist.
- **`owner`**: From the inherited `Ownable` contract, can assign a new `blacklister`.

------

#### Modifiers

| Modifier                  | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `onlyBlacklister`         | Restricts access to the current blacklister.                 |
| `notBlacklisted(address)` | Reverts if the address is blacklisted, used to protect token methods (e.g. `transfer`, `approve`). |



------

#### Public Functions

##### `blacklist(address _account)`

- Callable only by `blacklister`.
- Internally calls `_blacklist(_account)`.
- Emits `Blacklisted`.

##### `unBlacklist(address _account)`

- Callable only by `blacklister`.
- Calls `_unBlacklist(_account)`.
- Emits `UnBlacklisted`.

##### `updateBlacklister(address _newBlacklister)`

- Callable only by `owner`.
- Assigns a new `blacklister`.
- Reverts if address is `0x0`.

##### `isBlacklisted(address)`

- Public view function to expose internal blacklist state via `_isBlacklisted`.

------

##### Internal (Abstract) Functions

These must be implemented by derived contracts:

| Function                  | Purpose                                                    |
| ------------------------- | ---------------------------------------------------------- |
| `_isBlacklisted(address)` | Returns true/false if account is blacklisted.              |
| `_blacklist(address)`     | Logic to blacklist an account (e.g. set bit flag or bool). |
| `_unBlacklist(address)`   | Logic to unblacklist (reset state).                        |



------

#### Deprecated Storage

```
mapping(address => bool) internal _deprecatedBlacklisted;
```

- Used in earlier versions (`FiatTokenV1` and `V2`) for tracking blacklisted accounts.
- **Deprecated** in `FiatTokenV2_2`, where blacklist and balance are stored together using bit-packing.
- Still retained for **migration** purposes in `initializeV2_2`.

------

#### Example Integration

In `FiatTokenV2_2`, the contract overrides:

```
function _isBlacklisted(address _account) internal override view returns (bool)
function _blacklist(address _account) internal override
function _unBlacklist(address _account) internal override
```

Using this logic:

- High bit of `balanceAndBlacklistStates[_account]` indicates blacklist status.
- Provides a more **efficient and gas-optimized** mechanism compared to storing separate mappings.

------

#### Summary

| Aspect            | Value                                                        |
| ----------------- | ------------------------------------------------------------ |
| Purpose           | Control and enforce blacklist logic in compliant token contracts |
| Role-based Access | `blacklister` (custom), `owner` (from `Ownable`)             |
| Abstract?         | Yes — requires implementation in inheriting contracts        |
| Upgrade-friendly? | Yes — supports smooth migration of blacklist data            |
| Use case          | Compliance, regulatory enforcement, fraud protection         |



### Transfer

```
    /**
     * @notice Transfers tokens from the caller.
     * @param to    Payee's address.
     * @param value Transfer amount.
     * @return True if the operation was successful.
     */
    function transfer(address to, uint256 value)
        external
        override
        whenNotPaused
        notBlacklisted(msg.sender)
        notBlacklisted(to)
        returns (bool)
    {
        _transfer(msg.sender, to, value);
        return true;
    }
```



### Minting

    /**
     * @dev Throws if called by any account other than a minter.
     */
    modifier onlyMinters() {
        require(minters[msg.sender], "FiatToken: caller is not a minter");
        _;
    }
    
    /**
     * @notice Mints fiat tokens to an address.
     * @param _to The address that will receive the minted tokens.
     * @param _amount The amount of tokens to mint. Must be less than or equal
     * to the minterAllowance of the caller.
     * @return True if the operation was successful.
     */
    function mint(address _to, uint256 _amount)
        external
        whenNotPaused
        onlyMinters
        notBlacklisted(msg.sender)
        notBlacklisted(_to)
        returns (bool)
    {
        require(_to != address(0), "FiatToken: mint to the zero address");
        require(_amount > 0, "FiatToken: mint amount not greater than 0");
    
        uint256 mintingAllowedAmount = minterAllowed[msg.sender];
        require(
            _amount <= mintingAllowedAmount,
            "FiatToken: mint amount exceeds minterAllowance"
        );
    
        totalSupply_ = totalSupply_.add(_amount);
        _setBalance(_to, _balanceOf(_to).add(_amount));
        minterAllowed[msg.sender] = mintingAllowedAmount.sub(_amount);
        emit Mint(msg.sender, _to, _amount);
        emit Transfer(address(0), _to, _amount);
        return true;
    }
    
    /**
     * @dev Throws if called by any account other than the masterMinter
     */
    modifier onlyMasterMinter() {
        require(
            msg.sender == masterMinter,
            "FiatToken: caller is not the masterMinter"
        );
        _;
    }
    
    /**
     * @notice Gets the minter allowance for an account.
     * @param minter The address to check.
     * @return The remaining minter allowance for the account.
     */
    function minterAllowance(address minter) external view returns (uint256) {
        return minterAllowed[minter];
    }

## Burn/Redeem



```solidity
function burn(uint256 _amount)
        external
        whenNotPaused
        onlyMinters
        notBlacklisted(msg.sender)
    {
        uint256 balance = _balanceOf(msg.sender);
        require(_amount > 0, "FiatToken: burn amount not greater than 0");
        require(balance >= _amount, "FiatToken: burn amount exceeds balance");

        totalSupply_ = totalSupply_.sub(_amount);
        _setBalance(msg.sender, balance.sub(_amount));
        emit Burn(msg.sender, _amount);
        emit Transfer(msg.sender, address(0), _amount);
    }

```



## FiatTokenV2_1

The `FiatTokenV2_1` contract is a minor upgrade (version 2.1) of the `FiatTokenV2` contract. Here's a breakdown of its key features and functionality:

```solidity
/**
 * @title FiatToken V2.1
 * @notice ERC20 Token backed by fiat reserves, version 2.1
 */
contract FiatTokenV2_1 is FiatTokenV2 {
    /**
     * @notice Initialize v2.1
     * @param lostAndFound  The address to which the locked funds are sent
     */
    function initializeV2_1(address lostAndFound) external {
        // solhint-disable-next-line reason-string
        require(_initializedVersion == 1);

        uint256 lockedAmount = _balanceOf(address(this));
        if (lockedAmount > 0) {
            _transfer(address(this), lostAndFound, lockedAmount);
        }
        _blacklist(address(this));

        _initializedVersion = 2;
    }

    /**
     * @notice Version string for the EIP712 domain separator
     * @return Version string
     */
    function version() external pure returns (string memory) {
        return "2";
    }
}
```



------

### Key Changes in V2.1

1. **Initialization of Version 2.1 (`initializeV2_1`)**:
   - Adds a mechanism to handle locked funds in the contract's own address:
     - Transfers locked funds to a designated `lostAndFound` address.
     - Blacklists the contract's own address to prevent further transfers into it.
   - Ensures that the upgrade process is safe and idempotent:
     - Requires `_initializedVersion == 1` (ensuring this is run only after the V2 upgrade).
2. **Version String (`version()`)**:
   - Returns `"2"` for the EIP-712 domain separator, keeping compatibility with off-chain signing mechanisms like `permit` and `transferWithAuthorization`.

------

### Detailed Functionality

#### `initializeV2_1(address lostAndFound)`

- **Purpose**: Finalizes the V2.1 upgrade by handling locked funds and securing the contract's address.
- **Key Steps**:
  1. Checks `_initializedVersion == 1` to ensure it’s a valid transition from V2.
  2. Retrieves any tokens accidentally locked in the contract's address via `_balanceOf(address(this))`.
  3. Transfers the locked tokens to the `lostAndFound` address if the balance is greater than zero.
  4. Blacklists the contract's own address using `_blacklist(address(this))` to prevent future deposits.
  5. Updates `_initializedVersion` to `2` to signify the completion of the upgrade.





------

#### `version()`

- **Purpose**: Provides the version identifier for the EIP-712 domain separator.
- **Return Value**: A fixed string `"2"`.
  - This ensures consistency with the V2 contract for signature validation.

------

### Key Features

1. **Backward Compatibility**:
   - Retains all functionalities of `FiatTokenV2`.
   - Ensures off-chain signing mechanisms like `permit` and `transferWithAuthorization` remain unchanged.
2. **Upgrade Safety**:
   - Uses `_initializedVersion` to prevent accidental re-execution of initialization logic.
3. **Locked Funds Recovery**:
   - Resolves a common issue in ERC-20 tokens where tokens are accidentally locked in the contract address.
4. **Blacklist Enhancement**:
   - Ensures that no future transfers can occur to the contract's own address by blacklisting it.

------

###  Summary

The `FiatTokenV2_1` contract introduces a small but critical upgrade to improve operational safety and usability:

- Adds a mechanism to recover locked funds.
- Secures the contract against further deposits into its own address.
- Maintains backward compatibility and consistency with off-chain signing mechanisms.

Let me know if you'd like to discuss specific implementation details or test scenarios for the upgrade process!





## FiatTokenV2_2

The `FiatTokenV2_2` contract represents **version 2.2** of Circle’s fiat-backed ERC-20 token, continuing a pattern of incremental and safety-focused upgrades from previous versions (V2 and V2.1). Here's a comprehensive breakdown of its features, enhancements, and design rationale:

------

### Inheritance & Architecture

- Inherits from `FiatTokenV2_1`, and thereby also from:
  - `FiatTokenV2`
  - `FiatTokenV1_1`
  - `FiatTokenV1`
  - `Blacklistable`
  - `EIP2612` & `EIP3009` via V2
- Integrates `EIP712Domain` for domain separation logic.
- Emphasizes upgradability via `initializeV2_2`, like previous versions.

------

### New Features in V2.2

#### Unified Blacklist and Balance Storage

- Introduces `balanceAndBlacklistStates`, a `uint256` mapping:
  - **High bit (bit 255)**: Blacklist flag (`1` = blacklisted, `0` = not).
  - **Lower 255 bits**: Account balance.
- This **compresses blacklist and balance into a single storage slot**, reducing gas usage and complexity in managing state.

------

#### Blacklist Migration (`initializeV2_2`)

```
function initializeV2_2(address[] calldata accountsToBlacklist, string calldata newSymbol) external
```

- Ensures `_initializedVersion == 2` before proceeding (enforces upgrade sequence).
- **Migrates old blacklist** to new `balanceAndBlacklistStates` format.
- **Deletes legacy** `_deprecatedBlacklisted` data.
- **Updates symbol** via `newSymbol`.
- Also **blacklists the contract’s own address** (continued from V2.1).

```solidity
    /**
     * @notice Initialize v2.2
     * @param accountsToBlacklist   A list of accounts to migrate from the old blacklist
     * @param newSymbol             New token symbol
     * data structure to the new blacklist data structure.
     */
    function initializeV2_2(
        address[] calldata accountsToBlacklist,
        string calldata newSymbol
    ) external {
        // solhint-disable-next-line reason-string
        require(_initializedVersion == 2);

        // Update fiat token symbol
        symbol = newSymbol;

        // Add previously blacklisted accounts to the new blacklist data structure
        // and remove them from the old blacklist data structure.
        for (uint256 i = 0; i < accountsToBlacklist.length; i++) {
            require(
                _deprecatedBlacklisted[accountsToBlacklist[i]],
                "FiatTokenV2_2: Blacklisting previously unblacklisted account!"
            );
            _blacklist(accountsToBlacklist[i]);
            delete _deprecatedBlacklisted[accountsToBlacklist[i]];
        }
        _blacklist(address(this));
        delete _deprecatedBlacklisted[address(this)];

        _initializedVersion = 3;
    }
```



------

#### Signature Handling Update

- Accepts **packed `bytes` signatures** (r, s, v) for:
  - `permit`
  - `transferWithAuthorization`
  - `receiveWithAuthorization`
  - `cancelAuthorization`
- Improves compatibility with **smart contract wallets** and **EOAs** using signature abstraction.

------

#### EIP712 Domain Separator Customization

```
function _domainSeparator() internal override view returns (bytes32)
```

- Uses `EIP712.makeDomainSeparator(name, "2", _chainId())`.
- Dynamically fetches `chainid()` via inline assembly for better cross-chain compatibility.

------

### Key Internal Methods

#### `_setBlacklistState()`

- Sets high bit (255) to blacklist.
- Clears high bit to unblacklist, preserving balance.

#### `_setBalance()`

- Ensures balance ≤ 2²⁵⁵ – 1.
- Reverts if account is blacklisted.
- Stores balance in lower 255 bits.

#### `_balanceOf()`

- Retrieves balance using `& ((1 << 255) - 1)` (i.e., mask out the blacklist flag).

#### `_isBlacklisted()`

- Returns true if high bit is 1.

------

###  Overrides and Compatibility

- `approve()`, `permit()`, `increaseAllowance()`, `decreaseAllowance()` override earlier versions but keep the original logic.
- Dual `permit()` definitions:
  - One using traditional `(v, r, s)`.
  - One using a packed `bytes signature`.
- Maintains **backward compatibility** with off-chain tools and wallets while supporting new usage patterns.

------

### Security & Safety

- All critical functions are guarded by:
  - `whenNotPaused`
  - `notBlacklisted` (where applicable)
- Prevents balance changes for blacklisted addresses.
- Strict upgrade path enforced via `_initializedVersion`.

------

### Summary: What’s New in V2.2?

| Feature                          | Description                                   |
| -------------------------------- | --------------------------------------------- |
| **Bit-packed balance/blacklist** | More efficient storage pattern                |
| **Blacklist migration logic**    | Transition from legacy structure              |
| **Signature packing support**    | Packed signatures for wallet compatibility    |
| **Dynamic chain ID**             | EIP-712 support across chains                 |
| **Refined override logic**       | Dual `permit()` and streamlined compatibility |



------

### Final Thoughts

`FiatTokenV2_2` is a **robust and gas-efficient upgrade** that refines blacklist handling and expands compatibility with evolving Ethereum signature standards (especially relevant for smart contract wallets and meta-transactions). It's a production-quality upgrade aligned with compliance and usability goals.

Let me know if you'd like a visual of the bit-packing logic, test cases for the migration, or a sample integration guide!

## FiatTokenV2

This Solidity smart contract, `FiatTokenV2`, is a version 2 upgrade of an ERC-20 token backed by fiat reserves. It extends several components and implements additional ERC standards to enhance security, usability, and off-chain authorization capabilities. Here's a breakdown of the key aspects:

------

###  Inheritances & Interfaces

`FiatTokenV2` inherits:

- `FiatTokenV1_1`: Base implementation with core ERC-20 and possibly compliance features.
- `EIP3009`: Enables **off-chain signed authorization-based transfers** (e.g., `transferWithAuthorization`).
- `EIP2612`: Allows **off-chain signed approvals** (`permit`) using EIP-712.

------

###  New Functionalities in V2

#### `initializeV2(string calldata newName)`

- Ensures one-time initialization of version 2.
- Updates the token name and domain separator for EIP-712 based signing.
- Sets `_initializedVersion` to `1`.

------

###  Security Modifiers

Most external functions use:

- `whenNotPaused`: Ensures functionality is paused if needed.
- `notBlacklisted`: Ensures compliance by blocking addresses on a blacklist.

------

### Allowance Management

- `increaseAllowance` and `decreaseAllowance`: Safe ways to adjust spending limits and mitigate race conditions associated with the standard `approve()` function.

------

### EIP-3009 - Transfer Authorization

- `transferWithAuthorization`: Lets someone transfer tokens from an account using an off-chain signature.
- `receiveWithAuthorization`: Variant that **ensures the `to` address matches the caller** to prevent front-running.
- `cancelAuthorization`: Allows canceling unused authorizations using signatures.

------

### EIP-2612 - Permit

- `permit`: Updates allowance via a signed message instead of requiring an on-chain `approve()` call.
- Useful for gasless approvals and enhancing UX for DeFi and wallets.

------

###  Internal Functions

- `_increaseAllowance`: Adds to the existing allowance safely.
- `_decreaseAllowance`: Subtracts from allowance, reverting if the result would be negative.

------

###  Notable Design Decisions

- Maintains backward compatibility with `FiatTokenV1_1`.
- Uses a **version check (`_initializedVersion`)** to ensure upgrade logic runs only once.
- Leverages `EIP712.makeDomainSeparator` to regenerate the domain separator if the name changes, keeping signatures valid and secure.

------

### Summary

This is a V2 upgrade of a fiat-backed ERC-20 token that:

- Adds secure, gasless off-chain interactions via EIPs 2612 and 3009.
- Improves allowance handling.
- Maintains security through pause/blacklist controls.
- Is ready for integration with modern wallets and DeFi protocols.