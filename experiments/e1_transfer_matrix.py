"""E1: transfer-loss matrix x multi-metric distance reanalysis (Component A).

Pre-registered: 12 orthogonal diffusers (aperture radius x height dist x spectral shape),
12 trainings, full PSNR[i][j] transfer matrix, loss L[i,j]=PSNR[i,i]-PSNR[i,j].
Three candidate statistical distances; monotone vs segmented (changepoint) fits compared
by dBIC; permutation null calibrates changepoint false-positive rate.
Verdict: metric-robust law vs threshold artifact.
"""
import sys, math, json
import numpy as np
import torch
sys.path.insert(0, r"C:\zcode\SCI\论文项目\experiments")
from sim_common import (log, make_psf, conv_psf, lowpass, gen_objects, add_noise,
                        train_model, psnr, N, NTRAIN, NTEST, mtf_radius_analytic)

torch.manual_seed(0); np.random.seed(0)

# factor grid: 3 grain x 2 height x 2 spectral shape = 12 diffusers
RADII = [4, 6, 8]
HEIGHTS = ["gauss", "binary"]
SMOOTHS = [0.0, 1.0]
KEYS = [(r, h, s) for r in RADII for h in HEIGHTS for s in SMOOTHS]
EPOCHS = 12

# objects shared across all trainings (identical protocol)
GT_OBJ = gen_objects(NTRAIN + NTEST, seed=7)

def build_diffuser(key, idx):
    r, h, s = key
    psf = make_psf(r_aperture=r, seed=100+idx, height_dist=h, smooth_sigma=s)
    return psf, mtf_radius_analytic(r)

# ---------- distance metrics between diffusers ----------
def phase_samples(key, idx):
    """Phase-field sample values (height distribution fingerprint)."""
    r, h, s = key
    psf_ph = make_psf(r_aperture=r, seed=100+idx, height_dist=h, smooth_sigma=s)
    return None  # placeholder; real phase recovered below

def phi_field(key, idx):
    import torch as _t
    g = _t.Generator().manual_seed(100+idx)
    r, h, s = key
    phi = _t.randn(N, N, generator=g)
    if h == "binary":
        phi = _t.sign(phi) * math.pi
    else:
        phi = phi / phi.std() * math.pi
    if s > 0:
        from sim_common import gauss_kernel_1d, sep_conv2d
        k = gauss_kernel_1d(s)
        phi = sep_conv2d(phi[None, None], k, k)[0, 0]
    return phi.numpy().ravel()

def wasserstein_height(a_keys, b_keys, a_idx, b_idx):
    xa = np.sort(phi_field(a_keys, a_idx))
    xb = np.sort(phi_field(b_keys, b_idx))
    n = min(len(xa), len(xb))
    return float(np.abs(xa[:n] - xb[:n]).mean())

