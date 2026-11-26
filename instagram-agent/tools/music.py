#!/usr/bin/env python3.13
"""Original background music for reels (no copyrighted audio, made from scratch).

Oud-like plucked strings (Karplus-Strong) on Arabic maqamat with quarter tones,
a soft drone, and an optional frame-drum rhythm.

usage: python3.13 tools/music.py <mood> <seconds> <out.wav> [seed]
moods: hijaz (poetry, longing) · nahawand (wisdom, calm) · ajam (facts / on-this-day, light rhythm)
"""
import sys, wave
import numpy as np

SR = 44100
rng = None

# scale steps in semitones from tonic (quarter tones as .5)
MAQAM = {
    "hijaz":    [0, 1, 4, 5, 7, 8, 10, 12],
    "nahawand": [0, 2, 3, 5, 7, 8, 11, 12],
    "bayati":   [0, 1.5, 3, 5, 7, 8, 10, 12],
    "ajam":     [0, 2, 4, 5, 7, 9, 11, 12],
}
MOODS = {
    #           maqam      tonic Hz  bpm  drums  pluck density
    "hijaz":    ("hijaz",    146.83, 72, False, 0.85),
    "nahawand": ("nahawand", 130.81, 64, False, 0.75),
    "bayati":   ("bayati",   146.83, 76, True,  0.85),
    "ajam":     ("ajam",     174.61, 96, True,  0.85),
}


def pluck(freq, dur, bright=0.5):
    n = int(SR * dur)
    p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p) * (0.6 + 0.4 * bright)
    out = np.zeros(n)
    decay = 0.996 - 0.004 * (freq / 600)
    for i in range(n):
        out[i] = buf[i % p]
        j = i % p
        buf[j] = decay * 0.5 * (buf[j] + buf[(j + 1) % p])
    env = np.minimum(1, np.arange(n) / (0.004 * SR))
    return out * env


def drone(freq, dur):
    t = np.arange(int(SR * dur)) / SR
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.12 * t)
    s = (np.sin(2 * np.pi * freq / 2 * t) * 0.5 + np.sin(2 * np.pi * freq * t) * 0.25
         + np.sin(2 * np.pi * freq * 1.5 * t) * 0.12)
    return s * lfo


def drum(kind, dur=0.35):
    n = int(SR * dur)
    t = np.arange(n) / SR
    if kind == "dum":
        f = 90 * np.exp(-t * 18) + 55
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    else:  # tak
        s = rng.uniform(-1, 1, n) * np.exp(-t * 45) * 0.6
        s += np.sin(2 * np.pi * 420 * t) * np.exp(-t * 30) * 0.3
    return s


def mix_in(track, sig, start, gain=1.0):
    i = int(start * SR)
    if i >= len(track):
        return
    j = min(len(track), i + len(sig))
    track[i:j] += sig[: j - i] * gain


def melody(scale, tonic, beat, total, density):
    notes = []
    t, deg = beat * 2, 0
    while t < total - beat * 2:
        phrase = rng.integers(4, 8)
        for _ in range(phrase):
            if rng.random() < density:
                step = rng.choice([-2, -1, -1, 0, 1, 1, 2])
                deg = int(np.clip(deg + step, 0, len(scale) - 1))
                octave = 2 if rng.random() < 0.15 else 1
                f = tonic * octave * 2 ** (scale[deg] / 12)
                dur = beat * rng.choice([1, 1, 2])
                notes.append((t, f, dur * 3))
                # oud tremolo on long notes
                if dur > beat and rng.random() < 0.3:
                    for k in range(1, 4):
                        notes.append((t + k * beat / 4, f, beat))
                t += dur
            else:
                t += beat
        deg = 0 if rng.random() < 0.5 else deg  # resolve to tonic often
        notes.append((t, tonic, beat * 4))
        t += beat * 2
    return notes


def render(mood, total, seed=7):
    global rng
    rng = np.random.default_rng(seed)
    maqam, tonic, bpm, drums, density = MOODS[mood]
    scale = MAQAM[maqam]
    beat = 60 / bpm
    track = np.zeros(int(SR * (total + 2)))
    mix_in(track, drone(tonic, total + 2), 0, 0.10)
    for (t, f, d) in melody(scale, tonic, beat, total, density):
        mix_in(track, pluck(f, min(d, 2.5)), t, 0.32)
    if drums:
        # maqsum: dum tak . tak dum . tak .
        pat = [("dum", 0), ("tak", 1), ("tak", 2.5), ("dum", 3), ("tak", 4.5)]
        bar = beat * 4
        t = beat * 4
        while t < total - bar:
            for k, off in pat:
                mix_in(track, drum(k), t + off * beat / 1.25, 0.22 if k == "dum" else 0.12)
            t += bar
    track = track[: int(SR * total)]
    # gentle low-pass + fades + normalise
    k = np.ones(6) / 6
    track = np.convolve(track, k, mode="same")
    fi, fo = int(SR * 1.0), int(SR * 1.5)
    track[:fi] *= np.linspace(0, 1, fi)
    track[-fo:] *= np.linspace(1, 0, fo)
    track /= max(1e-9, np.max(np.abs(track)))
    return (track * 0.8 * 32767).astype(np.int16)


def main():
    mood, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    data = render(mood, secs, seed)
    stereo = np.repeat(data[:, None], 2, axis=1)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(stereo.tobytes())


if __name__ == "__main__":
    main()
