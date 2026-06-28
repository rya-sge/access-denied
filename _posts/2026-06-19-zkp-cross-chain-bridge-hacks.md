---
layout: post
title: "Zero-Knowledge Proof Failures in Cross-Chain Bridges — Exploits, Vulnerabilities, and Bug Bounties"
date: 2026-06-19
lang: en
locale: en-GB
categories: blockchain security zkp defi
tags: zkp zero-knowledge-proof cross-chain bridge exploit bug-bounty rollup
description: An analysis of security incidents in ZK-rollup bridges from 2023 to 2026, covering confirmed exploits, circuit-level vulnerability disclosures, and bug bounties targeting ZK withdrawal and settlement mechanisms.
image: /assets/article/blockchain/zkp/2026-06-19-zkp-cross-chain-bridge-hacks-mindmap.png
isMath: true
---

ZK-rollup bridges are the settlement mechanism through which layer-2 (L2) transactions become final on layer-1 (L1). Unlike optimistic bridges, which use fraud proofs and a challenge window, ZK-rollup bridges use cryptographic proofs to assert the validity of state transitions on-chain. When these proofs are accepted by the L1 verifier, funds move. This article examines the confirmed exploits, disclosed vulnerabilities, and bug bounties that have targeted the ZK proof and settlement components of cross-chain ZK bridges from 2023 to 2026.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills.

[TOC]

## How ZK-Rollup Bridges Work

A ZK-rollup bridge settles L2 state on L1 through the following pipeline:

```
  Users (L2)
      │  submit transactions
      ▼
  Sequencer
      │  orders transactions, produces batches
      ▼
  Prover (ZK backend)
      │  generates ZK proof: valid(batch) = true
      ▼
  L1 Settlement Contract
      │  receives (batch_calldata, zk_proof)
      │  verifies ZK proof against public inputs
      │  if valid: updates L1 state root, enables withdrawals
      ▼
  User receives L1 funds via withdrawal claim
```

Each step is an attack surface:

- The **ZK circuit** must correctly encode the valid-batch predicate.
- The **public inputs** to the circuit must be correctly bound: L1 must not read parameters from calldata that the ZK proof did not constrain.
- The **L1 settlement contract** must correctly verify the proof and must not accept proofs it never ran.
- The **proof generation backend** (sequencer/prover) must not contain a code path that allows forging high bits of values before proof generation.

This article documents incidents in which one of these layers failed.

---

## Summary Table

| # | Protocol | Date | Loss / At Risk | Layer of Failure |
|---|----------|------|----------------|-----------------|
| 1 | Aztec Connect (June 2026) | Jun 14–15, 2026 | $2.28$M exploited | L1/L2 boundary: `numRealTxs` not in ZK public inputs |
| 2 | ZKSwap | Jul 9, 2025 | $5$M exploited | L1 settlement: `return true` in verifier |
| 3 | ZKSpace | ~Jul 2025 | ~$4$M exploited | L1 settlement: proxy contract exploit |
| 4 | zkSync Era RAM Permutation | Sep 15, 2023 | $0$ / $1.9$B at risk | ZK circuit: unconstrained upper 128 bits of memory writes |
| 5 | zkSync Lite Proof Verification | Oct 5, 2023 | $0$ / $200$K bounty | ZK circuit: unconstrained mantissa in withdrawal amount |
| 6 | Aztec Connect Claim Proof | Sep 12, 2023 | $0$ / $5$M TVL / $450$K bounty | ZK circuit: unconstrained remainder in proportional claim |

---

## Confirmed Exploits

### 1. [Aztec Connect — Settlement Boundary Bypass](https://slowmist.medium.com/analysis-of-the-2-19-million-asset-theft-from-aztec-connect-d867c59b1fc6) (June 14–15, 2026, $2.28$M)

**Vulnerable contract:** `0xff1f2b4adb9df6fc8eafecdcbf96a2b351680455` (RollupProcessorV3)  
**Attacker 1 EOA:** `0x0F18D8b44a740272f0be4d08338d2b165b7EdD17`  
**Attacker 2 EOA:** `0x7ec9F769d932D3f716949E7ca3E079b7817d06DB`  
**Chain:** Ethereum  
**Status:** $2.19$M unlaundered; ~$88$K laundered via Tornado Cash

