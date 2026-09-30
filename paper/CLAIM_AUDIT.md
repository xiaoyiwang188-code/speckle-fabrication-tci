# Claim Audit Report

**Date**: 2026-09-30
**Artifact**: paper/main.pdf (7 pages, IEEE TCI format)
**Method**: automated numerical cross-check of every quantitative claim in the manuscript against the raw result files (`results/scaleup_results.json`, `results/e4_stdout.txt`, `results/e2_stdout.txt`, `results/e1_stdout.txt`, `results/registration_fix2.txt`, `results/registration_fix3.txt`, `results/claim_audit.json`). Wiener forward-error recomputed live under the fair-rescaling protocol.
**Verdict**: 43 checks → **3 paper errors caught and corrected; 1 audit-scope clarification; 43/43 pass in post-fix state.**

## Corrections applied (would have been caught by referees)

| # | Location | As written | Actual data | Fix applied |
|---|----------|-----------|-------------|-------------|
| 1 | §4.2 (compute-matched control sentence) | "0.0210 → 0.0213 on average" | control mean **0.0238** vs raw baseline 0.0210 (**13%** increase) | corrected to "$0.0210$ to $0.0238$ (about 13%)" |
| 2 | §4.1 (baseline ratio) | "5.8× lower" | 0.0210/0.0036 = **5.9×** | corrected to 5.9× |
| 3 | rel-fwd baseline range (5 occurrences: abstract, intro, §4.2, §4.4, conclusion) | "0.37–0.40" | actual min **0.363** | unified to "0.36–0.40" |

## Audit-scope clarification (paper text correct)

- "Wiener oob stays in 0.0003–0.0032 ... and two settings drive it to numerical zero": the check flagged the minimum because two of six settings are exactly 0; the manuscript states the non-zero range and the zeros separately and consistently. No edit needed.

## Verified (highlights of the 43 checks)

- Paired causal result: 0.34±0.11 / 0.20±0.08, 6/6, +0.026 rel-fwd diff — all match `scaleup_results.json`.
- Baselines, PSNR inversion (16.5/31.7/22.1), capacity contrasts (0.026/0.015, 0.028/0.017, 0.23/0.44) — all match per-architecture means.
- Wiener: rescaled rel-fwd 0.52–0.55 (recomputed live), sweep oob range, 2–6× gap — match.
- E4 (0.522/0.596/0.544), E2 sweep (0.522/0.486/0.498), E1 (ΔBIC −0.4/+6.0/+2.6; p 0.14/0.92/0.33; max loss 14.2 dB) — exact match to stored outputs.
- Real data: grain FWHM 1.93 px, platform 190.6±~1 px, CV 1.02 — match.

## Post-fix state

All three corrections applied; LaTeX recompiled clean (7 pages, no undefined references, bibtex clean). Machine-readable ledger: `CLAIM_AUDIT.json`.

---

## Round 2 — external adversarial review (2026-09-30, second reviewer)

The reproduction pack was sent to an independent reviewer; its full report (复现与对抗审查报告) is archived with this project. Findings and dispositions:

| # | Finding | Disposition |
|---|---|---|
| F1 | "order-of-magnitude worse" residue in §6.1 + Fig 4 caption (self-contradictory vs the corrected 1.4× claim) | **Fixed**: both rewritten to "roughly 1.4× (~40%) worse" |
| F2 | "2–6× below every learned arm" overbroad (half-bandwidth arm within ~1.1× of worst Wiener cell) | **Fixed**: scoped to "raw-target and matched arms; the half-bandwidth arm approaches the Wiener range" (abstract, intro, §4.4, caption) |
| D1 | capacity point estimates rounded low (base32: 0.026→0.027, 0.028→0.030, ratio 0.23→0.25) | **Fixed** in §4.3 and in this audit script's expected values |
| D2 | pixel-level pairing correlations not reproducible from pack files; recomputation shows the groups nearly overlap (means within ~0.01) | **Fixed**: §5 now cites the autocorrelation-NCC pairing evidence (0.60 vs 0.50, Welch t=3.2, archived); `pairing_stats.py` added so the pixel-level null result is also reproducible |
| F3 | one collapsed decoder in E1 (index 6) | **Root-caused**: binary-phase parameterization bug in `make_psf` (`exp(i·2π·(±π))` → effective ±0.89 rad); fixed to `sign·0.5` (±π); collapse guard added; E1 rerun. Two decoders still converge to partially object-independent solutions **out-of-family** (stable across seeds and parameterizations) — now disclosed in §4.6 with a sensitivity analysis: excluding both leaves the negative conclusion unchanged (ΔBIC −1.1 to +0.6, p 0.11–0.18). Runs archived as `e1_stdout_run{1,2}_*.txt` |
| F4 | rel-fwd "0.36–0.40" silently excluded the half-baseline (0.468) | **Fixed**: exclusion stated explicitly in §4.2 |

**Audit script status**: all previously-flagged check values updated to the current manuscript; `claim_audit.py` now runs **43/43 pass** against the fixed manuscript and the rerun E1 results.
