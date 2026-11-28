---
tags: [app]
---
# App (Base44, resondi.base44.app)

**What it does:** Lung and Heart modes with guided chest diagrams; files each recording by site; runs the lung
fusion network and the heart models in the browser; recording history, same-site comparison, trend charts;
practitioner review (confirm, change, repeat); English and Filipino; light and dark mode.

## Change records
- [[unslop-redesign-2026-11-27]]: redesign (Nunito, quiet colours, real waveform)
- [[welcome-and-security-2026-11-28]]: Maya-style welcome page, camera guide prototype, security check
- [[tibok-and-signup-2026-11-28]]: Tibok the mascot, step-by-step sign-up, new sign-in
- [[fusion-model-v2-and-device-transfer]] · [[heart-models-v1]] · [[seven-sites]] · [[model-4-class-labels]]

## Restore points (Base44 checkpoints)
| When | Checkpoint | State |
|---|---|---|
| 27 Nov | `6b0986f012fe3b837ac6627f` | before the unslop redesign |
| 28 Nov | `6b0a928421c712d4439e42b2` | before the Maya-style welcome page |
| 28 Nov | `6b0a999badd28a49c8f03865` | before the camera guide |
| 28 Nov 09:22 UTC | `6b0a9d56ed95d5e40911124a` | welcome + camera guide (published) |
| 28 Nov 10:43 UTC | `6b0ab05ce9546a130c909430` | Tibok + sign-up (published) |
| 28 Nov 10:56 UTC | `6b0ab34d0feca7058636b40e` | dark mode (published) |
| 28 Nov | `6b0ab5a2b5fb58e2a2b9fe56` | security limits + lockout message (before the test fixes) |
| 28 Nov 14:44 UTC | `6b0ae8bf2f74aad6b72e82be` | end-to-end test fixes + lockout message (published, current) |

## Open
- [x] Security limits live 28 Nov: 5 admin password tries per 15 min; 40 AI calls per user per hour
- [x] Lockout message published 28 Nov 14:44 UTC
- [ ] Decide: delete the test data from the end-to-end test? ([[end-to-end-test-2026-11-28]])
- [ ] Try the camera guide on a phone; it was never checked against physician-marked sites
- [ ] A Filipino speaker reads the new Filipino text
- [ ] IMRaD app figures 13-15 show the old look

Editing without credits: write files through Base44's API; only builder chat turns cost credits.
