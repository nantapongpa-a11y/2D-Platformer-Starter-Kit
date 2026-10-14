#!/usr/bin/env python3
"""
Music and sound effects for "Captain Go: Pirate Sea Adventure".

673380313-3 Nantapong Payakmaroeng - Lab 4 Computer Game Development

All three songs are composed note by note in this file and rendered with a small
synthesizer (fiddle, accordion, bass, drums, ocean waves). Run from the project root:

    python scripts/make_music.py

Output:
  Assets/Sound/captain_go_theme.ogg    - start screen / story (sea shanty, 6/8)
  Assets/Sound/sea_adventure.ogg       - levels 1-3 (pirate jig, 6/8)
  Assets/Sound/black_shark_battle.ogg  - level 4 boss fight (4/4)
  Assets/Sound/FX/sea_*.wav            - sound effects
Requires numpy, scipy and ffmpeg (for .ogg).
"""
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter

ROOT = Path(__file__).resolve().parent.parent
RATE = 32000
rng = np.random.default_rng(6733803133)

NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi(name):
    return 12 * (int(name[-1]) + 1) + NOTE[name[:-1]]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def chord_notes(ch, octave=4):
    root = ch[:2] if len(ch) > 1 and ch[1] == "#" else ch[:1]
    minor = ch[len(root):].startswith("m")
    r = 12 * (octave + 1) + NOTE[root]
    return [r, r + (3 if minor else 4), r + 7]


# ------------------------------------------------------------- synth parts --

def lowpass(x, cutoff, order=2):
    b, a = butter(order, cutoff / (RATE / 2), "low")
    return lfilter(b, a, x)


def highpass(x, cutoff, order=2):
    b, a = butter(order, cutoff / (RATE / 2), "high")
    return lfilter(b, a, x)


def env(n, a=0.01, d=0.08, s=0.7, r=0.06):
    t = np.arange(n) / RATE
    dur = n / RATE
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((dur - t) / max(r, 1e-4), 0, 1)
    return e * rel


def additive(f, dur, amps, vib=0.0, vib_rate=5.5, detune=0.0):
    n = int(dur * RATE)
    t = np.arange(n) / RATE
    f = f * (1 + detune)
    vib_env = np.clip(t / 0.25, 0, 1) * vib
    phase = 2 * np.pi * f * t + (f * vib_env / vib_rate) * np.sin(2 * np.pi * vib_rate * t)
    out = np.zeros(n)
    for k, a in enumerate(amps, start=1):
        if a and k * f < RATE / 2.4:
            out += a * np.sin(k * phase)
    return out


SAW = [1 / k for k in range(1, 14)]
SQUARE = [1 / k if k % 2 else 0 for k in range(1, 14)]
REED = [1, 0.45, 0.6, 0.22, 0.35, 0.12, 0.2, 0.08, 0.1, 0.05]


def fiddle(m, dur, vol=0.25):
    x = additive(hz(m), dur, SAW, vib=0.007)
    return lowpass(x, 3800) * env(x.size, 0.03, 0.2, 0.75, 0.07) * vol


def accordion(m, dur, vol=0.12):
    x = additive(hz(m), dur, REED, vib=0.003, vib_rate=6) + additive(hz(m), dur, REED, detune=0.0025)
    return lowpass(x, 3000) * env(x.size, 0.025, 0.1, 0.85, 0.05) * vol


def square_lead(m, dur, vol=0.18):
    x = additive(hz(m), dur, SQUARE, vib=0.005)
    return lowpass(x, 4500) * env(x.size, 0.01, 0.15, 0.6, 0.05) * vol


def brass(m, dur, vol=0.12):
    x = additive(hz(m), dur, SAW)
    cutoff = 1200 + 2000 * np.exp(-np.arange(x.size) / RATE / 0.12)
    y = lowpass(x, 2600) * (0.6 + 0.4 * cutoff / 3200)
    return y * env(x.size, 0.02, 0.1, 0.7, 0.05) * vol


def pluck_bass(m, dur, vol=0.3):
    n = int(dur * RATE)
    x = additive(hz(m), dur, [1, 0.5, 0.33, 0.2, 0.12, 0.08])
    return x * np.exp(-np.arange(n) / RATE / 0.35) * env(n, 0.005, 1, 1, 0.03) * vol


def noise(dur):
    return rng.uniform(-1, 1, int(dur * RATE))


