---
layout: post
title: The Chinese Remainder Theorem and its Cryptographic Applications
date:   2026-06-28
lang: en
locale: en-GB
categories: cryptography
tags: cryptography number-theory chinese-remainder-theorem rsa modular-arithmetic ring-isomorphism
description: How the Chinese Remainder Theorem works, why it defines a ring isomorphism, and how it accelerates RSA signatures and explains square roots modulo a composite.
image: /assets/article/cryptographie/crt/2026-06-28-chinese-remainder-theorem-cryptography.png
isMath: true
---

The Chinese Remainder Theorem (CRT) is usually introduced as a recipe for solving systems of congruences, but in cryptography its value comes from a stronger reading: it establishes a ring isomorphism between arithmetic modulo a composite and arithmetic on its coprime factors. This structural equivalence is what makes RSA signatures roughly four times faster and explains why a number can have four square roots modulo $$pq$$. This article presents the theorem, proves its constructive formula on a worked example, and develops the two applications most relevant to public-key cryptography.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The Classical Problem

The theorem takes its name from a problem recorded in the third-century text *Sunzi Suanjing*, phrased as a counting puzzle about an army:

> How many soldiers does Han Xing's army contain if, arranged in columns of 3 there remain 2 soldiers, arranged in columns of 5 there remain 3 soldiers, and arranged in columns of 7 there remain 2 soldiers?

Formally, the question asks for an integer $$x$$ satisfying the system

$$
\begin{aligned}
x &\equiv 2 \pmod{3} \\
x &\equiv 3 \pmod{5} \\
x &\equiv 2 \pmod{7}
\end{aligned}
$$

The CRT guarantees that such a system always has a solution when the moduli are pairwise coprime, and that the solution is unique modulo the product of the moduli.

## The Theorem

**Theorem (Chinese Remainder Theorem).** Let $$m_1, m_2, \ldots, m_n$$ be pairwise coprime positive integers and let $$a_1, a_2, \ldots, a_n \in \mathbb{Z}$$. The system

$$
\begin{aligned}
x &\equiv a_1 \pmod{m_1} \\
&\ \ \vdots \\
x &\equiv a_n \pmod{m_n}
\end{aligned}
$$

has a unique solution modulo $$m = m_1 m_2 \cdots m_n$$, given by

$$
\begin{aligned}
x \equiv \sum_{i=1}^{n} a_i \left( \left(\frac{m}{m_i}\right)^{-1} \bmod m_i \right) \frac{m}{m_i} \pmod{m}.
\end{aligned}
$$

The construction is easier to read term by term. For each index $$i$$, define $$M_i = m / m_i$$, the product of all moduli except $$m_i$$. Because the moduli are pairwise coprime, $$M_i$$ is invertible modulo $$m_i$$, so $$M_i^{-1} \bmod m_i$$ exists. The combination $$a_i \cdot (M_i^{-1} \bmod m_i) \cdot M_i$$ is congruent to $$a_i$$ modulo $$m_i$$ and to $$0$$ modulo every other $$m_j$$, because each $$M_i$$ is divisible by all moduli other than $$m_i$$. Summing these terms reproduces every residue simultaneously.

### Worked Example

Apply the formula to Han Xing's system, with $$m = 3 \cdot 5 \cdot 7 = 105$$:

$$
\begin{aligned}
x \equiv 2 \cdot \big(2 \cdot (5 \cdot 7)\big) + 3 \cdot \big(1 \cdot (3 \cdot 7)\big) + 2 \cdot \big(1 \cdot (3 \cdot 5)\big) \equiv 233 \equiv 23 \pmod{105}.
\end{aligned}
$$

The first inverse is $$M_1^{-1} = 35^{-1} \equiv 2^{-1} \equiv 2 \pmod 3$$; the other two inverses are $$1$$ because $$21 \equiv 1 \pmod 5$$ and $$15 \equiv 1 \pmod 7$$. The result $$x = 23$$ checks against all three congruences: $$23 \bmod 3 = 2$$, $$23 \bmod 5 = 3$$, and $$23 \bmod 7 = 2$$.

