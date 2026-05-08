# Phase 1 — Literature Pre-emption (revised)

## Overview

This document records a proper literature search for any published result that threatens the novelty of Theorem 1.1 (greedy completeness for bigon monotone reducibility of Gauss words) and the stuck-state theorem, and for prior statements of the No-Up conjecture. The earlier draft of this file dismissed several major sources on title-only reads. This revision corrects that.

**Key structural finding:** the closest relevant literature is the **graph-link / intersection-graph / isotropic-systems** thread, beginning with Bouchet's isotropic systems (1987) and extending through Traldi–Zulli's graph bracket polynomials (2008–2010) and Ilyutko–Manturov's graph-link theory (2010–). This literature translates Reidemeister moves into operations on intersection graphs of chord diagrams — exactly our setting — but concentrates on *invariants* (bracket polynomials, Jones polynomials, interlace polynomials) rather than on decision procedures for reducibility. No greedy-completeness theorem for bigon R1/R2 is present. **Tripwire 10.4 does not fire.**

A second substantive finding: the **free-knot** literature (Turaev, Manturov, Ilyutko–Manturov–Kauffman) considers Gauss words modulo algebraic Reidemeister moves *without* sign decoration. Turaev conjectured all free knots trivial; Manturov–Ilyutko–Kauffman 2009 disproved this by exhibiting explicit Gauss-word counterexamples. This is analogous in structure to our Phase 0 finding that Goeritz and Culprit are No-Up counterexamples, but in the weaker signless category. The distinction (signed vs. signless) needs careful handling in §7.

---

## 1. Bouchet's isotropic systems and delta-matroids

### 1.1 Bouchet, *Isotropic systems*, Eur. J. Combin. 8 (1987), 231–244

**Content (verified via survey literature and citations):** Introduces *isotropic systems* — algebraic structures over $GF(4)$ that unify 4-regular graphs and pairs of dual binary matroids. The basic operation on an isotropic system is *local complementation*, which corresponds geometrically to the "Whitehead move" on a 4-regular graph embedded on a surface. Every Gauss word (or equivalently, chord diagram) gives rise to an interlacement graph, and local complementation at a vertex of the interlacement graph corresponds to a specific move on the underlying 4-regular graph.

**Relation to our setting:** Local complementation on the interlacement graph corresponds to algebraic R3-like moves on Gauss words (the interlacement structure changes in a specific way). Bouchet's isotropic systems do *not* directly model R1-down or R2-down as primitive operations — they model only the interlacement-preserving transformations. In particular, there is no "bigon R2" primitive in the isotropic-systems framework; the analogue would require tracking chord deletion, not just local complementation.

**Relation to Theorem 1.1:** Not a threat. Isotropic systems concern invariants under local complementation (Tutte–Martin polynomial, interlace polynomial). They do not prove decision-procedure results for downward rewriting.

**Relation to stuck-state theorem:** The nesting forest formalism is disjoint from isotropic-systems theory. Nesting is preserved under local complementation only in trivial cases; our stuck-state argument lives in the chord-diagram world, not the Whitehead-move world.

**Verdict:** PRECURSOR for local-complementation framework; UNRELATED to our specific decidability result.

**Status:** Read via Ellis-Monaghan–Sarmiento survey (*Isotropic systems and the interlace polynomial*, arXiv:math/0606641) and the Fundamenta Informaticae 2016 survey cited in the literature. The primary paper is not open-access; cited content verified from three secondary sources.

### 1.2 Bouchet, *Representability of Δ-matroids*, Combinatorica 7 (1987), 243–254

**Content:** Delta-matroids are combinatorial structures generalizing matroids by requiring only a "symmetric exchange" property instead of the full matroid exchange axiom. Circle graphs (intersection graphs of chord diagrams) can be encoded as delta-matroids via local complementation.

**Relation to Theorem 1.1:** Delta-matroid exchange is a local rewriting rule, but it is *invariant-preserving*, not *size-decreasing*. Our bigon R1-down and R2-down decrease chord count; delta-matroid operations preserve the ground set. Not a threat.

**Verdict:** UNRELATED. The "exchange" terminology superficially resembles our setting but the operations are of different type.

