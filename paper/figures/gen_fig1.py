"""Fig 1: hero 3-panel. (a) MTF support + recon spectrum, oob shaded;
(b) raw vs matched recon from identical init; (c) suppression ratio bars.
Retrains two small models locally (CPU, ~3 min) from the scale-up protocol."""
import sys, json, math, copy
sys.path.insert(0, "paper/figures")
sys.path.insert(0, "experiments")
from paper_plot_style import *
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from sim_common import (make_psf, conv_psf, lowpass, gen_objects, add_noise,
                        train_model, N, mtf_radius_analytic)

torch.manual_seed(12345); np.random.seed(0)
R_APER = 6
R_MTF = mtf_radius_analytic(R_APER)
SIG = R_MTF/2.355*0.9

PSF = make_psf(r_aperture=R_APER, seed=1)
GT = gen_objects(1600, seed=7)
SPK = add_noise(conv_psf(GT, PSF))
tr_x, te_x = SPK[:1200], SPK[1200:]
tr_obj, te_obj = GT[:1200], GT[1200:]

raw = train_model(tr_x, tr_obj, epochs=20, seed=12345)
ft = copy.deepcopy(raw)
opt = torch.optim.Adam(ft.parameters(), lr=3e-4)
tgt = lowpass(tr_obj, SIG)
for ep in range(4):
    perm = torch.randperm(tr_x.shape[0])
    for i in range(0, tr_x.shape[0], 64):
        idx = perm[i:i+64]
        loss = F.mse_loss(ft(tr_x[idx]), tgt[idx])
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(ft.parameters(), 1.0); opt.step()

with torch.no_grad():
    pr = raw(te_x).numpy()
    pf = ft(te_x).numpy()

def radial_spec(img):
    P = np.fft.fftshift(np.abs(np.fft.fft2(img - img.mean()))**2)
    yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    r = np.sqrt((yy-N//2)**2+(xx-N//2)**2).round().astype(int)
    n = np.bincount(r.ravel(), minlength=48)[:48].astype(float)
    prof = np.bincount(r.ravel(), weights=P.ravel(), minlength=48)[:48]
    p = prof/np.maximum(n, 1)
    band = p[:int(R_MTF)].sum()
    return p / max(band, 1e-12)   # energy fraction per unit in-band energy

spec_r = np.mean([radial_spec(pr[k, 0]) for k in range(50)], axis=0)
spec_f = np.mean([radial_spec(pf[k, 0]) for k in range(50)], axis=0)
XMAX = 30

# ---- (c) ratio bars from the real scale-up data ----
d = json.load(open("results/scaleup_results.json"))
runs = d["runs_raw"]
ctrl = {(r["arch"], r["seed"]): r["out_of_band_energy"]
        for r in runs if r["arm"] == "raw_continued_control"}
rm = [r["out_of_band_energy"]/ctrl[(r["arch"], r["seed"])]
      for r in runs if r["arm"] == "finetune_matched"]
rh = [r["out_of_band_energy"]/ctrl[(r["arch"], r["seed"])]
      for r in runs if r["arm"] == "finetune_half"]

fig = plt.figure(figsize=(7.16, 2.3))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1.15, 0.75], wspace=0.42)

ax = fig.add_subplot(gs[0])
rr = np.arange(XMAX)
ax.plot(rr, spec_r[:XMAX], color=COL["raw"], lw=1.3, label="raw-trained")
ax.plot(rr, spec_f[:XMAX], color=COL["matched"], lw=1.3, ls="--", label="matched FT")
ax.axvspan(R_MTF, XMAX-1, color="0.88", alpha=0.9)
ax.axvline(R_MTF, color="k", lw=0.7, ls=":")
ax.text((R_MTF+XMAX)/2, 3e-3, "out-of-\nband", fontsize=FONT_SIZE-2, ha="center", va="center")
ax.set_yscale("log")
ax.set_xlim(0, XMAX-1)
ax.set_ylim(1e-6, 3)
ax.set_xlabel("radial frequency (px)")
ax.set_ylabel("energy fraction\n(per in-band unit)")
ax.legend(frameon=False, loc="upper right", fontsize=FONT_SIZE-2)
ax.set_title("(a)", fontsize=FONT_SIZE)

ax = fig.add_subplot(gs[1])
k = 5
img = np.concatenate([GT[1200+k, 0], pr[k, 0], pf[k, 0]], axis=1)
ax.imshow(img, cmap="gray", vmin=0, vmax=1)
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_visible(True)
ax.text(N/2, -4, "ground truth", fontsize=FONT_SIZE-2, ha="center")
ax.text(N+N/2, -4, "raw-trained", fontsize=FONT_SIZE-2, ha="center")
ax.text(2*N+N/2, -4, "matched FT", fontsize=FONT_SIZE-2, ha="center")
ax.set_title("(b)", fontsize=FONT_SIZE)

ax = fig.add_subplot(gs[2])
xs = np.arange(2)
means = [np.mean(rm), np.mean(rh)]
errs = [np.std(rm), np.std(rh)]
ax.bar(xs, means, yerr=errs, capsize=3, width=0.55,
       color=[COL["matched"], COL["half"]], edgecolor="k", linewidth=0.5)
ax.axhline(1.0, color="k", lw=0.7, ls="--")
ax.text(1.35, 1.03, "no change", fontsize=FONT_SIZE-2, ha="right", va="bottom")
ax.set_xticks(xs); ax.set_xticklabels(["0.9×", "0.45×"])
ax.set_xlabel("target bandwidth")
ax.set_ylabel("ratio vs control")
ax.set_ylim(0, 1.1)
ax.set_title("(c)", fontsize=FONT_SIZE)

fig.savefig(f"{FIG_DIR}/fig1_hero.pdf")
print("fig1 saved")
