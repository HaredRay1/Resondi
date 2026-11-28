# Tibok the mascot, the step-by-step sign-up and dark mode (28 Nov 2026, PUBLISHED)

User: "keep designing the app like a senior designer, add animations ... I really like maya's mobile app when the
user is signing up ... add a stethoscope with eyes, like those apps with animals that say 'Hi! Name'".

- **Tibok** (`src/components/brand/Tibok.jsx`): an SVG stethoscope whose chest piece is the face and whose ear
  tubes are the arms; "Tibok" is Filipino for heartbeat. Moods: idle, wave, happy, think, cover (covers its eyes
  while a password is typed), celebrate (jumps), listen (sound arcs). Eyes blink and can follow what is typed.
  `TibokSays` adds a speech bubble that pops when its text changes. Everything stops for reduced motion.
- **Sign-up** (`src/pages/Register.jsx`): one question per screen with a 3-part progress bar and a large pill
  button: hello (Tibok waves; Get started / Continue with Google) -> email (Tibok's eyes follow the typing) ->
  password (two fields, show/hide, live checks: 8+ characters, both match; Tibok covers its eyes) -> 6-digit
  code (30 s resend countdown; "Wrong email? Go back") -> "You're in!" with a small burst of hearts, then "/".
  The account calls are unchanged (register, verifyOtp, updateMe with language and policy_accepted, resendOtp,
  Google). If the email is already registered, the error offers "Sign in instead".
- **Sign-in** (`src/pages/Login.jsx`): same look; Tibok covers its eyes for the password; the error shakes. The
  button is never disabled for empty fields, because browsers autofill saved passwords without telling the page
  (found while checking: the button stayed grey over autofilled details).
- Tibok also on: the welcome page (above the headline), the loading screen (listening), every empty state
  (`EmptyState.jsx`), and the "Who are you?" role step.
- Checked in Chrome on the editor preview: sign-up hello, email and password steps run with no console errors
  (nothing was submitted; no account was created); sign-in renders. Not checked: the code step and the
  celebration (they need a real sign-up), the signed-in screens.
- Restore point before these changes: checkpoint `6b0a9d56ed95d5e40911124a` (the version published 28 Nov 09:22 UTC).
- Filipino text is Claude's; have a Filipino speaker read it.

## Published 28 Nov 2026, 10:43 UTC
Checkpoint `6b0ab05ce9546a130c909430`, commit `a993bb9a` (user: "publish").

## Dark mode (PUBLISHED 28 Nov 2026, 10:56 UTC)
User: "add a dark mode feature then publish it". Checkpoint `6b0ab34d0feca7058636b40e`, commit `c3b38250`.
- `src/lib/theme.js` (choice kept on the device in `resondi_theme`: light, dark or system; the app opens light
  unless the person chose otherwise, so screens nobody has checked in dark do not change for anyone by default),
  `src/components/ThemeToggle.jsx` (moon / sun button that turns as it swaps), `src/main.jsx` (theme set before
  the first render).
- Toggle on the welcome page (beside the language switch) and in the signed-in app's top bar (`AppShell.jsx`; the
  header's tint now follows the theme).
- Colours: `html.dark` block at the end of `src/unslop.css` (plum-tinted dark neutrals, rose accent unchanged,
  shadcn tokens for inputs, dialogs and toasts, and overrides for Tailwind white/gray utilities); the welcome
  page's tiles and buttons use variables with dark values.
- Checked in Chrome on the editor preview: the welcome page in dark mode, top and tiles, no console errors.
  Signed-in screens in dark mode were not seen; a team member should look through them.
- Note: a first publish call at 10:56 re-published the previous checkpoint by mistake; it was corrected seconds
  later with the dark-mode checkpoint.
- The published site could not be opened from this PC's Edge on 28 Nov: Microsoft Family Safety now asks for
  permission for resondi.base44.app. Claude did not try to get around it.