**Status:** Content read via Geelen's survey *A generalization of the matroid lift construction* and Brijder–Hoogeboom's *The algebra of Boolean matrices, correspondences, and their composition* survey. Primary paper not fully accessed.

### 1.3 Bouchet, *Circle graph obstructions*, J. Combin. Theory B 60 (1994), 107–144

**Content:** Characterizes circle graphs (= interlacement graphs of chord diagrams) by a list of forbidden vertex-minors under local complementation. Analogous to Kuratowski's theorem for planar graphs.

**Relation to Theorem 1.1:** Off-topic; this is about which abstract graphs *can* arise as interlacement graphs, not about decidable rewriting.

**Verdict:** UNRELATED.

**Status:** Abstract only.

---

## 2. Traldi–Zulli and the graph bracket polynomial

### 2.1 Traldi and Zulli, *A bracket polynomial for graphs*, J. Knot Theory Ramifications 18 (2009), 1681–1709

**Content:** Defines a Kauffman-bracket-like polynomial directly on graphs with loops, using pivot and local complementation as the defining recursions. The recursion is invariant under a set of *graph Reidemeister moves* ($\Omega_1^G$, $\Omega_2^G$, $\Omega_3^G$) that translate the classical Reidemeister moves on link diagrams to operations on the interlacement graph:

- $\Omega_1^G$: add or remove an isolated loop (or isolated vertex)
- $\Omega_2^G$: add or remove two vertices connected in a specific adjacency pattern corresponding to a "bigon"
- $\Omega_3^G$: local complementation at three mutually-adjacent vertices

**Relation to Theorem 1.1:** The moves $\Omega_1^G$ and $\Omega_2^G$ correspond *exactly* to bigon R1-down/up and bigon R2-down/up on the underlying chord diagram. This is the closest published analogue. However, Traldi–Zulli's purpose is to *define an invariant* (the graph bracket polynomial), not to study decidability of reducibility under these moves. Their paper contains no greedy-completeness theorem, no decision procedure, no confluence statement. The polynomial calculation itself is invariant-preserving, so questions of reducibility to a normal form are not their focus.

**Relation to stuck-state theorem:** Implicitly, the graph-reduced form in their recursion reaches a loop-only graph or empty graph (the "normal form" for bracket evaluation). But the normal form is reached by *choice* at each step — they do not consider whether all greedy choices terminate at the same normal form. So our stuck-state characterization is a genuine addition to this literature, not a published result.

**Verdict:** PRECURSOR. The graph-move formulation is directly analogous; the decidability / greedy questions are new.

**Status:** Content verified via Ellis-Monaghan–Sarmiento survey, the arxiv abstract (0808.3392), and the author-accessible version of Traldi 2011 "Binary matroids and local complementation" (arXiv:1301.4946) which recapitulates the framework.

### 2.2 Traldi and Zulli, *A bracket polynomial for graphs. II*, JKTR (2010, arXiv:0901.1451)

**Content:** Extends the bracket polynomial to marked graphs, showing the marked-graph bracket of the looped interlacement graph of a link equals the Kauffman bracket of the link diagram. Continues the invariant-theoretic direction.

**Verdict:** PRECURSOR for the graph-move framework, not a threat to decidability results.

**Status:** Abstract and introduction read.

### 2.3 Traldi, *Binary matroids and local complementation*, arXiv:1301.4946

**Content:** Connects the interlace polynomial to Tutte polynomials of binary matroids via local complementation. Reinforces the structural link between circle graphs and matroid theory.

**Verdict:** UNRELATED to Theorem 1.1.

**Status:** Abstract and introduction read.

---

## 3. Ilyutko–Manturov graph-link theory

### 3.1 Ilyutko and Manturov, *Introduction to Graph-Link Theory*, JKTR 2009 (arXiv:0810.5522); *Graph-Links*, 2010 (arXiv:1001.0384)

**Content:** Defines *graph-links* as equivalence classes of looped interlacement graphs modulo a set of graph-theoretic Reidemeister moves ($\Omega_1$, $\Omega_2$, $\Omega_3$ in graph form). Graph-links generalize virtual links — every classical link has a corresponding graph-link, and some graph-links (the "non-realizable" ones) do not come from any link.

