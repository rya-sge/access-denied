# Introduction to Lattices



Lattices are regular arrangements of points in Euclidean space. They naturally occur in many settings, like crystallography, sphere packings (stacking oranges), etc. 

They have many applications in computer science and mathematics, including the solution of integer programming problems, diophantine approximation, cryptanalysis, the design of error correcting codes for multi antenna systems, and many more. 

Recently, lattices have also attracted much attention as a source of computational hardness for the design of secure cryptographic functions. This course oers an introduction to lattices. We will study the best currently known algorithms to solve the most important lattice problems, and how lattices are used in several representative applications. We begin with the denition of lattices and their most important mathematical properties

Definition 1. 

A lattice is a discrete additive subgroup of R n , i.e., it is a subset Λ ⊆ R n satisfying the following properties: 

- **subgroup** 

(subgroup) Λ is closed under addition and subtraction

- Discrete

There is an   E > 0 such that any two distinct lattice points
$$
x \neq y ∈ Λ 
$$
are at distance at least
$$
|| x − y|| ≥ e
$$
Not every subgroup of `R^n` is a lattice.

(subgroup) 

Example: 

Q represent the  **field of rational numbers**

`Q^n` is a subgroup of `R^n` , but not a lattice, because it is not discrete  

The simplest example of lattice is the set of all n-dimensional vectors with integer entries.

Example 2:

The set `Z^n` is a lattice because integer vectors can be added and subtracted, and clearly the distance between any two integer vectors is at least 1.

Other lattices can be obtained from `Zn` by applying a (nonsingular) linear transformation.





https://cseweb.ucsd.edu/classes/wi10/cse206a/lec1.pdf

https://www.telsy.com/en/the-mathematics-behind-pqc-the-lattices/

https://www.telsy.com/la-matematica-dietro-la-pqc-i-reticoli/

https://www.telsy.com/la-matematica-dietro-la-pqc-i-reticoli/

## Lattice-based cryptography scheme

ome of the well-known lattice-based cryptographic schemes include:

### Learning With Errors (LWE)

LWE is a problem that is believed to be hard to solve, making it an excellent basis for cryptography. 

The LWE problem involves a given linear equation with a small error, and the challenge is to find the secret vector when the error is unknown. The presumed difficulty of solving LWE, even with a quantum computer, provides the security foundation for cryptographic schemes based on this problem.

### Ring-LWE

A variant of the LWE, Ring-LWE operates in a `ring` (a set with two operations satisfying properties like associativity and distributivity) instead of a vector space, making the scheme more efficient without compromising its security.

### NTRUEncrypt

1. NTRUEncrypt is a lattice-based public-key cryptosystem that is fast and maintains security levels even against quantum computers. It is considered one of the most practical and efficient lattice-based cryptographic schemes available.

https://medium.com/@ashfaqe.sa12/a-deep-dive-into-lattice-based-cryptography-navigating-the-quantum-future-d11261d3da4f

https://math.hawaii.edu/~jb/lat1-6.pdf

https://everydaymath.uchicago.edu/teaching-topics/computation/documents/mult-lattice-ex-1.pdf

https://user.math.uzh.ch/bariffi/slides_PhDSeminar_lattice.pdf

https://eprint.iacr.org/2015/938.pdf

https://math.libretexts.org/Bookshelves/Combinatorics_and_Discrete_Mathematics/Applied_Discrete_Structures_(Doerr_and_Levasseur)/13%3A_Boolean_Algebra/13.02%3A_Lattices

https://simons.berkeley.edu/sites/default/files/docs/14953/intro.pdf

https://pub.math.leidenuniv.nl/~stevenhagenp/ANTproc/06hwl.pdf