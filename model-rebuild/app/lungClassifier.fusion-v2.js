// Lung-sound classifier: Resondi fusion model v2 (ONNX, run in the browser with onnxruntime-web).
// Model: three-branch FDC-FS fusion (MFCC + spectrogram + chromagram), an ensemble of 3 training seeds,
// trained on ICBHI 2017 + SPRSound. Outputs four sound patterns: Crackles, Healthy, Wheezing,
// Wheezing with Crackles. In 5-fold patient cross-validation on all 126 ICBHI patients it scored 40.0%
// balanced accuracy (chance 25%); the previous model's design scored 34.0%. It has NOT been tested on
// Resondi device recordings. It is a screening aid; every result is confirmed by a practitioner.
//
// Files are in https://github.com/HaredRay1/Ausculta (model/resondi-lung-fusion-v2), served through
// jsDelivr and pinned to one commit, never a branch: a branch reference lets any push silently change
// the model every user runs. To update the model, change MODEL_COMMIT, MODEL_PATH and MODEL_VERSION
// together. Features are computed by ./fusionFeatures.js, a reproduction of the training code
// (model-rebuild/scripts/fusion.py), checked to give the same top label on 600 of 600 validation windows.

import { cutWindows, windowFeatures, SHAPES } from "./fusionFeatures";

const MODEL_COMMIT = "c9cd3fa2ca625a585efc6fb3f75734f585badfae";
const MODEL_PATH = "model/resondi-lung-fusion-v2/resondi-lung-fusion-v2.onnx";
const MODEL_URL = `https://cdn.jsdelivr.net/gh/HaredRay1/Ausculta@${MODEL_COMMIT}/${MODEL_PATH}`;

// The ONNX runtime, pinned to one version.
const ORT_VERSION = "1.20.1";
const ORT_BASE = `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ORT_VERSION}/dist/`;

// Saved with every analysis, so each result can be traced to the model that produced it.
// "resondi-lung-4class-v1" = the Edge Impulse model used 10-13 Nov 2026; empty = the withdrawn
// diagnosis model.
export const MODEL_VERSION = "resondi-lung-fusion-v2";

const LABELS = ["Crackles", "Healthy", "Wheezing", "Wheezing with Crackles"];
const SAMPLE_RATE = 16000;

// How long the model download and start-up may take before it counts as failed.
const MODEL_LOAD_TIMEOUT_MS = 60000;