#### Architecture

Aztec Connect was a ZK-rollup privacy bridge. Each rollup block contained up to 1,024 transaction rows across 32 inner-rollup slots. The ZK proof committed to all 32 slots by hashing the full `txData` payload via SHA-256.

On L1, the `processRollup()` function read a `numRealTxs` parameter directly from calldata and used it to bound the settlement loop:

```solidity
for (uint256 i = 0; i < numRealTxs; i++) {
    _processTransactionPair(state, txData, i);
}
```

The ZK circuit did not include `numRealTxs` as a public input. The proof attested to the entire `txData` array but placed no constraint on how many rows L1 would process.

#### Attack Mechanics

```
  Attacker-crafted rollup block:

  numRealTxs = 1  (read by L1 loop, NOT constrained by ZK proof)
  ┌─────────────────────────────────────────────────────────────────┐
  │ slot[0] : noop transaction (processed by L1 loop)               │
  │ slot[1] : deposit(attacker, 270,513 DAI)  ← L1 SKIPS           │
  │ slot[2] : deposit(attacker, 167.89 wstETH) ← L1 SKIPS          │
  │  ...                                                             │
  │ slot[31]: deposit(attacker, ...)           ← L1 SKIPS           │
  └─────────────────────────────────────────────────────────────────┘

  ZK proof: valid for all 32 slots (SHA-256 covers them all)
  L1 loop:  terminates at slot 0 (numRealTxs = 1)

  Result: L2 balance credited for slots 1–31, L1 never settled them
          => unbacked L2 balance created

  Then: submit valid withdrawal ZK proofs against L2 balance
        => drain real L1 funds
```

#### Timeline

- **12:26 UTC June 14** — First attack. Day 1 drained $2.19$M in DAI, wstETH, yvDAI, yvWETH, LUSD, and ETH in a single 4.5M-gas transaction.
- **12:30 UTC** — Aztec Labs identified the exploit internally.
- **13:52 UTC** — CertiK published an on-chain alert (74-minute delay after first attack).
- **04:00–05:17 UTC June 15** — Second attacker replicated the technique, draining ~$88$K.

#### Contributing Factors

A secondary issue: `processRollup()` had no on-chain access control enforced. Documentation described requirements for an authorized rollup provider, but the implementation accepted calls from arbitrary addresses. The protocol had been inactive for three years, with no team oversight of the live contracts.

#### Root Cause in One Sentence

`numRealTxs`, which determined how many transactions L1 processed and credited, was read from raw calldata rather than from the ZK proof's public inputs, decoupling the proof's commitment from L1's enforcement scope.

---

### 2. [ZKSwap — Dead Code in `verifyExitProof()`](https://www.blockaid.io/blog/how-zkswaps-5m-exploit-couldve-been-prevented-with-onchain-monitoring) (July 9, 2025, $5$M)

**Exploit contract:** `0x2D3103c8Fdd9d9411E24f555fdad6B22F29F613A`  
**Chain:** Ethereum

#### Architecture

ZKSwap was a ZK-rollup DEX and L2 bridge. Its standard operation used a ZK proof to settle batch withdrawals on L1. An additional emergency path, Exodus Mode, allowed individual users to prove a leaf in the L2 state tree and withdraw their funds independently, bypassing the batch mechanism.

The emergency exit function `verifyExitProof()` performed the ZK proof check for this path. It was deployed with the following logic:

```solidity
function verifyExitProof(
    bytes calldata storedBlockInfo,
    uint256 tokenId,
    uint128 amount,
    address owner,
    uint32 accountId,
    bytes calldata proof
) external view returns (bool) {
    return true;  // proof verification never executed

    // unreachable:
    uint256[] memory vk = getVerificationKey(tokenId);
    return Verifier.verify(vk, proof, storedBlockInfo);
}
```

#### Attack

