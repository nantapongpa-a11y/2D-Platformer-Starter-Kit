#!/usr/bin/env python3
"""
Level builder for "Captain Go: Pirate Sea Adventure".

673380313-3 Nantapong Payakmaroeng - Lab 4 Computer Game Development

Each level is described below with a few simple commands (ground, dock, plank, ...).
The script writes real Godot scenes (TileMapLayer + objects), so the levels can still be
opened and edited in the Godot editor afterwards.

    python scripts/make_levels.py              # write Scenes/Levels/level_01..04.tscn
    python scripts/make_levels.py --preview D  # also save preview pictures into folder D
"""
import base64
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = 13          # rows per level (rows 11-12 are the sea)
TILE = 64
SOLID = "SWR"
MAT_ROW = {"S": 0, "W": 1, "R": 2}
VARIANT = {(1, 1, 0): 0, (1, 0, 0): 1, (1, 0, 1): 2, (1, 1, 1): 3,
           (0, 1, 0): 4, (0, 0, 0): 5, (0, 0, 1): 6, (0, 1, 1): 7}
SINGLE = {"=": (0, 3), "C": (1, 3), "B": (2, 3), "|": (5, 3), "y": (6, 3), "v": (7, 3)}


class Level:
    def __init__(self, name, width, title):
        self.name, self.w, self.title = name, width, title
        self.grid = [["."] * width for _ in range(H)]
        self.ents = []        # (kind, x, y)
        self.texts = []       # (x, y, text)
        self.props = {}       # root overrides
        self.next_scene = None
        self.door_texture = None
        self.need_boss = False
        self.spawners = []    # (x, y, [enemy kinds], max)

    # ---- building commands ----
    def block(self, x0, x1, y0, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.grid[y][x] = ch

    def ground(self, x0, x1, top, mat):
        self.block(x0, x1, top, H - 1, mat)

    def dock(self, x0, x1, top, step=4):
        self.block(x0, x1, top, top, "W")
        xs = list(range(x0, x1 + 1, step))
        if xs[-1] != x1:
            xs.append(x1)
        for x in xs:
            self.block(x, x, top + 1, H - 1, "W")

    def plank(self, x0, x1, y):
        self.block(x0, x1, y, y, "=")

    def put(self, kind, x, y):
        self.ents.append((kind, x, y))

    def coins(self, *cells):
        for x, y in cells:
            self.put("c", x, y)

    def text(self, x, y, msg):
        self.texts.append((x, y, msg))

    # ---- tiles ----
    def cell(self, x, y):
        if x < 0 or x >= self.w or y >= H:
            return "#"
        if y < 0:
            return "#"
        return self.grid[y][x]

    def tiles(self):
        ground, sea = [], []
        for y in range(H):
            for x in range(self.w):
                ch = self.grid[y][x]
                if ch in SOLID:
                    top = int(self.cell(x, y - 1) not in SOLID + "#")
                    left = int(self.cell(x - 1, y) not in SOLID + "#")
                    right = int(self.cell(x + 1, y) not in SOLID + "#")
                    ground.append((x, y, VARIANT[(top, left, right)], MAT_ROW[ch]))
                elif ch in SINGLE:
                    ground.append((x, y, *SINGLE[ch]))
                if y >= H - 2 and ch not in SOLID + "CB":
                    sea.append((x, y, 3 if y == H - 2 else 4, 3))
        return ground, sea


def tile_data(cells):
    data = bytearray(struct.pack("<H", 0))
    for x, y, ax, ay in cells:
        data += struct.pack("<hhHHHH", x, y, 0, ax, ay, 0)
    return base64.b64encode(bytes(data)).decode()


# ------------------------------------------------------------------ levels ----

def level_1():
    L = Level("level_01", 84, "ด่าน 1: หาดเกาะมุก")
    L.next_scene = "level_02"
    L.ground(0, 14, 9, "S")
    L.put("P", 2, 8)
    L.put("t", 0, 8)
    L.put("t", 11, 8)
    L.coins((5, 7), (6, 7), (7, 7))
    L.text(1, 4, "A / D = เดิน     Space = กระโดด (กด 2 ครั้ง กระโดด 2 ชั้น)\nX = ฟันคลื่นน้ำใส่โจรสลัด")
    L.put("k", 12, 8)
    L.ground(18, 26, 9, "S")
    L.put("u", 22, 8)
    L.coins((21, 6), (22, 5), (23, 6))
    L.text(18, 4, "ระวังเม่นทะเล!")
    L.block(25, 25, 8, 8, "v")
    L.ground(27, 33, 8, "S")
    L.put("g", 31, 7)
    L.put("t", 33, 7)
    L.ground(34, 42, 10, "S")
    L.block(35, 38, 7, 7, "S")
    L.put("h", 36, 6)
    L.coins((35, 6), (37, 6), (38, 6))
    L.put("k", 41, 9)
    L.ground(46, 54, 9, "S")
    L.put("F", 47, 8)
    L.put("w", 52, 7)
    L.block(53, 53, 8, 8, "y")
    L.text(48, 4, "เปลือกหอยวายุ = วิ่งเร็ว + กระโดดสูง")
    L.plank(56, 58, 8)
    L.plank(61, 63, 7)
    L.plank(66, 68, 8)
    L.coins((57, 7), (62, 6), (67, 7))
    L.ground(70, 83, 9, "S")
    L.put("u", 73, 8)
    L.put("g", 76, 8)
    L.put("k", 79, 8)
    L.coins((74, 6), (75, 6))
    L.put("n", 80, 8)
    L.put("t", 83, 8)
    L.put("D", 82, 8)
    L.text(73, 4, "ประตูสู่ท่าเรือโจรสลัด")
    return L


def level_2():
    L = Level("level_02", 92, "ด่าน 2: ท่าเรือโจรสลัด")
    L.next_scene = "level_03"
    L.ground(0, 9, 9, "S")
    L.put("P", 2, 8)
    L.put("t", 0, 8)
    L.text(2, 4, "ท่าเรือของพวกโจรสลัด... ระวังสมอเหวี่ยง!")
    L.dock(10, 24, 9)
    L.block(15, 16, 8, 8, "C")
    L.block(16, 16, 7, 7, "C")
    L.block(21, 21, 8, 8, "B")
    L.put("g", 19, 8)
    L.coins((15, 6), (16, 5), (17, 6))
    L.dock(27, 38, 9)
    L.put("a", 32, 4)
    L.coins((29, 7), (30, 7))
    L.put("k", 36, 8)
    L.block(39, 39, 8, 8, "C")
    L.dock(40, 48, 7)
    L.put("l", 42, 4)
    L.put("g", 45, 6)
    L.put("F", 47, 6)
    L.dock(50, 64, 9)
    L.spawners.append((57, 6, ["grunt", "crab"], 2))
    L.put("u", 53, 8)
    L.put("u", 61, 8)
    L.coins((56, 6), (57, 6), (58, 6))
    L.put("h", 60, 6)
    L.plank(66, 68, 8)
    L.plank(70, 72, 6)
    L.plank(74, 76, 7)
    L.put("w", 71, 5)
    L.coins((67, 7), (75, 6))
    L.dock(78, 91, 9)
    L.put("a", 82, 4)
    L.block(85, 85, 8, 8, "C")
    L.put("g", 87, 8)
    L.put("D", 90, 8)
    L.text(79, 4, "ไปยึดเรือโจรสลัดกันเถอะ!")
    return L


def level_3():
    L = Level("level_03", 96, "ด่าน 3: บนเรือโจรสลัด")
    L.next_scene = "level_04"
    L.props["sky"] = "sky_sunset.png"
    L.props["far_tint"] = "Color(1, 0.8, 0.7, 1)"
    L.dock(0, 7, 9)
    L.put("P", 2, 8)
    L.text(1, 4, "บุกขึ้นเรือโจรสลัด!")
    L.ground(9, 58, 8, "W")
    L.put("m", 18, 7)
    L.put("m", 38, 7)
    L.put("s", 15, 7)
    L.block(22, 23, 7, 7, "B")
    L.coins((22, 5), (23, 5))
    L.put("a", 27, 3)
    L.put("g", 31, 7)
    L.block(34, 35, 7, 7, "C")
    L.block(35, 35, 6, 6, "C")
    L.coins((35, 4))
    L.put("F", 40, 7)
    L.put("s", 44, 7)
    L.put("h", 46, 6)
    L.block(47, 47, 7, 7, "B")
    L.block(48, 58, 6, 7, "W")
    L.put("g", 53, 5)
    L.put("l", 56, 3)
    L.coins((50, 4), (51, 4), (52, 4))
    L.put("w", 57, 4)
    L.plank(61, 63, 7)
    L.plank(66, 68, 6)
    L.plank(71, 73, 7)
    L.coins((62, 6), (67, 5), (72, 6))
    L.ground(75, 95, 8, "W")
    L.put("m", 84, 7)
    L.put("s", 80, 7)
    L.put("a", 88, 3)
    L.spawners.append((86, 5, ["skeleton"], 2))
    L.put("g", 92, 7)
    L.put("D", 94, 7)
    L.text(76, 3, "ต่อไป: ถ้ำสมบัติของกัปตันฉลามดำ")
    return L


def level_4():
    L = Level("level_04", 90, "ด่าน 4: ถ้ำสมบัติฉลามดำ")
    L.next_scene = "game_win"
    L.need_boss = True
    L.door_texture = "treasure_chest.png"
    L.props["sky"] = "cave_bg.png"
    L.props["music"] = "black_shark_battle.ogg"
    L.props["cave"] = True
    L.block(0, 89, 0, 0, "R")
    L.block(10, 13, 1, 1, "R")
    L.block(30, 33, 1, 1, "R")
    L.block(52, 55, 1, 1, "R")
    L.block(89, 89, 1, 8, "R")
    L.ground(0, 12, 9, "R")
    L.put("P", 2, 8)
    L.text(2, 4, "ถ้ำสมบัติ... กัปตันฉลามดำซ่อนไข่มุกไว้ข้างใน!")
    L.block(5, 5, 8, 8, "v")
    L.block(9, 9, 8, 8, "v")
    L.block(11, 11, 8, 8, "y")
    L.ground(15, 22, 8, "R")
    L.put("s", 19, 7)
    L.coins((16, 6), (17, 6))
    L.block(24, 27, 6, 6, "R")
    L.coins((24, 5), (25, 5), (26, 5), (27, 5))
    L.ground(29, 48, 9, "R")
    L.put("u", 32, 8)
    L.put("s", 36, 8)
    L.put("h", 38, 7)
    L.put("F", 42, 8)
    L.put("u", 44, 8)
    L.put("s", 46, 8)
    L.block(40, 40, 8, 8, "v")
    L.plank(50, 52, 8)
    L.plank(55, 57, 7)
    L.plank(60, 62, 8)
    L.put("w", 56, 6)
    L.coins((51, 7), (61, 7))
    L.ground(64, 88, 9, "R")
    L.put("F", 65, 8)
    L.block(70, 73, 6, 6, "R")
    L.block(80, 83, 6, 6, "R")
    L.put("h", 71, 5)
    L.coins((81, 5), (82, 5))
    L.put("X", 78, 8)
    L.put("T", 84, 8)
    L.put("l", 68, 3)
    L.put("l", 86, 3)
    L.put("D", 87, 8)
    L.text(66, 3, "ปราบกัปตันฉลามดำ แล้วเปิดหีบสมบัติ!")
    return L


# ------------------------------------------------------------- scene writer ----

EXT = {
    "base": ('PackedScene', 'uid="uid://bjntpxb1c8jxn" path="res://Scenes/Levels/base_level.tscn"'),
    "tiles": ('TileSet', 'path="res://Scenes/Prefabs/sea_tile_set.tres"'),
    "coin": ('PackedScene', 'uid="uid://bfmh3fm2de78o" path="res://Scenes/Prefabs/coin.tscn"'),
    "heal": ('PackedScene', 'uid="uid://dabag2r57aued" path="res://Scenes/Prefabs/heal_potion.tscn"'),
    "conch": ('PackedScene', 'path="res://Scenes/Prefabs/sea_conch.tscn"'),
    "urchin": ('PackedScene', 'path="res://Scenes/Prefabs/sea_urchin.tscn"'),
    "anchor": ('PackedScene', 'path="res://Scenes/Prefabs/anchor_trap.tscn"'),
    "flag": ('PackedScene', 'path="res://Scenes/Prefabs/checkpoint.tscn"'),
    "grunt": ('PackedScene', 'path="res://Scenes/Actors/pirate_grunt.tscn"'),
    "crab": ('PackedScene', 'path="res://Scenes/Actors/pirate_crab.tscn"'),
    "skeleton": ('PackedScene', 'path="res://Scenes/Actors/pirate_skeleton.tscn"'),
    "boss": ('PackedScene', 'path="res://Scenes/Actors/boss_black_shark.tscn"'),
    "spawn": ('PackedScene', 'uid="uid://bs70y1kitjd3r" path="res://Scenes/Actors/enemy_spawn.tscn"'),
    "theme": ('Theme', 'uid="uid://d3eng5cvycmjf" path="res://Scenes/Prefabs/theme.tres"'),
    "palm": ('Texture2D', 'path="res://Assets/Sea/palm_tree.png"'),
    "mast": ('Texture2D', 'path="res://Assets/Sea/pirate_mast.png"'),
    "lantern": ('Texture2D', 'path="res://Assets/Sea/lantern.png"'),
    "pile": ('Texture2D', 'path="res://Assets/Sea/treasure_pile.png"'),
    "sign": ('Texture2D', 'path="res://Assets/Sea/signpost.png"'),
}
ENEMY_KIND = {"g": "grunt", "k": "crab", "s": "skeleton", "X": "boss"}
DECOR = {"t": ("palm", 160), "m": ("mast", 200), "l": ("lantern", None), "T": ("pile", 32), "n": ("sign", 40)}


def write_level(L):
    ext = dict(EXT)
    if L.next_scene == "game_win":
        ext["next"] = ('PackedScene', 'uid="uid://b46lxwc5r3dy4" path="res://Scenes/Levels/game_win.tscn"')
    else:
        ext["next"] = ('PackedScene', f'path="res://Scenes/Levels/{L.next_scene}.tscn"')
    if "sky" in L.props:
        ext["sky"] = ('Texture2D', f'path="res://Assets/Sea/{L.props["sky"]}"')
    if "music" in L.props:
        ext["music"] = ('AudioStream', f'path="res://Assets/Sound/{L.props["music"]}"')
    if L.door_texture:
        ext["door_tex"] = ('Texture2D', f'path="res://Assets/Sea/{L.door_texture}"')

    out = ["[gd_scene format=3]", ""]
    for key, (typ, attrs) in ext.items():
        out.append(f'[ext_resource type="{typ}" {attrs} id="{key}"]')
    out += ["", '[sub_resource type="RectangleShape2D" id="sea_shape"]',
            f"size = Vector2({L.w * TILE + 800}, 300)", "",
            '[sub_resource type="RectangleShape2D" id="wall_shape"]', "size = Vector2(40, 2000)", ""]

    root = ['[node name="BaseLevel" unique_id=1997201631 instance=ExtResource("base")]']
    if "music" in L.props:
        root.append('music = ExtResource("music")')
    if "sky" in L.props:
        root.append('sky_texture = ExtResource("sky")')
    if "far_tint" in L.props:
        root.append(f'far_tint = {L.props["far_tint"]}')
    if L.props.get("cave"):
        root += ["show_far_sea = false", "show_waves = false", "camera_top_margin = 0"]
    out += root + [""]

    door = next((e for e in L.ents if e[0] == "D"))
    out += ['[node name="LevelFinishDoor" parent="." unique_id=1788542095]',
            f"position = Vector2({door[1] * TILE + 32}, {(door[2] + 1) * TILE - 48})",
            'next_scene = ExtResource("next")']
    if L.need_boss:
        out.append("need_boss_defeated = true")
    out.append("")
    if L.door_texture:
        out += ['[node name="Sprite2D" parent="LevelFinishDoor" unique_id=1854125426]',
                "position = Vector2(0, 0)", 'texture = ExtResource("door_tex")', ""]

    ground, sea = L.tiles()
    out += ['[node name="Ground" type="TileMapLayer" parent="Level"]',
            f'tile_map_data = PackedByteArray("{tile_data(ground)}")', 'tile_set = ExtResource("tiles")', "",
            '[node name="Sea" type="TileMapLayer" parent="Level"]', "z_index = 3",
            f'tile_map_data = PackedByteArray("{tile_data(sea)}")', 'tile_set = ExtResource("tiles")', "",
            '[node name="SeaKill" type="StaticBody2D" parent="Level" groups=["Sea"]]',
            "collision_layer = 8", "collision_mask = 0", "",
            '[node name="CollisionShape2D" type="CollisionShape2D" parent="Level/SeaKill"]',
            f"position = Vector2({L.w * TILE / 2}, {(H - 2) * TILE + 36 + 150})", 'shape = SubResource("sea_shape")', "",
            '[node name="Walls" type="StaticBody2D" parent="Level"]', "",
            '[node name="Left" type="CollisionShape2D" parent="Level/Walls"]',
            "position = Vector2(-20, 0)", 'shape = SubResource("wall_shape")', "",
            '[node name="Right" type="CollisionShape2D" parent="Level/Walls"]',
            f"position = Vector2({L.w * TILE + 20}, 0)", 'shape = SubResource("wall_shape")', "",
            '[node name="Decor" type="Node2D" parent="Level"]', "z_index = -1", "",
            '[node name="Traps" type="Node2D" parent="Level"]', ""]

    counts = {}

    def name(kind):
        counts[kind] = counts.get(kind, 0) + 1
        return f"{kind}{counts[kind]}"

    for kind, x, y in L.ents:
        cx = x * TILE + 32
        if kind == "P":
            out += ['[node name="Player" parent="." unique_id=850213228]',
                    f"position = Vector2({cx}, {(y + 1) * TILE - 2})", ""]
        elif kind in "chw":
            scene = {"c": "coin", "h": "heal", "w": "conch"}[kind]
            out += [f'[node name="{name(scene.capitalize())}" parent="Coins" instance=ExtResource("{scene}")]',
                    f"position = Vector2({cx}, {y * TILE + 32})", ""]
        elif kind in ENEMY_KIND:
            scene = ENEMY_KIND[kind]
            out += [f'[node name="{name(scene.capitalize())}" parent="Enemies" instance=ExtResource("{scene}")]',
                    f"position = Vector2({cx}, {(y + 1) * TILE - 2})", "direction = -1", ""]
        elif kind == "u":
            out += [f'[node name="{name("Urchin")}" parent="Level/Traps" instance=ExtResource("urchin")]',
                    f"position = Vector2({cx}, {(y + 1) * TILE})", ""]
        elif kind == "a":
            out += [f'[node name="{name("Anchor")}" parent="Level/Traps" instance=ExtResource("anchor")]',
                    f"position = Vector2({cx}, {y * TILE})", ""]
        elif kind == "F":
            out += [f'[node name="{name("Checkpoint")}" parent="Level" instance=ExtResource("flag")]',
                    f"position = Vector2({cx}, {(y + 1) * TILE})", ""]
        elif kind in DECOR:
            tex, half = DECOR[kind]
            py = y * TILE + 32 if half is None else (y + 1) * TILE - half
            out += [f'[node name="{name(tex.capitalize())}" type="Sprite2D" parent="Level/Decor"]',
                    f"position = Vector2({cx}, {py})", f'texture = ExtResource("{tex}")', ""]

    for x, y, kinds, mx in L.spawners:
        arr = ", ".join(f'ExtResource("{k}")' for k in kinds)
        out += [f'[node name="{name("Spawner")}" parent="Enemies" instance=ExtResource("spawn")]',
                f"position = Vector2({x * TILE + 32}, {y * TILE + 32})",
                f"enemy_scenes = Array[PackedScene]([{arr}])",
                "speed_range = Array[int]([60, 70, 80])",
                "respawn_time = Array[int]([8, 12])",
                f"max_instance = {mx}", ""]

    for x, y, msg in L.texts:
        msg = msg.replace('"', '\\"')
        out += [f'[node name="{name("Hint")}" type="Label" parent="Text"]',
                f"offset_left = {x * TILE}.0", f"offset_top = {y * TILE}.0",
                f"offset_right = {x * TILE + 700}.0", f"offset_bottom = {y * TILE + 90}.0",
                'theme = ExtResource("theme")',
                "theme_override_colors/font_color = Color(1, 0.97, 0.85, 1)",
                "theme_override_colors/font_outline_color = Color(0.15, 0.1, 0.25, 1)",
                "theme_override_constants/outline_size = 8",
                "theme_override_font_sizes/font_size = 22", f'text = "{msg}"', ""]

    out += ['[node name="Label" parent="UserInterface" unique_id=1103718868]', f'text = "{L.title}"', ""]
    path = ROOT / "Scenes/Levels" / f"{L.name}.tscn"
    path.write_text("\n".join(out), encoding="utf8")
    print("wrote", path.name, f"{L.w}x{H} tiles, {len(ground)} ground tiles, {len(L.ents)} objects")


# ---------------------------------------------------------------- preview ----

def preview(L, folder):
    from PIL import Image, ImageDraw
    sea = ROOT / "Assets/Sea"
    atlas = Image.open(sea / "sea_tiles.png").convert("RGBA")
    sky = "cave_bg.png" if L.props.get("cave") else L.props.get("sky", "sky_day.png")
    img = Image.open(sea / sky).convert("RGBA").resize((L.w * TILE, H * TILE))
    ground, water = L.tiles()
    for x, y, ax, ay in ground + water:
        img.alpha_composite(atlas.crop((ax * 64, ay * 64, ax * 64 + 64, ay * 64 + 64)), (x * 64, y * 64))
    sprites = {"g": ("pirate_grunt.png", 96, 96), "k": ("pirate_crab.png", 96, 96), "s": ("pirate_skeleton.png", 96, 96),
               "X": ("boss_black_shark.png", 128, 144), "c": ("doubloon.png",), "h": ("coconut.png",),
               "w": ("wind_conch.png",), "u": ("sea_urchin.png",), "F": ("flag_off.png",), "D": (L.door_texture or "door_ship.png",),
               "t": ("palm_tree.png",), "m": ("pirate_mast.png",), "l": ("lantern.png",), "T": ("treasure_pile.png",),
               "n": ("signpost.png",), "a": ("anchor_trap.png",), "P": ("captain_go.png",)}
    for kind, x, y in L.ents:
        f = sprites[kind]
        s = Image.open(sea / f[0]).convert("RGBA")
        if len(f) == 3:
            s = s.crop((0, 0, f[1], f[2]))
        if kind == "X":
            s = s.resize((int(s.width * 1.3), int(s.height * 1.3)))
        cx = x * 64 + 32
        if kind in "ch w":
            pos = (cx - s.width // 2, y * 64 + 32 - s.height // 2)
        elif kind == "a":
            pos = (cx - s.width // 2, y * 64)
        elif kind == "l":
            pos = (cx - s.width // 2, y * 64 + 32 - s.height // 2)
        else:
            pos = (cx - s.width // 2, (y + 1) * 64 - s.height)
        img.alpha_composite(s, pos)
    d = ImageDraw.Draw(img)
    for x, y, kinds, mx in L.spawners:
        d.rectangle((x * 64 + 8, y * 64 + 8, x * 64 + 56, y * 64 + 56), outline=(255, 0, 0), width=4)
    for x, y, msg in L.texts:
        d.rectangle((x * 64, y * 64, x * 64 + 300, y * 64 + 30), outline=(255, 255, 255), width=2)
    for x in range(0, L.w, 10):
        d.text((x * 64 + 4, 4), str(x), fill=(255, 255, 0))
    img = img.resize((img.width // 4, img.height // 4))
    img.convert("RGB").save(Path(folder) / f"{L.name}.png")


if __name__ == "__main__":
    levels = [level_1(), level_2(), level_3(), level_4()]
    for lv in levels:
        write_level(lv)
    if "--preview" in sys.argv:
        folder = sys.argv[sys.argv.index("--preview") + 1]
        for lv in levels:
            preview(lv, folder)
