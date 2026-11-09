"""Audio loading, resampling, windowing and MFCC features.

The MFCC follows the steps of Edge Impulse's audio MFCC block (which is based on SpeechPy):
pre-emphasis, framing, power spectrum, mel filterbank, log, DCT, then mean normalisation over a
sliding window. It is a close reimplementation, not Edge Impulse's code, so a model trained here
and a model trained in Edge Impulse Studio on the same data will be similar, not identical.
"""
import io
from math import gcd

import numpy as np
import soundfile as sf
from scipy.fft import dct
from scipy.signal import resample_poly


def load_audio(data_or_path, target_sr):
    """Return mono int16-scale float32 audio at target_sr."""
    src = io.BytesIO(data_or_path) if isinstance(data_or_path, (bytes, bytearray)) else data_or_path
    x, sr = sf.read(src, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    if sr != target_sr:
        g = gcd(int(sr), int(target_sr))
        x = resample_poly(x, target_sr // g, int(sr) // g).astype(np.float32)
    return np.clip(x * 32768.0, -32768, 32767).astype(np.float32)


def windows(x, start_s, end_s, sr, win, stride):
    """Cut [start, end) into fixed windows. Short segments are zero-padded to one window."""
    a, b = int(round(start_s * sr)), int(round(end_s * sr))
    seg = x[a:b]
    if len(seg) == 0:
        return []
    if len(seg) <= win:
        return [np.pad(seg, (0, win - len(seg)))]
    out = [seg[i:i + win] for i in range(0, len(seg) - win + 1, stride)]
    if (len(seg) - win) % stride:  # keep the tail of the segment
        out.append(seg[-win:])
    return out


def _mel(hz):
    return 1127.0 * np.log(1 + hz / 700.0)


def _hz(mel):
    return 700.0 * (np.exp(mel / 1127.0) - 1)


def _filterbank(n_filters, n_fft, sr, low, high):
    high = high or sr / 2
    mels = np.linspace(_mel(low), _mel(high), n_filters + 2)
    bins = np.floor((n_fft + 1) * _hz(mels) / sr).astype(int)
    fb = np.zeros((n_filters, n_fft // 2 + 1), dtype=np.float32)
    for i in range(n_filters):
        l, c, r = bins[i], bins[i + 1], bins[i + 2]
        for k in range(l, c):
            fb[i, k] = (k - l) / max(c - l, 1)
        for k in range(c, r):
            fb[i, k] = (r - k) / max(r - c, 1)
    return fb


class MFCC:
    def __init__(self, cfg, sr):
        self.c, self.sr = cfg, sr
        self.flen = int(round(cfg["frame_length"] * sr))
        self.fstep = int(round(cfg["frame_stride"] * sr))
        self.fb = _filterbank(cfg["num_filters"], cfg["fft_length"], sr, cfg["low_frequency"], cfg["high_frequency"])

    def n_frames(self, n_samples):
        return 1 + (n_samples - self.flen) // self.fstep

    def __call__(self, sig):
        c = self.c
        sig = np.append(sig[0], sig[1:] - c["pre_cof"] * sig[:-1])
        n = self.n_frames(len(sig))
        idx = np.arange(self.flen)[None, :] + self.fstep * np.arange(n)[:, None]
        frames = sig[idx]
        mag = np.abs(np.fft.rfft(frames, n=c["fft_length"]))
        power = (mag ** 2) / c["fft_length"]
        energies = power @ self.fb.T
        energies = np.where(energies == 0, np.finfo(np.float32).eps, energies)
        feats = dct(np.log(energies), type=2, axis=1, norm="ortho")[:, :c["num_cepstral"]]
        return self._cmvnw(feats, c["win_size"]).astype(np.float32)

    @staticmethod
    def _cmvnw(feats, win):
        """Mean normalisation over a sliding window (SpeechPy cmvnw, variance normalisation off)."""
        half = (win - 1) // 2
        pad = np.pad(feats, ((half, half), (0, 0)), mode="symmetric")
        csum = np.cumsum(np.vstack([np.zeros((1, feats.shape[1])), pad]), axis=0)
        means = (csum[win:win + len(feats)] - csum[:len(feats)]) / win
        return feats - means
