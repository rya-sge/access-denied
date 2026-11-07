#!/usr/bin/env python3
"""Numeric checks for the Grover article and the `grover-algorithm` skill.

Every number the article derives comes from a run of this script. It simulates
the algorithm exactly on a state vector (small N) and on the two-amplitude
recurrence of Grover's Theorem 2 (large N). Requires numpy only.

Run:  python3 verify_grover.py
Exit status is non-zero if any check fails.
"""
import math
import sys

import numpy as np

failures = 0


def check(label, ok, detail=""):
    global failures
    failures += 0 if ok else 1
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))


def walsh(n):
    """W_ij = 2^(-n/2) (-1)^(i.j), bitwise dot product."""
    N = 2**n
    W = np.empty((N, N))
    for i in range(N):
        for j in range(N):
            W[i, j] = (-1) ** bin(i & j).count("1")
    return W / math.sqrt(N)


def diffusion(N):
    """D_ij = 2/N off the diagonal, D_ii = -1 + 2/N (paper, eq. 4.0)."""
    return 2.0 / N * np.ones((N, N)) - np.eye(N)


def statevector_probs(N, marked, iters):
    """Success probability after 0..iters iterations, by full simulation."""
    amp = np.full(N, 1 / math.sqrt(N))
    D = diffusion(N)
    out = []
    for _ in range(iters + 1):
        out.append(float(np.sum(amp[list(marked)] ** 2)))
        amp[list(marked)] *= -1  # step (a): phase rotation by pi
        amp = D @ amp  # step (b): diffusion
    return out


def closed_form(N, M, j):
    """BBHT eq. (3): success probability sin^2((2j+1) theta)."""
    return math.sin((2 * j + 1) * math.asin(math.sqrt(M / N))) ** 2


print("== Paper, section 5: structure of the diffusion operator ==")
for n in (2, 3, 4, 5):
    N = 2**n
    W = walsh(n)
    R = -np.eye(N)
    R[0, 0] = 1
    D = diffusion(N)
    check(f"Theorem 1: D = WRW for n={n}", np.allclose(W @ R @ W, D))
    check(f"D^2 = I (D unitary) for n={n}", np.allclose(D @ D, np.eye(N)))
    P = np.ones((N, N)) / N
    check(f"P^2 = P and D = -I + 2P for n={n}", np.allclose(P @ P, P) and np.allclose(D, 2 * P - np.eye(N)))

v = np.array([3.0, -1.0, 2.0, 0.5, 7.0, -4.0, 1.0, 2.5])
check("D is inversion about the average", np.allclose(diffusion(8) @ v, 2 * v.mean() - v))

print("\n== Paper, Theorem 3 and the sqrt(2N) bound ==")
for N in (16, 64, 1024, 2**20):
    k, l = 1 / math.sqrt(N), 1 / math.sqrt(N)
    min_dk, steps = float("inf"), 0
    while k < 1 / math.sqrt(2):
        k1 = -k  # step (a)
        k2 = (2 / N - 1) * k1 + 2 * (N - 1) / N * l
        l2 = 2 / N * k1 + (N - 2) / N * l
        min_dk = min(min_dk, k2 - k)
        k, l = k2, l2
        steps += 1
    check(
        f"N={N}: gain per iteration > 1/(2 sqrt N); {steps} iterations reach k >= 1/sqrt2",
        min_dk > 1 / (2 * math.sqrt(N)) and steps < math.sqrt(2 * N),
        f"min gain*sqrt(N)={min_dk*math.sqrt(N):.3f}, sqrt(2N)={math.sqrt(2*N):.1f}, "
        f"pi/8 sqrt(N)={math.pi/8*math.sqrt(N):.1f}",
    )

print("\n== Closed form against a full state-vector simulation ==")
for N, M in ((4, 1), (8, 1), (16, 1), (64, 1), (64, 4), (256, 3), (1024, 1)):
    t = int(math.pi / 4 / math.asin(math.sqrt(M / N)))
    sim = statevector_probs(N, range(M), 2 * t + 2)
    ok = all(abs(sim[j] - closed_form(N, M, j)) < 1e-9 for j in range(len(sim)))
    check(f"N={N}, M={M}: sin^2((2j+1)theta) matches j=0..{2*t+2}", ok, f"floor(pi/(4 theta))={t}, P={sim[t]:.4f}")

