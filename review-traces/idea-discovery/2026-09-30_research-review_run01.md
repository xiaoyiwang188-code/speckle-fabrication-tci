# Research review trace — deepseek-v4-flash via sensenova relay

## Response

## Review summary

This is a well-composed, protocol-first program. The strongest part is that all three components are designed to be informative regardless of sign. The risk is not lack of novelty; it is that the inferential links between the three components are under-specified, and the current plan still allows several “law/knee/hallucination” claims to be obtained by analytic choices rather than by physics.

## 1. Scores

- **Photonics Research: 6/10**  
  The optical physics is present, but the core contribution is a statistical protocol. As written, it may be judged as “computational imaging presented in a photonics journal” unless the memory-effect/meterology component is made physically generative and predictive.

- **IEEE TCI: 7/10**  
  The method-aware, pre-registered, negative-outcome-tolerant design is a strong fit for TCI. The score is not higher because the combined program currently risks being three studies bundled by a shared simulator rather than one integrated claim.

If the three cheap experiments below are run and support the proposed causal/statistical attributions, I would move both scores to 8/10.

## 2. The three strongest objections a reviewer will raise

### Objection 1 — The statistical-distance “law” may be a metric artifact.

There is no pre-registered statistical distance. “Diffuser class” is not intrinsic: it depends on the chosen distance, the weighting of frequency bands, and the binning of parameters. If you generate diffusers along orthogonal axes and then measure transfer loss against a chosen distance, the “same class” boundary is effectively a threshold you chose. A changepoint can be obtained from a smooth monotone curve simply by discretizing too coarsely. Without multiple candidate distances, a permutation-null for the changepoint, and a model comparison that penalizes the segmented fit, the “law” will be criticized as circular.

### Objection 2 — “Hallucination” is defined with respect to an invisible reference.

The pilot result that “PSNR ranking flips with reference bandwidth” is expected, not evidence. If the reference contains out-of-band energy, a network that invents out-of-band content can score higher. The causal claim in B requires a **no-reference**, physics-constrained endpoint: null-space energy, spectral support violation, or forward-model consistency on a reconstruction. Without such an endpoint, and without sweeping fine-tune length, the effect could be a training nonstationarity or an optimizer artifact, not a property of band-unlimited GT.

### Objection 3 — The memory-effect knee in C is confounded with object complexity and training diversity.

Object extent changes the intrinsic dimensionality of the data distribution. Matching “training diversity” is not well-defined unless it is tied to a measurable quantity: number of effective degrees of freedom, per-pixel variance, number of training objects per extent, or the A-law distance. A changepoint at the memory-effect angle could still arise because larger objects are statistically harder, even without any physical memory-effect mechanism. The design needs a no-memory-effect control with matched conditioning, and the memory-effect angle should be varied independently of object-extent statistics.

## 3. Three cheapest discriminating experiments

### Experiment 1 — Null and multi-metric reanalysis of the transfer-loss matrix (Component A)

Use the existing trained models to build the full transfer-loss matrix across synthetic diffusers. Compute three different statistical distances: Wasserstein on height maps, KL/TV on speckle power spectra, and MMD on intensity patches. Fit both monotone and segmented models; compare via BIC or cross-validated predictive log-likelihood. Then permute class labels and repeat the changepoint fit to estimate the false-positive rate.  
**Cost:** hours, no new training.  
**This would settle whether the “law” is metric-robust or a threshold artifact.**

### Experiment 2 — Fine-tune-length / no-reference sweep on B’s existing checkpoints

Use the pilot checkpoints to compute physics-based no-reference endpoints as a function of fine-tune length: null-space energy, spectral energy outside the physical support, and forward-model consistency. Compare bandwidth-matched and band-unlimited GT under compute-matched schedules. Include a Wiener-filter or truncated pseudoinverse baseline.  
**Cost:** forward passes on existing checkpoints, or short retraining runs if checkpoints are incomplete.  
**This would convert B from a metric-flip observation into a causal, time-resolved statement about hallucination.**

### Experiment 3 — Memory-effect angle control for Component C

Hold the training object set fixed and vary only the simulated memory-effect angle (e.g., two additional angles, 2× and 0.5× the baseline). Retrain the same architecture on the same number of objects and same object-extent distribution. If the generalization-vs-extent changepoint moves with the memory-effect angle, physics is necessary. If it stays fixed, the knee is statistical.  
**Cost:** hours with reduced training grid on the existing CPU simulator.  
**This directly attacks the central attribution claim of C.**

## 4. One thing that argues for splitting — or for one paper

I would reject the combined program in favor of **two or three papers** if the only link between A, B, and C is the shared simulator. A common implementation is not a scientific integration.

Conversely, one thing argues strongly for **one paper**: if C’s “statistically matched training diversity” is *operationally defined* by A’s distance law, and if B’s no-reference hallucination endpoint is reported as the primary dependent variable for every C model. Then A, B, and C become one causal chain: A defines the matching statistics, B defines the trusted metric, and C tests whether the remaining generalization boundary is physical. If that chain is explicit, the combined paper is more than the sum of its parts.

## 5. Bottom line

Proceed, conditionally, with the three cheap experiments and a pre-registered analysis plan—the risks are manageable, and the program’s value is that each outcome discriminates between physical and statistical explanations rather than merely demonstrating another deep-learning speckle reconstruction result.
