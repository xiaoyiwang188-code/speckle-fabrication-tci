"""E1 sensitivity: does the negative conclusion (no changepoint) survive
excluding collapse-affected decoders (indices 2 and 6 in run3)?
Re-fits monotone vs segmented from the stored pair data, with and without
those decoders, and reports dBIC/p for both."""
import json, re, math
import numpy as np

src = open("results/e1_stdout.txt", encoding="utf-8").read()
e1 = json.loads(re.search(r"E1_JSON_BEGIN\n(.*)\nE1_JSON_END", src, re.S).group(1))
pairs = e1["pairs"]

def fit_mono(d, y):
    m = d > 1e-9
    x = np.log(d[m]); yy = np.log(np.clip(y[m], 1e-3, None))
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, yy, rcond=None)
    pred = np.exp(A @ coef)
    return float(((y[m]-pred)**2).sum()), 2

def _lin(x, y):
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(((y - A@coef)**2).sum())

def fit_seg(d, y, fracs=(0.2, 0.35, 0.5, 0.65, 0.8)):
    order = np.argsort(d); d_s, y_s = d[order], y[order]
    n = len(d_s); best = None
    for f in fracs:
        t = d_s[int(n*f)]
        m1, m2 = d <= t, d > t
        if m1.sum() < 4 or m2.sum() < 4: continue
        rss = _lin(d[m1], y[m1]) + _lin(d[m2], y[m2])
        if best is None or rss < best[0]:
            best = (rss, 4, float(t))
    return best

def bic(rss, n, k):
    return n*math.log(max(rss,1e-12)/n) + k*math.log(n)

rng = np.random.default_rng(0)
def analyze(exclude, label):
    print(f"--- {label} (excluded decoders: {sorted(exclude) or 'none'}) ---")
    res = {}
    for metric in ["d_w", "d_s", "d_m"]:
        d = np.array([p[metric] for p in pairs if p["i_key_idx"] not in exclude and p["j_key_idx"] not in exclude])
        y = np.array([max(p["loss_ij"], p["loss_ji"]) for p in pairs if p["i_key_idx"] not in exclude and p["j_key_idx"] not in exclude])
        m = d > 1e-9; d, y = d[m], y[m]; n = len(d)
        rss_mo, k_mo = fit_mono(d, y)
        seg = fit_seg(d, y)
        b_mo = bic(rss_mo, n, k_mo)
        b_se = bic(seg[0], n, seg[1])
        dbic = b_se - b_mo
        null = []
        for _ in range(100):
            yp = rng.permutation(y)
            r1, _ = fit_mono(d, yp)
            s2 = fit_seg(d, yp)
            null.append(bic(s2[0], n, s2[1]) - bic(r1, n, 2))
        p = float((np.array(null) <= dbic).mean())
        res[metric] = (round(dbic,2), round(p,2), n)
        print(f"  {metric}: dBIC={dbic:.2f} p={p:.2f} n_pairs={n}")
    return res

# need key idx mapping: pairs store "i"/"j" as lists like [4, 'gauss', 0.0]
for p in pairs:
    p["i_key_idx"] = None; p["j_key_idx"] = None
KEYS = [[r, h, s] for r in (4,6,8) for h in ("gauss","binary") for s in (0.0,1.0)]
for p in pairs:
    for idx, k in enumerate(KEYS):
        if list(p["i"]) == k: p["i_key_idx"] = idx
        if list(p["j"]) == k: p["j_key_idx"] = idx

full = analyze(set(), "full matrix")
excl = analyze({2, 6}, "excluding collapse-affected decoders 2,6")
concl = all(v[1] > 0.05 for v in full.values()) and all(v[1] > 0.05 for v in excl.values())
print(f"\nCONCLUSION STABLE (no changepoint in any metric, both fits): {concl}")
