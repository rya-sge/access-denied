---
layout: post
title: "OpenSSH Detached Signatures — sshsig, Namespaces and ssh-keygen -Y"
date:   2026-08-27
lang: en
locale: en-GB
categories: network security linux
tags: ssh linux network digital-signature
series: openssh
description: How sshsig signs arbitrary files with an SSH key, why the namespace field prevents cross-protocol replay, and how allowed_signers controls verification.
image: /assets/article/network/openssh-sshsig.png
isMath: false
---

OpenSSH is the implementation of the SSH protocol that ships with almost every Unix system. It provides `ssh` for remote login, `sshd` for the server side, `scp` and `sftp` for file transfer, and `ssh-keygen` for key management. All of that exists to open an authenticated connection to a remote host.

SSHSIG is the part that does not. It is a signature format that lets an ordinary SSH key sign arbitrary data, such as a file, a git commit or a release tarball, with no connection and no remote party involved. Its purpose is to reuse a key that a developer already holds, and already knows how to protect, for the signing work that would otherwise mean setting up PGP. `ssh-keygen -Y sign` produces a signature, `ssh-keygen -Y verify` checks one, and an `allowed_signers` file records which keys are trusted for which identity.

`sshsig.c` implements that format. It emits an armoured blob delimited by `-----BEGIN SSH SIGNATURE-----`, which is the mechanism behind `git config gpg.format ssh`. The OpenSSH project uses it on its own commits, which is why a `.git_allowed_signers` file sits at the root of the source tree.

The format is worth reading for one design decision in particular. A signature carries a mandatory namespace string that is covered by the signature itself, so a signature produced for one purpose cannot be presented as a signature for another. This article covers the blob layout, what is actually signed, how verification enforces the namespace and the hash algorithm, and how `allowed_signers` decides which keys are acceptable. The revision analysed declares `OpenSSH_10.5p1` in `version.h`.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What the operations are

Everything is reached through `ssh-keygen -Y`, and the subcommands are dispatched in `ssh-keygen.c`:

- `sign` produces a signature over a file, given a key and a namespace.
- `verify` checks a signature against an `allowed_signers` file, a claimed signer identity and a namespace.
- `check-novalidate` checks that a signature is well formed and internally consistent, without deciding whether the signing key is trusted.
- `find-principals` looks up which identities in an `allowed_signers` file correspond to the key that made a signature.
- `match-principals` resolves an identity against the patterns in an `allowed_signers` file.

The separation between `verify` and `check-novalidate` is the useful one. The first answers whether an authorised party signed this, the second answers only whether the signature is mathematically valid, which are different questions and are frequently confused in signature tooling.

![Component diagram of the sshsig format showing the armoured blob fields, the separately constructed signed pre-image, and the allowed_signers file consulted at verification]({{site.url_complet}}/assets/article/network/openssh-sshsig-concept.png)

## The blob and the signed pre-image are different objects

`PROTOCOL.sshsig` specifies the file that is written out:

```
#define MAGIC_PREAMBLE "SSHSIG"
#define SIG_VERSION    0x01

        byte[6]   MAGIC_PREAMBLE
        uint32    SIG_VERSION
        string    publickey
        string    namespace
        string    reserved
        string    hash_algorithm
        string    signature
```

What gets signed is a different structure, assembled in `sshsig_wrap_sign`:

```c
if ((r = sshbuf_put(tosign, MAGIC_PREAMBLE, MAGIC_PREAMBLE_LEN)) != 0 ||
    (r = sshbuf_put_cstring(tosign, sig_namespace)) != 0 ||
    (r = sshbuf_put_string(tosign, NULL, 0)) != 0 || /* reserved */
    (r = sshbuf_put_cstring(tosign, hashalg)) != 0 ||
    (r = sshbuf_put_stringb(tosign, h_message)) != 0) {
```

Comparing the two is instructive. The version and the public key appear in the file but not in the signed data, because they are needed to interpret the signature rather than protected by it. The namespace and the hash algorithm appear in both, so neither can be reinterpreted after the fact. And the final field is `h_message`, a hash of the content, not the content itself.

That last point makes the scheme two-level. The file is hashed once by `hash_file`, and the signature covers a short structure containing that hash, which is what keeps signing a large file inexpensive and allows a signature to be checked without re-reading the original in memory.

The hash algorithm is not free-form. It is chosen from an allowlist:

```c
#define HASHALG_DEFAULT		"sha512"
#define HASHALG_ALLOWED		"sha256,sha512"
```

and `sshsig_check_hashalg` is called on both the signing and the verifying path, so a signature naming an algorithm outside the list is rejected rather than attempted.

## The namespace is the point

`PROTOCOL.sshsig` states the purpose without hedging:

