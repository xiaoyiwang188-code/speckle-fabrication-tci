# Idea Triage Bundle — Cross-Model Review Request

You are acting as an independent senior reviewer (computational imaging + ML). The executor generated the candidate ideas below and ran a pilot. Your job: rank them and allocate scarce validation resources. Do NOT rewrite the ideas.

## Context

- Direction: deep learning for imaging through scattering media (speckle-based), SCI journal target (Photonics Research / Optics Express / IEEE TCI).
- Executor strengths: inverse problems, deep learning, diagnostic/assessment methodology (prior paper: FPM joint self-calibration fixed-budget optimization-ambiguity diagnostics with INR).
- Occupied hilltops: Nat Commun 2026 (physical mechanisms of generalization/hallucination); Photonics Research 2026 14(4):1280 (universal generalization + quantitative assessment); Deep Speckle Correlation (Optica 2018); dynamic-scattering real-time imaging (LSA 2024 / Sci Adv 2024 / PR 2026, crowded); INR-for-speckle (arXiv:2304.00837, 2608.06574).
- Pilot evidence (CPU simulation, speckle grain 6px, MTF support 12px, 400 test images):
  - GT-bandwidth ablation (Idea 2 below): bandwidth-matched training cut out-of-band hallucinated energy 3.1x (ratio 0.32 < 0.5 criterion PASS), but in-band PSNR dropped 3.2 dB (criterion FAIL) -> pre-registered verdict MIXED. Sub-finding: PSNR ranking flips with reference bandwidth (half 35.5 > raw 31.5 > matched 28.3 dB) — reference-dependence is itself a publishable protocol finding.
  - Novelty pre-checks: Idea 2 no direct precedent found; Idea 1 no capacity-swept two-point audit found (Barbastathis 2019 review discusses priors-vs-information qualitatively); Idea 3 has a close prior (Tivnan 2024 "Hallucination Index", 52 citations, no-reference hallucination IQM reasoning about forward process) -> differentiation narrowed to speckle-operator information-band calibration + decoupling phase diagram.

## Candidates (19, deduped, all within pilot budget; fine-tune pilot design note: Idea 2's effect size may partly depend on fine-tune length — flagged)

