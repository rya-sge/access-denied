# LinkedIn Post - Flexible Access Control Pattern in CMTAT

---

**How do you build a token framework that works for everyone?**

On-chain security tokens don't all work the same way. Some issuers need role-based access control with multiple operators. Others just want a single owner to manage everything. And some need to plug into an external policy manager like OpenZeppelin's AccessManager or Chainlink ACE.

The challenge: how do you support all these models without duplicating your entire codebase?

We solved this by separating business logic from authorization.

In CMTAT, a security token framewok by CMTA, we apply a pattern inspired by OpenZeppelin's AccessManaged contract:

1. **Modules** define *what* operations exist (pause, mint, burn, etc.)
2. **Authorization hooks** define *who* can execute them
3. **Base contracts** wire the hooks to a specific policy

You can see what it looks like in the code snippet attached:



The module doesn't know if you're using roles, ownership, or an external manager. It calls `_authorizePause()` and expects the implementation to revert if unauthorized.

**What you get:**

- Reusability: Same module code across all deployments
- Auditability: Business logic and access control reviewed separately
- **Flexibility**: Swap RBAC for Ownable or AccessManager without touching token logic
- **Adaptability**: Change your access control model as your organization evolves

This pattern works beyond CMTAT. If you're building any open-source library where users need different access control models, it keeps your code clean and modular.

I wrote an article explaining the architecture, with code examples  and guidelines for extending the pattern.

Full article: [LINK]

Cde snappet made with carbon: https://carbon.now.sh/

#Solidity #SmartContracts #Ethereum #SecurityTokens #CMTAT #AccessControl #Web3 #Blockchain #OpenSource

---

**Character count**: ~1,850 characters
**Word count**: ~295 words

abstract contract PauseModule {
    modifier onlyPauseManager() {
        _authorizePause();
        _;
    }

    function pause() public onlyPauseManager {
        _pause();
    }
    
    // No policy here - just a hook
    function _authorizePause() internal virtual;
}