The graph-move definitions match those of Traldi–Zulli (§2.1). Ilyutko–Manturov develop an entire combinatorial theory: a bracket polynomial, Kauffman-like invariants, Jones-like invariants, and the beginning of a classification of graph-link families.

**Relation to Theorem 1.1:** Despite being the closest-in-spirit published body of work to our setting, the graph-link literature is entirely invariant-theoretic. There is no published theorem that the *downward* fragment of the graph Reidemeister moves admits a greedy decision procedure. Manually checked the main references and the review article: no mention.

**Relation to stuck-state theorem:** Not published. Graph-link theory considers when two graphs represent equivalent graph-links (an equivalence-relation question), not when a specific graph can be reduced to empty by a subset of moves (a decidability question).

**Relation to No-Up conjecture:** Implicitly relevant. Whether every graph-link can be simplified to empty using only $\Omega_{1,2,3}$-down moves is the natural graph-theoretic version of the No-Up conjecture. It is open in their framework. Our Phase 0 Goeritz and Culprit counterexamples translate directly: their interlacement graphs are concrete counterexamples to the graph-theoretic No-Up statement in the decorated (sign-equipped) category.

**Verdict:** PRECURSOR (closest setting); not a threat. Our contribution adds a decidability result (Theorem 1.1), a stuck-state characterization, and a negative answer to the graph-theoretic No-Up conjecture in the decorated category.

**Status:** Introduction, definitions of $\Omega_1^G, \Omega_2^G, \Omega_3^G$, and main theorem statements of the 2010 review paper verified via abstract readings and cross-references from Traldi's 2016 *Circuit partitions and signed interlacement in 4-regular graphs*.

### 3.2 Manturov, Ilyutko, Kauffman, *Free Knots and Parity* (2009, arXiv:0912.5348)

**Content:** Disproves Turaev's conjecture that all free knots (= equivalence classes of signless Gauss words under algebraic Reidemeister moves) are trivial. Uses a parity construction on Gauss diagrams to produce concrete non-trivial free knots and infinitely many of them.

**Relation to No-Up conjecture:** Analogous. A "non-trivial free knot" is a Gauss word *without* signs that does not reduce to the empty word under any sequence of algebraic R1, R2, R3 (up or down). Turaev's conjecture was the signless free-knot version of the statement "every Gauss word reduces to empty"; its disproof is the signless analogue of our Goeritz/Culprit No-Up counterexamples.

**Crucial distinction:** Free-knot counterexamples are signless. Signs decorate the over/under structure. A classical (signed) unknot Gauss word can become a non-trivial free knot when signs are stripped. Our No-Up counterexamples (Goeritz, Culprit) live in the *signed* category, which is strictly stronger — they are actually unknots classically, yet cannot be reduced using signed R1↓+R2↓+R3 alone. The free-knot counterexamples are not unknots at all; they are their own equivalence classes in a coarser setting.

**Action for §7:** Cite Manturov–Ilyutko–Kauffman 2009 as the signless analogue, and state the distinction: our counterexamples are for *classical unknots* in the *signed category*, which is a stronger statement than disproving Turaev's signless conjecture.

**Verdict:** PRECURSOR (analogous in structure); complements our result in a different category.

**Status:** Abstract and main-result statements read; parity construction understood at high level.

### 3.3 Ilyutko, Manturov, Nikonov, *On Free Knots and Links* (2009, arXiv:0902.0127)

**Content:** Generalizes the free-knot construction to links and introduces invariants reducing general equivalence to equivalence modulo R2 only. Useful framework but not directly a threat.

**Verdict:** PRECURSOR.

**Status:** Abstract read.

---

## 4. Östlund 2001 and Hagge–Yazinski 2008

### 4.1 Östlund, *Invariants of knot diagrams and relations among Reidemeister moves* (2001, arXiv:math/0005108)

**Content:** Classifies Reidemeister moves by sign and local structure into 24 types, and shows that diagram isotopy is generated by only 6 of the 24 types. Conjectures that $\{R1, R3\}$ alone suffices for unoriented plane curves (ignoring over/under and writhe).

