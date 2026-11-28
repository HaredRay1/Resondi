# End-to-end test of the app (28 Nov 2026, editor preview, Chrome)

Run in the user's Chrome on the editor preview (the published site is blocked on this PC by Microsoft Family
Safety). The user signed in to every account and typed every password and code; Claude did the rest. Accounts:
one test patient, one test practitioner ("Test Practitioner (not real)", licence TEST-0000, Test Clinic), and the
user's own admin account. Test audio: one public SPRSound children's lung recording and one public CirCor heart
recording (patient 74417, aortic site, infant, murmur absent). No real patient data was used.

## Worked
- Patient: dashboard, guide pages, camera-guide page (camera not started), Quick Record .wav import, lung
  analysis (fusion model: "Possible crackles", score 36%, severity Mild) with the AI observations (so the new
  hourly AI cap lets normal use through), real waveform player, trends chart, heart exam .wav import, heart
  analysis (128 BPM, 39 S1 in 20.7 s, no murmur flagged), send for review, dark mode on every page visited.
- Heart rate check: CirCor's own S1 annotations for this recording give about 132 BPM (13 beats, 13.4-18.9 s);
  the app's segmentation network gave 128 BPM (4 BPM off, in line with the 3.0 BPM mean error on 189 patients).
  Code path: ONNX segmentation model labels every 20 ms; HR = 60 / median S1-S1 interval. Not invented.
- Practitioner: verification form, pending page, (admin approval), dashboard, patient profile with history,
  per-exercise approve / disapprove / further review with notes, status changes (Approved; Needs Further Review),
  "My Patients" count after review.
- Admin: dashboard counts, practitioner list, activity log records who verified whom.

## Problems found (to fix)
1. Heart recording results headed "Respiratory Sound Analysis".
2. Heart upload button says "...your lung recording".
3. AI observations invented "your current use of respiratory medications" (none entered): the assessSeverity
   prompt should forbid mentioning anything not in the given data.
4. "Verification Pending" page has no way to log out.
5. ~~A new account showed 5 notifications~~ Not a bug: the test patient account was used before; they are review notifications from 9 Nov.
6. Dark mode: the record buttons look dim.
7. Password-reset email still branded "AUSCULTA" (old logo and tagline), greets by username.
8. Exercise cards say "1 Minutes".
9. Heart recordings auto-suggest exercises incl. "Light Jogging in Place" before review (gated as Pending Review).
10. Quick Record import saves the length as 0 s (the file is 9 s); players show 0:00 / 0:00 until loaded.
11. Heart recording's exercise section headed "Recommended Respiratory Exercises".
12. Review decisions are signed with the account's username, not the practitioner's profile name.
13. The overall "Note for the patient about this plan" reaches the patient, but (a) it is copied onto every exercise
    that has no note of its own, (b) the patient sees it labelled "Your comment / explanation", and (c) the
    practitioner's reviewed card does not show it.
14. Notification times are 8 hours off: they show the review at 1:56 PM (UTC shown as local time); the review
    happened at 9:56 PM Philippine time, as the practitioner's and patient's cards say.
15. "Run again" is still offered on a heart recording after it was sent and reviewed (the lung page blocks re-runs).
16. Heart exercise cards show breathing-template figures that contradict the plan: "Gentle Walking, 5 minutes"
    shows "1 Minutes, 9 Breaths"; "Light Jogging in Place, 3 rounds x 40 s" shows "2 Minutes, 10 Breaths".

## Patient side after the review (checked)
- History: lung recording "Approved", heart recording "Requires Further Review".
- Notifications: one per reviewed recording, correct wording (times wrong, item 14).
- Approved exercises show "Start Exercise"; the disapproved one shows the practitioner's note and "Your
  practitioner has not approved these exercises"; the further-review one has no Start button.

## Fixes (28 Nov 2026, user: "fix everything except 7 and 9") — SAVED in the editor, NOT published
Restore point before the fixes: checkpoint `6b0ab5a2b5fb58e2a2b9fe56` (security limits).
- 1, 11: heart recordings say "Heart Sound Analysis" / "Recommended Heart Exercises" (patient page and
  practitioner card), in English and Filipino. `SessionDetail.jsx`, `SessionReviewCard.jsx`.
- 2: the heart exam's upload hint says "heart recording" (`SiteRecorder.jsx` takes `mode`; `HeartExam.jsx`).
- 3: `assessSeverity` prompt now forbids mentioning any medication, treatment, condition, test, habit or symptom not
  in the data given. (The test account's medical history may have mentioned medication; the rule holds either way.)
  Backend: live when saved.
- 4: "Log out" on the Verification Pending page (`PractitionerPending.jsx`).
- 6: not a bug: the button is the full rose (#E91E76) in dark mode; the screenshot caught the cards fading in.
- 8: "1 Minute" / "1 Breath" in the singular (English).
- 10: Quick Record saves the file's real length (`readDurationSeconds`, now exported from `SiteRecorder.jsx`).
- 12: reviews are signed with the practitioner's verified profile name (`submitPractitionerReview`; backend,
  live). Reviews written before the fix keep the username.
- 13: the overall note shows once ("Practitioner's note"), not copied onto every exercise; the practitioner's
  reviewed card shows it too.
- 14: notification and admin-activity times treat stored times as UTC (`src/lib/dates.js`): 9:56 PM, not 1:56 PM.
- 15: no "Run again" on a heart recording once it has been sent (`HeartAnalysisCard` `canRerun`).
- 16: exercise minutes come from the plan's own text when it states a time (heart and lung); heart exercises show
  no "Breaths".
Checked in Chrome on the preview (test patient): heart page headings, no re-run, exercise figures, note shown once;
notification times; lung "1 Minute" and "2 minutes -> 2 Minutes". Not re-checked live: 3 and 12 (need a new
analysis and a new review), 4 (needs a pending account), 10 (needs a new upload).

## Published 28 Nov 2026, 14:44 UTC (user: "1" = publish)
Checkpoint `6b0ae8bf2f74aad6b72e82be`, commit `fb95cc85`. Includes the security lockout message
(RoleSelection) saved earlier. The test data (2 recordings, the test practitioner) is still in the app; the user
has not decided whether to delete it.
