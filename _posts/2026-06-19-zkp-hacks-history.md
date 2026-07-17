---
layout: post
title: "Zero-Knowledge Proof Hacks — A Documented Record of Exploits and Vulnerabilities (2023–2026)"
date: 2026-06-19
lang: en
locale: en-GB
categories: blockchain security defi ZKP
tags: zkp zero-knowledge-proof exploit hack vulnerability bug-bounty
description: A chronological record of confirmed hacks, disclosed vulnerabilities, and bug bounties in zero-knowledge proof protocols from 2023 to 2026, with technical root cause analysis for each incident.
image: /assets/article/blockchain/zkp/2026-06-19-zkp-hacks-history-mindmap.png
isMath: true
---

Zero-knowledge proof (ZKP) systems have been deployed in production with billions of dollars in TVL since 2021. As adoption has grown, so has the number of security incidents touching ZK cryptography directly or ZK-rollup infrastructure. This article documents the confirmed exploits, disclosed vulnerabilities, and notable bug bounties from 2023 to 2026, organized chronologically with technical root cause analysis.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills.

[TOC]

## Scope and Classification

Incidents are grouped into three categories:

- **Part I — Direct ZK Cryptography Exploits:** the vulnerability resided in the ZK proof system (circuit, verification key, proof transcript, settlement boundary).
- **Part II — ZK-Rollup Protocol Exploits:** the bug was in surrounding contract logic rather than the proof itself, but ZK infrastructure was integral to the attack surface.
- **Part III — Disclosed Vulnerabilities (No Exploitation):** responsibly disclosed, patched before exploitation, and in several cases rewarded with a bug bounty.

The **ZK Bug?** column in the summary table uses three values: ✅ (ZK proof system directly vulnerable), ⚠️ (ZK chain or rollup, but contract-level bug), ❌ (ZK-branded protocol, DeFi bug only).

---

## Summary Table

| # | Protocol | Date | Loss / Risk | Category | ZK Bug? |
|---|----------|------|-------------|----------|---------|
| 1 | Aztec Connect Claim Proof | Sep 12, 2023 | $0$ / $5$M TVL / $450$K bounty | TurboPlonk unconstrained limbs | ✅ |
| 2 | zkSync Era RAM Permutation | Sep 15, 2023 | $0$ / $1.9$B at risk / 50K USDC bounty | EraVM unconstrained 128 bits | ✅ |
| 3 | zkSync Lite Proof Verification | Oct 5, 2023 | $0$ / $200$K bounty | Unconstrained mantissa | ✅ |
| 4 | Solana ZK ElGamal Bug #1 | Apr 16–18, 2025 | $0$ (patched) | Fiat-Shamir binding failure | ✅ |
| 5 | Haven Protocol | Dec 10, 2024 | Unlimited XHV mint | Range proof validation flaw | ✅ |
| 6 | zkLend | Feb 11, 2025 | $9.57$M | Precision loss (StarkNet) | ❌ |
| 7 | ZKSwap | Jul 9, 2025 | $5$M | `return true` verifier stub | ✅ |
| 8 | ZKSpace | ~Jul 2025 | ~$4$M | Proxy contract exploit | ⚠️ |
| 9 | Solana ZK ElGamal Bug #2 | Jun 10, 2025 | $0$ (patched) | Fiat-Shamir transcript incomplete | ✅ |
| 10 | OtterSec — 6 zkVMs | Sep 2025–Mar 2026 | $0$ (all patched) | Fiat-Shamir binding failure | ✅ |
| 11 | dYdX Supply Chain | Jan 27–28, 2026 | Unknown | npm/PyPI credential compromise | ❌ |
| 12 | Veil Cash | Feb 20, 2026 | ~$5$K | Groth16 trusted setup broken | ✅ |
| 13 | FoomCash | Feb 26, 2026 | $2.26$M ($420$K net) | Groth16 trusted setup broken | ✅ |
| 14 | HermesVault | May 19, 2026 | $29,466$ | ZK verification key-reset bypass | ✅ |
| 15 | Aztec Connect Bridge | Jun 14–15, 2026 | $2.28$M | ZK settlement boundary bypass | ✅ |

---

## Part I — Direct ZK Cryptography Exploits

### 1. Aztec Connect — Claim Proof Bug (TurboPlonk)

