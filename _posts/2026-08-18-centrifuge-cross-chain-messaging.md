---
layout: post
title: "Centrifuge Cross-Chain Messaging — Per-Pool Adapter Quorums, Batching and Failure Recovery"
date:   2026-08-18
lang: en
locale: en-GB
categories: blockchain security defi solidity
tags: BA-bridge cross-chain bridge centrifuge multi-adapter quorum layerzero wormhole axelar ccip messaging
description: How Centrifuge routes messages between chains - per-pool adapter sets, an n-of-m vote counter that tolerates duplicates, transient batching, gas subsidies, and the recovery paths.
image: /assets/article/blockchain/defi/cross-chain-bridge/2026-08-18-centrifuge-cross-chain-messaging-mindmap.png
isMath: true
---

Two earlier articles on this site examined cross-chain bridges from the outside: [ten incidents grouped into five failure classes](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-hacks/), and [a STRIDE threat model](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-threat-model/) of the assets and trust boundaries involved. This one goes the other way and reads a production implementation in detail. Centrifuge does not operate a bridge; it operates a protocol whose pools span several chains, and it treats the transport layer as replaceable. Messages travel over Axelar, Wormhole, LayerZero and Chainlink CCIP simultaneously, and a message is only executed once enough of them independently deliver it. This article follows a message end to end and examines the vote accounting, the batching and payment machinery, and what happens when any part of it fails.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The pipeline

A message crosses in seven hops, four on the source chain and three on the destination.

![Centrifuge messaging pipeline]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/centrifuge-messaging-pipeline-concept.png)

On the way out, a protocol contract calls `MessageDispatcher`, which serialises a typed struct into bytes. `Gateway` decides whether the message joins an in-progress batch or ships immediately, prices it through `GasService`, and pays for it. `MultiAdapter` fans the payload out to every adapter configured for that destination and pool. Each adapter hands it to its own transport.

On the way in, each transport delivers to its adapter, which authenticates the remote sender and forwards to `MultiAdapter`. Votes are counted there. Once the threshold is met the payload goes to `Gateway`, which splits the batch back into individual messages and executes each one through `MessageProcessor`, which deserialises and dispatches to the right handler.

`MultiAdapter` holds the trust assumption and `Gateway` holds the failure handling, so those two contracts carry most of what follows.

## The pool is the routing key

There are 26 message types. Five are pool-independent (`ScheduleUpgrade`, `CancelUpgrade`, `RecoverTokens`, `RegisterAsset`, `SetPoolAdapters`), and the remaining 21 carry a `PoolId` at byte offset 1, immediately after the one-byte type tag:

```solidity
function messagePoolId(bytes memory message) internal pure returns (PoolId poolId) {
    uint8 kind = message.toUint8(0);

    // All messages from NotifyPool to the end contains a PoolId in position 1.
    if (kind >= uint8(MessageType.NotifyPool)) {
        return PoolId.wrap(message.toUint64(1));
    }

    return PoolId.wrap(0);
}
```

The enum ordering is load-bearing. Because every pool-dependent type sorts after `NotifyPool`, a single comparison decides whether byte 1 holds a pool identifier, and the routing layer can extract it without a full deserialisation.

That identifier selects the adapter set:

```solidity
mapping(uint16 centrifugeId => mapping(PoolId => IAdapter[])) public adapters;
```

Each pool therefore chooses its own transports, per destination chain, and pool-independent messages resolve to pool 0, the protocol-wide set that `OpsGuardian.initAdapters` configures once per chain pair. There is no implicit fallback: `MultiAdapter.send` reverts with `EmptyAdapterSet` if the pool has no adapters configured for that destination, so a pool must either be given its own set through `Hub.setAdapters` or it cannot send.

`PoolId` is itself a composite, which is what allows the receiving side to verify provenance without a registry lookup:

```solidity
type PoolId is uint64;

function centrifugeId(PoolId poolId) pure returns (uint16) {
    return uint16(PoolId.unwrap(poolId) >> 48);
}
```

