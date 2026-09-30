"""Merge Colab scale-up units -> final stats + Wiener sensitivity (local CPU).
Reads results/scaleup_units/unit_*.json, computes paired finetune-vs-control
statistics, reruns Wiener K/support sweep on the same synthetic protocol,
writes results/scaleup_results.json and prints a summary."""
import json, math, glob, statistics, os, sys
import numpy as np
import torch
import torch.nn.functional as F

ROOT = os.path.normpath(os.path.abspath("."))
UNIT_DIR = os.path.join(ROOT, "results", "scaleup_units")
OUT_PATH = os.path.join(ROOT, "results", "scaleup_results.json")

units = []
for f in sorted(glob.glob(os.path.join(UNIT_DIR, "unit_*.json"))):
    units.append(json.load(open(f)))
print("units loaded:", len(units), file=sys.stderr)

runs = []
for u in units:
    for r in u["runs"]:
        runs.append({**r, "arch": u["arch"], "seed": u["seed"]})

# paired stats: finetune vs control within each (arch, seed)
stats = {}
for tname in ["matched", "half"]:
    oob_diffs, fwd_diffs, ratios = [], [], []
    for u in units:
        ctrl = next(r for r in u["runs"] if r["arm"] == "raw_continued_control")
        ft = next(r for r in u["runs"] if r["arm"] == f"finetune_{tname}")
        oob_diffs.append(ft["out_of_band_energy"] - ctrl["out_of_band_energy"])
        fwd_diffs.append(ft["rel_fwd_consistency"] - ctrl["rel_fwd_consistency"])
        ratios.append(ft["out_of_band_energy"] / ctrl["out_of_band_energy"])
    stats[tname] = {
        "n": len(oob_diffs),
        "mean_oob_ratio": round(statistics.mean(ratios), 3),
        "std_oob_ratio": round(statistics.stdev(ratios), 3) if len(ratios) > 1 else None,
        "oob_reduced_in": f"{sum(1 for d in oob_diffs if d < 0)}/{len(oob_diffs)}",
        "mean_rel_fwd_diff": round(statistics.mean(fwd_diffs), 4)}

# baseline summary by target
base = {}
for tname in ["raw", "matched", "half"]:
    vals = [r["out_of_band_energy"] for r in runs if r["arm"] == f"baseline_{tname}"]
    ps = [r["psnr_bandlimited"] for r in runs if r["arm"] == f"baseline_{tname}"]
    base[tname] = {"n": len(vals),
                   "oob_mean": round(statistics.mean(vals), 5),
                   "oob_std": round(statistics.stdev(vals), 5) if len(vals) > 1 else None,
                   "psnr_mean": round(statistics.mean(ps), 2)}

# Wiener sensitivity sweep (CPU, same protocol params as colab script)
N, R_APER = 64, 6
R_MTF = float(2 * R_APER)
def gk(sigma):
    r = int(max(1, round(3*sigma)))
    x = torch.arange(-r, r+1, dtype=torch.float32)
    k = torch.exp(-0.5*(x/sigma)**2)
    return k/k.sum()
def sep(x, kx, ky):
    return F.conv2d(F.conv2d(x, kx.view(1,1,-1,1), padding=(kx.numel()//2,0)),
                    ky.view(1,1,1,-1), padding=(0,ky.numel()//2))
def make_psf(r_aperture, seed):
    g = torch.Generator().manual_seed(seed)
    phi = torch.randn(N, N, generator=g); phi = phi/phi.std()*math.pi
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing="ij")
    rr = torch.sqrt(((yy-N//2)**2 + (xx-N//2)**2))
    pupil = (rr <= r_aperture).float()
    field = torch.fft.ifft2(torch.fft.ifftshift(pupil*torch.exp(1j*2*math.pi*phi)))
    psf = torch.abs(field)**2
    return psf/psf.sum()
PSF = make_psf(R_APER, 1)
H = np.fft.fft2(PSF.numpy()); Hm = np.abs(H)
yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
rr = np.sqrt(((yy-N//2)**2 + (xx-N//2)**2))
# use E2's saved test speckles if present else regenerate identical protocol
from PIL import Image, ImageDraw, ImageFont
rng = np.random.default_rng(7)
objs = torch.zeros(40, 1, N, N)
try:
    font = ImageFont.truetype("arial.ttf", 40)
except Exception:
    font = ImageFont.load_default()
for i in range(40):
    img = Image.new("L", (N, N), 0); d = ImageDraw.Draw(img); d.fontmode = "1"
    d.text((int(rng.integers(4,24)), int(rng.integers(0,20))), str(int(rng.integers(0,10))), fill=255, font=font)
    objs[i,0] = torch.from_numpy(np.asarray(img, dtype=np.float32)/255.0)
spk = F.conv2d(objs, PSF.view(1,1,N,N).flip(-1).flip(-2), padding=N//2)[..., :N, :N]
wiener = {}
for Krel in [1e-3, 1e-2, 1e-1]:
    Wf = np.conj(H) / (Hm**2 + Krel*Hm.max()**2)
    for rfac in [1.0, 1.5]:
        r_eff = R_MTF*rfac
        oobs, fwds = [], []
        for k in range(30):
            y_np = spk[k, 0].numpy()
            Xh = np.fft.ifft2(Wf*np.fft.fft2(y_np)).real
            Xh = np.clip(Xh, 0, None); Xh /= max(Xh.max(), 1e-9)
            P = np.abs(np.fft.fftshift(np.fft.fft2(Xh)))**2
            oobs.append(float(P[rr > r_eff].sum()/P.sum()))
            resd = np.fft.fft2(Xh) - np.fft.fft2(y_np)
            fwds.append(float(np.linalg.norm(resd)/np.linalg.norm(np.fft.fft2(y_np))))
        wiener[f"K{Krel}_sup{rfac}"] = {"oob": round(float(np.mean(oobs)), 5),
                                         "rel_fwd": round(float(np.mean(fwds)), 4)}

out = {"design": {"source": "Colab T4 scale-up", "n_units": len(units),
                  "archs": sorted({u["arch"] for u in units}),
                  "seeds": sorted({u["seed"] for u in units}),
                  "r_mtf": R_MTF},
       "baselines": base,
       "paired_stats_finetune_vs_control": stats,
       "wiener_sensitivity": wiener,
       "runs_raw": runs}
json.dump(out, open(OUT_PATH, "w"), indent=1)
print("WROTE", OUT_PATH)
print(json.dumps({k: out[k] for k in ["baselines", "paired_stats_finetune_vs_control"]}, indent=1))
