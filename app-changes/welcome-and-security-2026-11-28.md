# Welcome page redesign, camera guide and security check (28 Nov 2026)

## Welcome page (PUBLISHED 28 Nov 2026 09:22 UTC)
User asked for a new home screen for new users "like Maya's mobile app" with animations, instead of the
chest diagram. Reference: the Maya app's Google Play screenshots (not its website). Borrowed the structure,
not the brand: segmented dark tab bar (Lung | Heart) with a sliding pill, one dark "card" as the hero (an
animated example recording: breathing bars for lung, lub-dub bars for heart, a playhead, a light sweep,
gentle float; marked "Example"), a "Practitioner confirmed" toast that slides in and out, a grid of soft tiles
of different sizes that rise in on scroll, three numbered steps, and a dark floating action bar on phones.
Colours stay rose; Nunito. All motion stops for people who turn on reduced motion. Copy is in the file in
English and Filipino (the Filipino should be read by a Filipino speaker).

- Files: `src/pages/Welcome.jsx` (rewritten), `src/unslop.css` (app-wide: cards and results rise into place
  when a page opens, staggered; `animation-fill-mode: backwards`, so no transforms are left behind).
- Restore point: checkpoint `6b0a928421c712d4439e42b2` ("Before Maya-style welcome page and motion").
- Both files verified identical in the preview and compiling. Not viewed in a browser: Base44 blocks automated
  browsers from the preview, and the preview opens on the user agreement, which Claude does not accept for the
  user. Copies in `Downloads\Resondi-private\app-unslop\new\`.

## Security check against a 7-point checklist (a Facebook reel the user sent)
1. Secrets in the browser code: none found (no keys, tokens or VITE_ variables in `src/`). The admin password
   and Stripe keys are server secrets.
2-4. Ownership, database rules, mass assignment. Every entity has row rules; patient profiles are read only by
   the patient and admins, and practitioners get them through `getCasePatientProfiles`, which checks
   verification and assignment on the server. Weak spots (not changed; need testing with real accounts):
   - A patient can edit their own `AIAnalysis` / `HeartAnalysis` after creation (classification, severity,
     heart rate), so a practitioner could see an altered "AI" result.
   - A patient can set their own `SessionSubmission.submission_status` / `AuscultationSession.submission_status`
     to "approved".
   - `Notification` has no create rule, so any signed-in user may be able to create a notification for any
     user (check what the platform default is).
   - A patient can delete `PractitionerReview` rows on their own recordings (loses the review trail).
   - `FollowUpAppointment` can be created naming any patient and practitioner.
5. Checkout: prices come from the server by plan; the Stripe webhook verifies its signature. OK.
6. Rate limits: missing in two places.
   - `verifyAdminAccess`: unlimited password attempts; a correct guess makes the account an admin (all patient
     data). Proposed: refuse after 5 failed attempts in 15 minutes per account (counted from AuditLog).
   - `assessSeverity`: any signed-in user can call the paid AI model without limit. Proposed: a per-user hourly cap.
7. Proof (user B cannot read user A's record): not done; needs two test accounts.
`src/lib/authBypass.js` exists but `AUTH_BYPASS = false`; leave it false.

## Later the same day (PUBLISHED with the welcome page)
- Welcome page: the floating Sign In / Register bar was removed (user did not like it); tiles are one per row on
  phones and the two small tiles pair up on wider screens (a small tile had sat alone in half a row).
- **Camera-guided placement prototype** (user request): new page `src/pages/CameraGuide.jsx`, route
  `/guide/camera/:mode` (lung or heart; any signed-in role, so practitioners can open it too), linked from the
  patient guide pages ("Use the camera guide (prototype)"). MediaPipe Pose Landmarker 0.10.14 (Apache-2.0,
  loaded from jsDelivr; model from Google's storage, about 15 MB on first use) finds the shoulders and hips on
  the phone; each site is placed in body units (half shoulder widths sideways, fraction of shoulder-to-hip
  length downwards) ESTIMATED from general adult anatomy, because the app's chest diagrams are drawn wider and
  longer than a real chest (using them would have put the mitral marker about 7 cm too low). Sites follow the
  app's own sequence; prompts to turn the patient for the back; a side-site warning; a slider to move markers
  up or down; front/back camera switch. No frame is saved or sent. Not tested in a browser by Claude, never
  checked against physician-marked sites, not tested on children. Restore point before it:
  checkpoint `6b0a999badd28a49c8f03865`.
- Validation the team would need before any claim: physician marks sites with stickers on volunteers of
  different ages and builds; measure the marker-to-sticker distance in mm per site; report mean and worst.

## Published 28 Nov 2026, 09:22 UTC (user: "publish it")
Checkpoint `6b0a9d56ed95d5e40911124a`, commit `341180d7`, https://resondi.base44.app. Live welcome page checked
in a browser on desktop and phone: no script errors, five tiles, no floating bar, the hero card switching Lung /
Heart. The camera guide needs a signed-in account, so it was not opened by Claude; a team member should try it.
The two security limits (admin password attempts, AI calls) were NOT applied; they wait for the user's yes.
