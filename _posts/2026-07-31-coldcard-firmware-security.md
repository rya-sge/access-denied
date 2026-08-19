---
layout: post
title: "COLDCARD Firmware - Architecture and Security Model"
date:   2026-07-31
last_modified_at: 2026-08-18
lang: en
locale: en-GB
categories: blockchain cryptography security
tags: blockchain wallet coldcard bitcoin hardware
series: firmware-security
description: How the COLDCARD hardware wallet firmware works - the bootloader/MicroPython split, dual secure elements, PIN key stretching, trick PINs, signed firmware, and reproducible builds.
image: /assets/article/blockchain/wallet/coldcard/2026-07-31-coldcard-firmware-security-mindmap.png
isMath: false
---

The [COLDCARD](https://coldcard.com) is a Bitcoin-only hardware wallet built by [Coinkite](https://coinkite.com). Its firmware is published in full, so the security claims can be read against the code that implements them. This article walks through that code base: how it is organised, where the secrets live, what happens between a keypad press and a decrypted seed, how the device decides that the firmware it is about to run is authentic, and which limitations the project documents about its own design.

The reading is based on the `master` branch at version 5.6.0 (Q firmware 1.5.0Q), the release published on 2026-07-31. The exact commit is pinned in the references.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

------

## What the repository contains

The project is not a single firmware image but a small ecosystem built around one: the device code, a desktop emulator of that code, the test suite that drives both, and the tooling that proves a published binary was built from this source.

| Directory | Role |
|---|---|
| `shared/` | The wallet itself: 93 MicroPython modules covering PSBT signing, multisig, settings, NFC, QR, secure notes, spending policy, and the whole user interface. |
| `stm32/` | The embedded build: board ports, three bootloaders, the signed-firmware header, makefiles, and the containerised reproducible build. |
| `unix/` | A desktop simulator that runs the same `shared/` code against a simulated display, keypad, microSD card, and secure elements. |
| `testing/` | 36 pytest files driving either the simulator (`--sim`) or a physical device (`--dev`), with a fixture module of roughly 96 KB. |
| `docs/` | 27 documents describing the design, including the security model, the PIN system, the memory map, and the reproducible build process. |
| `cli/` | `signit.py`, the tool that signs, splits, and inspects firmware images. |
| `external/` | Submodules: Coinkite's MicroPython fork, `libngu` for cryptography, `ckcc-protocol` for the USB protocol, and `mpy-qr`. |
| `hardware/` | Schematics and bills of materials for Mk3, Mk4, Mk5 and Q, published so researchers can rebuild the device from off-the-shelf parts. |

Two hardware families share this tree. The Mk line (Mk4, Mk5) uses an OLED screen and a numeric keypad; the Q uses a colour LCD, a full QWERTY keyboard, a QR scanner, a battery, and two microSD slots. Both are built around an STM32L4S5VI, and the firmware identifies the model at runtime by probing pins rather than by shipping separate trees. What differs between models is which modules get frozen into the image, expressed in `shared/manifest_mk4.py` and `shared/manifest_q1.py` against the common `shared/manifest.py`.

------

## The trust boundary inside the chip

The code that enforces PIN policy is not the code that runs the wallet, and the separation is enforced by hardware rather than by convention.

The bootloader occupies the first 112 KB of flash and is written in C. It is set at the factory and cannot be replaced in the field, not even by a firmware upgrade signed with a factory key. It holds the pairing secrets that authenticate the device to its secure elements, and it is the only code that can talk to them. Around it, the STM32 hardware firewall is configured to reset the processor if any address inside the protected range is touched from outside. Write protection on the first 14 flash pages and readout protection at level 2 (RDP=2) close the remaining paths. `docs/secure-elements.md` also credits PCROP here, but `storage.c` says otherwise in a comment: PCROP is exec-only and blocks even D-bus reads from inside the protected area, so the lockdown code sets `WRP1AR` and the RDP level instead.

Above it sits MicroPython, which is everything a user would call "the wallet". It reaches the bootloader through a single narrow entry point, the callgate, exposed in Python as `shared/callgate.py` and implemented in `stm32/mk4-bootloader/dispatch.c`. Each call is dispatched by method number, every pointer is range-checked against main SRAM before use, the input length is capped, and the bootloader wipes its own SRAM on entry and on exit. The comment in `dispatch.c` is explicit about the reason: *"range check pointers so we aren't tricked into revealing our secrets"*.

The practical consequence, spelled out in `docs/pin-entry.md`, is that a developer can replace essentially all of the Python layer and still cannot weaken the PIN policy, because rate limiting, attempt counting, and secret retrieval all happen on the far side of the firewall.

------

## Three parties hold the seed

Marks 1 through 3 used a single secure element. If that part had an undisclosed weakness, the seed was at risk. Mk4 changed the model by splitting the decryption key across three components from two different vendors plus the main processor, so that all three must fall before the seed is readable.

![COLDCARD key architecture: MCU, SE1 and SE2]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/coldcard-key-architecture-concept.png)

