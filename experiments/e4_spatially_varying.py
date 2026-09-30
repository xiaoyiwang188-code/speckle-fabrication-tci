"""E4: spatially-varying PSF check (the second arm of the reviewer's real-data condition).

Design: 4-quadrant independently-seeded PSFs with soft quadrant weight masks -> a
position-dependent forward operator (finite-ME proxy). Question: does component B's
causal GT-bandwidth effect (matched/control out-of-band energy ratio ~0.5) SURVIVE
when shift-invariance is broken? If yes, the protocol does not depend on the
shift-invariant idealization.
"""
import sys, math, json
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, r"C:\zcode\SCI\论文项目\experiments")
from sim_common import (log, make_psf, conv_psf, lowpass, gen_objects, add_noise,
                        train_model, psnr, hf_energy, N, NTRAIN, NTEST,
                        mtf_radius_analytic)

torch.manual_seed(0); np.random.seed(0)
R_APER = 6
R_MTF = mtf_radius_analytic(R_APER)
SIG = R_MTF/2.355*0.9

# quadrant PSFs (different seeds) and soft weight masks (feathered 16px)
PSFS = [make_psf(r_aperture=R_APER, seed=s) for s in (11, 22, 33, 44)]
yy, xx = torch.meshgrid(torch.arange(N, dtype=torch.float32),
                        torch.arange(N, dtype=torch.float32), indexing="ij")
def soft_mask(qy, qx, feather=16.0):
    wy = torch.clamp(1 - torch.abs(yy - qy*N/2 + 0.5)/feather, 0, 1) if qy in (0, 1) else None
    return None
def quadrant_masks():
    fx = torch.clamp((xx - N/2)/feather_val + 0.5, 0, 1)
    fy = torch.clamp((yy - N/2)/feather_val + 0.5, 0, 1)
    m = [(1-fy)*(1-fx), (1-fy)*fx, fy*(1-fx), fy*fx]
    s = sum(m)
    return [mi/s for mi in m]
feather_val = 16.0
MASKS = quadrant_masks()

def conv_sv(imgs):
    """Spatially varying convolution: quadrant PSFs blended with feathered weights."""
    out = None
    for psf, mask in zip(PSFS, MASKS):
        yi = conv_psf(imgs, psf)
        out = yi*mask if out is None else out + yi*mask
    return out

GT_OBJ = gen_objects(NTRAIN+NTEST, seed=7)
SPK = add_noise(conv_sv(GT_OBJ))
tr_x, te_x = SPK[:NTRAIN], SPK[NTRAIN:]
tr_obj, te_obj = GT_OBJ[:NTRAIN], GT_OBJ[NTRAIN:]
REF = lowpass(te_obj, SIG)

log("E4: raw 20ep under spatially-varying PSF...")
raw = train_model(tr_x, tr_obj, epochs=20, seed=12345)
log("E4: raw-continued control 4ep...")
raw_cont = train_model(tr_x, tr_obj, epochs=4, lr=3e-4, init_model=raw)

log("E4: matched fine-tune sweep 1/2/4ep...")
import copy
ft = copy.deepcopy(raw)
opt = torch.optim.Adam(ft.parameters(), lr=3e-4)
tgt = lowpass(tr_obj, SIG)
sweep = []
for ep in range(1, 5):
    perm = torch.randperm(tr_x.shape[0])
    for i in range(0, tr_x.shape[0], 64):
        idx = perm[i:i+64]
        loss = F.mse_loss(ft(tr_x[idx]), tgt[idx])
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(ft.parameters(), 1.0)
        opt.step()
    if ep in (1, 2, 4):
        with torch.no_grad():
            pred = ft(te_x)
            e = {"psnr_bandlimited": round(psnr(pred, REF), 2),
                 "out_of_band_energy": round(hf_energy(pred, R_MTF), 5)}
        sweep.append(e)
        log(f"  ckpt {ep}ep: {e}")

with torch.no_grad():
    res = {"raw_20ep": {"psnr_bandlimited": round(psnr(raw(te_x), REF), 2),
                        "out_of_band_energy": round(hf_energy(raw(te_x), R_MTF), 5)},
           "raw_continued_4ep": {"psnr_bandlimited": round(psnr(raw_cont(te_x), REF), 2),
                                  "out_of_band_energy": round(hf_energy(raw_cont(te_x), R_MTF), 5)},
           "matched_ft": sweep}
ctrl = res["raw_continued_4ep"]["out_of_band_energy"]
ratios = [round(e["out_of_band_energy"]/max(ctrl, 1e-9), 3) for e in sweep]
res["ratios_matched_over_control"] = ratios
res["verdict"] = ("EFFECT_SURVIVES_SPATIAL_VARIATION" if ratios[-1] < 0.8
                  else "EFFECT_BREAKS_UNDER_SPATIAL_VARIATION")
out = {"design": {"quadrant_psfs": 4, "feather_px": feather_val, "r_aperture": R_APER,
                  "r_mtf": R_MTF, "note": "position-dependent operator = finite-ME proxy"},
       "results": res}
print("E4_JSON_BEGIN"); print(json.dumps(out, indent=1)); print("E4_JSON_END")