**Date:** September 12, 2023 (disclosed) / September 27–October 3, 2023 (fixed)  
**Loss:** $0$ (no exploitation)  
**TVL at risk:** ~$5$M  
**Bounty:** $450,000$  
**Discoverer:** lucash-dev  
**System:** TurboPlonk (Aztec Connect claim proof circuit)

**Technical detail:**

The claim proof circuit handled proportional token distribution from DeFi interactions routed through Aztec Connect's bridge. It decomposed a 252-bit value into 4 limbs for range checking. Two separate constraint failures combined into a multiple-spend vulnerability:

1. `limbs[3].create_range_constraint(68)` allowed a 68-bit range regardless of the actual maximum derivable from `MAX_INPUT_BITS`. The correct bound was much narrower.
2. The `remainder` variable in the proportional allocation had **no range constraint at all**:

$$
\begin{aligned}
\text{user\_output} &= \left\lfloor \frac{\text{total\_input} \times \text{bridge\_output\_a}}{\text{bridge\_output\_b}} \right\rfloor \\
\text{remainder} &= (\text{total\_input} \times \text{bridge\_output\_a}) \bmod \text{bridge\_output\_b}
\end{aligned}
$$

Because `remainder` was unconstrained, a malicious sequencer could choose any `remainder` value and correspondingly manipulate `user_output` upward, up to `total_input`, without the proof failing. This enabled multiple-spend across shared output tokens.

**Fix:** Narrowed `limbs[3]` based on `MAX_INPUT_BITS`; added constraint `remainder ∈ [0, bridge_output_b)`.

---

### 2. [zkSync Era — RAM Permutation Soundness Bug](https://blog.chainlight.io/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8)

**Date:** September 15, 2023 (discovered) / September 19, 2023 (reported)  
**Loss:** $0$ (no exploitation)  
**TVL at risk:** ~$1.9$B  
**Bounty:** 50,000 USDC (first ZK circuit bounty paid for zkSync Era)  
**Discoverer:** ChainLight  
**System:** EraVM ZK-EVM (Matter Labs)

**Technical detail:**

EraVM stores 256-bit register values but the BN254 proving field supports only 253-bit elements. The RAM Permutation circuit decomposes each value into `value` (lower 192 bits) and `value_residual` (upper 64 bits). When constructing a `MemoryWriteQuery`, the upper 128 bits were computed via a `LinearCombination` in `from_key_and_value_witness`:

```rust
lc.add_assign_number_with_coeff(&u64_word_2.inner, shifts[0]);
lc.add_assign_number_with_coeff(&u64_word_3.inner, shifts[64]);
lc.add_assign_number_with_coeff(&highest_128.inner, minus_one);
// Neither lc.enforce_zero(cs) nor lc.into_num(cs) was called
```

The `LinearCombination` was built but never enforced. The upper 128 bits of every stored memory value were completely unconstrained. A malicious prover could modify `_amount` in the packed `L2EthToken.withdraw()` representation to forge a withdrawal message claiming ~100,000 ETH while burning approximately 0.00002 ETH. The L1 `IMailbox.finalizeEthWithdrawal` would have paid out from the bridge.

Practical exploitation required either compromising the zkSync Era backend or stealing the sequencer private key, and surviving the 21-hour execution delay. The decentralization trajectory makes this constraint increasingly important.

**Fix:** Added `lc.enforce_zero(cs)` to enforce the LinearCombination.

---

### 3. [zkSync Lite — Insufficient Proof Verification](https://medium.com/immunefi/zksync-insufficient-proof-verification-bugfix-review-dcd57944d0e2)

**Date:** October 5, 2023 (disclosed) / November 7, 2023 (fixed)  
**Loss:** $0$ (no exploitation)  
**Bounty:** $200,000$  
**Discoverer:** LonelySloth  
**System:** zkSync Lite (`franklin-crypto` library)  
**Note:** Unrelated to zkSync Era.

**Technical detail:**

zkSync Lite encodes transaction amounts in a packed floating-point format: `amount = mantissa * 10^exponent`. The circuit must verify that the on-chain packed representation correctly encodes the amount used in the ZK computation. The `parse_with_exponent_le` function in `franklin-crypto` allocated the mantissa variable without any constraint:

```rust
// Before fix — no constraint:
let mantissa = AllocatedNum::alloc(cs.namespace(|| "allocating mantissa"), || ...)?;

// After fix — derived and constrained:
let mantissa = mantissa_result.into_allocated_num(cs.namespace(|| "accumulate mantissa"))?;
```

