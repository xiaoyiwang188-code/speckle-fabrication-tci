"""Fig 2: paired fine-tune vs compute-matched control (main causal result).
Data: results/scaleup_results.json. Single column (3.5in wide)."""
import sys, json
sys.path.insert(0, "paper/figures")
from paper_plot_style import *
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("results/scaleup_results.json"))
runs = d["runs_raw"]

ctrl = {}
for r in runs:
    if r["arm"] == "raw_continued_control":
        ctrl[(r["arch"], r["seed"])] = r["out_of_band_energy"]

fig, ax = plt.subplots(1, 1, figsize=(3.5, 2.6))
for tname, color, mk in [("matched", COL["matched"], "o"), ("half", COL["half"], "s")]:
    xs, ys = [], []
    for r in runs:
        if r["arm"] == f"finetune_{tname}":
            k = (r["arch"], r["seed"])
            c = ctrl[k]
            xs.append(c)
            ys.append(r["out_of_band_energy"])
    ax.scatter(xs, ys, color=color, marker=mk, s=28, zorder=3,
               label=("target 0.9× MTF" if tname == "matched" else "target 0.45× MTF"))
    for x, y in zip(xs, ys):
        ax.plot([x, x], [x, y], color=color, lw=0.8, alpha=0.5, zorder=2)

lim = max(max(ctrl.values()), max(r["out_of_band_energy"] for r in runs if r["arm"].startswith("finetune"))) * 1.15
ax.plot([0, lim], [0, lim], color="k", lw=0.7, ls="--", zorder=1)
ax.text(lim*0.62, lim*0.66, "no change", rotation=45, fontsize=FONT_SIZE-2, color="k")

ax.set_xlabel("control out-of-band energy")
ax.set_ylabel("fine-tuned out-of-band energy")
ax.set_xlim(0, lim); ax.set_ylim(0, lim)
ax.legend(frameon=False, loc="upper left")
fig.savefig(f"{FIG_DIR}/fig2_paired_control.pdf")

# paired statistics for caption
import statistics
ratios_m = [r["out_of_band_energy"]/ctrl[(r["arch"], r["seed"])] for r in runs if r["arm"] == "finetune_matched"]
ratios_h = [r["out_of_band_energy"]/ctrl[(r["arch"], r["seed"])] for r in runs if r["arm"] == "finetune_half"]
print("matched ratio: %.3f +/- %.3f (n=%d, reduced %d/%d)" % (
    statistics.mean(ratios_m), statistics.stdev(ratios_m), len(ratios_m),
    sum(1 for x in ratios_m if x < 1), len(ratios_m)))
print("half ratio: %.3f +/- %.3f" % (statistics.mean(ratios_h), statistics.stdev(ratios_h)))
