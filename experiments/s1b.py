t0 = time.time()
log(f"device={DEVICE}")
PSF = make_psf(r_aperture=R_APER, seed=1)
psf_dev = PSF.to(DEVICE)
GT_OBJ = gen_objects(NTRAIN+NTEST)
SPK = add_noise(conv_psf(GT_OBJ, PSF))
tr_x, te_x = SPK[:NTRAIN], SPK[NTRAIN:]
tr_obj, te_obj = GT_OBJ[:NTRAIN], GT_OBJ[NTRAIN:]
REF = lowpass(te_obj, SIG)
tr_x_d, tr_obj_d = tr_x.to(DEVICE), tr_obj.to(DEVICE)
log(f"data ready {time.time()-t0:.0f}s")

results = {"config": {"archs": ARCHS, "seeds": SEEDS,
                       "targets": {k: round(v, 3) for k, v in TARGETS.items()},
                       "r_mtf": R_MTF, "epochs": [EPOCHS_BASE, EPOCHS_FT],
                       "device": DEVICE},
           "runs": []}