The attacker activated Exodus Mode by calling the relevant trigger function, then submitted fabricated exit proofs for 15 different token IDs. Each call returned `true`. The `balancesToWithdraw` mapping credited the attacker for each accepted exit. The attacker called the standard `withdraw()` function 15 times and extracted $5$M in approximately 13 minutes (deployment at 14:12:35 UTC, first withdrawal at 14:25:23 UTC).

The rollup had been inactive since February 2025. The emergency exit code path had not been independently tested after its last revision.

#### Contributing Factor

Emergency exit paths in ZK-rollup bridges receive less routine coverage than normal operation paths. A single integration test asserting that an invalid proof is rejected would have detected this stub before deployment.

---

### 3. [ZKSpace — Proxy Contract Exploit](https://www.ainvest.com/news/zkspace-proxy-contract-exploited-4-million-stolen-2507/) (~July 2025, ~$4$M)

**Chain:** BNB Chain (funding) → Ethereum (drained)  
**Status:** ~$1.3$M laundered via Tornado Cash; ~$2.7$M distributed

ZKSpace was a ZK-rollup bridge. An address pre-funded through Tornado Cash executed a series of transactions targeting the ZKSpace proxy contract on Ethereum. Approximately $4$M was drained. The specific proxy vulnerability (upgrade mechanism misuse, storage slot collision, or delegatecall target replacement) was not publicly disclosed in available post-mortems.

This incident is categorized as a ZK-rollup bridge exploit where the failure layer was the proxy contract governance or upgrade path rather than the ZK circuit or settlement logic. The ZKSpaceOfficial X account was suspended at the time of the attack, and no official post-mortem was published.

---

## Disclosed Vulnerabilities and Bug Bounties

These three vulnerabilities were found by security researchers before exploitation, patched, and compensated with bug bounties. All three targeted the ZK circuits that underpin bridge withdrawal mechanisms.

---

### 4. [zkSync Era — RAM Permutation Soundness Bug](https://blog.chainlight.io/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8) (September 2023, $1.9$B at Risk)

**Discoverer:** ChainLight  
**Reported:** September 19, 2023  
**Bounty:** 50,000 USDC  
**TVL at risk:** ~$1.9$B  
**System:** EraVM ZK-EVM (Matter Labs)  
**Note:** First ZK circuit bug bounty ever claimed for zkSync Era.

#### The Vulnerability

EraVM processes 256-bit register values. The BN254 field supports only 253-bit elements. The RAM Permutation circuit decomposes each 256-bit memory value into:

- `value` (lower 192 bits, packed as `Num<E>`)
- `value_residual` (upper 64 bits, as `UInt64<E>`)

When constructing a `MemoryWriteQuery`, the upper 128 bits of the register value were handled as:

```rust
// In from_key_and_value_witness():
let [lowest_128, highest_128] = register_output.inner;

// Extract u64_word_2 and u64_word_3 from highest_128...
let u64_word_2 = UInt64::allocate_unchecked(cs, u64_word_2)?;  // no range check
let u64_word_3 = UInt64::allocate(cs, u64_word_3)?;

let mut lc = LinearCombination::zero();
lc.add_assign_number_with_coeff(&u64_word_2.inner, shifts[0]);
lc.add_assign_number_with_coeff(&u64_word_3.inner, shifts[64]);
lc.add_assign_number_with_coeff(&highest_128.inner, minus_one);
// BUG: lc is never enforced (no lc.enforce_zero(cs) or lc.into_num(cs))
```

The constraint `u64_word_2 + u64_word_3 * 2^64 == highest_128` was built as a `LinearCombination` but never added to the constraint system. The verifier circuit accepted any value for the upper 128 bits of any stored memory word.

#### Bridge Withdrawal Impact

The `L2EthToken` system contract handles ETH withdrawals from zkSync Era back to Ethereum. The `withdraw()` function stores `_amount` using misaligned `st.1` (store) instructions, which EraVM translates into two aligned `MemoryWriteQuery` entries:

```
Memory write 1 (address r1+56):
  value: (uint256(_to) << 64) | (_amount >> 192)

Memory write 2 (address r1+56 + 1):
  value: (_amount << 64)         ← high 128 bits are unconstrained
```

