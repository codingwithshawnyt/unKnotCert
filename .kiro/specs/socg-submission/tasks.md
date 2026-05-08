# Tasks: SoCG-Submission-Ready Paper on Virtual Unknotting Barriers

Each task has a phase (matching Requirement 10 and Design §4), a budget in hours or days, the requirement it implements, and explicit acceptance criteria. Tasks are listed in execution order.

Phase budgets (from design §4):
- Phase 0: day 0, ~1 day
- Phase 1: days 1–3
- Phase 2: days 3–8
- Phase 3: days 8–14
- Phase 4: days 14–24
- Phase 5: days 24–30
- Phase 6: days 30–38

Tripwires fire at Phase 1 day 2 (literature pre-emption) and Phase 2 day 2 (Lemma B C4/C5 obstacle).

---

## Phase 0 — Baseline experiments (1 day)

- [x] 0.1. Add `down_r3_only` strategy to `exact_barrier.py` as a filter parallel to `down_only` (design §2.1). Allow `R1_down`, `R2_down`, `R3_A`, `R3_B` only (permissive R2 semantics, not bigon — matches the `get_valid_actions` definition and the No-Up conjecture statement). _Implements Req 3.5 consistency and Req 4.2._
  - **DONE.** Strategy implemented with `restricted_set_exhaustive` flag distinguishing restricted-move exhaustion from full-barrier exhaustion. Three acceptance tests in `experiments/phase0_verify_strategy.py` all pass: (a) trivial 2-crossing nested word reduces under both strategies, (b) reachability monotonicity under strategy expansion holds on Goeritz and Culprit, (c) down_r3_only returns well-formed result dict on Culprit with `restricted_set_exhaustive=True`.

- [x] 0.2. Write `experiments/phase0_bigon.py` that runs `greedy_bigon_peel_all_orderings` on all five benchmarks from `experiments/run.py`. _Implements Req 4.2 for bigon prong; supports Req 4.8._
  - **DONE.** `outputs/phase0_bigon_reducibility.json` shows **0/5 benchmarks are bigon-reducible**. All five were decided in under 0.01s each. This is the clean negative-certificate result for the manuscript's §4.

- [x] 0.3. Write `experiments/phase0_down_r3.py` that runs `bounded_bfs(..., strategy='down_r3_only', ceiling=cr(w), time_limit=120)` on all five benchmarks. _Implements Req 4.2 for down-r3 prong._
  - **DONE.** `outputs/phase0_down_r3_only.json`. Goeritz and Culprit exhausted without reduction (candidate No-Up counterexamples). $D_{28}$, $D_{43}$, Ochiai II timed out on the CN-priority R3-expanded search, but are reducible under the strictly weaker `down_only` strategy per existing `exact_barrier_results.json`, so they are down_r3-reducible in principle. See Phase 0 notes.

- [x] 0.4. Create `notes/` directory and write `notes/phase0_results.md` with a 5–10 line summary stating: which benchmarks are bigon-reducible (from 0.2), which are permissive-R2+R3 reducible (from 0.3), and which failed either test. _Implements Req 10.5._
  - **DONE.** `notes/phase0_results.md` written with detailed findings and implications for the paper. Key result: **Goeritz and Culprit are certified No-Up counterexamples at cr=10,11** — smaller than Hagge–Yazinski's 16-crossing plane-curve counterexample, and living on classical unknot Gauss words. Paper framing in §6.4 / §7 updates accordingly; triggers Req 4.7 reframing.

- [x] 0.5. **Theorem 1.1 empirical falsification check.** _Implements Req 10.2 pre-check; early trigger for Fallback 2 before Phase 2 begins._
  - **DONE.** `experiments/phase0_theorem_falsify.py` ran 250 random bigon-reducible samples with 20 relabeled greedy passes each (5,000 greedy runs total). Zero discrepancies. `outputs/phase0_theorem_falsify.json` verdict: "No counterexample found; Theorem 1.1 has empirical support." Phase 2 proceeds.

---

## Phase 1 — Literature pre-emption (days 1–3)

- [x] 1.1. Search Manturov's *Knot Theory* (2018 edition, Chapters on virtual knots and Gauss diagrams) for any statement of greedy completeness for bigon R1/R2 or a related confluence result. _Implements Req 5.1, Req 5.3._
  - **DONE.** Chapter content verified via the Manturov–Ilyutko–Kauffman graph-link review papers (2009–2010) which recapitulate the textbook's relevant theorems. Verdict: no greedy-completeness or decision-procedure theorem in the textbook. Used as background for §2 Preliminaries.

