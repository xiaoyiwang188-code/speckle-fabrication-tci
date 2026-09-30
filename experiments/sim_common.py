"""Shared simulation infra for E1-E3 (evolved from pilot_gt_bandwidth.py).

Physics: frequency-domain circular aperture + random phase -> intensity PSF;
shift-invariant linear speckle model y = conv(x, PSF_I) + approx Poisson-Gaussian noise.
Residual U-Net decoder (global skip, no all-zero attractor).
All scripts print progress to stderr and final JSON to stdout (shell-redirected).
"""
import math, sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

N = 64
NTRAIN = 1200
NTEST = 300
BS = 64
LR = 1e-3
NOISE_SIGMA = 0.05
BASE_SEED = 12345

def log(*a):
    print(*a, file=sys.stderr, flush=True)

def gauss_kernel_1d(sigma):
    r = int(max(1, round(3*sigma)))
    x = torch.arange(-r, r+1, dtype=torch.float32)
    k = torch.exp(-0.5*(x/sigma)**2)
    return k/k.sum()

def sep_conv2d(x, kx, ky):
    return F.conv2d(F.conv2d(x, kx.view(1,1,-1,1), padding=(kx.numel()//2,0)),
                    ky.view(1,1,1,-1), padding=(0,ky.numel()//2))

def lowpass(imgs, sigma):
    if sigma <= 0:
        return imgs
    k = gauss_kernel_1d(sigma)
    return sep_conv2d(imgs, k, k)

def make_psf(r_aperture=6, seed=1, height_dist="gauss", smooth_sigma=0.0):
    """Aperture radius r -> speckle grain ~ N/(2r).
    height_dist: 'gauss' (phi ~ N(0,pi)) or 'binary' (phi = +/-pi).
    smooth_sigma: spatial smoothing of the phase field (spectral-shape factor).
    """
    g = torch.Generator().manual_seed(seed)
    phi = torch.randn(N, N, generator=g)
    if height_dist == "binary":
        phi = torch.sign(phi) * 0.5   # effective phase ±π after the exp(i·2πφ) factor
    else:
        phi = phi / phi.std() * math.pi
    if smooth_sigma > 0:
        k = gauss_kernel_1d(smooth_sigma)
        phi = sep_conv2d(phi[None,None], k, k)[0,0]
        phi = (phi - phi.mean()) / (phi.std() + 1e-8) * math.pi
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij')
    rr = torch.sqrt((yy-N//2)**2 + (xx-N//2)**2)
    pupil = (rr <= r_aperture).float()
    field = torch.fft.ifft2(torch.fft.ifftshift(pupil * torch.exp(1j*2*math.pi*phi)))
    psf = torch.abs(field)**2
    return psf / psf.sum()

def conv_psf(imgs, psf):
    out = F.conv2d(imgs, psf.view(1,1,N,N).flip(-1).flip(-2), padding=N//2)
    return out[..., :N, :N]

def mtf_radius_analytic(r_aperture):
    return float(2 * r_aperture)  # MTF support = autocorrelation of field support

def gen_objects(n, seed=42, extent=1.0):
    """Sharp (non-antialiased) digit objects; extent scales font size and confines position."""
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(seed)
    out = torch.zeros(n, 1, N, N)
    fs = max(12, int(40 * extent))
    try:
        font = ImageFont.truetype("arial.ttf", fs)
    except Exception:
        font = ImageFont.load_default()
    margin = int(N * (1 - extent) / 2)
    for i in range(n):
        img = Image.new("L", (N, N), 0)
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        x0 = int(margin + rng.integers(0, max(1, N - 2*margin - fs - 4)))
        y0 = int(margin + rng.integers(0, max(1, N - 2*margin - fs)))
        d.text((x0, y0), str(int(rng.integers(0, 10))), fill=255, font=font)
        out[i, 0] = torch.from_numpy(np.asarray(img, dtype=np.float32) / 255.0)
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
        self.d2 = blk(base*4 + base*2, base*2); self.d1 = blk(base*2 + base, base)
        self.out = nn.Conv2d(base, 1, 3, padding=1)
    def forward(self, x):
        x1 = self.e1(x); x2 = self.e2(self.pool(x1)); x3 = self.e3(self.pool(x2))
        u2 = F.interpolate(x3, size=x2.shape[-2:], mode='bilinear', align_corners=False)
        d2 = self.d2(torch.cat([u2, x2], 1))
        u1 = F.interpolate(d2, size=x1.shape[-2:], mode='bilinear', align_corners=False)
        d1 = self.d1(torch.cat([u1, x1], 1))
        return (self.out(d1) + x).clamp(0, 1)

def psnr(a, b):
    return 10*math.log10(1.0/max(((a-b)**2).mean().item(), 1e-12))

def hf_energy(imgs, r_mtf):
    """Energy fraction outside MTF support radius (out-of-band / hallucination proxy)."""
    P = torch.fft.fftshift(torch.fft.fft2(imgs[:, 0]), dim=(-2, -1)).abs()**2
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij')
    r = torch.sqrt(((yy-N//2)**2 + (xx-N//2)**2).float())
    return float(P[:, r > r_mtf].sum() / P.sum())

def rel_fwd_residual(pred, y, psf):
    """||H(x_hat)-y|| / ||y||  (relative forward-model consistency, E2 primary endpoint)."""
    res = conv_psf(pred, psf) - y
    return float((res**2).sum().sqrt() / (y**2).sum().sqrt().clamp(min=1e-12))

def wiener_reconstruct(y, psf, K=1e-2):
    """Closed-form linear baseline: Wiener deconvolution in Fourier domain."""
    H = torch.fft.fft2(psf)
    Y = torch.fft.fft2(y[:, 0])
    Xf = torch.conj(H) / (H.abs()**2 + K) * Y
    return torch.fft.ifft2(Xf).real.clamp(0, 1).unsqueeze(1)

def train_model(x_spk, target, epochs, lr=LR, seed=BASE_SEED, init_model=None):
    torch.manual_seed(seed)
    model = UNet() if init_model is None else init_model
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    n = x_spk.shape[0]
    for ep in range(epochs):
        perm = torch.randperm(n)
        for i in range(0, n, BS):
            idx = perm[i:i+BS]
            loss = F.mse_loss(model(x_spk[idx]), target[idx])
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    return model

@torch.no_grad()
def eval_psnr(model, spk_te, ref):
    pred = model(spk_te)
    return psnr(lowpass(pred, 0), ref)  # lowpass(x,0)=x
