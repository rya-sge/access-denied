---
layout: post
title: "Firmware Supply Chain - Reproducible Builds and Code Signing"
date:   2026-07-31
lang: en
locale: en-GB
categories: security blockchain
tags: firmware security reproducible-build code-signing coldcard
description: A signed firmware binary proves who built it, not what it was built from. How reproducible builds, deterministic toolchains and on-device signature checks close that gap, using the COLDCARD firmware as a worked example.
image: /assets/article/blockchain/wallet/coldcard/2026-07-31-firmware-reproducible-builds-mindmap.png
isMath: false
---

A code signature answers one question: who produced this binary. It says nothing about what
source that binary was compiled from. For a device holding private keys, the difference matters,
because a vendor with a signing key can sign anything, including a build that does not match the
published source, and nothing in the signature itself would reveal it.

Reproducible builds close that gap by making the compilation deterministic, so that anyone can
rebuild the published binary and compare it byte for byte. This article works through what that
requires in practice, using the [COLDCARD](https://coldcard.com) firmware as the example, and
then follows the chain onto the device to see which links a rebuild cannot cover.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

------

## The problem a signature does not solve

Firmware distribution normally works like this: a vendor builds a binary, signs it with a private
key, and publishes it. The device checks the signature against a public key burned into its
bootloader and refuses anything else. This stops third parties from installing their own code,
which is the threat most people have in mind.

It leaves three gaps.

- **The vendor is unconstrained.** A signature over a malicious build verifies exactly as well as
  a signature over an honest one. Publishing source alongside the binary changes nothing on its
  own, because nobody can check that the two correspond.
- **The build machine is in scope.** A compromised build server, or a backdoored compiler, yields
  a correctly signed binary that no key management can detect.
- **Coercion leaves no trace.** A vendor compelled to ship a targeted build has no technical
  obstacle, and the users who receive it see a valid signature.

The remedy is to make the mapping from source to binary verifiable by anyone: given the same
source, the same build must produce the same bytes. Then a published binary that differs from a
local rebuild is evidence, not a matter of opinion.

------

## What breaks determinism

Compilation is deterministic in principle and full of hidden inputs in practice. The usual
offenders:

- **Timestamps.** Anything that embeds the current date, from archive metadata to `__DATE__`
  macros to filesystem timestamps inside a generated image.
- **Paths.** Absolute build directories leaking into debug sections or assertion strings.
- **Toolchain version.** A different compiler, linker, or libc produces different code from
  identical source, so the toolchain has to be pinned as tightly as the source.
- **Dependency drift.** Submodules or packages resolved to "latest" rather than to a fixed
  revision.
- **Environment.** Locale, `PATH` ordering, parallel-build nondeterminism, and anything read from
  the ambient system rather than from the repository.

Each has to be either eliminated or fixed to a declared value. The COLDCARD build handles them
in a way that is worth reading as a checklist.

------

## The build, made deterministic

![What each link in the chain proves]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/repro-trust-chain-concept.png)

### Pinned inputs

`stm32/dockerfile.build` fixes the toolchain to a specific base image, `alpine:3.16.0`, and
installs the ARM cross-compiler from a pinned repository. The build runs inside that container
and nowhere else, so the local machine's compiler version stops being an input.

The source side is enforced by two makefile prerequisites in `stm32/shared.mk`, both of which
must pass before `repro` will run at all:

```makefile
repro: submods-match code-committed
```

`submods-match` runs `git submodule status` over every submodule declared in `.gitmodules` and
fails if any line is prefixed with a status character, meaning a submodule sits at anything other
than its recorded revision. `code-committed` runs `git diff --stat --exit-code` and fails on any
uncommitted change. Together they mean a reproducible build cannot silently include a local
modification, which is precisely the scenario a verifier is trying to rule out.

### Time, handled twice

Two distinct timestamp problems appear here, and they get two different solutions.