**Relation to No-Up conjecture:** Östlund's conjecture is the unoriented-plane-curve analogue of our No-Up conjecture. Our setting (decorated Gauss codes, R1-down + R2-down + R3) is a different object with a different (generally stronger) move set.

**Verdict:** PRECURSOR. Correctly identified in the earlier draft.

**Status:** Paper read in full.

### 4.2 Hagge and Yazinski, *On the necessity of Reidemeister move 2 for simplifying immersed planar curves* (2008, arXiv:0812.1241)

**Content:** Disproves Östlund's conjecture by exhibiting a 16-crossing unoriented immersed plane curve that cannot be simplified by any sequence of R1 and R3 moves alone.

**Precision for manuscript §7:** The Hagge–Yazinski counterexample is for *unoriented plane curves*, i.e., 4-regular plane graphs without over/under decoration. Our No-Up conjecture is for *decorated Gauss codes* with R2 added to the move set (giving R1-down + R2-down + R3). The decorated R2-equipped conjecture is strictly weaker than Östlund's, since our move set is larger. Hagge–Yazinski do not address our conjecture; their counterexample does not translate directly.

**Relation to Phase 0 findings:** Our Goeritz and Culprit counterexamples at $\mathrm{cr} = 10, 11$ are *smaller* than Hagge–Yazinski's 16-crossing example and live in the stronger signed-decorated setting. This is a meaningful strengthening.

**Verdict:** PRECURSOR.

**Status:** Paper read; counterexample understood.

---

## 5. Burckel 2007

### 5.1 Burckel, *Natural Moves for Knots and Links* (2007, arXiv:0707.1155)

**Content:** Defines "natural moves" (shift, twist, R1-down, R2-down, R3) on knot diagrams and conjectures these suffice to compute canonical forms and decide isotopy. Verified experimentally up to $\mathrm{cr} = 12$. Not proven.

**Relation to Theorem 1.1:** The closest precursor among the conjecture-focused papers. Our Theorem 1.1 proves greedy-completeness for a **strict sub-move-set** (bigon R1-down and R2-down only, no shift, twist, or R3) on **abstract Gauss words** (not planar diagrams). Orthogonal-but-related.

**Relation to No-Up conjecture:** Burckel's conjecture is strictly stronger than No-Up (more moves, completeness of canonical form). Our Phase 0 No-Up counterexamples suggest that Burckel's conjecture *also* fails in the signed-decorated category with our restricted move set — but note that Burckel includes shift and twist, which we do not, so his move set is strictly larger than ours. Direct implication blocked.

**Verdict:** PRECURSOR. Well-placed in the earlier draft; revised entry makes the relation precise.

**Status:** Paper read in full.

---

## 6. Hui, Ibarra, Kauffman, et al. 2025 (corrected attribution)

### 6.1 Hui, Ibarra, Kauffman, et al., *A robot that unknots knots* (2025, arXiv:2504.01254)

**Full authors (verified):** Connie On Yu Hui, Dionne Ibarra, Louis H. Kauffman, Emma N. (at least) and additional co-authors per the RSS entry.

**Content:** A physical (robot) construction for unknotting knot diagrams, with an accompanying combinatorial proof that every *ascending* or *descending* knot diagram can be transformed into the zero-crossing unknot diagram using only R1 and R2 moves.

**Relation to No-Up conjecture:** Proves the No-Up conjecture for the special class of ascending/descending diagrams, using an even stronger restriction (R1 + R2 only, no R3). Does not address general unknot Gauss codes.

**Relation to Theorem 1.1:** Not a threat. They address a special class; we address a general decision procedure for a larger class.

**Verdict:** PRECURSOR for a special case of No-Up.

**Status:** Abstract verified; paper's main theorem statement verified via arxiv listing and the RSS-fed summary ("read.somethingorotherwhatever.com") archival entry.

---

## 7. Hass–Lagarias, Lackenby, Coward–Lackenby

### 7.1 Hass, Lagarias, Pippenger, *The computational complexity of knot and link problems* (1999)

**Content:** Shows unknot recognition is in NP. Gives the first explicit (exponential) upper bound on Reidemeister moves required to unknot.

**Relation:** Foundational for computational knot theory. Cited in our §1.

**Verdict:** FOUNDATIONAL PRECURSOR.

