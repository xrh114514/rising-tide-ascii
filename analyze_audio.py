"""Analyze the soundtrack and write beats.json (tempo / onsets / energy map).

Run once:  python analyze_audio.py "track.flac" -o beats.json
The animation engine loads beats.json at runtime to sync pulses, glitches and
section intensity to the music.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 22050
HOP = 512          # ~23ms per analysis hop
FPS = SR / HOP


def decode(path: Path) -> np.ndarray:
    """Decode any audio format to mono float32 at SR using bundled ffmpeg."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(path),
           "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


def frames(x: np.ndarray):
    n = len(x) // HOP
    return x[: n * HOP].reshape(n, HOP)


def analyze(x: np.ndarray):
    fr = frames(x)
    win = np.hanning(HOP)
    spec = np.abs(np.fft.rfft(fr * win, axis=1))          # (n, 257)
    freqs = np.fft.rfftfreq(HOP, 1.0 / SR)

    energy = (fr ** 2).mean(axis=1)
    rms = np.sqrt(energy + 1e-12)

    # spectral flux onsets
    logspec = np.log1p(spec * 50.0)
    flux = np.maximum(0.0, np.diff(logspec, axis=0)).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    if flux.max() > 0:
        flux = flux / flux.max()

    # smooth + peak-pick onsets
    k = 4
    sm = np.convolve(flux, np.ones(k) / k, mode="same")
    onsets = []
    for i in range(2, len(flux) - 2):
        if flux[i] > 0.12 and flux[i] >= sm[i] * 1.35 and flux[i] == max(flux[i - 2:i + 3]):
            t = i * HOP / SR
            if not onsets or t - onsets[-1] > 0.12:
                onsets.append(t)

    # tempo via autocorrelation of the onset envelope (60..180 BPM)
    env = flux - sm
    env = np.maximum(env, 0.0)
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lag_min = int(FPS * 60.0 / 180.0)
    lag_max = int(FPS * 60.0 / 60.0)
    seg = ac[lag_min:lag_max]
    bpm = 60.0 * FPS / (lag_min + int(np.argmax(seg))) if seg.size else 120.0

    # low / mid / high band energies (for scene colour grading)
    band = lambda lo, hi: spec[:, (freqs >= lo) & (freqs < hi)].mean(axis=1)
    low = band(20, 200)
    mid = band(200, 2000)
    high = band(2000, 9000)

    def norm(a):
        m = a.max()
        return (a / m if m > 0 else a).astype(np.float32)

    return {
        "bpm": round(float(bpm), 2),
        "duration": round(float(len(x) / SR), 3),
        "onsets": [round(t, 3) for t in onsets],
        "energy": [round(float(v), 4) for v in norm(rms)[::2]],        # ~46ms grid
        "flux": [round(float(v), 4) for v in norm(flux)[::2]],
        "low": [round(float(v), 4) for v in norm(low)[::2]],
        "mid": [round(float(v), 4) for v in norm(mid)[::2]],
        "high": [round(float(v), 4) for v in norm(high)[::2]],
        "grid_dt": round(2 * HOP / SR, 5),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("-o", "--out", default="beats.json")
    a = ap.parse_args()
    data = analyze(decode(Path(a.audio)))
    Path(a.out).write_text(json.dumps(data), encoding="utf-8")
    print(f"bpm={data['bpm']} duration={data['duration']} "
          f"onsets={len(data['onsets'])} -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
