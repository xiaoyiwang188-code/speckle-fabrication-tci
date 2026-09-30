total_base = len(ARCHS)*len(SEEDS)*len(TARGETS)
k = 0
for base in ARCHS:
    for seed in SEEDS:
        torch.manual_seed(seed)
        raw_model = UNet(base).to(DEVICE)
        raw_model = train(raw_model, tr_x_d, tr_obj_d, EPOCHS_BASE, LR)
        results["runs"].append({"arm": "baseline_raw",
                                 **endpoints(raw_model, te_x.to(DEVICE), REF.to(DEVICE), psf_dev),
                                 "arch": base, "seed": seed, "target": "raw"})
        del raw_model
        k += 1
        log(f"baseline {k}/{total_base} ({time.time()-t0:.0f}s)")
        for tname, sig in [("matched", TARGETS["matched"]), ("half", TARGETS["half"])]:
            torch.manual_seed(seed+1)
            m = UNet(base).to(DEVICE)
            m = train(m, tr_x_d, lowpass(tr_obj_d, sig), EPOCHS_BASE, LR)
            results["runs"].append({"arm": f"baseline_{tname}",
                                     **endpoints(m, te_x.to(DEVICE), REF.to(DEVICE), psf_dev),
                                     "arch": base, "seed": seed, "target": tname})
            del m
            k += 1
            log(f"baseline {k}/{total_base} ({time.time()-t0:.0f}s)")
        torch.cuda.empty_cache()

