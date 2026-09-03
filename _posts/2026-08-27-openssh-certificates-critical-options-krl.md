---
layout: post
title: "OpenSSH Certificates — Critical Options, Extensions and the KRL Encoding"
date:   2026-08-27
lang: en
locale: en-GB
categories: network security linux
tags: ssh linux network digital-signature
series: openssh
description: How an OpenSSH certificate is validated, why unknown critical options are fatal while unknown extensions are ignored, and how KRL revocation lists compress.
image: /assets/article/network/openssh-certificates.png
isMath: false
---

An OpenSSH certificate gives a fleet the properties that make X.509 useful, which are delegated trust, an expiry date and a revocation mechanism, without any of its encoding machinery. There is no ASN.1, no chain to build, and no path validation. A certificate is a signed structure naming a key, a set of principals and a validity window, and it is verified against a single configured authority.

This article reads that structure in `sshkey.h`, the validation in `sshkey.c`, the option enforcement in `auth-options.c`, and the revocation list format in `krl.c`. The design decision it spends most time on is the split between critical options and extensions, because that split decides whether a restriction an issuer attached is enforced or silently discarded. The revision analysed declares `OpenSSH_10.5p1` in `version.h`.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The whole structure

The parsed form of a certificate is short enough to read in one piece:

```c
struct sshkey_cert {
	struct sshbuf	*certblob; /* Kept around for use on wire */
	u_int		 type; /* SSH2_CERT_TYPE_USER or SSH2_CERT_TYPE_HOST */
	uint64_t	 serial;
	char		*key_id;
	u_int		 nprincipals;
	char		**principals;
	uint64_t	 valid_after, valid_before;
	struct sshbuf	*critical;
	struct sshbuf	*extensions;
	struct sshkey	*signature_key;
	char		*signature_type;
};
```

A certificate is either a user certificate or a host certificate, and the distinction is carried in the structure rather than inferred from how it is used. `serial` is an issuer-assigned number used for revocation. `key_id` is a free-form label that appears in the server's logs. `principals` is the list of usernames, or hostnames for a host certificate, that the certificate is valid for, capped at `SSHKEY_CERT_MAX_PRINCIPALS`, which is 256. `signature_key` is the CA that signed it.

![Component diagram of an OpenSSH certificate showing the signed fields, the two option bags, the CA key, and the server-side configuration that establishes trust]({{site.url_complet}}/assets/article/network/openssh-certificates-concept.png)

