"""Claim audit: verify every number in the manuscript against raw result files.
Prints pass/fail per check to stdout; final JSON between CLAIM_JSON markers."""
import json, statistics, math, sys
import numpy as np
sys.path.insert(0, "experiments")

REPORT = []
def check(claim, value_paper, value_data, tol=0.005, note=""):
    ok = value_paper is not None and value_data is not None and abs(value_paper - value_data) <= tol
    REPORT.append({"claim": claim, "paper": value_paper, "data": value_data, "ok": ok, "note": note})
    print(("OK  " if ok else "FAIL") + f" | {claim} | paper={value_paper} data={value_data} {note}")

d = json.load(open("results/scaleup_results.json"))
runs = d["runs_raw"]
def vals(arm, arch=None):
    return [r["out_of_band_energy"] for r in runs if r["arm"] == arm and (arch is None or r["arch"] == arch)]
def psnrs(arm):
    return [r["psnr_bandlimited"] for r in runs if r["arm"] == arm]

# --- baselines (Table 1 / Sec 4.1 / abstract) ---
check("raw baseline oob 0.0210", 0.0210, round(statistics.mean(vals("baseline_raw")), 4), 0.0002)
check("raw baseline std 0.0073", 0.0073, round(statistics.stdev(vals("baseline_raw")), 4), 0.0002)
check("matched baseline oob 0.0066", 0.0066, round(statistics.mean(vals("baseline_matched")), 4), 0.0002)
check("matched baseline std 0.0006", 0.0006, round(statistics.stdev(vals("baseline_matched")), 4), 0.0002)
check("half baseline oob 0.0036", 0.0036, round(statistics.mean(vals("baseline_half")), 4), 0.0002)
check("half baseline std 0.0004", 0.0004, round(statistics.stdev(vals("baseline_half")), 4), 0.0002)
check("ratio 3.2x raw/matched", 3.2, round(statistics.mean(vals("baseline_raw"))/statistics.mean(vals("baseline_matched")), 1), 0.1)
check("ratio 5.9x raw/matched (paper 3.2x / 5.9x)", 5.9, round(statistics.mean(vals("baseline_raw"))/statistics.mean(vals("baseline_half")), 1), 0.1)
check("PSNR raw 16.5", 16.5, round(statistics.mean(psnrs("baseline_raw")), 1), 0.1)
check("PSNR matched 31.7", 31.7, round(statistics.mean(psnrs("baseline_matched")), 1), 0.1)
check("PSNR half 22.1", 22.1, round(statistics.mean(psnrs("baseline_half")), 1), 0.1)

# --- paired stats (Sec 4.2 / abstract) ---
ps = d["paired_stats_finetune_vs_control"]
check("matched ratio 0.34", 0.34, round(ps["matched"]["mean_oob_ratio"], 2), 0.005)
check("matched ratio std 0.11", 0.11, round(ps["matched"]["std_oob_ratio"], 2), 0.005)
check("half ratio 0.20", 0.20, round(ps["half"]["mean_oob_ratio"], 2), 0.005)
check("half ratio std 0.08", 0.08, round(ps["half"]["std_oob_ratio"], 2), 0.005)
check("6/6 matched", True, ps["matched"]["oob_reduced_in"] == "6/6", 0)
check("6/6 half", True, ps["half"]["oob_reduced_in"] == "6/6", 0)
check("rel-fwd diff +0.026", 0.026, round(ps["matched"]["mean_rel_fwd_diff"], 3), 0.001)
check("rel-fwd diff half +0.006", 0.006, round(ps["half"]["mean_rel_fwd_diff"], 3), 0.001)

# --- "raw continuation increases" claim (paper: 0.0210 -> 0.0238, ~13%) ---
ctrl_mean = statistics.mean(vals("raw_continued_control"))
raw_mean = statistics.mean(vals("baseline_raw"))
check("control vs raw: 0.0210 -> 0.0238 (paper)", 0.0238, round(ctrl_mean, 4), 0.0006,
      note=f"(actual control mean {ctrl_mean:.4f} vs raw {raw_mean:.4f})")

