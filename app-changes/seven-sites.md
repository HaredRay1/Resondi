# Resondi app: back to the seven-site lung protocol

**Why.** The live app (resondi.base44.app, checked 31 Oct 2026) guides **nine** lung sites. Every document (concept note, deck, script, IMRaD, Q&A, paper pack) says the app records **seven** and that nine is *planned*. Remove the two interscapular (upper-back) sites so the app matches.

**After the change the exam counter reads:** "Site n of 7" in standard (lung) mode and "of 12" in advanced (lung + heart) mode, matching the documents.

---

## Option A: prompt for the Base44 AI builder

Paste this into the Base44 editor chat:

> In the auscultation site definitions (the module that exports the lung and heart site lists, built as `auscultaSites`), remove the two interscapular sites from the `lungPosterior` plate: "Right upper, posterior" (bodyLocation `upper_right_back`) and "Left upper, posterior" (bodyLocation `upper_left_back`). Keep the two infrascapular sites, renumbered: "Right lower, posterior" becomes order 6, tag "5"; "Left lower, posterior" becomes order 7, tag "6". Do not change any other site, the heart sites, the translation labels, or the diagram coordinates, and do not delete existing recordings. Lung Mode should then have seven sites (Trachea plus six lung fields) and the full exam counter should show 7 in standard mode and 12 in advanced mode.

## Option B: edit the code directly

In the site-definitions file, replace the whole `lungPosterior` entry with:

```js
lungPosterior: {
  plate: 'lungPosterior',
  orientation: 'posterior',
  sites: [
    { order: 6, code: 'Pr-low', tag: '5', name: 'Right lower, posterior',
      landmark: 'Infrascapular, T8 to T10', bodyLocation: 'lower_right_back',
      icbhi: 'Pr', region: 'right lower lobe', seconds: 20,
      listen: 'Right lower lobe, where crackles collect.', left: 68.75, top: 72.169 },
    { order: 7, code: 'Pl-low', tag: '6', name: 'Left lower, posterior',
      landmark: 'Infrascapular, T8 to T10', bodyLocation: 'lower_left_back',
      icbhi: 'Pl', region: 'left lower lobe', seconds: 20,
      listen: 'Left lower lobe, where crackles collect.', left: 31.25, top: 72.169 },
  ],
},
```

The internal `code` values (`Pr-low`, `Pl-low`) are deliberately unchanged, in case saved recordings refer to them. With the upper-back pair gone, each of the seven sites now has its own ICBHI code (Tc, Ar, Al, Lr, Ll, Pr, Pl), which is what the concept note states.

## Leave these alone

- **Translation labels** for `upper_right_back` / `upper_left_back` (English and Filipino). Recordings already made at those sites still need their names in history views.
- **Diagram positions** for those sites in the Full Exam screen. They are only used when a site is in the list, so they become inert.

## Check after publishing

1. Patient side, Full Exam, standard mode: the header says 7 sites and the counter runs 1 to 7, ending on the two lower-back sites.
2. Advanced mode: 12 sites in total.
3. Lung Mode guide (Auscultation Guide page): the back view shows only the two lower sites, numbered 5 and 6.
4. An old recording made at an upper-back site still opens and shows its site name.
5. **Server-side rule layer.** The four-zone interpretation rules are not in the browser code, so they could not be checked from outside. If they read `upper_right_back` / `upper_left_back`, those inputs simply stop arriving; confirm the upper-zone rules still use the upper-front sites (`upper_right_front`, `upper_left_front`).
