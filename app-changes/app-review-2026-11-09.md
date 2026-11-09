# Resondi app review: 9 November 2026

The Base44 app ID is `6a927c5e8ee8ac619e690f90`, and it is published at https://resondi.base44.app.

This was a read-only review. Nothing was changed except the seven-site and rename edit, which was applied earlier on 9 Nov and is **not yet published**.

The sources were the Base44 security scan (run 9 Nov, 09:08), a full read of the source code, and the entity schemas with their access rules.

**About the confidence tags.**
- **Confirmed** means the code was read and the fault is certain.
- **Likely** means the code strongly suggests it, but it should be tested once.
- **Live data** means it was seen in the app's real records.

**About the plan.** Direct file editing (`edit_file` / `grep`) is blocked on the free Base44 plan. Fixes go through Base44 builder turns, which use credits. The other route is the platform's `coding/write` API, which is untested on this plan.

---

## PUBLISHED: 9 Nov 2026, 11:59 UTC

Published checkpoint `6af19ba21d326a26aab62dcf` (commit `8e209dea`) to https://resondi.base44.app. This publish also shipped the seven-site and rename edit.

**What was verified after publishing.**
- All 90 published script files were searched. They contain the model timeout, the pinned model version, the memory-card wording, "Possible crackles" and "Model score (not accuracy)". "via Bluetooth" no longer appears anywhere.
- An explicit function redeploy succeeded, so this plan **does** deploy backend functions. B1, B3 and B5 are therefore live.
- After that, `PractitionerReview` create and update were set to admin-only (**B2 applied**). Reviews can now be created only by `submitPractitionerReview`, which writes them with the server role.
- **Still to test:** one real practitioner review on the live app. If it fails, revert PractitionerReview create to `{"created_by_id": "{{user.id}}"}`.

## STATUS: what was fixed on 9 Nov (free plan)

Restore point: **"9 Nov fixes: heart mode, model loading, exam bugs, review security, wording"** (checkpoint `6af19abdf39469d212c08ab3`). The changes are in the editor preview and are **not published**.

**What is live and what isn't.**
- **Access rules** (entity RLS) apply to the live app **immediately**. Only one rule was changed, SessionSubmission, and it is compatible with the live app's current code.
- **Backend functions** go live only when the app is **published**. Base44's docs say "the published app keeps running the previous version of the function until you publish the app again". So B1, B3 and B5 below are fixed in the source and in the preview, and they reach the live site at the next publish.
- **Unconfirmed:** whether the free plan deploys functions at all. The docs say backend functions need the Builder plan. Check after publishing.

**Do right after publishing (B2, faking an approval).**
- The review function now writes reviews with the server role.
- Once that version is live, change the `PractitionerReview` rules so `create` and `update` are `{"user_condition": {"role": "admin"}}`.
- This was applied once and **reverted the same day**: the live app was still running the old function, and the new rule would have blocked every practitioner review.

**How the work was done.**
- Most fixes used the platform `coding/write` API, which uses **no builder credits** on the free plan.
- Each edited file was checked by fetching it from the preview server, which compiles it on request.
- The wording went through **one builder turn (2.1 credits)**, and that turn's full `vite build` passed.

