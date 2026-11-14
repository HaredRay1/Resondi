// Node parity check of the browser heart code (app/heartFeatures.js + onnxruntime-web) against the
// Python reference of the app path (scripts/heart_app_path.py, which writes work-exp/heart/js-fixture).
// Needs onnxruntime-web installed next to this file when run (a scratch folder with
// `npm i onnxruntime-web@1.20.1`); run there as: node check_heart_js.mjs <model-rebuild dir>
import * as ort from "onnxruntime-web";
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const MR = process.argv[2].replace(/\\/g, "/");
const H = await import(pathToFileURL(`${MR}/app/heartFeatures.js`).href);
const { MURMUR_THRESHOLD } = await import(pathToFileURL(`${MR}/app/heartConstants.js`).href);
ort.env.wasm.numThreads = 1;
const seg = await ort.InferenceSession.create(readFileSync(`${MR}/deploy/resondi-heart-v1/resondi-heart-seg-v1.onnx`));
const mur = await ort.InferenceSession.create(readFileSync(`${MR}/deploy/resondi-heart-v1/resondi-heart-murmur-v1.onnx`));
const FIX = `${MR}/work-exp/heart/js-fixture`;
const fixture = JSON.parse(readFileSync(`${FIX}/fixture.json`, "utf8"));
const f32 = (p) => { const b = readFileSync(p); return new Float32Array(b.buffer, b.byteOffset, b.length / 4); };

const rows = [];
let maxF = 0, nDiff = 0, nAll = 0, ms = 0;
for (const fx of fixture) {
  const id = String(fx.i).padStart(2, "0");
  const x16 = f32(`${FIX}/${id}.f32`);
  const t0 = Date.now();
  const { F, T } = H.features16k(x16);
  const Fp = f32(`${FIX}/${id}.F.f32`);
  if (T !== fx.T) throw new Error(`${fx.name}: frames ${T} vs ${fx.T}`);
  for (let i = 0; i < F.length; i++) { const d = Math.abs(F[i] - Fp[i]); if (d > 0) nDiff++; if (d > maxF) maxF = d; }
  nAll += F.length;
  const P = (await seg.run({ feats: new ort.Tensor("float32", F, [1, T, 129]) })).probs.data;
  const path = H.viterbi(P, T);
  const s1 = H.onsets(path, 0);
  const bpm = H.bpmFrom(s1);
  const { W, n } = H.murmurWindows(F, T);
  const pr = (await mur.run({ wins: new ort.Tensor("float32", W, [n, H.CROP, 129]) })).prob.data;
  const m = pr.reduce((a, b) => a + b, 0) / n;
  ms += Date.now() - t0;
  rows.push({ name: fx.name, bpm_py: fx.bpm, bpm_js: bpm, mur_py: fx.murmur, mur_js: m, s1_py: fx.s1, s1_js: s1.length,
              flag_same: (m >= MURMUR_THRESHOLD) === (fx.murmur >= MURMUR_THRESHOLD) });
}
const bpmOk = rows.filter((r) => (r.bpm_py === null) === (r.bpm_js === null) && (r.bpm_py === null || Math.abs(r.bpm_py - r.bpm_js) < 0.5)).length;
const murMax = Math.max(...rows.map((r) => Math.abs(r.mur_py - r.mur_js)));
const flags = rows.filter((r) => r.flag_same).length;
const summary = { recordings: rows.length, feature_values_differing: nDiff, feature_values: nAll, feature_max_abs_diff: maxF,
                  heart_rate_same_within_0_5_bpm: bpmOk, murmur_score_max_abs_diff: murMax, murmur_flag_same: flags,
                  ms_per_recording: ms / rows.length };
writeFileSync(`${MR}/results/heart-js-parity.json`, JSON.stringify({ summary, rows }, null, 1));
console.log(JSON.stringify(summary, null, 1));
