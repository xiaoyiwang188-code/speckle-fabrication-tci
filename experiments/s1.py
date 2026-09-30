"""Scale-up of component B on Colab T4 (reviewer minimum config).

Self-contained (no local imports, no filesystem writes): 2 architectures x
3 seeds x 3 target bandwidths x {baseline 20ep, raw-continued 4ep control,
matched fine-tune 4ep} + Wiener K/support sensitivity sweep.
No-reference primary endpoints. Results JSON -> stdout; progress -> stderr.
"""
import json, math, time, sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
N = 64
NTRAIN, NTEST, BS = 2400, 400, 128
EPOCHS_BASE, EPOCHS_FT = 20, 4
LR = 1e-3
NOISE_SIGMA = 0.05
R_APER = 6
R_MTF = float(2 * R_APER)
SIG = R_MTF / 2.355 * 0.9
SEEDS = [12345, 777, 2024]
TARGETS = {"raw": 0.0, "matched": SIG*0.9, "half": SIG*0.45}
ARCHS = [16, 32]

def log(msg):
    print(msg, file=sys.stderr, flush=True)

def gauss_kernel_1d(sigma):
    r = int(max(1, round(3*sigma)))
    x = torch.arange(-r, r+1, dtype=torch.float32)
    k = torch.exp(-0.5*(x/sigma)**2)
    return k/k.sum()

