"""Table 1: combined summary (LaTeX float) from scaleup_results.json. Prints to stdout
(shell-redirect to paper/figures/TABLE_1_main.tex)."""
import json, statistics

d = json.load(open("results/scaleup_results.json"))
runs = d["runs_raw"]
arms = [("baseline_raw", "Raw baseline (20 ep)"),
        ("baseline_matched", "Bandwidth-matched baseline (20 ep)"),
        ("baseline_half", "Half-bandwidth baseline (20 ep)"),
        ("raw_continued_control", "Raw-continued control (+4 ep)"),
        ("finetune_matched", "Matched fine-tune (4 ep)"),
        ("finetune_half", "Half fine-tune (4 ep)")]

rows = []
for arm, lab in arms:
    v = [r["out_of_band_energy"] for r in runs if r["arm"] == arm]
    p = [r["psnr_bandlimited"] for r in runs if r["arm"] == arm]
    rows.append((lab, statistics.mean(v), statistics.stdev(v),
                 statistics.mean(p), statistics.stdev(p), len(v)))

ctrl = {(r["arch"], r["seed"]): r["out_of_band_energy"]
        for r in runs if r["arm"] == "raw_continued_control"}

def paired(arm):
    rs = [r["out_of_band_energy"]/ctrl[(r["arch"], r["seed"])]
          for r in runs if r["arm"] == arm]
    return statistics.mean(rs), statistics.stdev(rs), sum(1 for x in rs if x < 1), len(rs)

pm = paired("finetune_matched")
ph = paired("finetune_half")

lines = []
lines.append(r"\begin{table}[t]")
lines.append(r"\centering")
lines.append(r"\small")
lines.append(r"\caption{Out-of-band energy (fabrication proxy) and band-limited PSNR across arms; mean$\pm$std over 6 units (2 architectures $\times$ 3 seeds). The paired block reports fine-tune-to-control ratios within units.}")
lines.append(r"\label{tab:main}")
lines.append(r"\begin{tabular}{lcc}")
lines.append(r"\toprule")
lines.append(r"Arm & Out-of-band energy & PSNR (dB) \\")
lines.append(r"\midrule")
for lab, mo, so, mp, sp, n in rows:
    lines.append(f"{lab} & ${mo:.4f} \\pm {so:.4f}$ & ${mp:.1f} \\pm {sp:.1f}$ \\\\")
lines.append(r"\midrule")
lines.append(r"\multicolumn{3}{l}{Paired (fine-tune vs.\ control, within unit)} \\")
lines.append(f"Matched fine-tune ratio & ${pm[0]:.2f} \\pm {pm[1]:.2f}$ & reduced {pm[2]}/{pm[3]} \\\\")
lines.append(f"Half fine-tune ratio & ${ph[0]:.2f} \\pm {ph[1]:.2f}$ & reduced {ph[2]}/{ph[3]} \\\\")
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\end{table}")
print("\n".join(lines))