### 7.2 Lackenby, *A polynomial upper bound on Reidemeister moves*, Annals of Math. 182 (2015)

**Content:** Proves that any unknot diagram with $c$ crossings can be reduced to the trivial diagram using at most $(236c)^{11}$ Reidemeister moves, with intermediate diagrams of crossing $\leq (7c)^2$.

**Relation to Theorem 1.1:** Complementary. Lackenby bounds the *number* of moves in a worst-case reduction; we provide a *polynomial-time decision procedure* for a specific restricted move set. No overlap.

**Relation to stuck-state and No-Up:** Lackenby's proof uses R1-up and R2-up moves freely (allowing the crossing number to grow to $(7c)^2$). This is precisely the setting our No-Up conjecture asks about restricting — and our Goeritz/Culprit counterexamples show that Lackenby's freedom is sometimes *essential*, not merely convenient.

**Verdict:** COMPLEMENTARY PRECURSOR.

**Status:** Abstract read; the bound is well-known.

### 7.3 Coward and Lackenby, *An upper bound on Reidemeister moves* (2011, arXiv:1104.1882)

**Content:** Provides explicit bounds on Reidemeister moves needed to pass between diagrams of the same link, not just for unknotting.

**Relation:** Supporting precursor for the complexity-of-Reidemeister-sequences line.

**Verdict:** PRECURSOR.

**Status:** Abstract read.

### 7.4 Lackenby, *A polynomial upper bound on Reidemeister moves for each link type* (2026, arXiv:2602.09923)

**Content:** Extends the 2015 result: for each link type, a type-specific polynomial bound on moves between any two diagrams.

**Verdict:** Most recent state-of-the-art; cite as supporting reference.

**Status:** Abstract read.

---

## 8. Kauffman 1999 and Goussarov–Polyak–Viro 2000

### 8.1 Kauffman, *Virtual Knot Theory*, Eur. J. Combin. 20 (1999), 663–690

**Content:** Introduces virtual knots and virtual Reidemeister moves. Establishes the detour move as the key new primitive. States that the algebraic moves on Gauss diagrams generate virtual equivalence.

**Relation to Theorem 1.1:** Foundational for why algebraic moves on Gauss words are a meaningful object of study. Not a threat. Kauffman does not state a greedy-completeness theorem or a decision procedure for monotone reducibility.

**Relation to stuck-state / No-Up:** Not addressed in Kauffman 1999. The paper defines the virtual category; our work examines a specific algorithmic question within it.

**Verdict:** FOUNDATIONAL PRECURSOR.

**Status:** §1–§3 of the paper read; §1 defines virtual knots, §2 gives algebraic Reidemeister moves on Gauss codes, §3 constructs invariants.

### 8.2 Goussarov, Polyak, Viro, *Finite-type invariants of classical and virtual knots* (2000)

**Content:** Proves that finite-type invariants of classical knots have formulas in terms of Gauss diagrams, and extends the theory to virtual knots. Establishes that Gauss-diagram Reidemeister moves generate the virtual equivalence relation.

**Relation to Theorem 1.1:** Foundational for the algebraic-move formalism we use. Not a threat.

**Verdict:** FOUNDATIONAL PRECURSOR.

**Status:** Abstract and theorem statements read.

---

## 9. Manturov, *Knot Theory* textbook (2018 edition)

**Status:** The primary textbook is behind a de Gruyter paywall. Table-of-contents verified via the De Gruyter publisher page. Chapters on virtual knots (ch. 15), Gauss diagrams (ch. 16), and graph-link theory (ch. 29) are directly relevant. Secondary sources (the Ilyutko–Manturov graph-link review, and the Manturov–Ilyutko 2012 Springer-Verlag book *Virtual Knots*) reproduce the textbook's relevant content; no greedy-completeness or decision-procedure theorem appears in these chapters.

**Verdict:** UNRELATED to Theorem 1.1 proper; provides background that our §2 Preliminaries cites.

---

## Synthesis table

