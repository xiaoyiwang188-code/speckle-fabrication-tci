# Matched Fine-Tuning Controls Spectral Fabrication in Learned Speckle Imaging

Reproduction package for the IEEE Transactions on Computational Imaging manuscript
**"Matched Fine-Tuning Controls Spectral Fabrication in Learned Speckle Imaging: Capacity Effects and a Compute-Matched Remedy"**.

Training-target bandwidth is isolated as a **causal, compute-matched** control of out-of-band
spectral fabrication in learned speckle reconstruction: from an identical initialization and
identical additional optimization, fine-tuning against bandwidth-matched targets reduces
out-of-band energy to **0.34 ± 0.11** (matched) and **0.20 ± 0.08** (half) of the control
across two architectures and three seeds (6/6 units, one-sided sign test *p* ≈ 0.016),
while the no-reference forward-consistency endpoint changes by only +0.026 on a 0.36–0.40 baseline.

## What is here

```
README_REPRO.md          reproduction + adversarial-review guide (READ THIS FIRST)
paper/                   LaTeX source (IEEEtran), compiled PDF, figures, bibliography,
                         citation audit and claim audit
experiments/             all experiment code (CPU-only; GPU scripts run identically, slower)
results/                 raw results: 36 scale-up runs, per-unit files, stage outputs,
                         ablation matrices, audit outputs
idea-stage/              idea-discovery record (novelty verification, ranked candidates)
refine-logs/             pre-registered experiment plan + tracker (pre-registration evidence)
.aris/traces/            cross-model review transcripts (all reviewer verdicts, auditable)
```

## Quick start

```bash
python -c "import torch, numpy, PIL, matplotlib; print('deps ok')"
python experiments/claim_audit.py     # 47 cross-checks: manuscript numbers vs results/
python paper/figures/gen_fig2.py      # regenerate figures (fig1 retrains 2 small models)
cd paper && latexmk -pdf -interaction=nonstopmode main.tex
```

Full command list, environment notes, and the number-to-file mapping table are in
[`README_REPRO.md`](README_REPRO.md).

## Data

The real-data section uses a public experimental speckle dataset (DSC; Zenodo record
**15361263**). **The raw images are not redistributed in this repository.** To fetch them:

```python
# see experiments/fetch_dsc_sample.py — downloads a 240-file sample (~28 MB) by HTTP range
python experiments/fetch_dsc_sample.py
```

The full dataset is ~13.9 GB; the scripts in `experiments/` read a local
`artifacts/dsc_data/` directory produced by that fetch step.

## Citation

If this work is useful in your research, please cite the manuscript (IEEE TCI, preprint
available in `paper/main.pdf`).