def kick(vol=0.55):
    n = int(0.22 * RATE)
    t = np.arange(n) / RATE
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 14) * vol


def bodhran(vol=0.35):
    n = int(0.25 * RATE)
    t = np.arange(n) / RATE
    f = 80 + 40 * np.exp(-t * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 12)
    return (body + lowpass(noise(0.25), 900) * np.exp(-t * 40) * 0.6) * vol


def snare(vol=0.3):
    n = int(0.18 * RATE)
    t = np.arange(n) / RATE
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (body * 0.5 + highpass(noise(0.18), 1500) * np.exp(-t * 22)) * vol


def hat(vol=0.08, length=0.05):
    t = np.arange(int(length * RATE)) / RATE
    return highpass(noise(length), 7000) * np.exp(-t * 60) * vol


def tambourine(vol=0.1):
    t = np.arange(int(0.12 * RATE)) / RATE
    jingle = highpass(noise(0.12), 5000) * (1 + 0.5 * np.sin(2 * np.pi * 70 * t))
    return jingle * np.exp(-t * 28) * vol


def timpani(m, vol=0.4):
    n = int(0.9 * RATE)
    t = np.arange(n) / RATE
    x = np.sin(2 * np.pi * hz(m) * t) + 0.4 * np.sin(2 * np.pi * hz(m) * 1.5 * t)
    return (x * np.exp(-t * 4) + lowpass(noise(0.9), 400) * np.exp(-t * 20)) * vol


def ocean(dur, vol=0.08):
    x = lowpass(noise(dur), 700)
    t = np.arange(x.size) / RATE
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / 6.5) ** 2
    return x * swell * vol / (np.abs(x).max() + 1e-9)


def reverb(x, seconds=1.4, wet=0.18):
    n = int(seconds * RATE)
    ir = noise(seconds) * np.exp(-np.arange(n) / RATE / (seconds / 5))
    ir = lowpass(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = fftconvolve(x, ir)[: x.size]
    return x + y * wet


class Track:
    def __init__(self, seconds):
        self.buf = np.zeros(int(seconds * RATE) + RATE * 3)

    def put(self, sig, at):
        i = int(at * RATE)
        end = min(self.buf.size, i + sig.size)
        self.buf[i:end] += sig[: end - i]

    def melody(self, notes, start, unit, inst, transpose=0, vol=None):
        t = start
        for name, length in notes:
            if name != "R":
                kw = {} if vol is None else {"vol": vol}
                self.put(inst(midi(name) + transpose, unit * length * 0.97, **kw), t)
            t += unit * length
        return t

    def render(self, path, wet=0.18):
        y = reverb(self.buf, wet=wet)
        nz = np.nonzero(np.abs(y) > 1e-4)[0]
        y = y[: nz[-1] + 1] if nz.size else y
        y = y / (np.abs(y).max() + 1e-9) * 0.89
        write_ogg(path, y)


def write_wav(path, sig):
    data = (np.clip(sig, -1, 1) * 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())


def write_ogg(path, sig):
    tmp = path.with_suffix(".tmp.wav")
    write_wav(tmp, sig)
    # mono and under 100 kbps, as the lab sheet asks
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-ac", "1",
                    "-c:a", "libvorbis", "-b:a", "80k", str(path)], check=True)
    tmp.unlink()
    print("saved", path.name, f"{sig.size / RATE:.1f}s")


# ------------------------------------------------------------------ songs ----