The first is the general one, solved with the
[`SOURCE_DATE_EPOCH`](https://reproducible-builds.org/docs/source-date-epoch/) convention:
build tooling that would otherwise read the clock reads this variable instead. `repro-build.sh`
derives it from the release filename, which itself encodes the publication time:

```sh
DT=$(basename $PUBLISHED_BIN | cut -d "-" -f1,2,3)
export SOURCE_DATE_EPOCH=$(python -c '...' "$DT")
```

So the rebuild inherits the original build's notion of "now" from the artefact it is checking
against.

The second is specific and more interesting. The firmware embeds a FAT timestamp used for files
on its internal filesystem, generated by `stm32/make_filetime.py` into `file_time.c`. Regenerating
that file on every build would change the binary every day. The script therefore reads the
existing file first and leaves it alone when it already carries the right version:

```python
if ('// version: %s\n' % version) in fd.read():
    print("==> %s already version %s; not changing it" % (out_fname, version))
    sys.exit(0)
```

The timestamp is keyed to the version number rather than to the calendar, and the generated file
is committed to the repository. A variable input has been converted into a constant that travels
with the source.

### Running it

![make repro workflow]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/repro-build-workflow.png)

```bash
git clone https://github.com/Coldcard/firmware.git
cd firmware
git checkout 2026-07-31T0519-v5.6.0
cd stm32
make -f MK-Makefile repro          # Q1-Makefile for the Q
```

Inside the container, `repro-build.sh` clones from the local `.git` rather than from the network,
initialises submodules, installs the signing tool into a virtualenv, and locates the published
binary. If it is not already in `../releases`, the script reads its exact filename out of the
signed hash list and downloads it:

```sh
PUBLISHED_BIN=`grep -F v$VERSION_STRING-$HW_MODEL-coldcard.dfu signatures.txt | dd bs=66 skip=1`
wget -S https://coldcard.com/downloads/$PUBLISHED_BIN
```

Then it builds, signs, and hands off to the comparison step.

------

## Comparing the result

A naive `cmp` of the two files would fail even on a perfect rebuild, for a reason worth stating
clearly: the binary contains its own signature. The verifier does not have the production private
key, so the locally built image is signed with the publicly available development key instead,
and those 64 bytes differ by construction.

`check-repro` in `stm32/shared.mk` deals with this by eliding exactly that range:

```makefile
check-repro: TRIM_SIG = sed -e 's/^00003f[89abcdef]0 .*/(firmware signature here)/'
    $(SIGNIT) split $(PUBLISHED_BIN) check-fw.bin check-bootrom.bin
    $(SIGNIT) check check-fw.bin
    $(SIGNIT) check firmware-signed.bin
    hexdump -C firmware-signed.bin | $(TRIM_SIG) > repro-got.txt
    hexdump -C check-fw.bin        | $(TRIM_SIG) > repro-want.txt
    diff repro-got.txt repro-want.txt
```

Three steps, each doing separate work:

- **`signit split`** parses the DFU container and writes out its two elements, the application
  firmware and the bootrom, printing their offsets and lengths so a reader can confirm the split
  was faithful.
- **`signit check`** decodes the 128-byte header of each binary and verifies the ECDSA signature
  against the public key named by the header's own `pubkey_num` field. Run on the published image
  it confirms a production key signed it; run on the local build it confirms the development key
  signed that one.
- **The hexdump diff** compares everything else. Using hexdumps rather than raw bytes is a
  usability choice: when the comparison fails, the output points at the offset.

An empty diff means the published binary and the local rebuild agree on every byte except the
signature. Since the signature is computed over those bytes, agreement on the content plus a
valid production signature over the published copy is what ties the vendor's key to this source
tree.

------

## Onto the device

A verified binary on a workstation is only half the question. The other half is whether the
device is running that binary, which is a separate mechanism with separate properties.

