// Check an Edge Impulse WebAssembly (browser) export before it goes into the app.
//
//   node scripts/check_deployed_model.js <folder with edge-impulse-standalone.js/.wasm and run-impulse.js> [clips folder]
//
// 1. Confirms the model outputs exactly the four labels, in config order.
// 2. Confirms it takes 16000 samples (1 s at 16 kHz), the input the app feeds it.
// 3. If a clips folder is given (export/edge-impulse/testing), classifies every test clip the way
//    the app does (1 s windows, scores averaged) and prints accuracy and a confusion matrix.
//    Those clips are from held-out patients, so this is a real test of the exported model.
const fs = require('fs');
const path = require('path');

const dir = path.resolve(process.argv[2] || '.');
const clips = process.argv[3] ? path.resolve(process.argv[3]) : null;
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'config', 'config.json'), 'utf8'));
process.chdir(dir);
global.Module = require(path.join(dir, 'edge-impulse-standalone.js'));
eval(fs.readFileSync(path.join(dir, 'run-impulse.js'), 'utf8').replace('class EdgeImpulseClassifier', 'global.EdgeImpulseClassifier = class'));

function readWav16(file) {  // 16-bit PCM mono WAV -> int16-scale numbers
  const b = fs.readFileSync(file);
  let p = 12, fmt = null;
  while (p < b.length) {
    const id = b.toString('ascii', p, p + 4), size = b.readUInt32LE(p + 4);
    if (id === 'fmt ') fmt = { ch: b.readUInt16LE(p + 10), sr: b.readUInt32LE(p + 12), bits: b.readUInt16LE(p + 22) };
    if (id === 'data') {
      if (!fmt || fmt.bits !== 16 || fmt.ch !== 1) throw new Error(file + ': need 16-bit mono');
      const n = size / 2, out = new Array(n);
      for (let i = 0; i < n; i++) out[i] = b.readInt16LE(p + 8 + 2 * i);
      return { sr: fmt.sr, x: out };
    }
    p += 8 + size + (size % 2);
  }
  throw new Error(file + ': no data chunk');
}

(async () => {
  const c = new EdgeImpulseClassifier();
  await c.init();
  const props = c.getProperties();
  const labels = Array.from({ length: props.labels.size ? props.labels.size() : props.labels.length },
    (_, i) => props.labels.get ? props.labels.get(i) : props.labels[i]);
  const win = props.input_features_count;
  console.log('project:', JSON.stringify(c.getProjectInfo()));
  console.log('labels:', labels.join(' | '));
  console.log('input samples:', win, 'at', props.frequency, 'Hz');
  let ok = true;
  if (JSON.stringify(labels) !== JSON.stringify(cfg.labels)) { ok = false; console.log('FAIL: labels differ from config:', cfg.labels.join(' | ')); }
  if (win !== 16000 || props.frequency !== 16000) { ok = false; console.log('FAIL: input is not 1 s at 16 kHz; the app would feed the wrong length'); }
  if (ok) console.log('PASS: labels and input size match the app');
  if (!clips) return process.exit(ok ? 0 : 1);

  const info = JSON.parse(fs.readFileSync(path.join(clips, '..', 'info.labels'), 'utf8'));
  const truth = Object.fromEntries(info.files.map(f => [path.basename(f.path), f.label.label]));
  const k = labels.length, cm = labels.map(() => new Array(k).fill(0));
  for (const f of fs.readdirSync(clips).filter(f => f.endsWith('.wav'))) {
    const { x } = readWav16(path.join(clips, f));
    const sums = new Array(k).fill(0);
    let n = 0;
    for (let s = 0; s === 0 || s + win <= x.length; s += win) {
      const w = x.slice(s, s + win);
      while (w.length < win) w.push(0);
      const r = c.classify(w);
      r.results.forEach(o => { sums[labels.indexOf(o.label)] += o.value; });
      n++;
      if (x.length <= win) break;
    }
    cm[cfg.labels.indexOf(truth[f])][sums.indexOf(Math.max(...sums))]++;
  }
  const total = cm.flat().reduce((a, b) => a + b, 0);
  const correct = cm.reduce((a, row, i) => a + row[i], 0);
  console.log(`\nheld-out test clips: ${total}, accuracy ${(correct / total).toFixed(3)}`);
  console.log('recall per class: ' + labels.map((l, i) => `${l} ${(cm[i][i] / Math.max(1, cm[i].reduce((a, b) => a + b, 0))).toFixed(3)}`).join(', '));
  console.log('confusion matrix (rows true, columns predicted):');
  cm.forEach((row, i) => console.log('  ' + labels[i].padEnd(24) + row.map(v => String(v).padStart(7)).join('')));
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error(e); process.exit(1); });
