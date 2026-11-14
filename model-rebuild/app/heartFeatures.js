// Feature extraction and decoding for the Resondi heart-sound models (resondi-heart-v1).
//
// A reproduction of model-rebuild/scripts/heart_data.py (features), heart_seg.py (Viterbi decoding,
// heart rate) and heart_murmur.py (6 s windows), so the browser feeds the models what they were trained on:
//   0. decimate     16 kHz device audio -> 4 kHz (CirCor's rate): centred FIR low-pass, every 4th sample
//   1. band-pass    25-1900 Hz Butterworth, order 4, zero-phase (an exact copy of scipy's sosfiltfilt)
//   2. level        RMS 0.1
//   3. log power    256-point periodic-Hann STFT, 20 ms hop (50 frames/s), reflect padding, 129 bins
//   4. standardise  per frequency bin over the recording, then rounded to float16
// No browser APIs: the same file runs in Node for the parity check (scripts/check_heart_js.mjs).

import { SOS, SOS_ZI, PADLEN, FIR, ADVANCE } from "./heartConstants.js";

export const SR = 4000;
export const FPS = 50;
const HOP = 80, NFFT = 256, NBIN = 129;
export const CROP = 300, WHOP = 150;   // murmur windows: 6 s, 3 s hop

// ---------------------------------------------------------------- float16 rounding
export function f16(x) {
  if (x === 0 || !Number.isFinite(x)) return x;
  const s = x < 0 ? -1 : 1, a = Math.abs(x);
  if (a >= 65520) return s * Infinity;
  let e = Math.floor(Math.log2(a));
  if (Math.pow(2, e) > a) e -= 1;
  else if (Math.pow(2, e + 1) <= a) e += 1;
  if (e < -14) e = -14;
  const ulp = Math.pow(2, e - 10);
  const q = a / ulp;
  let r = Math.floor(q);
  const d = q - r;
  if (d > 0.5 || (d === 0.5 && r % 2 === 1)) r += 1;
  return s * r * ulp;
}

// ---------------------------------------------------------------- 0. 16 kHz -> 4 kHz
// numpy.convolve(x, FIR, "same")[::4]
export function decimate16k(x) {
  const L = FIR.length, half = (L - 1) >> 1, n = x.length;
  const out = new Float64Array(Math.ceil(n / 4));
  for (let o = 0, i = 0; i < n; i += 4, o++) {
    let s = 0;
    for (let k = 0; k < L; k++) {
      const j = i + half - k;
      if (j >= 0 && j < n) s += FIR[k] * x[j];
    }
    out[o] = s;
  }
  return out;
}

// ---------------------------------------------------------------- 1. scipy.signal.sosfiltfilt
function sosfilt(x, zi0) {
  const y = Float64Array.from(x);
  for (let s = 0; s < SOS.length; s++) {
    const [b0, b1, b2, , a1, a2] = SOS[s];
    let z0 = SOS_ZI[s][0] * zi0, z1 = SOS_ZI[s][1] * zi0;
    for (let i = 0; i < y.length; i++) {
      const xi = y[i];
      const yi = b0 * xi + z0;
      z0 = b1 * xi - a1 * yi + z1;
      z1 = b2 * xi - a2 * yi;
      y[i] = yi;
    }
  }
  return y;
}

export function sosfiltfilt(x) {
  const n = x.length, p = PADLEN;
  if (n <= p) throw new Error("The recording is too short to analyse.");
  const ext = new Float64Array(n + 2 * p);
  for (let i = 0; i < p; i++) ext[i] = 2 * x[0] - x[p - i];
  for (let i = 0; i < n; i++) ext[p + i] = x[i];
  for (let i = 0; i < p; i++) ext[p + n + i] = 2 * x[n - 1] - x[n - 2 - i];
  let y = sosfilt(ext, ext[0]);
  y.reverse();
  y = sosfilt(y, y[0]);
  y.reverse();
  return y.subarray(p, p + n);
}

// ---------------------------------------------------------------- FFT (radix-2, n = 256)
const REV = new Uint32Array(NFFT), COS = new Float64Array(NFFT / 2), SIN = new Float64Array(NFFT / 2);
for (let i = 0; i < NFFT; i++) { let r = 0; for (let b = 0; b < 8; b++) r |= ((i >> b) & 1) << (7 - b); REV[i] = r; }
for (let i = 0; i < NFFT / 2; i++) { COS[i] = Math.cos((2 * Math.PI * i) / NFFT); SIN[i] = -Math.sin((2 * Math.PI * i) / NFFT); }
function fft(re, im) {
  for (let i = 0; i < NFFT; i++) {
    const j = REV[i];
    if (j > i) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
  }
  for (let size = 2; size <= NFFT; size <<= 1) {
    const half = size >> 1, step = NFFT / size;
    for (let s = 0; s < NFFT; s += size) {
      for (let k = 0; k < half; k++) {
        const wr = COS[k * step], wi = SIN[k * step], a = s + k, b = a + half;
        const xr = re[b] * wr - im[b] * wi, xi = re[b] * wi + im[b] * wr;
        re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi;
      }
    }
  }
}
const HANN = new Float64Array(NFFT);
for (let i = 0; i < NFFT; i++) HANN[i] = Math.fround(0.5 - 0.5 * Math.cos((2 * Math.PI * i) / NFFT));

