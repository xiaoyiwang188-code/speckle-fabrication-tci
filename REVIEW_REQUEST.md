# Review Request — Deep Read of the Revised Manuscript

**Manuscript**: "Matched Fine-Tuning Controls Spectral Fabrication in Learned Speckle Imaging: Capacity Effects and a Compute-Matched Remedy" (IEEE TCI format, 7 pages)
**Repository**: https://github.com/xiaoyiwang188-code/speckle-fabrication-tci
**Ground truth rule**: `results/` wins over the manuscript on any discrepancy.

## Start here

1. `README_REPRO.md` — reproduction commands, the number-to-file mapping table, and an
   author-written list of 8 known weak points.
2. `paper/main.pdf` — the manuscript itself.
3. `paper/CLAIM_AUDIT.md` / `paper/CITATION_AUDIT.md` — prior self-audits (treat as claims
   to verify, not as evidence).

A prior external review round already found and we fixed 6 issues (F1, F2, D1, D2, F3, F4 —
see `README_REPRO.md` §Revision history). **Those fixes touched the abstract, introduction,
§4.2, §4.4, §4.6, the discussion, and two figure captions.** This round should check whether
the fixes are internally consistent — that is exactly what a fresh read is for.

## What we specifically want examined

### 1. Consistency of the last round's fixes
- **F1**: "order-of-magnitude" residue was found in the discussion text and the Fig. 4 caption
  after the numbers had been corrected to 1.4×. Both were rewritten. Are there any remaining
  stale variants anywhere in the text, captions, or supplementary material?
- **F2**: "2–6× below every learned arm" was too strong (the half-bandwidth arm sits within
  ~1.1× of the worst Wiener cell). It was scoped to "raw-target and matched arms" in four
  places. Does any remaining sentence still imply the Wiener advantage covers all arms?
- **D2**: pixel-level speckle–ground-truth correlations turned out to be a non-signal
  (same-id and mismatched means within ~0.01), so they were withdrawn as evidence and the
  argument now rests on autocorrelation-NCC pairing (0.60 vs 0.50, Welch t = 3.2). Does §5
  now rest on a sound footing, or is the real-data section weaker than it needs to be?

### 2. The E1 collapse disclosure (§4.6)
Root cause of the original collapse: a phase-parameterization bug in `make_psf` — the binary
branch used `exp(i·2π·(±π))`, which is an effective ±0.89 rad weak phase, not ±π. After the
fix, two of twelve decoders still converge to partially object-independent solutions **on
out-of-family inputs**, stably across seeds and both parameterizations. The manuscript
discloses this and reports a collapse-exclusion sensitivity analysis (ΔBIC −1.1…+0.6,
p 0.11–0.18; the negative conclusion is unchanged). Questions: is the disclosure adequate, is
the sensitivity analysis the right test, and is it normal practice to report this?

### 3. The Wiener fairness protocol
The comparison now rescales the Wiener output by an optimal scalar before computing relative
forward error (a raw Wiener estimate is not amplitude-calibrated, and our first, un-rescaled
comparison produced a spurious "order of magnitude" gap). Is least-squares scalar rescaling a
fair way to compare a linear baseline against a trained network on this metric, or should it
be e.g. a full linear least-squares fit, or a different endpoint entirely?

### 4. The "2–6×" interval under F2's correction
With the half-bandwidth arm now close to the Wiener range, is the current phrasing the most
informative one, or is there a cleaner way to state what the Wiener anchor actually bounds?

## What we are least sure about (flagged for you specifically)

- Whether the Wiener fairness protocol (§3) is the right choice, and whether the resulting
  trade-off framing survives it.
- Whether the real-data section (§5) is doing enough work, or whether it should be framed as
  an explicit negative result rather than a boundary condition.
- Whether disclosing a training-collapse anomaly in a supporting experiment (§4.6) is the
  right call, and whether the sensitivity analysis reads as rigorous or defensive.

## Output request

A report with: (a) issues classified as substantive error / overreach / unclear / optional,
each with location and a concrete fix; (b) an independent recomputation of the headline numbers
(0.34 ± 0.11, 0.20 ± 0.08, 6/6, +0.026 rel-fwd, Wiener rescaled 0.52–0.55) against `results/`;
(c) any claim in the manuscript that the data in this repository does not support; (d) an
overall verdict: is this submission-ready, and if not, the minimum blocking list.