1. **two-point-resolution-ceiling** (diagnostic, LOW): capacity-swept two-point resolution audit of DL speckle reconstruction anchored to speckle Rayleigh limit + linear inverse; Jacobian diagnostics. Prior: qualitative only in reviews.
2. **gt-bandwidth-mismatch-hallucination-ablation** (empirical, LOW): does training against band-unlimited GT *cause* measured hallucination? Pilot: 3.1x effect, MIXED verdict, reference-dependence sub-finding.
3. **inverse-consistency-hallucination-decoupling** (diagnostic, MEDIUM): ||H(x̂)−y|| as label-free hallucination flag, decoupling vs information band. Prior: Tivnan 2024 Hallucination Index is close.
4. **diffuser-class-statistical-distance-law** (diagnostic, MEDIUM): orthogonal-factor attribution of generalization loss (correlation length × height distribution × spectrum) + statistical-distance→transfer-loss law with changepoint-vs-monotone discrimination. Defines whether "same diffuser class" is statistically meaningful.
5. **conformal-sets-localize-speckle-hallucination** (diagnostic, LOW): split-conformal prediction sets calibrated on one diffuser class; do set-size maps co-localize hallucinations under class shift? Guarantee-backed abstention probe.
6. **memory-effect-vs-texture-attribution** (diagnostic, LOW): factorial perturbation protocol decomposing network fidelity into ME-exploitation vs texture prior vs content prior; operational ME-exploitation index.
7. **conv-prior-breakdown-phase-diagram** (diagnostic, LOW): phase diagram in (FOV × memory-effect width): where does failure stop being informational and become architectural (conv shift-invariance prior invalid)? Convolutional vs non-stationary decoder vs linear floor.
8. **photon-per-grain-speckle-crossover** (empirical, LOW): photons-per-speckle-grain sweep 0.01–100; locate statistical crossover where CNN decoders fail qualitatively; photon-aware input encoding repair test.
9. **metric-doping-certification-audit** (diagnostic, LOW): inject quantified physical defects (blur/warp/amplitude/texture) into reconstructions; measure which of PSNR/SSIM/LPIPS/VIF certify vs miss each class; minimal metric bundle recommendation.
10. **tm-determinism-vs-learned-prior-crossover** (empirical, LOW): calibrated transmission-matrix inversion vs CNN under controlled operator drift ε; locate crossover ε*; failure-mode classification (hallucination vs graceful blur).
11. **memory-effect-knee-vs-training-diversity** (empirical, LOW): does the generalization-vs-object-extent curve kink at the memory-effect angle (physics) or decay smoothly set by training diversity (statistics)? Variance decomposition.
12. **digit-benchmark-statistics-portability-audit** (diagnostic, MEDIUM): statistics-matched cross-family transfer matrix (MNIST/FashionMNIST/CIFAR/natural resampled to MNIST statistics); do digit benchmarks measure object generalization or object statistics?
13. **autocorrelation-consistency-test-time-adaptation** (method, MEDIUM): label-free TTA to unseen diffuser via autocorrelation-consistency loss (memory-effect regime); vs entropy-only TTA which may amplify hallucination.
14. **dps-psf-decomposition-of-speckle-networks** (empirical, MEDIUM): training-free DPS (generic prior + one-shot pinhole PSF calibration) vs end-to-end U-Net on novel diffusers: decomposes performance into prior knowledge vs learned forward knowledge.
15. **shift-equivariance-symmetry-leakage-speckle** (diagnostic, MEDIUM): do zero-padded CNNs exploit aperture-edge cues that don't transfer? Equivariance-imposed matched-pair audit. Potential overlap with Nat Commun 2026 mechanism analysis — verify first.
16. **integration-time-m-crossover** (empirical, MEDIUM): single-exposure integration M=T/τc as a regime axis (random-convolution-like ↔ blur-like); M-conditioned decoder vs per-M specialists; transfer asymmetry direction.
17. **temporal-memory-crossover-phase-diagram** (empirical, MEDIUM, weeks): frame-to-frame correlation ρ sweep; where do temporal models beat memory-less CNNs and where do they produce persistence hallucinations (alternating-content test)?
18. **thin-screen-vs-volumetric-substrate-transfer** (empirical, MEDIUM): matched-statistics thin-screen vs multi-layer volumetric speckle cross-substrate transfer matrix; is substrate fidelity a hidden confound in simulation-heavy training?
19. **double-layer-speckle-regime-transition** (empirical, MEDIUM, weeks): excitation+emission double scattering in fluorescence; decoder-family crossover map (single-PSF vs model-aware vs ghost/correlation baseline) aligned with measured PSF stationarity length.

## Your tasks

For each candidate, make the strongest case both ways:
- Best case FOR it — what would make this the paper people cite?
- Strongest objection a reviewer would raise?
- Most likely failure mode?
- Is the prior-work note a real novelty problem, or differentiable?

Then:
- Rank ALL 19 by expected information and upside within the pilot budget — which results would matter most, whichever way they come out?
- Which 2-3 would you actually work on, and why?
- Do not let your picks be uniformly the safest — name the high-upside idea that most deserves a pilot slot and what result would convince you.
- Rank; do not rewrite. An objection is answered or recorded as a named risk on the idea — never absorbed by adding modules.

## Required output format

1. A ranked list: rank number, dedup_key, one-line justification, novelty-risk LOW/MED/HIGH.
2. "TOP PICKS: <2-3 dedup_keys>" with a paragraph each on why and what result would convince you.
3. "ELIMINATION CANDIDATES: <dedup_keys with reasons>" (only if a prior-work note is a genuine kill).
4. "PILOT DESIGN CAVEATS" — anything in the pilot evidence you do not trust.