The top 16 bits name the chain the pool was created on, the low 48 bits are a local counter. `AssetId` uses the same layout in 128 bits.

## The vote counter

`MultiAdapter` holds at most `MAX_ADAPTER_COUNT = 8` adapters per pool and destination, with three configured parameters:

| Parameter | Meaning |
|-----------|---------|
| `quorum` | Number of configured adapters, set implicitly to the array length |
| `threshold` | How many distinct adapters must deliver before execution, at most `quorum` |
| `recoveryIndex` | Index at which the array switches from primary adapters to recovery adapters |

Each adapter is assigned a sequential id starting at 1, and the inbound state per payload hash is a small array:

```solidity
struct Inbound {
    /// @dev Counts are stored as integers (instead of boolean values) to accommodate duplicate
    ///      messages (e.g. two investments from the same user with the same amount) being
    ///      processed in parallel. The entire struct is packed in a single bytes32 slot.
    ///      Max int16 = 32,767 so at most 32,767 duplicate messages can be processed in parallel
    int16[MAX_ADAPTER_COUNT] votes;
    uint128 sessionId;
}
```

Counting votes rather than setting booleans is what makes duplicate messages safe. Two investors submitting identical requests produce byte-identical payloads and therefore the same hash, and a boolean map would silently merge them. With counters, the second copy accumulates its own votes and executes separately.

![MultiAdapter inbound vote accounting]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/centrifuge-adapter-quorum-workflow.png)

### Why the counters are signed

What happens after the threshold is reached is less obvious:

```solidity
if (state.votes.countPositiveValues(adapter.quorum) >= adapter.threshold) {
    state.votes.decreaseFirstNValues(adapter.quorum, adapter.recoveryIndex);
    gateway.handle(centrifugeId, payload);
}
```

```solidity
function decreaseFirstNValues(int16[8] storage arr, uint8 numValues, uint8 numValuesLowerZero) internal {
    for (uint256 i; i < numValues; i++) {
        if (i >= numValuesLowerZero && arr[i] <= 0) continue;
        arr[i] -= 1;
    }
}
```

Execution consumes one vote from every adapter in the quorum, not only from those that voted. An adapter below `recoveryIndex` is decremented unconditionally and goes negative, which records a debt: when its delivery finally arrives, the increment settles that debt rather than counting toward a fresh execution. Without it, a threshold of two out of three would execute on the first two deliveries and then execute a second time when the third arrived alongside a later duplicate.

Adapters at or above `recoveryIndex` are exempt, since the loop skips them when their count is not positive. A recovery adapter that stays idle accumulates no debt, so its vote remains available for the moment it is actually needed. A normal transport and a recovery transport are distinguished by nothing more than that `continue`.

### Reconfiguration invalidates history

`setAdapters` increments a global `lastSessionId` and stamps it on every adapter it installs. Inbound state carries the session it was accumulated under:

```solidity
if (adapter.activeSessionId != state.sessionId) {
    // Clear votes from previous session
    delete state.votes;
    state.sessionId = adapter.activeSessionId;
}
```

Partial votes collected under an old adapter set are discarded on first contact rather than being migrated. Removing a compromised adapter therefore also removes any half-finished consensus it participated in, which matters because ids are positional and a reused index would otherwise inherit the departed adapter's votes.

One optimisation is worth flagging when reviewing a deployment: a quorum of exactly one bypasses the vote machinery entirely and forwards straight to the gateway. Single-adapter configurations get no independent confirmation at all, which is a deployment choice rather than a protocol property.

## Batching in transient storage

Cross-chain calls are dominated by per-message overhead, so `Gateway` accumulates messages within a transaction and sends one payload per destination.

```solidity
bool public transient isBatching;
bool internal transient _isSendingBatch;
address internal transient _batcher;
```

The batch itself lives in transient storage keyed by destination and pool, with a parallel accumulator for the gas limit:

```solidity
function _outboundBatchSlot(uint16 centrifugeId, PoolId poolId) internal pure returns (bytes32) {
    return keccak256(abi.encode("outboundBatch", centrifugeId, poolId));
}
```

