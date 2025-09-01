# Plonk

ll details). Our universal SNARK requires the prover to compute 5 polynomial commitments, combined with two opening proofs to evaluate the polynomial commitments at a random challenge point. 

There are two “flavours”of PlonK to suit the tastes of the user. 

- By increasing the proof size by two group elements, the total prover computations can be reduced by ≈ 10%. 
- The combined degree of the polynomials is either **9**(n + a) (larger proofs) or **11**(n + a) (smaller proofs, reduced verifier work), where `n` is the number of multiplication gates and `a` is the number of addition gates. 
- Currently, the most efficient fully-succinct SNARK construction available is Groth’s 2016 construction, which requires a unique, non-updateable CRS per circuit. 
  - Proof construction times are dominated by 3n + m G1 and n G2 group exponentiations, where m is formally the number of R1CS variables, and is typically bounded by n (for the rest of this section, the reader may assume m = n for simplicity). 
  - If we assume that one G2 exponentiation is equivalent to three G1 exponentiations, this yields 6n + m equivalent G1 group exponentiations



## Fast Fouriter transforms (FFT)

When constructing proofs, the time taken to perform the required fast fourier transforms is comparable to the time taken for elliptic curve scalar multiplications. 

- The number of field multiplications in table 1 is obtained from 8 FFTs of size 4n, 5 FFTs of size 2n and 12 FFTs of size n. 
- The number of FFT transforms can be significantly reduced, if a circuit’s preprocessed polynomials are provided as evaluations over the 4n’th roots of unity (instead of in Lagrange-base form).  However, given this dramatically increases the amount of information required to construct proofs, we omit this optimisation from our benchmarks. We conclude the introduction with a comparision to relevant concurrent work.



### Comparison with Marlin

Concrete comparison to Marlin 

While **Fractal** leverages the sparse bi-variate evaluation technique in the context of transparent recursive SNARKs, Marlin focuses on constructing a fully succinct (universal) SNARK as in this paper.

-  It is not completely straightforward to compare this work and Marlin, as we are in the realm of concrete constants, and the basic measure both works use is different. While we take our main parameter n to be the number of addition and multiplication gates in a fan-in two circuit; - 
  - Marlin uses as their main parameter the maximal number of non-zeroes in one of the three matrices describing an R1CS. 
  - For the same value of `n`, PlonK outperforms Marlin, e.g. by roughly a 2x factor in prover group operations and proof size. In the extreme case of a circuit with only multiplication gates, this would indeed represent the performance difference between the two systems.
  - However, in constraint systems with “frequent large addition fan-in” Marlin may outperform the currently specified variant7 of PlonK. For example, this happens in the extreme case of one “fully dense” R1CS constraint

https://eprint.iacr.org/2019/1047

We compare our universal SNARK (PlonK) to both non-universal and universal state-of-the-art SNARKs. As of publication, the only fully succinct universal SNARK is the fully-succinct Sonic protocol [MBKM], which requires the prover to perform 273n G1 exponentiations, where *n* is the number of multiplication gates. Sonic restricts each wire to three linear constraints, often necessitating dummy multiplication gates, inflating the actual gate count and hence prover effort.

In contrast, PlonK requires five polynomial commitments, combined with two opening proofs to evaluate the polynomial commitments at a random challenge point.

It supports two configurations: one with slightly larger proofs (and fewer prover computations), and another with smaller proofs (and less verifier work). The total polynomial degree is either 9(n + a) or 11(n + a), where *a* is the number of addition gates.

Groth16 [Gro16], the most efficient non-universal fully succinct SNARK, needs a unique non-updateable CRS per circuit. It involves 3n + m G1 and n G2 exponentiations, where m ≈ n. Assuming 1 G2 ≈ 3 G1, this totals ~6n + m equivalent G1 operations.

Direct comparisons depend on circuit assumptions. In practice, a ≈ 2n is common. For circuits with only multiplication gates:

- **PlonK vs Groth16**: ~1.1× more prover work.
- **PlonK vs Sonic**: ~30× less prover work.

When a = 2n:

- PlonK is ~2.25× more work than Groth16, but ~10× less than Sonic.

When a = 5n:

- PlonK is ~3× more than Groth16, but ~5× less than Sonic.

These comparisons focus on group exponentiations only.

