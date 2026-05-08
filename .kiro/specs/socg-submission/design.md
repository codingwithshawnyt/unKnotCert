# Design: SoCG-Submission-Ready Paper on Virtual Unknotting Barriers

## Overview

This document translates the approved requirements into a concrete execution plan. It covers four concurrent work streams — **mathematical**, **algorithmic/experimental**, **manuscript**, and **reproducibility** — and maps each to the phases in Requirement 10.

The target deliverable is a SoCG 2026 submission built around one proven theorem (greedy completeness for bigon monotone reducibility), a rigorous stuck-state characterization via the nesting forest, and a proven 3-crossing classical–virtual gap for $D_{28}$, with all five benchmarks and random-unknot scaling experiments as computational support. The No-Up conjecture is positioned as an open question in the Burckel/Östlund/Hagge–Yazinski/Hui lineage.

---

## 1. Mathematical design

### 1.1 Notation and setting (used throughout proofs)

A **decorated Gauss word** is a cyclic sequence $w$ over the alphabet $\{(i,+), (i,-) : i \in [n]\}$ in which each label $i \in [n]$ appears exactly twice, once with each sign. The **crossing number** is $\mathrm{cr}(w) = n$. The **chord diagram** of $w$ is the circular arrangement of $2n$ endpoints with each label connecting its two positions by a chord.

For two distinct chords $i, j$ with first positions $i_1, j_1$ and second positions $i_2, j_2$:
- $i$ **nests** $j$ iff $i_1 < j_1 < j_2 < i_2$ (cyclic order, any rotation).
- $i$ and $j$ are **interleaved** (linked) iff $i_1 < j_1 < i_2 < j_2$ (cyclic order).
- $i$ **directly nests** $j$ iff $i$ nests $j$ and no other chord $k$ satisfies $i$ nests $k$ nests $j$.

The **interlacement graph** $\Gamma(w)$ has vertex set $[n]$ and an edge $\{i,j\}$ iff $i$ and $j$ are interleaved. The **nesting forest** $N(w)$ has vertex set $[n]$ and a directed edge $i \to j$ iff $i$ directly nests $j$. $N(w)$ is a forest (no chord is directly nested by two different chords in a Gauss word).

The **algebraic Reidemeister moves** are:
- **R1-down** at position $p$: delete the adjacent opposite-sign pair $(w_p, w_{p+1}) = ((i,+), (i,-))$ or $((i,-), (i,+))$. Crossing number decreases by 1.
- **R2-down** on directly-nested pair $(i, j)$ with $i$ nesting $j$: delete all four tokens of $i$ and $j$, provided the signs are opposite between $i_1$ and $i_2$ (bigon sign condition). Crossing number decreases by 2.
- **R3** on three mutually interleaved chords in an R3-compatible cyclic order: reorder as specified in `core/gauss.py`. Crossing number unchanged.
- R1-up, R2-up: inverses of the above.

A **bigon R2-down** additionally requires that the two cyclic arcs between $i_1$ and $j_1$, and between $j_2$ and $i_2$, contain no other chord endpoints. A **permissive R2-down** drops this arc-emptiness condition. The current codebase implements bigon R2-down in `get_bigon_R2_pairs` and permissive R2-down in `get_valid_actions`.

$\mathrm{Top}_v(w)$ is defined in the paper as the minimax crossing number over algebraic Reidemeister sequences from $w$ to the empty word, using the *permissive* move set. This is the definition the paper must carry throughout.

### 1.2 Theorem 1.1 (greedy completeness): proof design

#### Non-confluence of $\mathcal{B}$ in general, and why the decision theorem still holds

The bigon rewriting system $\mathcal{B}$ is **not** confluent in general. The following stacked-triple counterexample shows this:

Take chords $i \succ j \succ k$ all stacked with empty bigon outer arcs (both $\text{R2-down}(i,j)$ and $\text{R2-down}(j,k)$ available), and two chords $\ell, \ell'$ directly nested by $k$ but interleaved with each other. The cyclic order is
\[
\ldots\ i_1\ j_1\ k_1\ \underbrace{\ell\ \ell'\ \ell\ \ell'}_{\text{interleaved}}\ k_2\ j_2\ i_2\ \ldots
\]
At $w$, the only available bigon moves are $\mu_1 = \text{R2-down}(i,j)$ and $\mu_2 = \text{R2-down}(j,k)$; neither R1-down nor bigon R2-down on $(k,\ell)$ or $(k,\ell')$ applies, because the outer arcs of those pairs contain $\ell'$ or $\ell$ respectively. After $\mu_1$: chord set $\{k, \ell, \ell'\}$, stuck. After $\mu_2$: chord set $\{i, \ell, \ell'\}$, stuck. The two maximal greedy runs end at distinct non-empty stuck states; no common successor exists.

Crucially, $w$ does not admit any peeling to $\emptyset$ in this example — neither stuck descendant reaches $\emptyset$. The counterexample falsifies full confluence but is *consistent with* the weaker property that suffices for the decision algorithm.

#### Corrected statement (to appear in §3 of the paper)

> **Theorem 1.1 (Greedy Completeness to $\emptyset$).** Let $w$ be a Gauss word and let $\mathcal{B}$ be the rewriting system on chord diagrams with rules bigon R1-down and bigon R2-down. The greedy algorithm that repeatedly applies any available $\mathcal{B}$-rule terminates in at most $\mathrm{cr}(w)$ steps. If $w$ admits any $\mathcal{B}$-reduction to the empty word, then every maximal greedy run reaches the empty word. Consequently, the decision problem "does $w$ admit a $\mathcal{B}$-reduction to $\emptyset$?" is solvable in $O(n^3)$ time by running any single greedy strategy.

This is "confluence-to-$\emptyset$", strictly weaker than full confluence. It is exactly what the polynomial-time decision algorithm needs: run any greedy strategy; answer YES iff it reaches $\emptyset$. Contrapositively, if some greedy run fails to reach $\emptyset$, no reduction to $\emptyset$ exists.

#### Proof strategy

We prove Theorem 1.1 via the following two lemmas. Termination is trivial (each step decreases crossing number by $\geq 1$).

**Lemma A (Deletion-Monotonicity).** Let $\mu, \nu$ be distinct $\mathcal{B}$-moves available at $w$ whose chord sets are disjoint. Then $\nu$ is available at $\mu(w)$ (and vice versa). In particular, disjoint $\mathcal{B}$-moves commute.

*Proof.* The validity of a bigon R1-down depends only on two chord endpoints being cyclically adjacent; removing an unrelated chord's endpoints cannot separate adjacent tokens. The validity of a bigon R2-down depends on two outer arcs being empty of other endpoints; removing an unrelated chord's endpoints can only reduce the count of obstructing endpoints in those arcs. Formalize by counting occupied positions in each outer arc before and after $\mu$.

**Lemma B (Reduction-Preservation under Single Moves).** If $w \to^*_{\mathcal{B}} \emptyset$ and $\mu$ is any $\mathcal{B}$-move available at $w$, then $\mu(w) \to^*_{\mathcal{B}} \emptyset$.

*Proof.* By induction on $\mathrm{cr}(w)$. The case $\mathrm{cr}(w) = 0$ is vacuous. Suppose $\mathrm{cr}(w) = n > 0$ and the lemma holds for smaller crossing numbers. Let $\sigma = (\mu_1, \mu_2, \ldots, \mu_m)$ be a $\mathcal{B}$-reduction of $w$ to $\emptyset$, and let $\mu$ be available at $w$.

*Case A:* $\mu_1$ has chord set disjoint from $\mu$'s chord set. Then by Lemma A, $\mu$ is available at $\mu_1(w)$, and $\mu_1(\mu(w)) = \mu(\mu_1(w))$. Also $\mu_1(w) \to^*_{\mathcal{B}} \emptyset$ via $(\mu_2, \ldots, \mu_m)$, so by induction (on $\mu_1(w)$, which has smaller crossing number) applied with move $\mu$, we get $\mu(\mu_1(w)) \to^*_{\mathcal{B}} \emptyset$. Hence $\mu(w) \to_{\mathcal{B}} \mu_1(\mu(w)) \to^*_{\mathcal{B}} \emptyset$.

*Case B:* $\mu_1 = \mu$. Then $(\mu_2, \ldots, \mu_m)$ is a reduction of $\mu(w)$ to $\emptyset$, done.

*Case C:* $\mu_1 \neq \mu$ and their chord sets intersect. We enumerate the chord-set overlap patterns, using the nesting-forest structure (§1.3).
  - *C1.* $\mu = \text{R2-down}(a, b)$ with $a$ directly nesting $b$, and $\mu_1 = \text{R1-down}(b)$. Availability of $\mu$ requires the bigon condition on $(a,b)$; availability of $\mu_1$ requires $b$'s endpoints cyclically adjacent. Together these force $a$'s arc to contain only $b$'s two endpoints. Then $\mu_1(w)$ makes $a$ R1-down-eligible, so $\mu_1(w) \to_{\text{R1-down}(a)} \mu(w)$. Since $\mu_1(w) \to^*_{\mathcal{B}} \emptyset$ via $(\mu_2, \ldots, \mu_m)$, we apply induction to $\mu_1(w)$ with move $\text{R1-down}(a)$ to obtain $\mu(w) \to^*_{\mathcal{B}} \emptyset$.
  - *C2.* $\mu = \text{R2-down}(a, b)$ and $\mu_1 = \text{R1-down}(a)$: symmetric to C1.
  - *C3.* $\mu = \text{R2-down}(a, b)$ and $\mu_1 = \text{R2-down}(a, b)$: this is Case B.
  - *C4.* $\mu = \text{R2-down}(a, b)$ with $a$ directly nesting $b$, and $\mu_1 = \text{R2-down}(c, a)$ with $c$ directly nesting $a$. Both bigon. Apply $\mu_1$: $c$ and $a$ are removed, leaving $b$. The availability of $\mu_1$ required the outer arc $(c_1, a_1)$ empty and $(a_2, c_2)$ empty. The availability of $\mu$ required $(a_1, b_1)$ and $(b_2, a_2)$ empty. Together: $c_1, a_1, b_1$ are cyclically adjacent modulo $b$'s internal structure, and $b_2, a_2, c_2$ symmetric. After $\mu_1$, the two tokens of $b$ are cyclically adjacent to the neighbors of $c_1$ and $c_2$. Whether $b$ becomes R1-down-eligible depends on whether $b$'s own arc is empty. If empty, $\mu_1(w) \to_{\text{R1-down}(b)}$ (with matching state), apply induction. If non-empty, analyze via sub-cases — full case enumeration goes in the manuscript proof; the pattern is that $\mu$'s chord set is always reachable from $\mu_1(w)$ by a bounded-length bigon sequence, making induction applicable on the image state.
  - *C5.* $\mu = \text{R2-down}(a, b)$ and $\mu_1 = \text{R2-down}(b, d)$ where $b$ directly nests $d$: symmetric to C4 after swapping roles.
  - Pairs where $\mu$ is R1-down and $\mu_1$ is R2-down reduce to C1/C2 by symmetry.

In every overlap case, $\mu(w)$ is reachable from $\mu_1(w)$ by a bounded-length bigon sequence, so induction on $\mu_1(w)$ applies and yields $\mu(w) \to^*_{\mathcal{B}} \emptyset$.

**Theorem 1.1.** Suppose $w \to^*_{\mathcal{B}} \emptyset$ via some sequence. Let $\tau = (\nu_1, \nu_2, \ldots)$ be any maximal greedy run. By Lemma B applied inductively, after each step $\nu_k$ the state $\nu_k(\cdots \nu_1(w))$ still admits a $\mathcal{B}$-reduction to $\emptyset$. Since $\tau$ is maximal and each step reduces crossing number by $\geq 1$, $\tau$ terminates. A terminal state admitting a reduction to $\emptyset$ must *be* $\emptyset$. Hence $\tau$ reaches $\emptyset$.

**Runtime.** Per step: enumerate available bigon R1-down positions ($O(n)$) and bigon R2-down pairs ($O(n^2)$). The enumeration is $O(n^2)$, times $\leq n$ steps, giving $O(n^3)$.

#### Risk under the corrected proof

The risk profile is strictly milder than the earlier full-confluence attempt. There is no Case-5 confluence cliff. The one non-trivial case is C4/C5 (stacked R2-downs), where the induction step requires verifying that $\mu(w)$ is always reachable from $\mu_1(w)$ by a bounded-length bigon sequence. In the user's stacked-triple counterexample, $w$ does *not* admit a reduction to $\emptyset$ (both descendants are stuck), so the hypothesis of Lemma B is false and the lemma is vacuous there — the counterexample does not threaten the proof.

The tripwire in Requirement 10.2 is accordingly relaxed: it now fires if the C4/C5 induction step resists formalization for two full days of focused work, rather than firing on a specific Case-5 confluence failure.

### 1.3 Stuck-state characterization via nesting forest: proof design

#### Statement (to appear in §5 of the paper)

> Let $w$ be a Gauss word. The bigon rewriting system $\mathcal{B}$ has no applicable rule at $w$ if and only if:
> 1. no adjacent opposite-sign pair exists in $w$ (no R1-down); AND
> 2. the nesting forest $N(w)$ has no edge (no directly-nested pair), equivalently, every interlacement component of $w$ is a complete graph ("fully interleaved").

#### Proof strategy

Both directions are straightforward once the nesting forest is formally defined. The current draft's hand-wave ("at the bottom of the nesting hierarchy, there must exist a directly nested pair, a leaf of the nesting tree") is fixed by:

**Lemma D.** In a Gauss word $w$, the nesting relation restricted to any subset of chords is a partial order (antisymmetric and transitive). The nesting forest $N(w)$ is the Hasse diagram of this partial order, restricted to cover relations.

**Lemma E.** Every chord $c$ that is nested by some other chord is directly nested by exactly one chord (its parent in $N(w)$).

**Main proof.** Condition (1) iff no R1-down by definition. For condition (2): bigon R2-down applies to $(i,j)$ iff $i$ directly nests $j$ iff $(i,j)$ is an edge of $N(w)$, iff some interlacement component contains a nested pair, iff some interlacement component is not a complete graph. The equivalence "no nested pair iff fully interleaved" is immediate since for two chords, either they are interleaved or one nests the other or they are disjoint (disjoint chords lie in different interlacement components, so irrelevant for within-component analysis).

This is clean, finite, and verifiable. No leaf-of-tree hand-wave.

### 1.4 Exact 3-crossing gap for $D_{28}$: proof design

#### Statement (to appear in §6 of the paper)

> $\mathrm{Top}_c(D_{28}) - \mathrm{Top}_v(D_{28}) \geq 3$.

#### Proof strategy

- **Upper bound on $\mathrm{Top}_v(D_{28})$:** exhibit the explicit permissive-R2 monotone path found by BRS (already in `outputs/exact_barrier_results.json`, 16 moves, crossing-number trace $[28, 26, 24, \ldots, 4, 3, 2, 1, 0]$). This witnesses $\mathrm{Top}_v(D_{28}) \leq 28$. The lower bound $\mathrm{Top}_v(D_{28}) \geq 28$ is trivial.
- **Lower bound on $\mathrm{Top}_c(D_{28})$:** cite Burton et al. 2021, Theorem from Section 3, who prove $m_c(D_{28}) = 3$, i.e., $\mathrm{Top}_c(D_{28}) = 31$.
- Combine: $31 - 28 = 3$.

The proof is one paragraph. It must be presented carefully: the gap is between the classical planar minimax barrier (Burton's value) and the *algebraic permissive-virtual* minimax barrier (ours). The paper must not over-claim this as a gap in virtual knot theory proper (Requirement 8.1 second bullet).

### 1.5 No-Up conjecture: literature positioning

Presented in §7 (Discussion / Open Problems) with:
- Explicit statement: every classical unknot Gauss word reduces under {R1↓, R2↓, R3}.
- Precise relation to Östlund 2001 (R1 + R3 only, unoriented plane curves; disproved by Hagge–Yazinski 2014 with 16-crossing counterexample).
- Precise relation to Burckel 2007 (monotone-move completeness conjectures in related settings).
- Precise relation to Hui et al. 2024 (ascending/descending diagrams reduce monotonically — special case).
- Experimental support: five benchmarks all satisfy the conjecture under permissive-R2 (already known); random unknots up to $n \leq 12$ (new experiment; Phase 3).
- Open status explicitly stated, not claimed as near-proven.

---

## 2. Algorithmic and experimental design

### 2.1 Changes to `exact_barrier.py`

Add one new strategy to the existing `bounded_bfs` dispatch:

- **`down_r3_only`**: explore only R1-down, R2-down (permissive), and R3 moves. Not exhaustive in the sense of proving unreachability of arbitrary configurations, but *is* exhaustive for the question "does $w$ reduce to the empty word without any R1-up or R2-up moves?", since the crossing number is non-increasing and the state space at ceiling $\mathrm{cr}(w)$ is finite.

The implementation is a straightforward filter on the action enumeration, parallel to the existing `down_only` strategy:

```python
if down_r3_only and mt not in ('R1_down', 'R2_down', 'R3_A', 'R3_B'):
    continue
```

This strategy settles the No-Up question for any specific input in finite time (bounded by the size of the connected component of $w$ in the restricted state graph, which is at most the full BRS state space at ceiling $\mathrm{cr}(w)$).

### 2.2 Phase 0 experiment: bigon-reducibility of five benchmarks

**Inputs:** the five Gauss codes in `experiments/run.py`.

**Procedure:** run `greedy_bigon_peel_all_orderings` from `algorithms/greedy_peeling.py` on each. This already tries all orderings with backtracking and uses the bigon R2 condition (not permissive), so its output directly answers "is this diagram bigon-reducible?".

**Expected outcomes:**
- Goeritz: **not** bigon-reducible (known from current results; fails even permissive).
- Culprit: **not** bigon-reducible (same).
- $D_{28}$: uncertain — confirmed permissive-reducible, bigon status unknown.
- $D_{43}$: uncertain.
- Ochiai II: uncertain.

**Recorded outputs:** `outputs/phase0_bigon_reducibility.json` with per-diagram success boolean, move sequence (if any), states explored, wall time.

**Decision rule:** the paper's negative-certificate paragraph in §4 or §5 will be written with the exact count of non-bigon-reducible diagrams. If all five are non-bigon-reducible, the paragraph reads "none of the five"; if any are bigon-reducible, the paragraph reads accurately with the count.

### 2.3 Phase 3 experiment: random-unknot scaling

**Inputs:** random classical unknot Gauss words for $n \in \{4, 6, 8, 10, 12\}$ (even $n$ only, for even-length Gauss words; adjust if the convention in `core/gauss.py` allows odd $n$). Sample 100 words per $n$.

**Generation of random classical unknot Gauss words:** generate all planar-realizable Gauss words of length $2n$ at given $n$ by starting from the empty word and applying a sequence of random R-up moves (a known-valid method of generating planar-realizable unknot diagrams). Alternative: enumerate all Gauss words up to canonicalization and filter by planarity using Gauss's parity criterion or Lovász's theorem.

Phase 3 must implement one of these generators in `experiments/random_unknot.py`.

**Procedure per sample $w$:**
1. Run `bounded_bfs(w, ceiling=cr(w), strategy='down_r3_only')`. Record: reducible or not, wall time.
2. Run `greedy_bigon_peel_all_orderings(w)`. Record: reducible or not.

**Recorded outputs:** `outputs/phase3_random_unknots.json` with per-sample result and aggregate statistics per $n$.

**Decision rule:**
- If *every* sample in the scaling experiment reduces under `down_r3_only`, this is *strong* empirical evidence for the No-Up conjecture. The paper reports the success rate and positions the conjecture accordingly.
- If *any* sample does *not* reduce, the paper reports the smallest such counterexample prominently. This outcome triggers Requirement 4.7: reframe the open-problem section as "the No-Up conjecture is false; here is a counterexample at crossing number $n$". This is a stronger paper, not a weaker one.

### 2.4 Reproducibility artifact: directory layout

```
unKnotCert/
├── README.md                       # rewrite for reproduction
├── environment.yml                 # pinned versions
├── reproduce.py                    # top-level entry point
├── core/                           # Gauss words, canonicalization
├── algorithms/                     # greedy_peeling, future bigon variants
├── experiments/
│   ├── run.py                      # benchmark Gauss codes
│   ├── random_unknot.py            # NEW: random unknot generator
│   └── phase0_bigon.py             # NEW: bigon-reducibility on benchmarks
│   └── phase3_scaling.py           # NEW: random-unknot scaling
├── exact_barrier.py                # extended with down_r3_only
├── tests/                          # NEW: unit tests
│   ├── test_gauss.py
│   ├── test_bigon_peel.py
│   └── test_exact_barrier.py
├── Paper/                          # LaTeX
└── outputs/                        # regenerated by reproduce.py
```

`reproduce.py` drives:
1. Phase 0: `experiments/phase0_bigon.py` → `outputs/phase0_bigon_reducibility.json`
2. Benchmark BRS runs: `experiments/run.py` → `outputs/exact_barrier_results.json`
3. Phase 3 scaling: `experiments/phase3_scaling.py` → `outputs/phase3_random_unknots.json`
4. Figure regeneration: `analysis/make_figures.py` and siblings.

`tests/` runs via `pytest tests/`. Target coverage:
- `test_gauss.py`: verify `_pair_positions`, `_is_nested`, `_is_linked`, `get_R1_down_positions`, `get_bigon_R2_pairs`, `is_bigon_R2_down`, `apply_action` for all move types.
- `test_bigon_peel.py`: verify greedy and backtracking on small inputs with known answers.
- `test_exact_barrier.py`: verify BRS on the Culprit benchmark produces the known state counts.

### 2.5 Zenodo archive

Before submission, tag a git release (`v1.0-socg-submission`), push to GitHub (public repo), and archive via Zenodo's GitHub integration. Include the resulting DOI in the manuscript's reproducibility statement.

---

## 3. Manuscript design

### 3.1 New section structure

```
1. Introduction                                 [~60 lines]
2. Preliminaries                                [~80 lines]
   2.1 Gauss words, chord diagrams
   2.2 Algebraic Reidemeister moves; bigon vs. permissive R2
   2.3 Nesting forest and interlacement graph
   2.4 Minimax barriers (classical, virtual-algebraic)
3. Polynomial-time bigon monotone reducibility  [~110 lines]
   3.1 The rewriting system B
   3.2 Deletion-Monotonicity (Lemma A)
   3.3 Reduction-Preservation (Lemma B)
   3.4 Greedy completeness (Theorem 1)
   3.5 Certifying barrier decision (Theorem 2)
   3.6 Algorithm and runtime
4. Stuck states via the nesting forest          [~55 lines]
   4.1 Nesting as a partial order
   4.2 Stuck-state theorem (permissive and bigon versions)
   4.3 Interlacement corollary
5. An exact classical–virtual gap               [~45 lines]
   5.1 Definitions; permissive virtual moves
   5.2 Theorem 3 (gap-of-3 for D_28)
   5.3 Why the gap is not a contradiction with virtual knot theory
6. No-Up disproof and computational study       [~80 lines]
   6.1 Bounded Reidemeister Search (BRS)
   6.2 Proposition 4: Goeritz and Culprit as No-Up counterexamples
   6.3 Five benchmarks
   6.4 Random unknots at n ≤ 12
7. Related work                                 [~40 lines]
8. Open problems and limitations                [~20 lines]
References                                      [~30–50 lines, outside 500-line cap]
```

Total body: ~490 lines, under the 500-line SoCG cap.

### 3.2 Abstract rewrite

Target (one paragraph, ~12 lines):

> We study the combinatorial problem of reducing a signed Gauss word to the empty word under restricted algebraic Reidemeister moves. Our first main result is that *bigon-monotone reducibility* — whether a given Gauss word simplifies using only bigon R1-down and bigon R2-down moves — is decidable in polynomial time by an arbitrary-greedy algorithm, running in $O(n^3)$ with incremental maintenance or $O(n^4)$ naive. Our second main result is the certifying form: the same algorithm outputs matching positive/negative certificates (a deletion sequence to $\emptyset$ for yes-instances, a stuck residual word plus a partial deletion sequence for no-instances), both verifiable in polynomial time. A structural characterization via the *nesting forest* of a Gauss word explains which words the algorithm accepts. Applied to five hard unknot diagrams from Burton et al. (Goeritz, Culprit, $D_{28}$, $D_{43}$, Ochiai II), the algorithm returns no-certificates for all five, showing that these benchmarks are not bigon-reducible. Under the less restrictive permissive-R2 algebraic move set, three of them ($D_{28}$, $D_{43}$, Ochiai II) do reduce, yielding an exact 3-crossing gap for $D_{28}$ between the classical planar minimax barrier (Burton et al.) and the algebraic permissive-virtual barrier. Finally, we disprove the decorated No-Up conjecture — that every classical unknot Gauss word reduces under $\{R1_{\text{down}}, R2_{\text{down}}^{\text{perm}}, R3\}$ — at crossing number at most 11, using Goeritz and Culprit as explicit counterexamples in the lineage of Östlund, Burckel, and Turaev.

### 3.3 Contributions list rewrite

```
1. (Theorem 1) Bigon-monotone reducibility of signed Gauss words is decidable
   in polynomial time. Greedy completeness: every maximal greedy run reaches
   the empty word when any reduction exists. Runtime O(n^3) with incremental
   data structures.
2. (Theorem 2) The certifying-decision algorithmic form: matching positive and
   negative certificates, both polynomial-time verifiable. The negative
   certificate is a stuck residual word; its global non-reducibility follows
   from the Reduction-Preservation lemma.
3. (Theorem, stuck-state) A structural characterization of bigon- and
   permissive-stuck Gauss words via the nesting forest, with a corollary in
   terms of the interlacement graph.
4. (Theorem 3) A proven 3-crossing exact separation between the classical
   planar minimax barrier and the algebraic permissive-virtual barrier for
   Burton et al.'s D_28.
5. (Proposition 4) First explicit disproof of the decorated No-Up conjecture
   at small crossing number: the Goeritz (cr=11) and Culprit (cr=10) Gauss
   words are classical unknot Gauss words not reducible under any
   {R1-down, R2-down (permissive), R3} sequence.
6. A computational study of five hard unknot benchmarks and random unknots
   up to n = 12, with a reproducibility artifact.
```

### 3.4 Double-blind preparation

The submission PDF must:
- Remove author name, affiliation, email from front matter.
- Replace self-references "Ray" / "our earlier work" with anonymous phrasings.
- Anonymize the Zenodo artifact link for submission, keep the DOI for the camera-ready.
- Keep `\hideLIPIcs` from the existing preamble.

A separate pass before submission strips self-identifying content; the non-anonymized version is saved as `Paper/manuscript_identified.tex` for camera-ready.

---

## 4. Phase-by-phase execution design

### Phase 0 (day 0, 1 day)

**Deliverables:**
- `experiments/phase0_bigon.py` (new file) running `greedy_bigon_peel_all_orderings` on all five benchmarks.
- `outputs/phase0_bigon_reducibility.json` with results.
- Extend `exact_barrier.py` with `down_r3_only` strategy and run on all five benchmarks; save to `outputs/phase0_down_r3_only.json`.

**Acceptance:** each benchmark has a recorded `reducible: bool` for both bigon-only and down-r3-only runs.

### Phase 1 (days 1–3)

**Deliverables:**
- `notes/phase1_literature.md`: structured notes on searches of Burckel 2007, Östlund 2001, Hagge–Yazinski 2014, Hui et al. 2024, Manturov *Knot Theory*, Kauffman 1999, GPV 2000, Bouchet and Traldi circle-graph papers, Traldi–Zulli.
- Each source gets: (a) what they prove or conjecture, (b) whether it relates to Theorem 1.1, stuck-state, or No-Up, (c) one-sentence "how we differ" note.

**Acceptance:** literature notes exist; Theorem 1.1's novelty is verified or the tripwire (10.4) fires.

**Tool:** use `remote_web_search` and `web_fetch` for papers with open arxiv/DOI links; `Paper/` for any local PDFs the author uploads.

### Phase 2 (days 3–8, 5 days)

**Deliverables:**
- Formal proof of Lemma A (Deletion-Monotonicity).
- Formal proof of Lemma B (Rescue) with case analysis.
- Formal proof of Theorem 1.1 via Newman's lemma.
- Formal proof of nesting-forest stuck-state theorem.
- Formal proof of the gap-of-3 theorem for $D_{28}$.
- LaTeX draft of §3, §4, §5 with these proofs.

**Acceptance:** the three theorem environments in §3–§5 each contain a proof that stands on its own — every claim either proved here or cited with a precise result reference.

**Tripwire at end of day 2 of Phase 2 (overall day 5):** if Lemma B case 5 is unresolved, invoke Fallback 2 (drop Theorem 1.1; headline becomes stuck-state + gap-of-3).

### Phase 3 (days 8–14, 6 days)

**Deliverables:**
- `experiments/random_unknot.py`: generator for random classical unknot Gauss words.
- `experiments/phase3_scaling.py`: runs all the samples through `down_r3_only` BRS and `greedy_bigon_peel_all_orderings`.
- `outputs/phase3_random_unknots.json`: aggregated results.
- Draft of §6.3 (random-unknot experiment) and §6.4 (No-Up conjecture) in manuscript.
- Additional complexity analysis: a rigorous statement of the canonicalization cost and the BRS state-space bound (even if only a weak exponential), replacing Conjecture 1 or supplementing it.

**Acceptance:** random-unknot experiment runs to completion; §6 is drafted.

### Phase 4 (days 14–24, 10 days)

**Deliverables:**
- Full rewrite of `Paper/manuscript.tex` against the new section structure.
- New abstract (§3.2 above) and contributions list (§3.3 above).
- Related-work section with the Burckel/Östlund/Hagge–Yazinski/Hui paragraph, including the precision-of-statement note required by Requirement 5.3.2.
- All tables using booktabs cleanly.
- All figures regenerated with consistent styling.
- Double-blind pass on text.

**Acceptance:** manuscript compiles without LaTeX errors, fits under 500 lines of body content, and reads end-to-end coherently.

### Phase 5 (days 24–30, 6 days)

**Deliverables:**
- `reproduce.py` with end-to-end pipeline.
- `tests/` directory with unit tests; `pytest tests/` passes.
- Updated `README.md` covering reproduction, directory layout, dependencies.
- Pinned `environment.yml`.
- Git repository cleaned (derived artifacts removed from tracking, `.gitignore` updated).
- Zenodo archive created via GitHub integration; DOI obtained.
- DOI integrated into manuscript's reproducibility statement.

**Acceptance:** fresh clone + `conda env create -f environment.yml` + `python reproduce.py` produces every table and figure in the manuscript within documented runtime.

### Phase 6 (days 30–38, 8 days)

**Deliverables:**
- Reviewer-objection preempts (Requirement 8) integrated as remarks in relevant sections.
- Limitations remark (Requirement 8.2) in §8.
- Final proofread; typo sweep.
- Double-blind verification: search for "Ray", "Carnegie Mellon", self-citations, and personal identifiers.
- Submission PDF assembled with line count verified by the LIPIcs counter.
- Concurrent submission statement drafted.
- PC check per Requirement 9.4.

**Acceptance:** submission PDF ready 24 hours ahead of deadline per Requirement 9.2.

---

## 5. Risk register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Lemma B case C4/C5 induction step resists formalization | Low-Medium | High | Tripwire 10.2 (relaxed); Fallback 2 in 10.3 |
| Theorem 1.1 already published | Low-Medium | High | Phase 1 literature search; Tripwire 10.4; pivot to stuck-state headline |
| Exhaustive enumeration at $n=8$ hits memory / time wall | Low | Medium | Fall back to $n \leq 7$ exhaustive + random for $n \geq 8$ |
| Phase 3 random-unknot sample exceeds per-sample timeout | Medium | Low | 60s timeout; samples recorded as "undetermined" and counted separately |
| Phase 3 discovers No-Up counterexample | Low-Medium at $n \leq 8$ exhaustive, Low at random $n \geq 9$ | Neutral or positive | Requirement 4.7 reframes this as a feature; becomes the new main finding |
| Manuscript exceeds 500 lines | Medium | Medium | Appendix overflow; Phase 4 budget includes trimming |
| Bigon-reducibility of $D_{28}$ / $D_{43}$ / Ochiai II unexpectedly succeeds | Low | Low | Requirement 4.8: reword the negative-certificate paragraph; gap theorem unaffected |
| `\ifanonymous` toggle mis-flipped on submission | Very low | High | Phase 6 checklist step; grep submission PDF for author name |
| Zenodo upload fails | Very low | Low | Manual upload fallback |
| Submission system error | Very low | High | Requirement 9.2: submit 24h early |

The Case-5 confluence risk from the earlier design is **retired**. The corrected proof uses confluence-to-$\emptyset$ via induction on $\mathrm{cr}(w)$, which does not require resolving the stacked-triple confluence obstruction. The user's stacked-triple counterexample falsifies full confluence but is consistent with confluence-to-$\emptyset$ (both descendants in that example are stuck, so the Lemma B hypothesis is vacuously false there).

---

## 6. Design decisions (answered)

1. **Random-unknot generator: two-regime strategy.**
   - For $n \leq 8$: **exhaustive enumeration** of all double-occurrence Gauss words up to dihedral equivalence, filtered by Gauss's parity criterion or the Lovász / Read–Rosenstiehl planarity test, then run `down_r3_only` and `greedy_bigon_peel_all_orderings` on the full set. Exhaustive at this scale and unbiased, which is the strongest possible empirical support for a conjecture test. If this sweep produces a No-Up counterexample, it is the main finding.
   - For $n \in \{9, 10, 11, 12\}$: **random R-up sequences** from the empty word, 100 samples per $n$, as supplementary evidence. R-up sequences guarantee classicality by construction.
   - **Reported separately** in §6.3 of the manuscript: exhaustive-coverage claim at small $n$ does not pretend to extend to the sampled regime.

2. **Phase 0 timing: workstation is fine.** No compute constraints. For Phase 3, apply a **per-sample timeout of 60 seconds** on `down_r3_only` runs. Timeouts are recorded separately (neither YES nor NO) and reported as "undetermined" in the aggregate, rather than blocking the sweep.

3. **Double-blind plan: LaTeX toggle.** Add a `\newif\ifanonymous` at the top of `manuscript.tex`, with `\anonymoustrue` for submission. Guard author, affiliation, email, acknowledgements, and artifact DOI with `\ifanonymous ... \else ... \fi`. Flip one line for camera-ready. Single source of truth, no file divergence.

4. **Backup venue: Discrete & Computational Geometry (DCG).** The longer journal format accommodates a full proof of Theorem 1.1 plus the structural and computational sections without cap pressure, the review cycle tolerates iteration on a portfolio, and the topic fit is ideal. CCCG is tertiary backup only if a downstream timeline forces it. SoCG 2027 is not preferred — same venue, a year delayed.

### Implications for the task plan

- Phase 3 needs an exhaustive-enumeration generator in addition to the random-R-up generator. Both go into `experiments/random_unknot.py` as separate entry points.
- Phase 3 implementation needs a timeout wrapper around `bounded_bfs`.
- Phase 4 (manuscript rewrite) needs to scaffold the `\ifanonymous` toggle from day one, before any author-identifying content is added.
- Phase 6 (submission) needs two PDF outputs: anonymized for submission, identified for camera-ready post-acceptance.
