# Outline review (IEEE TCI) - deepseek-v4-flash

## Response

Strong, mature outline. The claims–evidence matrix and honest limitation framing are excellent. My review assumes the numbers in the matrix reproduce from `scaleup_results.json` and that the “compute-matched control” is exactly as described.

| Criterion | Score | Key weakness | Minimum fix |
|---|---|---:|---|---|
| 1. Logical flow | 8/10 | §5 “Distance-Law Analysis” is a detour after the main causal story. It reads like a second paper and stalls momentum before real-data. | Compress §5 to a half-page “negative control” paragraph inside §4, or move the full E1 analysis to supplementary. Keep one sentence in the intro saying “we also reject a diffuser-distance explanation; see §4.6/supp.” |
| 2. Claim-evidence alignment | 7/10 | C2 “fabrication scales with network capacity” is overclaimed from two widths. C5’s “single distances are jointly incomplete” is not directly evidenced by the three p-values. Main paired claims lack explicit inferential statistics. | Reword C2: “in the two tested capacities, raw fabrication was higher for the larger net and matched suppression was stronger.” Add a one-sided sign-test/permutation p-value to C1/C4 (6/6 paired reductions gives one-sided p≈0.016). For C5, either add a multi-factor-regression fit (ΔAIC vs single-distance) or downgrade the claim to “suggestive.” |
| 3. Missing experiments/analysis | 7/10 | Science is strong, but reviewers will want (a) inferential statistics on the paired comparisons, (b) a third capacity point to support “capacity effects,” and ideally (c) one natural-image/phantom example showing that oob energy corresponds to visible artifacts, not just a spectral metric. | Minimum: add paired p-values/CIs in Table 2. If compute allows, add a cheap base8 arm (3 seeds) to §4.3; otherwise soften all “scales” language. Add one Siemens-star/USAF phantom panel to Fig. 5 to show oob suppression is visually meaningful. |
| 4. Positioning vs prior work | 8/10 | The gap is clear and the “compute-matched causal intervention” is persuasive. But “low-pass filtering training targets” is a common practical trick elsewhere; reviewers will ask why this is not just that trick applied to speckle. | Add 2–3 sentences in §2: prior low-pass/filtered-target stabilizations were not analyzed as a causal control for spectral fabrication, not quantified against measured MTF support, and not compared with a compute-matched raw-continued control. Also state explicitly how oob energy ratio differs from Tivnan’s Hallucination Index. |
| 5. Page budget feasibility | 7/10 | Sections alone sum to ~11.25 pages; figures/tables + refs will likely push toward 14 unless floats are tight. §5 and the full real-data section are the main overrun risks. | Merge Table 1 and Table 2 into one combined float. Reduce §5 to one paragraph (full transfer matrix → supplement). Set a hard cap: §4 text + Figures 2–4 + Table 1 must fit in 4 pages. |
| 6. Front-matter strength | 7/10 | The one-sentence contribution is strong and the hero figure concept is right. But there is no actual abstract draft, and the hero plan is dense/ambiguous — “measurement ground truth” is confusing and the two-panel structure may not be skimmable. | Write a 150-word abstract now: problem, intervention, key numbers, limitation, implication. Change the hero to a 3-panel triptych: (1) measured MTF support with reconstruction spectrum overlay and oob shaded; (2) raw-GT vs matched-GT reconstruction pair with oob visibly suppressed; (3) small bar chart of oob ratios (control/matched/half). Caption should say “oob energy is a fabrication proxy.” |

## Top-3 changes to apply before drafting

1. **Draft the abstract and simplify the hero figure.** This is the first thing TCI editors/skim readers see. A 150-word abstract with real numbers and a clean 3-panel hero will sell the paper much better than the current plan.

2. **Fix the capacity claim and add inferential statistics.** Soften C2 to “two tested capacities” or add a base8 arm. Add p-values/CIs to C1/C4. This will preempt the most likely reviewer objection: “6/6 is nice, but what is the uncertainty/effect size?”

3. **Rebalance for page budget: compress §5 and merge tables.** Move E1 to supplementary, merge Table 1 + Table 2, and use the saved space to make the real-data section a clear boundary condition rather than an incomplete result.

## Verdict

**REVISE — targeted, not structural.** The outline is very close to draft-ready. Apply the three changes above, and it is a **GO**. As written, the C2 overclaim and the §5 detour would likely draw reviewer fire and cost page budget.
