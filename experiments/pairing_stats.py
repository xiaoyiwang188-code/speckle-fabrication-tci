"""D2 fix: recompute per-pair speckle-GT pixel correlations (same-id vs mismatched)
and persist as results/pairing_stats.json (previously only in chat logs).
Prints summary to stdout; JSON between markers."""
import json, statistics
import numpy as np
from PIL import Image
import pathlib

root = pathlib.Path(r"C:/zcode/SCI/artifacts/dsc_data")
def sid(p): return int(p.name.split("__")[-1][:-4])
gt = {sid(p): np.array(Image.open(p)).astype(np.float64)/255
      for p in root.glob("Ground Truth__Digit__*.tif")}
tr = sorted(root.glob("Speckle Measurement__Data for training*__*.tif"))
def load(p):
    a = np.array(Image.open(p)).astype(np.float64)
    return a/a.max()

pairs = [(s, sid(s)) for s in tr if sid(s) in gt]
same, mism = [], []
ids = sorted(gt.keys())
for s, i in pairs[:20]:
    spk = load(s)
    c_same = float(np.corrcoef(spk.ravel(), gt[i].ravel())[0,1])
    j = next(k for k in ids if k != i)
    c_mism = float(np.corrcoef(spk.ravel(), gt[j].ravel())[0,1])
    same.append(round(c_same, 4))
    mism.append(round(c_mism, 4))

out = {
 "description": "per-pair pixel correlation between speckle and ground-truth digits",
 "same_id_correlations": same,
 "mismatched_correlations": mism,
 "same_mean": round(statistics.mean(same), 4),
 "same_min": min(same), "same_max": max(same),
 "mism_mean": round(statistics.mean(mism), 4),
 "mism_min": min(mism), "mism_max": max(mism),
 "n_pairs": len(same)}
print(f"same-id: {min(same):.3f}--{max(same):.3f} (mean {statistics.mean(same):.3f})")
print(f"mismatched: {min(mism):.3f}--{max(mism):.3f} (mean {statistics.mean(mism):.3f})")
print("PAIR_JSON_BEGIN")
print(json.dumps(out, indent=1))
print("PAIR_JSON_END")
