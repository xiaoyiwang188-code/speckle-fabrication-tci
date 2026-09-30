"""Pilot: GT-bandwidth-mismatch hallucination ablation + inverse-consistency decoupling.

Pre-registered decision criteria:
- POSITIVE: matched-GT hallucination energy < 0.5x raw-GT, in-band PSNR within 0.5 dB
- NEGATIVE: ratio > 0.8x -> hallucination intrinsic to ill-posedness
- else MIXED

Simulation: shift-invariant speckle regime, y = conv(x, PSF_I) + noise (linear
approximation standard in Deep Speckle Correlation-style pipelines). CPU-only.
Prints a single JSON object to stdout; no filesystem writes in-code.
"""
import json, math, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0); np.random.seed(0)
N = 64
NTRAIN = 2000
NTEST = 400
EPOCHS = 20
BS = 64
LR = 1e-3
LC_PX = 3.0
NOISE_SIGMA = 0.05

def gauss_kernel_1d(sigma):
    r = int(max(1, round(3*sigma)))
    x = torch.arange(-r, r+1, dtype=torch.float32)
    k = torch.exp(-0.5*(x/sigma)**2); return k/k.sum()

def sep_conv2d(x, kx, ky):
    return F.conv2d(F.conv2d(x, kx.view(1,1,-1,1), padding=(kx.numel()//2,0)),
                    ky.view(1,1,1,-1), padding=(0,ky.numel()//2))

def make_psf(r_aperture=6, seed=1):
    """Frequency-domain circular aperture (radius r_aperture px) with random
    phase -> intensity PSF. Speckle grain ~ N/(2*r_aperture)."""
    g = torch.Generator().manual_seed(seed)
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij')
    rr = torch.sqrt((yy-N//2)**2 + (xx-N//2)**2)
    pupil = (rr <= r_aperture).float()
    phi = torch.randn(N,N, generator=g)
    field = torch.fft.ifft2(torch.fft.ifftshift(pupil * torch.exp(1j*2*math.pi*phi)))
    psf = torch.abs(field)**2
    return psf / psf.sum()

def conv_psf(imgs, psf):
    out = F.conv2d(imgs, psf.view(1,1,N,N).flip(-1).flip(-2), padding=N//2)
    return out[..., :N, :N]   # even-size kernel: crop the extra row/col

def mtf_radius(psf):
    M = torch.abs(torch.fft.fftshift(torch.fft.fft2(psf)))
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij')
    r = torch.sqrt((yy-N//2)**2 + (xx-N//2)**2).round().long()
    prof = torch.zeros(int(r.max())+1); cnt = torch.zeros(int(r.max())+1)
    prof.index_add_(0, r.flatten(), M.flatten())
    cnt.index_add_(0, r.flatten(), torch.ones_like(M).flatten())
    prof = prof/cnt
    idx = torch.nonzero(prof < prof.max()/2)
    return float(idx[0]) if idx.numel() else float(N//2)

def lowpass(imgs, sigma):
    if sigma <= 0: return imgs
    k = gauss_kernel_1d(sigma)
    return sep_conv2d(imgs, k, k)

def gen_objects(n, seed=42):
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(seed)
    out = torch.zeros(n,1,N,N)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    for i in range(n):
        img = Image.new("L", (N,N), 0)
        d = ImageDraw.Draw(img)
        d.fontmode = "1"   # no anti-aliasing -> sharp strokes, high-frequency content
        d.text((int(rng.integers(4,24)), int(rng.integers(0,20))), str(int(rng.integers(0,10))), fill=255, font=font)
        out[i,0] = torch.from_numpy(np.asarray(img, dtype=np.float32)/255.0)
    return out

def add_noise(spk):
    return (spk + NOISE_SIGMA*2*torch.randn_like(spk)*spk.sqrt().clamp(min=0)).clamp(min=0)

class UNet(nn.Module):
    def __init__(self, base=16):
        super().__init__()
        def blk(i,o):
            return nn.Sequential(nn.Conv2d(i,o,3,padding=1), nn.ReLU(), nn.Conv2d(o,o,3,padding=1), nn.ReLU())
        self.e1=blk(1,base); self.e2=blk(base,base*2); self.e3=blk(base*2,base*4)
        self.pool=nn.MaxPool2d(2)
        self.d2=blk(base*4+base*2,base*2); self.d1=blk(base*2+base,base)
        self.out=nn.Conv2d(base,1,3,padding=1)
    def forward(self,x):
        x1=self.e1(x); x2=self.e2(self.pool(x1)); x3=self.e3(self.pool(x2))
        u2=F.interpolate(x3,size=x2.shape[-2:],mode='bilinear',align_corners=False)
        d2=self.d2(torch.cat([u2,x2],1))
        u1=F.interpolate(d2,size=x1.shape[-2:],mode='bilinear',align_corners=False)
        d1=self.d1(torch.cat([u1,x1],1))
        return (self.out(d1) + x).clamp(0,1)   # global residual: no all-zero attractor

def psnr(a,b):
    mse=((a-b)**2).mean().item()
    return 10*math.log10(1.0/max(mse,1e-12))

def fft_highfreq_energy(imgs, r_mtf):
    F_ = torch.fft.fftshift(torch.fft.fft2(imgs[:,0]), dim=(-2,-1))
    P = F_.abs()**2
    yy,xx = torch.meshgrid(torch.arange(N),torch.arange(N),indexing='ij')
    r = torch.sqrt(((yy-N//2)**2+(xx-N//2)**2).float())
    hi = P[:, r>r_mtf]
    if not torch.isfinite(hi.sum()) or not torch.isfinite(P.sum()):
        print("WARN: non-finite in hf_energy: pred_max=%.3f" % float(imgs.max()))
    return float(hi.sum() / P.sum())

def train(sigma, epochs, lr, init_model=None):
    # v2 design: one stable raw baseline, then fine-tune copies to each target
    # bandwidth from the SAME converged state -> target bandwidth is the only variable.
    import copy
    if init_model is None:
        torch.manual_seed(12345)
        model = UNet()
    else:
        model = copy.deepcopy(init_model)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    tgt_all = lowpass(GT_OBJ[:NTRAIN], sigma)
    t0=time.time()
    for ep in range(epochs):
        perm = torch.randperm(NTRAIN)
        for i in range(0, GT_OBJ.shape[0], BS):
            idx = perm[i:i+BS]
            loss = F.mse_loss(model(SPK_TR[idx]), tgt_all[idx])
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    print(f"[sigma={sigma:.2f}] trained {epochs}ep in {time.time()-t0:.0f}s", flush=True)
    return model

PSF = make_psf()
# Analytic information bandwidth: MTF support = autocorrelation of the field
# spectrum support = 2 * aperture radius (single-realization MTF is speckle-
# dominated, half-power estimation unusable — verified empirically).
R_MTF = float(2 * 6)
SIGMA_MTF = R_MTF/2.355
print(f"MTF half-power radius: {R_MTF:.1f}px (speckle grain ~ {2*LC_PX:.0f}px)", flush=True)

GT_OBJ = gen_objects(NTRAIN+NTEST, seed=7)
SPK = add_noise(conv_psf(GT_OBJ, PSF))
SPK_TR, SPK_TE = SPK[:NTRAIN], SPK[NTRAIN:]
OBJ_TE = GT_OBJ[NTRAIN:]

results = {}
models = {}
models["raw"] = train(0.0, EPOCHS, LR)
models["matched"] = train(SIGMA_MTF*0.9, 3, LR*0.3, init_model=models["raw"])
models["half"] = train(SIGMA_MTF*0.45, 3, LR*0.3, init_model=models["raw"])
# sanity: training targets must actually differ across modes
d_rm = float((lowpass(GT_OBJ[:50],0.0)-lowpass(GT_OBJ[:50],SIGMA_MTF*0.9)).pow(2).mean())
d_rh = float((lowpass(GT_OBJ[:50],0.0)-lowpass(GT_OBJ[:50],SIGMA_MTF*0.45)).pow(2).mean())
print(f"target L2 diff raw-vs-matched: {d_rm:.5f} | raw-vs-half: {d_rh:.5f}", flush=True)

REF = lowpass(OBJ_TE, SIGMA_MTF*0.9)
for mode in ["raw","matched","half"]:
    with torch.no_grad():
        pred = models[mode](SPK_TE)
        p_in = psnr(lowpass(pred, SIGMA_MTF*0.9), REF)
        h_energy = fft_highfreq_energy(pred, R_MTF)
        diff = (pred[:,0]-REF[:,0])**2
        bg = (OBJ_TE[:,0] < 0.02).all(dim=0)   # pixels empty in ALL test objects
        bg_art = float(diff.reshape(-1, N*N)[:, bg.reshape(-1)].mean()) if bg.any() else 0.0
    results[mode] = {"psnr_inband_vs_ref": round(p_in,2),
                     "hf_energy_frac": round(h_energy,5),
                     "bg_artifact_mse": round(bg_art,6)}
    print(mode, results[mode], flush=True)

sweep = []
sigmas = [0.0, 0.5*SIGMA_MTF, 1.0*SIGMA_MTF, 1.5*SIGMA_MTF, 2.0*SIGMA_MTF]
with torch.no_grad():
    for s in sigmas:
        obj_o = lowpass(OBJ_TE[:100], s)
        y_o = add_noise(conv_psf(obj_o, PSF))
        pred = models["raw"](y_o)
        p_vs_ref = psnr(pred, lowpass(REF[:100], s))
        res = conv_psf(pred, PSF) - y_o
        sweep.append({"blur_sigma_over_mtf": round(s/SIGMA_MTF,2),
                      "psnr_vs_blurred_ref": round(p_vs_ref,2),
                      "fwd_residual_mse": round(float((res**2).mean()),6)})
        print("sweep", sweep[-1], flush=True)

out = {"mtf_radius_px": R_MTF, "speckle_grain_px": 2*LC_PX,
       "decision_rules": "POSITIVE: matched.hf_energy < 0.5*raw.hf_energy and psnr drop < 0.5dB; NEGATIVE: ratio > 0.8x",
       "stage_A_results": results, "stage_B_sweep": sweep}
h_raw, h_mat = results["raw"]["hf_energy_frac"], results["matched"]["hf_energy_frac"]
p_raw, p_mat = results["raw"]["psnr_inband_vs_ref"], results["matched"]["psnr_inband_vs_ref"]
ratio = h_mat/max(h_raw,1e-9)
out["hallucination_ratio_matched_over_raw"] = round(ratio,3)
if ratio < 0.5 and (p_raw - p_mat) < 0.5:
    out["verdict_A"] = "POSITIVE"
elif ratio > 0.8:
    out["verdict_A"] = "NEGATIVE"
else:
    out["verdict_A"] = "MIXED"
print("PILOT_JSON_BEGIN")
print(json.dumps(out, indent=2))
print("PILOT_JSON_END")
