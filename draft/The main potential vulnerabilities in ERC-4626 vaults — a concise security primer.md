---

---

layout: post
title: "The main potential vulnerabilities in ERC-4626 vaults — a concise security primer"
date:   2025-11-07
lang: en
locale: en-GB
categories: blockchain ethereum 
tags: defi stablecoin
description: USD₮0 is an Omnichain Fungible Token (OFT) built on LayerZero, enabling cross-chain transfers of USDT. Learn how USD₮0 works, its architecture, and the Legacy Mesh that connects existing USDT networks.
image: 
isMath: false

ERC-4626 standardizes **tokenized vaults** that accept a single ERC-20 asset and mint transferable *shares* representing a pro rata claim on the vault’s `totalAssets()`. 

That composability is powerful — and it also concentrates a set of recurring, subtle attack surfaces developers and auditors keep finding in the wild. .

## Reminder

Here are the main functions available in the ERC-4626 interface

### Core Functions

**asset()**
 Returns the address of the underlying token the vault uses.

**totalAssets()**
 Returns the total amount of underlying assets the vault manages, including yield and fees.

**convertToShares(assets)**
 Returns how many shares would be received for a given amount of assets in an ideal scenario.

**convertToAssets(shares)**
 Returns how many assets would be received for a given amount of shares in an ideal scenario.

------

### Deposit Functions

**maxDeposit(receiver)**
 Returns the maximum amount of assets that can be deposited for a given receiver.

**previewDeposit(assets)**
 Simulates a deposit and shows how many shares would be minted without actually depositing.

**deposit(assets, receiver)**
 Deposits assets and mints corresponding shares for the receiver.

**maxMint(receiver)**
 Returns the maximum number of shares that can be minted for a receiver.

**previewMint(shares)**
 Simulates a mint and shows how many assets would be required without actually minting.

**mint(shares, receiver)**
 Mints exactly the specified number of shares in exchange for the required assets.

------

### Withdrawal Functions

**maxWithdraw(owner)**
 Returns the maximum amount of assets that the owner can withdraw.

**previewWithdraw(assets)**
 Simulates a withdrawal and shows how many shares would be burned.

**withdraw(assets, receiver, owner)**
 Withdraws assets by burning shares from the owner and sends them to the receiver.

**maxRedeem(owner)**
 Returns the maximum number of shares that can be redeemed by the owner.

**previewRedeem(shares)**
 Simulates a redemption and shows how many assets would be received without actually redeeming.

**redeem(shares, receiver, owner)**
 Redeems exactly the specified number of shares for the corresponding amount of assets.

------

### Events

**Deposit(sender, owner, assets, shares)**
 Emitted when assets are deposited and shares are minted.

**Withdraw(sender, receiver, owner, assets, shares)**
 Emitted when shares are redeemed or burned and assets are withdrawn.

**Exchange Rate Manipulation in ERC4626 Vaults**

The ERC4626 Tokenized Vault standard has grown rapidly, enabling DeFi protocols to issue tokenized shares representing deposits. However, this standard introduces several security risks related to **exchange rate manipulation** between vault shares and underlying assets.

### Key Attack Vectors

1. **First Deposit Frontrunning:**
    Attackers manipulate the exchange rate around the first deposit to capture most of the depositor’s assets via rounding and timing exploits.
2. **Share Price Manipulation:**
    Since vault shares are ERC20 tokens used as collateral or for borrowing, attackers can artificially inflate share prices to borrow more value than allowed (e.g., the CREAM attack).

### Manipulation Techniques

- **Direct Donation:**
   Attackers send tokens directly to the vault, increasing its balance without issuing new shares. This inflates the share price.
- **Stealth Donation:**
   Exploits rounding errors in deposits, withdrawals, or debt repayments, compounding small “donations” of unaccounted assets to the vault. This can exponentially manipulate the exchange rate (e.g., Wise Finance attack).
- **Unaccounted Flash Loans:**
   Flash loans temporarily change vault balances, distorting share value if not properly tracked.

### Mitigation Strategies

No single method fully prevents manipulation; combining approaches is often necessary.

