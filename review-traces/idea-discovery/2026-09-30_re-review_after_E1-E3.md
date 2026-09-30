# Re-review after E1-E3 — deepseek-v4-flash via sensenova relay

## Response

1. **Reshape yes, but A is not co-lead.** E1 killed the original monotone-boundary claim; the “smooth multi-factor” story is post hoc from 12 families / 144 correlated pairs, with null changepoint signals. It supports “class labels are arbitrary cuts” only as a caution, not as a headline law. **A becomes a supporting/motivational section; B is lead.**

2. **Top-3 reviewer attacks**
   - **A overreach:** 12 diffuser families, non-significant monotone tests, then redefinition as “multi-factor smooth function”; no held-out family split → unfalsifiable/post hoc.
   - **Simulator/physics validity:** E3 showed the shift-invariant simulator has no physical memory-effect boundary. Without real scattering data or a spatially varying PSF simulation, “speckle” claims reduce to a generic band-limited inverse-problem testbed.
   - **B endpoint/causal language:** “Out-of-band energy ratio” and the Wiener baseline are not hallucination ground truth; E2 varied fine-tune duration, not a full bandwidth dose-response; “causally controls bandwidth” overclaims; “full-band references are artifacts” is too strong.

3. **Minimum scale-up before submittable**
   - **Required:** A: ≥36 diffuser families, 3 seeds, explicit held-out families, surrogate transfer-loss regression tested on held-out pairs. B: 2 architectures × 3 seeds × 3 target bandwidths × {baseline, raw-cont, matched fine-tune}, plus a Wiener hyperparameter/support sensitivity sweep.
   - **Required if “speckle” stays in the title:** at least one real scattering-data or spatially varying PSF check. Otherwise retitle to “band-limited inverse problem.”
   - **Nice-to-have:** 5 seeds, 3+ architectures, two real datasets, integration of A’s distances into B’s endpoint predictions.
   - **GPU estimate:** A ≈ 108 full runs; B ≈ 13–25 full-run equivalents → ~120–135 full runs. At 0.5–1 GPU-h/run, **≈60–135 A100-GPU-h**; 5-seed/3-arch nice scale-up ≈250 GPU-h.

4. **No—do not promote 4.5× to headline yet.** The headline should be the matched/control causal reduction in out-of-band energy. 4.5× is a secondary quantitative anchor, and it remains a single-estimator ratio until Wiener regularization/support sensitivity and a second classical linear baseline are checked.

5. **Proceed to scale-up of reshaped A+B exactly as conditioned—A as support, B as lead, C deferred—and keep “speckle” out of the title until the real scattering/spatially varying PSF check is done.**