## The Theorem as a Ring Isomorphism

The constructive formula resembles a magic formula until it is read structurally. The CRT does more than solve a system: when $$m$$ and $$n$$ are coprime, it establishes a **ring isomorphism**

$$
\begin{aligned}
\mathbb{Z}_{mn} \;\cong\; \mathbb{Z}_m \times \mathbb{Z}_n.
\end{aligned}
$$

An element of $$\mathbb{Z}_m \times \mathbb{Z}_n$$ is a pair whose first component lives in $$\mathbb{Z}_m$$ and second component in $$\mathbb{Z}_n$$. Addition and multiplication are performed component by component, and inverses are computed component by component as well:

```
in Z_3 x Z_5:
  (1, 3) + (2, 2) = (1+2 mod 3, 3+2 mod 5) = (0, 0)
  (1, 2) . (2, 3) = (1*2 mod 3, 2*3 mod 5) = (2, 1)
```

A map $$f : A \to B$$ between two rings is a ring isomorphism when it is bijective and preserves both operations:

$$
\begin{aligned}
f(x + y) &= f(x) + f(y), \\
f(xy) &= f(x)\,f(y).
\end{aligned}
$$

Isomorphism means the two structures are interchangeable for the purpose of computation. One can move an element into whichever world makes the arithmetic cheaper, perform the operation there, and move the result back. The two directions of the map are not symmetric in cost.

```
       Z_15 world                            Z_3 x Z_5 world
  +----------------+        CRT^-1         +-------------------+
  |   x = 7 . 13   | -------------------->  | (1,2) . (1,3)     |
  +----------------+   (reduce mod 3, 5)    +-------------------+
          ^                                          |
          |                                          | multiply
          |              CRT                         v   componentwise
  +----------------+ <--------------------  +-------------------+
  |      x = 1     |    (recombine)         |      (1, 1)       |
  +----------------+                        +-------------------+
```

### Moving Between the Two Representations

The forward map, from $$\mathbb{Z}_{mn}$$ to $$\mathbb{Z}_m \times \mathbb{Z}_n$$, is a pair of reductions: an element $$x$$ maps to $$(x \bmod m,\ x \bmod n)$$. This direction is cheap.

The reverse map, from $$\mathbb{Z}_m \times \mathbb{Z}_n$$ back to $$\mathbb{Z}_{mn}$$, is exactly the CRT reconstruction. A pair $$(a, b)$$ maps to

$$
\begin{aligned}
x \equiv a\,(n^{-1} \bmod m)\,n + b\,(m^{-1} \bmod n)\,m \pmod{mn}.
\end{aligned}
$$

The two modular inverses $$n^{-1} \bmod m$$ and $$m^{-1} \bmod n$$ depend only on the moduli, so they can be precomputed once and reused for every reconstruction with the same factors.

## Application 1 — Fast RSA Signatures

RSA signing computes $$s = m^d \bmod n$$, where $$n = pq$$ is the product of two primes and $$d$$ is the private exponent. The modular exponentiation dominates the cost, and that cost grows with the size of the modulus. The CRT lets the signer work in $$\mathbb{Z}_p \times \mathbb{Z}_q$$ instead of $$\mathbb{Z}_n$$, where each exponentiation operates on numbers roughly half the bit length of $$n$$.

The signer holds the factorization $$n = pq$$ as part of the private key, so the CRT decomposition is available. The procedure computes the signature in each factor and recombines:

$$
\begin{aligned}
s_p &= m^{\,d \bmod (p-1)} \bmod p, \\
s_q &= m^{\,d \bmod (q-1)} \bmod q,
\end{aligned}
$$

and then reconstructs the full signature with the CRT formula:

$$
\begin{aligned}
s \equiv \big(s_p\,(q^{-1} \bmod p)\,q + s_q\,(p^{-1} \bmod q)\,p\big) \pmod{n}.
\end{aligned}
$$

