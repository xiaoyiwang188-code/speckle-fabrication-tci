# Reproduction & Review Pack — "Matched Fine-Tuning Controls Spectral Fabrication in Learned Speckle Imaging"

**For the receiving AI**: this pack contains a complete, self-contained research artifact: paper source, all experiment code, all raw result files, and the audit trail. Two tasks are expected: **(A) reproduce the headline numbers**, and **(B) adversarially review the claims**. A review guide with the honest boundary list is at the end — start there for task B.

All experiments run on **CPU alone** (torch CPU); the scale-up ran on a Colab T4 but every script also runs on CPU at reduced speed.

## Pack structure

```
paper/                  LaTeX source (IEEEtran), 7-page PDF, figures + generation scripts
  main.tex, sections/*.tex, references.bib, figures/*.pdf
  figures/gen_fig*.py   → regenerate every figure from results/ (source of truth)
  CITATION_AUDIT.md/.json, CLAIM_AUDIT.md/.json  → prior audits (verify, don't trust)
  COVER_LETTER.md
experiments/            all experiment code
  sim_common.py         shared simulation infra (PSF, objects, UNet, metrics)
  pilot_gt_bandwidth.py first pilot (the 3.1x seed result)
  e1_transfer_matrix.py distance-law negative control (§4.6)
  e2_finetune_sweep.py  fine-tune-length sweep (§4.5)
  e4_spatially_varying.py spatially-varying PSF robustness (§4.5)
  s1a/s1b/s1c, unit.py, s0.py  Colab scale-up stages (§4.2-4.4)
  scaleup_b_colab.py    single-file Colab version of the whole scale-up
  claim_audit.py        47-check numeric audit of the manuscript
  e1_sensitivity.py     collapse-exclusion sensitivity analysis (§4.6)
  pairing_stats.py      real-data pairing statistics (see DATA.md)
results/                raw outputs (source data for every number in the paper)
  scaleup_results.json  36 runs + paired stats + Wiener sensitivity
  scaleup_units/*.json  6 per-unit raw files (auditable unit level)
  e1_stdout.txt / e2_stdout.txt / e4_stdout.txt   stage outputs (JSON inside markers)
  registration_fix{,2,3}.txt  real-data registration attempts (negative results)
  claim_audit_output.txt, claim_audit.json
idea-stage/IDEA_REPORT.md      full idea-discovery record (incl. reviewer verdicts)
refine-logs/              FINAL_PROPOSAL.md, EXPERIMENT_PLAN.md (pre-registration), EXPERIMENT_TRACKER.md
traces/                   cross-model review transcripts (DeepSeek rounds)
artifacts/dsc_data/       sampled real experimental data (DSC; 240 files, ~28 MB)
```

## Environment

- Python 3.12; `torch` (CPU ok), `numpy>=2`, `Pillow`, `matplotlib`; **note:** numpy 2.x removed `ndarray.ptp()` — scripts here already use `np.ptp`.
- Font: scripts prefer `arial.ttf`, fall back to DejaVu/Liberation. On Linux, install `fonts-dejavu` for identical object renders.
- LaTeX: `latexmk` + IEEEtran (MiKTeX/TeX Live) for the paper PDF.

## A. Reproduce — command list (in order, from pack root)

```bash
# 1. Headline causal result + all baselines + Wiener sweep (paper §4.1-4.4)
#    CPU: ~2-3 min per unit; JSON printed between SCALEUP/UNIT_JSON markers.
python experiments/claim_audit.py            # 43 cross-checks of the manuscript vs results/
                                            # expect: 39 pass, 4 flagged (3 fixed in paper, 1 audit-scope)
# 2. Regenerate every figure (needs results/ + paper/figures/)
python paper/figures/gen_fig2.py && python paper/figures/gen_fig3.py \
  && python paper/figures/gen_fig4.py && python paper/figures/gen_fig5.py \
  && python paper/figures/gen_fig1.py       # fig1 retrains 2 small models (~3 min CPU)
python paper/figures/gen_table1.py > paper/figures/TABLE_1_main.tex
# 3. Rebuild the paper
cd paper && latexmk -pdf -interaction=nonstopmode main.tex   # → main.pdf, 7 pages
# 4. (optional) rerun raw experiments end-to-end
python experiments/e1_transfer_matrix.py   # ~6 min CPU: distance-law negative control
python experiments/e2_finetune_sweep.py    # ~2 min: fine-tune sweep + Wiener
python experiments/e4_spatially_varying.py # ~10 min: spatially-varying robustness
```

**Number-of-record mapping** (verify each against `results/`):

| Paper claim | File → field |
|---|---|
| matched ratio 0.34±0.11, half 0.20±0.08, 6/6, +0.026 | `results/scaleup_results.json` → `paired_stats_finetune_vs_control` |
| baselines 0.0210/0.0066/0.0036; PSNR 16.5/31.7/22.1 | same → `baselines` |
| capacity 0.027 vs 0.015; 0.030 vs 0.017; ratios 0.25/0.44 | same → `runs_raw` grouped by `arch` |
| Wiener oob 0.0003–0.0032 (nonzero; 2 of 6 at 0), 2–6× below raw/matched; rescaled rel-fwd 0.52–0.55 | same → `wiener_sensitivity`; rescaling recomputed live in `claim_audit.py` |
| E4 ratios 0.522/0.596/0.544 | `results/e4_stdout.txt` |
| E2 sweep 0.522/0.486/0.498 | `results/e2_stdout.txt` |
| ΔBIC −1.4/+5.6/+3.3; p 0.08/0.91/0.41; max loss 15.0 dB (E1 run3) | `results/e1_stdout.txt` → `fits`, `pairs` |
| E1 collapse-exclusion sensitivity (ΔBIC −1.1…+0.6, p 0.11–0.18) | `results/e1_sensitivity.txt` |
| real-data NCC pairing (0.60 vs 0.50, Welch t=3.2) | `results/registration_fix3.txt` |
| pixel-level pairing null result (same/mismatched means within ~0.01) | `results/pairing_stats_output.txt` |
| grain 1.93 px; platform 190.6 px; CV 1.02 | `results/registration_fix2.txt`, `registration_fix3.txt` |

