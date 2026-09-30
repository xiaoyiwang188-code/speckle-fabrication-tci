# Scale-registration fix design - deepseek-v4-flash

## Response

REASONING-ONLY:
∫_{f>r_hp} |H_est(f)|² |X(f)|² df / ∫_{f≤r_hp} |H_est|²|X|²? Or Wiener deconvolution:
      Ŝ? Actually Wiener baseline: deconvolve speckle using H and GT? The speckle is random? Hmm.
Let's parse "out-of-band energy of a Wiener baseline + one trained tiny CNN that converts our real-data section from 'preliminary pairing signal' to a quantitative claim usable for Photonics Research."
They want demonstrate that speckle contains object information beyond simple correlation. Wiener baseline: reconstruct object estimate by Wiener deconvolution from speckle using H? If speckle is random not convolution, maybe not. But if H estimated as transfer function from GT to speckle, maybe we can apply Wiener to a "forward model" to remove OTF. Need design:
- Wiener deconvolution baseline: Given measured speckle S and estimated OTF H, compute reconstructed object \hat O = ℱ^{-1} [ S(f) conj(H(f)) / (|H(f)|² + η) ] for each pair. Since S is speckle (random), Wiener will fail? The claim maybe "we can invert system OTF and recover object under CNN." Hmm.

Need be careful. The user wrote "measured MTF support + out-of-band energy of a Wiener baseline + one trained tiny CNN". Out-of-band energy of Wiener baseline: if estimated H support is limited, frequencies beyond support should be zero; Wiener baseline should have low out-of-band energy if using H as filter? Need propose.

Quantitative target:
- Use aligned GT as input, speckle as output? Train tiny CNN to map speckle → GT alignment? Wait "one trained tiny CNN to convert real-data section from preliminary pairing signal to quantitative claim" maybe CNN reconstruction from speckle to GT after alignment. But task is registration design, not CNN. We need set target for paper:
  - After alignment, the cross-validated normalized linear reconstruction SNR from Wiener filter exceeds a threshold? However speckle is random; "out-of-band energy" measure H's frequency response. Maybe no.

Let's define quantitative deliverable:
1. Estimated MTF support r_hp (with confidence interval) > 10px, so system passes more than 1px.
2. Out-of-band energy (OOBE) of residual after a linear Wiener inversion:
   For each held-out pair, apply Wiener filter W(f) = conj(H(f))/(|H(f)|²+η) to S, compute recovered R. Define error before/after alignment? Hmm.
Maybe "out-of-band energy" refers to H_est: After Wiener inversion, frequencies beyond estimated support should not contribute; if they contain signal energy, H support wrong. But no.

Let's search memory: In microscopy, "out-of-band background" in OTF indicates resolution. They may compute:
- For linear imaging model s = h * o + noise, OTF H. If support radius is R, then a Weiner estimate concentrates object energy within support. "Out-of-band energy" of Fourier ring correlation (FRC) maybe.
- Train tiny CNN to reconstruct from speckle; compare to Wiener baseline in terms of SSIM/error. If CNN beats Wiener on real data, that's quantitative.

Need propose targets:
- "We will report median SSIM/PSNR of CNN reconstruction on held-out pairs, and its advantage over the Wiener baseline by at least X% (or absolute SSIM > 0.3)." But user asks "minimal deliverable ... converts ... to quantitative claim". Need set achievable? We don't know. We can state "minimum bar: same-id NCC of CNN output vs GT > paired speckle NCC by 0.15, and statistically significant over mismatched (p<0.01)."

Need be terse but comprehensive.

Let's outline final answer in numbered plan.

Maybe include "decision tree" at end:
1. Run robust autocorr FWHM.
2. If FWHM ratio finite: initialize scale α0.
3. Run profile fitting; if fit residual low (<0.05 normalized) and α profile within 20% of α_FWHM, accept α*.
4. Run NCC scale search around α*; if score lift > threshold, use NCC to refine scale and estimate dx,dy/θ. If lift fails but profile succeeded, proceed with α* and set dx=dy=0? But if translations unknown, use phase retrieval? Need decision tree handle.
5. Re-estimate OTF; check r_hp. If r_hp in band, success.
6. Else if OTF degenerates, diagnose scale flip; test reciprocal α; maybe rotation; if still fail, inconclusive.