> The purpose of the namespace value is to specify a unambiguous interpretation domain for the signature, e.g. file signing. This prevents cross-protocol attacks caused by signatures intended for one intended domain being accepted in another. The namespace value MUST NOT be the empty string.

Verification enforces it as an equality check, and treats a mismatch as an invalid signature rather than as a separate class of error:

```c
if (strcmp(expect_namespace, got_namespace) != 0) {
	error("Couldn't verify signature: namespace does not match");
	debug_f("expected namespace \"%s\" received \"%s\"",
	    expect_namespace, got_namespace);
	r = SSH_ERR_SIGNATURE_INVALID;
	goto done;
}
```

The hash algorithm is checked immediately afterwards in the same manner, closing the corresponding substitution.

![Activity diagram of the sshsig sign and verify paths showing the message hashed first, the namespace bound into the signed pre-image, and verification rejecting a namespace mismatch]({{site.url_complet}}/assets/article/network/openssh-sshsig-workflow.png)

This is domain separation implemented as a required API parameter rather than as advice. Because the caller cannot sign without naming a namespace, and cannot verify without stating the namespace it expects, an application that adopts sshsig is isolated from every other user of the same key by construction. Git signs with the namespace `git`, so a Git commit signature is not a valid file signature and the reverse is equally false.

The general form of the problem is worth stating plainly, because it is not specific to SSH. A key used for two purposes without domain separation lets a signature gathered under one purpose be replayed under the other, and whether that matters depends entirely on what the two purposes authorise. Placing the purpose inside the signed data and checking it on the way out removes the question.

## Deciding whose signature counts

A valid signature says only that some key signed something. `allowed_signers` is what turns that into an authorisation decision, and `ssh-keygen.1` describes it as "a simple list of identities and keys to determine whether a signature comes from an authorized source", using "a format patterned after the AUTHORIZED_KEYS FILE FORMAT".

Each line carries principals, options, a key type and a key. The principals field is a pattern list of `USER@DOMAIN` identities, and the manual is specific about the matching rule: the identity presented with `-I` "must match a principals pattern in order for the corresponding key to be considered acceptable for verification".

Two consequences follow. Verification is always relative to a claimed identity, so a caller must know who it expects rather than accepting whoever signed. And the file supports a `cert-authority` option, which allows an entry to designate a CA whose certificates are accepted instead of enumerating every individual key, giving the same delegation model that certificates provide for authentication.

## Conclusion

The format is small and its properties come from where fields are placed rather than from any cryptographic novelty. Putting the namespace and the hash algorithm inside the signed structure, while leaving the version and the public key outside it, is what determines which parts of a signature an attacker can restate. Hashing the message first is what keeps the scheme practical on large files.

Two things transfer to work unrelated to SSH. A signature format should carry its own interpretation domain, checked on verification, rather than relying on callers to keep contexts apart. And validating a signature is a different operation from deciding that the signer was authorised, which is why `check-novalidate` and `verify` are separate subcommands rather than one with a flag.

