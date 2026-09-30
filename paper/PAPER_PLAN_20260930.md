# Paper Plan

**Title**: Matched Fine-Tuning Controls Spectral Fabrication in Learned Speckle Imaging: Capacity Effects and a Compute-Matched Remedy
**One-sentence contribution**: Training against bandwidth-matched targets causally suppresses out-of-band spectral fabrication in learned speckle reconstruction without degrading (no-reference) forward-model error; fabrication grows with network capacity, and Wiener reconstruction occupies a distinct fidelity/fabrication trade-off point.
**Venue**: IEEE Transactions on Computational Imaging (TCI)
**Type**: empirical / diagnostic (protocol + audit)
**Date**: 2026-09-30
**Page budget**: ~13 pages including references (IEEE journal Transactions; references counted)
**Style**: IEEEtran, `\cite{}` numeric
**Section count**: 6 (Abstract + §1 Intro, §2 Related, §3 Setup/Protocol, §4 Experiments incl. §4.6 negative control, §5 Real-Data Assessment, §6 Discussion/Limitations/Conclusion)

## Claims–Evidence Matrix

| # | Claim | Evidence | Status | Section |
|---|-------|----------|--------|---------|
| C1 | Bandwidth-matched fine-tuning (causal intervention) reduces out-of-band spectral fabrication: ratio 0.34±0.11 (matched) and 0.20±0.08 (half) vs compute-matched control, **6/6 units, one-sided sign test p≈0.016** | Scale-up (2 arch × 3 seeds); E2 sweep (0.52/0.49/0.50 stable); pilot 3.1× | **Supported** (core) | §4.2 |
| C2 | In the two tested capacities, raw fabrication was higher for the larger net (0.026 vs 0.015) and matched suppression was stronger (0.23 vs 0.44) — described as observed capacity trend, not a scaling law | Scale-up | **Supported (bounded)** | §4.3 |
| C3 | Wiener reconstruction occupies a distinct operating point: oob 0.0003–0.0032 (2–6× below DL, robust across K/support grid) but relative forward error 4.4–8.9 vs DL 0.37–0.47 | Wiener sensitivity sweep (6 cells) | **Supported** | §4.4 |
| C4 | The causal intervention does not degrade the no-reference forward-consistency endpoint (mean diff +0.026 vs control; sign test p≈0.016 for no-degradation direction) | Scale-up paired stats | **Supported** | §4.2 |
| C5 | (Negative control, half-page in §4.6; full matrix → supplement) Cross-diffuser transfer loss varies smoothly with statistical distance; no changepoint; single distances are suggestive of, but not proven jointly incomplete (downgraded per review) | E1 (12 diffusers, 3 metrics, perm p 0.14/0.92/0.33) | **Supported (negative result, bounded)** | §4.6 |
| C6 | The effect survives a position-dependent (spatially varying PSF) forward operator | E4 (0.52/0.60/0.54) | **Supported** | §4.5 |
| C7 | Real-data collateral: measured system parameters (grain FWHM 1.93 px, ~52% Nyquist support, ME ~191 px) and pairing statistics are quantifiable, but quantitative real-data reconstruction requires a dedicated forward-calibration stage (unparseable-mapping datasets) | DSC 240-file study + 3 failed registration methods | **Preliminary / limitation** | §5 |

**Honesty notes**: C1–C4, C6 simulation-based (documented protocol). "Out-of-band energy" is a fabrication proxy — not a semantic/perceptual metric. Real-data quantitative claims are explicitly preliminary.

## Abstract Draft (~150 words)

Learned reconstruction through scattering media reports steadily improving fidelity, yet a reconstruction can spectrally invent content the measurement cannot physically contain. We isolate a free preprocessing choice — the bandwidth of the training target — as a causal control of this fabrication. In a controlled speckle-imaging protocol with a compute-matched control (identical initialization, identical extra optimization), fine-tuning against bandwidth-matched targets reduces the reconstruction's out-of-band spectral energy to 0.34±0.11 (matched) and 0.20±0.08 (half) of the control across two architectures and three seeds (6/6 units), without degrading a no-reference forward-consistency endpoint. Raw fabrication and suppression strength both increase in the larger of the two tested capacities. A Wiener linear baseline constrains the fabrication budget (2–6× below the learned models) but operates at far lower forward fidelity (relative error 4.4–8.9 vs 0.37–0.47), and a cross-diffuser distance-law analysis shows no class boundary — supporting protocol-level rather than label-level reporting. Real-data assessment is preliminary and motivates a dedicated forward-calibration stage. Out-of-band energy is a fabrication proxy, not a perceptual metric.