`AllocatedNum::alloc()` creates a new witness variable without adding any R1CS constraint. Any `(packed_amount, unpacked_amount)` pair could be used to generate a proof accepted by the verification keys. This enabled unauthorized token minting, transfer amount manipulation, and token theft.

---

### 4. Haven Protocol — Range Proof Validation Flaw

**Date:** December 10, 2024  
**Loss:** Unlimited XHV minting (amount unquantified publicly)  
**System:** Haven Protocol (Monero-derived privacy chain)

**Technical detail:**

Haven Protocol extends the Monero protocol with oracle-based stablecoin minting: users burn XHV to mint xUSD, xBTC, and other denominated assets. Transaction amounts in Monero-derived systems are hidden using Pedersen commitments:

$$
\begin{aligned}
C = v \cdot G + r \cdot H
\end{aligned}
$$

and their validity (non-negativity) is proven via Bulletproof range proofs asserting $$v \in [0, 2^{64})$$. A flaw in Haven's range proof validation allowed transactions with amounts outside this interval to pass consensus checks. Because $$v$$ is interpreted modulo the field order, an out-of-range commitment that wraps around appears as a very large positive value, enabling the minting of XHV without economic backing.

The bug targeted the Bulletproof range proof layer that is integral to the system's privacy and inflation controls.

---

### 5. [ZKSwap — `return true` in `verifyExitProof()`](https://www.blockaid.io/blog/how-zkswaps-5m-exploit-couldve-been-prevented-with-onchain-monitoring)

**Date:** July 9, 2025  
**Loss:** $5$M  
**Attacker EOA:** `0x0a652decf9caca373e2b50607ecb7b069d71a7ba`  
**Exploit contract:** `0x2D3103c8Fdd9d9411E24f555fdad6B22F29F613A`  
**Chain:** Ethereum

**Technical detail:**

ZKSwap was a ZK-rollup DEX and L2 bridge. Its emergency exit mechanism, `verifyExitProof()`, was deployed with a bare `return true` at the beginning of the function body. All subsequent ZK verification logic (loading the verification key, calling the verifier) was dead code. No proof check was ever performed.

The attacker activated Exodus Mode, submitted fabricated proofs for 15 token IDs (all accepted), and drained $5$M in approximately 13 minutes. The rollup had been inactive since February 2025, and the emergency exit path had not been reviewed since its last modification.

```
  verifyExitProof(bytes calldata proof, uint256[] calldata publicInput)
      returns (bool) {
      return true;          // verification dead gate

      // unreachable from this point:
      uint256[] memory vk = loadVerificationKey();
      return Verifier.verify(vk, proof, publicInput);
  }
```

---

### 6. [Veil Cash — Groth16 Trusted Setup Broken](https://rekt.news/default-settings)

**Date:** February 20, 2026  
**Loss:** ~2.9 ETH (~$5$K)  
**Chain:** Ethereum  
**Status:** Funds mostly recovered

**Technical detail:**

Veil Cash was a ZK privacy protocol using Groth16. The verification key was deployed with $$\gamma = \delta = G_{2,\text{gen}}$$, the default BN254 G2 generator point, because the `snarkjs zkey contribute` trusted setup ceremony step was never executed. The Groth16 verifier equation degenerates when $$\gamma = 1$$: the blinding of the public input sum collapses, and any fabricated proof satisfying the weakened algebraic check is accepted.

An attacker submitted 29 fabricated proofs using null-prefix nullifier hashes (`0xdead0000` through `0xdead001c`) in a single transaction, draining the contract. Rekt News characterized this as the first confirmed live exploit of ZK cryptography.

---

### 7. [FoomCash — Groth16 Trusted Setup Broken (Copycat)](https://rekt.news/the-unfinished-proof)

**Date:** February 26, 2026  
**Loss:** $2.26$M gross / ~$420$K net  
**Chains:** Ethereum + Base  
**Status:** $1.84$M recovered by Decurity; ~$320$K retained by bounty claimant

**Technical detail:**

FoomCash was a ZK-proof privacy lottery. It deployed an identical broken Groth16 verifier to Veil Cash: $$\gamma = \delta = G_{2,\text{gen}}$$. Six days after the Veil Cash post-mortem was published, two independent actors read it and exploited FoomCash the same morning:

