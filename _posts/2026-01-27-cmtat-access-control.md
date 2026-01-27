## Flexible Access Control in CMTAT

Security‑token systems must adapt to heterogeneous governance and regulatory setups. In this context, the **same tokenization logic** may need to be governed by different access‑control models (role based, ownership based, external manager, etc.), depending on the deployment environment.

CMTAT addresses this requirement by **separating business logic from authorization policy** through a small but systematic pattern:

- **Modules** (pause, mint, burn, documents, snapshots, enforcement, etc.) define:
  - **Modifiers** such as `onlyPauseManager`
  - **Internal virtual hooks** such as `_authorizePause()`
- A **base access‑control contract** implements these hooks with a concrete policy (currently role‑based, but ownership or `AccessManager` can be used instead).

This article describes **the rationale** for this design, **its realization** in the CMTAT codebase (with `PauseModule` and `CMTATBaseAccessControl`), and **how to replace the default policy** with alternative access‑control mechanisms.

---

### Motivation for flexible access control

- **Separation of concerns**:  
  - Modules focus on *functional behavior* (pause, mint, burn, document management, etc.).  
  - Access‑control code focuses on *authorization logic* (which caller is permitted to execute which operation).
- **Reusability of business logic**:  
  - The same `PauseModule` or `ERC20MintModule` can be reused across deployments that differ only in their governance or organizational structure.
- **Configurable governance per deployment**:  
  - A deployment can choose role‑based access control (RBAC), a single owner, a governance/management contract such as OpenZeppelin’s `AccessManager`, or any other scheme without modifying module internals.
- **Auditability**:  
  - Auditors can review each module’s state transitions and invariants independently from the access‑control implementation.  
  - The authorization wiring can be reviewed as a separate concern.

Informally, the pattern can be viewed as a **policy “socket”**: modules expose authorization hooks, and deployments plug in the desired policy by overriding those hooks.

---

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
    function _authorizePause() internal virtual;
    function _authorizeDeactivate() internal virtual;
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

---

### `CMTATBaseAccessControl`: wiring modules to RBAC

`CMTATBaseAccessControl` is the concrete wiring used in the standard CMTAT deployment. It inherits from the access‑control wrapper (`AccessControlModule`) and from several functional modules, and **overrides each authorization hook** to enforce a role‑based access‑control model:

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

---

### Replacing the access‑control model

Because all sensitive operations are routed through internal virtual hooks, the authorization model can be changed by **modifying the overrides only**, without altering module functionality or storage layout.

The following subsections present three possible variants.

---

#### 1. Ownership‑based access control

For a minimal setup, a single‑owner control model can be used instead of RBAC. This can be achieved by:

- Defining `onlyOwner` (or an equivalent check).
- Overriding the hooks to apply ownership semantics.

```solidity
contract OwnablePauseAccess is PauseModule {
    address private _owner;

    modifier onlyOwner() {
        require(msg.sender == _owner, "Not owner");
        _;
    }

    constructor(address owner_) {
        _owner = owner_;
    }

    // Hook: who can pause / unpause?
    function _authorizePause() internal virtual override {
        require(msg.sender == _owner, "Not authorized to pause");
    }

    // Hook: who can permanently deactivate the contract?
    function _authorizeDeactivate() internal virtual override {
        require(msg.sender == _owner, "Not authorized to deactivate");
    }
}
```

Analogously, other hooks such as `_authorizeMint` or `_authorizeBurn` can be implemented with `onlyOwner`, yielding an owner‑controlled deployment while still reusing the same modules.

---

#### 2. OpenZeppelin `AccessManager` as policy engine

OpenZeppelin’s `AccessManager` (or `AccessManagerUpgradeable`) centralizes authorization decisions in a dedicated contract and exposes an `isAuthorized`‑style API. CMTAT modules can be integrated with such a manager as follows:

- Keep the existing modules and hooks unchanged.
- Override the hooks so that they query an `AccessManager` instance.

```solidity
import {IAccessManager} from "@openzeppelin/contracts/access/manager/IAccessManager.sol";

abstract contract AccessManagerBackedCMTAT is PauseModule /*, other modules */ {
    IAccessManager public immutable accessManager;

    bytes32 public constant PAUSE_PERMISSION_ID      = keccak256("PAUSE_PERMISSION");
    bytes32 public constant DEACTIVATE_PERMISSION_ID = keccak256("DEACTIVATE_PERMISSION");

    constructor(IAccessManager manager_) {
        accessManager = manager_;
    }

    function _authorizePause() internal virtual override {
        _checkPermission(PAUSE_PERMISSION_ID);
    }

    function _authorizeDeactivate() internal virtual override {
        _checkPermission(DEACTIVATE_PERMISSION_ID);
    }

    function _checkPermission(bytes32 permissionId) internal view {
        // Pseudocode: see actual AccessManager API for details
        bool ok = accessManager.isAuthorized(
            msg.sender,
            address(this),
            permissionId,
            msg.data
        );
        require(ok, "AccessManager: unauthorized");
    }
}
```

In such a configuration:

- Permissions are maintained in `AccessManager` (e.g. roles, proposers, executors, time locks).
- CMTAT modules call their hooks, which delegate the authorization decision to `AccessManager`.
- Governance changes (e.g. changing approvers or adding constraints) occur in the manager contract without modifying token modules.

---

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

---

### Practical guidelines when extending CMTAT

If you are authoring new modules or customizing access control in CMTAT:

- **When writing a module:**
  - Use **modifiers + internal hooks** for all sensitive actions.  
    - Example: `modifier onlyDebtManager { _authorizeDebtManagement(); _; }`
  - Keep the module **agnostic to concrete roles or ownership**.
  - Document the expected access‑control behavior in NatSpec (`@custom:access-control`).

- **When wiring a deployment:**
  - Create a base access‑control contract (for example, `CMTATBaseAccessControl`).
  - Override all required hooks with your chosen model:
    - Roles via `AccessControl`.
    - Simple ownership.
    - OpenZeppelin `AccessManager`.
    - External policy contracts or multisigs.
  - Keep the overrides small and explicit so auditors can easily review them.

- **When changing governance later:**
  - Prefer changing the wiring, not the modules:
    - Override hooks differently in a new base.
    - Or point hooks to a new external policy contract.
  - This way you preserve the safety of previously‑audited business logic.

---

### Conclusion

By combining **modifiers**, **internal virtual authorization hooks**, and **a dedicated access‑control base contract**, CMTAT implements **flexible and auditable access control**:

- Modules remain focused on functional behavior and can be reused across deployments.
- Governance can evolve from single owner to roles, `AccessManager`, or external policy contracts without rewriting core token logic.

This separation between functional behavior and authorization policy is particularly useful in long‑lived deployments, where governance requirements may change independently of the underlying token mechanics.


