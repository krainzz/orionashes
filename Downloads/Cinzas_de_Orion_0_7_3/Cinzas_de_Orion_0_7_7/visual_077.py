# visual_077.py - Sistema Universal de Cartas Sci-Fi TCG Holografico (0.7.7)
# + Base Consolidada 0.7.6 (Heroi, Equipamentos Direcionais, Nave e Shaders)
from __future__ import annotations
import math
from pathlib import Path
import pygame
from content import (
    CARDS, SPECIES, BOSSES, HELMET_DESIGNS, CARD_RARITIES,
    SHIP_INTERIOR, UNIQUE_VARIANT_MULTIPLIERS, UNIQUE_MOMENTUM_DEFS,
    format_card_name
)

ROOT = Path(__file__).resolve().parent
EQUIPS_DIR = ROOT / "assets" / "equips"

PX_DARK = (18, 23, 29)
PX_BLACK = (11, 14, 19)
PX_STEEL = (119, 133, 143)
PX_STEEL_HI = (182, 198, 208)
PX_STEEL_D = (64, 76, 86)
PX_SUIT = (34, 45, 56)
PX_SUIT_HI = (58, 74, 90)
PX_SKIN_DEEP = (46, 27, 18)
PX_SKIN = (78, 46, 31)
PX_SKIN_MID = (104, 64, 43)
PX_SKIN_HI = (136, 86, 58)
PX_EYE_WHITE = (232, 240, 245)
PX_CYAN = (87, 225, 205)
PX_CYAN_HI = (185, 255, 246)
PX_GOLD = (228, 176, 86)
PX_GOLD_D = (152, 108, 42)

DIRECTION_TO_INT = {
    "down": 0,
    "up": 1,
    "left": 2,
    "right": 3,
}

# Requisito 2 e 3: Cores exatas do Brilho Neon da Barra de Nome por Raridade (Uniforms RGB)
RARITY_NEON_GLOW_COLORS = {
    "Comum": (255, 255, 255),      # Branco Neon
    "Incomum": (90, 255, 130),     # Verde Claro Neon
    "Rara": (0, 228, 255),         # Azul Ciano Neon
    "Mítica": (200, 72, 255),      # Roxo Neon
    "Mitica": (200, 72, 255),
    "Lendária": (255, 210, 45),    # Dourado Neon
    "Lendaria": (255, 210, 45),
    "Única": (255, 38, 46),        # Vermelho Neon Estrito
    "Unica": (255, 38, 46),
}


def _rect(s, c, x, y, w, h, r=0):
    pygame.draw.rect(s, c, (x, y, w, h), border_radius=r)


# ==============================================================================
# EXTRATOR DE PALETA DE EQUIPAMENTOS E SPRITES DO HEROI (0.7.6 PRESERVADO)
# ==============================================================================

