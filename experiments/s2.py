import copy, statistics
t0 = time.time()
ft_results = []
total_ft = len(ARCHS)*len(SEEDS)*3
k = 0
import copy
for base in ARCHS:
    for seed in SEEDS:
        torch.manual_seed(seed)
        raw_model = UNet(base).to(DEVICE)
        raw_model = train(raw_model, tr_x_d, tr_obj_d, EPOCHS_BASE, LR)
        ctrl = copy.deepcopy(raw_model)
        ctrl = train(ctrl, tr_x_d, tr_obj_d, EPOCHS_FT, LR*0.3)
        e_ctrl = endpoints(ctrl, te_x.to(DEVICE), REF.to(DEVICE), psf_dev)
        results["runs"].append({"arm": "raw_continued_control", **e_ctrl,
                                 "arch": base, "seed": seed})
        del ctrl
        k += 1
        log(f"ft {k}/{total_ft} control ({time.time()-t0:.0f}s)")
        for tname, sig in [("matched", TARGETS["matched"]), ("half", TARGETS["half"])]:
            m = copy.deepcopy(raw_model)
            m = train(m, tr_x_d, lowpass(tr_obj_d, sig), EPOCHS_FT, LR*0.3)
            e = endpoints(m, te_x.to(DEVICE), REF.to(DEVICE), psf_dev)
            results["runs"].append({"arm": f"finetune_{tname}", **e,
                                     "arch": base, "seed": seed})
            ft_results.append((tname, base, seed, e, e_ctrl))
            del m
            k += 1
            log(f"ft {k}/{total_ft} ({time.time()-t0:.0f}s)")
        del raw_model
        torch.cuda.empty_cache()

import statistics
stats = {}
for tname in ["matched", "half"]:
    diffs_oob, diffs_fwd = [], []
    for t, base, seed, e, e_ctrl in ft_results:
        if t != tname:
            continue
        diffs_oob.append(e["out_of_band_energy"] - e_ctrl["out_of_band_energy"])
        diffs_fwd.append(e["rel_fwd_consistency"] - e_ctrl["rel_fwd_consistency"])
    stats[tname] = {
        "n": len(diffs_oob),
        "mean_oob_diff": round(statistics.mean(diffs_oob), 5),
        "std_oob_diff": round(statistics.stdev(diffs_oob), 5) if len(diffs_oob) > 1 else None,
        "mean_rel_fwd_diff": round(statistics.mean(diffs_fwd), 4),
        "oob_reduced_in": f"{sum(1 for d in diffs_oob if d < 0)}/{len(diffs_oob)}"}

