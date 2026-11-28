# Welcome page redesign and security check (28 Nov 2026)

## Welcome page (SAVED in the editor, NOT published)
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
