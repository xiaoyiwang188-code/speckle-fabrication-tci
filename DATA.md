# Data

## Real experimental speckle data (not redistributed here)

The real-data section of the manuscript (§5) uses a public experimental speckle
dataset with paired ground-truth digits, reported in:

> Y. Li, Y. Xue, and L. Tian, "Deep speckle correlation: a deep learning approach
> toward scalable imaging through scattering media," *Optica* 5(10), 1181–1190 (2018).

**Dataset record**: Zenodo **15361263** — <https://zenodo.org/records/15361263>
(full archive `Deep Speckle.zip`, ~13.9 GB)

The upstream repository README carries a tokenized download link for the record;
copy it from <https://github.com/bu-cisl/Deep-Speckle-Correlation>.

**This repository does not redistribute those images** (they remain © their
original authors). Everything needed to reproduce the *analysis* is included: the
measurements we quote (grain FWHM, autocorrelation platform length, pairing
statistics) were computed from a 240-file sample, and the scripts that consume the
data are in `experiments/`.

### Archive layout used by the scripts

```
SpeckleAll/Speckle Decorrelation/deep speckle/
├── Ground Truth/Digit/<n>.tif                        (512×512, uint8)
└── Speckle Measurement/
    ├── Data for training (4 diffusers)/<n>.tif       (512×512, uint16 photon counts)
    └── Data for testing (unseen diffusers)/<n>.tif
```

Ground-truth and speckle files pair **by filename index** (`0.tif` ↔ `0.tif`).

### Locally used analysis scripts

| Script | Reads | Produces |
|---|---|---|
| `experiments/pairing_stats.py` | a local copy of the sampled files | same-id vs mismatched correlation statistics |
| results archived in `results/registration_fix{,2,3}.txt` | same | grain FWHM, autocorrelation platform length, registration attempts |

The real-data section deliberately stops at environment characterization
(information support, correlation structure, pairing statistics); see §5 of the
manuscript for why quantitative reconstruction on this dataset requires a
dedicated forward-calibration stage.

## Simulated data

All simulation data is generated on the fly by the scripts (fixed seeds); no
dataset is shipped. See `README_REPRO.md` for the exact generation parameters.
