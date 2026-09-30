# Novelty check trace — deepseek-v4-flash

Adjudication summary:  
**A: PROCEED**  
**B: PROCEED WITH CAUTION**  
**C: PROCEED**

---

## A. Diffuser-class statistical-distance law

**Verdict: PROCEED**

**Closest work:**  
- Zhang, *Nat Commun* 2026: physics mechanisms of generalization/hallucination via diffuser illumination zones  
- Long, *Photonics Research* 2026: universal generalization + quantitative assessment  
- Li/Tian, *Optica* 2018: one-to-all same-class training  
- Research Square rs-7097373: physics-guided dataset homogeneity for universal generalization  

**Concrete differentiation claim:**  
Existing work treats “same diffuser class” via physical illumination zones, empirical homogeneity, or one-to-all training recipes. A converts this into a *testable statistical law*: cross-diffuser generalization loss is predicted by factor-attributed statistical distance in **correlation length × height distribution × spectral shape**, with a changepoint that determines whether “same class” is a real boundary or an arbitrary labeling.

**Must hold to survive review:**  
- The statistical-distance → transfer-loss law predicts held-out diffusers, not just fits two classes.  
- Factor attribution must be causal, e.g., synthetic phase screens where correlation length, height distribution, and spectral shape are independently varied.  
- The changepoint model must beat a monotone-decay null via cross-validated likelihood or information criteria.  
- The result must be robust across at least three diffuser classes and two reconstruction architectures.

---

## B. GT-bandwidth-mismatch hallucination ablation

**Verdict: PROCEED WITH CAUTION**

**Closest work:**  
- Tivnan 2024, Hallucination Index: no-reference hallucination IQM  
- Zhang, *Nat Commun* 2026: physics mechanisms of hallucination  
- Long, *Photonics Research* 2026: quantitative generalization assessment  

**Concrete differentiation claim:**  
Tivnan gives a *metric*; Zhang studies physical *mechanisms*. B asks a sharper causal question: **does the bandwidth of the training target itself cause measured hallucination?** The pilot result is promising but confounded: bandwidth-matched training suppresses out-of-band hallucinated energy 3.1× while in-band PSNR drops 3.2 dB, and PSNR ranking flips with reference bandwidth.

**Must hold to survive review:**  
- The 3.1× out-of-band reduction must not be caused by a global attenuation/flattening of the output; report total spectral power and in-band structural fidelity.  
- Use a no-reference hallucination index as primary outcome, because PSNR is ambiguous when reference bandwidth differs.  
- Evaluate with matched band-limited references or multi-band PSNR, not a single full-band reference.  
- Pre-register training epochs / fine-tune length and check multiple checkpoints.  
- Include a compute-matched baseline: band-unlimited GT trained for the same epoch budget, not just until early stopping.

---

## C. Memory-effect knee vs training-diversity smooth decay

**Verdict: PROCEED**

**Closest work:**  
- Mashiko 2023, *Appl Opt*: extrapolated speckle correlation beyond memory effect  
- Fu 2026, *Opt Commun*: imaging beyond OME, method paper  
- Research Square rs-7097373: dataset design for universal generalization  
- Zhang, *Nat Commun* 2026: physics of generalization/hallucination  

**Concrete differentiation claim:**  
Mashiko and Fu show *methods* that can operate beyond the memory effect. C is not a method paper; it is an **attribution/benchmark** paper asking whether the generalization-vs-object-extent curve has a **physical changepoint at the memory-effect angle** or decays smoothly once training diversity is statistically matched. This variance-decomposition question is absent from prior work.

**Must hold to survive review:**  
- The changepoint credible interval must include the theoretical memory-effect angle.  
- Variance decomposition must show that the physics factor explains additional variance beyond training diversity.  
- A smooth-decay null model must be rejected, or the null result must be shown to be robust.  
- The result must generalize across object classes, diffuser realizations, and network architectures.

---

## 3×3 table: has (1) or (7) already contained these?

| Prior work | (a) distance-to-transfer-loss law | (b) controlled GT-bandwidth hallucination ablation | (c) diversity-vs-ME-kink variance decomposition |
|---|---|---|---|
| (1) Zhang, *Nat Commun* 2026 | Unknown — illumination zones may imply distance-to-loss, but statistical-factor changepoint law not explicit | No | No |
| (7) Research Square rs-7097373 | Unknown — dataset homogeneity could function as a distance-like measure, but no statistical-distance law or changepoint test stated | No | Unknown — dataset homogeneity/diversity is related, but no variance decomposition or ME-kink changepoint analysis stated |

**Key:**  
- **No** = not present in the cited work as summarized.  
- **Unknown** = the title/abstract suggests a related concept, but full-text confirmation is needed.

---

## Is the fine-tune-length moderator fatal for B?

**Addressable, not fatal.**

The pilot’s mixed signal does not refute the hypothesis; it reveals that the result is sensitive to training dynamics and evaluation metric. The right response is to make fine-tune length a **pre-registered moderator**, not an uncontrolled nuisance.

If longer fine-tuning erases the hallucination suppression, the claim becomes:  
> “Bandwidth mismatch does not cause hallucination at convergence; it affects hallucination during training dynamics.”  

That is still a valuable, publishable finding — but it is not the same claim. If the suppression persists across fine-tune lengths, the causal claim is strong. Either way, the experiment is informative.

**Decisive recommendation:**  
Run B with:
- fixed fine-tune budget,
- multiple checkpoints,
- a no-reference hallucination index as primary endpoint,
- band-limited PSNR as a secondary endpoint.

Then the fine-tune length is an addressable experimental axis, not a fatal flaw.