| Component | Part | What it holds |
|---|---|---|
| Main MCU | STM32L4S5VI | Pairing secrets for both secure elements, `mcu_hmac_key` fixed at factory time, `hash_cache_secret`, and 256 write-once "replaceable MCU key" slots. |
| SE1 | Microchip ATECC608 | The AES-encrypted 72-byte secret, the PIN key-stretching key, the monotonic attempt counter, and the flash checksum slot that drives the genuine light. |
| SE2 | Maxim DS28C36B | Fourteen hashed trick-PIN slots with their duress seeds, and two of the three inputs to the seed decryption key. |

The seed decryption key is assembled only after a correct PIN:

```
k = HMAC-SHA256(key = mcu_hmac_key,
                msg = SE2_easy_key || SE2_hard_key || current_replaceable_mcu_key)
```

and `k` is then used with AES-256-CTR over the secret stored in SE1. Authentication of that decryption is done by appending 32 zero bytes before encryption and checking they decode correctly, with the MAC held in a separate SE1 slot.

Two design details follow from this arrangement, and they do more work than the key schedule itself.

- **SE1 never holds a key that can decrypt its own contents.** Extracting the SE1 secret in full still yields ciphertext. Reaching the `SE2 hard key` requires SE1 to perform an ECC signature and an ECDH exchange, which requires the PIN.
- **The MCU can destroy its share instantly.** Clearing the current replaceable key is a single flash write inside the processor. `docs/security-model.md` calls this Fast Wipe, and its value is that it produces no traffic on either bus, so an attacker probing the I2C line to SE2 or the single-wire line to SE1 has nothing to block or interrupt. Since the key is one of the three inputs, its loss makes the seed permanently undecryptable without touching either secure element. There are 256 such slots for the life of the device, and each wipe consumes one.

Both secure elements also authenticate their traffic. Most commands and responses are XORed with an HMAC-SHA256 value keyed by the relevant pairing secret, so an attacker who desolders the parts and inserts active circuitry cannot simply replay or forge exchanges. The MCU additionally captures values that should never change, such as chip serial numbers and the public halves of the joining keypairs, and refuses to accept different ones later.

------

## From keypad to seed

PINs are numeric, split into a prefix and a suffix, each between two and six digits. The path from those digits to a usable seed involves both secure elements and is deliberately slow.

![COLDCARD login workflow]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/coldcard-pin-login-workflow.png)

### Hashing and key stretching

The bootloader first computes a device-unique digest:

```
md = SHA256(SHA256(pairing_secret || purpose_salt || pin_digits))
```

The pairing secret makes the result unique per device, so the same PIN on two COLDCARDs produces unrelated values. The purpose salt separates the anti-phishing computation from the login computation.

That digest is then stretched by repeated HMAC-SHA256 operations whose key lives only inside SE1, eight rounds for a login attempt and twelve for the anti-phishing words in the documented constants. The point is not computational hardness in the usual sense, because SHA-256 is cheap. It is that each round requires a full round trip over SE1's single-wire protocol at 230,400 bps, including a nonce exchange and a `CheckMac` challenge on the pairing secret. `docs/pin-entry.md` works the arithmetic out to about 30 ms per iteration in the best case, and measures the real login delay at roughly four seconds. No attacker can go faster, because only the chip knows the HMAC key.

### The attempt counter

Rate limiting alone would not be enough, so SE1 also enforces a hard ceiling. A monotonically increasing counter tracks failures; it cannot be reset, decremented, or bypassed, and only a correct PIN updates the "last successful attempt" record. After 13 failures the secure element bricks itself and the device becomes unrecoverable. This is the mechanism behind the blunt statement in the documentation that a forgotten PIN with no seed backup is unrecoverable, by anyone, including the vendor.

### Anti-phishing words

