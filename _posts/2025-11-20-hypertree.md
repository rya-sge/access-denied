---
layout: post
title: Hypergraph and Hypertree - Overview
date:   2025-11-19
locale: en-GB
lang: en
last-update: 
categories: programmation
tags: graph hypertreee hypergraph tree
description: Tornado Cash is one of Ethereum’s pioneering privacy protocols build on zk-SNARK and Circom zero-knowledge circuits.
isMath: false
image: /assets/article/cryptographie/zero-knowledge-proof/tornado_cash/tornado_cash_deposit.drawio.png
---

A **hypergraph** is a generalization of a graph where an edge may connect **any number of vertices**, not just two.
 Formally, it is a pair `H=(V,E)`where `V` is a set of vertices and each **hyperedge** `e∈E` is a subset of `V`.

Examples:

- Ordinary graphs → hypergraphs where all edges have size 2
- Fano plane → a 3-uniform hypergraph (all edges have size 3)

[TOC]



------

### Hypertree (in a few words)

A **hypertree** is a *tree-like hypergraph*.
 It is a hypergraph that can be arranged on an underlying tree so that each hyperedge forms a connected subtree.
 Hypertrees represent the “acyclic” hypergraphs—those without complex cycle structures—and are the structural backbone of efficient algorithms in CSPs and databases.

## Hypergraphs: Definitions and Constructions**



https://engineering.tamu.edu/news/2025/06/hypergraphs-are-worth-the-hype.html



https://www.math.ucdavis.edu/~saito/data/tensor/bretto_hypergraph-theory.pdf





A **hypergraph** is a pair

$$
H = (V, E)
$$
where:

- V is a finite set of **vertices**,

- E is a set (or multiset) of **hyperedges**, each hyperedge being a subset of vertices:

  $$
  e \subseteq V.
  $$

A hypergraph is **kkk-uniform** if all hyperedges have size kkk:

$$
\forall e \in E,\quad |e| = k.
$$


------

## Auxiliary Graphs

Several classical graphs derived from a hypergraph are used to study structural properties.

### Incidence graph

$$
I(H) = (V \cup E,\; \{(v,e)\mid v\in e\})
$$

### 2-section (primal graph)

Two vertices are adjacent if they co-occur in some hyperedge:

$$
G(H) = (V,\; \{\{u,v\}\mid \exists e\in E:\{u,v\}\subseteq e\})
$$

### Line graph

Vertices represent hyperedges, edges represent intersecting hyperedges:

$$
L(H) = (E,\; \{\{e,f\}\mid e\cap f\neq\varnothing\})
$$

------

## Cycles and Acyclicity in Hypergraphs

Unlike graphs, hypergraphs admit multiple inequivalent definitions of acyclicity.



------

## Fagin’s Acyclicity Notions (α,β,γ\alpha,\beta,\gammaα,β,γ)

These definitions are fundamental in database theory.

### α\alphaα-acyclicity

A hypergraph H=(V,E)H=(V,E)H=(V,E) is **α\alphaα-acyclic** if it admits a **join tree**:
 a tree whose nodes are hyperedges such that for every vertex v∈Vv\in Vv∈V, the set:

$$
\{\, e\in E \mid v\in e \,\}
$$
induces a connected subtree.

α\alphaα-acyclicity is the strongest widely used database notion of hypergraph acyclicity.

### β\betaβ-acyclicity and γ\gammaγ-acyclicity

Stronger acyclicity notions, each eliminating additional forms of cycle-like structures.
 They satisfy:

$$
\gamma\text{-acyclic} \;\Rightarrow\; \beta\text{-acyclic} 
\;\Rightarrow\; \alpha\text{-acyclic}.
$$

------

## Hypertrees

A **hypertree** is a hypergraph that can be represented by a host tree.

## Host-tree definition

A hypergraph H=(V,E) is a **hypertree** if there exists a tree `T` with vertex set containing `V` such that every hyperedge `e∈E` induces a **connected** subtree of T:

$$
\forall e\in E,\quad T[e]\ \text{is connected}.
$$


## Helly property

Hypertrees satisfy the **Helly property**:

$$
\text{If every pair of edges in } \mathcal{F}\subseteq E \text{ intersects,}
\quad\text{then}\quad \bigcap \mathcal{F}\neq\varnothing.
$$

## Duality characterization

A hypergraph is a hypertree **if** its **dual hypergraph** is α\alphaα-acyclic.

------

## Hypertree Decompositions

Hypertree decompositions generalize graph tree decompositions to hypergraphs.

A **hypertree decomposition** of H=(V,E) consists of:

- a tree `T`,
- a bag function χ:V(T)→2V\chi : V(T)\to 2^Vχ:V(T)→2V,
- an edge-cover function λ:V(T)→2E\lambda : V(T)\to 2^Eλ:V(T)→2E,

such that:

### Edge coverage

$$
\forall e\in E,\;\exists t\in V(T):\; e\subseteq \chi(t).
$$

### Running intersection property

For every vertex `v∈V`, the set of nodes containing `v` is connected:

$$
\{\, t \in V(T) \mid v \in \chi(t) \,\}
\text{ induces a connected subtree of } T.
$$

### Bag coverage by hyperedges

Each bag is covered by the hyperedges assigned to that node:

$$
\chi(t) \subseteq \bigcup_{e\in \lambda(t)} e.
$$
Variants (generalized, fractional) modify condition 3 to allow fractional or more flexible coverings.

------