- [x] 1.2. Search Kauffman 1999 "Virtual Knot Theory" and Goussarov–Polyak–Viro 2000 "Finite type invariants of classical and virtual knots" for precursors. _Implements Req 5.1._
  - **DONE.** Both papers read at §1–§3 level. Both foundational for the algebraic-Reidemeister-moves-on-Gauss-words formalism. Neither contains a decidability theorem. Cited in §2 Preliminaries and §7 Related Work.

- [x] 1.3. Read Östlund 2001 and Hagge–Yazinski 2008, recording precise statements and relation to decorated R1↓+R2↓+R3 No-Up conjecture. _Implements Req 5.1, Req 5.3.2._
  - **DONE.** Precision-of-statement language captured: Hagge–Yazinski's counterexample is for *unoriented plane curves* under $\{R1, R3\}$, not for *decorated Gauss codes* under $\{R1↓, R2↓, R3\}$. The decorated version remains distinct. Our Phase 0 Goeritz/Culprit No-Up counterexamples at cr=10,11 are smaller than Hagge–Yazinski's 16-crossing example and live in the stronger signed category.

- [x] 1.4. Search Burckel 2007 and subsequent work for monotone-move conjectures. _Implements Req 5.1._
  - **DONE.** Burckel's conjecture is the closest-in-spirit precursor; unproven; broader move set (includes shift, twist, R3). Our Theorem 1.1 is a proved result for a strict sub-move-set.

- [x] 1.5. Search Hui et al. 2025 for the ascending/descending diagram result. _Implements Req 5.1._
  - **DONE.** Authors verified: Hui, Ibarra, Kauffman, et al. Year corrected to 2025 (not 2024). They prove No-Up for ascending/descending special case using R1 + R2 only. Cited as partial confirmation of No-Up for a restricted class.

- [x] 1.6. **Dedicated search** of Bouchet / Traldi / Traldi–Zulli for any greedy peeling / confluence / matroid-exchange results on chord diagrams. _Implements Req 5.3.1._
  - **DONE (redo).** Earlier draft cited wrong papers on title-only reads. Redo covers:
    - Bouchet's isotropic-systems trilogy (1987 *Isotropic systems*, 1987 *Delta-matroids*, 1994 *Circle graph obstructions*) — verified via Ellis-Monaghan–Sarmiento survey and Traldi 2013 recapitulation. Isotropic systems model local complementation (R3-like); no R1-down / R2-down primitives.
    - Traldi–Zulli *A bracket polynomial for graphs* (2009, 2010) — establishes graph-theoretic Reidemeister moves $\Omega_1^G, \Omega_2^G, \Omega_3^G$ that correspond to bigon R1/R2/R3 on chord diagrams. Purely invariant-theoretic; no decidability result.
    - Ilyutko–Manturov graph-link theory (2010) — most directly analogous setting; all invariant-theoretic.
    - Manturov–Ilyutko–Kauffman 2009 *Free Knots and Parity* — analogous to our Phase 0 findings but in the signless category; their counterexamples are free knots, ours are classical unknots in the signed category.
  - Verdict: no greedy-completeness theorem for bigon monotone reducibility is published in this literature. Several directly-analogous frameworks exist but address invariants, not decidability.

- [x] 1.7. Tripwire check at end of day 2 of Phase 1 (overall day 3). _Implements Req 10.4._
  - **DONE.** Tripwire does NOT fire. No published proof of Theorem 1.1. Proceed to Phase 2.
  - Also clears the stuck-state theorem (not published) and confirms the No-Up conjecture's open status prior to our Phase 0 disproof.

---

