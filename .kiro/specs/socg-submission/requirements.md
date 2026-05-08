# Requirements: SoCG-Submission-Ready Paper on Virtual Unknotting Barriers

## Introduction

### Context and current state

The existing manuscript (`Paper/manuscript.tex`) presents an exact algorithm **BRS** (Bounded Reidemeister Search) that computes a *virtual minimax barrier* $\mathrm{Top}_v(D)$ for five benchmark hard unknot diagrams from Burton et al. (Goeritz, Culprit, $D_{28}$, $D_{43}$, Ochiai II). It reports $\mathrm{Top}_v(D) = \mathrm{cr}(D)$ for all five and claims a classical–virtual gap of at least 3 for $D_{28}$.

### Critical problems identified in the draft

1. The headline quantitative result $\mathrm{Top}_v(D) = \mathrm{cr}(D)$ is a consequence of the *trivial* lower bound $\mathrm{Top}_v(D) \geq \mathrm{cr}(D)$ combined with a reachability witness. The "lower bound" BFS at ceiling $N = \mathrm{cr}(D) - 1$ visits zero states — it is not a real lower bound argument, just a restatement of triviality.
2. The "virtual barrier" naming in the current draft is misleading. The permissive R2 move is a well-defined algebraic operation on Gauss words but is not a standard virtual Reidemeister move on virtual diagrams. The paper must rename or carefully scope this throughout.
3. The algorithm is bounded BFS with canonicalization — a standard technique. The FPT claim is only a conjecture (Conjecture 1). The novel algorithmic content is the greedy-peeling algorithm for bigon R1/R2, whose correctness requires a rigorous confluence proof (currently only sketched).
4. The stuck-state theorem (Theorem 5) has a hand-wavy proof of the nesting-leaf step.
5. No infinite-family result — the paper analyzes only five diagrams. (This is acceptable for a computational-witness framing but not as a standalone headline.)
6. LaTeX previously failed to load `booktabs` (now fixed); tables need a polish pass.
7. Paper is 12 pages — under the SoCG 500-line cap, but means there is room for more theorem content.
8. The general no-up reducibility question is open research (in the lineage of Burckel/Östlund/Hagge–Yazinski/Hui) and is not solvable on a submission timeline. The paper must position it as an open conjecture, not a target theorem.

### SoCG context

- **Venue:** International Symposium on Computational Geometry. 41st edition (2025) in Kanazawa; 42nd (2026) will be the target.
- **Format:** LIPIcs, 500-line limit (excluding front matter, references, and appendix), double-blind review.
- **Acceptance rate:** approximately 30–35% overall. Pure knot theory / computational topology subset typically has 3–5 accepted papers per year.
- **Recent comparable accepts:** *Hard Diagrams of Split Links* (Lunel, de Mesmay, Spreer, SoCG 2025); *A Practical Algorithm for Knot Factorisation* (He, Sedgwick, Spreer, SoCG 2025); *Small triangulations of 4-manifolds* (Burke, Burton, Spreer, SoCG 2025).
- **Common features of accepted knot papers:** a single headline theorem with a crisp complexity or structural statement; formal proof is the result, experiments are support; connection to at least one prior SoCG paper; either matching upper and lower bounds, a hardness reduction, or a polynomial algorithm for a previously exponential problem.

### Goal of this spec

Transform the current draft from an empirical case study into a theorem-driven paper whose headline result would be SoCG-acceptable on its own, with experiments, literature positioning, and polish serving as supporting armor. Target submission: **SoCG 2026** (deadline historically late November / early December).

### Honest framing

"Surefire accept" is not achievable — SoCG rejects strong papers routinely. The achievable target is **strongest defensible submission**, meaning a paper where:

- the main theorem would be publishable in *Discrete & Computational Geometry* or *J. ACM* on its own;
- no referee can identify a hand-wave in a proof;
- no competitive paper exists that does the same thing better;
- the computational contribution is non-trivial and reproducible;
- the writing clears SoCG's presentation standards without effort.

### Pivot: one theorem plus structural context, not a research lottery