Since the slot is per `(chain, pool)` pair, messages for different pools never merge, and a locator for each pair is pushed onto a transient array the first time that pair is written. On close, the gateway walks the locators and sends one payload each. The inbound side re-checks the invariant while splitting: every message in a batch must report the same pool, or `MalformedBatch` reverts.

Batching is entered through a callback pattern rather than an explicit open and close:

```solidity
function withBatch(bytes memory data, uint256 callbackValue, address refund) public payable {
    ...
    _batcher = msg.sender;
    (bool success, bytes memory returnData) = msg.sender.call{value: callbackValue}(data);
    ...
    // Force the user to call lockCallback()
    require(address(_batcher) == address(0), CallbackWasNotLocked());
```

The caller must clear `_batcher` from inside the callback via `lockCallback`, which only the original caller can do. A contract that fails to lock reverts the whole batch. Combined with `_isSendingBatch`, which rejects any new message while accumulated batches are being dispatched, this closes the reentrancy paths around a partially built batch.

Batches are bounded. Each message's gas limit is added to a running total that must stay under `maxBatchGasLimit(centrifugeId)`, a per-chain block-capacity figure packed one byte per chain into a single immutable word and expressed in millions of gas. A batch that would exceed the destination chain's practical limit reverts at build time with `BatchTooExpensive`, rather than becoming an undeliverable payload.

## Paying for delivery

`GasService` stores a benchmarked gas figure for every message type, regenerated by a script in the repository:

```solidity
notifyShareClass = _gasValue(1883390);
updateVaultDeployAndLink = _gasValue(2866252);
requestCallback = _gasValue(355279); // approve deposit case
```

Each is inflated for the calls made on the way in:

$$
\begin{aligned}
G_{\text{overall}} = \left(G_{\text{process}} + G_{\text{base}}\right) \cdot \frac{64^3}{63^3}
= \left(G_{\text{process}} + G_{\text{base}}\right) \cdot \frac{262144}{250047}
\end{aligned}
$$

The cube is deliberate. EIP-150 forwards at most 63/64 of remaining gas per call, and the inbound path crosses three call boundaries (executor to adapter, adapter to `MultiAdapter`, `MultiAdapter` to `Gateway`), so the reserve has to survive three applications of that rule. `BASE_COST` of 75,000 covers the gateway and multi-adapter work itself, and `PROCESS_FAIL_MESSAGE_GAS` of 35,000 is held back so a failing message still has enough gas to record its own failure.

Three payment routes exist.

- **Direct.** The caller sends native value; `Gateway` estimates the cost across all adapters, forwards it, and returns the remainder to a caller-specified refund address.
- **Pool subsidy.** `SubsidyManager` holds a `RefundEscrow` per pool that anyone can top up with `deposit(poolId)`. Authorised protocol contracts pull from it, which is how an investor's cross-chain request gets paid for without the investor holding gas on both chains.
- **Unpaid mode.** When `unpaidMode` is set and the value is short, the batch is not dropped. It is recorded as underpaid and can be settled later by anyone:

```solidity
struct Underpaid {
    uint128 gasLimit;
    uint64 counter;
}
```

`repay` decrements the counter and re-attempts the send at the originally recorded gas limit. The counter, again, exists so identical batches queued more than once are settled once each.

## Executing on arrival

The inbound gateway splits the batch and processes each message under an explicit gas reservation:

```solidity
uint128 gasLimit = messageProperties.messageProcessingGasLimit(localCentrifugeId, message);
require(gasleft() >= gasLimit, NotEnoughGas());

_safeProcess(centrifugeId, message, messageHash, gasLimit);
```

Execution is deliberately isolated:

```solidity
(bool success, bytes memory err) = address(processor)
    .excessivelySafeCall(
        gasLimit - PROCESS_FAIL_MESSAGE_GAS,
        0,
        ERR_MAX_LENGTH,
        abi.encodeWithSelector(IMessageHandler.handle.selector, centrifugeId, message)
    );

if (success) {
    emit ExecuteMessage(centrifugeId, messageHash);
} else {
    failedMessages[centrifugeId][messageHash]++;
    emit FailMessage(centrifugeId, messageHash, err);
}
```