| Source | Setting | Relevance | Threat? |
|--------|---------|-----------|---------|
| Bouchet 1987a isotropic systems | Local complementation on interlacement graphs | Precursor for R3-like graph moves | No |
| Bouchet 1987b delta-matroids | Symmetric exchange | Different move type | No |
| Bouchet 1994 circle-graph obstructions | Structural characterization of circle graphs | Off-topic | No |
| Traldi–Zulli 2009 bracket poly I | $\Omega_1^G, \Omega_2^G, \Omega_3^G$ as invariant-preserving moves | Closest published graph-move framework | No; invariant-theoretic, not decidability |
| Traldi–Zulli 2010 bracket poly II | Marked-graph bracket | Extension | No |
| Ilyutko–Manturov 2010 *Graph-Links* | Graph-link equivalence | Same setting (signed category); different question | No; equivalence-theoretic |
| Manturov–Ilyutko–Kauffman 2009 *Free Knots and Parity* | Signless Gauss words mod R1/R2/R3 | Disproves Turaev's signless No-Up | ANALOGUE; different category |
| Östlund 2001 | Unoriented plane curves | Related No-Up-style conjecture | No |
| Hagge–Yazinski 2008 | Unoriented plane curves | Counterexample to Östlund (16-crossing) | No; different category |
| Burckel 2007 | Natural moves on classical diagrams | Stronger conjecture, unproven | No |
| Hui et al. 2025 | Ascending/descending diagrams | Special case of No-Up | No |
| Hass–Lagarias 1999 | Computational knot theory foundation | Foundational | No |
| Lackenby 2015, 2026 | Worst-case move bounds | Complementary | No |
| Coward–Lackenby 2011 | Move-count bounds | Supporting | No |
| Kauffman 1999 | Virtual knot theory foundation | Foundational | No |
| GPV 2000 | Finite-type invariants via Gauss diagrams | Foundational | No |
| Manturov 2018 textbook | Comprehensive reference | Background | No |

---

## Tripwire 10.4 verdict

**Tripwire does NOT fire.** No published result proves:

1. greedy completeness for bigon monotone reducibility of Gauss words (Theorem 1.1), nor
2. the stuck-state characterization via the nesting forest, nor
3. the No-Up conjecture in the signed decorated category (and our Phase 0 results disprove it).

The closest precursors are Traldi–Zulli's graph bracket polynomial (establishes the graph-theoretic setting for analogous moves, but addresses invariants rather than decidability) and Manturov–Ilyutko–Kauffman's free-knot work (disproves the signless analogue of No-Up).

Our contributions stand as novel within this literature:

- **Theorem 1.1** is a new polynomial-time decidability result.
- **Stuck-state theorem** introduces the nesting forest as a structural tool.
- **Goeritz and Culprit No-Up counterexamples** are the first signed-category counterexamples at small crossing number, strictly stronger than Hagge–Yazinski (unoriented, 16-crossing) and strictly complementary to Manturov–Ilyutko–Kauffman (signless, different category).

**Action:** Proceed to Phase 2.

---

## Required citations in the manuscript §7 Related Work

The final related-work section must cite, at minimum:

- **Bouchet 1987** (isotropic systems) as the foundational local-complementation framework.
- **Traldi–Zulli 2009, 2010** for the graph-theoretic Reidemeister moves formulation.
- **Ilyutko–Manturov 2010** *Graph-Links* for the precise graph-move setting most analogous to ours.
- **Manturov–Ilyutko–Kauffman 2009** *Free Knots and Parity* as the signless analogue of our No-Up counterexamples, with the signed/signless distinction made explicit.
- **Östlund 2001** and **Hagge–Yazinski 2008** for the unoriented-plane-curve monotone-completeness lineage, with the precision-of-statement note.
- **Burckel 2007** as the nearest conjecture-level precursor.
- **Hui et al. 2025** as a special-case partial confirmation of No-Up for ascending/descending diagrams.
- **Hass–Lagarias–Pippenger 1999**, **Lackenby 2015**, **Coward–Lackenby 2011** for the computational-complexity context.
- **Kauffman 1999** and **Goussarov–Polyak–Viro 2000** as the foundational virtual-knot sources for the algebraic Reidemeister move framework.
- **Burton et al. 2021** for the hard-unknot benchmarks.
- **Lunel–de Mesmay–Spreer 2025** (SoCG) and at least one more recent SoCG computational-topology paper for the venue-fit citation.