| Item | Status |
|---|---|
| A1, A2: lung model run on heart recordings | **Fixed.** Heart sessions show "Automated heart-sound classification is not available…" and never call the classifier. |
| A3: heart recordings can't be sent | **Fixed.** The send panel shows for heart recordings without an analysis. |
| A4: model loading hangs or caches failure | **Fixed.** 45 s timeout, a failed load is not cached, the audio download has a 30 s timeout, and the error stays visible. |
| A5: model loaded from `@main` | **Fixed.** Pinned to commit `4e49a196…` (`MODEL_VERSION` in `lungClassifier.js`); all three files were checked to exist at that commit. |
| A6: classifier input window and scaling | **Not changed.** Needs a test against Edge Impulse Studio first. |
| A7: 12-site exam routed as lung | **Fixed.** The exam summary has one send box per mode, each listing only practitioners of that specialty. |
| A8: plans and analyses invisible to the practitioner | **Fixed.** New analyses and plans copy the session's `practitioner_ids`. |
| A9: silent heart-save failure | **Fixed.** The error is shown, the file is kept for retry, and an exercise-plan failure no longer blocks the exam. |
| B1: anyone can read any patient's profile | **Fixed.** The submission rule is live now: create requires `patient_id` = the creator. The `getCasePatientProfiles` hardening, which requires a verified practitioner and checks each patient against the actual recording and its assignment, goes live at publish. |
| B3: review of cases not sent to you | **Fixed in source; live at publish.** `submitPractitionerReview` requires a submission naming the caller, the session assigned to them, and not their own recording. The Base44 rescan no longer reports it. |
| B5: reminder job runs anonymously | **Fixed in source; live at publish.** Signed-in admin only. It had no run history, so no schedule depended on it. The rescan no longer reports it. |
| B9: `app_role=admin` shows the admin screens | **Fixed.** `RoleGuard` ignores `app_role` "admin". |
| C1: mirrored back markers | **Fixed** (`examSites.js`). |
| C2: Exit / Finish early do nothing | **Fixed.** Both go to `/patient`. |
| C4: "Improving" from one exam | **Fixed.** Trend and score compare exams (or days), not the sites within one exam; the trend is lung-only. |
| C5: duration always 0 s | **Fixed.** Duration is read from the WAV file, and "0s" is hidden. The two-15-s-file issue remains. |
| C6: duplicate saves / stuck cursor | **Fixed.** A recorded site can't be saved again, and the next-site search wraps round. |
| C8: newest-200 lookups | **Fixed** in SessionDetail, ExamSummary and RecordingHistory, which now look up per session. Practitioner pages and the dashboard still use newest-200. |
| C9: history sent as raw keys | **Fixed.** History is translated before it goes to `assessSeverity`. |
| C10: delete leaves orphans | **Fixed.** The history delete removes the analysis, plan, reviews and submissions. Patients can now delete their own submissions, which the scan recommended. |
| One approval overrides a disapproval | **Fixed.** A disapproval now wins. |
| D1–D3, D5–D10, D12, D13 (wording) | **Fixed** by the builder turn. Summaries now read as possibilities. |
| Everything else | **Still open.** Listed below, mostly needing the Builder plan or a decision from you (section F). |

**Found while fixing.**
- 6 of the 7 verified practitioners have **no specialisation set**, so they are allowed to review both modes. An admin should set each one, under Admin → Practitioners, before the empty-list loophole (B6) is closed. Closing it now would lock them all out.
- Patients could never delete a recording that had been sent: the submission delete was refused and the error was swallowed. This is fixed by the SessionSubmission rule above.

---

## A. Heart Mode: the "loading classification" problem