1. **Initial Deposit (Dead Shares):**
    Seed the vault with a non-redeemable deposit to reduce manipulation impact from donations and rounding.
2. **Virtual Deposit:**
    Use a minimal “virtual” deposit (e.g., 1 wei and 1 share) to mitigate first-deposit attacks.
3. **Internal Asset Balance Tracking:**
    Track asset balances internally to prevent direct donations from altering share prices.
4. **Increased Share Precision:**
    Increase the precision or decimals of share tokens to make rounding-based attacks ineffective.
5. **Averaging Share Price:**
    Use time-averaged exchange rates (like DEX oracles) to reduce sensitivity to rapid manipulations.
6. **Discarding Stealth Donations:**
    Exclude rounding remainders from vault accounting to limit compounding manipulation.
7. **Virtual Assets During Flash Loans:**
    Adjust total asset tracking to include temporarily lent amounts during flash loans.
8. **Explicit Exchange Rate Tracking:**
    Store and update exchange rates directly in vault storage to prevent manipulation via asset transfers.

### Conclusion

ERC4626 vaults are susceptible to exchange rate manipulation through donation-based and rounding-based attacks. Effective defenses require layered mitigation—combining methods like initial or virtual deposits, precision adjustments, and explicit tracking. Developers should tailor protections to their specific vault logic to ensure robustness and maintain a secure DeFi ecosystem.

## List

------

## 1) Share-inflation / “donation” / exchange-rate manipulation



If `totalAssets()` can increase without shares being minted in the same atomic context (e.g., an attacker transfers tokens directly into the vault, or external rewards land in the vault), the exchange-rate calculation (`convertToShares` / `convertToAssets`) can be skewed. 

An attacker can donate assets or manipulate balance reporting to inflate their own position, or to make other protocols treat the vault’s token as more valuable than it really is. This class of issues has produced real advisories and defensive patterns in the community.

### Inflation attack 

First deposit frontrunning

Standard scenario

1. Users **deposit tokens** (the underlying asset) into the vault.
2. The vault **mints “shares”** to represent each user’s portion of the total pool.
3. The **share-to-asset exchange rate** determines how much each share is worth.
4. When users **withdraw**, they get their assets back according to how many shares they hold.

Inflation attack

**Step 1 – A new vault is empty.**
 The vault starts with zero assets and zero shares.

**Step 2 – Attacker makes a tiny first deposit.**
 They deposit **1 wei** (a microscopic amount) and receive **all the shares** since they’re the first depositor.

**Step 3 – Victim tries to deposit normally.**
 Another user plans to deposit **100 tokens** right after.

**Step 4 – Attacker “donates” assets.**
 Before the victim’s transaction finishes, the attacker **transfers (donates) 100 tokens** directly to the vault.

- This increases the vault’s total assets.
- But the attacker’s shares stay the same (they still own all of them).
- No new shares are minted for the donation.

**Step 5 – Victim’s deposit is processed.**
 Now the vault thinks it already has 100 + 1 tokens, so when calculating how many new shares to give the victim,
 the formula rounds down to **zero shares** (because 100 / 101 ≈ 0).

**Step 6 – Attacker withdraws.**
 As the only share-holder, the attacker withdraws **the entire vault balance**, which now includes the victim’s 100 tokens.

#### 

