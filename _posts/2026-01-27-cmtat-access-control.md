---
layout: post
title: "Flexible Access Control in smart contracts (CMTAT)"
date:   2026-01-27
locale: en-GB
lang: en
last-update: 
categories: blockchain solidity
tags: solidity CMTAT RWA access-control RBAC
description: This article describes how CMTAT implements flexible access control by separating business logic from authorization policy, allowing deployments to choose between RBAC, ownership, OpenZeppelin AccessManager, or custom policies.
isMath: false
image: /assets/article/blockchain/ethereum/cmtat/access-control-snipet.png
---

Security‑token systems must adapt to heterogeneous regulatory and organizational setups. In this context, the **same tokenization logic** may need to be governed by different access‑control models (role based, ownership based, external manager, etc.), depending on the deployment environment.

CMTAT, a security token framework, addresses this requirement by **separating** business logic from authorization policy through a small but systematic pattern:

- **Modules** (pause, mint, burn, documents, snapshots, enforcement, etc.) define:
  - **Modifiers** such as `onlyPauseManager`
  - **Internal virtual hooks** such as `_authorizePause()`
- A **base access‑control contract** implements these hooks with a concrete policy base. CMTAT implements for the moment only a traditional [RBAC access control](https://docs.openzeppelin.com/contracts/5.x/access-control#role-based-access-control) but could be extended to  use instead [ownership](https://docs.openzeppelin.com/contracts/5.x/access-control#ownership-and-ownable), OpenZeppelin `AccessManager` or [Chainlink ACE](https://chain.link/automated-compliance-engine).

This article describes the rationale for this design, its realization in the CMTAT codebase (with `PauseModule` and `CMTATBaseAccessControl`), and how to replace the default policy with alternative access‑control mechanisms.

While this article focuses on CMTAT, this "design pattern" is relevant for other context, particularly to build open source library where the users may want to use a different type of access control

This design is based on the pattern used by OpenZeppelin for their [AccessManaged](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/manager/AccessManaged.sol) contract

[TOC]



### Motivation for flexible access control

- **Separation of concerns**:  
  - Modules focus on *functional behavior* (pause, mint, burn, document management, etc.).  
  - Access‑control code focuses on *authorization logic* (which caller is permitted to execute which operation).
- **Reusability of business logic**:  
  - The same `PauseModule` or `ERC20MintModule` can be reused across deployments that differ only in their access control requirements.
- **Configurable access control per deployment**:
  - A deployment can choose role‑based access control (RBAC), a single owner, a policy contract such as OpenZeppelin's `AccessManager`, or any other scheme without modifying module internals.
- **Auditability**:  
  - Auditors can review each module’s state transitions and invariants independently from the access‑control implementation.  
  - The authorization wiring can be reviewed as a separate concern.

Informally, the pattern can be viewed as a **policy “socket”**: modules expose authorization hooks, and deployments plug in the desired policy by overriding those hooks.

## CMTAT architecture

CMTAT is structured in three layers:

1. **Functional modules**
    Each module implements a single concern (pause, mint, burn, documents, enforcement, etc.).

   e.g.`PauseModule`

2. **Base wiring contracts** 
   These aggregate modules and implement authorization hooks using a concrete policy (e.g. RBAC).

   e.g.`CMTATBaseAccessControl`

3. **Deployable contracts**
    Non-abstract contracts that finalize initialization and are meant to be deployed.

   e.g.`CMTATUpgradeable`

CMTAT is divided into several module; each module implements a specific logic such as Pause and Deactivate functionality for the PauseModule.

Then several base contracts are responsible to put together the different modules such as 

Finally, a set of deployable contracts are available. These contracts are not abstract and will inherit from base contract

Schema have been generated with [surya](https://github.com/ConsenSysDiligence/surya)

### PauseModule

Here is the UML for the PauseModule.

You can see the different internal function available such as `_authorizePause()` and `_authorizeDeactivate()`

The key point to notice is that all externally callable state-changing functions are protected by modifiers that defer authorization to internal hooks. No role or ownership logic appears in the module itself.

![PauseModule.png]({{site.url_complet}}/assets/article/blockchain/ethereum/cmtat/PauseModule.png)

#### Contracts Description Table


|    Contract     |          Type          |                            Bases                             |                |                               |
| :-------------: | :--------------------: | :----------------------------------------------------------: | :------------: | :---------------------------: |
|        └        |   **Function Name**    |                        **Visibility**                        | **Mutability** |         **Modifiers**         |
|                 |                        |                                                              |                |                               |
| **PauseModule** |     Implementation     | PausableUpgradeable, IERC3643Pause, IERC7551Pause, ICMTATDeactivate |                |                               |
|        └        |         pause          |                           Public ❗️                           |       🛑        |       onlyPauseManager        |
|        └        |        unpause         |                           Public ❗️                           |       🛑        |       onlyPauseManager        |
|        └        |   deactivateContract   |                           Public ❗️                           |       🛑        | onlyDeactivateContractManager |
|        └        |         paused         |                           Public ❗️                           |                |              NO❗️              |
|        └        |      deactivated       |                           Public ❗️                           |                |              NO❗️              |
|        └        |    _authorizePause     |                          Internal 🔒                          |       🛑        |                               |
|        └        |  _authorizeDeactivate  |                          Internal 🔒                          |       🛑        |                               |
|        └        | _requireNotDeactivated |                          Internal 🔒                          |                |                               |
|        └        | _getPauseModuleStorage |                          Private 🔐                           |                |                               |


##### Legend

| Symbol | Meaning                   |
| :----: | ------------------------- |
|   🛑    | Function can modify state |
|   💵    | Function is payable       |

### CMTATBaseAccessControl

Here is the UML for CMTAT Base Access Control

![CMTATBaseAccessControl.png]({{site.url_complet}}/assets/article/blockchain/ethereum/cmtat/CMTATBaseAccessControl.png)

#### Contracts Description Table


|          Contract          |                 Type                 |                Bases                 |                |                  |
| :------------------------: | :----------------------------------: | :----------------------------------: | :------------: | :--------------: |
|             └              |          **Function Name**           |            **Visibility**            | **Mutability** |  **Modifiers**   |
|                            |                                      |                                      |                |                  |
| **CMTATBaseAccessControl** |            Implementation            | AccessControlModule, CMTATBaseCommon |                |                  |
|             └              | __CMTAT_commonModules_init_unchained |              Internal 🔒              |       🛑        | onlyInitializing |
|             └              |          supportsInterface           |               Public ❗️               |                |       NO❗️        |
|             └              |  _authorizeERC20AttributeManagement  |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |            _authorizeMint            |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |            _authorizeBurn            |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |     _authorizeDocumentManagement     |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |    _authorizeExtraInfoManagement     |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |       _authorizeERC20Enforcer        |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |       _authorizeForcedTransfer       |              Internal 🔒              |       🛑        |     onlyRole     |
|             └              |         _authorizeSnapshots          |              Internal 🔒              |       🛑        |     onlyRole     |

##### Legend

| Symbol | Meaning                   |
| :----: | ------------------------- |
|   🛑    | Function can modify state |
|   💵    | Function is payable       |

### Pattern instantiation in `PauseModule`

The `PauseModule` defines the pause/deactivate behavior and exposes **modifiers** and **internal authorization hooks**:

```solidity
abstract contract PauseModule is PausableUpgradeable, IERC3643Pause, IERC7551Pause, ICMTATDeactivate {
    error CMTAT_PauseModule_ContractIsDeactivated();
    error EnforcedDeactivation();

    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    // --- Modifiers ---
    modifier onlyPauseManager() {
        _authorizePause();
        _;
    }

    modifier onlyDeactivateContractManager() {
        _authorizeDeactivate();
        _;
    }

    // --- External API ---
    function pause()
        public
        virtual
        override(IERC3643Pause, IERC7551Pause)
        onlyPauseManager
    {
        _pause();
    }

    function unpause()
        public
        virtual
        override(IERC3643Pause, IERC7551Pause)
        onlyPauseManager
    {
        // … deactivation checks …
        _unpause();
    }

    function deactivateContract()
        public
        virtual
        override(ICMTATDeactivate)
        onlyDeactivateContractManager
    {
        // … implementation …
    }

    // --- Internal authorization hooks (no policy here) ---
    function _authorizePause() internal view virtual;
    function _authorizeDeactivate() internal view virtual;
}
```

The module deliberately avoids binding itself to a specific access‑control mechanism:

- It does **not** call `onlyRole(...)`.
- It does **not** rely on `onlyOwner`.
- It is agnostic to whether permissions are provided by roles, ownership, `AccessManager`, or another policy contract.

Instead, the module:

- Declares **which operations require authorization** via modifiers (`onlyPauseManager`, `onlyDeactivateContractManager`).
- Delegates authorization to **abstract internal functions** (`_authorizePause`, `_authorizeDeactivate`).
- Expects a **separate contract** to implement the policy by overriding those internal functions.

### `CMTATBaseAccessControl`: wiring modules to RBAC

`CMTATBaseAccessControl` is the concrete wiring used in the standard CMTAT deployment. It inherits from the access‑control wrapper (`AccessControlModule`) and from several functional modules, and **overrides** each authorization hook to enforce a role‑based access‑control model:

```solidity
abstract contract CMTATBaseAccessControl is
    AccessControlModule,
    CMTATBaseCommon
{
    // Initializer sets up roles, ERC20 base, and extra info
    function __CMTAT_commonModules_init_unchained(
        address admin,
        ICMTATConstructor.ERC20Attributes memory erc20Attrs,
        ICMTATConstructor.ExtraInformationAttributes memory extraAttrs
    )
        internal
        virtual
        onlyInitializing
    {
        __AccessControlModule_init_unchained(admin);
        __ERC20BaseModule_init_unchained(
            erc20Attrs.decimalsIrrevocable,
            erc20Attrs.name,
            erc20Attrs.symbol
        );
        __ExtraInformationModule_init_unchained(
            extraAttrs.tokenId,
            extraAttrs.terms,
            extraAttrs.information
        );
    }

    // --- Internal authorization overrides (current RBAC policy) ---

    function _authorizeERC20AttributeManagement()
        internal
        virtual
        override(ERC20BaseModule)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {}

    function _authorizeMint()
        internal
        virtual
        override(ERC20MintModule)
        onlyRole(MINTER_ROLE)
    {}

    function _authorizeBurn()
        internal
        virtual
        override(ERC20BurnModule)
        onlyRole(BURNER_ROLE)
    {}

    function _authorizeDocumentManagement()
        internal
        virtual
        override(DocumentEngineModule)
        onlyRole(DOCUMENT_ROLE)
    {}

    function _authorizeSnapshots()
        internal
        virtual
        override(SnapshotEngineModule)
        onlyRole(SNAPSHOOTER_ROLE)
    {}

    // …and so on for other modules like enforcement, forced transfers, etc.
}
```

In the same way, another base contract in the hierarchy overrides `_authorizePause` and `_authorizeDeactivate` from `PauseModule` using roles such as `PAUSER_ROLE` and `DEFAULT_ADMIN_ROLE`.

The resulting structure is:

- Modules define **abstract hooks**.
- `CMTATBaseAccessControl` (and related base contracts) plug those hooks into a concrete RBAC scheme.

### Replacing the access‑control model

Because all sensitive operations are routed through internal virtual hooks, the authorization model can be changed by modifying the overrides only, without altering module functionality or storage layout.

The following subsections present three possible variants.

#### 1. Ownership‑based access control

> Here: use instead OpenZeppelin Ownable library and the modifier onlyOwner

For a minimal setup, a single‑owner control model can be used instead of RBAC. This can be achieved by:

- Defining `onlyOwner` (or an equivalent check).
- Overriding the hooks to apply ownership semantics.

```solidity
contract OwnablePauseAccess is PauseModule, Ownable {
    function _authorizePause() internal view override onlyOwner {}

    function _authorizeDeactivate() internal view override onlyOwner {}
}
```

Analogously, other hooks such as `_authorizeMint` or `_authorizeBurn` can be implemented with `onlyOwner`, yielding an owner‑controlled deployment while still reusing the same modules.

#### 2. OpenZeppelin `AccessManager` as policy engine

OpenZeppelin's `AccessManager` (or `AccessManagerUpgradeable`) centralizes authorization decisions in a dedicated contract and exposes a `canCall` API. CMTAT modules can be integrated with such a manager as follows:

- Keep the existing modules and hooks unchanged.
- Override the hooks so that they query an `AccessManager` instance.

```solidity
import {IAccessManager} from "@openzeppelin/contracts/access/manager/IAccessManager.sol";

abstract contract AccessManagerBackedCMTAT is PauseModule /*, other modules */ {
    IAccessManager public immutable accessManager;

    constructor(IAccessManager manager_) {
        accessManager = manager_;
    }

    function _authorizePause() internal view virtual override {
        _checkCanCall(msg.sender, msg.sig);
    }

    function _authorizeDeactivate() internal view virtual override {
        _checkCanCall(msg.sender, msg.sig);
    }

    function _checkCanCall(address caller, bytes4 selector) internal view {
        (bool allowed, ) = accessManager.canCall(
            caller,
            address(this),
            selector
        );
        if (!allowed) {
            revert("AccessManager: unauthorized");
        }
    }
}
```

In such a configuration:

- Permissions are maintained in `AccessManager` (e.g. roles, proposers, executors, time locks).
- CMTAT modules call their hooks, which delegate the authorization decision to `AccessManager`.
- Policy changes (e.g. changing approvers or adding constraints) occur in the manager contract without modifying token modules.

#### 3. Hybrid or context‑based access control

Since the hooks are plain Solidity functions, more complex policies can be expressed:

- Allow either a role or an owner to pause:

```solidity
function _authorizePause() internal virtual override {
    if (hasRole(PAUSER_ROLE, msg.sender)) return;
    if (msg.sender == owner()) return;
    revert("Not authorized to pause");
}
```

- Forward to an external validator:

```solidity
function _authorizePause() internal virtual override {
    require(externalPolicy.canPause(msg.sender), "External policy denied");
}
```

Modules remain independent of these choices. They simply call `_authorizePause()` (or analogous hooks), and the implementation determines which policy is applied.

### Practical guidelines when extending CMTAT

If you are authoring new modules or customizing access control in CMTAT:

- **When writing a module:**
  - Use **modifiers + internal hooks** for all sensitive actions.  
    - Example: `modifier onlyDebtManager { _authorizeDebtManagement(); _; }`
  - Keep the module agnostic to concrete roles or ownership.
  - Document the expected access‑control behavior in NatSpec (`@custom:access-control`).

- **When wiring a deployment:**
  - Create a base access‑control contract (for example, `CMTATBaseAccessControl`).
  - Override all required hooks with your chosen model:
    - Roles via `AccessControl`.
    - Simple ownership.
    - OpenZeppelin `AccessManager`.
    - External policy contracts or multisigs.
  - Keep the overrides small and explicit so auditors can easily review them.

- **When changing the access control model later:**
  - Prefer changing the wiring, not the modules:
    - Override hooks differently in a new base.
    - Or point hooks to a new external policy contract.
  - This way you preserve the safety of previously‑audited business logic.

### Annex

#### Short example

```solidity
abstract contract PauseModule is Pausable {
    // --- Modifiers ---
    modifier onlyPauseManager() {
        _authorizePause();
        _;
    }

    // --- External API ---
    function pause() public virtual onlyPauseManager {
        _pause();
    }

    // --- Authorization hook ---
    // Must revert if msg.sender is not allowed to pause
    function _authorizePause() internal virtual;
}

// Deployable contract – ownership-based policy
contract OwnablePauseAccess is PauseModule, Ownable {
    function _authorizePause() internal view override onlyOwner{}
}
```



#### Openzeppelin

This design is based on the one used by OpenZeppelin for their [AccessManaged contract](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/manager/AccessManaged.sol).

Here is a shortened version with the modifier `restricted` which calls the internal function `_checkCanCall`

Base contract can apply the modifier `restricted`and override the function `_checkCanCall`if they have an additional check to perform.

```solidity
// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.4.0) (access/manager/AccessManaged.sol)

pragma solidity ^0.8.20;

/**
 * @dev This contract module makes available a {restricted} modifier.
 */
abstract contract AccessManaged is Context, IAccessManaged {


    /**
     * @dev Restricts access to a function as defined by the connected Authority for this contract and the
     * caller and selector of the function that entered the contract.*/
    modifier restricted() {
        _checkCanCall(_msgSender(), _msgData());
        _;
    }

    /**
     * @dev Reverts if the caller is not allowed to call the function identified by a selector. Panics if the calldata
     * is less than 4 bytes long.
     */
    function _checkCanCall(address caller, bytes calldata data) internal virtual {
        (bool immediate, uint32 delay) = AuthorityUtils.canCallWithDelay(
            authority(),
            caller,
            address(this),
            bytes4(data[0:4])
        );
        if (!immediate) {
            if (delay > 0) {
                _consumingSchedule = true;
                IAccessManager(authority()).consumeScheduledOp(caller, data);
                _consumingSchedule = false;
            } else {
                revert AccessManagedUnauthorized(caller);
            }
        }
    }
}
```



### Conclusion

By combining modifiers, internal virtual authorization hooks, and a dedicated access‑control base contract, CMTAT implements flexible access control:

- Modules remain focused on functional behavior and can be reused across deployments.
- The access control model can evolve from single owner to roles, `AccessManager`, or external policy contracts without rewriting core token logic.

This separation between functional behavior and authorization policy is particularly useful in long‑lived deployments, where access control requirements may change independently of the underlying token mechanics.

This is also particularly relevant for open-source library such as CMTAT to allow the different library users to define and use the access control of their choice without required for them to rewrite the core logic.

## Reference

- [OpenZeppelin V5 Access Control](https://docs.openzeppelin.com/contracts/5.x/access-control#role-based-access-control)
- [OpenZeppelin AccessManaged](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/manager/AccessManaged.sol)
- [Composable Security - The Role of Access Control in Solidity Smart Contracts](https://composable-security.com/blog/the-role-of-access-control-in-solidity-smart-contracts/)
- [Cursor](https://cursor.com/) and [Claude Code](https://claude.com/product/claude-code) to write the first draft of this article and review the content.
