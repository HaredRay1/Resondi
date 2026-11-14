# Ahnycca's papers (regional science and technology fair, heart and lung)

The final revised IMRaD and research plan, each as Word and PDF. Last refreshed 14 Nov 2026, after the heart models went live in the Resondi app (17:30).

| File | What it is |
|---|---|
| `Resondi-IMRaD-Heart-and-Lung-FINAL` | The IMRaD paper: lung and heart, with no financial requirement. Includes the rebuilt classifier, the cross-validation, the leakage demonstration (Table 4), the run on Resondi device recordings (Figure 16), and the heart-sound models on CirCor test patients and in the app (Table 5, Figure 17). The Results end with the outcome for each of the nine objectives. |
| `Resondi-Research-Plan-Heart-and-Lung-FINAL` | The individual proponent research plan (Ahnycca Krish N. Malimban), revised, with the heart component and the heart-sound model results (Table 20, Figure 16). Its Results and Discussion answers each of the 11 research questions under a heading that names it, and Table 21 summarizes every answer and how complete it is. |

These are copies, renamed FINAL. The builders write to `../imrad/Resondi-IMRaD-Heart-and-Lung-2026-11-13` and `../research-plan/Resondi-Research-Plan-Revised-Heart-and-Lung-2026-11-13`; after a rebuild, copy those here again under the FINAL names. Kept out of this folder on 14 Nov, at the user's request:
- the IMRaD fill-ins (15 `[[TO FILL]]` items, 9 blocking): `../imrad/Resondi-IMRaD-Heart-and-Lung-Open-Items-2026-11-13`;
- the research plan revision log: `../research-plan/Resondi-Research-Plan-Revision-Log-Heart-and-Lung-2026-11-13`.

The lung-only versions are in `../imrad/old-lung-only/` and `../research-plan/old-lung-only/`.

**Before submitting, fill the marked gaps.** These are facts only the team can supply, so they are left visible on purpose and must not be guessed:
- The IMRaD has 15 `[[TO FILL: ...]]` notes, 9 of them blocking. The fill-ins document in `../imrad/` lists them with what each needs.
- The research plan's reference list has 1 `[[... CONFIRM ...]]` note: the full reference for Shkarupylo et al. (2024), cited in the Rationale for noise and contact artifacts. (Park et al., 2025 was completed on 14 Nov with the JMIR meta-analysis, chosen by the user.)

**Never quote the leaky rows of Table 4 as accuracy.** They show how a leaky split inflates the score. The model's accuracy on unseen patients is 40.0 percent balanced (39.0 percent for the single seed in Table 4), against 25 percent by chance.

**The heart results (IMRaD Table 5, research plan Table 20) are on CirCor recordings only,** not on the Resondi device. The murmur detector reached 66.7 percent sensitivity on the test patients, short of its 80 percent target, so never quote 80 percent as its result. Both papers say:
- the heart models run in the app (published 14 Nov);
- they went in before the device test the plan had put first;
- every heart result in the app is marked as a screening aid.