![Mindmap of OpenSSH detached signatures covering the ssh-keygen -Y operations, the blob and pre-image layouts, namespace domain separation and allowed_signers]({{site.url_complet}}/assets/article/network/openssh-sshsig.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Detached signature** | A signature stored separately from the data it covers, which is the only form sshsig currently supports. |
| **Armoured format** | The base64 encoding delimited by `-----BEGIN SSH SIGNATURE-----` and its matching footer, which a signature file must begin and end with. |
| **Signed pre-image** | The structure actually passed to the signing operation, containing the preamble, namespace, reserved field, hash algorithm and message hash. |
| **Namespace** | The mandatory interpretation domain carried in the signature and compared for equality at verification, which may not be empty. |
| **Cross-protocol attack** | Presenting a signature made for one interpretation domain as though it were made for another, which the namespace exists to prevent. |
| **`allowed_signers`** | The file mapping identity patterns to keys, which decides whose signatures are acceptable. |
| **Signer identity** | The `USER@DOMAIN` value supplied with `-I` at verification, matched against the principals patterns in `allowed_signers`. |
| **`cert-authority`** | The `allowed_signers` option marking an entry as a CA, so certificates it issued are accepted rather than individual keys. |
| **`check-novalidate`** | The operation that verifies a signature is well formed without deciding whether the signing key is trusted. |
| **Hash algorithm allowlist** | The `sha256,sha512` set from which a signature's hash algorithm must be drawn, enforced on signing and verification alike. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A signature verifies only under the namespace it was created for. | The namespace inside the signed pre-image and the equality check in `sshsig_wrap_verify`. | A signature collected in one application is replayed against another sharing the key. |
| The namespace is never empty. | The requirement stated in `PROTOCOL.sshsig`. | Signatures carry no interpretation domain, and domain separation is lost. |
| The hash algorithm named by a signature is one of a fixed pair. | `sshsig_check_hashalg` against `HASHALG_ALLOWED`, on both paths. | A signature names a weak or unexpected digest and is honoured. |
| A signature with an unsupported version is refused. | The version check against `SIG_VERSION`, required by the specification. | A future format is misparsed as the current one. |
| A valid signature alone does not establish authorisation. | The separation of `verify` from `check-novalidate`, and the `allowed_signers` lookup. | Any key becomes acceptable, since a self-generated key produces valid signatures. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Signing and verifying both require a namespace, and the two must match exactly. | Choose one stable namespace string per application, document it, and record it alongside the allowed-signers file. |
| `check-novalidate` performs no trust decision. | Use `verify` wherever the question is whether an authorised party signed, and reserve `check-novalidate` for format checks. |
| Verification is relative to an identity supplied with `-I`. | Determine the expected signer before verifying, rather than accepting whichever key produced the signature. |
| The public key travels inside the signature blob. | Do not treat the embedded key as evidence of anything until it has been matched against `allowed_signers`. |
| An `allowed_signers` entry can delegate to a CA with `cert-authority`. | Use the CA form for a fleet, so signer turnover does not require editing the file on every verifier. |

## Frequently Asked Questions

**Q: What is the difference between the signature blob and the data that is signed?**

The blob is the file that gets written, and it contains the magic preamble, the version, the public key, the namespace, a reserved field, the hash algorithm and the signature. The signed pre-image is a different structure containing the preamble, the namespace, the reserved field, the hash algorithm and the hash of the message.

The version and public key appear only in the blob, since they are needed to interpret a signature rather than protected by it. The namespace and hash algorithm appear in both, which is what makes them unforgeable rather than merely declared.

**Q: Why is the message hashed before signing rather than signed directly?**

To keep the cost of signing independent of file size and to keep the signed structure small. `hash_file` reduces the content to a digest, and the signature then covers a short structure containing that digest along with the namespace and algorithm identifier. A verifier can therefore re-hash the file once and check a small signature, without holding the content in memory as a single buffer.

**Q: What exactly does the namespace prevent?**

It prevents a signature produced for one purpose being accepted for another. Because the namespace is inside the signed pre-image, an attacker who obtains a signature made with the namespace `git` cannot present it where a verifier expects `file`, since the verifier compares the two strings and returns `SSH_ERR_SIGNATURE_INVALID` on a mismatch. `PROTOCOL.sshsig` names this class of problem directly as a cross-protocol attack, and requires the namespace to be non-empty.

**Q: A signature verifies with `check-novalidate`. What has been established?**

Only that the signature is well formed and consistent with the public key embedded in it. Nothing has been established about whether that key belongs to anyone in particular, so an attacker who generates their own key and signs with it produces a signature that passes this check.

Deciding that the signer was authorised requires `verify`, which consults `allowed_signers` and matches the identity given with `-I` against the principals patterns in that file.

**Q: How do the namespace and `allowed_signers` divide responsibility, and why are both needed?**

They answer different questions, and either alone leaves a gap.

The namespace answers what a signature was made for. It is carried inside the signed data and checked by equality, so it constrains how a signature may be interpreted, but it says nothing about who produced it.

`allowed_signers` answers who is acceptable. It maps identity patterns to keys, optionally delegating to a CA, and it is consulted only at verification time, so it says nothing about what the signature was intended to authorise.

A system with namespaces but no signer list accepts signatures from anyone in the right context. A system with a signer list but no namespaces accepts an authorised party's signature in a context they never agreed to. Both mechanisms are required for a verification to mean that an authorised party signed this, for this purpose.

## References

### Specifications

- [RFC 4253 — The Secure Shell (SSH) Transport Layer Protocol](https://datatracker.ietf.org/doc/html/rfc4253), whose public key encoding the blob reuses
- [draft-miller-ssh-cert](https://datatracker.ietf.org/doc/draft-miller-ssh-cert/) — the certificate format, relevant to the `cert-authority` option in `allowed_signers`

### OpenSSH documents

- [PROTOCOL.sshsig](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.sshsig) — the armoured and blob formats, and the namespace requirement quoted here
- [PROTOCOL.u2f](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.u2f) — the hardware-backed key types that can also produce these signatures

### Manual pages

- [ssh-keygen(1)](https://man.openbsd.org/ssh-keygen.1), including its ALLOWED SIGNERS section

### Analyzed source

- [openssh/openssh-portable](https://github.com/openssh/openssh-portable) — analyzed at commit [`0ef0f5a839831c213f24e3f2ae434765c607fb50`](https://github.com/openssh/openssh-portable/tree/0ef0f5a839831c213f24e3f2ae434765c607fb50), 2026-08-27. The commit carries no release tag and sits after `V_9_7_P1`; `version.h` at this revision declares `OpenSSH_10.5p1`.