| # | Problem | Where | Confidence |
|---|---|---|---|
| A1 | **The lung classifier runs on heart recordings.** A heart session's detail page offers "Run AI analysis", which loads the lung model and labels the heart sound normal, crackles or wheezing, with a confidence and a severity. | `src/pages/patient/SessionDetail.jsx` (handleAnalyze, AI card) | Confirmed |
| A2 | **The same thing happens in the 12-site exam.** "Analyze all" on the exam summary classifies the 5 cardiac sites with the lung model. | `src/pages/patient/ExamSummary.jsx` runAll / runClassification | Confirmed |
| A3 | **A heart recording cannot be sent for review from its own page unless the lung model has been run on it.** The send panel only appears once an analysis exists (`analysisReady={!!analysis}`). | `SessionDetail.jsx`, `SubmissionPanel.jsx` | Confirmed |
| A4 | **Classifier loading has no timeout, and a failure is cached.** If the model download stalls, the spinner stays on "Loading" indefinitely. If it fails once, every retry fails until the page is reloaded, because the rejected promise is kept. When the loader closes, the error message disappears with it. | `src/lib/lungClassifier.js` loadClassifier; `InferenceLoader.jsx` | Confirmed |
| A5 | **The model is loaded from a moving target.** It comes from GitHub `HaredRay1/Ausculta@main` through jsDelivr, so any push silently changes the deployed model, and the CDN can serve a stale copy for up to a week. No model version is saved with a result. | `lungClassifier.js` MODEL_BASE | Confirmed |
| A6 | **The classifier's input window and scaling are probably wrong.** The window size is read from a field Edge Impulse does not provide, so the code falls back to 1 s. Audio is also fed as −1..1 floats, where Edge Impulse usually expects int16-scale values. Either could make the scores meaningless. | `lungClassifier.js` getInputWindow | Likely; test against Edge Impulse Studio's Live Classification |
| A7 | **Advanced (12-site) exams are routed as lung exams.** The cardiac sites go to a respiratory reviewer. | `ExamSummary.jsx` ~L93 `mode: "lung"` | Confirmed |
| A8 | **Cardiac exercise plans can be invisible to the practitioner.** The plan is created on the patient's first view, after sending, so it lacks `practitioner_ids` and stays "pending review" forever. | `SessionDetail.jsx` load(); `caseAssignment.js` | Confirmed |
| A9 | **A heart save that fails gives no message.** The site stays put, the user records again, and duplicate sessions result. | `src/pages/patient/HeartExam.jsx` handleSave (`catch (e) {}`) | Confirmed |
| A10 | **Every heart recording gets a cardiac rehab plan automatically,** including light jogging, with no classification behind it. It does wait for practitioner approval. | `HeartExam.jsx`, `exerciseSessions.js` attachCardiacPlan | Confirmed; **needs your decision** |

**Fix direction.** Heart sessions never run the lung model. They show "Recorded for practitioner review: automated heart analysis is not available yet", and they can always be sent. Model loading gets a timeout, a clear error and a working retry. The model is pinned to a fixed version.

---

## B. Security: fix before any real patient data

| # | Problem | Severity |
|---|---|---|
| B1 | **Any signed-in user can read any patient's full profile:** medical and family history, birth date, blood type and phone. They create a `SessionSubmission` naming themselves as practitioner and the victim as patient, then call `getCasePatientProfiles`. The same trick lets a removed practitioner restore their own access. | Critical, confirmed |
| B2 | **Practitioner approvals can be forged.** Any user can write a `PractitionerReview` marked "approved" under any doctor's name. A patient can mark their own exercises approved and edit their AI result. A patient can also delete reviews about themselves. | High, confirmed |
| B3 | **A practitioner can review sessions never sent to them.** `submitPractitionerReview` does not check the assignment. This was flagged by the Base44 scan. | High, confirmed |
| B4 | **One shared password makes any user a permanent admin,** with full access to all health data. The option is offered on the role-selection screen, with no rate limit. **Live data:** the app has 5 admins, and the audit log shows 3 failed attempts (31 Aug) and 1 success (1 Sep). | High, confirmed |
| B5 | **The weekly reminder job can be triggered by anyone, even signed out.** This was flagged by the Base44 scan. | High (scan) / limited impact |
| B6 | **A verified practitioner can change their own licence number, name and specialisation without re-review.** Adding "cardiac" unlocks heart cases. An empty specialisation list counts as "authorised for everything". | Medium, confirmed |
| B7 | **Any user can send any other user a notification with any text,** for example a fake "your result is severe, call …" alert. | Medium |
| B8 | **One recording is still at a public URL** (session `6a928d38…`, 29 Aug). The migration function also has bugs that leave public links in place. | Medium, live data |
| B9 | **A user can set their own `app_role` to admin, which shows the admin screens.** Their data calls still fail, so nothing leaks. **Live data:** one such account exists. | Low |
| B10 | **`assessSeverity` is open to any user.** It sends free text to an AI model, which allows cost abuse and prompt injection, and the AI model then sets the patient-facing severity (see D4). | Low (security) |
| B11 | **A crafted link can sign a victim into someone else's account,** through the `?access_token=` handling in the standard Base44 template. | Low, unverified |