Need address "registration failed but diagnosis confirmed" vs "inconclusive":
- If OTF r_hp remains < 3 after alignment, that confirms failure diagnosis (scale mismatch not fixed/Otf invalid) but not registration.
- If scale estimators disagree and NCC lift < threshold and OTF r_hp not in band, inconclusive.

Need provide "candidate estimators should evaluate and pick/combine": Our plan includes all three and combination.

Need ensure formulas exact. Let's write robust formula for FWHM_with shot noise more explicitly.

Function `radial_autocorr(I, Rmax=None)`:

```
def radial_autocorr(I, Rmax=128):
    I = np.asarray(I, float)
    I = I - np.median(I)          # or I.mean()
    N = I.shape[0]
    Ip = np.zeros((2*N, 2*N), dtype=float)
    Ip[:N,:N] = I? Wait if zero-pad by placing image at one corner, linear autocorr via circular with zero padding works if image in top-left. To get shifts in [-N,N] with zero-pad, center? If image is at corner of 2Nx2N then circular shifts wrap zeros from opposite edge; for shifts where image overlaps itself without wrap, valid for all shifts from -(N-1) to N-1? Actually zero-padding at top-left corner: circular autocorr for shift (N,0) between top-left and bottom-right? It includes zeros; no wrap because outside zeros in all directions due to circular? Wait circular wrap from right edge to left edge where zeros except top-left image? For shift dx positive, the image at left overlaps copy shifted? The padded array has zeros everywhere except top-left NxN. Circular shift by dx moves zeros from left into the right edge? When shifted by +dx, the top-left block moves right; the vacated left columns are filled from wrap-around of rightmost columns. But because rightmost columns are zero (since image only top-left), no image wrap. Similarly for negative. So valid for -N<shift<N. Good.
    F = np.fft.fft2(Ip)
    C = np.fft.ifft2(F * np.conj(F)).real   # circular autocorr, zero at (0,0)? Need shift dx dy at (dx+? Actually if both arrays same, autocorr C[dy,dx] = sum_{y,x} Ip[y,x] Ip[(y+dy) mod 2N, (x+dx) mod 2N]. This C[0,0]=sum. For dx positive, C[0,dx]=sum_{y,x} Ip[y,x] Ip[y, x+dx mod]. Since Ip only nonzero at x<N and x+dx<N if dx positive; valid overlap length N-dx. For dx negative, C[0,mod dx]=same as C[0,N-dx]? Because due to circular, C[0,N-dx] corresponds shift -dx? Actually if we want C for dx from -N+1..N-1, use fftshift? Let's not detail.
    center=(N,N) after fftshift? If we use C = np.fft.fftshift(C, axes=(0,1)), center=(N,N). Then C[center + (dy,dx)] for small signed shifts corresponds? fftshift moves zero lag to N,N; C[N+dy,N+dx] = circular autocorr for shift with wrap? Should be okay.
```

But image at corner and fftshift? Maybe easier: Use scipy.signal.fftconvolve(I, I[::-1,::-1], mode='full')? That gives linear autocorrelation full size (2N-1)x(2N-1), with zero lag at center. For 512x512, fftconvolve may be memory heavy but okay. But numpy only? User says numpy/scipy only. Use `scipy.signal.fftconvolve`. Formula:
```
from scipy.signal import fftconvolve
A = fftconvolve(I - mean, (I - mean)[::-1,::-1], mode='full')
center = (I.shape[0]-1, I.shape[1]-1)
A = A[center[0]-Rmax:center[0]+Rmax+1, center[1]-Rmax:center[1]+Rmax+1]
```
A at (dy,dx) for shift vector. This is exact linear. Then compute radial bins. Use full? 512x512 fftconvolve with zero padding to 1024. Good.

Need robust normalization:
```
A = A / A[center]
r = sqrt(dy^2 + dx^2)
profile = [median(A[np.abs(r-bin)<0.5]) for bin in range(1,Rmax+1)]
# subtract far baseline:
bg = median(profile[Rmax//2:])? But if autocorr not decayed by Rmax/2, baseline wrong. Choose Rmax = 80? The FWHM likely tens; background can be estimated at tail 60-80. Use bg = median(profile[int(Rmax*0.7):Rmax+1]) 
A0 = median of profile[0:2]? Use C(0).
# normalized:
p = (profile - bg) / (A0 - bg)
```
For speckle, A0 includes shot noise