`excessivelySafeCall` caps copied return data at 128 bytes, which defeats the return bomb where a handler returns megabytes of data to force an out-of-gas in the caller. More importantly, a failing message does not revert the batch. It increments a counter and the loop continues, so one bad message cannot block the twenty behind it.

Recovery is then permissionless:

```solidity
function retry(uint16 centrifugeId, bytes memory message) external pauseable {
    bytes32 messageHash = keccak256(message);
    require(failedMessages[centrifugeId][messageHash] > 0, NotFailedMessage());

    failedMessages[centrifugeId][messageHash]--;
    processor.handle(centrifugeId, message);
    ...
}
```

Anyone may retry a message that previously failed, and only such a message: the counter is the authorisation. Note that `retry` calls the processor directly with no gas cap, so a message that failed on gas can succeed on a second attempt with a larger transaction, while a message failing on logic simply fails again and the counter stays consumed only on success, since the call reverts before the decrement is committed.

## What the adapters actually verify

The four transport adapters are thin and share a shape. Each holds an immutable `entrypoint`, a wiring map in both directions, and validates two things on receive: that the caller is the expected local transport contract, and that the remote sender matches the wired counterpart for that source chain.

```solidity
WormholeSource memory source = sources[sourceWormholeId];
require(source.addr != address(0) && source.addr == sourceAddress.toAddressLeftPadded(), InvalidSource());
require(msg.sender == address(relayer), NotWormholeRelayer());
```

Sending is symmetric: `require(msg.sender == address(entrypoint), NotEntrypoint())`, so only `MultiAdapter` can emit through an adapter. Each also carries a `RECEIVE_COST` constant for its own delivery overhead, which is added to the gas limit passed downstream: 70,000 for Wormhole, 26,000 for Axelar, 4,000 for both LayerZero and CCIP.

Wiring is one-shot per chain, guarded at the guardian level:

```solidity
function wire(address adapter, uint16 centrifugeId, bytes memory data) external onlySafe {
    require(!IAdapterWiring(adapter).isWired(centrifugeId), AdapterAlreadyWired());
    IAdapterWiring(adapter).wire(centrifugeId, data);
}
```

Rewiring a live adapter to a different remote address is therefore not an available operation, which removes a class of governance mistake. Replacing a transport means installing a different adapter through `setAdapters`, which invalidates pending votes as a side effect.

## Emergency controls

Four mechanisms operate at different granularities.

- **`RecoveryAdapter`** is an adapter that implements `send` as a no-op returning empty data, and `handle` as an `auth`-gated injection into the entrypoint. It can introduce a message into the protocol without any transport having carried it, and it can never emit one. Placed at or above `recoveryIndex`, it supplies the missing vote when a transport is down or has censored a payload, without accumulating debt while unused.
- **`blockOutgoing(centrifugeId, poolId, isBlocked)`** stops outbound traffic for one pool toward one chain. `ProtocolGuardian` uses it with pool 0 for the protocol-wide case; a pool manager can invoke it for their own pool.
- **Global pause** gates `handle`, `send`, `retry` and `repay` through a `pauseable` modifier reading `Root.paused()`.
- **Source authentication** in `MessageProcessor` restricts privileged message types by origin. Upgrade scheduling, upgrade cancellation and token recovery are accepted only from `MAINNET_CENTRIFUGE_ID`, and asset registration and adapter configuration only from the chain encoded in the identifier they carry:

```solidity
} else if (kind == MessageType.SetPoolAdapters) {
    MessageLib.SetPoolAdapters memory m = message.deserializeSetPoolAdapters();
    require(centrifugeId == PoolId.wrap(m.poolId).centrifugeId(), OnlyFromSource());
```

That check is the reason the chain identifier is embedded in `PoolId` and `AssetId` rather than kept in a registry. A compromised spoke cannot reconfigure another pool's adapters, because the pool identifier itself declares which chain is allowed to speak for it.

