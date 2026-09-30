# Cover Letter — draft for IEEE TCI submission

*(Copy into the submission system's cover-letter field or export as PDF. Replace bracketed placeholders.)*

---

Dear Editor-in-Chief,

We submit for consideration in the *IEEE Transactions on Computational Imaging* the manuscript:

**"Matched Fine-Tuning Controls Spectral Fabrication in Learned Speckle Imaging: Capacity Effects and a Compute-Matched Remedy"**

by [Author names].

**Contributions.** Learned reconstruction through scattering media can spectrally fabricate content the measurement cannot contain, a phenomenon increasingly discussed but never isolated as a controllable training-time choice. This paper (i) establishes the bandwidth of the training target as a *causal, compute-matched* control of out-of-band spectral fabrication, reducing it to 0.34±0.11 (matched) and 0.20±0.08 (half) of an identical-initialization control across two architectures and three seeds (6/6 units, sign test p≈0.016); (ii) shows fabrication grows with capacity in the tested range and that bandwidth-matched targets reclaim it; (iii) anchors the result against a Wiener linear baseline across a six-cell regularization/support grid, characterizing the fabrication/forward-fidelity trade-off; (iv) reports a negative control showing no cross-diffuser "class boundary," motivating protocol-level (measured bandwidth, measured distance) reporting; and (v) quantifies a real-data boundary condition on a public experimental dataset, identifying the forward-calibration requirement explicitly.

**Fit with TCI.** The work is protocol- and audit-centered rather than architecture-centered: its central quantities are defined against the measured MTF support of the system, and its claims are established under pre-registered, compute-matched controls with no-reference endpoints. We believe this methodological focus matches TCI's scope at the intersection of image formation and computation. Code, figure-generation scripts, and all raw result files are available to support reproducibility and can be provided as supplementary material.

**Declarations.** This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission and declare no conflicts of interest. Portions of this work were [supported by grant/acknowledgment info, or: conducted without external funding].

**Suggested reviewers.** [Enter 3–5 names/affiliations/emails — recommended profile: researchers active in computational imaging through scattering (speckle/TM/memory-effect), deep-learning-based inverse problems, or hallucination/uncertainty evaluation in learned imaging. Please avoid collaborators and same-institution colleagues.]

Sincerely,
[Corresponding author name, affiliation, email]
