#!/usr/bin/env python3
"""
Art generator for "Captain Go: Pirate Sea Adventure" (กัปตันโก้ ผจญภัยทะเลโจรสลัด).

673380313-3 Nantapong Payakmaroeng - Lab 4 Computer Game Development

Every picture used by the game (hero, pirates, tiles, items, traps, backgrounds, UI art)
is drawn by the code in this file. Run from the project root:

    python scripts/make_art.py

Requires Pillow and numpy.
"""
import math
import random
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Assets" / "Sea"
SS = 4  # draw 4x bigger, then shrink for smooth edges

OUTLINE = (28, 22, 36, 255)
GOLD = (246, 196, 58)
GOLD_DARK = (190, 130, 30)
SKIN = (255, 208, 160)
SKIN_DARK = (226, 160, 118)
WHITE = (250, 250, 245)
NAVY = (36, 58, 122)
NAVY_DARK = (24, 38, 84)
NAVY_LIGHT = (70, 104, 182)
HAT = (30, 30, 52)
RED = (206, 46, 52)
RED_DARK = (150, 30, 38)
WOOD = (150, 94, 50)
WOOD_DARK = (102, 60, 30)
WOOD_LIGHT = (196, 134, 78)


# ------------------------------------------------------------------ helpers --

def S(*xy):
    """Scale coordinates to the supersampled canvas."""
    return [v * SS for v in xy]


def new(w, h):
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def shrink(img):
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def outline(img, color=OUTLINE, size=1):
    """Add a dark outline around everything that is not transparent."""
    a = img.split()[3].point(lambda v: 255 if v > 90 else 0)
    grown = a.filter(ImageFilter.MaxFilter(size * 2 + 1))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", img.size, color), (0, 0), grown)
    out.alpha_composite(img)
    return out


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name)
    print("saved", name, img.size)


