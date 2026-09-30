# Idea Generation Bundle — Imaging Through Scattering Media

You are a senior ML/optics researcher brainstorming research ideas.

## Research direction
Deep learning methods for imaging through scattering media (speckle-based computational imaging), targeting SCI journals (Photonics Research / Optics Express / IEEE Transactions on Computational Imaging / Optics Letters). The executor's strengths: inverse problems, deep learning, diagnostic/assessment methodology (prior work: FPM joint self-calibration optimization-ambiguity analysis with INR parameterization).

## Current verified landscape

| # | Paper | Venue | Core contribution |
|---|-------|-------|-------------------|
| 1 | Deep Speckle Correlation (Li, Xue, Tian) — arXiv:1806.04139 | Optica 2018 | "One-to-all" statistical DL: train on a class of diffusers, generalize across same-class media |
| 2 | Zhang et al., "Physical mechanisms governing generalization and hallucination in DL for imaging through scattering media", DOI 10.1038/s41467-026-72304-z | Nat Commun 2026 | Physical explanation of why DL generalizes/hallucinates across scattering conditions |
| 3 | Long et al., "Universal generalization and quantitative assessment of imaging through scattering media", PRJ 14(4):1280 | Photonics Research 2026 | MIMO framing + universal generalization benchmark + quantitative assessment protocol |
| 4 | Liu et al., "Learning-based real-time imaging through dynamic scattering media" | Light Sci Appl 2024 | Real-time imaging under dynamically changing scattering |
| 5 | Zhang et al., "Memory-less scattering imaging with ultrafast CNNs", DOI 10.1126/sciadv.adn2205 | Sci Adv 2024 | Memory-less assumption → ultrafast CNN, no accumulation across frames |
| 6 | "Disorder-invariant Implicit Neural Representation" — arXiv:2304.00837 | 2023 | INR made invariant to medium disorder |
| 7 | "Implicit Neural Speckle Denoising" — arXiv:2608.06574 | 2026-08 | INR parameterization for speckle denoising |
| 8 | [UNVERIFIED] Support-free speckle-correlation imaging with INR | recent | INR for speckle reconstruction without object-support prior |
| 9 | [UNVERIFIED] Transfer learning for speckle reconstruction | IEEE Access 2024 | TL across scattering conditions |
| 10 | [UNVERIFIED] Speckle Transformer | Adv. Photonics Nexus 2025 | Classification through scattering with limited data |
| 11 | "Universal sensitivity of speckle intensity correlations to wavefront change" — arXiv:1610.01671 | 2016 (classic) | Theory: speckle correlations sensitivity to wavefront changes |

## Occupied hilltops (must differentiate, not avoid)
- "Universal generalization + quantitative assessment of reconstruction quality" — occupied by #3
- "Physical mechanism of generalization/hallucination" — occupied by #2
- Real-time dynamic scattering — heavily crowded (#4, #5, ScatteringODNN PR 2026)
- "INR applied to speckle" as such — no longer novel (#6, #7, #8)

## Preliminary gaps (candidate angles — verify, refine, or propose better ones)
- G1: reliability declaration / abstention at inference time: "when should we NOT trust a speckle reconstruction?" (no ground truth available in real experiments)
- G2: continuous drift of a scattering medium (multi-parameter coupled drift: angle + thickness + wavelength simultaneously) — systematic diagnosis absent
- G3: polarization/spectral dimension generalization
- G4: task-level (downstream application) evaluation vs reconstruction-metric evaluation
- G5: identifiability/ambiguity analysis of INR parameterizations in speckle inverse problems (executor's strength)
- G6: cross-device / cross-wavelength evaluation protocol standardization

## Your task
Generate 8-12 concrete research ideas. For each idea:
1. One-sentence summary
2. Core hypothesis (what you expect to find and why)
3. Minimum viable experiment (cheapest way to test; simulation-heavy is fine)
4. Expected contribution type: empirical finding / new method / theoretical result / diagnostic
5. Risk level: LOW (likely works) / MEDIUM (50-50) / HIGH (speculative)
6. Estimated effort: days / weeks / months

Prioritize ideas that are:
- Testable with moderate compute (1 GPU ≤ 2h for a pilot; simulation-based OK)
- Likely to produce a clear positive OR negative result (both publishable)
- Simple at the core: one mechanism, few moving parts
- Aware of the papers above — awareness, not avoidance
- Genuinely creative: surprising connections, inverted assumptions, questions nobody asked. A bold idea with a named risk beats a hedged one with none.

Output format: numbered list, each idea with fields 1-6 above.