let sessionPromise = null;

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[data-src="${src}"]`);
    if (existing) {
      if (existing.dataset.loaded === "1") return resolve();
      if (existing.dataset.failed === "1") existing.remove();
      else {
        existing.addEventListener("load", () => resolve());
        existing.addEventListener("error", () => reject(new Error("Failed to load " + src)));
        return;
      }
    }
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.crossOrigin = "anonymous";
    s.dataset.src = src;
    s.onload = () => { s.dataset.loaded = "1"; resolve(); };
    s.onerror = () => { s.dataset.failed = "1"; reject(new Error("Failed to load " + src)); };
    document.head.appendChild(s);
  });
}

function timeout(promise, ms, message) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(message)), ms);
    promise.then(
      (v) => { clearTimeout(timer); resolve(v); },
      (e) => { clearTimeout(timer); reject(e); },
    );
  });
}

async function loadSession() {
  if (sessionPromise) return sessionPromise;
  const attempt = (async () => {
    await loadScript(ORT_BASE + "ort.wasm.min.js");
    const ort = window.ort;
    if (!ort) throw new Error("ONNX runtime not available");
    ort.env.wasm.wasmPaths = ORT_BASE;
    ort.env.wasm.numThreads = 1; // threads need cross-origin isolation, which the app does not have
    const res = await fetch(MODEL_URL);
    if (!res.ok) throw new Error("Failed to download the sound model");
    const bytes = new Uint8Array(await res.arrayBuffer());
    const session = await ort.InferenceSession.create(bytes, { executionProviders: ["wasm"] });
    return { ort, session };
  })();
  sessionPromise = timeout(
    attempt,
    MODEL_LOAD_TIMEOUT_MS,
    "The sound model took too long to load. Check the connection and try again.",
  );
  // A failed or stalled load must not be cached, or every retry fails until the page is reloaded.
  sessionPromise.catch(() => { sessionPromise = null; });
  return sessionPromise;
}

function resample(input, fromRate, toRate) {
  if (fromRate === toRate) return input;
  const ratio = toRate / fromRate;
  const outLen = Math.round(input.length * ratio);
  const out = new Float32Array(outLen);
  for (let i = 0; i < outLen; i++) {
    const srcIdx = i / ratio;
    const i0 = Math.floor(srcIdx);
    const i1 = Math.min(i0 + 1, input.length - 1);
    const frac = srcIdx - i0;
    out[i] = input[i0] * (1 - frac) + input[i1] * frac;
  }
  return out;
}

async function decodeAudio(url, targetRate) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch audio");
  const buf = await res.arrayBuffer();
  const Ctx = window.AudioContext || window.webkitAudioContext;
  let ctx;
  try { ctx = new Ctx({ sampleRate: targetRate }); }
  catch { ctx = new Ctx(); }
  try {
    const audioBuf = await ctx.decodeAudioData(buf);
    let data = audioBuf.getChannelData(0);
    if (audioBuf.sampleRate !== targetRate) data = resample(data, audioBuf.sampleRate, targetRate);
    return data;
  } finally {
    ctx.close();
  }
}

const nextFrame = () => new Promise((r) => setTimeout(r, 0));

export async function analyzeAudio(audioUrl, onStatus) {
  onStatus?.("loading");
  const { ort, session } = await loadSession();
  onStatus?.("decoding");
  const samples = await timeout(
    decodeAudio(audioUrl, SAMPLE_RATE),
    30000,
    "The recording took too long to download. Check the connection and try again.",
  );
  onStatus?.("classifying");

  // Consecutive 1-second windows across the whole file, with per-class scores averaged, so one
  // outlier window can't dominate the result. Each window is band-limited to 100-3900 Hz and
  // levelled before its features are computed, exactly as in training.
  const wins = cutWindows(samples);
  const n = wins.length;
  const views = Object.fromEntries(Object.entries(SHAPES).map(([k, [t, f]]) => [k, new Float32Array(n * t * f)]));
  for (let w = 0; w < n; w++) {
    const f = windowFeatures(wins[w]);
    for (const k of Object.keys(views)) views[k].set(f[k], w * f[k].length);
    if (w % 4 === 3) await nextFrame(); // keep the page responsive on long recordings
  }
  const feeds = Object.fromEntries(
    Object.entries(SHAPES).map(([k, [t, f]]) => [k, new ort.Tensor("float32", views[k], [n, t, f])]),
  );
  const out = await session.run(feeds);
  const probs = out.probs.data;

  const results = LABELS.map((label, c) => {
    let s = 0;
    for (let w = 0; w < n; w++) s += probs[w * LABELS.length + c];
    return { label, value: s / n };
  });
  const top = results.reduce((a, b) => ((b?.value ?? -1) > (a?.value ?? -1) ? b : a), null);
  return { top, results, windows: n, modelVersion: MODEL_VERSION };
}

export function mapClassification(label) {
  const l = (label || "").toLowerCase().trim();
  // Current model labels (sound patterns). The combined label is checked first,
  // because it contains both "wheez" and "crackle".
  if (/wheez/.test(l) && /crackle/.test(l)) return "wheezing_crackles";
  if (/crackle/.test(l)) return "crackles";
  if (/wheez/.test(l)) return "wheezing";
  if (/(healthy|normal|clear|clean|silence)/.test(l)) return "normal";
  // Earlier, withdrawn model (diagnosis labels), kept so old saved breakdowns still display.
  if (/asthma/.test(l)) return "wheezing";
  if (/(bronch|tuberculosis|^tb$)/.test(l)) return "wheezing_crackles";
  if (/(pneumonia|influenza)/.test(l)) return "crackles";
  if (/(abnormal|other|unknown|noise|artifact)/.test(l)) return "other_abnormal";
  return "undetermined";
}

// Everything below is unchanged from the 4-class v1 version of this file.

export function deriveSeverity(classification, confidence) {
  if (classification === "normal") return "normal";
  if (classification === "undetermined") return "mild";
  return confidence >= 85 ? "moderate" : "mild";
}

const SUMMARIES = {
  normal: "The AI model did not flag an abnormal respiratory sound pattern in this recording. This is a screening result, not a clinical all-clear; follow your practitioner's guidance.",
  crackles: "The AI model flagged a possible crackling pattern, which can be associated with fluid or secretions in the airways. This is a possibility, not a diagnosis; a practitioner must review it.",
  wheezing: "The AI model flagged a possible wheezing pattern, which is often associated with narrowed airways. This is a possibility, not a diagnosis; a practitioner must review it.",
  wheezing_crackles: "The AI model flagged a possible combination of wheezing and crackling patterns. This is a possibility, not a diagnosis; a practitioner must review it.",
  other_abnormal: "The AI model flagged a possible abnormal respiratory sound pattern. This is a possibility, not a diagnosis; a practitioner must review it.",
  undetermined: "The AI model could not confidently classify your recording. Practitioner review is recommended.",
};

export function buildSummary(classification) {
  return SUMMARIES[classification] || SUMMARIES.undetermined;
}

export function buildRecommendation(classification) {
  const map = {
    normal: {
      recommendation: "Diaphragmatic Breathing — 5 minutes daily. Pursed-lip Breathing — 3 repetitions, twice daily. Box Breathing — 3 minutes daily. Shoulder Rolls — 10 slow circles. Seated Marching — 2 minutes.",
      reason: "To support healthy lung function, keep the chest wall mobile, and maintain clear airways.",
      exercises: [
        { name: "Diaphragmatic Breathing", description: "5 minutes daily", status: "pending_review" },
        { name: "Pursed-lip Breathing", description: "3 repetitions, twice daily", status: "pending_review" },
        { name: "Box Breathing", description: "3 minutes daily", status: "pending_review" },
        { name: "Shoulder Rolls", description: "10 slow circles", status: "pending_review" },
        { name: "Seated Marching", description: "2 minutes", status: "pending_review" },
      ],
    },
    crackles: {
      recommendation: "Active Cycle of Breathing Technique — 2 cycles, twice daily. Huff Coughing — 3 repetitions as needed. Chest Expansion Breathing — 5 slow breaths. Seated Marching — 2 minutes.",
      reason: "Airway-clearance techniques to help move secretions detected as crackling sounds, plus gentle mobility to keep the chest wall moving.",
      exercises: [
        { name: "Active Cycle of Breathing Technique", description: "2 cycles, twice daily", status: "pending_review" },
        { name: "Huff Coughing", description: "3 repetitions as needed", status: "pending_review" },
        { name: "Chest Expansion Breathing", description: "5 slow breaths", status: "pending_review" },
        { name: "Seated Marching", description: "2 minutes", status: "pending_review" },
      ],
    },
    wheezing: {
      recommendation: "Pursed-lip Breathing — 5 repetitions during wheezing episodes. Diaphragmatic Breathing — 5 minutes daily. Paced Walking with Breathing — 5 minutes. Shoulder Rolls — 10 slow circles.",
      reason: "Breathing techniques to help keep airways open during wheezing, with paced walking to build tolerance for everyday activity.",
      exercises: [
        { name: "Pursed-lip Breathing", description: "5 repetitions during episodes", status: "pending_review" },
        { name: "Diaphragmatic Breathing", description: "5 minutes daily", status: "pending_review" },
        { name: "Paced Walking with Breathing", description: "5 minutes, easy pace", status: "pending_review" },
        { name: "Shoulder Rolls", description: "10 slow circles", status: "pending_review" },
      ],
    },
    wheezing_crackles: {
      recommendation: "Pursed-lip Breathing — 5 repetitions, twice daily. Active Cycle of Breathing Technique — 2 cycles daily. Diaphragmatic Breathing — 5 minutes daily. Standing Chest Opening — 5 slow breaths.",
      reason: "Combined wheezing and crackles suggest both airway narrowing and secretions; these techniques help keep airways open and clear secretions.",
      exercises: [
        { name: "Pursed-lip Breathing", description: "5 repetitions, twice daily", status: "pending_review" },
        { name: "Active Cycle of Breathing Technique", description: "2 cycles daily", status: "pending_review" },
        { name: "Diaphragmatic Breathing", description: "5 minutes daily", status: "pending_review" },
        { name: "Standing Chest Opening", description: "5 slow breaths", status: "pending_review" },
      ],
    },
    other_abnormal: {
      recommendation: "Diaphragmatic Breathing — 5 minutes daily. Practitioner review recommended before starting further exercises.",
      reason: "An abnormal sound was detected; clinical evaluation is advised.",
      exercises: [
        { name: "Diaphragmatic Breathing", description: "5 minutes daily", status: "pending_review" },
      ],
    },
    undetermined: {
      recommendation: "Await practitioner review before starting any new breathing exercises.",
      reason: "The AI model could not confidently classify the recording.",
      exercises: [],
    },
  };
  return map[classification] || map.undetermined;
}

// Cardiac rehabilitation plan. Heart recordings are reviewed by a cardiac
// practitioner, so these arrive pending approval like every other plan.
export function buildCardiacRecommendation() {
  return {
    recommendation:
      "Light Jogging in Place — 3 rounds of 40 seconds. Gentle Walking — 5 minutes. Seated Marching — 2 minutes. Arm Circles — 10 each direction. Standing Chest Opening — 5 slow breaths.",
    reason:
      "Light aerobic activity with gentle mobility work, at a pace where you can still speak, to support heart health and build everyday stamina.",
    exercises: [
      { name: "Light Jogging in Place", description: "3 rounds · 40 seconds each", status: "pending_review" },
      { name: "Gentle Walking", description: "5 minutes, conversational pace", status: "pending_review" },
      { name: "Seated Marching", description: "2 minutes", status: "pending_review" },
      { name: "Arm Circles", description: "10 each direction", status: "pending_review" },
      { name: "Standing Chest Opening", description: "5 slow breaths", status: "pending_review" },
    ],
  };
}