PlonK’s structured reference string (SRS) size matches the number of gates (for the “fast” variant), significantly smaller than in other schemes.

Additionally, proof construction in PlonK involves a non-trivial number of field multiplications and FFTs, which are also present in other universal SNARKs.

## Details

We describe the protocol below as a non-interactive protocol using the Fiat-Shamir heuristic. 

For this purpose we always denote by transcript the concatenation of the common preprocessed input, and public input, and the proof elements written by the prover up to a certain point in time. We use transcript for obtaining random challenges via Fiat-Shamir. 

One can alternatively, replace all points where we write below “compute challenges”, by the verifier sending random field elements, to obtain the interactive protocol from which we derive the non-interactive one



### Veri





Explanation:

### **a) Compute Zero Polynomial Evaluation**

The zero polynomial ZH(X)` vanishes on all points in the evaluation domain H:
$$
Z_H(X) = \prod_{w \in H} (X - w)
$$
It's used to ensure that certain constraints are satisfied on the domain HHH. Typically, the prover evaluates it at a challenge point ζ\zetaζ:
$$
Z_H(\zeta)
$$

------

#### **b) Compute Lagrange Polynomial Evaluation**

Each Lagrange basis polynomial Li(X)L_i(X)Li(X) satisfies Li(wj)=δijL_i(w_j) = \delta_{ij}Li(wj)=δij for domain points wj∈Hw_j \in Hwj∈H:
$$
L_i(X) = \prod_{\substack{j = 0 \\ j \ne i}}^{n - 1} \frac{X - w_j}{w_i - w_j}
$$
To evaluate at the challenge point ζ\zetaζ:
$$
L_i(\zeta)
$$

------

### **c) Compute Public Input Polynomial Evaluation**

The public input polynomial `PI(X)` is defined as a linear combination of the first `k`Lagrange polynomials (assuming `k` public inputs π0,…,πk\pi_0, \ldots, \pi_kπ0,…,πk):
$$
\$$
PI(X) = \sum_{i=0}^k \pi_i \cdot L_i(X)
\$$
$$
Evaluate it at the challenge point ζ\zetaζ:
$$
PI(\zeta)
$$

------

### **d) Compute First Part of Batched Polynomial Commitment**

To reduce verifier cost, PlonK combines multiple polynomial openings into one by taking a random linear combination. If the committed polynomials are P1(X),P2(X),…,Pk(X),  and random scalars a1,…,ak, then the batched polynomial is:
$$
R(X) = a_1 P_1(X) + a_2 P_2(X) + \cdots + a_k P_k(X)
$$
This is the first step in computing a batched opening proof at a single evaluation point (e.g., ζ\zetaζ).



### Summary Table:

| Step                               | What                                 | Why it Matters in PlonK                                 |
| ---------------------------------- | ------------------------------------ | ------------------------------------------------------- |
| a) Zero polynomial eval            | Evaluates ZH(X)Z_H(X)ZH(X)           | Enforces that constraints vanish over the domain        |
| b) Lagrange polynomial eval        | Evaluates Li(X)L_i(X)Li(X)           | Enables interpolation and handling of fixed inputs      |
| c) Public input polynomial eval    | Evaluates PI(X)PI(X)PI(X)            | Enforces public input consistency                       |
| d) Batched commitment (first part) | Builds a linear combo of polynomials | Enables a single opening proof for multiple commitments |

# Reference

- [David Wong - How does PLONK work? Part 1: What's PLONK?](https://www.youtube.com/watch?v=RUZcam_jrz0)

- [ZK Whiteboard Sessions - Module Five: PLONK and Custom Gates with Adrian Hamelink](https://www.youtube.com/watch?v=Uldlq35Se3k)

- [ZKP MOOC Lecture 5: The Plonk SNARK](https://www.youtube.com/watch?v=A0oZVEXav24)

- [ZKpodcast: Dive into Plonk](https://www.youtube.com/watch?v=n6_nicI4ckM)

- [ZK Whiteboard Sessions – Interview with Ariel Gabizon on The PLONK Origin Story and Roadmap](https://www.youtube.com/watch?v=GKja-cJFYdA)

  





https://www.maya-zk.com/blog/plonk-round1



https://coingeek.com/how-plonk-works-part-1/

https://vitalik.eth.limo/general/2019/09/22/plonk.html