## Hypertree Width

Given a hypertree decomposition (T,χ,λ)(T,\chi,\lambda)(T,χ,λ), the **width** is:

$$
\max_{t \in V(T)} |\lambda(t)|.
$$


The **hypertree width** of HHH is the minimum achievable width:

$$
\mathsf{hw}(H)
=
\min_{(T,\chi,\lambda)}\;
\max_{t\in V(T)}
|\lambda(t)|.
$$

### Fractional hypertree width

Allows fractional covers and is always ≤ generalized hypertree width.

------

### Algorithmic Implications

If a CSP or conjunctive query has hypergraph `H` with:

$$
\mathsf{hw}(H) \le k,
$$
then evaluation is polynomial-time for fixed `k`.
 Bounded (fractional) hypertree width ⇒ tractable cases of many NP-hard problems.



### Example

#### Why the Fano plane is a hypergraph

The **Fano plane**  {F} is the smallest finite projective plane. It has:

- **7 points**
- **7 lines**
- each line contains **3 points**
- each pair of points lies on **exactly one** line

If we denote:

- the **points** by a set `V`
- each **line** by a set of points e⊆Ve \subseteq Ve⊆V

then we can treat every line as a **hyperedge**, because a hyperedge is simply a subset of vertices, not restricted to size 2.

Explicitly:
$$
\mathcal{F} = (V, E)
$$
with:
$$
V = \{1,2,3,4,5,6,7\}
$$
and the 7 “lines” (hyperedges), each of size 3, e.g.:
$$
E = 
\Big\{
\{1,2,3\},
\{1,4,5\},
\{1,6,7\},
\{2,4,6\},
\{2,5,7\},
\{3,4,7\},
\{3,5,6\}
\Big\}
$$
Every set in E has 3 elements ⇒ the Fano plane is a **3-uniform hypergraph**.

------

#### So what type of hypergraph is it?

- It is **3-uniform** (every line has 3 points).
- It is **linear** (every pair of hyperedges intersects in at most one point).
- It is **regular** (each point is in exactly 3 hyperedges).
- It is **symmetric** (same number of points and lines: 7).
- It is **not acyclic** — it contains multiple cycle structures.

In fact, the Fano plane is a **Steiner system** S(2,3,7), which is a special class of uniform, pairwise-balanced hypergraphs.

------

#### Is the Fano plane a hypertree?

**No.**
 The Fano plane is *not* a hypertree and does *not* satisfy any common hypergraph acyclicity notions:

- It is **not Berge-acyclic** (it contains Berge cycles).
- It is **not α\alphaα-, β\betaβ-, or γ\gammaγ-acyclic**.
- It does **not** have a join-tree.
- It does **not** satisfy the Helly property.

The Fano plane is **strongly cyclic** as a hypergraph.

------

#### Summary

| Concept              | Does the Fano plane satisfy it? | Why                                        |
| -------------------- | ------------------------------- | ------------------------------------------ |
| Hypergraph           | &#x2611;                        | points = vertices, lines = hyperedges      |
| 3-uniform hypergraph | &#x2611;                        | each line has 3 points                     |
| Linear hypergraph    | &#x2611;                        | any two lines meet in ≤1 point             |
| Hypertree            | &#x2612;                        | strongly cyclic, fails Helly, no join tree |
| Acyclic hypergraph   | &#x2612;                        | contains cycles                            |

------

## Worked Example

Let:

$$
V = \{a,b,c,d\},\qquad
E = \{\{a,b\},\{b,c\},\{c,d\}\}.
$$
A hypertree decomposition:

Bags:

$$
\chi(t_1)=\{a,b\},\qquad
\chi(t_2)=\{b,c\},\qquad
\chi(t_3)=\{c,d\}
$$
Edge covers:

$$
\lambda(t_1)=\{\{a,b\}\},\qquad
\lambda(t_2)=\{\{b,c\}\},\qquad
\lambda(t_3)=\{\{c,d\}\}
$$
Width:

$$
\max_i |\lambda(t_i)| = 1.
$$

------

## References (hyperlinks)

- **Hypergraph — Wikipedia**
   [https://en.wikipedia.org/wiki/Hypergraph](https://en.wikipedia.org/wiki/Hypergraph?utm_source=chatgpt.com)
- **Hypertree — Wikipedia**
   [https://en.wikipedia.org/wiki/Hypertree](https://en.wikipedia.org/wiki/Hypertree?utm_source=chatgpt.com)
- **Di Fonzo (2025), “Hypertrees and their host trees: a survey”**
   [https://arxiv.org/pdf/2504.15570](https://arxiv.org/pdf/2504.15570?utm_source=chatgpt.com)
- **Gottlob, Greco, Scarcello — “Treewidth and Hypertree Width”**
   [https://www.mat.unical.it/~ggreco/files/GottlobGrecoScarcello.pdf](https://www.mat.unical.it/~ggreco/files/GottlobGrecoScarcello.pdf?utm_source=chatgpt.com)
- **Fagin — “Degrees of Acyclicity for Hypergraphs and Relational Database Schemes”**
   [https://databasetheory.org/sites/default/files/2016-07/RonFagin-ullman.pdf](https://databasetheory.org/sites/default/files/2016-07/RonFagin-ullman.pdf?utm_source=chatgpt.com)

## Use case

### Hypergrpah Neural network

https://sites.google.com/view/hnn-tutorial

https://www.youtube.com/watch?v=yQRzCkHZFu4