An earlier draft of this spec framed the headline as a choice among four possible theorem forms (no-up theorem, family gap, FPT result, counterexample). This was rejected after analysis: each form is either open research (Form A is in the same lineage as Östlund's conjecture, disproved for the R1+R3 case by Hagge–Yazinski 2014 via a 16-crossing counterexample; the decorated R1↓+R2↓+R3 case is open), a major open problem (Form B), a multi-week side project (Form C), or an unschedulable discovery (Form D). None is an 11-day deliverable, and committing three weeks to the gamble would leave the manuscript, artifact, and polish phases unfunded.

The replacement framing is **one rigorous theorem, plus structural context, plus a computational witness, plus a well-positioned open question**:

- **Headline theorem:** Deciding bigon-monotone reducibility of Gauss words is in P. Concretely, the greedy algorithm that repeatedly applies any available bigon R1-down or bigon R2-down move is *confluent* (Church–Rosser): if any maximal greedy run empties the word, every maximal greedy run does. This is a new complexity result about a natural Reidemeister-sequence problem.
- **Structural context:** The stuck-state characterization (Theorem 5 in the current draft), tightened via a formal nesting-forest argument, explains *which* Gauss words admit a bigon-monotone unknotting and which have unavoidable fully-interleaved kernels.
- **Computational witness:** The five hard unknots (Goeritz, Culprit, $D_{28}$, $D_{43}$, Ochiai II) are *not* bigon-reducible — the polynomial-time algorithm decides "no" in every case — yet three of them ($D_{28}$, $D_{43}$, Ochiai II) admit a permissive-R2 monotone path, giving the gap-of-3 separation against Burton et al.'s classical lower bound for $D_{28}$.
- **Open question:** Whether every classical unknot Gauss word reduces under {R1↓, R2↓, R3} — the No-Up conjecture — is positioned as a real open problem in the lineage of Burckel 2007, Östlund 2001, Hagge–Yazinski 2014, and Hui et al. 2024, supported by experiments on benchmarks and random unknots. Not claimed as a theorem.

This is tighter than a pure portfolio (three-independent-contributions papers are borderline at SoCG unless unified by a strong spine) and avoids the research gamble. The principal risk is that Theorem 3 (greedy completeness) turns out harder to prove than expected; this risk is controlled by a 2-day tripwire in Phase 2.

---

## Requirements

### Requirement 1: Rigorous headline theorems and portfolio structure

**User story:** As a SoCG reviewer, I want the paper to state and prove three crisp, rigorous theorems, supported by a tight structural characterization and computational witnesses, so that I can recommend acceptance on the strength of complementary mathematical contributions rather than on empirical claims.

#### Acceptance criteria

1.1. WHEN the paper is read, THE paper SHALL state the following headline theorem in its abstract, introduction, and contributions list:

> **Theorem 1 (Greedy Completeness to $\emptyset$ for Bigon Monotone Reducibility).** Let $w$ be a decorated Gauss word. Consider the rewriting system $\mathcal{B}$ on chord diagrams with rules bigon R1-down and bigon R2-down. The greedy algorithm that repeatedly applies any available $\mathcal{B}$-rule terminates in at most $\mathrm{cr}(w)$ steps. If $w$ admits any $\mathcal{B}$-reduction to the empty word, then every maximal greedy run reaches the empty word. Consequently, the decision problem "does $w$ admit a $\mathcal{B}$-reduction to $\emptyset$?" is solvable in $O(n^3)$ time with an incremental move-set data structure, or $O(n^4)$ naive.

    This is *confluence-to-$\emptyset$*, strictly weaker than full confluence. The paper's headline SHALL NOT claim full confluence, which is false: a stacked-triple configuration can produce two maximal greedy runs terminating at distinct non-empty stuck states.

1.1bis. WHEN the paper is read, THE paper SHALL state the following certifying-decision theorem as a second headline result, immediately after Theorem 1:

> **Theorem 2 (Certifying bigon-barrier decision).** There is a deterministic algorithm that, given a signed Gauss word $w$ with $n$ chords, outputs exactly one of: (a) a bigon deletion sequence reducing $w$ to $\emptyset$; or (b) a nonempty stuck residual word $z$ together with the deletion sequence from $w$ to $z$. In case (a), $w$ is bigon-reducible; in case (b), $w$ is not bigon-reducible. Both certificates are verifiable in polynomial time. The algorithm runs in $O(n^3)$ time with incremental maintenance or $O(n^4)$ naive.

    THE paper SHALL NOT pitch Theorem 2 as deciding virtual unknotting; it decides the specific restricted combinatorial problem of bigon-monotone reducibility. This scope distinction SHALL be made explicit in the introduction and in the accompanying scope remark in `Paper/proofs/theorem_1_2_certifying.tex`.

1.2. WHEN Theorems 1 and 2 are proved, THE proofs SHALL be rigorous and self-contained, including explicit statements and proofs of their two supporting lemmas: a **Deletion-Monotonicity Lemma** (disjoint-chord bigon moves commute and neither invalidates the other) and a **Reduction-Preservation Lemma** (if $w$ admits a $\mathcal{B}$-reduction to $\emptyset$ and $\mu$ is any $\mathcal{B}$-move available at $w$, then $\mu(w)$ also admits a $\mathcal{B}$-reduction to $\emptyset$). The proof of Theorem 1 from these two lemmas SHALL proceed by induction on $\mathrm{cr}(w)$. The proof of Theorem 2 SHALL be the algorithmic form of the contrapositive of the Reduction-Preservation Lemma, using the same lemma machinery plus termination.

1.3. THE paper SHALL prove the tightened stuck-state characterization as a supporting structural theorem, using a formally defined nesting forest per Requirement 2. Both the **permissive** and **bigon** versions of the stuck-state theorem SHALL be stated separately, with correct proofs for each, and with a corollary giving the accurate interlacement-graph characterization of permissive-stuck words (not the incorrect "every component is a clique" form).

1.4. THE paper SHALL prove an exact separation result for $D_{28}$:

> **Theorem 3 (Classical–Virtual Gap for $D_{28}$).** $\mathrm{Top}_c(D_{28}) - \mathrm{Top}_v(D_{28}) = 3$, where $\mathrm{Top}_v$ is the permissive algebraic virtual barrier, the upper bound is witnessed by an explicit permissive-R2 monotone path, and the lower bound on $\mathrm{Top}_c$ is due to Burton et al. The gap is between the classical planar barrier and the algebraic permissive-virtual barrier, not between classical and any standard geometric virtual barrier.

1.4bis. THE paper SHALL prove the following proposition as a headline structural finding:

> **Proposition 4 (No-Up disproof at small crossing number).** The Goeritz (crossing number 11) and Culprit (crossing number 10) Gauss words are classical unknot Gauss words that admit no reduction to $\emptyset$ under the algebraic rewrite system $\{R1_{\text{down}}, R2_{\text{down}}^{\text{perm}}, R3\}$. Consequently, the No-Up conjecture for signed classical unknot Gauss words — the decorated analogue, in the lineage of Östlund 2001 and Burckel 2007, of Turaev's signless free-knot conjecture disproved by Manturov–Ilyutko–Kauffman 2009 — is false, with counterexamples at crossing number at most $11$.

    Proposition 4 is proved by exhaustive BFS over the restricted state space at ceiling $\mathrm{cr}(w)$; the state spaces are recorded in `outputs/phase0_down_r3_only.json` (1070 states for Goeritz, 269 for Culprit), both small enough for independent re-verification.

1.5. WHEN the paper frames its contribution, THE contribution SHALL be presented as six numbered items:
    - **(1)** Theorem 1: greedy completeness for bigon monotone reducibility, in $O(n^3)$ or $O(n^4)$ time;
    - **(2)** Theorem 2: the certifying-decision algorithmic form with matching positive/negative certificates, both polynomial-time verifiable;
    - **(3)** The stuck-state structural characterization via the nesting forest, separating bigon and permissive versions with a correct interlacement corollary;
    - **(4)** Theorem 3: the exact 3-crossing classical–virtual gap for $D_{28}$, with precise permissive-vs-bigon scope disambiguation;
    - **(5)** Proposition 4: the No-Up disproof at crossing number $\leq 11$, via the Goeritz and Culprit counterexamples;
    - **(6)** The computational study of five hard unknot benchmarks and random unknots up to $n = 12$ (Phase 3), serving as verification of Theorem 2's yes-certificate path on easy instances and as empirical context for Proposition 4.

1.6. THE paper SHALL NOT state or imply that $\mathrm{Top}_v(w) = \mathrm{cr}(w)$ holds in general for classical unknot Gauss words, nor that it has been proved for any diagram where the argument reduces to the trivial bound $\mathrm{Top}_v(w) \geq \mathrm{cr}(w)$.

1.7. THE paper SHALL position the No-Up conjecture's history — Östlund 2001 (disproved for unoriented plane curves under R1+R3 by Hagge–Yazinski 2014), Burckel 2007 (conjectured monotone-move completeness for a broader move set, unproven), Hui–Ibarra–Kauffman et al. 2025 (proves No-Up for ascending/descending special case), and Turaev's signless free-knot conjecture (disproved by Manturov–Ilyutko–Kauffman 2009) — as the setting within which Proposition 4 provides the first disproof for signed classical unknot Gauss words at small crossing number. Proposition 4 SHALL NOT be framed as subordinate motivation for Theorems 1 or 2; it is a co-headline structural finding.

1.8. WHEN the main theorems are stated, THE paper SHALL include one-paragraph informal explanations before each formal proof:
    - For Theorem 1: "bigon R1/R2 would be confluent if nesting chains could not stack; the Reduction-Preservation lemma shows that for any word admitting a reduction, any available first move preserves reducibility."
    - For Theorem 2: "the algorithmic form of Theorem 1 says that the greedy run, on failure, produces a stuck residual that certifies global non-reducibility — not merely a local failure. This is the essential algorithmic content of the Reduction-Preservation lemma."

1.9. IF the proof of any headline theorem encounters an unforeseen obstacle during revision, THEN the tripwire in 10.2 SHALL fire and the paper SHALL be re-scoped per 10.3 to a weaker but still-SoCG-plausible statement, or re-targeted to a different venue.

---

### Requirement 2: Correctness and precision of Theorem 5 (stuck state)

**User story:** As a SoCG reviewer examining the structural claims, I want the stuck-state characterization to have a rigorous proof using a formally defined nesting forest, so I am not left with unresolved "leaf of the nesting tree" hand-waves.

#### Acceptance criteria

2.1. WHEN the nesting structure is introduced, THE paper SHALL formally define the **nesting forest** $N(w)$ of a Gauss word: vertex set equal to the crossing-label set, with a directed edge $a \to b$ iff $a$ strictly nests $b$ and no third crossing lies strictly between them in the nesting hierarchy.

2.2. WHEN Theorem 5 is proved, THE proof SHALL show:
    - the leaves of $N(w)$ are exactly the directly-nested pairs to which R2-down applies (modulo the bigon/permissive distinction, explicit throughout);
    - $N(w)$ has at least one edge if and only if some interleavement component of $w$ is not fully interleaved;
    - these two facts combine to give the theorem.

2.3. THE proof SHALL explicitly handle the bigon R2 case versus the permissive R2 case, stating which version of Theorem 5 applies in each setting.

2.4. IF the permissive R2 version is used, THEN the proof SHALL cite or prove the algebraic validity of permissive R2-down as a Reidemeister move on Gauss words in the virtual category.

---

### Requirement 3: Tighten the complexity / algorithm section

**User story:** As a SoCG reviewer, I want the algorithm's claimed efficiency to be backed by a proven bound, not a conjecture, so that the computational contribution is tangible.

#### Acceptance criteria

3.1. WHEN BRS is analyzed, THE paper SHALL prove at least one of:
    - an FPT bound of the form $O(f(k) \cdot \mathrm{poly}(\mathrm{cr}(D)))$ where $k$ is a named parameter;
    - a polynomial bound on the state space for a named subclass of inputs;
    - a matching hardness result (e.g., computing $\mathrm{Top}_v$ is NP-hard or PSPACE-hard in general).

3.2. IF Conjecture 1 (state space bounded by an exponential in the ceiling alone) is retained, THEN it SHALL be restated as an explicit conjecture with a proof sketch of a weaker form, and SHALL NOT be cited as if it were a theorem.

3.3. WHEN the canonicalization step is described, THE paper SHALL state the canonicalization cost ($O(n^2)$ or similar) and justify the choice of canonical form (cyclic rotation + reversal + label relabeling).

3.4. THE algorithm section SHALL include pseudocode for BRS, formatted per LIPIcs conventions.

3.5. WHEN the `down_only` strategy is discussed, THE paper SHALL state explicitly that it is non-exhaustive and cannot prove unreachability, matching the implementation in `exact_barrier.py`.

---

### Requirement 4: Experimental evidence supporting the theorem and the open conjecture

**User story:** As a SoCG reviewer, I want the experiments to serve as supporting evidence for the theorem and as empirical support for a clearly-stated open conjecture, so that the paper's contribution is mathematical while the experiments add real content without overreaching.

#### Acceptance criteria

4.1. WHEN experimental results are presented, THE paper SHALL frame them as (a) **verification** of the main theorem on specific diagrams, (b) **a negative certificate** that none of the five hard benchmarks is bigon-reducible, and (c) **empirical support** for the No-Up conjecture.

4.2. THE paper SHALL include a new experiment (not present in the current draft) that runs BRS under the `{R1-down, R2-down, R3}-only` move restriction on each of the five benchmark diagrams, reporting whether each reduces to the empty word under this restricted move set. This tests the No-Up conjecture directly on the hardest known instances.

4.3. THE paper SHALL include a scaling experiment on random classical unknot Gauss words of crossing number up to 12, reporting (a) the fraction that reduce under bigon R1↓/R2↓ only, (b) the fraction that reduce under {R1↓, R2↓, R3}, and (c) for any instance that does *not* reduce under {R1↓, R2↓, R3}, its explicit Gauss word as a candidate counterexample to the No-Up conjecture.

4.4. WHEN experimental results are summarized, THE paper SHALL report wall-clock time, state-space size, edge count, and ceiling for each BRS run, using a single consistent table format across all diagrams.

4.5. THE paper SHALL clearly mark which claims are **proven** (from Theorems 1.1, 1.4, and the stuck-state theorem) and which are **empirical** (from specific BRS runs), using a consistent visual convention (e.g., theorem numbers vs. table entries).

4.6. THE experimental section SHALL NOT claim $\mathrm{Top}_v = \mathrm{cr}$ for specific diagrams on the basis of the trivial lower bound alone; it shall report "upper bound verified by exhaustive BFS at ceiling $N$" and distinguish this from the trivial lower bound.

4.7. IF the random-unknot scaling experiment (4.3) produces a classical unknot Gauss word that does *not* reduce under {R1↓, R2↓, R3}, THEN the paper SHALL report this instance prominently as disproving the No-Up conjecture and reframe the open-problem discussion accordingly. This is a positive outcome (a publishable counterexample), not a failure.

4.8. **Bigon-reducibility status for the five benchmarks is an empirical question to be resolved in Phase 0, not assumed.** Goeritz and Culprit are known to fail even permissive R2 reducibility and will therefore also fail bigon reducibility. $D_{28}$, $D_{43}$, and Ochiai II are confirmed permissive-reducible but their bigon-reducibility is not yet confirmed. IF any of these three turns out to be bigon-reducible, THEN the "none of five" negative-certificate claim SHALL be weakened to the correct count, and the relevant paragraph in the paper SHALL be revised; the gap-of-3 witness for $D_{28}$ is unaffected either way.

---

### Requirement 5: Literature positioning

**User story:** As a SoCG reviewer, I want the paper to situate its contribution within the virtual knot theory, circle-graph, and computational-complexity-of-knots literatures, so that I can judge whether the result is actually new.

#### Acceptance criteria

5.1. THE paper SHALL include a dedicated related-work section or long paragraph covering, at minimum:
    - classical Reidemeister-move complexity (Hass et al. 1999, Lackenby 2015, Coward–Lackenby);
    - virtual knot theory (Kauffman 1999, Manturov, GPV: Goussarov–Polyak–Viro);
    - Gauss-code realizability (Dehn, Lovász, Cairns–Elton, de Fraysseix);
    - circle graphs / interlacement graphs (Bouchet, Traldi, Zulli, Traldi);
    - Dynnikov's monotonic simplification for arc presentations;
    - hard-unknot constructions (Burton et al. 2021, Lunel–de Mesmay–Spreer 2025);
    - NP-hardness of unknotting moves (Lackenby, de Mesmay et al.);
    - **the monotone-move completeness lineage directly relevant to the No-Up conjecture: Burckel 2007, Östlund 2001, Hagge–Yazinski 2014 (disproving the R1+R3 case via a 16-crossing counterexample), and Hui et al. 2024 (ascending/descending special case).** This lineage SHALL be discussed in at least one paragraph, not just listed, since it is the closest published context for the paper's open conjecture.

5.2. WHEN citing each related work, THE paper SHALL state precisely how the present contribution differs or builds on it (one sentence per citation).

5.3. BEFORE finalizing the paper, THE author SHALL search for prior statements of Theorem 1.1 (greedy completeness for bigon monotone reducibility), the stuck-state characterization, and the No-Up conjecture in Manturov's *Knot Theory*, Kauffman's 1999 paper, the GPV 2000 paper, Östlund 2001, Traldi's circle-graph work, Burckel 2007, Hagge–Yazinski 2014, Hui et al. 2024, and the Bouchet/Traldi–Zulli delta-matroid literature. If any result is already known, the paper SHALL cite it and reframe the contribution accordingly.

5.3.1. **The Bouchet / Traldi / Traldi–Zulli delta-matroid and circle-graph literature SHALL receive dedicated attention**, not a skim. Greedy peeling of chord diagrams under a deletion-monotone predicate is exactly the kind of result that can appear in the delta-matroid exchange / matroid-style-confluence literature under different terminology. A specific search SHALL be conducted for (a) confluent rewriting on interlacement graphs, (b) matroid greedy results on circle graphs, (c) any published decision procedure for bigon reducibility or equivalent chord-diagram rewriting problems. IF such a result is found, THEN the tripwire in 10.4 fires.

5.3.2. **When discussing Hagge–Yazinski 2014 (Requirement 5.1) the paper SHALL state precisely that the counterexample disproves Östlund's conjecture for unoriented plane curves under R1 + R3 only, not for decorated Gauss codes under R1↓ + R2↓ + R3.** The decorated version of the No-Up conjecture is strictly weaker (the move set is larger) and remains open. Reviewers familiar with the lineage will check this distinction; the paper must not mischaracterize it.

5.4. THE paper SHALL cite at least one SoCG-published paper from the last five years in a non-trivial way (e.g., using its techniques, extending its results, or comparing against its bounds).

---

### Requirement 6: Manuscript presentation and LaTeX polish

**User story:** As a SoCG reviewer glancing at the first pages, I want the manuscript to meet LIPIcs typographic standards and be free of LaTeX errors, so that presentation does not prejudice my review.

#### Acceptance criteria

6.1. THE manuscript SHALL compile cleanly under `pdflatex manuscript.tex` with no undefined control sequences and no "! Error" or "! Undefined" lines in the log. This requires `\usepackage{booktabs}` (already added).

6.2. THE manuscript SHALL respect the 500-line SoCG cap on body content (excluding front matter, references, and any clearly-marked appendix), measured by the official line-counter LaTeX class.

6.3. THE manuscript SHALL use `socg-lipics-v2021.cls` (the SoCG-specific LIPIcs class) rather than the generic LIPIcs class.

6.4. THE manuscript SHALL be prepared in **double-blind** form: author names, affiliations, email addresses, and any self-identifying references removed or anonymized in the submission PDF, with a separate non-anonymized version for the camera-ready.

6.5. THE abstract SHALL be rewritten so the headline theorem appears in the first two sentences; the five benchmark diagrams SHALL appear only as supporting evidence, not as a headline.

6.6. THE contributions list SHALL be rewritten with the theorem as contribution 1, the certification/verification procedure as contribution 2, and the experimental/structural consequences as contributions 3+.

6.7. ALL tables SHALL use `booktabs` (\toprule, \midrule, \bottomrule), no vertical lines, and consistent column alignment.

6.8. ALL figures SHALL have vector-format sources (PDF) and self-contained captions explaining what the figure shows, what the axes mean, and what conclusion the reader should draw.

6.9. THE bibliography SHALL use the LIPIcs `plainurl` style and include DOI/URL for every citation.

6.10. THE manuscript SHALL include a reproducibility statement with a link to a public code/data archive (Zenodo or equivalent) with a DOI.

---

### Requirement 7: Reproducibility artifact

**User story:** As a SoCG reviewer or follow-up researcher, I want to reproduce the paper's computational results with one command, so that the experimental claims are independently verifiable.

#### Acceptance criteria

7.1. THE repository SHALL include a top-level `reproduce.py` or `Makefile` that runs every experiment in the paper and regenerates every figure and table, starting from a clean checkout.

7.2. THE repository SHALL include a locked environment specification (`environment.yml` with pinned versions) so that dependency drift does not break reproduction.

7.3. THE repository SHALL include unit tests covering the core Gauss-word operations (`get_valid_actions`, `apply_action`, `canonical`, bigon R2 detection) and the BRS search for the smallest benchmark (Culprit).

7.4. THE repository SHALL include a README describing:
    - what each directory contains;
    - how to reproduce the paper;
    - how long each experiment takes;
    - what outputs are generated.

7.5. THE repository SHALL be archived on Zenodo (or equivalent) with a DOI before submission, and the DOI cited in the manuscript.

7.6. THE repository SHALL NOT include derived files (PDFs, PNGs, pickles) in version control; these shall be generated by `reproduce.py`.

---

### Requirement 8: Defensibility against foreseeable reviewer objections

**User story:** As the author preparing for peer review, I want the paper to preempt the specific objections a hostile SoCG reviewer would raise, so that the paper survives contested review.

#### Acceptance criteria

8.1. THE paper SHALL explicitly address and preempt the following objections in dedicated paragraphs or remarks:

    - **"Greedy completeness for bigon moves is obvious / already known."** The paper must cite what *is* known (Burckel's conjecture, Östlund's conjecture, Hagge–Yazinski's counterexample, Hui et al.'s special case) and explain precisely what is new: a confluent rewrite-system theorem for the bigon fragment that has not appeared in the cited literature, delivered as a polynomial-time algorithm. If literature search finds the theorem already published, the contribution pivots to the stuck-state characterization and the gap-of-3 witness, and the manuscript is reframed within Phase 3.

    - **"The permissive R2 move is not a standard Reidemeister move; this is not a real gap."** The paper must define terms precisely (bigon R2 vs. permissive R2, algebraic vs. virtual-diagram moves), cite Kauffman / GPV to justify the algebraic move set, and honestly frame the separation as "algebraic virtual vs.\ classical planar" rather than over-claiming a geometric virtual gap.

    - **"The five hard unknots are a case study, not a theorem."** The paper answers: the case study is the *computational witness* for the gap-of-3 separation, not the headline. The headline is the polynomial-time algorithm.

    - **"BRS is just bounded BFS."** The paper must pitch BRS as a *tool in service of the theorem and the witness*, not as a novel algorithm in itself. The novelty claim for computation is the greedy-peeling algorithm (Theorem 1.1), which is not BFS.

    - **"Burton et al. already did this."** The paper must precisely state what Burton et al.\ proved ($m_c$ lower bounds for classical Reidemeister moves in $\mathbb{S}^2$) and what is new here: (a) the polynomial-time algorithm for bigon-monotone reducibility, (b) the structural characterization of stuck states, (c) the proven 3-crossing classical–virtual gap for $D_{28}$.

    - **"The No-Up conjecture is vaporware."** The paper must honestly present it as a conjecture with experimental support and a known literature lineage, not as a near-theorem. The paper's acceptance must not depend on it.

8.2. THE paper SHALL include a "Limitations" remark acknowledging at least two ways the result could be strengthened in future work, to signal mathematical maturity.

8.3. THE paper SHALL explicitly state which results depend on unproven conjectures and which do not, using a consistent convention.

---

### Requirement 9: Submission logistics and deadline compliance

**User story:** As the author, I want the paper submitted in compliance with the SoCG 2026 call for papers, so that it is not desk-rejected for administrative reasons.

#### Acceptance criteria

9.1. WHEN the SoCG 2026 call for papers is released (expected October 2025), THE author SHALL verify the current draft against the call's page limit, formatting, and topic-fit requirements, and update the spec if anything has changed.

9.2. THE submission SHALL be uploaded to EasyChair (or the specified submission system) at least 24 hours before the deadline, in anonymized PDF form, with any appendix clearly marked as "to be read at the reviewers' discretion."

9.3. THE submission SHALL include a concurrent submission statement per SoCG policy.

9.4. THE author SHALL identify at least two SoCG PC members whose expertise matches the paper's topics (computational topology / knot theory / combinatorial algorithms) and ensure the PC includes at least one such member before submitting.

9.5. IF the paper is rejected at SoCG 2026, THEN the author SHALL revise based on reviewer feedback and target the next appropriate venue (SoCG 2027, *Discrete & Computational Geometry*, or a specialty topology journal).

---

### Requirement 10: Prioritized execution plan

**User story:** As the author allocating time over the coming weeks, I want a priority order over the above requirements so that effort is spent on what moves the needle on acceptance, with explicit tripwires that fire early if a phase is at risk.

#### Acceptance criteria

10.1. THE execution order SHALL be:

    - **Phase 0 (day 0, 1 day):** Run the `{R1↓, R2↓, R3}-only` experiment (Requirement 4.2) on all five benchmarks and the bigon-only experiment on all five benchmarks. Record results. The benchmark outcomes are already partially known but need to be formally reproduced and logged; the bigon-only result is the empirical foundation of the negative certificate.

    - **Phase 1 (days 1–3):** Literature search per Requirement 5.3. Verify that Theorem 1.1 (greedy completeness for bigon R1/R2) has *not* been published. Read Burckel 2007, Östlund 2001, Hagge–Yazinski 2014, Hui et al. 2024, Traldi's circle-graph papers, Manturov. If Theorem 1.1 is already known, pivot immediately to the stuck-state theorem and gap-of-3 witness as the headline, with the algorithm demoted to a tool.

    - **Phase 2 (days 3–8, 5 days):** Prove Theorem 1.1 (greedy completeness), the stuck-state theorem with the nesting-forest formalism, and the exact-gap-3 theorem for $D_{28}$. Writing and verification.

    - **Phase 3 (days 8–14, 6 days):** Run the random-unknot scaling experiment (Requirement 4.3) in parallel with manuscript drafting. Tighten the algorithm/complexity section (Requirement 3). Complete the stuck-state proof if not finished in Phase 2.

    - **Phase 4 (days 14–24, 10 days):** Full manuscript rewrite per Requirement 6. New abstract, new contributions list, new related-work section (Requirement 5). Double-blind preparation.

    - **Phase 5 (days 24–30, 6 days):** Build the reproducibility artifact (Requirement 7), archive on Zenodo, integrate the DOI.

    - **Phase 6 (days 30–38, 8 days):** Polish, proofread, preempt reviewer objections (Requirement 8), double-blind check, internal read-throughs, submit per Requirement 9.

    This allocates 38 days total. If the SoCG 2026 deadline is shorter than 38 days out, phases SHALL be compressed proportionally, with compression taken first from Phase 6 (polish) and last from Phases 1 (literature) and 2 (theorems).

10.2. **Tripwire at Phase 2 day 2 (overall day 5):** IF the induction step in Lemma B (Reduction-Preservation under Single Moves), specifically cases C4/C5 where two bigon R2-down moves share a middle chord in a stacked configuration, has encountered a concrete unresolved obstacle after two full days of focused work, THEN the author SHALL immediately stop proof work and invoke the fallback in 10.3. The trigger is a *specific* obstacle (e.g., a stacked configuration where the induction hypothesis cannot be instantiated on $\mu_1(w)$ because $\mu(w)$ is not reachable from it by any bounded bigon sequence), not generalized difficulty. The earlier Case-5 confluence tripwire is retired: the corrected proof (design §1.2) uses confluence-to-$\emptyset$ rather than full confluence, so the stacked-triple counterexample is vacuous rather than fatal.

10.3. **Fallback cascade.** IF the tripwire fires, THEN the paper SHALL be re-scoped in the following order, stopping at the first option that is within budget and still SoCG-plausible:
    - **Fallback 1:** Demote Theorem 1.1 to a partial result (e.g., greedy completeness for the sub-fragment with only R1-down, or for chord diagrams of bounded interleavement). Keep the stuck-state theorem and the gap-of-3 witness as the headline pair.
    - **Fallback 2:** Drop Theorem 1.1 entirely. Make the headline the stuck-state characterization (formalized via the nesting forest) plus the exact gap-of-3 witness for $D_{28}$. Acknowledge that this is a structural-computational paper rather than an algorithm paper.
    - **Fallback 3:** Re-target submission. If even Fallback 2 does not produce a paper that meets Requirement 1, the submission SHALL be redirected from SoCG 2026 to *Discrete & Computational Geometry*, CCCG, or another venue where the portfolio framing is more accepted, and the SoCG submission for this work SHALL be deferred to 2027.

10.4. **Tripwire at Phase 1 day 2 (overall day 3):** IF the literature search finds that Theorem 1.1 is already published, THEN Phase 2 SHALL immediately pivot to Fallback 2 (no proof work on the algorithm; headline becomes stuck-state + gap-of-3 witness) and the saved Phase 2 time SHALL be reallocated to Phase 3 (random-unknot experiment, additional structural results) and Phase 4 (manuscript).

10.5. AT the end of each phase, THE author SHALL update this spec with a brief progress note and adjust subsequent phases if blockers appear.

10.6. IF at any point the paper's headline theorem would require an unproven conjecture to hold, THEN the paper SHALL NOT be submitted in that form. The fallback cascade in 10.3 applies.
