"""E2: fine-tune-length sweep x no-reference endpoints (Component B).

Pre-registered: raw baseline (20ep) -> compute-matched arms:
  raw-continued (raw target, 4 more epochs)  vs  matched fine-tune (4 epochs, checkpoints at 1/2/4).
Primary endpoints are NO-REFERENCE physics quantities:
  out-of-band energy ratio, relative forward-consistency ||H(x)-y||/||y||.
Secondary: band-limited PSNR. Wiener deconvolution as linear baseline.
Verdict rule: matched-vs-raw-cont endpoint gap that grows/stays with fine-tune length
=> GT-bandwidth effect is causal, not under-training.
"""
import sys, json, math
import numpy as np
import torch
sys.path.insert(0, r"C:\zcode\SCI\论文项目\experiments")
from sim_common import (log, make_psf, conv_psf, lowpass, gen_objects, add_noise,
                        train_model, psnr, hf_energy, rel_fwd_residual, wiener_reconstruct,
                        N, NTRAIN, NTEST, mtf_radius_analytic)

torch.manual_seed(0); np.random.seed(0)
R_APER = 6
PSF = make_psf(r_aperture=R_APER, seed=1)
R_MTF = mtf_radius_analytic(R_APER)
SIG = R_MTF/2.355*0.9

GT_OBJ = gen_objects(NTRAIN+NTEST, seed=7)
SPK = add_noise(conv_psf(GT_OBJ, PSF))
tr_x, te_x = SPK[:NTRAIN], SPK[NTRAIN:]
tr_obj, te_obj = GT_OBJ[:NTRAIN], GT_OBJ[NTRAIN:]
REF = lowpass(te_obj, SIG)

log("E2: raw baseline 20ep...")
raw = train_model(tr_x, tr_obj, epochs=20, seed=12345)

def endpoints(model):
    with torch.no_grad():
        pred = model(te_x)
        y = te_x
        return {"psnr_bandlimited": round(psnr(pred, REF), 2),
                "out_of_band_energy": round(hf_energy(pred, R_MTF), 5),
                "rel_fwd_consistency": round(rel_fwd_residual(pred, y, PSF), 4)}

results = {"raw_20ep": endpoints(raw)}

# compute-matched control: continue raw on RAW target for 4 more epochs
log("E2: raw-continued 4ep (compute-matched control)...")
raw_cont = train_model(tr_x, tr_obj, epochs=4, lr=3e-4, init_model=raw)
results["raw_continued_4ep"] = endpoints(raw_cont)

# matched fine-tune with checkpoints at 1/2/4 epochs
log("E2: matched fine-tune sweep 1/2/4ep...")
import copy
ft = copy.deepcopy(raw)
opt = torch.optim.Adam(ft.parameters(), lr=3e-4)
from sim_common import BS
tgt = lowpass(tr_obj, SIG)
for ep in range(1, 5):
    perm = torch.randperm(tr_x.shape[0])
    for i in range(0, tr_x.shape[0], BS):
        idx = perm[i:i+BS]
        loss = torch.nn.functional.mse_loss(ft(tr_x[idx]), tgt[idx])
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(ft.parameters(), 1.0)
        opt.step()
    if ep in (1, 2, 4):
        results[f"matched_ft_{ep}ep"] = endpoints(ft)
        log(f"  checkpoint {ep}ep done")

# Wiener linear baseline
with torch.no_grad():
    w = wiener_reconstruct(te_x, PSF, K=1e-2)
results["wiener_linear_baseline"] = {
    "psnr_bandlimited": round(psnr(w, REF), 2),
    "out_of_band_energy": round(hf_energy(w, R_MTF), 5),
    "rel_fwd_consistency": round(rel_fwd_residual(w, te_x, PSF), 4)}

# verdict: gap stability across fine-tune length
def gap(a, b, k):
    return round(results[a][k] - results[b][k], 4)
sweep = [results[f"matched_ft_{e}ep"]["out_of_band_energy"] for e in (1, 2, 4)]
ctrl = results["raw_continued_4ep"]["out_of_band_energy"]
ratio = [round(s/max(ctrl, 1e-9), 3) for s in sweep]
results["sweep_out_of_band_matched_over_control"] = ratio
results["verdict"] = ("CAUSAL_EFFECT" if ratio[-1] < 0.8 else
                      "FADES_WITH_LENGTH" if ratio[0] < 0.8 else "NO_EFFECT")

out = {"design": {"r_aperture": R_APER, "r_mtf": R_MTF, "ntrain": NTRAIN,
                  "arms": ["raw_20ep", "raw_continued_4ep(control)", "matched_ft_1/2/4ep", "wiener"],
                  "pre_registered": "no-reference primary endpoints; compute-matched control; fine-tune sweep"},
       "results": results}
print("E2_JSON_BEGIN"); print(json.dumps(out, indent=1)); print("E2_JSON_END")
