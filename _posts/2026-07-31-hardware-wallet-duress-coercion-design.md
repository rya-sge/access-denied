---
layout: post
title: "Designing for Coercion - Duress PINs, Decoy Wallets and Plausible Deniability"
date:   2026-07-31
lang: en
locale: en-GB
categories: blockchain security
tags: hardware wallet duress coldcard trezor security
description: How hardware wallets handle an attacker who has both the device and the user - duress PINs, decoy wallets, delta mode, passive wipe triggers - and where each defence stops working.
image: /assets/article/blockchain/wallet/coldcard/2026-07-31-hardware-wallet-duress-mindmap.png
isMath: false
---

Most security engineering assumes the legitimate user is on your side. Coercion breaks that
assumption: the person entering the PIN is doing so under compulsion, and every mechanism
designed to help them prove their identity now works against them. A hardware wallet is one of
the few consumer devices whose designers must treat this as a routine case rather than an edge
case, because the asset is bearer-controlled, irreversible, and worth a physical confrontation.

This article looks at how that problem is actually solved in firmware, using the
[COLDCARD](https://coldcard.com) implementation as the primary example and contrasting it with
the passphrase-based approach taken by [Trezor](https://trezor.io), covered in an
[earlier article]({{site.url_complet}}/2024/10/15/trezor-wallet-security/) on this site. The
interesting material is less the feature list than the reasoning about what an attacker can
observe, and the places where the designers concede that a defence does not hold.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

------

## The threat model

The scenario is usually called the "$5$ wrench attack" after the [XKCD strip](https://xkcd.com/538/):
rather than attacking the cryptography, the attacker attacks the person holding the key. For a
firmware designer this resolves into a set of concrete assumptions.

- **The attacker has the device**, and can power it, open it, and keep it indefinitely.
- **The attacker can compel the user** to enter a PIN, and can watch the screen while they do it.
- **The attacker may know what to expect.** They may have found an extended public key on the
  user's computer, in which case they know the wallet's real balance and its transaction history,
  and a decoy holding a token amount will not satisfy them.
- **The attacker may be technically capable.** Opening the case and probing the bus between the
  processor and the secure elements is not exotic.
- **The user cannot be trusted to act.** Under duress, any defence that requires remembering a
  procedure or performing a visible action may not happen.

The last two assumptions are what separate a serious design from a marketing feature. A duress
mode that is obvious on an oscilloscope, or that requires the victim to calmly execute a
sequence, has failed in exactly the situation it was built for.

------

## Why not a secret keystroke?

The intuitive design is a hidden gesture: hold two keys, or enter the PIN backwards, and the
device wipes. `docs/pin-entry.md` explains why that approach was rejected, and the reasoning
generalises well beyond this product.

- **The feature has to be documented.** Anything shipped in a product gets written up, indexed
  and searchable. A secret that is public is not a secret, and an attacker who has read the
  manual will watch for the gesture.
- **The user may not be at the device.** A PIN can be extracted by phone, by text message, or
  from a written note found in a drawer. A keystroke cannot be performed remotely, so the defence
  is unavailable in exactly the cases where the user is not physically present.
- **A trap that everyone knows is not a trap.** As the document puts it, a fixed magic value such
  as `666-666` cannot be made to do something special once a search engine will tell anyone that
  it is a trap.

The conclusion is that duress responses must be **configurable PIN codes** rather than fixed
gestures or fixed values. The user chooses which PIN triggers which effect, so the attacker
cannot know from documentation alone whether the PIN they were given is real. The cost is that
the user must set it up in advance, which is a real usability problem and the reason many owners
never enable any of it.

------

## The response palette

Once duress responses are PINs, the design question becomes which responses to offer. In the
COLDCARD implementation these are stored as 14 slots in the second secure element, each holding a
hashed PIN together with a flags word, an argument, and optionally up to 64 bytes of seed
material.

![Where each trick-PIN flag is interpreted]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/duress-flag-interpretation-concept.png)

The flags divide into two groups, and the split is the interesting part.

**Interpreted by the bootloader**, in code that firmware upgrades cannot replace:

| Flag | Effect |
|---|---|
| `TC_WIPE` | Clear the processor's share of the seed key |
| `TC_BRICK` | Roll the secure element's pairing secret to a value nobody records |
| `TC_FAKE_OUT` | Report the PIN as wrong while performing other effects |
| `TC_WORD_WALLET` / `TC_XPRV_WALLET` | Open a decoy wallet from a seed stored in the secure element |

**Interpreted by the wallet application**, because the user interface has to participate:

| Flag | Effect |
|---|---|
| `TC_DELTA_MODE` | Run the real wallet in a restricted state |
| `TC_COUNTDOWN` | Show a login countdown, `tc_arg` carrying the number of minutes |
| `TC_BLANK_WALLET` | Present the device as having no seed |
| `TC_REBOOT` | Restart with no change of state |
| `TC_FW_DEFINED` | Firmware-defined behaviour, used for the spending-policy bypass PIN |

The dividing line is a mask, `TC_HIDDEN_MASK = 0xf800`, covering exactly the first group. Those
bits are stripped before the result is handed to the application, so the wallet code is never
told that a wipe, a brick, or a decoy login occurred. This is a deliberate compartmentalisation:
the Python layer is large, replaceable, and the part an attacker would most plausibly modify, so
it is kept ignorant of the facts that would betray the user.

------

## Hiding the response

Offering a duress mode is easy. Making its use undetectable is the actual engineering, and it
happens at three levels.

**On the bus.** The function that tests a PIN against the trick slots always checks all of them,
with a comment in `se2.h` stating the reason directly: *"will always check all slots so bus
traffic doesn't change based on result"*. A constant number of transactions means an attacker
watching the I2C lines sees the same pattern whether the PIN matched a trick slot or not.

**In the processor.** The wipe operation clears the current replaceable key in the main
processor's own flash. It is one write, it produces no traffic on either secure-element bus, and
there is nothing for an attacker to interrupt or block. This matters because the alternative
design, clearing the seed inside a secure element, would be visible on the wire and could be
attacked by cutting power at the right moment.

**On the screen.** A decoy login is made to look like a normal one. The device does not display
which wallet it opened, and the failure counter is suppressed when a decoy PIN was used, because
showing "1 failed attempt" after a successful duress login would give the game away.

There is a fourth level that the documentation admits is not solved, and it is worth quoting
because vendors rarely write this down. From `docs/pin-entry.md`:

> When the duress password succeeds, activity on the bus would be clearly different from the
> normal PIN. There is nothing we can do about that because traffic analysis of the bus is not
> hard even though the all sensitive data is encrypted.

The bus traffic *pattern* leaks, even though the *content* does not. A decoy wallet lives in a
different place and is fetched differently from the real one, so an attacker with probes attached
can tell that something other than a normal login happened. The documented recommendation follows
from that: if wires are attached to the board, use a brick PIN rather than a decoy, because
bricking completes in roughly 50 milliseconds, well before any confirmation appears on screen and
too fast to interrupt.

------

## Decoys, and when they fail

A decoy wallet only works if the attacker believes it is the whole story. Two design details
determine whether that holds.

**Where the decoy seed comes from.** The COLDCARD derives duress wallets from the real seed using
[BIP-85](https://github.com/bitcoin/bips/blob/master/bip-0085.mediawiki) at reserved indices,
1001 to 1003 for 24-word wallets and 2001 to 2003 for 12-word wallets. The practical consequence
is that backing up the real seed also backs up every decoy, so funds placed in a decoy are not
lost when the device is. Older firmware used a fixed derivation path, `m/2147431408'/0'/0'`, for
the same reason. A decoy generated from independent randomness would need its own backup, which
users would not make.

**What the attacker already knows.** This is where a decoy fails. If the attacker has seen an
extended public key, from a watch-only wallet on a laptop or an exported descriptor, they know the
real balance and can check on-chain whether the wallet they are being shown is the one they came
for. `docs/security-model.md` states this as the motivation for a different mechanism entirely.

The answer offered is **delta mode**, which inverts the usual logic. Instead of showing a fake
wallet, it opens the real one. The delta PIN differs from the true PIN only in the last four
digits, and the bootloader reconstructs the true PIN by substituting four digits carried in the
slot argument. The device then behaves normally, showing the correct extended public keys and the
correct UTXO set, so an attacker checking against their research sees exactly what they expected.

What they cannot do is spend. Transactions signed in delta mode carry signatures that do not
verify, so a broadcast attempt is rejected by the network. Any action that would expose key
material, viewing the seed words or opening the trick-PIN menu, wipes the seed instead. It buys
time and plausibility rather than safety, and the documentation is explicit that it is not for
novices.

------

## Passive triggers

Every mechanism so far requires the victim to choose a PIN under pressure and enter it correctly.
Two features remove that requirement, which arguably makes them the most useful of the set.

**MicroSD as a second factor** inverts the usual logic of a second factor. Once enrolled, the
device expects a specific card to be present at login; if the slot is empty or the card is not
recognised, the seed is wiped after the correct PIN is entered. The enrolment file is a small
encrypted blob whose key is derived from both the master secret and a hash of the card's unique
serial number read at a low level, so copying the file to another card does not work.

The duress property follows from the default state. Keep no card in the device, and a coerced
login wipes the seed with no action from the user at all, nothing shown on screen, and no
decision to make while under pressure. `docs/microsd-2fa.md` recommends exactly this, and notes
that the enrolled card can live in a safe deposit box because it contains nothing sensitive.

**The kill key** assigns a single keypress to trigger a wipe during login. On the Mk models it is
active while the anti-phishing words are shown; on the Q any letter can be assigned and it works
throughout the login sequence, including while the nickname is displayed. `shared/login.py`
handles it inline with normal key processing. The documentation warns against choosing the first
digit of the PIN's second half, which is a good illustration of how narrow the usable design space
is: a defence that fires on a common keystroke will eventually fire by accident.

![Choosing a duress response]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/duress-response-selection-workflow.png)

------

## A different approach: passphrase-derived hidden wallets

Trezor solves the same problem with [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
passphrases rather than with duress PINs. Any passphrase produces a valid wallet, so the device
holds no notion of a "real" or "hidden" one, and there is no stored flag an attacker could find
by examining the device.

The trade-offs run in both directions.

- **Deniability of existence.** The passphrase approach has the stronger story here: since every
  passphrase yields a wallet, there is nothing on the device that proves another wallet exists.
  A trick-PIN table, by contrast, is stored state, even if it is hashed and its outcomes are
  hidden from the application layer.
- **Response richness.** The trick-PIN approach can do things a passphrase cannot: destroy the
  seed, brick the device, start a countdown, or open a decoy while suppressing the failure
  counter. A passphrase wallet is only ever a wallet.
- **Failure mode under a knowledgeable attacker.** Both fail the same way against an attacker who
  knows the target's extended public key. Neither a hidden wallet nor a decoy satisfies someone
  who can check the balance they expected against the one they are shown.
- **User error.** A forgotten passphrase means permanently lost funds with no recourse, and there
  is no counter to warn the user. A misconfigured duress PIN generally fails safe, though a delta
  PIN with the wrong length is simply dropped on restore.

Neither is strictly better. The passphrase model minimises stored state; the trick-PIN model
maximises the range of responses. A design that wanted both would have to accept the storage.

------

## What none of this solves

Four limits deserve stating plainly, since they bound the whole category.

**Traffic analysis.** Covered above, and conceded in the vendor's own documentation. Against an
attacker with probes on the board, a duress login is distinguishable from a normal one.

**Knowledge asymmetry.** Every deception mechanism assumes the attacker does not already know what
they should be seeing. Once they do, decoys stop working and only destructive or degrading
responses remain useful.

**Finite resources.** Wipes consume one of 256 write-once key slots over the life of the device.
Trick PINs occupy 14 slots, one of which is avoided on the Mk4, and a decoy wallet takes two
contiguous slots (three for the legacy format). These are generous limits, but they are limits.

**The user.** Every mechanism here has to be configured in advance by someone imagining a
situation they would rather not think about, and the passive triggers exist precisely because the
active ones cannot be relied on. The most robust configuration in this whole design is the one
that requires the victim to do nothing at all.

------

## Conclusion

The design problem here is not cryptographic. Every mechanism described above is built from
ordinary primitives, and none of them would be interesting in isolation. What makes them work, to
the extent they do, is the attention paid to what an attacker can observe: constant bus traffic
regardless of outcome, a wipe that produces no external signal, hidden flags stripped before the
application layer can learn them, and a suppressed failure counter after a decoy login.

The honest reading of the documentation is that these defences degrade in a specific order.
Against an opportunistic thief, a decoy wallet works. Against someone who researched the target,
only delta mode or destruction does. Against someone with probes on the board, the vendor's own
advice is to stop trying to deceive and destroy the secret instead. And against an attacker
willing to keep the user rather than the device, none of it applies.

The mechanisms most likely to help are the ones that need no presence of mind: an absent memory
card that wipes the seed automatically, or a single key pressed during a login that was going to
happen anyway.

![Designing for coercion mindmap]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/2026-07-31-hardware-wallet-duress-mindmap.png)

------

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Duress PIN** | A PIN, configured in advance, that performs some effect other than a normal login, such as opening a decoy wallet or destroying the seed. |
| **Trick slot** | One of 14 records in the second secure element holding a hashed PIN, a flags word, an argument, and optionally seed material for a decoy wallet. |
| **Hidden flag mask** | The bitmask covering wipe, brick, fake-out and both decoy-wallet flags; those bits are removed before the result reaches the wallet application. |
| **Decoy (duress) wallet** | A functional wallet with its own funds, derived deterministically from the real seed so the main backup also covers it, presented to an attacker in place of the real one. |
| **Delta mode** | A duress PIN differing from the real one only in its last four digits, which opens the real wallet but produces invalid signatures and wipes the seed on any attempt to expose key material. |
| **Fast Wipe** | Destruction of the seed by clearing the processor's share of the decryption key, producing no traffic on either secure-element bus. |
| **Brick PIN** | A duress PIN that permanently disables the device by rotating a shared secret to a value nobody records, completing in about 50 milliseconds. |
| **Look-blank** | A response that presents the device as having no seed while leaving all data intact. |
| **MicroSD 2FA** | An enrolment scheme where a specific card must be present at login; its absence wipes the seed, making inaction the duress response. |
| **Kill key** | A single keypress, configured in advance, that triggers a seed wipe during the login sequence with no visible indication. |

------

## Annex — Security Implementation Checklist

For anyone designing or reviewing duress features in a device that holds bearer secrets.

### Indistinguishability

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Candidate PINs are tested against every duress slot on every attempt, in constant time and constant traffic. | The number or timing of bus transactions reveals that a duress PIN matched. |
| ☐ | Destructive responses execute locally, with no traffic on an external bus. | An attacker can cut power or jam the bus to prevent the wipe and retry. |
| ☐ | The user interface after a decoy login is identical to a normal login. | A visible difference (a counter, a label, a delay) betrays the deception. |
| ☐ | Failure counters are suppressed when a decoy login succeeds. | A non-zero failure count after a "successful" login is a tell. |
| ☐ | Sensitive outcomes are masked before reaching replaceable application code. | Modified or curious application code can report that a wipe or decoy occurred. |

### Trigger design

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Duress responses are user-configured values, not fixed gestures or documented magic numbers. | A published trigger is a trigger the attacker watches for. |
| ☐ | At least one response requires no action from the user under duress. | A defence that depends on presence of mind is unavailable when it is needed. |
| ☐ | Any single-keystroke trigger is chosen so it cannot fire during normal use. | Accidental destruction of the seed by an ordinary keypress. |
| ☐ | The device can be unlocked remotely by voice or text without losing the duress option. | Defences that require physical presence do not cover the extraction-by-phone case. |

### Decoy integrity

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Decoy seeds derive deterministically from the real seed. | A decoy needing its own backup will be unbacked, so its funds are lost with the device. |
| ☐ | A decoy wallet behaves as a full wallet, including signing and receiving. | An attacker who tests the wallet detects it is a shell. |
| ☐ | Changing a PIN while logged into a decoy does not reveal the deception. | Probing the PIN-change path distinguishes decoy from real. |
| ☐ | Degraded modes produce invalid signatures rather than restricted menus. | A restricted interface is noticed; an invalid signature is not, until broadcast. |

### Honest limits

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Documentation states which observers defeat which defence. | Users choose a decoy in a situation where destruction was the only viable answer. |
| ☐ | Finite resources (key slots, duress slots) are surfaced to the user. | A defence silently becomes unavailable after repeated use. |
| ☐ | Recovery from a duress wipe is possible from an existing backup. | The defence and total loss become the same outcome. |

------

## Frequently Asked Questions

**Q: Why not use a secret key combination instead of a duress PIN?**

Three reasons, all from the vendor's own design notes:

- **It has to be documented**, so it is public, so an attacker who has read the manual watches for it.
- **The user may not be present.** PINs get extracted by phone or found written down, and a keystroke cannot be performed in either case.
- **A known magic value is not a trap.** A fixed code such as `666-666` cannot do anything special once anyone can search for what it does.

A configurable PIN carries none of these problems: the attacker knows the feature exists but cannot know whether the value they were handed is real.

**Q: If the attacker can watch the bus, does any of this work?**

Deception does not; destruction does. The vendor states plainly that a successful duress login looks different on the bus even though the payload is encrypted, because traffic analysis does not need to decrypt anything. Against that observer, the recommended response is a brick PIN, which rotates a shared secret to an unknown value in about 50 milliseconds, far faster than an attacker could react to the visible bus activity.

**Q: What is the point of a mode that opens the real wallet?**

It addresses an attacker who has done research. Someone who found an extended public key on the victim's computer knows the real balance and can verify on-chain whether they are being shown the right wallet, so a decoy fails immediately. Delta mode shows them exactly the wallet they came for, which satisfies the check, while quietly producing signatures that the network will reject and wiping the seed if they try to view the key material.

**Q: How do duress wallets get backed up?**

They do not need separate backups, because they derive deterministically from the real seed, at reserved BIP-85 indices in current firmware and at a fixed derivation path in older versions. Writing down the real seed therefore captures every decoy and any funds sitting in them. This is a deliberate choice: a decoy generated from independent randomness would need its own backup, and in practice nobody would make one.

**Q: How does the passphrase approach compare?**

They optimise for different properties. A passphrase-derived hidden wallet leaves no stored state proving another wallet exists, which is the stronger deniability story. A duress-PIN table can do things a passphrase cannot: destroy the seed, brick the device, start a countdown, or open a decoy while hiding the failure counter.

Both fail against the same adversary, the one who already knows the extended public key they are looking for, and both depend on setup the user must do before anything goes wrong.

**Q: Which of these features is actually worth enabling?**

The ones requiring no action under pressure, on the reasoning that a coerced person cannot be relied on to execute a plan. Enrolling a memory card as a second factor and then keeping no card in the device means a coerced login wipes the seed automatically, with nothing shown on screen and no decision to make. A configured kill key is second, since it needs one keystroke during a login that was happening anyway. Decoy wallets need funding, maintenance, and an attacker who has not done their homework, which is a longer list of conditions.

------

## References

### Analyzed source

- [Coldcard/firmware](https://github.com/Coldcard/firmware) — analyzed at commit [`3238f6fd9977eed786012d0034a04d888c3263bb`](https://github.com/Coldcard/firmware/tree/3238f6fd9977eed786012d0034a04d888c3263bb) (release [2026-07-31T0519-v5.6.0](https://github.com/Coldcard/firmware/releases/tag/2026-07-31T0519-v5.6.0)), 2026-07-31

### Design documentation

- [`docs/security-model.md`](https://github.com/Coldcard/firmware/blob/master/docs/security-model.md) — trick PIN catalogue, delta mode rationale
- [`docs/pin-entry.md`](https://github.com/Coldcard/firmware/blob/master/docs/pin-entry.md) — "Dark Duress Thoughts", why secret keystrokes were rejected
- [`docs/secure-elements.md`](https://github.com/Coldcard/firmware/blob/master/docs/secure-elements.md) — trick slot storage and hashing
- [`docs/microsd-2fa.md`](https://github.com/Coldcard/firmware/blob/master/docs/microsd-2fa.md) — card enrolment and the duress default
- [`docs/spending-policy.md`](https://github.com/Coldcard/firmware/blob/master/docs/spending-policy.md) — bypass PIN game theory
- [`docs/limitations.md`](https://github.com/Coldcard/firmware/blob/master/docs/limitations.md) — slot counts and delta-mode constraints

### Standards and background

- [BIP-39 — Mnemonic Code for Generating Deterministic Keys](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
- [BIP-85 — Deterministic Entropy From BIP32 Keychains](https://github.com/bitcoin/bips/blob/master/bip-0085.mediawiki)
- [XKCD 538 — Security](https://xkcd.com/538/)

### Related articles on this site

- [COLDCARD Firmware - Architecture and Security Model]({{site.url_complet}}/2026/07/31/coldcard-firmware-security/)
- [Trezor Crypto Wallet - Cryptography and Security]({{site.url_complet}}/2024/10/15/trezor-wallet-security/)
- [Hardware Fault Injection Attack]({{site.url_complet}}/2024/12/30/hardware-fault-injection-attack/)
