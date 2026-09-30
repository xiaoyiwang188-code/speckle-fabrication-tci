"""Fig 5: robustness — (a) spatially-varying PSF ratios; (b) real-data preliminary.
Panel a: E4 results. Panel b: DSC speckle autocorr profile + pairing NCC bars."""
import sys, json, re
sys.path.insert(0, "paper/figures")
from paper_plot_style import *
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pathlib

# ---- panel a: E4 ----
e4 = open("results/e4_stdout.txt", encoding="utf-8").read()
m = re.search(r"E4_JSON_BEGIN\n(.*)\nE4_JSON_END", e4, re.S)
d4 = json.loads(m.group(1))["results"]
ratios = d4["ratios_matched_over_control"]

# ---- panel b1: DSC speckle autocorr radial profile (grain + platform) ----
root = pathlib.Path(r"C:/zcode/SCI/artifacts/dsc_data")
tr = sorted(root.glob("Speckle Measurement__Data for training*__*.tif"))[:10]
def load(p):
    a = np.array(Image.open(p)).astype(np.float64)
    return a / a.max()
def radial_ac(img):
    x = img - img.mean()
    F = np.fft.fft2(x)
    ac = np.fft.fftshift(np.fft.ifft2(F * np.conj(F)).real)
    ac /= ac.max()
    yy, xx = np.meshgrid(np.arange(512), np.arange(512), indexing="ij")
    r = np.sqrt((yy - 256) ** 2 + (xx - 256) ** 2).round().astype(int)
    n = np.bincount(r.ravel(), minlength=512)[:512].astype(float)
    prof = np.bincount(r.ravel(), weights=ac.ravel(), minlength=512)[:512]
    return prof / np.maximum(n, 1)
prof = np.zeros(512)
for s in tr:
    prof += radial_ac(load(s))
prof /= len(tr)

fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.5))

ax = axes[0]
ax.plot(np.arange(200), prof[:200], color=COL["matched"], lw=1.2)
ax.axvspan(0, 6, color="0.85", alpha=0.7)
ax.text(3, prof[10]*1.4, "grain", fontsize=FONT_SIZE-2, ha="center")
ax.text(95, prof[10]*1.4, "platform = object information", fontsize=FONT_SIZE-2, ha="center")
ax.set_xlabel("lag radius (px)")
ax.set_ylabel("speckle autocorrelation")
ax.set_xlim(0, 200)

# panel a as inset-style second half? keep fig5 = 2 panels: (a) E4 bars, (b) autocorr
plt.close(fig)
fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.4))

ax = axes[0]
x = np.arange(len(ratios))
ax.bar(x, ratios, color=COL["matched"], edgecolor="k", linewidth=0.5, width=0.6)
ax.axhline(1.0, color="k", lw=0.7, ls="--")
ax.set_xticks(x); ax.set_xticklabels(["1", "2", "3"])
ax.set_xlabel("fine-tune epoch")
ax.set_ylabel("matched/control ratio")
ax.set_ylim(0, 1.1)
ax.text(0.02, 0.95, "spatially varying PSF", transform=ax.transAxes, fontsize=FONT_SIZE-1, va="top")

ax = axes[1]
ax.plot(np.arange(200), prof[:200], color=COL["matched"], lw=1.2)
ax.axvspan(0, 6, color="0.85", alpha=0.7)
ax.annotate("grain", xy=(3, prof[8]), xytext=(22, prof[8]+0.12), fontsize=FONT_SIZE-2,
            arrowprops=dict(arrowstyle="-", lw=0.6))
ax.annotate("object information (platform)", xy=(90, prof[60]), xytext=(55, prof[60]+0.35),
            fontsize=FONT_SIZE-2, arrowprops=dict(arrowstyle="-", lw=0.6))
ax.set_xlabel("lag radius (px)")
ax.set_ylabel("speckle autocorrelation")
ax.set_xlim(0, 200)

fig.savefig(f"{FIG_DIR}/fig5_robustness.pdf")
print("fig5 saved")