## Structure

### §1 Introduction (~1.5 p)
- Hook: learned reconstruction is the default for speckle imaging; reported fidelity numbers are rising, but a reconstruction can invent spectral content the measurement cannot contain (hallucination literature 2024–2026).
- Gap: existing work explains *why* fabrication happens physically (Nat Commun 2026) or proposes assessment frameworks (PR 2026), but no *causal, protocol-level control knob* with a compute-matched design has been demonstrated; reference bandwidth of the training target — a free preprocessing choice — has not been isolated as a causal factor.
- One-sentence contribution (above). Contributions bullets: (1) causal GT-bandwidth intervention with compute-matched control + no-reference endpoints; (2) capacity–fabrication scaling result; (3) Wiener-anchored fabrication quantification + fidelity/fabrication trade-off characterization; (4) supporting distance-law negative result; (5) robustness (spatially varying PSF) + real-data assessment with documented limitation.
- Hero figure = Figure 1 (see plan). Key citations: DSC (Li 2018), Nat Commun 2026, PR 2026, LSA 2024/Sci Adv 2024, Tivnan 2024.

### §2 Related Work (~1 p)
- Three families: (a) speckle/scattering reconstruction with DL (Optica 2018 lineage; dynamic-scattering real-time line); (b) hallucination/fabrication and evaluation in learned imaging (Nat Commun 2026; PR 2026; Hallucination Index 2024; metric audits); (c) forward-model-informed protocols and linear baselines (Wiener/deconvolution; memory-effect theory).
- Positioning (per review): low-pass/filtered training targets are a known practical stabilization trick elsewhere — add 2–3 sentences distinguishing this work: prior filtered-target practices were (i) not analyzed as a causal control for spectral fabrication, (ii) not quantified against measured MTF support, (iii) not compared against a compute-matched raw-continued control from identical initialization. Also state explicitly how the out-of-band energy ratio differs from Tivnan's Hallucination Index (ours is anchored to the measured system MTF support and used as a causal-intervention endpoint, not a generic no-reference quality metric).
- Positioning summary: we do not propose a new architecture or another assessment framework; we make the *training-target bandwidth* an experimentally controlled variable with a compute-matched causal design and quantify fabrication relative to its measured information support and to a linear baseline.

### §3 Problem Setup and Protocol (~1.5 p)
- Speckle forward model (shift-invariant intensity PSF; aperture-limited; Poisson-Gaussian noise); MTF support radius R from aperture geometry (2r analytic, cross-checked empirically).
- Definitions: out-of-band spectral energy ratio (fabrication proxy); relative forward-consistency ‖H(x̂)−y‖/‖y‖ (no-reference endpoint); band-limited PSNR (secondary).
- The intervention: fine-tuning arms {raw-continued control (compute-matched), matched (0.9·σ_MTF), half (0.45·σ_MTF)}; identical init/seed; pre-registered decision rules.
- Architectures (residual U-Net base 16/32), seeds, budgets. Note on the residual-skip design (eliminates the all-zero attractor; validated).

### §4 Experiments (~4 p)
- §4.1 Baselines: monotone ordering raw > matched > half in oob (0.021 / 0.0066 / 0.0036) with PSNR inversion (16.5 / 31.7 / 22.1) — the reference-dependence phenomenon.
- §4.2 Main control: paired fine-tune vs compute-matched control, 6/6 reductions; ratios 0.34±0.11 / 0.20±0.08; forward-consistency non-degradation (+0.026). Figure 2.
- §4.3 Capacity: base16 vs base32 (Figure 3).
- §4.4 Wiener anchor and trade-off: K×support grid; Figure 4.
- §4.5 Robustness: spatially varying PSF (E4); fine-tune sweep stability (E2).
- §4.6 Negative control (½ page): E1 in one paragraph — no changepoint under three distance metrics; class labels are arbitrary cuts; full transfer matrix → supplement. One intro sentence references this to forestall the "diffuser-distance explanation".
- Table: ONE combined summary float (all arms + paired statistics with sign-test p-values).
- Hard cap: §4 text + Figures 2–4 + Table 1 must fit in 4 pages.

### §4.6 (was §5 Distance-Law; merged per review)

### §5 Real-Data Assessment (~0.75 p)
- DSC 240-file study: measurable system parameters; pairing statistics (0.10–0.18 vs 0.05–0.11); three registration methods failed; documented interpretation: end-to-end-mapping datasets require a dedicated forward-calibration stage before bandwidth-protocol claims can be made quantitatively. Framed as a boundary condition + roadmap item, not a result.

