# Ahnycca's papers (regional science and technology fair, heart and lung)

Copies made on 14 Nov 2026. Each Word file has a PDF beside it.

| File | What it is |
|---|---|
| `Resondi-IMRaD-Heart-and-Lung-2026-11-13` | The IMRaD paper: lung and heart, no financial requirement. Includes the rebuilt classifier, the cross-validation, the leakage demonstration (Table 4), the run on Resondi device recordings (Figure 16) and the heart-sound models on CirCor test patients (Table 5, Figure 17). |
| `Resondi-IMRaD-Heart-and-Lung-Open-Items-2026-11-13` | The IMRaD fill-ins: 15 facts only the team can supply, 9 of them blocking. Each is marked `[[TO FILL]]` in the paper. |
| `Resondi-Research-Plan-Revised-Heart-and-Lung-2026-11-13` | The individual proponent research plan (Ahnycca Krish N. Malimban), revised, with the heart component and the heart-sound model results (Table 20, Figure 16). |
| `Resondi-Research-Plan-Revision-Log-Heart-and-Lung-2026-11-13` | Every change made to the research plan, old and new text side by side. |

These are copies. The builders write to `../imrad/` and `../research-plan/`; after a rebuild, copy the new files here again. The lung-only versions are in `../imrad/old-lung-only/` and `../research-plan/old-lung-only/`.

**Never quote the leaky rows of Table 4 as accuracy.** They show how a leaky split inflates the score. The model's accuracy on unseen patients is 40.0 percent balanced (39.0 percent for the single seed in Table 4), against 25 percent by chance.

**Heart results (IMRaD Table 5, research plan Table 20) are on CirCor recordings only,** not on the Resondi device. The murmur detector reached 66.7 percent sensitivity on test patients, short of its 80 percent target; do not quote 80 percent as its result.