The COLDCARD bootloader checks the 128-byte header (`stm32/sigheader.h`) before executing
anything: magic value `0xCC001234`, a length within bounds, a hardware-compatibility mask, and a
`pubkey_num` that must be less than the number of known keys. Only then does it verify the
secp256k1 signature over the double-SHA-256 of the image. Validating the fields before using them
is the right order, since `pubkey_num` indexes into a fixed table.

Two additional device-side mechanisms are worth naming because they cover things a rebuild
cannot:

- **The world checksum.** At boot the bootloader hashes roughly 1.59 MB spanning the firmware,
  the bootloader region, the OTP area, both option-byte banks, the system ROM and the device
  serial, and proves the result against a value held in the secure element. Only that proof turns
  the "genuine" light green, and only the main PIN can update the stored value. This detects
  modification of the running device, which a source-to-binary comparison says nothing about.
- **Downgrade protection.** Version timestamps are written into one-time-programmable memory, and
  `check_is_downgrade()` refuses any image older than the recorded high-water mark. Without it, a
  correctly signed and perfectly reproducible *old* release with a known bug would remain
  installable forever.

------

## Where the chain still bottoms out

Reproducible builds are a strong link, not a complete one. Being explicit about the remainder is
part of using them honestly.

**The bootloader is not in scope.** `make repro` verifies the application firmware. The bootloader
is factory-set, cannot be replaced in the field, and is not rebuilt by the repro flow. What is
available instead is an in-place measurement: callgate method 1 makes the device hash its own
bootloader region with a caller-supplied 32-bit nonce, so recorded answers cannot be replayed, and
the result can be compared against a hash computed from the source tree.

**Trust in the published hash list.** The `releases/signatures.txt` file is a PGP-clearsigned list
of SHA-256 hashes covering the change logs and the DFU files, produced by a `sign-release` target
that pipes `shasum` output into `gpg --clearsign`. It protects the download against tampering in
transit or on the mirror, but the signing key is the vendor's, so it is an authenticity control
rather than an independent one.

**The build container.** Pinning `alpine:3.16.0` fixes the toolchain relative to that image, which
still has to be fetched from a registry. Verifiers who care can pin by digest rather than by tag.

**Hardware.** No amount of software reproducibility says anything about the silicon, the secure
elements, or whether the unit in your hand is the one that left the factory. That is the domain
of the tamper-evident packaging, the serialised bag number, and the genuine light, none of which
a rebuild can substitute for.

------

## Conclusion

Reproducibility converts a claim into a check. Before it, "this binary was built from the
published source" is something a user either believes or does not; after it, the claim is
falsifiable by anyone with the repository, a container runtime, and the published artefact.

Making it work is mostly bookkeeping rather than cryptography: pin the toolchain, refuse to build
from a dirty tree or drifting submodules, remove clock reads or key them to the version, and
exclude only the bytes that provably cannot match. The comparison step then needs no trust at
all, because a byte-for-byte diff has no discretion in it.

What remains outside the mechanism should be stated rather than implied. The bootloader is
measured in place instead of rebuilt, the hash list is signed by the same party that ships the
binaries, and hardware authenticity is a separate problem with separate controls.

![Firmware supply chain mindmap]({{site.url_complet}}/assets/article/blockchain/wallet/coldcard/2026-07-31-firmware-reproducible-builds-mindmap.png)