### §6 Discussion, Limitations, Conclusion (~1.5 p)
- Limitations (mandatory hedges): simulated protocols; oob is a proxy; tested architectures/budgets/bandwidths only; real data preliminary; single noise model; no natural-image objects yet.
- Future work: natural-object extension; real-data forward calibration; temporal integration regime (M-crossover).
- Conclusion.

## Figure Plan

| ID | Type | Description | Data Source | Priority |
|----|------|-------------|-------------|----------|
| Fig 1 | Hero (3-panel triptych) | (a) measured MTF support with radial-spectrum overlay of a reconstruction, out-of-band region shaded — the definition; (b) raw-GT vs matched-GT reconstruction pair from identical initialization with oob visibly suppressed; (c) small bar chart: oob ratio control/matched/half | scale-up runs + protocol figure | HIGH |
| Fig 2 | Scatter+paired lines | Paired finetune vs control per unit (6 points, matched & half), connecting lines; inset: relative forward-consistency (no-reference) unchanged | scaleup_results.json | HIGH |
| Fig 3 | Bar+scatter | oob by arm for base16 vs base32 (raw baseline, control, matched-ft) — observed capacity trend | scaleup_results.json | HIGH |
| Fig 4 | Scatter (trade-off) | oob vs relative forward error: Wiener grid (6 cells) vs DL arms; annotate 2–6× fabrication gap, ~10× forward-fidelity gap | scaleup_results.json | HIGH |
| Fig 5 | Two-panel robustness | (a) E4 spatially-varying PSF ratios; (b) real-data: speckle autocorr profile (grain + platform) + pairing NCC distribution | e4 + dsc results | MEDIUM |
| Table 1 | Combined summary | All arms (mean±std oob, PSNR, n=6) + paired statistics (ratios, 6/6, sign-test p≈0.016) in one float | scaleup_results.json | HIGH |

Hero-figure caption draft: "Training-target bandwidth controls spectral fabrication. (a) Out-of-band energy ratio = reconstruction spectral energy outside the measured MTF support (shaded); it quantifies fabrication beyond what the measurement can contain. (b) From an identical initialization, the model fine-tuned against bandwidth-matched targets fabricates visibly less out-of-band content than the compute-matched raw-target control. (c) Suppression ratios across both architectures and all seeds. Out-of-band energy is a fabrication proxy, not a perceptual metric."

## Citation Plan

- §1: Li/Tian Optica 2018 (DSC); Zhang Nat Commun 2026; Long Photonics Research 2026; Liu LSA 2024; Zhang Sci Adv 2024; Tivnan 2024 (Hallucination Index); Barbastathis 2019 review.
- §2: + Goodman speckle theory; memory-effect literature (Freund 1988; Bertolotti 2012 / Katz 2014 lineage); Wiener; U-Net (Ronneberger 2015); CNN-optics reviews.
- §3: forward-model conventions (DSC; Loetgering/Zhou FPM-adjacent conventions as needed).
- §6: DSC Zenodo datasets (15361263; 14939667).

All citations to be verified before writing (no BibTeX from memory; reuse/extend `论文项目/01_文献/references.bib` with verified metadata).

## Reviewer Feedback

**[Round 6 — DeepSeek outline review, `2026-09-30_outline-review.md`]** Scores: flow 8 / claim-evidence 7 / missing-exp 7 / positioning 8 / budget 7 / front-matter 7. **Verdict: GO with revisions.** Applied: (1) abstract drafted (150 words, real numbers) + hero figure redesigned as 3-panel triptych; (2) C2 reworded to bounded "two tested capacities" claim, sign-test p≈0.016 added to C1/C4, C5 downgraded to bounded/suggestive; (3) §5 compressed into §4.6 half-page (full matrix → supplement), Table 1+2 merged into one float, §2 positioning extended (filtered-target precedent + Hallucination Index differentiation). Deferred (documented): base8 third capacity arm and USAF-phantom visual panel — noted as scale-up options if compute allows; softened "scales" language covers their absence.

## Next Steps
- [ ] Outline review by DeepSeek (cross-model) → apply
- [ ] `/paper-figure` for Figures 1–5 + Tables 1–2 from `results/scaleup_results.json` + e4/dsc results
- [ ] `/paper-write` LaTeX (IEEEtran) drafting from this plan
- [ ] `/paper-compile` build PDF
