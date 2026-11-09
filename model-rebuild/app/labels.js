// Resondi lung classifier labels, for the app (src/lib/lungClassifier.js and every page that shows a result).
//
// The model outputs these four labels in exactly this order (alphabetical; Edge Impulse always sorts them).
// Read labels from the result objects ({label, value}) rather than by position wherever possible.
export const MODEL_LABELS = ['Crackles', 'Healthy', 'Wheezing', 'Wheezing with Crackles'];

// What the user sees. The labels are already sound patterns, so they display as themselves,
// with one plain-language line each. None of them is a diagnosis.
export const DISPLAY = {
  'Crackles': { title: 'Crackles', note: 'Short popping sounds were detected.' },
  'Healthy': { title: 'No adventitious sounds', note: 'No crackles or wheezes were detected.' },
  'Wheezing': { title: 'Wheezing', note: 'A continuous musical sound was detected.' },
  'Wheezing with Crackles': { title: 'Wheezing with crackles', note: 'Both wheezes and crackles were detected.' },
};

// Results saved by the old model used diagnosis labels. Show them as they were, marked as from the old model,
// and never convert them into the new labels: the old model did not detect sounds, so its output cannot be re-read as one.
export const LEGACY_LABELS = ['Asthma', 'Bronchiolitis', 'Healthy', 'Pneumonia'];
export const isLegacyResult = (result) => !result.model_version || result.model_version.startsWith('smartstethoscope-v5');

// Save this with every result, so a result can always be traced to the model that produced it.
export const MODEL_VERSION = 'resondi-lung-4class-v1';   // change when a new model is deployed