- **duha_real (Base):** 10 loop iterations; drained 99.97% of the Base pool (~$320$K); kept the funds under the protocol's own published "code is law" bounty.
- **Decurity (Ethereum):** 30 loop iterations; drained 99.99% of the Ethereum pool; returned $1.84$M for a $100$K fee.

The protocol's Bitcointalk listing stated: *"THE ONLY RULE IS CODE. If your code can take the funds, YOU'VE WON."* The team later framed the incident as an "elite white-hat response."

---

### 8. HermesVault — ZK Verification Key-Reset Bypass

**Date:** May 19, 2026  
**Loss:** $29,466$  
**Chain:** Algorand

**Technical detail:**

HermesVault was a ZK-based privacy protocol on Algorand. An attacker found a mechanism to reset the cryptographic keys governing the ZK proof verifier, decoupling the verifier's expected public parameters from those used to generate legitimate proofs. With verification neutralized, the attacker extracted funds without submitting valid ZK proofs. The specific implementation detail (whether the key reset was achieved via governance, an upgrade path, or a parameter mutation in the on-chain verifier state) was not fully disclosed.

---

### 9. [Aztec Connect Bridge — Settlement Boundary Bypass](https://slowmist.medium.com/analysis-of-the-2-19-million-asset-theft-from-aztec-connect-d867c59b1fc6)

**Date:** June 14–15, 2026  
**Loss:** $2.28$M  
**Vulnerable contract:** `0xff1f2b4adb9df6fc8eafecdcbf96a2b351680455` (RollupProcessorV3)  
**Chain:** Ethereum  
**Status:** $2.19$M unlaundered at attacker EOA; ~$88$K laundered via Tornado Cash

**Technical detail:**

Aztec Connect was a ZK-rollup privacy bridge deprecated by Aztec Labs and inactive for three years. Its `processRollup()` function on L1 read `numRealTxs` directly from calldata to determine the processing loop boundary. The ZK circuit committed to all 32 transaction slots per block via SHA-256, but this commitment did not constrain the value of `numRealTxs` in the proof's public inputs.

By submitting rollup blocks with `numRealTxs = 1` but packing fabricated deposit transactions into slots 2–32, attackers caused:

1. The ZK proof to be valid (covering all 32 slots).
2. The L1 settlement loop to terminate after slot 1, silently skipping slots 2–32.
3. L2 credit to be issued for the deposits in slots 2–32 without any L1 backing.

Attackers then submitted legitimate ZK withdrawal proofs against the unbacked L2 balance, draining real L1 assets.

**Day 1 (June 14, single transaction, 4.5M gas):** $2.19$M drained (DAI, wstETH, yvDAI, yvWETH, LUSD, ETH).  
**Day 2 (June 15, 04:00–05:17 UTC):** Second attacker drained ~$88$K using the same method.

A secondary gap: `processRollup()` had no caller access control enforced on-chain, allowing arbitrary addresses to submit rollup blocks.

---

## Part II — ZK-Rollup Protocol Exploits

### 10. [ZKSpace — Proxy Contract Exploit](https://www.ainvest.com/news/zkspace-proxy-contract-exploited-4-million-stolen-2507/)

**Date:** ~July 2025  
**Loss:** ~$4$M  
**Chains:** BNB Chain (funding origin) → Ethereum (drained)  
**Status:** ~$1.3$M laundered via Tornado Cash; ~$2.7$M distributed across two addresses

**Technical detail:**

An address funded via Tornado Cash on BNB Chain executed transactions targeting the ZKSpace proxy contract on Ethereum. Approximately $4$M was drained. The specific proxy contract vulnerability was not publicly disclosed in available post-mortems. The ZKSpaceOfficial X account was suspended at the time of the attack.

This incident is classified as a partial ZK incident: ZKSpace is a ZK-rollup, and the attack targeted the contract layer rather than the ZK proof system.

---

### 11. [zkLend — Precision Loss on StarkNet](https://rekt.news/zklend-rekt)

**Date:** February 11, 2025  
**Loss:** $9.57$M  
**Chain:** StarkNet (ZK-rollup)  
**Attacker (StarkNet):** `0x04d7191dc8eac499bac710dd368706e3ce76c9945da52535de770d06ce7d3b26`

**Technical detail:**

