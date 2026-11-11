# Pre-specified primary model: ICBHI + SPRSound round

Written 11 Nov 2026, 23:45, **before any test patient was read for this round.**

## Rule (the same as the morning ICBHI round)
The primary model is the version with the best mean cycle-level balanced accuracy on the 30 ICBHI validation patients, over 3 seeds. Its test seed is the seed with the best ICBHI validation score.

## Validation results, ICBHI + rebalanced SPRSound

Training data: ICBHI + rebalanced SPRSound (all SPRSound crackles and wheezes; SPRSound healthy capped at ICBHI's count). Features: 0.1–3.9 kHz, levelled, normalised per source. Every (source, class) cell weighted equally.

| Version | ICBHI val (mean ± SD) | Seeds 11 / 22 / 33 | SPRSound val |
|---|---|---|---|
| **fdc3 (FDC-FS three-branch)** | **48.7% ± 1.0** | 48.9 / 47.4 / **49.9** | 49.5–51.3% |
| late3 (late fusion) | 48.1% ± 1.8 | 46.0 / 50.5 / 47.7 | 51.6–52.9% |
| single_spec | 47.1% ± 0.9 | 46.1 / 46.8 / 48.3 | 47.1–48.8% |
| single_mfcc | 43.2% ± 1.1 | 42.0 / 44.7 / 42.8 | 48.2–49.6% |
| single_chroma | 41.2% ± 2.6 | 38.1 / 40.8 / 44.6 | 38.9–47.0% |
| fdc2_nochroma | (running; ablation only, not a candidate) | | |

## Decision
- **Primary: `fdc3`, seed 33** (ICBHI validation 49.9%). Saved model: `models/fusion-icbhi-sprs-2026-11-11/fdc3_seed33.pt`.
- **Test sets:** the 31 ICBHI test patients (main), and the held-out SPRSound test children (230 IDs, secondary).
- **Other versions:** they may also be scored for comparison, but none can replace the primary on the strength of its test score.

## History of the ICBHI test set (report all of these)
1. 11 Nov 02:50: MFCC baseline.
2. 11 Nov 14:52: the ICBHI-only fusion study, primary late3, 32.9% (other session).
3. This round, the third read. Every row is in `results/final-test-log.csv`.