## Reading the design against the threat model

Mapping the mechanisms onto the failure classes from the earlier articles gives a compact summary of what is and is not covered.

| Failure class | Mechanism | Residual exposure |
|---------------|-----------|-------------------|
| Single verifier compromise | n-of-m adapter threshold over independent transports | A configuration with quorum 1, which bypasses voting entirely |
| Forged or replayed message | Per-payload vote accounting with signed counters, plus per-adapter source authentication | Correlated compromise of `threshold` transports |
| Privileged message from the wrong chain | `OnlyFromMainnet` and `OnlyFromSource` checks against the identifier's embedded chain | Compromise of the mainnet hub itself |
| Stuck or failing message | Failure counter plus permissionless `retry`, underpaid batches plus `repay` | A message that fails deterministically on logic |
| Transport outage or censorship | `RecoveryAdapter` injection, exempt from vote debt | Requires an authorised party to act |
| Malicious handler return data | `excessivelySafeCall` with a 128-byte copy cap | None material at this layer |
| Runaway or unwanted traffic | Per-pool `blockOutgoing`, global pause, per-chain batch gas ceiling | Governance latency |

The honest reading is that the trust assumption has been moved rather than eliminated. A message is as safe as the assumption that `threshold` of the configured transports do not fail together, and each of those transports has its own validator set with its own history. What the design does buy is that the assumption is explicit, configurable per pool, and revocable without redeploying anything.

## Conclusion

Centrifuge's messaging layer treats transports as interchangeable and puts the security decision in one contract. `MultiAdapter` decides how many independent deliveries a payload needs before the protocol acts on it, and that number is set per pool and per destination rather than protocol-wide. Around it, `Gateway` handles the operational realities: batching within a transaction, pricing from benchmarked per-type gas figures, subsidised payment so end users need no gas on the destination chain, and a failure counter that keeps one bad message from blocking a batch.

Three implementation details do more work than their size suggests. Signed vote counters make duplicate payloads safe and prevent a late delivery from triggering a second execution. Session identifiers discard partial consensus when the adapter set changes. The `recoveryIndex` split exempts recovery adapters from vote debt, which is what lets a standby transport sit idle and still be usable the moment it is needed.

![Centrifuge cross-chain messaging mindmap]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-08-18-centrifuge-cross-chain-messaging-mindmap.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Adapter** | A contract wrapping one transport (Axelar, Wormhole, LayerZero, CCIP), responsible for sending a payload and authenticating incoming deliveries from its wired counterpart. |
| **Quorum** | The number of adapters configured for a given destination chain and pool, set implicitly to the length of the adapter array, capped at eight. |
| **Threshold** | How many distinct adapters must deliver the same payload before it is executed; at most the quorum. |
| **Recovery index** | The array position at which adapters stop being decremented unconditionally after an execution, marking them as standby transports. |
| **Session identifier** | A counter stamped on every adapter when a set is installed, used to discard votes accumulated under a previous configuration. |
| **Centrifuge id** | A 16-bit chain identifier embedded in the high bits of `PoolId` and `AssetId`, letting a receiver check which chain is entitled to send a given privileged message. |
| **Locator** | A packed destination-and-pool key pushed to a transient array so the gateway knows which accumulated batches to dispatch when batching ends. |
| **Underpaid batch** | A batch whose sender did not cover the estimated cost, recorded with its gas limit and a counter so anyone can settle it later through `repay`. |
| **Subsidy** | Native value held in a per-pool `RefundEscrow` that authorised protocol contracts draw on to pay messaging costs on a user's behalf. |
| **Recovery adapter** | An adapter that cannot send and whose `handle` is authority-gated, used to inject a message directly when a transport is unavailable. |

## Annex — Security Implementation Checklist

The items below are the properties an n-of-m cross-chain messaging layer has to hold for its trust assumption to mean what it claims. Each is stated as a requirement, paired with what breaks when it is violated.