zkLend is a lending protocol on StarkNet. The `lending_accumulator` variable tracking interest accrual was subject to a rounding flaw exploitable when combined with three conditions: empty market initialization was permitted; token donations were accepted and inflated the accumulator; and withdrawal rounding favored the attacker.

The attacker used flash loans to inflate `lending_accumulator` to 4.069297906051644020. At this value, depositing the minimum wstETH amount yielded only 2 wei of receipt tokens, enabling a withdrawal of approximately 1.5× the deposit per cycle. Over many iterations, the attacker drained 2,200+ ETH plus USDC, STRK, and USDT.

This is a standard DeFi precision loss error unrelated to the ZK cryptography; the classification reflects that it occurred on a ZK-rollup chain.

**Recovery note:** The attacker attempted to launder funds through Railgun. Railgun's privacy pool compliance controls automatically rejected the transaction and returned ~706 ETH to the sender.

---

## Part III — Disclosed Vulnerabilities (No Exploitation)

### 12. [Solana ZK ElGamal Proof Bug #1](https://solana.com/news/post-mortem-june-25-2025)

**Date:** April 16–18, 2025 (reported and patched)  
**Discoverer:** LonelySloth  
**Bounty:** undisclosed  
**System:** Solana Token-2022 ZK ElGamal Proof program

**Technical detail:**

The ZK ElGamal Proof program verifies zero-knowledge proofs for Token-2022 confidential transfers. Certain algebraic components were not included in the Fiat-Shamir hash transcript before the challenge was derived. An attacker could construct forged proofs enabling unlimited token minting or unauthorized withdrawal from any confidential token account.

Patches were deployed within 26 hours to Agave (v2.1.21+, v2.2.11+), Jito-Solana, and Firedancer. Reviewed by Asymmetric Research, Neodyme, and OtterSec.

---

### 13. [Solana ZK ElGamal Proof Bug #2](https://solana.com/news/post-mortem-june-25-2025)

**Date:** June 10, 2025 (reported) / June 19, 2025 (program disabled at epoch 805)  
**Discoverer:** suneal_eth (@zksecurityXYZ)  
**System:** Solana Token-2022 ZK ElGamal Proof program

**Technical detail:**

Approximately 60 days after Bug #1 was patched, a different binding failure was reported in the same program: a separate component was absent from the Fiat-Shamir transcript hash. Token-2022 confidential transfers were disabled on June 11; the ZK ElGamal program was disabled at epoch 805 on June 19.

No exploitation occurred. Usage of confidential transfers was near-zero at the time: stablecoins PYUSD, AUSD, and USDG had enabled the Token-2022 extension but had not activated confidential transfers for end users.

The occurrence of two independent transcript binding failures in the same program within two months indicates that a systematic transcript audit, covering all prover-controlled elements, was not conducted after the first fix.

---

### 14. [OtterSec — Fiat-Shamir Binding Failures in 6 zkVMs](https://osec.io/blog/2026-03-03-zkvms-unfaithful-claims/)

**Date:** September 2025–March 2026 (disclosed and patched)  
**Researchers:** Himanshu Sheoran and Valter Wik (OtterSec)  
**Systems affected:** 6 independent zkVM implementations

**Technical detail:**

OtterSec disclosed independent Fiat-Shamir transcript binding failures across six zkVM implementations over six months. In each case, one or more prover-controlled values that influence a verification equation were omitted from the transcript hash input, allowing a forged proof to be generated for a false statement.

| System | Reported | Patched |
|--------|----------|---------|
| Jolt (a16z) | September 2025 | October 3, 2025 |
| Nexus | October 2025 | October 24, 2025 |
| Cairo-M (Kakarot Labs) | October 2025 | October 31, 2025 |
| Binius64 | December 2025 | December 29, 2025 |
| Expander (Polyhedra) | November 2025 | January 21, 2026 |
| Ceno (Scroll) | November 2025 | March 5, 2026 |

The longest delay between disclosure and patch was approximately four months (Ceno). Trail of Bits had documented the same bug class in 2022 under the "Frozen Heart" label in SnarkJS, gnark, and Dusk Network's Plonk implementation. Independent recurrence across six teams confirms that Fiat-Shamir transcript construction is not consistently specified in protocol documentation.

---

### 15. [dYdX — npm/PyPI Supply Chain Attack](https://socket.dev/blog/malicious-dydx-packages-published-to-npm-and-pypi)

