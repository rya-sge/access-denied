# Defi Protocol - Protection Against MEV boot

## GMX V2

A unique technical characteristic of GMX is its two-step transaction process for key actions like swapping, opening/closing positions, and providing/removing liquidity. Instead of a single blockchain transaction confirming the action, GMX splits it into two:

1. **Request Transaction:** The user initiates and signs a transaction from their wallet. This transaction acts as a *request* submitted to the GMX protocol, signaling their intent to perform a specific action (e.g., open a long position).
2. **Execution Transaction:** The GMX protocol's infrastructure picks up this request and executes the intended action in a *separate, subsequent* blockchain transaction.

## How GMX Mitigates MEV (Maximal Extractable Value)

The primary reason for implementing the two-step transaction process is to protect users from Maximal Extractable Value (MEV), particularly front-running attacks.

MEV refers to the maximum value that can be extracted from block production beyond the standard block reward and transaction fees. In the context of DEXs, malicious actors (often called MEV bots or searchers) monitor pending transactions in the mempool. If GMX used a single-step process, a bot could see a user's large trade order before it's confirmed. The bot could then submit its *own* transaction with a higher gas fee to be executed *just before* the user's trade (front-running). This could slightly worsen the execution price for the user, allowing the bot to profit from the price impact.

By separating the user's request from the protocol's execution, GMX introduces a buffer. The protocol controls the timing and sequencing of the final execution transaction, making it significantly harder for MEV bots to reliably front-run user trades and thereby protecting users from this form of value extraction.

https://updraft.cyfrin.io/courses/gmx-perpetuals-trading/foundation/what-is-gmx