class EquipmentPaletteSampler076:
    _palettes = {}
    DEFAULT_PALETTES = {
        "helmet": {"dark": (46, 58, 70), "mid": (86, 104, 120), "light": (162, 184, 198), "trim": (222, 172, 84), "visor": (87, 225, 205)},
        "chest": {"dark": (50, 64, 78), "mid": (96, 114, 130), "light": (176, 194, 206), "trim": (224, 174, 86), "visor": (87, 225, 205)},
        "locomotion": {"dark": (48, 60, 74), "mid": (92, 108, 124), "light": (170, 188, 202), "trim": (226, 176, 86), "visor": (87, 225, 205)},
        "gauntlet": {"dark": (132, 92, 38), "mid": (212, 160, 74), "light": (245, 212, 132), "trim": (178, 194, 206), "visor": (87, 225, 205)},
    }

    @classmethod
    def get_palette(cls, piece_key: str) -> dict:
        if piece_key in cls._palettes:
            return cls._palettes[piece_key]
        file_map = {"helmet": "Elmo.png", "chest": "Peitoral.png", "locomotion": "Grevas.png", "gauntlet": "Manopla.png"}
        base_pal = dict(cls.DEFAULT_PALETTES.get(piece_key, cls.DEFAULT_PALETTES["chest"]))
        fname = file_map.get(piece_key)
        fpath = EQUIPS_DIR / fname if fname else None
        if fpath and fpath.exists():
            try:
                surf = pygame.image.load(str(fpath))
                w, h = surf.get_size()
                step = max(1, min(w, h) // 24)
                metals, golds, cyans = [], [], []
                for x in range(0, w, step):
                    for y in range(0, h, step):
                        c = surf.get_at((x, y))
                        if len(c) == 4 and c[3] < 128:
                            continue
                        r, g, b = int(c[0]), int(c[1]), int(c[2])
                        lum = 0.299 * r + 0.587 * g + 0.114 * b
                        if lum < 22 or lum > 248:
                            continue
                        if b > r + 25 and g > r + 15:
                            cyans.append((r, g, b))
                        elif r > b + 35 and g > b + 15:
                            golds.append((r, g, b))
                        else:
                            metals.append((lum, (r, g, b)))
                if len(metals) >= 6:
                    metals.sort(key=lambda item: item[0])
                    base_pal["dark"] = metals[int(len(metals) * 0.20)][1]
                    base_pal["mid"] = metals[int(len(metals) * 0.55)][1]
                    base_pal["light"] = metals[int(len(metals) * 0.85)][1]
                if golds:
                    ar = sum(p[0] for p in golds) // len(golds)
                    ag = sum(p[1] for p in golds) // len(golds)
                    ab = sum(p[2] for p in golds) // len(golds)
                    if piece_key == "gauntlet":
                        base_pal["mid"] = (ar, ag, ab)
                        base_pal["dark"] = (max(0, ar - 55), max(0, ag - 45), max(0, ab - 30))
                        base_pal["light"] = (min(255, ar + 35), min(255, ag + 35), min(255, ab + 35))
                    else:
                        base_pal["trim"] = (ar, ag, ab)
                if cyans:
                    base_pal["visor"] = (
                        sum(p[0] for p in cyans) // len(cyans),
                        sum(p[1] for p in cyans) // len(cyans),
                        sum(p[2] for p in cyans) // len(cyans),
                    )
            except Exception:
                pass
        cls._palettes[piece_key] = base_pal
        return base_pal


def make_hero_down_sprite(frame=0):
    s = pygame.Surface((44, 58), pygame.SRCALPHA)
    step = int(frame) % 3
    pal_chest = EquipmentPaletteSampler076.get_palette("chest")
    pal_gaunt = EquipmentPaletteSampler076.get_palette("gauntlet")
    if step == 0:
        _rect(s, PX_SUIT, 13, 34, 6, 14); _rect(s, PX_SUIT, 25, 34, 6, 14)
        _rect(s, PX_STEEL_D, 13, 39, 6, 4, 1); _rect(s, PX_STEEL_D, 25, 39, 6, 4, 1)
        _rect(s, PX_BLACK, 12, 47, 7, 9, 2); _rect(s, PX_BLACK, 25, 47, 7, 9, 2)
    elif step == 1:
        _rect(s, PX_SUIT, 12, 35, 6, 15); _rect(s, PX_SUIT, 26, 33, 6, 11)
        _rect(s, PX_STEEL_D, 12, 41, 6, 4, 1); _rect(s, PX_STEEL_D, 26, 37, 6, 4, 1)
        _rect(s, PX_BLACK, 11, 49, 8, 8, 2); _rect(s, PX_BLACK, 26, 43, 7, 8, 2)
    else:
        _rect(s, PX_SUIT, 12, 33, 6, 11); _rect(s, PX_SUIT, 26, 35, 6, 15)
        _rect(s, PX_STEEL_D, 12, 37, 6, 4, 1); _rect(s, PX_STEEL_D, 26, 41, 6, 4, 1)
        _rect(s, PX_BLACK, 11, 43, 7, 8, 2); _rect(s, PX_BLACK, 25, 49, 8, 8, 2)

    pygame.draw.polygon(s, PX_SUIT, [(12, 19), (32, 19), (34, 29), (30, 36), (14, 36), (10, 29)])
    pygame.draw.polygon(s, pal_chest["dark"], [(13, 20), (31, 20), (32, 30), (29, 35), (15, 35), (12, 30)])
    pygame.draw.polygon(s, pal_chest["mid"], [(15, 21), (29, 21), (30, 29), (27, 33), (17, 33), (14, 29)])
    pygame.draw.line(s, pal_chest["light"], (16, 21), (28, 21), 2)
    pygame.draw.line(s, pal_chest["trim"], (15, 20), (29, 20), 1)
    _rect(s, pal_chest["dark"], 14, 33, 16, 3, 1)
    _rect(s, pal_chest["trim"], 19, 33, 6, 3, 1)

    pygame.draw.polygon(s, pal_chest["dark"], [(8, 19), (14, 17), (15, 23), (9, 25)])
    pygame.draw.polygon(s, pal_chest["dark"], [(30, 17), (36, 19), (35, 25), (29, 23)])
    pygame.draw.line(s, pal_chest["trim"], (9, 19), (14, 18), 2)
    pygame.draw.line(s, pal_chest["trim"], (30, 18), (35, 19), 2)

    pygame.draw.polygon(s, PX_DARK, [(22, 22), (27, 27), (22, 32), (17, 27)])
    pygame.draw.polygon(s, PX_CYAN, [(22, 23), (26, 27), (22, 31), (18, 27)])
    pygame.draw.polygon(s, PX_CYAN_HI, [(22, 25), (24, 27), (22, 29), (20, 27)])

    left_arm_y = 23 + (1 if step == 2 else (-1 if step == 1 else 0))
    right_arm_y = 22 + (1 if step == 1 else (-1 if step == 2 else 0))
    _rect(s, PX_SUIT_HI, 7, left_arm_y, 5, 6, 1)
    _rect(s, PX_SKIN, 6, left_arm_y + 5, 5, 5, 1)
    _rect(s, PX_STEEL_D, 6, left_arm_y + 10, 5, 5, 1)

    _rect(s, PX_SUIT_HI, 32, right_arm_y, 5, 6, 1)
    _rect(s, PX_SKIN, 33, right_arm_y + 5, 5, 4, 1)
    pygame.draw.polygon(s, pal_gaunt["dark"], [(32, right_arm_y + 8), (41, right_arm_y + 8), (42, right_arm_y + 21), (33, right_arm_y + 21)])
    _rect(s, pal_gaunt["mid"], 33, right_arm_y + 9, 8, 11, 2)
    _rect(s, pal_gaunt["light"], 34, right_arm_y + 10, 6, 2)
    _rect(s, PX_DARK, 34, right_arm_y + 13, 6, 4, 1)
    _rect(s, pal_gaunt["visor"], 35, right_arm_y + 14, 4, 2)
    pygame.draw.circle(s, PX_CYAN_HI, (37, right_arm_y + 19), 2)

    _rect(s, PX_SKIN_DEEP, 19, 14, 6, 5); _rect(s, PX_SKIN, 20, 14, 4, 4)
    pygame.draw.polygon(s, PX_SKIN_DEEP, [(15, 7), (17, 2), (27, 2), (29, 7), (28, 14), (25, 17), (19, 17), (16, 14)])
    pygame.draw.polygon(s, PX_SKIN, [(16, 7), (18, 4), (26, 4), (28, 7), (27, 13), (24, 16), (20, 16), (17, 13)])
    _rect(s, PX_SKIN_MID, 18, 5, 8, 3, 1); _rect(s, PX_SKIN_HI, 21, 8, 2, 4)
    pygame.draw.polygon(s, PX_BLACK, [(15, 7), (16, 2), (28, 2), (29, 7), (27, 5), (17, 5)])
    _rect(s, PX_EYE_WHITE, 18, 8, 2, 2); _rect(s, PX_BLACK, 19, 8, 1, 2)
    _rect(s, PX_EYE_WHITE, 24, 8, 2, 2); _rect(s, PX_BLACK, 24, 8, 1, 2)
    pygame.draw.lines(s, PX_BLACK, False, [(17, 12), (19, 15), (22, 16), (25, 15), (27, 12)], 2)
    return s


def make_hero_up_sprite(frame=0):
    s = pygame.Surface((44, 58), pygame.SRCALPHA)
    step = int(frame) % 3
    pal_chest = EquipmentPaletteSampler076.get_palette("chest")
    pal_gaunt = EquipmentPaletteSampler076.get_palette("gauntlet")
    if step == 0:
        _rect(s, PX_SUIT, 13, 34, 6, 14); _rect(s, PX_SUIT, 25, 34, 6, 14)
        _rect(s, PX_STEEL_D, 13, 39, 6, 4, 1); _rect(s, PX_STEEL_D, 25, 39, 6, 4, 1)
        _rect(s, PX_BLACK, 12, 47, 7, 9, 2); _rect(s, PX_BLACK, 25, 47, 7, 9, 2)
    elif step == 1:
        _rect(s, PX_SUIT, 12, 33, 6, 11); _rect(s, PX_SUIT, 26, 35, 6, 15)
        _rect(s, PX_STEEL_D, 12, 37, 6, 4, 1); _rect(s, PX_STEEL_D, 26, 41, 6, 4, 1)
        _rect(s, PX_BLACK, 11, 43, 7, 8, 2); _rect(s, PX_BLACK, 25, 49, 8, 8, 2)
    else:
        _rect(s, PX_SUIT, 12, 35, 6, 15); _rect(s, PX_SUIT, 26, 33, 6, 11)
        _rect(s, PX_STEEL_D, 12, 41, 6, 4, 1); _rect(s, PX_STEEL_D, 26, 37, 6, 4, 1)
        _rect(s, PX_BLACK, 11, 49, 8, 8, 2); _rect(s, PX_BLACK, 26, 43, 7, 8, 2)

    pygame.draw.polygon(s, PX_SUIT, [(12, 19), (32, 19), (34, 29), (30, 36), (14, 36), (10, 29)])
    pygame.draw.polygon(s, pal_chest["dark"], [(14, 20), (30, 20), (31, 30), (28, 35), (16, 35), (13, 30)])
    pygame.draw.polygon(s, pal_chest["mid"], [(16, 21), (28, 21), (29, 29), (26, 34), (18, 34), (15, 29)])
    pygame.draw.line(s, pal_chest["trim"], (15, 20), (29, 20), 1)
    _rect(s, pal_chest["dark"], 19, 21, 6, 13, 1)
    _rect(s, pal_chest["light"], 21, 22, 2, 11)
    for ry in (23, 26, 29):
        pygame.draw.line(s, PX_DARK, (17, ry), (27, ry), 1)
    _rect(s, pal_chest["dark"], 14, 33, 16, 3, 1)

    left_arm_y = 23 + (1 if step == 1 else (-1 if step == 2 else 0))
    right_arm_y = 22 + (1 if step == 2 else (-1 if step == 1 else 0))
    pygame.draw.polygon(s, pal_chest["dark"], [(8, 19), (14, 17), (15, 23), (9, 25)])
    pygame.draw.polygon(s, pal_chest["dark"], [(30, 17), (36, 19), (35, 25), (29, 23)])
    pygame.draw.line(s, pal_chest["trim"], (9, 19), (14, 18), 2)
    pygame.draw.line(s, pal_chest["trim"], (30, 18), (35, 19), 2)

    _rect(s, PX_SUIT_HI, 7, left_arm_y, 5, 6, 1)
    _rect(s, PX_SKIN, 6, left_arm_y + 5, 5, 5, 1)
    _rect(s, PX_STEEL_D, 6, left_arm_y + 10, 5, 5, 1)

    _rect(s, PX_SUIT_HI, 32, right_arm_y, 5, 6, 1)
    _rect(s, PX_SKIN, 33, right_arm_y + 5, 5, 4, 1)
    _rect(s, pal_gaunt["dark"], 32, right_arm_y + 8, 9, 13, 2)
    _rect(s, pal_gaunt["mid"], 33, right_arm_y + 9, 7, 11, 2)
    _rect(s, pal_gaunt["trim"], 34, right_arm_y + 10, 5, 2)

    _rect(s, PX_SKIN_DEEP, 18, 13, 8, 6); _rect(s, PX_SKIN, 19, 12, 6, 5)
    pygame.draw.polygon(s, PX_SKIN, [(16, 7), (17, 2), (27, 2), (28, 7), (27, 13), (17, 13)])
    pygame.draw.polygon(s, PX_BLACK, [(16, 9), (17, 2), (27, 2), (28, 9), (26, 11), (18, 11)])
    pygame.draw.line(s, PX_SKIN_MID, (18, 11), (26, 11), 1)
    return s


def make_hero_side_sprite(direction="right", frame=0):
    s = pygame.Surface((44, 58), pygame.SRCALPHA)
    step = int(frame) % 3
    pal_chest = EquipmentPaletteSampler076.get_palette("chest")
    pal_gaunt = EquipmentPaletteSampler076.get_palette("gauntlet")
    is_left = (direction == "left")
    def mx(x_val, width=0):
        return (44 - x_val - width) if is_left else x_val
    def mpt(pt):
        return (44 - pt[0], pt[1]) if is_left else pt

    if step == 0:
        _rect(s, PX_SUIT, mx(18, 7), 34, 7, 14)
        _rect(s, PX_STEEL_D, mx(18, 7), 39, 7, 4, 1)
        _rect(s, PX_BLACK, mx(17, 9), 47, 9, 9, 2)
    elif step == 1:
        pygame.draw.polygon(s, PX_DARK, [mpt((18, 34)), mpt((23, 34)), mpt((15, 47)), mpt((10, 46))])
        _rect(s, PX_BLACK, mx(9, 8), 46, 8, 7, 2)
        pygame.draw.polygon(s, PX_SUIT, [mpt((19, 34)), mpt((25, 34)), mpt((31, 47)), mpt((25, 48))])
        _rect(s, PX_STEEL_D, mx(23, 6), 39, 6, 4, 1)
        _rect(s, PX_BLACK, mx(25, 9), 47, 9, 8, 2)
    else:
        pygame.draw.polygon(s, PX_DARK, [mpt((19, 34)), mpt((25, 34)), mpt((30, 46)), mpt((24, 47))])
        _rect(s, PX_BLACK, mx(24, 8), 46, 8, 7, 2)
        pygame.draw.polygon(s, PX_SUIT, [mpt((18, 34)), mpt((24, 34)), mpt((16, 48)), mpt((11, 47))])
        _rect(s, PX_STEEL_D, mx(14, 6), 39, 6, 4, 1)
        _rect(s, PX_BLACK, mx(10, 9), 47, 9, 8, 2)

    pygame.draw.polygon(s, PX_SUIT, [mpt((15, 19)), mpt((28, 19)), mpt((30, 29)), mpt((27, 36)), mpt((17, 36)), mpt((14, 29))])
    pygame.draw.polygon(s, pal_chest["mid"], [mpt((17, 20)), mpt((27, 20)), mpt((28, 29)), mpt((26, 34)), mpt((18, 34)), mpt((16, 29))])
    pygame.draw.line(s, pal_chest["light"], mpt((18, 21)), mpt((26, 21)), 2)
    pygame.draw.line(s, pal_chest["trim"], mpt((17, 20)), mpt((27, 20)), 1)

    cx = 18 if is_left else 26
    pygame.draw.polygon(s, PX_CYAN, [(cx, 24), (cx + 3, 27), (cx, 30), (cx - 2, 27)])
    pygame.draw.polygon(s, PX_CYAN_HI, [(cx, 25), (cx + 1, 27), (cx, 29), (cx - 1, 27)])

    arm_swing = 2 if step == 1 else (-2 if step == 2 else 0)
    if not is_left:
        _rect(s, PX_SUIT_HI, 19 + arm_swing, 22, 6, 6, 1)
        _rect(s, PX_SKIN, 21 + arm_swing, 27, 5, 4, 1)
        _rect(s, pal_gaunt["dark"], 22 + arm_swing, 30, 11, 9, 2)
        _rect(s, pal_gaunt["mid"], 23 + arm_swing, 31, 9, 7, 2)
        _rect(s, pal_gaunt["light"], 24 + arm_swing, 32, 6, 2)
        pygame.draw.circle(s, PX_CYAN_HI, (30 + arm_swing, 35), 2)
    else:
        pygame.draw.line(s, pal_gaunt["dark"], (15, 31), (12, 35), 3)
        _rect(s, PX_SUIT_HI, 19 - arm_swing, 22, 6, 6, 1)
        _rect(s, PX_SKIN, 17 - arm_swing, 27, 5, 6, 1)
        _rect(s, PX_STEEL_D, 15 - arm_swing, 32, 5, 5, 1)

    _rect(s, PX_SKIN_DEEP, mx(19, 6), 14, 6, 5)
    pygame.draw.polygon(s, PX_SKIN_DEEP, [mpt((16, 7)), mpt((18, 2)), mpt((27, 2)), mpt((30, 8)), mpt((29, 14)), mpt((24, 16)), mpt((17, 14))])
    pygame.draw.polygon(s, PX_SKIN, [mpt((17, 7)), mpt((19, 4)), mpt((26, 4)), mpt((29, 8)), mpt((28, 13)), mpt((24, 15)), mpt((18, 13))])
    _rect(s, PX_SKIN_HI, mx(26, 3), 8, 3, 3)
    pygame.draw.polygon(s, PX_BLACK, [mpt((16, 8)), mpt((17, 2)), mpt((27, 2)), mpt((26, 6)), mpt((18, 6))])
    _rect(s, PX_EYE_WHITE, mx(25, 2), 8, 2, 2)
    _rect(s, PX_BLACK, mx(26, 1), 8, 1, 2)
    pygame.draw.lines(s, PX_BLACK, False, [mpt((23, 12)), mpt((25, 15)), mpt((28, 14)), mpt((28, 11))], 2)
    return s


def make_hero_world_sprite(direction="down", frame=0):
    if direction == "up":
        return make_hero_up_sprite(frame)
    if direction == "left":
        return make_hero_side_sprite("left", frame)
    if direction == "right":
        return make_hero_side_sprite("right", frame)
    return make_hero_down_sprite(frame)


def make_hero_combat_sprite(frame=0):
    s = pygame.Surface((84, 66), pygame.SRCALPHA)
    step = int(frame) % 2
    pal_chest = EquipmentPaletteSampler076.get_palette("chest")
    pal_gaunt = EquipmentPaletteSampler076.get_palette("gauntlet")
    _rect(s, PX_BLACK, 26, 49, 10, 11, 2); _rect(s, PX_BLACK, 42, 49, 10, 11, 2)
    _rect(s, PX_SUIT, 27, 35, 9, 15); _rect(s, PX_SUIT, 42, 35, 9, 15)
    _rect(s, PX_SUIT_HI, 29, 36, 3, 12); _rect(s, PX_SUIT_HI, 44, 36, 3, 12)
    _rect(s, PX_STEEL_D, 27, 38, 9, 5, 1); _rect(s, PX_STEEL_D, 42, 38, 9, 5, 1)

    pygame.draw.polygon(s, PX_SUIT, [(25, 18), (47, 18), (52, 26), (49, 43), (43, 47), (29, 47), (23, 42), (21, 26)])
    pygame.draw.polygon(s, pal_chest["dark"], [(27, 20), (45, 20), (49, 27), (47, 40), (42, 44), (30, 44), (25, 39), (24, 27)])
    pygame.draw.polygon(s, pal_chest["mid"], [(29, 21), (43, 21), (47, 27), (45, 38), (41, 42), (31, 42), (27, 38), (26, 27)])
    pygame.draw.line(s, pal_chest["light"], (30, 22), (42, 22), 2)
    pygame.draw.line(s, pal_chest["trim"], (28, 20), (44, 20), 2)
    pygame.draw.line(s, pal_chest["dark"], (29, 38), (43, 38), 2)

    pygame.draw.polygon(s, PX_DARK, [(36, 23), (42, 29), (36, 35), (30, 29)])
    pygame.draw.polygon(s, PX_CYAN, [(36, 24), (41, 29), (36, 34), (31, 29)])
    pygame.draw.polygon(s, PX_CYAN_HI, [(36, 26), (39, 29), (36, 32), (33, 29)])

    pygame.draw.line(s, PX_SUIT_HI, (24, 24), (30, 31), 5)
    pygame.draw.line(s, PX_SKIN, (30, 31), (37, 32), 4)
    _rect(s, PX_DARK, 34, 28, 8, 6, 1); _rect(s, PX_CYAN, 35, 30, 6, 2); _rect(s, PX_SKIN_HI, 38, 30, 5, 4, 1)

    arm_lift = -2 if step else 0
    pygame.draw.line(s, PX_SUIT_HI, (48, 24), (56, 26 + arm_lift), 6)
    pygame.draw.line(s, PX_SKIN, (54, 25 + arm_lift), (60, 26 + arm_lift), 5)
    _rect(s, pal_gaunt["dark"], 58, 21 + arm_lift, 12, 11, 2)
    _rect(s, pal_gaunt["mid"], 59, 22 + arm_lift, 10, 9, 2)
    _rect(s, pal_gaunt["mid"], 68, 18 + arm_lift, 10, 14, 2)
    _rect(s, pal_gaunt["light"], 60, 23 + arm_lift, 8, 2)
    for ry in (20, 24, 28):
        pygame.draw.line(s, pal_gaunt["trim"], (70, ry + arm_lift), (76, ry + arm_lift), 2)
    pygame.draw.circle(s, PX_CYAN, (70, 25 + arm_lift), 4 + step)
    pygame.draw.circle(s, PX_CYAN_HI, (70, 25 + arm_lift), 2)
    if step:
        pygame.draw.circle(s, PX_CYAN_HI, (78, 25 + arm_lift), 3)

    _rect(s, PX_SKIN_DEEP, 33, 13, 8, 6); _rect(s, PX_SKIN, 34, 13, 6, 5)
    pygame.draw.polygon(s, PX_SKIN_DEEP, [(29, 7), (31, 2), (43, 2), (46, 8), (44, 15), (40, 17), (33, 17), (30, 14)])
    pygame.draw.polygon(s, PX_SKIN, [(30, 7), (32, 3), (42, 3), (45, 8), (43, 14), (39, 16), (34, 16), (31, 13)])
    _rect(s, PX_SKIN_MID, 32, 5, 10, 3, 1); _rect(s, PX_SKIN_HI, 37, 8, 2, 4)
    pygame.draw.polygon(s, PX_BLACK, [(29, 7), (31, 1), (43, 1), (46, 7), (43, 5), (31, 5)])
    _rect(s, PX_EYE_WHITE, 33, 8, 2, 2); _rect(s, PX_BLACK, 34, 8, 1, 2)
    _rect(s, PX_EYE_WHITE, 40, 8, 2, 2); _rect(s, PX_BLACK, 41, 8, 1, 2)
    pygame.draw.lines(s, PX_BLACK, False, [(31, 12), (34, 16), (38, 16), (42, 15), (44, 12)], 2)
    return s


def draw_locomotion_overlay_076(surface, raw_width, raw_height, pose="world", direction="down", frame=0):
    sx = surface.get_width() / max(1, raw_width)
    sy = surface.get_height() / max(1, raw_height)
    layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    step = int(frame) % 3
    pal = EquipmentPaletteSampler076.get_palette("locomotion")

    def R(col, rect, rad=1):
        rr = pygame.Rect(int(rect[0] * sx), int(rect[1] * sy), max(1, int(rect[2] * sx)), max(1, int(rect[3] * sy)))
        pygame.draw.rect(layer, col, rr, border_radius=max(0, int(rad * min(sx, sy))))

    def L(col, a, b, w=1):
        pygame.draw.line(layer, col, (int(a[0] * sx), int(a[1] * sy)), (int(b[0] * sx), int(b[1] * sy)), max(1, int(w * min(sx, sy))))

    if pose == "combat":
        for lx in (26, 41):
            R(pal["dark"], (lx, 36, 10, 18), 2); R(pal["mid"], (lx + 1, 37, 8, 14), 1)
            L(pal["light"], (lx + 2, 38), (lx + 2, 50), 1)
            R(pal["visor"], (lx + 3, 44, 4, 3), 1); R(pal["trim"], (lx + 1, 51, 8, 3), 1)
    elif direction in ("left", "right"):
        is_left = (direction == "left")
        def mx(x_val, w_val):
            return (44 - x_val - w_val) if is_left else x_val
        if step == 0:
            R(pal["dark"], (mx(17, 8), 36, 8, 16), 2); R(pal["mid"], (mx(18, 6), 37, 6, 13), 1)
            R(pal["visor"], (mx(20, 4), 43, 4, 3), 1); R(pal["trim"], (mx(17, 8), 50, 8, 3), 1)
        elif step == 1:
            R(pal["dark"], (mx(10, 7), 38, 7, 13), 2); R(pal["dark"], (mx(23, 8), 36, 8, 16), 2)
            R(pal["mid"], (mx(24, 6), 37, 6, 13), 1); R(pal["visor"], (mx(25, 4), 43, 4, 3), 1)
            R(pal["trim"], (mx(23, 8), 50, 8, 3), 1)
        else:
            R(pal["dark"], (mx(23, 7), 38, 7, 13), 2); R(pal["dark"], (mx(11, 8), 36, 8, 16), 2)
            R(pal["mid"], (mx(12, 6), 37, 6, 13), 1); R(pal["visor"], (mx(13, 4), 43, 4, 3), 1)
            R(pal["trim"], (mx(11, 8), 50, 8, 3), 1)
    elif direction == "up":
        pairs = ((12, 36, 16), (25, 36, 16)) if step == 0 else (((11, 35, 13), (25, 36, 17)) if step == 1 else ((11, 36, 17), (25, 35, 13)))
        for lx, ly, lh in pairs:
            R(pal["dark"], (lx, ly, 7, lh), 2); R(pal["mid"], (lx + 1, ly + 1, 5, max(4, lh - 4)), 1)
            R(PX_DARK, (lx + 2, ly + 3, 3, max(2, lh - 7)), 1)
            R(pal["visor"], (lx + 2, ly + lh - 5, 3, 2), 1); R(pal["trim"], (lx, ly + lh - 3, 7, 3), 1)
    else:
        pairs = ((12, 36, 16), (25, 36, 16)) if step == 0 else (((11, 36, 17), (25, 35, 13)) if step == 1 else ((11, 35, 13), (25, 36, 17)))
        for lx, ly, lh in pairs:
            R(pal["dark"], (lx, ly, 7, lh), 2); R(pal["mid"], (lx + 1, ly + 1, 5, max(4, lh - 4)), 1)
            L(pal["light"], (lx + 2, ly + 2), (lx + 2, ly + lh - 4), 1)
            R(pal["visor"], (lx + 2, ly + lh // 2, 3, 3), 1); R(pal["trim"], (lx, ly + lh - 3, 7, 3), 1)

    surface.blit(layer, (0, 0))


def draw_helmet_overlay_076(app, surface, raw_width, raw_height, design_id, pose="world", direction="down"):
    data = HELMET_DESIGNS.get(design_id, HELMET_DESIGNS["tactical"])
    pal = EquipmentPaletteSampler076.get_palette("helmet")
    sx = surface.get_width() / max(1, raw_width)
    sy = surface.get_height() / max(1, raw_height)
    shell = data.get("shell", pal["mid"])
    shell_dark = (max(0, shell[0] - 22), max(0, shell[1] - 22), max(0, shell[2] - 22))
    visor = data.get("visor", pal["visor"])
    accent = data.get("accent", pal["trim"])
    layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

    def P(x, y):
        return (int(x * sx), int(y * sy))
    def R(color, rect, radius=0):
        rr = pygame.Rect(int(rect[0] * sx), int(rect[1] * sy), max(1, int(rect[2] * sx)), max(1, int(rect[3] * sy)))
        pygame.draw.rect(layer, color, rr, border_radius=max(0, int(radius * min(sx, sy))))
    def L(color, a, b, width=1):
        pygame.draw.line(layer, color, P(*a), P(*b), max(1, int(width * min(sx, sy))))
    def Poly(color, pts):
        pygame.draw.polygon(layer, color, [P(*pt) for pt in pts])

    if pose == "combat":
        Poly(shell_dark, [(27, 7), (30, 1), (44, 1), (48, 7), (47, 16), (41, 18), (32, 18), (28, 15)])
        Poly(shell, [(29, 7), (31, 2), (43, 2), (46, 7), (45, 15), (40, 17), (33, 17), (30, 14)])
        L(pal["light"], (32, 3), (42, 3), 2); R(PX_DARK, (30, 7, 15, 5), 1); R(visor, (31, 8, 13, 3), 1); L(accent, (30, 13), (44, 13), 1)
    elif direction == "up":
        Poly(shell_dark, [(14, 7), (16, 1), (28, 1), (30, 7), (29, 16), (15, 16)])
        Poly(shell, [(15, 7), (17, 2), (27, 2), (29, 7), (28, 15), (16, 15)])
        L(pal["light"], (18, 3), (26, 3), 2); R(shell_dark, (18, 6, 8, 7), 1); L(accent, (17, 13), (27, 13), 2); R(PX_DARK, (21, 5, 2, 8), 1)
    elif direction in ("left", "right"):
        is_left = (direction == "left")
        def mx(x_val, w_val=0):
            return (44 - x_val - w_val) if is_left else x_val
        def mpt(pt):
            return (44 - pt[0], pt[1]) if is_left else pt
        Poly(shell_dark, [mpt((14, 7)), mpt((17, 1)), mpt((28, 1)), mpt((31, 8)), mpt((30, 15)), mpt((24, 17)), mpt((15, 15))])
        Poly(shell, [mpt((15, 7)), mpt((18, 2)), mpt((27, 2)), mpt((30, 8)), mpt((29, 14)), mpt((24, 16)), mpt((16, 14))])
        L(pal["light"], mpt((18, 3)), mpt((26, 3)), 2)
        R(PX_DARK, (mx(22, 8), 7, 8, 5), 1); R(visor, (mx(23, 7), 8, 7, 3), 1); L(accent, mpt((18, 13)), mpt((28, 13)), 1)
    else:
        Poly(shell_dark, [(14, 7), (16, 1), (28, 1), (30, 7), (29, 15), (25, 17), (19, 17), (15, 15)])
        Poly(shell, [(15, 7), (17, 2), (27, 2), (29, 7), (28, 14), (24, 16), (20, 16), (16, 14)])
        L(pal["light"], (18, 3), (26, 3), 2); R(PX_DARK, (16, 7, 12, 5), 1); R(visor, (17, 8, 10, 3), 1); L(accent, (17, 13), (27, 13), 1)

    surface.blit(layer, (0, 0))


# ==============================================================================
# SISTEMA DE CARTAS 0.7.7: TEMPLATE SCI-FI TCG HOLOGRAFICO + MODERNGL NEON GLOW
# ==============================================================================

def get_rarity_neon_color_077(rarity: str):
    return RARITY_NEON_GLOW_COLORS.get(rarity or "Comum", (255, 255, 255))


def compute_tcg_zones_077(rect: pygame.Rect):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    pad_x = max(7, int(w * 0.045))
    if h >= 350:
        art_top = y + 26
        art_h = int(h * 0.28)
        name_h = 32
        name_top = art_top + art_h + 6
        info_top = name_top + name_h + 6
        info_h = max(36, (y + h) - info_top - 10)
    elif h >= 180:
        art_top = y + 10
        art_h = int(h * 0.36)
        name_h = 24
        name_top = art_top + art_h + 4
        info_top = name_top + name_h + 4
        info_h = max(24, (y + h) - info_top - 8)
    else:
        art_top = y + 6
        art_h = max(32, int(h * 0.36))
        name_h = max(19, int(h * 0.19))
        name_top = art_top + art_h + 3
        info_top = name_top + name_h + 3
        info_h = max(18, (y + h) - info_top - 6)

    art_rect = pygame.Rect(x + pad_x, art_top, w - pad_x * 2, art_h)
    name_bar_rect = pygame.Rect(x + pad_x, name_top, w - pad_x * 2, name_h)
    info_box_rect = pygame.Rect(x + pad_x, info_top, w - pad_x * 2, info_h)
    return art_rect, name_bar_rect, info_box_rect


def draw_upgrade_diamond_077(app, rect: pygame.Rect, variant: str, neon_col=(255, 255, 255)):
    v = (variant or "normal").lower()
    if v in ("plus", "+"):
        symbol = "+"
    elif v in ("plusplus", "++"):
        symbol = "++"
    else:
        return

    box = pygame.Rect(rect)
    r = 12 if box.height < 160 else 16
    cx = box.right - r - 4
    cy = box.bottom - r - 4

    pts_outer = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    r_in = max(4, r - 3)
    pts_inner = [(cx, cy - r_in), (cx + r_in, cy), (cx, cy + r_in), (cx - r_in, cy)]

    pygame.draw.polygon(app.canvas, (6, 16, 26), pts_outer)
    pygame.draw.polygon(app.canvas, (14, 34, 48), pts_inner)
    pygame.draw.polygon(app.canvas, neon_col, pts_outer, 2)
    pygame.draw.polygon(app.canvas, (185, 248, 255), pts_inner, 1)

    f_size = 11 if symbol == "++" and r <= 12 else (13 if r <= 12 else 15)
    fnt = app.font(f_size)
    txt_surf = fnt.render(symbol, True, (245, 255, 255))
    app.canvas.blit(txt_surf, (cx - txt_surf.get_width() // 2, cy - txt_surf.get_height() // 2))


def draw_tcg_card_frame_077(app, rect, rarity="Comum", cache_tag=None):
    box = pygame.Rect(rect)
    w, h = box.width, box.height
    hover = box.collidepoint(app.mouse())
    neon_col = get_rarity_neon_color_077(rarity)
    dim_col = tuple(max(25, int(c * 0.45)) for c in neon_col)

    local_box = pygame.Rect(0, 0, w, h)
    art_local, name_local, info_local = compute_tcg_zones_077(local_box)

    card_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cut = min(12, max(6, min(w, h) // 12))
    outer_pts = [
        (cut, 1), (w - cut - 1, 1), (w - 2, cut),
        (w - 2, h - cut - 1), (w - cut - 1, h - 2),
        (cut, h - 2), (1, h - cut - 1), (1, cut)
    ]

    pygame.draw.polygon(card_surf, (8, 18, 28, 248) if not hover else (12, 26, 40, 252), outer_pts)

    trace_col = (*neon_col, 42 if not hover else 68)
    node_col = (*neon_col, 95)
    for offset_y in (art_local.centery, name_local.centery, info_local.centery):
        pygame.draw.lines(card_surf, trace_col, False, [(2, offset_y), (art_local.left - 2, offset_y)], 1)
        pygame.draw.lines(card_surf, trace_col, False, [(art_local.right + 2, offset_y), (w - 3, offset_y)], 1)
        pygame.draw.circle(card_surf, node_col, (max(3, art_local.left - 3), int(offset_y)), 2)
        pygame.draw.circle(card_surf, node_col, (min(w - 4, art_local.right + 3), int(offset_y)), 2)

    pygame.draw.lines(card_surf, trace_col, False, [(cut + 4, 4), (cut + 14, 14), (w - cut - 14, 14), (w - cut - 4, 4)], 1)
    pygame.draw.lines(card_surf, trace_col, False, [(cut + 4, h - 5), (cut + 14, h - 15), (w - cut - 14, h - 15), (w - cut - 4, h - 5)], 1)

    pygame.draw.rect(card_surf, (5, 12, 20, 235), art_local, border_radius=4)
    g_step = max(12, art_local.width // 8)
    for gx in range(art_local.left + g_step, art_local.right, g_step):
        pygame.draw.line(card_surf, (*neon_col, 20), (gx, art_local.top + 1), (gx, art_local.bottom - 1), 1)
    for gy in range(art_local.top + 10, art_local.bottom, 12):
        pygame.draw.line(card_surf, (*neon_col, 20), (art_local.left + 1, gy), (art_local.right - 1, gy), 1)
    pygame.draw.rect(card_surf, (*dim_col, 225), art_local, 1, border_radius=4)

    pygame.draw.rect(card_surf, (12, 22, 34, 248), name_local, border_radius=4)
    pygame.draw.rect(card_surf, (*neon_col, 255), name_local, 2, border_radius=4)
    pygame.draw.rect(card_surf, (*neon_col, 255), (name_local.left + 2, name_local.top + 3, 3, max(2, name_local.height - 6)))
    pygame.draw.rect(card_surf, (*neon_col, 255), (name_local.right - 5, name_local.top + 3, 3, max(2, name_local.height - 6)))

    pygame.draw.rect(card_surf, (6, 14, 22, 218), info_local, border_radius=4)
    pygame.draw.rect(card_surf, (*dim_col, 195), info_local, 1, border_radius=4)
    pygame.draw.line(card_surf, (*neon_col, 28), (info_local.left + 6, info_local.top + 5), (info_local.right - 18, info_local.top + 5), 1)
    pygame.draw.circle(card_surf, (*neon_col, 55), (info_local.right - 14, info_local.top + 5), 2)
    pygame.draw.line(card_surf, (*neon_col, 28), (info_local.left + 18, info_local.bottom - 5), (info_local.right - 6, info_local.bottom - 5), 1)
    pygame.draw.circle(card_surf, (*neon_col, 55), (info_local.left + 14, info_local.bottom - 5), 2)

    pygame.draw.polygon(card_surf, (*neon_col, 235 if hover else 190), outer_pts, 2)

    hud_renderer = getattr(app, "combat_hud_renderer", None)
    if hud_renderer is not None and getattr(hud_renderer, "available", False):
        card_surf = hud_renderer.apply_tcg_card_glow(
            card_surf,
            rarity_color=neon_col,
            name_bar_rect=(name_local.x, name_local.y, name_local.width, name_local.height),
            time=getattr(app, "frame", 0.0),
            cache_tag=cache_tag or (rarity, hover),
        )
    else:
        glow_rect = name_local.inflate(6, 6)
        pygame.draw.rect(card_surf, (*neon_col, 85), glow_rect, 3, border_radius=6)

    app.canvas.blit(card_surf, box.topleft)
    return compute_tcg_zones_077(box)


def render_complete_tcg_card_077(
    app,
    rect,
    *,
    rarity="Comum",
    title="CARTA",
    element=None,
    species=None,
    variant="normal",
    is_unique=False,
    top_left_badge=None,
    info_lines=None,
    enabled=True,
):
    box = pygame.Rect(rect)
    effective_rarity = "Única" if is_unique else (rarity or "Comum")
    neon_col = get_rarity_neon_color_077(effective_rarity)
    art_rect, name_rect, info_rect = draw_tcg_card_frame_077(app, box, effective_rarity)

    clean_title = str(title or "").strip()
    inferred_variant = variant or "normal"
    if clean_title.endswith("++"):
        inferred_variant = "plusplus"
        clean_title = clean_title[:-2].strip()
    elif clean_title.endswith("+"):
        inferred_variant = "plus"
        clean_title = clean_title[:-1].strip()

    if top_left_badge:
        app.label(str(top_left_badge), art_rect.x + 6, art_rect.y + 3, 10, neon_col)

    if is_unique or effective_rarity in ("Única", "Unica"):
        logo_r = max(8, min(art_rect.width, art_rect.height) // 3 + 2)
        app.draw_element_symbol(element, art_rect.center, logo_r, glow=True)
    else:
        spr = app.sprites.get((species, 0)) if species else None
        if spr is not None:
            max_w = max(12, art_rect.width - 36)
            max_h = max(12, art_rect.height - 6)
            scale = min(max_w / max(1, spr.get_width()), max_h / max(1, spr.get_height()))
            sw = max(1, int(spr.get_width() * scale))
            sh = max(1, int(spr.get_height() * scale))
            im = pygame.transform.scale(spr, (sw, sh))
            app.canvas.blit(im, (art_rect.centerx - sw // 2, art_rect.centery - sh // 2 + 1))
        elif element is None:
            pygame.draw.circle(app.canvas, (32, 165, 195), art_rect.center, min(14, art_rect.height // 2 - 3), 2)
            pygame.draw.circle(app.canvas, (195, 252, 255), art_rect.center, min(6, art_rect.height // 4))

        if element:
            badge_r = 6 if box.height < 140 else (8 if box.height < 260 else 11)
            app.draw_element_symbol(element, (art_rect.right - badge_r - 8, art_rect.centery), badge_r, glow=False)

    name_font_size = 11 if box.height < 130 else (12 if box.height < 240 else 15)
    f_name = app.font(name_font_size)
    fitted_name = app.fit_text(clean_title, name_font_size, max(24, name_rect.width - 16))
    name_color = (242, 252, 255) if enabled else (130, 152, 160)
    n_surf = f_name.render(fitted_name, True, name_color)
    app.canvas.blit(
        n_surf,
        (name_rect.centerx - n_surf.get_width() // 2, name_rect.centery - n_surf.get_height() // 2),
    )

    if info_lines:
        iy = info_rect.y + 3
        for line_item in info_lines:
            if isinstance(line_item, tuple):
                l_txt, l_col, l_sz = line_item
            else:
                l_txt, l_col, l_sz = str(line_item), (218, 245, 248) if enabled else (120, 145, 152), 9
            if iy + l_sz <= info_rect.bottom - 1:
                fitted_line = app.fit_text(str(l_txt), l_sz, max(20, info_rect.width - 28))
                app.label(fitted_line, info_rect.x + 8, iy, l_sz, l_col)
                iy += l_sz + 3

    draw_upgrade_diamond_077(app, box, inferred_variant, neon_col=neon_col)
    return art_rect, name_rect, info_rect


def draw_element_symbol_077(app, element, center, size, glow=False):
    if element not in app.ELEMENT_COLORS:
        return
    cx, cy = int(center[0]), int(center[1])
    r = max(4, int(size))
    if r <= 7:
        r = int(round(r * 1.65))
    elif r <= 10:
        r = int(round(r * 1.30))

    color = app.ELEMENT_COLORS[element]
    badge = getattr(app, "element_badges", {}).get(element)
    if badge is not None:
        target = max(14, int(r * 2))
        scale = min(target / max(1, badge.get_width()), target / max(1, badge.get_height()))
        w = max(1, int(round(badge.get_width() * scale)))
        h = max(1, int(round(badge.get_height() * scale)))
        scaled = pygame.transform.smoothscale(badge, (w, h))

        backing = pygame.Surface(app.canvas.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(backing, (7, 16, 24, 225), (cx, cy), max(w, h) // 2 + 2)
        pygame.draw.circle(backing, (*color, 210 if glow else 155), (cx, cy), max(w, h) // 2 + 2, 1)
        if glow:
            pygame.draw.circle(backing, (*color, 65), (cx, cy), int(target * 0.72))
        app.canvas.blit(backing, (0, 0))
        app.canvas.blit(scaled, (cx - w // 2, cy - h // 2))
        return


# ==============================================================================
# SUBSTITUICAO UNIVERSAL DE TODAS AS TELAS DE CARTAS DO JOGO (0.7.7)
# ==============================================================================

def draw_slot_card_077(app, rect, cid, slot_label, rarity_override=None):
    rect = pygame.Rect(rect)
    rarity = rarity_override or "Comum"
    card = None
    variant = "normal"
    is_unique = False

    if cid:
        try:
            card, variant_data, _, variant = app.state.card_data(cid)
            is_unique = app.state.is_unique_card(cid)
            rarity = "Única" if is_unique else card.get("rarity", rarity)
        except ValueError:
            cid = None

    if not cid or not card:
        render_complete_tcg_card_077(
            app,
            rect,
            rarity=rarity,
            title="SLOT VAZIO",
            element=None,
            species=None,
            variant="normal",
            is_unique=(rarity == "Única"),
            top_left_badge=slot_label,
            info_lines=[("CLIQUE PARA EQUIPAR CARTA", (149, 167, 169), 9)],
            enabled=False,
        )
        return

    info_lines = []
    if is_unique:
        u_data = app.state.unique_cards.get(cid, {})
        mult = UNIQUE_VARIANT_MULTIPLIERS.get(variant, 1.0)
        buff_strs = [app._unique_buff_text(b, mult) for b in u_data.get("buffs", [])[:2]]
        if buff_strs:
            info_lines.append((" | ".join(buff_strs), (236, 187, 100), 9))
        if u_data.get("momentum") in UNIQUE_MOMENTUM_DEFS:
            info_lines.append(("MOMENTUM ATIVO", (86, 215, 197), 8))
    else:
        stat_str = f"MEM {card.get('cost', 0)}   |   DANO {card['damage'][0]}-{card['damage'][1]}"
        bonus = app.card_bonus_lines(card.get("attributes", {}))
        if bonus:
            stat_str += "   |   " + " ".join(bonus[:2])
        info_lines.append((stat_str, (86, 215, 197), 9))

    render_complete_tcg_card_077(
        app,
        rect,
        rarity=rarity,
        title=format_card_name(card["name"]),
        element=card.get("type"),
        species=card.get("species"),
        variant=variant,
        is_unique=is_unique,
        top_left_badge=slot_label,
        info_lines=info_lines,
        enabled=True,
    )


def draw_mini_card_077(app, rect, cid, slot_number):
    draw_slot_card_077(app, rect, cid, f"SLOT {slot_number}")


def card_collection_view_077(app):
    rarity_order = {rarity: idx for idx, rarity in enumerate(CARD_RARITIES)}
    cards = [(cid, card, "regular") for cid, card in CARDS.items() if cid in app.state.known_cards]
    cards = [item for item in cards if item[1].get("rarity") in CARD_RARITIES]
    cards.sort(key=lambda item: (
        rarity_order.get(item[1].get("rarity", "Comum"), 0),
        item[1].get("type", ""),
        format_card_name(item[1].get("name", "")).casefold(),
        item[0]
    ))
    page_count = max(1, (len(cards) + 2) // 3)
    app.album_page = max(0, min(app.album_page, page_count - 1))
    shown = cards[app.album_page * 3 : app.album_page * 3 + 3]

    for local_i, (cid, c, _kind) in enumerate(shown):
        x = (25, 405, 785)[local_i]
        card_rect = pygame.Rect(x, 180, 365, 472)
        rarity = c.get("rarity", "Comum")
        neon_col = get_rarity_neon_color_077(rarity)

        counts = app._card_variant_counts(cid)
        best_variant = "plusplus" if counts.get("plusplus", 0) > 0 else ("plus" if counts.get("plus", 0) > 0 else "normal")

        art_rect, name_rect, info_rect = render_complete_tcg_card_077(
            app,
            card_rect,
            rarity=rarity,
            title=format_card_name(c.get("name", "Carta")),
            element=c.get("type"),
            species=c.get("species"),
            variant=best_variant,
            is_unique=(rarity == "Única"),
            top_left_badge=f"{rarity.upper()}  •  {c.get('type', '-').upper()}",
            info_lines=None,
            enabled=True,
        )

        desc_rect = pygame.Rect(info_rect.x + 8, info_rect.y + 8, info_rect.width - 16, 142)
        app._draw_scroll_text_box(desc_rect, c.get("description", ""), f"card_effect_{local_i}", 10, (230, 234, 226), 14)

        stat_y = desc_rect.bottom + 8
        app.label(f"MEM {c.get('cost', 0)}   |   DANO {c.get('damage', (0, 0))[0]}-{c.get('damage', (0, 0))[1]}", info_rect.x + 10, stat_y, 11, (86, 215, 197))

        bonus_lines = app.card_bonus_lines(c.get("attributes", {}))
        if bonus_lines:
            bonus_rect = pygame.Rect(info_rect.x + 8, stat_y + 20, info_rect.width - 16, 40)
            app._draw_scroll_text_box(bonus_rect, "BONUS: " + "  |  ".join(bonus_lines), f"card_bonus_{local_i}", 9, (236, 187, 100), 12)

        available = sum(1 for inst in app.state.card_instances(cid) if inst not in app.state.slots)
        foot_y = info_rect.bottom - 22
        app.label(f"N {counts['normal']}   + {counts['plus']}   ++ {counts['plusplus']}", info_rect.x + 10, foot_y, 9, (149, 167, 169))
        app.label(f"DISPONIVEIS: {available}", info_rect.x + 165, foot_y, 9, (86, 215, 197) if available else (149, 167, 169))

        draw_upgrade_diamond_077(app, card_rect, best_variant, neon_col=neon_col)

    if not cards:
        app.label("NENHUMA CARTA DESCOBERTA", 420, 350, 20, (149, 167, 169))
    app.label(f"PAGINA {app.album_page + 1}/{page_count}", 480, 692, 12, (86, 215, 197))
    app.button((35, 680, 170, 38), "< ANTERIOR", lambda: setattr(app, "album_page", app.album_page - 1), app.album_page > 0)
    app.button((995, 680, 170, 38), "PROXIMA >", lambda: setattr(app, "album_page", app.album_page + 1), app.album_page < page_count - 1)


def card_picker_077(app):
    slot = app.card_picker_slot
    if slot is None:
        return
    special = slot == "special"
    slot_label = "SLOT UNICO" if special else f"SLOT {slot + 1}"
    app.panel_header("SELECIONAR CARTA", f"Escolha a carta que ocupara o {slot_label}.")
    app.box((55, 108, 1090, 556), (9, 17, 24), (54, 76, 86))
    app.label(slot_label, 78, 130, 16, (236, 187, 100))
    app.label("Cartas disponiveis na Pool.", 195, 131, 12, (149, 167, 169))
    app.button((915, 121, 205, 36), "CANCELAR", app.close_card_picker, True)

    cards = []
    current = getattr(app.state, "gauntlet_special_slot", None) if special else app.state.slots[int(slot)]
    cards.append(("__empty__", None, None, None, None, current is None))
    for cid in app.state.crafted:
        if special and not app.state.is_unique_card(cid):
            continue
        if not special and app.state.is_unique_card(cid):
            continue
        try:
            card, variant_data, base_id, variant = app.state.card_data(cid)
        except ValueError:
            continue
        equipped = cid == current
        if not special and cid in app.state.slots and app.state.slots.index(cid) != int(slot):
            continue
        cards.append((cid, card, variant_data, base_id, variant, equipped))

    rarity_order = {rarity: idx for idx, rarity in enumerate(CARD_RARITIES)}
    cards[1:] = sorted(
        cards[1:],
        key=lambda item: (
            rarity_order.get(item[1].get("rarity", "Comum"), 0),
            item[1].get("type", ""),
            format_card_name(item[1].get("name", "")).casefold(),
            item[4],
            item[0],
        ),
    )

    view = pygame.Rect(78, 174, 645, 420)
    row_h = 70
    max_scroll = max(0, len(cards) * row_h - view.height)
    app.ui_scroll["card_picker"] = max(0, min(app.ui_scroll.get("card_picker", 0), max_scroll))
    selected = app.card_picker_selection
    app.canvas.set_clip(view)
    y = view.y - int(app.ui_scroll["card_picker"])
    for cid, card, variant_data, _base_id, variant, equipped in cards:
        rect = pygame.Rect(view.x, y, view.width - 16, 58)
        chosen = cid == selected
        if cid == "__empty__":
            app.box(rect, (17, 35, 38) if chosen else (12, 22, 29), (86, 215, 197) if chosen else (236, 187, 100))
            app.label("SLOT VAZIO", rect.x + 14, rect.y + 8, 14, (230, 234, 226))
            app.label("Desequipar e devolver a carta atual a Pool.", rect.x + 14, rect.y + 31, 10, (149, 167, 169))
        else:
            rarity = "Única" if special else card.get("rarity", "Comum")
            neon_col = get_rarity_neon_color_077(rarity)
            app.box(rect, (18, 37, 39) if chosen or equipped else (15, 25, 32), (86, 215, 197) if chosen else neon_col)
            app.label(app.fit_text(format_card_name(card["name"]) + variant_data["label"], 14, 350), rect.x + 14, rect.y + 7, 14, (230, 234, 226))
            app.label(
                f"{rarity} • {card.get('type', '-')} • " + ("Carta Unica" if special else f"MEM {card['cost']} • DANO {card['damage'][0]}-{card['damage'][1]}"),
                rect.x + 14,
                rect.y + 30,
                10,
                neon_col,
            )
            app.draw_element_symbol(card.get("type"), (rect.right - 125, rect.y + 29), 6)
            draw_upgrade_diamond_077(app, rect, variant, neon_col=neon_col)
            status = "SELECIONADA" if chosen else ("ATUAL" if equipped else "DISPONIVEL")
            app.label(status, rect.right - 105, rect.y + 10, 9, (86, 215, 197) if chosen else ((236, 187, 100) if equipped else (149, 167, 169)))
        app.buttons.append((rect, lambda inst=cid: app.select_card_for_picker(inst), True))
        y += row_h
    app.canvas.set_clip(None)
    app._draw_scrollbar((705, 174, 9, 420), app.ui_scroll["card_picker"], max_scroll)
    app._register_scrollbar("card_picker", (705, 174, 9, 420), app.ui_scroll["card_picker"], max_scroll)

    preview = pygame.Rect(742, 174, 364, 420)
    app.box(preview, (7, 15, 22), (54, 76, 86))
    app.label("PRE-VISUALIZACAO", 760, 192, 14, (86, 215, 197))
    if not selected:
        app.label("Selecione uma carta.", 760, 236, 12, (149, 167, 169))
    elif selected == "__empty__":
        app.label("SLOT VAZIO", 760, 236, 20, (236, 187, 100))
        app.wrap("O slot ficara livre e a carta atualmente equipada retornara a Pool.", 760, 274, 315, 11, (230, 234, 226), 16)
    else:
        try:
            card, variant_data, _base_id, variant = app.state.card_data(selected)
        except ValueError:
            card, variant_data, variant = None, None, "normal"
        if card:
            is_uniq = app.state.is_unique_card(selected)
            rarity = "Única" if is_uniq else card.get("rarity", "Comum")
            neon_col = get_rarity_neon_color_077(rarity)
            p_lines = [
                (f"{card.get('type', '-')}", neon_col, 9),
                (f"MEM {card.get('cost', 0)} | {card.get('damage', (0, 0))[0]}-{card.get('damage', (0, 0))[1]}", (86, 215, 197), 9),
            ]
            render_complete_tcg_card_077(
                app,
                pygame.Rect(758, 218, 154, 225),
                rarity=rarity,
                title=format_card_name(card.get("name", "Carta")),
                element=card.get("type"),
                species=card.get("species"),
                variant=variant,
                is_unique=is_uniq,
                top_left_badge=rarity.upper(),
                info_lines=p_lines,
                enabled=True,
            )
            if is_uniq:
                u = app.state.unique_cards.get(selected, {})
                mult = UNIQUE_VARIANT_MULTIPLIERS.get(variant, 1.0)
                effects = [app._unique_buff_text(b, mult) for b in u.get("buffs", []) if isinstance(b, dict)]
                mom = u.get("momentum")
                if mom in UNIQUE_MOMENTUM_DEFS:
                    effects.append("Momentum - " + UNIQUE_MOMENTUM_DEFS[mom]["description"].format(type=card.get("type", "-")))
                detail = chr(10).join(effects) if effects else "Nenhum efeito aplicado."
            else:
                detail = card.get("description", "Sem descricao.")
            app._draw_scroll_text_box((922, 218, 168, 225), detail, "card_picker_preview", 9, (230, 234, 226), 13, neon_col)

    app.button((850, 610, 235, 44), "EQUIPAR", app.equip_selected_card_from_picker, selected is not None)
    app.label("Clique uma vez para selecionar; a pre-visualizacao atualiza a direita.", 78, 617, 10, (149, 167, 169))


def redraw_combat_cards_077(app):
    enabled = app.phase == "choose"
    lo, hi, _, _, _, _, _, _ = app.state._player_attack_profile("basic")
    card_y, card_w, card_h, gap = 535, 210, 118, 10

    for idx in range(4):
        rect = pygame.Rect(30 + idx * (card_w + gap), card_y, card_w, card_h)
        if idx == 0:
            render_complete_tcg_card_077(
                app,
                rect,
                rarity="Comum",
                title="RAIO DE PLASMA",
                element=None,
                species=None,
                variant="normal",
                is_unique=False,
                top_left_badge="[1] BASICO",
                info_lines=[
                    (f"DANO {lo}-{hi}  |  SEM CUSTO", (86, 215, 197), 9),
                ],
                enabled=enabled,
            )
            continue

        slot_idx = idx - 1
        cid = app.state.slots[slot_idx]
        can_use = False
        card = None
        variant = "normal"
        if cid:
            try:
                card, _variant_data, _, variant = app.state.card_data(cid)
                can_use = enabled and app.state.memory >= int(card.get("cost", 0))
            except ValueError:
                card = None
                cid = None

        if not cid or not card:
            render_complete_tcg_card_077(
                app,
                rect,
                rarity="Comum",
                title="SLOT VAZIO",
                element=None,
                species=None,
                variant="normal",
                is_unique=False,
                top_left_badge=f"[{idx + 1}] VAZIO",
                info_lines=[("EQUIPE NA MANOPLA", (149, 167, 169), 9)],
                enabled=False,
            )
            continue

        is_uniq = app.state.is_unique_card(cid)
        rarity = "Única" if is_uniq else card.get("rarity", "Comum")
        stat_col = (86, 215, 197) if can_use else (130, 150, 158)
        render_complete_tcg_card_077(
            app,
            rect,
            rarity=rarity,
            title=format_card_name(card["name"]),
            element=card.get("type"),
            species=card.get("species"),
            variant=variant,
            is_unique=is_uniq,
            top_left_badge=f"[{idx + 1}] {rarity.upper()}",
            info_lines=[
                (f"MEM {card.get('cost', 0)}   |   DANO {card.get('damage', (0, 0))[0]}-{card.get('damage', (0, 0))[1]}", stat_col, 9),
            ],
            enabled=can_use,
        )


# ==============================================================================
# NAVE EXTERIOR E INTERIOR + MONSTROS + TELA INICIAL (MANTIDOS DA 0.7.6)
# ==============================================================================

def draw_ship_exterior_076(app, x, y, shadow=True):
    s = app.canvas
    pulse = 0.5 + 0.5 * math.sin(getattr(app, "frame", 0.0) * 4.2)
    if shadow:
        sh = pygame.Surface((164, 56), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (15, 12, 14, 135), (0, 8, 164, 44))
        pygame.draw.ellipse(sh, (38, 28, 24, 90), (20, 14, 124, 32))
        s.blit(sh, (int(x - 82), int(y - 8)))

    for gx, gy in ((x - 46, y + 18), (x + 42, y + 18), (x + 4, y + 25)):
        pygame.draw.line(s, (88, 102, 114), (gx, gy - 14), (gx - 4, gy + 6), 3)
        pygame.draw.rect(s, (52, 64, 74), (gx - 11, gy + 4, 16, 5), border_radius=2)
        pygame.draw.line(s, PX_CYAN, (gx - 9, gy + 6), (gx + 3, gy + 6), 1)

    for ny_off in (-16, 12):
        pygame.draw.polygon(s, (42, 56, 68), [(x - 78, y + ny_off - 4), (x - 42, y + ny_off - 8), (x - 42, y + ny_off + 8), (x - 78, y + ny_off + 6)])
        glow_r = int(6 + 3 * pulse)
        pygame.draw.circle(s, (32, 185, 215), (int(x - 76), int(y + ny_off + 1)), glow_r)
        pygame.draw.circle(s, (195, 255, 255), (int(x - 76), int(y + ny_off + 1)), max(2, glow_r // 2))

    pygame.draw.polygon(s, (48, 64, 78), [(x - 68, y + 6), (x - 28, y - 24), (x + 36, y - 22), (x + 78, y + 4), (x + 46, y + 24), (x - 48, y + 24)])
    pygame.draw.polygon(s, (78, 96, 112), [(x - 58, y + 4), (x - 22, y - 18), (x + 34, y - 16), (x + 68, y + 3), (x + 40, y + 18), (x - 40, y + 18)])
    pygame.draw.polygon(s, (124, 142, 156), [(x - 46, y - 4), (x - 14, y - 15), (x + 44, y - 12), (x + 74, y + 2), (x + 42, y + 12), (x - 36, y + 12)])
    pygame.draw.line(s, (210, 225, 235), (x - 28, y - 8), (x + 42, y - 8), 2)
    pygame.draw.line(s, PX_GOLD, (x - 32, y + 8), (x + 34, y + 8), 2)
    pygame.draw.polygon(s, (16, 38, 52), [(x + 12, y - 11), (x + 44, y - 9), (x + 64, y + 1), (x + 42, y + 7), (x + 14, y + 5)])
    pygame.draw.polygon(s, (56, 198, 220), [(x + 16, y - 9), (x + 42, y - 7), (x + 56, y), (x + 40, y + 4), (x + 18, y + 3)], 1)
    pygame.draw.line(s, (190, 250, 255), (x + 22, y - 6), (x + 44, y - 4), 2)
    pygame.draw.polygon(s, (64, 84, 98), [(x - 12, y - 8), (x + 2, y - 28), (x + 18, y - 8)])
    pygame.draw.circle(s, PX_CYAN_HI if pulse > 0.5 else PX_CYAN, (int(x + 3), int(y - 24)), 3)
    pygame.draw.rect(s, (24, 34, 42), (x - 12, y + 8, 22, 11), border_radius=2)
    pygame.draw.rect(s, PX_GOLD, (x - 12, y + 8, 22, 11), 1, border_radius=2)


def draw_ship_interior_076(app):
    s = app.canvas
    t = getattr(app, "frame", 0.0)
    pulse = 0.5 + 0.5 * math.sin(t * 3.2)

    s.fill((5, 10, 18))
    for sx, sy, sr, sph, ssp in getattr(app, "title_stars", [])[:45]:
        tw = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * ssp * 2.0 + sph))
        pygame.draw.circle(s, (int(140 * tw + 60), int(185 * tw + 50), 235), (sx, sy), sr)

    app.label("NAVE CORVETA V-7 // CONVES INTERNO", 35, 24, 26, (86, 215, 197))
    app.label("ESTACOES TATICAS E BIO-ESTASE ONLINE", 35, 62, 13, (149, 167, 169))

    hull_outer = [(130, 650), (130, 230), (220, 135), (360, 92), (840, 92), (980, 135), (1070, 230), (1070, 650)]
    hull_inner = [(158, 632), (158, 244), (242, 154), (372, 114), (828, 114), (958, 154), (1042, 244), (1042, 632)]
    pygame.draw.polygon(s, (34, 48, 60), hull_outer); pygame.draw.polygon(s, (78, 112, 132), hull_outer, 3)
    pygame.draw.polygon(s, (14, 22, 32), hull_inner); pygame.draw.polygon(s, (46, 88, 108), hull_inner, 2)

    tile_w, tile_h = 54, 52
    grid_ox, grid_oy = 276, 152
    for gx in range(12):
        for gy in range(9):
            tx = grid_ox + gx * tile_w
            ty = grid_oy + gy * tile_h
            if (gx, gy) in SHIP_INTERIOR["solid"]:
                continue
            tile_rect = pygame.Rect(tx, ty, tile_w - 2, tile_h - 2)
            is_corridor = 3 <= gx <= 8 and 2 <= gy <= 7
            pygame.draw.rect(s, (24, 36, 48) if is_corridor else (18, 28, 38), tile_rect, border_radius=3)
            pygame.draw.rect(s, (36, 54, 68), tile_rect, 1, border_radius=3)
            pygame.draw.line(s, (30, 44, 56), (tx + 8, ty + tile_h // 2), (tx + tile_w - 10, ty + tile_h // 2), 1)

    conduit_col = (42, int(170 + 55 * pulse), 215)
    pygame.draw.lines(s, conduit_col, False, [(600, 245), (600, 420), (384, 420)], 2)
    pygame.draw.lines(s, conduit_col, False, [(600, 420), (816, 420)], 2)
    pygame.draw.lines(s, (30, int(205 + 45 * pulse), 175), False, [(600, 420), (600, 560), (438, 560)], 2)
    pygame.draw.lines(s, (228, 176, 86), False, [(600, 560), (762, 560)], 2)

    cockpit_surf = pygame.Surface((320, 145), pygame.SRCALPHA)
    pygame.draw.polygon(cockpit_surf, (8, 24, 38, 240), [(20, 55), (55, 10), (265, 10), (300, 55), (275, 75), (45, 75)])
    pygame.draw.polygon(cockpit_surf, (72, 224, 245, 220), [(20, 55), (55, 10), (265, 10), (300, 55), (275, 75), (45, 75)], 2)
    pygame.draw.circle(cockpit_surf, (25, 195, 225, 180), (160, 42), 20, 2)
    for cx_chair, trim_col in ((105, (236, 187, 100)), (215, (86, 215, 197))):
        pygame.draw.rect(cockpit_surf, (32, 42, 52), (cx_chair - 22, 118, 44, 14), border_radius=3)
        pygame.draw.rect(cockpit_surf, (52, 68, 82), (cx_chair - 24, 88, 48, 34), border_radius=6)
        pygame.draw.rect(cockpit_surf, (74, 94, 112), (cx_chair - 18, 92, 36, 24), border_radius=4)
        pygame.draw.rect(cockpit_surf, (40, 54, 66), (cx_chair - 18, 68, 36, 24), border_radius=5)
        pygame.draw.rect(cockpit_surf, trim_col, (cx_chair - 12, 72, 24, 5), border_radius=2)
        pygame.draw.rect(cockpit_surf, (28, 38, 46), (cx_chair - 30, 86, 8, 28), border_radius=2)
        pygame.draw.rect(cockpit_surf, (28, 38, 46), (cx_chair + 22, 86, 8, 28), border_radius=2)
    s.blit(cockpit_surf, (440, 122))
    app.label("COCKPIT", 568, 266, 12, (236, 187, 100))

    comp_surf = pygame.Surface((165, 130), pygame.SRCALPHA)
    pygame.draw.rect(comp_surf, (38, 54, 68), (8, 12, 148, 96), border_radius=8)
    pygame.draw.rect(comp_surf, (86, 215, 197), (8, 12, 148, 96), 2, border_radius=8)
    for mx, mw in ((18, 38), (62, 42), (108, 38)):
        pygame.draw.rect(comp_surf, (8, 26, 38), (mx, 22, mw, 34), border_radius=3)
        pygame.draw.rect(comp_surf, (72, 235, 245), (mx, 22, mw, 34), 1, border_radius=3)
    pygame.draw.rect(comp_surf, (14, 32, 44), (24, 64, 116, 22), border_radius=3)
    s.blit(comp_surf, (275, 345))
    app.label("COMPUTADOR", 315, 462, 12, (86, 215, 197))

    stat_surf = pygame.Surface((180, 135), pygame.SRCALPHA)
    pygame.draw.rect(stat_surf, (10, 22, 34, 245), (6, 10, 168, 102), border_radius=8)
    pygame.draw.rect(stat_surf, (0, 238, 255), (6, 10, 168, 102), 2, border_radius=8)
    for idx, sid in enumerate(("hull", "power", "propulsion", "navigation", "comms", "ftl")):
        cond = int(app.state.ship_systems.get(sid, 0))
        by = 22 + idx * 13
        pygame.draw.rect(stat_surf, (6, 14, 22), (18, by, 118, 8), border_radius=2)
        bar_w = int(118 * max(0.08, min(1.0, cond / 100.0)))
        neon_col = (40, 255, 195) if cond >= 100 else ((0, 225, 255) if cond >= 40 else (255, 92, 145))
        pygame.draw.rect(stat_surf, neon_col, (18, by, bar_w, 8), border_radius=2)
        pygame.draw.circle(stat_surf, neon_col, (152, by + 4), 4)
    s.blit(stat_surf, (785, 345))
    app.label("PAINEL DE STATUS NEON", 796, 462, 11, (0, 238, 255))

    tank_surf = pygame.Surface((150, 145), pygame.SRCALPHA)
    pygame.draw.ellipse(tank_surf, (20, 225, 165, int(65 + 45 * pulse)), (10, 92, 130, 42))
    pygame.draw.rect(tank_surf, (46, 64, 76), (30, 98, 90, 24), border_radius=6)
    fluid_col = (25, int(230 + 25 * pulse), int(175 + 30 * pulse), 215)
    pygame.draw.rect(tank_surf, (12, 65, 58, 220), (36, 22, 78, 76), border_radius=10)
    pygame.draw.rect(tank_surf, fluid_col, (40, 26, 70, 68), border_radius=8)
    for bi in range(5):
        bx = 50 + (bi * 13) % 52
        by = 84 - int((t * 28 + bi * 17) % 54)
        pygame.draw.circle(tank_surf, (210, 255, 240, 240), (bx, by), 3 if bi % 2 == 0 else 2)
    pygame.draw.rect(tank_surf, (95, 255, 215, 250), (36, 22, 78, 76), 2, border_radius=10)
    pygame.draw.ellipse(tank_surf, (54, 76, 88), (32, 12, 86, 20))
    s.blit(tank_surf, (365, 495))
    app.label("TANQUE DE RENASCIMENTO", 362, 636, 10, (65, 255, 195))

    caps_surf = pygame.Surface((150, 145), pygame.SRCALPHA)
    pygame.draw.ellipse(caps_surf, (236, 187, 100, int(50 + 35 * pulse)), (16, 94, 118, 36))
    pygame.draw.rect(caps_surf, (52, 46, 38), (32, 96, 86, 24), border_radius=6)
    pygame.draw.rect(caps_surf, (24, 34, 44, 235), (38, 28, 74, 72), border_radius=12)
    pygame.draw.rect(caps_surf, (236, 187, 100), (38, 28, 74, 72), 2, border_radius=12)
    c_bob = int(math.sin(t * 3.5) * 4)
    pygame.draw.polygon(caps_surf, (255, 215, 110), [(75, 42 + c_bob), (91, 62 + c_bob), (75, 82 + c_bob), (59, 62 + c_bob)])
    s.blit(caps_surf, (690, 495))
    app.label("CAPSULA DE ESSENCIAS", 698, 636, 10, (236, 187, 100))

    pygame.draw.circle(s, (28, 40, 54), (600, 520), 34)
    pygame.draw.circle(s, (190, 122, 230), (600, 520), 34, 2)
    pygame.draw.circle(s, (120, 220, 255), (600, 520), int(18 + 4 * pulse), 1)
    app.label("SIMULADOR", 566, 558, 10, (198, 142, 235))

    airlock_rect = pygame.Rect(552, 598, 96, 68)
    pygame.draw.rect(s, (28, 36, 44), airlock_rect, border_radius=6)
    pygame.draw.rect(s, (236, 187, 100), airlock_rect, 2, border_radius=6)
    pygame.draw.line(s, (12, 16, 20), (600, 600), (600, 664), 3)
    app.label("ESCOTILHA", 566, 670, 11, (236, 187, 100))

    ship_x, ship_y = app.state.ship_pos
    actor_x = grid_ox + ship_x * tile_w + tile_w // 2
    actor_y = grid_oy + ship_y * tile_h + tile_h - 6
    walk_f = getattr(app, "walk_frame", 0)
    app.actor("hero", actor_x, actor_y, 1.18, walk_f, direction=app.facing)

    hud_renderer = getattr(app, "combat_hud_renderer", None)
    if hud_renderer is not None and getattr(hud_renderer, "available", False):
        glowed_ship = hud_renderer.apply_ship_interior_glow(s, time=t, tank_pos=(440, 565), status_pos=(875, 405))
        s.blit(glowed_ship, (0, 0))

    point = app.state.ship_interaction()
    if point == "cockpit" and app.state.missions.get("ship_navigation", {}).get("status") == "active":
        app.label("E - REPARAR REFERENCIA ESTELAR", 400, 704, 14, (236, 187, 100))
    elif point:
        hints = {
            "cockpit": "E - abrir cockpit",
            "computer": "E - abrir computador",
            "status": "E - abrir painel de status neon",
            "simulator": ("E - usar simulador" if app.state.simulator_built else ("E - projeto do simulador" if app.state.simulator_unlocked else "E - suporte vazio")),
            "respawn_tank": ("E - tanque de renascimento operacional" if app.state.respawn_tank_built else "E - construir tanque de renascimento"),
            "essence_storage": "E - abrir capsula de essencias",
            "airlock": "E - abrir escotilha e sair da nave",
        }
        app.label(hints[point], 390, 704, 14, (236, 187, 100))

    app.label(f"VIDA {app.state.hp}/{app.state.max_hp}", 35, 748, 12, (149, 167, 169))
    app.bar(32, 767, 350, app.state.hp, app.state.max_hp, (203, 112, 94))
    app.label(f"MEMORIA {app.state.memory}/{app.state.max_memory}", 790, 748, 12, (149, 167, 169))
    app.bar(790, 767, 350, app.state.memory, max(1, app.state.max_memory), (86, 215, 197))


def make_scarab_sprite(frame=0):
    s = pygame.Surface((52, 44), pygame.SRCALPHA)
    bob = frame % 2
    pygame.draw.ellipse(s, (22, 18, 18, 95), (6, 33, 40, 8))
    for lx, dx in ((14, -6), (24, -2), (34, 5)):
        pygame.draw.lines(s, (58, 36, 28), False, [(lx, 26 + bob), (lx + dx, 33), (lx + dx - 2, 40 - bob)], 2)
        pygame.draw.lines(s, (82, 52, 38), False, [(lx + 2, 24 + bob), (lx + dx + 3, 31), (lx + dx + 2, 38 + bob)], 2)
    pygame.draw.ellipse(s, (92, 52, 34), (7, 13 + bob, 32, 21))
    pygame.draw.ellipse(s, (158, 92, 48), (9, 14 + bob, 28, 17))
    pygame.draw.ellipse(s, (208, 136, 74), (12, 15 + bob, 20, 9))
    pygame.draw.line(s, (62, 34, 24), (10, 23 + bob), (37, 23 + bob), 2)
    pygame.draw.polygon(s, (118, 68, 42), [(31, 14 + bob), (41, 16 + bob), (42, 28 + bob), (31, 30 + bob)])
    pygame.draw.polygon(s, (68, 40, 32), [(40, 18 + bob), (49, 14 + bob), (45, 22 + bob)])
    pygame.draw.polygon(s, (68, 40, 32), [(40, 26 + bob), (49, 29 + bob), (45, 23 + bob)])
    pygame.draw.circle(s, PX_GOLD, (39, 20 + bob), 2)
    return s


def make_lizard_sprite(frame=0):
    s = pygame.Surface((62, 48), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (25, 22, 20, 95), (7, 38, 48, 7))
    pygame.draw.polygon(s, (56, 78, 48), [(16, 26), (5, 24), (0, 19 + step), (6, 29), (17, 33)])
    for lx, ly in ((19, 29), (38, 29)):
        pygame.draw.polygon(s, (54, 74, 46), [(lx, ly), (lx + 6, ly), (lx + 4, 41 - step), (lx - 2, 41 - step)])
        pygame.draw.line(s, (186, 178, 112), (lx - 2, 41 - step), (lx + 5, 42 - step), 2)
    pygame.draw.ellipse(s, (72, 102, 62), (14, 17, 32, 17))
    pygame.draw.ellipse(s, (148, 168, 96), (17, 23, 26, 9))
    for cx in (19, 25, 31, 37):
        pygame.draw.polygon(s, (188, 182, 108), [(cx, 18), (cx + 3, 11), (cx + 5, 18)])
    pygame.draw.polygon(s, (84, 114, 68), [(40, 16), (48, 12), (59, 17), (58, 23), (44, 25)])
    pygame.draw.circle(s, PX_GOLD, (50, 16), 2)
    return s


def make_hound_sprite(frame=0):
    s = pygame.Surface((64, 52), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (26, 20, 20, 95), (6, 42, 50, 7))
    pygame.draw.lines(s, (82, 50, 42), False, [(12, 26), (5, 21), (2, 15 + step)], 3)
    for lx, off in ((15, step), (24, -step), (38, step), (46, -step)):
        pygame.draw.lines(s, (86, 54, 44), False, [(lx, 29), (lx - 2, 38), (lx + 1, 46 + off)], 4)
        _rect(s, (168, 118, 84), lx - 1, 45 + off, 5, 3, 1)
    pygame.draw.polygon(s, (116, 72, 56), [(11, 27), (18, 17), (38, 16), (49, 22), (46, 33), (28, 34), (14, 32)])
    pygame.draw.polygon(s, (176, 116, 78), [(16, 20), (36, 18), (45, 23), (36, 28), (18, 27)])
    for sx in (20, 28, 36):
        pygame.draw.polygon(s, (74, 44, 38), [(sx, 17), (sx + 4, 10), (sx + 7, 18)])
    pygame.draw.polygon(s, (108, 66, 52), [(43, 18), (51, 13), (61, 18), (60, 24), (46, 25)])
    pygame.draw.circle(s, PX_GOLD, (52, 17), 2)
    return s


def make_burrower_sprite(frame=0):
    s = pygame.Surface((62, 50), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (24, 28, 28, 95), (6, 40, 48, 7))
    for idx, (cx, cy, rw, rh) in enumerate(((42, 28, 14, 16), (33, 25, 16, 19), (23, 24, 17, 20), (14, 25, 15, 18))):
        pygame.draw.ellipse(s, (76, 102, 94) if idx % 2 == 0 else (94, 124, 114), (cx - rw // 2, cy - rh // 2, rw, rh))
        pygame.draw.arc(s, (172, 198, 184), (cx - rw // 2, cy - rh // 2, rw, rh), 0.4, 2.7, 2)
    pygame.draw.polygon(s, (148, 168, 160), [(10, 18), (0, 22 + step), (10, 26)])
    pygame.draw.polygon(s, (182, 204, 192), [(10, 24), (1, 29 - step), (10, 33)])
    for lx in (16, 26, 36, 44):
        pygame.draw.line(s, (58, 78, 72), (lx, 32), (lx - 4, 43 - step), 3)
    pygame.draw.circle(s, PX_GOLD, (15, 22), 2)
    return s


def make_manta_sprite(frame=0):
    s = pygame.Surface((68, 50), pygame.SRCALPHA)
    flap = 2 if (frame % 2) else -2
    pygame.draw.ellipse(s, (26, 22, 22, 85), (10, 40, 48, 7))
    pygame.draw.polygon(s, (108, 82, 64), [(34, 12), (50, 17), (66, 26 + flap), (50, 32), (38, 30), (34, 36), (30, 30), (18, 32), (2, 26 + flap), (18, 17)])
    pygame.draw.polygon(s, (168, 128, 88), [(34, 15), (47, 19), (59, 26 + flap), (46, 29), (34, 27), (22, 29), (9, 26 + flap), (21, 19)])
    pygame.draw.line(s, (214, 178, 126), (34, 14), (34, 44), 3)
    pygame.draw.circle(s, PX_GOLD, (29, 21), 2); pygame.draw.circle(s, PX_GOLD, (39, 21), 2); pygame.draw.circle(s, PX_CYAN, (34, 24), 2)
    return s


def make_stalker_sprite(frame=0):
    s = pygame.Surface((60, 56), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (20, 24, 28, 95), (8, 47, 44, 7))
    pygame.draw.lines(s, (48, 64, 74), False, [(25, 31), (18, 40), (21, 51 - step)], 3)
    pygame.draw.lines(s, (48, 64, 74), False, [(35, 31), (42, 40), (39, 51 + step)], 3)
    pygame.draw.polygon(s, (66, 88, 102), [(22, 16), (38, 16), (41, 26), (35, 34), (25, 34), (19, 26)])
    pygame.draw.polygon(s, (124, 154, 168), [(25, 18), (35, 18), (37, 25), (33, 31), (27, 31), (23, 25)])
    pygame.draw.lines(s, (54, 72, 82), False, [(22, 19), (12, 25), (8, 35 + step)], 3)
    pygame.draw.polygon(s, PX_STEEL_HI, [(8, 35 + step), (15, 28), (13, 39 + step)])
    pygame.draw.lines(s, (54, 72, 82), False, [(38, 19), (48, 25), (52, 35 - step)], 3)
    pygame.draw.polygon(s, PX_STEEL_HI, [(52, 35 - step), (45, 28), (47, 39 - step)])
    pygame.draw.polygon(s, (78, 102, 114), [(23, 14), (26, 6), (34, 6), (37, 14), (30, 17)])
    _rect(s, (232, 88, 72), 26, 10, 8, 3, 1); pygame.draw.circle(s, PX_CYAN, (30, 24), 2)
    return s


def make_kuvaar_sprite(frame=0):
    s = pygame.Surface((88, 66), pygame.SRCALPHA)
    pulse = frame % 2
    pygame.draw.ellipse(s, (28, 24, 22, 105), (6, 52, 76, 10))
    for lx in (16, 30, 52, 66):
        _rect(s, (68, 58, 50), lx, 42, 9, 17, 2); _rect(s, (112, 96, 82), lx + 1, 43, 5, 12, 1)
    pygame.draw.ellipse(s, (96, 82, 68), (10, 22, 68, 30))
    pygame.draw.polygon(s, (176, 164, 142), [(12, 34), (20, 18), (34, 10), (50, 12), (66, 18), (76, 34), (66, 46), (22, 46)])
    for pts in ([(18, 28), (24, 12), (31, 26)], [(31, 24), (39, 6), (47, 24)], [(47, 24), (56, 9), (63, 26)], [(60, 28), (69, 15), (73, 30)]):
        pygame.draw.polygon(s, (235, 228, 206), pts); pygame.draw.polygon(s, (142, 132, 114), pts, 1)
    pygame.draw.polygon(s, (78, 64, 56), [(26, 24), (38, 16), (52, 16), (60, 26), (54, 39), (32, 39)])
    _rect(s, PX_GOLD, 34, 25, 5, 3, 1); _rect(s, PX_GOLD, 47, 25, 5, 3, 1)
    if pulse:
        pygame.draw.circle(s, PX_CYAN_HI, (44, 21), 2)
    return s


def make_ry_sprite(frame=0):
    s = pygame.Surface((100, 92), pygame.SRCALPHA)
    pulse = 0.5 + 0.5 * math.sin(frame * 1.8)
    pygame.draw.ellipse(s, (18, 24, 34, 90), (20, 78, 60, 9))
    for sign in (-1, 1):
        pygame.draw.polygon(s, (195, 228, 255, 135), [(50 + sign * 8, 36), (50 + sign * 42, 16), (50 + sign * 46, 34), (50 + sign * 32, 54), (50 + sign * 10, 48)])
    pygame.draw.circle(s, (180, 225, 255, int(110 + 50 * pulse)), (50, 42), 26, 2)
    pygame.draw.polygon(s, (225, 242, 255, 230), [(50, 14), (64, 42), (50, 70), (36, 42)])
    pygame.draw.polygon(s, (255, 255, 255, 255), [(50, 22), (58, 42), (50, 62), (42, 42)])
    pygame.draw.circle(s, PX_GOLD, (50, 42), 5 if pulse > 0.5 else 4)
    return s


def make_nahr_shadow_sprite(frame=0):
    s = pygame.Surface((48, 52), pygame.SRCALPHA)
    sway = int(math.sin(frame * 1.4))
    pygame.draw.ellipse(s, (0, 0, 0, 75), (10, 42, 28, 6))
    pygame.draw.polygon(s, (14, 16, 24, 242), [(24, 8), (35, 14), (39, 28), (36, 41), (12, 41), (9, 28), (13, 14)])
    pygame.draw.polygon(s, (32, 36, 50, 220), [(24, 11), (32, 16), (34, 29), (31, 38), (17, 38), (14, 29), (16, 16)])
    _rect(s, (185, 225, 255, 245), 19 + sway, 20, 4, 2); _rect(s, (185, 225, 255, 245), 26 + sway, 20, 4, 2)
    return s


def make_boss_sprite(kind, frame=0):
    s = pygame.Surface((100, 92), pygame.SRCALPHA)
    pulse = frame % 2
    if kind == "fagor":
        pygame.draw.ellipse(s, (38, 28, 25, 90), (10, 76, 80, 10))
        pygame.draw.polygon(s, (68, 54, 48), [(26, 54), (42, 54), (45, 82), (24, 82)])
        pygame.draw.polygon(s, (68, 54, 48), [(58, 54), (74, 54), (76, 82), (55, 82)])
        pygame.draw.polygon(s, (96, 78, 68), [(18, 24), (32, 10), (68, 10), (82, 24), (78, 58), (22, 58)])
        pygame.draw.polygon(s, (138, 86, 62), [(28, 20), (72, 20), (68, 52), (32, 52)])
        pygame.draw.polygon(s, (228, 84, 42), [(50, 22), (62, 35), (50, 48), (38, 35)])
        pygame.draw.circle(s, (255, 196, 84), (50, 35), 6 if pulse else 5)
    elif kind == "kael":
        pygame.draw.ellipse(s, (32, 28, 26, 85), (8, 80, 84, 8))
        pygame.draw.polygon(s, (92, 66, 46), [(34, 82), (38, 40), (50, 32), (62, 40), (68, 82)])
        for x, y, r in ((24, 24, 16), (40, 16, 18), (62, 18, 19), (76, 28, 15), (30, 36, 16), (70, 38, 16), (50, 24, 22)):
            pygame.draw.circle(s, (48, 98, 58), (x, y), r); pygame.draw.circle(s, (74, 138, 78), (x - 2, y - 2), max(4, r - 5))
        _rect(s, PX_GOLD, 43, 52, 4, 3); _rect(s, PX_GOLD, 53, 52, 4, 3)
    elif kind == "ry":
        return make_ry_sprite(frame)
    elif kind == "ounull":
        pygame.draw.ellipse(s, (25, 48, 56, 90), (14, 74, 72, 10))
        pygame.draw.polygon(s, (56, 138, 156, 220), [(14, 48), (30, 18), (50, 10), (70, 18), (86, 48), (70, 72), (30, 72)])
        pygame.draw.ellipse(s, (92, 196, 212, 235), (24, 18, 52, 48))
        pygame.draw.circle(s, (235, 255, 255), (40, 36), 4); pygame.draw.circle(s, (235, 255, 255), (60, 36), 4)
    elif kind == "alphor":
        pygame.draw.ellipse(s, (36, 20, 18, 95), (10, 78, 80, 10))
        pygame.draw.polygon(s, (112, 42, 32), [(34, 32), (8, 12), (14, 48), (32, 56)])
        pygame.draw.polygon(s, (112, 42, 32), [(66, 32), (92, 12), (86, 48), (68, 56)])
        pygame.draw.polygon(s, (78, 38, 30), [(28, 78), (26, 40), (38, 22), (62, 22), (74, 40), (72, 78)])
        pygame.draw.polygon(s, (178, 72, 36), [(36, 42), (50, 26), (64, 42), (58, 66), (42, 66)])
        _rect(s, (255, 215, 90), 42, 28, 5, 3); _rect(s, (255, 215, 90), 53, 28, 5, 3)
    elif kind == "broom":
        pygame.draw.ellipse(s, (22, 28, 40, 95), (18, 78, 64, 9))
        pygame.draw.polygon(s, (52, 64, 86), [(34, 78), (32, 42), (42, 28), (58, 28), (68, 42), (64, 78)])
        pygame.draw.polygon(s, (96, 114, 142), [(38, 44), (44, 32), (56, 32), (62, 44), (56, 68), (44, 68)])
        pygame.draw.line(s, PX_CYAN, (62, 46), (86, 8), 5)
    elif kind in ("mekron", "nocther", "voltrik", "moryss", "verdak", "gravorn"):
        palettes = {
            "mekron": ((88, 102, 114), (168, 188, 202), PX_CYAN),
            "nocther": ((52, 38, 68), (118, 84, 156), (218, 112, 245)),
            "voltrik": ((48, 84, 118), (102, 186, 232), (245, 232, 110)),
            "moryss": ((38, 92, 108), (84, 178, 198), PX_CYAN_HI),
            "verdak": ((54, 92, 58), (112, 176, 98), (215, 245, 155)),
            "gravorn": ((84, 74, 66), (148, 132, 114), PX_GOLD),
        }
        dark, mid, core = palettes[kind]
        pygame.draw.ellipse(s, (20, 24, 30, 95), (12, 76, 76, 10))
        pygame.draw.polygon(s, dark, [(24, 76), (20, 36), (34, 16), (66, 16), (80, 36), (76, 76), (58, 82), (42, 82)])
        pygame.draw.polygon(s, mid, [(30, 40), (38, 22), (62, 22), (70, 40), (62, 66), (38, 66)])
        pygame.draw.polygon(s, core, [(50, 28), (60, 42), (50, 56), (40, 42)])
    else:
        return None
    return s


def draw_title_screen_077(app):
    ui_layer = pygame.Surface((1200, 800), pygame.SRCALPHA)
    ui_layer.fill((0, 0, 0, 0))
    pygame.draw.rect(ui_layer, (58, 210, 228, 90), (24, 20, 1152, 760), 1, border_radius=8)

    title_text = "CINZAS DE ORION"
    f_title = app.font(46)
    f_sub = app.font(15)
    t_glow = f_title.render(title_text, True, (42, 185, 208))
    t_main = f_title.render(title_text, True, (232, 250, 255))
    tx = 600 - t_main.get_width() // 2
    ui_layer.blit(t_glow, (tx + 2, 54)); ui_layer.blit(t_main, (tx, 52))

    sub_text = "CRONICAS DE VEYRA  -  EDICAO 0.7.7"
    s_surf = f_sub.render(sub_text, True, (236, 187, 100))
    ui_layer.blit(s_surf, (600 - s_surf.get_width() // 2, 110))
    pygame.draw.line(ui_layer, (86, 215, 197, 160), (420, 136), (780, 136), 1)

    prompt_text = "Pressione qualquer botao para comecar"
    f_prompt = app.font(20)
    p_surf = f_prompt.render(prompt_text, True, (218, 248, 255))
    px = 600 - p_surf.get_width() // 2; py = 690
    pygame.draw.rect(ui_layer, (8, 24, 34, 180), (px - 24, py - 10, p_surf.get_width() + 48, p_surf.get_height() + 20), border_radius=6)
    pygame.draw.rect(ui_layer, (86, 215, 197, 210), (px - 24, py - 10, p_surf.get_width() + 48, p_surf.get_height() + 20), 1, border_radius=6)
    ui_layer.blit(p_surf, (px, py))

    hud_renderer = getattr(app, "combat_hud_renderer", None)
    rendered = None
    if hud_renderer is not None and getattr(hud_renderer, "available", False):
        rendered = hud_renderer.render_title_screen(ui_layer, time=app.frame)

    if rendered is not None:
        app.canvas.blit(rendered, (0, 0))
    else:
        for yy in range(800):
            u = yy / 799.0
            pygame.draw.line(app.canvas, (int(6 + 14 * u), int(10 + 22 * u), int(20 + 34 * u)), (0, yy), (1200, yy))
        for x, y, r, phase, speed in getattr(app, "title_stars", []):
            tw = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(app.frame * speed * 3.0 + phase))
            pygame.draw.circle(app.canvas, (int(165 * tw + 70), int(205 * tw + 45), int(235 * tw + 20)), (x, y), r)
        cx, cy, rad = 600, 415, 155
        for ir in range(rad, 0, -2):
            k = (rad - ir) / rad
            pygame.draw.circle(app.canvas, (int(28 + 158 * k), int(42 + 92 * k), int(64 + 42 * k)), (cx - int(k * 22), cy - int(k * 18)), ir)
        pygame.draw.circle(app.canvas, (98, 238, 248), (cx, cy), rad, 3)
        app.canvas.blit(ui_layer, (0, 0))


def draw_combat_hud_ambient_077(app, surface):
    dock_rect = pygame.Rect(18, 523, 896, 142)
    pygame.draw.rect(surface, (3, 14, 22, 115), dock_rect, border_radius=8)
    pygame.draw.rect(surface, (46, 198, 218, 95), dock_rect, 1, border_radius=8)

    grid_col = (42, 198, 218, 26)
    for i in range(33):
        gx = dock_rect.left + int(round(i * dock_rect.width / 32))
        pygame.draw.line(surface, grid_col, (gx, dock_rect.top), (gx, dock_rect.bottom), 1)
    for j in range(6):
        gy = dock_rect.top + int(round(j * dock_rect.height / 5))
        pygame.draw.line(surface, grid_col, (dock_rect.left, gy), (dock_rect.right, gy), 1)

    edge = (68, 224, 235, 115)
    for x, dx in ((12, 1), (1200 - 12, -1)):
        for y, dy in ((12, 1), (800 - 12, -1)):
            pygame.draw.line(surface, edge, (x, y), (x + dx * 22, y), 1)
            pygame.draw.line(surface, edge, (x, y), (x, y + dy * 18), 1)

    font = app.font(8)
    surface.blit(font.render("SYS_STATUS: ACTIVE // 0.7.7", True, (89, 214, 224)), (875, 23))
    surface.blit(font.render("HUD LINK: STABLE", True, (62, 148, 167)), (875, 36))
    width = 245
    phase = (math.sin(app.frame * 2.1) + 1.0) * 0.5
    fill_width = int(width * (0.28 + phase * 0.66))
    pygame.draw.rect(surface, (9, 30, 39, 150), (875, 52, width, 4), border_radius=2)
    pygame.draw.rect(surface, (42, 205, 218, 165), (875, 52, fill_width, 4), border_radius=2)


def export_all_077_assets_to_disk(project_root: Path, sprite_fn):
    pygame.init()
    out_base = project_root / "assets" / "sprites_077"
    player_dir = out_base / "player"
    monsters_dir = out_base / "monsters"
    cards_dir = out_base / "cards"
    for d in (player_dir, monsters_dir, cards_dir):
        d.mkdir(parents=True, exist_ok=True)

    dir_map = {"down": "baixo", "up": "cima", "left": "esquerda", "right": "direita"}
    for d_key, stem in dir_map.items():
        for f_idx in range(3):
            suffix = "" if f_idx == 0 else f"_{f_idx}"
            pygame.image.save(make_hero_world_sprite(d_key, f_idx), str(player_dir / f"{stem}{suffix}.png"))

    pygame.image.save(make_hero_combat_sprite(0), str(player_dir / "combate_idle.png"))
    pygame.image.save(make_hero_combat_sprite(1), str(player_dir / "combate_ataque.png"))

    class _DummyCardApp:
        def __init__(self, canvas):
            self.canvas = canvas
            self.frame = 0.5
            self.combat_hud_renderer = None
        def mouse(self):
            return (-999, -999)
        def font(self, sz):
            return pygame.font.SysFont("consolas", sz, bold=True)

    for rar in ("Comum", "Incomum", "Rara", "Mítica", "Lendária", "Única"):
        for var_tag, var_code in (("normal", "normal"), ("plus", "plus"), ("plusplus", "plusplus")):
            c_surf = pygame.Surface((210, 118), pygame.SRCALPHA)
            dummy = _DummyCardApp(c_surf)
            draw_tcg_card_frame_077(dummy, pygame.Rect(0, 0, 210, 118), rar)
            draw_upgrade_diamond_077(dummy, pygame.Rect(0, 0, 210, 118), var_code, neon_col=get_rarity_neon_color_077(rar))
            safe_rar = rar.lower().replace("í", "i").replace("á", "a").replace("ú", "u")
            pygame.image.save(c_surf, str(cards_dir / f"tcg_077_{safe_rar}_{var_tag}.png"))
