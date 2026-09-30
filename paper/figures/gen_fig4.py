"""Fig 4: fabrication vs forward-fidelity trade-off. Wiener grid vs DL arms."""
import sys, json
sys.path.insert(0, "paper/figures")
from paper_plot_style import *
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("results/scaleup_results.json"))
w = d["wiener_sensitivity"]
runs = d["runs_raw"]

fig, ax = plt.subplots(1, 1, figsize=(3.5, 2.6))
wx = [max(v["oob"], 1.2e-4) for v in w.values()]   # floor for log axis (two settings have oob=0)
wy = [v["rel_fwd"] for v in w.values()]
ax.scatter(wx, wy, marker="x", s=36, color=COL["wiener"], zorder=4, label="Wiener (6 settings)")
ax.axvline(1.2e-4, color="0.6", lw=0.6, ls=":")
ax.text(1.3e-4, 8.2, "2 settings:\noob $\\approx$ 0", fontsize=FONT_SIZE-3, color="0.35")

for arm, lab, c, mk in [("baseline_raw", "raw-trained DL", COL["raw"], "^"),
                         ("finetune_matched", "matched fine-tune", COL["matched"], "o"),
                         ("finetune_half", "half fine-tune", COL["half"], "s")]:
    xs = [r["out_of_band_energy"] for r in runs if r["arm"] == arm]
    ys = [r["rel_fwd_consistency"] for r in runs if r["arm"] == arm]
    ax.scatter(xs, ys, marker=mk, s=28, color=c, zorder=3, label=lab)

ax.set_xscale("log")
ax.set_xlabel("out-of-band energy (fabrication proxy)")
ax.set_ylabel("relative forward error")
ax.legend(frameon=False, loc="center right", fontsize=FONT_SIZE-2)
ax.annotate("", xy=(0.0006, 6.0), xytext=(0.02, 6.0),
            arrowprops=dict(arrowstyle="<->", lw=0.7, color="k"))
ax.text(0.004, 6.6, "2–6× fabrication gap", fontsize=FONT_SIZE-2, ha="center")
fig.savefig(f"{FIG_DIR}/fig4_tradeoff.pdf")
print("fig4 saved")