def sep_conv2d(x, kx, ky):
    return F.conv2d(F.conv2d(x, kx.view(1,1,-1,1), padding=(kx.numel()//2,0)),
                    ky.view(1,1,1,-1), padding=(0,ky.numel()//2))

def make_psf(r_aperture=6, seed=1):
    g = torch.Generator().manual_seed(seed)
    phi = torch.randn(N, N, generator=g)
    phi = phi / phi.std() * math.pi
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij')
    rr = torch.sqrt(((yy-N//2)**2 + (xx-N//2)**2))
    pupil = (rr <= r_aperture).float()
    field = torch.fft.ifft2(torch.fft.ifftshift(pupil * torch.exp(1j*2*math.pi*phi)))
    psf = torch.abs(field)**2
    return psf / psf.sum()

def conv_psf(imgs, psf):
    out = F.conv2d(imgs, psf.view(1,1,N,N).flip(-1).flip(-2), padding=N//2)
    return out[..., :N, :N]

def lowpass(imgs, sigma):
    if sigma <= 0:
        return imgs
    k = gauss_kernel_1d(sigma)
    return sep_conv2d(imgs, k, k)

def gen_objects(n, seed=42):
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(seed)
    out = torch.zeros(n, 1, N, N)
    font = None
    for cand in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        try:
            font = ImageFont.truetype(cand, 40)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    for i in range(n):
        img = Image.new("L", (N, N), 0)
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        d.text((int(rng.integers(4, 24)), int(rng.integers(0, 20))),
               str(int(rng.integers(0, 10))), fill=255, font=font)
        out[i, 0] = torch.from_numpy(np.asarray(img, dtype=np.float32)/255.0)
    return out

def add_noise(spk):
    return (spk + NOISE_SIGMA*2*torch.randn_like(spk)*spk.sqrt().clamp(min=0)).clamp(min=0)

class UNet(nn.Module):
    def __init__(self, base=16):
        super().__init__()
        def blk(i, o):
            return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.ReLU(),
                                 nn.Conv2d(o, o, 3, padding=1), nn.ReLU())
        self.e1 = blk(1, base); self.e2 = blk(base, base*2); self.e3 = blk(base*2, base*4)
        self.pool = nn.MaxPool2d(2)
        self.d2 = blk(base*4+base*2, base*2); self.d1 = blk(base*2+base, base)
        self.out = nn.Conv2d(base, 1, 3, padding=1)
    def forward(self, x):
        x1 = self.e1(x); x2 = self.e2(self.pool(x1)); x3 = self.e3(self.pool(x2))
        u2 = F.interpolate(x3, size=x2.shape[-2:], mode='bilinear', align_corners=False)
        d2 = self.d2(torch.cat([u2, x2], 1))
        u1 = F.interpolate(d2, size=x1.shape[-2:], mode='bilinear', align_corners=False)
        d1 = self.d1(torch.cat([u1, x1], 1))
        return (self.out(d1) + x).clamp(0, 1)

def train(model, x, tgt, epochs, lr):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    n = x.shape[0]
    for ep in range(epochs):
        perm = torch.randperm(n, device=x.device)
        for i in range(0, n, BS):
            idx = perm[i:i+BS]
            loss = F.mse_loss(model(x[idx]), tgt[idx])
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    return model

def psnr(a, b):
    return 10*math.log10(1.0/max(((a-b)**2).mean().item(), 1e-12))

def hf_energy(imgs, r_mtf):
    P = torch.fft.fftshift(torch.fft.fft2(imgs[:, 0]), dim=(-2, -1)).abs()**2
    yy, xx = torch.meshgrid(torch.arange(N, device=imgs.device),
                            torch.arange(N, device=imgs.device), indexing='ij')
    r = torch.sqrt(((yy-N//2)**2 + (xx-N//2)**2))
    return float(P[:, r > r_mtf].sum() / P.sum())

def rel_fwd(pred, y, psf):
    res = conv_psf(pred, y.new_tensor(0)) if False else conv_psf(pred, psf) - y
    return float((res**2).sum().sqrt() / (y**2).sum().sqrt().clamp(min=1e-12))

def endpoints(model, te_x, te_ref, psf):
    with torch.no_grad():
        pred = model(te_x)
        return {"psnr_bandlimited": round(psnr(pred, te_ref), 2),
                "out_of_band_energy": round(hf_energy(pred, R_MTF), 5),
                "rel_fwd_consistency": round(rel_fwd(pred, te_x, psf), 4)}

def main():
    t0 = time.time()
    log(f"device={DEVICE}")
    PSF = make_psf(r_aperture=R_APER, seed=1)
    psf_dev = PSF.to(DEVICE)
    GT_OBJ = gen_objects(NTRAIN+NTEST)
    SPK = add_noise(conv_psf(GT_OBJ, PSF))
    tr_x, te_x = SPK[:NTRAIN], SPK[NTRAIN:]
    tr_obj, te_obj = GT_OBJ[:NTRAIN], GT_OBJ[NTRAIN:]
    REF = lowpass(te_obj, SIG)
    tr_x_d, tr_obj_d = tr_x.to(DEVICE), tr_obj.to(DEVICE)
    log(f"data ready {time.time()-t0:.0f}s")

    results = {"config": {"archs": ARCHS, "seeds": SEEDS,
                           "targets": {k: round(v, 3) for k, v in TARGETS.items()},
                           "r_mtf": R_MTF, "epochs": [EPOCHS_BASE, EPOCHS_FT],
                           "device": DEVICE},
               "runs": []}

    total_base = len(ARCHS)*len(SEEDS)*len(TARGETS)
    k = 0
    for base in ARCHS:
        for seed in SEEDS:
            torch.manual_seed(seed)
            raw_model = UNet(base).to(DEVICE)
            raw_model = train(raw_model, tr_x_d, tr_obj_d, EPOCHS_BASE, LR)
            results["runs"].append({"arm": "baseline_raw",
                                     **endpoints(raw_model, te_x.to(DEVICE), REF.to(DEVICE), psf_dev),
                                     "arch": base, "seed": seed, "target": "raw"})
            del raw_model
            k += 1
            log(f"baseline {k}/{total_base} ({time.time()-t0:.0f}s)")
            for tname, sig in [("matched", TARGETS["matched"]), ("half", TARGETS["half"])]:
                torch.manual_seed(seed+1)
                m = UNet(base).to(DEVICE)
                m = train(m, tr_x_d, lowpass(tr_obj_d, sig), EPOCHS_BASE, LR)
                results["runs"].append({"arm": f"baseline_{tname}",
                                         **endpoints(m, te_x.to(DEVICE), REF.to(DEVICE), psf_dev),
                                         "arch": base, "seed": seed, "target": tname})
                del m
                k += 1
                log(f"baseline {k}/{total_base} ({time.time()-t0:.0f}s)")
            torch.cuda.empty_cache()

    log("STAGE1 DONE")