# --- rel-fwd baseline range 0.36-0.40 (paper, excl. baseline_half per text) ---
fwd = [r["rel_fwd_consistency"] for r in runs if r["arm"] in ("finetune_matched", "finetune_half",
                                                              "raw_continued_control", "baseline_raw")]
check("rel-fwd range lo 0.36", 0.36, round(min(fwd), 2), 0.011)
check("rel-fwd range hi 0.40", 0.40, round(max(fwd), 2), 0.02, note=f"(actual max {max(fwd):.3f})")

# --- capacity (Sec 4.3; values as printed in the current manuscript) ---
check("base32 raw 0.027", 0.027, round(statistics.mean(vals("baseline_raw", 32)), 3), 0.002)
check("base16 raw 0.015", 0.015, round(statistics.mean(vals("baseline_raw", 16)), 3), 0.002)
check("base32 control 0.030", 0.030, round(statistics.mean(vals("raw_continued_control", 32)), 3), 0.002)
check("base16 control 0.017", 0.017, round(statistics.mean(vals("raw_continued_control", 16)), 3), 0.002)
def ratio_arch(arch):
    v = [r["out_of_band_energy"]/next(c["out_of_band_energy"] for c in runs
            if c["arm"] == "raw_continued_control" and c["arch"] == r["arch"] and c["seed"] == r["seed"])
         for r in runs if r["arm"] == "finetune_matched" and r["arch"] == arch]
    return round(statistics.mean(v), 2)
check("base32 matched ratio 0.25", 0.25, ratio_arch(32), 0.015)
check("base16 matched ratio 0.44", 0.44, ratio_arch(16), 0.02)

# --- Wiener (Sec 4.4; fair rescaled recompute + stored sweep) ---
import torch, torch.nn.functional as F
from sim_common import make_psf, conv_psf, gen_objects, add_noise
N = 64
PSF = make_psf(r_aperture=6, seed=1)
GT = gen_objects(1600, seed=7)
SPK = add_noise(conv_psf(GT, PSF))
te_x = SPK[1200:]
H = np.fft.fft2(PSF.numpy()); Hm = np.abs(H)
rescaled = {}
for Krel in [1e-3, 1e-2, 1e-1]:
    Wf = np.conj(H) / (Hm**2 + Krel*Hm.max()**2)
    rels = []
    for k in range(30):
        y_np = te_x[k, 0].numpy()
        Xh = np.fft.ifft2(Wf * np.fft.fft2(y_np)).real
        Xh = np.clip(Xh, 0, None)
        x_t = torch.from_numpy(Xh).float().view(1,1,N,N)
        y_t = te_x[k:k+1]
        hx = conv_psf(x_t, PSF)
        a = float((hx*y_t).sum() / max((hx*hx).sum(), 1e-12))
        res = a*hx - y_t
        rels.append(float((res**2).sum().sqrt() / (y_t**2).sum().sqrt()))
    rescaled[Krel] = round(float(np.mean(rels)), 3)
check("Wiener rescaled rel-fwd lo 0.52", 0.52, min(rescaled.values()), 0.01)
check("Wiener rescaled rel-fwd hi 0.55", 0.55, max(rescaled.values()), 0.01)
check("~40% higher (mean 0.53 vs 0.38)", 0.40, round((statistics.mean(rescaled.values())/0.385 - 1), 2), 0.06)
check("DL rel-fwd mean ~0.385 (range check)", 0.385, round(statistics.mean(fwd), 3), 0.02)
w = d["wiener_sensitivity"]
wv = [v["oob"] for v in w.values()]
nz = [x for x in wv if x > 0]
check("Wiener oob nonzero-min 0.0003", 0.0003, round(min(nz), 4), 0.0002,
      note=f"(zeros: {sum(1 for x in wv if x==0)} of {len(wv)})")
check("Wiener oob max 0.0032", 0.0032, round(max(wv), 4), 0.0002)

