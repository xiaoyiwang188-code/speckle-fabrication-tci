"""Shared publication style for all paper figures (IEEEtran)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FONT_SIZE = 8          # IEEE two-column body is 10pt but figures read at ~8pt
FIG_DIR = "paper/figures"

matplotlib.rcParams.update({
    "font.size": FONT_SIZE,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "axes.labelsize": FONT_SIZE,
    "axes.titlesize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE - 1,
    "ytick.labelsize": FONT_SIZE - 1,
    "legend.fontsize": FONT_SIZE - 1,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "text.usetex": False,
    "mathtext.fontset": "stix",
})

COL = {
    "raw": "#d62728",
    "matched": "#1f77b4",
    "half": "#2ca02c",
    "control": "#7f7f7f",
    "wiener": "#9467bd",
    "accent": "#ff7f0e",
}
MARKERS = ["o", "s", "^", "D", "v", "P"]