The format used to be described by a file in the source tree called `PROTOCOL.certkeys`. It is no longer there: it was deleted in May 2025, and `PROTOCOL` now points instead at an IETF Internet-Draft, [draft-miller-ssh-cert](https://datatracker.ietf.org/doc/draft-miller-ssh-cert/). The commit message gives the reason, which is that the draft supersedes "the much more basic format description we had previously". Anyone following an older reference to `PROTOCOL.certkeys` should expect to find nothing at that path in a current checkout.

## Validation is a short list of refusals

`sshkey_cert_check_authority` in `sshkey.c` is the function a server calls to decide whether a certificate is acceptable, and it reads as a sequence of rejections, each with the message the operator will see:

```c
if (want_host) {
	if (k->cert->type != SSH2_CERT_TYPE_HOST) {
		*reason = "Certificate invalid: not a host certificate";
		return SSH_ERR_KEY_CERT_INVALID;
	}
} else {
	if (k->cert->type != SSH2_CERT_TYPE_USER) {
		*reason = "Certificate invalid: not a user certificate";
		return SSH_ERR_KEY_CERT_INVALID;
	}
}
if (verify_time < k->cert->valid_after) {
	*reason = "Certificate invalid: not yet valid";
	return SSH_ERR_KEY_CERT_INVALID;
}
if (verify_time >= k->cert->valid_before) {
	*reason = "Certificate invalid: expired";
	return SSH_ERR_KEY_CERT_INVALID;
}
if (k->cert->nprincipals == 0) {
	*reason = "Certificate lacks principal list";
	return SSH_ERR_KEY_CERT_INVALID;
}
```

Three properties of this function are worth naming. A user certificate can never be accepted where a host certificate is expected, so a CA that signs both cannot have one repurposed as the other. The validity window is half-open, since `valid_after` is compared with `<` and `valid_before` with `>=`. And a certificate with an empty principal list is rejected outright rather than treated as matching everything, which is the safe reading of an ambiguous document.

Principal matching then follows, with the wildcard behaviour selected by the caller rather than by the certificate:

```c
for (i = 0; i < k->cert->nprincipals; i++) {
	if (wildcard_pattern) {
		if (match_pattern(name, k->cert->principals[i])) {
			principal_matches = 1;
			break;
		}
	} else if (strcmp(name, k->cert->principals[i]) == 0) {
```

## Critical options and extensions

The two option bags are the part of the design that carries the most weight. Both are parsed by the same function in `auth-options.c`, called twice with different arguments:

```c
/* Handle options and critical extensions separately */
if (cert_option_list(ret, k->cert->critical,
    OPTIONS_CRITICAL, 1) == -1) {
	sshauthopt_free(ret);
	return NULL;
}
if (cert_option_list(ret, k->cert->extensions,
    OPTIONS_EXTENSIONS, 0) == -1) {
	sshauthopt_free(ret);
	return NULL;
}
```

That final argument is a flag named `crit`, and it decides what happens when the parser meets a name it does not know:

```c
if (!found) {
	if (crit) {
		error("Certificate critical option \"%s\" "
		    "is not supported", name);
		goto out;
	} else {
		logit("Certificate extension \"%s\" "
		    "is not supported", name);
	}
}
```

An unrecognised critical option aborts the parse, and the certificate is refused. An unrecognised extension is logged and skipped, and the rest of the certificate is honoured.

![Activity diagram of certificate option parsing showing an unknown critical option rejecting the certificate while an unknown extension is logged and skipped]({{site.url_complet}}/assets/article/network/openssh-certificates-options-workflow.png)

The asymmetry follows from what each bag contains. The critical options are restrictions:

- `force-command`, which replaces whatever the user asked to run.
- `source-address`, which limits the addresses the certificate may be used from, and whose value is syntax-checked at parse time with `addr_match_cidr_list`.
- `verify-required`, which demands a user-verification gesture on a hardware key.

The extensions are grants: `permit-pty`, `permit-port-forwarding`, `permit-agent-forwarding`, `permit-X11-forwarding`, `permit-user-rc`, and `no-touch-required`.

A server that does not understand a restriction cannot apply it, and accepting the certificate anyway would hand out access the issuer intended to constrain. A server that does not understand a grant simply fails to grant it, which errs toward less access. So critical options fail closed and extensions fail open, and the same certificate can be deployed across servers of different vintages without becoming more permissive on the older ones.

The practical rule for an issuer follows directly. A restriction that must hold belongs in the critical bag, where an incapable server refuses the certificate rather than ignoring the constraint.

## Revocation lists

Expiry handles the ordinary case, and short-lived certificates are the usual answer to revocation. When a certificate must be withdrawn before it expires, the mechanism is a Key Revocation List, specified in `PROTOCOL.krl` and implemented in `krl.c`. A KRL is a sequence of typed sections:

```c
#define KRL_SECTION_CERTIFICATES	1
#define KRL_SECTION_EXPLICIT_KEY	2
#define KRL_SECTION_FINGERPRINT_SHA1	3
#define KRL_SECTION_SIGNATURE		4
#define KRL_SECTION_FINGERPRINT_SHA256	5
#define KRL_SECTION_EXTENSION		255
```

A KRL can therefore revoke a plain key by its full blob or by its fingerprint, and certificates by serial number or key identifier. It can also be signed, which is what `KRL_SECTION_SIGNATURE` is for, so a list can be distributed over a channel that is not itself trusted.

### Choosing an encoding by cost

Certificates revoked by serial can be recorded three ways:

```c
#define KRL_SECTION_CERT_SERIAL_LIST	0x20
#define KRL_SECTION_CERT_SERIAL_RANGE	0x21
#define KRL_SECTION_CERT_SERIAL_BITMAP	0x22
```

The encoder does not choose by policy. It estimates the size in bits of every candidate for the run of serials it is currently emitting, including the cost of switching away from the section type already in use, and takes the minimum:

```c
/* Estimate base cost in bits of each section type */
cost_list += 64 * contig + (final ? 0 : 8+64);
cost_range += (2 * 64) + (final ? 0 : 8+64);
cost_bitmap += last_gap + contig + (final ? 0 : MINIMUM(next_gap, 8+64));
cost_bitmap_restart += contig + (final ? 0 : MINIMUM(next_gap, 8+64));

/* Convert to byte costs for actual comparison */
cost_list = (cost_list + 7) / 8;
```

The three encodings suit three distributions. Scattered serials cost 64 bits each as a list. A contiguous batch, which is what revoking everything a compromised CA issued in a window looks like, collapses to two endpoints. A dense region becomes a bitmap at one bit per serial, backed by `bitmap.c`.

The switching cost is why the calculation is not a simple per-run comparison. Starting a new section has its own overhead, so a short run is sometimes cheaper to encode badly inside the current section than to encode well in a new one. The result is that a revocation list covering a large fleet stays small enough to distribute to every server that has to consult it, which is what makes serial-based revocation practical rather than theoretical.

## Conclusion

The certificate format is small because it delegates. There is no chain to validate, so the trust decision reduces to whether the signing key is configured as an authority. The validation function is a list of refusals with operator-readable reasons, and the interesting behaviour is concentrated in the option bags rather than in the parsing.

The split between critical options and extensions is the part worth carrying to other systems. Separating a bag that must be understood from a bag that may be ignored lets one artefact be consumed by implementations of different capability without the older ones quietly becoming more permissive. The KRL encoder is a smaller lesson in the same direction, where measuring three candidate encodings against each other keeps a revocation list small enough to actually deploy.

![Mindmap of OpenSSH certificates covering the certificate structure, validation checks, critical options versus extensions, and KRL revocation encodings]({{site.url_complet}}/assets/article/network/openssh-certificates.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Certificate** | A signed structure binding a public key to a principal list and a validity window, verified against a configured authority rather than a chain. |
| **Principal** | A username, for a user certificate, or a hostname, for a host certificate, that the certificate is valid for. |
| **Key ID** | A free-form label carried in the certificate and written to the server's logs, used to identify the holder in an audit trail. |
| **Serial** | An issuer-assigned number identifying a certificate, and the value a revocation list uses to withdraw it. |
| **Critical option** | An option that restricts what the holder may do, and whose presence in an unrecognised form causes the certificate to be rejected. |
| **Extension** | An option that grants a privilege, and which is logged and skipped when unrecognised. |
| **`force-command`** | The critical option that replaces the command the client requested with one chosen by the issuer. |
| **`source-address`** | The critical option restricting the addresses a certificate may be presented from, syntax-checked when parsed. |
| **KRL** | A Key Revocation List, a compact signed artefact enumerating revoked keys and certificates. |
| **Serial bitmap** | The KRL encoding that records a dense region of revoked serials at one bit each. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A certificate carrying an unrecognised critical option is rejected. | The `crit` flag passed to `cert_option_list`. | A server grants access while silently failing to apply a restriction the issuer attached. |
| A user certificate is never accepted where a host certificate is required. | The `type` comparison against `SSH2_CERT_TYPE_HOST` and `SSH2_CERT_TYPE_USER`. | A CA that signs both kinds has one repurposed as the other. |
| A certificate with an empty principal list is refused. | The `nprincipals == 0` check. | An empty list is read as matching every principal. |
| The validity window is half-open, excluding the instant given by `valid_before`. | Comparison with `<` on `valid_after` and `>=` on `valid_before`. | Two certificates issued back to back overlap by one second. |
| `source-address` contents are well-formed before they are relied upon. | The `addr_match_cidr_list` syntax check at parse time. | A malformed address list is evaluated at authentication time with unclear results. |
| A revocation list stays small enough to distribute fleet-wide. | The per-run cost comparison between list, range and bitmap encodings. | Revocation by serial becomes impractical at fleet scale. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Unrecognised extensions are logged and ignored rather than rejected. | Express any restriction that must be enforced as a critical option, never as an extension. |
| A certificate's principal list is matched against a name supplied by the caller, with wildcards enabled by the caller. | Do not assume a principal entry is a literal string; check how the calling path sets the wildcard flag. |
| `key_id` appears in server logs and is not otherwise interpreted. | Put something identifying in it at issuance, since it is the field an audit trail will have. |
| Revocation requires the KRL to reach every server that must honour it. | Treat KRL distribution as part of the deployment, and prefer short validity windows so revocation is a fallback rather than the primary control. |
| A KRL can carry its own signature. | Sign the list when it is distributed over a channel that is not already trusted, and verify it on the servers that consume it. |

## Frequently Asked Questions

**Q: What does an OpenSSH certificate contain, and what does it deliberately leave out?**

It contains a type distinguishing user from host, a serial, a free-form key identifier, a principal list, a validity window, two option bags, and the identity of the signing key. It leaves out everything associated with path validation. There is no chain, no intermediate CA, and no ASN.1, so verification reduces to checking one signature against a key the server has been configured to trust.

**Q: A certificate carries an option the server does not recognise. Is that fatal?**

It depends which bag holds it. An unrecognised name in the `critical` bag causes the parse to abort and the certificate to be refused. An unrecognised name in the `extensions` bag is logged and skipped, and the rest of the certificate is honoured as normal.

**Q: Why are the two bags treated differently?**

Because they mean opposite things. Critical options restrict the holder, so a server that cannot apply one must not accept the certificate, since accepting it would grant access the issuer meant to constrain. Extensions grant privileges, so a server that does not understand one merely withholds a capability, which is the safe direction to fail.

The result is that a single certificate can be deployed across servers of differing versions without becoming more permissive on the older ones.

**Q: Why does the KRL encoder compute costs in bits instead of applying a rule?**

Because no single encoding is best across the distributions a real revocation list contains. Scattered serials are cheapest as an explicit list at 64 bits each, a contiguous batch is cheapest as a pair of endpoints, and a dense region is cheapest as a bitmap at one bit per serial. The encoder estimates each candidate for the current run, adds the cost of switching section type, and picks the minimum, which keeps a fleet-wide list small enough to distribute.

**Q: Given expiry and revocation both exist, how should an issuer combine them?**

Expiry should be the primary control and revocation the exception. A certificate's validity window is enforced by every server independently, using only the certificate itself, whereas a KRL is enforced only by servers that have received the current list. That makes revocation dependent on a distribution step that can fail silently.

Short validity windows reduce the exposure of a compromised key to the remaining lifetime, and reduce how often the KRL has to be updated. The revocation list then handles the cases that cannot wait for expiry, and signing it lets it travel over a channel that is not otherwise trusted.

## References

### Specifications

- [RFC 4251 — The Secure Shell (SSH) Protocol Architecture](https://datatracker.ietf.org/doc/html/rfc4251)
- [RFC 4253 — The Secure Shell (SSH) Transport Layer Protocol](https://datatracker.ietf.org/doc/html/rfc4253)

### OpenSSH documents

- [draft-miller-ssh-cert](https://datatracker.ietf.org/doc/draft-miller-ssh-cert/) — the certificate format, now the normative reference after `PROTOCOL.certkeys` was removed from the tree
- [PROTOCOL](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL) — section 1.3, which points at the certificate Internet-Draft
- [PROTOCOL.krl](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.krl) — the key revocation list format

### Manual pages

- [ssh-keygen(1)](https://man.openbsd.org/ssh-keygen.1)
- [sshd(8)](https://man.openbsd.org/sshd.8)
- [sshd_config(5)](https://man.openbsd.org/sshd_config.5)

### Analyzed source

- [openssh/openssh-portable](https://github.com/openssh/openssh-portable) — analyzed at commit [`0ef0f5a839831c213f24e3f2ae434765c607fb50`](https://github.com/openssh/openssh-portable/tree/0ef0f5a839831c213f24e3f2ae434765c607fb50), 2026-08-27. The commit carries no release tag and sits after `V_9_7_P1`; `version.h` at this revision declares `OpenSSH_10.5p1`.

### Related articles

- [How Fail2Ban Works — Architecture, Privilege Model and Residual Risk]({{site.url_complet}}/2026/09/03/fail2ban-architecture-privilege-model/)