# --- E4 / E2 / E1 ---
import re
e4 = json.loads(re.search(r"E4_JSON_BEGIN\n(.*)\nE4_JSON_END", open("results/e4_stdout.txt", encoding="utf-8").read(), re.S).group(1))
check("E4 ratios 0.52/0.60/0.54", True, e4["results"]["ratios_matched_over_control"] == [0.522, 0.596, 0.544], 0, note=str(e4["results"]["ratios_matched_over_control"]))
e2 = json.loads(re.search(r"E2_JSON_BEGIN\n(.*)\nE2_JSON_END", open("results/e2_stdout.txt", encoding="utf-8").read(), re.S).group(1))
check("E2 sweep 0.52/0.49/0.50", True, e2["results"]["sweep_out_of_band_matched_over_control"] == [0.522, 0.486, 0.498], 0, note=str(e2["results"]["sweep_out_of_band_matched_over_control"]))
e1 = json.loads(re.search(r"E1_JSON_BEGIN\n(.*)\nE1_JSON_END", open("results/e1_stdout.txt", encoding="utf-8").read(), re.S).group(1))
fits = e1["fits"]
check("E1 dBIC -1.4/+5.6/+3.3 (run3)", True,
      [round(fits[k]["dBIC_seg_minus_mono"],1) for k in ("d_w","d_s","d_m")] == [-1.4, 5.6, 3.3], 0,
      note=str([fits[k]["dBIC_seg_minus_mono"] for k in ("d_w","d_s","d_m")]))
check("E1 perm p 0.08/0.91/0.41 (run3)", True,
      [round(fits[k]["perm_p_seg_beats_null"],2) for k in ("d_w","d_s","d_m")] == [0.08, 0.91, 0.41], 0,
      note=str([fits[k]["perm_p_seg_beats_null"] for k in ("d_w","d_s","d_m")]))
maxloss = max(max(p["loss_ij"], p["loss_ji"]) for p in e1["pairs"])
check("E1 max loss 15.0 dB (run3)", 15.0, round(maxloss, 1), 0.1)
sens_txt = open("results/e1_sensitivity.txt", encoding="utf-8").read()
check("E1 collapse-exclusion sensitivity: conclusion stable", True,
      "CONCLUSION STABLE (no changepoint in any metric, both fits): True" in sens_txt, 0)

# --- real data (Sec 5) ---
reg = json.loads(re.search(r"REG_JSON_BEGIN\n(.*)\nREG_JSON_END", open("results/registration_fix2.txt", encoding="utf-8").read(), re.S).group(1))
check("grain FWHM 1.93px", 1.93, reg["system_bandwidth"]["grain_fwhm_px"], 0.01)
spk = [r["L_spk"] for r in reg["per_pair"]]
check("platform mean 191px", 191, round(statistics.mean(spk), 0), 1, note=f"(actual {statistics.mean(spk):.1f})")
check("platform std 1.3px", 1.3, round(statistics.stdev(spk), 1), 0.4, note=f"(actual {statistics.stdev(spk):.2f})")
reg3 = json.loads(re.search(r"REG_JSON_BEGIN\n(.*)\nREG_JSON_END", open("results/registration_fix3.txt", encoding="utf-8").read(), re.S).group(1))
check("2D NCC CV 1.02", 1.02, round(reg3["alpha_cv"], 2), 0.01)
check("2D NCC matched 0.60", 0.60, round(reg3["ncc_matched"], 2), 0.01, note=f"(actual {reg3['ncc_matched']})")
check("2D NCC mismatched 0.50", 0.50, round(reg3["ncc_mismatched"], 2), 0.01, note=f"(actual {reg3['ncc_mismatched']})")
check("2D NCC Welch t 3.2", 3.2, round(reg3["welch_t"], 1), 0.15, note=f"(actual {reg3['welch_t']})")

# --- summary ---
n_fail = sum(1 for r in REPORT if not r["ok"])
print(f"\n=== CLAIM AUDIT: {len(REPORT)-n_fail}/{len(REPORT)} checks pass ===")
for r in REPORT:
    if not r["ok"]:
        print("  FAIL:", r)
print("CLAIM_JSON_BEGIN")
print(json.dumps({"checks": REPORT, "failures": n_fail}, indent=1))
print("CLAIM_JSON_END")