def captain_go_theme():
    """Start screen: a calm sea shanty in D minor, 6/8."""
    unit = 0.25
    bars = [
        ("Dm", [("D4", 2), ("A4", 1), ("A4", 2), ("F4", 1)]),
        ("Dm", [("D5", 3), ("C5", 2), ("A4", 1)]),
        ("C", [("G4", 2), ("C5", 1), ("C5", 2), ("E5", 1)]),
        ("C", [("G5", 3), ("E5", 3)]),
        ("Dm", [("F5", 2), ("E5", 1), ("D5", 2), ("A4", 1)]),
        ("Dm", [("F4", 2), ("A4", 1), ("D5", 3)]),
        ("A", [("E5", 2), ("C#5", 1), ("A4", 2), ("C#5", 1)]),
        ("A", [("E5", 6)]),
        ("F", [("F5", 2), ("F5", 1), ("E5", 2), ("D5", 1)]),
        ("F", [("C5", 3), ("A4", 3)]),
        ("C", [("E5", 2), ("E5", 1), ("D5", 2), ("C5", 1)]),
        ("C", [("G4", 3), ("C5", 3)]),
        ("Dm", [("D5", 2), ("E5", 1), ("F5", 2), ("A5", 1)]),
        ("A", [("G5", 2), ("F5", 1), ("E5", 2), ("C#5", 1)]),
        ("Dm", [("D5", 6)]),
        ("Dm", [("R", 3), ("A4", 3)]),
    ]
    bar = unit * 6
    loops = 2
    total = bar * len(bars) * loops + bar
    tr = Track(total)
    tr.put(ocean(total + 2, 0.05), 0)
    t0 = bar  # one bar of waves first
    for loop in range(loops):
        for b, (ch, notes) in enumerate(bars):
            t = t0 + (loop * len(bars) + b) * bar
            tr.melody(notes, t, unit, fiddle if loop else accordion, vol=0.24 if loop else 0.2)
            if loop:
                tr.melody(notes, t, unit, accordion, transpose=-12, vol=0.08)
            cn = chord_notes(ch, 3)
            tr.put(pluck_bass(cn[0] - 12, unit * 2.8), t)
            tr.put(pluck_bass(cn[2] - 12, unit * 2.8, 0.22), t + unit * 3)
            for k in (1, 2, 4, 5):
                for m in cn:
                    tr.put(accordion(m + 12, unit * 0.8, 0.045), t + unit * k)
            tr.put(bodhran(0.25), t)
            tr.put(bodhran(0.15), t + unit * 3)
            for k in range(6):
                tr.put(hat(0.03), t + unit * k)
    tr.render(ROOT / "Assets/Sound/captain_go_theme.ogg", wet=0.25)


def sea_adventure():
    """Levels 1-3: a lively pirate jig in G major, 6/8."""
    unit = 0.17
    a_part = [
        ("G", [("G4", 1), ("B4", 1), ("D5", 1), ("G5", 2), ("D5", 1)]),
        ("G", [("B4", 1), ("D5", 1), ("B4", 1), ("G4", 3)]),
        ("C", [("E5", 1), ("D5", 1), ("C5", 1), ("E5", 2), ("G5", 1)]),
        ("D", [("F#5", 1), ("E5", 1), ("D5", 1), ("A4", 3)]),
        ("G", [("G4", 1), ("B4", 1), ("D5", 1), ("G5", 2), ("A5", 1)]),
        ("G", [("B5", 2), ("A5", 1), ("G5", 3)]),
        ("Am", [("A5", 1), ("G5", 1), ("E5", 1), ("C5", 2), ("E5", 1)]),
        ("D", [("D5", 3), ("F#5", 3)]),
        ("Em", [("G5", 1), ("F#5", 1), ("E5", 1), ("B4", 2), ("E5", 1)]),
        ("Em", [("G5", 2), ("F#5", 1), ("E5", 3)]),
        ("C", [("E5", 1), ("F#5", 1), ("G5", 1), ("C5", 2), ("E5", 1)]),
        ("D", [("D5", 1), ("E5", 1), ("F#5", 1), ("A5", 3)]),
        ("G", [("B5", 1), ("A5", 1), ("G5", 1), ("D5", 2), ("B4", 1)]),
        ("C", [("C5", 1), ("E5", 1), ("G5", 1), ("E5", 2), ("C5", 1)]),
        ("D", [("D5", 1), ("F#5", 1), ("A5", 1), ("F#5", 1), ("E5", 1), ("D5", 1)]),
        ("G", [("G5", 3), ("G4", 3)]),
    ]
    b_part = [
        ("C", [("E5", 2), ("G5", 1), ("C6", 2), ("G5", 1)]),
        ("C", [("E5", 1), ("G5", 1), ("E5", 1), ("C5", 3)]),
        ("G", [("D5", 2), ("G5", 1), ("B5", 2), ("G5", 1)]),
        ("G", [("D5", 1), ("G5", 1), ("D5", 1), ("B4", 3)]),
        ("Am", [("C5", 1), ("E5", 1), ("A5", 1), ("C6", 2), ("A5", 1)]),
        ("Am", [("E5", 1), ("A5", 1), ("E5", 1), ("C5", 3)]),
        ("D", [("D5", 1), ("F#5", 1), ("A5", 1), ("D6", 2), ("A5", 1)]),
        ("D", [("F#5", 1), ("E5", 1), ("D5", 1), ("A4", 3)]),
        ("Em", [("B4", 1), ("E5", 1), ("G5", 1), ("B5", 2), ("G5", 1)]),
        ("Em", [("E5", 1), ("G5", 1), ("E5", 1), ("B4", 3)]),
        ("C", [("C5", 1), ("E5", 1), ("G5", 1), ("C6", 2), ("B5", 1)]),
        ("C", [("A5", 1), ("G5", 1), ("E5", 1), ("G5", 3)]),
        ("Am", [("A5", 2), ("G5", 1), ("E5", 2), ("C5", 1)]),
        ("D", [("D5", 1), ("E5", 1), ("F#5", 1), ("A5", 2), ("F#5", 1)]),
        ("G", [("G5", 1), ("D5", 1), ("B4", 1), ("G4", 3)]),
        ("G", [("B4", 1), ("D5", 1), ("G5", 1), ("G5", 3)]),
    ]
    song = a_part + b_part
    bar = unit * 6
    loops = 2
    tr = Track(bar * len(song) * loops)
    for loop in range(loops):
        for b, (ch, notes) in enumerate(song):
            t = (loop * len(song) + b) * bar
            tr.melody(notes, t, unit, fiddle, vol=0.26)
            if loop == 1:
                tr.melody(notes, t, unit, accordion, transpose=-12, vol=0.09)
            cn = chord_notes(ch, 3)
            tr.put(pluck_bass(cn[0] - 12, unit * 2.6), t)
            tr.put(pluck_bass(cn[2] - 12, unit * 2.6, 0.24), t + unit * 3)
            for k in (1, 2, 4, 5):
                for m in cn:
                    tr.put(accordion(m + 12, unit * 0.7, 0.04), t + unit * k)
            tr.put(kick(0.4), t)
            tr.put(bodhran(0.22), t + unit * 3)
            for k in range(6):
                tr.put(tambourine(0.07 if k % 3 else 0.11), t + unit * k)
    tr.render(ROOT / "Assets/Sound/sea_adventure.ogg")


