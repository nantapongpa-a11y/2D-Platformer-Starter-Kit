#!/usr/bin/env python3
"""
Generate the original assets for "Nanta and the Wind Feather".

Created by 673380313-3 Nantapong Payakmaroeng for Lab 4 (Computer Game Development).

Outputs:
  Assets/Spritesheet/hero_nanta.png   - player texture (same part layout as student_thai.png,
                                        so the Skeleton2D rig in Scenes/Sprites/student.tscn still fits)
  Assets/Spritesheet/wind_feather.png - Wind Feather power-up item (64x64)
  Assets/Sound/bgm_wind_feather.ogg   - chiptune background music (composed note by note below)
  Assets/Sound/FX/powerup.wav         - sound effect when the Wind Feather is collected

Usage (from the project root):
  python scripts/make_assets.py
Requires Pillow, numpy and ffmpeg (for the .ogg conversion).
"""
import re
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SS = 4  # supersampling factor for smooth drawing


# ---------------------------------------------------------------- character --

def read_part_polygons():
    """Read the UV polygon of each body part from the existing rig."""
    text = (ROOT / "Scenes/Sprites/student.tscn").read_text(encoding="utf8")
    parts = {}
    for m in re.finditer(r'\[node name="(\w+)" type="Polygon2D".*?\n(.*?)\n\n', text, re.S):
        body = m.group(2)
        if 'ExtResource("1_jda5o")' not in body:
            continue  # skip the wand, it has its own texture
        uv = re.search(r"uv = PackedVector2Array\((.*?)\)", body).group(1)
        v = [float(x) for x in uv.split(",")]
        parts[m.group(1)] = list(zip(v[0::2], v[1::2]))
    return parts


def part_mask(poly, size, grow=0):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon([(x * SS, y * SS) for x, y in poly], fill=255)
    if grow:
        mask = mask.filter(ImageFilter.MaxFilter(grow * SS * 2 + 1))
    return mask


def S(*xy):
    """Scale coordinates to the supersampled canvas."""
    return [v * SS for v in xy]


ROBE = (52, 86, 178)
ROBE_DARK = (34, 58, 128)
ROBE_LIGHT = (92, 132, 220)
GOLD = (250, 200, 60)
SCARF = (220, 60, 60)
SKIN = (255, 214, 172)
SKIN_DARK = (230, 170, 130)
HAIR = (70, 44, 30)
PANTS = (110, 76, 50)
BOOT = (170, 50, 40)
OUTLINE = (24, 22, 40, 255)


def draw_head(d):
    d.rectangle(S(0, -4, 100, 82), fill=ROBE)                     # hood
    d.ellipse(S(8, -6, 60, 30), fill=ROBE_LIGHT)                   # hood highlight
    d.ellipse(S(30, 22, 86, 78), fill=ROBE_DARK)                   # hood rim
    d.ellipse(S(34, 26, 82, 74), fill=SKIN)                        # face
    d.ellipse(S(34, 26, 82, 74), outline=GOLD, width=2 * SS)       # golden hood trim
    # hair fringe (bangs)
    d.polygon(S(36, 40, 42, 28, 58, 24, 76, 28, 82, 40, 76, 36, 72, 42, 66, 35, 60, 41,
                54, 34, 48, 41, 43, 35), fill=HAIR)
    # big eye looking right
    d.ellipse(S(61, 43, 73, 59), fill=(255, 255, 255))
    d.ellipse(S(65, 45, 73, 58), fill=(30, 40, 90))
    d.ellipse(S(68, 47, 71, 51), fill=(255, 255, 255))
    d.line(S(60, 41, 73, 40), fill=HAIR, width=2 * SS)            # eyebrow
    d.ellipse(S(52, 58, 62, 65), fill=(255, 150, 150))            # cheek blush
    d.line(S(66, 67, 72, 66), fill=(150, 60, 60), width=SS * 2)   # smile
    # gold star on the hood
    cx, cy, r1, r2 = 24, 22, 9, 4
    pts = []
    for i in range(10):
        a = -np.pi / 2 + i * np.pi / 5
        r = r1 if i % 2 == 0 else r2
        pts += [cx + r * np.cos(a), cy + r * np.sin(a)]
    d.polygon(S(*pts), fill=GOLD)


def draw_body(d):
    d.rectangle(S(40, 70, 104, 136), fill=ROBE)
    d.rectangle(S(40, 70, 60, 136), fill=ROBE_DARK)               # back shading
    d.rectangle(S(40, 106, 104, 113), fill=GOLD)                  # belt
    d.rectangle(S(70, 105, 78, 114), fill=(255, 240, 150))        # buckle
    d.rectangle(S(40, 122, 104, 136), fill=ROBE_LIGHT)            # robe hem
    d.line(S(40, 122, 104, 122), fill=GOLD, width=2 * SS)
    d.rectangle(S(40, 74, 104, 86), fill=SCARF)                   # scarf
    d.polygon(S(48, 82, 60, 82, 58, 104, 46, 100), fill=SCARF)    # scarf tail
    d.line(S(48, 96, 58, 98), fill=(170, 40, 40), width=SS)