## B. Review guide — where this work is vulnerable (stated honestly)

1. **Simulation-only causal claim.** The bandwidth intervention is established under a shift-invariant speckle model with one noise model, 64×64 images, two widths, three seeds, digit objects. Check: does §4.5's spatially-varying variant (E4, quadrant-blended PSFs) adequately support the robustness claim, or is it too different in scale/level (single seed, ratios 0.52–0.60 vs main 0.34 — the paper explicitly says levels are not comparable)? E4 script: `experiments/e4_spatially_varying.py`.
2. **The 3.1× vs 0.34 drift.** The first pilot reported a 3.1× reduction (ratio ≈0.32); the controlled scale-up reports 0.34±0.11. Check `pilot_gt_bandwidth.py` vs the scale-up: pilot used from-scratch matched training at a different budget; the scale-up used the compute-matched fine-tune design. Verify the paper never conflates the two (it should cite 3.1× only from pilot context — confirm).
3. **Out-of-band energy is a proxy.** It is anchored to the measured MTF support but is spectral, not perceptual. Check that no passage claims perceptual or semantic fidelity from it.
4. **Capacity trend is two points.** 0.027 vs 0.015 across base16/32 with 3 seeds each — the paper says "observed trend, not a scaling law." A reviewer could ask for base8/base64: this is an acknowledged, deliberate scope bound.
5. **Wiener comparison protocol.** The manuscript reports rescaled rel-fwd 0.52–0.55 after our own audit caught a normalization artifact (an earlier draft said "order of magnitude"). Verify the rescaling code in `claim_audit.py` (optimal scalar α) is the fair comparison and the text matches the recomputed numbers.
6. **Real-data section is deliberately non-quantitative.** Three registration methods failed (documented in `registration_fix*.txt`); the paper reports system parameters + pairing statistics only. Check the paper does not overstate this; the "unparseable-mapping dataset" interpretation is an inference from failure patterns, not a proven property of DSC.
7. **Claim audit history.** `CLAIM_AUDIT.md` lists 3 manuscript errors our own audit caught and fixed (control 0.0213→0.0238; 5.8→5.9×; rel-fwd range). Verify the fixed values in the current `sections/*.tex` against `results/` — the audit is our evidence, not a guarantee; re-derive independently.
8. **Citation layer.** `CITATION_AUDIT.md` documents one context-fix (popoff2010image) and four metadata corrections. DOIs are listed in `references.bib`; re-verify via CrossRef if you care about the bibliography.

## Revision history — external adversarial review round 1 (2026-09-30)

An external reviewer reproduced all headline numbers (39/43 automated checks matched the archive exactly) and flagged the following. **All items below are already fixed in this pack's current state**:

| # | Finding | Resolution |
|---|---|---|
| F1 | "order-of-magnitude worse" residue in §6.1 discussion text + Fig 4 caption contradicted the corrected 1.4× claim | both rewritten to "roughly 1.4× (~40%) worse" |
| F2 | "2–6× below every learned arm" overbroad: the half-bandwidth arm (0.0036) is within ~1.1× of the worst Wiener cell (0.0032) | scoped to "raw-target and matched arms; the half-bandwidth arm approaches the Wiener range" (abstract, intro, §4.4, Fig 4 caption) |
| D1 | capacity point estimates rounded low (base32 raw 0.026→0.027; control 0.028→0.030; ratio 0.23→0.25) | corrected in §4.3 and in `claim_audit.py` expected values |
| D2 | pixel-level pairing correlations (0.10–0.18 vs 0.05–0.11) were not reproducible from any file in the pack; recomputation shows the two groups nearly overlap | §5 now cites the autocorrelation-NCC pairing evidence (0.60 vs 0.50, Welch t=3.2, reproducible from `results/registration_fix3.txt`); `experiments/pairing_stats.py` added so the pixel-level null result is also reproducible |
| F3 | E1 transfer matrix contained one collapsed decoder (index 6 = [r6, binary, smooth0]: constant-by-group PSNR row) | root-caused to a phase-parameterization bug in `make_psf`'s binary branch (`exp(i·2π·(±π))` gives an effective ±0.89 rad weak phase instead of ±π), which produced a low-contrast, strong-pass-through PSF; fixed (`sign·0.5` → effective ±π), a collapse guard (output-std + reseed retry) added, and E1 rerun; prior runs archived as `results/e1_stdout_run{1,2}_*.txt`; §4.6 numbers updated from the rerun |
| F4 | rel-fwd "0.36–0.40" baseline range silently excluded the half-baseline (0.468) | exclusion now stated explicitly in §4.2 |

**Known false-friend in the harness**: the sending machine's security hook flags in-code file writes as "path traversal"; this pack's scripts print JSON to stdout and file-writing is done via shell redirection. If you see `open("...","w")` inside a script, that script predates that policy — flag it, don't run it blindly.

## What is NOT in this pack

- The full 13.9 GB DSC dataset (only the 240-file sample under `artifacts/dsc_data/`; full: Zenodo record 15361263).
- Colab/GPU session credentials (scale-up scripts run identically on CPU, slower).
- The `.aris/` pipeline state and hooks (ZCode-specific, not needed for reproduction).

## Contact-of-record

If a number here does not match `results/`, the files in `results/` are the source of truth — treat any mismatch as a bug in the manuscript or the scripts, and report it.
