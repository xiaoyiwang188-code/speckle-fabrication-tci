"""Fig 3: capacity effect. oob by arm for base16 vs base32. Single column."""
import sys, json
sys.path.insert(0, "paper/figures")
from paper_plot_style import *
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("results/scaleup_results.json"))
runs = d["runs_raw"]

arms = ["baseline_raw", "raw_continued_control", "finetune_matched", "finetune_half"]
labels = ["raw\nbaseline", "raw-cont\n(control)", "matched\nfine-tune", "half\nfine-tune"]
archs = [16, 32]
width = 0.35

fig, ax = plt.subplots(1, 1, figsize=(3.5, 2.5))
for ai, arch in enumerate(archs):
    vals, errs = [], []
    for arm in arms:
        v = [r["out_of_band_energy"] for r in runs if r["arm"] == arm and r["arch"] == arch]
        vals.append(np.mean(v)); errs.append(np.std(v))
    x = np.arange(len(arms)) + (ai - 0.5) * width
    ax.bar(x, vals, width, yerr=errs, capsize=2,
           color=[COL["accent"], COL["control"], COL["matched"], COL["half"]],
           alpha=[1.0, 1.0, 1.0 if ai else 0.55][0] if False else 1.0,
           edgecolor="k", linewidth=0.5,
           hatch=["" , "", "", ""][0] if ai == 0 else "///"*(0), label=f"base {arch}")
# redo with clean legend: two hatch/styles
plt.close(fig)
fig, ax = plt.subplots(1, 1, figsize=(3.5, 2.5))
colors = [COL["accent"], COL["control"], COL["matched"], COL["half"]]
for ai, arch in enumerate(archs):
    vals, errs = [], []
    for arm in arms:
        v = [r["out_of_band_energy"] for r in runs if r["arm"] == arm and r["arch"] == arch]
        vals.append(np.mean(v)); errs.append(np.std(v))
    x = np.arange(len(arms)) + (ai - 0.5) * width
    ax.bar(x, vals, width, yerr=errs, capsize=2, color=colors,
           edgecolor="k", linewidth=0.5, hatch="" if ai == 0 else "///",
           label=f"base {arch} (n=3 seeds)")
ax.set_xticks(np.arange(len(arms)))
ax.set_xticklabels(labels, fontsize=FONT_SIZE-1)
ax.set_ylabel("out-of-band energy")
ax.legend(frameon=False, ncol=2, loc="upper left")
fig.savefig(f"{FIG_DIR}/fig3_capacity.pdf")
print("fig3 saved")