def speckle_power_spectrum(spk):
    F_ = torch.fft.fftshift(torch.fft.fft2(spk[:, 0]), dim=(-2, -1)).abs()**2
    yy, xx = torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij')
    r = torch.sqrt(((yy-N//2)**2 + (xx-N//2)**2).float()).round().long()
    prof = torch.zeros(int(r.max())+1); cnt = torch.zeros(int(r.max())+1)
    prof.index_add_(0, r.flatten(), F_.mean(0).flatten())
    cnt.index_add_(0, r.flatten(), torch.ones(N*N))
    p = (prof/cnt)
    return (p / p.sum()).numpy()

def spectral_js(pa, pb, eps=1e-12):
    pa = np.clip(pa, eps, None); pb = np.clip(pb, eps, None)
    pa /= pa.sum(); pb /= pb.sum()
    m = 0.5*(pa+pb)
    return float(0.5*np.sum(pa*np.log(pa/m)) + 0.5*np.sum(pb*np.log(pb/m)))

def patch_mmd(sa, sb, n_patch=60, side=8, seed=0):
    rng = np.random.default_rng(seed)
    def feats(s):
        arr = s[:, 0].numpy()
        idxs = rng.choice(arr.shape[0], size=min(n_patch, arr.shape[0]), replace=False)
        ps = []
        for i in idxs:
            y0 = rng.integers(0, N-side); x0 = rng.integers(0, N-side)
            ps.append(arr[i, y0:y0+side, x0:x0+side].ravel())
        p = np.stack(ps)
        return p / (np.linalg.norm(p, axis=1, keepdims=True) + 1e-8)
    fa, fb = feats(sa), feats(sb)
    def k(u, v, sigmas=(0.5, 1.0, 2.0)):
        d2 = ((u[:, None, :]-v[None, :, :])**2).sum(-1)
        return sum(np.exp(-d2/(2*s*s)) for s in sigmas)/len(sigmas)
    return float(k(fa, fa).mean() + k(fb, fb).mean() - 2*k(fa, fb).mean())

# ---------- run ----------
log("E1: training 12 models on orthogonal diffusers...")
psfs, spectra, psnr_mat = {}, {}, {}
test_objs = GT_OBJ[NTRAIN:]
for i, key in enumerate(KEYS):
    psf, r_mtf = build_diffuser(key, i)
    psfs[i] = psf
    sig = r_mtf/2.355*0.9
    tr_obj = lowpass(GT_OBJ[:NTRAIN], sig)          # band-matched target (fixed protocol)
    tr_spk = add_noise(conv_psf(GT_OBJ[:NTRAIN], psf))
    model = None
    for attempt, sd in enumerate((12345, 999, 4242)):
        m = train_model(tr_spk, tr_obj, epochs=EPOCHS, seed=sd)
        with torch.no_grad():
            out_std = float(m(tr_spk[:16]).std())
        if out_std > 0.01:                           # collapse guard: reject constant outputs
            model = m
            log(f"  [{i}] trained ok (seed {sd}, out_std {out_std:.3f})")
            break
        log(f"  [{i}] collapse detected at seed {sd} (out_std {out_std:.4f}); retrying")
    if model is None:
        model = m
    spectra[i] = None
    psnr_mat[i] = {}
    with torch.no_grad():
        ref_j_cache = {}
        for j, key_j in enumerate(KEYS):
            psf_j, r_mtf_j = build_diffuser(key_j, j)
            sig_j = r_mtf_j/2.355*0.9
            if j not in ref_j_cache:
                te_obj_j = lowpass(test_objs, sig_j)
                te_spk_j = add_noise(conv_psf(test_objs, psf_j))
                ref_j_cache[j] = (te_spk_j, te_obj_j)
            te_spk_j, te_obj_j = ref_j_cache[j]
            pred = model(te_spk_j)
            psnr_mat[i][j] = round(psnr(pred, te_obj_j), 3)
    log(f"  [{i}] {key}: diag PSNR={psnr_mat[i][i]}")

# transfer loss L[i][j] = PSNR[i][i] - PSNR[i][j]  (i==j -> 0)
L = np.zeros((len(KEYS), len(KEYS)))
for i in KEYS.index and range(len(KEYS)):
    for j in range(len(KEYS)):
        L[i, j] = psnr_mat[i][i] - psnr_mat[i][j]

# pairwise distances (upper triangle)
pairs = []
for i in range(len(KEYS)):
    for j in range(i+1, len(KEYS)):
        d_w = wasserstein_height(KEYS[i], KEYS[j], i, j)
        # spectral distance from each side's transfer direction
        sp_i = speckle_power_spectrum(add_noise(conv_psf(test_objs[:20], psfs[i])))
        sp_j = speckle_power_spectrum(add_noise(conv_psf(test_objs[:20], psfs[j])))
        d_s = spectral_js(sp_i, sp_j)
        sa = add_noise(conv_psf(test_objs[:20], psfs[i]))
        sb = add_noise(conv_psf(test_objs[:20], psfs[j]))
        d_m = patch_mmd(sa, sb)
        # loss observed when training on i, testing on j  and the reverse
        l_ij = L[i, j]; l_ji = L[j, i]
        pairs.append({"i": KEYS[i], "j": KEYS[j], "d_w": round(d_w, 4),
                      "d_s": round(d_s, 6), "d_m": round(d_m, 6),
                      "loss_ij": round(l_ij, 3), "loss_ji": round(l_ji, 3)})

# ---------- fits: monotone power-law vs segmented, per distance metric ----------
def fit_mono(d, y):
    m = d > 1e-9
    x = np.log(d[m]); yy = np.log(np.clip(y[m], 1e-3, None))
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, yy, rcond=None)
    pred = np.exp(A @ coef)
    rss = float(((y[m]-pred)**2).sum())
    return rss, 2, pred

def fit_seg(d, y, fracs=(0.2, 0.35, 0.5, 0.65, 0.8)):
    order = np.argsort(d)
    d_s, y_s = d[order], y[order]
    n = len(d_s)
    best = None
    for f in fracs:
        t = d_s[int(n*f)]
        m1, m2 = d <= t, d > t
        if m1.sum() < 4 or m2.sum() < 4:
            continue
        rss1, c1 = _lin(d[m1], y[m1]); rss2, c2 = _lin(d[m2], y[m2])
        rss = rss1 + rss2; k = 4
        if best is None or rss < best[0]:
            best = (rss, k, t, c1, c2)
    return best

def _lin(x, y):
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    return float(((y-pred)**2).sum()), coef

def bic(rss, n, k):
    return n*math.log(max(rss, 1e-12)/n) + k*math.log(n)

results_fits = {}
rng = np.random.default_rng(0)
for metric in ["d_w", "d_s", "d_m"]:
    d = np.array([p[metric] for p in pairs])
    # symmetric loss: max of both directions per pair (severity of mismatch)
    y = np.array([max(p["loss_ij"], p["loss_ji"]) for p in pairs])
    m = d > 1e-9
    d, y = d[m], y[m]
    n = len(d)
    rss_mo, k_mo, _ = fit_mono(d, y)
    seg = fit_seg(d, y)
    b_mo = bic(rss_mo, n, k_mo)
    if seg is None:
        results_fits[metric] = {"n": n, "note": "segmented fit failed"}
        continue
    rss_se, k_se, t_se, _, _ = seg
    b_se = bic(rss_se, n, k_se)
    dBIC = b_se - b_mo
    # permutation null: shuffle y, refit segmented, distribution of dBIC
    null = []
    for _ in range(100):
        yp = rng.permutation(y)
        r1, _, _ = fit_mono(d, yp)
        s2 = fit_seg(d, yp)
        if s2 is None:
            continue
        null.append(bic(s2[0], n, s2[1]) - bic(r1, n, 2))
    null = np.array(null)
    p_perm = float((null <= dBIC).mean())
    results_fits[metric] = {
        "n_pairs": n, "dBIC_seg_minus_mono": round(dBIC, 2),
        "seg_wins": bool(dBIC < -10), "changepoint_at": round(float(t_se), 4),
        "perm_p_seg_beats_null": round(p_perm, 3),
        "verdict": "LAW(metric-robust)" if dBIC < -10 and p_perm < 0.05 else "MONOTONE_OR_ARTIFACT"}

out = {"design": {"diffusers": [list(map(str, k)) for k in KEYS], "epochs": EPOCHS,
                  "ntrain": NTRAIN, "pre_registered": "3 distances, segmented-vs-monotone BIC, permutation null x100"},
       "psnr_matrix": {str(i): psnr_mat[i] for i in psnr_mat},
       "pairs": pairs, "fits": results_fits}
print("E1_JSON_BEGIN"); print(json.dumps(out, indent=1)); print("E1_JSON_END")
