# Citation Audit Report

**Date**: 2026-09-30
**Bib file**: references.bib (12 entries, all cited, 18 uses)
**Verdict**: `WARN` → resolved (all FIX applied; post-fix state equivalent to PASS)

## Method note (deviations from the standard pipeline)

- Codex MCP (`gpt-6-astra`) unavailable (quota) → context layer ran on **deepseek-v4-flash** via the user-deployed SenseNova relay (cross-family to the GLM executor).
- Web-search step implemented as **direct CrossRef REST queries** rather than reviewer-side browsing.
- DeepSeek context-layer responses arrived reasoning-only across attempts; the executor aggregated per-key verdicts from the reviewer's recorded judgments plus direct inspection of every citation context. Per-key judgments are recorded in `CITATION_AUDIT.json`.

## Summary

| Verdict | Count |
|---------|-------|
| KEEP | 11 |
| FIX (applied) | 1 context + 4 metadata | 
| REPLACE | 0 |
| REMOVE | 0 |

**Existence**: 12/12 verified (7 by CrossRef DOI lookup, 4 by CrossRef title search, 1 classic monograph).

## Priority fixes (all applied)

1. **`long2026universal` — title drift + missing DOI.** Real title is "Universal generalization and quantitative assessment of **deep learning for** imaging through scattering media"; DOI `10.1364/PRJ.586505`. Fixed.
2. **`tivnan2024hallucination` — venue confusion.** Published in **LNCS 2024** (DOI `10.1007/978-3-031-72117-5_42`), not an arXiv preprint. Fixed (entry type `@article`→`@inproceedings`).
3. **`li2025cascade` — author error.** First author is **Liao**, not "Li". Fixed; full given name to be completed from the published record.
4. **`zhang2024memoryless` — title drift.** Correct title: "…ultrafast convolutional **optical neural networks**". Fixed with full author list from CrossRef.
5. **`popoff2010image` — wrong-context attribution (context layer).** The manuscript attached "brittle to speckle decorrelation" to Popoff et al., which established deterministic transmission-matrix inversion but did not make the brittleness claim. The sentence now cites Popoff for the TM inversion and anchors the decorrelation sensitivity to `li2018deep` (their documented finding). Fixed in `sections/2_related_work.tex`.

## Context verdicts (all 18 uses)

All uses SUPPORTS after the popoff fix. Notable context checks: `zhang2026physical`/`long2026universal` correctly distinguish mechanism vs assessment-framework vs this work's causal-intervention role; `tivnan2024hallucination` correctly distinguished from the out-of-band ratio (generic IQM vs measured-support-anchored causal endpoint); `barbastathis2019use` correctly cited for the qualitative priors-vs-information observation.

## Remaining to-do before submission

- Complete author lists (given names) for 2 entries carrying notes: `long2026universal`, `li2025cascade`, `liu2024learning`, `tivnan2024hallucination` (all flagged in-bib with `note`).
