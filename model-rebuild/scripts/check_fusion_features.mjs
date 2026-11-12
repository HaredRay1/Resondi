// Node half of the fusion parity check: read int16 windows, compute features with app/fusionFeatures.js.
// Run by scripts/check_fusion_features.py; not meant to be run on its own.
import { readFileSync, writeFileSync } from "node:fs";
import { windowFeatures } from "../app/fusionFeatures.js";

const [, , rawPath, outPath, nStr] = process.argv;
const n = Number(nStr);
const buf = readFileSync(rawPath);
const raw = new Int16Array(buf.buffer, buf.byteOffset, n * 16000);
const parts = { mfcc: [], spec: [], chroma: [] };
const t0 = Date.now();
for (let w = 0; w < n; w++) {
  const x = Float64Array.from(raw.subarray(w * 16000, (w + 1) * 16000));
  const f = windowFeatures(x);
  for (const k of Object.keys(parts)) parts[k].push(f[k]);
}
const ms = (Date.now() - t0) / n;
for (const k of Object.keys(parts)) {
  const len = parts[k][0].length;
  const all = new Float32Array(n * len);
  parts[k].forEach((a, i) => all.set(a, i * len));
  writeFileSync(`${outPath}.${k}.bin`, Buffer.from(all.buffer));
}
console.log(`node: ${n} windows, ${ms.toFixed(1)} ms per window`);