def vgradient(w, h, stops):
    """Vertical gradient. stops = [(pos 0..1, (r,g,b,a)), ...]"""
    ys = np.linspace(0, 1, h)
    arr = np.zeros((h, w, 4), dtype=np.float32)
    pos = [p for p, _ in stops]
    for c in range(4):
        vals = [col[c] for _, col in stops]
        arr[:, :, c] = np.interp(ys, pos, vals)[:, None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


def star_points(cx, cy, r1, r2, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        a = rot + i * math.pi / n
        r = r1 if i % 2 == 0 else r2
        pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
    return pts


def thick_line(d, pts, color, width):
    d.line(S(*pts), fill=color, width=int(width * SS), joint="curve")
    for x, y in zip(pts[0::2], pts[1::2]):
        r = width / 2
        d.ellipse(S(x - r, y - r, x + r, y + r), fill=color)


def anchor(d, cx, top, size, color, width):
    """Small anchor emblem."""
    s = size
    thick_line(d, [cx, top + s * 0.25, cx, top + s], color, width)
    thick_line(d, [cx - s * 0.3, top + s * 0.4, cx + s * 0.3, top + s * 0.4], color, width)
    d.arc(S(cx - s * 0.45, top + s * 0.45, cx + s * 0.45, top + s * 1.05), 20, 160, fill=color, width=int(width * SS))
    d.ellipse(S(cx - s * 0.13, top, cx + s * 0.13, top + s * 0.26), outline=color, width=int(width * SS * 0.8))


# ------------------------------------------------------------------- hero ----

def read_part_polygons():
    text = (ROOT / "Scenes/Sprites/student.tscn").read_text(encoding="utf8")
    parts = {}
    for m in re.finditer(r'\[node name="(\w+)" type="Polygon2D".*?\n(.*?)\n\n', text, re.S):
        body = m.group(2)
        if 'ExtResource("1_jda5o")' not in body:
            continue
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


def hero_head(d):
    d.rectangle(S(0, -4, 100, 82), fill=(70, 42, 28))               # hair base
    d.ellipse(S(34, 28, 86, 82), fill=SKIN)                          # face
    d.ellipse(S(38, 46, 50, 62), fill=SKIN_DARK)                     # ear
    d.ellipse(S(41, 50, 47, 58), fill=(240, 180, 140))
    d.polygon(S(30, 30, 48, 34, 44, 60, 32, 56), fill=(70, 42, 28))  # sideburn / hair
    # eye, brow, nose, grin
    d.ellipse(S(63, 45, 75, 60), fill=WHITE)
    d.ellipse(S(68, 47, 76, 59), fill=(60, 36, 20))
    d.ellipse(S(70, 49, 73, 52), fill=WHITE)
    thick_line(d, [60, 42, 70, 39, 78, 41], (60, 36, 22), 3)
    d.ellipse(S(78, 52, 88, 62), fill=SKIN)
    d.ellipse(S(54, 60, 63, 67), fill=(255, 150, 140))
    d.chord(S(64, 60, 80, 72), 10, 170, fill=(120, 40, 40))
    d.rectangle(S(67, 66, 76, 68), fill=WHITE)
    # captain tricorne hat
    d.rounded_rectangle(S(16, -8, 88, 28), radius=14 * SS, fill=HAT)
    d.ellipse(S(26, -6, 60, 12), fill=(56, 56, 86))                  # shine
    d.rectangle(S(16, 18, 88, 25), fill=GOLD)
    d.ellipse(S(2, 18, 100, 38), fill=HAT)                           # brim
    d.arc(S(2, 18, 100, 38), 0, 180, fill=GOLD, width=2 * SS)
    d.polygon(S(2, 30, 10, 8, 22, 26), fill=HAT)                     # turned up sides
    d.polygon(S(100, 30, 92, 8, 80, 26), fill=HAT)
    d.line(S(2, 30, 10, 8), fill=GOLD, width=2 * SS)
    d.line(S(100, 30, 92, 8), fill=GOLD, width=2 * SS)
    anchor(d, 52, -1, 18, GOLD, 2.4)
    d.polygon(S(*star_points(72, 6, 4, 2)), fill=WHITE)


def hero_body(d):
    d.rectangle(S(40, 70, 104, 136), fill=NAVY)
    d.rectangle(S(40, 70, 62, 136), fill=NAVY_DARK)
    d.polygon(S(74, 74, 100, 74, 88, 104), fill=WHITE)               # shirt
    for y in (82, 90, 98):
        d.arc(S(80, y - 4, 94, y + 4), 0, 180, fill=(210, 210, 220), width=SS)
    for y in (88, 97):
        d.ellipse(S(70, y - 3, 76, y + 3), fill=GOLD)
    d.rectangle(S(40, 104, 104, 114), fill=RED)                      # sash
    d.rectangle(S(40, 111, 104, 114), fill=RED_DARK)
    d.polygon(S(50, 110, 60, 110, 62, 128, 54, 126), fill=RED)       # sash knot tail
    d.rectangle(S(40, 114, 104, 136), fill=NAVY)
    d.rectangle(S(40, 114, 60, 136), fill=NAVY_DARK)
    d.line(S(40, 125, 104, 125), fill=GOLD, width=2 * SS)
    d.rounded_rectangle(S(84, 74, 104, 84), radius=3 * SS, fill=GOLD)  # epaulette
    for x in range(86, 104, 4):
        d.line(S(x, 84, x, 89), fill=GOLD_DARK, width=SS)


def hero_front_arm(d):
    d.rectangle(S(100, 80, 126, 110), fill=NAVY_LIGHT)
    d.rectangle(S(100, 98, 126, 110), fill=NAVY)
    d.rectangle(S(121, 80, 128, 110), fill=GOLD)
    d.ellipse(S(126, 82, 141, 103), fill=SKIN)
    d.ellipse(S(130, 86, 138, 98), fill=SKIN_DARK)


def hero_back_arm(d):
    d.rectangle(S(4, 80, 42, 125), fill=NAVY_DARK)
    thick_line(d, [14, 118, 30, 98], GOLD, 4)
    d.ellipse(S(4, 104, 20, 122), fill=SKIN_DARK)


def hero_leg(d):
    d.rectangle(S(28, 118, 62, 142), fill=(236, 226, 200))
    d.rectangle(S(28, 118, 36, 142), fill=(208, 196, 168))
    d.rectangle(S(28, 140, 62, 158), fill=(48, 34, 30))
    d.rectangle(S(28, 140, 62, 145), fill=(110, 70, 40))
    d.rectangle(S(40, 147, 48, 151), fill=GOLD)
    d.rectangle(S(28, 154, 62, 158), fill=(20, 14, 12))


def make_hero():
    src = Image.open(ROOT / "Assets/Spritesheet/student_thai.png")
    w, h = src.size
    big = (w * SS, h * SS)
    out = Image.new("RGBA", big, (0, 0, 0, 0))
    painters = {"head": hero_head, "body": hero_body, "LArm": hero_front_arm,
                "RArm": hero_back_arm, "LLeg": hero_leg, "RLeg": hero_leg}
    polys = read_part_polygons()
    order = ["RArm", "body", "LLeg", "RLeg", "LArm", "head"]
    for name in order:
        layer = Image.new("RGBA", big, (0, 0, 0, 0))
        painters[name](ImageDraw.Draw(layer))
        out.paste(layer, (0, 0), part_mask(polys[name], big, grow=1))
    out = shrink(out)
    px = out.load()
    for name in order:  # dark outline on the edge of every body part
        m = part_mask(polys[name], big).resize((w, h), Image.LANCZOS).point(lambda v: 255 if v > 127 else 0)
        edge = Image.composite(m, Image.new("L", (w, h), 0), Image.eval(m.filter(ImageFilter.MinFilter(3)), lambda v: 255 - v))
        e = edge.load()
        for y in range(h):
            for x in range(w):
                if e[x, y]:
                    px[x, y] = OUTLINE
    save(out, "captain_go.png")


def make_cutlass():
    img, d = new(64, 64)
    ox, oy = 11, 55
    ux, uy = 0.7071, -0.7071          # along the blade
    nx, ny = 0.7071, 0.7071           # across the blade

    def P(u, v):
        return ox + ux * u + nx * v, oy + uy * u + ny * v

    # blade with a little curve
    edge1, edge2 = [], []
    for i in range(21):
        u = 17 + i * 2.6
        bend = 0.0025 * (u - 17) ** 2
        width = 4.2 * (1 - i / 22) + 0.6
        edge1.append(P(u, -width + bend))
        edge2.append(P(u, width * 0.7 + bend))
    blade = edge1 + edge2[::-1]
    d.polygon(S(*sum(blade, ())), fill=(205, 214, 228))
    d.line(S(*sum(edge1, ())), fill=WHITE, width=2 * SS)
    d.line(S(*sum([P(18 + i * 2.5, 1 + 0.0025 * (i * 2.5) ** 2) for i in range(18)], ())), fill=(150, 160, 180), width=SS)
    # grip, guard and pommel
    thick_line(d, [*P(3, 0), *P(15, 0)], (90, 52, 28), 5)
    for u in (6, 9, 12):
        d.line(S(*P(u, -2.5), *P(u, 2.5)), fill=(60, 34, 18), width=SS)
    thick_line(d, [*P(16, -8), *P(16, 8)], GOLD, 3.5)
    thick_line(d, [*P(16, 7), *P(10, 9), *P(4, 7), *P(1, 2)], GOLD, 2)  # knuckle bow
    x, y = P(1, 0)
    d.ellipse(S(x - 3.5, y - 3.5, x + 3.5, y + 3.5), fill=GOLD)
    save(outline(shrink(img)), "cutlass.png")


def make_orbs():
    for name, inner, outer in (("water_orb.png", (200, 250, 255), (30, 140, 230)),
                               ("cannonball.png", (110, 110, 125), (25, 25, 32))):
        n = 64
        yy, xx = np.mgrid[0:n, 0:n]
        dist = np.sqrt((xx - 32) ** 2 + (yy - 32) ** 2) / 28
        hl = np.sqrt((xx - 24) ** 2 + (yy - 22) ** 2) / 28
        t = np.clip(hl, 0, 1)[..., None]
        rgb = np.array(inner) * (1 - t) + np.array(outer) * t
        alpha = np.clip((1 - dist) * 12, 0, 1) * 255
        if name == "water_orb.png":
            alpha = alpha * np.where(dist < 0.75, 0.85, 1.0)
        arr = np.dstack([rgb, alpha]).astype(np.uint8)
        img = Image.fromarray(arr, "RGBA")
        d = ImageDraw.Draw(img)
        d.ellipse((16, 12, 28, 22), fill=(255, 255, 255, 220))
        if name == "water_orb.png":
            d.arc((8, 8, 56, 56), 200, 260, fill=(255, 255, 255, 200), width=3)
            d.ellipse((40, 40, 46, 46), fill=(255, 255, 255, 160))
        save(img, name)


# ---------------------------------------------------------------- enemies ----

def frame_sheet(frames, w, h, name, scale_outline=1):
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.alpha_composite(outline(f, size=scale_outline), (i * w, 0))
    save(sheet, name)


def leg(d, hip, foot, color, boot, width=8):
    thick_line(d, [*hip, *foot], color, width)
    fx, fy = foot
    d.ellipse(S(fx - 9, fy - 5, fx + 5, fy + 4), fill=boot)


def pirate_grunt(i):
    img, d = new(96, 96)
    ph = i / 6 * 2 * math.pi
    sw = math.sin(ph) * 8
    bob = abs(math.sin(ph)) * 2
    # legs
    leg(d, (52, 66 - bob), (52 - sw, 89), (90, 60, 40), (40, 28, 24))
    # back arm
    thick_line(d, [58, 46 - bob, 66 + sw * 0.5, 60 - bob], (230, 180, 140), 6)
    # torso with stripes
    torso, td = new(96, 96)
    td.rectangle(S(0, 0, 96, 96), fill=WHITE)
    for k in range(7):
        y = 40 + k * 6 - bob
        td.rectangle(S(30, y, 70, y + 3), fill=RED)
    mask = Image.new("L", torso.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(S(34, 38 - bob, 66, 72 - bob), radius=12 * SS, fill=255)
    img.paste(torso, (0, 0), mask)
    d.rectangle(S(34, 63 - bob, 66, 68 - bob), fill=(70, 42, 24))
    d.rectangle(S(46, 62 - bob, 53, 69 - bob), fill=GOLD)
    leg(d, (44, 66 - bob), (44 + sw, 89), (110, 74, 48), (50, 34, 28))
    # head
    d.ellipse(S(28, 10 - bob, 62, 44 - bob), fill=SKIN)
    d.chord(S(30, 26 - bob, 60, 46 - bob), 0, 180, fill=(196, 150, 120))   # stubble
    d.ellipse(S(22, 24 - bob, 32, 33 - bob), fill=SKIN)                  # nose
    d.chord(S(26, 8 - bob, 64, 34 - bob), 180, 360, fill=RED)          # bandana
    d.rectangle(S(26, 20 - bob, 64, 23 - bob), fill=RED)
    for x, y in ((36, 14), (46, 12), (55, 16), (41, 19)):
        d.ellipse(S(x, y - bob, x + 3, y + 3 - bob), fill=WHITE)
    d.polygon(S(62, 18 - bob, 74, 14 - bob, 72, 24 - bob), fill=RED)    # knot
    d.polygon(S(62, 20 - bob, 72, 30 - bob, 66, 30 - bob), fill=RED_DARK)
    d.ellipse(S(32, 24 - bob, 38, 30 - bob), fill=(30, 20, 20))         # eye
    d.line(S(30, 21 - bob, 60, 26 - bob), fill=(20, 20, 20), width=SS)
    d.ellipse(S(43, 23 - bob, 51, 31 - bob), fill=(20, 20, 20))         # eye patch
    thick_line(d, [26, 35 - bob, 36, 33 - bob], (60, 36, 22), 2.5)       # moustache
    d.line(S(28, 39 - bob, 36, 38 - bob), fill=(120, 40, 40), width=SS)
    # front arm with cutlass
    thick_line(d, [40, 46 - bob, 26, 56 - bob], (230, 180, 140), 6)
    d.polygon(S(26, 56 - bob, 10, 28 - bob, 13, 26 - bob, 30, 52 - bob), fill=(205, 214, 228))
    thick_line(d, [22, 54 - bob, 32, 58 - bob], GOLD, 3)
    d.ellipse(S(22, 52 - bob, 30, 60 - bob), fill=SKIN)
    return shrink(img)


def crab(i):
    img, d = new(96, 96)
    ph = i / 6 * 2 * math.pi
    snap = (math.sin(ph * 2) + 1) * 0.5
    bob = abs(math.sin(ph)) * 2
    for k, x in enumerate((24, 34, 44, 54, 64, 72)):
        off = math.sin(ph + k) * 4
        thick_line(d, [x, 74 - bob, x - 6 + off, 90], (190, 60, 30), 4)
    # claws
    for cx, side in ((14, -1), (82, 1)):
        thick_line(d, [48 + side * 18, 66 - bob, cx, 48 - bob], (210, 70, 40), 6)
        d.ellipse(S(cx - 11, 32 - bob, cx + 11, 54 - bob), fill=(232, 88, 50))
        open_ = 10 * snap
        d.polygon(S(cx - 3, 36 - bob, cx + side * 2, 18 - bob - open_ * 0.3, cx + 6 * side, 36 - bob), fill=(232, 88, 50))
        d.polygon(S(cx - 8, 42 - bob, cx - 2, 40 - bob - open_ * 0.2, cx + 2, 46 - bob), fill=(255, 230, 210))
    d.ellipse(S(18, 50 - bob, 78, 84 - bob), fill=(222, 74, 44))       # shell
    d.ellipse(S(26, 54 - bob, 66, 70 - bob), fill=(246, 120, 80))
    d.chord(S(34, 64 - bob, 56, 78 - bob), 0, 180, fill=(120, 30, 30))  # mouth
    # little pirate hat on the shell
    d.chord(S(36, 40 - bob, 60, 62 - bob), 180, 360, fill=HAT)
    d.rectangle(S(32, 50 - bob, 64, 54 - bob), fill=HAT)
    d.ellipse(S(44, 42 - bob, 51, 48 - bob), fill=WHITE)
    for x in (34, 58):                                                  # eye stalks
        thick_line(d, [x, 56 - bob, x - 2, 38 - bob], (210, 70, 40), 4)
        d.ellipse(S(x - 9, 28 - bob, x + 5, 42 - bob), fill=WHITE)
        d.ellipse(S(x - 8, 32 - bob, x - 2, 39 - bob), fill=(20, 20, 30))
    return shrink(img)


def skeleton(i):
    img, d = new(96, 96)
    ph = i / 6 * 2 * math.pi
    sw = math.sin(ph) * 8
    bob = abs(math.sin(ph)) * 2
    bone = (236, 232, 214)
    shade = (180, 176, 160)
    leg(d, (52, 64 - bob), (52 - sw, 89), shade, (60, 40, 70), 5)
    thick_line(d, [56, 44 - bob, 66 + sw * 0.5, 58 - bob], shade, 4)
    # tattered purple vest and ribs
    d.polygon(S(36, 40 - bob, 64, 40 - bob, 62, 68 - bob, 38, 68 - bob), fill=(84, 52, 120))
    d.polygon(S(38, 68 - bob, 44, 62 - bob, 48, 70 - bob, 54, 62 - bob, 60, 70 - bob, 62, 68 - bob), fill=(84, 52, 120))
    d.rectangle(S(44, 42 - bob, 56, 64 - bob), fill=(30, 20, 40))
    for k in range(4):
        y = 44 + k * 5 - bob
        d.arc(S(42, y - 2, 58, y + 4), 180, 360, fill=bone, width=2 * SS)
    thick_line(d, [50, 42 - bob, 50, 66 - bob], bone, 3)
    leg(d, (44, 64 - bob), (44 + sw, 89), bone, (70, 46, 80), 5)
    # skull
    d.ellipse(S(30, 10 - bob, 62, 40 - bob), fill=bone)
    d.rounded_rectangle(S(32, 30 - bob, 52, 44 - bob), radius=4 * SS, fill=bone)
    d.ellipse(S(34, 20 - bob, 42, 29 - bob), fill=(30, 20, 30))
    d.ellipse(S(46, 20 - bob, 54, 29 - bob), fill=(30, 20, 30))
    d.ellipse(S(36, 23 - bob, 39, 26 - bob), fill=(255, 60, 60))
    d.ellipse(S(48, 23 - bob, 51, 26 - bob), fill=(255, 60, 60))
    d.polygon(S(30, 30 - bob, 34, 34 - bob, 30, 36 - bob), fill=(30, 20, 30))
    for x in range(34, 52, 4):
        d.line(S(x, 37 - bob, x, 43 - bob), fill=shade, width=SS)
    # black hat
    d.chord(S(30, 0 - bob, 64, 30 - bob), 180, 360, fill=HAT)
    d.ellipse(S(24, 10 - bob, 70, 20 - bob), fill=HAT)
    d.polygon(S(*star_points(47, 9 - bob, 4, 2)), fill=bone)
    # arm with rusty sword
    thick_line(d, [40, 44 - bob, 26, 54 - bob], bone, 4)
    d.polygon(S(26, 54 - bob, 8, 34 - bob, 11, 31 - bob, 30, 50 - bob), fill=(170, 120, 90))
    thick_line(d, [21, 52 - bob, 31, 56 - bob], (120, 90, 60), 3)
    return shrink(img)


def shark_boss(i):
    img, d = new(128, 144)
    ph = i / 6 * 2 * math.pi
    sw = math.sin(ph) * 10
    bob = abs(math.sin(ph)) * 3 - 16  # negative = whole body moved down to fit the hat
    skin = (96, 118, 150)
    belly = (220, 228, 236)
    # legs: boot and wooden peg
    thick_line(d, [72, 88 - bob, 72 - sw, 138], (60, 30, 30), 10)
    d.ellipse(S(60 - sw, 132, 78 - sw, 142), fill=(30, 20, 20))
    thick_line(d, [56, 88 - bob, 56 + sw, 138], (150, 100, 56), 6)
    # long red coat
    d.polygon(S(36, 50 - bob, 88, 50 - bob, 96, 100 - bob, 30, 100 - bob), fill=RED)
    d.polygon(S(62, 50 - bob, 88, 50 - bob, 96, 100 - bob, 66, 100 - bob), fill=RED_DARK)
    d.polygon(S(44, 50 - bob, 62, 50 - bob, 56, 86 - bob), fill=belly)
    for y in (60, 70, 80):
        d.ellipse(S(40, y - bob, 46, y + 6 - bob), fill=GOLD)
    d.rectangle(S(34, 84 - bob, 92, 91 - bob), fill=(40, 24, 18))
    d.rectangle(S(56, 82 - bob, 66, 93 - bob), fill=GOLD)
    # back arm with pistol
    thick_line(d, [86, 58 - bob, 98, 74 - bob], RED_DARK, 9)
    # shark head pointing left
    d.polygon(S(10, 44 - bob, 30, 16 - bob, 70, 8 - bob, 90, 22 - bob, 88, 54 - bob, 40, 60 - bob), fill=skin)
    d.polygon(S(10, 44 - bob, 40, 60 - bob, 80, 56 - bob, 60, 44 - bob, 30, 40 - bob), fill=belly)
    d.polygon(S(16, 40 - bob, 64, 40 - bob, 60, 52 - bob, 24, 50 - bob), fill=(120, 20, 30))   # mouth
    for x in range(18, 62, 6):
        d.polygon(S(x, 40 - bob, x + 3, 46 - bob, x + 6, 40 - bob), fill=WHITE)
        d.polygon(S(x + 2, 52 - bob, x + 5, 46 - bob, x + 8, 51 - bob), fill=WHITE)
    d.ellipse(S(34, 22 - bob, 46, 34 - bob), fill=WHITE)
    d.ellipse(S(36, 25 - bob, 43, 33 - bob), fill=(200, 20, 20))
    thick_line(d, [30, 20 - bob, 48, 24 - bob], (40, 50, 70), 3)                           # angry brow
    for x in (70, 75, 80):
        d.arc(S(x - 6, 26 - bob, x + 2, 44 - bob), 290, 70, fill=(60, 76, 100), width=SS * 2)
    # captain hat with feather
    d.polygon(S(104, 0 - bob, 120, -8 - bob, 96, 14 - bob), fill=(220, 40, 60))
    d.chord(S(36, -14 - bob, 96, 30 - bob), 180, 360, fill=HAT)
    d.ellipse(S(26, 2 - bob, 104, 16 - bob), fill=HAT)
    d.arc(S(26, 2 - bob, 104, 16 - bob), 0, 180, fill=GOLD, width=2 * SS)
    d.ellipse(S(60, -6 - bob, 72, 4 - bob), fill=WHITE)                                      # skull emblem
    d.ellipse(S(62, -3 - bob, 65, 0 - bob), fill=HAT)
    d.ellipse(S(67, -3 - bob, 70, 0 - bob), fill=HAT)
    # front arm with hook
    thick_line(d, [46, 58 - bob, 24, 72 - bob], RED, 9)
    d.rectangle(S(18, 66 - bob, 26, 78 - bob), fill=GOLD)
    d.arc(S(4, 62 - bob, 22, 82 - bob), 90, 330, fill=(200, 210, 222), width=3 * SS)
    return shrink(img)


def make_enemies():
    frame_sheet([pirate_grunt(i) for i in range(6)], 96, 96, "pirate_grunt.png")
    frame_sheet([crab(i) for i in range(6)], 96, 96, "pirate_crab.png")
    frame_sheet([skeleton(i) for i in range(6)], 96, 96, "pirate_skeleton.png")
    frame_sheet([shark_boss(i) for i in range(6)], 128, 144, "boss_black_shark.png")


# ------------------------------------------------------------------ items ----

def make_items():
    # gold doubloon
    img, d = new(64, 64)
    d.ellipse(S(8, 8, 56, 56), fill=GOLD_DARK)
    d.ellipse(S(11, 11, 53, 53), fill=GOLD)
    d.ellipse(S(17, 17, 47, 47), outline=GOLD_DARK, width=2 * SS)
    anchor(d, 32, 20, 22, GOLD_DARK, 3)
    d.arc(S(14, 14, 50, 50), 200, 250, fill=(255, 250, 210), width=3 * SS)
    save(outline(shrink(img)), "doubloon.png")

    # coconut drink (+HP)
    img, d = new(64, 64)
    thick_line(d, [40, 30, 50, 6], (255, 110, 170), 3.5)
    d.chord(S(10, 18, 54, 60), 0, 180, fill=(120, 72, 40))
    d.ellipse(S(10, 26, 54, 42), fill=WHITE)
    d.ellipse(S(14, 29, 50, 39), fill=(255, 245, 230))
    for k in range(6):
        x = 16 + k * 6
        d.line(S(x, 44, x + 3, 54), fill=(90, 50, 26), width=SS)
    for a in range(5):                                         # hibiscus flower
        ang = a * 2 * math.pi / 5
        x, y = 22 + 7 * math.cos(ang), 24 + 7 * math.sin(ang)
        d.ellipse(S(x - 5, y - 5, x + 5, y + 5), fill=(240, 60, 90))
    d.ellipse(S(19, 21, 25, 27), fill=(255, 220, 60))
    save(outline(shrink(img)), "coconut.png")

    # wind conch (speed + jump power-up)
    img, d = new(64, 64)
    for k, r in enumerate((26, 21, 16)):
        d.arc(S(32 - r, 32 - r, 32 + r, 32 + r), 200 + k * 50, 300 + k * 50, fill=(120, 230, 255), width=2 * SS)
    d.polygon(S(14, 46, 30, 12, 50, 22, 52, 44, 30, 54), fill=(255, 214, 196))
    d.polygon(S(30, 12, 50, 22, 40, 26), fill=(255, 170, 160))
    for k in range(4):
        y = 22 + k * 7
        d.arc(S(18 + k * 2, y, 52 - k, y + 12), 160, 350, fill=(230, 140, 140), width=SS * 2)
    d.ellipse(S(10, 42, 24, 56), fill=(255, 150, 160))
    save(outline(shrink(img)), "wind_conch.png")


# ------------------------------------------------------------------ traps ----

def make_traps():
    img, d = new(64, 64)
    for k in range(17):
        a = math.pi + k * math.pi / 16
        r = 30 if k % 2 == 0 else 24
        thick_line(d, [32, 46, 32 + r * math.cos(a), 46 + r * math.sin(a)], (60, 30, 80), 2.5)
    d.ellipse(S(16, 32, 48, 62), fill=(110, 50, 140))
    d.ellipse(S(22, 36, 36, 46), fill=(160, 90, 190))
    for x in (26, 38):
        d.ellipse(S(x - 3, 44, x + 3, 50), fill=WHITE)
        d.ellipse(S(x - 1, 46, x + 2, 50), fill=(20, 10, 20))
    save(outline(shrink(img)), "sea_urchin.png")

    img, d = new(96, 288)
    for k in range(13):                        # chain
        y = 4 + k * 16
        if k % 2 == 0:
            d.ellipse(S(40, y, 56, y + 20), outline=(110, 110, 120), width=3 * SS)
        else:
            d.rectangle(S(46, y, 50, y + 20), fill=(90, 90, 100))
    iron, dark = (80, 86, 100), (50, 54, 66)
    d.ellipse(S(36, 196, 60, 220), outline=iron, width=5 * SS)
    d.rectangle(S(42, 214, 54, 276), fill=iron)
    d.rounded_rectangle(S(22, 222, 74, 232), radius=4 * SS, fill=iron)
    d.arc(S(10, 228, 86, 284), 20, 160, fill=iron, width=9 * SS)
    d.polygon(S(6, 250, 20, 244, 16, 262), fill=iron)
    d.polygon(S(90, 250, 76, 244, 80, 262), fill=iron)
    d.line(S(44, 216, 44, 272), fill=dark, width=2 * SS)
    save(outline(shrink(img)), "anchor_trap.png")


# -------------------------------------------------------------- level props --

def make_props():
    # wooden door with ship wheel (level exit)
    img, d = new(96, 128)
    d.rounded_rectangle(S(6, 8, 90, 128), radius=40 * SS, fill=(74, 46, 28))
    d.rounded_rectangle(S(14, 16, 82, 128), radius=34 * SS, fill=WOOD)
    for x in (30, 48, 66):
        d.line(S(x, 18, x, 128), fill=WOOD_DARK, width=2 * SS)
    for y in (52, 100):
        d.rectangle(S(14, y, 82, y + 6), fill=(70, 70, 82))
    cx, cy = 48, 76
    d.ellipse(S(cx - 15, cy - 15, cx + 15, cy + 15), outline=GOLD, width=3 * SS)
    for k in range(8):
        a = k * math.pi / 4
        thick_line(d, [cx + 6 * math.cos(a), cy + 6 * math.sin(a), cx + 20 * math.cos(a), cy + 20 * math.sin(a)], GOLD, 2.5)
    d.ellipse(S(cx - 5, cy - 5, cx + 5, cy + 5), fill=GOLD)
    d.ellipse(S(70, 84, 76, 90), fill=GOLD)
    save(outline(shrink(img)), "door_ship.png")

    # treasure chest (final goal)
    img, d = new(112, 96)
    for k in range(18):
        x, y = random.Random(k).randint(22, 86), random.Random(k + 50).randint(20, 40)
        d.ellipse(S(x - 7, y - 7, x + 7, y + 7), fill=GOLD if k % 3 else (255, 250, 240))
    d.polygon(S(14, 40, 98, 40, 92, 10, 20, 10), fill=WOOD)
    d.rectangle(S(14, 44, 98, 92), fill=WOOD)
    d.rectangle(S(14, 44, 98, 54), fill=WOOD_DARK)
    for x in (22, 86):
        d.rectangle(S(x, 44, x + 6, 92), fill=GOLD)
    d.rectangle(S(50, 52, 62, 66), fill=GOLD)
    d.ellipse(S(53, 56, 59, 62), fill=(40, 20, 10))
    save(outline(shrink(img)), "treasure_chest.png")

    # checkpoint flags
    for name, flag in (("flag_off.png", (150, 150, 150)), ("flag_on.png", (40, 120, 220))):
        img, d = new(64, 128)
        d.rectangle(S(10, 6, 16, 128), fill=WOOD_DARK)
        d.ellipse(S(7, 2, 19, 12), fill=GOLD)
        d.polygon(S(16, 12, 60, 22, 52, 34, 60, 46, 16, 50), fill=flag)
        anchor(d, 34, 18, 22, WHITE, 2.5)
        save(outline(shrink(img)), name)

    # palm tree
    img, d = new(192, 320)
    pts = []
    for k in range(12):
        t = k / 11
        pts.append((96 + 30 * math.sin(t * 2.2) - 20 * t, 316 - t * 210))
    for k, (x, y) in enumerate(pts[:-1]):
        d.ellipse(S(x - 12, y - 16, x + 12, y + 6), fill=(150, 104, 60) if k % 2 else (128, 86, 48))
    tx, ty = pts[-1]
    for k, a in enumerate((-175, -140, -105, -75, -40, -5, 160, 20)):
        ang = math.radians(a)
        length = 92 if k % 2 else 80
        edge1, edge2 = [], []
        for j in range(13):
            t = j / 12
            x = tx + math.cos(ang) * length * t
            y = ty + math.sin(ang) * length * t * 0.7 + 46 * t * t   # droop
            wdt = 13 * math.sin(math.pi * min(1, t * 1.15))
            nx_, ny_ = -math.sin(ang), math.cos(ang)
            edge1.append((x + nx_ * wdt, y + ny_ * wdt * 0.6))
            edge2.append((x - nx_ * wdt, y - ny_ * wdt * 0.6))
        d.polygon(S(*sum(edge1 + edge2[::-1], ())), fill=(52, 160, 72) if k % 2 else (40, 136, 62))
        d.line(S(*sum([(tx + math.cos(ang) * length * t, ty + math.sin(ang) * length * t * 0.7 + 46 * t * t) for t in [j / 12 for j in range(13)]], ())), fill=(26, 100, 46), width=2 * SS)
    for dx in (-10, 6, -2):
        d.ellipse(S(tx + dx - 9, ty + 4, tx + dx + 9, ty + 22), fill=(110, 70, 30))
    save(outline(shrink(img)), "palm_tree.png")

    # pirate ship mast with black sail
    img, d = new(192, 400)
    d.rectangle(S(90, 0, 102, 400), fill=WOOD)
    d.rectangle(S(20, 60, 172, 70), fill=WOOD_DARK)
    d.polygon(S(26, 70, 166, 70, 176, 250, 16, 250), fill=(40, 40, 52))
    d.polygon(S(16, 250, 40, 236, 60, 252, 90, 238, 120, 252, 150, 238, 176, 250), fill=(0, 0, 0, 0))
    d.ellipse(S(76, 120, 116, 158), fill=WHITE)                          # skull
    d.rounded_rectangle(S(84, 150, 108, 168), radius=4 * SS, fill=WHITE)
    d.ellipse(S(82, 130, 94, 142), fill=(40, 40, 52))
    d.ellipse(S(98, 130, 110, 142), fill=(40, 40, 52))
    thick_line(d, [60, 176, 132, 206], WHITE, 7)
    thick_line(d, [132, 176, 60, 206], WHITE, 7)
    d.polygon(S(102, 0, 150, 12, 102, 24), fill=RED)
    d.rectangle(S(70, 30, 122, 40), fill=WOOD_DARK)                     # crow's nest
    save(outline(shrink(img)), "pirate_mast.png")

    # small decorations
    img, d = new(32, 48)
    thick_line(d, [16, 0, 16, 8], (60, 60, 60), 2)
    d.rounded_rectangle(S(6, 8, 26, 40), radius=5 * SS, fill=(60, 50, 40))
    d.rounded_rectangle(S(9, 12, 23, 36), radius=4 * SS, fill=(255, 210, 90))
    d.ellipse(S(12, 18, 20, 30), fill=(255, 250, 200))
    save(outline(shrink(img)), "lantern.png")

    img, d = new(128, 64)
    rnd = random.Random(7)
    for k in range(40):
        x, y = rnd.randint(10, 118), rnd.randint(28, 58)
        d.ellipse(S(x - 7, y - 4, x + 7, y + 4), fill=GOLD if k % 4 else (255, 250, 240))
    d.polygon(S(54, 30, 74, 30, 70, 12, 58, 12), fill=GOLD)
    d.polygon(S(*star_points(90, 22, 9, 4)), fill=(80, 200, 255))
    save(outline(shrink(img)), "treasure_pile.png")

    img, d = new(64, 80)
    d.rectangle(S(28, 30, 36, 80), fill=WOOD_DARK)
    d.polygon(S(4, 10, 52, 10, 62, 26, 52, 42, 4, 42), fill=WOOD)
    d.line(S(10, 26, 48, 26), fill=WOOD_DARK, width=3 * SS)
    d.polygon(S(48, 18, 56, 26, 48, 34), fill=WOOD_DARK)
    save(outline(shrink(img)), "signpost.png")


# ------------------------------------------------------------------ tiles ----

def tile_material(d, x0, y0, mat, top, left, right, rnd):
    def R(x1, y1, x2, y2, **kw):
        d.rectangle(S(x0 + x1, y0 + y1, x0 + x2, y0 + y2), **kw)

    if mat == "sand":
        body, dark, top_c, top_hl = (214, 168, 98), (190, 144, 80), (248, 218, 150), (255, 238, 190)
    elif mat == "wood":
        body, dark, top_c, top_hl = (140, 86, 46), (100, 60, 30), (190, 128, 72), (220, 160, 100)
    else:
        body, dark, top_c, top_hl = (86, 96, 116), (62, 70, 88), (60, 150, 112), (100, 196, 150)
    R(0, 0, 64, 64, fill=body)
    if mat == "wood":
        for y in (16, 32, 48):
            R(0, y, 64, y + 2, fill=dark)
        for k in range(4):
            yy = k * 16 + 8
            xx = (k * 23) % 48 + 8
            R(xx, yy - 6, xx + 2, yy + 6, fill=dark)
            d.ellipse(S(x0 + xx + 6, y0 + yy - 2, x0 + xx + 9, y0 + yy + 1), fill=(70, 70, 70))
    else:
        for _ in range(9):
            px, py = rnd.randint(4, 58), rnd.randint(top and 18 or 4, 58)
            r = rnd.randint(2, 5)
            d.ellipse(S(x0 + px - r, y0 + py - r * 0.7, x0 + px + r, y0 + py + r * 0.7), fill=dark)
        if mat == "sand" and rnd.random() < 0.4:
            sx, sy = rnd.randint(14, 48), rnd.randint(30, 52)
            d.chord(S(x0 + sx - 6, y0 + sy - 6, x0 + sx + 6, y0 + sy + 6), 180, 360, fill=(255, 190, 200))
        if mat == "rock":
            for _ in range(2):
                cx, cy = rnd.randint(8, 56), rnd.randint(20, 56)
                d.line(S(x0 + cx, y0 + cy, x0 + cx + 8, y0 + cy + 6, x0 + cx + 4, y0 + cy + 12), fill=(48, 54, 70), width=SS * 2)
    if left:
        R(0, 0, 5, 64, fill=dark)
    if right:
        R(59, 0, 64, 64, fill=dark)
    if top:
        R(0, 0, 64, 14, fill=top_c)
        R(0, 0, 64, 4, fill=top_hl)
        for k in range(8):                                            # wavy lower edge
            cx = k * 8 + 4
            d.ellipse(S(x0 + cx - 5, y0 + 9, x0 + cx + 5, y0 + 18), fill=top_c)
        if mat == "sand":
            for _ in range(2):
                gx = rnd.randint(8, 56)
                for dx in (-3, 0, 3):
                    d.line(S(x0 + gx, y0 + 10, x0 + gx + dx, y0 + 2), fill=(90, 170, 70), width=SS * 2)
        if mat == "rock":
            for _ in range(3):
                gx = rnd.randint(6, 58)
                d.ellipse(S(x0 + gx - 4, y0 + 10, x0 + gx + 4, y0 + 22), fill=(50, 130, 96))


def make_tiles():
    img, d = new(512, 256)
    rnd = random.Random(673380313)
    variants = [(1, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]
    for row, mat in enumerate(("sand", "wood", "rock")):
        for col, (top, left, right) in enumerate(variants):
            tile_material(d, col * 64, row * 64, mat, top, left, right, rnd)
    y0 = 192
    # 0: one-way plank
    d.rectangle(S(0, y0, 64, y0 + 16), fill=WOOD_LIGHT)
    d.rectangle(S(0, y0 + 12, 64, y0 + 16), fill=WOOD_DARK)
    d.rectangle(S(0, y0, 64, y0 + 3), fill=(236, 180, 120))
    for x in (8, 54):
        d.ellipse(S(x - 2, y0 + 6, x + 2, y0 + 10), fill=(70, 70, 70))
    # 1: crate
    x0 = 64
    d.rectangle(S(x0 + 2, y0 + 2, x0 + 62, y0 + 62), fill=(176, 120, 66))
    d.rectangle(S(x0 + 2, y0 + 2, x0 + 62, y0 + 62), outline=WOOD_DARK, width=5 * SS)
    d.line(S(x0 + 6, y0 + 6, x0 + 58, y0 + 58), fill=WOOD_DARK, width=5 * SS)
    d.line(S(x0 + 58, y0 + 6, x0 + 6, y0 + 58), fill=WOOD_DARK, width=5 * SS)
    # 2: barrel
    x0 = 128
    d.rounded_rectangle(S(x0 + 6, y0 + 2, x0 + 58, y0 + 64), radius=16 * SS, fill=(150, 90, 46))
    for y in (12, 50):
        d.rectangle(S(x0 + 6, y0 + y, x0 + 58, y0 + y + 5), fill=(80, 80, 92))
    for x in (20, 32, 44):
        d.line(S(x0 + x, y0 + 4, x0 + x, y0 + 62), fill=WOOD_DARK, width=SS)
    # 3: water surface, 4: deep water
    for k, (x0, top) in enumerate(((192, True), (256, False))):
        d.rectangle(S(x0, y0 + (14 if top else 0), x0 + 64, y0 + 64), fill=(30, 120, 210, 190))
        if top:
            for c in range(4):
                cx = x0 + c * 16 + 8
                d.ellipse(S(cx - 9, y0 + 6, cx + 9, y0 + 22), fill=(60, 160, 235, 220))
                d.arc(S(cx - 9, y0 + 6, cx + 9, y0 + 22), 200, 340, fill=(230, 250, 255, 255), width=2 * SS)
        else:
            d.line(S(x0 + 10, y0 + 20, x0 + 30, y0 + 20), fill=(90, 180, 240, 160), width=2 * SS)
            d.line(S(x0 + 34, y0 + 46, x0 + 56, y0 + 46), fill=(90, 180, 240, 160), width=2 * SS)
    # 5: rope rail (decoration)
    x0 = 320
    d.rectangle(S(x0 + 28, y0 + 20, x0 + 36, y0 + 64), fill=WOOD_DARK)
    d.arc(S(x0 - 32, y0 + 10, x0 + 32, y0 + 44), 0, 90, fill=(220, 190, 130), width=3 * SS)
    d.arc(S(x0 + 32, y0 + 10, x0 + 96, y0 + 44), 90, 180, fill=(220, 190, 130), width=3 * SS)
    # 6: coral, 7: seaweed (decoration)
    x0 = 384
    for (a, b, c, dd) in ((32, 64, 20, 30), (32, 50, 46, 26), (24, 40, 12, 26), (40, 40, 54, 20)):
        thick_line(d, [x0 + a, y0 + b, x0 + c, y0 + dd], (255, 110, 130), 6)
    x0 = 448
    for k in range(3):
        bx = x0 + 14 + k * 16
        pts = []
        for j in range(8):
            pts += [bx + math.sin(j * 1.1 + k) * 5, y0 + 64 - j * 7]
        thick_line(d, pts, (50, 150, 80), 5)
    save(outline(shrink(img), size=1) if False else shrink(img), "sea_tiles.png")


# ------------------------------------------------------------ backgrounds ----

def clouds(img, rnd, count, area, color=(255, 255, 255, 235), shadow=(210, 225, 240, 235)):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x1, y1, x2, y2 = area
    for _ in range(count):
        cx, cy = rnd.randint(x1, x2), rnd.randint(y1, y2)
        w = rnd.randint(90, 200)
        for k in range(6):
            ox = rnd.randint(-w // 2, w // 2)
            r = rnd.randint(26, 48)
            d.ellipse((cx + ox - r, cy - r + 10, cx + ox + r, cy + r + 10), fill=shadow)
        for k in range(6):
            ox = rnd.randint(-w // 2, w // 2)
            r = rnd.randint(22, 44)
            d.ellipse((cx + ox - r, cy - r, cx + ox + r, cy + r), fill=color)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(2)))


def make_backgrounds():
    rnd = random.Random(3)
    # day sky
    sky = vgradient(1600, 900, [(0, (60, 140, 226, 255)), (0.65, (150, 210, 245, 255)), (1, (220, 244, 255, 255))])
    glow = Image.new("RGBA", sky.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((1180, 80, 1420, 320), fill=(255, 250, 200, 140))
    sky.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    ImageDraw.Draw(sky).ellipse((1250, 150, 1350, 250), fill=(255, 250, 215, 255))
    clouds(sky, rnd, 9, (0, 60, 1600, 420))
    save(sky.convert("RGB"), "sky_day.png")

    # sunset sky
    sky = vgradient(1600, 900, [(0, (54, 40, 110, 255)), (0.45, (200, 90, 110, 255)), (0.75, (255, 160, 90, 255)), (1, (255, 214, 130, 255))])
    glow = Image.new("RGBA", sky.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((560, 380, 1040, 860), fill=(255, 220, 140, 150))
    sky.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    ImageDraw.Draw(sky).ellipse((720, 520, 880, 680), fill=(255, 236, 170, 255))
    clouds(sky, rnd, 8, (0, 80, 1600, 380), color=(255, 180, 170, 220), shadow=(150, 80, 130, 220))
    save(sky.convert("RGB"), "sky_sunset.png")

    # far sea with islands and a pirate ship (repeats every 1152 px)
    w, h, horizon = 1152, 648, 420
    far = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(far)
    for (cx, wid, hei) in ((160, 300, 90), (420, 180, 50), (860, 360, 120)):
        d.ellipse(S(cx - wid / 2, horizon - hei, cx + wid / 2, horizon + hei), fill=(70, 140, 130, 255))
        d.ellipse(S(cx - wid / 2 + 20, horizon - hei + 14, cx + wid / 2 - 30, horizon + hei), fill=(90, 160, 140, 255))
    for (px, py) in ((140, 330), (190, 340), (880, 300), (930, 310)):
        thick_line(d, [px, horizon - 10, px + 6, py], (50, 100, 90, 255), 5)
        for a in (-150, -110, -60, -20):
            ang = math.radians(a)
            d.line(S(px + 6, py, px + 6 + 34 * math.cos(ang), py + 22 * math.sin(ang) + 12), fill=(50, 110, 90, 255), width=5 * SS)
    # distant pirate ship
    sx, sy = 640, horizon - 4
    hull = (70, 46, 40, 255)
    d.polygon(S(sx - 70, sy - 20, sx + 62, sy - 20, sx + 48, sy, sx - 56, sy), fill=hull)
    d.polygon(S(sx - 70, sy - 20, sx - 84, sy - 30, sx - 64, sy - 26), fill=hull)
    d.line(S(sx + 62, sy - 20, sx + 92, sy - 34), fill=hull, width=2 * SS)
    for mx, mh in ((sx - 34, 74), (sx + 22, 88)):
        d.rectangle(S(mx - 1.5, sy - mh - 6, mx + 1.5, sy - 20), fill=hull)
        d.polygon(S(mx - 16, sy - mh, mx + 16, sy - mh, mx + 19, sy - mh + 26, mx - 19, sy - mh + 26), fill=(36, 36, 48, 255))
        d.polygon(S(mx - 18, sy - mh + 30, mx + 18, sy - mh + 30, mx + 21, sy - 26, mx - 21, sy - 26), fill=(36, 36, 48, 255))
        d.ellipse(S(mx - 4, sy - mh + 8, mx + 4, sy - mh + 16), fill=(225, 225, 225, 255))
    d.polygon(S(sx + 22, sy - 94, sx + 40, sy - 90, sx + 22, sy - 86), fill=(200, 40, 50, 255))
    far = shrink(far)
    sea = vgradient(w, h - horizon, [(0, (70, 160, 220, 255)), (1, (24, 86, 170, 255))])
    sd = ImageDraw.Draw(sea)
    for _ in range(90):
        x, y = rnd.randint(0, w - 30), rnd.randint(4, h - horizon - 4)
        ln = rnd.randint(8, 30)
        sd.line((x, y, x + ln, y), fill=(200, 235, 255, 150), width=2)
    far.alpha_composite(sea, (0, horizon))
    save(far, "far_sea.png")

    # waves strip (seamless)
    w, h = 1152, 160
    wv = vgradient(w, h, [(0, (40, 130, 210, 0)), (0.25, (40, 130, 210, 220)), (1, (20, 80, 160, 255))])
    d = ImageDraw.Draw(wv)
    for row, (y, amp, col) in enumerate(((40, 8, (230, 248, 255, 255)), (80, 6, (150, 210, 250, 200)), (118, 5, (120, 190, 240, 170)))):
        pts = [(x, y + amp * math.sin(x / w * 2 * math.pi * 16 + row)) for x in range(0, w + 1, 4)]
        d.line(pts, fill=col, width=3)
    save(wv, "waves.png")

    # cave background (repeats every 1152 px)
    w, h = 1152, 700
    cave = vgradient(w, h, [(0, (16, 18, 34, 255)), (1, (34, 46, 74, 255))])
    d = ImageDraw.Draw(cave)
    for x in range(0, w, 64):                                   # stalactites and stalagmites
        ln = rnd.randint(60, 180)
        d.polygon((x, 0, x + 64, 0, x + 32 + rnd.randint(-10, 10), ln), fill=(40, 46, 66))
        ln = rnd.randint(40, 140)
        d.polygon((x, h, x + 64, h, x + 32 + rnd.randint(-10, 10), h - ln), fill=(44, 52, 74))
    glow = Image.new("RGBA", cave.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    crystals = [(rnd.randint(40, w - 40), rnd.randint(220, 520)) for _ in range(14)]
    for (x, y) in crystals:
        gd.ellipse((x - 40, y - 40, x + 40, y + 40), fill=(80, 220, 255, 70))
    cave.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    for (x, y) in crystals:
        d.polygon((x, y - 18, x + 8, y, x, y + 14, x - 8, y), fill=(140, 240, 255))
        d.polygon((x, y - 18, x + 8, y, x, y), fill=(220, 255, 255))
    save(cave.convert("RGB"), "cave_bg.png")


# --------------------------------------------------------------- menu art ----

def make_menu_art():
    # Captain Go's ship
    img, d = new(440, 400)
    d.polygon(S(30, 300, 410, 300, 370, 370, 70, 370), fill=(120, 70, 36))
    d.polygon(S(30, 300, 410, 300, 404, 316, 36, 316), fill=WOOD_DARK)
    d.polygon(S(380, 300, 440, 270, 430, 290, 404, 316), fill=(120, 70, 36))
    d.line(S(36, 330, 396, 330), fill=GOLD, width=4 * SS)
    for x in range(90, 380, 52):
        d.ellipse(S(x - 9, 340, x + 9, 356), fill=(40, 30, 30))
        d.ellipse(S(x - 9, 340, x + 9, 356), outline=GOLD, width=2 * SS)
    for mx, top in ((130, 30), (300, 60)):
        d.rectangle(S(mx - 6, top, mx + 6, 300), fill=WOOD)
        d.polygon(S(mx - 70, top + 30, mx + 70, top + 30, mx + 78, top + 150, mx - 78, top + 150), fill=WHITE)
        d.polygon(S(mx - 64, top + 160, mx + 64, top + 160, mx + 70, top + 236, mx - 70, top + 236), fill=WHITE)
        d.line(S(mx - 78, top + 150, mx + 78, top + 150), fill=(200, 200, 210), width=3 * SS)
        anchor(d, mx, top + 52, 70, NAVY, 7)
        d.polygon(S(mx + 6, top, mx + 50, top + 12, mx + 6, top + 24), fill=(40, 120, 220))
    d.line(S(296, 60, 430, 276), fill=(220, 190, 130), width=2 * SS)
    d.line(S(130, 30, 30, 296), fill=(220, 190, 130), width=2 * SS)
    save(outline(shrink(img), size=2), "hero_ship.png")

    # pier where the captain stands
    img, d = new(460, 160)
    for x in range(30, 460, 70):
        d.rectangle(S(x, 30, x + 18, 160), fill=WOOD_DARK)
    d.rectangle(S(0, 18, 460, 44), fill=WOOD)
    d.rectangle(S(0, 18, 460, 24), fill=WOOD_LIGHT)
    for x in range(0, 460, 46):
        d.line(S(x, 18, x, 44), fill=WOOD_DARK, width=2 * SS)
    d.rounded_rectangle(S(380, -20, 420, 30), radius=8 * SS, fill=(150, 90, 46))
    save(outline(shrink(img), size=2), "pier.png")

    # title ribbon
    img, d = new(840, 190)
    d.polygon(S(0, 70, 120, 60, 120, 170, 0, 180, 40, 125), fill=RED_DARK)
    d.polygon(S(840, 70, 720, 60, 720, 170, 840, 180, 800, 125), fill=RED_DARK)
    d.rounded_rectangle(S(70, 20, 770, 150), radius=26 * SS, fill=RED)
    d.rounded_rectangle(S(80, 30, 760, 140), radius=20 * SS, outline=GOLD, width=5 * SS)
    d.rectangle(S(90, 34, 750, 60), fill=(230, 80, 80))
    save(outline(shrink(img), size=3), "ribbon.png")

    # parchment
    w, h = 820, 500
    img, d = new(w, h)
    d.rounded_rectangle(S(20, 30, w - 20, h - 30), radius=20 * SS, fill=(244, 226, 184))
    rnd = random.Random(11)
    stains = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(stains)
    for _ in range(40):
        x, y = rnd.randint(40, w - 40), rnd.randint(50, h - 50)
        r = rnd.randint(20, 60)
        sd.ellipse(S(x - r, y - r, x + r, y + r), fill=(200, 160, 100, 40))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(S(20, 30, w - 20, h - 30), radius=20 * SS, fill=255)
    stains = stains.filter(ImageFilter.GaussianBlur(14 * SS))
    stains.putalpha(Image.composite(stains.split()[3], Image.new("L", img.size, 0), mask))
    img.alpha_composite(stains)
    d = ImageDraw.Draw(img)
    for y in (20, h - 40):
        d.rounded_rectangle(S(0, y, w, y + 22), radius=11 * SS, fill=(196, 150, 96))
        d.rounded_rectangle(S(0, y, w, y + 8), radius=4 * SS, fill=(220, 180, 120))
    save(outline(shrink(img), color=(90, 60, 30, 255), size=2), "parchment.png")

    # seagull (2 frames)
    sheet = Image.new("RGBA", (96, 32), (0, 0, 0, 0))
    for k, up in enumerate((True, False)):
        img, d = new(48, 32)
        wy = 4 if up else 22
        thick_line(d, [4, wy, 16, 16, 24, 18, 32, 16, 44, wy], WHITE, 3)
        d.ellipse(S(20, 14, 28, 22), fill=WHITE)
        d.polygon(S(20, 18, 14, 19, 20, 20), fill=(255, 190, 60))
        sheet.alpha_composite(outline(shrink(img)), (k * 48, 0))
    save(sheet, "seagull.png")


if __name__ == "__main__":
    random.seed(673380313)
    make_hero()
    make_cutlass()
    make_orbs()
    make_enemies()
    make_items()
    make_traps()
    make_props()
    make_tiles()
    make_backgrounds()
    make_menu_art()
