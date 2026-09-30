"""One (arch, seed) unit: 6 runs, ~4-5 min on T4. Reads UBASE/USEED env.
Requires s0.py executed first (functions + data in kernel). Prints unit JSON."""
import os, copy, json, time
import torch
import torch.nn.functional as F

UBASE = int(os.environ["UBASE"])
USEED = int(os.environ["USEED"])

t0 = time.time()
unit = {"arch": UBASE, "seed": USEED, "runs": []}
TGT_GPU = {t: lowpass(tr_obj, s_).to(DEVICE)
           for t, s_ in [("matched", TARGETS["matched"]), ("half", TARGETS["half"])]}

torch.manual_seed(USEED)
raw = UNet(UBASE).to(DEVICE)
raw = train(raw, tr_x_d, tr_obj_d, EPOCHS_BASE, LR)
unit["runs"].append({"arm": "baseline_raw",
                     **endpoints(raw, te_x.to(DEVICE), REF.to(DEVICE), psf_dev)})
print("raw done", round(time.time()-t0), flush=True)

for tname, sig in [("matched", TARGETS["matched"]), ("half", TARGETS["half"])]:
    torch.manual_seed(USEED + 1)
    m = UNet(UBASE).to(DEVICE)
    m = train(m, tr_x_d, TGT_GPU[tname], EPOCHS_BASE, LR)
    unit["runs"].append({"arm": f"baseline_{tname}",
                         **endpoints(m, te_x.to(DEVICE), REF.to(DEVICE), psf_dev)})
    del m
    print(f"baseline_{tname} done", round(time.time()-t0), flush=True)

ctrl = copy.deepcopy(raw)
ctrl = train(ctrl, tr_x_d, tr_obj_d, EPOCHS_FT, LR*0.3)
e_ctrl = endpoints(ctrl, te_x.to(DEVICE), REF.to(DEVICE), psf_dev)
unit["runs"].append({"arm": "raw_continued_control", **e_ctrl})
del ctrl
print("control done", round(time.time()-t0), flush=True)

for tname, sig in [("matched", TARGETS["matched"]), ("half", TARGETS["half"])]:
    m = copy.deepcopy(raw)
    m = train(m, tr_x_d, TGT_GPU[tname], EPOCHS_FT, LR*0.3)
    unit["runs"].append({"arm": f"finetune_{tname}",
                         **endpoints(m, te_x.to(DEVICE), REF.to(DEVICE), psf_dev)})
    del m
    print(f"finetune_{tname} done", round(time.time()-t0), flush=True)

unit["wall_s"] = round(time.time()-t0)
print("UNIT_JSON_BEGIN")
print(json.dumps(unit, indent=1))
print("UNIT_JSON_END")