**Date:** January 27–28, 2026  
**Loss:** Unknown (no confirmed fund losses publicly reported)  
**Target:** dYdX v4 (StarkWare ZK-rollup backend)

**Technical detail:**

A threat actor compromised a dYdX package maintainer's npm and PyPI credentials and injected malicious code into multiple SDK package versions:

| Package | Malicious versions |
|---------|-------------------|
| `@dydxprotocol/v4-client-js` (npm) | 3.4.1, 1.22.1, 1.15.2, 1.0.31 |
| `dydx-v4-client` (PyPI) | 1.1.5post1 |

The npm variant embedded credential exfiltration code inside `createRegistry()`, stealing wallet seed phrases and private keys. The PyPI variant added malware to `config.py` and `_bootstrap.py` that installed a Remote Access Trojan enabling persistent system access and lateral movement.

Detection occurred within 24 hours via Socket's supply chain monitoring. This incident is classified as a ZK ecosystem supply chain attack rather than a ZK cryptographic failure.

---

## Patterns and Observations

**Trusted setup failures are a deployment-time risk.** Veil Cash and FoomCash both deployed Groth16 verifiers with $$\gamma = \delta = G_{2,\text{gen}}$$. The error was not in the circuit logic but in the ceremony that generates the verification key. Standard Solidity audits do not inspect deployed verification keys.

**Fiat-Shamir binding errors recur independently.** The same bug class appeared in SnarkJS/gnark/Dusk (2022), Solana ZK ElGamal twice (2025), and six zkVMs (2025–2026). The root pattern is identical each time: a prover-controlled group element is absent from the hash before the challenge is derived.

**Under-constrained witnesses have a single footprint.** The three circuit-level bugs (Aztec Connect claim proof, zkSync Era RAM Permutation, zkSync Lite mantissa) share a common code pattern: `AllocatedNum::alloc()` without a follow-up constraint, or a `LinearCombination` built but never enforced. The pattern is syntactically silent in code review.

**Deprecated contracts remain exploitable.** Both the Aztec Connect June 2026 exploit and the September 2023 Aztec Connect claim proof bug targeted a protocol that had been inactive for an extended period. Immutable contracts on Ethereum do not expire.

**ZK branding does not imply ZK security.** zkLend's $9.57$M loss was a precision loss error unrelated to StarkNet's proof system. ZKSpace's proxy exploit did not touch ZK cryptography. Building on a ZK chain does not transfer ZK-verified properties to the application logic.

---

## Conclusion

Across the 15 incidents documented here, eight involved a direct vulnerability in the ZK proof system (trusted setup, Fiat-Shamir binding, circuit soundness, proof verification bypass, settlement boundary). The remaining seven involved the surrounding protocol infrastructure on ZK chains or ecosystems. The total value lost in confirmed exploits is approximately $19$M at the application layer, with an additional $1.9$B+ in peak at-risk TVL for the three largest disclosed vulnerabilities.

![ZKP hacks 2023–2026 mindmap]({{site.url_complet}}/assets/article/blockchain/zkp/2026-06-19-zkp-hacks-history-mindmap.png)

## Frequently Asked Questions

**Q: What is the difference between a "direct ZK exploit" and a "ZK-rollup protocol exploit" as used in this article?**

A direct ZK exploit targets a failure in the proof system itself: the ZK circuit is missing a constraint, the trusted setup was not executed, the Fiat-Shamir transcript omits a component, or the verifier function is bypassed. In all such cases, the ZK proof system accepted a false statement as true. A ZK-rollup protocol exploit targets the surrounding contract logic (access control, share accounting, proxy upgradeability) while the ZK proof system itself functioned correctly. zkLend's precision loss and ZKSpace's proxy exploit are examples: the proofs were valid, but the protocol's economic logic had independent flaws.

**Q: How did the FoomCash attackers learn about the trusted setup vulnerability so quickly?**

The Veil Cash post-mortem was published by Rekt News six days before the FoomCash attack. The post-mortem described the root cause ($$\gamma = \delta = G_{2,\text{gen}}$$), the attack method (submitting fabricated proofs), and the verification key structure. FoomCash used an identical verifier. The attacker read the post-mortem and replicated the exploit on a protocol with a much larger TVL. This illustrates the dual-use nature of security disclosures: public post-mortems accelerate both defenses and copycat attacks.

**Q: Why did Aztec Connect remain exploitable three years after being deprecated?**