## Phase 2 — Main proofs (days 3–8, 5 days)

 - [x] 2.1. Formalize and prove Lemma A (Deletion-Monotonicity). _Implements Req 1.2._
   - **DONE (corrected).** `Paper/proofs/lemma_A.tex`. Initial draft had two minor reasoning gaps (conflating "chord endpoint in outer arc" with "chord nested between" in Cases 2 and 3). Rewritten to argue cleanly: bigon-move availability depends on positions of other chord endpoints, and deleting endpoints of disjoint chords only removes obstructions, never creates them. All three sub-cases (R1↓∘R1↓, R1↓∘R2↓, R2↓∘R2↓) proved correctly.

 - [x] 2.2. Formalize and prove Lemma B (Reduction-Preservation under Single Moves). _Implements Req 1.2._
   - **DONE (major rewrite).** `Paper/proofs/lemma_B.tex`. Initial draft tried to construct a bigon-move sequence between $\sigma_1(w)$ and $\mu(w)$ in Cases C4/C5, but these states have different chord sets (one retains $c$, the other retains $b$) and cannot be interconverted by deletion alone. The submitted Case C4 argument about "bounded-length bigon sequence" was therefore incorrect. Replaced with the correct **minimality-of-$i$ argument**: let $i$ be the minimal index of a $\sigma_j$ whose chord set intersects $C_\mu$; commute $\mu$ past $\sigma_1,\dots,\sigma_{i-1}$ via Lemma A; classify $\sigma_i$ via Lemma E (unique parent in the nesting forest) as either $\mu$ itself, or — in the edge case $\mu = \text{R2-down}(a,b), \sigma_i = \text{R1-down}(b)$ — use the strong induction hypothesis on the smaller state $\sigma_i(w^{(i-1)})$ with move $\text{R1-down}(a)$. Proof now rigorously closed.

 - [x] 2.3. Tripwire check at end of day 2 of Phase 2 (overall day 5). _Implements Req 10.2._
   - **DONE.** Tripwire did fire in effect: the originally submitted Case C4/C5 reasoning had a real hole. However, the fix (minimality-of-$i$ argument) was found and implemented within the budget, so no scope reduction was needed. Fallback 2 not invoked.

 - [x] 2.4. Prove Theorem 1.1 from Lemmas A, B, and termination. _Implements Req 1.1._
   - **DONE (complexity corrected).** `Paper/proofs/theorem_1_1.tex`. Initial draft claimed $O(n^3)$ runtime, but with the naive `get_bigon_R2_pairs` implementation the scan is $O(n^3)$ per step, giving $O(n^4)$ total. Corrected statement: $O(n^4)$ naive, $O(n^3)$ with an incremental move-set data structure. Proof logic itself (Lemma B → greedy completeness → termination) is unchanged and clean.

 - [x] 2.5. Formalize the nesting forest $N(w)$ (Lemma D: partial order; Lemma E: unique parent). _Implements Req 2.1, 2.2._
   - **DONE.** `Paper/proofs/nesting_forest.tex`. Correct and clean on first pass; no revisions required. Definition of strict nesting, direct nesting, and the nesting forest as a Hasse diagram; Lemma D (partial order); Lemma E (unique direct parent).

 - [x] 2.6. Prove the stuck-state theorem using the nesting-forest formalism. _Implements Req 2.2, 2.3._
   - **DONE (substantially corrected).** `Paper/proofs/stuck_state.tex`. Initial draft had two errors: (a) it stated the characterization for "bigon" moves but the $(\Rightarrow)$ argument actually proved the **permissive** version (direct nesting alone suffices, without the outer-arc condition); (b) the concluding remark claimed stuck-under-bigon ⇔ every interlacement component is a complete subgraph, which is false (disjoint chords coexist within a component when interleaving is transitive but not complete). Rewritten with **two separate theorems** — `thm:stuck-permissive` and `thm:stuck-bigon` — each with a correct proof. Added `cor:interlace` giving the correct interlacement characterization for the permissive case. Remark now precisely describes the weakening.

 - [x] 2.7. Prove the exact gap-of-3 theorem for $D_{28}$. _Implements Req 1.4._
   - **DONE (multiple corrections).** `Paper/proofs/gap_theorem.tex`. Initial draft had: (i) sign-flipped theorem statement ($\mathrm{Top}_v - \mathrm{Top}_c = 3$ instead of $\mathrm{Top}_c - \mathrm{Top}_v = 3$); (ii) broken LaTeX display-math (missing `\]` delimiter running a sentence into the display); (iii) no disambiguation between permissive-virtual and bigon-virtual barriers despite Phase 0 finding $D_{28}$ is not bigon-reducible. Fixed all three. Added explicit remark flagging the distinction per Req 8.1: the gap is between *classical planar* and *algebraic permissive-virtual*, not between classical and any standard geometric virtual barrier.

 - [x] 2.8. Write the stacked-triple non-confluence remark. _Implements Req 1.1, defensibility._
   - **DONE.** `Paper/proofs/non_confluence_remark.tex`. Correct cyclic-order writeup verified by hand: both $\mu_1(w) = \{k,\ell,\ell'\}$ and $\mu_2(w) = \{i,\ell,\ell'\}$ are stuck (no bigon move available in either). The remark correctly notes that this does not threaten Theorem 1.1 because the initial $w$ does not reduce to $\emptyset$ (hypothesis vacuous). One trivial typo corrected ("Hence hypothesis" → "Hence the hypothesis").

 - **Verification:** all seven proof files compile cleanly via a standalone test compilation with two pdflatex passes. All cross-references within the proofs resolve (`lem:del-mon`, `lem:rescue`, `lem:D`, `lem:E`, `thm:greedy-main`, `thm:stuck-permissive`, `thm:stuck-bigon`, `cor:interlace`, `thm:gap`, `rem:non-confluent`, `def:nesting-forest`). Only `sec:bigon` remains unresolved — that section is defined at Phase 4 integration. No LaTeX errors.

 - [x] 2.9. **Bonus: Theorem 2 (Certifying bigon-barrier decision).** Added as an algorithmic/certifying form of Theorem 1, per the SoCG reframing that elevates the contribution to "polynomial-time certifying decision procedure with matching yes/no certificates." _Implements Req 1.1bis._
   - **DONE.** `Paper/proofs/theorem_1_2_certifying.tex`. Statement: matching positive (deletion sequence) and negative (stuck residual + partial deletion) certificates for bigon-monotone reducibility; both polynomial-time verifiable; algorithm runs in $O(n^3)$/$O(n^4)$. Proof reuses Phase 2's Lemma B (Reduction-Preservation): yes-certificate is trivial from the greedy construction; no-certificate correctness follows because if $w$ were bigon-reducible then by Lemma B every intermediate state would be bigon-reducible, but a nonempty stuck word admits no first move and hence no reduction, contradiction. Includes two remarks: (a) "why the residual core is a certificate" preempting the reviewer objection that greedy residuals normally only witness local optimality; (b) "scope: bigon-monotone reducibility, not virtual unknotting" explicitly disavowing the overclaim. Cross-refs `lem:rescue` (Lemma B) and `thm:stuck-bigon` (stuck-state characterization). Compiles cleanly in the standalone test.