These were checked and are fine: Stripe prices are set on the server, the webhook signature is checked, there are no hard-coded secrets, no tokens or health data are logged, licence numbers are protected, and the developer login bypass is switched off. `authBypass.js` can still be deleted.

---

## C. Other bugs

| # | Problem | Confidence |
|---|---|---|
| C1 | **The back-view markers on the torso diagram are left–right mirrored,** so a recording placed by the marker is filed under the wrong side (`src/lib/examSites.js` L57–60). | Confirmed |
| C2 | **"Exit" and "Finish early" (with nothing recorded) do nothing.** They navigate to the page they are already on (`FullExam.jsx` L100, L108). | Confirmed |
| C3 | **Quick recording and the guided exam use different site names,** so same-site comparison never matches across them. This undermines the longitudinal-comparison claim. | Confirmed |
| C4 | **"Improving / Needs attention" is shown from a single exam.** It compares the first sites recorded against the last ones, not one exam against a later one (`healthScore.js`, `trend.js`). | Confirmed |
| C5 | **Recording duration is always saved as 0 s.** The 20 s lung site, which is two 15 s files, has nowhere to put the second file. | Confirmed |
| C6 | **Re-recording a site creates duplicates,** and jumping ahead past sites can leave the exam stuck (`FullExam.jsx`). | Confirmed |
| C7 | **The headline result and the breakdown bars can disagree.** One uses the top raw label, the other sums by category. | Confirmed |
| C8 | **Pages load only the newest 200 analyses, reviews and plans app-wide.** After about 16 full exams, older sessions show "no analysis" and invite duplicate runs. | Confirmed |
| C9 | **Patient history reaches the AI model as raw keys** like `mh.q1: onboarding.yes`, not as readable text. | Confirmed |
| C10 | **Deleting from Recording History leaves the recording's analysis, plan and submission behind.** The practitioner queue then points at nothing. | Confirmed |
| C11 | **Exam-summary analyses get no exercise plan.** | Confirmed |
| C12 | **Subscriptions are broken in four ways.** The tier unlocks nothing. Checkout creates duplicate subscription rows. The renewal date is always blank (a Stripe API field change). Any tier can be switched to. | Confirmed |
| C13 | **Several smaller faults.** The follow-up scheduler may crash and has no error handling. The "incomplete sessions" banner never clears. The PDF includes disapproved exercises. One approval overrides another reviewer's disapproval. Age goes stale. | Mixed |

---

## D. Wording that contradicts the project facts

All of these are in `src/lib/i18n.jsx`, English and Filipino, unless noted.

