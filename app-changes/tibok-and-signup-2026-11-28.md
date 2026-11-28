# Tibok the mascot and the step-by-step sign-up (28 Nov 2026, SAVED in the editor, NOT published)

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