def black_shark_battle():
    """Level 4: boss fight against Captain Black Shark, E minor 4/4."""
    unit = 0.2
    song = [
        ("Em", [("E5", 1), ("E5", 1), ("B4", 1), ("E5", 1), ("G5", 2), ("F#5", 1), ("E5", 1)]),
        ("Em", [("D5", 2), ("B4", 2), ("E5", 4)]),
        ("C", [("C5", 1), ("E5", 1), ("G5", 1), ("C6", 1), ("B5", 2), ("G5", 2)]),
        ("D", [("A5", 1), ("F#5", 1), ("D5", 1), ("F#5", 1), ("A5", 4)]),
        ("Em", [("B5", 2), ("A5", 1), ("G5", 1), ("F#5", 2), ("E5", 2)]),
        ("Em", [("G5", 1), ("F#5", 1), ("E5", 1), ("D5", 1), ("E5", 4)]),
        ("C", [("E5", 1), ("G5", 1), ("C6", 2), ("B5", 1), ("A5", 1), ("G5", 2)]),
        ("B", [("F#5", 2), ("D#5", 2), ("B4", 4)]),
        ("Am", [("A4", 1), ("C5", 1), ("E5", 1), ("A5", 1), ("G5", 2), ("E5", 2)]),
        ("Am", [("C5", 2), ("E5", 2), ("A5", 4)]),
        ("Em", [("G5", 1), ("F#5", 1), ("E5", 1), ("B4", 1), ("E5", 2), ("G5", 2)]),
        ("Em", [("B5", 4), ("E5", 4)]),
        ("C", [("C6", 2), ("B5", 2), ("G5", 2), ("E5", 2)]),
        ("D", [("D6", 2), ("A5", 2), ("F#5", 2), ("D5", 2)]),
        ("B", [("D#5", 1), ("F#5", 1), ("B5", 1), ("F#5", 1), ("D#5", 2), ("B4", 2)]),
        ("B", [("B4", 2), ("D#5", 2), ("F#5", 4)]),
    ]
    bar = unit * 8
    loops = 2
    tr = Track(bar * len(song) * loops)
    for loop in range(loops):
        for b, (ch, notes) in enumerate(song):
            t = (loop * len(song) + b) * bar
            tr.melody(notes, t, unit, square_lead, vol=0.2)
            tr.melody(notes, t, unit, brass, transpose=-12, vol=0.08 if loop else 0.0)
            cn = chord_notes(ch, 3)
            for k in range(8):
                tr.put(pluck_bass(cn[0] - 12 + (12 if k % 2 else 0), unit * 0.9, 0.26), t + unit * k)
            for k in (0, 3, 6):
                for m in cn:
                    tr.put(brass(m + 12, unit * 1.2, 0.05), t + unit * k)
            if b % 4 == 0:
                tr.put(timpani(cn[0] - 12, 0.35), t)
            for k in range(8):
                if k in (0, 3, 4):
                    tr.put(kick(0.5), t + unit * k)
                if k in (2, 6):
                    tr.put(snare(0.32), t + unit * k)
                tr.put(hat(0.06), t + unit * k)
    tr.render(ROOT / "Assets/Sound/black_shark_battle.ogg", wet=0.12)