The second write's high 128 bits carry the upper portion of `_amount` in the L1 withdrawal message. Because these bits were unconstrained, a malicious prover could set them to an arbitrary value, forging a withdrawal message that claimed a large `_amount` while burning only a tiny ETH value on L2:

```
  Attacker burns:   0x133713371337 wei  ≈ 0.00002 ETH
  Forged message:   0x152d0000133713371337 wei ≈ 100,000 ETH
  L1 finalizes:     pays 100,000 ETH from bridge
```

The PoC required modifying the zkSync Era backend (`uma.rs` and `write_query.rs`) to detect a magic value and substitute the forged high bits before proof generation. Practical exploitation would have required compromising the sequencer backend or obtaining the private key, followed by a 21-hour execution delay.

**Fix:** Added `lc.enforce_zero(cs)` to enforce the constraint.

---

### 5. [zkSync Lite — Unconstrained Mantissa in Withdrawal Amount](https://medium.com/immunefi/zksync-insufficient-proof-verification-bugfix-review-dcd57944d0e2) (October 2023, $200$K Bounty)

**Discoverer:** LonelySloth  
**Reported:** October 5, 2023  
**Fixed:** November 7, 2023  
**Bounty:** $200,000$  
**System:** zkSync Lite (`franklin-crypto` library)

#### The Vulnerability

zkSync Lite uses a packed floating-point format to represent transaction amounts in calldata. Each amount is encoded as `mantissa * 10^exponent`, where both components are packed into a compact binary representation. The ZK circuit must verify that the on-chain packed representation corresponds exactly to the unpacked amount used in balance computations.

The decoding function `parse_with_exponent_le` in `franklin-crypto` allocated the mantissa using `AllocatedNum::alloc()`:

```rust
let mantissa = AllocatedNum::alloc(
    cs.namespace(|| "allocating mantissa"),
    || Ok(mantissa_value.get()?)
)?;
// No constraint links `mantissa` to packed_amount or exponent_result
mantissa.mul(cs.namespace(|| "calculate floating point result"), &exponent_result)
```

`AllocatedNum::alloc()` creates a private witness variable with no R1CS constraint on its value. The circuit then used this unconstrained mantissa in subsequent computations. Any `(packed_amount, unpacked_amount)` pair could produce a valid proof.

#### Bridge Withdrawal Impact

In zkSync Lite, transfers, swaps, and withdrawals all encode their amounts through this packed format. A prover with access to the backend could:

- **Forge withdrawal amounts:** Submit a packed withdrawal for 0.001 ETH but prove a withdrawal of 1,000 ETH, draining the L1 bridge.
- **Tamper with transfer amounts:** Alter the effective amount of any transfer without changing the on-chain calldata in a way detectable by the circuit.
- **Mint tokens:** Create balances on L2 without corresponding deposits.

**Fix:** Replaced `AllocatedNum::alloc()` with `mantissa_result.into_allocated_num(cs)`, which derives the mantissa from the computation and enforces the constraint linking it to the packed representation.

---

### 6. Aztec Connect — TurboPlonk Claim Proof Bug (September 2023, $450$K Bounty)

**Discoverer:** lucash-dev  
**Reported:** September 12, 2023  
**Fixed:** September 27–October 3, 2023  
**Bounty:** $450,000$  
**TVL at risk:** ~$5$M  
**System:** TurboPlonk (Aztec Connect claim proof circuit)

#### The Vulnerability

Aztec Connect routed user DeFi interactions through bridges, batching deposits and collecting output tokens for distribution. The claim proof circuit determined each user's share of bridge output using proportional allocation:

$$
\begin{aligned}
\text{user\_output} &= \left\lfloor \frac{\text{total\_input} \times \text{bridge\_output\_a}}{\text{bridge\_output\_b}} \right\rfloor \\
\text{remainder} &= (\text{total\_input} \times \text{bridge\_output\_a}) \bmod \text{bridge\_output\_b}
\end{aligned}
$$