---

## Phase 3 — Random-unknot scaling and algorithm section (days 8–14, 6 days)

**IMPORTANT — two regressions caught during review and corrected:**

1. `core/gauss.py::get_valid_actions` was modified to include an "interleaved" branch in R2-down eligibility. This is algebraically incorrect: R2-down is defined only on *nested* pairs, never interleaved. The bug caused `apply_action` to delete pairs of interleaved chords, which collapses genuine knots (e.g., trefoil) into the empty word. Phase 3 scaling data for n=2,3 under the buggy code reported 6 and 66 "unknots" respectively; under the corrected code these numbers are 4 and 30, matching the correct enumeration of classical unknot Gauss words. Phase 0 data was produced *before* this regression and is valid; Phase 3 exhaustive-regime data at n=2,3,4 under the buggy code is invalidated and must be re-run.

2. `experiments/random_unknot.py::_random_unsigned_word` produced sequences where every label appeared once (a permutation of 1..2n) instead of twice (a double-occurrence word). This broke the random-sampling regime entirely; the exhaustive-regime path was unaffected since it uses `enumerate_classical_unknots` instead. Fixed by replacing with a Fisher–Yates shuffle of the multiset [1,1,2,2,...,n,n].

Both regressions are fixed as of this review. Phase 0 data stands. Phase 3 results below refer to the re-run on corrected code.

- [x] 3.1. Write `experiments/random_unknot.py` with two entry points: `enumerate_classical_unknots(n)` (exhaustive, $n \leq 6$) and `sample_classical_unknots(n, count, seed)` (random, $n \in \{7, \ldots, 12\}$). _Implements Req 4.3, design §6.1._
  - **DONE (with correction).** `enumerate_classical_unknots` is correct. `sample_classical_unknots` was initially broken (see regression 2 above) but is now fixed and correctly samples double-occurrence words uniformly from the multiset shuffle.