Reference: [A Novel Defense Against ERC4626 Inflation Attacks](https://www.openzeppelin.com/news/a-novel-defense-against-erc4626-inflation-attacks) [](https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks)

#### Real case

[Cream Finance - Incident Disclosure 2021-10-27](https://github.com/yearn/yearn-security/blob/master/disclosures/2021-10-27.md)

#### Exchange Rate Manipulation in ERC4626 Vaults

Other protocols (lending markets, leveraged positions, routers) often use the vault’s reported `totalAssets()` or share-price as an oracle. A manipulated exchange rate cascades into mispriced collateral, wrong liquidations, or theft of yield. [euler.finance](https://www.euler.finance/blog/exchange-rate-manipulation-in-erc4626-vaults)

**Mitigations.**

- Use an explicit accounting model: prefer `totalAssets()` that is *explicitly* maintained by strategy entry/exit functions rather than relying on `balanceOf` alone.
- Reject or handle raw ERC-20 transfers (implement `beforeDeposit` hooks or a `sync()` pattern).
- Require `minShares` or “first-deposit” protections; use the guarded deposit/mint logic from battle-tested libraries (e.g., OpenZeppelin implementations and their published defenses). [blog.openzeppelin.com+1](https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks)

------

## 2) Reentrancy & flash-loan side-entrance attacks

**What it is.** Vault functions that perform external calls (strategy interactions, rewards distribution, token transfers) without proper reentrancy guards can be reentered by an attacker (often via a malicious token, receiver hook, or flash loan callback). Flash loans let attackers perform complex multi-step manipulations inside a single block/transaction to exploit temporary accounting inconsistencies. [ackee.xyz+1](https://ackee.xyz/blog/flash-loan-reentrancy-attack/)

**Why it matters.** Reentrancy can let attackers withdraw more than their fair share, manipulate internal bookkeeping mid-operation, or combine with donation/exchange-rate issues to amplify loss.

**Mitigations.**

- Apply `nonReentrant` (or equivalent checks-effects-interactions discipline) around state-changing entry points.
- Avoid doing external calls before updating internal accounting.
- Audit all token callbacks/hooks and avoid trusting tokens with nonstandard transfer behavior.

------

## 3) Tokens with nonstandard behavior (fee-on-transfer, rebasing, hooks)

**What it is.** ERC-4626 assumes a standard underlying ERC-20, but many tokens have transfer fees, rebasing supply, or callbacks that change balances unexpectedly. Vaults that use `IERC20.transferFrom` and assume the transferred amount equals the intended `assets` can be tricked or simply break accounting. [speedrunethereum.com](https://speedrunethereum.com/guides/erc-4626-vaults)

**Why it matters.** Misaccounting for fees or rebases leads to drift between `totalAssets()` and actual value, enabling rounding abuse, stuck withdrawals, or value loss for users.

**Mitigations.**

- Support (or explicitly reject) fee-on-transfer tokens; measure received amounts (use `balanceBefore/After` checks).
- For rebasing tokens, document incompatibility or implement special handling.
- Use `safeTransfer` patterns and explicit `amountReceived = token.balanceOf(this) - before` checks.

------

## 4) Rounding, precision and off-by-one share math

**What it is.** Vaults convert between assets and shares. Poorly handled integer division, rounding direction, or edge-cases (e.g., zero `totalSupply` on the first deposit) produce exploitable gaps — especially combined with donation or oracle manipulation. Much of the ERC-4626 literature stresses correct semantics for `convertToShares`/`convertToAssets` and initial-deposit edge cases. [Medium+1](https://medium.com/coinmonks/another-look-at-the-security-of-erc4626-vaults-9901618d0923)

**Why it matters.** Rounding choices determine who loses when small remainders exist; attackers can sometimes craft sequences that benefit from rounding (e.g., mint tiny shares repeatedly).

**Mitigations.**

- Follow reference implementations (OpenZeppelin) and their tested conversion formulas.
- Add property tests and fuzzing for small/large values and first deposit cases.
- Consider minimal mint thresholds, or use well-defined rounding rules (document them).

------

## 5) Oracle & composition risks (external protocol coupling)

**What it is.** Vaults are often plugged into other systems (lenders, AMMs, leverage engines). If those systems use vault share price as an oracle without safeguards, an attacker can manipulate on-chain state (e.g., via low-liquidity deposits or price manipulations) to trigger liquidations or bad decisions elsewhere. Recent writeups show how exchange-rate manipulations in vaults ripple into lending markets. [OpenZeppelin+1](https://www.openzeppelin.com/news/erc-4626-tokens-in-defi-exchange-rate-manipulation-risks)

**Why it matters.** Even a small vault can be a systemic risk if composed into larger systems.

**Mitigations.**

- Encourage consumers to use TWAPs or vetted oracles rather than instant share-price for critical collateral decisions.
- Make clear in docs that share price is a *local* view and may be influenced by direct transfers; recommend oracles with smoothing.

------

## 6) Upgradeability, access control, and emergency functions

**What it is.** Improperly secured admin functions, poorly documented upgrade mechanisms, or overly-powerful emergency withdraws can be exploited by insiders or via compromised keys. Vaults with upgradable logic must clearly lock down who can upgrade and how the upgrade path is controlled. [ChainSecurity](https://www.chainsecurity.com/security-audit/yearn-erc4626-router)

**Mitigations.**

- Use multisig / timelocks for upgrades.
- Minimize privileged code paths; prefer push-button pausing only when absolutely necessary.
- Publicly document admin powers and publish key-holder OPSEC guidance.

------

## Practical checklist (quick)

1. Use a battle-tested ERC-4626 reference (OpenZeppelin) and review their defense patterns. [blog.openzeppelin.com](https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks)
2. Prevent/handle raw token donations (sync pattern, explicit `donate()` handling, or revert on stray transfers). [mixbytes.io](https://mixbytes.io/blog/overview-of-the-inflation-attack)
3. Add `nonReentrant`, follow checks-effects-interactions. [ackee.xyz](https://ackee.xyz/blog/flash-loan-reentrancy-attack/)
4. Test edge cases (first deposit, tiny amounts, fee-on-transfer tokens, rebasing). Use fuzzing/property testing. [composable-security.com](https://composable-security.com/blog/erc-4626-easy-to-understand-essentials/)
5. Limit upgrade surface and use timelocks/multisigs; document admin powers. [ChainSecurity](https://www.chainsecurity.com/security-audit/yearn-erc4626-router)

------

## Final notes — what auditors and teams are saying

Auditors repeatedly find the same families of mistakes: improper handling of unexpected token transfers, unsafe rounding and initial supply logic, and insufficient guarding against reentrancy + flash loans. The community has proposed several well-documented mitigations (OpenZeppelin’s blog, MixBytes overviews, Euler/Open source analyses), and those pieces together give a practical defensive playbook for ERC-4626 vaults. If you’re building or auditing a vault, prioritize *accounting invariants, explicit handling of out-of-band balance changes, and strong testing/fuzzing*. [zellic.io+1](https://www.zellic.io/blog/exploring-erc-4626)

# Reference

- [OpenZeppelin Forum – “ERC4626 Inflation attack discussion”](https://forum.openzeppelin.com/t/erc4626-inflation-attack-discussion/41643?utm_source=chatgpt.com)

- [MixBytes – “Overview of the Inflation Attack”](https://mixbytes.io/blog/overview-of-the-inflation-attack?utm_source=chatgpt.com)

- [OpenZeppelin Blog – “A Novel Defense Against ERC4626 Inflation Attacks”](https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks?utm_source=chatgpt.com)

- [OpenZeppelin Docs – “ERC4626” (section on inflation attack) ](https://docs.openzeppelin.com/contracts/4.x/erc4626?utm_source=chatgpt.com)

- [OpenZeppelin Docs – “ERC4626” (version 5.x) ](https://docs.openzeppelin.com/contracts/5.x/erc4626?utm_source=chatgpt.com)

- [Cyfrin – “Solodit Checklist Explained (3): Donation Attacks”](https://www.cyfrin.io/blog/solodit-checklist-explained-3-donation-attacks?utm_source=chatgpt.com)

- [Medium – “Another look at the security of ERC4626 Vaults”](https://medium.com/coinmonks/another-look-at-the-security-of-erc4626-vaults-9901618d0923?utm_source=chatgpt.com)

- [RivaNorth Blog – “ERC-4626 Vulnerabilities and How to Avoid Them in Your Project”](https://rivanorth.com/blog/erc-4626-vulnerabilities-and-how-to-avoid-them-in-your-project?utm_source=chatgpt.com)

- [Zellic Audit Report – “Risk of ERC-4626 inflation attack”](https://reports.zellic.io/publications/beefy-wrapper/findings/informational-beefywrapper-risk-of-erc-4626-inflation-attack?utm_source=chatgpt.com)