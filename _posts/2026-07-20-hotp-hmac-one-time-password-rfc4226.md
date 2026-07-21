---
layout: post
title: "HOTP - An HMAC-Based One-Time Password Algorithm (RFC 4226)"
date:   2026-07-20
lang: en
locale: en-GB
categories: cryptography security rfc
tags: cryptography hotp otp hmac two-factor-authentication rfc4226 oath totp
description: How HOTP (RFC 4226) turns a shared secret and a counter into a 6-digit one-time password using HMAC-SHA-1 and dynamic truncation, with its security analysis, validation rules, and link to TOTP.
image: /assets/article/cryptographie/hotp/2026-07-20-hotp-hmac-one-time-password-rfc4226.png
isMath: true
---

HOTP is the algorithm behind the six-digit codes that hardware tokens and authenticator apps have shown for close to two decades. Published in December 2005 as [RFC 4226](https://datatracker.ietf.org/doc/html/rfc4226) by the OATH (Open AuTHentication) initiative, it turns a shared secret and an increasing counter into a short numeric password that is valid once. This article walks through the construction, the dynamic truncation trick that produces a human-readable code, the security analysis that justifies a 6-digit output, and the validation rules a server must implement. It closes on how HOTP became the foundation for the time-based variant TOTP.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why a One-Time Password

A static password has one structural weakness: it is the same value on every use, so an attacker who captures it once can replay it forever. Two-factor authentication addresses this by asking for *something you know* (a PIN or password) alongside *something you have* (a token). The token contributes a one-time password (OTP): a value that changes on every authentication and is therefore useless to an eavesdropper after a single use.

At the time RFC 4226 was written, two-factor authentication was deployed narrowly. Vendors shipped tokens and validation servers coupled through proprietary technology, which produced high-cost solutions and poor interoperability. The OATH members set out to specify an algorithm that any hardware manufacturer or software developer could implement freely, so that a token from one vendor could be validated by a server from another. The design targets are worth keeping in mind because they shape the algorithm: it had to run on low-cost, battery-limited devices with no numeric keypad, such as Java smart cards, USB dongles, and GSM SIM cards.

HOTP is *event-based*. The moving factor is a counter that increments each time a new password is produced, not a clock. That choice keeps the token cheap (no accurate time source is required) but introduces a synchronization problem between token and server that the specification spends considerable effort solving.

## The HOTP Construction

HOTP is built from two well-understood primitives: HMAC-SHA-1 as defined in [RFC 2104](https://datatracker.ietf.org/doc/html/rfc2104), and a truncation step. The top-level definition is compact:

$$
\begin{aligned}
\text{HOTP}(K, C) = \text{Truncate}\big(\text{HMAC-SHA-1}(K, C)\big)
\end{aligned}
$$

The two inputs are the shared secret and the counter.

- **$$K$$ — the shared secret.** A symmetric key known only to the token and the validation server. Each token holds a distinct key. The specification requires at least 128 bits and recommends 160 bits, matching the SHA-1 output width.
- **$$C$$ — the counter.** An 8-byte value, the moving factor, that must stay synchronized between the token (generator) and the server (validator). Key, counter, and any data are processed high-order byte first, and the generated values are treated as big-endian.

HMAC-SHA-1 returns a 160-bit (20-byte) string. That is far too long to read off a small display and type into a login form, so HOTP truncates it down to a short number. The interesting part of the algorithm is *how* it truncates.

### Dynamic Truncation

A naive truncation would always take, say, the first four bytes of the HMAC. HOTP instead uses **dynamic truncation (DT)**: the starting offset is itself derived from the HMAC output, so which four bytes get selected varies unpredictably from one counter value to the next. The procedure operates on the 20-byte string `HS = HMAC-SHA-1(K, C)`:

1. **Read the offset.** Take the low-order 4 bits of the last byte, `HS[19]`. This yields an integer `offset` in the range 0 to 15.
2. **Extract four bytes.** Read the four bytes `HS[offset]` through `HS[offset+3]` as a 32-bit big-endian value `P`.
3. **Mask the top bit.** Return the low 31 bits of `P` (mask the first byte with `0x7f`). Masking the most significant bit removes any ambiguity between signed and unsigned interpretation across processors.

The result is a 31-bit unsigned integer, the *dynamic binary code*. The final step reduces it to the desired number of digits:

$$
\begin{aligned}
\text{HOTP value} = \text{DBC} \bmod 10^{d}
\end{aligned}
$$

where $$d$$ is the digit count, at least 6. The byte layout below shows where the offset and the selected window come from for a concrete HMAC output.

```
byte #   00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19
value    1f 86 98 69 0e 02 ca 16 61 85 50 ef 7f 19 da 8e 94 5b 55 5a
                                          \__________/              ^^
                                          selected window        offset
                                          (bytes 10..13)         low nibble
                                                                 of byte 19 = 0xa = 10
```

### A Worked Example

RFC 4226 gives a full worked example for a 6-digit code, reproduced here step by step. Suppose the HMAC-SHA-1 output is the 20 bytes shown above.

- The last byte is `0x5a`; its low 4 bits are `0xa`, so the offset is 10.
- The four bytes starting at index 10 are `50 ef 7f 19`, giving the dynamic binary code `0x50ef7f19`.
- The most significant bit is already 0 (`0x50 & 0x7f = 0x50`), so masking leaves `0x50ef7f19`, which is $$1{,}357{,}872{,}921$$ in decimal.
- Reducing modulo $$10^{6}$$ gives the final HOTP value $$872921$$.

The specification also publishes a table of test vectors that every implementation should reproduce. Using the ASCII secret `"12345678901234567890"` and counter values 0 through 9, the 6-digit HOTP values are:

| Counter $$C$$ | HOTP value |
|---------------|------------|
| 0 | 755224 |
| 1 | 287082 |
| 2 | 359152 |
| 3 | 969429 |
| 4 | 338314 |
| 5 | 254676 |
| 6 | 287922 |
| 7 | 162583 |
| 8 | 399871 |
| 9 | 520489 |

These ten values are the canonical HOTP test vectors. Anyone who has configured an authenticator app has effectively relied on the same reference numbers, because TOTP reuses this exact construction.

![HOTP generation pipeline from secret and counter to a six-digit code]({{site.url_complet}}/assets/article/cryptographie/hotp/hotp-generation-pipeline.png)

## Design Requirements

The construction was not chosen arbitrarily. Six requirements (R1 to R6) drove the design, and each explains a specific decision.

- **R1 — sequence-based.** The algorithm must use a counter, so it can be embedded in high-volume devices such as Java smart cards, USB dongles, and SIM cards.
- **R2 — economical.** It should be cheap to implement in hardware, minimizing demands on battery, buttons, computation, and display size.
- **R3 — no numeric input required.** It must work on tokens that have no keypad, though it may also run on richer devices with a secure PIN-pad.
- **R4 — easy to read and type.** The displayed value must be short. HOTP values must be at least 6 digits and preferably numeric only, so they can be entered on a phone.
- **R5 — resynchronization.** There must be a user-friendly way to resynchronize the counter, because token and server counters can drift apart.
- **R6 — strong shared secret.** The key must be at least 128 bits, with 160 bits recommended.

Requirements R4 and R6 pull in opposite directions: R6 wants a wide secret and a wide MAC, while R4 forces a short output. Dynamic truncation is the compromise that keeps the internal computation full-width while exposing only a short code, and the security analysis exists to prove that this compromise is safe.

## Validation and Counter Synchronization

Because HOTP is event-based, the token and the server each keep their own copy of the counter, and these copies can fall out of step. The token increments its counter every time a user requests a new code, whether or not that code is ever submitted. The server increments its counter only after a *successful* authentication. A user who generates several codes without logging in therefore pushes the token ahead of the server.

The specification handles drift with a **look-ahead window** governed by a resynchronization parameter $$s$$. On receiving a candidate value, the server does not test only its current counter $$C_{\text{server}}$$; it recomputes HOTP for the next $$s$$ consecutive counters and accepts a match anywhere in that range.

$$
\begin{aligned}
\text{accept } z \iff z = \text{HOTP}(K, i) \text{ for some } i \in \{C_{\text{server}}, \ldots, C_{\text{server}} + s - 1\}
\end{aligned}
$$

If a match is found at index $$i$$, the server resynchronizes by setting its counter to $$i + 1$$. If no match is found within the window, the value is rejected. The window has an upper bound on purpose: without one, the server would compute HOTP values forever, which both wastes resources and hands an attacker a larger set of acceptable answers. The specification recommends keeping $$s$$ as low as usability allows.

![Server-side validation with the look-ahead window and resynchronization]({{site.url_complet}}/assets/article/cryptographie/hotp/hotp-validation-workflow.png)

An optional strengthening asks the user to submit a short sequence of consecutive values (say two or three) instead of one. Forging a run of consecutive HOTP values is harder than guessing a single one, so this tightens security without lengthening the code.

## Throttling and the Brute-Force Bound

Truncating a 160-bit MAC to six digits necessarily makes guessing easier: there are only a million possible 6-digit codes. The specification is explicit that the server, not the algorithm, must contain this risk, and it does so with two levers.

- **Throttling parameter $$T$$.** A cap on the number of failed attempts before the server locks the account. It should be as low as usability permits, and the delay or lockout must persist across login sessions so an attacker cannot bypass it with parallel guessing.
- **Delay scheme.** As an alternative to a hard lockout, the server can impose a growing delay after each failed attempt $$A$$, for example waiting $$T \cdot 2^{A}$$ seconds, so repeated guessing becomes rapidly impractical.

The relationship between these parameters and the guessing probability is captured by a single approximate formula. The probability that an attacker succeeds is

$$
\begin{aligned}
\text{Sec} = \frac{s \cdot v}{10^{d}}
\end{aligned}
$$

where $$s$$ is the look-ahead window size, $$v$$ is the number of verification attempts the attacker is allowed, and $$d$$ is the digit count. The window $$s$$ appears in the numerator because a larger acceptance window means more values the attacker can hit, which is precisely why $$s$$ cannot be made large without cost. An operator tunes $$v$$ (through $$T$$) and $$d$$ to reach a target security level while preserving usability.

## Security Analysis

Appendix A of the RFC contains a formal analysis that answers one question: is guessing the best an attacker can do, or can observing many legitimate codes help them do better? The conclusion is that, for practical purposes, brute force is optimal. The argument proceeds in three parts.

### From Bits to Digits

The first concern is bias. Dynamic truncation of a random HMAC yields a uniform 31-bit string, but reducing a 31-bit value modulo $$10^{6}$$ is not perfectly uniform, because $$2^{31}$$ is not a multiple of $$10^{6}$$. Writing $$(q, r) = \text{IntDiv}(2^{31}, 10^{6})$$ gives $$q = 2147$$ and $$r = 483648$$. The outputs split into two groups with slightly different probabilities:

| Output range | Probability of appearing |
|--------------|--------------------------|
| $$0, \ldots, 483647$$ | $$2148 / 2^{31} \approx 1.00024 / 10^{6}$$ |
| $$483648, \ldots, 999999$$ | $$2147 / 2^{31} \approx 0.99977 / 10^{6}$$ |

The distribution is slightly non-uniform: some codes are marginally more likely than others. The gap is tiny, roughly two parts in ten thousand, and the analysis shows it is negligible for security.

### Brute Force Is the Best Attack

An attacker who knows the bias could target the more probable codes first, gaining a slight edge. The analysis quantifies this. For an adversary making $$v$$ verification queries against the idealized algorithm, the success probability is bounded by

$$
\begin{aligned}
\text{Adv}(B) \le \frac{s \cdot v \cdot (q + 1)}{2^{31}} = s \cdot v \cdot \frac{1.00024}{10^{6}}
\end{aligned}
$$

The decisive result is Proposition 2: *no* strategy beats this bound. Even an adversary who eavesdrops on many successful authentications and tries to cryptanalyze them to learn how to build valid codes gains no meaningful advantage over blind guessing, as long as the number of observed authentications is not astronomically large. Collecting legitimate codes does not help forge new ones.

### The PRF Assumption and SHA-1

The idealized analysis replaces HMAC-SHA-1 with a truly random function. To transfer the result to the real algorithm, the RFC assumes HMAC-SHA-1 behaves as a secure **pseudorandom function (PRF)**: its input-output behaviour is indistinguishable from random in practice. Under this assumption, Theorem 1 bounds the real adversary's advantage by

$$
\begin{aligned}
\text{Adv}(B) \le \frac{s \cdot v \cdot (q + 1)}{2^{31}} + \frac{t/T}{2^{k}} + \frac{(s v + a)^{2}}{2^{n}}
\end{aligned}
$$

The first term is the brute-force bound. The remaining two terms cover an exhaustive key search and a birthday attack on the MAC; with a 160-bit key and output ($$k = n = 160$$), they fall to roughly $$2^{-78}$$, far below the first term. In practical terms, attacking HOTP is no easier than guessing, and the truncation adds no exploitable weakness.

A note on SHA-1 is warranted, since collision attacks against SHA-1 were announced the same year RFC 4226 appeared. Appendix B addresses this directly: those attacks find collisions in the bare hash, but HMAC does not rely on collision resistance. HMAC's security depends on the difficulty of finding *hidden-key collisions*, where the attacker does not know the internal keys derived from $$K$$. The 2005 SHA-1 collision results do not extend to that setting, so they leave HMAC-SHA-1, and therefore HOTP, unaffected. The security proof requires only that HMAC-SHA-1 be a good PRF, a property the collision attacks did not touch.

## Managing the Shared Secret

The secret $$K$$ is the only thing an attacker lacks, so its handling is critical. The specification describes two provisioning strategies with different trade-offs.

- **Deterministic generation.** Each token's secret is derived from a master key held in a tamper-resistant module, for example $$K_{i} = \text{SHA-1}(\text{MK}, i)$$ where $$i$$ is public device information such as a serial number. The benefit is that secrets never need to be stored, since they can be regenerated on demand. The drawback is severe: exposure of the master key lets an attacker rebuild every token's secret, forcing a full revocation.
- **Random generation.** Each secret is generated independently from a good random source following [RFC 4086](https://datatracker.ietf.org/doc/html/rfc4086), then stored securely. Compromise of one secret does not endanger the others, but every secret must be protected at rest, ideally encrypted under a tamper-resistant module and decrypted only for the moment a value is verified.

Whichever strategy is used, the data store holding the secrets must sit inside a secure perimeter, and access must be restricted to the validation processes alone. The specification stresses that protecting the shared secrets is of the utmost importance, because their leakage compromises the whole system.

Two related ideas extend the basic scheme. A **composite shared secret** folds an extra factor, such as a user PIN, into $$K$$ during provisioning, so the token stores only a seed and reconstructs $$K$$ at computation time. **Bi-directional authentication** lets the token also verify the server: a three-pass exchange in which the server proves it knows the shared secret, all carried over a secure channel such as TLS.

## Extensions and the Road to TOTP

Appendix E lists variations that are not part of the standard but show how the design can be tuned.

- **More digits.** Extracting an 8-digit code (modulo $$10^{8}$$) drops the guessing probability from $$sv/10^{6}$$ to $$sv/10^{8}$$, improving security at a small usability cost.
- **Alphanumeric values.** Using a 32-symbol alphabet instead of ten digits raises the space to $$32^{d}$$; a 6-symbol alphanumeric code already exceeds a 9-digit numeric one.
- **Sequence of values.** Requiring $$L$$ consecutive HOTP values raises the bar for a forger without lengthening any single code.
- **Counter-based resynchronization.** If the client can transmit its counter alongside the code, the server can drop the look-ahead window entirely and verify against the reported counter directly, cutting the success probability to $$v/10^{6}$$.

The last extension in the appendix is the most consequential. The **data field** allows the moving factor to be something other than a plain counter. In particular, the RFC suggests deriving the moving factor from a timer, using UNIX time divided by a fixed step:

$$
\begin{aligned}
\text{moving factor} = \left\lfloor \frac{\text{UNIX time}}{\text{time step}} \right\rfloor
\end{aligned}
$$

This is precisely the idea that [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238) later standardized as TOTP (Time-based One-Time Password). TOTP is HOTP with the counter replaced by a time interval, which is why the codes rotate on a clock and why an authenticator app needs no button press. Every authenticator app in common use today runs the HOTP truncation described here over a time-derived counter.

## Conclusion

RFC 4226 specifies HOTP by composing HMAC-SHA-1 with dynamic truncation to convert a shared secret and a counter into a short numeric code. The dynamic offset keeps the full width of the MAC in play while exposing only six digits, and the accompanying analysis shows that this truncation introduces only negligible bias, leaving brute force as the best available attack. Because guessing is the limiting factor, the security of a deployment rests on the server: a throttling parameter and a bounded look-ahead window are what keep the million-strong code space out of reach. The event-based counter makes the token cheap but creates the drift that the resynchronization rules manage. The same construction, run over a time-derived moving factor, became TOTP, which is how these codes reached everyday use.

![HOTP RFC 4226 mindmap covering construction, validation, security analysis, and extensions]({{site.url_complet}}/assets/article/cryptographie/hotp/2026-07-20-hotp-hmac-one-time-password-rfc4226.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **HOTP** | HMAC-based One-Time Password; the RFC 4226 algorithm that maps a shared secret and a counter to a short numeric code valid once. |
| **OATH** | Open AuTHentication, the industry initiative that authored RFC 4226 to make interoperable strong authentication freely available. |
| **HMAC-SHA-1** | The keyed message authentication code (RFC 2104) used as the base function of HOTP, producing a 160-bit output from key and message. |
| **Dynamic truncation (DT)** | The step that selects a 4-byte window from the HMAC at an offset read from the HMAC itself, then masks the top bit to yield a 31-bit value. |
| **Dynamic binary code (DBC)** | The 31-bit unsigned integer produced by dynamic truncation before reduction modulo a power of ten. |
| **Moving factor** | The changing input to HOTP; a counter in HOTP, or a time interval in the TOTP variant. |
| **Counter ($$C$$)** | The 8-byte event counter that must stay synchronized between the token and the validation server. |
| **Look-ahead window ($$s$$)** | The number of consecutive counter values the server tests when validating a code, allowing it to tolerate token drift. |
| **Throttling ($$T$$)** | The server-side limit on failed attempts that contains the brute-force risk inherent in a short code. |
| **Pseudorandom function (PRF)** | The security assumption on HMAC-SHA-1; that its outputs are practically indistinguishable from those of a random function, on which the HOTP proof rests. |

## Frequently Asked Questions

**Q: What are the two inputs to the HOTP function, and what is its output?**

HOTP takes a shared secret $$K$$ and a counter $$C$$, and returns a short decimal code, at least 6 digits long. The secret is a symmetric key of at least 128 bits (160 recommended) known only to the token and the server; the counter is an 8-byte value that both parties keep and must keep synchronized. Internally the function computes $$\text{HMAC-SHA-1}(K, C)$$ and truncates the 160-bit result down to the displayed code.

**Q: Why does HOTP use dynamic truncation instead of simply taking the first four bytes of the HMAC?**

Dynamic truncation reads the starting offset from the low 4 bits of the last HMAC byte, so the four bytes selected depend on the HMAC output and vary unpredictably between counter values. Fixing the offset would not break security under the PRF assumption, but deriving it dynamically avoids privileging any particular byte position and is the design the specification and its security proof analyze. The final masking of the top bit removes signed-versus-unsigned ambiguity across processors.

**Q: A 6-digit code has only a million possibilities. What stops an attacker from guessing it?**

The algorithm itself does not; the server does. Because the guessing probability is approximately $$sv/10^{d}$$, the server must bound the number of verification attempts $$v$$ with a throttling parameter $$T$$ (or a growing delay) and keep the look-ahead window $$s$$ small. Crucially, the lockout or delay must apply across login sessions, otherwise an attacker could split guesses over many parallel sessions to sidestep the cap. With those controls, the effective space is far larger than a single unthrottled million-guess search.

**Q: Why can the token and server counters fall out of synchronization, and how is that resolved?**

The token increments its counter every time a code is generated, whether or not the user submits it, while the server increments only after a successful login. Generating codes without logging in therefore advances the token past the server. The server resolves this with a look-ahead window: it recomputes HOTP for the next $$s$$ counter values and accepts a match anywhere in that range, then resynchronizes its counter to one past the matched value. The window is bounded so it cannot be abused as a denial-of-service vector or widen the attacker's target set.

**Q: SHA-1 collision attacks were announced in 2005. Does that break HOTP?**

No. Those attacks find collisions in the bare SHA-1 hash, but HOTP relies on HMAC-SHA-1, whose security does not depend on collision resistance. HMAC's security rests on the difficulty of finding hidden-key collisions, where the attacker does not know the internal keys derived from $$K$$, and the 2005 results do not extend to that setting. The HOTP proof requires only that HMAC-SHA-1 be a good pseudorandom function, a property the collision work did not undermine.

**Q: How does HOTP relate to TOTP, the codes an authenticator app displays?**

TOTP (RFC 6238) is HOTP with the counter replaced by a time-derived value: the moving factor becomes UNIX time divided by a fixed step, so the code changes on a clock rather than on a button press. This idea appears already in RFC 4226 Appendix E as the data-field extension. The truncation, the HMAC base function, and the security reasoning are identical; only the source of the moving factor differs, which is why the canonical HOTP test vectors also govern TOTP implementations.

## References

- [RFC 4226 — HOTP: An HMAC-Based One-Time Password Algorithm](https://datatracker.ietf.org/doc/html/rfc4226)
- [RFC 2104 — HMAC: Keyed-Hashing for Message Authentication](https://datatracker.ietf.org/doc/html/rfc2104)
- [RFC 6238 — TOTP: Time-Based One-Time Password Algorithm](https://datatracker.ietf.org/doc/html/rfc6238)
- [RFC 4086 — Randomness Requirements for Security](https://datatracker.ietf.org/doc/html/rfc4086)
- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119)
- [Bellare, Canetti, Krawczyk — Keyed Hash Functions and Message Authentication (CRYPTO '96)](https://cseweb.ucsd.edu/~mihir/papers/kmd5.pdf)
- [Initiative for Open Authentication (OATH)](https://openauthentication.org/)
