---
layout: post
title: "Lattice-Based Cryptography - The Short Integer Solution (SIS) Problem"
date: 2025-04-23
lang: en
locale: en-GB
categories: cryptography security
tags: ipfs merkle-tree merkle-dag dag graph git
description: Short integer solution (SIS)is an average-case problems used in lattice-based cryptography constructions. SIS is one of the problems believed to be hard even for quantum computers.
image: /assets/article/cryptographie/lattice/SIS-average-case.png
isMath: true
---

**Short integer solution (SIS)** is an average-case problems used in [lattice-based cryptography](https://en.wikipedia.org/wiki/Lattice-based_cryptography) constructions.  SIS is one of the problems believed to be hard even for quantum computers. 

SIS was introduced by Ajtain in 1996 who presented a family of one-way functions based on the SIS problem. 

 SIS underpins a wide range of cryptographic protocols, from digital signatures, hash function, to post-quantum encryption schemes.

> This article comes primarily  from several different pdfs as well as Wikipedia. I hope to make it more personal in the future

[TOC]



## Average VS worst-case problem

The Short Integer Solution (SIS) problem is an *average* case problem that is used in lattice-based cryptography constructions. He showed that it is secure in an average case if ![{\displaystyle \mathrm {SVP} _{\gamma }}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6cdaf054b38c3d4501a98ef0e0874ac4cf9efbe1) (where ![{\displaystyle \gamma =n^{c}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6556c3ef5e2c02127afc193d154dba653591cca2) for some constant ![{\displaystyle c>0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2ba126f626d61752f62eaacaf11761a54de4dc84)) is hard in a worst-case scenario. Such a reduction is called a *worst-case to average-case reduction*. 

One of the key features that lattice cryptography provides is that it allows cryptography to be based on worst-case problems. 

- Average problems:

So far, all of the problems that we have seen so far such as CDH, DDH, and Factor are all average-case problems. In order for an adversary to break these problems, it must only succeed in solving the problem for some random instance. 

-  Worst-case. 

Lattice cryptography can be based on worst-case problems such as GapSVP. In order for an adversary to break these problems, it must succeed in solving the problem on all instance of the problem.

![average-worst-case-problem]({{site.url_complet}}/assets/article/cryptographie/lattice/average-worst-case-problem.png)

Image from [crypto.stanford - Lecture 9: Lattice Cryptography and the SIS Problem](https://crypto.stanford.edu/cs355/18sp/lec9.pdf)

Average case problems are the problems that are hard to be solved for some randomly selected instances. For cryptography applications, worst case complexity is not sufficient, and we need to guarantee cryptographic construction are hard based on average case complexity. 

But thanks to Ajtai, if SIVP_y is hard in the worst-case, then SIS is hard on average.



Schema from [Cryptography 101 - Lecture 5. SIS/LWE and lattices](https://www.youtube.com/watch?v=5QdJJWS7Umw)![SIS-average-case]({{site.url_complet}}/assets/article/cryptographie/lattice/SIS-average-case.png)



Reference:  [Wikipedia - Short integer solution problem](https://en.wikipedia.org/wiki/Short_integer_solution_problem), [Cryptography 101 - Lecture 5. SIS/LWE and lattices](https://www.youtube.com/watch?v=5QdJJWS7Umw)

### Lattice Problems

In order to construct crypto schemes, worst-case problems such as`GapSVP` are not used directly. 

Instead, people use average-case problems that have reductions from GapSVP. 

There are two main average-case problems that people use.

- The first problem is called the **short integers solutions (SIS)** problem, which was introduced by Ajtai. It gives rise to one-way functions, collision-resistant hash functions, digital signatures, and other “minicrypt” primitives. 
- The second problem is called the **learning with errors (LWE)** problem, which was introduced by Regev. It gives rise to public-key encryption, fully homomorphic encryption, identity-based encryption, and beyond. 

The existence of an adversary that can break SIS or LWE can be directly translated to breaking the GapSVP problem. 

## What Is the SIS Problem?

The SIS problem can be understood as follows:

Let `n, m, q, B` ∈ `N` be positive integers.

Given a matrix A, **find** a non-zero integer vector X such that:
$$
\begin{aligned}
A \in \mathbb{Z}_q^{m \times n}
\end{aligned}
$$

$$
\begin{aligned}
\mathbf{x} \in \mathbb{Z}^n \
\end{aligned}
$$

$$
\begin{aligned}
A \cdot \mathbf{x} \equiv \mathbf{0} \pmod{q} \quad \text{and} \quad \|\mathbf{x}\|_∞ \leq \beta
\end{aligned}
$$

where:

x is a *non-zero* vector

In simpler terms, SIS asks for a short (i.e., low-norm) integer vector that satisfies a modular linear equation defined by a given matrix.

So the SIS problem is parameterized by the matrix dimensions n, m ∈ N, modulus q, and a norm bound `B` on the solution. 

At first, it might be difficult to keep track of all these parameters.

- One should think of `n` as the security parameter `λ` that defines the hardness of the problem. 

The bigger the n is, the harder the problem becomes. 

- The parameter `m` is set depending on the specific applications, but generally m >> n. 
- The modulus `q` can be set to be any `q = poly(n)`, but concretely, just think of `q = O(n^2 )`. 
- The norm bound `B << q` should also be set depending on the specific applications

It is conjectured that for any sufficiently large `n ∈ N` (this is the security parameter), for any `m, q, B ∈ N`, satisfying `q > B · poly(n)` (for any polynomial poly), the SIS(n, m, q, B) is hard. 

The SIS(n, m, q, B) problem can be used to construct a collision resistant hash function.

Reference: [crypto.stanford - Lecture 9: Lattice Cryptography and the SIS Problem](https://crypto.stanford.edu/cs355/18sp/lec9.pdf)

## Why Is SIS Hard?

SIS is a generalization of well-known hard problems in lattice theory, especially the **Shortest Vector Problem (SVP)**. The difficulty of SIS depends on the parameters \( n \), \( m \), \( q \), and B. For appropriately chosen values, SIS is believed to be computationally infeasible — even for quantum adversaries.

The hardness of SIS has been rigorously related to worst-case lattice problems, meaning that a solution to a single average-case instance of SIS can imply a solution to the hardest instances of lattice problems. This connection makes SIS a powerful foundation for cryptographic applications.

## SIS in Cryptography

SIS serves as a cornerstone for **lattice-based cryptographic primitives**, including:

- **Hash functions**: SIS-based constructions yield collision-resistant hash functions with strong security guarantees.
- **Digital signatures**: Many post-quantum signature schemes, like **Lyubashevsky’s scheme**, rely on SIS.
- **Zero-knowledge proofs**: SIS enables efficient, non-interactive zero-knowledge proofs that are post-quantum secure.
- **Commitment schemes**: SIS offers a strong basis for building binding and hiding commitment protocols.

### Post-Quantum Cryptography

The SIS problem and its variants are used in several post-quantum security schemes including [CRYSTALS-Dilithium](https://en.wikipedia.org/wiki/Lattice-based_cryptography) and [Falcon](https://en.wikipedia.org/wiki/Lattice-based_cryptography).

See [falcon sign ](https://falcon-sign.info) & [CRYSTALS-Dilithium](https://pq-crystals.org/dilithium/data/dilithium-specification-round3.pdf)

## SIS vs. LWE

SIS is often discussed alongside the **Learning With Errors (LWE)** problem. While LWE underlies many encryption schemes, SIS is primarily used for authentication and integrity-related protocols like signatures. Both are fundamental to **post-quantum cryptography**, but they solve different problems and have different mathematical structures.

## Conclusion

The Short Integer Solution (SIS) problem stands as a pillar of lattice-based cryptography, offering a high level of security rooted in hard mathematical problems. With the rise of quantum computing, SIS and related lattice problems are poised to play a central role in safeguarding digital communication for decades to come.

Mindmap made with the help of ChatGPT

![lattice-sis-mindmap]({{site.url_complet}}/assets/article/cryptographie/lattice/lattice-sis-mindmap.png)

## Reference

- ChatGPT with the inputs "Write me an article about *Short Integer Solution (SIS)*", "Explain this: the hardness of SIS has been rigorously related to worst-case lattice problems...."
- [crypto.stanford - Lecture 9: Lattice Cryptography and the SIS Problem](https://crypto.stanford.edu/cs355/18sp/lec9.pdf)
- [Simons berkeley - The SIS Problem and Cryptographic Applications](https://simons.berkeley.edu/sites/default/files/docs/14967/sis.pdf)
- [Wikipedia - Short integer solution problem](https://en.wikipedia.org/wiki/Short_integer_solution_problem)
