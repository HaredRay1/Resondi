# Start-here prompts for a new Claude session

Copy the prompt for the tool you're using, replace the last line with your request, and send it.

---

## Claude Code (desktop app or terminal, opened in `C:\Users\Hared\Downloads\Resondi`)

```
Before doing anything, read these in full, in this order:
1. CLAUDE.md (project root). Read the top note first: it is newer than the sections below it.
2. HANDOFF-2026-11-10-model.md. Start with "CURRENT STATE", then sections 7–9. Later sections override earlier ones.
3. Your memory index (MEMORY.md) and any memory it points to that relates to my request.
4. Run `git status` and `git log --oneline -10` so you know what is committed and whether another session is working here.
5. Any file in the folder that my request touches. Open it; don't work from memory.

Rules while you work:
- Facts come from those files. If two files disagree, the newer one wins; tell me about the conflict.
- Never quote 71.1% / 83% as model accuracy. Never say the model is validated, diagnoses, or works on the Resondi device.
- My Google Docs and the 83-page paper: don't edit them, give me the revised text to paste.
- The Drive folder is link-shared: no names, e-mails, patient data, passwords, keys or answer keys in Downloads\Resondi. Use Downloads\Resondi-private.
- Never type credentials into any login form. Ask before downloading files.
- I'm on Windows: PowerShell, not bash.
- When you finish, update CLAUDE.md or the handoff with anything a future session needs, then commit and push (GitHub HaredRay1/Resondi, branch master).

When you have read everything, reply with three lines: what the project is, where the lung model stands, and what you'll do for my request. Then do it.

My request: [WRITE WHAT YOU WANT HERE]
```

---

## Claude chat (claude.ai)

Attach `CLAUDE.md` and `HANDOFF-2026-11-10-model.md` from the Resondi folder, plus any file your request is about, then send:

```
I've attached my project's two handoff files. Before answering, read both in full:
1. CLAUDE.md. Its top note is newer than the sections below it.
2. HANDOFF-2026-11-10-model.md. Start with "CURRENT STATE", then sections 7–9. Later sections override earlier ones.
Also read any other file I attached.

Rules:
- Use only the numbers in these files. If two disagree, the newer one wins; point out the conflict.
- Never quote 71.1% / 83% as model accuracy. Never say the model is validated, diagnoses, or works on the Resondi device.
- The live app's model scores 33.5% balanced; the best model (not in the app yet) scores 40.0% balanced in 5-fold cross-validation (chance is 25%).
- If you don't know something from these files, say so; don't guess.
- For my Google Docs and paper, give me revised text to paste, not a summary of changes.

When you have read everything, reply in three lines: what the project is, where the lung model stands, and your plan for my request. Then do it.

My request: [WRITE WHAT YOU WANT HERE]
```