print("\n== Small worked example, N=8, M=1 ==")
theta8 = math.asin(1 / math.sqrt(8))
print(f"theta = {theta8:.6f} rad = {math.degrees(theta8):.3f} deg")
for j in range(7):
    print(f"  j={j}: P={closed_form(8, 1, j):.4f}")
amp = np.full(8, 1 / math.sqrt(8))
D8 = diffusion(8)
for j in (1, 2):
    amp[5] *= -1
    amp = D8 @ amp
    print(f"  after iteration {j}: marked amplitude {amp[5]:.5f}, other amplitudes {amp[0]:.5f}")
check("N=4 finishes with certainty after one iteration", abs(closed_form(4, 1, 1) - 1) < 1e-12)
check("M = N/4 finishes with certainty after one iteration", abs(closed_form(1024, 256, 1) - 1) < 1e-12)

print("\n== BBHT numeric claims, N = 2^20 ==")
N = 2**20
theta = math.asin(1 / math.sqrt(N))
m = int(math.pi / (4 * theta))
check("floor(pi/(4 theta)) = 804", m == 804, f"m={m}, failure={1-closed_form(N,1,m):.3e}, 1/N={1/N:.3e}")
p596 = closed_form(N, 1, 596)
check("596 iterations give P about 0.8442", abs(p596 - 0.8442) < 5e-4, f"P={p596:.4f}, expected cost={596/p596:.1f}")
check("804 iterations with 4 solutions give P < 1e-6", closed_form(N, 4, 804) < 1e-6, f"P={closed_form(N,4,804):.3e}")
j_paper = round(math.sqrt(2 * N))
check("sqrt(2N) iterations give P below 9.5%", closed_form(N, 1, j_paper) < 0.095, f"j={j_paper}, P={closed_form(N,1,j_paper):.4f}")
j_half = next(j for j in range(m) if closed_form(N, 1, j) >= 0.5)
print(f"first j with P >= 1/2: {j_half}; pi/8 sqrt(N) = {math.pi/8*math.sqrt(N):.1f}")

best_j = min(range(1, m + 1), key=lambda j: j / closed_form(N, 1, j))
print(f"restart strategy optimum: j={best_j}, P={closed_form(N,1,best_j):.4f}, E={best_j/closed_form(N,1,best_j):.1f}")

print("\n== BBHT Lemma 2: uniformly random iteration count ==")
for N, M in ((1024, 1), (1024, 7), (4096, 64)):
    th = math.asin(math.sqrt(M / N))
    mm = math.ceil(1 / math.sin(2 * th))
    avg = sum(closed_form(N, M, j) for j in range(mm)) / mm
    formula = 0.5 - math.sin(4 * mm * th) / (4 * mm * math.sin(2 * th))
    check(f"N={N}, M={M}, m={mm}: average = formula, and >= 1/4", abs(avg - formula) < 1e-10 and avg >= 0.25, f"P={avg:.4f}")

print("\n== Cryptographic sizes ==")
for bits in (56, 128, 192, 256):
    print(f"  {bits}-bit key: pi/4 * 2^{bits//2} = 2^{math.log2(math.pi/4)+bits/2:.2f} iterations")
for depth in (40, 64, 96):
    print(f"  AES-128, MAXDEPTH=2^{depth}: quantum gates 2^{170-depth}")
print("  parallel Grover on S machines: budget of each is sqrt(N/S) iterations")
for maxd, bits in ((40, 128), (64, 128)):
    # S machines each run depth 2^maxd: need pi/4 sqrt(N/S) = 2^maxd in iterations (one iteration taken as one depth unit)
    s = 2 * (math.log2(math.pi / 4) + bits / 2 - maxd)
    print(f"  {bits}-bit key, depth 2^{maxd} iterations per machine: 2^{s:.1f} machines")
check("SHA-256 Toffoli-depth iteration: 2*10112+509+509 = 21242", 2 * 10112 + 509 + 509 == 21242, f"log2={math.log2(21242):.2f}")
print(f"  2^(78-64) squared = 2^{2*(78-64)} = {2**28}")

print(f"\n{'ALL CHECKS PASSED' if failures == 0 else str(failures) + ' CHECK(S) FAILED'}")
sys.exit(1 if failures else 0)