def draw_front_arm(d):
    d.rectangle(S(100, 80, 126, 110), fill=ROBE)
    d.rectangle(S(100, 98, 126, 110), fill=ROBE_DARK)
    d.rectangle(S(124, 80, 129, 110), fill=GOLD)                  # cuff
    d.ellipse(S(127, 82, 140, 102), fill=SKIN)                    # hand


def draw_back_arm(d):
    d.rectangle(S(4, 80, 42, 125), fill=ROBE_DARK)
    d.line(S(14, 118, 30, 98), fill=GOLD, width=3 * SS)           # cuff
    d.ellipse(S(4, 104, 20, 122), fill=SKIN_DARK)                 # hand


def draw_leg(d):
    d.rectangle(S(28, 120, 62, 143), fill=PANTS)
    d.rectangle(S(28, 143, 62, 158), fill=BOOT)
    d.rectangle(S(28, 152, 62, 158), fill=(60, 30, 25))           # sole
    d.line(S(34, 145, 46, 145), fill=(230, 110, 90), width=SS)    # boot shine


def make_hero():
    src = Image.open(ROOT / "Assets/Spritesheet/student_thai.png")
    w, h = src.size
    big = (w * SS, h * SS)
    out = Image.new("RGBA", big, (0, 0, 0, 0))
    painters = {
        "head": draw_head, "body": draw_body, "LArm": draw_front_arm,
        "RArm": draw_back_arm, "LLeg": draw_leg, "RLeg": draw_leg,
    }
    polys = read_part_polygons()
    order = ["RArm", "body", "LLeg", "RLeg", "LArm", "head"]
    for name in order:
        layer = Image.new("RGBA", big, (0, 0, 0, 0))
        painters[name](ImageDraw.Draw(layer))
        out.paste(layer, (0, 0), part_mask(polys[name], big, grow=1))
    out = out.resize((w, h), Image.LANCZOS)

    # dark outline on the edge of every part
    px = out.load()
    for name in order:
        m = part_mask(polys[name], big).resize((w, h), Image.LANCZOS).point(lambda v: 255 if v > 127 else 0)
        edge = Image.eval(m.filter(ImageFilter.MinFilter(3)), lambda v: 255 - v)
        edge = Image.composite(m, Image.new("L", (w, h), 0), edge)
        e = edge.load()
        for y in range(h):
            for x in range(w):
                if e[x, y]:
                    px[x, y] = OUTLINE
    path = ROOT / "Assets/Spritesheet/hero_nanta.png"
    out.save(path)
    print("saved", path)


# ---------------------------------------------------------------- item -------

def make_feather():
    n = 64 * SS
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # wind swirls
    for i, (r, a0) in enumerate([(22, 200), (17, 20), (12, 140)]):
        d.arc(S(32 - r, 32 - r, 32 + r, 32 + r), a0, a0 + 110, fill=(140, 230, 255, 200), width=2 * SS)
    # feather vane (rotated ellipse)
    vane = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vane)
    vd.ellipse(S(22, 6, 42, 52), fill=(30, 60, 110, 255))
    vd.ellipse(S(24, 8, 40, 50), fill=(235, 250, 255, 255))
    vd.ellipse(S(26, 12, 32, 46), fill=(170, 225, 255, 255))
    for y in range(14, 48, 6):  # little cuts in the vane
        vd.line(S(40, y, 34, y + 3), fill=(30, 60, 110, 255), width=SS)
        vd.line(S(24, y + 2, 29, y + 5), fill=(30, 60, 110, 255), width=SS)
    vd.line(S(32, 10, 32, 60), fill=GOLD + (255,), width=2 * SS)  # quill
    vane = vane.rotate(-35, resample=Image.BICUBIC, center=(n / 2, n / 2))
    img.alpha_composite(vane)
    img = img.resize((64, 64), Image.LANCZOS)
    path = ROOT / "Assets/Spritesheet/wind_feather.png"
    img.save(path)
    print("saved", path)


# ---------------------------------------------------------------- music ------

RATE = 22050
NOTE_INDEX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
              "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def freq(name):
    note, octave = name[:-1], int(name[-1])
    midi = 12 * (octave + 1) + NOTE_INDEX[note]
    return 440.0 * 2 ** ((midi - 69) / 12)


def square(f, dur, duty=0.5, vol=0.2):
    t = np.arange(int(RATE * dur)) / RATE
    wave_ = np.where((t * f) % 1.0 < duty, 1.0, -1.0)
    env = np.minimum(1.0, t / 0.01) * np.exp(-t * 3.0)
    return wave_ * env * vol


def triangle(f, dur, vol=0.25):
    t = np.arange(int(RATE * dur)) / RATE
    wave_ = 2 * np.abs(2 * ((t * f) % 1.0) - 1) - 1
    env = np.minimum(1.0, t / 0.005) * np.where(t > dur * 0.8, 0.3, 1.0)
    return wave_ * env * vol