Between the prefix and the suffix, the device shows two words drawn from the [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) English list. They are derived from 22 bits of the stretched prefix hash, giving roughly four million combinations, using an [HMAC](https://csrc.nist.gov/csrc/media/publications/fips/198/1/final/documents/fips-198-1_final.pdf) key that exists only inside that one chip.

The purpose is to defeat a substituted device. Because the HMAC key never leaves the genuine unit's SE1, a doppelgänger cannot compute the correct pair, and a user who memorises the words for their own prefix can stop after entering only that prefix. `docs/pin-entry.md` notes the residual case: an attacker who both knows the victim's prefix and has had access to the real device could record the words it displays and replay them on a substitute. Trying several different prefixes defeats that, and the same rate limiting is what makes harvesting every prefix-to-word mapping from a stolen device impractical.

------

## Trick PINs

Any PIN other than the true one can be configured to do something. This replaces the older single duress PIN and single "brick me" PIN with fourteen programmable slots in SE2, each holding a hashed PIN plus flags and arguments, and optionally up to 64 bytes of seed material.

The behaviour flags are defined in `stm32/mk4-bootloader/se2.h`:

| Flag | Effect |
|---|---|
| `TC_WIPE` | Clear the replaceable MCU key, destroying access to the seed. |
| `TC_BRICK` | Roll the SE1 pairing secret to a value nobody knows, permanently. |
| `TC_FAKE_OUT` | Report the PIN as incorrect while performing other configured effects. |
| `TC_WORD_WALLET` / `TC_XPRV_WALLET` | Log in to a duress wallet whose seed is stored in SE2. |
| `TC_DELTA_MODE` | Reconstruct the true PIN from the entered one and run in a restricted mode. |
| `TC_REBOOT` | Restart the device with no change of state. |

Three properties of the implementation are worth separating from the feature list.

- **Every PIN is tested against every slot.** The comment on `se2_test_trick_pin()` states that all slots are always checked *"so bus traffic doesn't change based on result"*. An observer watching the I2C bus cannot distinguish a trick hit from a miss.
- **The most sensitive effects are invisible to the wallet code.** `TC_HIDDEN_MASK` covers wipe, brick, fake-out, and both duress-wallet flags, and those bits are stripped before the result is handed to MicroPython. The Python layer cannot report what it is not told. Delta mode is deliberately excluded from the mask, because the application needs to know it is running hobbled.
- **Duress wallets are derivable from the real seed.** They come from [BIP-85](https://github.com/bitcoin/bips/blob/master/bip-0085.mediawiki) derivation at reserved account indices (1001 to 1003 for 24-word wallets, 2001 to 2003 for 12-word), so backing up the main seed also backs up the decoy and its funds. Legacy duress wallets sit at the fixed path `m/2147431408'/0'/0'`.

Delta mode deserves its own note because it inverts the usual duress logic. Rather than presenting a decoy wallet, it opens the real one: the trick PIN differs from the true PIN only in the last four digits, and the bootloader reconstructs the true PIN by substituting four digits carried in the slot argument. The device then behaves normally, with the real extended public keys and the real UTXO set, which defeats an attacker who has researched the target's wallet and would notice a decoy. What it will not do is produce valid signatures, and any attempt to view seed words or reach the trick PIN menu wipes the seed. The threat model it addresses is an attacker who already knows which wallet they are looking for.

`docs/security-model.md` is candid about the residual risk: an attacker sophisticated enough to probe the buses can tell that *something* different happened when a duress PIN succeeds, even though the payload is encrypted, because traffic analysis is not hard. The documentation's own advice is that in that situation the brick PIN is the better answer, since it completes in about 50 ms, well before any on-screen confirmation appears.

------

## Proving the firmware is genuine

The device answers two separate questions at boot: *is this firmware signed by someone I trust*, and *has anything in my flash changed since the last time the owner approved it*.

### The signed header

Every image carries a 128-byte header (`stm32/sigheader.h`) placed in an unused gap ending 16 KB into the binary, with magic value `0xCC001234`. It holds a BCD timestamp, a human-readable version string, the index of the public key used, the firmware length, an `install_flags` field, a `hw_compat` bitmask naming the models allowed to run it, and a 64-byte secp256k1 signature over the double-SHA256 of the image.

The bootloader trusts six public keys. Key 0 is published in the repository, private half included, so anyone can sign their own build. Keys 1 to 5 are factory keys. Firmware signed with key 0 boots, but on Mk4 and later it always shows a warning screen with a forced delay, and unlike earlier generations that warning can no longer be suppressed by blessing the firmware with the main PIN. `docs/dev-access.md` describes this path as officially supported for third-party development, with the caveat that a crash before the upgrade path is reachable leaves a brick.

Downgrade protection is separate from signing. Timestamps of installed versions are recorded into the MCU's one-time-programmable area, and `check_is_downgrade()` refuses any image whose timestamp is older than the recorded high-water mark. A signature alone does not let an attacker roll the device back to a version with a known bug.

### The world checksum

The genuine light is not a status flag the firmware sets. At boot, the bootloader computes a double-SHA256 over roughly 1.59 MB spanning the firmware, the bootloader including its pairing-secret page, the unprogrammed and filesystem regions, the OTP area, both option-byte banks, the STM system ROM, and the device serial number. The MCU keys page is excluded, since it changes at runtime by design.

That digest is proved against a value stored in SE1 slot 14. Anyone can turn the light red, since that requires no authentication, but turning it green requires knowing both the pairing secret and the existing slot value, and the LED lines are wired to SE1 rather than to the processor. Updating the expected value requires the main PIN. An evil maid who reflashes the device therefore cannot restore a green light without the PIN, which is the entire point of the mechanism.

Physical bit-flipping attacks are addressed by the memory rather than by the firmware. Flash cells carry 8 ECC bits per 64-bit word, correcting single-bit errors and detecting double-bit errors; a detected double-bit error raises a non-maskable interrupt and crashes the processor. `docs/security-model.md` states plainly that the project treats any such event as an attack, for example targeted UV-C exposure of the bare die, and accepts bricking as the outcome.

------

## Upgrade and recovery

Since Mk4 the external SPI flash chip is gone, and firmware images are staged in an 8 MB PSRAM chip which forgets everything at power down. That creates an obvious hazard: a power cut during the 15 seconds of flash programming would leave no complete copy of the firmware anywhere. The recovery design is arranged so this is survivable without opening a hole.

![Firmware upgrade and recovery sequence]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/coldcard-firmware-upgrade-sequence.png)

The ordering is the security-relevant part. The world checksum for the *new* image is computed and written into SE1 **before** any flash is erased. Every recovery path then requires a candidate image to reproduce that stored value.

- If the device resets while PSRAM still holds the image, the bootloader re-verifies the signature and the world checksum and resumes.
- If power was actually lost, PSRAM is empty, and the screen asks for a microSD card. Every DFU file found is checked for a valid factory signature and for a world checksum matching the value in SE1.

`docs/upgrade-recovery.md` explains the attack this ordering blocks. An attacker could corrupt one bit of main flash to force recovery mode, then place a different factory-signed image in PSRAM, perhaps an older version with a feature they want. The world checksum makes that fail, because only the image that was actually being installed reproduces it. The same rule means recovery mode cannot be used to load new code, only to finish an interrupted install, which is why the project deliberately provides no key combination to enter recovery mode.

------

## The wallet layer

Above the security machinery sits a conventional but strict Bitcoin wallet.

**Transaction signing.** `shared/psbt.py`, the largest module at about 101 KB, parses [PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki) files up to 2 MB held in PSRAM. Its central concern is change-output validation: the presence of a derivation path in the PSBT is treated as a claim to be verified, not as information to be trusted. A mismatch between the claimed key path and the actual output script raises `FraudulentChangeOutput` rather than a warning, on the reasoning stated in the code that these are not innocent errors. Fees above a configurable share of the transaction value (10% by default) are rejected outright, and anything above 5% raises a warning. Non-`ALL` sighash flags produce warnings, and `NONE` variants are rejected unless explicitly enabled.

**Multisig.** `shared/multisig.py` requires registration of a wallet before it will sign for it, enforces unique fingerprints across cosigners, caps cosigners at 15 due to the `scriptSig` size limit, and treats [BIP-67](https://github.com/bitcoin/bips/blob/master/bip-0067.mediawiki) sorted and unsorted variants of the same key set as duplicates on import.

**Settings.** `shared/nvstore.py` stores configuration as JSON encrypted with AES-256-CTR in an LFS2 flash area, keyed from the wallet secret itself, across 100 slots. The counter includes the slot number, so an entry cannot be relocated, and a SHA-256 check detects tampering. Before login, a fixed public key is used instead, which is what allows a nickname or a login countdown to be shown before any secret is available.

**Host communication.** `shared/usb.py` establishes an ECDH session key over secp256k1 and runs AES-256-CTR over it, with a `mitm` command that signs the session key with the wallet's master key so a host can confirm it is talking to the expected device. In HSM mode, which the Mk line supports and the Q does not, only a whitelist of commands remains reachable.

**Policies and transfers.** `shared/ccc.py` implements spending policy in both single-signer and multisig-cosigner forms, with per-transaction magnitude caps, velocity limits keyed on `nLockTime` block heights, an address whitelist of up to 25 entries, and optional web 2FA. `shared/teleport.py` moves secrets between two Q devices using ECDH plus a second layer keyed by an 8-character password stretched with 5000 rounds of PBKDF2-SHA512, transported over QR codes and NFC.

**Backups.** `shared/backups.py` and `shared/compat7z.py` write standard 7z archives with AES-256, protected by a 12-word BIP-39 passphrase the device generates, giving roughly 132 bits of entropy without relying on the archive format's own key stretching. The format is deliberately standard so that funds can be recovered with ordinary tools.

------

## Reproducible builds

A signed binary from a vendor proves who built it, not what it was built from. The project closes that gap with `make repro`, which runs in Docker, requires a clean tree and matching submodules, downloads the published DFU from `coldcard.com`, splits it into firmware and bootrom, verifies both signatures, and diffs a hexdump of the locally built image against the published one with the 64 signature bytes elided.

```bash
git clone https://github.com/Coldcard/firmware.git
cd firmware
git checkout 2026-07-31T0519-v5.6.0
cd stm32
make -f MK-Makefile repro          # Q1-Makefile for the Q
```

`docs/notes-on-repro.md` breaks the process down step by step for anyone who does not want to trust the wrapper. The result verifies the application firmware; the bootloader is factory-set and can only be inspected by asking the device to hash itself with a caller-supplied nonce, which is what callgate method 1 does.

------

## Documented limits

The project's `docs/limitations.md` states the boundaries of the design directly. Some entries that matter for security reasoning:

- **Temporary seeds bypass the secure elements by design.** The documentation states that they *"completely defeat the design of Coldcard's security model"*, because the secret lives in RAM rather than in SE1. They exist for one-off recovery and balance checks. A BIP-39 passphrase has been handled internally as a temporary seed since version 5.2.0.
- **Fast Wipe is finite.** 256 MCU key slots exist for the life of the device, and each wipe consumes one.
- **Trick PIN slots are scarce.** Fourteen exist, one is avoided on Mk4, and a duress wallet consumes two contiguous slots (three for the legacy format).
- **A delta-mode PIN must match the true PIN's length** and differ only in the final four positions.
- **Address ownership checks are bounded**, covering only the first 1528 addresses per wallet and not searching the Seed Vault.
- **Coinbase transactions are not signed**, and only a single multisig wallet may be involved in one PSBT.

To this the security documentation adds the honest caveats already noted: bus traffic analysis can reveal that a duress PIN succeeded, and a brute-force attack against every PIN combination remains the theoretical last line of defence if all three components were fully compromised.

------

## A worked example: the v5.6.0 entropy hotfix

The release analysed here is itself a security fix, which makes it a useful illustration of how such a defect surfaces in this code base.

Per `releases/ChangeLog.md`, seeds generated by earlier firmware could carry as little as roughly 72 bits of entropy on Mk4, Mk5 and Q, against a 128-bit design target, and roughly 40 bits on Mk3 for versions 4.0.1 and later. Coinkite advises regenerating affected seeds, and is not planning a Mk3 update.

The corresponding change is commit `ca72463709f4e3f8964952039d5caf955f566a87`. Its effect in the tree is a build-system fix rather than an algorithm change: the board-local `rng.c` did not export `rng_get()`, so that symbol resolved to MicroPython's fallback software PRNG rather than to the hardware peripheral. Each board's `mpconfigboard.mk` now compiles upstream's `stm32/rng.c` to an empty object, the board-local `rng.c` exports `rng_get()` backed by the STM32 hardware RNG peripheral, and `stm32/shared.mk` gains a `rng-code-check` target that runs `arm-none-eabi-nm` at build time:

```makefile
rng-code-check:
	@upstream_symbols="$$($(NM) --defined-only $(BUILD_DIR)/rng.o)" || exit $$?; \
	if test -n "$$upstream_symbols"; then \
		echo "ERROR: micropython's stm32/rng.o must not define any symbols"; \
```

The build now fails if upstream's `rng.o` defines any symbol at all, or if the board's object does not export a global `rng_get`. Two observations follow. First, the defect lived in the link step rather than in any reviewed cryptographic routine, which is a recurring blind spot in firmware built on a vendored upstream. Second, the fix ships with a mechanical check rather than a comment, so the whole class of defect is closed instead of the single instance.

------

## Conclusion

The COLDCARD firmware organises its defences around one arrangement: the code that decides whether to release the seed is not the code that runs the wallet, and neither of them holds the seed key alone. The bootloader sits behind a hardware firewall with a narrow callgate; the key material is split across two secure elements from different vendors and the processor itself; and the processor's share can be destroyed faster than an attacker with probes on both buses can react.

Around that core, the remaining mechanisms are mostly about verification rather than secrecy. Signed headers and a whole-flash checksum held in a secure element establish what is running, downgrade protection through OTP timestamps bounds which versions can run, an ordering rule on the upgrade path ensures recovery can only finish an interrupted install, and reproducible builds let a user connect the published binary back to the published source.

The documentation is candid about what remains outside the model: bus traffic analysis can distinguish a duress login, temporary seeds deliberately step outside the secure elements, and finite resources such as MCU key slots and trick PIN slots bound how often some defences can be used. The 5.6.0 release is a reminder that the weak point is not always in the parts a threat model examines closely, since low-entropy seed generation arrived through the link step rather than through any of the cryptography described above.

![COLDCARD firmware mindmap]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/2026-07-31-coldcard-firmware-security-mindmap.png)

------

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Pairing secret** | A 32-byte value held by the bootloader and shared with a secure element, used to authenticate and encrypt every exchange between them; a separate one exists for SE1 and SE2. |
| **Callgate** | The single, method-numbered entry point through the STM32 firewall by which MicroPython requests bootloader services, with all pointers range-checked and bootloader SRAM wiped on entry and exit. |
| **World checksum** | A double-SHA256 over the firmware plus the surrounding flash, OTP, option bytes, system ROM and serial number, stored in SE1 and required to turn the genuine light green. |
| **Replaceable MCU key** | One of 256 write-once flash slots holding the processor's share of the seed decryption key; clearing the active slot is the Fast Wipe operation. |
| **Fast Wipe** | Destruction of the seed by clearing the replaceable MCU key inside the processor, leaving no observable traffic on either secure-element bus. |
| **Fast Brick** | Permanent disabling of the device by rotating the SE1 pairing secret to a value that is never recorded, making the secure element unreachable. |
| **Trick PIN** | Any PIN other than the true one, stored hashed in SE2 with flags and arguments describing the effect it triggers, from wiping the seed to opening a duress wallet. |
| **Delta mode** | A trick PIN differing from the true PIN only in its last four digits, which opens the real wallet in a restricted state where signatures are invalid and any attempt to expose key material wipes the seed. |
| **Anti-phishing words** | Two BIP-39 words derived from 22 bits of a stretched hash of the PIN prefix using a key held only inside SE1, shown mid-login so a substituted device can be detected. |
| **Key stretching** | Repeated HMAC-SHA256 rounds performed inside SE1 whose cost is dominated by the chip's serial protocol, bounding the rate at which PIN guesses can be tested regardless of attacker compute. |

------

### Security Implementation Checklist

Derived from the mechanisms described above. Each row is a property that separates a secure implementation of this class of device from an insecure one, phrased so it can be checked against code or a design document.

#### Secret storage and key separation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | No single component holds a key sufficient to decrypt the seed on its own. | Compromise of one secure element or of the processor yields the seed outright. |
| ☐ | Secrets held in a secure element are stored encrypted with a key that element does not possess. | An undisclosed weakness in that part exposes plaintext seed material. |
| ☐ | Keys come from separate vendors where two secure elements are used. | Shared silicon or shared firmware bugs defeat the point of having two parts. |
| ☐ | Values that must never change (chip serial numbers, joining public keys) are captured and re-checked. | Part substitution during an active attack goes undetected. |
| ☐ | Destruction of the processor's key share is a single local write with no external bus traffic. | An attacker probing the buses can block or interrupt the wipe and retry PINs freely. |

#### PIN handling

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | PIN hashing mixes in a device-unique secret before any comparison. | Precomputed tables work across devices, and hashes become comparable between units. |
| ☐ | Key stretching is performed by the secure element, not by the host processor. | An attacker who replaces the firmware simply skips the delay and brute-forces at full speed. |
| ☐ | Failed attempts increment a monotonic counter that cannot be reset without the correct PIN. | Unlimited guessing defeats a short numeric PIN regardless of per-attempt delay. |
| ☐ | Rate limiting and attempt counting live in code that field firmware cannot replace. | Custom firmware removes the policy while retaining access to the secrets. |
| ☐ | The anti-phishing response is shown after the prefix and before the remaining digits. | A substituted device collects the full PIN before the user can detect it. |

#### Duress and covert response

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every entered PIN is tested against all trick slots, with constant bus traffic. | Timing or traffic differences reveal to a probing attacker that a duress PIN was used. |
| ☐ | The most sensitive trick outcomes are masked before the application layer sees them. | Compromised or curious application code can report that a wipe or duress login occurred. |
| ☐ | Duress wallets are derived deterministically from the real seed. | A decoy wallet not covered by the main backup silently loses the funds placed in it. |
| ☐ | Signatures produced in a hobbled mode are invalid rather than merely restricted. | An attacker who reaches that mode can move real funds. |

#### Firmware authenticity

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The signature is verified over the whole image before execution, against a fixed set of trusted keys. | Arbitrary code runs with access to the PIN entry path. |
| ☐ | Header fields (length, magic, hardware compatibility, key index) are validated before the signature check. | Malformed headers reach parsing code or select an out-of-range key. |
| ☐ | Version timestamps are recorded in one-time-programmable memory and older images refused. | A properly signed but vulnerable old release can be reinstalled. |
| ☐ | The integrity indicator is controlled by the secure element and cannot be set by the processor alone. | Modified firmware can display a "genuine" state to the user. |
| ☐ | Unofficially signed images always warn the user, with no way to suppress the warning. | A user cannot distinguish vendor firmware from third-party firmware. |

#### Upgrade and recovery

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The expected post-upgrade integrity value is committed before any flash is erased. | An interrupted upgrade leaves no way to distinguish a legitimate resume from an injected image. |
| ☐ | Recovery accepts only an image reproducing the committed integrity value. | Forced recovery becomes a path for installing a different signed version. |
| ☐ | No user-accessible key sequence enters recovery mode. | The recovery path becomes a routine attack surface rather than a fault handler. |

#### Randomness

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | All seed and key generation draws from the hardware RNG, never from a fallback software PRNG. | Generated seeds carry far less entropy than intended and become searchable. |
| ☐ | The build fails if an unintended RNG implementation is linked in. | A silent link-order change reintroduces a weak generator without any source change. |
| ☐ | The RNG is validated at startup and refuses to return degenerate values. | A failed peripheral yields constant or repeated output that is accepted as random. |

------

## Frequently Asked Questions

**Q: Why are two secure elements used instead of one?**

Because the failure being designed against is not weak silicon in general but an undisclosed flaw in one specific part. SE1 (Microchip ATECC608) and SE2 (Maxim DS28C36B) come from different vendors, so they do not share design bugs or errata. Combined with the processor's own key share, the arrangement means a break in any single component leaves the seed encrypted under material the attacker still does not have.

**Q: What actually stops someone from brute-forcing a numeric PIN?**

Two independent mechanisms:

- **Rate limiting inside SE1.** The PIN hash is stretched by eight HMAC-SHA256 rounds whose key exists only inside the chip, and each round costs a full round trip over a 230,400 bps single-wire link. The measured login time is about four seconds, and no amount of attacker compute changes that, because the key cannot be extracted.
- **A monotonic attempt counter.** SE1 counts failures, the counter cannot be reset or reversed without a correct PIN, and at 13 failures the part bricks itself.

Replacing the firmware does not help, because both are enforced behind the hardware firewall in code that cannot be changed in the field.

**Q: If the firmware is open source and key 0's private half is published, what stops an attacker from installing their own build?**

Installing firmware requires the main PIN, which an attacker who had it would not need firmware for. Beyond that, an image signed with key 0 always shows a warning screen with a forced delay on Mk4 and later, and that warning can no longer be suppressed by blessing the firmware. Separately, any change to flash invalidates the world checksum held in SE1, so the genuine light turns red and cannot be restored to green without the main PIN.

**Q: What is the difference between Fast Wipe and Fast Brick?**

Fast Wipe clears the current replaceable MCU key inside the processor. The seed becomes undecryptable because one of the three inputs to the AES key is gone, but the device still works and can be loaded with a new seed. It consumes one of 256 slots.

Fast Brick rotates the SE1 pairing secret to a value that is never computed or recorded. The processor can no longer authenticate to SE1 at all, so the device is permanently unusable.

The choice between them is a duress decision. Wipe is recoverable from a backup and leaves a working device; brick is final but unmistakably terminal, which the documentation argues is the safer option when an attacker is watching the buses.

**Q: The device stages a firmware image in an external, unauthenticated PSRAM chip. Why is that not an obvious attack surface?**

Because the acceptance rule for a staged image is not "is it validly signed" but "does it reproduce the world checksum already written into SE1". That value is committed before any erase begins and covers the specific image the owner approved. An attacker who corrupts one bit of flash to force recovery mode and swaps in a different factory-signed image fails at that check, since a different image produces a different checksum. The same rule is why recovery from a microSD card can only finish an interrupted install and cannot load new code.

**Q: How can a user verify that the binary on their device matches this source?**

By combining two checks. `make repro` rebuilds the published release inside Docker and diffs it byte for byte against the download from `coldcard.com`, with only the 64 signature bytes excluded, which ties the published binary to the published source. For the bootloader, which is factory-set and not part of that build, callgate method 1 makes the device hash its own bootloader region with a caller-supplied nonce, so stored responses cannot be replayed, and the result can be compared against a hash computed from the tree.

------

## References

### Analyzed source

- [Coldcard/firmware](https://github.com/Coldcard/firmware) — analyzed at commit [`3238f6fd9977eed786012d0034a04d888c3263bb`](https://github.com/Coldcard/firmware/tree/3238f6fd9977eed786012d0034a04d888c3263bb) (release [2026-07-31T0519-v5.6.0](https://github.com/Coldcard/firmware/releases/tag/2026-07-31T0519-v5.6.0)), 2026-07-31

### Project documentation

- [COLDCARD Mk4/Mk5/Q Security Model](https://github.com/Coldcard/firmware/blob/master/docs/security-model.md)
- [Dual Secure Elements](https://github.com/Coldcard/firmware/blob/master/docs/secure-elements.md)
- [Coldcard PIN Design and Operation](https://github.com/Coldcard/firmware/blob/master/docs/pin-entry.md)
- [Coldcard Memory Map](https://github.com/Coldcard/firmware/blob/master/docs/memory-map.md)
- [Firmware Upgrade and Recovery Process](https://github.com/Coldcard/firmware/blob/master/docs/upgrade-recovery.md)
- [Notes on Reproducible Builds](https://github.com/Coldcard/firmware/blob/master/docs/notes-on-repro.md)
- [Backup Feature](https://github.com/Coldcard/firmware/blob/master/docs/backup-files.md)
- [Key Teleport](https://github.com/Coldcard/firmware/blob/master/docs/key-teleport.md)
- [Documented Limitations](https://github.com/Coldcard/firmware/blob/master/docs/limitations.md)
- [Developing on COLDCARD](https://github.com/Coldcard/firmware/blob/master/docs/dev-access.md)

### Standards

- [BIP-32 — Hierarchical Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
- [BIP-39 — Mnemonic Code for Generating Deterministic Keys](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
- [BIP-67 — Deterministic Public Key Ordering for Multisig](https://github.com/bitcoin/bips/blob/master/bip-0067.mediawiki)
- [BIP-85 — Deterministic Entropy From BIP32 Keychains](https://github.com/bitcoin/bips/blob/master/bip-0085.mediawiki)
- [BIP-174 — Partially Signed Bitcoin Transaction Format](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
- [FIPS 198-1 — The Keyed-Hash Message Authentication Code (HMAC)](https://csrc.nist.gov/csrc/media/publications/fips/198/1/final/documents/fips-198-1_final.pdf)

### Vendor and hardware

- [Coldcard product site](https://coldcard.com)
- [Coinkite blog: supply chain trust minimisation](https://blog.coinkite.com/supply-chain-trust-minimized/)
- [Microchip ATECC608 product page](https://www.microchip.com/en-us/product/ATECC608B)
- [Key Teleport web component](https://keyteleport.com/)

### Related articles on this site

- [Trezor Crypto Wallet - Cryptography and Security]({{site.url_complet}}/2024/10/15/trezor-wallet-security/)
- [Hardware Fault Injection Attack]({{site.url_complet}}/2024/12/30/hardware-fault-injection-attack/)