The exponents are reduced modulo $$p-1$$ and $$q-1$$ by Fermat's little theorem, which keeps them small as well. The two exponentiations act on half-size parameters, and modular exponentiation cost grows faster than linearly in operand size, so splitting the work into two half-size exponentiations is substantially cheaper than one full-size exponentiation. In practice this yields roughly a fourfold speedup.

```
   Z_n world                                Z_p x Z_q world
  +-------------+        CRT^-1           +-----------------------+
  | m mod n     | ----------------------> | (m mod p, m mod q)    |
  +-------------+   (reduce mod p, q)     +-----------------------+
                                                    |
                                                    | exponentiate
                                                    | in each factor
                                                    v
  +-------------+         CRT             +-----------------------+
  | m^d mod n   | <---------------------- | (m^d mod p, m^d mod q)|
  +-------------+      (recombine)        +-----------------------+
```

**Security note.** The CRT speedup introduces a fault-attack surface. If a hardware fault corrupts exactly one of the two branches, say $$s_p$$ is computed correctly but $$s_q$$ is not, the resulting faulty signature $$s'$$ satisfies $$\gcd(s'^{\,e} - m,\ n) = p$$, which reveals the factorization of $$n$$. This is the [Boneh–DeMillo–Lipton fault attack](https://link.springer.com/article/10.1007/s001450010016). Implementations that use RSA-CRT must verify the signature before releasing it, or otherwise guard against single-branch faults.

## Application 2 — Square Roots Modulo a Composite

The isomorphism also explains a counting fact that looks surprising from inside $$\mathbb{Z}_n$$ alone: a number can have **four** square roots modulo $$pq$$.

In a field, the picture is constrained. A polynomial of degree $$k$$ has at most $$k$$ roots, so in $$\mathbb{Z}_p$$ with $$p$$ an odd prime a number has at most two square roots. Concretely, in $$\mathbb{Z}_7$$ the value $$4$$ has the two roots $$2$$ and $$5$$, while $$3$$ has none.

The ring $$\mathbb{Z}_{pq}$$ with $$p \neq q$$ both odd primes is not a field, and here a number has either $$0$$ or $$4$$ square roots. The reason is the CRT. Through the isomorphism $$f : \mathbb{Z}_p \times \mathbb{Z}_q \to \mathbb{Z}_{pq}$$, a square root in $$\mathbb{Z}_{pq}$$ corresponds to a pair of square roots, one in each factor. If $$\pm x_p$$ are the two roots of $$x$$ in $$\mathbb{Z}_p$$ and $$\pm x_q$$ are the two roots in $$\mathbb{Z}_q$$, then because the isomorphism preserves multiplication,

$$
\begin{aligned}
f(x_p, x_q)\,f(x_p, x_q) = f(x_p x_p,\ x_q x_q) = f(x, x) = x,
\end{aligned}
$$

so $$f(x_p, x_q)$$ is a square root of $$x$$ in $$\mathbb{Z}_{pq}$$. The same holds for each of the four sign combinations $$(\pm x_p, \pm x_q)$$, giving four distinct roots. For example, $$1$$ has the four square roots $$1, 4, 11, 14$$ in $$\mathbb{Z}_{15}$$, since $$4^2 = 16 \equiv 1$$, $$11^2 = 121 \equiv 1$$, and $$14^2 = 196 \equiv 1 \pmod{15}$$.

This four-root structure underpins the Rabin cryptosystem and the broader observation that extracting square roots modulo $$n$$ is equivalent to factoring $$n$$: knowing two square roots whose sum is not $$0$$ modulo $$n$$ yields a nontrivial factor through a single $$\gcd$$ computation.

## Frequently Asked Questions

**Q: What condition must the moduli satisfy for the Chinese Remainder Theorem to apply?**

The moduli must be pairwise coprime, meaning $$\gcd(m_i, m_j) = 1$$ for every pair $$i \neq j$$. Under this condition the system has a unique solution modulo the product $$m = m_1 \cdots m_n$$. Pairwise coprimality is what makes each $$M_i = m/m_i$$ invertible modulo $$m_i$$, which the constructive formula requires.

**Q: Why is the forward direction of the CRT map cheaper than the reverse direction?**

The forward map sends $$x$$ to the tuple of residues $$(x \bmod m_1, \ldots, x \bmod m_n)$$, which is just a set of reductions. The reverse map must reconstruct a single integer from its residues, which requires the modular inverses $$M_i^{-1} \bmod m_i$$ and a weighted sum. Computing inverses is the expensive part, though they can be precomputed once when the moduli are fixed.

**Q: Concretely, where does the speedup in RSA-CRT signing come from?**

Two places. First, the exponentiations run modulo $$p$$ and $$q$$ rather than modulo $$n = pq$$, so the operands are about half the bit length. Second, the exponents are reduced modulo $$p-1$$ and $$q-1$$ via Fermat's little theorem, keeping them small. Since modular exponentiation cost grows faster than linearly in operand size, two half-size exponentiations cost much less than one full-size exponentiation, yielding roughly a fourfold improvement.

**Q: Why does a number have four square roots modulo $$pq$$ but at most two modulo a prime?**

Modulo a prime $$p$$, the ring $$\mathbb{Z}_p$$ is a field, so the degree-2 equation $$y^2 = x$$ has at most two roots. Modulo $$pq$$ the CRT isomorphism $$\mathbb{Z}_{pq} \cong \mathbb{Z}_p \times \mathbb{Z}_q$$ means a root corresponds to an independent choice of root in each factor. With two sign choices in each of the two factors, there are $$2 \times 2 = 4$$ combinations, hence four roots when any exist.

**Q: Combining the applications, why does the CRT both speed up RSA and threaten it through square roots?**

Both facts come from the same isomorphism $$\mathbb{Z}_n \cong \mathbb{Z}_p \times \mathbb{Z}_q$$. The speedup uses it constructively: the signer, who knows $$p$$ and $$q$$, moves into the product ring to compute cheaply. The threat uses it destructively: an attacker who can obtain two distinct square roots of the same value (for instance via a single-branch fault in RSA-CRT signing) recovers a factor of $$n$$ through $$\gcd$$, because the differing roots disagree in exactly one CRT component. The structure that helps the key holder also leaks the factorization to anyone who can observe inconsistent results across the two components.

**Q: Why must an RSA-CRT implementation verify the signature before releasing it?**

Because a fault affecting only one of the two CRT branches produces a faulty signature $$s'$$ with $$\gcd(s'^{\,e} - m,\ n) = p$$, directly exposing the private factorization. Verifying $$s'^{\,e} \equiv m \pmod n$$ before output catches the corrupted result and prevents the leak, neutralizing the Boneh–DeMillo–Lipton fault attack.

## Conclusion

The Chinese Remainder Theorem is best understood not as a congruence-solving trick but as the ring isomorphism $$\mathbb{Z}_{mn} \cong \mathbb{Z}_m \times \mathbb{Z}_n$$ between two equivalent computational worlds. The forward direction is a cheap pair of reductions; the reverse direction is the constructive reconstruction formula. RSA signing exploits this by computing in the half-size factors and recombining, at the cost of a fault-attack surface that requires verification before release. The same isomorphism accounts for the four square roots a value can have modulo $$pq$$, and for the equivalence between extracting those roots and factoring the modulus.

![CRT cryptography mindmap]({{site.url_complet}}/assets/article/cryptographie/crt/2026-06-28-chinese-remainder-theorem-cryptography.png)

## References

- [Boneh, DeMillo, Lipton — On the Importance of Eliminating Errors in Cryptographic Computations](https://link.springer.com/article/10.1007/s001450010016)
- [keylength.com — Cryptographic Key Length Recommendations](https://www.keylength.com)
- [Claude Code](https://claude.com/product/claude-code)