def noise(dur, decay, vol):
    t = np.arange(int(RATE * dur)) / RATE
    return np.random.uniform(-1, 1, t.size) * np.exp(-t * decay) * vol


def kick(vol=0.5):
    t = np.arange(int(RATE * 0.15)) / RATE
    f = 120 * np.exp(-t * 25) + 40
    return np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 18) * vol


# Melody of "Wind Feather" - (note, length in eighth notes); "R" = rest
MELODY = [
    # A section: Am F C G | Am F C G
    [("A4", 2), ("C5", 1), ("E5", 1), ("D5", 2), ("C5", 2)],
    [("A4", 2), ("F4", 1), ("A4", 1), ("C5", 4)],
    [("G4", 2), ("C5", 1), ("E5", 1), ("G5", 2), ("E5", 2)],
    [("D5", 3), ("B4", 1), ("G4", 4)],
    [("A4", 1), ("C5", 1), ("E5", 2), ("A5", 2), ("G5", 2)],
    [("F5", 2), ("E5", 1), ("D5", 1), ("C5", 4)],
    [("E5", 2), ("D5", 1), ("C5", 1), ("D5", 2), ("E5", 2)],
    [("D5", 2), ("C5", 1), ("B4", 1), ("A4", 4)],
    # B section: F G Em Am | F G C E
    [("C5", 1), ("C5", 1), ("F5", 2), ("F5", 1), ("E5", 1), ("D5", 2)],
    [("D5", 1), ("D5", 1), ("G5", 2), ("G5", 1), ("F5", 1), ("E5", 2)],
    [("E5", 2), ("G5", 2), ("B5", 2), ("G5", 2)],
    [("A5", 4), ("E5", 4)],
    [("F5", 2), ("E5", 2), ("D5", 2), ("C5", 2)],
    [("D5", 2), ("E5", 2), ("F5", 2), ("D5", 2)],
    [("E5", 2), ("G5", 2), ("C6", 4)],
    [("B5", 2), ("G#5", 2), ("E5", 4)],
]
CHORDS = [
    ["A", "C", "E"], ["F", "A", "C"], ["C", "E", "G"], ["G", "B", "D"],
    ["A", "C", "E"], ["F", "A", "C"], ["C", "E", "G"], ["G", "B", "D"],
    ["F", "A", "C"], ["G", "B", "D"], ["E", "G", "B"], ["A", "C", "E"],
    ["F", "A", "C"], ["G", "B", "D"], ["C", "E", "G"], ["E", "G#", "B"],
]


def make_music():
    bpm = 140
    eighth = 60 / bpm / 2
    bar = eighth * 8
    loops = 2
    total = np.zeros(int(RATE * bar * len(MELODY) * loops) + RATE)

    def put(sig, start):
        i = int(start * RATE)
        total[i:i + sig.size] += sig[: max(0, total.size - i)]

    for loop in range(loops):
        for b, (notes, chord) in enumerate(zip(MELODY, CHORDS)):
            t0 = (loop * len(MELODY) + b) * bar
            # lead
            t = t0
            for name, length in notes:
                if name != "R":
                    put(square(freq(name), eighth * length * 0.95, 0.5, 0.16), t)
                t += eighth * length
            # bass: root, octave jumping on eighth notes
            root = chord[0]
            for i in range(8):
                put(triangle(freq(root + ("2" if i % 2 == 0 else "3")), eighth * 0.9), t0 + i * eighth)
            # soft arpeggio on sixteenth notes
            for i in range(16):
                put(square(freq(chord[i % 3] + "4"), eighth / 2 * 0.9, 0.25, 0.05), t0 + i * eighth / 2)
            # drums
            for beat in range(4):
                bt = t0 + beat * eighth * 2
                put(kick() if beat % 2 == 0 else noise(0.12, 25, 0.25), bt)
                put(noise(0.04, 80, 0.06), bt + eighth)

    total /= max(1.0, np.abs(total).max() / 0.9)
    wav_path = ROOT / "Assets/Sound/bgm_wind_feather.wav"
    write_wav(wav_path, total)
    ogg_path = wav_path.with_suffix(".ogg")
    if shutil.which("ffmpeg"):
        # mono, bitrate under 100 kbps as required in the lab sheet
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
                        "-ac", "1", "-c:a", "libvorbis", "-b:a", "80k", str(ogg_path)], check=True)
        wav_path.unlink()
        print("saved", ogg_path)
    else:
        print("ffmpeg not found, kept", wav_path)


def make_powerup_sfx():
    parts = []
    for i, n in enumerate(["C5", "E5", "G5", "C6", "E6", "G6"]):
        parts.append(square(freq(n), 0.06, 0.25, 0.35))
    sig = np.concatenate(parts + [square(freq("C7"), 0.25, 0.5, 0.3)])
    path = ROOT / "Assets/Sound/FX/powerup.wav"
    write_wav(path, sig)
    print("saved", path)


def write_wav(path, sig):
    data = (np.clip(sig, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    np.random.seed(673380313)
    make_hero()
    make_feather()
    make_music()
    make_powerup_sfx()
