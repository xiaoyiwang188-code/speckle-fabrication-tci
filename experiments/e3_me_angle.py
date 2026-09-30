"""E3: memory-effect angle control (Component C).

Pre-registered: physics lever = speckle grain size (r_aperture in {4,6,12};
grain = N/(2r), ME angle ~ 1/grain). Objects FIXED (same seed, extent=0.6 training set);
test buckets at extents {0.30,0.45,0.60,0.75}. Per grain setting: one model, PSNR-vs-extent
curve, segmented-fit breakpoint t*(grain).
Verdict: t* increases with grain following ~grain proportionality => physics;
t* invariant across grain => statistical.
Bootstrap: 2 extra training seeds at each grain for t* spread.
"""
import sys, json, math
import numpy as np
import torch
sys.path.insert(0, r"C:\zcode\SCI\论文项目\experiments")
from sim_common import (log, make_psf, conv_psf, lowpass, gen_objects, add_noise,
                        train_model, psnr, N, NTRAIN, NTEST, mtf_radius_analytic)

torch.manual_seed(0); np.random.seed(0)
RADII = [4, 6, 12]
EXTENTS = [0.30, 0.45, 0.60, 0.75]
TRAIN_EXTENT = 0.6
EPOCHS = 12

train_obj = gen_objects(NTRAIN+NTEST, seed=7, extent=TRAIN_EXTENT)

def lin(x, y):
    A = np.vstack([x, np.ones_like(x)]).T
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(((y - A@c)**2).sum()), c

def breakpoint(y):
    """Largest single-drop location via segmented fit over extent index grid."""
    x = np.array(EXTENTS, dtype=float)
    y = np.asarray(y, dtype=float)
    best = None
    for i in range(1, len(x)):
        m1, m2 = np.arange(len(x)) < i, np.arange(len(x)) >= i
        if m1.sum() < 2 or m2.sum() < 2:
            continue
        r1, c1 = lin(x[m1], y[m1]); r2, c2 = lin(x[m2], y[m2])
        rss = r1 + r2
        if best is None or rss < best[0]:
            best = (rss, x[i], c1, c2, m1.sum(), m2.sum())
    return best  # (rss, t*, coef1, coef2, n1, n2)

per_grain = {}
for r in RADII:
    psf = make_psf(r_aperture=r, seed=1)
    r_mtf = mtf_radius_analytic(r)
    sig = r_mtf/2.355*0.9
    tr_t = lowpass(train_obj[:NTRAIN], sig)
    tr_x = add_noise(conv_psf(train_obj[:NTRAIN], psf))
    grain_px = N/(2*r)
    t_stars = []
    for seed in (12345, 777):
        model = train_model(tr_x, tr_t, epochs=EPOCHS, seed=seed)
        curve = []
        with torch.no_grad():
            for ext in EXTENTS:
                te_obj = gen_objects(80, seed=200+int(ext*100), extent=ext)
                te_ref = lowpass(te_obj, sig)
                te_spk = add_noise(conv_psf(te_obj, psf))
                pred = model(te_spk)
                curve.append(round(psnr(pred, te_ref), 2))
        bp = breakpoint(curve)
        t_stars.append(bp[1] if bp else None)
        log(f"  r={r} seed={seed}: curve={curve} t*={bp[1] if bp else None}")
    ts = [t for t in t_stars if t is not None]
    per_grain[str(r)] = {"grain_px": round(grain_px, 2), "t_star_extents": ts,
                         "t_star_mean": round(float(np.mean(ts)), 3) if ts else None,
                         "curves": curve}

# physics prediction: t* proportional to grain (rank correlation across settings)
grains = [per_grain[str(r)]["grain_px"] for r in RADII]
tmeans = [per_grain[str(r)]["t_star_mean"] for r in RADII]
ok = all(t is not None for t in tmeans)
rank_corr = None
if ok and len(set(tmeans)) > 1:
    from scipy.stats import spearmanr
    rank_corr = round(float(spearmanr(grains, tmeans).statistic), 3)

out = {"design": {"radii": RADII, "train_extent": TRAIN_EXTENT, "test_extents": EXTENTS,
                  "physics_prediction": "t* rises with grain (ME angle ~ 1/grain); invariance => statistical",
                  "epochs": EPOCHS, "seeds": [12345, 777]},
       "per_grain": per_grain,
       "spearman_grain_vs_tstar": rank_corr,
       "verdict": ("PHYSICS_BOUNDARY" if (rank_corr is not None and rank_corr > 0.8)
                   else "STATISTICAL" if (rank_corr is not None and rank_corr < -0.8)
                   else "INCONCLUSIVE_LOW_POWER")}
print("E3_JSON_BEGIN"); print(json.dumps(out, indent=1)); print("E3_JSON_END")