Ethereum smart contracts are immutable once deployed. The `RollupProcessorV3` contract was never paused, the funds were never withdrawn to a safe address, and no on-chain access control was added after deprecation. The protocol's documentation indicated that `processRollup()` should require an authorized rollup provider, but the implementation did not enforce this restriction. The contract continued to hold real user funds and accept arbitrary rollup submissions from any caller throughout the three-year dormant period.

**Q: What is the monetary value of bug bounties paid for ZK circuit vulnerabilities in this dataset?**

Three disclosed ZK circuit vulnerabilities were rewarded with documented bounties:
- Aztec Connect Claim Proof Bug: $450,000$ (Immunefi)
- zkSync Era RAM Permutation Bug: $50,000$ USDC (Matter Labs program)
- zkSync Lite Insufficient Proof Verification: $200,000$ (Immunefi)

Total documented: $700,000$ in ZK circuit bug bounties for the three incidents. The Solana ZK ElGamal disclosures and OtterSec zkVM disclosures also resulted in bounties, but the specific amounts were not disclosed publicly in the available sources.

**Q: In the OtterSec zkVM disclosures, all six implementations had the same bug class but were developed independently. What does this indicate about the state of Fiat-Shamir implementation guidance?**

The recurrence of the same binding failure across six independent implementations over six months indicates that protocol specifications for zkVM proof systems do not consistently define which elements must be included in the Fiat-Shamir transcript before each challenge is derived. Developers implementing the transcript construction from a paper or specification may omit elements that the paper does not explicitly identify as necessary, either because the paper focuses on the algebraic construction rather than the implementation detail, or because the necessity of binding a particular element only becomes apparent from a security analysis of the specific combination of prover algorithms. The fix in each case was one or two lines of code, but the design documents did not prevent the error.

**Q: Does the Haven Protocol incident mean that Bulletproofs are fundamentally insecure?**

No. Bulletproofs as a cryptographic construction are secure under the discrete logarithm assumption. The Haven Protocol incident reflects a failure in the application of Bulletproof range proofs within the consensus rules, not a break in the underlying proof system. Specifically, the consensus validation did not correctly enforce that all committed transaction amounts fell within the valid range $$[0, 2^{64})$$. A valid Bulletproof range proof guarantees that the committed value lies in the range only if the verifier correctly enforces all proof components. If the enforcement logic has a gap, transactions with amounts outside the range may pass validation even though the proof system itself is sound.

## References

- [Aztec Connect Claim Proof Bug — HackMD](post-mortem/Aztec Connect Claim Proof Bug - HackMD.pdf)
- [Aztec Multiple-Spend Error Bugfix Review — Immunefi](post-mortem/Aztec Multiple-Spend Error Bugfix Review _ by Immunefi Editor _ Immunefi _ Medium.pdf)
- [zkSync Era Soundness Bug — ChainLight Blog](https://blog.chainlight.io/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8)
- [zkSync Lite Proof Verification Bugfix — Immunefi](https://medium.com/immunefi/zksync-insufficient-proof-verification-bugfix-review-dcd57944d0e2)
- [Solana ZK ElGamal Post-Mortem June 2025](https://solana.com/news/post-mortem-june-25-2025)
- [OtterSec zkVM Fiat-Shamir Disclosures](https://osec.io/blog/2026-03-03-zkvms-unfaithful-claims/)
- [Veil Cash / FoomCash — Rekt News Default Settings](https://rekt.news/default-settings)
- [FoomCash — Rekt News The Unfinished Proof](https://rekt.news/the-unfinished-proof)
- [ZKSwap Exploit Analysis — Blockaid](https://www.blockaid.io/blog/how-zkswaps-5m-exploit-couldve-been-prevented-with-onchain-monitoring)
- [Aztec Connect Exploit Analysis — SlowMist](https://slowmist.medium.com/analysis-of-the-2-19-million-asset-theft-from-aztec-connect-d867c59b1fc6)
- [zkLend Exploit — Rekt News](https://rekt.news/zklend-rekt)
- [dYdX Supply Chain Attack — Socket](https://socket.dev/blog/malicious-dydx-packages-published-to-npm-and-pypi)
- [SlowMist Hacked Database](slowmist/SlowMist Hacked - SlowMist Zone.pdf)
- [Claude Code](https://claude.com/product/claude-code)
