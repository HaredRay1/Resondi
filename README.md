# Resondi — project folder (updated 9 November 2026)

Open this folder with Claude Code. **`CLAUDE.md` is in the root and loads automatically.** First prompt for a new session:

> Read CLAUDE.md, then continue from the Open Work list.

---

## What is in here

| Folder | Contents |
|---|---|
| `CLAUDE.md` | **The handoff. Read this first.** Verified facts, standing instructions, open work. |
| `final/` | **The submission set:** numbered documents 01–17, each with a PDF, plus `README.md`. |
| `chapters/` | Revised Chapters 1–3 of the research paper, the revision log, and the untouched originals. |
| `model-rebuild/` | **The retrained lung sound model** (Crackles, Healthy, Wheezing, Wheezing with Crackles): code, results, the checked Edge Impulse build for the app (`deploy/`), and the local-dataset guide. Start with its `README.md`. |
| `heart-validation/` | The blinded CirCor heart-sound set (25 recordings, answer sheet, instructions) for the reviewing cardiologist. The answer key is kept outside this folder on purpose. |
| `app-changes/` | App review and the Base44 changes: seven sites, rename, and the switch to the 4-class model. |
| `build/` | Every document and figure builder. Documents are generated: edit the builder and rebuild, never the `.docx`. |
| `deliverables/` | Where builders write; copy into `final/` after a rebuild. |
| `figures/` | Every figure the concept note and IMRaD read, including the 3D device render and the VER 2.0 block diagram. |
| `pricing/` | Subscription tiers and trial spec for the app. |
| `assess/` | The concept-note assessment against the PSC XI criteria. |
| `deck_fix/`, `src/` | The deck builder and the source deck it corrects. |
| `source-material/` | The research paper, spec sheet, STL files, the Blender model (`3d/`), compliance review, rule citations. |
| `data/`, `HF_Lung_V1/` | The ICBHI index, the paper's extracted text, and the HF_Lung_V1 Taiwanese lung-sound corpus. |
| `history/` | Earlier handoffs and replaced files, for provenance only. |

**Kept outside this folder on purpose:** the ICBHI 2017 audio (`Downloads\archive.zip`, about 4 GB), the CirCor heart dataset (`Downloads\circor\`), the acceptance survey CSV (contains personal data) and the heart-validation answer key (`Downloads\Resondi-private\`). Everything inside this folder can be synced to Google Drive.

**Large generated folders** that can be deleted and rebuilt with the scripts: `model-rebuild\export\` (about 590 MB), `model-rebuild\history-run1\` (about 210 MB) and `model-rebuild\work\` (about 70 MB).

## Build environment

Documents: see the 2 Nov handoff in `history/` (section B3). On Windows:

```powershell
python -m pip install python-docx python-pptx openpyxl matplotlib trimesh numpy scipy soundfile pypdf pillow pymupdf playwright defusedxml lxml
python -m playwright install chromium
cd build\cn2; npm.cmd install
```

The model: see `model-rebuild\README.md` (PyTorch CPU, NumPy, SciPy, soundfile, ONNX).
