# Full draft review (IEEE TCI) - deepseek-v4-flash

## Response

REASONING:
e not exact. But if a reader compares, conflict. Need flag.

Need "in the main arm matched fine-tune ratio 0.34; robustness shift-invariant sweep 0.50" Could be because robustness sweep uses base 16 only? Need it should specify. Since "two architectures and three seeds" main. Need "Fine-tune-length sweep" maybe with base16 only and matched target, but not stated. Need ask.

Also "matched-to-control out-of-band ratio is 0.52, 0.60, 0.54" Under position-dependent operator. If main effect 0.34, robustness shows weaker but still; okay. "same arms" maybe not. Need flag under "numerical consistency/reproducibility."

Need "BIC values" "ΔBIC = -0.4, +6.0, +2.6" Need they say "under all three metrics, segmented fit fails to beat smooth monotone fit by criterion." If ΔBIC = BIC_seg - BIC_smooth, positive values favor smooth. Negative -0.4 favors segment but by less than 2, so fail. Good. But need define. Fine.

Need "speckle intensity autocorrelation decomposition into sub-pixel grain peak superposed on wide platform extending to ~191 px lag" "sub-pixel grain peak" maybe width 1.93px? Wait FWHM 1.93 px, "sub-pixel" inconsistent: 1.93 px is nearly 2px not sub-pixel. Maybe autocorrelation grain peak "sub-pixel grain peak" vs FWHM 1.93 px? No, if grain FWHM 1.93 px, peak width is not sub-pixel. Need flag? Let's check: "grain full-width at half-maximum is 1.93 px" Could be "grain peak" has sub-pixel width? The text says "speckle intensity autocorrelation decomposes into a sub-pixel grain peak superposed on a wide platform" but earlier "grain FWHM is 1.93 px" = ~2px. "Sub-pixel" should be <1px. In speckle imaging, speckle intensity autocorrelation has a narrow peak of width of a speckle (about 1 px) maybe "sub-pixel" if sampled? If FWHM 1.93 pixels, not sub-pixel. Need flag numerical inconsistency: either "one-to-two-pixel grain peak" or provide evidence it's sub-pixel before quoting 1.93 px. But maybe "grain full-width at half-maximum 1.93px" corresponds to "MTF support 52% Nyquist"; "sub-pixel grain peak" could be if pixel size larger? Eh. Need flag minor.

Need "cross-spectral transfer-function estimate degenerates because linear-convolution forward model does not hold for speckle (correct structure lives in autocorrelation domain, per Siegert relation)" Hmm For speckle intensity, the relation between object intensity and speckle intensity is actually convolution? Under memory effect, speckle intensity pattern for a thin diffuser is convolution of object with speckle PSF (incoherent, shift-invariant) provided object is illuminated by spatially incoherent? Wait in "noninvasive imaging through scattering layers" by Katz et al., the autocorrelation of the speckle intensity equals object autocorrelation plus background, with approximations. The field at camera is scatter from object? The linear convolution relation might hold for coherent? Actually speckle intensity is not a convolution with object intensity? Let's think: In "scattering media" with memory effect, if object is embedded behind diffuser, the speckle image is convolution of object's complex amplitude? For incoherent object, intensity at camera equals |h * u|^2? If h is complex field PSF, and u is object field; intensity = |h*u|^2, not linear in object intensity. But in "noninvasive imaging" they use speckle autocorrelation of object intensity. The draft's simulated forward model "y = h * x + n" where h is intensity PSF and x object intensity is a shift-invariant incoherent speckle PSF? Is a "speckle intensity PSF" a point spread function in intensity: for a point object, camera intensity pattern is a speckle pattern. The intensity from extended incoherent object is indeed convolution of object intensity with speckle PSF (incoherent imaging). Is that correct? For a thin diffuser illuminated by a point source, speckle pattern; for multiple independent object points, intensities add (incoherent) -> convolution. So linear conv can hold in intensity. Then why "linear-convolution forward model does not hold for speckle"? Maybe because each object point field random phase? Actually if object is illuminated coherently, object points have fixed phase, intensities interfere; but with "incoherent illumination" maybe. The protocol may simulate intensity PSF. In real data, "object-to-speckle mapping is learned end-to-end because not analytically parsimonious" but maybe okay. Need no.

