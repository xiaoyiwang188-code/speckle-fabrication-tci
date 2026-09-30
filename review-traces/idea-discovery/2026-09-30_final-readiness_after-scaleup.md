# Final readiness assessment after scale-up - deepseek-v4-flash

## Response

**Round 4 final.**

**Q1. Honest score / readiness.**  
**TCI: 7/10 — submittable as-is**, with real data explicitly labeled preliminary.  
**Photonics Research: 6/10 — not as-is**; optics reviewers will press on the real-data scale mismatch.  
Blocking items: **0 for the simulation core.**  
For PR/experimental-speckle claims only, **1 blocking item**: add a scale-registration stage and recalibrate on a held-out DSC subset. Cost: **~2–3 days, <10 Colab hours**, not a full new campaign.  
E1 stays supporting/supplementary; E3 remains deferred.

**Q2. Thesis and figures.**  
Thesis: **Matched target-bandwidth fine-tuning suppresses out-of-band spectral fabrication in learned speckle imaging without degrading relative forward-model error, while raw fabrication grows with network capacity and Wiener reconstructions cannot match DL’s forward-fidelity operating point.**

Figures:
1. **Phenomenon/metric**: raw DL reconstruction vs measured MTF support; out-of-band spectral energy definition.
2. **Main control**: paired matched-fine-tune vs compute-matched control, matched/half target; 6/6 reductions; no-reference forward-residual inset.
3. **Capacity**: base16 vs base32 raw and fine-tuned OOB energy; larger net fabricates more absolutely and is suppressed more strongly.
4. **Wiener trade-off**: OOB vs relative forward error across Wiener sweep; DL 2–6× above Wiener OOB but ~10× better forward fidelity.
5. **Robustness/preliminary real data**: spatially varying PSF survival + DSC pairing signal, with scale-registration limitation.

**Q3. “Speckle” in title?**  
Yes, with **“learned speckle imaging”**, not **“experimental speckle reconstruction.”**  
Candidates:
- *Matched fine-tuning controls spectral fabrication in learned speckle imaging*
- *Spectral fabrication in learned speckle imaging: capacity effects and a compute-matched fine-tuning remedy*

**Q4. Exact abstract hedges required.**  
- “In our simulated protocols…” for every main quantitative claim.  
- “Out-of-band spectral energy is a fabrication proxy; it is not a semantic or perceptual metric.”  
- “Real-data evidence is preliminary: the pairing signal is present, but forward calibration has a scale mismatch; quantitative real-data reconstruction requires scale registration.”  
- “These conclusions are limited to the architectures, training budgets, and bandwidths tested.”  
- Optional: “Matched fine-tuning did not increase no-reference relative forward-model error (+0.026).”

**Q5. Bottom line.**  
**Submit now to TCI** with real data framed as preliminary; if you require a Photonics Research experimental-speckle claim, do the 2–3 day scale-registration fix first — not another full round.