| # | Current | Problem | Suggested |
|---|---|---|---|
| D1 | "Connect a physical Resondi stethoscope via **Bluetooth** when available" (shown on 4 screens) | The device has no Bluetooth, and the link to the platform is not built | "The device records to its memory card. Import the .wav from the card; automatic transfer is not built yet." |
| D2 | Heart Mode: "S1, S2, **S3, S4** and murmurs" | Heart Mode classifies nothing, and S3/S4 are not promised | "Heart sounds are recorded at five sites for practitioner review. Automated heart analysis is not available yet." |
| D3 | "Crackles **detected**", "Wheezing **detected**"; summaries say "were detected" | Reads as a finding, not a possibility | "Possible crackles: awaiting practitioner review" |
| D4 | Normal / Mild / Moderate / **Severe**, assigned by an AI model | A clinical grade, in no project document | Remove it, or relabel "Screening priority (AI-suggested, not confirmed)" |
| D5 | "Confidence Score {n}%" | Reads like accuracy | "Model score (not accuracy; model not yet validated)", or show it to practitioners only |
| D6 | "The AI model **will be integrated later**" (directly above a working Run button) | The model is integrated | "Not analysed yet. Run classification, or send for practitioner review." |
| D7 | Practitioner type: "cardiac **classifications**" | There is no heart classifier | "Heart recordings (no automated classification yet)" |
| D8 | Exam takes "about 4 / about 8 minutes" | The documented figures are about 34 and 45+ minutes | Drop the time, or state the documented figure |
| D9 | Filipino "buto ng **balakang**" for shoulder blade | It means hip bone | "paypay (talim ng balikat)" |
| D10 | Three other Filipino mistranslations ("Nagsasagip", "Sinasala", and one more) | Mistranslated | See the full notes |
| D11 | Privacy policy | Says lung only; says "stored securely" with no detail; names no Base44 or Stripe; says nothing on AI processing, the Data Privacy Act (RA 10173), guardian consent for minors, or a contact | The text needs your facts (see F5) |
| D12 | Share preview: "AI-assisted respiratory **and heart** sound monitoring" (`index.html`) | Implies heart AI | "AI-assisted lung-sound screening and guided heart-sound recording" |
| D13 | Heart guide names diseases ("aortic stenosis", "VSD"); Erb's point says "not passed to the classifier" | Implies a heart classifier exists | Acoustic wording only |
| D14 | "AI Placement Guidance" from a photo | This feature is not in any document | Confirm whether the screen is reachable |

These were checked and are correct: the site counts (7 / 5 / 12), the not-a-diagnosis disclaimers, no model accuracy figures shown anywhere, and no user-visible "Ausculta".

---

## E. Pricing does not match the business model

| # | App today | Business model |
|---|---|---|
| E1 | Four consumer plans are on sale now: Essential ₱1,500, **Plus ₱2,500, Pro ₱3,500, Clinic ₱5,000**, framed as "Personal monitoring" | Facility tiers: Essential ₱1,500 (now); Clinical ₱2,900 and Network ₱4,500, minimum 3 (both **after the build**, not purchasable); school licence ₱30,000/yr |
| E2 | Annual plan = 11 × monthly, labelled "**1 month free**" | The free month is withdrawn, and Essential has no room for a discount |
| E3 | No trial | Limited trial: 14 days or 25 exams, no payment details, no auto-conversion |
| E4 | Essential says "AI sound classification" for lung **and heart** | Heart is recording only |
| E5 | Same-site comparison is in "Pro" | You decided on 2 Nov it belongs in Essential, but the note still has it in Clinical |
| E6 | The page says plans are "informational, every feature is free", next to a working Stripe checkout | Contradictory. Are the Stripe prices live or test? |

Fixing E1 means creating new Stripe prices as well as changing the code.

---

## F. Decisions needed from you before fixing

1. **Stripe:** live or test mode? Should Clinical and Network be shown as "coming after the build" and not be purchasable?
2. **Same-site comparison:** Essential (your 2 Nov decision) or Clinical (what the note says)?
3. **Admin access:** remove the shared-password route and grant admin only from the Base44 dashboard? Also, who are the 5 current admins, and should the extra `app_role=admin` account be reset?
4. **AI severity grade:** remove it, or keep it as "screening priority"?
5. **Privacy policy:** a team contact e-mail. Does `assessSeverity` send data to a third-party AI? Should guardian consent for minors be required?
6. **Automatic cardiac plan:** keep auto-attaching a cardiac exercise plan to every heart recording, or attach one only when a practitioner chooses to?
7. **Lung-site names:** the app's six fields are upper front, mid-axillary (side) and lower back, left and right. Is that the canonical set the documents use?

## Suggested order

1. Heart Mode (A1–A4, A7–A9) and the Bluetooth / S3–S4 wording (D1, D2). These are what a judge would see in a demo.
2. Security B1–B5. Do these before any real patient uses the app.
3. Pricing (E), once F1 and F2 are decided.
4. The remaining bugs (C) and wording (D).
5. Then publish, which also ships the seven-site and rename edit.
