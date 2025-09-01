# How to Transfer Ether in Solidity (and Design a Safe `withdraw()`)

There are three main ways contracts move ETH: `transfer`, `send`, and low-level `call{value: ...}("")`. Each has different behavior for error handling, gas, and security—especially since gas repricing upgrades (e.g., EIP-1884) made “2300-gas-stipend” assumptions brittle. Below is a practical, security-minded guide with code you can lift into a `withdraw()` routine.

[TOC]



------

## `address.transfer(amount)`

- Sends ETH and **reverts on failure**. 
- Forwards a **fixed 2300 gas stipend** to the receiver’s `receive()`/`fallback()`.

**Why it’s risky today:** 

Any contract that needs more than 2300 gas in its receive path will make your transfer fail—creating a DoS footgun against your own logic (e.g., a “poisoned” payee). Gas repricing like **EIP-1884** changed opcode costs; future changes may, too, making fixed stipends unsafe to rely on. [Solidity Documentation+1](https://docs.soliditylang.org/en/latest/common-patterns.html?utm_source=chatgpt.com)[Consensys Diligence](https://diligence.consensys.io/blog/2019/09/stop-using-soliditys-transfer-now/?utm_source=chatgpt.com)

```
payable(to).transfer(amount); // reverts on failure, 2300 gas to receiver
```

**Pros**

- Simple and auto-reverting on failure.

**Cons**

- Hard dependency on the 2300 stipend; can break recipients or let them DoS you.
- Considered outdated for general use due to gas-assumption fragility. [Consensys Diligence](https://diligence.consensys.io/blog/2019/09/stop-using-soliditys-transfer-now/?utm_source=chatgpt.com)

------

##  `address.send(amount)`

- Sends ETH, **returns `false` on failure (no revert)**. 
- Also forwards only **2300 gas**.

**Why it’s rarely used:** You must check the boolean and handle errors yourself. It combines the stipend fragility with easier-to-ignore failures. [Ethereum Stack Exchange](https://ethereum.stackexchange.com/questions/6470/send-vs-call-differences-and-when-to-use-and-when-not-to-use?utm_source=chatgpt.com)

```
bool ok = payable(to).send(amount);
require(ok, "Send failed"); // many devs forget this check
```

**Pros**

- Never auto-reverts; you control failure handling.

**Cons**

- Same 2300-gas pitfalls as `transfer`.
- Easy to misuse by ignoring the return value. [Ethereum Stack Exchange](https://ethereum.stackexchange.com/questions/6470/send-vs-call-differences-and-when-to-use-and-when-not-to-use?utm_source=chatgpt.com)

------

## `to.call{value: amount}("")`

- Low-level call that can **forward custom gas** (by default it forwards *all remaining* gas) and returns `(success, returndata)`. 
- **You must check `success`** and decide whether to revert. 
- This is the modern default for value transfers. [DEV Community](https://dev.to/ceasermikes002/understanding-send-transfer-and-call-in-solidity-security-implications-and-preferences-4pog?utm_source=chatgpt.com)

```solidity
(bool ok, ) = to.call{value: amount}("");
require(ok, "ETH transfer failed"); // recommended pattern
```

**Pros**

- No 2300-gas limit; compatible with complex recipients.
- Lets *you* choose gas and failure policy; recommended over `transfer`/`send`. 

Reference: [Consensys Diligence - Stop Using Solidity's transfer() Now](https://diligence.consensys.io/blog/2019/09/stop-using-soliditys-transfer-now/)

**Cons**

- Because it can run complex code in the receiver, it **re-enables reentrancy risk** if your function isn’t structured safely.
- Slightly more verbose (must check the boolean).

------

## Gas perspective (what really matters)

- **2300-gas stipend**: `transfer` and `send` always forward 2300 gas to the receiver’s `receive()/fallback()`. That used to be “enough to log, not enough to reenter,” but gas repricing (e.g., **EIP-1884**) made the stipend unreliable and likely to break innocent recipients. **This is the core reason many auditors recommend avoiding `transfer`/`send`.** [Consensys Diligence](https://diligence.consensys.io/blog/2019/09/stop-using-soliditys-transfer-now/?utm_source=chatgpt.com)[Fellowship of Ethereum Magicians](https://ethereum-magicians.org/t/eip-1884-repricing-for-trie-size-dependent-opcodes/3024?utm_source=chatgpt.com)
- **`call` is future-proof**: you don’t bake in stipend assumptions; you can cap gas manually if you want to. [DEV Community](https://dev.to/ceasermikes002/understanding-send-transfer-and-call-in-solidity-security-implications-and-preferences-4pog?utm_source=chatgpt.com)

------

## Security perspective (designing `withdraw()`)

1. **Always use the Checks-Effects-Interactions (CEI) pattern**
   - **Checks**: validate inputs and entitlement
   - **Effects**: update internal state (zero the user balance)
   - **Interactions**: finally send ETH (external call)
      This minimizes reentrancy risk because the balance is set to 0 *before* you transfer. [ethereum.org](https://ethereum.org/en/developers/docs/smart-contracts/security/)
2. **Prefer Pull over Push**
    Instead of pushing ETH in loops or during state-changing flows, record credits and let users **call `withdraw()`** to pull their funds. This isolates failures and avoids mass-payout DoS. Libraries like OpenZeppelin’s **PullPayment** implement an escrowed version of this idea. [blog.openzeppelin.com](https://blog.openzeppelin.com/reentrancy-after-istanbul?utm_source=chatgpt.com)[OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/4.x/api/security)
3. **Guard reentrancy explicitly**
    Use CEI, and when appropriate, a mutex or OpenZeppelin’s **ReentrancyGuard** (`nonReentrant`). Be careful to avoid calling another `nonReentrant` function from a `nonReentrant` one. [OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/5.x/api/security)
4. **Keep `receive()`/`fallback()` tiny**
    If your contract must accept ETH directly, implement `receive()` for plain ETH and keep it trivial (log only). Complex logic belongs in explicit functions. [Solidity Documentation](https://docs.soliditylang.org/en/latest/contracts.html?utm_source=chatgpt.com)

------

## A robust `withdraw()` (pull-payments + `call` + CEI)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    mapping(address => uint256) public credits;

    // Users earn credits via your app logic...
    function credit(address user, uint256 amount) external {
        // access control omitted for brevity
        credits[user] += amount;
    }

    // Safe withdraw using CEI + call
    function withdraw(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");
        uint256 bal = credits[msg.sender];
        require(bal >= amount, "Insufficient credits");

        // EFFECTS
        credits[msg.sender] = bal - amount;

        // INTERACTION
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "ETH transfer failed");
    }
}
```

Why this design:

- **Pull pattern**: each user withdraws their own funds; one failing recipient doesn’t break others. [blog.openzeppelin.com](https://blog.openzeppelin.com/reentrancy-after-istanbul?utm_source=chatgpt.com)
- **CEI + nonReentrant**: state is reduced before the external call; reentrancy is blocked. [ethereum.org](https://ethereum.org/en/developers/docs/smart-contracts/security/?utm_source=chatgpt.com)[OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/4.x/api/security?utm_source=chatgpt.com)
- **`call`**: no 2300-gas brittleness, and we explicitly revert on failure. [DEV Community](https://dev.to/ceasermikes002/understanding-send-transfer-and-call-in-solidity-security-implications-and-preferences-4pog?utm_source=chatgpt.com)

------

## When *might* you still use `transfer`/`send`?

- **Extremely constrained scenarios** where you *want* the transfer to fail if the receiver isn’t trivial, and you accept the risk that future gas repricing could brick it. Even Solidity’s own docs caution that `transfer` can trap contracts if the recipient purposely or accidentally consumes more than the stipend. In general, auditors and the Solidity community now advise **against** making this assumption. [Solidity Documentation](https://docs.soliditylang.org/en/latest/common-patterns.html?utm_source=chatgpt.com)

------

## Practical checklist

- ✅ Default to **`call{value: amount}("")` + `require(success)`**. [DEV Community](https://dev.to/ceasermikes002/understanding-send-transfer-and-call-in-solidity-security-implications-and-preferences-4pog?utm_source=chatgpt.com)
- ✅ Structure state-changing flows with **CEI**; consider **`nonReentrant`** for functions that make external calls. [ethereum.org](https://ethereum.org/en/developers/docs/smart-contracts/security/?utm_source=chatgpt.com)[OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/4.x/api/security?utm_source=chatgpt.com)
- ✅ Use **pull-payments** (`withdraw()`), not push-payout loops. For shared revenue, check **OpenZeppelin PaymentSplitter**. [OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/3.x/api/payment?utm_source=chatgpt.com)
- ✅ Keep `receive()` and `fallback()` **minimal**; prefer explicit payable functions. [Solidity Documentation](https://docs.soliditylang.org/en/latest/contracts.html?utm_source=chatgpt.com)
- ❌ Avoid relying on **2300 gas** behavior (`transfer`/`send`); EVM gas can change. [Consensys Diligence](https://diligence.consensys.io/blog/2019/09/stop-using-soliditys-transfer-now/?utm_source=chatgpt.com)

------

## Summary tab

Here’s a concise **summary table** of Ether transfer methods in Solidity, including gas and security considerations:

| Method                       | Gas Behavior                                     | Error Handling           | Pros                                            | Cons / Risks                                                 | Recommended Use     |
| ---------------------------- | ------------------------------------------------ | ------------------------ | ----------------------------------------------- | ------------------------------------------------------------ | ------------------- |
| `address.transfer(amount)`   | Forwards **2300 gas**                            | **Reverts** on failure   | Simple syntax; auto-reverting                   | Breaks if receiver needs >2300 gas; can DoS withdrawals; brittle due to gas repricing (EIP-1884) | Avoid (legacy only) |
| `address.send(amount)`       | Forwards **2300 gas**                            | Returns **false**        | Lets you handle errors manually                 | Same 2300 gas pitfalls; easy to ignore return value; brittle under gas repricing | Avoid               |
| `to.call{value: amount}("")` | Forwards **all remaining gas** (or configurable) | Returns **(bool, data)** | Flexible, future-proof, recommended by auditors | Must check success explicitly; reentrancy risk if CEI pattern not followed |                     |



### References / Further reading

- **Consensys Diligence**: “Stop Using Solidity’s `transfer()` Now”. Why 2300-gas assumptions are dangerous; recommendation to use `call`. [Consensys Diligence](https://diligence.consensys.io/blog/2019/09/stop-using-soliditys-transfer-now/?utm_source=chatgpt.com)
- **Solidity docs**: `receive`/`fallback` behavior, 2300-gas stipend implications, and pitfalls of `transfer`. [Solidity Documentation+2Solidity Documentation+2](https://docs.soliditylang.org/en/latest/contracts.html?utm_source=chatgpt.com)
- **Ethereum.org (Security)**: CEI and reentrancy guidance. [ethereum.org](https://ethereum.org/en/developers/docs/smart-contracts/security/?utm_source=chatgpt.com)
- **OpenZeppelin**: ReentrancyGuard & PullPayment utilities; post-Istanbul reentrancy guidance. [OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/4.x/api/security?utm_source=chatgpt.com)[blog.openzeppelin.com](https://blog.openzeppelin.com/reentrancy-after-istanbul?utm_source=chatgpt.com)