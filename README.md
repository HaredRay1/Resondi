# Resondi — project folder (updated 15 November 2026)

**Start here:** `START-HERE-PROMPTS.md` has the prompt for a new Claude Code session and for Claude chat.
`CLAUDE-CHAT-BRIEF.md` is the whole project's current state on one page. `CLAUDE.md` is in the root and loads
automatically in Claude Code.

**Current work (since 13 Nov):** Ahnycca's research plan and IMRaD paper for the Regional Science and Technology
Fair, both in `Ahnyccas papers/` with the compiled submission and a plain-language to-do list. The PSC XI business
competition is over.

---

## What is in here

| Folder or file | Contents |
|---|---|
| `CLAUDE-CHAT-BRIEF.md` | **The current state on one page** (papers, model numbers, app, what is missing, rules). Newest status file. |
| `START-HERE-PROMPTS.md` | Prompts to start a Claude Code or Claude chat session. |
| `CLAUDE.md` | The 6 Nov handoff with a newer top note: standing instructions, verified facts, history. |
| `HANDOFF-2026-11-10-model.md` | The 9–14 Nov work on the lung and heart models and the app, with "CURRENT STATE" at the top. |
| `Ahnyccas papers/` | **The final papers:** IMRaD and research plan (Word + PDF), the compiled RSTF submission (kept out of git; it holds ISEF contact details), the title page and contents, the AI usage disclosure and the to-do list. See its `README.md`. |
| `imrad/`, `research-plan/` | Working copies of the two papers under their dated names, the fill-ins, and the plan's revision log. |
| `model-rebuild/` | **The rebuilt models:** lung (four sound classes, patient-wise split, feature fusion, cross-validation) and heart (CirCor: heart rate, murmur). Code, results (`results/`), models. Start with its `README.md`. |
| `app-changes/` | Every change made to the Base44 app, with checkpoints for rollback (fusion model, heart models, device transfer page). |
| `heart-validation/` | The blinded CirCor heart-sound set (25 recordings, answer sheet, instructions) for the reviewing cardiologist. The answer key is kept outside this folder on purpose. |
| `build/` | Every document and figure builder. Documents are generated: edit the builder and rebuild, never the `.docx`. `build/style/house_style.py` sets the papers' format; `build/compile/` makes the compiled submission. |
| `final/` | The PSC submission set (documents 01–20, each with a PDF) and its `README.md`. |
| `chapters/` | Revised Chapters 1–3 of the original research paper, the revision log, and the untouched originals. |
| `deliverables/` | Where some builders write; copy into `final/` after a rebuild. |
| `figures/` | Figures the documents read, including the 3D device render, the product image and the product video. |
| `pricing/`, `assess/`, `deck_fix/`, `src/` | PSC-era material: subscription tiers, the concept-note assessment, the deck builder and its source deck. |
| `source-material/` | The original research paper, spec sheet, STL files, the Blender model (`3d/`), compliance review, rule citations. |
| `data/` | The ICBHI index and the original paper's extracted text. |
| `HF_Lung_V1/` | **Empty.** The clone is broken and the GitHub source now returns 404; the corpus is not on this PC. |
| `tools/` | The Drive mirror task and `make_manifest.py`, which writes `MANIFEST.txt` (every file in the folder). |
| `history/` | Earlier handoffs and replaced files, for provenance only. |

**Kept outside this folder on purpose:**

- The ICBHI 2017 audio (`Downloads\archive.zip`, about 4 GB).
- The CirCor heart dataset (`Downloads\circor\`) and SPRSound (`Downloads\sprsound\`).
- The acceptance survey CSV, which contains personal data.
- `Downloads\Resondi-private\`: the heart-validation answer key, the compile sources, field photos and the app
  security review.

Everything inside this folder is meant to be safe to share through the link-shared Drive folder. Drive for desktop
syncing has been **paused since 12 Nov**, so the Drive copy is out of date until syncing is resumed.

**Large generated folders** that can be deleted and rebuilt with the scripts: `model-rebuild\export\` (about
590 MB), `model-rebuild\history-run1\` (about 210 MB) and `model-rebuild\work*\`.

## Build environment

On Windows, use the Python at `%LOCALAPPDATA%\Python\bin\python.exe`, which has the libraries:

```powershell
python -m pip install python-docx python-pptx openpyxl matplotlib trimesh numpy scipy soundfile pypdf pillow pymupdf playwright defusedxml lxml
python -m playwright install chromium
cd build\cn2; npm.cmd install
```

PDFs are exported with Microsoft Word, as `ExportAsFixedFormat`. The statistical figures need R with the `jmv`
package (`build/imrad/jamovi_figures.R`). The model needs PyTorch CPU, NumPy, SciPy, soundfile and ONNX; see
`model-rebuild\README.md`.