### Consensus over transports

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Delivery counts are per adapter and per payload, never a single shared counter. | One compromised transport delivering repeatedly reaches the threshold alone. |
| ☐ | Counters are signed, and an execution consumes one vote from every non-recovery adapter in the quorum. | A late delivery from a slow adapter combines with a duplicate payload to execute the message twice. |
| ☐ | Counters, not booleans, so byte-identical payloads accumulate independently. | Two legitimate identical requests are merged and one is silently dropped. |
| ☐ | Changing the adapter set invalidates votes accumulated under the old set. | A newly installed adapter inherits the positional votes of the one it replaced. |
| ☐ | An adapter must be registered for the exact destination chain and pool whose message it delivers. | An adapter authorised for one pool injects messages on behalf of another. |
| ☐ | Deployments with a threshold of one are treated as trusted-transport deployments, not verified ones. | A configuration that bypasses the vote path entirely is mistaken for an n-of-m guarantee. |

### Message authenticity and scope

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each adapter verifies both the local transport caller and the wired remote sender. | Any contract on the source chain can inject payloads through the transport. |
| ☐ | Only the multi-adapter entrypoint may cause an adapter to emit. | An arbitrary caller sends protocol-shaped messages at the pool's expense. |
| ☐ | Privileged message types are accepted only from the chain entitled to send them, checked against the identifier the message carries. | A compromised spoke schedules an upgrade or reconfigures another pool's transports. |
| ☐ | Every message in a batch is verified to belong to the same pool during the inbound split. | A batch mixes pools, so a routing decision made once is wrong for part of the payload. |
| ☐ | Adapter wiring for a given chain is one-shot and cannot be silently repointed. | A governance action redirects a live adapter to an attacker-controlled counterpart. |

### Execution and liveness

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Handler execution is isolated so one failing message does not revert the whole batch. | A single malformed message blocks every message queued behind it, indefinitely. |
| ☐ | Return data from the handler is copied under a fixed cap. | A handler returning very large return data forces an out-of-gas in the caller. |
| ☐ | Remaining gas is checked against the message's requirement before each execution, with a reserve held back for recording failure. | A message runs out of gas mid-execution and its failure is never recorded, so it cannot be retried. |
| ☐ | Retry is limited to messages that actually failed, tracked by a counter that decrements once per successful retry. | Arbitrary messages can be replayed, or a failed message can be executed more times than it was delivered. |
| ☐ | Batch gas totals are capped against the destination chain's capacity at build time. | An oversized batch is paid for and dispatched but can never be executed on arrival. |
| ☐ | A recovery path exists that can inject a message without any transport, and it can never emit one. | A transport outage permanently strands a pool, or the recovery path becomes a second unmonitored sender. |

## Frequently Asked Questions

**Q: Why are the vote counters signed integers rather than unsigned counts?**

Because an execution consumes a vote from every adapter in the quorum, including those that have not delivered yet. Those adapters go to minus one, recording that their eventual delivery is already accounted for. When it arrives, the increment brings them back to zero rather than to one, so it cannot contribute to a second execution. With unsigned counters the protocol would either have to skip absent adapters, which lets a late delivery combine with a duplicate payload to execute twice, or track delivery separately at a higher storage cost.

**Q: What exactly does `recoveryIndex` change about an adapter's behaviour?**

Only whether it is decremented when it has not voted. The decrement loop skips any index at or above `recoveryIndex` whose count is not positive, so a recovery adapter never accumulates debt while idle.

The consequence is operational rather than cryptographic. A standby transport can sit unused across many messages and still have a usable vote the moment it is needed, whereas a primary adapter that has been offline for ten messages carries a debt of ten and would have to deliver eleven times before contributing again.

**Q: A message arrives, the threshold is met, but the handler reverts. What is the state afterwards, and who can fix it?**

The batch continues. The gateway records the failure rather than propagating it:

- `failedMessages[centrifugeId][messageHash]` is incremented, and a `FailMessage` event is emitted carrying up to 128 bytes of the revert data.
- Remaining messages in the same batch are still executed, so the failure is isolated to one message.
- Anyone may then call `retry` with the exact message bytes, which is authorised solely by that counter being positive.

