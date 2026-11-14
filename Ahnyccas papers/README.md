# Ahnycca's papers (regional science and technology fair, heart and lung)

This folder holds the final revised IMRaD and research plan (each as Word and PDF), the list of what is still missing, and the compiled submission. Last refreshed 14 Nov 2026, after filling gaps from the team's Drive folders.

| File | What it is |
|---|---|
| `Resondi-Compiled-RSTF-FINAL.pdf` | **The compiled submission, 148 pages, with bookmarks.** Same layout as the example compilation `MCS-I-RSTF7b`, in the order: I. Research Plan, II. ISEF Forms (the team's signed set), III. ISEF Abstract, IV. Research Paper (the IMRaD), V. Project Data Book (logbook placeholder), VI. SRC Evaluation (the signed review form of 5 Nov 2026). Rebuilt by `../build/compile/compile_rstf.py`. |
| `Resondi-IMRaD-Heart-and-Lung-FINAL` | The IMRaD paper: lung and heart, with no financial requirement. Includes the rebuilt classifier, the cross-validation, the leakage demonstration (Table 4), the run on Resondi device recordings (Figure 16), and the heart-sound models on CirCor test patients and in the app (Table 5, Figure 17). The Results end with the outcome for each of the nine objectives. The cover page credits the research adviser and consultants, and the abstract is 250 words, as the fair's review form requires. |
| `Resondi-Research-Plan-Heart-and-Lung-FINAL` | The individual proponent research plan (Ahnycca Krish N. Malimban), revised, with the heart component and the heart-sound model results (Table 20, Figure 16). Its Results and Discussion answers each of the 11 research questions under a heading that names it, and Table 21 summarizes every answer and how complete it is. |
| `Resondi-Missing-Items-Research-Plan-and-IMRaD` | What is still missing from each paper, from the fair forms and from the compiled document. Each item lists what closes it, who can supply it, and its priority (blocks submission / before the fair / future work). It ends with what the Drive folders resolved. Rebuilt by `../build/missing/build_missing.py`, which reads the visible markers from the papers. |

**Privacy.** The compiled PDF contains the ISEF forms, which list phone numbers and e-mail addresses. It is kept out of git (`.gitignore`). Its downloaded sources are in `Downloads\Resondi-private\compile-sources\`. This folder is meant to mirror to the link-shared Drive folder, so think before sharing that link.

**Copies, not sources.** The papers here are copies, renamed FINAL. The builders write to `../imrad/Resondi-IMRaD-Heart-and-Lung-2026-11-13` and `../research-plan/Resondi-Research-Plan-Revised-Heart-and-Lung-2026-11-13`. After any change:
1. rebuild the paper;
2. recopy it here under its FINAL name, replacing the old copy;
3. rerun `build_missing.py`;
4. rerun `compile_rstf.py`.

Kept out of this folder on 14 Nov, at the user's request:
- the IMRaD fill-ins (now 12 `[[TO FILL]]` items, 7 blocking): `../imrad/Resondi-IMRaD-Heart-and-Lung-Open-Items-2026-11-13`;
- the research plan revision log: `../research-plan/Resondi-Research-Plan-Revision-Log-Heart-and-Lung-2026-11-13`.

The lung-only versions are in `../imrad/old-lung-only/` and `../research-plan/old-lung-only/`.

**Before submitting, fill the marked gaps** (all listed in the missing-items file). They are facts only the team can supply, so they are left visible on purpose and must not be guessed:
- the IMRaD has 12 `[[TO FILL: ...]]` notes, 7 of them facts its main claims rest on;
- the research plan has 1 CONFIRM note, the full reference for Shkarupylo et al. (2024);
- the compiled document needs the logbook scans and Ahnycca's own answers to questions 2, 5 and 6 on the ISEF abstract page.

**Never quote the leaky rows of Table 4 as accuracy.** They show how a leaky split inflates the score. The model's accuracy on unseen patients is 40.0 percent balanced (39.0 percent for the single seed in Table 4), against 25 percent by chance.

**The heart results (IMRaD Table 5, research plan Table 20) are on CirCor recordings only,** not on the Resondi device. The murmur detector reached 66.7 percent sensitivity on the test patients, short of its 80 percent target, so never quote 80 percent as its result. Both papers say:
- the heart models run in the app (published 14 Nov);
- they went in before the device test the plan had put first;
- every heart result in the app is marked as a screening aid.