------

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Reproducible build** | A build process that yields bit-for-bit identical output from identical source, so an independent party can confirm a published binary corresponds to published source. |
| **`SOURCE_DATE_EPOCH`** | A convention where build tooling reads a fixed timestamp from this environment variable instead of the system clock, removing the build date as a source of variation. |
| **DFU file** | The Device Firmware Upgrade container distributed to users; for this device it holds two elements, the application firmware and the bootrom, which `signit split` separates. |
| **Firmware header** | A 128-byte structure inside the image carrying magic value, BCD timestamp, version, key index, length, hardware-compatibility mask and a 64-byte signature. |
| **Development key (key 0)** | A signing key whose private half is published in the repository, so anyone can produce a binary the bootloader will run, always with a warning shown to the user. |
| **World checksum** | A double-SHA-256 over the firmware and its surrounding flash, OTP, option bytes, system ROM and serial number, stored in the secure element and required to show the device as genuine. |
| **High-water mark** | A version timestamp recorded in one-time-programmable memory; images older than it are refused, preventing rollback to a signed but vulnerable release. |
| **Callgate** | The narrow, method-numbered entry point from application code into the protected bootloader; method 1 returns a nonce-salted hash of the bootloader itself. |
| **`submods-match`** | A build prerequisite that fails if any submodule is checked out at other than its recorded revision, so a rebuild cannot quietly use different dependency source. |
| **Clearsigned hash list** | A plain-text list of file hashes wrapped in a PGP signature, published so downloads can be checked for integrity against the vendor's key. |

------

## Annex — Security Implementation Checklist

For a firmware project intending to be independently verifiable.

### Determinism of the build

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The toolchain is pinned to a specific container image or digest, not to a floating tag. | A compiler update changes the output and every verification fails, training users to ignore mismatches. |
| ☐ | The build refuses to run from a dirty working tree. | A local modification silently enters the "reproducible" binary. |
| ☐ | The build refuses to run with submodules off their recorded revisions. | Dependency source differs from what the verifier reviews. |
| ☐ | Clock reads are eliminated or fixed via `SOURCE_DATE_EPOCH` or a version-keyed constant. | The binary differs by build date and can never be reproduced. |
| ☐ | Absolute paths and hostnames do not reach the output. | The binary depends on where it was built, so only the vendor can reproduce it. |

### Comparison procedure

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Only bytes that provably cannot match (the signature itself) are excluded from the diff. | A generous exclusion mask hides real differences. |
| ☐ | The excluded range is fixed and documented, not derived from the file being checked. | An attacker-controlled length field could widen the ignored region. |
| ☐ | Signatures on both the published and the rebuilt binary are verified, not just their contents. | Content equality without a valid vendor signature proves nothing about origin. |
| ☐ | The published artefact is fetched by exact filename from a signed manifest. | A substituted "published" binary would be compared against itself. |

### Device-side verification

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Header fields are validated before the signature check, including a bounds check on the key index. | An out-of-range key index reads outside the trusted key table. |
| ☐ | The signature covers the whole image, with only the signature bytes excluded. | Unsigned regions become a place to hide code or data. |
| ☐ | Rollback is blocked by monotonic version state in write-once memory. | A signed old release with a known flaw stays installable indefinitely. |
| ☐ | An integrity indicator is controlled by a secure element, not by the application processor. | Modified firmware can report itself as genuine. |
| ☐ | Any code excluded from the reproducible build can be measured in place with a fresh nonce. | Stored responses can be replayed by modified firmware. |

------

## Frequently Asked Questions

**Q: If the binary contains its own signature, how can two builds ever be compared?**

The signature bytes are excluded from the comparison and checked separately. The verifier does
not hold the production key, so the local build is signed with the published development key,
and those 64 bytes necessarily differ. The comparison covers everything else, using a fixed
offset range rather than one derived from the file. The published image's signature is then
verified in its own right, which is what links the vendor's key to the content that was just
shown to match.

**Q: Why pin the compiler? The source is the same either way.**

Different compiler versions make different optimisation choices, lay out code differently, and
emit different debug metadata, all from identical source. Without pinning, a mismatch tells you
nothing, because you cannot distinguish a malicious build from a toolchain difference. Pinning
turns any mismatch into a signal worth investigating.

**Q: What does `SOURCE_DATE_EPOCH` actually do here?**

It replaces the clock as an input. Build tooling that would embed "now" reads the variable
instead, and the repro script derives its value from the timestamp in the published release
filename. The rebuild therefore inherits the original build's notion of the current time from the
artefact it is checking, rather than from the machine it runs on.