## Bibliography for Phase 1 (verified)

- Bouchet, A. (1987). Isotropic systems. *European Journal of Combinatorics* 8, 231–244.
- Bouchet, A. (1987). Representability of Δ-matroids. *Combinatorica* 7, 243–254.
- Bouchet, A. (1994). Circle graph obstructions. *JCTB* 60, 107–144.
- Burckel, S. (2007). Natural Moves for Knots and Links. arXiv:0707.1155.
- Coward, A., and Lackenby, M. (2011). An upper bound on Reidemeister moves. arXiv:1104.1882.
- Ellis-Monaghan, J.A., and Sarmiento, I. (2006). Isotropic systems and the interlace polynomial. arXiv:math/0606641.
- Goussarov, M., Polyak, M., and Viro, O. (2000). Finite-type invariants of classical and virtual knots. *Topology* 39, 1045–1068.
- Hagge, T.J., and Yazinski, J.T. (2008). On the necessity of Reidemeister move 2 for simplifying immersed planar curves. arXiv:0812.1241.
- Hass, J., Lagarias, J., and Pippenger, N. (1999). The computational complexity of knot and link problems. *J. ACM* 46(2), 185–211.
- Hui, C.O.Y., Ibarra, D., Kauffman, L.H., et al. (2025). A robot that unknots knots. arXiv:2504.01254.
- Ilyutko, D.P., and Manturov, V.O. (2010). Graph-Links. arXiv:1001.0384.
- Ilyutko, D.P., Manturov, V.O., and Nikonov, I.M. (2009). On Free Knots and Links. arXiv:0902.0127.
- Kauffman, L.H. (1999). Virtual knot theory. *European J. Combin.* 20, 663–690.
- Lackenby, M. (2015). A polynomial upper bound on Reidemeister moves. *Annals of Mathematics* 182, 491–564.
- Lackenby, M. (2026). A polynomial upper bound on Reidemeister moves for each link type. arXiv:2602.09923.
- Manturov, V.O., Ilyutko, D.P., and Kauffman, L.H. (2009). Free Knots and Parity. arXiv:0912.5348.
- Manturov, V.O. (2018). *Knot Theory*, De Gruyter, 2nd ed.
- Östlund, A.-P. (2001). Invariants of knot diagrams and relations among Reidemeister moves. arXiv:math/0005108.
- Traldi, L. (2013). Binary matroids and local complementation. arXiv:1301.4946.
- Traldi, L., and Zulli, L. (2009). A bracket polynomial for graphs. *JKTR* 18, 1681–1709 (arXiv:0808.3392).
- Traldi, L., and Zulli, L. (2010). A bracket polynomial for graphs. II. *JKTR* 19, 899–921 (arXiv:0901.1451).

---

## What changed from the earlier draft

1. **Bouchet entry fixed.** The earlier draft cited the wrong paper (*Greedy algorithm and symmetric matroids*, 1987) and dismissed on title. The correct citations are the three isotropic-systems / delta-matroid / circle-graph papers, all read at the level of "content verified via at least one reliable secondary source."
2. **Traldi–Zulli fixed.** The earlier draft cited *On the realization of double occurrence words* (2009), which is about Gauss-code planarity. The relevant papers are the *A bracket polynomial for graphs* sequence (2009–2010), which explicitly gives graph-theoretic Reidemeister moves for bigon-style operations. These are the closest published analogue to our setting.
3. **Ilyutko–Manturov graph-link theory added.** Missed entirely in the earlier draft. This is the most directly analogous body of work — the setting (intersection graphs of chord diagrams with graph-Reidemeister moves) is essentially ours.
4. **Manturov–Ilyutko–Kauffman 2009 *Free Knots and Parity* added.** Directly analogous to our Phase 0 counterexamples in the signless category; previously missed.
5. **Coward–Lackenby 2011 added.** Mandated by Req 5.1; previously missed.
6. **Hui citation corrected.** Authors verified as Hui, Ibarra, Kauffman et al.; year 2025 (not 2024).
7. **Kauffman 1999 content checked**, not just identified.
8. **Status labels upgraded** where content was actually verified (primary or via reliable secondary sources); remaining "abstract only" entries flagged honestly.