Two constraint failures in the TurboPlonk circuit combined into a multiple-spend vulnerability:

**Failure 1 — Limb width too wide:**  
`limbs[3].create_range_constraint(68)` applied a 68-bit range check to the top limb of the decomposed value. Given the actual maximum of `user_output` relative to `total_input` and `MAX_INPUT_BITS`, the correct bound was significantly narrower. This left room for limb values that summed beyond the true maximum.

**Failure 2 — Remainder unconstrained:**  
The `remainder` variable was computed but had no range constraint. No constraint enforced `remainder < bridge_output_b`. A malicious sequencer could choose any `remainder` value, and the proportional formula would accept a correspondingly inflated `user_output` (up to `total_input`) without the proof failing.

```
  Normal proportional claim:
  user_output = floor(total_input × output_a / output_b)
  remainder   = (total_input × output_a) mod output_b  [0 ≤ remainder < output_b]

  Malicious claim (no constraint on remainder):
  user_output = total_input  (maximum possible)
  remainder   = anything     (no circuit check)
  => user drains entire output pool, other claimants receive nothing
```

#### Bridge Impact

Aztec Connect batched user interactions: multiple users deposited funds, the bridge interacted with DeFi protocols (Aave, Curve, etc.), and output tokens were distributed proportionally. A malicious sequencer could exploit the unconstrained remainder to assign the entire output to a single claim, leaving other users' claims invalid (multiple-spend at the circuit level).

**Fix:** Corrected limb bit widths based on `MAX_INPUT_BITS`; added constraint `remainder ∈ [0, bridge_output_b)`.

---

## Attack Surface Map for ZK-Rollup Bridges

```
  ZK-Rollup Bridge — Security Layers and Known Failure Points

  ┌─────────────────────────────────────────────────────────────────┐
  │  LAYER 1: ZK CIRCUIT                                            │
  │  • Under-constrained witnesses (zkSync Era, zkSync Lite)        │
  │  • Incorrect range constraints (Aztec claim proof)              │
  │  • Settlement parameter not in public inputs (Aztec Connect)    │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │ proof + calldata
  ┌──────────────────────────────▼──────────────────────────────────┐
  │  LAYER 2: L1 SETTLEMENT CONTRACT                                │
  │  • Dead verification code: return true (ZKSwap)                 │
  │  • Parameters read from calldata, not from ZK public inputs     │
  │  • No caller access control (Aztec Connect)                     │
  │  • Proxy upgrade path misuse (ZKSpace)                          │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │ on-chain state update
  ┌──────────────────────────────▼──────────────────────────────────┐
  │  LAYER 3: WITHDRAWAL EXECUTION                                  │
  │  • Unbacked L2 balance → legitimate withdrawal ZK proof         │
  │  • Forged amount in withdrawal message → L1 overpayment         │
  └─────────────────────────────────────────────────────────────────┘
```

---

## Vulnerability Patterns Specific to ZK Bridges

**Public input binding.** The Aztec Connect June 2026 exploit and the zkSync Era RAM Permutation bug share a structural pattern: a value that controls the scope or amount of a L1 settlement was not correctly bound to the ZK proof's public inputs. In the first case, `numRealTxs` was read from calldata. In the second, the upper bits of the withdrawal amount were in an unconstrained circuit variable. In both cases, the ZK proof was accepted as valid; the error was that the proof did not commit to the exploited parameter.

**Emergency exit code paths.** ZKSwap's $5$M loss resulted from a `return true` stub in the emergency Exodus Mode exit path, not the standard batch settlement path. Emergency paths are exercised rarely, receive fewer integration tests, and are modified during protocol adjustments without the same review cadence as the main path. The risk is proportional to the TVL held behind the bridge.

**Proof backend access as a prerequisite.** The zkSync Era RAM Permutation bug required modifying the EraVM backend before a proof was generated. In the current centralized sequencer model, this means compromising the backend or the sequencer private key. As zkSync Era and similar protocols move toward decentralized sequencer and prover networks, this prerequisite weakens, and the exploitability of such bugs increases.