Need "We used public experimental speckle dataset (measured through diffusers, paired ground-truth digits; 240 files sampled)" Need dataset name/identifier; "public experimental dataset" unspecified. Need flag reproducibility. Maybe real-data section too preliminary; should include dataset citation.

Need "A real-data assessment ... system parameters and pairing statistics are quantified" But no actual reconstruction? Fine as boundary condition. Need "out-of-band energy cannot be measured without forward model; they instead quantify environment." Good.

Need "Wiener linear baseline constrains fabrication budget (2–6x below learned models)" In abstract maybe "Wiener baseline constrains the fabrication budget (2–6x below learned models)" If "Wiener's OOB values range 0.0003-0.0032, 2-6x below learned models" Could be "the learned models' OOB is 2-6x above Wiener in corresponding cells" Wait if learned raw 0.021, Wiener 0.0032 ratio 6.6; if learned half 0.0036, ratio 1.1. Maybe "2-6x" not universal. Need fix. If in abstract, "orders of magnitude" maybe more accurate? Let's compute: Wiener min 0.0003; raw 0.021 ratio 70. So "up to 70×" below. Why do they choose 2-6? Maybe because "2-6x below learned models" might be "relative forward error 4.4-8.9 vs 0.37-0.47" (factor 12-19?) no. Need "fabrication budget" maybe Wiener "fabrication budget (2-6x below learned models)" Actually "fabrication budget" could be "Wiener uses 2-6x less out-of-band energy than learned models at same forward fidelity"? No. Need investigate.

Maybe "across a grid of six regularization/support settings, the Wiener reconstruction's out-of-band energy stays in 0.0003--0.0032---2--6x below every learned arm in every cell". Wait if "in every cell" maybe they compare each Wiener cell to the learned arm trained with corresponding target bandwidth? Not enough. Need fix to: "Wiener OOB is 0.0003–0.0032, which is 1–70× below the learned arms depending on arm; the learned arms are 2–6× higher than Wiener in the half-power sense?" Need specific.

Potential issue: "two settings drive it to numerical zero" If numerical zero, ratio not "2-6x"; avoid.

Need "relative forward error Wiener 4.4-8.9 vs learned 0.37-0.47" Does "operating point" phrase okay.

Need "Supporting protocol-level rather than label-level reporting" Good.

Need "This paper reports out-of-band energy as fabrication proxy, not perceptual metric." Good.

Need "No-reference forward consistency endpoint" Actually "no-reference" might be confusing because it uses h and y; "no-reference" in image quality means no ground truth x. It also uses forward operator h; okay. Need define "no-reference" (no ground truth) to avoid confusion? It says "requires no ground truth" in eq. Good.

Need "The residual skip removes the all-zero output attractor observed in early pilots" This is a methodological detail; "all-zero output attractor" maybe not needed. Fine.

Need "pre-registered" with "early pilots" maybe okay.

Potential issue: "A companion fine-tune-length sweep under shift-invariant protocol shows same stability (0.52, 0.49, 0.50), which rules out a transient-optimization explanation." Wait if main result says matched fine-tune at 4 epochs reduces to 0.34, and sweep at 4 epochs is 0.50, then there is inconsistency. Maybe "companion" uses half target? It says "same arms" "matched-to-control" maybe yes. Need not use "same stability" if values differ. Need flag.

Need "real-data section says grain FWHM 1.93px, MTF support radius 52% Nyquist." If MTF support radius 52% Nyquist, out-of-band threshold at 0.52*Nyquist. Does that conflict with simulation R_MTF=2r? No.

Need "Single-realization MTF half-power estimation unusable (speckle-dominated)" In real data they use speckle power spectrum grain FWHM; okay.

Need "Speckle intensity autocorrelation (Fig. right)" But Fig. robust combined left/right; perhaps okay. Need if figure caption "robustness" includes real-data autocorrelation; okay.

Need "Results mean ± sd over six units unless stated." Good.

Need "pre-registered decision rule" If "pre-registered" in a journal paper, maybe not necessary but if claim, need include URL. Need "decision rule: causal effect if ratio below 0.8" maybe arbitrary. But okay.

Potential issue: "The central comparison is paired: from a converged raw-target baseline (20 epochs), one arm continues on same raw target for four additional epochs (control), while other fine-tunes on band-limited target for same four epochs." Wait raw baseline trained 20 epochs; matched fine-tune 4 epochs; total 24. From-scratch matched baseline trained
