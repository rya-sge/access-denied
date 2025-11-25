---
layout: post
title: Hypergraph and Hypertree - Overview
date:   2025-11-25
locale: en-GB
lang: en
last-update: 
categories: programmation
tags: graph hypertreee hypergraph tree
description: A hypergraph is a generalization of a graph where an edge may connect any number of vertices, not just two.
isMath: true
image: 
---

A **hypergraph** is a generalization of a graph where an edge may connect **any number of vertices**, not just two.
 Formally, it is a pair `H=(V,E)`where `V` is a set of vertices and each **hyperedge** `e∈E` is a subset of `V`.

Examples:

- Ordinary graphs → hypergraphs where all edges have size 2
- Fano plane → a 3-uniform hypergraph (all edges have size 3)

[TOC]



------

### Introduction

A **hypertree** is a *tree-like hypergraph*.

- It is a hypergraph that can be arranged on an underlying tree so that each hyperedge forms a connected subtree.
- Hypertrees represent the “acyclic” hypergraphs—those without complex cycle structures—and are the structural backbone of efficient algorithms in CSPs and databases.

## Hypergraphs: Definitions and Constructions

A **hypergraph** is a pair

$$
\begin{aligned}
H = (V, E)
\end{aligned}
$$
where:

- V is a finite set of **vertices**,

- E is a set (or multiset) of **hyperedges**, each hyperedge being a subset of vertices:

  $$
  \begin{aligned}
  e \subseteq V.
  \end{aligned}
  $$

A hypergraph is **k-uniform** if all hyperedges have size `k`:

$$
\begin{aligned}
\forall e \in E,\quad |e| = k.
\end{aligned}
$$



Reference:

- [xengineering.tamu.edu - HYPERGRAPHS ARE WORTH THE HYPE](https://engineering.tamu.edu/news/2025/06/hypergraphs-are-worth-the-hype.html)
- [Alain Bretto - Hypergraph Theory](https://www.math.ucdavis.edu/~saito/data/tensor/bretto_hypergraph-theory.pdf)

------

## Cycles and Acyclicity in Hypergraphs

### Acyclicity Notion

A hypergraph can be reduced to have no hyperedge by the Graham reduction.

A hypergraph is **α-acyclic** if you can repeatedly apply the **Graham reduction** until no hyperedges remain.

If the process gets stuck before all hyperedges are removed, then the hypergraph is **α-cyclic**.

[Alain Bretto - Hypergraph Theory](https://www.math.ucdavis.edu/~saito/data/tensor/bretto_hypergraph-theory.pdf), page.72

------

## Hypertrees

A **hypertree** is a hypergraph that can be represented by a host tree.

- Hypertrees are also called arboreal hypergraphs 
- hypergraph H is a hypertree if and only if H is Helly and its line graph is [chordal](https://en.wikipedia.org/wiki/Chordal_graph).

Reference: Complexity Aspects of the Helly Property: Graphs and Hypergraphs, page 6

### Host-tree definition

A hypergraph H=(V,E) is a **hypertree** if there exists a tree `T` with vertex set containing `V` such that every hyperedge `e∈E` induces a **connected** subtree of T:

$$
\forall e\in E,\quad T[e]\ \text{is connected}.
$$

### Helly property

A hypergraph has the Helly property if each intersecting family has a non-empty intersection 

- It an hypergraph contains a triangle it has not the Helly property. 
- A hypergraph having the Helly property will be called Helly hypergraph.

Hypertrees satisfy the **Helly property**:

$$
\text{If every pair of edges in } \mathcal{F}\subseteq E \text{ intersects,}
\quad\text{then}\quad \bigcap \mathcal{F}\neq\varnothing.
$$

Example:

**Helly**

H having V (H) = {1, 2, 3, 4} and E(H) = {{1, 2},{1, 3}, {1, 4}} is Helly

**Not-Helly**

E(H) = {{1, 2}, {1, 3}, {2, 3}} then H is not Helly.

[Alain Bretto - Hypergraph Theory](https://www.math.ucdavis.edu/~saito/data/tensor/bretto_hypergraph-theory.pdf), page. 30

[Alain Bretto - Hypergraph Theory](https://www.math.ucdavis.edu/~saito/data/tensor/bretto_hypergraph-theory.pdf), page.6



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
\begin{aligned}
\mathcal{F} = (V, E)
\end{aligned}
$$
with:
$$
\begin{aligned}
V = \{1,2,3,4,5,6,7\}
\end{aligned}
$$
and the 7 “lines” (hyperedges), each of size 3, e.g.:
$$
\begin{aligned}
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
\end{aligned}
$$
Every set in E has 3 elements ⇒ the Fano plane is a **3-uniform hypergraph**.

------

##### So what type of hypergraph is it?

- It is **3-uniform** (every line has 3 points).
- It is **linear** (every pair of hyperedges intersects in at most one point).
- It is **regular** (each point is in exactly 3 hyperedges).
- It is **symmetric** (same number of points and lines: 7).
- It is **not acyclic** — it contains multiple cycle structures.

In fact, the Fano plane is a **Steiner system** S(2,3,7), which is a special class of uniform, pairwise-balanced hypergraphs.

------

##### Is the Fano plane a hypertree?

**No.**
 The Fano plane is *not* a hypertree and does *not* satisfy any common hypergraph acyclicity notions:

- It is **not Berge-acyclic** (it contains Berge cycles).
- It is **not α\alphaα-, β\betaβ-, or γ\gammaγ-acyclic**.
- It does **not** have a join-tree.
- It does **not** satisfy the Helly property.

The Fano plane is **strongly cyclic** as a hypergraph.

------

##### Summary

| Concept              | Does the Fano plane satisfy it? | Why                                        |
| -------------------- | ------------------------------- | ------------------------------------------ |
| Hypergraph           | &#x2611;                        | points = vertices, lines = hyperedges      |
| 3-uniform hypergraph | &#x2611;                        | each line has 3 points                     |
| Linear hypergraph    | &#x2611;                        | any two lines meet in ≤1 point             |
| Hypertree            | &#x2612;                        | strongly cyclic, fails Helly, no join tree |
| Acyclic hypergraph   | &#x2612;                        | contains cycles                            |

------



## Use case

### Hypergrpah Neural network

- [Hypergraph Neural Networks: An In-Depth and Step-By-Step Guide](https://sites.google.com/view/hnn-tutorial)
- [YouTube  - Hypergraph Neural Networks: An In-depth and Step-By-Step Guide (Teaser)](https://www.youtube.com/watch?v=yQRzCkHZFu4)

## Reference

- [Wikipedia - Hypergraph](https://en.wikipedia.org/wiki/Hypergraph)

- [xengineering.tamu.edu - HYPERGRAPHS ARE WORTH THE HYPE](https://engineering.tamu.edu/news/2025/06/hypergraphs-are-worth-the-hype.html)

- [Alain Bretto - Hypergraph Theory](https://www.math.ucdavis.edu/~saito/data/tensor/bretto_hypergraph-theory.pdf)

- [Wikipedia - Hypertree — Wikipedia](https://en.wikipedia.org/wiki/Hypertree)
  
- [Arxiv - Di Fonzo (2025) - Hypertrees and their host trees: a survey](https://arxiv.org/pdf/2504.15570)
  
- [Gottlob, Greco, Scarcello — “Treewidth and Hypertree Width](https://www.mat.unical.it/~ggreco/files/GottlobGrecoScarcello.pdf)
  
  