**Dormant contracts retain live risk.** Two of the three confirmed exploits targeted deprecated or dormant systems: Aztec Connect (inactive three years) and ZKSwap (inactive since February 2025). Immutable contracts on Ethereum do not expire and do not stop holding user funds unless funds are explicitly withdrawn. A protocol that deprecates without draining retains full exploit exposure indefinitely.

---

## Comparative Analysis

The six incidents in this article span three failure modes:

| Failure Mode | Incidents | Total Confirmed Loss | Notes |
|---|---|---|---|
| ZK circuit soundness (undiscovered in prod) | ZKSwap*, Aztec Connect** | $7.28$M | *stub, not a circuit bug; **boundary bypass |
| ZK circuit soundness (disclosed pre-exploit) | zkSync Era, zkSync Lite, Aztec claim proof | $0$ | $700$K in bounties paid |
| Settlement/contract layer on ZK bridge | ZKSpace | ~$4$M | Proxy, not ZK |

(*ZKSwap's bug was in the verifier call, not the ZK circuit itself, but the effect was equivalent to a soundness failure.)

The disclosed-but-unexploited category represents approximately $1.9$B in at-risk TVL (zkSync Era alone) for bugs caught before exploitation. This is the expected outcome when active bug bounty programs cover circuit code at appropriate reward levels. The $700$K paid in bounties for three bugs stands against a potential loss that exceeds $1.9$B.

---

## Conclusion

ZK-rollup bridge security depends on the integrity of multiple layers, and each layer has failed in production. The most architecturally novel failures are those where the ZK proof was valid but the system was still exploited: the Aztec Connect June 2026 boundary bypass (the proof did not commit to `numRealTxs`) and the zkSync Era mantissa bug (the proof did not constrain the upper bits of withdrawal amounts). These incidents show that a correct ZK proof is a necessary but insufficient condition for bridge security. The proof must commit to all parameters that govern fund movement on L1.

The disclosed vulnerabilities demonstrate that production ZK bridge circuits contain exploitable soundness errors, and that bug bounty programs are a functional mechanism for finding them before exploitation. The three circuits that were fixed pre-exploitation (Aztec Connect claim proof, zkSync Era RAM Permutation, zkSync Lite mantissa) covered a combined at-risk value exceeding $1.9$B.

![ZK Bridge Security mindmap]({{site.url_complet}}/assets/article/blockchain/zkp/2026-06-19-zkp-cross-chain-bridge-hacks-mindmap.png)

## Frequently Asked Questions

**Q: What is the structural difference between the ZKSwap exploit and the zkSync Era bug?**

In the ZKSwap exploit, the ZK proof was never executed: the verifier function contained `return true` as its first statement, so no cryptographic check took place. The ZK system was bypassed entirely. In the zkSync Era bug, the ZK proof ran correctly and was accepted as valid, but the circuit failed to constrain the upper 128 bits of memory write values. The proof system was sound for the circuit as written; the problem was that the circuit did not correctly encode the property it was supposed to prove. Both result in the same practical outcome (forged withdrawal), but the root cause is structurally different: one is a dead-code stub, the other is a circuit soundness failure.

**Q: Why does the Aztec Connect June 2026 exploit qualify as a ZK security failure if the ZK proof was valid?**

The ZK proof was valid for the computation described by the circuit. However, the ZK circuit committed to all 32 transaction slots in a rollup block while the L1 settlement function read a separate `numRealTxs` parameter from calldata to determine how many slots to process. These two were not linked: the ZK proof did not include `numRealTxs` as a public input. The security requirement for a ZK bridge is that the L1 settlement processes exactly the transactions the proof attests to. When `numRealTxs` can be set independently of the proof, this requirement fails. The failure is a ZK bridge design error: a parameter governing fund movement was outside the proof's scope.

**Q: Could the zkSync Era RAM Permutation bug have been exploited without controlling the prover backend?**

No, not in the centralized configuration that existed at the time of disclosure. To exploit the bug, an attacker needed to modify the witness-generation code in the prover backend (`uma.rs` or `write_query.rs`) so that it substituted arbitrary high-bit values into memory write queries before generating the proof. This required either compromising the Matter Labs prover infrastructure or obtaining the sequencer's private key. The 21-hour execution delay between proof submission and L1 finalization provided an additional detection window. As zkSync Era progresses toward a decentralized prover network, the prerequisite of controlling the backend weakens: any permissioned prover in the network could potentially generate a malicious proof.

**Q: What is the role of the bug bounty program in ZK bridge security for the incidents in this article?**

Three bugs in this article were caught and patched before exploitation through responsible disclosure programs: Aztec Connect Claim Proof ($450$K bounty), zkSync Era RAM Permutation ($50$K USDC), and zkSync Lite Insufficient Proof Verification ($200$K). Combined, these three bugs put over $1.9$B in TVL at risk. The bounty payments totaled $700$K, which represents less than 0.04% of the at-risk value. The three exploited incidents (Aztec Connect June 2026, ZKSwap, ZKSpace) either did not have active circuit-level bounty programs covering the relevant code paths or the vulnerability was in contract/proxy logic rather than the circuit. The pattern suggests that circuit-level bounties with meaningful rewards are among the most cost-effective risk controls available to ZK bridge operators.

**Q: How can a ZK circuit team verify that all relevant parameters are correctly bound to public inputs?**

The procedure involves three steps. First, enumerate all parameters that govern fund movement on L1: iteration bounds, amount fields, recipient addresses, token identifiers. Second, for each parameter, trace whether it appears as a public input to the ZK circuit (i.e., the verifier contract checks it as part of the proof verification, not just reads it from calldata separately). Third, verify that the circuit constrains the relationship between the public input and the on-chain representation. Parameters that influence L1 behavior but are not in the circuit's public input set are potential attack vectors of the Aztec Connect type. This audit should be repeated after any change to the settlement function's calldata parsing logic or to the circuit's public input list.

**Q: Is a deprecated ZK bridge safe to leave unpaused on-chain?**

No. Smart contracts on Ethereum are immutable and continue to accept function calls and hold funds indefinitely unless a pause or self-destruct is explicitly implemented. Both ZKSwap and Aztec Connect were inactive for months or years before exploitation. The dormant period does not reduce exploit risk; it often increases it, because the security team's monitoring and response capacity diminishes, the on-chain state diverges from documentation, and the funds remain accessible to anyone who finds a vulnerability. The correct practice for a deprecated ZK bridge is to pause the contract, drain user funds to individual claimants or a safe multisig, and document a final state root. Leaving a dormant bridge on-chain with user funds is operationally equivalent to maintaining the full attack surface without the corresponding oversight.

## References

- [Aztec Connect Exploit Analysis — SlowMist](https://slowmist.medium.com/analysis-of-the-2-19-million-asset-theft-from-aztec-connect-d867c59b1fc6)
- [Aztec Connect — Rekt News](https://rekt.news/aztec-connect-rekt)
- [ZKSwap Exploit — Blockaid](https://www.blockaid.io/blog/how-zkswaps-5m-exploit-couldve-been-prevented-with-onchain-monitoring)
- [zkSync Era Soundness Bug — ChainLight](https://blog.chainlight.io/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8)
- [zkSync Lite Proof Verification Bugfix — Immunefi](https://medium.com/immunefi/zksync-insufficient-proof-verification-bugfix-review-dcd57944d0e2)
- [Aztec Connect Claim Proof Bug — HackMD](post-mortem/Aztec Connect Claim Proof Bug - HackMD.pdf)
- [Aztec Multiple-Spend Error Bugfix Review — Immunefi](post-mortem/Aztec Multiple-Spend Error Bugfix Review _ by Immunefi Editor _ Immunefi _ Medium.pdf)
- [ZKSpace Exploit — ainvest.com](https://www.ainvest.com/news/zkspace-proxy-contract-exploited-4-million-stolen-2507/)
- [SlowMist Hacked Database — Zone.pdf](slowmist/SlowMist Hacked - SlowMist Zone.pdf)
- [Claude Code](https://claude.com/product/claude-code)