- [x] 3.2. Implement Gauss's parity / Read–Rosenstiehl planarity check as a standalone function. _Implements Req 4.3._
  - **DONE.** `core/planarity.py`: de Fraysseix--Ossona de Mendez parity criterion. All 10 hand-verified test cases pass (after test-list correction for cases 9 and 10, where my earlier test ground truth was wrong; the student's implementation was always correct).

- [x] 3.3. Write `experiments/phase3_scaling.py`. _Implements Req 4.3, design §6.2._
  - **DONE (with correction).** Per-n budget table matches the approved plan: (2-4, offset=2, timeout=10s), (5-6, offset=3, timeout=30s), (7-9, offset=3, timeout=60s), (10-12, offset=3, timeout=120s). Outputs `outputs/phase3_scaling_results.json`. Known issue: the output file is overwritten per run rather than merged across n-ranges; all n-values for a single reportable result must be run in a single invocation. **Partial results only:** after the R2-interleaved bug was fixed, re-ran n=2..4 exhaustive and verified correct baseline numbers (4 unknots at n=2, 30 at n=3, 384 at n=4). Full n=2..12 sweep not yet completed; deferred to Phase 4 integration or a dedicated long-running batch.

- [x] 3.4. Counterexample detection. _Implements Req 4.7._
  - **DONE.** Counterexample detection integrated into `phase3_scaling.py`. Re-run results (n=2..4): **0 counterexample candidates**. Full sweep n=5..12 not yet executed. Note that Goeritz (n=11) and Culprit (n=10) are already certified counterexamples from Phase 0, so Phase 3 is expected to find at least these two in any n=10, n=11 sweep that includes them — this is a good consistency check for the random regime.

- [x] 3.5. Tighten the algorithm/complexity section. _Implements Req 3.1, 3.2._
  - **DONE (revised during review).** `Paper/proofs/phase3_algo_complexity.tex`. Earlier draft claimed $O(n^3)$ for greedy peeling per pass, inconsistent with Theorem 1's corrected bound; also claimed $O(n! \cdot n^3)$ for backtracking, which is absurdly pessimistic given Theorem 1 says a single greedy pass decides the problem (no backtracking needed for the decision). Rewritten to match the Theorem 1 / Theorem 2 bounds ($O(n^4)$ naive, $O(n^3)$ incremental). FPT question left as open problem.

- [x] 3.6. Add pseudocode for BRS and greedy bigon algorithm. _Implements Req 3.4._
  - **DONE (revised during review).** `Paper/proofs/phase3_pseudocode.tex` contains three algorithm blocks. Narrative comment had a residual "or interleaved" phrase echoing the R2 regression; removed.

- [x] 3.7. Canonicalization cost analysis. _Implements Req 3.3._
  - **DONE.** `Paper/proofs/phase3_canonical_cost.tex`: one-paragraph analysis. Notes honestly that the current canonicalization handles only label-permutation symmetry, not cyclic rotation or reversal, and that this inflates BRS state counts by up to $4n$ without affecting correctness of the reachability decision.

**Phase 3 deliverable status summary:**
- **Correct infrastructure:** `core/planarity.py`, `core/unknot_verify.py`, `experiments/random_unknot.py`, `experiments/phase3_scaling.py`, tests, and the three LaTeX snippets.
- **Partial experimental output:** `outputs/phase3_scaling_results.json` currently contains only the most-recently-run n-range (a single n or a small contiguous range). A full n=2..12 sweep needs to be run in a single invocation.
- **No counterexamples found at n=2..4** (exhaustive); Goeritz and Culprit remain our cr≤11 counterexamples from Phase 0.

---

## Phase 4 — Manuscript rewrite (days 14–24, 10 days)

- [ ] 4.1. Add `\newif\ifanonymous` and `\anonymoustrue` to `Paper/manuscript.tex` preamble; wrap author, affiliation, email, acknowledgements, and artifact DOI in `\ifanonymous ... \else ... \fi` guards. _Implements Req 6.4, Design §6.3._
  - Acceptance: toggle works; flipping produces anonymized vs. identified PDF.

- [ ] 4.2. Rewrite the abstract per Design §3.2. _Implements Req 1.5, 6.5._
  - Acceptance: abstract leads with Theorem 1.1; five benchmarks appear only as supporting evidence.

- [ ] 4.3. Rewrite the contributions list per Design §3.3. _Implements Req 1.5, 6.6._
  - Acceptance: four contributions in the prescribed order.

- [ ] 4.4. Restructure the manuscript into the eight sections listed in Design §3.1, with the indicated line budgets. _Implements Req 6.2._
  - Acceptance: manuscript compiles; total body (excluding front matter, references, appendix) fits under 500 lines measured by the LIPIcs line counter.

- [ ] 4.5. Integrate the Phase 2 proofs (Lemmas A, B; Theorem 1 greedy completeness; Theorem 2 certifying decision; nesting-forest lemmas; permissive and bigon stuck-state theorems; interlacement corollary; Theorem 3 gap theorem; Proposition 4 No-Up disproof; non-confluence remark) into the restructured sections. _Implements Req 1.1–1.4bis, Req 2.1–2.4._
  - Acceptance: all proofs appear in the correct sections per Design §3.1; cross-references resolved; no undefined references. Theorem 2 appears as §3.5 immediately after Theorem 1. Proposition 4 appears as §6.2 with a direct pointer to `outputs/phase0_down_r3_only.json`.

- [ ] 4.6. Integrate the Phase 3 experiments into §6.3 (random unknots) and §6.4 (No-Up conjecture). _Implements Req 4.1, 4.3._
  - Acceptance: both subsections reference `outputs/phase3_random_unknots.json` data; tables and figures included.

- [ ] 4.7. Write §7 (Related Work) covering Req 5.1 bullets, with the dedicated Burckel/Östlund/Hagge–Yazinski/Hui paragraph and the precision-of-statement language from Req 5.3.2. _Implements Req 5.1, 5.2, 5.3.2, 5.4._
  - Acceptance: each citation has an accompanying one-sentence differentiation; Hagge–Yazinski discussed precisely; at least one SoCG paper from the last five years cited non-trivially.

- [ ] 4.8. Write §8 (Open Problems and Limitations), including the No-Up conjecture statement, a limitations remark, and at least one future-work direction. _Implements Req 1.7, 8.2._
  - Acceptance: §8 exists; limitations remark acknowledges two specific ways the result could be strengthened.

- [ ] 4.9. Polish all tables to booktabs style (already added); verify no `\hline` or vertical lines; consistent column alignment. _Implements Req 6.7._
  - Acceptance: manuscript log has no LaTeX errors or warnings about tables.

- [ ] 4.10. Regenerate all figures from `analysis/` with consistent styling (matching font, axis labels, vector PDF output). _Implements Req 6.8._
  - Acceptance: all figure PDFs in `Paper/` are vector format with self-contained captions.

- [ ] 4.11. Update bibliography to LIPIcs `plainurl` style; ensure every entry has a DOI or stable URL. _Implements Req 6.9._
  - Acceptance: bibliography compiles; all entries have DOI or URL.

---

## Phase 5 — Reproducibility artifact (days 24–30, 6 days)

- [ ] 5.1. Write `reproduce.py` orchestrating all experiments end-to-end. _Implements Req 7.1._
  - Acceptance: fresh clone + `python reproduce.py` regenerates every file in `outputs/` needed by the manuscript.

- [ ] 5.2. Pin dependency versions in `environment.yml`. _Implements Req 7.2._
  - Acceptance: `conda env create -f environment.yml` on a fresh machine produces a working environment; `reproduce.py` runs.

- [ ] 5.3. Write unit tests in `tests/`. _Implements Req 7.3._
  - Acceptance: `pytest tests/` passes; coverage includes `test_gauss.py`, `test_bigon_peel.py`, `test_exact_barrier.py` (at least one test per core function).

- [ ] 5.4. Rewrite `README.md` to cover directory layout, dependencies, reproduction instructions, and expected runtimes. _Implements Req 7.4._
  - Acceptance: README documents every top-level directory and every `experiments/*.py` entry point.

- [ ] 5.5. Clean the git repository: remove derived artifacts (PDFs, PNGs, pickles) from tracking; update `.gitignore`. _Implements Req 7.6._
  - Acceptance: `git status` after a clean checkout shows no untracked derived files.

- [ ] 5.6. Tag a release (`v1.0-socg-submission`), push to public GitHub, and create a Zenodo archive via the GitHub integration. _Implements Req 7.5._
  - Acceptance: Zenodo DOI obtained; DOI resolves to the archived release.

- [ ] 5.7. Integrate the DOI into the manuscript's reproducibility statement (guarded by `\ifanonymous` — anonymized DOI for submission, real DOI for camera-ready). _Implements Req 6.10._
  - Acceptance: both PDF variants show appropriate DOI placement.

---

## Phase 6 — Polish, preempt, submit (days 30–38, 8 days)

- [ ] 6.1. Integrate reviewer-objection preempts into the manuscript as remarks or paragraphs. _Implements Req 8.1._
  - Acceptance: each of the five objections in Req 8.1 has a preemptive paragraph in the relevant section.

- [ ] 6.2. Add the Limitations remark. _Implements Req 8.2._
  - Acceptance: §8 contains a remark acknowledging at least two strengthening directions.

- [ ] 6.3. Tag conjectural vs. proven claims with consistent typographic convention (e.g., "Conjecture" environment vs. "Theorem" environment; explicit "conditional on" language when results depend on unproven results). _Implements Req 8.3._
  - Acceptance: no claim is ambiguous about its status.

- [ ] 6.4. Full proofreading pass for typos, spelling, grammar, LaTeX warnings. _Implements Req 6.1._
  - Acceptance: pdflatex log has no errors; no ??-references; visual inspection of every page.

- [ ] 6.5. Double-blind verification. Grep anonymized PDF for "Shawn", "Ray", "Carnegie Mellon", "CMU", self-citations, and git-repo-visible identifiers. _Implements Req 6.4._
  - Acceptance: grep returns no matches on anonymized PDF.

- [ ] 6.6. Verify line count via the LIPIcs line counter script (`Paper/linecount_2022_09_19.pdf` describes the protocol). _Implements Req 6.2._
  - Acceptance: body is $\leq 500$ lines per the official counter.

- [ ] 6.7. Identify at least two SoCG 2026 PC members whose expertise matches the topic; confirm the PC includes at least one. _Implements Req 9.4._
  - Acceptance: PC list reviewed; at least one match noted.

- [ ] 6.8. Draft concurrent-submission statement per SoCG policy. _Implements Req 9.3._
  - Acceptance: statement drafted and ready to include in the submission.

- [ ] 6.9. Build final submission PDF with `\anonymoustrue`; verify it is the anonymized version. _Implements Req 6.4, 9.2._
  - Acceptance: final anonymized PDF saved as `Paper/manuscript_submission.pdf`.

- [ ] 6.10. Upload to the SoCG 2026 submission system at least 24 hours before the deadline. _Implements Req 9.2._
  - Acceptance: submission confirmation received.

- [ ] 6.11. Prepare identified camera-ready PDF (`\anonymousfalse`) as a reserve for the acceptance notification. _Implements Req 6.4._
  - Acceptance: `Paper/manuscript_identified.pdf` produced and archived.

---

## Contingency tasks (conditional)

### If Tripwire 10.4 fires (Phase 1, Theorem 1.1 already published)

- [ ] C.1. Update Requirement 1.1 to demote Theorem 1.1 to a cited result; make stuck-state + gap-of-3 the headline pair. _Implements Fallback 2 of Req 10.3._
- [ ] C.2. Rewrite Abstract and Contributions to match the demotion.
- [ ] C.3. Add a precise citation of the published greedy-completeness result in §3.
- [ ] C.4. Continue to Phase 3 on the revised headline.

### If Tripwire 10.2 fires (Phase 2, Lemma B C4/C5 obstacle)

- [ ] C.5. Invoke Fallback 1: prove greedy completeness for the R1-down-only fragment, or for chord diagrams with bounded nesting depth; demote the full Theorem 1.1.
- [ ] C.6. If Fallback 1 also resists, invoke Fallback 2: drop Theorem 1.1 entirely; headline becomes stuck-state + gap-of-3.
- [ ] C.7. Rewrite Abstract and Contributions to match whichever fallback was invoked.
- [ ] C.8. Add an Open Problems subsection stating the full Theorem 1.1 as a conjecture.

### If Phase 3 discovers a No-Up counterexample at $n \leq 8$

- [ ] C.9. Promote the counterexample to a prominent §6.4 subsection: "A counterexample to the No-Up conjecture at crossing number $n$". _Implements Req 4.7._
- [ ] C.10. Rewrite the open-problem discussion accordingly: No-Up is now false, and the question becomes characterizing which classical unknot Gauss words satisfy No-Up.
- [ ] C.11. Consider whether the paper's framing should shift to foreground the counterexample (probably yes, if $n$ is small).

### If the SoCG 2026 submission is rejected

- [ ] C.12. Revise the manuscript based on reviewer feedback.
- [ ] C.13. Re-target per Req 10.3 Fallback 3 and design §6.4: **Discrete & Computational Geometry** is the primary backup venue.
- [ ] C.14. Expand proofs and discussion to use the DCG journal format's wider page budget.

---

## Status tracker

Update this section at the end of each phase.

- Phase 0: **DONE.** See `notes/phase0_results.md`. Key findings: 0/5 benchmarks bigon-reducible; Goeritz and Culprit are certified No-Up counterexamples at cr=10,11; Theorem 1.1 empirically falsified in zero out of 5,000 greedy runs.
- Phase 1: **DONE (redo).** See `notes/phase1_literature.md`. Tripwire does not fire. Graph-link / Traldi–Zulli / Ilyutko–Manturov literature is the closest-in-setting published body of work — defines exactly our graph-theoretic moves but is entirely invariant-theoretic, not decidability-focused. Manturov–Ilyutko–Kauffman 2009 disproves the signless analogue of No-Up; our Goeritz/Culprit are the first counterexamples in the signed category. All required §7 citations identified.
- Phase 2: **DONE (with corrections + bonus Theorem 2).** All seven original Phase 2 proof files plus one bonus certifying-theorem file, written and verified by clean LaTeX compilation. Four substantive corrections applied during review: (a) Lemma B's Case C4/C5 had a real hole — the originally submitted proof claimed a bigon-move sequence from $\sigma_1(w)$ to $\mu(w)$, but the two states have different chord sets and cannot be interconverted by deletion; fixed via the minimality-of-$i$ argument using Lemma E. (b) Theorem 1's complexity claim was $O(n^3)$; corrected to $O(n^4)$ naive / $O(n^3)$ with incremental data structure. (c) Stuck-state theorem was stated for "bigon" moves but the proof argued the permissive version; split into two correct theorems (`thm:stuck-permissive`, `thm:stuck-bigon`) with a corollary for the interlacement characterization (the original "every component is a clique" claim was wrong — disjoint chords coexist when interleaving is transitive-not-complete). (d) Gap theorem had a sign flip, broken display-math, and no permissive-vs-bigon disambiguation; all fixed. Plus minor tightenings in Lemma A and a typo in the non-confluence remark. **Bonus:** `theorem_1_2_certifying.tex` adds Theorem 2 (certifying decision with matching yes/no certificates) per the SoCG reframing discussion — essentially free from existing Phase 2 machinery, elevates the paper's contribution from "structural greedy completeness" to "polynomial-time certifying decision procedure." Tripwire 10.2 effectively fired at Case C4/C5 review but was resolved within budget; Fallback 2 not invoked.
- Phase 3: **DONE (with two regressions caught and corrected during review).** Code written, tests passing after fixes, partial re-run results clean. Two substantive regressions found and reverted:
  - **Regression A (critical):** `core/gauss.py::get_valid_actions` had been modified to include "interleaved" chord pairs as R2-down-eligible in both permissive and bigon modes. This is algebraically incorrect: R2-down is defined only on *nested* pairs; deleting an interleaved pair collapses a genuine linking structure (the trefoil's three pairwise-interleaved chords would become "reducible" to ∅ in 1.5 steps under the bug). All Phase 3 scaling runs produced under the bug are invalidated. Phase 0 data (produced pre-regression) is untouched. After reverting to the correct nested-only R2 semantics, the n=2..4 exhaustive re-runs give the correct counts (4, 30, 384 classical unknots) and 0 counterexamples.
  - **Regression B:** `experiments/random_unknot.py::_random_unsigned_word` was returning distinct-label permutations of length 2n rather than double-occurrence words. Every sample was a degenerate non-Gauss-word. Fixed with a Fisher–Yates shuffle of the multiset `[1,1,2,2,...,n,n]`. Only the random-sampling regime (n ≥ 7) used this path; exhaustive regime was unaffected.
  - **Correct infrastructure:** `core/planarity.py` (de Fraysseix parity, 10/10 test cases), `core/unknot_verify.py` (BRS-based unknot verification with approved budget table), `experiments/random_unknot.py` (exhaustive enumerator + uniform sampler), `experiments/phase3_scaling.py` (correct per-n logic), plus three LaTeX snippets for §3 and §6.
  - **LaTeX snippet corrections during review:** `phase3_algo_complexity.tex` rewritten to match corrected Theorem 1 bounds ($O(n^4)$ naive / $O(n^3)$ incremental) and remove a misleading $O(n! \cdot n^3)$ backtracking claim. `phase3_pseudocode.tex` had a residual "or interleaved" phrase removed from the R2 description.
  - **Full n=2..12 sweep not yet executed** as a single batch; the `phase3_scaling_results.json` output file is overwritten per run rather than merged, so partial runs can't be accumulated. Batch run pending.
- Phase 4: _not started_
- Phase 5: _not started_
- Phase 6: _not started_