Retry calls the processor directly without a gas cap, so a message that failed because the reserved gas was insufficient can succeed in a larger transaction. One that fails deterministically will keep failing, and its counter stays where it is because the call reverts before the decrement is committed.

**Q: How does a pool with no native token on the destination chain pay for its messages?**

Through `SubsidyManager`, which holds a `RefundEscrow` per pool. Anyone can fund a pool by sending value to `deposit(poolId)`, and authorised protocol contracts withdraw from it when a message needs paying for. In the asynchronous vault path, the request manager pulls the whole balance before dispatching and passes the escrow as the refund address, so the unused remainder returns immediately.

If the subsidy is insufficient and the caller set `unpaidMode`, the batch is recorded as underpaid with its gas limit rather than reverting, and any third party can settle it later with `repay`.

**Q: Why is the chain identifier packed into `PoolId` rather than stored in a registry?**

So that provenance can be checked from the message alone. The top 16 bits of the 64-bit `PoolId` name the chain the pool was created on, which lets `MessageProcessor` enforce that a `SetPoolAdapters` message came from the pool's own hub with a single comparison, before any state lookup. A registry would work but would need to be populated by an earlier cross-chain message, which is circular for exactly the configuration messages that most need the check.

**Q: The protocol sends over four transports at once. Under what circumstances is that still not enough, and what would a reviewer look at first?**

The guarantee is that `threshold` of the configured adapters must be compromised or must independently deliver a forged payload. That is weakest when the transports are not as independent as they appear, so the first thing to check is the actual configuration rather than the code.

- The quorum and threshold for the pool and destination in question, since a threshold of one skips the vote path entirely and a threshold equal to one out of two is barely stronger.
- How many configured adapters are genuinely distinct systems, as opposed to different products sharing validators, relayers, or an underlying attestation service.
- Where `recoveryIndex` sits, because adapters above it are standby transports and should not be counted toward everyday security.
- Whether the recovery adapter's authority is held by the same entity that controls the guardian, which would collapse two supposedly separate recovery paths into one.

The code enforces the arithmetic correctly. Whether the arithmetic means anything depends entirely on the independence of the transports someone chose.

## References

### Related articles on this site

- [Cross-Chain Bridge Hacks: Ten Incidents, Five Failure Classes](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-hacks/)
- [Cross-Chain Bridge Threat Model: Assets, Trust Boundaries, STRIDE and Threat Register](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-threat-model/)
- [How Centrifuge Vaults Work: Asynchronous ERC-7540 Investment on a Hub-and-Spoke Protocol](https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-vaults/)

### Transports

- [Axelar General Message Passing](https://docs.axelar.dev/dev/general-message-passing/overview/)
- [Chainlink CCIP documentation](https://docs.chain.link/ccip)
- [LayerZero V2 documentation](https://docs.layerzero.network/v2)
- [Wormhole Relayer documentation](https://wormhole.com/docs/build/contract-integrations/wormhole-relayers/)

### Specifications and prior art

- [EIP-150: Gas cost changes for IO-heavy operations](https://eips.ethereum.org/EIPS/eip-150)
- [EIP-1153: Transient storage opcodes](https://eips.ethereum.org/EIPS/eip-1153)
- [nomad-xyz/ExcessivelySafeCall](https://github.com/nomad-xyz/ExcessivelySafeCall)

### Protocol documentation

- [Centrifuge developer documentation](https://docs.centrifuge.io/)
- [Chain abstraction](https://docs.centrifuge.io/developer/protocol/features/chain-abstraction/)
- [Security reviews and audit reports](https://docs.centrifuge.io/developer/security/audits)

### Analyzed source

- [centrifuge/protocol](https://github.com/centrifuge/protocol) — analyzed at commit [`a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1`](https://github.com/centrifuge/protocol/tree/a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1) (no release tag on this commit; it follows the `deploy-testnet-v3.2` tag), 2026-08-18
