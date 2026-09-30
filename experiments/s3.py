import statistics
wiener = {}
te_y_np = te_x[:100].numpy()
H = np.fft.fft2(PSF.numpy())
Hm = np.abs(H)
yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')
r = np.sqrt(((yy-N//2)**2 + (xx-N//2)**2))
for Krel in [1e-3, 1e-2, 1e-1]:
    K = Krel * Hm.max()**2
    Wf = np.conj(H) / (Hm**2 + K)
    for rfac in [1.0, 1.5]:
        r_eff = R_MTF * rfac
        oobs, fwds = [], []
        for y_np in te_y_np[:30]:
            Xh = np.fft.ifft2(Wf * np.fft.fft2(y_np[0])).real
            Xh = np.clip(Xh, 0, None)
            Xh /= max(Xh.max(), 1e-9)
            P = np.fft.fftshift(np.fft.fft2(Xh), dim=(-2, -1)).abs()**2
            oobs.append(float(P[r > r_eff].sum()/P.sum()))
            resd = np.fft.fft2(Xh) - np.fft.fft2(y_np[0])
            fwds.append(float(np.linalg.norm(resd)/np.linalg.norm(np.fft.fft2(y_np[0]))))
        wiener[f"K{Krel}_sup{rfac}"] = {"oob": round(float(np.mean(oobs)), 5),
                                         "rel_fwd": round(float(np.mean(fwds)), 4)}
results["paired_stats"] = stats
results["wiener_sensitivity"] = wiener
results["wall_time_s"] = round(time.time()-t0, 0)

