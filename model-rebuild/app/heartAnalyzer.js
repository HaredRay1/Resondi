// Heart-sound analysis: Resondi heart models v1 (ONNX, run in the browser with onnxruntime-web).
//   1. Segmentation (CNN + BiGRU, one seed): labels every 20 ms as S1, systole, S2 or diastole; decoded in
//      cardiac-cycle order. Heart rate = 60 / median interval between successive S1 sounds.
//   2. Murmur (1-D CNN, 3 seeds averaged): score per 6 s window, averaged over the recording; flagged when
//      the score reaches the threshold fixed on validation patients. A patient is flagged when any site is.
// Trained and tested on the public CirCor DigiScope dataset (Brazilian children), patient-wise split. On 189
// test patients: heart rate within 3.0 BPM on average; murmur sensitivity 66.7% against a pre-specified 80%,
// specificity 97.1%. NOT tested on Resondi device recordings. A screening aid; a practitioner confirms
// every result, and "no murmur flagged" never rules a murmur out.
//
// Files are in https://github.com/HaredRay1/Ausculta (model/resondi-heart-v1), served through jsDelivr,
// pinned to one commit, never a branch. Change MODEL_COMMIT and MODEL_VERSION together.
// Features: ./heartFeatures.js, checked against the Python reference in Node (results/heart-js-parity.json).

import { features16k, murmurWindows, viterbi, onsets, bpmFrom, CROP, FPS } from "./heartFeatures.js";
import { MURMUR_THRESHOLD } from "./heartConstants.js";

const MODEL_COMMIT = "1e34348bf5cd536cc35b33fbfa43137cac5052c5";
const BASE = `https://cdn.jsdelivr.net/gh/HaredRay1/Ausculta@${MODEL_COMMIT}/model/resondi-heart-v1/`;
const SEG_URL = BASE + "resondi-heart-seg-v1.onnx";
const MUR_URL = BASE + "resondi-heart-murmur-v1.onnx";

// The same pinned runtime as the lung model, so the page loads it once.
const ORT_VERSION = "1.20.1";
const ORT_BASE = `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ORT_VERSION}/dist/`;

export const HEART_MODEL_VERSION = "resondi-heart-v1";
export { MURMUR_THRESHOLD };

const SAMPLE_RATE = 16000;
const MIN_SECONDS = 4;
const LOAD_TIMEOUT_MS = 60000;

let sessionsPromise = null;

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[data-src="${src}"]`);
    if (existing) {
      if (existing.dataset.loaded === "1" || window.ort) return resolve();
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
    promise.then((v) => { clearTimeout(timer); resolve(v); }, (e) => { clearTimeout(timer); reject(e); });
  });
}

async function fetchBytes(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to download the heart-sound model");
  return new Uint8Array(await res.arrayBuffer());
}

async function loadSessions() {
  if (sessionsPromise) return sessionsPromise;
  const attempt = (async () => {
    if (!window.ort) await loadScript(ORT_BASE + "ort.wasm.min.js");
    const ort = window.ort;
    if (!ort) throw new Error("ONNX runtime not available");
    ort.env.wasm.wasmPaths = ORT_BASE;
    ort.env.wasm.numThreads = 1;
    const [segBytes, murBytes] = await Promise.all([fetchBytes(SEG_URL), fetchBytes(MUR_URL)]);
    const seg = await ort.InferenceSession.create(segBytes, { executionProviders: ["wasm"] });
    const mur = await ort.InferenceSession.create(murBytes, { executionProviders: ["wasm"] });
    return { ort, seg, mur };
  })();
  sessionsPromise = timeout(attempt, LOAD_TIMEOUT_MS,
    "The heart-sound model took too long to load. Check the connection and try again.");
  sessionsPromise.catch(() => { sessionsPromise = null; });
  return sessionsPromise;
}

function resample(input, fromRate, toRate) {
  if (fromRate === toRate) return input;
  const ratio = toRate / fromRate;
  const out = new Float32Array(Math.round(input.length * ratio));
  for (let i = 0; i < out.length; i++) {
    const src = i / ratio, i0 = Math.floor(src), i1 = Math.min(i0 + 1, input.length - 1), fr = src - i0;
    out[i] = input[i0] * (1 - fr) + input[i1] * fr;
  }
  return out;
}

async function decodeAudio(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch audio");
  const buf = await res.arrayBuffer();
  const Ctx = window.AudioContext || window.webkitAudioContext;
  let ctx;
  try { ctx = new Ctx({ sampleRate: SAMPLE_RATE }); } catch { ctx = new Ctx(); }
  try {
    const audio = await ctx.decodeAudioData(buf);
    let data = audio.getChannelData(0);
    if (audio.sampleRate !== SAMPLE_RATE) data = resample(data, audio.sampleRate, SAMPLE_RATE);
    return data;
  } finally {
    ctx.close();
  }
}

const nextFrame = () => new Promise((r) => setTimeout(r, 0));

// Returns { heartRate: number|null, beats, murmurScore, murmurFlag, seconds, modelVersion }.
export async function analyzeHeart(audioUrl, onStatus) {
  onStatus?.("loading");
  const { ort, seg, mur } = await loadSessions();
  onStatus?.("decoding");
  const samples = await timeout(decodeAudio(audioUrl), 30000,
    "The recording took too long to download. Check the connection and try again.");
  const seconds = samples.length / SAMPLE_RATE;
  if (seconds < MIN_SECONDS) throw new Error("The recording is too short for heart-sound analysis.");
  onStatus?.("classifying");
  await nextFrame();
  const { F, T } = features16k(samples);
  await nextFrame();
  const P = (await seg.run({ feats: new ort.Tensor("float32", F, [1, T, 129]) })).probs.data;
  const s1 = onsets(viterbi(P, T), 0);
  const heartRate = bpmFrom(s1);
  const { W, n } = murmurWindows(F, T);
  const pr = (await mur.run({ wins: new ort.Tensor("float32", W, [n, CROP, 129]) })).prob.data;
  let murmurScore = 0;
  for (let i = 0; i < n; i++) murmurScore += pr[i];
  murmurScore /= n;
  return {
    heartRate: heartRate === null ? null : Math.round(heartRate),
    beats: s1.length,
    murmurScore,
    murmurFlag: murmurScore >= MURMUR_THRESHOLD,
    seconds: Math.round((T / FPS) * 10) / 10,
    modelVersion: HEART_MODEL_VERSION,
  };
}