# ------------------------------------------------------------ sound effects --

def sweep(f0, f1, dur, amps=SQUARE, vol=0.5, curve=1.0):
    n = int(dur * RATE)
    t = np.arange(n) / RATE
    f = f0 + (f1 - f0) * (t / dur) ** curve
    phase = 2 * np.pi * np.cumsum(f) / RATE
    x = sum(a * np.sin(k * phase) for k, a in enumerate(amps, start=1) if a)
    return x * env(n, 0.005, 1, 1, 0.03) * vol


def bell(m, dur, vol=0.4):
    n = int(dur * RATE)
    t = np.arange(n) / RATE
    f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
    return x * np.exp(-t * 5) * vol


def make_sfx():
    fx = ROOT / "Assets/Sound/FX"

    def out(name, sig):
        sig = sig / (np.abs(sig).max() + 1e-9) * 0.85
        write_wav(fx / name, sig)
        print("saved", name)

    out("sea_jump.wav", sweep(320, 760, 0.14, vol=0.4, curve=0.6))
    c = np.zeros(int(0.45 * RATE))
    a, b = bell(midi("B5"), 0.1), bell(midi("E6"), 0.35)
    c[: a.size] += a
    c[int(0.08 * RATE): int(0.08 * RATE) + b.size] += b
    out("sea_coin.wav", c)
    out("sea_hurt.wav", sweep(420, 140, 0.28, vol=0.5) + lowpass(noise(0.28), 2000) * np.exp(-np.arange(int(0.28 * RATE)) / RATE * 12) * 0.3)
    fan = np.zeros(int(1.6 * RATE))
    for k, (n, t) in enumerate((("C5", 0), ("E5", 0.14), ("G5", 0.28), ("C6", 0.42))):
        s = brass(midi(n), 0.9 if k == 3 else 0.16, 0.5)
        i = int(t * RATE)
        fan[i:i + s.size] += s
    out("sea_level_complete.wav", fan)
    parts = [sweep(hz(midi(n)), hz(midi(n)) * 1.02, 0.06, vol=0.35) for n in ("C5", "E5", "G5", "C6", "E6", "G6")]
    out("sea_powerup.wav", np.concatenate(parts + [bell(midi("C7"), 0.4, 0.3)]))
    n = int(0.22 * RATE)
    out("sea_shoot.wav", sweep(900, 220, 0.22, amps=[1, 0.3], vol=0.5, curve=0.5) + highpass(noise(0.22), 3000) * np.exp(-np.arange(n) / RATE * 20) * 0.25)
    n = int(0.45 * RATE)
    t = np.arange(n) / RATE
    out("sea_enemy_defeat.wav", lowpass(noise(0.45), 1500) * np.exp(-t * 9) + sweep(500, 90, 0.45, vol=0.4))
    n = int(0.9 * RATE)
    t = np.arange(n) / RATE
    splash = lowpass(highpass(noise(0.9), 400), 4000) * np.exp(-t * 5) * (1 - np.exp(-t * 80))
    out("sea_splash.wav", splash)
    d = np.zeros(int(0.7 * RATE))
    for k, m in enumerate(("G5", "D6")):
        s = bell(midi(m), 0.5, 0.4)
        i = int(k * 0.15 * RATE)
        d[i:i + s.size] += s
    out("sea_checkpoint.wav", d)
    n = int(0.8 * RATE)
    t = np.arange(n) / RATE
    boom = np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-t * 18)) / RATE) * np.exp(-t * 6) + lowpass(noise(0.8), 900) * np.exp(-t * 8)
    out("sea_cannon.wav", boom)


if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required to write .ogg files")
    make_sfx()
    captain_go_theme()
    sea_adventure()
    black_shark_battle()
