---
layout: post
title: "ML-DSA in Rust — Inside the Quantus qp-rusty-crystals Implementation"
date:   2026-08-25
lang: en
locale: en-GB
categories: cryptography blockchain
tags: cryptography post-quantum lattice ml-dsa dilithium fips-204 rust
description: How the Quantus qp-rusty-crystals crate implements FIPS 204 ML-DSA in no_std Rust, from const-generic parameter sets to streaming matrix expansion.
image: /assets/article/cryptographie/lattice/2026-08-25-ml-dsa-rust-implementation-quantus.png
isMath: true
---

[FIPS 204](https://doi.org/10.6028/NIST.FIPS.204) describes ML-DSA as a sequence of algorithms over polynomial rings. It says nothing about how to lay those algorithms out in a systems language, how to keep a 56 KB matrix off the stack of a hardware wallet, or how to stop a Rust compiler from leaving a copy of the signing seed in a dead stack frame. Those questions belong to the implementer, and the answers show up as architecture.

This article reads one such implementation: `qp-rusty-crystals-dilithium`, the pure-Rust ML-DSA crate used by [Quantus Network](https://www.quantus.com), a Substrate-based Layer 1 that replaces elliptic-curve signatures with lattice-based ones throughout. The crate is `#![no_std]`, contains no `unsafe`, and supports all three FIPS 204 parameter sets from a single code path. The source was read at the revision pinned in the references, which is the snapshot published for the project's Immunefi audit competition.

The focus here is deliberately narrow. Rather than restating what ML-DSA is (a previous article, [ML-DSA — The Module-Lattice Digital Signature Standard (FIPS 204)]({{site.url_complet}}/2026/06/29/ml-dsa-fips-204-post-quantum-signatures/), covers the construction, the hard problems, and the rejection-sampling paradigm), this one looks at the engineering decisions that turn that specification into a crate: const-generic monomorphization, a sealed polynomial type with a documented bounds contract, a sponge that carries its rate in the type system, streamed matrix expansion, and a secret-handling discipline built around borrowing rather than moving.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Scope and Crate Layout

The crate implements the three FIPS 204 algorithms (`ML-DSA.KeyGen`, `ML-DSA.Sign`, `ML-DSA.Verify`) in their pure form, with the domain-separation prefix that binds an optional context string. It does not implement HashML-DSA, the pre-hash variant. Roughly 8,200 lines of Rust sit across sixteen source files, organised into four layers.

| Layer | Files | Responsibility |
|-------|-------|----------------|
| Public API | `frontend.rs`, `ml_dsa_44.rs`, `ml_dsa_65.rs`, `ml_dsa_87.rs`, `errors.rs`, `lib.rs` | `Keypair` / `SecretKey` / `PublicKey`, length and context guards, secret wrappers |
| Scheme core | `sign.rs`, `packing.rs` | The three algorithms and the three wire encodings, const-generic over the parameter set |
| Arithmetic | `poly.rs`, `polyvec.rs`, `ntt.rs`, `rounding.rs`, `reduce.rs`, `fips202.rs` | Ring arithmetic, rounding, hashing, sampling |
| Parameters | `params.rs` | FIPS 204 Table 1 and Table 2, plus `const fn` size arithmetic |

`poly.rs` is by far the largest file at 2,287 lines, and `sign.rs` follows at 1,282. That distribution is characteristic: the algorithms themselves are short, and most of the code is in the polynomial layer where the bit-level codecs, the samplers, and the bounds contracts live.

`lib.rs` keeps the arithmetic modules public (`poly`, `polyvec`, `packing`, `params`, `rounding`, `fips202`) while sealing `sign`, `frontend`, `ntt`, and `reduce` behind `pub(crate)`. That split is what lets the sibling threshold-signing crate build on the same ring arithmetic without reaching into the signature algorithms.

## One Code Path, Three Parameter Sets

ML-DSA-44, ML-DSA-65, and ML-DSA-87 are not three implementations in this crate. They are three monomorphizations of one.

Everything from `sign.rs` downwards is generic over const parameters. The signing core takes fourteen of them:

```rust
pub(crate) fn signature_var<
	const K: usize,
	const L: usize,
	const ETA: usize,
	const TAU: usize,
	const GAMMA1: usize,
	const GAMMA2: usize,
	const OMEGA: usize,
	const CD: usize,
	const PZ: usize,
	const W1: usize,
	const KW1: usize,
	const PK: usize,
	const SK: usize,
	const SIG: usize,
>(
	signature_output: &mut [u8; SIG],
	domain_prefix: &[u8],
	message: &[u8],
	secret_key_bytes: &[u8; SK],
	hedge: Option<&SensitiveBytes32>,
)
```

The first seven are the FIPS 204 parameters. The remaining seven are derived sizes that Rust cannot compute from the others in a const-generic position on stable, so they are passed in and then verified. Each variant module is a single line:

```rust
crate::frontend::define_ml_dsa!(crate::params::ml_dsa_87);
```

`define_ml_dsa!` expands to the whole public surface for that parameter set: the `Keypair`, `SecretKey`, and `PublicKey` types, the import and export paths, the size constants, and the `sign` / `verify` methods that pin the fourteen const parameters. Writing the API once and stamping it three times means an invariant added to one variant is added to all three by construction.

### Parameter consistency as a compile error

Passing derived sizes as separate const parameters creates an obvious hazard: nothing stops a caller from instantiating the ML-DSA-87 core with ML-DSA-65's signature length. The crate closes that with a `const` block evaluated at monomorphization:

```rust
const fn assert_sign_params<
	const K: usize, const L: usize, const ETA: usize,
	const GAMMA1: usize, const GAMMA2: usize, const OMEGA: usize,
	const CD: usize, const PZ: usize, const W1: usize, const KW1: usize,
	const PK: usize, const SK: usize, const SIG: usize,
>() {
	assert!(PZ == params::polyz_packedbytes(GAMMA1));
	assert!(W1 == params::polyw1_packedbytes(GAMMA2));
	assert!(KW1 == K * W1);
	assert!(PK == params::publickeybytes(K));
	assert!(SK == params::secretkeybytes(K, L, ETA));
	assert!(SIG == params::signbytes(K, L, GAMMA1, OMEGA, CD));
}
```

The helpers it calls are `const fn` in `params.rs`, and they are total only over the values FIPS 204 defines:

```rust
pub const fn polyz_packedbytes(gamma1: usize) -> usize {
	match gamma1 {
		0x20000 => 18 * N as usize / 8, // 18 bits per coefficient (ML-DSA-44)
		0x80000 => 20 * N as usize / 8, // 20 bits per coefficient (ML-DSA-65/87)
		_ => panic!("unsupported GAMMA1 parameter"),
	}
}
```

A `panic!` inside a `const fn` evaluated at compile time is a compile error, so an unsupported `GAMMA1` never produces a binary. The same pattern rejects an `ETA` outside `{2, 4}` and a `GAMMA2` outside the two permitted values. An inconsistent instantiation fails to build rather than silently mis-parsing bytes at runtime.

The Cargo features are additive rather than exclusive, so one binary can carry several levels at once. That matters for a chain that must verify signatures it did not produce.

## The Arithmetic Core

The ring is the standard one:

$$
\begin{aligned}
R_q = \mathbb Z_q[X]/(X^{256}+1), \qquad q = 2^{23} - 2^{13} + 1 = 8380417
\end{aligned}
$$

Three modular primitives live in `reduce.rs`, and each carries an explicitly documented input domain. `montgomery_reduce` is the interesting one, because its domain is half-open:

```rust
/// For integer a with -2^{31} * Q <= a < 2^31 * Q,
/// compute r \equiv 2^{-32} * a (mod Q) such that -Q < r < Q.
pub fn montgomery_reduce(a: i64) -> i32 {
	let mut t = (a as i32).wrapping_mul(Q_INV) as i64;
	t = (a - t.wrapping_mul(crate::params::Q as i64)) >> 32;
	t as i32
}
```

At exactly $2^{31} q$ the signed low word truncates to `i32::MIN` and the reduction returns $q$ itself, which the stated output range `(-q, q)` excludes. The crate documents that endpoint, pins it with a unit test, and keeps the negative endpoint inclusive because it reduces cleanly to zero. This is the level of precision the whole arithmetic layer is written at.

`caddq` carries a note worth quoting, because it records a genuine difference between the Rust and C versions of the same trick:

```rust
pub fn caddq(a: i32) -> i32 {
	// In C right-shift of negative signed integers is implementation-defined, so C reference
	// implementation contains bug. In Rust if a < 0 right-shift is defined to fill with 1s, 0s
	// otherwise, so we're bug free here.
	a + ((a >> 31) & crate::params::Q)
}
```

### A sealed polynomial with a bounds contract

The routines in `poly.rs` do not re-validate their inputs, for performance and for constant-time behaviour. Instead the module publishes a contract: each function documents the coefficient bounds it requires and the bounds its output satisfies. To stop external code from violating that contract, `Poly` hides its coefficient array behind three entry points.

```rust
#[derive(Clone, Zeroize, ZeroizeOnDrop)]
pub struct Poly {
	pub(crate) coeffs: [i32; N],
}
```

`Poly::from_coeffs` is the validated door for untrusted data. It accepts $(-q, q)$, which is inside the domain of every public routine in the module, so a polynomial built there can be handed to any of them. The unpack functions produce bounded coefficients by construction. `coeffs_mut` is the deliberate escape hatch for advanced integrations, and it moves the obligation to the caller in its own documentation.

Routines whose domain is narrower than $(-q, q)$ are not public at all. `shiftl` requires $|c| < 2^{31-d}$, so it is `pub(crate)`, and the module docs pin that with a `compile_fail` doctest showing that boundary-validated data cannot reach it. Every precondition is additionally checked with `debug_assert!`, which costs nothing in release and fails loudly in tests:

```rust
pub fn invntt_tomont(a: &mut Poly) {
	debug_assert!(
		a.coeffs.iter().all(|&c| c.unsigned_abs() < params::Q as u32),
		"poly::invntt_tomont precondition violated: |coefficient| >= Q"
	);
	ntt::invntt_tomont(&mut a.coeffs);
}
```

## Rounding, Hints, and Exhaustive Verification

`rounding.rs` holds `Power2Round`, `Decompose`, `MakeHint`, and `UseHint`. Two implementation choices stand out.

The first is that `Decompose` extracts high bits with fixed-point reciprocals rather than division, and the constants differ per parameter set: `(1025, >> 22)` for $\gamma_2 = (q-1)/32$, and `(11275, >> 24)` for $\gamma_2 = (q-1)/88$. Because 44 is not a power of two, the wrap of the top high-bits value cannot be a mask, so it is written as branchless arithmetic:

```rust
	} else {
		a1 = (a1 * 11275 + (1 << 23)) >> 24;
		// Branchless wrap of the top high-bits value: a1 == 44 maps to 0.
		// (43 - a1) is negative only for a1 == 44, so the arithmetic-shift
		// mask is all-ones exactly then, and 44 ^ 44 == 0.
		a1 ^= ((43 - a1) >> 31) & a1;
	}
```

Constants like these are correct by verification rather than by inspection, and the crate treats them that way. The test module contains a reference implementation transcribed directly from the FIPS 204 definition, and checks both `Decompose` and `UseHint` against it for **every** input in $[0, q)$, for both $\gamma_2$ values. That is about 8.4 million values per arm, plus a reconstruction invariant on each. It runs as an ordinary `cargo test`.

The second choice is that `Power2Round` and `Decompose` canonicalise their input before applying the FIPS formula:

```rust
	// Canonicalize to the standard representative in [0, Q); branchless, so
	// constant-time, and identity for inputs already in [0, Q).
	let a = crate::reduce::caddq(a);
```

The FIPS definitions are written over $a \bmod^{+} q$, so a signed representative and its standard representative must decompose identically. Without the canonicalisation a negative-but-valid input produces non-canonical bits, and the crate pins the property with tests asserting `power2round(a) == power2round(a + Q)` across a set of negative inputs.

`MakeHint` is branchless for a specific reason stated in its documentation: it runs on secret-derived data, and on rejected signing attempts whose hints are never published, so a data-dependent branch there could leak.

```rust
pub fn make_hint<const GAMMA2: usize>(a0: i32, a1: i32) -> i32 {
	let gamma2 = GAMMA2 as i32;
	// -1 iff a0 > GAMMA2
	let gt = (gamma2 - a0) >> 31;
	// -1 iff a0 < -GAMMA2; t == 0 iff a0 == -GAMMA2
	let t = a0 + gamma2;
	let lt = t >> 31;
	// -1 iff t == 0 (i.e. a0 == -GAMMA2)
	let eq = !((t | t.wrapping_neg()) >> 31);
	// -1 iff a1 != 0
	let a1_nonzero = (a1 | a1.wrapping_neg()) >> 31;
	(gt | lt | (eq & a1_nonzero)) & 1
}
```

`UseHint` is not branchless, and the documentation says why: it runs only during verification, on public data.

## Hashing and Sampling

ML-DSA uses SHAKE128 for `ExpandA` and SHAKE256 for everything else. Those two differ only in their sponge rate (168 and 136 bytes), and mixing them corrupts a state in a way that is easy to write and hard to see. The crate makes it a type error by parameterising the state on its rate:

```rust
#[derive(Default, Zeroize, ZeroizeOnDrop)]
pub struct KeccakState<const R: usize> {
	s: [u64; 25],
	pos: usize,
	squeezing: bool,
}

pub type Shake128State = KeccakState<SHAKE128_RATE>;
pub type Shake256State = KeccakState<SHAKE256_RATE>;
```

A state built by SHAKE128 operations cannot reach a SHAKE256 function, and the module documents that with a `compile_fail` doctest. The absorb-to-squeeze transition is tracked at runtime in `squeezing` and checked with `debug_assert!`, so absorbing into a finalised state panics in tests and stays deterministic in release.

The fields are private, and that is load-bearing rather than stylistic. The squeeze loop relies on `pos <= R` to make progress; a state restored from untrusted bytes with `pos > R` would emit zero bytes per iteration and spin forever. A defensive `>=` guard remains as a backstop:

```rust
		// `>=` (rather than `==`) is a defensive guard: a well-formed state always
		// has `pos <= R`, but if an out-of-range `pos` ever reaches here we must
		// still permute and reset so the loop makes progress.
		if pos >= R {
			keccakf1600_statepermute(&mut state.s);
			pos = 0;
		}
```

`KeccakState` implements neither `Copy` nor `Clone`. A copy of a state that has absorbed the signing seed $K$ would be a second live instance of that secret, invisible to the original's zeroization, so duplication is replaced by `init()`.

### Sampling and the shape of the rejection loops

Four samplers sit on top of the sponge. `poly::uniform` is one element of `ExpandA`, `uniform_eta` is `ExpandS`, `uniform_gamma1` is `ExpandMask`, and `challenge` is `SampleInBall`.

`ExpandS` is the one that departs most visibly from the reference structure. Rather than squeezing blocks until 256 coefficients have been accepted, it squeezes a fixed number of blocks and takes the first 256 of whatever the pass produced:

```rust
	// - ETA = 2: two blocks = 544 nibbles, each accepted with probability 15/16 (mean 510, sigma
	//   ~5.7) — falling short of 256 is a ~45-sigma event (< 2^-600).
	// - ETA = 4: the acceptance probability drops to 9/16, so two blocks (mean 306, sigma ~11.6)
	//   would fall short of 256 at a ~4.3-sigma rate (~1e-5) — an observable timing variation.
	//   Three blocks = 816 nibbles (mean 459, sigma ~14.2) push the shortfall back out to ~14 sigma
	//   (< 2^-150).
	let fixed_rounds: usize = if ETA == 2 { 2 } else { 3 };
```

The round count is chosen per `ETA` so the retry branch is effectively never taken, which keeps the observed timing of secret sampling constant. A fallback loop still exists, because exact sampling requires it.

The inner rejection sampler is branchless. Its index clamp is worth reading closely, because the comment names the attack class it is avoiding:

```rust
			let has_space = ctr < alen;
			let inc_ctr = nibble_valid & has_space;
			let store_mask = -(inc_ctr as i32);
			// Clamp the index instead of `ctr % alen`: division/modulo latency can be
			// operand-dependent on some CPUs (KyberSlash class), and ctr is secret-derived.
			// `min` compiles to a conditional move, and when ctr == alen the store mask is
			// zero so the clamped slot is rewritten with its own value.
			let idx = ctr.min(alen - 1);
			a[idx] = (coeff & store_mask) | (a[idx] & !store_mask);
			ctr += inc_ctr as usize;
```

`SampleInBall` is the deliberate exception. It is plain variable-time rejection sampling, and the documentation justifies that: its timing depends only on the bytes of $\tilde c = H(\mu, w_1)$, which is a hash output that is published in an accepted signature and never leaves the device for a rejected one.

## Streaming the Matrix Instead of Materialising It

For ML-DSA-87 the matrix $\mathbf A$ is 8 by 7 polynomials, which is 56 KB once expanded. A reference implementation expands it once and multiplies. On a hardware wallet that number is a problem, and the crate treats peak stack as a first-class constraint.

`matrix_pointwise_montgomery_streamed` regenerates each element from $\rho$ on demand and never stores the matrix:

```rust
pub fn matrix_pointwise_montgomery_streamed<const K: usize, const L: usize>(
	t: &mut Polyvec<K>,
	rho: &[u8; params::SEEDBYTES],
	v: &Polyvec<L>,
) {
	let mut a_ij = Poly::default();
	let mut prod = Poly::default();
	for (i, t_i) in t.vec.iter_mut().enumerate() {
		poly::uniform(&mut a_ij, rho, (i << 8) as u16);
		poly::pointwise_montgomery(t_i, &a_ij, &v.vec[0]);
		for j in 1..L {
			poly::uniform(&mut a_ij, rho, ((i << 8) + j) as u16);
			poly::pointwise_montgomery(&mut prod, &a_ij, &v.vec[j]);
			poly::add_ip(t_i, &prod);
		}
	}
}
```

![Two package diagrams contrasting a materialised K by L matrix of 56 KB against the streamed loop that regenerates one polynomial at a time and keeps a two-polynomial working set]({{site.url_complet}}/assets/article/cryptographie/lattice/qp-rusty-crystals-streaming-matrix.png)

Peak extra working memory is two polynomials, roughly 2 KB. The accumulation order is unchanged, so the result is identical bit for bit to the materialised version, and only stack usage differs. The trade is recomputation: signing regenerates the whole matrix on every rejection-sampling attempt, and ML-DSA-87 averages 3.85 attempts.

The commitment to that decision shows up outside the crate. A `stack-check.sh` script builds for `thumbv7em-none-eabihf` with per-function stack-size emission and reports the frame of every ML-DSA entry point, specifically so that a change re-introducing a materialised matrix is caught before it reaches hardware.

## The Signing Loop as Implemented

`signature_var` decomposes into named helpers rather than one long function: `unpack_secret_key_for_signing`, `prepare_signing_context`, `derive_message_hash`, `derive_mask_seed`, `generate_masking_vector_and_commitment`, `generate_challenge_polynomial`, and four `compute_and_check_*` predicates.

The message hash absorbs its inputs as separate slices rather than concatenating them:

```rust
fn derive_message_hash(
	public_key_hash_tr: &[u8; params::TR_BYTES],
	domain_prefix: &[u8],
	message: &[u8],
) -> [u8; params::CRHBYTES] {
	let mut keccak_state = fips202::KeccakState::default();
	fips202::shake256_absorb(&mut keccak_state, public_key_hash_tr);
	fips202::shake256_absorb(&mut keccak_state, domain_prefix);
	fips202::shake256_absorb(&mut keccak_state, message);
	fips202::shake256_finalize(&mut keccak_state);
	let mut message_hash_mu = [0u8; params::CRHBYTES];
	fips202::shake256_squeeze(&mut message_hash_mu, &mut keccak_state);
	message_hash_mu
}
```

SHAKE absorption is incremental, so this is bit-identical to hashing the concatenation while avoiding a heap copy of a message that may be tens of megabytes and is attacker-controlled.

### Four predicates, no short-circuit

FIPS 204 lists four rejection conditions. Written naturally in Rust they would short-circuit, and the attempt would then take a different amount of time depending on which bound failed. The crate evaluates all four unconditionally and combines them with non-short-circuiting `&`:

```rust
		// All four rejection checks are always evaluated (no short-circuit between them),
		// so a rejected attempt reveals only that it was rejected, not which bound failed.
		let condition1 = compute_and_check_signature_z::<L, GAMMA1, TAU, ETA>(...);
		let condition2 = compute_and_check_commitment_w0::<K, GAMMA2, TAU, ETA>(...);
		let condition3 = compute_and_check_challenge_t0::<K, GAMMA2>(...);
		let condition4 = compute_and_check_hint_vector::<K, GAMMA2, OMEGA>(...);

		if condition1 & condition2 & condition3 & condition4 {
			packing::pack_sig::<K, L, GAMMA1, OMEGA, CD, PZ, SIG>(...);
			return;
		}
```

The *number* of attempts is still variable, and the crate is explicit that this is intentional: FIPS 204 treats the attempt count as public, and every mainstream implementation uses an early-exit loop. What must not vary is the arithmetic within an attempt.

The norm check itself is computed in `i64`, which is not merely defensive:

```rust
/// (The classic 32-bit shift trick `c - (mask & 2*c)` overflows `2*c` for
/// |c| > i32::MAX/2 and mis-handles i32::MIN; out-of-range coefficients would
/// then *pass* the norm check instead of failing it.)
```

A norm check that fails open on out-of-range input is worse than no check, so the absolute value is taken in a wider type with a sign-mask fold, and every coefficient is always visited.

### Nonce discipline

Mask reuse in ML-DSA is the analogue of ECDSA nonce reuse: two signatures under the same $\mathbf y$ let an attacker subtract the responses and recover $\mathbf s_1$. `ExpandMask` derives its stream nonce as $L \cdot \kappa + i$, and only the low two bytes are absorbed, so a large enough $\kappa$ would alias two distinct attempts onto one stream. The signer bounds it:

```rust
	// Largest attempt_nonce for which the per-polynomial mask nonce (L*attempt_nonce + i,
	// i < L) still fits in u16. Reaching this requires an astronomically improbable run of
	// rejection-sampling failures, which would signal a broken RNG/entropy source.
	let max_safe_attempt_nonce: u16 = (u16::MAX - (L as u16 - 1)) / (L as u16);
```

The helper it protects is `pub(crate)`, and its documentation states the requirement, so an external caller cannot reach it with an unchecked nonce.

## Verification

`verify_var` follows the reference structure and adds one check. Before parsing the signature it rejects a public key whose $\mathbf t_1$ is entirely zero:

```rust
	// Reject the degenerate all-zero t1 public key. With t1 = 0 the term c*2^d*t1 in the
	// verification relation vanishes for every challenge c, so w1 = UseHint(h, Az) no longer
	// binds the challenge to the key. An attacker can then forge a signature (z = 0, empty
	// hint, c = H(mu || w1Encode(0))) with no secret key.
	if t1.vec.iter().all(|p| p.coeffs.iter().all(|&c| c == 0)) {
		return false;
	}
```

Honest key generation never produces that key, so the check costs nothing on the legitimate path. `PublicKey::from_bytes` applies it at import as well, and `public_key_from_secret_var` refuses to import a secret key that derives it.

Beyond that, the verifier recomputes $\mu$ from its own $\mathsf{SHAKE256}(pk)$ rather than trusting anything supplied with the signature, checks $\lVert \mathbf z \rVert_\infty < \gamma_1 - \beta$ before doing any lattice arithmetic, and requires the hint section to be canonically encoded. That last check is what `unpack_sig` returns, and the flag is marked `#[must_use]` with a `compile_fail` doctest proving that a caller cannot discard it:

```rust
#[must_use = "the return value is the only signal that the hint encoding is canonical; \
              on false the outputs are invalid and must be rejected"]
pub fn unpack_sig<...>(...) -> bool
```

Both `sign` and `verify` cap the message at 64 MiB and the context string at the 255 bytes FIPS 204 allows. The cap is a denial-of-service bound rather than a cryptographic one, and it does mean the crate will not verify a conformant signature over a larger message.

## Handling Secret Material

A move in Rust is a copy, and the source of that copy is dead but never dropped, so `ZeroizeOnDrop` cannot reach it. The crate builds its whole secret-handling discipline around that fact, and the resulting style is unusual enough to be worth showing.

Sensitive byte strings live in wrappers that consume their input:

```rust
#[derive(ZeroizeOnDrop)]
pub struct SensitiveBytes32([u8; 32]);
```

`new` takes `&mut [u8; 32]` and zeroizes the caller's buffer, so the secret exists in one place. There is deliberately no `into_bytes`, because handing the array back as a plain `Copy` value would re-create every hazard the wrapper exists to prevent. `Clone` is not derived. Equality goes through an explicit constant-time method rather than `PartialEq`, since a short-circuiting comparison on secret bytes leaks the length of the matching prefix:

```rust
#[must_use]
pub fn ct_eq_32(a: &[u8; 32], b: &[u8; 32]) -> bool {
	let mut diff = 0u8;
	for (x, y) in a.iter().zip(b.iter()) {
		diff |= x ^ y;
	}
	core::hint::black_box(diff) == 0
}
```

Inside the signing path the same reasoning produces an out-parameter style. The unpacked secret key is never returned by value; the caller places a zeroed struct and the callee fills it through `&mut`:

```rust
	/// All-zero placeholder to be filled in place by
	/// [`unpack_secret_key_for_signing`]. Constructed by the caller so the
	/// secret-bearing value never has to be returned by value: a by-value
	/// return moves the struct out of the callee's frame, and the dead source
	/// copy — containing the signing key `K` and the NTT-form secret
	/// polynomials — is beyond the reach of `ZeroizeOnDrop`.
	fn zeroed() -> Self {
```

The same shape appears in `Keypair::generate`, which builds the struct in tail position rather than binding it to a named local first, and in `Keypair::from_bytes`, which validates a borrowed buffer instead of passing a `SecretKey` by value.

None of this is verifiable by reading the source, because it is a claim about codegen. The crate therefore tests it from the outside. Three integration test files paint a stack region with a sentinel byte, run the operation on it through `psm::on_stack`, and scan the region afterwards for 32-byte windows of known secret material. They are compiled only for optimised builds, since unoptimised codegen materialises move temporaries that no source-level fix can wipe. A fourth test attacks the same problem from the heap side, installing a global allocator that scans every freed block for the key-generation seed.

## Validated Key Import

Where the reference implementation parses a secret key, this crate validates one. `SecretKey::from_bytes`, `Keypair::from_bytes`, and `Keypair::from_parts` all re-derive the public key from the secret material and check the packed key's internal invariants.

![Activity diagram of secret-key import showing the coefficient-range pre-check, public key re-derivation, and the stored t0, tr and non-zero t1 comparisons, each rejecting on mismatch]({{site.url_complet}}/assets/article/cryptographie/lattice/qp-rusty-crystals-key-import-validation.png)

Four properties are enforced:

- Every packed $\mathbf s_1$ and $\mathbf s_2$ slot must decode inside $[-\eta, \eta]$, since non-canonical slots decode to coefficients outside the distribution the $\beta = \tau\eta$ rejection margin is sized for.
- The stored $\mathbf t_0$ must equal the re-derived low bits of $\mathbf A \mathbf s_1 + \mathbf s_2$.
- The stored $tr$ must equal $\mathsf{SHAKE256}(pk)$.
- The derived $\mathbf t_1$ must not be zero.

Re-deriving a public key is a key-generation-scale computation, which makes the import path an obvious amplification target. The coefficient-range flag doubles as a cheap pre-check, because a random blob of the right length almost always has at least one out-of-range slot:

```rust
	if !s_in_range {
		key.zeroize();
		s1.zeroize();
		s2.zeroize();
		t0.zeroize();
		return None;
	}
```

A blob crafted with canonical coefficients but an inconsistent $\mathbf t_0$ still costs one full derivation to reject, which is inherent to correspondence checking. The documentation states that cost and tells callers exposing the import to untrusted input to rate-limit or authenticate first.

One field cannot be validated, and the crate is explicit about it. The nonce seed $K$ is independent entropy with no stored commitment, so a tampered $K$ imports cleanly and produces signatures that verify. The documented consequence is that known-$K$ deterministic signatures leak the secret vector, and the documented mitigations are integrity-protected key storage or hedged signing.

The correspondence invariant is then held by the type system. `Keypair`'s fields are private, so a mismatched pair cannot be assembled, and two `compile_fail` doctests pin it:

```rust
/// ```compile_fail
/// use qp_rusty_crystals_dilithium::ml_dsa_87::{Keypair, PublicKey, SecretKey};
///
/// fn forge(secret: SecretKey, public: PublicKey) -> Keypair {
///     Keypair { secret, public } // ERROR: fields are private
/// }
/// ```
```

## How the Implementation Is Validated

The test strategy is layered to match the code.

- **NIST ACVP known-answer tests.** `src/acvp.rs` runs keyGen, sigGen (deterministic and hedged), and sigVer for all three parameter sets against vectors vendored unmodified from `usnistgov/ACVP-Server`, restricted to the `signatureInterface == "internal"` groups that correspond to `Sign_internal` and `Verify_internal`. This is the self-service half of the [NIST CAVP](https://csrc.nist.gov/projects/cryptographic-algorithm-validation-program) pipeline.
- **SHAKE256 known-answer tests** over the NIST short-message and long-message response files.
- **Exhaustive verification** of `Decompose` and `UseHint` against transcribed FIPS 204 definitions over all of $[0, q)$, for both $\gamma_2$ values.
- **Adversarial import tests**, stamped per parameter set because the defenses are parameter-dependent, covering spliced keypairs, corrupted $tr$ and $\mathbf t_0$ regions, and out-of-range packed coefficients.
- **Painted-stack zeroization probes** for key generation, signing, import, and the secret wrappers, release-only, plus a heap probe that scans freed allocations for the key-generation seed.
- **A dudect timing harness** (`examples/ct_bench.rs`) over the secret-consuming samplers, gated behind an off-by-default `ct-internals` feature so the internals it times are not exposed in a normal build.
- **`compile_fail` doctests** pinning the API invariants: private key fields, no `Clone` on sponge state, the `#[must_use]` hint flag, and `shiftl` being unreachable from boundary-validated data.

Tests in that last category are easy to leave out, and they hold invariants that would otherwise decay the first time someone adds a convenience constructor.

## Conclusion

The specification defines a signature scheme; the implementation defines what happens when the scheme meets a 32-bit microcontroller, an optimising compiler, and a caller who supplies the bytes. Reading `qp-rusty-crystals-dilithium` alongside FIPS 204 makes the boundary between those two visible.

Three decisions carry most of the structure. Const-generic monomorphization behind a single macro means the three parameter sets share one audited code path, with size consistency enforced as a compile error. Streaming the matrix trades recomputation for a two-polynomial working set, and an external stack-measurement script keeps that trade honest. And the secret-handling style, which borrows rather than moves and fills through out-parameters, is a direct response to the fact that Rust's ownership model does not by itself erase what it copies.

The parts that are documented as deliberate exceptions are as informative as the hardened ones: a variable-time `SampleInBall` on public data, a rejection-attempt count treated as public per FIPS 204, and a nonce seed that no import check can validate.

![Mindmap of the qp-rusty-crystals ML-DSA implementation covering genericity, arithmetic core, rounding, hashing, memory strategy, secret handling, key import and validation]({{site.url_complet}}/assets/article/cryptographie/lattice/2026-08-25-ml-dsa-rust-implementation-quantus.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Monomorphization** | The compiler step that turns one const-generic function into a separate concrete function per parameter set, folding constant conditions away so unused branches do not exist in the binary. |
| **`const` block assertion** | An `assert!` inside a `const { ... }` block, evaluated at compile time; a failure is a build error, used here to cross-check derived buffer sizes against base parameters. |
| **Montgomery reduction** | Modular reduction that replaces division by a multiplication and a shift, computing a representative of $2^{-32}a \bmod q$; the crate's version has a documented half-open input domain. |
| **NTT** | Number-theoretic transform, the finite-field analogue of the FFT, which turns polynomial multiplication in $R_q$ into coefficient-wise multiplication. |
| **Power2Round** | The split of a public vector $\mathbf t$ into high bits $\mathbf t_1$ (published) and low bits $\mathbf t_0$ (kept secret and needed to compute the hint). |
| **Hint** | The sparse per-coefficient correction, bounded in total weight by $\omega$, that lets a verifier recover the signer's high bits despite $\mathbf t_1$ being a truncation of $\mathbf t$. |
| **Sponge rate** | The number of state bytes a Keccak instance absorbs or squeezes per permutation: 168 for SHAKE128, 136 for SHAKE256. The crate encodes it as a const generic on the state type. |
| **Rejection sampling** | Discarding candidate values that fall outside a target range so the accepted output is unbiased; in ML-DSA it also removes the secret-dependent bias from the response $\mathbf z$. |
| **Hedged signing** | Deriving the mask seed as $\rho' = H(K \Vert rnd \Vert \mu)$ with fresh random $rnd$ rather than $rnd = 0^{32}$, so the mask stays unpredictable even if $K$ is compromised. |
| **Painted-stack probe** | A test that fills a stack region with a sentinel byte, runs an operation on it, then scans the region for secret patterns, verifying that zeroization survived optimised codegen. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A `Poly` reaching any public routine has coefficients in $(-q, q)$. | `Poly::from_coeffs` validation, bounded unpack functions, and `pub(crate)` on narrower-domain routines such as `shiftl`. | A caller writes through `coeffs_mut` without upholding the documented bounds. |
| Derived buffer sizes agree with the base parameters of the same variant. | `assert_sign_params` in a `const` block, evaluated at monomorphization. | A generic core is instantiated with hand-written sizes that bypass the `params.rs` helpers. |
| A `Keypair`'s public half corresponds to its secret half. | Private fields plus public-key re-derivation in `generate`, `from_bytes`, and `from_parts`. | A constructor is added that assembles the halves without the correspondence check. |
| An imported secret key has canonical coefficients and consistent $\mathbf t_0$ and $tr$. | `public_key_from_secret_var`, called by every import path. | An import path is added that parses the blob without re-deriving the public key. |
| A verified public key has non-zero $\mathbf t_1$. | The degenerate-key check in both `verify_var` and `PublicKey::from_bytes`. | The check is moved to import only, since `PublicKey.bytes` is publicly constructible. |
| Two signing attempts never share a mask $\mathbf y$. | Distinct $\mu$ or $rnd$ per signature, plus the `max_safe_attempt_nonce` bound on the per-attempt counter. | `polyvec::uniform_gamma1` is reached with a nonce that overflows the two absorbed bytes. |
| Secret intermediates do not outlive their frame. | `ZeroizeOnDrop` on `Poly`, `Polyvec`, `KeccakState` and the key structs, plus borrow-and-fill instead of return-by-value. | A helper is refactored to return a secret-bearing struct by value. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `sign` and `verify` reject messages larger than 64 MiB. | Chunk or pre-hash above that size, and do not assume conformant signatures over larger messages will verify. |
| `Keypair::generate` zeroizes the caller's `SensitiveBytes32` in place. | Build a fresh wrapper per call; a reused wrapper is all zeros on the second call. |
| The nonce seed $K$ is not validated at import and cannot be. | Integrity-protect stored key blobs, or pass fresh `hedge` randomness so a tampered $K$ does not yield a predictable mask. |
| `hedge: None` selects deterministic signing, which is not the FIPS 204 default. | Pass `Some(fresh randomness)` unless byte-reproducible signatures are a requirement. |
| Importing a secret key costs a full key generation. | Rate-limit or authenticate before calling the import paths on untrusted input. |
| `unpack_sig` writes its outputs even when it returns `false`. | Treat the returned flag as the only validity signal; the `#[must_use]` attribute enforces this at compile time. |
| `PublicKey.bytes` is a public field, so `from_bytes` validation is bypassable by direct construction. | Build public keys through `from_bytes` rather than the struct literal. |
| The crate is `#![no_std]` and allocates nothing. | Budget stack, not heap; use the repository's `stack-check.sh` when targeting constrained hardware. |

## Frequently Asked Questions

**Q: Why does the signing core take fourteen const parameters when FIPS 204 defines only seven per parameter set?**

The first seven are the FIPS 204 parameters themselves. The other seven are sizes derived from them, such as the packed length of one $\mathbf z$ polynomial and the total signature length. Stable Rust cannot compute one const-generic array length from another inside a generic function signature, so the derived sizes must be supplied by the caller.

That creates a mismatch hazard, which the crate answers with `assert_sign_params` in a `const` block: every derived size is recomputed from the base parameters by the `const fn` helpers in `params.rs` and compared. A wrong combination is a compile error, not a runtime mis-parse.

**Q: What does streaming the matrix cost, and what does it buy?**

It buys peak memory. A materialised $\mathbf A$ is $k \times \ell$ polynomials, which is about 56 KB for ML-DSA-87; the streamed version keeps two polynomials live, roughly 2 KB.

It costs recomputation. Each rejection-sampling attempt regenerates the whole matrix from $\rho$ through SHAKE128, and ML-DSA-87 averages 3.85 attempts per signature. The accumulation order is unchanged, so the output is identical bit for bit and only the stack profile differs.

**Q: The crate says the number of rejection attempts is public but the arithmetic inside an attempt is not. Why is that distinction safe?**

FIPS 204's security analysis treats the attempt count as public information, and it is independent of the long-term key: whether an attempt passes depends on the freshly sampled mask, not on $\mathbf s_1$. Every mainstream implementation therefore uses an early-exit loop and leaks the count.

What would leak the key is *which* bound failed, because the four conditions test different secret-derived quantities. That is why the crate evaluates all four predicates unconditionally and combines them with a non-short-circuiting `&`, so a rejected attempt is indistinguishable from any other rejected attempt.

**Q: Why is `SampleInBall` allowed to be variable-time when the other samplers are branchless?**

Its only input is the challenge seed $\tilde c = H(\mu, w_1)$, and no secret-key material flows into it. For an accepted attempt $\tilde c$ is published in the signature, so its timing reveals nothing new. For a rejected attempt it never leaves the device, and it cannot be inverted to recover $w_1$. The other samplers consume $\rho'$ or produce $\mathbf s_1$ and $\mathbf s_2$ directly, so their timing is secret-dependent and they are written branchless.

**Q: What can secret-key import validate, what can it not, and why does the gap matter?**

It validates four things: that every packed $\mathbf s_1$ and $\mathbf s_2$ coefficient decodes inside $[-\eta, \eta]$, that the stored $\mathbf t_0$ matches the low bits re-derived from $\mathbf A \mathbf s_1 + \mathbf s_2$, that the stored $tr$ equals $\mathsf{SHAKE256}(pk)$, and that the derived $\mathbf t_1$ is non-zero.

It cannot validate the nonce seed $K$. $K$ is independent entropy squeezed from the key-generation seed, the seed is not stored, and under FIPS 204 every 32-byte value is a valid $K$, so no stored field commits to it.

The gap matters because $K$ is exactly the input that makes deterministic signing deterministic. An attacker who can rewrite a stored key blob can substitute a known $K$; every import check still passes and signatures still verify, but the mask seed $\rho' = H(K \Vert 0^{32} \Vert \mu)$ becomes computable, and a known mask recovers $\mathbf s_1$ from the published $\mathbf z$. Hedged signing keeps $\rho'$ unpredictable regardless.

**Q: Why does the crate treat returning a value as a secret-handling problem?**

Because a move in Rust is a copy. Returning a secret-bearing struct by value copies it into the caller's frame and leaves the source copy in the callee's frame, dead but never dropped, so `ZeroizeOnDrop` never runs on it. Whether the compiler elides that copy is an optimisation decision, not a guarantee.

The crate's response is to place secrets in the caller's frame and fill them through `&mut`, as `UnpackedSecretKey::zeroed` plus `unpack_secret_key_for_signing` do, and to build values in tail position rather than binding them to a named local first. Since none of that is checkable by reading the source, four release-only integration tests paint a stack region, run the operation on it, and scan for secret patterns afterwards.

## References

### Standards

- [NIST FIPS 204 — Module-Lattice-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.204)
- [NIST FIPS 202 — SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions](https://doi.org/10.6028/NIST.FIPS.202)
- [CRYSTALS-Dilithium specification](https://pq-crystals.org/dilithium/)
- [NIST Post-Quantum Cryptography project](https://csrc.nist.gov/projects/post-quantum-cryptography)

### Validation and test material

- [NIST Cryptographic Algorithm Validation Program (CAVP)](https://csrc.nist.gov/projects/cryptographic-algorithm-validation-program)
- [usnistgov/ACVP-Server — ML-DSA test vectors](https://github.com/usnistgov/ACVP-Server)
- [dudect-bencher](https://github.com/rozbb/dudect-bencher) — the timing-leak harness used by the crate's constant-time example
- [KyberSlash](https://kyberslash.cr.yp.to/) — the division-timing attack class the branchless index clamp cites

### Related reading on this site

- [ML-DSA — The Module-Lattice Digital Signature Standard (FIPS 204)]({{site.url_complet}}/2026/06/29/ml-dsa-fips-204-post-quantum-signatures/)
- [ML-KEM — The Module-Lattice Key Encapsulation Standard (FIPS 203)]({{site.url_complet}}/2026/06/29/ml-kem-fips-203-post-quantum-key-encapsulation/)
- [SLH-DSA — Stateless Hash-Based Signatures (FIPS 205)]({{site.url_complet}}/2026/06/29/slh-dsa-fips-205-hash-based-signatures/)

### Project

- [Quantus Network](https://www.quantus.com)
- [Quantus-Network/qp-rusty-crystals](https://github.com/Quantus-Network/qp-rusty-crystals) — the upstream project repository

### Analyzed source

- [immunefi-team/audit-comp-quantus-qp-rusty-crystals](https://github.com/immunefi-team/audit-comp-quantus-qp-rusty-crystals) — the audit-competition snapshot of `Quantus-Network/qp-rusty-crystals`, analyzed at commit [`94dfe6e671b29689c66148991630406e983e2457`](https://github.com/immunefi-team/audit-comp-quantus-qp-rusty-crystals/tree/94dfe6e671b29689c66148991630406e983e2457) (crate `qp-rusty-crystals-dilithium` v4.1.0, no tag on this commit), 2026-08-25