**Q: A reproducible build proves the binary matches the source. Does it prove my device runs that binary?**

No, and these are worth keeping separate:

- **Reproducibility** ties a published binary to published source. It happens on your
  workstation, before anything is installed.
- **The signature check** ties the image on the device to a trusted key, at install and boot time.
- **The world checksum** ties the current contents of flash to a value the owner approved,
  held in the secure element and unreachable without the PIN.

You need all three. A reproducible binary installed on a device whose flash was subsequently
modified is not a secure device, and the checksum is the mechanism that notices.

**Q: The bootloader is not covered by the rebuild. Is that a hole?**

It is a documented limit with a partial mitigation. The bootloader is factory-set and cannot be
replaced in the field, so there is no upgrade path to verify, but that also means you cannot
rebuild and compare it. Instead the device will hash its own bootloader region on demand, salted
with a nonce you supply, so a modified device cannot replay a stored answer. Comparing that hash
against one computed from the source is weaker than a rebuild, since it depends on the code doing
the hashing, but it is not nothing.

**Q: Could a vendor still ship a targeted build to one user?**

Only to users who do not check. That is the practical value of the mechanism: it does not prevent
a malicious build, it makes one detectable by anybody who runs the comparison, and detectable by
one person is enough to make it public. The residual risk concentrates on the parts outside the
scheme, which is why the bootloader measurement, the signed hash list, and hardware authenticity
controls are worth treating as separate questions rather than as details.

------

## References

### Analyzed source

- [Coldcard/firmware](https://github.com/Coldcard/firmware) — analyzed at commit [`3238f6fd9977eed786012d0034a04d888c3263bb`](https://github.com/Coldcard/firmware/tree/3238f6fd9977eed786012d0034a04d888c3263bb) (release [2026-07-31T0519-v5.6.0](https://github.com/Coldcard/firmware/releases/tag/2026-07-31T0519-v5.6.0)), 2026-07-31

### Build and verification sources in that tree

- [`docs/notes-on-repro.md`](https://github.com/Coldcard/firmware/blob/master/docs/notes-on-repro.md) — step-by-step breakdown of the repro flow
- [`stm32/shared.mk`](https://github.com/Coldcard/firmware/blob/master/stm32/shared.mk) — `repro`, `check-repro`, `submods-match`, `code-committed`, `sign-release`
- [`stm32/repro-build.sh`](https://github.com/Coldcard/firmware/blob/master/stm32/repro-build.sh) — the in-container build script
- [`stm32/dockerfile.build`](https://github.com/Coldcard/firmware/blob/master/stm32/dockerfile.build) — pinned toolchain image
- [`stm32/make_filetime.py`](https://github.com/Coldcard/firmware/blob/master/stm32/make_filetime.py) — version-keyed timestamp generation
- [`cli/signit.py`](https://github.com/Coldcard/firmware/blob/master/cli/signit.py) — `sign`, `split`, `check`
- [`stm32/sigheader.h`](https://github.com/Coldcard/firmware/blob/master/stm32/sigheader.h) — firmware header format

### General references

- [Reproducible Builds project](https://reproducible-builds.org/)
- [`SOURCE_DATE_EPOCH` specification](https://reproducible-builds.org/docs/source-date-epoch/)
- [Coinkite: supply chain trust minimisation](https://blog.coinkite.com/supply-chain-trust-minimized/)

### Related articles on this site

- [COLDCARD Firmware - Architecture and Security Model]({{site.url_complet}}/2026/07/31/coldcard-firmware-security/)
- [STM32 Memory Protection in Practice]({{site.url_complet}}/2026/07/31/stm32-memory-protection-firmware-security/)
- [Trezor Crypto Wallet - Cryptography and Security]({{site.url_complet}}/2024/10/15/trezor-wallet-security/)