// ---------------------------------------------------------------- 1-4. 4 kHz audio -> features
// Returns { F: Float32Array(T * 129), T }.
export function features4k(x4) {
  const b = sosfiltfilt(x4);
  const n = b.length;
  let ss = 0;
  const xf = new Float32Array(n);
  for (let i = 0; i < n; i++) { xf[i] = b[i]; ss += xf[i] * xf[i]; }
  const g = 0.1 / (Math.sqrt(ss / n) + 1e-8);
  for (let i = 0; i < n; i++) xf[i] = Math.fround(xf[i] * g);
  // reflect padding by NFFT/2 on each side
  const pad = NFFT / 2, m = n + 2 * pad;
  const xp = new Float32Array(m);
  for (let i = 0; i < m; i++) {
    let j = i - pad;
    if (j < 0) j = -j;
    else if (j >= n) j = 2 * (n - 1) - j;
    xp[i] = xf[j];
  }
  const T = 1 + Math.floor((m - NFFT) / HOP);
  const L = new Float64Array(T * NBIN);
  const re = new Float64Array(NFFT), im = new Float64Array(NFFT);
  for (let t = 0; t < T; t++) {
    for (let i = 0; i < NFFT; i++) { re[i] = Math.fround(xp[t * HOP + i] * HANN[i]); im[i] = 0; }
    fft(re, im);
    for (let k = 0; k < NBIN; k++) L[t * NBIN + k] = Math.fround(Math.log(Math.fround(re[k] * re[k] + im[k] * im[k]) + 1e-10));
  }
  const F = new Float32Array(T * NBIN);
  for (let k = 0; k < NBIN; k++) {
    let mu = 0;
    for (let t = 0; t < T; t++) mu += L[t * NBIN + k];
    mu /= T;
    let v = 0;
    for (let t = 0; t < T; t++) { const d = L[t * NBIN + k] - mu; v += d * d; }
    const sd = Math.sqrt(v / T) + 1e-5;
    for (let t = 0; t < T; t++) F[t * NBIN + k] = f16((L[t * NBIN + k] - mu) / sd);
  }
  return { F, T };
}

// Browser audio at 16 kHz (-1..1) -> features.
export function features16k(x16) {
  return features4k(decimate16k(x16));
}

// ---------------------------------------------------------------- murmur windows
// 6 s windows at a 3 s hop; a recording of 6 s or less becomes one zero-padded window.
export function murmurWindows(F, T) {
  const starts = [];
  if (T <= CROP) starts.push(0);
  else for (let s = 0; s + CROP <= T; s += WHOP) starts.push(s);
  const W = new Float32Array(starts.length * CROP * NBIN);
  starts.forEach((s, w) => {
    const len = Math.min(CROP, T - s);
    W.set(F.subarray(s * NBIN, (s + len) * NBIN), w * CROP * NBIN);
  });
  return { W, n: starts.length };
}

// ---------------------------------------------------------------- segmentation decoding
// Cyclic S1 -> systole -> S2 -> diastole Viterbi on frame probabilities P (T x 4).
export function viterbi(P, T, adv = ADVANCE) {
  const ls = Math.log(1 - adv), la = Math.log(adv);
  let V = new Float64Array(4);
  for (let s = 0; s < 4; s++) V[s] = Math.log(P[s] + 1e-9);
  const back = new Int8Array(T * 4);
  for (let t = 1; t < T; t++) {
    const NV = new Float64Array(4);
    for (let s = 0; s < 4; s++) {
      const prev = (s + 3) % 4;
      const stay = V[s] + ls, move = V[prev] + la;
      const choose = move > stay;
      back[t * 4 + s] = choose ? prev : s;
      NV[s] = (choose ? move : stay) + Math.log(P[t * 4 + s] + 1e-9);
    }
    V = NV;
  }
  const path = new Int8Array(T);
  let best = 0;
  for (let s = 1; s < 4; s++) if (V[s] > V[best]) best = s;
  path[T - 1] = best;
  for (let t = T - 1; t > 0; t--) path[t - 1] = back[t * 4 + path[t]];
  return path;
}

export function onsets(path, state) {
  const out = [];
  for (let t = 0; t < path.length; t++) if (path[t] === state && (t === 0 || path[t - 1] !== state)) out.push(t);
  return out;
}

// 60 / median interval between successive S1 onsets (intervals 0.25-2 s); null when fewer than 3 S1.
export function bpmFrom(on) {
  if (on.length < 3) return null;
  const iv = [];
  for (let i = 1; i < on.length; i++) {
    const d = (on[i] - on[i - 1]) / FPS;
    if (d > 0.25 && d < 2.0) iv.push(d);
  }
  if (iv.length < 2) return null;
  iv.sort((a, b) => a - b);
  const h = iv.length >> 1;
  const med = iv.length % 2 ? iv[h] : (iv[h - 1] + iv[h]) / 2;
  return 60 / med;
}
