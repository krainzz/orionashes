"""Cinzas de Órion 0.7.2 — progressão, cartas, combate e viagens espaciais"""
import math
import os
from pathlib import Path
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
from content import (format_card_name, CARDS, OTHER_RECIPES, SPECIES, MEMORY_MODULES, MEMORY_RECIPES, PLANET, CIVILIZATION,
                    FACTIONS, CIVILIZATIONS, ACHIEVEMENTS, MISSION_REWARDS, FUTURE_UPGRADES, SHIP_SYSTEMS, SHIP_DIAGNOSTIC_ORDER,
                    SHIP_INTERIOR, PLAYER_COMBAT, CARD_VARIANTS, NAHR_CIVILIZATION, CARD_RARITY_RULES, CARD_RARITIES, RELIC_STONE_NAME, MAX_HP, BOSSES, HERBS, STELLAR_ROUTES, AURORA_UPGRADES, TOTAL_MEMORY_SLOTS, CHEST_MEMORY_SLOTS, CHEST_MEMORY_SLOT_UNLOCKS, RENOWN_MILESTONES, RENOWN_REWARDS, GALAXY_ID, GALAXY_NAME, GALAXIES, GALAXY_DISPLAY_ORDER, GALAXY_CONNECTIONS, HELMET_DESIGNS, HELMET_DESIGN_ORDER, SHIP_MISSION_DATA, HELMET_TIERS, HELMET_SCAN_ABILITIES, CREATURE_TYPES, UNIQUE_CARD_ESSENCE_COST, UNIQUE_VARIANT_MULTIPLIERS, UNIQUE_BUFF_DEFS, UNIQUE_BUFF_COUNT_CHANCES, UNIQUE_MOMENTUM_DEFS, UNIQUE_MOMENTUM_CHANCE, DOMAIN_ELEMENTS, DOMAIN_LEVEL_MAX, DOMAIN_LEVEL_XP, DOMAIN_BONUSES, creature_achievement_id, creature_achievement_data, boss_achievement_id, boss_achievement_data, BOSS_ACHIEVEMENT_TIERS, COMBAT_CHALLENGE_CATALOG)
from core import State, distance, load_campaign, OBJECTIVES, creature_level
from world import SECTORS, protected_tile

W, H = 1200, 800
ROOT = Path(__file__).resolve().parent
LOCAL_APPDATA = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share'))
SAVE_DIR = LOCAL_APPDATA / 'Cinzas de Órion'
SAVE_DIR.mkdir(parents=True, exist_ok=True)
SAVE = SAVE_DIR / 'save.json'
BG, PANEL, EDGE = (17, 24, 33), (26, 37, 47), (54, 76, 86)
INK, MUTED, TEAL, GOLD = (230, 234, 226), (149, 167, 169), (86, 215, 197), (236, 187, 100)
CARD_RARITY_ACCENTS = {'Comum': EDGE, 'Incomum': (87, 145, 90), 'Rara': (83, 116, 184), 'Mítica': (130, 93, 168), 'Lendária': (196, 157, 54), 'Única': (137, 117, 158)}

ELEMENT_BADGE_FILES = {
    'Fogo': 'fogo.png',
    'Água': 'agua.png',
    'Planta': 'planta.png',
    'Terra': 'terra.png',
    'Metal': 'metal.png',
    'Elétrico': 'eletrico.png',
    'Luz': 'luz.png',
    'Trevas': 'trevas.png',
}

# Artes oficiais das peças de equipamento. Os arquivos são fornecidos manualmente
# pelo usuário em assets/equips/; esta build apenas os referencia.
EQUIPMENT_ASSET_FILES = {
    'helmet': 'Elmo.png',
    'chest': 'Peitoral.png',
    'locomotion': 'Grevas.png',
    'gauntlet': 'Manopla.png',
}

# Sprites-base opcionais do protagonista. Um arquivo por direção é suficiente;
# um segundo frame opcional *_1.png pode ser adicionado para a animação de caminhada.
PLAYER_ASSET_FILES = {
    'down': 'baixo.png',
    'up': 'cima.png',
    'left': 'esquerda.png',
    'right': 'direita.png',
}


def iso(x, y):
    return (int(450 + (x-y)*27), int(100 + (x+y)*14))


# ============================ SPRITES PIXEL ART =============================
PX_DARK=(18,23,29); PX_BLACK=(11,14,19)
PX_STEEL=(119,133,143); PX_STEEL_HI=(177,190,197); PX_STEEL_D=(70,81,90)
PX_SUIT=(39,49,60); PX_SUIT_HI=(61,76,91)
PX_SKIN=(129,83,58); PX_SKIN_HI=(173,118,80)
PX_CYAN=(87,225,205); PX_CYAN_HI=(180,255,244)
PX_GOLD=(222,170,84)

def _rect(s,c,x,y,w,h): pygame.draw.rect(s,c,(x,y,w,h))

def make_hero_down_sprite(frame=0):
    s = pygame.Surface((44, 58), pygame.SRCALPHA)
    step = frame % 2
    if step == 0:
        _rect(s, PX_BLACK, 11, 47, 8, 9); _rect(s, PX_BLACK, 25, 47, 8, 9)
        _rect(s, PX_SUIT, 13, 34, 7, 14); _rect(s, PX_SUIT, 24, 34, 7, 14)
    else:
        _rect(s, PX_BLACK, 9, 48, 8, 8); _rect(s, PX_BLACK, 27, 46, 8, 10)
        _rect(s, PX_SUIT, 11, 35, 7, 13); _rect(s, PX_SUIT, 26, 33, 7, 15)
    _rect(s, PX_STEEL_D, 13, 35, 7, 4); _rect(s, PX_STEEL_D, 24, 35, 7, 4)
    pygame.draw.polygon(s, PX_SUIT, [(13,20),(31,20),(33,31),(29,41),(15,41),(11,31)])
    pygame.draw.polygon(s, PX_STEEL, [(15,21),(29,21),(30,32),(27,38),(17,38),(14,32)])
    pygame.draw.line(s, PX_STEEL_HI, (16,22),(28,22),2); pygame.draw.line(s, PX_STEEL_D,(16,33),(28,33),1)
    pygame.draw.polygon(s, PX_CYAN_HI, [(22,25),(26,29),(22,34),(18,29)]); pygame.draw.polygon(s, PX_CYAN, [(22,27),(24,29),(22,32),(20,29)])
    pygame.draw.polygon(s, PX_STEEL_D, [(9,20),(14,18),(16,23),(11,26)]); pygame.draw.polygon(s, PX_STEEL_D, [(30,18),(35,20),(34,26),(29,23)])
    pygame.draw.line(s, PX_SUIT_HI,(11,23),(7,32),4); pygame.draw.line(s, PX_SUIT,(7,31),(9,38),4); _rect(s,PX_STEEL_D,5,35,8,5); _rect(s,PX_STEEL,6,35,5,3)
    pygame.draw.line(s, PX_SUIT_HI,(33,23),(37,31),4); pygame.draw.line(s, PX_STEEL_D,(37,30),(39,35),4); _rect(s,PX_GOLD,34,34,8,7); _rect(s,PX_GOLD,36,39,7,7); _rect(s,PX_STEEL_HI,37,34,5,2); pygame.draw.circle(s,PX_CYAN,(39,43),2)
    _rect(s,PX_DARK,31,27,7,5); _rect(s,PX_CYAN,32,28,5,2)
    _rect(s,PX_SKIN,19,14,6,6); pygame.draw.polygon(s,PX_SKIN,[(16,8),(18,3),(26,3),(30,8),(28,14),(24,17),(19,16),(17,12)]); pygame.draw.polygon(s,PX_SKIN_HI,[(20,5),(25,5),(28,8),(26,11),(20,10)]); _rect(s,PX_DARK,18,3,9,3); _rect(s,PX_DARK,18,10,2,1); _rect(s,PX_DARK,25,10,2,1); _rect(s,PX_SKIN_HI,27,11,2,2)
    return s

def make_hero_up_sprite(frame=0):
    s = pygame.Surface((44,58), pygame.SRCALPHA); step=frame%2
    if step == 0:
        _rect(s,PX_BLACK,11,47,8,9); _rect(s,PX_BLACK,25,47,8,9)
        _rect(s,PX_SUIT,13,34,7,14); _rect(s,PX_SUIT,24,34,7,14)
    else:
        _rect(s,PX_BLACK,9,48,8,8); _rect(s,PX_BLACK,27,46,8,10)
        _rect(s,PX_SUIT,11,35,7,13); _rect(s,PX_SUIT,26,33,7,15)
    pygame.draw.polygon(s,PX_STEEL_D,[(14,20),(30,20),(32,31),(29,41),(15,41),(12,31)]); pygame.draw.line(s,PX_STEEL_HI,(17,23),(28,23),2); pygame.draw.line(s,PX_STEEL_D,(16,33),(29,33),1)
    pygame.draw.polygon(s,PX_STEEL_D,[(9,20),(14,18),(16,23),(11,26)]); pygame.draw.polygon(s,PX_STEEL_D,[(30,18),(35,20),(34,26),(29,23)])
    pygame.draw.line(s,PX_SUIT_HI,(11,23),(7,32),4); pygame.draw.line(s,PX_SUIT,(7,31),(9,38),4); pygame.draw.line(s,PX_SUIT_HI,(33,23),(37,31),4); pygame.draw.line(s,PX_STEEL_D,(37,30),(39,35),4); _rect(s,PX_GOLD,34,34,8,8); pygame.draw.circle(s,PX_CYAN,(39,43),2)
    # cabeça vista de costas, sem rosto/visor
    _rect(s,PX_SKIN,18,11,10,7); pygame.draw.polygon(s,PX_DARK,[(16,8),(18,3),(26,3),(30,8),(28,14),(18,14)])
    pygame.draw.line(s,PX_STEEL_HI,(17,24),(27,24),1); pygame.draw.line(s,PX_STEEL_D,(17,28),(27,28),1)
    return s

def make_hero_side_sprite(direction='right', frame=0):
    """Perfil lateral mais estreito, com anatomia realmente de lado.

    A Manopla permanece exclusivamente na mão direita: ela aparece no perfil
    direito (braço próximo ao observador) e fica ocultada pelo tronco no perfil
    esquerdo, em vez de ser espelhada mecanicamente para os dois lados.
    """
    s = pygame.Surface((44, 58), pygame.SRCALPHA)
    step = frame % 2

    # Uma única perna dominante em perfil. A passada altera discretamente
    # posição/comprimento para não parecer que o personagem desliza.
    if step == 0:
        _rect(s, PX_SUIT, 20, 34, 7, 14)
        _rect(s, PX_STEEL_D, 20, 35, 7, 4)
        _rect(s, PX_BLACK, 19, 47, 8, 9)
    else:
        _rect(s, PX_SUIT, 18, 35, 7, 13)
        _rect(s, PX_STEEL_D, 18, 36, 7, 4)
        _rect(s, PX_BLACK, 17, 48, 8, 8)

    # Tronco estreito e vertical, sem a inclinação excessiva da versão anterior.
    pygame.draw.polygon(s, PX_SUIT, [(17, 20), (27, 20), (29, 31), (27, 41), (19, 41), (16, 31)])
    pygame.draw.polygon(s, PX_STEEL_D, [(18, 21), (26, 21), (28, 31), (26, 38), (20, 38), (17, 31)])
    pygame.draw.line(s, PX_STEEL_HI, (19, 22), (26, 22), 2)
    pygame.draw.line(s, PX_STEEL_D, (19, 33), (26, 33), 1)

    # Núcleo do peitoral fica parcialmente visível em perfil.
    pygame.draw.polygon(s, PX_CYAN, [(22, 26), (24, 29), (22, 32), (20, 29)])

    if direction == 'right':
        # Braço direito é o lado visível; Manopla aparece somente aqui.
        pygame.draw.line(s, PX_SUIT_HI, (26, 23), (31, 30), 4)
        pygame.draw.line(s, PX_STEEL_D, (30, 29), (33, 35), 4)
        _rect(s, PX_GOLD, 30, 33, 9, 8)
        pygame.draw.circle(s, PX_CYAN, (37, 39), 2)
        # Braço esquerdo permanece atrás do tronco.
        pygame.draw.line(s, PX_SUIT, (18, 24), (16, 31), 3)
    else:
        # Perfil esquerdo: a mão direita fica do lado distante e não deve
        # exibir a Manopla como se ela estivesse na mão esquerda.
        pygame.draw.line(s, PX_SUIT_HI, (18, 23), (15, 30), 4)
        pygame.draw.line(s, PX_STEEL_D, (15, 29), (13, 35), 3)
        # Braço direito oculto atrás do tronco; no máximo um pequeno contorno.
        pygame.draw.line(s, PX_SUIT, (26, 23), (29, 29), 2)

    # Cabeça compacta e ereta, com a face apontando para o lado correto.
    _rect(s, PX_SKIN, 20, 14, 6, 5)
    if direction == 'right':
        pygame.draw.polygon(s, PX_SKIN, [(19, 9), (20, 5), (26, 4), (29, 8), (27, 13), (23, 15), (20, 13)])
        _rect(s, PX_DARK, 20, 4, 7, 3)
        pygame.draw.line(s, PX_DARK, (27, 9), (29, 9), 1)
        _rect(s, PX_SKIN_HI, 28, 10, 1, 1)
    else:
        pygame.draw.polygon(s, PX_SKIN, [(29, 9), (28, 5), (22, 4), (19, 8), (21, 13), (25, 15), (28, 13)])
        _rect(s, PX_DARK, 21, 4, 7, 3)
        pygame.draw.line(s, PX_DARK, (21, 9), (19, 9), 1)
        _rect(s, PX_SKIN_HI, 20, 10, 1, 1)
    return s

def make_hero_world_sprite(direction='down', frame=0):
    if direction == 'up':
        return make_hero_up_sprite(frame)
    if direction == 'left':
        return make_hero_side_sprite('left', frame)
    if direction == 'right':
        return make_hero_side_sprite('right', frame)
    return make_hero_down_sprite(frame)


def make_hero_combat_sprite(frame=0):
    """Pose frontal de combate: corpo esbelto, mão esquerda no painel
    e Manopla estendida com palma aberta, sem aparência de garra."""
    s = pygame.Surface((84, 66), pygame.SRCALPHA)
    step = frame % 2
    # pernas / base
    _rect(s, PX_BLACK, 27, 49, 9, 11)
    _rect(s, PX_BLACK, 41, 49, 9, 11)
    _rect(s, PX_SUIT, 28, 35, 8, 15)
    _rect(s, PX_SUIT, 41, 35, 8, 15)
    _rect(s, PX_STEEL_D, 28, 36, 8, 4)
    _rect(s, PX_STEEL_D, 41, 36, 8, 4)
    # tronco estreito e peitoral
    pygame.draw.polygon(s, PX_SUIT, [(28, 19), (44, 19), (51, 26), (48, 43), (42, 48), (30, 48), (23, 42), (22, 27)])
    pygame.draw.polygon(s, PX_STEEL, [(29, 21), (43, 21), (48, 27), (46, 39), (41, 44), (31, 44), (26, 39), (25, 28)])
    pygame.draw.line(s, PX_STEEL_HI, (30, 22), (42, 22), 2)
    pygame.draw.line(s, PX_STEEL_D, (30, 38), (44, 38), 1)
    # núcleo
    pygame.draw.polygon(s, PX_CYAN_HI, [(36, 24), (40, 29), (36, 34), (32, 29)])
    pygame.draw.polygon(s, PX_CYAN, [(36, 26), (38, 29), (36, 32), (34, 29)])
    # braço esquerdo proporcional, cruzando até o painel
    pygame.draw.line(s, PX_SUIT_HI, (25, 25), (32, 31), 5)
    pygame.draw.line(s, PX_STEEL_D, (31, 30), (39, 32), 4)
    _rect(s, PX_DARK, 35, 28, 8, 6)
    _rect(s, PX_CYAN, 36, 30, 6, 2)
    _rect(s, PX_SKIN_HI, 39, 30, 5, 4)  # mão esquerda apoiada
    # braço direito: curto, robusto e integrado à Manopla
    pygame.draw.line(s, PX_SUIT_HI, (49, 25), (56, 27), 5)
    pygame.draw.line(s, PX_STEEL, (54, 26), (61, 28), 4)
    _rect(s, PX_GOLD, 59, 23, 10, 9)
    _rect(s, PX_GOLD, 63, 20, 9, 8)
    _rect(s, PX_STEEL_HI, 60, 24, 7, 2)
    # palma aberta / emissor plano, sem dedos longos
    _rect(s, PX_GOLD, 69, 19, 9, 12)
    pygame.draw.line(s, PX_STEEL_HI, (71, 21), (76, 21), 2)
    pygame.draw.line(s, PX_STEEL_HI, (71, 25), (77, 25), 2)
    pygame.draw.line(s, PX_STEEL_HI, (71, 29), (76, 29), 2)
    pygame.draw.circle(s, PX_CYAN, (69, 25), 4)
    pygame.draw.circle(s, PX_CYAN_HI, (69, 25), 1)
    if step:
        _rect(s, PX_CYAN_HI, 77, 24, 3, 2)
    # pescoço e rosto exposto
    _rect(s, PX_SKIN, 34, 13, 7, 6)
    pygame.draw.polygon(s, PX_SKIN, [(30, 8), (32, 3), (40, 2), (45, 8), (42, 14), (39, 17), (33, 16)])
    pygame.draw.polygon(s, PX_SKIN_HI, [(33, 5), (39, 4), (43, 8), (41, 10), (34, 9)])
    _rect(s, PX_DARK, 32, 2, 10, 3)  # cabelo
    _rect(s, PX_DARK, 33, 10, 2, 1)
    _rect(s, PX_DARK, 40, 10, 2, 1)
    _rect(s, PX_SKIN_HI, 41, 11, 2, 2)
    return s


def make_scarab_sprite(frame=0):
    s=pygame.Surface((52,44),pygame.SRCALPHA); bob=frame%2
    pygame.draw.ellipse(s,(42,36,34,90),(8,31,34,7))
    pygame.draw.ellipse(s,(103,62,43),(7,18+bob,35,19))
    pygame.draw.ellipse(s,(174,102,56),(10,16+bob,28,16))
    pygame.draw.line(s,(97,55,45),(24,18),(24,34),2)
    pygame.draw.line(s,(225,153,91),(14,20),(34,20),2)
    for x in (12,20,28,36): pygame.draw.line(s,(65,42,38),(x,31),(x-5,41),2)
    pygame.draw.polygon(s,(78,47,40),[(9,25),(1,21),(3,28),(10,29)])
    pygame.draw.polygon(s,(78,47,40),[(39,25),(47,20),(46,28),(39,29)])
    pygame.draw.circle(s,PX_GOLD,(15,23),2)
    pygame.draw.line(s,(143,92,61),(39,19),(46,11),1)
    pygame.draw.line(s,(143,92,61),(36,18),(44,8),1)
    return s


def make_lizard_sprite(frame=0):
    s = pygame.Surface((62, 48), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (45, 40, 35, 85), (6, 38, 46, 7))
    # cauda
    pygame.draw.polygon(s, (64, 86, 55), [(6, 30), (0, 25), (3, 22), (17, 25), (24, 31), (16, 35)])
    pygame.draw.line(s, (125, 143, 83), (4, 27), (19, 28), 2)
    # tronco
    pygame.draw.polygon(s, (70, 96, 61), [(16, 25), (22, 18), (39, 17), (48, 23), (46, 33), (33, 38), (18, 34)])
    pygame.draw.polygon(s, (152, 166, 98), [(20, 22), (31, 19), (40, 21), (44, 27), (31, 29), (20, 27)])
    # cabeça e focinho
    pygame.draw.polygon(s, (91, 112, 68), [(37, 18), (42, 11), (51, 14), (57, 20), (51, 26), (42, 24)])
    pygame.draw.polygon(s, (188, 181, 108), [(42, 12), (45, 7), (48, 14)])
    pygame.draw.polygon(s, (188, 181, 108), [(38, 15), (39, 10), (42, 17)])
    pygame.draw.circle(s, PX_GOLD, (49, 18), 2)
    pygame.draw.line(s, (220, 194, 124), (53, 22), (60, 21), 1)
    # placas do dorso
    for x, y in ((22, 18), (28, 15), (34, 16)):
        pygame.draw.polygon(s, (58, 77, 49), [(x-3, y+4), (x, y-3), (x+4, y+4)])
    # quatro membros
    legs = [(19, 30), (28, 32), (38, 31), (44, 28)]
    for lx, ly in legs:
        pygame.draw.line(s, (58, 74, 49), (lx, ly), (lx-4, 42-step), 2)
        pygame.draw.line(s, (97, 119, 70), (lx-4, 42-step), (lx, 44-step), 1)
    return s


def make_hound_sprite(frame=0):
    s = pygame.Surface((64, 52), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (50, 40, 38, 85), (6, 42, 50, 7))
    # corpo quadrúpede
    pygame.draw.polygon(s, (113, 73, 58), [(8, 34), (12, 23), (24, 17), (39, 18), (51, 25), (57, 33), (49, 40), (28, 41), (14, 37)])
    pygame.draw.polygon(s, (177, 117, 78), [(14, 23), (24, 18), (38, 20), (47, 26), (26, 31), (15, 29)])
    # cabeça e mandíbula
    pygame.draw.polygon(s, (104, 66, 55), [(39, 20), (49, 16), (59, 22), (55, 30), (42, 28)])
    pygame.draw.polygon(s, (165, 108, 73), [(46, 18), (52, 14), (56, 22), (48, 24)])
    pygame.draw.circle(s, PX_GOLD, (51, 21), 2)
    _rect(s, (70, 45, 42), 54, 24, 5, 3)
    # cristas
    for x, h in ((17, 12), (25, 9), (33, 11)):
        pygame.draw.polygon(s, (80, 52, 48), [(x, 20), (x+4, h), (x+7, 21)])
    # pernas
    for x, y, off in ((15, 34, 0), (27, 36, -1), (40, 35, 1), (48, 33, 0)):
        pygame.draw.line(s, (75, 53, 47), (x, y), (x-2, 47+off+step), 3)
        pygame.draw.line(s, (119, 77, 60), (x-2, 47+off+step), (x+2, 48+off+step), 1)
    pygame.draw.polygon(s, (76, 50, 44), [(10, 29), (2, 24), (4, 36), (12, 36)])
    return s


def make_burrower_sprite(frame=0):
    s = pygame.Surface((62, 50), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (47, 49, 48, 90), (6, 40, 48, 7))
    # corpo segmentado
    pygame.draw.polygon(s, (87, 113, 105), [(7, 27), (13, 19), (27, 16), (42, 19), (53, 28), (46, 38), (17, 38)])
    pygame.draw.polygon(s, (166, 188, 174), [(13, 24), (19, 16), (26, 20), (31, 13), (38, 19), (46, 24), (40, 33), (17, 33)])
    for x in (17, 25, 33, 41):
        pygame.draw.line(s, (76, 96, 90), (x, 19), (x+2, 34), 1)
    # broca frontal
    pygame.draw.polygon(s, (70, 91, 84), [(7, 26), (0, 20), (3, 30)])
    pygame.draw.polygon(s, (70, 91, 84), [(8, 29), (1, 31), (8, 34)])
    pygame.draw.polygon(s, (185, 206, 191), [(5, 23), (1, 18+step), (8, 23)])
    # pequenas patas
    for x in (14, 24, 34, 44):
        pygame.draw.line(s, (66, 86, 81), (x, 33), (x-3, 44-step), 2)
        pygame.draw.line(s, (105, 132, 122), (x, 33), (x+3, 43-step), 1)
    _rect(s, PX_GOLD, 46, 23, 3, 3)
    return s


def make_manta_sprite(frame=0):
    s = pygame.Surface((68, 50), pygame.SRCALPHA)
    pulse = frame % 2
    pygame.draw.ellipse(s, (43, 38, 36, 85), (7, 40, 52, 7))
    # asas largas e corpo central
    pygame.draw.polygon(s, (112, 87, 69), [(1, 30), (14, 16), (26, 19), (33, 12), (47, 19), (66, 30), (48, 35), (35, 30), (23, 37), (11, 33)])
    pygame.draw.polygon(s, (173, 133, 90), [(8, 28), (19, 19), (29, 23), (35, 17), (46, 24), (57, 29), (44, 31), (34, 27), (24, 32), (16, 30)])
    # cauda
    pygame.draw.polygon(s, (78, 67, 62), [(33, 28), (38, 37), (34, 43), (31, 31)])
    # sensores
    _rect(s, (52, 60, 62), 28, 24, 11, 6)
    pygame.draw.circle(s, PX_GOLD, (48, 26), 3)
    pygame.draw.line(s, (196, 167, 122), (11, 27), (22, 24), 1)
    pygame.draw.line(s, (196, 167, 122), (45, 24), (56, 28), 1)
    if pulse:
        _rect(s, PX_CYAN, 31, 20, 4, 2)
    return s


def make_stalker_sprite(frame=0):
    s = pygame.Surface((60, 56), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(s, (32, 35, 38, 90), (6, 47, 48, 7))
    # tronco alto / pernas longas
    pygame.draw.polygon(s, (64, 85, 96), [(15, 42), (12, 26), (19, 16), (31, 12), (43, 18), (51, 33), (43, 44), (28, 40)])
    pygame.draw.polygon(s, (126, 153, 164), [(17, 27), (21, 17), (29, 20), (27, 32), (20, 36)])
    # cabeça separada
    pygame.draw.polygon(s, (77, 100, 109), [(21, 15), (25, 6), (34, 6), (39, 14), (34, 20), (25, 19)])
    _rect(s, (223, 96, 77), 25, 12, 6, 4)
    # placas laterais
    for x in (18, 25, 34, 41):
        pygame.draw.line(s, (45, 58, 66), (x, 25), (x+4, 36), 2)
    # braços
    pygame.draw.line(s, (47, 59, 66), (18, 29), (9, 41+step), 3)
    pygame.draw.line(s, (47, 59, 66), (42, 29), (52, 39-step), 3)
    # pernas
    pygame.draw.line(s, (47, 59, 66), (22, 37), (16, 52+step), 4)
    pygame.draw.line(s, (47, 59, 66), (37, 37), (45, 52-step), 4)
    _rect(s, PX_CYAN, 40, 24, 3, 3)
    return s


def make_kuvaar_sprite(frame=0):
    s=pygame.Surface((88,66),pygame.SRCALPHA); pulse=frame%2
    pygame.draw.ellipse(s,(50,43,38,100),(8,50,66,9)); pygame.draw.ellipse(s,(93,81,69),(9,21,65,33)); pygame.draw.polygon(s,(171,160,139),[(6,34),(15,18),(28,5),(43,12),(58,7),(77,24),(81,39),(61,51),(25,51)])
    for pts in [[(14,31),(21,16),(31,22),(25,39)],[(27,18),(36,6),(44,19),(38,33)],[(44,17),(55,9),(62,24),(53,35)],[(58,27),(70,17),(78,31),(65,41)]]: pygame.draw.polygon(s,(226,216,188),pts)
    for x in (18,31,55,69): pygame.draw.line(s,(67,58,52),(x,47),(x-6,61),4)
    pygame.draw.polygon(s,(77,63,56),[(27,20),(37,12),(49,17),(45,29),(32,31)]); _rect(s,PX_GOLD,37,21,4,3); _rect(s,PX_GOLD,44,21,4,3)
    if pulse: _rect(s,(255,246,218),16,27,3,2)
    return s

def make_ry_sprite(frame=0):
    s = pygame.Surface((100, 92), pygame.SRCALPHA)
    pulse = 0.5 + 0.5 * math.sin(frame * 1.8)
    pygame.draw.ellipse(s, (18, 21, 27, 90), (17, 77, 66, 9))
    # Esfera translúcida disforme: múltiplas camadas irregulares sugerem luz
    # sem transformá-la em uma bola sólida.
    a1 = int(45 + 25*pulse)
    a2 = int(70 + 35*pulse)
    pygame.draw.ellipse(s, (214, 228, 255, a1), (17, 8, 66, 68), 2)
    pygame.draw.polygon(s, (233, 245, 255, a2), [(31,14),(56,7),(77,17),(86,36),(78,58),(55,74),(27,64),(14,43),(18,25)])
    pygame.draw.ellipse(s, (232, 248, 255, int(90 + 55*pulse)), (28, 17, 47, 45))
    pygame.draw.polygon(s, (255,255,255, int(135 + 65*pulse)), [(48,21),(62,18),(69,30),(61,45),(47,48),(39,36)])
    pygame.draw.circle(s, (255,255,255,int(175 + 55*pulse)), (57,31), 5 if pulse > .55 else 4)
    pygame.draw.line(s, (190,220,255,int(75 + 65*pulse)), (24,55),(15,67),2)
    pygame.draw.line(s, (190,220,255,int(75 + 65*pulse)), (77,52),(89,64),2)
    return s

def make_nahr_shadow_sprite(frame=0):
    s = pygame.Surface((48, 52), pygame.SRCALPHA)
    sway = math.sin(frame * 1.4)
    pygame.draw.ellipse(s, (0,0,0,60), (10,42,28,6))
    body = [(14,34),(10,27),(14,18),(21,14),(30,12),(38,18),(40,27),(35,35),(25,39)]
    pygame.draw.polygon(s, (10,12,17,238), body)
    pygame.draw.polygon(s, (31,34,43,210), [(18,27),(20,18),(28,15),(35,20),(33,29),(26,34)])
    eye = (182,217,255,230)
    pygame.draw.rect(s, eye, (22+int(sway),24,4,2))
    pygame.draw.rect(s, (100,151,191,180), (28-int(sway),25,3,2))
    pygame.draw.line(s, (40,45,58,190), (17,32),(11,39),2)
    pygame.draw.line(s, (40,45,58,190), (34,32),(41,38),2)
    return s

def make_boss_sprite(kind, frame=0):
    s = pygame.Surface((100, 92), pygame.SRCALPHA)
    pulse = frame % 2
    if kind == 'fagor':
        pygame.draw.ellipse(s, (38,30,27,80), (8,76,84,10))
        # Duas pernas robustas; não há braços nem cabeça.
        pygame.draw.polygon(s, (71,58,51), [(29,58),(43,56),(47,78),(39,84),(27,80)])
        pygame.draw.polygon(s, (71,58,51), [(55,56),(70,59),(75,80),(63,84),(54,76)])
        pygame.draw.polygon(s, (91,77,67), [(18,25),(29,13),(51,8),(74,15),(84,31),(79,61),(62,69),(37,66),(20,52)])
        pygame.draw.polygon(s, (128,82,60), [(37,28),(49,17),(66,22),(70,39),(58,52),(42,47)])
        pygame.draw.polygon(s, (205,74,44), [(48,31),(58,22),(67,29),(63,43),(53,48),(46,40)])
        pygame.draw.line(s, (236,125,61), (56,26),(61,43),2)
        pygame.draw.circle(s, (245,151,70), (58,35), 4 if pulse else 3)
        pygame.draw.line(s, (166,92,62), (26,38),(19,53),2); pygame.draw.line(s,(166,92,62),(73,25),(82,34),2)
    elif kind == 'kael':
        pygame.draw.ellipse(s, (35,31,29,75), (6,81,88,8))
        pygame.draw.polygon(s, (91,67,47), [(35,80),(39,42),(50,32),(62,43),(68,80)])
        pygame.draw.polygon(s, (117,80,48), [(43,75),(45,42),(53,37),(58,43),(60,75)])
        for a,b,c,d in ((50,42,25,24),(54,38,37,14),(59,42,78,21),(48,50,18,43),(62,51,86,44)):
            pygame.draw.line(s,(83,64,45),(a,b),(c,d),4)
        for x,y,r in ((22,22,16),(40,14,18),(64,20,20),(80,30,15),(28,40,17),(73,42,17),(51,25,22)):
            pygame.draw.circle(s,(53,105,63),(x,y),r)
        pygame.draw.circle(s,(83,141,76),(50,31),5 if pulse else 4)
    elif kind == 'ry':
        return make_ry_sprite(frame)
    elif kind == 'ounull':
        pygame.draw.ellipse(s,(35,55,61,70),(12,14,76,67))
        pygame.draw.ellipse(s,(72,157,171,150),(19,9,61,62))
        pygame.draw.polygon(s,(126,221,225,180),[(50,4),(62,16),(57,27),(44,24),(40,12)])
        pygame.draw.circle(s,(205,247,239),(42,31),3); pygame.draw.circle(s,(205,247,239),(59,31),3)
        pygame.draw.circle(s,(27,53,60),(42,31),1); pygame.draw.circle(s,(27,53,60),(59,31),1)
        pygame.draw.line(s,(126,221,225,170),(25,53),(16,70),3); pygame.draw.line(s,(126,221,225,170),(75,50),(85,67),3)
    elif kind == 'alphor':
        # Balrog: corpo massivo, chifres e asas de fogo estilizadas.
        pygame.draw.ellipse(s,(36,22,18,95),(10,78,80,10))
        pygame.draw.polygon(s,(74,42,30),[(27,73),(25,42),(36,25),(50,21),(65,29),(74,50),(69,78),(56,84),(40,83)])
        pygame.draw.polygon(s,(104,53,31),[(35,47),(39,28),(51,20),(62,31),(59,56),(49,69),(38,61)])
        pygame.draw.polygon(s,(160,70,34),[(42,45),(50,25),(59,40),(54,61),(47,65)])
        pygame.draw.polygon(s,(92,44,29),[(34,32),(15,13),(19,37),(29,51)])
        pygame.draw.polygon(s,(92,44,29),[(65,33),(84,12),(82,38),(70,51)])
        pygame.draw.line(s,(213,115,45),(39,31),(25,11),3); pygame.draw.line(s,(213,115,45),(61,31),(76,10),3)
        pygame.draw.polygon(s,(227,129,54),[(25,12),(33,17),(27,21),(20,18)])
        pygame.draw.polygon(s,(227,129,54),[(76,11),(69,16),(75,21),(82,17)])
        pygame.draw.circle(s,(255,197,81),(47,43),3 if pulse else 2)
        pygame.draw.line(s,(235,100,45),(35,78),(28,89),3); pygame.draw.line(s,(235,100,45),(63,78),(71,89),3)
    elif kind == 'broom':
        # Samurai humanoide: lâmina lateral, armadura estreita e raio vertical.
        pygame.draw.ellipse(s,(24,28,39,90),(18,78,64,9))
        pygame.draw.polygon(s,(54,64,84),[(36,77),(34,48),(43,34),(57,39),(63,51),(61,78)])
        pygame.draw.polygon(s,(91,103,128),[(39,54),(42,39),(55,41),(58,55),(53,67),(45,65)])
        pygame.draw.polygon(s,(39,47,65),[(38,34),(42,18),(56,14),(65,25),(59,38),(46,40)])
        pygame.draw.line(s,(187,202,224),(44,24),(61,27),2)
        pygame.draw.polygon(s,(151,167,193),[(62,42),(74,20),(77,23),(68,48)])
        pygame.draw.line(s,(202,220,255),(73,20),(86,4),2)
        pygame.draw.line(s,(107,196,229),(17,8),(34,33),2); pygame.draw.line(s,(107,196,229),(83,8),(62,33),2)
        pygame.draw.circle(s,(135,219,245),(50,27),3 if pulse else 2)
        pygame.draw.line(s,(74,90,115),(39,70),(31,86),4); pygame.draw.line(s,(74,90,115),(57,70),(68,86),4)
    else:
        return None
    return s

def make_avarin_sprite(guard=False, frame=0):
    s=pygame.Surface((48,60),pygame.SRCALPHA); sway=frame%2; cloth=(84,72,62) if guard else (112,96,79); cloth_hi=(120,101,80) if guard else (165,137,104); metal=(79,88,94) if guard else (61,66,72)
    pygame.draw.ellipse(s,(47,40,35,80),(8,50,34,7)); _rect(s,(56,49,47),12,44,8,9); _rect(s,(56,49,47),28,44,8,9); pygame.draw.polygon(s,cloth,[(8,24),(15,18),(31,18),(40,25),(36,47),(11,47)]); pygame.draw.polygon(s,cloth_hi,[(11,26),(16,20),(28,20),(35,26),(32,33),(14,33)])
    pygame.draw.polygon(s,metal,[(13,19),(16,8),(30,8),(35,20),(30,27),(18,27)]); _rect(s,PX_BLACK,16,14,15,6); _rect(s,PX_GOLD if not guard else PX_CYAN,18,21+sway,10,3); pygame.draw.line(s,cloth_hi,(9,27),(3,39),3); pygame.draw.line(s,cloth_hi,(38,27),(44,38),3); return s

def make_new_fauna_sprite(kind, frame=0):
    """Silhuetas pixel-art dedicadas à fauna dos quatro mundos novos."""
    spec = SPECIES.get(kind, {})
    base = spec.get('color', (92, 118, 124))
    hi = tuple(min(255, c + 36) for c in base)
    dark = tuple(max(0, c - 34) for c in base)
    s = pygame.Surface((64, 52), pygame.SRCALPHA)
    sway = frame % 2
    pygame.draw.ellipse(s, (35,31,29,80), (7,40,47,8))

    if kind == 'salamander_igneous':
        pygame.draw.polygon(s, dark, [(7,34),(0,28),(4,24),(18,28),(25,35),(17,39)])
        pygame.draw.polygon(s, base, [(15,31),(19,22),(34,20),(46,25),(50,34),(41,40),(22,39)])
        pygame.draw.polygon(s, hi, [(20,24),(31,18),(41,22),(34,28),(22,29)])
        pygame.draw.polygon(s, base, [(39,21),(48,15),(54,22),(48,27)])
        for x in (22, 37, 46): pygame.draw.line(s, dark, (x,34),(x-3,44),3)
        pygame.draw.line(s, hi, (49,20),(57,16),2); pygame.draw.circle(s, (247,204,95), (48,23),2)
        for x in (28,36,44): pygame.draw.circle(s, (245,133,74), (x,23),1)
    elif kind == 'ironback_crab':
        pygame.draw.ellipse(s, dark, (11,17,42,27)); pygame.draw.ellipse(s, base, (14,14,37,27)); pygame.draw.line(s, hi, (18,19),(46,19),2)
        for x in (19,27,36,44): pygame.draw.line(s, dark, (x,34),(x-6,45),2)
        pygame.draw.line(s, dark,(14,25),(4,20),4); pygame.draw.line(s,dark,(49,25),(60,20),4)
        pygame.draw.circle(s, hi, (20,21),2); pygame.draw.circle(s, hi, (40,21),2)
    elif kind == 'ion_wasp':
        pygame.draw.ellipse(s, dark, (25,17,18,25)); pygame.draw.ellipse(s, base, (28,14,16,26));
        pygame.draw.polygon(s, (105,181,196,150), [(27,22),(10,8),(18,25),(27,29)]); pygame.draw.polygon(s,(105,181,196,150),[(43,22),(56,8),(52,27),(43,29)])
        pygame.draw.line(s, hi,(35,16),(35,39),2); pygame.draw.circle(s,(238,214,110),(32,18),2)
        pygame.draw.line(s,dark,(34,39),(31,48),2); pygame.draw.line(s,dark,(38,39),(42,48),2)
    elif kind == 'frost_wolf':
        pygame.draw.polygon(s, base, [(9,33),(16,24),(32,22),(45,27),(53,23),(55,31),(47,34),(42,40),(22,40),(14,37)])
        pygame.draw.polygon(s, hi, [(16,25),(23,15),(28,24),(23,30)])
        pygame.draw.polygon(s, dark, [(45,26),(57,20),(54,29),(48,31)])
        for x in (19,30,41,48): pygame.draw.line(s,dark,(x,35),(x-2,45),3)
        pygame.draw.circle(s,(222,239,247),(39,27),2); pygame.draw.circle(s,(20,28,38),(39,27),1)
        pygame.draw.line(s, hi,(11,31),(3,28),2)
    elif kind == 'crystal_grazer':
        pygame.draw.ellipse(s, base, (11,21,43,24)); pygame.draw.polygon(s, hi, [(18,23),(13,7),(22,16),(30,5),(36,18),(46,10),(45,25)])
        pygame.draw.polygon(s,dark,[(45,23),(56,16),(54,28),(47,31)])
        for x in (19,29,40,48): pygame.draw.line(s,dark,(x,36),(x-2,46),3)
        pygame.draw.circle(s,(224,242,248),(49,21),2)
    elif kind == 'glacial_eel':
        pygame.draw.lines(s, base, False, [(6,33),(17,24),(30,28),(44,20),(57,26)], 8)
        pygame.draw.lines(s, hi, False, [(8,30),(18,22),(29,26),(43,18),(56,24)], 2)
        pygame.draw.polygon(s, dark, [(9,33),(2,28),(4,38)])
        pygame.draw.circle(s,(226,240,248),(54,24),2); pygame.draw.line(s,dark,(49,19),(60,15),2)
    elif kind == 'root_scorpion':
        pygame.draw.ellipse(s, base, (18,22,28,19)); pygame.draw.ellipse(s,dark,(24,14,18,16))
        pygame.draw.line(s, hi,(16,29),(7,23),4); pygame.draw.line(s, hi,(48,30),(57,24),4)
        for x,y in ((20,34),(25,39),(33,39),(40,34)): pygame.draw.line(s,dark,(x,y),(x-5,y+8),2)
        pygame.draw.lines(s, base, False, [(43,20),(52,15),(55,8),(51,4)], 4); pygame.draw.circle(s,(197,216,103),(51,6),2)
    elif kind == 'basalt_tortoise':
        pygame.draw.ellipse(s, dark, (8,18,46,27)); pygame.draw.ellipse(s, base, (11,14,42,27)); pygame.draw.polygon(s,hi,[(17,18),(24,9),(30,18),(39,10),(43,21),(30,26)])
        for x in (17,25,38,46): pygame.draw.line(s,dark,(x,35),(x-3,44),4)
        pygame.draw.circle(s,(217,191,126),(51,25),3); pygame.draw.line(s,dark,(52,28),(60,34),3)
    elif kind == 'salt_spider':
        pygame.draw.ellipse(s,dark,(23,19,18,16)); pygame.draw.ellipse(s,base,(25,16,15,14))
        for a,b,c,d in ((25,22,9,14),(25,26,7,25),(27,30,12,36),(39,22,53,14),(39,26,56,25),(37,30,51,37),(30,18,19,10),(34,18,47,10)):
            pygame.draw.line(s,hi,(a,b),(c,d),2)
        pygame.draw.circle(s,(239,226,164),(29,21),1); pygame.draw.circle(s,(239,226,164),(36,21),1)
    elif kind == 'luminous_stag':
        pygame.draw.polygon(s,base,[(11,34),(18,25),(31,23),(42,28),(50,23),(54,30),(45,34),(41,41),(20,40)])
        for x in (19,29,40,47): pygame.draw.line(s,dark,(x,35),(x-2,46),3)
        pygame.draw.polygon(s,hi,[(36,24),(39,15),(48,11),(45,18),(53,13),(49,21),(55,19),(50,26)])
        pygame.draw.circle(s,(235,255,201),(47,25),2); pygame.draw.circle(s,(230,245,213),(42,19),1)
    elif kind == 'shadow_panther':
        pygame.draw.polygon(s,base,[(8,34),(17,25),(34,23),(47,27),(55,23),(55,29),(48,33),(42,40),(20,40),(13,37)])
        for x in (19,30,41,49): pygame.draw.line(s,dark,(x,34),(x-2,45),3)
        pygame.draw.polygon(s,hi,[(17,25),(17,14),(25,21),(31,14),(33,24)])
        pygame.draw.line(s,base,(47,30),(61,17),4); pygame.draw.circle(s,(214,115,236),(28,23),2)
    elif kind == 'spore_manta':
        pygame.draw.polygon(s,base,[(32,14),(40,25),(57,35),(41,38),(32,30),(23,38),(7,34),(24,24)])
        pygame.draw.polygon(s,hi,[(32,17),(37,25),(50,33),(38,34),(32,28)])
        for x in (18,24,32,40): pygame.draw.circle(s,(198,232,165),(x,28+sway),2)
        pygame.draw.circle(s,(223,238,188),(32,27),2)
    elif kind == 'ferrous_mite':
        pygame.draw.ellipse(s,dark,(18,20,28,18)); pygame.draw.ellipse(s,base,(20,16,25,18))
        for x in (18,24,31,37,44): pygame.draw.line(s,hi,(x,29),(x-5,42),2)
        pygame.draw.circle(s,hi,(43,21),2); pygame.draw.circle(s,hi,(49,26),1)
    elif kind == 'magnetic_ram':
        pygame.draw.polygon(s,base,[(8,34),(18,24),(36,23),(47,29),(55,24),(57,32),(49,35),(44,41),(17,41),(12,37)])
        pygame.draw.polygon(s,hi,[(38,25),(43,15),(48,22),(54,16),(52,29)])
        for x in (18,31,43,50): pygame.draw.line(s,dark,(x,35),(x-2,46),3)
        pygame.draw.circle(s,(220,228,219),(48,27),2)
    elif kind == 'gloom_moth':
        pygame.draw.ellipse(s,base,(28,13,12,29)); pygame.draw.polygon(s,hi,[(28,20),(7,8),(17,31),(29,29)]); pygame.draw.polygon(s,hi,[(40,20),(57,8),(51,31),(39,29)])
        pygame.draw.line(s,dark,(34,41),(31,49),2); pygame.draw.line(s,dark,(36,41),(41,49),2); pygame.draw.circle(s,(205,140,231),(34,19),2)
    elif kind == 'vesper_cat':
        pygame.draw.polygon(s,base,[(9,35),(18,25),(35,24),(47,29),(55,25),(55,32),(46,35),(41,41),(18,41),(13,37)]); pygame.draw.polygon(s,hi,[(15,26),(19,14),(27,23),(36,14),(39,26)])
        for x in (19,29,41,49): pygame.draw.line(s,dark,(x,35),(x-2,46),3)
        pygame.draw.circle(s,(214,119,226),(48,29),2)
    elif kind == 'charge_ray':
        pygame.draw.polygon(s,base,[(3,31),(18,16),(31,22),(43,13),(61,28),(42,34),(31,42),(17,36)]); pygame.draw.circle(s,hi,(30,28),4); pygame.draw.line(s,hi,(9,31),(1,39),2); pygame.draw.line(s,hi,(53,28),(63,34),2)
    elif kind == 'ion_toad':
        pygame.draw.ellipse(s,base,(13,20,39,25)); pygame.draw.circle(s,hi,(23,21),7); pygame.draw.circle(s,hi,(42,21),7); pygame.draw.circle(s,(35,35,40),(24,20),2); pygame.draw.circle(s,(35,35,40),(41,20),2); pygame.draw.line(s,dark,(18,40),(11,47),3); pygame.draw.line(s,dark,(47,39),(55,47),3)
    elif kind == 'cinder_strider':
        pygame.draw.ellipse(s,base,(24,13,19,28)); pygame.draw.polygon(s,hi,[(28,16),(31,5),(36,15),(40,6),(43,18)]); pygame.draw.line(s,dark,(29,38),(18,49),2); pygame.draw.line(s,dark,(34,39),(30,50),2); pygame.draw.line(s,dark,(41,38),(51,49),2); pygame.draw.line(s,hi,(44,23),(59,16),2)
    elif kind == 'magma_beetle':
        pygame.draw.ellipse(s,dark,(9,17,50,28)); pygame.draw.ellipse(s,base,(12,14,45,27)); pygame.draw.line(s,hi,(16,21),(53,21),3); pygame.draw.line(s,dark,(18,34),(10,45),2); pygame.draw.line(s,dark,(28,37),(23,48),2); pygame.draw.line(s,dark,(40,35),(48,46),2); pygame.draw.circle(s,(255,162,66),(35,23),2)
    elif kind == 'reef_skimmer':
        pygame.draw.polygon(s,base,[(3,31),(17,19),(31,22),(42,16),(60,28),(44,35),(30,41),(16,37)]); pygame.draw.line(s,hi,(18,24),(41,29),2); pygame.draw.circle(s,hi,(45,26),2)
    elif kind == 'tide_serpent':
        pygame.draw.lines(s,base,False,[(4,34),(16,24),(28,31),(40,20),(57,27)],7); pygame.draw.lines(s,hi,False,[(6,31),(17,21),(28,28),(40,17),(56,24)],2); pygame.draw.circle(s,hi,(55,24),2)
    elif kind == 'spore_hare':
        pygame.draw.ellipse(s,base,(13,24,37,20)); pygame.draw.ellipse(s,hi,(38,12,16,18)); pygame.draw.polygon(s,hi,[(41,14),(42,3),(47,14),(51,5),(54,17)]); pygame.draw.line(s,dark,(19,39),(15,49),3); pygame.draw.line(s,dark,(42,39),(47,49),3); pygame.draw.circle(s,(230,245,197),(49,20),2)
    elif kind == 'mycelial_beast':
        pygame.draw.polygon(s,base,[(10,41),(12,26),(19,17),(28,12),(41,16),(49,24),(52,41)]); pygame.draw.polygon(s,hi,[(17,22),(25,10),(34,18),(41,7),(47,23)]); pygame.draw.line(s,dark,(23,40),(20,49),3); pygame.draw.line(s,dark,(40,40),(44,49),3); pygame.draw.circle(s,(210,239,176),(29,24),2)
    elif kind == 'wind_stalker':
        pygame.draw.polygon(s,base,[(22,42),(18,24),(26,15),(38,18),(46,29),(42,43),(32,38)]); pygame.draw.line(s,hi,(19,29),(8,18),2); pygame.draw.line(s,hi,(43,31),(58,19),2); pygame.draw.line(s,dark,(27,40),(22,52),3); pygame.draw.line(s,dark,(37,40),(44,51),3); pygame.draw.polygon(s,hi,[(24,16),(28,7),(33,15),(37,7),(40,18)])
    elif kind == 'leviwing':
        pygame.draw.polygon(s,base,[(31,11),(42,24),(59,31),(42,37),(31,29),(20,37),(4,31),(20,23)]); pygame.draw.polygon(s,hi,[(31,14),(37,24),(50,31),(38,32),(31,27)]); pygame.draw.circle(s,(225,232,247),(31,25),2)
    elif kind == 'street_drone':
        pygame.draw.polygon(s,base,[(16,12),(47,12),(53,41),(10,41)]); pygame.draw.rect(s,dark,(18,20,27,11),border_radius=2); pygame.draw.line(s,hi,(23,25),(40,25),2); pygame.draw.circle(s,(118,230,223),(47,17),2); pygame.draw.line(s,hi,(16,41),(10,48),2); pygame.draw.line(s,hi,(46,41),(52,48),2)
    elif kind == 'plasma_hound':
        pygame.draw.polygon(s,base,[(7,35),(15,24),(31,21),(44,26),(53,22),(56,30),(47,34),(42,41),(20,41),(13,38)]); pygame.draw.polygon(s,hi,[(16,25),(22,14),(27,23),(34,13),(39,26)]); pygame.draw.line(s,dark,(20,36),(17,47),3); pygame.draw.line(s,dark,(39,36),(43,47),3); pygame.draw.line(s,hi,(48,29),(61,20),3); pygame.draw.circle(s,(107,230,255),(44,27),2)
    else:
        return None
    return s

def sprite(kind, frame=0):
    if kind=='hero': return make_hero_world_sprite('down', frame)
    if kind in {'salamander_igneous','ironback_crab','ion_wasp','frost_wolf','crystal_grazer','glacial_eel','root_scorpion','basalt_tortoise','salt_spider','luminous_stag','shadow_panther','spore_manta','ferrous_mite','magnetic_ram','gloom_moth','vesper_cat','charge_ray','ion_toad','cinder_strider','magma_beetle','reef_skimmer','tide_serpent','spore_hare','mycelial_beast','wind_stalker','leviwing','street_drone','plasma_hound'}:
        return make_new_fauna_sprite(kind, frame)
    if kind=='scarab': return make_scarab_sprite(frame)
    if kind=='lizard': return make_lizard_sprite(frame)
    if kind=='hound': return make_hound_sprite(frame)
    if kind=='burrower': return make_burrower_sprite(frame)
    if kind=='manta': return make_manta_sprite(frame)
    if kind=='stalker': return make_stalker_sprite(frame)
    if kind=='kuvaar': return make_kuvaar_sprite(frame)
    if kind in {'fagor','kael','ounull','alphor','broom'}: return make_boss_sprite(kind, frame)
    if kind == 'ry': return make_ry_sprite(frame)
    if kind == 'nahr_shadow': return make_nahr_shadow_sprite(frame)
    if kind=='avarin': return make_avarin_sprite(False,frame)
    if kind=='avarin_guard': return make_avarin_sprite(True,frame)
    s=pygame.Surface((48,52),pygame.SRCALPHA); pygame.draw.polygon(s,(77,103,119),[(4,40),(13,18),(29,14),(44,24),(37,42),(12,44)]); pygame.draw.rect(s,PX_CYAN,(17,28,13,4)); return s

def make_shadow():
    s=pygame.Surface((34,12),pygame.SRCALPHA); pygame.draw.ellipse(s,(0,0,0,80),(0,0,34,12)); return s
SHADOW=make_shadow()

class App:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption('Cinzas de Órion | 0.7.2')
        self.canvas = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.fonts = {n: pygame.font.SysFont('consolas', n, bold=n >= 25) for n in (12, 13, 14, 15, 16, 18, 22, 28, 40)}
        self.state, self.message = load_campaign(SAVE_DIR, legacy_directories=(ROOT,), current_filename='save.json')
        # A campanha é carregada primeiro para manter o save íntegro; a tela de título
        # segura a apresentação até uma tecla, quando o último save é carregado novamente.
        self.mode = 'title'
        self._popup_message = None
        self._popup_until = 0.0
        self.ship_diagnostic_rows = []
        self.ship_diagnostic_summary = ''
        # O menu é uma camada global: ao fechá-lo, a campanha sempre retorna ao mundo.
        # O estado de combate não passa pelo menu nesta versão.
        # Histórico real de navegação: cada tela aberta empilha a anterior.
        # ESC sempre remove somente a tela atual, preservando a origem exata.
        self.nav_stack = []
        self.menu_return_mode = 'world'
        self.panel_return_mode = 'world'
        self.state.refresh_journal()
        self.buttons = []
        self.frame = 0.0
        self.move_wait = 0
        self.patrol_wait = 0
        self.visual_pos = [float(x) for x in self.state.pos]
        self.phase, self.phase_time = 'choose', 0.0
        self.result, self.loot = {}, {}
        self.selected_slot = 0
        self.selected_memory_slot = 0
        self.craft_page = 0
        self.album_page = 0
        self.album_section = 'collection'
        self.unique_card_source = None
        self.unique_gacha_card_id = None
        self.unique_gacha_kind = None
        self.unique_gacha_until = 0.0
        self.craft_reward_card_id = None
        self.craft_reward_until = 0.0
        self.craft_notice = None
        self.craft_notice_until = 0.0
        self.achievement_page = 0
        self.achievement_category = 'Todos'
        self.inventory_selected_item = None
        self.statistics_category = 'Combate'
        self.journal_category = 'Campanha'
        self.ship_mission_id = None
        self.craft_category = 'Equipamento'
        self.selected_route_id = getattr(self.state, 'selected_planet', 'veyra')
        self.travel_origin_planet = None
        self.travel_target_planet = None
        self.travel_time = 0.0
        self.travel_duration = 3.2
        self.travel_encounter_pending = False
        self.travel_encounter_trigger = 0.0
        self.travel_encounter_result = None
        self.asteroid_game = None
        self.renown_category = 'Veyra'
        self.domain_selected = 'Água'
        self.loadout_selected = 0
        self.civ_mission_civ = None
        self.challenge_menu_open = False
        self.battle_species = "scarab"
        self.bestiary_selected = None
        self.facing = 'down'
        self.attack_kind = 'basic'
        self.selected_battle_target = 'body'
        self.dialogue_npc = None
        self.mission_id = 'water_supply'
        self.journal_selected_mission = 'water_supply'
        self.ui_scroll = {'journal': 0, 'journal_list': 0, 'status_left': 0, 'status_right': 0, 'inventory_materials': 0, 'inventory_details': 0, 'gauntlet_nexus': 0, 'resources': 0, 'card_picker': 0, 'unique_card_craft': 0, 'statistics': 0, 'bestiary': 0, 'bestiary_detail': 0, 'bestiary_list': 0, 'renown': 0, 'routes_right': 0, 'achievements': 0, 'helmet_config': 0, 'simulator': 0, 'stellar_destinations': 0, 'domain': 0, 'loadouts': 0, 'civilization_missions': 0, 'card_picker_preview': 0}
        self.scroll_drag = None
        self.scrollbars = {}
        self.achievement_alert_text = None
        self.achievement_alert_kind = None
        self.achievement_alert_until = 0.0
        self.card_alert_cid = None
        self.card_fx = None
        self.enemy_fx = None
        self.stasis_qte = None
        self.language_qte = None
        self.card_picker_slot = None
        self.card_picker_selection = None
        self.hack_return_mode = 'world'
        self.victory_boss = None
        self.last_combat_summary = None
        self.combat_summary = self._new_combat_summary()
        self.combat_narration = None
        self.ship_popup_kind = None
        self.ship_popup_notice = ''
        self.hero_sprites = {(direction, f): make_hero_world_sprite(direction, f) for direction in ('down','up','left','right') for f in range(2)}
        # Sprites-base externos do protagonista. Quando presentes, substituem apenas
        # a arte-base do mundo; o sprite de combate continua usando a pose frontal própria.
        self.hero_images = {}
        self.hero_image_mtimes = {}
        self.hero_dir = ROOT / 'assets' / 'player'
        self._refresh_hero_images(force=True)
        self.sprites = {(k, f): sprite(k, f) for k in (*SPECIES, 'avarin', 'avarin_guard', *BOSSES, 'nahr_shadow') for f in range(2)}
        self.element_badges = {}
        element_dir = ROOT / 'assets' / 'elements'
        for element, filename in ELEMENT_BADGE_FILES.items():
            badge_path = element_dir / filename
            if badge_path.exists():
                try:
                    self.element_badges[element] = pygame.image.load(str(badge_path)).convert_alpha()
                except (pygame.error, OSError):
                    pass
        # Os quatro assets de equipamento não acompanham o ZIP por solicitação do
        # usuário. Quando presentes, substituem a arte procedural apenas nas
        # visualizações das peças; caso não estejam presentes, o fallback antigo
        # permanece para preservar a funcionalidade da build.
        self.equipment_images = {}
        self.equipment_image_mtimes = {}
        self.equipment_dir = ROOT / 'assets' / 'equips'
        # Os arquivos são fornecidos manualmente pelo usuário. A leitura é feita
        # também sob demanda em draw_gear_piece(), permitindo que os PNGs sejam
        # colocados na pasta depois da inicialização sem exigir alteração de código.
        self._refresh_equipment_images(force=True)
        self.rarity_styles = {
            'Comum': dict(edge=(103, 117, 122), fill=(17, 25, 31), width=1, accent=(156, 167, 164)),
            'Incomum': dict(edge=(87, 173, 153), fill=(13, 34, 33), width=2, accent=(116, 220, 194)),
            'Rara': dict(edge=(100, 143, 207), fill=(13, 27, 47), width=2, accent=(125, 176, 240)),
            'Mítica': dict(edge=(168, 104, 193), fill=(35, 19, 42), width=3, accent=(206, 141, 232)),
            'Lendária': dict(edge=(226, 170, 70), fill=(49, 33, 14), width=3, accent=(251, 211, 112)),
            'Única': dict(edge=(239, 106, 77), fill=(49, 19, 15), width=4, accent=(255, 158, 123)),
        }
        self.terrains = {key: self.make_terrain(key) for key in SECTORS}
        self.sync_sector()
        # Estrelas determinísticas para a tela inicial: sem randomização por quadro.
        self.title_stars = [
            ((i * 83 + 31) % (W - 30) + 15, (i * 47 + 19) % (H - 90) + 20,
             1 + ((i * 7) % 3), (i % 9) * 0.37, 0.7 + (i % 5) * 0.14)
            for i in range(78)
        ]
        self.running = True

    def font(self, size):
        # Cria a fonte sob demanda para evitar KeyError quando uma tela usar
        # um tamanho que não estava pré-cadastrado na inicialização.
        size = int(size)
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont('consolas', size, bold=size >= 25)
        return self.fonts[size]

    def label(self, value, x, y, size=18, color=INK):
        self.canvas.blit(self.font(size).render(str(value), True, color), (x, y))

    def fit_text(self, value, size, max_width):
        """Encurta textos de interface para nunca escapar da área disponível."""
        value = str(value)
        fnt = self.font(size)
        if fnt.size(value)[0] <= max_width:
            return value
        ellipsis = '…'
        while value and fnt.size(value + ellipsis)[0] > max_width:
            value = value[:-1]
        return (value.rstrip() + ellipsis) if value else ellipsis

    def set_message(self, value):
        self.message = str(value)
        # Qualquer nova interação reinicia o display, mesmo que o texto seja igual ao anterior.
        self._popup_message = None
        self._popup_until = 0.0

    def wrap(self, value, x, y, width, size=16, color=MUTED, leading=23):
        words, line = str(value).split(), ''
        for word in words:
            trial = f'{line} {word}'.strip()
            if self.font(size).size(trial)[0] > width and line:
                self.label(line, x, y, size, color); y += leading; line = word
            else:
                line = trial
        if line:
            self.label(line, x, y, size, color)
        return y + leading

    def box(self, rect, color=PANEL, border=EDGE):
        pygame.draw.rect(self.canvas, color, rect, border_radius=8)
        if border:
            pygame.draw.rect(self.canvas, border, rect, 1, border_radius=8)

    def button(self, rect, title, callback, enabled=True, subtitle=None):
        rect = pygame.Rect(rect)
        hover = rect.collidepoint(self.mouse())
        color = (39, 65, 70) if enabled and hover else PANEL
        self.box(rect, color, TEAL if enabled and hover else EDGE)
        title_text = self.fit_text(title, 16, max(20, rect.width - 28))
        self.label(title_text, rect.x+14, rect.y+11, 16, INK if enabled else MUTED)
        if subtitle:
            subtitle_text = self.fit_text(subtitle, 14, max(20, rect.width - 28))
            self.label(subtitle_text, rect.x+14, rect.y+36, 14, TEAL if enabled else MUTED)
        self.buttons.append((rect, callback, enabled))

    def mouse(self):
        ww, wh = self.window.get_size()
        scale = min(ww/W, wh/H)
        mx, my = pygame.mouse.get_pos()
        return ((mx-(ww-W*scale)/2)/scale, (my-(wh-H*scale)/2)/scale)

    def bar(self, x, y, width, value, maximum, color):
        pygame.draw.rect(self.canvas, (12, 20, 29), (x, y, width, 9), border_radius=4)
        ratio = max(0, min(1, value/maximum)) if maximum > 0 else 0
        pygame.draw.rect(self.canvas, color, (x, y, int(width*ratio), 9), border_radius=4)

    def sync_sector(self):
        self.rocks = self.state.area['rocks']
        self.visual_pos = list(map(float, self.state.pos))
        self.patrol_wait = 1.8

    def project(self, x, y):
        px, py = iso(x, y)
        cx, cy = iso(*self.visual_pos)
        return (px-cx+445, py-cy+335)

    def make_terrain(self, sector):
        data = SECTORS[sector]
        size = data['size']
        s = pygame.Surface((size*54+54, size*28+56), pygame.SRCALPHA)
        for depth in range(size*2):
            for x in range(size):
                y = depth-x
                if not 0 <= y < size:
                    continue
                px, py = size*27+(x-y)*27, 20+(x+y)*14
                v = (x*17+y*11)%9
                pts = [(px, py-14), (px+27, py), (px, py+14), (px-27, py)]
                water = data.get('water_tiles', set())
                island = data.get('island_tiles', set())
                if (x,y) in island:
                    base_color = (69, 108, 67)
                elif (x,y) in water:
                    base_color = (43, 103, 118)
                else:
                    base_color = tuple(c+v for c in data['tint'])
                pygame.draw.polygon(s, base_color, pts)
                if data.get('forest_style') and (x*3+y*5)%9==0 and (x,y) not in water:
                    pygame.draw.circle(s, (43,91,53), (px+5, py-7), 7)
                    pygame.draw.circle(s, (55,112,63), (px-3, py-5), 6)
                    pygame.draw.line(s, (76,62,43), (px, py+7), (px, py-1), 2)
                elif data.get('lava_style') and (x*5+y*3)%11==0:
                    pygame.draw.line(s, (187,78,47), (px-11, py+2), (px+4, py-4), 2)
                elif (x+y)%4 == 0:
                    pygame.draw.line(s, (155, 126, 92), (px-9, py), (px-3, py+2), 1)
                if x == size-1 or y == size-1:
                    pygame.draw.line(s, (69, 54, 49), (px, py+14), (px, py+23), 5)
        return s

    def aurora_detail_color(self):
        return {
            0: PX_CYAN,
            1: (224, 112, 93),
            2: (236, 187, 100),
            3: (86, 150, 240),
        }.get(int(getattr(self.state, 'aurora_level', 0)), PX_CYAN)

    def draw_helmet_overlay(self, surface, raw_width, raw_height, design_id, pose='world', direction='down'):
        """Desenha o design do elmo sobre o sprite base em suas quatro direções."""
        data = HELMET_DESIGNS.get(design_id, HELMET_DESIGNS['tactical'])
        sx = surface.get_width() / max(1, raw_width)
        sy = surface.get_height() / max(1, raw_height)
        shell = data.get('shell', (62, 77, 87))
        visor = data.get('visor', PX_CYAN)
        accent = data.get('accent', PX_CYAN)
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        def P(x, y):
            return (int(x * sx), int(y * sy))
        def R(color, rect, radius=0):
            rr = pygame.Rect(int(rect[0]*sx), int(rect[1]*sy), max(1,int(rect[2]*sx)), max(1,int(rect[3]*sy)))
            pygame.draw.rect(layer, color, rr, border_radius=max(0,int(radius*sx)))
        def L(color, a, b, width=1):
            pygame.draw.line(layer, color, P(*a), P(*b), max(1,int(width*min(sx,sy))))
        def Poly(color, pts):
            pygame.draw.polygon(layer, color, [P(*pt) for pt in pts])

        if pose == 'combat':
            # Cabeça frontal na pose de combate, proporcional ao sprite 84x66.
            Poly(shell, [(24,8),(31,3),(42,1),(51,5),(56,13),(54,21),(47,24),(28,22),(22,16)])
            Poly((max(0,shell[0]-15),max(0,shell[1]-15),max(0,shell[2]-15)), [(27,8),(31,4),(41,3),(48,6),(51,11),(48,12),(30,12)])
            R(visor, (29,10,19,4), 1)
            L(accent, (30,14), (47,14), 1)
            if design_id == 'recon':
                L(accent, (49,7), (54,2), 2); R(accent, (52,2,4,4), 1)
            elif design_id == 'combat':
                Poly((52,55,64), [(24,13),(28,20),(31,22),(27,22)])
                Poly((52,55,64), [(50,13),(54,12),(57,18),(52,22)])
            else:
                R((43,58,67), (25,16,29,3), 1)
        elif direction == 'up':
            Poly(shell, [(15,8),(18,3),(27,1),(34,4),(38,9),(36,18),(19,18)])
            Poly((max(0,shell[0]-12),max(0,shell[1]-12),max(0,shell[2]-12)), [(18,7),(21,3),(31,3),(35,8),(33,11),(19,11)])
            L(accent, (19,13), (34,13), 1)
            if design_id == 'recon':
                R(accent, (29,3,7,3), 1)
                L(accent, (36,7), (40,2), 2)
            elif design_id == 'combat':
                R((52,55,64), (17,15,21,3), 1)
                R((52,55,64), (34,14,5,4), 1)
        elif direction in ('left','right'):
            # Perfil lateral: não espelhar automaticamente detalhes da Manopla;
            # somente o capacete acompanha o sentido do rosto.
            if direction == 'right':
                Poly(shell, [(18,6),(23,3),(29,4),(33,8),(32,15),(27,19),(19,17),(16,12)])
                R(visor, (26,8,7,3), 1)
                L(accent, (28,12), (33,12), 1)
                if design_id == 'recon':
                    L(accent, (29,5), (35,1), 2); R(accent, (34,1,3,4), 1)
                elif design_id == 'combat':
                    Poly((52,55,64), [(16,10),(21,7),(23,18),(18,17)])
                    R((52,55,64), (28,14,5,4), 1)
            else:
                Poly(shell, [(26,6),(21,3),(15,4),(11,8),(12,15),(17,19),(25,17),(28,12)])
                R(visor, (11,8,7,3), 1)
                L(accent, (11,12), (16,12), 1)
                if design_id == 'recon':
                    L(accent, (15,5), (9,1), 2); R(accent, (7,1,3,4), 1)
                elif design_id == 'combat':
                    Poly((52,55,64), [(28,10),(23,7),(21,18),(26,17)])
                    R((52,55,64), (11,14,5,4), 1)
        else:
            Poly(shell, [(15,8),(18,3),(27,1),(34,4),(39,9),(37,18),(20,18)])
            Poly((max(0,shell[0]-12),max(0,shell[1]-12),max(0,shell[2]-12)), [(18,7),(21,3),(31,3),(36,8),(33,11),(19,11)])
            R(visor, (20,9,16,4), 1)
            L(accent, (21,14), (36,14), 1)
            if design_id == 'recon':
                L(accent, (31,6), (37,2), 2); R(accent, (36,2,3,4), 1)
            elif design_id == 'combat':
                Poly((52,55,64), [(15,12),(20,8),(20,19),(16,18)])
                Poly((52,55,64), [(35,8),(40,11),(37,19),(34,18)])
        surface.blit(layer, (0,0))

    def draw_aurora_detail(self, surface, raw_width, raw_height, pose='world'):
        sx = surface.get_width() / max(1, raw_width)
        sy = surface.get_height() / max(1, raw_height)
        col = self.aurora_detail_color()
        cx, cy = ((36,29) if pose == 'combat' else (22,29))
        cx, cy = int(cx * sx), int(cy * sy)

        # Glow propositalmente pequeno: só o suficiente para transmitir que a
        # AURORA está energizada, sem transformar o peito em uma fonte de luz.
        pulse = 0.72 + 0.28 * (0.5 + 0.5 * math.sin(self.frame * 3.2))
        glow = pygame.Surface(surface.get_size())
        glow.fill((0, 0, 0))
        r1 = max(4, int(7 * min(sx, sy) * pulse))
        r2 = max(2, int(r1 * 0.58))
        dim = tuple(max(0, int(c * 0.24)) for c in col)
        mid = tuple(max(0, int(c * 0.52)) for c in col)
        bright = tuple(min(255, int(c * 0.95)) for c in col)
        pygame.draw.circle(glow, dim, (cx, cy), r1)
        pygame.draw.circle(glow, mid, (cx, cy), r2 + 2)
        pygame.draw.circle(glow, bright, (cx, cy), r2)
        surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        if pose == 'combat':
            pts = [(36,24),(40,29),(36,34),(32,29)]
            pygame.draw.polygon(layer, col, [(int(x*sx),int(y*sy)) for x,y in pts])
            pygame.draw.polygon(layer, (min(255,col[0]+35),min(255,col[1]+35),min(255,col[2]+35),255), [(int(x*sx),int(y*sy)) for x,y in [(36,26),(38,29),(36,32),(34,29)]])
        elif pose == 'world':
            pygame.draw.polygon(layer, col, [(int(x*sx),int(y*sy)) for x,y in [(22,25),(26,29),(22,34),(18,29)]])
            pygame.draw.polygon(layer, (min(255,col[0]+30),min(255,col[1]+30),min(255,col[2]+30),255), [(int(x*sx),int(y*sy)) for x,y in [(22,27),(24,29),(22,32),(20,29)]])
        surface.blit(layer, (0,0))

    def actor(self, kind, x, y, scale=1.5, frame=0, flip=False, pose='world', direction=None):
        hero_direction = direction or getattr(self, 'facing', 'down')
        if kind == 'hero' and pose == 'combat':
            raw = make_hero_combat_sprite(frame % 2)
        elif kind == 'hero':
            self._refresh_hero_images()
            raw = self.hero_images.get((hero_direction, frame % 2), self.hero_sprites[(hero_direction, frame % 2)])
        else:
            raw = self.sprites[(kind, frame % 2)]
        if flip:
            raw = pygame.transform.flip(raw, True, False)
        im = pygame.transform.scale(raw, (int(raw.get_width()*scale), int(raw.get_height()*scale)))
        if kind == 'hero':
            self.draw_aurora_detail(im, raw.get_width(), raw.get_height(), pose=pose)
            if getattr(self.state, 'helmet_equipped', False):
                design = getattr(self.state, 'helmet_design', None) or 'tactical'
                self.draw_helmet_overlay(im, raw.get_width(), raw.get_height(), design, pose=pose, direction=hero_direction)
        shadow_w=max(24,int(34*scale)); shadow_h=max(8,int(12*scale)); pygame.draw.ellipse(self.canvas,(50,43,39),(int(x-shadow_w/2),int(y-shadow_h/2),shadow_w,shadow_h))
        self.canvas.blit(im,(int(x-im.get_width()/2),int(y-im.get_height()+4)))

    def ship(self, x, y, shadow=True):
        # Nave em linguagem pixel-art: pequena, modular e com leitura clara dos
        # pontos funcionais/danificados, mantendo a silhueta já estabelecida.
        if shadow:
            pygame.draw.ellipse(self.canvas, (51, 43, 40), (x-58, y+2, 116, 34))
        pygame.draw.polygon(self.canvas, (54, 70, 81), [(x-67,y+8),(x-24,y-10),(x+36,y-12),(x+66,y+7),(x+48,y+20),(x+4,y+14),(x-43,y+21)])
        pygame.draw.polygon(self.canvas, (123,138,147), [(x-24,y-10),(x+36,y-12),(x+48,y+1),(x-16,y+2)])
        pygame.draw.polygon(self.canvas, (34,48,58), [(x+9,y-10),(x+35,y-8),(x+48,y+1),(x+18,y+2)])
        pygame.draw.line(self.canvas, (181,193,198), (x-14,y-7),(x+28,y-8), 1)
        pygame.draw.polygon(self.canvas, (70,92,104), [(x-1,y-4),(x+12,y-27),(x+27,y-5),(x+18,y+5),(x+5,y+5)])
        pygame.draw.polygon(self.canvas, TEAL, [(x+10,y-21),(x+19,y-8),(x+11,y-4),(x+4,y-10)])
        pygame.draw.rect(self.canvas, (81,96,104), (x-49,y+8,17,9)); pygame.draw.rect(self.canvas, (168,93,70), (x-47,y+10,12,4))
        pygame.draw.rect(self.canvas, (81,96,104), (x+33,y+5,16,10)); pygame.draw.rect(self.canvas, (198,113,76), (x+36,y+7,10,3))
        for offset in (-39, 26):
            pygame.draw.line(self.canvas, (72,84,91), (x+offset,y+15),(x+offset-4,y+27), 2)
            pygame.draw.rect(self.canvas, (70,80,86), (x+offset-8,y+26,8,3))
        pygame.draw.circle(self.canvas, (27,31,35), (x-8,y+10), 4)
        pygame.draw.circle(self.canvas, (27,31,35), (x+24,y+9), 3)
        pygame.draw.line(self.canvas, (202,211,216), (x-7,y+7),(x-2,y+12), 1)

    def save(self):
        try:
            self.state.save(SAVE)
            self.set_message(r'Progresso salvo em AppData\Local\Cinzas de Órion\save.json.')
        except (OSError, ValueError) as exc:
            self.set_message(f'Não foi possível salvar: {exc}')

    def _sync_navigation_context(self):
        self.panel_return_mode = self.nav_stack[-1] if self.nav_stack else 'world'

    def set_mode(self, mode, return_to=None):
        """Navega para uma nova tela mantendo o histórico para o ESC.

        return_to é mantido por compatibilidade com chamadas antigas; a tela
        atualmente visível é sempre a origem real do novo painel.
        """
        if mode == self.mode:
            return
        self.nav_stack.append(self.mode)
        self.mode = mode
        self._sync_navigation_context()

    def open_panel(self, mode, return_to='world'):
        if mode == self.mode:
            return
        self.nav_stack.append(self.mode)
        self.mode = mode
        self._sync_navigation_context()

    def close_panel(self):
        if self.nav_stack:
            self.mode = self.nav_stack.pop()
        else:
            self.mode = 'world'
        self._sync_navigation_context()

    def open_menu(self):
        if self.mode == 'menu':
            return
        # O menu é uma camada de primeiro nível: ao sair dele voltamos
        # exatamente para a tela que estava aberta quando o Menu foi chamado.
        self.nav_stack = [self.mode]
        self.menu_return_mode = self.mode
        self.mode = 'menu'
        self._sync_navigation_context()

    def close_menu(self):
        if self.mode != 'menu':
            return
        if self.nav_stack:
            self.mode = self.nav_stack.pop()
        else:
            self.mode = 'world'
        self._sync_navigation_context()

    def reset_mode(self, mode='world'):
        """Vai para uma tela base sem deixar histórico para o ESC.
        Usado somente em transições que encerram uma atividade, como sair
        da nave, terminar um combate ou encerrar a campanha.
        """
        self.nav_stack = []
        self.mode = mode
        self._sync_navigation_context()

    def checkpoint(self):
        message = self.message
        self.save()
        if self.message.startswith('Progresso salvo'):
            self.set_message(message)

    def open_ship_diagnostic(self, return_to='world'):
        rows, summary, changed = self.state.analyze_ship()
        if rows is None:
            self.set_message(summary)
            return
        self.ship_diagnostic_rows = rows
        self.ship_diagnostic_summary = summary
        self.open_panel('ship_diag', return_to)
        self.set_message('Diagnóstico técnico concluído. A decolagem permanece indisponível.')
        if changed:
            self.checkpoint()

    def interact(self):
        if self.state.inside_ship:
            self.ship_interact()
            return
        if self.state.near_ship_exterior():
            if self.state.enter_ship():
                self.reset_mode('ship')
                self.set_message('Escotilha selada. Nave online. E interage com cockpit, computador e painel de status.')
            return
        # Saídas no chão agora também aceitam E; isso resolve pontos de transição
        # que não ficam exatamente na borda do mapa (como Cânion -> Estação).
        exact_exit = self.state.nearby_exit(1)
        if exact_exit:
            ok, msg = self.state.use_nearby_exit(1)
            if ok:
                self.sync_sector()
                self.set_message(msg)
            else:
                self.set_message(msg)
            return

        npc = self.state.nearby_npc()
        if npc:
            text, changed = self.state.interact_npc(npc)
            self.set_message(text)
            pending_civ = getattr(self.state, 'pending_language_civilization', None)
            if pending_civ:
                self.dialogue_npc = npc
                self.language_qte = {
                    'civilization': pending_civ,
                    'npc': npc.get('id'),
                    'until': self.frame + 9.0,
                    'seconds': 9.0,
                    'key': 'ASDFQWE'[sum(ord(c) for c in pending_civ) % 7],
                    'speed': 2.35,
                }
                self.mode = 'language_qte'
                self.nav_stack = ['world']
                self._sync_navigation_context()
                if changed:
                    self.checkpoint()
                return
            if npc.get('civilization') and self.state.knows_language(npc.get('civilization')):
                self.civ_mission_civ = npc.get('civilization')
            conflict_status = self.state.missions.get('faction_conflict', {}).get('status')
            if self.state.language_mastered and npc.get('id') in ('faction_c_leader', 'avarin_waterkeeper') and conflict_status == 'active':
                self.dialogue_npc = npc
                self.mission_id = 'faction_conflict'
                self.open_panel('dialogue', 'world')
            elif self.state.language_mastered and npc.get('id') == 'faction_c_leader' and conflict_status == 'available':
                self.dialogue_npc = npc
                self.mission_id = 'faction_conflict'
                self.open_panel('dialogue', 'world')
            elif self.state.language_mastered and npc.get('id') == 'avarin_waterkeeper' and self.state.missions['kuvaar_hunt']['status'] == 'available':
                self.dialogue_npc = npc
                self.mission_id = 'kuvaar_hunt'
                self.open_panel('dialogue', 'world')
            elif self.state.language_mastered and npc.get('id') == 'avarin_waterkeeper' and self.state.missions['water_supply']['status'] == 'available':
                self.dialogue_npc = npc
                self.mission_id = 'water_supply'
                self.open_panel('dialogue', 'world')
            elif npc.get('civilization') and self.state.knows_language(npc.get('civilization')):
                self.dialogue_npc = npc
                self.civ_mission_civ = npc.get('civilization')
                self.mission_id = None
                self.open_panel('dialogue', 'world')
            if changed:
                self.checkpoint()
            return
        # Pontos no chão são tratados como hotspots de interação reais.
        # A lista vem ordenada por distância e prioridade para evitar que um
        # marco informativo esconda uma estação/terminal/boss próximo.
        for landmark in self.state.nearby_landmarks(1):
            if landmark.get('cultural'):
                ok, text, changed = self.state.analyze_culture()
                self.set_message(text)
                if changed:
                    self.checkpoint()
                return
            if landmark.get('boss_trace'):
                ok, text, changed = self.state.inspect_boss_trace(landmark)
                self.set_message(text)
                if changed:
                    self.checkpoint()
                return
            if landmark.get('boss_site'):
                ok, msg = self.state.start_boss_battle(landmark['boss_site'], virtual=False)
                self.set_message(msg)
                if ok:
                    self.battle_species = landmark['boss_site']
                    self.mode, self.phase, self.phase_time = 'battle', 'choose', 0.0
                    self.visual_pos = list(map(float, self.state.pos))
                return
            if landmark.get('ship_mission_site') == 'ship_comms' and self.state.missions.get('ship_comms',{}).get('status') == 'active':
                ok,msg=self.state.communication_repair(); self.set_message(msg)
                if ok: self.checkpoint()
                return
            if landmark.get('id') == 'kuvaar_diversion' and self.state.missions['kuvaar_hunt']['status'] == 'water':
                self.open_panel('mission_choice', 'world')
                return
        faction_hack_site = self.state.nearby_faction_hack_site()
        if faction_hack_site and self.state.missions.get('faction_conflict', {}).get('status') == 'active':
            ok, text = self.state.start_faction_hack()
            self.set_message(text)
            if ok:
                self.set_mode('hack')
            return
        hack_site = self.state.nearby_hack_site()
        if hack_site and self.state.missions['water_supply']['status'] == 'active':
            ok, text = self.state.start_hack()
            self.set_message(text)
            if ok:
                self.set_mode('hack')
            return
        mission_site = self.state.mission_site()
        if mission_site == 'water_supply' and self.state.missions['water_supply']['status'] == 'active':
            self.mission_id = mission_site
            self.open_panel('mission_choice', 'world')
            return
        generic_landmark = self.state.nearby_landmark()
        if generic_landmark and any(generic_landmark.get(k) for k in ('mission_site','hack_site','diversion')):
            self.set_message(generic_landmark.get('text', 'Ponto de interesse detectado pela Manopla.'))
            return

        nearby_exit = self.state.nearby_exit(1)
        if nearby_exit:
            ok, msg = self.state.use_nearby_exit(1)
            if ok:
                self.sync_sector()
            self.set_message(msg)
            return

        self.set_message(self.state.collect())
        if self.message.startswith('Coletou') or self.message.startswith('Análise cultural'):
            self.checkpoint()
        if self.message.startswith('Aproxime') and any(distance(self.state.pos, p) <= 1 for p in self.rocks):
            if self.state.helmet_scan_abilities().get('rocks'):
                self.set_message('Scan geológico concluído. A composição mineral desta rocha foi registrada pela Manopla.')
            else:
                self.set_message('Rocha intacta. A extração de minerais exigirá um equipamento futuro.')

    def enter_ship_from_menu(self):
        if self.state.near_ship_exterior() and self.state.enter_ship():
            self.reset_mode('ship')
            self.set_message('Entrou na nave. Explore o interior para acessar seus sistemas.')
        else:
            self.set_message('A nave não está acessível deste ponto.')

    def ship_interact(self):
        point = self.state.ship_interaction()
        if point == 'cockpit':
            self.state.ensure_dobra_core_mission()
            if (not self.state.dobra_core_installed
                    and int(self.state.inventory.get('Núcleo de Dobra', 0)) > 0
                    and self.state.missions.get('dobra_core_install', {}).get('status') == 'active'):
                self.ship_popup_kind = 'dobra_core_confirm'
                self.ship_popup_notice = ''
                self.open_panel('ship_popup', 'ship')
                self.set_message('NÚCLEO DE DOBRA detectado. O Cockpit aguarda confirmação para potencializar a nave.')
            elif self.state.missions.get('ship_navigation',{}).get('status') == 'active':
                self.ship_mission_id='ship_navigation'
                self.open_panel('ship_mission','ship')
                self.set_message('Interação de reparo da referência estelar disponível.')
            else:
                self.open_panel('cockpit', 'ship')
                self.set_message('COCKPIT: sistemas de rota e decolagem identificados.')
        elif point == 'computer':
            self.open_panel('ship_computer', 'ship')
            self.set_message('COMPUTADOR DE BORDO: funções internas da nave disponíveis.')
        elif point == 'status':
            self.open_ship_diagnostic('ship')
        elif point == 'simulator':
            if self.state.simulator_built:
                self.open_panel('simulator','chest','renown')
                self.set_message('Simulador de Combate online.')
            elif self.state.simulator_unlocked:
                self.set_message('O módulo do simulador pode ser construído no computador de bordo.')
            else:
                self.set_message('Um suporte vazio aguarda um sistema que ainda não existe na nave.')
        elif point == 'respawn_tank':
            if self.state.respawn_tank_built:
                self.ship_popup_kind = 'respawn_built'
            elif int(self.state.inventory.get('Essência', 0)) < 50:
                self.ship_popup_kind = 'respawn_insufficient'
            else:
                self.ship_popup_kind = 'respawn_confirm'
            self.ship_popup_notice = ''
            self.open_panel('ship_popup', 'ship')
        elif point == 'essence_storage':
            self.ship_popup_kind = 'essence_storage'
            self.ship_popup_notice = ''
            self.open_panel('ship_popup', 'ship')
        elif point == 'airlock':
            self.state.leave_ship()
            self.reset_mode('world')
            self.set_message('Escotilha aberta. Retornando ao exterior.')
        else:
            self.set_message('A nave está silenciosa. Há módulos e cabos sem energia ao longo do corredor.')

    def accept_mission(self):
        if self.mission_id == 'faction_conflict':
            ok, msg = self.state.accept_faction_conflict()
            self.set_message(msg)
            if ok:
                self.dialogue_npc = None
                self.close_panel()
                self.checkpoint()
            return
        if self.mission_id == 'kuvaar_hunt':
            ok, msg = self.state.accept_boss_mission()
            self.set_message(msg)
            if ok:
                self.dialogue_npc = None
                self.close_panel()
                self.checkpoint()
            return
        ok, msg = self.state.accept_mission('water_supply')
        self.set_message(msg)
        if ok:
            self.dialogue_npc = None
            self.close_panel()
            self.checkpoint()

    def faction_conflict_action(self, path):
        if self.mission_id != 'faction_conflict' or self.state.missions.get('faction_conflict', {}).get('status') != 'active':
            return
        if path == 'sabotage':
            ok, msg = self.state.start_faction_hack()
            self.set_message(msg)
            if ok:
                self.close_panel()
                self.set_mode('hack')
            return
        if path == 'warn':
            ok, msg = self.state.resolve_faction_conflict('warn')
            self.set_message(msg)
            if ok:
                self.close_panel()
                self.checkpoint()
            return

    def mission_action(self, path):
        if self.mission_id == 'kuvaar_hunt':
            ok, msg = self.state.prepare_kuvaar_water(path)
            self.set_message(msg)
            if ok:
                self.close_panel(); self.checkpoint()
            return
        if path == 'force':
            self.close_panel()
            if self.state.start_force_mission():
                self.mode, self.phase, self.phase_time = 'battle', 'choose', 0.0
                self.battle_species = 'guard'
                self.set_message('Resistência detectada. A guarda do complexo bloqueou seu acesso.')
            return
        if path == 'hack':
            ok, msg = self.state.start_hack()
            if ok:
                self.hack_return_mode = 'world'
                self.close_panel(); self.set_mode('hack'); self.set_message(msg)
            else:
                self.set_message(msg)
            return
        ok, reward, msg = self.state.complete_mission('water_supply', 'repair')
        if ok:
            self.close_panel()
            self.set_message('Abastecimento restaurado. Recompensa recebida: ' + ', '.join(f'{q} {n}' for n,q in reward.items()) + '.')
            self.checkpoint()
        else:
            self.set_message(msg)

    def hack_event(self, action):
        if action == 'up': self.state.hack_move(0,-1)
        elif action == 'down': self.state.hack_move(0,1)
        elif action == 'left': self.state.hack_move(-1,0)
        elif action == 'right': self.state.hack_move(1,0)
        elif action == 'up_left': self.state.hack_move(-1,-1)
        elif action == 'up_right': self.state.hack_move(1,-1)
        elif action == 'down_left': self.state.hack_move(-1,1)
        elif action == 'down_right': self.state.hack_move(1,1)
        elif action == 'breach':
            result = self.state.hack_breach()
            self.set_message(result['message'])
            if result.get('failed'):
                self.reset_mode('world')
            elif result.get('success'):
                self.reset_mode('world')
                self.checkpoint()
        
    def equip_helmet(self):
        ok, msg = self.state.equip_helmet()
        self.set_message(msg)
        if ok:
            self.checkpoint()

    def configure_memory(self, module):
        self.set_message(self.state.configure_memory(self.selected_memory_slot, module))
        if self.message.startswith('Peitoral reconfigurado'):
            self.checkpoint()

    def rest(self):
        self.set_message(self.state.rest())
        if self.state.at_ship():
            msg = self.message
            self.save()
            if self.message.startswith('Progresso'):
                self.set_message(msg + ' Progresso salvo.')

    def craft(self, cid):
        # Cartas precisam de um fluxo próprio: além de fabricar, mostramos a
        # instância recém-criada em um popup de recompensa. O snapshot evita
        # depender do texto retornado pelo State e funciona para N/+/++ .
        before_crafted = set(self.state.crafted) if isinstance(cid, str) and cid in CARDS else set()
        msg = self.state.craft(cid)
        self.set_message(msg)
        if isinstance(cid, str) and cid in CARDS and msg.startswith('Carta fabricada'):
            created = next((inst for inst in reversed(self.state.crafted) if inst not in before_crafted and not self.state.is_unique_card(inst)), None)
            if created:
                self.craft_reward_card_id = created
                self.craft_reward_until = self.frame + 4.8
            self.checkpoint()
            return
        if self.message.startswith((
            'Kit de reparo fabricado', 'Módulo guardado', 'Peitoral atualizado',
            'Núcleo de decodificação fabricado', 'Célula de energia instável fabricada',
            'Elmo reconstruído', 'Purificador improvisado construído', 'Cinco unidades de Água Pura armazenadas', 'Carga de Simulação armazenada', 'Simulador de Combate construído'
        )):
            self.checkpoint()

    def _show_craft_notice(self, message, seconds=3.6):
        self.craft_notice = str(message)
        self.craft_notice_until = self.frame + float(seconds)

    def _craft_card_ui(self, cid):
        """Entrada única da UI para fabricação de cartas."""
        if not isinstance(cid, str) or cid not in CARDS:
            self._show_craft_notice('Carta inválida.')
            return
        if self.state.battle:
            self._show_craft_notice('Não é possível fabricar cartas durante o combate.')
            return
        card = CARDS[cid]
        conflict = self.state.missions.get('faction_conflict', {})
        if card.get('acquisition') == 'faction_conflict':
            acquisition_ok = conflict.get('status') == 'completed' and conflict.get('winner_card') == cid
        else:
            acquisition_ok = cid in self.state.known_cards
        if not acquisition_ok:
            self._show_craft_notice('Derrote a criatura correspondente para desbloquear esta carta.')
            return
        recipe = card.get('recipe', {})
        for name, qty in recipe.items():
            owned = self.state.essence_total() if name == 'Essência' else int(self.state.inventory.get(name, 0))
            if owned < qty:
                self._show_craft_notice('Faltam materiais. Confira as quantidades na receita.')
                return
        before = set(self.state.crafted)
        message = self.state.craft_card(cid)
        self.set_message(message)
        if not message.startswith('Carta fabricada'):
            self._show_craft_notice(message)
            return
        created = next((inst for inst in reversed(self.state.crafted) if inst not in before and not self.state.is_unique_card(inst)), None)
        if created:
            self.craft_reward_card_id = created
            self.craft_reward_until = self.frame + 4.8
            self.craft_notice = None
            self.craft_notice_until = 0.0
            self.checkpoint()
        else:
            self._show_craft_notice('Carta criada, mas a instância não pôde ser exibida.')

    def equip(self, cid):
        if self.state.equip(cid, self.selected_slot):
            self.set_message(f'{self.state.card_name(cid)} inserida no slot {self.selected_slot+1}.')
            self.card_picker_slot = None
            self.card_picker_selection = None
            self.ui_scroll['card_picker'] = 0
            self.checkpoint()

    def open_card_picker(self, slot_index):
        if slot_index == 'special':
            self.card_picker_slot = 'special'
            self.card_picker_selection = None
            self.ui_scroll['card_picker'] = 0
            self.ui_scroll['card_picker_preview'] = 0
            return
        self.selected_slot = int(slot_index)
        self.card_picker_slot = int(slot_index)
        self.card_picker_selection = None
        self.ui_scroll['card_picker'] = 0
        self.ui_scroll['card_picker_preview'] = 0

    def close_card_picker(self):
        self.card_picker_slot = None
        self.card_picker_selection = None
        self.ui_scroll['card_picker'] = 0
        self.ui_scroll['card_picker_preview'] = 0

    def select_card_for_picker(self, cid):
        if self.card_picker_slot is not None:
            self.card_picker_selection = cid

    def equip_selected_card_from_picker(self):
        slot = self.card_picker_slot
        cid = self.card_picker_selection
        if slot is None or cid is None:
            self._show_craft_notice('Selecione uma carta para equipar.')
            return
        if cid == '__empty__':
            if slot == 'special':
                ok, msg = self.state.unequip_unique()
            else:
                ok, msg = self.state.unequip(int(slot))
            self.set_message(msg)
        elif slot == 'special':
            ok, msg = self.state.equip_unique(cid)
            self.set_message(msg)
        else:
            ok = self.state.equip(cid, int(slot))
            msg = f'{self.state.card_name(cid)} equipada no slot {int(slot)+1}.' if ok else 'Não foi possível equipar esta carta.'
            self.set_message(msg)
        if ok:
            self.close_card_picker()
            self.checkpoint()

    def equip_from_picker(self, cid):
        # Compatibilidade com callbacks antigos: apenas seleciona.
        self.select_card_for_picker(cid)

    def set_facing(self, dx, dy):
        if dx > 0: self.facing = 'right'
        elif dx < 0: self.facing = 'left'
        elif dy > 0: self.facing = 'down'
        elif dy < 0: self.facing = 'up'

    def move(self, dx, dy):
        before_sighting = 'first_sighting' in self.state.journal['seen']
        target = (self.state.pos[0] + dx, self.state.pos[1] + dy)
        blocked_by_water = (
            not self.state.battle
            and self.state.locomotion_generation < 1
            and target in self.state.area.get('water_tiles', set())
        )
        changed_sector = self.state.move(dx, dy)
        if blocked_by_water and not changed_sector:
            self.set_message('O Módulo de Locomoção permite voar sobre a água e alcançar a ilhota de Ounull.')
        journal_changed = self.state.refresh_journal()
        if changed_sector:
            self.sync_sector()
            boss_zone = next((l for l in self.state.area.get('landmarks', []) if l.get('boss_site')), None)
            if boss_zone and self.state.boss_available(boss_zone.get('boss_site')):
                self.set_message('ZONA DE PERIGO! CUIDADO! A leitura ambiental indica uma ameaça de grande porte nas proximidades.')
            else:
                self.set_message(self.state.area['name'] + '. M abre o mapa de rotas; J mostra o diário.')
        if not before_sighting and 'first_sighting' in self.state.journal['seen']:
            self.set_message('Você avista movimento entre as ruínas: há habitantes neste mundo.')
        if journal_changed:
            self.checkpoint()
        self.move_wait = .18

    def _new_combat_summary(self):
        return {
            'dealt': 0, 'taken': 0,
            'dealt_elemental': {element: 0 for element in CREATURE_TYPES},
            'dealt_untyped': 0, 'dealt_dot': 0,
            'dealt_dot_elemental': {'Fogo': 0},
            'dealt_critical': 0, 'critical_hits': 0,
            'attacks': 0, 'misses': 0,
            'turns': 0,
            'advantage_damage': 0, 'advantage_hits': 0,
            'healing': 0, 'max_hit': 0,
            'taken_elemental': {element: 0 for element in CREATURE_TYPES},
            'taken_untyped': 0, 'taken_dot': 0,
            'taken_dot_elemental': {'Fogo': 0},
            'taken_critical': 0, 'taken_critical_hits': 0,
            'enemy_attacks': 0, 'enemy_misses': 0,
            'vampirism_healing': 0, 'shield_absorbed': 0,
            'technique_damage_reduced': 0,
        }

    def _record_player_combat_result(self, result):
        if not isinstance(result, dict) or not result.get('ok'):
            return
        if result.get('escape') or result.get('pass_turn'):
            self.combat_summary['healing'] += int(result.get('heal', 0) or 0)
            self.combat_summary['vampirism_healing'] += int(result.get('vampirism_heal', 0) or 0)
            return
        if self.attack_kind in ('kit', 'flee'):
            self.combat_summary['healing'] += int(result.get('heal', 0) or 0)
            self.combat_summary['vampirism_healing'] += int(result.get('vampirism_heal', 0) or 0)
            return
        self.combat_summary['attacks'] += 1
        self.combat_summary['healing'] += int(result.get('heal', 0) or 0)
        self.combat_summary['vampirism_healing'] += int(result.get('vampirism_heal', 0) or 0)
        if result.get('miss'):
            self.combat_summary['misses'] += 1
            return
        damage = max(0, int(result.get('damage', 0) or 0))
        if damage <= 0:
            return
        self.combat_summary['dealt'] += damage
        self.combat_summary['max_hit'] = max(self.combat_summary.get('max_hit', 0), damage)
        attack_type = result.get('attack_type')
        if attack_type in self.combat_summary['dealt_elemental']:
            self.combat_summary['dealt_elemental'][attack_type] += damage
        else:
            self.combat_summary['dealt_untyped'] += damage
        if result.get('critical'):
            self.combat_summary['critical_hits'] += 1
            self.combat_summary['dealt_critical'] += damage
        if result.get('type_relation') == 'advantage':
            self.combat_summary['advantage_hits'] += 1
            self.combat_summary['advantage_damage'] += damage

    def _record_enemy_combat_result(self, result):
        if not isinstance(result, dict):
            return
        is_attack = ('attack_base' in result) or result.get('special') or result.get('miss') or result.get('stasis_triggered')
        dot = max(0, int(result.get('damage_over_time', 0) or 0))
        if dot:
            # Queimadura que estava aplicada ao inimigo acontece no início do turno
            # inimigo: é dano CONTÍNUO causado pelo jogador, não dano sofrido.
            self.combat_summary['dealt'] += dot
            self.combat_summary['dealt_dot'] += dot
            self.combat_summary['dealt_dot_elemental']['Fogo'] += dot
            self.combat_summary['max_hit'] = max(self.combat_summary.get('max_hit', 0), dot)
        if not is_attack:
            return
        self.combat_summary['enemy_attacks'] += 1
        self.combat_summary['shield_absorbed'] += int(result.get('shield_absorbed', 0) or 0)
        self.combat_summary['technique_damage_reduced'] += int(result.get('technique_damage_reduced', 0) or 0)
        hit = max(0, int(result.get('damage', 0) or 0) - dot)
        if result.get('miss'):
            self.combat_summary['enemy_misses'] += 1
        if hit:
            self.combat_summary['taken'] += hit
            attack_type = result.get('attack_type')
            if attack_type in self.combat_summary['taken_elemental']:
                self.combat_summary['taken_elemental'][attack_type] += hit
            else:
                self.combat_summary['taken_untyped'] += hit
            if result.get('critical'):
                self.combat_summary['taken_critical_hits'] += 1
                self.combat_summary['taken_critical'] += hit

    def engage(self, index):
        if self.state.start_battle(index):
            self.battle_species = self.state.battle['species']
            self.mode, self.phase, self.phase_time = 'battle', 'choose', 0.0
            self.card_fx = None
            self.enemy_fx = None
            self.selected_battle_target = self.state.battle.get('target', 'body')
            self.combat_summary = self._new_combat_summary()
            # Snapshots para o resumo pós-combate: permitem mostrar apenas o
            # progresso efetivamente obtido nesta luta, sem alterar a lógica de XP.
            self.combat_summary['nexus_xp_before'] = int(getattr(self.state, 'gauntlet_nexus_xp', 0) or 0)
            battle_spec = BOSSES.get(self.battle_species) if self.battle_species in BOSSES else SPECIES.get(self.battle_species, {})
            domain_element = battle_spec.get('type') if isinstance(battle_spec, dict) else None
            self.combat_summary['domain_element'] = domain_element if domain_element in DOMAIN_ELEMENTS else None
            self.combat_summary['domain_xp_before'] = int(getattr(self.state, 'domain_xp', {}).get(domain_element, 0) or 0) if domain_element in DOMAIN_ELEMENTS else 0
            self.last_combat_summary = None
            self.set_message('Sua vez. Selecione o alvo e escolha uma técnica.')
            self.visual_pos = list(map(float, self.state.pos))

    def _combat_player_action_name(self, kind):
        if kind == 'basic':
            return 'Raio de Plasma'
        if kind == 'kit':
            return 'Kit de Reparo'
        if kind == 'flee':
            return 'Fuga'
        try:
            return self.state.card_name(kind)
        except Exception:
            return str(kind)

    def _combat_enemy_action_name(self, result):
        species = self.battle_species
        spec = BOSSES[species] if species in BOSSES else SPECIES.get(species, {})
        special_card = result.get('special_card')
        if special_card:
            try:
                return self.state.card_name(special_card)
            except Exception:
                return CARDS.get(special_card, {}).get('name', 'Técnica especial')
        if result.get('attack_base') is not None:
            return 'Ataque básico'
        return 'Ataque'

    def _player_combat_result_message(self, result):
        enemy_name = (BOSSES.get(self.battle_species, SPECIES.get(self.battle_species, {}))).get('name', self.battle_species)
        if result.get('water_deposit'):
            return 'Você atingiu o depósito de Água Pura.'
        if result.get('miss'):
            return 'Você errou o alvo.'
        if result.get('heal') and not result.get('damage'):
            return f'Você recuperou {int(result.get("heal", 0))} de Vida.'
        damage = int(result.get('damage', 0) or 0)
        if damage <= 0:
            return 'O ataque não causou dano.'
        tags=[]
        if result.get('critical'):
            tags.append('CRÍTICO')
        relation=result.get('type_relation')
        if relation == 'advantage':
            tags.append('VANTAGEM')
        elif relation == 'disadvantage':
            tags.append('DESVANTAGEM')
        suffix = f' ({" • ".join(tags)})' if tags else ''
        parts=[f'{enemy_name} sofreu {damage} de dano{suffix}.']
        if result.get('heal'):
            parts.append(f'Você recuperou {int(result.get("heal",0))} de Vida.')
        if result.get('status_notes'):
            parts.extend(str(v).strip().rstrip('.') + '.' for v in result.get('status_notes', []))
        return ' '.join(parts)

    def _enemy_combat_result_message(self, result):
        enemy_name=(BOSSES.get(self.battle_species, SPECIES.get(self.battle_species, {}))).get('name', self.battle_species)
        if result.get('stasis_triggered'):
            return f'{enemy_name} preparou um ataque fatal.'
        if result.get('miss'):
            return f'{enemy_name} errou o ataque.'
        damage=int(result.get('damage',0) or 0)
        parts=[]
        dot=int(result.get('damage_over_time',0) or 0)
        direct=max(0,damage-dot)
        if direct:
            parts.append(f'Você sofreu {direct} de dano')
        elif damage:
            parts.append(f'Você sofreu {damage} de dano')
        else:
            parts.append('Você não sofreu dano')
        if result.get('critical'):
            parts.append('CRÍTICO')
        if dot:
            parts.append(f'Queimadura causou {dot} de dano contínuo')
        if result.get('status_notes'):
            parts.extend(str(v).strip().rstrip('.') for v in result.get('status_notes', []))
        return '. '.join(parts) + ('.' if parts else '')

    def choose(self, kind):
        if self.phase != 'choose':
            return
        target = self.selected_battle_target if self.state.battle else None
        result = self.state.action(kind, target)
        if not result['ok']:
            self.set_message(result['message'])
            return
        self.result = result
        self.attack_kind = kind
        self._record_player_combat_result(result)
        if not result.get('escape'):
            self.combat_summary['turns'] = int(self.combat_summary.get('turns', 0)) + 1
        if kind == 'basic':
            self.card_fx = {'card': 'basic'}
        elif kind not in ('kit', 'flee'):
            try:
                base_id = self.state.card_parts(kind)[0]
            except ValueError:
                base_id = str(kind)
            self.card_fx = {'card': base_id}
        else:
            self.card_fx = None
        if result.get('escape'):
            self.set_message(result.get('message', 'Fuga concluída.'))
            self.combat_narration = None
            self.reset_mode('world')
            return
        self.state.end_player_turn()
        action_name=self._combat_player_action_name(kind)
        self.combat_narration={'side':'player','announce':True,'result_shown':False,'result':result,'action_name':action_name}
        self.set_message(f'Você usou {action_name}.')
        self.phase, self.phase_time = 'hero', 0.0

    def _advance_achievement_alert(self, dt):
        if self.achievement_alert_until > self.frame:
            return
        alert = self.state.pop_achievement_alert()
        if not alert:
            return
        if alert.get('type') == 'card':
            card = CARDS.get(alert.get('cid'), {})
            self.card_alert_cid = alert.get('cid')
            self.achievement_alert_text = 'NOVA CARTA DESBLOQUEADA PARA CRIAÇÃO!'
            self.achievement_alert_kind = 'card'
        elif alert.get('type') == 'renown_claimed':
            self.achievement_alert_text = 'RENOME — RECOMPENSA RESGATADA'
            self.achievement_alert_kind = 'renown_claimed'
        elif alert.get('type') == 'flight_unlocked':
            self.achievement_alert_text = 'VOO INTERPLANETÁRIO AUTORIZADO'
            self.achievement_alert_kind = 'flight_unlocked'
        elif alert.get('type') == 'helmet_advanced':
            self.achievement_alert_text = 'PESQUISA AVANÇADA DO ELMO DISPONÍVEL'
            self.achievement_alert_kind = 'helmet_advanced'
        elif alert.get('type') == 'civ_mission_started':
            self.achievement_alert_text = 'PEDIDO ADQUIRIDO'
            self.achievement_alert_kind = 'civ_mission_started'
        elif alert.get('type') == 'civ_mission_updated':
            self.achievement_alert_text = 'PEDIDO ATUALIZADO'
            self.achievement_alert_kind = 'civ_mission_updated'
        elif alert.get('type') == 'civ_mission_completed':
            self.achievement_alert_text = 'PEDIDO CONCLUÍDO'
            self.achievement_alert_kind = 'civ_mission_completed'
        elif alert.get('type') == 'mission_started':
            mid = alert.get('mid')
            title = SHIP_MISSION_DATA.get(mid, {}).get('title')
            title = {
                'water_supply': 'Água para Qaresh',
                'faction_conflict': 'A Dívida da Fenda',
                'kuvaar_hunt': 'A Sede de Qaresh',
                'ry_investigation': 'Investigue Vazio de RY',
                'dobra_core_install': 'Potencializar a nave',
                'explore_galaxy': 'Explore o Universo',
                'alphor_path': 'Abrir a Caldeira de Alphor',
                'broom_path': 'Subir à Coroa de Broom',
                'respawn_tank': 'Tanque de Renascimento',
            }.get(mid, title)
            self.achievement_alert_text = f'MISSÃO ADQUIRIDA — {title or "Missão"}'
            self.achievement_alert_kind = 'mission_started'
        elif alert.get('type') == 'mission_updated':
            mid = alert.get('mid')
            title = SHIP_MISSION_DATA.get(mid, {}).get('title') or OBJECTIVES.get(mid, {}).get('title')
            if mid == 'water_mission': title = 'Água para Qaresh'
            elif mid == 'faction_conflict': title = 'A Dívida da Fenda'
            elif mid == 'kuvaar': title = 'A Sede de Qaresh'
            elif mid == 'explore_space': title = 'Explore o Universo'
            elif mid == 'ry_investigation': title = 'Investigue Vazio de RY'
            elif mid == 'dobra_core_install': title = 'Potencializar a nave'
            elif mid == 'alphor_path': title = 'Abrir a Caldeira de Alphor'
            elif mid == 'broom_path': title = 'Subir à Coroa de Broom'
            elif mid == 'respawn_tank': title = 'Tanque de Renascimento'
            elif mid == 'ship_laser_project': title = 'Projeto: Emissor Laser'
            elif mid == 'travel_repair': title = 'Reparar a nave'
            self.achievement_alert_text = f'MISSÃO ATUALIZADA — {title or "Missão"}'
            self.achievement_alert_kind = 'mission_updated'
        elif alert.get('type') == 'mission':
            title = SHIP_MISSION_DATA.get(alert.get('mid'), {}).get('title')
            if alert.get('mid') == 'water_supply': title = 'Água para Qaresh'
            elif alert.get('mid') == 'faction_conflict': title = 'A Dívida da Fenda'
            elif alert.get('mid') == 'kuvaar_hunt': title = 'A Sede de Qaresh'
            elif alert.get('mid') == 'ship_laser_project': title = 'Projeto: Emissor Laser'
            elif alert.get('mid') == 'travel_repair': title = 'Reparar a nave'
            self.achievement_alert_text = f'MISSÃO CONCLUÍDA — {title or "Missão"}'
            self.achievement_alert_kind = 'mission'
        else:
            data = ACHIEVEMENTS.get(alert.get('aid'), {})
            name = data.get('name', 'Conquista')
            if alert.get('type') == 'claimed':
                self.achievement_alert_text = f'CONQUISTA RECEBIDA — {name}'
                self.achievement_alert_kind = 'claimed'
            else:
                self.achievement_alert_text = f'CONQUISTA DESBLOQUEADA — {name}'
                self.achievement_alert_kind = 'unlocked'
        self.achievement_alert_until = self.frame + 3.6

    def advance(self, dt):
        self.frame += dt
        if self.mode in ('opening','game_over'):
            self._advance_achievement_alert(dt)
            return
        if self.mode == 'language_qte':
            self._advance_achievement_alert(dt)
            if self.language_qte and self.frame >= self.language_qte.get('until', self.frame):
                self.state.pending_language_civilization = None
                self.state.pending_language_npc_id = None
                self.language_qte = None
                self.set_message('CALIBRAÇÃO FALHOU — o Elmo não reuniu padrões linguísticos suficientes.')
                self.reset_mode('world')
            return
        if self.mode == 'stasis':
            self._advance_achievement_alert(dt)
            if self.stasis_qte and self.frame >= self.stasis_qte.get('until', self.frame):
                result = self.state.resolve_stasis(False)
                self.set_message(result.get('message',''))
                self.stasis_qte = None
                self.reset_mode('game_over' if self.state.game_over else 'ship')
                if not self.state.game_over:
                    self.checkpoint()
            return
        if self.mode == 'travel':
            self._advance_achievement_alert(dt)
            self.travel_time += dt
            if self.travel_encounter_pending and self.travel_time >= self.travel_encounter_trigger:
                self.start_asteroid_encounter()
                return
            if self.travel_time >= self.travel_duration:
                self.finish_planet_travel()
            return
        if self.mode == 'asteroids':
            self._advance_achievement_alert(dt)
            self.advance_asteroid_encounter(dt)
            return
        if self.mode not in ('world', 'battle', 'ship'):
            self._advance_achievement_alert(dt)
            return
        self._advance_achievement_alert(dt)
        self.state.tick(dt)
        if self.mode == 'battle':
            self.phase_time += dt
            if self.phase == 'hero':
                if self.phase_time >= .66 and self.combat_narration and not self.combat_narration.get('result_shown'):
                    self.combat_narration['result_shown']=True
                    self.set_message(self._player_combat_result_message(self.result))
                if self.phase_time >= 1.08:
                    if self.result.get('win'):
                        was_virtual = bool(self.state.battle and self.state.battle.get('virtual'))
                        self.loot = self.state.win()
                        self.last_combat_summary = dict(self.combat_summary)
                        self.last_combat_summary['dealt_elemental'] = dict(self.combat_summary.get('dealt_elemental',{}))
                        self.last_combat_summary['taken_elemental'] = dict(self.combat_summary.get('taken_elemental',{}))
                        # XP do NEXUS e do Domínio após a recompensa da vitória.
                        nexus_before = int(self.combat_summary.get('nexus_xp_before', getattr(self.state, 'gauntlet_nexus_xp', 0)) or 0)
                        nexus_after = int(getattr(self.state, 'gauntlet_nexus_xp', 0) or 0)
                        self.last_combat_summary['nexus_xp_gained'] = max(0, nexus_after - nexus_before)
                        self.last_combat_summary['nexus_xp_total'] = nexus_after
                        nexus_level = int(getattr(self.state, 'gauntlet_nexus_level', 0) or 0)
                        from content import NEXUS_LEVEL_XP
                        if nexus_level >= max(NEXUS_LEVEL_XP):
                            self.last_combat_summary['nexus_xp_to_next'] = 0
                        else:
                            self.last_combat_summary['nexus_xp_to_next'] = max(0, int(NEXUS_LEVEL_XP.get(nexus_level + 1, nexus_after)) - nexus_after)

                        domain_element = self.combat_summary.get('domain_element')
                        domain_after = int(getattr(self.state, 'domain_xp', {}).get(domain_element, 0) or 0) if domain_element in DOMAIN_ELEMENTS else 0
                        domain_before = int(self.combat_summary.get('domain_xp_before', domain_after) or 0)
                        domain_level = int(getattr(self.state, 'domain_levels', {}).get(domain_element, 0) or 0) if domain_element in DOMAIN_ELEMENTS else 0
                        self.last_combat_summary['domain_element'] = domain_element
                        self.last_combat_summary['domain_xp_gained'] = max(0, domain_after - domain_before)
                        self.last_combat_summary['domain_xp_total'] = domain_after
                        if domain_level >= DOMAIN_LEVEL_MAX:
                            self.last_combat_summary['domain_xp_to_next'] = 0
                        else:
                            self.last_combat_summary['domain_xp_to_next'] = max(0, int(DOMAIN_LEVEL_XP.get(domain_level + 1, domain_after)) - domain_after)
                        self.mode = 'victory'
                        self.ui_scroll['combat_result'] = 0
                        self.nav_stack = ['world']
                        self._sync_navigation_context()
                        if was_virtual:
                            self.set_message('Confronto concluído. A simulação virtual registrou novamente o resultado.')
                        elif self.battle_species in self.state.bosses:
                            self.victory_boss = self.battle_species
                            self.set_message('Boss derrotado. O registro foi integrado ao bestiário. Um projeto de simulador agora pode ser fabricado na nave.')
                        else:
                            self.set_message('Combate concluído. Os dados do confronto foram registrados.')
                        self.combat_narration = None
                        self.save()
                        return
                    self.card_fx = None
                    self.phase, self.phase_time = 'enemy', 0.0
                    self.result = self.state.enemy_turn()
                    self._record_enemy_combat_result(self.result)
                    self.enemy_fx = {'species': self.battle_species, 'special': bool(self.result.get('special')), 'card': self.result.get('special_card')}
                    enemy_name=(BOSSES.get(self.battle_species, SPECIES.get(self.battle_species, {}))).get('name',self.battle_species)
                    enemy_attack=self._combat_enemy_action_name(self.result)
                    self.combat_narration={'side':'enemy','announce':True,'result_shown':False,'result':self.result,'action_name':enemy_attack}
                    self.set_message(f'{enemy_name} utilizou {enemy_attack}.')
                    if self.result.get('stasis_triggered'):
                        seconds=float(self.result.get('stasis_seconds',10.0))
                        self.stasis_qte={'until':self.frame+seconds,'seconds':seconds,'key':self.result.get('stasis_key','F'),'name':self.battle_species,'speed':2.25}
                        self.mode='stasis'
                        return
                    if self.result.get('defeat_enemy'):
                        self.result['win'] = True
                        self.phase = 'hero'
                        self.phase_time = 0.0
            elif self.phase == 'enemy':
                if self.phase_time >= .66 and self.combat_narration and not self.combat_narration.get('result_shown'):
                    self.combat_narration['result_shown']=True
                    self.set_message(self._enemy_combat_result_message(self.result))
                if self.phase_time >= 1.08:
                    if self.result.get('defeat'):
                        self.reset_mode('game_over' if self.state.game_over else 'ship')
                        self.combat_narration = None
                        if not self.state.game_over:
                            self.checkpoint()
                    else:
                        self.enemy_fx = None
                        status = self.state.prepare_player_turn()
                        if status.get('damage'):
                            burn = int(status.get('damage', 0) or 0)
                            self.combat_summary['taken'] += burn
                            self.combat_summary['taken_dot'] += burn
                            self.combat_summary['taken_dot_elemental']['Fogo'] += burn
                        if status.get('defeat'):
                            self.set_message(status.get('message',''))
                            self.reset_mode('game_over' if self.state.game_over else 'ship')
                            if not self.state.game_over:
                                self.checkpoint()
                        elif status.get('stunned'):
                            self.state.end_player_turn()
                            self.result = {'win': False, 'stunned': True}
                            self.set_message(status.get('message','Você está atordoado e perde este turno.'))
                            self.phase, self.phase_time = 'hero', 0.0
                        else:
                            if status.get('message'):
                                self.set_message(status['message'])
                            self.phase, self.phase_time = 'choose', 0.0
            return
        if self.mode == 'ship':
            self.move_wait -= dt
            keys = pygame.key.get_pressed()
            if self.move_wait <= 0:
                directions = [(pygame.K_w, pygame.K_UP, 0, -1), (pygame.K_s, pygame.K_DOWN, 0, 1),
                              (pygame.K_a, pygame.K_LEFT, -1, 0), (pygame.K_d, pygame.K_RIGHT, 1, 0)]
                for a, b, dx, dy in directions:
                    if keys[a] or keys[b]:
                        self.set_facing(dx, dy); self.state.move_ship(dx, dy); self.move_wait = .12; break
            return
        self.move_wait -= dt
        keys = pygame.key.get_pressed()
        if self.move_wait <= 0:
            directions = [(pygame.K_w, pygame.K_UP, 0, -1), (pygame.K_s, pygame.K_DOWN, 0, 1),
                          (pygame.K_a, pygame.K_LEFT, -1, 0), (pygame.K_d, pygame.K_RIGHT, 1, 0)]
            for a, b, dx, dy in directions:
                if keys[a] or keys[b]:
                    self.set_facing(dx, dy); self.move(dx, dy); break
        for i in range(2):
            self.visual_pos[i] += (self.state.pos[i]-self.visual_pos[i])*min(1, dt*16)
        self.patrol_wait -= dt
        if self.patrol_wait <= 0:
            self.patrol_wait = 1.8
            for e in self.state.enemies:
                if e['dead']:
                    continue
                dx, dy = self.state.rng.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
                p = [e['pos'][0]+dx, e['pos'][1]+dy]
                if (all(0 <= v < self.state.area['size'] for v in p) and distance(p, e['home']) <= 1
                    and not protected_tile(self.state.sector, p) and tuple(p) not in self.rocks
                    and not self.state.npc_at(p)
                    and not any(other is not e and not other['dead'] and other['pos'] == p for other in self.state.enemies)):
                    e['pos'] = p
        if self.state.grace <= 0 and not protected_tile(self.state.sector, self.state.pos):
            for i, e in enumerate(self.state.enemies):
                if not e['dead'] and distance(e['pos'], self.state.pos) <= 1:
                    self.engage(i); break

    def settlement_structure(self, kind, x, y):
        # Arquitetura Avarin: formas baixas para sobreviver ao vento, tecidos e um reservatório central.
        if kind == 'reservoir':
            pygame.draw.rect(self.canvas, (72, 73, 70), (x-18, y-43, 36, 43))
            pygame.draw.ellipse(self.canvas, (154, 148, 127), (x-20, y-52, 40, 18))
            pygame.draw.ellipse(self.canvas, (74, 132, 137), (x-13, y-48, 26, 9))
            pygame.draw.line(self.canvas, (190, 175, 141), (x-14, y-33), (x+14, y-33), 2)
        elif kind == 'dwelling':
            pygame.draw.ellipse(self.canvas, (122, 106, 86), (x-27, y-35, 54, 35))
            pygame.draw.arc(self.canvas, (191, 164, 124), (x-24, y-32, 48, 25), math.pi, math.tau, 2)
            pygame.draw.rect(self.canvas, (67, 57, 52), (x-7, y-16, 14, 16))
        elif kind == 'shade':
            pygame.draw.line(self.canvas, (73, 67, 61), (x-22, y-7), (x-17, y-41), 4)
            pygame.draw.line(self.canvas, (73, 67, 61), (x+22, y-7), (x+17, y-41), 4)
            pygame.draw.polygon(self.canvas, (143, 119, 91), [(x-24,y-39),(x+18,y-45),(x+27,y-31),(x-17,y-25)])
            pygame.draw.polygon(self.canvas, (183, 151, 105), [(x-12,y-38),(x+3,y-41),(x+10,y-31),(x-5,y-29)])
        elif kind == 'watch':
            pygame.draw.rect(self.canvas, (81, 82, 82), (x-8, y-55, 16, 55))
            pygame.draw.polygon(self.canvas, (181, 158, 118), [(x,y-66),(x+11,y-53),(x-11,y-53)])
            pygame.draw.rect(self.canvas, (50, 65, 69), (x-5,y-44,10,6))
            pygame.draw.line(self.canvas, GOLD, (x-4,y-38), (x+4,y-38), 2)
        elif kind == 'shadow_node':
            pygame.draw.ellipse(self.canvas, (9,11,16), (x-21, y-8, 42, 12))
            pygame.draw.polygon(self.canvas, (19,22,31), [(x-12,y-16),(x,y-48),(x+14,y-16),(x+10,y-3),(x-10,y-3)])
            pygame.draw.line(self.canvas, (83,103,126), (x-2,y-27),(x+9,y-38), 2)
            pygame.draw.circle(self.canvas, (122,167,204), (x+3,y-24), 3, 1)
        elif kind == 'shadow_obelisk':
            pygame.draw.polygon(self.canvas, (11,13,18), [(x-13,y),(x-8,y-60),(x+5,y-68),(x+14,y-8),(x+8,y)])
            pygame.draw.polygon(self.canvas, (28,31,42), [(x-5,y-7),(x,y-56),(x+7,y-61),(x+9,y-9)])
            pygame.draw.line(self.canvas, (95,112,136), (x-2,y-31),(x+5,y-35), 1)
        elif kind == 'city_gate':
            # Portal urbano compacto: entrada de distrito, claramente diferente
            # das moradias de Qaresh e dos abrigos de Nahr.
            pygame.draw.rect(self.canvas, (42,52,66), (x-28, y-58, 56, 58), border_radius=4)
            pygame.draw.rect(self.canvas, (85,103,122), (x-22, y-52, 44, 52), 2, border_radius=3)
            pygame.draw.rect(self.canvas, (14,28,38), (x-11, y-38, 22, 38))
            pygame.draw.line(self.canvas, TEAL, (x-18,y-45),(x+18,y-45),2)
            pygame.draw.circle(self.canvas, GOLD, (x,y-47), 3)
        elif kind == 'city_block':
            pygame.draw.rect(self.canvas, (53,61,76), (x-31, y-52, 62, 52), border_radius=3)
            pygame.draw.rect(self.canvas, (91,103,119), (x-27, y-48, 54, 44), 1, border_radius=3)
            for wx in (-17, 0, 17):
                pygame.draw.rect(self.canvas, (40,91,103), (x+wx-4, y-35, 8, 7), border_radius=1)
                pygame.draw.line(self.canvas, GOLD, (x+wx-3,y-33),(x+wx+3,y-33),1)
            pygame.draw.rect(self.canvas, (26,31,40), (x-7,y-13,14,13))
        elif kind == 'tower':
            pygame.draw.rect(self.canvas, (50,58,73), (x-17, y-115, 34, 115))
            pygame.draw.polygon(self.canvas, (84,99,120), [(x-20,y-115),(x,y-132),(x+20,y-115)])
            for yy in range(y-101, y-18, 17):
                pygame.draw.line(self.canvas, TEAL, (x-12,yy),(x+12,yy),2)
            pygame.draw.rect(self.canvas, (18,26,34), (x-5,y-24,10,24))

    def draw_faction_site(self, site):
        # Acampamento provisório dos Filhos da Fenda: arquitetura mais áspera que
        # Qaresh, com tecidos rasgados, estruturas de observação e marca própria.
        for structure in site.get('structures', []):
            x, y = self.project(*structure['pos'])
            if -90 <= x <= 940 and 55 <= y <= 645:
                kind = structure.get('type')
                if kind == 'shade':
                    pygame.draw.line(self.canvas, (61, 54, 50), (x-22, y-8), (x-17, y-38), 4)
                    pygame.draw.line(self.canvas, (61, 54, 50), (x+20, y-7), (x+15, y-37), 4)
                    pygame.draw.polygon(self.canvas, (105, 65, 56), [(x-25,y-37),(x+17,y-42),(x+24,y-29),(x-17,y-25)])
                    pygame.draw.polygon(self.canvas, (153, 90, 61), [(x-9,y-34),(x+3,y-37),(x+10,y-29),(x-3,y-27)])
                elif kind == 'dwelling':
                    pygame.draw.ellipse(self.canvas, (88, 69, 60), (x-27,y-34,54,34))
                    pygame.draw.arc(self.canvas, (154, 91, 68), (x-24,y-31,48,24), math.pi, math.tau, 2)
                    pygame.draw.rect(self.canvas, (48, 41, 41), (x-7,y-15,14,15))
                elif kind == 'watch':
                    pygame.draw.rect(self.canvas, (67, 67, 69), (x-7,y-52,14,52))
                    pygame.draw.polygon(self.canvas, (153, 88, 67), [(x,y-63),(x+10,y-51),(x-10,y-51)])
                    pygame.draw.rect(self.canvas, (32, 47, 51), (x-4,y-40,8,6))
        for npc in site.get('npcs', []):
            x, y = self.project(*npc['pos'])
            if -80 <= x <= 940 and 70 <= y <= 645:
                frame_seed = sum(ord(ch) for ch in npc['id']) % 2
                self.actor(npc['kind'], x, y, 1.12, int(self.frame*4 + frame_seed))
                near = distance(self.state.pos, npc['pos']) <= 3
                if near:
                    self.label(npc['role'].upper(), x-65, y-70, 11, GOLD if npc['id'] not in self.state.society['seen_npcs'] else (201, 133, 96))
        cx, cy = self.project(*site['center'])
        pygame.draw.circle(self.canvas, (196, 93, 70), (cx, cy-62), 5, 1)
        pygame.draw.line(self.canvas, (196, 93, 70), (cx,cy-60), (cx,cy-47), 1)
        self.label('FILHOS DA FENDA', cx-69, cy-82, 11, (214, 119, 86))

    def draw_settlement(self, settlement):
        eliminated = self.state.missions.get('faction_conflict', {}).get('loser') if self.state.missions.get('faction_conflict', {}).get('status') == 'completed' else None
        for structure in settlement['structures']:
            x, y = self.project(*structure['pos'])
            if -90 <= x <= 940 and 55 <= y <= 645:
                self.settlement_structure(structure['type'], x, y)
        for npc in settlement['npcs']:
            if npc.get('faction') == eliminated:
                continue
            x, y = self.project(*npc['pos'])
            if -80 <= x <= 940 and 70 <= y <= 645:
                frame_seed = sum(ord(ch) for ch in npc['id']) % 2
                self.actor(npc['kind'], x, y, 1.12, int(self.frame*4 + frame_seed))
                near = distance(self.state.pos, npc['pos']) <= 3
                if near:
                    label_text = ('SOMBRAS DE NAHR' if npc.get('faction') == 'nahr_shadows' and npc['id'] not in self.state.society['seen_npcs'] else npc['role'].upper())
                    self.label(label_text, x-72, y-70, 11, GOLD if npc['id'] not in self.state.society['seen_npcs'] else TEAL)
        cx, cy = self.project(*settlement['center'])
        pygame.draw.circle(self.canvas, GOLD, (cx, cy-63), 5, 1)
        pygame.draw.line(self.canvas, GOLD, (cx,cy-61), (cx,cy-48), 1)

    def world_backdrop(self):
        planet_id = self.state.current_planet_id()
        configs = {
            'veyra': dict(sky=(18,23,34), horizon=(112,67,56), ground=(80,61,55), sun=(239,185,110), secondary=(211,109,86)),
            'orionis': dict(sky=(20,14,17), horizon=(126,57,42), ground=(70,43,38), sun=(255,139,73), secondary=(184,65,52)),
            'kael': dict(sky=(12,22,34), horizon=(71,103,125), ground=(54,73,83), sun=(197,225,245), secondary=(108,157,189)),
            'nahr': dict(sky=(17,16,20), horizon=(97,57,44), ground=(54,43,42), sun=(232,118,75), secondary=(135,67,54)),
            'elyra': dict(sky=(11,25,27), horizon=(56,109,99), ground=(42,72,67), sun=(167,224,201), secondary=(100,153,157)),
            'dornak': dict(sky=(16,20,25), horizon=(90,83,74), ground=(66,68,69), sun=(218,173,112), secondary=(125,135,141)),
            'nyxara': dict(sky=(9,12,22), horizon=(59,48,76), ground=(38,39,49), sun=(168,137,207), secondary=(84,113,158)),
            'zereth': dict(sky=(11,25,36), horizon=(65,101,123), ground=(49,66,76), sun=(152,221,241), secondary=(89,167,201)),
            'pyraxis': dict(sky=(31,14,12), horizon=(132,61,39), ground=(77,43,36), sun=(252,144,61), secondary=(184,73,48)),
            'thalassene': dict(sky=(10,29,38), horizon=(56,115,129), ground=(42,82,88), sun=(183,226,221), secondary=(102,179,191)),
            'mycelon': dict(sky=(15,28,22), horizon=(71,113,75), ground=(43,73,52), sun=(208,219,151), secondary=(136,177,107)),
            'tethra': dict(sky=(18,24,32), horizon=(96,105,112), ground=(61,67,73), sun=(222,219,193), secondary=(137,152,169)),
            'nerissa': dict(sky=(12,18,29), horizon=(72,88,112), ground=(47,54,66), sun=(228,196,144), secondary=(112,156,191)),
        }
        cfg = configs.get(planet_id, configs['veyra'])
        for yy in range(H):
            t=yy/max(1,H-1)
            if t<0.58:
                u=t/0.58; a=cfg['sky']; z=cfg['horizon']; c=tuple(int(a[i]+(z[i]-a[i])*u) for i in range(3))
            else:
                u=(t-0.58)/0.42; a=cfg['horizon']; z=cfg['ground']; c=tuple(int(a[i]+(z[i]-a[i])*u) for i in range(3))
            pygame.draw.line(self.canvas,c,(0,yy),(W,yy))
        pygame.draw.circle(self.canvas,cfg['sun'],(W-190,150),34)
        pygame.draw.circle(self.canvas,tuple(min(255,c+25) for c in cfg['sun']),(W-190,150),24)
        pygame.draw.circle(self.canvas,cfg['secondary'],(W-120,125),14)
        pygame.draw.polygon(self.canvas,tuple(max(0,c-15) for c in cfg['ground']),[(0,308),(130,275),(280,315),(420,270),(600,310),(760,272),(930,316),(1200,274),(1200,410),(0,410)])
        pygame.draw.polygon(self.canvas,tuple(min(255,c+12) for c in cfg['ground']),[(0,350),(180,316),(330,360),(520,320),(720,360),(940,315),(1200,350),(1200,455),(0,455)])
        # Detalhes atmosféricos simples, diferentes por planeta.
        if planet_id == 'orionis':
            for i in range(18):
                x=(i*97+33)%W; y=165+((i*31)%160); pygame.draw.line(self.canvas,(207,103,61),(x,y),(x+13,y-3),1)
        elif planet_id == 'kael':
            for i in range(22):
                x=(i*67+19)%W; y=135+((i*53)%180); pygame.draw.circle(self.canvas,(199,224,239),(x,y),1 if i%4 else 2)
        elif planet_id == 'nahr':
            for i in range(16):
                x=(i*91+47)%W; y=175+((i*41)%145); pygame.draw.circle(self.canvas,(189,76,53),(x,y),1 if i%3 else 2)
        elif planet_id == 'elyra':
            for i in range(24):
                x=(i*53+31)%W; y=145+((i*29)%175); pygame.draw.circle(self.canvas,(126,205,177),(x,y),1 if i%3 else 2)
        elif planet_id == 'dornak':
            for i in range(16):
                x=(i*79+23)%W; y=155+((i*37)%170); pygame.draw.line(self.canvas,(141,150,157),(x,y),(x+10,y-4),1)
        elif planet_id == 'nyxara':
            for i in range(18):
                x=(i*67+17)%W; y=148+((i*43)%182); pygame.draw.circle(self.canvas,(107,89,144),(x,y),1 if i%3 else 2)
        elif planet_id == 'zereth':
            for i in range(22):
                x=(i*61+11)%W; y=145+((i*31)%190); pygame.draw.line(self.canvas,(104,192,220),(x,y),(x+4,y+12),1)
        elif planet_id == 'pyraxis':
            for i in range(20):
                x=(i*71+37)%W; y=170+((i*29)%145); pygame.draw.circle(self.canvas,(240,116,59),(x,y),1 if i%4 else 2)
        elif planet_id == 'thalassene':
            for i in range(20):
                x=(i*58+25)%W; y=160+((i*41)%150); pygame.draw.arc(self.canvas,(105,188,198),(x,y,22,8),0,math.pi,1)
        elif planet_id == 'mycelon':
            for i in range(22):
                x=(i*57+18)%W; y=145+((i*34)%180); pygame.draw.circle(self.canvas,(139,190,118),(x,y),1 if i%4 else 2)
        elif planet_id == 'tethra':
            for i in range(16):
                x=(i*83+29)%W; y=165+((i*37)%150); pygame.draw.line(self.canvas,(191,197,192),(x,y),(x+26,y-7),1)
        elif planet_id == 'nerissa':
            for i in range(14):
                x=(i*89+35)%W; y=145+((i*31)%170); pygame.draw.line(self.canvas,(126,173,191),(x,y),(x,y+12),1)
        else:
            for i in range(28):
                x=(i*83+41)%W; y=150+((i*47)%165); pygame.draw.circle(self.canvas,(192,154,123),(x,y),1 if i%4 else 2)

    def draw_monster_label(self, species_id, x, y):
        spec=SPECIES.get(species_id)
        if not spec: return
        text=spec['name'] if not self.state.scan_unlocked else f'{spec["name"]}  NV {creature_level(spec)}'
        tw=self.font(10).size(text)[0]
        rect=pygame.Rect(int(x-tw/2-7), int(y-84), tw+14, 20)
        pygame.draw.rect(self.canvas,(5,8,11),rect,border_radius=3)
        self.label(text,rect.x+7,rect.y+5,10,(245,245,240))

    def world(self):
        area = self.state.area
        self.world_backdrop()
        self.label('CINZAS DE ÓRION', 30, 25, 28)
        current_planet = next((r for r in STELLAR_ROUTES if r['id'] == self.state.current_planet_id()), STELLAR_ROUTES[0])
        self.label(f"{area['name'].upper()} / {area['size']} x {area['size']} / {current_planet['name'].upper()}", 32, 65, 14, GOLD)
        if self.state.sector == 'canyon' and self.state.missions.get('kuvaar_hunt', {}).get('status') in ('tracking','water','boss_ready'):
            self.label('RASTRO DE SAL / ROTA DA BACIA DE KUVAAR', 420, 65, 12, (224,112,93))
        self.button((1080, 24, 85, 36), 'MENU', self.open_menu)

        # O mapa ganhou a largura que antes era ocupada pela HUD lateral.
        self.canvas.set_clip(pygame.Rect(20, 98, 1160, 565))
        px, py = self.project(0, 0)
        self.canvas.blit(self.terrains[self.state.sector], (px-area['size']*27, py-20))
        planet_id = self.state.current_planet_id()
        if planet_id == 'pyraxis' and not area.get('boss_arena'):
            # Silhueta do vulcão: a caldeira deve ser reconhecível mesmo antes do boss.
            vx, vy = self.project(14, 7)
            pygame.draw.polygon(self.canvas, (59, 37, 34), [(vx-150,vy+70),(vx-92,vy-15),(vx-42,vy-88),(vx+4,vy-125),(vx+51,vy-74),(vx+113,vy-12),(vx+164,vy+70)])
            pygame.draw.polygon(self.canvas, (118, 50, 38), [(vx-33,vy-80),(vx+4,vy-114),(vx+38,vy-73),(vx+12,vy-61)])
            pygame.draw.line(self.canvas, (232,112,56), (vx+4,vy-82),(vx+4,vy+18),5)
            pygame.draw.line(self.canvas, (226,124,58), (vx+4,vy-53),(vx-38,vy+14),3)
        elif planet_id == 'nerissa' and area.get('settlement'):
            # Skyline simples e limpo para indicar que a cidade não é apenas um acampamento.
            sx, sy = self.project(12, 7)
            for i, h in enumerate((70, 108, 84, 132, 92)):
                bx = sx - 155 + i*58
                pygame.draw.rect(self.canvas, (43,50,64), (bx, sy-h, 42, h), border_radius=2)
                for wy in range(sy-h+12, sy-10, 18):
                    pygame.draw.rect(self.canvas, (74,131,145), (bx+8,wy,7,5))
                    pygame.draw.rect(self.canvas, (217,173,105), (bx+25,wy,6,4))
        for gate in area['exits']:
            if not self.state.route_visible(gate):
                continue
            x, y = self.project(*gate['at'])
            is_boss_gate = bool(gate.get('boss_gate')) or gate.get('target') == 'salt_basin'
            is_station_gate = gate.get('target') == 'waterworks'
            near_gate = distance(self.state.pos, gate['at']) <= 1
            if is_boss_gate:
                pulse = 2 + int(2*abs(math.sin(self.frame*2.2)))
                pygame.draw.circle(self.canvas, (224,112,93), (x,y-8), 19+pulse, 2)
                pygame.draw.circle(self.canvas, GOLD, (x,y-8), 11, 2)
                pygame.draw.line(self.canvas, (224,112,93), (x,y-10), (x,y-55), 3)
                boss_id = gate.get('boss_id','kuvaar')
                boss_name = BOSSES.get(boss_id, BOSSES['kuvaar'])['name']
                self.label('ZONA DE BOSS', x-58, y-82, 14, (224,112,93))
                self.label(boss_name.upper(), x-105, y-63, 10, (224,112,93))
                if gate.get('requires_locomotion') and not self.state.locomotion_generation:
                    self.label('MÓDULO DE LOCOMOÇÃO NECESSÁRIO', x-125, y-46, 9, GOLD)
                elif near_gate:
                    self.label('E  ACESSAR', x-45, y-46, 11, GOLD)
            elif is_station_gate:
                pygame.draw.circle(self.canvas, (95, 180, 175), (x,y-8), 19, 2)
                pygame.draw.polygon(self.canvas, (86,215,197), [(x-15,y-8),(x,y-20),(x+15,y-8),(x,y+4)], 2)
                pygame.draw.line(self.canvas, (86,215,197), (x,y-8), (x,y-48), 3)
                self.label('ENTRADA / ESTAÇÃO', x-76, y-74, 13, TEAL)
                if near_gate:
                    self.label('E  ENTRAR', x-37, y-53, 11, GOLD)
            else:
                pygame.draw.polygon(self.canvas, TEAL, [(x,y-12), (x+24,y), (x,y+12), (x-24,y)], 3)
                pygame.draw.line(self.canvas, TEAL, (x,y-10), (x,y-43), 3)
                self.label('SAÍDA / '+gate['key'], x-65, y-65, 14, TEAL)
                if near_gate:
                    self.label('E  ACESSAR', x-43, y-45, 11, GOLD)

        settlement = area.get('settlement')
        if settlement:
            self.draw_settlement(settlement)
        faction_site = area.get('faction_site')
        eliminated_faction = self.state.missions.get('faction_conflict', {}).get('loser') if self.state.missions.get('faction_conflict', {}).get('status') == 'completed' else None
        if faction_site and faction_site.get('faction') != eliminated_faction:
            self.draw_faction_site(faction_site)

        entities = [(sum(p), 'rock', p) for p in self.rocks]
        if area['ship'] is not None:
            entities.append((sum(area['ship']), 'ship', area['ship']))
        entities += [(sum(n['pos']), 'node', n) for n in area['nodes']]
        entities += [(sum(n['pos']), 'landmark', n) for n in area['landmarks']]
        for lm in area['landmarks']:
            boss_id = lm.get('boss_site')
            if boss_id and self.state.boss_available(boss_id):
                entities.append((sum(lm['pos']) - 0.05, 'boss_actor', (boss_id, lm['pos'])))
        entities += [(sum(e['pos']), e['species'], e['pos']) for e in self.state.enemies if not e['dead']]
        entities += [(sum(npc['pos']) + .05, npc['kind'], npc['pos'])
                     for npc in (settlement['npcs'] if settlement else [])]
        entities.append((sum(self.visual_pos)+.1, 'hero', self.visual_pos))

        for _, kind, data in sorted(entities, key=lambda item: item[0]):
            # Os NPCs já foram desenhados pelo assentamento e entram na lista apenas
            # para preservar sua camada física visual; não redesenhamos aqui.
            if kind in ('avarin', 'avarin_guard', 'nahr_shadow'):
                continue
            if kind == 'node':
                x, y = self.project(*data['pos'])
                collected = data['id'] in self.state.collected_nodes
                if data.get('category') == 'flora':
                    if not collected:
                        # Planta alienígena simples em pixel art: caule, folhas e
                        # inflorescência, claramente diferente de um depósito de sucata.
                        style = data.get('flora_style', 'alien')
                        styles = {
                            'fiery': ((154, 76, 55), (218, 121, 73), (238, 175, 93)),
                            'icy': ((89, 145, 163), (124, 194, 211), (210, 236, 244)),
                            'basalt': ((106, 87, 57), (155, 116, 62), (206, 159, 81)),
                            'luminous': ((65, 141, 112), (103, 201, 153), (186, 236, 181)),
                            'alien': ((64, 145, 116), (86, 190, 142), (206, 163, 102)),
                        }
                        stem, leaf, bloom = styles.get(style, styles['alien'])
                        pygame.draw.line(self.canvas, stem, (x, y+2), (x, y-15), 2)
                        pygame.draw.polygon(self.canvas, leaf, [(x, y-8), (x-10, y-13), (x-5, y-4)])
                        pygame.draw.polygon(self.canvas, leaf, [(x, y-11), (x+9, y-16), (x+5, y-7)])
                        pygame.draw.circle(self.canvas, bloom, (x, y-18), 4)
                        pygame.draw.circle(self.canvas, (238, 205, 137), (x, y-18), 2)
                    else:
                        pygame.draw.line(self.canvas, (69, 83, 72), (x-6, y), (x+6, y), 2)
                elif not collected:
                    color = GOLD if data['item'] == 'Fragmento histórico' else TEAL
                    pygame.draw.polygon(self.canvas, color, [(x-8,y), (x,y-11), (x+9,y), (x,y+5)])
                else:
                    pygame.draw.line(self.canvas, (77, 72, 64), (x-6, y), (x+6, y), 3)
                continue
            if kind == 'landmark':
                lm = data
                x, y = self.project(*lm['pos'])
                if lm.get('boss_route_marker'):
                    pulse = 2 + int(2*abs(math.sin(self.frame*2.0)))
                    pygame.draw.circle(self.canvas, (224,112,93), (x,y-10), 15+pulse, 2)
                    pygame.draw.polygon(self.canvas, (224,112,93), [(x+15,y-10),(x+4,y-18),(x+4,y-3)])
                    pygame.draw.line(self.canvas, GOLD, (x-18,y-10),(x+8,y-10),2)
                    if distance(self.state.pos, lm['pos']) <= 2:
                        boss_id = lm.get('boss_route_marker')
                        boss_name = BOSSES.get(boss_id, {}).get('name', 'BOSS').upper()
                        self.label(f'ALERTA → {boss_name}', x-72, y-56, 11, GOLD)
                elif lm.get('mission_site'):
                    pygame.draw.ellipse(self.canvas, (59,73,77), (x-19,y-18,38,24))
                    pygame.draw.rect(self.canvas, (88,101,102), (x-12,y-28,24,18), border_radius=3)
                    pygame.draw.rect(self.canvas, GOLD, (x-7,y-22,14,4))
                    pygame.draw.line(self.canvas, (111,126,125), (x+10,y-12),(x+22,y-28),2)
                elif lm.get('hack_site'):
                    pygame.draw.rect(self.canvas, (62,84,91), (x-12,y-36,24,36), border_radius=3)
                    pygame.draw.rect(self.canvas, (11,29,34), (x-8,y-29,16,10))
                    pygame.draw.line(self.canvas, TEAL, (x-5,y-24),(x+5,y-24),1)
                    pygame.draw.line(self.canvas, TEAL, (x-3,y-20),(x+7,y-20),1)
                elif lm.get('diversion'):
                    pygame.draw.circle(self.canvas, (72,91,92), (x,y-10), 16, 3)
                    pygame.draw.circle(self.canvas, GOLD, (x,y-10), 5, 2)
                    pygame.draw.line(self.canvas, (118,133,133), (x-18,y-10),(x+18,y-10),2)
                elif lm.get('ship_mission_site') == 'ship_comms':
                    pygame.draw.line(self.canvas, (110,126,132), (x,y-6),(x,y-58),4)
                    pygame.draw.line(self.canvas, (110,126,132), (x,y-48),(x-18,y-35),2)
                    pygame.draw.line(self.canvas, (110,126,132), (x,y-48),(x+18,y-35),2)
                    led=(224,112,93) if self.state.missions.get('ship_comms',{}).get('status')!='completed' else TEAL
                    pygame.draw.circle(self.canvas, led, (x,y-62), 5)
                else:
                    pygame.draw.rect(self.canvas, (73, 93, 105), (x-12, y-55, 24, 55))
                    for row in range(4):
                        pygame.draw.line(self.canvas, GOLD, (x-7, y-46+row*9), (x+4, y-42+row*9), 2)
                if distance(self.state.pos, lm['pos']) <= 1:
                    self.label('E  INTERAGIR', x-43, y-62, 10, TEAL)
                continue
            if kind == 'boss_actor':
                boss_id, boss_pos = data
                x, y = self.project(*boss_pos)
                if not -100 <= x <= 1160 or not 60 <= y <= 650:
                    continue
                pulse = 3 + int(2 * (0.5 + 0.5*math.sin(self.frame*2.2)))
                pygame.draw.circle(self.canvas, (214, 119, 87), (x, y-18), 48 + pulse, 2)
                pygame.draw.circle(self.canvas, GOLD, (x, y-18), 33, 1)
                scale = {'kuvaar':1.85,'fagor':1.55,'kael':1.38,'ounull':1.65,'ry':1.85}.get(boss_id,1.6)
                self.actor(boss_id, x, y, scale, int(self.frame*4), True)
                data_boss=BOSSES[boss_id]
                text=data_boss['name'] if not self.state.scan_unlocked else f'{data_boss["name"]}  NV {creature_level(data_boss)}'
                tw=self.font(10).size(text)[0]; r=pygame.Rect(int(x-tw/2-7),int(y-118),tw+14,20)
                pygame.draw.rect(self.canvas,(5,8,11),r,border_radius=3); self.label(text,r.x+7,r.y+5,10,(245,245,240))
                self.label('ZONA DE PERIGO',x-52,y-91,10,(224,112,93)); continue
            x, y = self.project(*data)
            if not -80 <= x <= 1160 or not 70 <= y <= 650:
                continue
            if kind == 'ship':
                self.ship(x, y)
            elif kind == 'rock':
                pygame.draw.polygon(self.canvas, (93, 85, 77), [(x-13,y), (x-8,y-21), (x+6,y-28), (x+16,y-3), (x+3,y+7)])
                pygame.draw.polygon(self.canvas, (133, 117, 95), [(x-8,y-21), (x+6,y-28), (x+5,y-9), (x-13,y)])
            else:
                moving = kind != 'hero' or any(abs(self.visual_pos[i]-self.state.pos[i]) > .03 for i in range(2))
                self.actor(kind, x, y, 1.08, int(self.frame*4.5) if moving else 0)
                if kind in SPECIES:
                    self.draw_monster_label(kind, x, y)
                if kind == 'hero':
                    pygame.draw.polygon(self.canvas, TEAL, [(x-4,y-72), (x+4,y-72), (x,y-66)])
        self.canvas.set_clip(None)

        # HUD de mundo deliberadamente discreta. Informações sobre fauna, respawn,
        # coletas e detalhes sociais deixaram de ficar expostas o tempo inteiro.
        self.label(f'VIDA  {self.state.hp}/{self.state.max_hp}', 32, 748, 12, MUTED)
        self.bar(32, 767, 500, self.state.hp, self.state.max_hp, (203, 112, 94))
        self.label(f'MEMÓRIA  {self.state.memory}/{self.state.max_memory}', 638, 748, 12, MUTED)
        self.bar(638, 767, 500, self.state.memory, max(1, self.state.max_memory), TEAL)

    def has_unclaimed_achievements(self):
        """Indica apenas conquistas já desbloqueadas cuja recompensa ainda não foi resgatada."""
        achievements = getattr(self.state, 'achievements', {})
        if not isinstance(achievements, dict):
            return False
        return any(
            isinstance(entry, dict)
            and bool(entry.get('unlocked'))
            and not bool(entry.get('claimed'))
            for entry in achievements.values()
        )

    def hack_inventory(self):
        self.state.inventory['Essência'] = int(self.state.inventory.get('Essência', 0)) + 20000
        materials = set()
        for card in CARDS.values():
            for item in card.get('recipe', {}) or {}:
                if item != 'Essência':
                    materials.add(item)
        for item in materials:
            self.state.inventory[item] = int(self.state.inventory.get(item, 0)) + 100
        self.set_message(f'HACK ATIVADO: +20.000 Essências e +100 de {len(materials)} materiais das cartas.')
        self.checkpoint()

    def menu(self):
        self.label('MENU', 35, 28, 28, TEAL)
        self.box((50, 86, 1100, 626), (7,15,22), EDGE)
        cols = [
            ('CAMPANHA', 80, [
                ('CONTINUAR', self.close_menu, True),
                ('DIÁRIO', lambda:self.open_panel('journal'), True),
                ('MAPA', lambda:self.open_panel('routes'), True),
                ('CARTAS', lambda:self.open_panel('album'), True),
                ('INVENTÁRIO', lambda:self.open_panel('inventory'), True),
            ]),
            ('REGISTROS', 440, [
                ('BESTIÁRIO', lambda:self.open_panel('bestiary'), True),
                ('CONQUISTAS', lambda:self.open_panel('achievements'), True),
                ('ESTATÍSTICAS', lambda:self.open_panel('statistics'), True),
                ('RENOME', lambda:self.open_panel('renown'), True),
                ('EQUIPAMENTO', lambda:self.open_panel('equipment'), True),
            ]),
            ('SISTEMAS', 800, [
                ('MANOPLA', lambda:self.open_panel('gauntlet'), True),
                ('STATUS', lambda:self.open_panel('status'), True),
                ('DESCANSAR', self.rest, self.state.at_ship()),
                ('SALVAR', self.save, True),
                ('SAIR', lambda:setattr(self,'running',False), True),
            ]),
        ]
        for heading, x, entries in cols:
            self.label(heading, x, 112, 15, GOLD)
            for i,(title,cb,en) in enumerate(entries):
                rect_btn=(x, 145+i*83, 320, 57)
                self.button(rect_btn, title, cb, en)
                if title == 'CONQUISTAS' and self.has_unclaimed_achievements():
                    cx, cy = rect_btn[0]+rect_btn[2]-18, rect_btn[1]+14
                    pygame.draw.circle(self.canvas, (224,112,93), (cx,cy), 8)
                    self.label('!', cx-3, cy-6, 9, (250,230,205))
        self.button((975, 655, 145, 30), 'HACK', self.hack_inventory, True)
        self.label('ESC  fechar', 80, 680, 11, MUTED)

    def _mission_catalog(self, category=None):
        campaign = {
            'water_supply': {'title':'Água para Qaresh','objective':'Descubra por que a estação de captação perdeu pressão e escolha como resolver a crise de abastecimento.'},
            'kuvaar_hunt': {'title':'A Sede de Qaresh','objective':'Siga o rastro de sal, garanta Água Pura e enfrente Kuvaar, o Sorvedouro.'},
            'faction_conflict': {'title':'A Dívida da Fenda','objective':'Escolha o destino do confronto entre os Guardiões dos Reservatórios e os Filhos da Fenda.'},
            'explore_galaxy': {'title': self.state.exploration_mission_title(), 'objective':'Viaje pelos mundos conhecidos da Galáxia Nárion. Quando novas galáxias forem descobertas, esta missão passará a se chamar Explore o Universo.'},
            'ry_investigation': {'title': self.state.ry_mission_title(), 'objective':'Investigue o Vazio de RY. Derrote Kuvaar, Trembe, Ounull e Fagor; depois, fale com o povo de Nahr para descobrir a história do lugar.'},
            'dobra_core_install': {'title':'Potencializar a nave', 'objective':'Instale o Núcleo de Dobra recuperado de RY no motor da nave para habilitar viagens intergalácticas.'},
            'ship_laser_project': {'title':'Projeto: Emissor Laser', 'objective':'Receba o projeto de Mira nas Oficinas de Sifra após alcançar o primeiro nível de Renome dos Recuperadores de Qaresh.'},
        }
        ship = {mid:{'title':data['title'],'objective':data['objective'],'category':'NAVE'} for mid,data in SHIP_MISSION_DATA.items()}
        ship['travel_repair'] = {'title':'Reparar a nave','objective':'Repare os danos estruturais da última travessia usando Sucata.'}
        all_data = campaign | ship
        selected = category or getattr(self, 'journal_category', 'Campanha')
        ids = campaign.keys() if selected == 'Campanha' else ship.keys()
        return [(mid, all_data[mid], self.state.missions.get(mid, {})) for mid in ids]

    def _mission_detail(self, mission_id, mission):
        if mission_id in SHIP_MISSION_DATA:
            data = SHIP_MISSION_DATA[mission_id]
            if mission.get('status') == 'completed':
                return [f'{data["title"]} concluída.', f'{SHIP_SYSTEMS[data["system"]]["name"]}: 100%.']
            return [data['objective']]
        if mission_id == 'explore_galaxy':
            title = self.state.exploration_mission_title()
            mission = self.state.missions.get('explore_galaxy', mission)
            visited = mission.get('galaxies', []) if isinstance(mission, dict) else []
            if title == 'Explore o Universo':
                return [
                    'A exploração deixou de se limitar à Galáxia Nárion.',
                    f'Galáxias registradas nesta missão: {len(visited)}.',
                    'Novos avanços serão incorporados quando novos sistemas galácticos entrarem na campanha.',
                ]
            return [
                'Todos os sistemas essenciais da nave foram restaurados.',
                f'Galáxia catalogada: {GALAXY_NAME}.',
                'Viaje entre os mundos conhecidos e amplie o registro estelar. O objetivo continuará aberto até que novas galáxias sejam criadas.',
            ]
        if mission_id == 'dobra_core_install':
            if mission.get('status') == 'completed':
                return ['O Núcleo de Dobra foi instalado no motor da nave.', 'Vharos e Meridion agora estão disponíveis na Rota Estelar.']
            return [
                'O Núcleo de Dobra recuperado de RY foi reconhecido pelo motor.',
                'Acesse o Cockpit. A nave oferecerá a confirmação de instalação assim que detectar o item no inventário.',
            ]
        if mission_id == 'ry_investigation':
            state = self.state.missions.get('ry_investigation', mission)
            flags = state.get('flags', {})
            boss_names = [('kuvaar','Kuvaar'),('kael','Trembe'),('ounull','Ounull'),('fagor','Fagor')]
            if state.get('stage') == 'bosses':
                lines = ['Os quatro grandes bosses de Nárion precisam ser derrotados para revelar a presença no Vazio de RY.']
                for bid, name in boss_names:
                    lines.append(f'[OK] Derrote {name}' if flags.get(bid) else f'[ ] Derrote {name}')
                lines.append(f'Progresso: {sum(bool(flags.get(b)) for b,_ in boss_names)}/4.')
                return lines
            if state.get('stage') == 'history':
                return [
                    'Todos os quatro bosses de Nárion foram derrotados.',
                    'Investigue a história do Vazio de RY.',
                    'Fale com o povo de Nahr para aprender o idioma, ouvir seus relatos e descobrir quem habita esse lugar.',
                ]
            return [
                'A história do Vazio de RY foi revelada pelo povo de Nahr.',
                'RY, a personificação da morte segundo essa civilização, agora se manifesta no centro da área.',
                'A área de boss está disponível para confronto.',
            ]
        if mission_id == 'water_supply':
            status = mission.get('status')
            if status == 'completed':
                path = {'repair':'restauração manual','force':'confronto direto','hack':'infiltração pela Manopla'}.get(mission.get('path'),'solução registrada')
                return [
                    'A crise de abastecimento de Qaresh foi resolvida.',
                    f'Caminho utilizado: {path}.',
                    'A recompensa foi registrada e a investigação sobre a causa dos novos poços secando foi liberada.',
                ]
            return [
                'A Estação de Captação perdeu pressão e os Guardiões dos Reservatórios precisam de ajuda.',
                'Localize a estação e analise a origem da falha.',
                'Quando o problema estiver compreendido, escolha como resolver a crise: restaurar, tomar a recompensa à força ou infiltrar-se com a Manopla.',
            ]
        if mission_id == 'kuvaar_hunt':
            status = mission.get('status')
            if status == 'completed':
                return [
                    'Kuvaar, o Sorvedouro, foi derrotado.',
                    'A crise hídrica agora possui uma solução conhecida, e o registro do boss foi incorporado ao Simulador de Combate quando seu gadget for construído.',
                ]
            stage = int(mission.get('stage', 0))
            if status == 'tracking':
                return [
                    f'Rastros verdadeiros confirmados: {stage}/3.',
                    'Analise os rastros espalhados pelos setores de Veyra. Os rastros falsos consomem tempo e recursos de campo.',
                    'Depois dos três rastros verdadeiros, prepare Água Pura para entrar na Bacia Seca.',
                ]
            if status in ('water','boss_ready'):
                source = mission.get('water_source')
                source_text = {'borrow':'emprestada aos Avarin','produce':'produzida na nave','divert':'desviada de um reservatório'}.get(source, 'ainda não definida')
                return [
                    'A trilha de sal converge para a Bacia Seca de Kuvaar.',
                    f'Fonte da Água Pura: {source_text}.',
                    'Leve a reserva necessária até a Bacia Seca e use a água sobre a Couraça de Sal para abrir pontos vulneráveis.',
                ]
            return ['Investigue a causa viva que continua drenando o lençol freático ao redor de Qaresh.']
        if mission_id == 'ship_laser_project':
            if mission.get('status') == 'completed':
                return ['Projeto adquirido: Emissor Laser.', 'Instale-o pelo Computador da Nave quando possuir os componentes.']
            return ['Mira, nas Oficinas de Sifra, pode entregar o projeto.', 'Requisito: Avari conhecido e 25 Renome com os Recuperadores de Qaresh.']
        if mission_id == 'travel_repair':
            damage = int(getattr(self.state, 'travel_damage', 0) or 0)
            required = int(mission.get('required', damage) or damage)
            scrap = int(self.state.inventory.get('Sucata', 0))
            return [f'Dano de viagem: {damage}.', f'Reparo: {min(scrap, required)}/{required} Sucata.']
        if mission_id == 'faction_conflict':
            status = mission.get('status')
            if status == 'completed':
                winner = FACTIONS.get(mission.get('winner'), {}).get('name', 'facção vencedora')
                loser = FACTIONS.get(mission.get('loser'), {}).get('name', 'facção derrotada')
                path = 'sabotagem' if mission.get('path') == 'sabotage' else 'alerta ao líder dos Guardiões'
                return [
                    f'O confronto entre as facções terminou. Vencedores: {winner}. Derrotados: {loser}.',
                    f'Escolha registrada: {path}.',
                    f'A carta do líder derrotado foi registrada. A carta do líder vencedor pode ser fabricada na oficina mediante sua receita.',
                ]
            if status == 'active':
                return [
                    'Tarek quer que você comprometa a rede de comunicação dos Guardiões dos Reservatórios para que eles entrem despreparados em uma emboscada.',
                    'Ao alcançar Iria, você poderá executar a invasão ou alertá-la sobre a armadilha.',
                    'O resultado determinará qual líder cairá e qual Carta Mítica ficará disponível como consequência.',
                ]
            return ['Os Filhos da Fenda ainda não apresentaram sua proposta.']
        return ['Objetivo registrado. Consulte os detalhes conforme novos dados forem descobertos.']

    def _draw_scrollbar(self, rect, scroll, max_scroll):
        rect = pygame.Rect(rect)
        track = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
        pygame.draw.rect(self.canvas, (9,16,23), track, border_radius=4)
        if max_scroll <= 0:
            pygame.draw.rect(self.canvas, EDGE, track, border_radius=4)
            return
        thumb_h = max(28, int(track.height * (track.height/(track.height+max_scroll))))
        thumb_y = track.y + int((track.height-thumb_h)*(scroll/max_scroll))
        pygame.draw.rect(self.canvas, TEAL, (track.x, thumb_y, track.width, thumb_h), border_radius=4)

    def _register_scrollbar(self, key, rect, scroll, max_scroll):
        rect = pygame.Rect(rect)
        if max_scroll <= 0:
            self.scrollbars[key] = {'rect': rect, 'scroll': 0, 'max': 0, 'thumb': rect.copy()}
            return
        thumb_h = max(28, int(rect.height * (rect.height/(rect.height+max_scroll))))
        thumb_y = rect.y + int((rect.height-thumb_h)*(scroll/max_scroll))
        self.scrollbars[key] = {'rect': rect.copy(), 'scroll': scroll, 'max': max_scroll, 'thumb': pygame.Rect(rect.x, thumb_y, rect.width, thumb_h)}

    def _scroll_from_mouse(self, key, mouse_y):
        data = self.scrollbars.get(key)
        if not data or data['max'] <= 0:
            return
        rect, thumb = data['rect'], data['thumb']
        span = max(1, rect.height - thumb.height)
        pos = max(0, min(span, mouse_y - rect.y - thumb.height // 2))
        self.ui_scroll[key] = int(round(data['max'] * pos / span))

    def _mission_status_label(self, mission):
        status = mission.get('status', 'locked') if isinstance(mission, dict) else 'locked'
        return {'completed':'CONCLUÍDA','failed':'FRACASSADA','locked':'BLOQUEADA','available':'EM ANDAMENTO','active':'EM ANDAMENTO','resolving':'EM ANDAMENTO','tracking':'EM ANDAMENTO','water':'EM ANDAMENTO','boss_ready':'EM ANDAMENTO'}.get(status, 'EM ANDAMENTO')

    def journal(self):
        self.panel_header('DIÁRIO', 'Catálogo de missões da campanha.')
        mission_rect=pygame.Rect(35,111,575,590); detail_rect=pygame.Rect(635,111,530,590)
        self.box(mission_rect,(7,15,22),EDGE); self.box(detail_rect,(7,15,22),EDGE)
        self.button((55,125,180,30),'CAMPANHA',lambda:(setattr(self,'journal_category','Campanha'),self.ui_scroll.__setitem__('journal_list',0)),self.journal_category!='Campanha')
        self.button((245,125,160,30),'NAVE',lambda:(setattr(self,'journal_category','Nave'),self.ui_scroll.__setitem__('journal_list',0)),self.journal_category!='Nave')
        entries=self._mission_catalog(self.journal_category)
        active=[(mid,d,m) for mid,d,m in entries if m.get('status') not in ('completed','failed','locked')]
        completed=[(mid,d,m) for mid,d,m in entries if m.get('status')=='completed']
        other=[(mid,d,m) for mid,d,m in entries if m.get('status') in ('locked','failed')]
        sections=[('EM ANDAMENTO',active,TEAL,False),('CONCLUÍDAS',completed,GOLD,True),('OUTRAS',other,EDGE,False)]
        view=pygame.Rect(55,164,510,510); row_h=58; y=view.y-int(self.ui_scroll.get('journal_list',0))
        self.canvas.set_clip(view)
        for title,group,accent,completed_group in sections:
            self.label(title,58,y,16,GOLD if completed_group else accent); y+=28
            if not group:
                self.label('Nenhuma missão nesta categoria.',58,y,11,EDGE); y+=36; continue
            for mid,data,mission in group:
                rect=pygame.Rect(55,y,510,48); selected=self.journal_selected_mission==mid; status_text=self._mission_status_label(mission)
                status_color=GOLD if status_text=='CONCLUÍDA' else (224,112,93) if status_text=='FRACASSADA' else EDGE if status_text=='BLOQUEADA' else TEAL
                self.box(rect,(18,38,39) if selected else (12,22,29),status_color if selected else EDGE)
                self.label(self.fit_text(data['title'],13,315),rect.x+14,rect.y+9,13,TEAL if selected else INK); self.label(status_text,rect.right-150,rect.y+9,11,status_color)
                self.buttons.append((rect,lambda m=mid:(setattr(self,'journal_selected_mission',m),self.ui_scroll.__setitem__('journal',0)),True)); y+=row_h
        self.canvas.set_clip(None)
        max_left=max(0,y-(view.bottom-2)); self.ui_scroll['journal_list']=max(0,min(self.ui_scroll.get('journal_list',0),max_left))
        self._draw_scrollbar((573,164,8,510),self.ui_scroll['journal_list'],max_left); self._register_scrollbar('journal_list',(573,164,8,510),self.ui_scroll['journal_list'],max_left)
        selected=next(((mid,d,m) for mid,d,m in entries if mid==self.journal_selected_mission), entries[0] if entries else None)
        self.label('DETALHES DA MISSÃO',660,134,20,GOLD)
        if selected:
            mid,data,mission=selected; status=self._mission_status_label(mission); color=GOLD if status=='CONCLUÍDA' else EDGE if status=='BLOQUEADA' else (224,112,93) if status=='FRACASSADA' else TEAL
            self.label(self.fit_text(data['title'],20,430),660,173,20,TEAL); self.label(status,660,203,12,color)
            viewport=pygame.Rect(658,238,475,410)
            lines=[data['objective'],'']+self._mission_detail(mid,mission)
            self.canvas.set_clip(viewport); start_y=240-int(self.ui_scroll.get('journal',0)); yt=start_y
            for block in lines:
                if not block: yt+=12; continue
                yt=self.wrap(block,660,yt,445,14,INK if yt==start_y else MUTED,21)+6
            self.canvas.set_clip(None); max_scroll=max(0,yt-(viewport.bottom-4)); self.ui_scroll['journal']=max(0,min(self.ui_scroll.get('journal',0),max_scroll))
            self._draw_scrollbar((1138,238,9,410),self.ui_scroll['journal'],max_scroll); self._register_scrollbar('journal',(1138,238,9,410),self.ui_scroll['journal'],max_scroll)
    def routes(self):
        self.panel_header('MAPA', 'Mapa local e pontos conhecidos.')
        area = self.state.area
        self.box((35, 112, 530, 590))
        self.label(area['name'], 57, 133, 22, TEAL)
        cell = 18
        origin = (80, 193)
        for x in range(area['size']):
            for y in range(area['size']):
                color = tuple(c//2 for c in area['tint'])
                if (x,y) in area['rocks']:
                    color = (126, 134, 137)
                pygame.draw.rect(self.canvas, color, (origin[0]+x*cell, origin[1]+y*cell, cell-1, cell-1))
        def mark(pos, color, radius):
            pygame.draw.circle(self.canvas, color, (origin[0]+pos[0]*cell+8, origin[1]+pos[1]*cell+8), radius)
        for n in area['nodes']:
            if n['id'] not in self.state.collected_nodes:
                mark(n['pos'], GOLD, 3)
        for gate in area['exits']:
            if not self.state.route_visible(gate):
                continue
            mark(gate['at'], (224,112,93) if gate.get('target') == 'salt_basin' else TEAL, 9 if gate.get('target') == 'salt_basin' else 7)
        if area['ship']:
            mark(area['ship'], (156, 178, 240), 7)
        boss_site = next((l for l in area.get('landmarks', []) if l.get('boss_site') and self.state.boss_available(l.get('boss_site'))), None)
        if boss_site:
            mark(boss_site['pos'], (224, 112, 93), 8)
        settlement = area.get('settlement')
        if settlement and settlement['id'] in self.state.society['discovered_settlements']:
            mark(settlement['center'], GOLD, 6)
        faction_site = area.get('faction_site')
        if faction_site and faction_site.get('faction') != self.state.missions.get('faction_conflict', {}).get('loser'):
            mark(faction_site['center'], (214, 119, 86), 6)
        mark(self.state.pos, INK, 5)
        self.label('Você', 57, 641, 12, INK)
        self.label('Saídas', 120, 641, 12, TEAL)
        self.label('Coletas', 180, 641, 12, GOLD)
        self.label('Pontos especiais', 255, 641, 12, (224,112,93))

        self.box((590, 112, 575, 590))
        self.label('PONTOS CONHECIDOS', 614, 138, 20, GOLD)
        entries = []
        for gate in area['exits']:
            if self.state.route_visible(gate):
                target_name = SECTORS[gate['target']]['name']
                entries.append(('PASSAGEM', target_name, f'Posição {gate["at"][0]}, {gate["at"][1]} • tecla {gate["key"].upper()}', TEAL))
        if area['ship']:
            entries.append(('NAVE', 'Nave', f'Posição {area["ship"][0]}, {area["ship"][1]}', (156,178,240)))
        if boss_site:
            boss_id = boss_site.get('boss_site', 'kuvaar')
            entries.append(('BOSS', BOSSES.get(boss_id, {}).get('name', 'Boss'), f'Posição {boss_site["pos"][0]}, {boss_site["pos"][1]}', (224,112,93)))
        if settlement and settlement['id'] in self.state.society['discovered_settlements']:
            entries.append(('ASSENTAMENTO', settlement['name'], 'Ponto de interesse conhecido', GOLD))
        if faction_site and faction_site.get('faction') != self.state.missions.get('faction_conflict', {}).get('loser'):
            faction_name = FACTIONS.get(faction_site.get('faction'), {}).get('name', 'Facção')
            entries.append(('FACÇÃO', faction_name, 'Comunicação e contexto de missão', (214,119,86)))
        visible_sectors = [key for key in SECTORS if key in self.state.visited and (key != 'comms_ridge' or self.state.communication_route_visible())]
        for key in visible_sectors:
            status = 'ATUAL' if key == self.state.sector else ('VISITADO' if key in self.state.visited else 'NÃO VISITADO')
            entries.append(('SETOR', SECTORS[key]['name'], status, TEAL if key == self.state.sector else MUTED))

        view = pygame.Rect(614, 165, 512, 505)
        row_h = 68
        max_scroll = max(0, len(entries) * row_h - view.height)
        self.ui_scroll['routes_right'] = max(0, min(self.ui_scroll.get('routes_right', 0), max_scroll))
        self.canvas.set_clip(view)
        y = view.y - int(self.ui_scroll['routes_right'])
        for kind, title, detail, color in entries:
            rect = pygame.Rect(view.x, int(y), view.width-4, row_h-6)
            self.box(rect, (14,25,31), EDGE)
            self.label(kind, rect.x+12, rect.y+8, 10, color)
            self.label(self.fit_text(title, 14, 330), rect.x+12, rect.y+26, 14, INK)
            self.label(self.fit_text(detail, 10, 460), rect.x+12, rect.y+48, 10, MUTED)
            y += row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((1138,165,9,505),self.ui_scroll['routes_right'],max_scroll)
        self._register_scrollbar('routes_right',(1138,165,9,505),self.ui_scroll['routes_right'],max_scroll)
    def combat_backdrop(self):
        """Fundo da arena de combate com piso estável e simétrico.

        A versão anterior usava bordas em vários níveis de Y diferentes, fazendo
        o piso parecer inclinado no início do combate. Agora o chão tem uma linha
        de horizonte reta e uma plataforma central sem inclinação global; apenas
        os ladrilhos internos preservam a sensação de profundidade.
        """
        rect = pygame.Rect(285, 108, 545, 360)
        for yy in range(rect.top, rect.bottom):
            t = (yy - rect.top) / rect.height
            c = (int(24 + 50 * t), int(28 + 26 * t), int(37 + 16 * t))
            pygame.draw.line(self.canvas, c, (rect.left, yy), (rect.right, yy))

        # Céu/horizonte distante: linha completamente horizontal.
        horizon_y = 278
        pygame.draw.line(self.canvas, (83, 66, 60), (rect.left, horizon_y), (rect.right, horizon_y), 2)

        # Piso central: duas faixas trapezoidais, alinhadas no mesmo eixo.
        floor_top = 278
        floor_mid = 321
        floor_bottom = 370
        pygame.draw.polygon(
            self.canvas, (74, 57, 52),
            [(rect.left, floor_top), (rect.right, floor_top),
             (rect.right, floor_mid), (rect.left, floor_mid)]
        )
        pygame.draw.polygon(
            self.canvas, (106, 77, 59),
            [(rect.left, floor_mid), (rect.right, floor_mid),
             (rect.right, floor_bottom), (rect.left, floor_bottom)]
        )

        # Sol de fundo.
        pygame.draw.circle(self.canvas, (239, 185, 110), (742, 164), 26)
        pygame.draw.circle(self.canvas, (255, 220, 170), (742, 164), 17)

        # Ladrilhos isométricos discretos, todos dentro de um retângulo estável.
        tile_y = 339
        for gy in range(4):
            for gx in range(7):
                px = 560 + (gx - gy) * 38
                py = tile_y + (gx + gy) * 14
                pts = [(px, py - 12), (px + 26, py), (px, py + 12), (px - 26, py)]
                if rect.left - 30 <= px <= rect.right + 30 and floor_mid - 12 <= py <= floor_bottom + 20:
                    pygame.draw.polygon(self.canvas, (128 + ((gx + gy) % 3) * 4, 91 + ((gx + gy) % 3) * 2, 67), pts)
                    pygame.draw.lines(self.canvas, (106, 77, 61), True, pts, 1)

        pygame.draw.line(self.canvas, (72, 49, 45), (rect.left, floor_bottom), (rect.right, floor_bottom), 1)

    def draw_kuvaar_water_deposits(self, b):
        """Desenha os depósitos ambientais de Água Pura do encontro com Kuvaar."""
        if not b or not b.get('boss') or b.get('species') != 'kuvaar':
            return
        total = int(b.get('water_deposit_total', 0))
        used = set(b.get('used_water_deposits', []))
        positions = ((585, 472), (810, 470), (690, 530))
        active_index = 0
        for idx in range(1, total + 1):
            if f'water_deposit_{idx}' in used:
                continue
            if active_index >= len(positions):
                break
            x, y = positions[active_index]
            # Reservatório compacto, luminoso e legível mesmo no mapa reduzido da batalha.
            pygame.draw.ellipse(self.canvas, (34, 82, 96), (x-24, y-12, 48, 25))
            pygame.draw.ellipse(self.canvas, (75, 157, 177), (x-20, y-17, 40, 16))
            pygame.draw.ellipse(self.canvas, (128, 211, 222), (x-15, y-14, 30, 10), 2)
            pygame.draw.rect(self.canvas, (62, 118, 132), (x-18, y-1, 36, 10), border_radius=4)
            pygame.draw.line(self.canvas, GOLD, (x, y-10), (x, y-25), 2)
            pygame.draw.circle(self.canvas, GOLD, (x, y-28), 4, 1)
            active_index += 1

    def _battle_target_pos(self, b, enemy_x):
        target = (b or {}).get('target', 'body')
        if str(target).startswith('water_deposit_'):
            try:
                idx = int(str(target).rsplit('_', 1)[-1]) - 1
            except ValueError:
                idx = 0
            positions = ((585, 472), (810, 470), (690, 530))
            return positions[max(0, min(idx, len(positions)-1))]
        return (enemy_x, 390 if not (b and b.get('boss')) else 382)

    def _attack_basis(self, start, end):
        dx = float(end[0] - start[0])
        dy = float(end[1] - start[1])
        length = max(1.0, math.hypot(dx, dy))
        ux, uy = dx / length, dy / length
        return ux, uy, -uy, ux

    def _draw_card_fx(self, b, hero_x, enemy_x, start_override=None, end_override=None):
        fx = self.card_fx
        if not fx or self.phase != 'hero':
            return
        t = self.phase_time
        duration = 0.68
        if t >= duration:
            return
        card_id = fx.get('card')
        card = CARDS.get(card_id, {}) if card_id != 'basic' else {}
        visual = 'plasma' if card_id == 'basic' else card.get('visual_key', 'orb')
        target = self._battle_target_pos(b, enemy_x)
        start = start_override if start_override is not None else (hero_x + 48, 364)
        end = end_override if end_override is not None else target
        p = max(0.0, min(1.0, t / 0.42))
        if p > 0.78:
            p = 1.0
        px = int(start[0] + (end[0] - start[0]) * p)
        py = int(start[1] + (end[1] - start[1]) * p)

        if visual == 'plasma':
            self._draw_basic_gauntlet_attack(start, end, (px, py), p, t)
            return

        palette = {
            'silica_shard': (201, 236, 236), 'sand_bite': (211, 169, 100), 'electric_burst': (90, 203, 230),
            'silica_charge': (230, 115, 88), 'glass_break': (174, 142, 220), 'dust_dive': (183, 151, 105),
            'prism_rend': (106, 225, 208), 'guard_strike': (226, 177, 91), 'monolith_sentence': (194, 177, 139),
            'rift_break': (219, 104, 76), 'saline_dissolution': (215, 230, 214), 'fireball': (232, 105, 58),
            'root_vigor': (88, 167, 100), 'water_flux': (102, 205, 224), 'luminous_fulgor': (222, 236, 242),
            'water_tide': (90, 193, 219), 'magma_spear': (220, 86, 51), 'forge_pincer': (189, 198, 198),
            'ion_burst': (106, 210, 237), 'frost_bite': (165, 222, 242), 'crystal_fragment': (172, 236, 248),
            'frost_wind': (116, 202, 224), 'root_spear': (94, 179, 107), 'basalt_boulder': (130, 127, 119),
            'salt_spit': (222, 226, 203), 'luminous_ray': (194, 245, 245), 'umbra_claw': (137, 97, 180),
            'spore_cloud': (112, 193, 103), 'iron_cut': (177, 190, 198), 'magnetic_ram': (124, 151, 168),
            'gloom_wing': (110, 82, 154), 'vesper_claw': (143, 104, 187), 'charge_arc': (100, 201, 231),
            'ion_jump': (123, 222, 242), 'ember_dash': (225, 105, 59), 'scoria_bite': (214, 93, 47),
            'tide_cut': (106, 210, 228), 'abyss_fang': (76, 175, 208), 'spore_burst': (103, 194, 93),
            'mycelial_claws': (125, 184, 104), 'wind_slash': (135, 213, 199), 'light_dive': (184, 245, 242),
            'street_pulse': (104, 200, 215), 'prismatic_hunt': (111, 231, 215), 'magnetic_pulse': (107, 166, 181),
            'eclipse': (113, 91, 143), 'storm_arc': (99, 201, 238), 'reverse_tide': (84, 187, 218),
            'predator_spore': (112, 190, 99), 'monolithic_impact': (145, 138, 127), 'fireball_colossal': (241, 91, 48),
            'broom_lightning': (122, 218, 245), 'orb': TEAL,
        }
        color = palette.get(visual, TEAL)
        ux, uy, nx, ny = self._attack_basis(start, end)
        multi = bool(card.get('target_mode') == 'multi')
        glow = pygame.Surface((W, H))
        glow.fill((0, 0, 0))

        def gline(points, width, gain=1.0):
            c = tuple(min(255, int(v * gain)) for v in color)
            pygame.draw.lines(glow, c, False, [(int(a), int(b_)) for a,b_ in points], max(1, int(width)))

        def gcircle(pos, radius, gain=1.0):
            c = tuple(min(255, int(v * gain)) for v in color)
            pygame.draw.circle(glow, c, (int(pos[0]), int(pos[1])), max(1, int(radius)))

        def shard(cx, cy, size, fill=None):
            fill = fill or color
            pts = [(int(cx + ux*size), int(cy + uy*size)),
                   (int(cx + nx*size*0.55), int(cy + ny*size*0.55)),
                   (int(cx - ux*size*0.65), int(cy - uy*size*0.65)),
                   (int(cx - nx*size*0.45), int(cy - ny*size*0.45))]
            pygame.draw.polygon(self.canvas, fill, pts)
            pygame.draw.line(self.canvas, (242, 248, 244), pts[0], pts[2], 1)

        # Todos os estilos começam com uma pequena preparação luminosa do projétil.
        if visual in ('silica_shard', 'silica_charge', 'crystal_fragment', 'ice_crystal'):
            shard(px, py, 12 if visual != 'silica_charge' else 14)
            for i, q in enumerate((0.22, 0.46, 0.68)):
                cx = start[0] + (end[0]-start[0])*max(0, p-q)
                cy = start[1] + (end[1]-start[1])*max(0, p-q)
                shard(cx + nx*(i-1)*5, cy + ny*(i-1)*5, 5 + i)
            gcircle((px,py), 13, 0.18)
        elif visual == 'sand_bite':
            for i in range(11):
                q = ((i * 7) % 12) / 12.0
                bx = start[0] + (end[0]-start[0])*min(p, q) + nx * math.sin(i*1.6 + t*3)*18*(q+0.2)
                by = start[1] + (end[1]-start[1])*min(p, q) + ny * math.sin(i*1.6 + t*3)*18*(q+0.2)
                r = 2 + (i % 3)
                pygame.draw.circle(self.canvas, color, (int(bx), int(by)), r)
            pygame.draw.arc(self.canvas, (236, 197, 128), (px-17,py-13,34,28), 0.25, 2.9, 2)
            gcircle((px,py), 17, 0.12)
        elif visual in ('electric_burst', 'charge_arc', 'ion_jump', 'storm_arc'):
            pts=[start]; steps=max(3,int(7*p))
            for i in range(1,steps+1):
                q=i/steps; bx=start[0]+(end[0]-start[0])*q; by=start[1]+(end[1]-start[1])*q
                jx = nx * (7 + 4*math.sin(i*2.1+t*7))
                jy = ny * (7 + 4*math.sin(i*2.1+t*7))
                pts.append((int(bx+jx), int(by+jy)))
            gline(pts, 8, 0.35); gline(pts, 4, 0.65)
            pygame.draw.lines(self.canvas, (218, 249, 255), False, pts, 2)
            if visual in ('electric_burst','ion_jump'):
                for off in (-1, 1):
                    pygame.draw.line(self.canvas, color, (px,py), (int(px+nx*off*22+ux*10), int(py+ny*off*22+uy*10)), 2)
            gcircle((px,py), 11, 0.5)
        elif visual in ('glass_break', 'monolithic_impact', 'monolith_sentence', 'basalt_boulder', 'magnetic_ram'):
            size = 15 if visual in ('monolithic_impact','monolith_sentence') else 11
            shard(px, py, size, color if visual != 'glass_break' else (185,150,225))
            for i, a in enumerate((0.0, 1.8, 3.6, 5.2)):
                dist = 16 + ((i*9) % 13) * (0.45 + 0.35*p)
                qx, qy = int(px + math.cos(a+t*2.2)*dist), int(py + math.sin(a+t*2.2)*dist)
                pygame.draw.line(self.canvas, color, (px,py), (qx,qy), 2)
            gcircle((px,py), 18, 0.25)
        elif visual in ('dust_dive', 'spore_cloud', 'predator_spore'):
            spread = 22 if visual != 'predator_spore' else 31
            for i in range(17 if visual == 'predator_spore' else 12):
                q = ((i*5)%13)/13.0
                bx = start[0] + (end[0]-start[0])*min(p,q) + nx*math.sin(i*1.55+t*2.3)*spread*(0.4+q)
                by = start[1] + (end[1]-start[1])*min(p,q) + ny*math.sin(i*1.55+t*2.3)*spread*(0.4+q)
                pygame.draw.circle(self.canvas, color, (int(bx),int(by)), 1+(i%3))
            gline([(start[0]+nx*9,start[1]+ny*9),(px+nx*spread,py+ny*spread)], 9, 0.20)
            gline([(start[0]-nx*9,start[1]-ny*9),(px-nx*spread,py-ny*spread)], 9, 0.20)
        elif visual in ('prism_rend', 'prismatic_hunt', 'luminous_ray', 'luminous_fulgor'):
            for off in (-8,0,8):
                a=(start[0]+nx*off,start[1]+ny*off); z=(px+nx*off*0.45,py+ny*off*0.45)
                gline([a,z], 7, 0.22)
                pygame.draw.line(self.canvas, (205, 252, 245), a, z, 1 if off else 2)
            if visual == 'luminous_fulgor':
                for ang in (-0.55,-0.18,0.18,0.55):
                    pygame.draw.line(self.canvas, (238,247,241), (px,py), (int(px+math.cos(math.atan2(uy,ux)+ang)*24), int(py+math.sin(math.atan2(uy,ux)+ang)*24)), 2)
            gcircle((px,py), 15, 0.22)
        elif visual in ('guard_strike','iron_cut','forge_pincer','vesper_claw','umbra_claw','gloom_wing'):
            for off in (-9,0,9):
                a=(px+nx*off-ux*12,py+ny*off-uy*12); z=(px+nx*off+ux*15,py+ny*off+uy*15)
                pygame.draw.line(self.canvas, color, a, z, 3)
                gline([a,z], 6, 0.25)
            if visual == 'guard_strike' and t >= 0.42:
                pygame.draw.circle(self.canvas, TEAL, (int(start[0]),int(start[1])), 13, 2)
        elif visual in ('rift_break','eclipse'):
            width = 28 if visual == 'rift_break' else 20
            for off in (-width//2, 0, width//2):
                a=(int(px+nx*off-ux*12), int(py+ny*off-uy*12)); z=(int(px+nx*off+ux*15), int(py+ny*off+uy*15))
                pygame.draw.line(self.canvas, color, a, z, 2)
                gline([a,z], 7, 0.22)
            gcircle((px,py), 17, 0.24)
        elif visual in ('saline_dissolution','salt_spit'):
            for i in range(9):
                ang = math.atan2(uy,ux) + (-0.44 + i*0.11)
                dist = 10 + i*2
                qx=int(px+math.cos(ang)*dist); qy=int(py+math.sin(ang)*dist)
                pygame.draw.circle(self.canvas, color, (qx,qy), 2+(i%2))
            gline([(start[0],start[1]),(px,py)], 6, 0.18)
        elif visual in ('fireball','fireball_colossal'):
            radius = 15 if visual == 'fireball' else 24
            pygame.draw.circle(self.canvas, color, (px,py), radius)
            pygame.draw.circle(self.canvas, (250, 184, 98), (px-int(ux*5),py-int(uy*5)), int(radius*0.68))
            pygame.draw.circle(self.canvas, (255, 241, 196), (px-int(ux*8),py-int(uy*8)), int(radius*0.28))
            for i in range(7):
                qx=int(px-ux*(16+i*4)-nx*math.sin(i+t*5)*5); qy=int(py-uy*(16+i*4)-ny*math.sin(i+t*5)*5)
                pygame.draw.circle(self.canvas, (242, 138, 68), (qx,qy), 2+(i%2))
            gcircle((px,py), radius+11, 0.35)
        elif visual in ('root_vigor','root_spear','mycelial_claws'):
            count = 5 if visual != 'root_spear' else 3
            for i in range(count):
                side = (i-(count-1)/2)*8
                pts=[(int(start[0]+nx*side),int(start[1]+ny*side))]
                for q in (0.35,0.68,1.0):
                    bx=start[0]+(end[0]-start[0])*min(p,q); by=start[1]+(end[1]-start[1])*min(p,q)
                    bend=math.sin(q*6+i+t*4)*6
                    pts.append((int(bx+nx*side+nx*bend),int(by+ny*side+ny*bend)))
                pygame.draw.lines(self.canvas, color, False, pts, 3)
            gline([(start[0],start[1]),(px,py)], 7, 0.18)
        elif visual in ('water_flux','water_tide','reverse_tide','tide_cut','abyss_fang'):
            spread = 22 if visual in ('water_tide','reverse_tide') else 10
            pts=[]
            for i in range(9):
                q=i/8; bx=start[0]+(end[0]-start[0])*min(p,q); by=start[1]+(end[1]-start[1])*min(p,q)
                wave=math.sin(q*math.tau*1.6+t*8)*spread*(0.25+0.75*q)
                pts.append((int(bx+nx*wave),int(by+ny*wave)))
            gline(pts, 8, 0.24); pygame.draw.lines(self.canvas, (203,245,250), False, pts, 2)
            for side in (-1,1):
                pygame.draw.arc(self.canvas, color, (px-15,py-10,30,20), (0.2 if side>0 else 2.9), (2.2 if side>0 else 5.0), 2)
            if visual == 'abyss_fang':
                shard(px,py,18,(132,224,241))
        elif visual in ('magma_spear','scoria_bite','ember_dash'):
            shard(px,py,14,(222,85,49))
            for i in range(6):
                qx=int(px-ux*(10+i*5)+nx*math.sin(i+t*5)*4); qy=int(py-uy*(10+i*5)+ny*math.sin(i+t*5)*4)
                pygame.draw.circle(self.canvas,(232,117,62),(qx,qy),2+(i%2))
            gline([(start[0],start[1]),(px,py)], 9, 0.22)
        elif visual in ('ion_burst','magnetic_pulse','street_pulse','charge_arc'):
            for r in (7,13,19):
                pygame.draw.circle(self.canvas, color, (px,py), r, 2)
            gline([(px-25,py),(px+25,py)], 6, 0.22)
            gline([(px,py-20),(px,py+20)], 6, 0.16)
        elif visual == 'frost_bite':
            shard(px,py,15,(168,224,245)); pygame.draw.line(self.canvas,(228,249,255),(px,py),end,1); gcircle((px,py),15,0.24)
        elif visual == 'frost_wind':
            for off in (-10,0,10):
                pygame.draw.arc(self.canvas,color,(px-19+off,py-14,34,28),0.1,2.85,2)
            gline([(start[0],start[1]),(px,py)],7,0.18)
        elif visual == 'basalt_boulder':
            pygame.draw.polygon(self.canvas, (132,125,117), [(px-13,py+7),(px-8,py-9),(px+5,py-14),(px+15,py-2),(px+10,py+10),(px-3,py+13)])
            pygame.draw.line(self.canvas,(205,192,175),(px-6,py-6),(px+5,py+5),2); gcircle((px,py),16,0.17)
        elif visual == 'salt_spit':
            for off in (-11,-5,1,7,13):
                qx=int(px+nx*off+ux*8); qy=int(py+ny*off+uy*8)
                pygame.draw.line(self.canvas,(243,239,218),(qx,qy),(int(qx+ux*8),int(qy+uy*8)),2)
            gcircle((px,py),13,0.18)
        elif visual == 'root_spear':
            pts=[(int(px-ux*18-nx*7),int(py-uy*18-ny*7)),(px,py),(int(px-ux*18+nx*7),int(py-uy*18+ny*7))]
            pygame.draw.polygon(self.canvas,color,pts); gcircle((px,py),12,0.18)
        elif visual == 'luminous_ray':
            gline([start,(px,py)],13,0.25); pygame.draw.line(self.canvas,(248,255,255),start,(px,py),2)
        elif visual == 'spore_burst':
            for i in range(10):
                ang=i*0.63+t*1.5; rad=6+i*2
                pygame.draw.circle(self.canvas,color,(int(px+math.cos(ang)*rad),int(py+math.sin(ang)*rad)),2)
            gcircle((px,py),16,0.16)
        elif visual == 'magnetic_ram':
            shard(px,py,15,(129,155,169)); pygame.draw.circle(self.canvas,(176,204,211),(px,py),19,2); gcircle((px,py),22,0.20)
        elif visual == 'light_dive':
            pygame.draw.line(self.canvas,(233,255,252),(px-int(nx*11),py-int(ny*11)),(px+int(nx*11),py+int(ny*11)),3)
            pygame.draw.line(self.canvas,color,(px-int(ux*24),py-int(uy*24)),(px+int(ux*7),py+int(uy*7)),2); gcircle((px,py),13,0.28)
        elif visual == 'prismatic_hunt':
            pts=[(px+int(nx*12),py+int(ny*12)),(px+int(ux*17),py+int(uy*17)),(px-int(nx*12),py-int(ny*12))]
            pygame.draw.polygon(self.canvas,color,pts); pygame.draw.line(self.canvas,(230,255,249),pts[1],pts[0],2); gcircle((px,py),16,0.22)
        else:
            pygame.draw.circle(self.canvas,color,(px,py),7)
            pygame.draw.circle(self.canvas,(245,250,246),(px-int(ux*2),py-int(uy*2)),3)
            gcircle((px,py),10,0.18)

        # A camada aditiva unifica o novo padrão luminoso sem apagar o núcleo desenhado.
        self.canvas.blit(glow, (0,0), special_flags=pygame.BLEND_RGB_ADD)

        # Impacto / expansão curta.
        if t >= 0.42:
            k = min(1.0, (t - 0.42) / 0.26)
            radius = int(8 + 25 * k)
            pygame.draw.circle(self.canvas, color, end, max(4, radius), 2)
            if multi:
                for off in (-16, 0, 16):
                    pygame.draw.circle(self.canvas, color, (int(end[0]+nx*off), int(end[1]+ny*off)), max(3, radius//2), 1)
            if visual in ('guard_strike','water_flux','luminous_fulgor'):
                pygame.draw.circle(self.canvas, TEAL, (int(start[0]),int(start[1])), int(8+10*k), 2)

    def _draw_basic_gauntlet_attack(self, start, end, tip, progress, elapsed):
        """Raio de Plasma: feixe tecnológico luminoso com bloom aditivo.

        O efeito é construído em uma superfície RGB preta e aplicado ao canvas
        com BLEND_RGB_ADD. Assim, as camadas de brilho realmente somam luz ao
        cenário, enquanto o núcleo branco mantém a leitura de um emissor
        tecnológico. O movimento é totalmente determinístico para não causar
        tremulação aleatória entre quadros.
        """
        beam = pygame.Surface((W, H))
        beam.fill((0, 0, 0))

        # Vetor normalizado do feixe para posicionar um halo suave ao redor do núcleo.
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / length, dx / length

        # O disparo nasce comprimido na Manopla e cresce rapidamente até o alvo.
        beam_end = (int(start[0] + dx * progress), int(start[1] + dy * progress))

        # Glow externo: três passagens largas em ciano/azul, todas aditivas.
        pygame.draw.line(beam, (18, 62, 86), start, beam_end, 18)
        pygame.draw.line(beam, (32, 118, 146), start, beam_end, 11)
        pygame.draw.line(beam, (72, 196, 218), start, beam_end, 6)

        # Pequenas estrias laterais dão sensação de plasma fluindo pelo feixe.
        pulse = 0.55 + 0.45 * math.sin(elapsed * 28.0)
        side_amp = 2.0 + 2.0 * pulse
        for i in range(1, 9):
            q = i / 9.0
            bx = start[0] + (beam_end[0] - start[0]) * q
            by = start[1] + (beam_end[1] - start[1]) * q
            offset = math.sin(elapsed * 20.0 + i * 1.7) * side_amp
            a = (int(bx + nx * offset - dx / length * 7), int(by + ny * offset - dy / length * 7))
            b = (int(bx + nx * offset + dx / length * 7), int(by + ny * offset + dy / length * 7))
            pygame.draw.line(beam, (105, 232, 246), a, b, 1)

        # O centro quase branco é o elemento de maior energia visual.
        pygame.draw.line(beam, (190, 248, 255), start, beam_end, 3)
        pygame.draw.line(beam, (255, 255, 255), start, beam_end, 1)

        # Partículas e halo no emissor.
        emitter_radius = int(5 + 3 * pulse)
        pygame.draw.circle(beam, (115, 232, 245), start, emitter_radius)
        pygame.draw.circle(beam, (245, 255, 255), start, max(2, emitter_radius // 2))

        # Impacto: fragmentos determinísticos se espalham do ponto de contato.
        if elapsed >= 0.34:
            impact_k = min(1.0, (elapsed - 0.34) / 0.34)
            ix, iy = end
            ring_r = int(6 + 24 * impact_k)
            pygame.draw.circle(beam, (70, 190, 218), (int(ix), int(iy)), ring_r, max(1, int(4 - 2 * impact_k)))
            pygame.draw.circle(beam, (196, 248, 255), (int(ix), int(iy)), max(3, int(ring_r * 0.42)), 1)
            for i in range(10):
                angle = elapsed * (4.2 + i * 0.11) + i * (math.tau / 10.0)
                dist = 10 + 24 * impact_k + (i % 3) * 4
                sx = int(ix + math.cos(angle) * dist)
                sy = int(iy + math.sin(angle) * dist)
                pygame.draw.line(beam, (130, 224, 240), (int(ix), int(iy)), (sx, sy), 1)

        self.canvas.blit(beam, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _draw_enemy_fx(self, b, hero_x, enemy_x):
        fx = self.enemy_fx
        if not fx or self.phase != 'enemy':
            return
        t = self.phase_time
        if t >= 0.68:
            return
        species = fx.get('species', 'scarab')
        target = (hero_x - 45, 365)
        start = (enemy_x - 48, 355)
        p = max(0.0, min(1.0, t / 0.42))
        if p > 0.78:
            p = 1.0
        px = int(start[0] + (target[0] - start[0]) * p)
        py = int(start[1] + (target[1] - start[1]) * p)

        # Técnicas especiais reutilizam exatamente a identidade visual da carta
        # correspondente. Assim, criatura e carta comunicam a mesma habilidade.
        card_id = fx.get('card') if fx.get('special') else None
        if card_id:
            card = CARDS.get(card_id, {})
            visual = card.get('visual_key')
            if visual == 'broom_lightning':
                glow = pygame.Surface((W,H)); glow.fill((0,0,0))
                for spread, width, gain in ((10, 11, .22), (5, 6, .48), (2, 3, .90)):
                    pts=[start]
                    steps=max(3,int(7*p))
                    for i in range(1,steps+1):
                        q=i/steps; bx=start[0]+(target[0]-start[0])*q; by=start[1]+(target[1]-start[1])*q
                        pts.append((int(bx+(7 if i%2 else -6)), int(by+(5 if i%3 else -5))))
                    pygame.draw.lines(glow, (120,220,245), False, pts, width)
                self.canvas.blit(glow,(0,0),special_flags=pygame.BLEND_RGB_ADD)
                pts=[start]; steps=max(3,int(7*p))
                for i in range(1,steps+1):
                    q=i/steps; bx=start[0]+(target[0]-start[0])*q; by=start[1]+(target[1]-start[1])*q
                    pts.append((int(bx+(7 if i%2 else -6)), int(by+(5 if i%3 else -5))))
                pygame.draw.lines(self.canvas,(228,250,255),False,pts,2)
                if t >= 0.42:
                    k=min(1.0,(t-.42)/.26); pygame.draw.circle(self.canvas,(151,229,247),target,int(7+18*k),2)
                return
            # Reaproveitamos o mesmo renderer passando a técnica pelo canal de carta.
            saved = self.card_fx
            self.card_fx = {'card': card_id}
            old_phase, old_time = self.phase, self.phase_time
            self.phase = 'hero'
            self.phase_time = t
            self._draw_card_fx(b, hero_x, enemy_x, start_override=start, end_override=target)
            self.phase, self.phase_time = old_phase, old_time
            self.card_fx = saved
            return

        # Ataque básico: impacto físico simples, sem alterar regra ou dano.
        spec = BOSSES.get(species) or SPECIES.get(species, {})
        type_colors = {'Metal':(177,190,198),'Terra':(189,156,103),'Fogo':(224,105,59),'Água':(103,203,223),
                       'Planta':(96,177,100),'Elétrico':(105,210,236),'Luz':(210,237,235),'Trevas':(135,96,175)}
        color = type_colors.get(spec.get('type'), (205,184,144))
        pygame.draw.line(self.canvas, color, start, (px,py), 3)
        if p >= 0.55:
            pygame.draw.line(self.canvas, color, (px-11,py-7),(px+8,py+8),3)
            pygame.draw.line(self.canvas, color, (px-7,py+9),(px+10,py-7),2)
        if t >= 0.42:
            k=min(1.0,(t-.42)/.26)
            pygame.draw.circle(self.canvas,color,target,max(4,int(7+16*k)),2)

    def battle_view(self):
        b = self.state.battle
        species = b['species'] if b else self.battle_species
        boss = bool(b and b.get('boss'))
        spec = BOSSES[species] if boss else SPECIES[species]

        self.label('COMBATE', 30, 20, 24, GOLD)
        self.label(spec['name'].upper(), 30, 54, 19, TEAL)
        self.label('SUA VEZ' if self.phase == 'choose' else 'AÇÃO EM CURSO', 30, 80, 14, MUTED)
        if b and b.get('challenge') is None and int(b.get('turns',0)) == 0 and self.state.gauntlet_nexus_installed:
            self.button((620,56,145,30),'DESAFIOS',lambda:setattr(self,'challenge_menu_open',True),True)

        self.box((30, 112, 235, 190), (9, 17, 24), EDGE)
        self.label('VOCÊ', 50, 130, 18, TEAL)
        self.label(f'VIDA {self.state.hp}/{self.state.max_hp}', 50, 164, 13, INK)
        self.bar(50, 188, 195, self.state.hp, self.state.max_hp, (203, 112, 94))
        self.label(f'MEMÓRIA {self.state.memory}/{self.state.max_memory}', 50, 222, 13, INK)
        self.bar(50, 246, 195, self.state.memory, max(1, self.state.max_memory), TEAL)
        self.label('Atributos: consulte STATUS.', 50, 279, 11, MUTED)

        self.combat_backdrop()
        self.draw_kuvaar_water_deposits(b)
        hero_x, enemy_x = 420, (700 if boss else 720)
        if self.phase == 'hero' and self.result.get('damage', 0):
            hero_x += math.sin(min(1, self.phase_time/.7)*math.pi)*45
        if self.phase == 'enemy':
            enemy_x -= math.sin(min(1, self.phase_time/.7)*math.pi)*45
        self.actor('hero', hero_x, 414, 1.95, int(self.frame*5), pose='combat')
        self.actor(species, enemy_x, 390 if not boss else 392, 2.45 if not boss else 3.55, int(self.frame*5), True)
        self._draw_card_fx(b, hero_x, enemy_x)
        self._draw_enemy_fx(b, hero_x, enemy_x)

        if self.phase in ('hero', 'enemy') and self.phase_time < .65:
            hit = self.result.get('damage', 0)
            x, y = (690, 205) if self.phase == 'hero' else (405, 230)
            popup_color = GOLD if self.phase == 'hero' else (247, 124, 116)
            if self.result.get('water_deposit'):
                self.label('DEPÓSITO ATINGIDO', x-72, y-int(self.phase_time*35), 20, TEAL)
                self.label('COURAÇA - 1 CAMADA', x-64, y-36-int(self.phase_time*30), 12, GOLD)
            elif self.result.get('miss'):
                self.label('ERROU!', x-10, y-int(self.phase_time*35), 28, popup_color)
            elif self.result.get('heal'):
                self.label(f'+{self.result["heal"]}', x, y-int(self.phase_time*45), 34, popup_color)
            else:
                # A leitura do dano prioriza o estado mais forte: Crítico > Vantagem > Desvantagem.
                # Quando há combinação (ex.: Crítico + Vantagem), os rótulos continuam sendo
                # exibidos individualmente acima do valor para que nenhuma informação se perca.
                relation = self.result.get('type_relation')
                is_critical = bool(self.result.get('critical'))
                if is_critical:
                    damage_color = (248, 211, 95)
                elif relation == 'advantage':
                    damage_color = (92, 232, 178)
                elif relation == 'disadvantage':
                    damage_color = (226, 126, 184)
                else:
                    damage_color = popup_color
                self.label(f'-{hit}', x, y-int(self.phase_time*45), 34, damage_color)

                label_y = y-46-int(self.phase_time*30)
                if relation == 'advantage':
                    self.label('VANTAGEM', x-34, label_y, 14, (92, 232, 178))
                    label_y -= 21
                elif relation == 'disadvantage':
                    self.label('DESVANTAGEM', x-46, label_y, 14, (226, 126, 184))
                    label_y -= 21
                if is_critical:
                    self.label('CRÍTICO!', x-30, label_y, 15, (248, 211, 95))

        # Área exclusiva para seleção do ponto de impacto.
        # O bloco superior é somente para alvo; a leitura do inimigo fica separada.
        self.box((850, 112, 320, 232), (9, 17, 24), EDGE)
        self.label('PONTO DE IMPACTO', 872, 130, 18, GOLD)
        targets = self.state.battle_targets() if b else []
        target_y = 157
        target_h = 29
        target_gap = 4
        for target in targets:
            active = target['id'] == (b.get('target') if b else self.selected_battle_target)
            chance = self.state.target_hit_chance(target['id'])
            rect = (870, target_y, 280, target_h)
            marker = '▶ ' if active else '  '
            # O estado selecionado é comunicado pelo próprio destaque do botão;
            # não ocupamos a área com um subtítulo redundante.
            self.button(rect, marker + f'{target["name"].upper()}    {chance}%',
                        lambda tid=target['id']: self.select_battle_target(tid),
                        self.phase == 'choose')
            target_y += target_h + target_gap

        # Informação vital do inimigo fica abaixo, sem disputar espaço com os alvos.
        self.box((850, 356, 320, 136), (9, 17, 24), EDGE)
        self.label(spec['name'].upper(), 872, 372, 15, TEAL)
        self.label('INTEGRIDADE', 872, 395, 11, MUTED)
        hp_value = b['hp'] if b else spec['hp']
        self.bar(872, 415, 260, hp_value, spec['hp'], (193, 93, 84))
        scanned = bool(self.state.bestiary_scanned and species in self.state.bestiary_scanned)
        if boss and self.state.helmet_equipped and self.state.scan_unlocked:
            scanned = True
        if boss and species == 'kuvaar':
            shell_layers = b.get('shell_layers', 3)
            exposure = 'EXPOSTO' if b.get('exposed_turns', 0) > 0 or shell_layers <= 0 else 'BLINDADO'
            self.label(f'COURAÇA: {exposure}', 872, 437, 11, GOLD if exposure == 'EXPOSTO' else MUTED)
            remaining = int(b.get('water_deposits_remaining', 0))
            self.label(f'DEPÓSITOS: {remaining}/{int(b.get("water_deposit_total", 0))}', 1010, 437, 11, TEAL if remaining else MUTED)
        elif boss and species == 'fagor':
            z=b.get('zone_hp',{}); zm=b.get('zone_hp_max',{})
            self.label(f'PERNA ESQ. {int(z.get("leg_left",0))}/{int(zm.get("leg_left",1))}',872,438,10,INK)
            self.bar(872,451,118,int(z.get('leg_left',0)),max(1,int(zm.get('leg_left',1))),(224,112,93))
            self.label(f'PERNA DIR. {int(z.get("leg_right",0))}/{int(zm.get("leg_right",1))}',1000,438,10,INK)
            self.bar(1000,451,132,int(z.get('leg_right',0)),max(1,int(zm.get('leg_right',1))),(224,112,93))
            core_open=int(z.get('leg_left',0))<=0 and int(z.get('leg_right',0))<=0
            self.label('NÚCLEO DE MAGMA EXPOSTO' if core_open else 'NÚCLEO DE MAGMA BLOQUEADO',872,478,10,GOLD if core_open else MUTED)
        elif boss and species == 'kael':
            z=b.get('zone_hp',{}); zm=b.get('zone_hp_max',{})
            self.label(f'COPA {int(z.get("crown",0))}/{int(zm.get("crown",1))}',872,438,10,INK)
            self.bar(872,451,260,int(z.get('crown',0)),max(1,int(zm.get('crown',1))),(89,145,74))
            crown_ratio=max(0.0,min(1.0,int(z.get('crown',0))/max(1,int(zm.get('crown',1)))))
            atk=1+int(round((spec['attack'][1]-1)*crown_ratio)); self.label(f'ATQ ATUAL {max(1,atk)}',872,478,10,GOLD)
        elif boss and species == 'ounull':
            self.label('AFogamento ativa risco de recuperação',872,438,10,(83,181,196) if b.get('player_drowning_pending') else MUTED)
            self.label('ATAQUES DE MEMÓRIA CURAM OUNULL',872,459,10,INK)
            self.label('DOBRO ENQUANTO HOUVER AFOGAMENTO',872,478,9,MUTED)
        if boss and scanned and species not in ('fagor','kael','ounull'):
            mana_now = int(b.get('mana', spec.get('mana_max', 0)))
            mana_max = max(1, int(b.get('mana_max', spec.get('mana_max', 1))))
            self.label('MANA', 872, 458, 10, GOLD); self.bar(916,459,216,mana_now,mana_max,TEAL); self.label(f'{mana_now}/{mana_max}',1015,478,10,INK)
        elif scanned:
            mana_now = int(b.get('mana', spec.get('mana_max', 0)))
            mana_max = max(1, int(b.get('mana_max', spec.get('mana_max', 1))))
            self.label('MANA', 872, 439, 10, GOLD)
            self.bar(916, 440, 216, mana_now, mana_max, TEAL)
            self.label(f'{mana_now}/{mana_max}', 1015, 459, 10, INK)

        enabled = self.phase == 'choose'
        lo, hi, _, _, _, _, _, _ = self.state._player_attack_profile('basic')
        card_y, card_w, card_h, gap = 535, 210, 118, 10
        combat_slots=[]
        for idx in range(4):
            rect=pygame.Rect(30 + idx*(card_w + gap), card_y, card_w, card_h)
            if idx == 0:
                self.card_frame(rect, 'Comum')
                self.label('1', rect.x+12, rect.y+9, 12, GOLD)
                self.label('RAIO DE PLASMA', rect.x+12, rect.y+31, 13, INK)
                self.label(f'{lo}–{hi} ATQ Skill', rect.x+12, rect.y+56, 11, TEAL)
                self.label('SEM CUSTO', rect.x+12, rect.y+80, 9, MUTED)
                self.buttons.append((rect, lambda: self.choose('basic'), enabled))
                continue
            slot_idx=idx-1; cid=self.state.slots[slot_idx]
            can_use=False
            if cid:
                try:
                    card,variant_data,_,_=self.state.card_data(cid)
                    can_use=enabled and self.state.memory >= int(card.get('cost',0))
                except ValueError:
                    card=None; variant_data=None; cid=None
            else:
                card=None; variant_data=None
            rarity=card.get('rarity','Comum') if card else 'Comum'
            self.card_frame(rect, rarity)
            self.label(str(idx+1), rect.x+12, rect.y+9, 12, self.rarity_styles[rarity]['accent'])
            if not cid or not card:
                self.label('SLOT VAZIO', rect.x+12, rect.y+34, 13, MUTED)
                self.label('EQUIPAR CARTA', rect.x+12, rect.y+61, 10, EDGE)
                self.buttons.append((rect, lambda c=None: None, False))
                continue
            self.label(self.fit_text(format_card_name(card['name'])+(variant_data['label'] if variant_data else ''),13,170), rect.x+12, rect.y+30, 13, INK if can_use else MUTED)
            art=pygame.Rect(rect.x+12, rect.y+51, 74, 55)
            pygame.draw.rect(self.canvas,(7,15,22),art,border_radius=5)
            pygame.draw.rect(self.canvas,self.rarity_styles[rarity]['edge'],art,1,border_radius=5)
            self.draw_element_symbol(card.get('type'), (art.right-10, art.y+10), 5)
            spr=self.sprites.get((card.get('species'),0))
            if spr:
                scale=min((art.width-10)/max(1,spr.get_width()),(art.height-8)/max(1,spr.get_height()))
                im=pygame.transform.scale(spr,(max(1,int(spr.get_width()*scale)),max(1,int(spr.get_height()*scale))))
                self.canvas.blit(im,(art.centerx-im.get_width()/2,art.centery-im.get_height()/2+2))
            self.label(f'MEM {card.get("cost",0)}', rect.x+96, rect.y+56, 9, TEAL if can_use else MUTED)
            self.label(f'DANO {card.get("damage",(0,0))[0]}–{card.get("damage",(0,0))[1]}', rect.x+96, rect.y+76, 9, TEAL if can_use else MUTED)
            self.buttons.append((rect, lambda c=cid: self.choose(c), can_use))
            combat_slots.append((rect,cid,card))

        # Utilidades discretas no canto inferior direito.
        util_x=1018
        self.button((util_x,545,147,34),f'KIT [{self.state.inventory.get("Kit",0)}]',lambda:self.choose('kit'),enabled and self.state.inventory.get('Kit',0)>0 and self.state.hp<self.state.max_hp)
        self.button((util_x,587,147,34),'FUGIR [6]',lambda:self.choose('flee'),enabled)

        # Tooltip compacto por hover, mantendo a HUD principal limpa.
        hover_card=next(((rect,cid,card) for rect,cid,card in combat_slots if rect.collidepoint(self.mouse())),None)
        if hover_card and enabled:
            rect,cid,card=hover_card
            tip_w=585; tip_h=132; tx=max(24,min(830-tip_w,rect.centerx-tip_w//2)); ty=391
            self.box((tx,ty,tip_w,tip_h),(7,15,22),TEAL)
            style=self.rarity_styles.get(card.get('rarity','Comum'),self.rarity_styles['Comum'])
            self.label(self.fit_text(card.get('name','Carta'),15,360),tx+14,ty+10,15,style['accent'])
            self.wrap(card.get('description','Sem descrição.'),tx+14,ty+34,557,10,INK,13)
            unique_id=getattr(self.state,'gauntlet_special_slot',None)
            if self.state.is_unique_card(unique_id):
                u=self.state.unique_cards.get(unique_id,{})
                element=u.get('element')
                variant=u.get('variant','normal'); mult=UNIQUE_VARIANT_MULTIPLIERS.get(variant,1.0)
                self.label('EFEITOS DA CARTA ÚNICA',tx+14,ty+74,9,GOLD)
                effect_lines=[self._unique_buff_text(b,mult) for b in u.get('buffs',[]) if isinstance(b,dict)]
                momentum=u.get('momentum')
                if momentum in UNIQUE_MOMENTUM_DEFS:
                    effect_lines.append('Momentum - '+UNIQUE_MOMENTUM_DEFS[momentum]['description'].format(type=element))
                self.wrap(' • '.join(effect_lines) if effect_lines else 'Nenhum efeito aplicado.',tx+14,ty+90,557,9,MUTED,12)

    def select_battle_target(self, target_id):
        if self.state.set_battle_target(target_id):
            self.selected_battle_target = target_id
            names = {t['id']:t['name'] for t in self.state.battle_targets()}
            self.set_message('Alvo selecionado: ' + names.get(target_id, target_id) + '.')

    def card_frame(self, rect, rarity):
        style = self.rarity_styles.get(rarity, self.rarity_styles['Comum'])
        box = pygame.Rect(rect)
        pygame.draw.rect(self.canvas, style['fill'], box, border_radius=10)
        pygame.draw.rect(self.canvas, style['edge'], box, style['width'], border_radius=10)
        # Cada tier recebe uma linguagem visual própria sem depender de arte futura.
        if rarity in ('Rara', 'Mítica', 'Lendária', 'Única'):
            for inset in (7, 11) if rarity in ('Lendária', 'Única') else (8,):
                pygame.draw.rect(self.canvas, style['edge'], box.inflate(-inset*2, -inset*2), 1, border_radius=7)
        if rarity in ('Mítica', 'Lendária', 'Única'):
            pts = [(box.left+16, box.top+2), (box.left+28, box.top+2), (box.left+22, box.top+11)]
            pygame.draw.polygon(self.canvas, style['accent'], pts)
            pts2 = [(box.right-16, box.bottom-2), (box.right-28, box.bottom-2), (box.right-22, box.bottom-11)]
            pygame.draw.polygon(self.canvas, style['accent'], pts2)

    ELEMENT_COLORS = {
        'Fogo': (232, 105, 58), 'Água': (102, 205, 224), 'Planta': (96, 177, 100),
        'Terra': (189, 156, 103), 'Metal': (177, 190, 198), 'Elétrico': (106, 210, 237),
        'Luz': (238, 227, 157), 'Trevas': (137, 97, 180),
    }

    def draw_element_symbol(self, element, center, size, glow=False):
        """Desenha a badge pixel-art oficial do elemento, sem o rótulo textual.

        A arte é escalada com nearest-neighbor para preservar os pixels. Se algum
        asset não estiver disponível, mantém-se o símbolo procedural anterior como
        fallback para não quebrar builds ou instalações antigas.
        """
        if element not in self.ELEMENT_COLORS:
            return
        cx, cy = int(center[0]), int(center[1])
        r = max(3, int(size))
        color = self.ELEMENT_COLORS[element]
        badge = getattr(self, 'element_badges', {}).get(element)
        if badge is not None:
            target = max(6, int(r * 2))
            scale = min(target / max(1, badge.get_width()), target / max(1, badge.get_height()))
            w = max(1, int(round(badge.get_width() * scale)))
            h = max(1, int(round(badge.get_height() * scale)))
            scaled = pygame.transform.scale(badge, (w, h))
            if glow:
                glow_layer = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
                halo_radius = max(r + 2, int(target * 0.60))
                pygame.draw.circle(glow_layer, (*color, 42), (cx, cy), halo_radius)
                self.canvas.blit(glow_layer, (0, 0))
            self.canvas.blit(scaled, (cx - w // 2, cy - h // 2))
            return

        # Fallback procedural para instalações que ainda não carregaram os assets.
        layer = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        def poly(points, fill=color): pygame.draw.polygon(layer, fill, [(int(x),int(y)) for x,y in points])
        def line(points, width=max(1,r//7), fill=color): pygame.draw.lines(layer, fill, False, [(int(x),int(y)) for x,y in points], width)
        if element == 'Fogo':
            poly([(cx,cy+r),(cx-r//2,cy+r//3),(cx-r//4,cy-r//5),(cx,cy-r),(cx+r//4,cy-r//3),(cx+r//2,cy+r//5)])
            poly([(cx,cy+r//2),(cx-r//5,cy),(cx,cy-r//2),(cx+r//5,cy)], (255,232,181))
        elif element == 'Água':
            poly([(cx,cy-r),(cx-r//2,cy),(cx-r//3,cy+r//2),(cx,cy+r),(cx+r//3,cy+r//2),(cx+r//2,cy)])
            pygame.draw.circle(layer,(221,249,255),(cx-r//6,cy-r//5),max(1,r//8))
        elif element == 'Planta':
            poly([(cx,cy+r),(cx-r//2,cy+r//4),(cx-r//3,cy-r//2),(cx+r//4,cy-r),(cx+r//2,cy-r//4),(cx+r//2,cy+r//4)])
            line([(cx,cy+r//3),(cx+r//5,cy-r//3)],max(1,r//10),(226,255,220))
        elif element == 'Terra':
            poly([(cx-r,cy+r//2),(cx-r//3,cy-r//3),(cx,cy+r//5),(cx+r//3,cy-r//2),(cx+r,cy+r//2)])
            line([(cx-r//2,cy+r//3),(cx,cy),(cx+r//2,cy+r//3)],max(1,r//10),(230,207,170))
        elif element == 'Metal':
            pygame.draw.circle(layer,color,(cx,cy),r,max(2,r//4)); pygame.draw.circle(layer,(24,32,38),(cx,cy),max(2,r//3))
            for i in range(8):
                a=math.tau*i/8; p1=(cx+int(math.cos(a)*(r+2)),cy+int(math.sin(a)*(r+2))); p2=(cx+int(math.cos(a)*(r+r//4)),cy+int(math.sin(a)*(r+r//4))); pygame.draw.line(layer,color,p1,p2,max(2,r//5))
            pygame.draw.circle(layer,(235,241,243),(cx,cy),max(1,r//8))
        elif element == 'Elétrico':
            poly([(cx+r//5,cy-r),(cx-r//4,cy-r//8),(cx-r//7,cy-r//8),(cx-r//2,cy+r),(cx+r//4,cy+r//8),(cx+r//7,cy+r//8)])
        elif element == 'Luz':
            pts=[]
            for i in range(16):
                a=-math.pi/2+math.tau*i/16; rr=r if i%2==0 else max(2,r//2); pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
            poly(pts); pygame.draw.circle(layer,(255,249,218),(cx,cy),max(1,r//3))
        elif element == 'Trevas':
            pygame.draw.circle(layer,color,(cx,cy),r); pygame.draw.circle(layer,(10,15,21),(cx+r//3,cy-r//4),int(r*.82)); pygame.draw.circle(layer,(198,166,225),(cx-r//3,cy+r//3),max(1,r//10))
        if glow:
            gl=pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA); gc=(*color, 90); pygame.draw.circle(gl,gc,(cx,cy),max(2,int(r*1.45))); self.canvas.blit(gl,(0,0))
        self.canvas.blit(layer,(0,0))

    def card_bonus_lines(self, attrs):
        labels = (
            ('attack_pct', 'ATQ', lambda v: f'+{float(v):.1f}%'),
            ('precision', 'PREC', lambda v: f'+{int(v)}'),
            ('defense', 'DEF', lambda v: f'+{int(v)}'),
            ('amp', 'AMP', lambda v: f'+{float(v):.2f}%'),
            ('crit_rate', 'Taxa Crítica', lambda v: f'+{float(v):.2f}%'),
            ('crit_damage', 'Dano Crítico', lambda v: f'+{float(v):.2f}x'),
            ('min_damage_bonus', 'DANO MÍN.', lambda v: f'+{int(v)}'),
        )
        return [f'{label} {fmt(attrs.get(key, 0))}' for key, label, fmt in labels if float(attrs.get(key, 0)) != 0]

    def _card_variant_counts(self, cid):
        counts = {variant: 0 for variant in ('normal', 'plus', 'plusplus')}
        for inst in self.state.card_instances(cid):
            try:
                variant = self.state.card_parts(inst)[1]
            except ValueError:
                continue
            if variant in counts:
                counts[variant] += 1
        return counts

    def _unique_buff_text(self, buff, multiplier=1.0):
        kind = buff.get('kind') if isinstance(buff, dict) else buff
        data = UNIQUE_BUFF_DEFS.get(kind)
        if not data:
            return 'Bônus desconhecido'
        value = float(data['value']) * float(multiplier)
        label = data['label']
        if kind == 'attack':
            return f'+{value:g}% ATQ por carta do tipo'
        if kind == 'min_damage':
            return f'+{int(round(value))} {label} por carta do tipo'
        if kind in ('crit_rate', 'amp'):
            return f'+{value:g}% {label} por carta do tipo'
        if kind == 'crit_damage':
            return f'+{value:g}% {label} por carta do tipo'
        return label

    def _spare_regular_cards(self):
        items=[]
        for cid in self.state.crafted:
            if cid in self.state.slots or self.state.is_unique_card(cid):
                continue
            try:
                card, variant_data, base_id, variant = self.state.card_data(cid)
            except ValueError:
                continue
            items.append((cid, card, variant_data, base_id, variant))
        rarity_order = {rarity: idx for idx, rarity in enumerate(CARD_RARITIES)}
        items.sort(key=lambda item: (rarity_order.get(item[1].get('rarity','Comum'),0), item[1].get('type',''), format_card_name(item[1].get('name','')).casefold(), item[4], item[0]))
        return items

    def album(self):
        self.panel_header('CARTAS', 'Coleção, fabricação e o Slot Único da Manopla.')
        nav = (
            ('COLEÇÃO', 'collection'),
            ('FABRICAÇÃO', 'craft'),
            ('CARTAS ÚNICAS', 'unique'),
        )
        for x, (label, section) in zip((35, 220, 405), nav):
            active = self.album_section == section
            self.button((x, 96, 170 if section != 'unique' else 190, 38), label,
                        lambda sec=section: (setattr(self, 'album_section', sec), setattr(self, 'album_page', 0), setattr(self, 'unique_card_source', None), self.ui_scroll.__setitem__('unique_card_craft', 0)), True,
                        'ATIVA' if active else None)
        self.button((760, 96, 190, 38), 'MANOPLA', lambda: self.open_panel('gauntlet'), True)
        self.box((965, 96, 200, 65))
        equipped_unique = bool(getattr(self.state, 'gauntlet_special_slot', None))
        available_regular = sum(1 for inst in self.state.crafted if inst not in self.state.slots and not self.state.is_unique_card(inst))
        owned_unique = sum(1 for inst in self.state.crafted if self.state.is_unique_card(inst) and inst != getattr(self.state,'gauntlet_special_slot',None))
        self.label(f'DISPONÍVEIS: {available_regular + owned_unique}', 985, 110, 13, TEAL)
        self.label(f'ÚNICAS: {owned_unique + (1 if equipped_unique else 0)}', 985, 133, 11, MUTED)
        self.label('SLOT ÚNICO: ' + ('OCUPADO' if equipped_unique else 'LIVRE'), 985, 149, 10, GOLD if equipped_unique else MUTED)

        if self.album_section == 'craft':
            self.card_crafting_view()
        elif self.album_section == 'unique':
            self.unique_card_crafting_view()
        else:
            self.card_collection_view()

    def _draw_scroll_text_box(self, rect, text, key, font_size=10, color=MUTED, leading=14, border=EDGE):
        rect = pygame.Rect(rect)
        lines=[]
        font=self.font(font_size)
        words=str(text or '').split()
        line=''
        max_w=max(1,rect.width-17)
        for word in words:
            trial=word if not line else line+' '+word
            if font.size(trial)[0] <= max_w:
                line=trial
            else:
                if line: lines.append(line)
                line=word
        if line: lines.append(line)
        max_scroll=max(0,len(lines)*leading-rect.height+4)
        scroll=max(0,min(int(self.ui_scroll.get(key,0)),max_scroll)); self.ui_scroll[key]=scroll
        self.box(rect,(7,15,22),border)
        viewport=rect.inflate(-8,-6)
        self.canvas.set_clip(viewport)
        y=viewport.y-scroll
        for line in lines:
            self.label(line,viewport.x,y,font_size,color); y+=leading
        self.canvas.set_clip(None)
        sb=pygame.Rect(rect.right-8,rect.y+5,5,max(1,rect.height-10))
        self._draw_scrollbar(sb,scroll,max_scroll); self._register_scrollbar(key,sb,scroll,max_scroll)
        return rect.bottom

    def card_collection_view(self):
        rarity_order = {rarity: idx for idx, rarity in enumerate(CARD_RARITIES)}
        # A COLEÇÃO registra apenas cartas regulares descobertas.
        # Cartas Únicas pertencem exclusivamente ao fluxo de Carta Única/Manopla.
        cards=[(cid, card, 'regular') for cid, card in CARDS.items() if cid in self.state.known_cards]
        cards=[item for item in cards if item[1].get('rarity') in CARD_RARITIES]
        cards.sort(key=lambda item: (rarity_order.get(item[1].get('rarity','Comum'),0), item[1].get('type',''), format_card_name(item[1].get('name','')).casefold(), item[0]))
        page_count=max(1,(len(cards)+2)//3)
        self.album_page=max(0,min(self.album_page,page_count-1))
        shown=cards[self.album_page*3:self.album_page*3+3]
        for local_i,(cid,c,kind) in enumerate(shown):
            x=(25,405,785)[local_i]
            rarity=c.get('rarity','Comum'); style=self.rarity_styles.get(rarity,self.rarity_styles['Comum'])
            self.card_frame((x,180,365,472),rarity)
            self.label(self.fit_text(rarity.upper(),10,125),x+22,193,10,style['accent'])
            self.label(self.fit_text(format_card_name(c.get('name','Carta')),18,318),x+20,222,18,INK)
            self.label(f"TIPO: {c.get('type','-').upper()}", x+20, 252, 10, GOLD)
            art_box=pygame.Rect(x+24,278,317,102)
            pygame.draw.rect(self.canvas,(7,15,22),art_box,border_radius=6)
            pygame.draw.rect(self.canvas,style['edge'],art_box,1,border_radius=6)
            if c.get('species'):
                self.actor(c['species'],x+182,365,1.85)
            self.draw_element_symbol(c.get('type'), (x+315,292), 10)
            self._draw_scroll_text_box((x+20,390,315,150), c.get('description',''), f'card_effect_{local_i}', 10, INK, 14)
            self.label(f'MEM {c.get("cost",0)}  |  DANO {c.get("damage",(0,0))[0]}–{c.get("damage",(0,0))[1]}',x+20,548,10,TEAL)
            bonus_lines=self.card_bonus_lines(c.get('attributes',{}))
            if bonus_lines:
                self._draw_scroll_text_box((x+20,565,315,43), 'BÔNUS: '+'  |  '.join(bonus_lines), f'card_bonus_{local_i}', 9, GOLD, 12)
            counts=self._card_variant_counts(cid)
            available=sum(1 for inst in self.state.card_instances(cid) if inst not in self.state.slots)
            self.label(f'N {counts["normal"]}   + {counts["plus"]}   ++ {counts["plusplus"]}',x+20,590,9,MUTED)
            self.label(f'DISPONÍVEIS: {available}',x+190,590,9,TEAL if available else MUTED)
        if not cards:
            self.label('NENHUMA CARTA DESCOBERTA',420,350,20,MUTED)
        self.label(f'PÁGINA {self.album_page+1}/{page_count}',480,692,12,TEAL)
        self.button((35,680,170,38),'‹ ANTERIOR',lambda:setattr(self,'album_page',self.album_page-1),self.album_page>0)
        self.button((995,680,170,38),'PRÓXIMA ›',lambda:setattr(self,'album_page',self.album_page+1),self.album_page<page_count-1)

    def card_crafting_view(self):
        self.label('FABRICAÇÃO DE CARTAS', 35, 155, 17, GOLD)
        self.label('Somente cartas já descobertas aparecem aqui.', 270, 159, 11, MUTED)
        cards=[(cid,data) for cid,data in CARDS.items() if cid in self.state.known_cards and data.get('recipe') and data.get('craftable') is not False]
        rarity_order={rarity:idx for idx,rarity in enumerate(CARD_RARITIES)}
        cards.sort(key=lambda item:(rarity_order.get(item[1].get('rarity','Comum'),0),item[1].get('type',''),format_card_name(item[1].get('name','')).casefold(),item[0]))
        per_page=4; page_count=max(1,(len(cards)+per_page-1)//per_page)
        self.album_page=max(0,min(self.album_page,page_count-1))
        page_cards=cards[self.album_page*per_page:(self.album_page+1)*per_page]
        for i,(cid,data) in enumerate(page_cards):
            y=180+i*121
            rarity=data.get('rarity','Comum')
            style=self.rarity_styles.get(rarity,self.rarity_styles['Comum'])
            self.box((35,y,1130,110),style['fill'],style['edge'])
            pygame.draw.rect(self.canvas,style['accent'],(35,y,5,110),border_radius=2)
            self.label(self.fit_text(format_card_name(data['name']),16,340),54,y+11,16,INK)
            self.label(f"{rarity} • {data.get('type','-')} • MEM {data.get('cost',0)} • DANO {data.get('damage',(0,0))[0]}–{data.get('damage',(0,0))[1]}",54,y+35,10,style['accent'])
            self.draw_element_symbol(data.get('type'), (440,y+21), 6)
            self._draw_scroll_text_box((54,y+55,385,45),data.get('description',''),f'craft_effect_{i}',9,MUTED,12)
            recipe=list(data.get('recipe',{}).items())
            rx=480
            for idx,(name,qty) in enumerate(recipe[:3]):
                owned=int(self.state.essence_total()) if name=='Essência' else int(self.state.inventory.get(name,0)); self.label(self.fit_text(name,9,155),rx+(idx%3)*150,y+16,9,INK); self.label(f'{owned}/{qty}',rx+(idx%3)*150,y+34,9,TEAL if owned>=qty else (224,112,93))
            if len(recipe)>3:
                for idx,(name,qty) in enumerate(recipe[3:6]):
                    owned=int(self.state.essence_total()) if name=='Essência' else int(self.state.inventory.get(name,0)); self.label(self.fit_text(name,9,155),rx+(idx%3)*150,y+55,9,INK); self.label(f'{owned}/{qty}',rx+(idx%3)*150,y+73,9,TEAL if owned>=qty else (224,112,93))
            conflict=self.state.missions.get('faction_conflict',{})
            is_conflict=data.get('acquisition')=='faction_conflict'
            enough_materials=all((self.state.essence_total() if n=='Essência' else int(self.state.inventory.get(n,0)))>=q for n,q in data.get('recipe',{}).items())
            acquisition_ok=(conflict.get('status')=='completed' and conflict.get('winner_card')==cid) if is_conflict else (cid in self.state.known_cards)
            can=bool(not self.state.battle and enough_materials and acquisition_ok)
            subtitle = None
            if not enough_materials:
                subtitle = 'MATERIAIS INSUFICIENTES'
            elif not acquisition_ok:
                subtitle = 'CARTA AINDA BLOQUEADA'
            self.button((980,y+51,165,40),'FABRICAR',lambda c=cid:self._craft_card_ui(c),can,subtitle)
        if not page_cards:
            self.label('NENHUMA CARTA DISPONÍVEL PARA FABRICAÇÃO',365,360,18,MUTED)
        self.label(f'PÁGINA {self.album_page+1}/{page_count}',500,675,12,TEAL)
        self.button((35,665,170,38),'‹ ANTERIOR',lambda:setattr(self,'album_page',self.album_page-1),self.album_page>0)
        self.button((995,665,170,38),'PRÓXIMA ›',lambda:setattr(self,'album_page',self.album_page+1),self.album_page<page_count-1)

    def unique_card_crafting_view(self):
        self.label('CRAFT DE CARTAS ÚNICAS', 35, 155, 17, GOLD)
        self.box((35,180,620,475),(7,15,22),EDGE)
        self.label('CARTAS SOBRESSALENTES',58,202,13,TEAL)
        self.label('Escolha a carta elemental que será consumida.',270,204,10,MUTED)
        items=self._spare_regular_cards(); view=pygame.Rect(58,232,574,385); row_h=70
        max_scroll=max(0,len(items)*row_h-view.height)
        self.ui_scroll['unique_card_craft']=max(0,min(self.ui_scroll.get('unique_card_craft',0),max_scroll))
        selected=self.unique_card_source
        self.canvas.set_clip(view)
        y=view.y-int(self.ui_scroll['unique_card_craft'])
        for cid,card,variant_data,base_id,variant in items:
            rect=pygame.Rect(view.x,y,558,60)
            chosen=cid==selected
            self.box(rect,(17,35,38) if chosen else (12,22,29),TEAL if chosen else EDGE)
            self.label(self.fit_text(format_card_name(card['name'])+variant_data['label'],14,270),rect.x+12,rect.y+8,14,INK)
            self.label(f"{card.get('type','-')} • {card.get('rarity','Comum')} • {variant.upper()}",rect.x+12,rect.y+32,10,self.rarity_styles.get(card.get('rarity','Comum'),self.rarity_styles['Comum'])['accent'])
            self.label('SELECIONADA' if chosen else 'USAR',rect.right-95,rect.y+21,9,TEAL if chosen else MUTED)
            self.buttons.append((rect,lambda inst=cid:setattr(self,'unique_card_source',inst),True)); y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((638,232,9,385),self.ui_scroll['unique_card_craft'],max_scroll)
        self._register_scrollbar('unique_card_craft',(638,232,9,385),self.ui_scroll['unique_card_craft'],max_scroll)
        self.box((680,180,485,475),(7,15,22),EDGE)
        essence=int(self.state.essence_total()); self.label('ESSÊNCIAS',708,202,13,GOLD); self.label(f'{essence:,}'.replace(',', '.'),708,226,28,TEAL if essence>=UNIQUE_CARD_ESSENCE_COST else (224,112,93)); self.label(f'CUSTO: {UNIQUE_CARD_ESSENCE_COST:,}'.replace(',', '.'),880,233,11,MUTED)
        self.label('PROBABILIDADE DO RESULTADO',708,278,11,GOLD)
        self.label('1 buff  75%    |    2 buffs  24%    |    3 buffs  1%',708,300,10,INK)
        self.label('VARIANTES',708,332,11,GOLD); self.label('Normal 95%   |   + 4,5%   |   ++ 0,5%',708,370,10,INK)
        self.label('BUFFS POSSÍVEIS',708,402,11,GOLD)
        y=425
        for kind,data in UNIQUE_BUFF_DEFS.items():
            label=data['label']; value=data['value']; value_text=f'+{int(value)}' if kind in ('attack','min_damage') else f'+{value:g}%'
            self.label(f'{value_text} {label} por carta do tipo',708,y,10,INK); self.label(f'{data["chance"]*100:g}%',1072,y,10,MUTED); y+=22
        self.label('SELECIONADA',708,528,10,GOLD)
        selected_card=None
        if selected:
            try: selected_card=self.state.card_data(selected)[0]
            except ValueError: selected_card=None
        if selected_card:
            self.label(self.fit_text(format_card_name(selected_card['name']),13,280),708,548,13,INK)
            self.label(f"TIPO: {selected_card.get('type','-')}",708,570,10,TEAL)
            self.label('1 carta + 2000 Essências → Carta Única',708,594,10,MUTED)
        else:
            self.label('Selecione uma carta elemental sobressalente.',708,548,11,MUTED)
        can=bool(selected_card) and essence>=UNIQUE_CARD_ESSENCE_COST and not self.state.battle
        unique_subtitle = 'ESSÊNCIAS INSUFICIENTES' if essence < UNIQUE_CARD_ESSENCE_COST else None
        self.button((895,610,230,40),'CRAFTAR CARTA ÚNICA',self.craft_unique_card_ui,can,unique_subtitle)

    def craft_unique_card_ui(self):
        source=self.unique_card_source
        if self.state.battle:
            self._show_craft_notice('Não é possível fabricar Cartas Únicas durante o combate.')
            return
        if not source:
            self._show_craft_notice('Selecione uma carta elemental sobressalente.')
            return
        if source not in self.state.crafted or source in self.state.slots or self.state.is_unique_card(source):
            self._show_craft_notice('A carta-fonte precisa estar na Pool de cartas e não pode ser Única.')
            return
        result,msg=self.state.craft_unique_card(source)
        self.set_message(msg)
        if result:
            self.unique_gacha_card_id=result['card_id']
            self.unique_gacha_kind=result['buff_count']
            self.unique_gacha_until=self.frame+5.8
            self.unique_card_source=None
            self.ui_scroll['unique_card_craft']=0
            self.craft_notice=None
            self.craft_notice_until=0.0
            self.checkpoint()
        else:
            self._show_craft_notice(msg)

    def remove_selected_card(self):
        ok, message = self.state.remove_card(self.selected_slot)
        self.set_message(message)
        if ok:
            self.checkpoint()

    def draw_slot_card(self, rect, cid, slot_label, rarity_override=None):
        """Carta compacta para a tela da Manopla, sem estourar o cartão."""
        rect = pygame.Rect(rect)
        rarity = rarity_override or 'Comum'
        card = None
        variant_data = None
        if cid:
            try:
                card, variant_data, _, _ = self.state.card_data(cid)
                rarity = card.get('rarity', rarity)
            except ValueError:
                cid = None
        self.card_frame(rect, rarity)
        accent = self.rarity_styles[rarity]['accent']
        self.label(self.fit_text(slot_label, 11, rect.width-24), rect.x+12, rect.y+9, 11, accent)
        if not cid or not card:
            self.label('VAZIO', rect.x+14, rect.y+43, 18, EDGE)
            return
        self.label(self.fit_text(card['name'] + (variant_data['label'] if variant_data else ''), 13, 220), rect.x+12, rect.y+28, 13, INK)
        art_box = pygame.Rect(rect.x+12, rect.y+50, 118, rect.height-62)
        pygame.draw.rect(self.canvas, (7,15,22), art_box, border_radius=5)
        pygame.draw.rect(self.canvas, self.rarity_styles[rarity]['edge'], art_box, 1, border_radius=5)
        if rarity == 'Única':
            self.draw_element_symbol(card.get('type'), art_box.center, 12, glow=True)
        else:
            self.draw_element_symbol(card.get('type'), (art_box.right-10, art_box.y+10), 7)
        spr = self.sprites.get((card['species'], 0))
        if spr:
            scale = min((art_box.width-12)/max(1,spr.get_width()), (art_box.height-8)/max(1,spr.get_height()))
            im = pygame.transform.scale(spr, (max(1,int(spr.get_width()*scale)), max(1,int(spr.get_height()*scale))))
            self.canvas.blit(im, (art_box.centerx-im.get_width()/2, art_box.centery-im.get_height()/2+2))
        info_x = art_box.right + 12
        if self.state.is_unique_card(cid):
            self.label(f'TIPO {card.get("type","-")}', info_x, rect.y+55, 10, TEAL)
            unique_data=self.state.unique_cards.get(cid,{})
            variant=self.state.unique_card_parts(cid)[1]
            mult=UNIQUE_VARIANT_MULTIPLIERS.get(variant,1.0)
            for idx,buff in enumerate(unique_data.get('buffs',[])[:2]):
                self.label(self.fit_text(self._unique_buff_text(buff,mult), 9, rect.right-info_x-10), info_x, rect.y+73+idx*17, 9, GOLD)
            if unique_data.get('momentum') in UNIQUE_MOMENTUM_DEFS:
                self.label('Momentum', info_x, rect.y+91, 8, GOLD)
        else:
            self.label(f'MEM {card["cost"]}', info_x, rect.y+55, 10, TEAL)
            self.label(f'DANO {card["damage"][0]}–{card["damage"][1]}', info_x, rect.y+73, 10, TEAL)
            bonus = self.card_bonus_lines(card.get('attributes',{}))
            if bonus:
                self.label(self.fit_text(' | '.join(bonus[:2]), 10, rect.right-info_x-10), info_x, rect.y+91, 10, GOLD)

    def draw_challenge_menu(self):
        if not self.challenge_menu_open or self.mode!='battle': return
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((4,9,13,220)); self.canvas.blit(ov,(0,0))
        x,y,w,h=185,150,830,500; self.box((x,y,w,h),(8,17,24),TEAL)
        self.label('DESAFIOS DE COMBATE',x+35,y+28,24,GOLD)
        self.label('Escolha um objetivo opcional para este confronto.',x+35,y+65,12,MUTED)
        for i,c in enumerate(self.state.battle.get('challenge_offers',[])[:3]):
            ry=y+105+i*112; self.box((x+35,ry,w-70,94),(12,24,31),GOLD if c.get('premium') else EDGE)
            self.label(c.get('name','DESAFIO'),x+52,ry+12,13,TEAL)
            self.wrap(c.get('description',''),x+52,ry+37,520,10,INK,15)
            self.label(f'+{int(c.get("reward",0))} Essências',x+600,ry+18,11,GOLD)
            self.button((x+650,ry+45,130,34),'ATIVAR',lambda idx=i:self._activate_challenge(idx),True)
        self.button((x+650,y+400,130,34),'CANCELAR',lambda:setattr(self,'challenge_menu_open',False),True)

    def _activate_challenge(self,index):
        ok,msg=self.state.set_combat_challenge(index); self.set_message(msg); self.challenge_menu_open=False

    def gauntlet(self):
        from content import NEXUS_LEVEL_XP
        self.panel_header('MANOPLA', 'Configuração da Manopla V-7.')

        self.box((35,108,330,590),(7,15,22),EDGE)
        self.label('MANOPLA V-7',60,134,22,GOLD)
        self.draw_gear_piece('gauntlet',200,245,1.05,True)
        self.label('NEXUS',60,322,16,TEAL)
        level=int(self.state.gauntlet_nexus_level); xp=int(self.state.gauntlet_nexus_xp); max_level=max(NEXUS_LEVEL_XP); max_xp=NEXUS_LEVEL_XP[max_level]
        if level>=max_level:
            bar_value,bar_max=max_xp,max_xp; xp_text=f'XP {xp:,} / {max_xp:,}'.replace(',','.')
        else:
            target=NEXUS_LEVEL_XP.get(level+1,NEXUS_LEVEL_XP[2]); previous=0 if level<=1 else NEXUS_LEVEL_XP.get(level,0)
            bar_value=max(0,xp-previous); bar_max=max(1,target-previous); xp_text=f'XP {xp:,} / {target:,}'.replace(',','.')
        self.label(f'NÍVEL {level}',60,350,20,TEAL); self.bar(60,383,280,bar_value,bar_max,TEAL)
        self.label(self.fit_text(xp_text,10,280),60,401,10,MUTED); self.label('1 DANO = 1 XP',60,425,11,GOLD)
        self.label(f'{max_xp:,} XP ATÉ O NÍVEL {max_level}'.replace(',','.'),60,468,10,MUTED)
        self.button((60,500,280,38),'DOMÍNIO',lambda:self.set_mode('domain'),True)
        self.button((60,546,280,38),'ÁRVORE DO NEXUS',lambda:self.set_mode('gauntlet_nexus'),True)
        self.button((60,592,280,38),'CARTAS',lambda:self.open_panel('album'),True)
        self.button((60,638,280,38),'LOADOUTS',lambda:self.open_panel('loadouts'),True)

        self.box((390,108,775,310),(7,15,22),EDGE)
        self.label('CARTAS EQUIPADAS',415,134,20,GOLD)
        slot_positions=[(410,158),(790,158),(410,273),(790,273)]
        for i in range(3):
            rect=pygame.Rect(slot_positions[i][0],slot_positions[i][1],355,103); selected=i==self.selected_slot
            self.draw_slot_card(rect,self.state.slots[i],f'SLOT {i+1}'+(' • SELECIONADO' if selected else ''))
            if selected: pygame.draw.rect(self.canvas,TEAL,rect.inflate(4,4),2,border_radius=7)
            self.buttons.append((rect,lambda idx=i:self.open_card_picker(idx),True))
        special_rect=pygame.Rect(slot_positions[3][0],slot_positions[3][1],355,103)
        self.draw_slot_card(special_rect,getattr(self.state,'gauntlet_special_slot',None),'ESPECIAL / ÚNICA','Única')
        self.buttons.append((special_rect,lambda:self.open_card_picker('special'),True))

        manage=pygame.Rect(390,425,775,72); self.box(manage,(9,18,25),EDGE)
        self.label('GERENCIAR CARTAS',410,439,13,TEAL)
        current=self.state.slots[self.selected_slot] if 0<=self.selected_slot<3 else None; current_name=self.state.card_name(current) if current else 'Slot vazio'
        self.label(self.fit_text(f'Slot {self.selected_slot+1}: {current_name}',11,690),410,463,11,INK)
        self.label('Clique em um slot para escolher e equipar.',880,463,9,MUTED)

        self.box((390,510,775,188),(7,15,22),EDGE); self.label(RELIC_STONE_NAME.upper(),415,528,17,GOLD)
        stones=getattr(self.state,'gauntlet_stones',[None]*6); stones=(stones+[None]*6)[:6]
        for i in range(6):
            col,row=i%3,i//3; x,y=415+col*245,556+row*37; has_stone=bool(stones[i])
            pygame.draw.circle(self.canvas,GOLD if has_stone else EDGE,(x+10,y+10),8,2)
            self.label(f'{i+1}  '+('ENCAIXADA' if has_stone else 'VAZIO'),x+25,y+4,10,TEAL if has_stone else MUTED)

    def loadouts(self):
        self.panel_header('LOADOUTS', 'Configurações rápidas da Manopla.')
        self.box((55,110,1090,570),(7,15,22),EDGE)
        for i in range(3):
            y=145+i*160; data=getattr(self.state,'gauntlet_loadouts',[None]*3)[i]
            self.box((78,y,1042,130),(10,19,26),EDGE)
            self.label(f'LOADOUT {i+1}',96,y+16,16,GOLD)
            if data:
                labels=[]
                for cid in data.get('slots',[])[:3]: labels.append(self.state.card_name(cid) if cid else 'Vazio')
                self.label(self.fit_text(' • '.join(labels),11,700),96,y+48,11,INK)
                special=data.get('special')
                self.label('ÚNICA: '+(self.state.card_name(special) if special else 'Vazio'),96,y+76,10,MUTED)
                self.button((820,y+19,255,40),'EQUIPAR',lambda idx=i:self._equip_loadout(idx),True)
            else:
                self.label('Ainda não configurado.',96,y+52,11,MUTED)
            self.button((820,y+68,255,40),'SALVAR ATUAL',lambda idx=i:self._save_loadout(idx),True)
        self.button((78,640,260,40),'VOLTAR',self.close_panel,True)

    def _save_loadout(self,index):
        ok,msg=self.state.save_loadout(index); self.set_message(msg)
        if ok: self.checkpoint()

    def _equip_loadout(self,index):
        ok,msg=self.state.equip_loadout(index); self.set_message(msg)
        if ok: self.checkpoint()

    def draw_mini_card(self, rect, cid, slot_number):
        if not cid:
            self.card_frame(rect, 'Comum')
            self.label(f'SLOT {slot_number}', rect.x+14, rect.y+14, 12, MUTED)
            self.label('VAZIO', rect.x+80, rect.y+73, 20, EDGE)
            return
        try:
            card, variant_data, base_id, variant = self.state.card_data(cid)
        except ValueError:
            self.card_frame(rect, 'Comum')
            self.label(f'SLOT {slot_number} / INVÁLIDA', rect.x+12, rect.y+12, 11, (224,112,93))
            return
        rarity = card.get('rarity', 'Comum')
        self.card_frame(rect, rarity)
        style = self.rarity_styles[rarity]
        self.label(f'SLOT {slot_number}', rect.x+12, rect.y+10, 10, MUTED)
        self.label(variant_data['label'].strip().upper() or 'NORMAL', rect.right-56, rect.y+10, 10, style['accent'])
        self.label(format_card_name(card['name'])[:23], rect.x+12, rect.y+30, 14, INK)
        art_box = pygame.Rect(rect.x+12, rect.y+55, rect.width-24, 72)
        pygame.draw.rect(self.canvas, (7,15,22), art_box, border_radius=5)
        pygame.draw.rect(self.canvas, style['edge'], art_box, 1, border_radius=5)
        spr = self.sprites.get((card['species'], 0))
        if spr:
            max_w, max_h = art_box.width-18, art_box.height-12
            scale = min(max_w/max(1,spr.get_width()), max_h/max(1,spr.get_height()))
            im = pygame.transform.scale(spr, (max(1,int(spr.get_width()*scale)), max(1,int(spr.get_height()*scale))))
            self.canvas.blit(im, (art_box.centerx-im.get_width()/2, art_box.centery-im.get_height()/2+4))
        self.label(f'MEM {card["cost"]} | {card["damage"][0]}–{card["damage"][1]}', rect.x+12, rect.y+135, 10, TEAL)
        bonus = self.card_bonus_lines(card.get('attributes',{}))
        if bonus:
            self.label('  '.join(bonus[:2]), rect.x+12, rect.y+155, 9, GOLD)

    def card_picker(self):
        slot=self.card_picker_slot
        if slot is None: return
        special=slot=='special'; slot_label='SLOT ÚNICO' if special else f'SLOT {slot+1}'
        self.panel_header('SELECIONAR CARTA',f'Escolha a carta que ocupará o {slot_label}.')
        self.box((55,108,1090,556),(9,17,24),EDGE)
        self.label(slot_label,78,130,16,GOLD)
        self.label('Cartas disponíveis na Pool.',170,131,12,MUTED)
        self.button((915,121,205,36),'CANCELAR',self.close_card_picker,True)

        cards=[]; current=getattr(self.state,'gauntlet_special_slot',None) if special else self.state.slots[int(slot)]
        cards.append(('__empty__',None,None,None,None,current is None))
        for cid in self.state.crafted:
            if special and not self.state.is_unique_card(cid): continue
            if not special and self.state.is_unique_card(cid): continue
            try: card,variant_data,base_id,variant=self.state.card_data(cid)
            except ValueError: continue
            equipped=cid==current
            # Uma carta já equipada em outro slot não deve aparecer como opção válida.
            if not special and cid in self.state.slots and self.state.slots.index(cid)!=int(slot): continue
            cards.append((cid,card,variant_data,base_id,variant,equipped))
        rarity_order={rarity:idx for idx,rarity in enumerate(CARD_RARITIES)}
        cards[1:]=sorted(cards[1:],key=lambda item:(rarity_order.get(item[1].get('rarity','Comum'),0),item[1].get('type',''),format_card_name(item[1].get('name','')).casefold(),item[4],item[0]))

        # Lista enxuta à esquerda; painel de pré-visualização à direita.
        view=pygame.Rect(78,174,645,420)
        row_h=70
        max_scroll=max(0,len(cards)*row_h-view.height)
        self.ui_scroll['card_picker']=max(0,min(self.ui_scroll.get('card_picker',0),max_scroll))
        selected=self.card_picker_selection
        self.canvas.set_clip(view); y=view.y-int(self.ui_scroll['card_picker'])
        for cid,card,variant_data,base_id,variant,equipped in cards:
            rect=pygame.Rect(view.x,y,view.width-16,58); chosen=cid==selected
            if cid=='__empty__':
                self.box(rect,(17,35,38) if chosen else (12,22,29),TEAL if chosen else GOLD)
                self.label('SLOT VAZIO',rect.x+14,rect.y+8,14,INK)
                self.label('Desequipar e devolver a carta atual à Pool.',rect.x+14,rect.y+31,10,MUTED)
            else:
                rarity=card.get('rarity','Comum'); style=self.rarity_styles.get(rarity,self.rarity_styles['Comum'])
                self.box(rect,(18,37,39) if chosen or equipped else (15,25,32),TEAL if chosen else style['edge'])
                self.label(self.fit_text(format_card_name(card['name'])+variant_data['label'],14,350),rect.x+14,rect.y+7,14,INK)
                self.label(f'{rarity} • {card.get("type","-")} • '+('Carta Única' if special else f'MEM {card["cost"]} • DANO {card["damage"][0]}–{card["damage"][1]}'),rect.x+14,rect.y+30,10,style['accent'])
                self.draw_element_symbol(card.get('type'),(rect.right-120,rect.y+29),6)
                status='SELECIONADA' if chosen else ('ATUAL' if equipped else 'DISPONÍVEL')
                self.label(status,rect.right-100,rect.y+20,9,TEAL if chosen else (GOLD if equipped else MUTED))
            self.buttons.append((rect,lambda inst=cid:self.select_card_for_picker(inst),True)); y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((705,174,9,420),self.ui_scroll['card_picker'],max_scroll)
        self._register_scrollbar('card_picker',(705,174,9,420),self.ui_scroll['card_picker'],max_scroll)

        # Pré-visualização da carta escolhida.
        preview=pygame.Rect(742,174,364,420)
        self.box(preview,(7,15,22),EDGE)
        self.label('PRÉ-VISUALIZAÇÃO',760,192,14,TEAL)
        if not selected:
            self.label('Selecione uma carta.',760,236,12,MUTED)
        elif selected=='__empty__':
            self.label('SLOT VAZIO',760,236,20,GOLD)
            self.wrap('O slot ficará livre e a carta atualmente equipada retornará à Pool.',760,274,315,11,INK,16)
        else:
            try:
                card,variant_data,base_id,variant=self.state.card_data(selected)
            except ValueError:
                card=None; variant_data=None; base_id=None; variant='normal'
            if card:
                rarity=card.get('rarity','Comum'); style=self.rarity_styles.get(rarity,self.rarity_styles['Comum'])
                self.card_frame((760,215,150,215),rarity)
                self.label(self.fit_text(rarity.upper(),9,110),772,227,9,style['accent'])
                art=pygame.Rect(772,254,126,74)
                pygame.draw.rect(self.canvas,(7,15,22),art,border_radius=5)
                pygame.draw.rect(self.canvas,style['edge'],art,1,border_radius=5)
                if rarity=='Única':
                    self.draw_element_symbol(card.get('type'),art.center,18,glow=True)
                else:
                    spr=self.sprites.get((card.get('species'),0))
                    if spr:
                        scale=min((art.width-10)/max(1,spr.get_width()),(art.height-8)/max(1,spr.get_height()))
                        im=pygame.transform.scale(spr,(max(1,int(spr.get_width()*scale)),max(1,int(spr.get_height()*scale))))
                        self.canvas.blit(im,(art.centerx-im.get_width()/2,art.centery-im.get_height()/2+2))
                    self.draw_element_symbol(card.get('type'),(art.right-9,art.y+9),6)
                self.label(self.fit_text(format_card_name(card.get('name','Carta'))+variant_data['label'],10,126),772,340,10,INK)
                self.label(f'{card.get("type","-")} • {variant.upper()}',772,357,8,style['accent'])
                self.label(f'MEM {card.get("cost",0)} • DANO {card.get("damage",(0,0))[0]}–{card.get("damage",(0,0))[1]}',772,372,8,TEAL)
                if rarity=='Única':
                    u=self.state.unique_cards.get(selected,{})
                    mult=UNIQUE_VARIANT_MULTIPLIERS.get(variant,1.0)
                    effects=[self._unique_buff_text(b,mult) for b in u.get('buffs',[]) if isinstance(b,dict)]
                    mom=u.get('momentum')
                    if mom in UNIQUE_MOMENTUM_DEFS:
                        effects.append('Momentum - '+UNIQUE_MOMENTUM_DEFS[mom]['description'].format(type=card.get('type','-')))
                    detail='\n'.join(effects) if effects else 'Nenhum efeito aplicado.'
                else:
                    detail=card.get('description','Sem descrição.')
                self._draw_scroll_text_box((922,215,165,215),detail,'card_picker_preview',9,INK,13,style['edge'])

        selected_ok=selected is not None
        self.button((850,610,235,44),'EQUIPAR',self.equip_selected_card_from_picker,selected_ok)
        self.label('Clique uma vez para selecionar; a pré-visualização atualiza à direita.',78,617,10,MUTED)

    def domain_view(self):
        """Menu exclusivo do Domínio, acessível pela Manopla."""
        self.panel_header('DOMÍNIO', 'Progressão elemental ofensiva e defensiva da Manopla.')
        element = self.domain_selected if self.domain_selected in DOMAIN_ELEMENTS else DOMAIN_ELEMENTS[0]
        self.domain_selected = element
        level = int(getattr(self.state, 'domain_levels', {}).get(element, 0) or 0)
        xp = int(getattr(self.state, 'domain_xp', {}).get(element, 0) or 0)
        bar_value, bar_max, level, target = self.state.domain_progress(element)

        # Painel principal — propositalmente maior e à esquerda.
        self.box((35,108,770,560),(7,15,22),EDGE)
        self.draw_element_symbol(element, (82,151), 25, glow=True)
        self.label(element.upper(), 125, 134, 22, GOLD)
        self.label(f'NÍVEL {level} / {DOMAIN_LEVEL_MAX}', 125, 164, 15, TEAL)
        if level >= DOMAIN_LEVEL_MAX:
            progress_text = f'XP TOTAL {xp:,} / {DOMAIN_LEVEL_XP[DOMAIN_LEVEL_MAX]:,}  •  NÍVEL MÁXIMO'.replace(',', '.')
        else:
            progress_text = f'XP {xp:,} / {target:,}  •  PRÓXIMO NÍVEL {level + 1}'.replace(',', '.')
        self.label(progress_text, 60, 202, 12, GOLD)
        self.bar(60, 226, 690, bar_value, bar_max, TEAL)
        self.label('Cada vitória concede XP ao Domínio do elemento da criatura.', 60, 252, 10, MUTED)
        self.label('Bônus ofensivos: técnicas de carta do elemento.  •  Bônus defensivos: ataques recebidos do elemento.', 60, 270, 9, MUTED)

        self.label('PROGRESSÃO DE BÔNUS', 60, 302, 15, GOLD)
        view = pygame.Rect(55, 332, 720, 310)
        row_h = 42
        content_h = DOMAIN_LEVEL_MAX * row_h
        max_scroll = max(0, content_h - view.height)
        self.ui_scroll['domain'] = max(0, min(int(self.ui_scroll.get('domain', 0)), max_scroll))
        self.canvas.set_clip(view)
        y = view.y - int(self.ui_scroll['domain'])
        for level_id in range(1, DOMAIN_LEVEL_MAX + 1):
            node = DOMAIN_BONUSES[element][level_id]
            learned = level_id <= level
            next_level = level_id == level + 1
            border = TEAL if learned else GOLD if next_level else EDGE
            bg = (13,30,34) if learned else (12,22,29) if next_level else (8,16,23)
            rect = pygame.Rect(view.x, y, view.width - 10, 34)
            self.box(rect, bg, border)
            self.label(f'N{level_id:02d}', rect.x + 10, rect.y + 9, 10, border)
            self.label(node['name'], rect.x + 62, rect.y + 8, 11, TEAL if learned else GOLD if next_level else MUTED)
            state_text = 'CONQUISTADO' if learned else 'PRÓXIMO' if next_level else 'BLOQUEADO'
            self.label(state_text, rect.right - 100, rect.y + 9, 8, TEAL if learned else GOLD if next_level else MUTED)
            y += row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((765,332,9,310), self.ui_scroll['domain'], max_scroll)
        self._register_scrollbar('domain', (765,332,9,310), self.ui_scroll['domain'], max_scroll)

        # Seleção de elemento à direita, em ordem alfabética.
        self.box((825,108,340,560),(7,15,22),EDGE)
        self.label('ELEMENTO', 850, 134, 16, GOLD)
        self.label('Selecione um Domínio', 850, 158, 10, MUTED)
        y = 194
        for option in DOMAIN_ELEMENTS:
            active = option == element
            rect = pygame.Rect(850, y, 290, 43)
            self.box(rect, (14,34,38) if active else (11,20,27), TEAL if active else EDGE)
            self.draw_element_symbol(option, (872, y + 21), 7, glow=active)
            self.label(option, 892, y + 12, 12, TEAL if active else INK)
            opt_level = int(getattr(self.state, 'domain_levels', {}).get(option, 0) or 0)
            self.label(f'N{opt_level:02d}', 1090, y + 12, 10, GOLD if active else MUTED)
            self.buttons.append((rect, lambda e=option: (setattr(self, 'domain_selected', e), self.ui_scroll.__setitem__('domain', 0)), True))
            y += 52
        self.label('XP por criatura', 850, 622, 10, GOLD)
        self.label('Comum 20  •  Incomum 40  •  Rara 100', 850, 641, 8, MUTED)
        self.label('Mítica 200  •  Lendária 500', 850, 654, 8, MUTED)

    def gauntlet_nexus(self):
        from content import NEXUS_NODES, NEXUS_LEVEL_XP
        self.panel_header('NEXUS','Evolução cognitiva automática da Manopla V-7.')
        current=int(self.state.gauntlet_nexus_level); xp=int(self.state.gauntlet_nexus_xp); max_level=max(NEXUS_LEVEL_XP); max_xp=NEXUS_LEVEL_XP[max_level]
        self.box((35,108,1130,145),(7,15,22),EDGE); installed=bool(self.state.gauntlet_nexus_installed)
        self.label('ATIVO' if installed else 'NÃO INSTALADO — PRÉ-VISUALIZAÇÃO',60,130,14,TEAL if installed else GOLD); self.label(f'NEXUS NÍVEL {current}',60,156,22,TEAL)
        if current>=max_level:
            bar_value,bar_max=xp,max_xp; progress_text=f'XP TOTAL {xp:,} / {max_xp:,}  |  NÍVEL MÁXIMO'.replace(',','.')
        else:
            prev=0 if current<=1 else NEXUS_LEVEL_XP.get(current,0); target=NEXUS_LEVEL_XP.get(current+1,max_xp); bar_value=max(0,xp-prev); bar_max=max(1,target-prev); progress_text=f'XP {xp:,} / {target:,}  |  PRÓXIMO NÍVEL {current+1}'.replace(',','.')
        self.label(progress_text,60,187,12,GOLD); self.bar(60,211,675,bar_value,bar_max,TEAL)
        self.label(f'DROP +{float(getattr(self.state,"gauntlet_nexus_drop_bonus_pct",0.0)):.0f}%  •  VANTAGEM +{float(getattr(self.state,"gauntlet_nexus_advantage_bonus_pct",0.0)):.0f}%  •  VAMPIRISMO +{float(getattr(self.state,"gauntlet_nexus_vampirism_pct",0.0)):.0f}%',770,151,10,TEAL)
        self.label(f'{max_xp:,} XP'.replace(',','.'),1040,190,10,MUTED)
        self.label('ÁRVORE DO NEXUS',35,282,20,GOLD)
        view=pygame.Rect(35,318,1130,350); row_h=40; col_gap=555; rows_total=(max_level+1)//2; content_h=rows_total*row_h+10; max_scroll=max(0,content_h-view.height)
        self.ui_scroll['gauntlet_nexus']=max(0,min(self.ui_scroll.get('gauntlet_nexus',0),max_scroll))
        self.canvas.set_clip(view); y0=view.y-int(self.ui_scroll['gauntlet_nexus'])
        for level in range(1,max_level+1):
            col=0 if level%2==1 else 1; row=(level-1)//2; x=35+col*col_gap; y=y0+row*row_h; node=NEXUS_NODES.get(f'nexus_level_{level:02d}',{})
            learned=level<=current; next_level=level==current+1; border=TEAL if learned else GOLD if next_level else EDGE; bg=(13,30,34) if learned else (9,17,24)
            self.box((x,y,540,34),bg,border); self.label(f'N{level:02d}',x+10,y+9,10,border)
            self.label(self.fit_text(node.get('name',f'Nível {level}'),10,180),x+52,y+8,10,TEAL if learned else INK if next_level else MUTED)
            self.label(self.fit_text(node.get('description',''),9,265),x+240,y+9,9,GOLD if learned else INK if next_level else MUTED)
        self.canvas.set_clip(None); self._draw_scrollbar((1145,318,9,350),self.ui_scroll['gauntlet_nexus'],max_scroll); self._register_scrollbar('gauntlet_nexus',(1145,318,9,350),self.ui_scroll['gauntlet_nexus'],max_scroll)
        self.box((35,682,1130,28),(9,18,25),EDGE); self.label('1 dano = 1 XP',55,690,9,MUTED); self.label('DROP: materiais  •  VANTAGEM: multiplicador elemental  •  VAMPIRISMO: cura por dano',300,690,9,MUTED)

    def ship_popup_view(self):
        self.ship_interior()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((3, 8, 12, 168))
        self.canvas.blit(overlay, (0, 0))
        kind = self.ship_popup_kind or 'essence_storage'
        if kind == 'dobra_core_confirm':
            w,h=650,320; x,y=(W-w)//2,215
            self.box((x,y,w,h),(7,15,22),GOLD)
            self.label('NÚCLEO DE DOBRA',x+34,y+28,25,GOLD)
            self.label('POTENCIALIZAR A NAVE?',x+34,y+88,21,INK)
            self.wrap('A Manopla detectou o Núcleo de Dobra recuperado de RY. A instalação acoplará o núcleo ao motor e permitirá viagens para outras galáxias.',x+34,y+130,580,13,MUTED,19)
            self.button((x+34,y+226,270,48),'INSTALAR NÚCLEO',self._confirm_dobra_core,True)
            self.button((x+342,y+226,270,48),'AGORA NÃO',self.close_panel,True)
            return
        if kind == 'essence_storage':
            title='ARMAZENADOR DE ESSÊNCIAS'
            stored=max(0,int(self.state.essence_storage)); inventory=max(0,int(self.state.inventory.get('Essência',0)))
            w,h=620,330; x,y=(W-w)//2,210
            self.box((x,y,w,h),(7,15,22),GOLD)
            self.label(title,x+32,y+28,23,GOLD)
            self.label('ESSÊNCIAS ABASTECIDAS',x+32,y+92,13,MUTED)
            self.label(f'{stored:,}'.replace(',','.'),x+32,y+118,32,TEAL)
            self.label('ESSÊNCIAS NO INVENTÁRIO',x+350,y+92,13,MUTED)
            self.label(f'{inventory:,}'.replace(',','.'),x+350,y+118,32,INK)
            self.wrap(self.ship_popup_notice or 'Essências armazenadas ficam protegidas contra a penalidade de morte.',x+32,y+172,555,12,MUTED,18)
            self.button((x+32,y+230,340,48),'ARMAZENAR ESSÊNCIAS',self._deposit_essence_from_popup,inventory>0,'Você não possui Essências no inventário.')
            self.button((x+390,y+230,198,48),'FECHAR',self.close_panel,True)
            return
        w,h=620,330; x,y=(W-w)//2,210
        self.box((x,y,w,h),(7,15,22),GOLD)
        if kind=='respawn_confirm':
            inventory=max(0,int(self.state.essence_total()))
            self.label('TANQUE DE RENASCIMENTO',x+32,y+28,23,GOLD)
            self.label('INSTALAR ESTE MÓDULO?',x+32,y+90,18,INK)
            self.label(f'CUSTO  50 ESSÊNCIAS   •   DISPONÍVEL  {inventory}',x+32,y+132,13,TEAL)
            self.wrap('A instalação conclui a missão e ativa o retorno à nave após uma morte.',x+32,y+170,555,12,MUTED,19)
            self.button((x+32,y+235,250,48),'INSTALAR TANQUE',self._confirm_respawn_tank,inventory>=50)
            self.button((x+315,y+235,250,48),'CANCELAR',self.close_panel,True)
        elif kind=='respawn_insufficient':
            inventory=max(0,int(self.state.essence_total()))
            self.label('TANQUE DE RENASCIMENTO',x+32,y+28,23,GOLD)
            self.label('ESSÊNCIAS INSUFICIENTES',x+32,y+95,18,(224,112,93))
            self.label(f'NECESSÁRIO  50   •   DISPONÍVEL  {inventory}',x+32,y+145,14,INK)
            self.wrap('Derrote criaturas para obter mais Essências antes de instalar o Tanque.',x+32,y+185,555,13,MUTED,20)
            self.button((x+32,y+240,250,46),'FECHAR',self.close_panel,True)
        else:
            self.label('TANQUE DE RENASCIMENTO',x+32,y+28,23,GOLD)
            self.label('UNIDADE OPERACIONAL',x+32,y+105,20,TEAL)
            self.wrap('O Tanque está instalado e pronto para restaurar seu corpo após uma morte.',x+32,y+150,555,14,MUTED,21)
            self.button((x+32,y+240,250,46),'FECHAR',self.close_panel,True)

    def _confirm_dobra_core(self):
        ok,msg=self.state.install_dobra_core()
        self.set_message(msg)
        if ok:
            self.close_panel()
            self.checkpoint()

    def _confirm_respawn_tank(self):
        msg=self.state.craft('respawn_tank')
        if msg.startswith('Tanque de Renascimento construído'):
            self.set_message(msg); self.close_panel(); self.checkpoint()
        else:
            self.ship_popup_notice=msg
            if int(self.state.inventory.get('Essência',0)) < 50:
                self.ship_popup_kind='respawn_insufficient'

    def _deposit_essence_from_popup(self):
        amount=self.state.deposit_essence()
        if amount:
            self.ship_popup_notice=f'{amount} Essência(s) armazenada(s).'
            self.checkpoint()
        else:
            self.ship_popup_notice='Nenhuma Essência disponível no inventário.'

    def ship_interior(self):
        self.label('NAVE / INTERIOR', 35, 28, 28, TEAL)
        self.label('CONFIGURAÇÃO DE BORDO', 35, 70, 14, MUTED)
        # Layout top-down de uma pequena nave de exploração, inspirado na referência:
        # cockpit na proa, corredor central, consoles laterais e área técnica na popa.
        pygame.draw.polygon(self.canvas,(42,55,62),[(140,640),(140,240),(225,150),(355,105),(805,105),(935,150),(1020,240),(1020,640)])
        pygame.draw.polygon(self.canvas,(20,31,38),[(168,620),(168,255),(250,170),(370,128),(790,128),(910,170),(992,255),(992,620)])
        # corredor central
        pygame.draw.rect(self.canvas,(45,58,65),(365,285,430,285),border_radius=8)
        pygame.draw.rect(self.canvas,(29,41,48),(392,310,376,235),border_radius=5)
        for xx in range(410,770,60):
            pygame.draw.line(self.canvas,(47,63,69),(xx,315),(xx,535),1)
        # cockpit/proa
        pygame.draw.polygon(self.canvas,(60,74,81),[(435,290),(445,190),(505,135),(655,135),(715,190),(725,290)])
        pygame.draw.polygon(self.canvas,(8,20,27),[(463,246),(473,187),(520,154),(640,154),(687,187),(697,246)])
        pygame.draw.rect(self.canvas,(10,29,37),(510,168,140,62),border_radius=4)
        pygame.draw.rect(self.canvas,(61,132,146),(520,177,120,42),1,border_radius=3)
        # assentos de piloto e co-piloto
        for sx,accent in ((548,GOLD),(662,TEAL)):
            pygame.draw.rect(self.canvas,(51,65,72),(sx-20,232,40,39),border_radius=7)
            pygame.draw.rect(self.canvas,(30,42,48),(sx-14,220,28,19),border_radius=6)
            pygame.draw.rect(self.canvas,accent,(sx-11,216,22,4),border_radius=2)
        # consoles laterais
        def console(x,y,accent,w=100,h=78):
            pygame.draw.rect(self.canvas,(52,67,74),(x-w//2,y-h//2,w,h),border_radius=7)
            pygame.draw.rect(self.canvas,(10,24,31),(x-w//2+10,y-h//2+10,w-20,h-20),border_radius=4)
            pygame.draw.rect(self.canvas,accent,(x-w//2+17,y-h//2+21,w-34,4),border_radius=2)
            for ox in (-18,0,18):
                pygame.draw.rect(self.canvas,accent,(x+ox-3,y-h//2+36,6,6),border_radius=1)
        console(270,335,GOLD); console(890,335,TEAL); console(270,500,TEAL); console(890,500,GOLD)
        # computador e diagnóstico
        pygame.draw.rect(self.canvas,(52,67,74),(300,382,118,86),border_radius=6)
        pygame.draw.rect(self.canvas,(9,24,31),(314,394,90,49),2,border_radius=4)
        pygame.draw.rect(self.canvas,TEAL,(331,409,56,3)); pygame.draw.rect(self.canvas,GOLD,(322,421,74,4))
        pygame.draw.rect(self.canvas,(52,67,74),(815,382,118,86),border_radius=6)
        pygame.draw.rect(self.canvas,(9,24,31),(829,394,90,49),2,border_radius=4)
        for i,sid in enumerate(('propulsion','navigation','power')):
            self.bar(837,401+i*11,64,self.state.ship_systems[sid],100,TEAL if self.state.ship_systems[sid]>=60 else GOLD)
        # área técnica na popa
        pygame.draw.rect(self.canvas,(53,62,68),(448,575,330,55),border_radius=8)
        pygame.draw.rect(self.canvas,(11,23,30),(474,584,278,35),border_radius=4)
        pygame.draw.line(self.canvas,(73,94,99),(498,601),(728,601),1)
        for x in (480,745):
            pygame.draw.ellipse(self.canvas,(50,57,61),(x-18,635,x+18,664))
            pygame.draw.rect(self.canvas,(43,51,56),(x-14,660,x+14,678))
        # paredes técnicas, tubos, luzes e porta de manutenção
        for x in range(220,970,78):
            pygame.draw.line(self.canvas,(65,82,87),(x,178),(x+18,145),2)
        for x in (220,330,850,960): pygame.draw.circle(self.canvas,(78,127,136),(x,206),4)
        pygame.draw.line(self.canvas,(81,104,111),(520,130),(640,130),4)
        pygame.draw.line(self.canvas,(81,104,111),(545,635),(685,635),4)
        # áreas interativas, agora visualmente posicionadas sobre cada estação
        tank_x, tank_y = 465, 585
        pygame.draw.rect(self.canvas,(46,54,59),(tank_x-58,tank_y-22,116,74),border_radius=6)
        pygame.draw.rect(self.canvas,(12,25,31),(tank_x-48,tank_y-14,96,46),border_radius=4)
        pygame.draw.ellipse(self.canvas,(76,93,98),(tank_x-22,tank_y-7,tank_x+22,tank_y+28),2)
        pygame.draw.line(self.canvas,TEAL,(tank_x-15,tank_y+10),(tank_x+15,tank_y+10),2)
        storage_x, storage_y = 735, 585
        pygame.draw.rect(self.canvas,(46,54,59),(storage_x-58,storage_y-22,116,74),border_radius=6)
        pygame.draw.rect(self.canvas,(12,25,31),(storage_x-48,storage_y-14,96,46),border_radius=4)
        pygame.draw.rect(self.canvas,GOLD,(storage_x-25,storage_y-2,50,20),2,border_radius=3)
        self.label('TANQUE DE RENASCIMENTO',tank_x-60,tank_y+40,9,GOLD)
        self.label('ARMAZENADOR DE ESSÊNCIAS',storage_x-66,storage_y+40,9,GOLD)
        points=[('cockpit','COCKPIT',620,248,GOLD),('computer','COMPUTADOR',359,470,TEAL),('status','STATUS',874,470,(123,185,226)),('simulator','SIMULADOR',613,610,(190,122,210)),('airlock','ESCOTILHA',613,680,MUTED)]
        for key,name,px,py,color in points:
            self.label(name,px-42,py,10,color)
        # personagem no interior: a posição visual acompanha a célula real de
        # movimento da nave. O mapa usa uma grade lógica pequena para manter
        # colisões/interações simples, mas o personagem é projetado sobre o
        # layout visual da nave.
        ship_x, ship_y = self.state.ship_pos
        actor_x = 330 + ship_x * 45
        actor_y = 165 + ship_y * 60
        self.actor('hero', actor_x, actor_y, 1.18, int(self.frame*4), direction=self.facing)
        point=self.state.ship_interaction()
        if point=='cockpit' and self.state.missions.get('ship_navigation',{}).get('status')=='active':
            self.label('E — REPARAR REFERÊNCIA ESTELAR',400,690,14,GOLD)
        elif point:
            hints={'cockpit':'E — abrir cockpit','computer':'E — abrir computador','status':'E — abrir painel de status','simulator':('E — usar simulador' if self.state.simulator_built else ('E — projeto do simulador' if self.state.simulator_unlocked else 'E — suporte vazio')),'respawn_tank':('E — tanque operacional' if self.state.respawn_tank_built else 'E — construir tanque'),'essence_storage':'E — armazenar essências','airlock':'E — sair da nave'}
            self.label(hints[point],390,690,14,GOLD)
        self.label(f'VIDA {self.state.hp}/{self.state.max_hp}',35,748,12,MUTED); self.bar(32,767,350,self.state.hp,self.state.max_hp,(203,112,94))
        self.label(f'MEMÓRIA {self.state.memory}/{self.state.max_memory}',790,748,12,MUTED); self.bar(790,767,350,self.state.memory,max(1,self.state.max_memory),TEAL)

    def simulator(self):
        self.panel_header('SIMULADOR', 'Reprodução virtual de bosses já concluídos. As simulações preservam a condição real do combate.')
        self.box((70, 118, 1060, 555), (6, 15, 22), EDGE)
        self.label('BOSSES DISPONÍVEIS', 105, 152, 21, GOLD)
        defeated = [bid for bid in BOSSES if self.state.bosses.get(bid, {}).get('defeated')]
        view = pygame.Rect(98, 187, 968, 345)
        row_h = 82
        max_scroll = max(0, len(defeated) * row_h - view.height)
        self.ui_scroll['simulator'] = max(0, min(self.ui_scroll.get('simulator', 0), max_scroll))
        self.canvas.set_clip(view)
        y = view.y - int(self.ui_scroll['simulator'])
        for bid in defeated:
            boss = BOSSES[bid]
            card = CARDS.get(boss.get('card'), {})
            rect = pygame.Rect(view.x, int(y), view.width - 10, row_h - 10)
            self.box(rect, (19, 30, 38), CARD_RARITY_ACCENTS.get(card.get('rarity', 'Rara'), EDGE))
            self.label(boss.get('name', bid).upper(), rect.x + 16, rect.y + 10, 17, TEAL)
            self.label(f"{boss.get('type','-')}  |  {card.get('name','-')}  |  {card.get('rarity','Rara')}", rect.x + 16, rect.y + 37, 12, MUTED)
            self.label(f"VIRTUAIS: {int(self.state.bosses.get(bid, {}).get('virtual_defeats', 0) or 0)}", rect.x + 16, rect.y + 57, 11, GOLD)
            charge = self.state.inventory.get('Carga de Simulação', 0)
            self.button((rect.right - 245, rect.y + 18, 225, 42), f'SIMULAR  [{charge} CARGAS]', lambda b=bid: self.start_virtual_boss(b), charge > 0)
            y += row_h
        self.canvas.set_clip(None)
        if not defeated:
            self.label('Nenhum boss concluído.', 116, 215, 16, MUTED)
        self._draw_scrollbar((1078, 187, 9, 345), self.ui_scroll['simulator'], max_scroll)
        self._register_scrollbar('simulator', (1078, 187, 9, 345), self.ui_scroll['simulator'], max_scroll)
        self.wrap('Cada simulação consome 1 Carga de Simulação, não altera seu HP ou Memória reais e permite repetir o confronto para progressão de conquistas.', 105, 555, 940, 14, INK, 20)
        self.button((105, 625, 300, 40), 'ESC  Voltar', self.close_panel)

    def start_virtual_boss(self, boss_id):
        ok, msg = self.state.start_boss_battle(boss_id, virtual=True)
        self.set_message(msg)
        if ok:
            self.battle_species = boss_id
            self.mode, self.phase, self.phase_time = 'battle', 'choose', 0.0
            boss = BOSSES[boss_id]
            self.selected_battle_target = next((tid for tid, zone in boss.get('target_zones', {}).items() if not zone.get('exposed_only')), next(iter(boss.get('target_zones', {'body':{}}))))

    def start_virtual_kuvaar(self):
        self.start_virtual_boss('kuvaar')

    def dialogue(self):
        npc = self.dialogue_npc
        if npc and npc.get('civilization') not in ('avarin','nahr_shadows'):
            civ = CIVILIZATIONS.get(npc.get('civilization'), {})
            self.panel_header('COMUNICAÇÃO', 'Idioma reconhecido pela database do Elmo.')
            self.box((90, 145, 1020, 360), (7,15,22), EDGE)
            self.label(f'{npc["name"].upper()} // {npc["role"]}',125,178,22,GOLD)
            self.label('CIVILIZAÇÃO: ' + civ.get('name','Desconhecida'),125,215,14,TEAL)
            self.label('IDIOMA: ' + civ.get('language','—'),125,240,13,MUTED)
            self._draw_scroll_text_box((125,275,920,125), npc.get('dialogue', 'Contato estabelecido.'), 'language_dialogue', 14, INK, 19)
            if self.civ_mission_civ and self.state.knows_language(self.civ_mission_civ):
                self.button((125,555,330,52),'PEDIDOS',self.open_civilization_missions,True)
                self.button((475,555,290,52),'ESC  Encerrar',self.close_panel,True)
            else:
                self.button((125,555,440,68),'ESC  Encerrar conversa',self.close_panel,True)
            return
        self.panel_header('COMUNICAÇÃO', 'A Manopla agora consegue traduzir o Avari em nível funcional.')
        self.box((90, 145, 1020, 360), (7,15,22), EDGE)
        title = 'ESPAÇO  Aceitar missão'
        available = False
        if npc:
            self.label(f'{npc["name"].upper()} // {npc["role"]}', 125, 178, 22, GOLD)
            faction = FACTIONS.get(npc.get('faction'), {}).get('name', 'Avarin')
            self.label('Facção: ' + faction, 125, 215, 14, TEAL)
            conflict = self.state.missions.get('faction_conflict', {})
            if self.mission_id == 'faction_conflict':
                if npc.get('id') == 'faction_c_leader' and conflict.get('status') == 'available':
                    text = ('Tarek, Voz da Fenda, revela que os Guardiões dos Reservatórios irão deslocar uma comitiva confiando no próprio sistema de comunicação. ' +
                            'Ele quer que você comprometa a rede para que a comitiva entre despreparada em uma emboscada. Mas você também pode recusar o golpe e alertar Iria antes do ataque.')
                    title = 'ESPAÇO  ACEITAR A DÍVIDA DA FENDA'
                    available = True
                elif npc.get('id') == 'faction_c_leader' and conflict.get('status') == 'active':
                    text = ('Tarek mantém a postura fechada. A ordem é simples: encontre Iria e decida se a rede dos Guardiões será comprometida. ' +
                            'A Manopla registra que ainda existe uma alternativa antes do confronto.')
                    title = 'MISSÃO EM ANDAMENTO'
                elif npc.get('id') == 'avarin_waterkeeper' and conflict.get('status') == 'active':
                    text = ('Iria ouve a informação sobre a emboscada. Você pode se infiltrar no sistema de comunicação dos Guardiões e transmitir uma rota falsa para a comitiva, ' +
                            'ou revelar a emboscada e permitir que os Guardiões preparem uma resposta. O resultado será permanente e definirá qual líder perderá o confronto.')
                    self.wrap(text, 125, 255, 920, 18, INK, 27)
                    self.button((125, 555, 440, 68), '1  HACKEAR A COMUNICAÇÃO', lambda: self.faction_conflict_action('sabotage'), True, 'Invadir a rede dos Guardiões e manter o plano de Tarek')
                    self.button((595, 555, 440, 68), '2  ALERTAR IRIA', lambda: self.faction_conflict_action('warn'), True, 'Revelar a emboscada antes que a comitiva saia')
                    return
                elif conflict.get('status') == 'completed':
                    winner = FACTIONS.get(conflict.get('winner'), {}).get('name', 'facção vencedora')
                    loser = FACTIONS.get(conflict.get('loser'), {}).get('name', 'facção derrotada')
                    text = f'O conflito terminou. {winner} venceu e {loser} foi derrotada. A decisão já está registrada na Manopla.'
                else:
                    text = 'A proposta dos Filhos da Fenda ainda não está disponível.'
            elif self.mission_id == 'kuvaar_hunt':
                text = 'Iria explica que os reservatórios voltaram a cair. Uma criatura gigantesca está drenando o lençol freático na bacia. Os Avarin precisam que você descubra onde ela está e interrompa a crise.'
                title = 'ESPAÇO  Aceitar caça a Kuvaar'
                available = self.state.missions['kuvaar_hunt']['status']=='available'
            else:
                text = 'Iria explica que a Estação de Captação perdeu pressão e que os reservatórios de Qaresh estão entrando em nível crítico. Você poderia ajudá-los porque sua armadura entende tecnologias que eles já não conseguem reparar.'
                title = 'ESPAÇO  Aceitar missão'
                available = self.state.missions['water_supply']['status']=='available'
            self.wrap(text, 125, 255, 920, 18, INK, 27)
        self.button((125, 555, 440, 68), title if npc else 'ESPAÇO  Aceitar missão', self.accept_mission, available if npc else False)
        if self.civ_mission_civ and self.state.knows_language(self.civ_mission_civ) and not available:
            self.button((595, 555, 210, 52), 'PEDIDOS', self.open_civilization_missions, True)
            self.button((815, 555, 220, 52), 'ESC  Encerrar', self.close_panel, True)
        else:
            self.button((595, 555, 440, 68), 'ESC  Encerrar conversa', self.close_panel, True)

    def mission_choice(self):
        if self.mission_id == 'kuvaar_hunt':
            self.panel_header('ÁGUA PURA', 'Kuvaar só pode ser exposto com uma reserva de água pura.')
            self.box((90, 125, 1020, 540), (7,15,22), EDGE)
            self.label('PREPARAÇÃO DA CAÇADA', 125, 160, 23, GOLD)
            self.wrap('A criatura está drenando o lençol freático. Água comum não terá efeito. Escolha de onde virá a reserva que será levada até a Bacia Seca.', 125, 202, 920, 17, MUTED, 24)
            choices = self.state.kuvaar_water_options()
            for i, (path, title, desc) in enumerate(choices):
                y = 295 + i*105
                self.button((125, y, 920, 82), f'{i+1}  {title}', lambda p=path: self.mission_action(p), True, desc)
            self.button((125, 625, 350, 38), 'ESC  Adiar', self.close_panel)
            return
        self.panel_header('DECISÃO', 'A crise pode ser solucionada por conhecimento, força ou infiltração.')
        self.box((90, 125, 1020, 540), (7,15,22), EDGE)
        self.label('ESTAÇÃO DE CAPTAÇÃO', 125, 160, 23, GOLD)
        self.wrap('A pressão do sistema caiu. O pedido dos Guardiões dos Reservatórios chegou até você e a recompensa já foi definida. A escolha abaixo será registrada no seu histórico.', 125, 202, 920, 17, MUTED, 24)
        choices = self.state.mission_choices('water_supply')
        for i, (path, title, desc) in enumerate(choices):
            y = 295 + i*105
            self.button((125, y, 920, 82), f'{i+1}  {title}', lambda p=path: self.mission_action(p), True, desc)
        self.button((125, 625, 350, 38), 'ESC  Adiar decisão', self.close_panel)

    def hack(self):
        h = self.state.hack or {'cursor':[0,0], 'access':[(0,0)], 'firewall':[], 'goal':(2,2), 'alert':0, 'turns':0}
        self.label('MANOPLA // INTRUSÃO', 35, 28, 30, TEAL)
        hack_title = 'Rede do Complexo Neris — acesso remoto' if h.get('purpose') != 'faction_conflict' else 'Enlace de comunicações dos Guardiões — acesso pelo terminal de Qaresh'
        self.label(hack_title, 35, 70, 16, MUTED)
        self.box((270, 125, 660, 520), (5,13,19), EDGE)
        self.label('ALERTA FIREWALL', 720, 150, 13, GOLD)
        self.label(f'{h.get("alert",0)}/{h.get("alert_limit",3)}', 828, 148, 17, TEAL if h.get('alert',0)==0 else (224,112,93))
        ox, oy, step = 390, 215, 180
        for yy in range(3):
            for xx in range(3):
                pos=(xx,yy)
                cx,cy=ox+xx*step, oy+yy*step
                color = (34,74,80) if pos in h.get('access',[]) else EDGE
                if pos in h.get('firewall',[]): color=(101,67,59)
                if pos==h.get('goal'): color=GOLD
                pygame.draw.rect(self.canvas, color, (cx-45,cy-45,90,90), border_radius=8)
                pygame.draw.rect(self.canvas, TEAL if pos==tuple(h.get('cursor',[0,0])) else EDGE, (cx-50,cy-50,100,100), 2, border_radius=8)
                self.label('CORE' if pos==h.get('goal') else ('FIREWALL' if pos in h.get('firewall',[]) else f'NODE {yy*3+xx+1}'), cx-31, cy-8, 11, INK)
        controls='Setas: selecionar nó | ESPAÇO: infiltrar'
        if self.state.gauntlet_nexus_hack_diagonal:
            controls += ' | diagonais via numpad 7/9/1/3'
        self.label(controls, 315, 585, 14, MUTED)
        self.label('Acesso atual: ' + ', '.join(f'{x},{y}' for x,y in h.get('access',[])), 315, 615, 12, TEAL)
        self.button((315, 660, 270, 40), 'ESC  Abandonar intrusão', lambda: (setattr(self.state, 'hack', None), setattr(self, 'mode', 'world')))

    def claim_achievement(self, aid):
        ok, msg = self.state.claim_achievement(aid)
        self.set_message(msg)
        if ok:
            self.checkpoint()

    def achievement_catalog(self):
        entries = []
        for aid, data in ACHIEVEMENTS.items():
            entries.append((aid, data))
        for sid in self.state.bestiary_known:
            data = creature_achievement_data(sid)
            if data:
                aid = creature_achievement_id(sid)
                if aid in self.state.achievements:
                    entries.append((aid, data))
        # Bosses novos só entram no menu depois da liberação de viagens interplanetárias.
        # As etapas maiores permanecem ocultas até a etapa anterior ser concluída.
        for boss_id in BOSSES:
            if boss_id in ('fagor','kael','ounull') and not self.state.ship_flight_ready():
                continue
            if boss_id == 'kuvaar' or self.state.ship_flight_ready():
                for target in BOSS_ACHIEVEMENT_TIERS:
                    aid = boss_achievement_id(boss_id, target)
                    data = boss_achievement_data(boss_id, target)
                    if not data:
                        continue
                    if target > 1:
                        prev = boss_achievement_id(boss_id, 1 if target == 100 else 100)
                        if not self.state.achievements.get(prev, {}).get('unlocked', False):
                            continue
                    entries.append((aid, data))
        return entries

    def achievement_progress_text(self, aid, data):
        condition = data.get('condition')
        if condition == 'species_kills':
            current = min(1000, int(self.state.kills.get(data.get('species'), 0)))
            return f'{current}/1000 abates'
        if condition == 'boss_defeats':
            boss_id = data.get('boss')
            target = int(data.get('target', 1) or 1)
            if target == 1:
                current = int(self.state.statistics.get('bosses_defeated', {}).get(boss_id, 0) or 0)
            else:
                current = int(self.state.bosses.get(boss_id, {}).get('virtual_defeats', 0) or 0)
            return f'{min(target, current)}/{target} abates'
        return ''

    def achievements(self):
        self.panel_header('CONQUISTAS', 'Marcos e recompensas.')
        categories = ('Todos','Combate','Coleção','Exploração','Tecnologia','Campanha')
        x_positions = (35, 225, 415, 605, 795, 985)
        for x, cat in zip(x_positions, categories):
            active = self.achievement_category == cat
            self.button((x,96,170,36), cat.upper(), lambda c=cat: (setattr(self,'achievement_category',c), self.ui_scroll.__setitem__('achievements',0)), True,
                        subtitle='ATIVA' if active else None)
        entries = [(aid,data) for aid,data in self.achievement_catalog() if self.achievement_category == 'Todos' or data.get('category','Campanha') == self.achievement_category]
        self.box((35, 145, 1130, 548), (7,15,22), EDGE)
        view = pygame.Rect(58, 174, 1068, 490)
        row_h = 76
        max_scroll = max(0, len(entries)*row_h-view.height)
        self.ui_scroll['achievements'] = max(0,min(self.ui_scroll.get('achievements',0),max_scroll))
        self.canvas.set_clip(view)
        y=view.y-int(self.ui_scroll['achievements'])
        if not entries:
            self.label('Nenhuma conquista registrada nesta categoria.', 80, y+20, 16, MUTED)
        for aid,data in entries:
            unlocked=self.state.achievements.get(aid,{}).get('unlocked',False)
            claimed=self.state.achievements.get(aid,{}).get('claimed',False)
            accent=TEAL if unlocked else EDGE
            rect=pygame.Rect(view.x,int(y),view.width-2,row_h-7)
            self.box(rect,(18,37,39) if unlocked else (12,22,29),accent)
            self.label(data.get('category','Campanha').upper(),rect.x+12,rect.y+7,9,accent)
            self.label(('✓ ' if unlocked else '○ ')+self.fit_text(data['name'],17,430),rect.x+12,rect.y+24,16,TEAL if unlocked else GOLD)
            progress=self.achievement_progress_text(aid,data)
            desc=self.fit_text(data.get('description',''),11,650)
            self.label(desc,rect.x+12,rect.y+48,11,INK)
            if progress:
                self.label(progress, 770, rect.y+10, 11, GOLD)
            self.label(self.fit_text('RECOMPENSA: '+data.get('reward','—'),10,300), 770, rect.y+30, 10, GOLD if unlocked else MUTED)
            if claimed:
                self.label('✓ RECEBIDA', rect.x+945, rect.y+50, 10, TEAL)
            elif unlocked:
                self.button((960,rect.y+8,145,34),'RESGATAR',lambda a=aid:self.claim_achievement(a),True)
            else:
                self.label('BLOQUEADA', rect.x+965, rect.y+52, 10, MUTED)
            y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((1138,174,9,490),self.ui_scroll['achievements'],max_scroll)
        self._register_scrollbar('achievements',(1138,174,9,490),self.ui_scroll['achievements'],max_scroll)
    def panel_header(self, title, subtitle):
        self.label(self.fit_text(title, 28, 915), 35, 28, 28, TEAL)
        self.label(self.fit_text(subtitle, 16, 945), 35, 70, 16, MUTED)
        self.button((1000, 27, 165, 45), 'VOLTAR', self.close_panel)

    def _craft_is_single_instance_built(self, cid):
        checks = {
            'chest_g2': lambda: self.state.chest_generation >= 2,
            'helmet_g1': lambda: bool(self.state.helmet_owned),
            'helmet_g2': lambda: self.state.helmet_generation >= 2,
            'gauntlet_nexus': lambda: bool(self.state.gauntlet_nexus_installed),
            'water_purifier': lambda: bool(self.state.water_purifier_built),
            'respawn_tank': lambda: bool(self.state.respawn_tank_built),
            'combat_simulator': lambda: bool(self.state.simulator_built),
            'chest_g3': lambda: self.state.chest_generation >= 3,
            'locomotion_g1': lambda: self.state.locomotion_generation >= 1,
        }
        fn=checks.get(cid)
        return bool(fn()) if fn else False

    def craft_entries(self, category=None):
        category = category or self.craft_category
        all_entries = [(key, OTHER_RECIPES[key]) for key in ('kit','memory','memory_g2','chest_g2','helmet_g2','decoder_core','energy_cell','water_purifier','pure_water','helmet_g1','gauntlet_nexus','respawn_tank','combat_simulator','simulation_charge') if key in OTHER_RECIPES]
        all_entries += [(uid, data) for uid, data in FUTURE_UPGRADES.items() if uid not in OTHER_RECIPES and uid not in CARDS and uid in ('chest_g3','memory_g3','locomotion_g1')]
        def cat(cid):
            if cid in ('chest_g2','memory','memory_g2','memory_g3','helmet_g1','helmet_g2','gauntlet_nexus','chest_g3','locomotion_g1'):
                return 'Equipamento'
            if cid in ('kit','pure_water','simulation_charge'):
                return 'Itens'
            return 'Outros'
        entries=[(cid,data) for cid,data in all_entries if cat(cid)==category]
        gated=[]
        for cid,data in entries:
            # Projetos de instância única somem completamente da Oficina assim que construídos.
            if self._craft_is_single_instance_built(cid): continue
            if cid=='helmet_g2' and self.state.helmet_generation<1: continue
            if cid=='memory_g2' and self.state.chest_generation<2: continue
            if cid=='chest_g3' and self.state.chest_generation<2: continue
            if cid=='memory_g3' and self.state.memory_owned.get('advanced',0)<1: continue
            gated.append((cid,data))
        return gated

    def _craft_category(self):
        cats=('Equipamento','Itens','Outros')
        return cats

    def craft_view(self):
        self.panel_header('FABRICAÇÃO', 'Projetos e equipamentos; cartas são fabricadas no menu CARTAS.')
        cats=('Equipamento','Itens','Outros')
        x_positions=(35,410,785)
        for x,cat in zip(x_positions,cats):
            self.button((x,96,335,38),cat.upper(),lambda c=cat:(setattr(self,'craft_category',c),setattr(self,'craft_page',0)),True,'ATIVA' if self.craft_category==cat else None)
        entries=self.craft_entries(self.craft_category); per_page=4; page_count=max(1,(len(entries)+per_page-1)//per_page); self.craft_page=max(0,min(self.craft_page,page_count-1))
        page_entries=entries[self.craft_page*per_page:(self.craft_page+1)*per_page]
        for i,(cid,data) in enumerate(page_entries):
            y=140+i*130; self.box((35,y,1130,116))
            self.label(self.fit_text(data.get('name',cid),19,430),54,y+9,19,INK)
            self.wrap(data.get('description',data.get('effect','')),54,y+37,500,12,MUTED,15)
            recipe=list(data.get('recipe',{}).items()); self.label('MATERIAIS',610,y+10,10,GOLD)
            for idx,(item_name,required) in enumerate(recipe[:6]):
                col=idx%2; row=idx//2; cx=610+col*175; cy=y+30+row*22; owned=int(self.state.essence_total()) if item_name=='Essência' else int(self.state.inventory.get(item_name,0)); self.label(self.fit_text(item_name,9,125),cx,cy,9,INK); self.label(f'{owned}/{required}',cx+130,cy,9,TEAL if owned>=required else (224,112,93))
            can=all((self.state.essence_total() if n=='Essência' else int(self.state.inventory.get(n,0)))>=q for n,q in data.get('recipe',{}).items())
            if cid=='chest_g2': can=can and self.state.chest_generation<2
            if cid=='helmet_g1': can=can and not self.state.helmet_owned
            if cid=='helmet_g2': can=can and self.state.helmet_generation>=1 and self.state.helmet_generation<2
            if cid=='memory': can=can and self.state.memory_owned[MEMORY_RECIPES[cid]]<CHEST_MEMORY_SLOTS
            if cid=='memory_g2': can=can and self.state.chest_generation>=2 and self.state.memory_owned[MEMORY_RECIPES[cid]]<CHEST_MEMORY_SLOTS
            if cid=='memory_g3': can=can and self.state.memory_owned.get('advanced',0)>=1
            if cid=='chest_g3': can=can and self.state.chest_generation>=2 and self.state.chest_generation<3
            if cid=='gauntlet_nexus': can=can and not self.state.gauntlet_nexus_installed
            if cid=='water_purifier': can=can and not self.state.water_purifier_built
            if cid=='pure_water': can=can and self.state.water_purifier_built
            if cid=='combat_simulator': can=can and self.state.simulator_unlocked and not self.state.simulator_built
            if cid=='simulation_charge': can=can and self.state.simulator_built
            if cid=='respawn_tank': can=can and (not self.state.respawn_tank_built) and self.state.missions.get('respawn_tank',{}).get('status') == 'active'
            self.button((950,y+49,195,42),'FABRICAR',lambda c=cid:self.craft(c),can)
        self.button((35,671,335,42),'RECURSOS',lambda:self.open_panel('resources','craft'),True)
        self.button((704,671,155,42),'Anterior',lambda:setattr(self,'craft_page',self.craft_page-1),self.craft_page>0)
        self.label(f'{self.craft_page+1}/{page_count}',890,682,16,GOLD)
        self.button((983,671,182,42),'Próxima página',lambda:setattr(self,'craft_page',self.craft_page+1),self.craft_page<page_count-1)

    def _inventory_item_usage(self, item_name):
        """Retorna usos de crafting conhecidos e fontes de drop conhecidas."""
        usages = []
        # Cartas: só revelar receitas de cartas já conhecidas pelo jogador.
        for cid, data in CARDS.items():
            if cid not in self.state.known_cards:
                continue
            if item_name in data.get('recipe', {}):
                usages.append((format_card_name(data.get('name', cid)), f'Carta • {data["recipe"][item_name]}'))

        # Receitas comuns atualmente disponíveis.
        recipe_sources = list(OTHER_RECIPES.items())
        # Projetos futuros apenas quando o predecessor já os tornou visíveis.
        for uid, data in FUTURE_UPGRADES.items():
            if uid in OTHER_RECIPES or uid in CARDS or uid == 'special_slot':
                continue
            if self.future_upgrade_visible(uid):
                recipe_sources.append((uid, data))
        for rid, data in recipe_sources:
            if item_name in data.get('recipe', {}):
                usages.append((format_card_name(data.get('name', rid)), f'Projeto • {data["recipe"][item_name]}'))
        usages.sort(key=lambda pair: pair[0].casefold())

        # Só listar criaturas que o jogador já conhece pelo Bestiário.
        sources = []
        for sid in self.state.bestiary_known:
            spec = SPECIES.get(sid)
            if not spec:
                continue
            if any(drop[0] == item_name for drop in spec.get('drops', [])):
                sources.append(spec['name'])
        sources.sort(key=str.casefold)
        return usages, sources

    def inventory(self):
        self.panel_header('INVENTÁRIO', 'Itens adquiridos. Selecione um item para consultar seus usos conhecidos e criaturas que o fornecem.')
        left = pygame.Rect(35, 112, 500, 560)
        right = pygame.Rect(565, 112, 600, 560)
        self.box(left, (7, 15, 22), EDGE)
        self.box(right, (7, 15, 22), EDGE)

        self.label('ITENS ADQUIRIDOS', 58, 136, 22, GOLD)
        items = sorted([(name, qty) for name, qty in self.state.inventory.items() if int(qty) > 0], key=lambda pair: pair[0].casefold())
        material_view = pygame.Rect(58, 175, 444, 447)
        row_h = 30
        max_scroll = max(0, len(items) * row_h - material_view.height)
        self.ui_scroll['inventory_materials'] = max(0, min(self.ui_scroll.get('inventory_materials', 0), max_scroll))
        self.canvas.set_clip(material_view)
        y = material_view.y - self.ui_scroll['inventory_materials']
        for name, qty in items:
            row_rect = pygame.Rect(material_view.x, int(y), material_view.width-4, row_h-2)
            selected = name == self.inventory_selected_item
            self.box(row_rect, (18, 37, 39) if selected else (11, 21, 28), TEAL if selected else EDGE)
            self.label(name, row_rect.x+10, row_rect.y+7, 13 if len(name) > 23 else 14, TEAL if selected else INK)
            self.label(str(qty), row_rect.right-32, row_rect.y+7, 14, TEAL)
            visible_rect = row_rect.clip(material_view)
            if visible_rect.height > 0:
                self.buttons.append((visible_rect, lambda item=name: setattr(self, 'inventory_selected_item', item), True))
            y += row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((511, 175, 10, 447), self.ui_scroll['inventory_materials'], max_scroll)
        self._register_scrollbar('inventory_materials', (511, 175, 10, 447), self.ui_scroll['inventory_materials'], max_scroll)

        selected = self.inventory_selected_item if self.inventory_selected_item in dict(items) else (items[0][0] if items else None)
        if selected != self.inventory_selected_item:
            self.inventory_selected_item = selected
        self.label('INFORMAÇÕES DO ITEM', 590, 136, 22, GOLD)
        detail_view = pygame.Rect(590, 175, 540, 447)
        self.box(detail_view, (11, 21, 28), EDGE)
        if not selected:
            self.label('Nenhum item adquirido.', 615, 205, 16, MUTED)
        else:
            usages, sources = self._inventory_item_usage(selected)
            qty = int(dict(items).get(selected, 0))
            usage_count = max(1, len(usages))
            source_count = max(1, len(sources))
            content_height = 80 + 35 + usage_count * 28 + 35 + source_count * 25 + 10
            max_detail = max(0, content_height - detail_view.height + 16)
            self.ui_scroll['inventory_details'] = max(0, min(self.ui_scroll.get('inventory_details', 0), max_detail))
            self.canvas.set_clip(detail_view)
            y = detail_view.y + 25 - int(self.ui_scroll['inventory_details'])
            self.label(self.fit_text(format_card_name(selected), 22, 410), 615, y, 22, TEAL); y += 34
            self.label(f'QUANTIDADE: {qty}', 615, y, 14, GOLD); y += 38
            self.label('USADO EM', 615, y, 17, GOLD); y += 32
            if usages:
                for name, detail in usages:
                    self.label(self.fit_text(name, 12, 350), 615, y, 13, INK)
                    self.label(detail, 985, y, 10, TEAL)
                    y += 28
            else:
                self.label('Nenhum projeto conhecido utiliza este item.', 615, y, 12, MUTED); y += 28
            y += 8
            self.label('CRIATURAS QUE FORNECEM', 615, y, 17, GOLD); y += 32
            if sources:
                for source in sources:
                    self.label('• ' + self.fit_text(source, 12, 435), 615, y, 12, INK); y += 25
            else:
                self.label('Nenhuma criatura conhecida fornece este item.', 615, y, 12, MUTED); y += 25
            self.canvas.set_clip(None)
            self._draw_scrollbar((1138, 175, 9, 447), self.ui_scroll['inventory_details'], max_detail)
            self._register_scrollbar('inventory_details', (1138, 175, 9, 447), self.ui_scroll['inventory_details'], max_detail)

        free_modules = sum(self.state.loose_modules(k) for k in MEMORY_MODULES)
        if free_modules > 0:
            self.label('Módulos livres', 58, 646, 13, GOLD)
            self.label(str(free_modules), 190, 646, 14, TEAL)

    def renown(self):
        self.panel_header('RENOME', 'Reputação')
        self.box((35,112,1130,560),(7,15,22),EDGE)
        visited_planets = self.state.visited_planet_ids()
        if not visited_planets:
            visited_planets = ['veyra']
        selected_id = self.state.selected_planet if self.state.selected_planet in visited_planets else visited_planets[0]
        self.state.selected_planet = selected_id
        selected = next((r for r in STELLAR_ROUTES if r['id'] == selected_id), STELLAR_ROUTES[0])

        left = pygame.Rect(58,150,735,495)
        right = pygame.Rect(810,150,320,495)
        self.box(left,(11,21,28),EDGE); self.box(right,(11,21,28),EDGE)

        # Painel amplo do planeta selecionado.
        galaxy_id = selected.get('galaxy', GALAXY_ID)
        galaxy_name = GALAXIES.get(galaxy_id, {}).get('name', galaxy_id)
        self.label('PLANETA SELECIONADO',80,175,12,GOLD)
        self.label(selected['name'].upper(),80,202,30,TEAL)
        self.label(galaxy_name,80,239,13,MUTED)
        planet_total = self.state.renown_planets.get(selected_id,0)
        self.label('RENOME DO PLANETA',80,279,12,GOLD)
        self.label(str(planet_total),80,306,34,TEAL)

        # Resumo de facções apenas para o planeta atualmente apoiado pelo sistema de renome da campanha.
        if selected_id == 'veyra':
            self.label('FACÇÕES',285,279,12,GOLD)
            fy=306
            for fid in ('waterkeepers','rift_children'):
                self.label(FACTIONS[fid]['name'],285,fy,11,INK); self.label(str(self.state.renown_by_faction.get(fid,0)),675,fy,12,GOLD); fy+=28

        self.label('MILESTONES DO PLANETA',80,365,16,GOLD)
        y=394
        for i,threshold in enumerate(RENOWN_MILESTONES['planet']):
            claim=self.state.renown_reward('planet',selected_id,i)
            reward=self.state.renown_reward_items('planet',selected_id,i)
            reward_text=' + '.join(f'{n} ×{q}' for n,q in reward)
            rr=pygame.Rect(80,y,675,44)
            self.box(rr,(10,19,25),GOLD if claim else EDGE)
            self.label(f'{planet_total}/{threshold}',95,y+9,11,TEAL if planet_total>=threshold else MUTED)
            self.label(self.fit_text(reward_text,10,365),220,y+9,10,INK)
            if claim:
                self.button((635,y+6,105,31),'RESGATAR',lambda idx=i:self.claim_renown('planet',selected_id,idx),True)
            elif planet_total>=threshold:
                self.label('✓',710,y+12,12,EDGE)
            y+=52

        self.label('RENOME DA GALÁXIA',80,562,13,GOLD)
        galaxy_total=self.state.renown_galaxies.get(galaxy_id,0)
        self.label(str(galaxy_total),80,586,21,TEAL)

        # Milestones da galáxia ficam compactos abaixo, preparados para várias galáxias.
        gy=556
        self.label('MILESTONES',285,562,13,GOLD)
        for i,threshold in enumerate(RENOWN_MILESTONES['galaxy']):
            claim=self.state.renown_reward('galaxy',galaxy_id,i)
            reward=self.state.renown_reward_items('galaxy',galaxy_id,i)
            reward_text=' + '.join(f'{n} ×{q}' for n,q in reward)
            self.label(f'{galaxy_total}/{threshold}',285,586+i*28,10,TEAL if galaxy_total>=threshold else MUTED)
            self.label(self.fit_text(reward_text,9,260),390,586+i*28,9,INK)
            if claim:
                self.button((660,580+i*28,80,23),'RESG.',lambda idx=i:self.claim_renown('galaxy',galaxy_id,idx),True)

        # Lista navegável de galáxias e planetas visitados.
        self.label('GALÁXIAS VISITADAS',828,174,12,GOLD)
        galaxy_ids=self.state.visited_galaxy_ids()
        content=[]
        for gid in galaxy_ids:
            content.append(('galaxy',gid,GALAXIES.get(gid,{}).get('name',gid)))
            for pid in self.state.galaxy_planet_ids(gid):
                route=next((r for r in STELLAR_ROUTES if r['id']==pid),None)
                if route: content.append(('planet',pid,route['name']))
        row_h=31; header_h=27; total_h=0
        for typ,_,_ in content: total_h += header_h if typ=='galaxy' else row_h
        view=pygame.Rect(820,198,300,425)
        max_scroll=max(0,total_h-view.height)
        self.ui_scroll['renown']=max(0,min(self.ui_scroll.get('renown',0),max_scroll))
        self.canvas.set_clip(view); y=view.y-int(self.ui_scroll['renown'])
        for typ,key,name in content:
            if typ=='galaxy':
                self.label(name.upper(),830,y+6,10,GOLD); y+=header_h
            else:
                selected_row=(key==selected_id)
                rr=pygame.Rect(830,y,270,27)
                self.box(rr,(18,37,39) if selected_row else (10,19,25),TEAL if selected_row else EDGE)
                self.label(name,842,y+7,11,TEAL if selected_row else INK)
                self.buttons.append((rr,lambda pid=key:self.select_renown_planet(pid),True))
                y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((1122,198,8,425),self.ui_scroll['renown'],max_scroll)
        self._register_scrollbar('renown',(1122,198,8,425),self.ui_scroll['renown'],max_scroll)

    def select_renown_planet(self, planet_id):
        if planet_id in self.state.visited_planet_ids():
            self.state.selected_planet = planet_id
            self.ui_scroll['renown'] = self.ui_scroll.get('renown', 0)

    def claim_renown(self,scope,key,index):
        ok,msg=self.state.claim_renown_reward(scope,key,index); self.set_message(msg)
        if ok: self.checkpoint()

    def statistics_view(self):
        self.panel_header('ESTATÍSTICAS', 'Registros da campanha organizados por contexto e mantidos separados das conquistas.')
        cats=('Combate','Coleção','Planetas','Civilizações','Facções','Missões')
        x_positions=(35,220,405,590,775,960)
        for x,cat in zip(x_positions,cats):
            self.button((x,100,165,34),cat.upper(),lambda c=cat:(setattr(self,'statistics_category',c),setattr(self,'ui_scroll', {**self.ui_scroll,'statistics':0})),True)
        self.box((35,150,1130,540),(7,15,22),EDGE)
        view=pygame.Rect(58,190,1080,470)
        cat=self.statistics_category
        st=self.state.statistics
        rows=[]
        if cat=='Combate':
            bosses_defeated = sum(max(0, int(v)) for v in st.get('bosses_defeated', {}).values() if isinstance(v, (int, float)))
            rows=[
                ('Batalhas iniciadas',st.get('battles_started',0)),
                ('Vitórias',st.get('battles_won',0)),
                ('Fugas',st.get('battles_fled',0)),
                ('Acertos críticos',st.get('critical_hits',0)),
                ('Maior dano causado',st.get('max_damage_dealt',0)),
                ('Maior dano sofrido',st.get('max_damage_taken',0)),
                ('Bosses derrotados',bosses_defeated),
            ]
        elif cat=='Coleção':
            rows=[
                ('Itens coletados',sum(st.get('collectibles',{}).values())),
                ('Tipos de recurso registrados',len(st.get('collectibles',{}))),
                ('Cartas fabricadas',sum(st.get('cards_crafted',{}).values())),
                ('Cartas normais',st.get('cards_crafted',{}).get('normal',0)),
                ('Cartas +',st.get('cards_crafted',{}).get('plus',0)),
                ('Cartas ++',st.get('cards_crafted',{}).get('plusplus',0)),
                ('Cartas conhecidas',len(self.state.known_cards)),
                ('Criaturas no Bestiário',len(self.state.bestiary_known)),
            ]
        elif cat=='Planetas':
            visited_sectors = set(self.state.visited)
            visited_planets = sum(
                1 for route in STELLAR_ROUTES
                if route.get('landing_sector') in visited_sectors
                or (route.get('id') != 'veyra' and any(sid.startswith(route['id'] + '_') for sid in visited_sectors))
            )
            rows=[
                ('Planetas conhecidos',len(self.state.known_planets)),
                ('Planetas visitados',visited_planets),
                ('Mapas visitados',len(visited_sectors)),
                ('Mapas disponíveis',len(SECTORS)),
            ]
        elif cat=='Civilizações':
            known_civs = {civ for civs in self.state.known_civilizations_by_planet.values() for civ in civs}
            rows=[
                ('Civilizações conhecidas',len(known_civs)),
                ('Assentamentos descobertos',len(self.state.society.get('discovered_settlements',[]))),
                ('Habitantes vistos',len(self.state.society.get('seen_npcs',[]))),
                ('Idiomas dominados',1 if self.state.language_mastered else 0),
            ]
        elif cat=='Facções':
            discovered_factions = {data.get('faction') for data in SECTORS.values() if data.get('settlement') and data.get('faction')}
            conflicts_resolved = sum(1 for mission in self.state.missions.values() if isinstance(mission, dict) and mission.get('winner'))
            rows=[
                ('Facções conhecidas',len(discovered_factions)),
                ('Renome: Guardiões dos Reservatórios',self.state.renown_by_faction.get('waterkeepers',0)),
                ('Renome: Filhos da Fenda',self.state.renown_by_faction.get('rift_children',0)),
                ('Renome planetário total',sum(self.state.renown_planets.values())),
                ('Renome das galáxias',sum(self.state.renown_galaxies.values())),
                ('Conflitos de facção resolvidos',conflicts_resolved),
            ]
        else:
            active_statuses={'active','tracking','water','boss_ready','resolving'}
            missions_active=sum(1 for mission in self.state.missions.values() if isinstance(mission,dict) and mission.get('status') in active_statuses)
            rows=[
                ('Missões concluídas',st.get('missions_completed',0)),
                ('Missões falhadas',st.get('missions_failed',0)),
                ('Missões em andamento',missions_active),
                ('Caminho: Restaurar',st.get('mission_paths',{}).get('repair',0)),
                ('Caminho: Força',st.get('mission_paths',{}).get('force',0)),
                ('Caminho: Hack',st.get('mission_paths',{}).get('hack',0)),
            ]
        row_h=36; max_scroll=max(0,len(rows)*row_h-view.height); self.ui_scroll['statistics']=max(0,min(self.ui_scroll.get('statistics',0),max_scroll))
        self.canvas.set_clip(view); y=view.y-int(self.ui_scroll['statistics'])
        for name,value in rows:
            self.box((58,y,1060,30),(14,25,31),EDGE); self.label(str(name),72,y+7,12,INK); self.label(str(value),610,y+7,12,TEAL if str(value).upper() in ('SIM','VISITADO') else GOLD); y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((1128,190,10,470),self.ui_scroll['statistics'],max_scroll); self._register_scrollbar('statistics',(1128,190,10,470),self.ui_scroll['statistics'],max_scroll)

    def open_civilization_missions(self):
        civ=self.civ_mission_civ or (self.dialogue_npc or {}).get('civilization')
        if not civ:
            self.set_message('Nenhuma civilização disponível.')
            return
        if not self.state.knows_language(civ):
            self.set_message('Idioma ainda não calibrado.')
            return
        self.civ_mission_civ=civ; self.open_panel('civilization_missions','dialogue')

    def civilization_missions_view(self):
        civ=self.civ_mission_civ
        if not civ or not self.state.knows_language(civ):
            self.close_panel(); return
        self.state.refresh_civilization_missions(civ); data=self.state.civilization_missions.get(civ,{})
        self.panel_header('PEDIDOS', f'Pedidos de {CIVILIZATIONS.get(civ,{}).get("name",civ)}.')
        self.box((55,108,1090,585),(7,15,22),EDGE)
        remaining=max(0,7200-int(__import__('time').time())+int(data.get('generated_at',0)))
        self.label(f'PRÓXIMA ATUALIZAÇÃO  {remaining//3600:02d}:{(remaining%3600)//60:02d}:{remaining%60:02d}',78,130,11,MUTED)
        active=data.get('active',[])
        y=162
        for m in active:
            self.box((78,y,680,82),(15,27,33),TEAL if m.get('status')=='ready' else EDGE)
            self.label(self.fit_text(m.get('description','Pedido'),12,560),94,y+12,12,INK)
            self.label(f'PROGRESSO {m.get("progress",0)}/{m.get("params",{}).get("target",1)}',94,y+42,10,TEAL if m.get('status')=='ready' else MUTED)
            if m.get('status')=='ready': self.button((570,y+22,170,36),'ENTREGAR',lambda mid=m['id']:self._claim_civ_mission(civ,mid),True)
            y+=92
        y=170 if not active else min(600,y+10)
        offers=[m for m in data.get('offers',[]) if m.get('status')=='available']
        view=pygame.Rect(785,160,330,470); self.canvas.set_clip(view)
        yy=view.y-int(self.ui_scroll.get('civilization_missions',0))
        for m in offers:
            h=112; self.box((785,yy,315,h),(12,22,29),GOLD if m.get('premium') else EDGE)
            self.label(('PREMIUM • ' if m.get('premium') else '')+'PEDIDO',800,yy+10,10,GOLD if m.get('premium') else TEAL)
            self.wrap(m.get('description',''),800,yy+30,270,10,INK,15)
            reward=m.get('reward',{}); self.label(f'+{reward.get("item_amount",0)} {reward.get("item","Sucata")} • +{reward.get("Essência",0)} Ess.',800,yy+82,9,MUTED)
            self.button((935,yy+80,150,28),'ACEITAR',lambda mid=m['id']:self._accept_civ_mission(civ,mid),True)
            yy+=h+10
        self.canvas.set_clip(None)
        max_scroll=max(0,len(offers)*122-view.height); self._draw_scrollbar((1122,160,8,470),self.ui_scroll.get('civilization_missions',0),max_scroll); self._register_scrollbar('civilization_missions',(1122,160,8,470),self.ui_scroll.get('civilization_missions',0),max_scroll)
        self.button((78,640,220,40),'VOLTAR',self.close_panel,True)

    def _accept_civ_mission(self,civ,mid):
        ok,msg=self.state.accept_civilization_mission(civ,mid); self.set_message(msg)
        if ok: self.checkpoint()

    def _claim_civ_mission(self,civ,mid):
        ok,msg=self.state.claim_civilization_mission(civ,mid); self.set_message(msg)
        if ok: self.checkpoint()

    def bestiary(self):
        self.panel_header('BESTIÁRIO', 'Somente criaturas derrotadas entram na lista. O Elmo e o Scan determinam os dados técnicos revelados.')
        left=pygame.Rect(35,110,795,590); right=pygame.Rect(850,110,315,590)
        self.box(left,(7,15,22),EDGE); self.box(right,(7,15,22),EDGE)
        defeated=[sid for sid in self.state.bestiary_known if sid in SPECIES and self.state.kills.get(sid,0)>0]
        defeated.sort(key=lambda sid: (str(SPECIES[sid].get('type','')), str(SPECIES[sid].get('name',''))))
        if self.bestiary_selected not in defeated:
            self.bestiary_selected=defeated[0] if defeated else None
        self.label('CRIATURAS DERROTADAS',873,136,17,GOLD)
        view=pygame.Rect(870,165,270,485); row_h=48
        max_list=max(0,len(defeated)*row_h-view.height)
        self.ui_scroll['bestiary_list']=max(0,min(self.ui_scroll.get('bestiary_list',0),max_list))
        self.canvas.set_clip(view); y=view.y-int(self.ui_scroll['bestiary_list'])
        for sid in defeated:
            sp=SPECIES[sid]; selected=sid==self.bestiary_selected
            rect=pygame.Rect(view.x,int(y),view.width-4,40)
            self.box(rect,(18,38,39) if selected else (14,25,31),TEAL if selected else EDGE)
            self.label(sp['name'],rect.x+10,rect.y+7,11,TEAL if selected else INK)
            self.label(f'{sp.get("type","—")}  •  {self.state.kills.get(sid,0)} derrota(s)',rect.x+10,rect.y+24,9,MUTED)
            self.buttons.append((rect,lambda species=sid:(setattr(self,'bestiary_selected',species),self.ui_scroll.__setitem__('bestiary_detail',0)),True))
            y+=row_h
        self.canvas.set_clip(None); self._draw_scrollbar((1145,165,9,485),self.ui_scroll['bestiary_list'],max_list); self._register_scrollbar('bestiary_list',(1145,165,9,485),self.ui_scroll['bestiary_list'],max_list)
        if not self.bestiary_selected:
            self.label('Nenhuma criatura derrotada ainda.',60,210,18,MUTED); return
        sid=self.bestiary_selected; sp=SPECIES[sid]; card=CARDS.get(sp.get('card'),{})
        image_box=pygame.Rect(58,145,749,225); self.box(image_box,(10,20,27),EDGE)
        self.actor(sid,image_box.centerx,300,scale=3.5,frame=int(self.frame)%2)
        self.label(sp['name'],78,385,20,TEAL); self.label(f'TIPO: {sp.get("type","—")}   |   DERROTAS: {self.state.kills.get(sid,0)}',78,412,11,GOLD)
        scanned=sid in self.state.bestiary_scanned
        visited_maps = {
            SECTORS[k]['name'] for k,d in SECTORS.items()
            if k in self.state.visited and any((e.get('species') if isinstance(e,dict) else e[0]) == sid for e in d.get('spawns', []))
        }
        text=[f'MAPA(S) VISITADO(S): {", ".join(sorted(visited_maps)) or "—"}.',
              '', f'ATAQUE BÁSICO: {sp["attack"][0]}–{sp["attack"][1]}', f'TÉCNICA: {card.get("name","—")} — {card.get("damage",(0,0))[0]}–{card.get("damage",(0,0))[1]}']
        if scanned:
            text += [f'HP: {sp.get("hp","—")}   |   DEF: {sp.get("defense","—")}   |   PREC: {sp.get("precision","—")}',
                     f'TAXA CRÍTICA: {float(sp.get("crit_rate",0)):.1f}%   |   DANO CRÍTICO: {float(sp.get("crit_damage",1.0)):.2f}x',
                     f'MANA: {int(sp.get("mana_max",0))}   |   CUSTO DA TÉCNICA: {int(sp.get("mana_cost",0))}   |   CHANCE: {float(sp.get("special_chance",0)):.0f}%',
                     '', f'EFEITO DA TÉCNICA: {card.get("description","-")}']
            if getattr(self.state,'helmet_advanced_research_unlocked',False):
                vd=sp.get('vital_rupture',{})
                text += ['', 'PESQUISA AVANÇADA', f'PONTO VITAL: {sp.get("target_zones",{}).get(sp.get("vital_zone"),{}).get("name", sp.get("vital_zone","—"))}', f'RUPTURA: {vd.get("description","—")}']
        else:
            text += ['', 'DADOS TÉCNICOS OCULTOS.', 'Crie e equipe o Elmo e use o Scan nesta criatura para analisar HP, DEF, PREC, Mana e parâmetros da técnica.']
        self.label('DADOS REGISTRADOS',78,445,15,GOLD)
        self._draw_scroll_text_box((78,470,700,190),'\n'.join(text),'bestiary_detail',11,INK,18)

    def victory(self):
        """Tela final do combate: drop discreto, estatísticas categorizadas e retrato do herói."""
        self.label('RESULTADO DO COMBATE', 35, 28, 28, TEAL)
        self.label('Registro final do confronto.', 35, 70, 16, MUTED)

        # Drop compacto no topo, sem ocupar a maior parte da tela.
        self.box((35,108,1130,62),(7,15,22),EDGE)
        self.label('DROP',58,123,10,GOLD)
        if self.loot:
            parts=[f'+{qty} {name}' for name,qty in self.loot.items()]
            self.label(self.fit_text('  •  '.join(parts),11,1000),58,145,11,TEAL)
        else:
            self.label('Nenhum item recuperado.',58,145,11,MUTED)

        summary=self.last_combat_summary or self.combat_summary or self._new_combat_summary()
        total_dealt=int(summary.get('dealt',0)); total_taken=int(summary.get('taken',0))
        turns=max(1, int(summary.get('turns',0)))
        avg_damage=total_dealt / turns
        attacks=int(summary.get('attacks',0)); misses=int(summary.get('misses',0)); crits=int(summary.get('critical_hits',0))
        enemy_attacks=int(summary.get('enemy_attacks',0)); enemy_misses=int(summary.get('enemy_misses',0))
        dealt_dot=int(summary.get('dealt_dot',0)); dealt_critical=int(summary.get('dealt_critical',0))
        taken_dot=int(summary.get('taken_dot',0)); taken_critical=int(summary.get('taken_critical',0))
        pct=lambda part,total: f'{(part/total*100.0 if total else 0.0):.1f}%'

        # Caixa de dados menor e alinhada à esquerda; a leitura fica em linhas independentes.
        stats_box=pygame.Rect(35,190,700,465)
        self.box(stats_box,(7,15,22),EDGE)
        self.label('DADOS DO COMBATE',58,210,18,GOLD)
        view=pygame.Rect(55,240,660,390)

        rows=[]
        rows.append(('header','NEXUS'))
        rows += [('row',f'XP adquirida: {int(summary.get("nexus_xp_gained",0))}'),
                 ('row',f'XP total: {int(summary.get("nexus_xp_total", getattr(self.state, "gauntlet_nexus_xp", 0)) or 0)}'),
                 ('row',f'Falta para o próximo nível: {int(summary.get("nexus_xp_to_next",0))}')]
        domain_element = summary.get('domain_element')
        if domain_element in DOMAIN_ELEMENTS:
            rows.append(('header',f'DOMÍNIO — {domain_element.upper()}'))
            rows += [('row',f'XP adquirida: {int(summary.get("domain_xp_gained",0))}'),
                     ('row',f'XP total: {int(summary.get("domain_xp_total",0))}'),
                     ('row',f'Falta para o próximo nível: {int(summary.get("domain_xp_to_next",0))}')]
        rows.append(('header','TURNOS'))
        rows.append(('row',f'Turnos de combate: {turns}'))
        rows.append(('header','ATAQUE'))
        rows += [('row',f'Ataques realizados: {attacks}'),
                 ('row',f'Acertos: {max(0,attacks-misses)}'),
                 ('row',f'Erros: {misses}'),
                 ('row',f'Dano causado: {total_dealt}'),
                 ('row',f'Dano médio por turno: {avg_damage:.1f}'),
                 ('row',f'Dano direto: {max(0,total_dealt-dealt_dot)} ({pct(max(0,total_dealt-dealt_dot),total_dealt)})'),
                 ('row',f'Dano contínuo: {dealt_dot} ({pct(dealt_dot,total_dealt)})')]
        elemental=summary.get('dealt_elemental',{}) or {}
        for element in CREATURE_TYPES:
            qty=int(elemental.get(element,0))
            if qty:
                rows.append(('row',f'{element}: {qty} dano ({pct(qty,total_dealt)})'))
        untyped=int(summary.get('dealt_untyped',0))
        if untyped:
            rows.append(('row',f'Sem tipo: {untyped} dano ({pct(untyped,total_dealt)})'))
        if dealt_dot:
            dot_fogo=int((summary.get('dealt_dot_elemental',{}) or {}).get('Fogo',0))
            if dot_fogo:
                rows.append(('row',f'Contínuo — Fogo / Queimadura: {dot_fogo} dano ({pct(dot_fogo,total_dealt)})'))

        rows.append(('header','CRÍTICO'))
        rows += [('row',f'Ataques críticos: {crits}'),
                 ('row',f'Taxa crítica observada: {pct(crits,attacks)}'),
                 ('row',f'Dano crítico: {dealt_critical} ({pct(dealt_critical,total_dealt)})'),
                 ('row',f'Maior dano em um acerto: {int(summary.get("max_hit",0))}'),
                 ('row',f'Dano de vantagem: {int(summary.get("advantage_damage",0))}'),
                 ('row',f'Acertos com vantagem: {int(summary.get("advantage_hits",0))}')]

        rows.append(('header','DEFESA'))
        rows += [('row',f'Dano sofrido: {total_taken}'),
                 ('row',f'Dano direto sofrido: {max(0,total_taken-taken_dot)} ({pct(max(0,total_taken-taken_dot),total_taken)})'),
                 ('row',f'Dano contínuo sofrido: {taken_dot} ({pct(taken_dot,total_taken)})')]
        taken_elemental=summary.get('taken_elemental',{}) or {}
        for element in CREATURE_TYPES:
            qty=int(taken_elemental.get(element,0))
            if qty:
                rows.append(('row',f'Recebido — {element}: {qty} dano ({pct(qty,total_taken)})'))
        taken_untyped=int(summary.get('taken_untyped',0))
        if taken_untyped:
            rows.append(('row',f'Recebido — Sem tipo: {taken_untyped} dano ({pct(taken_untyped,total_taken)})'))
        rows += [('row',f'Ataques inimigos: {enemy_attacks}'),
                 ('row',f'Acertos inimigos: {max(0,enemy_attacks-enemy_misses)}'),
                 ('row',f'Erros inimigos: {enemy_misses}'),
                 ('row',f'Ataques inimigos críticos: {int(summary.get("taken_critical_hits",0))}'),
                 ('row',f'Dano crítico sofrido: {taken_critical} ({pct(taken_critical,total_taken)})'),
                 ('row',f'Cura obtida: {int(summary.get("healing",0))}'),
                 ('row',f'Cura por Vampirismo: {int(summary.get("vampirism_healing",0))}'),
                 ('row',f'Dano protegido por escudo: {int(summary.get("shield_absorbed",0))}'),
                 ('row',f'Dano reduzido por técnicas: {int(summary.get("technique_damage_reduced",0))}'),
                 ('row',f'Vida final: {int(self.state.hp)} / {int(self.state.max_hp)}')]

        line_h=22; header_h=28
        content_h=0
        for kind,_ in rows: content_h += header_h if kind=='header' else line_h
        max_scroll=max(0,content_h-view.height)
        scroll=max(0,min(int(self.ui_scroll.get('combat_result',0)),max_scroll)); self.ui_scroll['combat_result']=scroll
        self.canvas.set_clip(view)
        yy=view.y-scroll
        for kind,text in rows:
            if kind=='header':
                self.label(text,view.x,yy,14,GOLD); yy+=header_h
            else:
                self.label(self.fit_text(text,12,view.width-20),view.x+10,yy+2,12,INK); yy+=line_h
        self.canvas.set_clip(None)
        sb=pygame.Rect(view.right-7,view.y+4,5,max(1,view.height-8))
        self._draw_scrollbar(sb,scroll,max_scroll); self._register_scrollbar('combat_result',sb,scroll,max_scroll)

        # Retrato do personagem permanece no pós-combate, reaproveitando a pose de batalha.
        hero_box=pygame.Rect(760,190,405,465)
        self.box(hero_box,(7,15,22),EDGE)
        self.label('VOCÊ',785,215,18,TEAL)
        self.label(f'VIDA {int(self.state.hp)}/{int(self.state.max_hp)}',785,244,11,INK)
        self.bar(785,263,355,max(0,int(self.state.hp)),max(1,int(self.state.max_hp)),(203,112,94))
        self.label('REGISTRO VISUAL',785,304,10,GOLD)
        self.actor('hero',962,535,3.25,int(self.frame*5),pose='combat')
        self.label('Manopla / AURORA',785,610,10,MUTED)

        self.button((890,688,275,48),'VOLTAR AO JOGO',lambda:(setattr(self,'victory_boss',None),self.reset_mode('world')),True)

    def install_dobra_core_ui(self):
        ok, msg = self.state.install_dobra_core()
        self.set_message(msg)
        if ok:
            self.selected_route_id = self.state.selected_planet
            self.close_panel()
            self.checkpoint()

    def start_ship_mission_ui(self, mission_id):
        ok, msg = self.state.start_ship_mission(mission_id)
        if not ok:
            self.set_message(msg)
            return
        system = SHIP_MISSION_DATA[mission_id]['system']
        self.set_message(f'ANÁLISE DA MANOPLA: {SHIP_SYSTEMS[system]["name"]} requer intervenção. {msg}')
        self.ship_mission_id = mission_id
        if mission_id in ('ship_navigation','ship_comms'):
            self.close_panel()
        else:
            self.open_panel('ship_mission', 'ship_diag')
        self.checkpoint()

    def ship_mission(self):
        mid = self.ship_mission_id or 'ship_hull'
        data = SHIP_MISSION_DATA.get(mid, {})
        mission = self.state.missions.get(mid, {})
        self.panel_header(data.get('title','MISSÃO DA NAVE'), data.get('objective',''))
        self.box((80,120,1040,550),(7,15,22),EDGE)
        self.label(data.get('system','').replace('_',' ').upper(), 115, 150, 12, GOLD)
        status=mission.get('status','locked')
        if status=='completed':
            self.label('SISTEMA OPERACIONAL — 100%',115,185,24,TEAL)
            self.button((115,575,300,42),'VOLTAR',self.close_panel,True)
            return
        if mid=='ship_hull':
            prog=int(mission.get('progress',0)); self.label(f'PULSOS SINCRONIZADOS  {prog}/3',115,195,20,TEAL)
            center_y=310; width=700; left=245; phase=(self.frame*1.6)%1.0; marker=left+int(width*phase)
            pygame.draw.rect(self.canvas,(14,24,31),(left,center_y,width,14),border_radius=6)
            pygame.draw.rect(self.canvas,(71,105,109),(left+int(width*.40),center_y, int(width*.20),14),border_radius=6)
            pygame.draw.line(self.canvas,GOLD,(marker,center_y-15),(marker,center_y+29),3)
            self.label('Pressione ESPAÇO quando o marcador entrar na faixa central.',115,365,14,INK)
        elif mid=='ship_power':
            vals=list(mission.get('values',[20,30,25,25])); self.label('BARRAMENTOS',115,190,20,TEAL); self.label('Use 1–4 para selecionar. ←/→ ajusta 5%.',115,222,13,MUTED)
            names=['PRIMÁRIO','SENSORIAL','PROPULSÃO','SISTEMAS']; total=sum(vals)
            for i,(name,val) in enumerate(zip(names,vals)):
                y=275+i*63; self.label(f'{i+1}  {name}',130,y,12,INK); self.bar(295,y+2,470,val,50,GOLD if val<15 or val>35 else TEAL); self.label(f'{val}%',785,y,13,INK)
            self.label(f'TOTAL {total}%',130,535,15,TEAL if total==100 and all(15<=v<=35 for v in vals) else MUTED)
            self.button((840,520,210,45),'ESTABILIZAR',lambda:self._ship_power_try(), total==100 and all(15<=v<=35 for v in vals))
        elif mid=='ship_propulsion':
            seq=mission.get('sequence',['up','right','down','left']); cur=int(mission.get('cursor',0));
            self.label(f'VETOR {cur+1}/4',115,195,22,TEAL); self.label(' → '.join(x.upper() for x in seq),115,250,19,GOLD); self.label('Use as setas na sequência exibida.',115,300,14,INK)
        elif mid=='ship_ftl':
            prog=int(mission.get('progress',0)); self.label(f'JANELAS ESTABILIZADAS  {prog}/3',115,195,20,TEAL)
            left=245; width=700; y=315; phase=(self.frame*2.1)%1.0; marker=left+int(width*phase)
            pygame.draw.rect(self.canvas,(14,24,31),(left,y,width,16),border_radius=7)
            pygame.draw.rect(self.canvas,(72,107,115),(left+int(width*.45),y,int(width*.10),16),border_radius=7)
            pygame.draw.line(self.canvas,GOLD,(marker,y-16),(marker,y+32),3)
            self.label('Pressione ESPAÇO dentro da janela de ressonância.',115,375,14,INK)
        elif mid=='ship_navigation':
            self.label('Acesse o COCKPIT para reparar a referência estelar.',115,195,20,TEAL)
            self.label('CUSTO: 80 SUCATAS',115,240,16,GOLD)
            owned = self.state.inventory.get('Sucata', 0)
            self.label(f'SUCATA {owned}/80', 115, 279, 13, TEAL if owned >= 80 else (224,112,93))
            self.button((115,320,310,48),'REPARAR COM 80 SUCATAS',self._ship_navigation_try,True)
        elif mid=='ship_comms':
            defeated=self.state.communication_guards_defeated(); self.label(f'SENTINELAS ELIMINADAS  {defeated}/4',115,195,20,TEAL)
            self.label('Vá ao MORRO DA ANTENA a oeste da nave.',115,240,15,INK)
            self.label('Após derrotar as quatro, acione a antena.',115,280,15,INK)
        self.button((115,575,300,42),'VOLTAR',self.close_panel,True)

    def _ship_navigation_try(self):
        if self.state.inventory.get('Sucata', 0) < 80:
            self.set_message('A Manopla exige 80 unidades de Sucata para reparar a referência estelar.')
            return
        ok, msg = self.state.navigation_repair()
        self.set_message(msg)
        if ok:
            self.close_panel()
            self.checkpoint()

    def _ship_power_try(self):
        mission=self.state.missions.get('ship_power',{}); vals=mission.get('values',[20,30,25,25])
        if sum(vals)==100 and all(15<=v<=35 for v in vals):
            ok,msg=self.state.complete_ship_mission('ship_power'); self.set_message(msg); self.close_panel(); self.checkpoint()
        else:
            self.set_message('A Manopla detectou carga fora da faixa segura.')

    def open_ship_communications(self):
        changed=self.state.reveal_communications()
        self.open_panel('ship_communications','ship')
        self.set_message('Rede de comunicação restaurada. Referências estelares recebidas.')
        if changed: self.checkpoint()

    def ship_communications(self):
        self.panel_header('COMUNICAÇÃO', 'Contatos de longa distância da Galáxia Nárion.')
        self.box((80,120,1040,550),(7,15,22),EDGE)
        self.label('CONTATOS DA GALÁXIA',115,155,20,GOLD)
        rows=[r for r in STELLAR_ROUTES]
        for i,r in enumerate(rows):
            y=205+i*72; self.box((115,y,950,54),(13,25,32),EDGE); self.label(r['name'].upper(),135,y+16,15,TEAL); self.label('CONTATO DISPONÍVEL',760,y+16,11,GOLD)
        self.button((115,590,300,42),'VOLTAR',self.close_panel,True)

    def ship_computer(self):
        self.panel_header('COMPUTADOR', 'Funções internas da nave.')
        self.box((60, 108, 1080, 592), (7,15,22), EDGE)
        options=[
            ('EQUIPAMENTO', lambda:self.open_panel('equipment','ship')),
            ('PROJETOS TECNOLÓGICOS', lambda:self.open_panel('tech','ship')),
            ('OFICINA / CRAFT', lambda:self.open_panel('craft','ship')),
            ('DIAGNÓSTICO DA NAVE', lambda:self.open_ship_diagnostic('ship')),
            ('SIMULADOR DE COMBATE', lambda:self.open_panel('simulator','ship')),
        ]
        if self.state.ship_systems.get('comms',0) >= 100:
            options.append(('COMUNICAÇÃO', self.open_ship_communications))
        positions=[(95,155),(630,155),(95,275),(630,275),(95,395),(630,395)]
        for (title,cb),pos in zip(options,positions):
            self.button((pos[0],pos[1],475,78),title,cb,True)
        self.button((95,565,300,40),'SALVAR CAMPANHA',self.save,True)
        self.button((805,565,300,40),'ESCOTILHA',lambda:(self.state.leave_ship(), setattr(self,'mode','world')),True)

    def select_stellar_route(self, route_id):
        route = next((r for r in STELLAR_ROUTES if r['id']==route_id), None)
        if not route:
            return
        self.selected_route_id = route_id
        self.state.selected_planet = route_id
        self.set_message((route['name'] if route_id in self.state.known_planets else 'Destino não identificado: ???') + '.')

    def start_planet_travel(self):
        target = self.selected_route_id
        ok, result = self.state.can_travel_to_planet(target)
        if not ok:
            self.set_message(result)
            return False
        self.travel_origin_planet = self.state.current_planet_id()
        self.travel_target_planet = target
        self.travel_time = 0.0
        self.travel_duration = 3.2
        self.travel_encounter_pending = bool(self.state.should_trigger_asteroid_encounter(target))
        self.travel_encounter_trigger = self.state.rng.uniform(0.8, 2.0) if self.travel_encounter_pending else 0.0
        self.travel_encounter_result = None
        self.asteroid_game = None
        self.mode = 'travel'
        self.nav_stack = ['cockpit']
        self._sync_navigation_context()
        self.set_message(f'Rota estelar confirmada: {result["name"]}.')
        return True

    def finish_planet_travel(self):
        target = self.travel_target_planet
        if not target:
            self.mode = 'cockpit'
            return
        result = self.travel_encounter_result
        ok, msg = self.state.arrive_at_planet(target)
        self.travel_target_planet = None
        self.travel_origin_planet = None
        self.travel_time = 0.0
        self.travel_encounter_pending = False
        self.travel_encounter_trigger = 0.0
        self.asteroid_game = None
        if ok:
            if isinstance(result, dict):
                self.state.resolve_asteroid_encounter(result.get('destroyed', 0), result.get('damage', 0))
                destroyed = int(result.get('destroyed', 0))
                damage = int(result.get('damage', 0))
                if damage:
                    msg = f'{msg}  Asteroides: {destroyed} destruídos • dano sofrido: {damage}.'
                else:
                    msg = f'{msg}  Asteroides: {destroyed} destruídos.'
            self.travel_encounter_result = None
            self.mode = 'world'
            self.nav_stack = []
            self._sync_navigation_context()
            self.sync_sector()
            self.set_message(msg)
            self.checkpoint()
        else:
            self.travel_encounter_result = None
            self.mode = 'cockpit'
            self.nav_stack = []
            self._sync_navigation_context()
            self.set_message(msg)

    def start_asteroid_encounter(self):
        if self.mode != 'travel' or not self.travel_encounter_pending:
            return False
        self.travel_encounter_pending = False
        self.asteroid_game = {
            'player_x': W // 2,
            'player_y': H - 92,
            'elapsed': 0.0,
            'duration': 8.5,
            'spawn_timer': 0.0,
            'fire_cooldown': 0.0,
            'invuln': 0.0,
            'destroyed': 0,
            'damage': 0,
            'shots': [],
            'asteroids': [],
            'stars': [(int((i * 173) % W), int((i * 97) % H), 1 + (i % 2)) for i in range(55)],
        }
        self.mode = 'asteroids'
        self.set_message('ALERTA  //  CAMPO DE ASTEROIDES')
        return True

    def fire_asteroid_laser(self):
        game = self.asteroid_game
        if not game or game.get('fire_cooldown', 0.0) > 0.0:
            return
        game['shots'].append({'x': float(game['player_x']), 'y': float(game['player_y'] - 28), 'speed': 540.0})
        game['fire_cooldown'] = 0.18

    def _spawn_asteroid(self):
        game = self.asteroid_game
        if not game:
            return
        r = self.state.rng.randint(9, 22)
        game['asteroids'].append({
            'x': float(self.state.rng.randint(r + 18, W - r - 18)),
            'y': float(-r - 8),
            'r': r,
            'speed': float(self.state.rng.randint(185, 295)),
            'drift': float(self.state.rng.uniform(-35, 35)),
            'angle': float(self.state.rng.random() * math.tau),
        })

    def advance_asteroid_encounter(self, dt):
        game = self.asteroid_game
        if not game:
            self.mode = 'travel'
            return
        game['elapsed'] += dt
        game['spawn_timer'] -= dt
        game['fire_cooldown'] = max(0.0, game['fire_cooldown'] - dt)
        game['invuln'] = max(0.0, game['invuln'] - dt)
        keys = pygame.key.get_pressed()
        dx = 0.0
        if keys[pygame.K_LEFT]: dx -= 1.0
        if keys[pygame.K_RIGHT]: dx += 1.0
        game['player_x'] = max(42, min(W - 42, game['player_x'] + dx * 385.0 * dt))
        if game['spawn_timer'] <= 0.0:
            self._spawn_asteroid()
            game['spawn_timer'] = 0.48

        for shot in game['shots']:
            shot['y'] -= shot['speed'] * dt
        game['shots'] = [shot for shot in game['shots'] if shot['y'] > -30]

        for asteroid in game['asteroids']:
            asteroid['y'] += asteroid['speed'] * dt
            asteroid['x'] += asteroid['drift'] * dt
            asteroid['angle'] += dt * 1.8

        remaining_asteroids = []
        used_shots = set()
        for asteroid in game['asteroids']:
            hit = False
            for idx, shot in enumerate(game['shots']):
                if idx in used_shots:
                    continue
                if math.hypot(asteroid['x'] - shot['x'], asteroid['y'] - shot['y']) <= asteroid['r'] + 5:
                    used_shots.add(idx)
                    hit = True
                    game['destroyed'] += 1
                    break
            if hit:
                continue
            if game['invuln'] <= 0.0 and math.hypot(asteroid['x'] - game['player_x'], asteroid['y'] - game['player_y']) <= asteroid['r'] + 26:
                game['damage'] = min(6, game['damage'] + 1)
                game['invuln'] = 0.62
                continue
            if asteroid['y'] < H + asteroid['r'] + 10:
                remaining_asteroids.append(asteroid)
        game['asteroids'] = remaining_asteroids
        game['shots'] = [shot for idx, shot in enumerate(game['shots']) if idx not in used_shots]

        if game['elapsed'] >= game['duration']:
            destroyed, damage = game['destroyed'], game['damage']
            self.asteroid_game = None
            self.travel_encounter_result = {'destroyed': destroyed, 'damage': damage}
            self.mode = 'travel'
            self.set_message(f'CAMPO SUPERADO  //  {destroyed} destruídos  //  dano {damage}/6')

    def asteroid_encounter_scene(self):
        game = self.asteroid_game or {}
        self.canvas.fill((3, 8, 14))
        for x, y, radius in game.get('stars', []):
            pygame.draw.circle(self.canvas, (95, 125, 138), (x, y), radius)
        self.label('CAMPO DE ASTEROIDES', 44, 32, 28, TEAL)
        self.label(f'ESSÊNCIA  +{int(game.get("destroyed", 0))}', 44, 74, 14, GOLD)
        self.label(f'DANO  {int(game.get("damage", 0))}/6', 930, 74, 14, (224,112,93) if game.get('damage', 0) else INK)
        progress = max(0.0, min(1.0, float(game.get('elapsed', 0.0)) / max(0.1, float(game.get('duration', 1.0)))))
        pygame.draw.rect(self.canvas, (12,20,29), (44, 105, 1110, 6), border_radius=3)
        pygame.draw.rect(self.canvas, TEAL, (44, 105, int(1110 * progress), 6), border_radius=3)
        for asteroid in game.get('asteroids', []):
            cx, cy, r = int(asteroid['x']), int(asteroid['y']), int(asteroid['r'])
            points = []
            for i in range(8):
                ang = asteroid['angle'] + i * math.tau / 8.0
                rr = r * (0.78 + ((i * 17) % 31) / 100.0)
                points.append((int(cx + math.cos(ang) * rr), int(cy + math.sin(ang) * rr)))
            pygame.draw.polygon(self.canvas, (91, 83, 77), points)
            pygame.draw.polygon(self.canvas, (129, 119, 109), points, 1)
        for shot in game.get('shots', []):
            pygame.draw.line(self.canvas, (180,255,244), (int(shot['x']), int(shot['y'] + 8)), (int(shot['x']), int(shot['y'] - 12)), 3)
        px = int(game.get('player_x', W//2)); py = int(game.get('player_y', H-92))
        if float(game.get('invuln', 0.0)) <= 0.0 or int(self.frame * 16) % 2 == 0:
            self.ship(px, py, shadow=False)
        self.label('←  →  MOVER    //    ESPAÇO  DISPARAR', 392, 740, 13, GOLD)

    def travel_scene(self):
        self.canvas.fill((3,8,14))
        pulse = self.frame
        for i in range(95):
            x = int((i*137 + 37) % W)
            base_y = int((i*71 + 83) % H)
            speed = 18 + (i % 7)*9
            yy = int((base_y + pulse*speed) % H)
            brightness = 95 + (i % 5)*28
            pygame.draw.circle(self.canvas, (brightness, min(255,brightness+18), min(255,brightness+28)), (x, yy), 1 if i%6 else 2)
        origin = next((r for r in STELLAR_ROUTES if r['id']==self.travel_origin_planet), STELLAR_ROUTES[0])
        target = next((r for r in STELLAR_ROUTES if r['id']==self.travel_target_planet), STELLAR_ROUTES[0])
        t = max(0.0, min(1.0, self.travel_time/max(0.01,self.travel_duration)))
        # Planeta de destino crescendo no horizonte.
        px, py = 980, 405
        planet_colors = {'veyra':(201,139,94),'orionis':(202,77,50),'kael':(104,157,194),'nahr':(129,78,58),'elyra':(95,173,151)}
        pcol = planet_colors.get(target['id'], (110,150,170))
        radius = int(72 + 8*math.sin(t*math.pi))
        pygame.draw.circle(self.canvas, pcol, (px,py), radius)
        pygame.draw.circle(self.canvas, tuple(min(255,c+35) for c in pcol), (px-16,py-18), max(2,radius//3))
        pygame.draw.arc(self.canvas, tuple(max(0,c-35) for c in pcol), (px-radius,py-radius,2*radius,2*radius), 0.2, 2.5, 2)
        pygame.draw.line(self.canvas, (65,144,170), (170,400), (900,400), 1)
        # A nave pequena, sempre orientada para a direita durante a viagem.
        ship_x = int(150 + 720*t)
        ship_y = int(400 + math.sin(t*math.pi*2)*22)
        self.ship(ship_x, ship_y, shadow=False)
        self.label('NAVEGAÇÃO ESTELAR', 44, 36, 30, TEAL)
        self.label(f'{origin["name"].upper()}  →  {target["name"].upper()}', 46, 82, 18, GOLD)
        self.label('ROTA CONFIRMADA', 46, 610, 12, MUTED)
        self.label(f'VELOCIDADE DE CRUZEIRO  //  {int(100+t*900)} u/s', 46, 633, 13, INK)
        self.label(f'TEMPO DE VOO  //  {max(0.0,self.travel_duration-self.travel_time):.1f}s', 46, 657, 13, MUTED)
        progress = pygame.Rect(46, 690, 730, 7)
        pygame.draw.rect(self.canvas, (12,20,29), progress, border_radius=3)
        pygame.draw.rect(self.canvas, TEAL, (progress.x,progress.y,int(progress.width*t),progress.height), border_radius=3)
        if self.travel_encounter_pending:
            self.label('SINAL DE PERIGO  //  ASTEROIDES DETECTADOS', 900, 700, 12, (224,112,93))
            self.label('ESPAÇO  //  INICIAR INTERCEPÇÃO', 900, 722, 10, GOLD)
        else:
            self.label('ESPAÇO  //  PULAR NAVEGAÇÃO', 900, 700, 12, GOLD)

    def cockpit(self):
        self.panel_header('COCKPIT', 'Rota Estelar / selecione galáxias e planetas pela lista de destinos.')
        self.box((70, 108, 1060, 584), (6,14,20), EDGE)

        selected_gid = getattr(self.state, 'selected_galaxy_id', GALAXY_ID)
        if selected_gid not in GALAXIES or (selected_gid != GALAXY_ID and not self.state.dobra_core_installed):
            selected_gid = GALAXY_ID
            self.state.selected_galaxy_id = GALAXY_ID

        routes = [r for r in STELLAR_ROUTES if r.get('galaxy', GALAXY_ID) == selected_gid]
        selected = next((r for r in routes if r['id'] == self.selected_route_id), None)
        if selected is None:
            selected = next((r for r in routes if r['id'] == self.state.selected_planet), routes[0] if routes else STELLAR_ROUTES[0])
            self.selected_route_id = selected['id']

        # MAPA — área principal, sem os botões de galáxia sobrepostos.
        map_rect = pygame.Rect(95, 150, 655, 455)
        pygame.draw.rect(self.canvas, (8,20,29), map_rect, border_radius=10)
        pygame.draw.rect(self.canvas, (42,91,98), map_rect, 1, border_radius=10)
        galaxy_name=GALAXIES.get(selected_gid,{}).get('name',selected_gid)
        galaxy_surface=self.font(11).render(galaxy_name.upper(),True,MUTED)
        self.canvas.blit(galaxy_surface,(map_rect.x+16,map_rect.y+14))

        nav_ok = self.state.ship_systems.get('navigation',0) >= 100
        flight_ready = self.state.ship_flight_ready()
        led_ring = TEAL if nav_ok else (132,48,54)
        led_core = TEAL if nav_ok else (38,16,19)
        led_center = (map_rect.right-28, map_rect.bottom-24)
        pygame.draw.circle(self.canvas,led_ring,led_center,8,1)
        pygame.draw.circle(self.canvas,led_core,led_center,4)
        self.label('NAV',map_rect.right-66,map_rect.bottom-31,9,MUTED)

        posmap={r['id']:r['pos'] for r in routes}
        for a,b in GALAXY_CONNECTIONS.get(selected_gid,()):
            if a in posmap and b in posmap:
                pygame.draw.line(self.canvas,(43,73,82),posmap[a],posmap[b],1)
        for r in routes:
            x,y=r['pos']
            known=r['id'] in self.state.known_planets
            is_selected=r['id']==self.selected_route_id
            base=GOLD if is_selected else (TEAL if known else EDGE)
            pygame.draw.circle(self.canvas,(7,14,20),(x,y),10 if is_selected else 7,1)
            pygame.draw.circle(self.canvas,base,(x,y),4 if known else 2)
            sel_name=r['name'] if known else '???'
            self.label(sel_name.upper(),x+14,y-8,10,base)
            self.buttons.append((pygame.Rect(x-16,y-16,32,32),lambda rid=r['id']:self.select_stellar_route(rid),known))

        # LISTA HIERÁRQUICA — mesma lógica visual do menu Renome:
        # galáxia como cabeçalho e planetas como linhas selecionáveis.
        list_rect = pygame.Rect(775, 150, 325, 270)
        self.box(list_rect, (11,21,28), EDGE)
        self.label('DESTINOS', 797, 172, 14, GOLD)
        list_view = pygame.Rect(790, 198, 295, 207)
        content=[]
        for gid in GALAXY_DISPLAY_ORDER:
            gdata=GALAXIES.get(gid,{})
            locked=(gid != GALAXY_ID and not self.state.dobra_core_installed)
            content.append(('galaxy',gid,gdata.get('name',gid),locked))
            for route in STELLAR_ROUTES:
                if route.get('galaxy',GALAXY_ID)==gid:
                    content.append(('planet',route['id'],route['name'],locked or route['id'] not in self.state.known_planets))
        row_h=25; header_h=25
        total_h=sum(header_h if typ=='galaxy' else row_h for typ,_,_,_ in content)
        max_scroll=max(0,total_h-list_view.height)
        self.ui_scroll['stellar_destinations']=max(0,min(self.ui_scroll.get('stellar_destinations',0),max_scroll))
        self.canvas.set_clip(list_view)
        y=list_view.y-int(self.ui_scroll['stellar_destinations'])
        for typ,key,name,locked in content:
            if typ=='galaxy':
                active=(key==selected_gid)
                rr=pygame.Rect(list_view.x,y,list_view.width,header_h-2)
                self.box(rr,(18,37,39) if active else (10,19,25),TEAL if active else EDGE)
                suffix='  //  BLOQUEADA' if locked else ''
                self.label(self.fit_text(name.upper()+suffix,10,rr.width-16),rr.x+8,rr.y+7,10,TEAL if active else (EDGE if locked else GOLD))
                self.buttons.append((rr,lambda gid=key:self.select_galaxy(gid),not locked))
                y+=header_h
            else:
                active=(key==self.selected_route_id)
                rr=pygame.Rect(list_view.x+14,y,list_view.width-14,row_h-2)
                self.box(rr,(18,37,39) if active else (10,19,25),TEAL if active else EDGE)
                display=name.upper() if key in self.state.known_planets else '???'
                self.label(self.fit_text(display,11,rr.width-16),rr.x+10,rr.y+7,11,TEAL if active else (MUTED if locked else INK))
                self.buttons.append((rr,lambda pid=key:self.select_stellar_route(pid),not locked))
                y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((1089,198,7,207),self.ui_scroll['stellar_destinations'],max_scroll)
        self._register_scrollbar('stellar_destinations',(1089,198,7,207),self.ui_scroll['stellar_destinations'],max_scroll)

        # Informações do destino em lista, sem bloco monolítico de texto.
        info_box=pygame.Rect(775, 435, 325, 170)
        self.box(info_box, (11,21,28), EDGE)
        known=selected['id'] in self.state.known_planets
        self.label('DESTINO SELECIONADO',797,456,12,GOLD)
        sel_name=selected['name'] if known else '???'
        self.label(self.fit_text(sel_name.upper(),16,275),797,480,18,TEAL if known else EDGE)
        civilizations = ', '.join(selected.get('initial_known_civilizations', [])) or 'Nenhuma catalogada'
        info_rows=[
            ('GALÁXIA', GALAXIES.get(selected.get('galaxy',GALAXY_ID),{}).get('name',selected.get('galaxy',GALAXY_ID))),
            ('ATMOSFERA', selected.get('atmosphere','—')),
            ('TEMPERATURA', selected.get('temperature','—')),
            ('LUAS', selected.get('moons','—')),
            ('CIVILIZAÇÕES CONHECIDAS', civilizations),
        ]
        yy=508
        for k,v in info_rows:
            self.label(k,797,yy,8,GOLD)
            self.label(self.fit_text(str(v) if known else 'NÃO CATALOGADO',10,220),905,yy-1,10,INK if known else MUTED)
            yy+=21

        # Faixa inferior: motor à esquerda e ação de voo à direita.
        core_box=pygame.Rect(95, 620, 655, 72)
        self.box(core_box,(11,21,28),EDGE)
        self.label('MOTOR DE DOBRA',117,638,10,GOLD)
        core_status='INSTALADO — VIAGENS INTERGALÁCTICAS LIBERADAS' if self.state.dobra_core_installed else 'AUSENTE — RECUPERE O NÚCLEO DE RY'
        self.label(self.fit_text(core_status,10,500),117,657,10,TEAL if self.state.dobra_core_installed else MUTED)

        current_id=self.state.current_planet_id()
        travel_damage = int(getattr(self.state, 'travel_damage', 0) or 0)
        if travel_damage > 0:
            flight='BLOQUEADA — NAVE DANIFICADA'; flight_color=(224,112,93)
        elif not flight_ready:
            flight='BLOQUEADA — RESTAURE A NAVE'; flight_color=(224,112,93)
        elif selected['id']==current_id:
            flight='PLANETA ATUAL'; flight_color=TEAL
        elif selected['id'] in self.state.known_planets:
            flight='ROTA DISPONÍVEL'; flight_color=TEAL
        else:
            flight='PLANETA NÃO CATALOGADO'; flight_color=MUTED
        can_fly=flight_ready and travel_damage == 0 and selected['id']!=current_id and selected['id'] in self.state.known_planets
        self.button((775,615,325,48),'VIAJAR PARA '+selected['name'].upper() if selected['id']!=current_id else 'PLANETA ATUAL',self.start_planet_travel,can_fly)
        self.label('STATUS DE VOO',775,675,9,MUTED)
        self.label(self.fit_text(flight,10,230),869,673,10,flight_color)

    def select_galaxy(self, galaxy_id):
        if galaxy_id != GALAXY_ID and not self.state.dobra_core_installed:
            self.set_message('Instale o Núcleo de Dobra no motor da nave para alcançar outras galáxias.')
            return
        self.state.selected_galaxy_id=galaxy_id
        self.state.selected_planet=next((r['id'] for r in STELLAR_ROUTES if r.get('galaxy',GALAXY_ID)==galaxy_id and r['id'] in self.state.known_planets), next(r['id'] for r in STELLAR_ROUTES if r.get('galaxy',GALAXY_ID)==galaxy_id))
        self.selected_route_id=self.state.selected_planet
        self.ui_scroll['stellar_destinations']=0

    def ship_diagnostic(self):
        self.label('STATUS DA NAVE', 35, 28, 28, TEAL)
        self.box((35, 128, 1130, 565), (7,15,22), EDGE)
        avg = int(sum(self.state.ship_systems.get(sid,0) for sid in SHIP_DIAGNOSTIC_ORDER) / len(SHIP_DIAGNOSTIC_ORDER))
        self.label('INTEGRIDADE GERAL', 880, 108, 13, GOLD); self.label(f'{avg}%', 1050,104,18,TEAL)
        travel_damage = int(getattr(self.state, 'travel_damage', 0) or 0)
        if travel_damage > 0:
            self.label('DANO DE VIAGEM', 620, 108, 11, GOLD)
            self.label(f'{travel_damage}/6', 735, 104, 16, (224,112,93))
        active_repairs = [
            SHIP_MISSION_DATA[mid]['title']
            for mid in SHIP_MISSION_DATA
            if self.state.missions.get(mid, {}).get('status') == 'active'
        ]
        self.label('REPAROS EM ANDAMENTO', 62, 142, 12, GOLD)
        if active_repairs:
            resumo = f'{len(active_repairs)} ativo(s)  •  ' + '  |  '.join(active_repairs)
            self.label(self.fit_text(resumo, 11, 770), 225, 141, 11, TEAL)
        else:
            self.label('Nenhum reparo em andamento.', 225, 141, 11, MUTED)
        self.label('SISTEMAS DE BORDO', 62, 172, 16, GOLD)
        for i,sid in enumerate(SHIP_DIAGNOSTIC_ORDER):
            row=SHIP_SYSTEMS[sid]; condition=int(self.state.ship_systems.get(sid,row['condition']))
            col=i%2; line=i//2; x=55+col*550; y=185+line*150
            self.box((x,y,525,128),(12,27,34),EDGE)
            color=TEAL if condition>=100 else GOLD if condition>=20 else (224,112,93)
            self.label(row['name'].upper(),x+18,y+14,15,INK)
            status='OPERACIONAL' if condition>=100 else row['status']
            self.label(f'{condition:>3}%  {status}',x+18,y+42,15,color)
            self.bar(x+18,y+72,290,condition,100,color)
            mid=f'ship_{sid}'
            mstatus=self.state.missions.get(mid,{}).get('status')
            if sid == 'ftl' and self.state.dobra_core_installed:
                self.label('NÚCLEO INSTALADO',x+335,y+25,10,TEAL)
                self.label('DOBRA INTERGALÁCTICA ONLINE',x+335,y+45,9,GOLD)
            elif sid == 'ftl' and self.state.inventory.get('Núcleo de Dobra',0) > 0:
                self.label('NÚCLEO DE DOBRA DETECTADO',x+335,y+25,10,GOLD)
                self.button((x+335,y+58,160,42),'INSTALAR',self.install_dobra_core_ui,True)
            elif condition>=100:
                self.label('CONCLUÍDO',x+340,y+75,10,TEAL)
            elif mstatus=='active':
                self.label('REPARO EM ANDAMENTO',x+335,y+39,9,GOLD)
                self.button((x+335,y+58,160,42),'CONTINUAR',lambda m=mid:self.start_ship_mission_ui(m),True)
            else:
                self.button((x+335,y+58,160,42),'VERIFICAR',lambda m=mid:self.start_ship_mission_ui(m),True)
        self.button((55, 645, 260, 42), 'ESC  Voltar', self.close_panel, True)
        if travel_damage > 0:
            enough_scrap = int(self.state.inventory.get('Sucata', 0)) >= travel_damage
            self.button((865, 645, 300, 42), f'REPARAR NAVE  •  {travel_damage} SUCATA', self.repair_travel_damage_ui, enough_scrap, 'Falta Sucata para concluir o reparo.' if not enough_scrap else 'Reparar os danos da última travessia.')
    def repair_travel_damage_ui(self):
        ok, message = self.state.repair_travel_damage()
        self.set_message(message)
        if ok:
            self.checkpoint()

    def future_upgrade_visible(self, upgrade_id):
        if upgrade_id == 'special_slot':
            return False
        if upgrade_id == 'dobra_core_install':
            return False
        if upgrade_id == 'helmet_g2':
            return self.state.helmet_generation >= 1
        if upgrade_id == 'chest_g3':
            return self.state.chest_generation >= 2
        if upgrade_id == 'memory_g3':
            return self.state.memory_owned.get('advanced', 0) >= 1
        if upgrade_id == 'ship_laser':
            return bool(self.state.ship_laser_project_unlocked)
        return True

    def _craft_from_technology_laser(self):
        message = self.state.craft('ship_laser')
        self.set_message(message)
        if 'instalado' in message.lower():
            self.checkpoint()

    def _craft_from_technology_nexus(self):
        message = self.state.craft('gauntlet_nexus')
        self.set_message(message)
        if message.startswith('Fabricado:') or 'instalado' in message.lower() or 'senciência' in message.lower():
            self.checkpoint()

    def technology(self):
        self.panel_header('PROJETOS TECNOLÓGICOS', 'Blueprints conhecidos pela Manopla. Alguns projetos já podem ser fabricados; outros dependem de recursos de mundos futuros.')
        self.box((35, 110, 1130, 590))
        self.label('PROJETOS E MATERIAIS DE PROGRESSÃO', 58, 132, 20, GOLD)
        self.wrap('Alguns componentes atuais continuam úteis, mas os próximos saltos de tecnologia exigirão materiais que o personagem ainda não encontrou. Isso impede que toda evolução possa ser resolvida apenas farmando o planeta inicial.', 58, 163, 1060, 14, MUTED, 20)
        y = 205
        entries = [(uid, data) for uid, data in FUTURE_UPGRADES.items() if self.future_upgrade_visible(uid)]
        card_h = 104
        row_step = 113
        for i, (uid, data) in enumerate(entries):
            col = i % 2
            row = i // 2
            x = 58 + col * 555
            yy = y + row * row_step
            self.box((x, yy, 525, card_h), (20, 30, 39), EDGE)
            self.label(data['name'], x+17, yy+10, 17, TEAL)
            self.label(data['slot'], x+17, yy+34, 11, GOLD)
            recipe = '  |  '.join(f'{name} ×{qty}' for name, qty in data['recipe'].items())
            self.wrap(data['effect'], x+17, yy+52, 490, 12, INK, 15)
            self.wrap('Custo: ' + recipe, x+17, yy+81, 490, 11, MUTED, 14)
            if uid == 'gauntlet_nexus':
                req_ok = all(self.state.inventory.get(name, 0) >= qty for name, qty in data['recipe'].items())
                if self.state.gauntlet_nexus_installed:
                    self.label('INSTALADO — SENCIÊNCIA ATIVA', x+320, yy+10, 10, TEAL)
                elif req_ok and self.state.at_ship():
                    self.label('PRONTO PARA FABRICAÇÃO', x+320, yy+10, 10, TEAL)
                elif req_ok:
                    self.label('REQUISITOS ATENDIDOS — ENTRE NA NAVE', x+320, yy+10, 10, GOLD)
                else:
                    self.label('REQUISITOS INCOMPLETOS', x+320, yy+10, 10, MUTED)
                status_x = x + 320
                status_y = yy + 39
                req_line = ' | '.join(f'{name} {self.state.inventory.get(name, 0)}/{qty}' for name, qty in data['recipe'].items())
                self.label(self.fit_text(req_line, 9, 190), status_x, status_y, 9, INK if req_ok else MUTED)
                can_nexus = (not self.state.gauntlet_nexus_installed) and req_ok and self.state.at_ship()
                button_text = 'FABRICAR NEXUS' if can_nexus else ('INSTALADO' if self.state.gauntlet_nexus_installed else 'FABRICAÇÃO BLOQUEADA')
                self.button((status_x, yy+62, 190, 29), button_text, self._craft_from_technology_nexus, can_nexus, 'Siga para a nave para fabricar.' if req_ok and not self.state.at_ship() else 'Instalar o NEXUS e habilitar a senciência da Manopla.')
            elif uid == 'ship_laser':
                req_ok = all(self.state.inventory.get(name, 0) >= qty for name, qty in data['recipe'].items())
                if self.state.ship_laser_installed:
                    self.label('INSTALADO', x+320, yy+10, 10, TEAL)
                elif req_ok and self.state.at_ship():
                    self.label('PRONTO PARA INSTALAÇÃO', x+320, yy+10, 10, TEAL)
                elif req_ok:
                    self.label('REQUISITOS ATENDIDOS — ENTRE NA NAVE', x+320, yy+10, 10, GOLD)
                else:
                    self.label('REQUISITOS INCOMPLETOS', x+320, yy+10, 10, MUTED)
                status_x = x + 320
                req_line = ' | '.join(f'{name} {self.state.inventory.get(name, 0)}/{qty}' for name, qty in data['recipe'].items())
                self.label(self.fit_text(req_line, 9, 190), status_x, yy+39, 9, INK if req_ok else MUTED)
                can_laser = (not self.state.ship_laser_installed) and req_ok and self.state.at_ship()
                button_text = 'INSTALAR LASER' if can_laser else ('INSTALADO' if self.state.ship_laser_installed else 'INSTALAÇÃO BLOQUEADA')
                self.button((status_x, yy+62, 190, 29), button_text, self._craft_from_technology_laser, can_laser, 'Siga para a nave para instalar o emissor.' if req_ok and not self.state.at_ship() else 'Instalar o Emissor Laser e liberar a defesa da nave.')
        # O catálogo de Recursos pertence aos Projetos Tecnológicos, não ao Menu global.
        self.button((58, 654, 1060, 40), 'RECURSOS', lambda: self.open_panel('resources', 'tech'), True, 'Catálogo de materiais, criaturas de origem e locais conhecidos')

    def resource_catalog(self):
        catalog = {}
        # Recursos de criaturas atuais: mostram espécies e setores onde aparecem.
        for species_id, spec in SPECIES.items():
            locations = sorted({SECTORS[sid]['name'] for sid, data in SECTORS.items() if any((sp.get('species') if isinstance(sp, dict) else sp[0]) == species_id for sp in data['spawns'])})
            for item_name, *_ in spec.get('drops', []):
                entry = catalog.setdefault(item_name, {'sources': set(), 'locations': set(), 'boss': False})
                entry['sources'].add(spec['name'])
                entry['locations'].update(locations)
        # Recursos de boss: sem localização, apenas indicação de perigo.
        for boss_id, boss in BOSSES.items():
            for item_name, *_ in boss.get('drops', []):
                entry = catalog.setdefault(item_name, {'sources': set(), 'locations': set(), 'boss': False})
                entry['sources'].add(boss['name'])
                entry['boss'] = True
        # Recursos coletáveis diretamente no mapa.
        for sid, data in SECTORS.items():
            for node in data['nodes']:
                if node.get('category') == 'flora':
                    continue
                name = node.get('item')
                if not name:
                    continue
                entry = catalog.setdefault(name, {'sources': set(), 'locations': set(), 'boss': False})
                entry['sources'].add('Coleta de campo')
                entry['locations'].add(data['name'])
        # Flora fica catalogada como recurso, mas sem prometer coleta antes do Scan.
        for herb_name in HERBS:
            entry = catalog.setdefault(herb_name, {'sources': set(), 'locations': set(), 'boss': False})
            entry['sources'].add('Flora')
            for sid, data in SECTORS.items():
                if any(n.get('category') == 'flora' and n.get('item') == herb_name for n in data['nodes']):
                    entry['locations'].add(data['name'])
        if self.state.inventory.get('Essência', 0) > 0:
            catalog['Essência'] = {'sources': {'Derrotas de criaturas', 'Asteroides destruídos'}, 'locations': set(), 'boss': False}
        # Recursos sem fonte efetiva neste planeta não entram no catálogo.
        # Isso evita apresentar placeholders de mundos futuros como se já fossem
        # recursos obtíveis pelo jogador.
        return sorted(catalog.items(), key=lambda item: item[0].casefold())

    def resources(self):
        self.panel_header('RECURSOS', 'Catálogo de recursos atualmente registráveis pela Manopla: origem conhecida e local de obtenção.')
        outer = pygame.Rect(35, 110, 1130, 590)
        self.box(outer, (7,15,22), EDGE)
        headers_y=132
        self.label('RECURSO', 58, headers_y, 13, GOLD)
        self.label('ORIGEM', 360, headers_y, 13, GOLD)
        self.label('LOCAL', 730, headers_y, 13, GOLD)
        view=pygame.Rect(58,168,1080,510)
        rows=self.resource_catalog(); row_h=54
        max_scroll=max(0,len(rows)*row_h-view.height)
        self.ui_scroll['resources']=max(0,min(self.ui_scroll.get('resources',0),max_scroll))
        self.canvas.set_clip(view)
        y=view.y-int(self.ui_scroll['resources'])
        for name, entry in rows:
            self.box((58,y,1070,45),(14,25,31),EDGE)
            self.label(self.fit_text(name,13,275),70,y+7,13,INK)
            src=', '.join(sorted(entry['sources']))
            self.label(self.fit_text(src,12,345),360,y+8,12,TEAL)
            if entry.get('boss'):
                loc='[!] BOSS'
                color=(224,112,93)
            else:
                loc=', '.join(sorted(entry['locations'])) if entry['locations'] else 'MUNDOS FUTUROS'
                color=GOLD if 'futuro' in loc.lower() else MUTED
            self.label(self.fit_text(loc,12,370),730,y+8,12,color)
            y+=row_h
        self.canvas.set_clip(None)
        self._draw_scrollbar((1126,168,10,510),self.ui_scroll['resources'],max_scroll)
        self._register_scrollbar('resources',(1126,168,10,510),self.ui_scroll['resources'],max_scroll)
        self.label('Roda do mouse ou arraste a barra para navegar pelo catálogo.',58,684,10,EDGE)

    def _refresh_hero_images(self, force=False):
        """Carrega/recarrega os sprites-base externos do protagonista.

        Arquivos obrigatórios por direção:
          assets/player/baixo.png
          assets/player/cima.png
          assets/player/esquerda.png
          assets/player/direita.png

        Um segundo frame opcional usa o sufixo ``_1`` (ex.: ``baixo_1.png``).
        Sem o segundo frame, o primeiro é reutilizado nos dois estados da caminhada.
        A leitura é preguiçosa para permitir adicionar ou trocar os PNGs com o jogo aberto.
        """
        player_dir = getattr(self, 'hero_dir', ROOT / 'assets' / 'player')
        images = getattr(self, 'hero_images', {})
        mtimes = getattr(self, 'hero_image_mtimes', {})
        for direction, filename in PLAYER_ASSET_FILES.items():
            primary = player_dir / filename
            alt = primary.with_name(f'{primary.stem}_1{primary.suffix}')
            primary_key = (direction, 0)
            alt_key = (direction, 1)
            try:
                primary_mtime = primary.stat().st_mtime_ns
            except OSError:
                if force:
                    images.pop(primary_key, None); images.pop(alt_key, None)
                    mtimes.pop(primary_key, None); mtimes.pop(alt_key, None)
                continue
            try:
                alt_mtime = alt.stat().st_mtime_ns
            except OSError:
                alt_mtime = None
            stamp = (primary_mtime, alt_mtime)
            if not force and mtimes.get(primary_key) == stamp and primary_key in images:
                continue
            try:
                first = pygame.image.load(str(primary)).convert_alpha()
                second = pygame.image.load(str(alt)).convert_alpha() if alt_mtime is not None else first
                images[primary_key] = first
                images[alt_key] = second
                mtimes[primary_key] = stamp
                mtimes[alt_key] = stamp
            except (pygame.error, OSError):
                if force:
                    images.pop(primary_key, None); images.pop(alt_key, None)
                    mtimes.pop(primary_key, None); mtimes.pop(alt_key, None)
        self.hero_images = images
        self.hero_image_mtimes = mtimes

    def _refresh_equipment_images(self, force=False):
        """Carrega/recarrega as artes oficiais de equipamento quando necessário.

        Os PNGs vivem fora da distribuição e são colocados manualmente em
        assets/equips/. O mtime evita releituras desnecessárias, mas a função também
        detecta arquivos adicionados depois que o jogo já foi iniciado.
        """
        equipment_dir = getattr(self, 'equipment_dir', ROOT / 'assets' / 'equips')
        for kind, filename in EQUIPMENT_ASSET_FILES.items():
            image_path = equipment_dir / filename
            try:
                mtime = image_path.stat().st_mtime_ns
            except OSError:
                if force:
                    self.equipment_images.pop(kind, None)
                    self.equipment_image_mtimes.pop(kind, None)
                continue
            if not force and self.equipment_image_mtimes.get(kind) == mtime and kind in self.equipment_images:
                continue
            try:
                self.equipment_images[kind] = pygame.image.load(str(image_path)).convert_alpha()
                self.equipment_image_mtimes[kind] = mtime
            except (pygame.error, OSError):
                # Mantém eventual imagem anterior; o fallback procedural continua disponível.
                if force:
                    self.equipment_images.pop(kind, None)
                    self.equipment_image_mtimes.pop(kind, None)

    def draw_gear_piece(self, kind, cx, cy, scale=1.0, active=True):
        self._refresh_equipment_images()
        border = TEAL if active else EDGE
        fill = (29, 43, 51) if active else (18, 27, 34)
        box = pygame.Rect(int(cx-82*scale), int(cy-58*scale), int(164*scale), int(116*scale))
        pygame.draw.rect(self.canvas, fill, box, border_radius=8)
        pygame.draw.rect(self.canvas, border, box, 1, border_radius=8)

        # Arte oficial, quando fornecida pelo usuário. O recorte do bounding box
        # transparente evita que margens vazias reduzam demais a peça na tela.
        # pygame.transform.scale é intencional: mantém a aparência pixel-art sem
        # interpolação. O fallback procedural abaixo permanece intacto.
        official = getattr(self, 'equipment_images', {}).get(kind)
        if official is not None:
            image = official
            bounds = image.get_bounding_rect(min_alpha=1)
            if bounds.width > 0 and bounds.height > 0:
                image = image.subsurface(bounds).copy()
            pad = max(8, int(10 * scale))
            max_w = max(1, box.width - 2 * pad)
            max_h = max(1, box.height - 2 * pad)
            ratio = min(max_w / image.get_width(), max_h / image.get_height())
            draw_w = max(1, int(image.get_width() * ratio))
            draw_h = max(1, int(image.get_height() * ratio))
            image = pygame.transform.scale(image, (draw_w, draw_h))
            self.canvas.blit(image, (box.centerx - draw_w // 2, box.centery - draw_h // 2))
            return

        if kind == 'helmet':
            design = getattr(self.state, 'helmet_design', None) or 'tactical'
            data = HELMET_DESIGNS.get(design, HELMET_DESIGNS['tactical'])
            pygame.draw.polygon(self.canvas, data['shell'], [(cx-38*scale,cy+22*scale),(cx-30*scale,cy-25*scale),(cx,cy-40*scale),(cx+30*scale,cy-25*scale),(cx+38*scale,cy+22*scale)])
            pygame.draw.polygon(self.canvas, (48,57,64), [(cx-29*scale,cy-18*scale),(cx-18*scale,cy-32*scale),(cx+10*scale,cy-35*scale),(cx+27*scale,cy-22*scale),(cx+22*scale,cy-15*scale),(cx-24*scale,cy-15*scale)])
            pygame.draw.rect(self.canvas, data['visor'], (int(cx-28*scale), int(cy-1*scale), int(56*scale), int(9*scale)), border_radius=max(1,int(2*scale)))
            pygame.draw.line(self.canvas, data['accent'], (int(cx-18*scale), int(cy-17*scale)), (int(cx+18*scale), int(cy-17*scale)), max(1,int(2*scale)))
            if design == 'recon':
                pygame.draw.line(self.canvas, data['accent'], (int(cx+24*scale),int(cy-21*scale)), (int(cx+35*scale),int(cy-37*scale)), max(1,int(3*scale)))
            elif design == 'combat':
                pygame.draw.polygon(self.canvas, (52,55,64), [(cx-37*scale,cy-8*scale),(cx-28*scale,cy+22*scale),(cx-16*scale,cy+24*scale),(cx-20*scale,cy-5*scale)])
                pygame.draw.polygon(self.canvas, (52,55,64), [(cx+37*scale,cy-8*scale),(cx+28*scale,cy+22*scale),(cx+16*scale,cy+24*scale),(cx+20*scale,cy-5*scale)])
        elif kind == 'chest':
            pygame.draw.polygon(self.canvas, (65, 78, 87), [(cx-44*scale,cy-30*scale),(cx-20*scale,cy-46*scale),(cx+20*scale,cy-46*scale),(cx+44*scale,cy-30*scale),(cx+35*scale,cy+40*scale),(cx,cy+48*scale),(cx-35*scale,cy+40*scale)])
            aur = self.aurora_detail_color()
            pygame.draw.circle(self.canvas, aur, (int(cx),int(cy)), int(13*scale), 2)
            pygame.draw.circle(self.canvas, tuple(min(255,c+30) for c in aur), (int(cx),int(cy)), max(2,int(5*scale)))
        elif kind == 'gauntlet':
            # Antebraço + Manopla V-7: formato modular, painel LED e sockets de aprimoramento.
            pygame.draw.polygon(self.canvas, (60, 73, 81), [(cx-55*scale,cy-24*scale),(cx-35*scale,cy-37*scale),(cx+8*scale,cy-29*scale),(cx+19*scale,cy-5*scale),(cx+10*scale,cy+20*scale),(cx-28*scale,cy+28*scale),(cx-49*scale,cy+12*scale)])
            pygame.draw.polygon(self.canvas, GOLD if active else (78, 88, 96), [(cx+5*scale,cy-18*scale),(cx+36*scale,cy-10*scale),(cx+53*scale,cy+5*scale),(cx+41*scale,cy+30*scale),(cx+14*scale,cy+21*scale)])
            # Painel LED no dorso do antebraço.
            pygame.draw.rect(self.canvas, (11, 19, 25), (int(cx-24*scale), int(cy-13*scale), int(29*scale), int(17*scale)), border_radius=3)
            pygame.draw.rect(self.canvas, TEAL, (int(cx-20*scale), int(cy-9*scale), int(21*scale), int(4*scale)))
            pygame.draw.line(self.canvas, (154, 238, 225), (int(cx-19*scale),int(cy-2*scale)), (int(cx-5*scale),int(cy-2*scale)), max(1,int(scale)))
            # emissor da palma
            pygame.draw.circle(self.canvas, (87,225,205), (int(cx+31*scale), int(cy+7*scale)), max(4,int(7*scale)), 2)
            pygame.draw.circle(self.canvas, (180,255,244), (int(cx+31*scale), int(cy+7*scale)), max(2,int(2*scale)))
            # sockets futuros; quando uma pedra existir, a própria Manopla
            # mostra o encaixe preenchido também no painel de equipamento.
            stones = getattr(self.state, 'gauntlet_stones', [None] * 6)
            stones = (stones + [None] * 6)[:6]
            for k in range(6):
                col, row = k % 3, k // 3
                socket_x = cx - 17*scale + col*14*scale
                socket_y = cy + (17 + row*9)*scale
                has_stone = bool(stones[k])
                pygame.draw.circle(self.canvas, GOLD if has_stone else EDGE, (int(socket_x), int(socket_y)), max(3,int(4*scale)), 2)
                if has_stone:
                    pygame.draw.circle(self.canvas, GOLD, (int(socket_x), int(socket_y)), max(2,int(2*scale)))
        elif kind == 'locomotion':
            pygame.draw.polygon(self.canvas, (66, 79, 88), [(cx-42*scale,cy-41*scale),(cx-13*scale,cy-47*scale),(cx-7*scale,cy+5*scale),(cx-20*scale,cy+47*scale),(cx-43*scale,cy+32*scale)])
            pygame.draw.polygon(self.canvas, (66, 79, 88), [(cx+42*scale,cy-41*scale),(cx+13*scale,cy-47*scale),(cx+7*scale,cy+5*scale),(cx+20*scale,cy+47*scale),(cx+43*scale,cy+32*scale)])
            pygame.draw.line(self.canvas, TEAL, (int(cx-8*scale),int(cy-18*scale)), (int(cx+8*scale),int(cy+18*scale)), max(1,int(3*scale)))

    def equipment_config(self, kind):
        if kind == 'gauntlet':
            self.open_panel('gauntlet')
        elif kind == 'chest':
            self.open_panel('chest')
        elif kind == 'helmet' and self.state.helmet_owned:
            self.open_panel('helmet_config')
        else:
            self.set_message('Configuração indisponível.')

    def helmet_config(self):
        self.panel_header('ELMO', 'Tier, passivas, idiomas e protocolos de Scan.')
        self.box((35, 112, 1130, 560), (7,15,22), EDGE)
        # Coluna de identificação/equipamento.
        self.label('ELMO ATUAL', 58, 137, 13, GOLD)
        current_tier = max(0, min(3, int(self.state.helmet_generation)))
        tier_data = HELMET_TIERS.get(current_tier, HELMET_TIERS[1])
        design = HELMET_DESIGNS.get(getattr(self.state,'helmet_design',None) or 'tactical', HELMET_DESIGNS['tactical'])
        self.label(tier_data['name'].upper(),58,165,22,TEAL)
        self.label(design['name'],58,195,12,MUTED)
        self.draw_gear_piece('helmet', 190, 300, 1.12, True)
        self.label('PASSIVAS', 330, 137, 16, GOLD)
        passive_rows=(('Precisão',f'+{tier_data["precision"]}'),('Taxa Crítica',f'+{tier_data["crit_rate"]:.0f}%'))
        y=168
        for name,value in passive_rows:
            self.box((330,y,260,54),(14,25,31),EDGE)
            self.label(name,346,y+9,11,INK)
            self.label(value,500,y+9,16,TEAL)
            y+=65
        self.label('IDIOMA', 330, 315, 16, GOLD)
        lang_status='APRENDIDO' if self.state.language_mastered else f'EM APRENDIZADO {self.state.language_progress}/3'
        self.box((330,343,260,58),(14,25,31),EDGE)
        self.label('Avari',346,353,14,INK)
        self.label(lang_status,346,376,10,TEAL if self.state.language_mastered else MUTED)

        self.label('SCAN', 630, 137, 16, GOLD)
        abilities=self.state.helmet_scan_abilities()
        scan_rows=[('creatures','Scan de criaturas'),('rocks','Scan de rochas'),('flora','Scan de flora')]
        y=168
        for key,name in scan_rows:
            enabled=abilities.get(key,False)
            self.box((630,y,485,42),(18,37,39) if enabled else (12,22,29),TEAL if enabled else EDGE)
            self.label(name,646,y+7,11,INK)
            self.label('ATIVO' if enabled else 'BLOQUEADO', 980,y+8,9,TEAL if enabled else MUTED)
            y+=50
        research_ok=bool(getattr(self.state,'helmet_advanced_research_unlocked',False))
        self.box((630,322,485,52),(18,37,39) if research_ok else (12,22,29),TEAL if research_ok else EDGE)
        self.label('PESQUISA AVANÇADA',646,332,11,GOLD)
        self.label('ATIVA' if research_ok else f'{min(5,len(set(self.state.bestiary_scanned)))} / 5 análises',960,333,9,TEAL if research_ok else MUTED)
        self.label('TIERS', 630, 389, 16, GOLD)
        y=420
        for level in (1,2,3):
            data=HELMET_TIERS[level]
            active=level==current_tier
            next_tier=(level==current_tier+1)
            box_color=(18,37,39) if active else (12,22,29)
            border=TEAL if active or next_tier else EDGE
            self.box((630,y,485,78),box_color,border)
            self.label(f'TIER {level}',646,y+9,12,TEAL if active else MUTED)
            self.label(f'+{data["precision"]} PREC • +{data["crit_rate"]:.0f}% de Taxa Crítica',646,y+31,11,GOLD)
            if level==1:
                status='ATIVO' if active else 'BASE'
            elif active:
                status='ATIVO'
            elif data.get('available') and next_tier:
                status='PRÓXIMO'
            else:
                status='FUTURO'
            self.label(status,1000,y+31,10,TEAL if active or next_tier else MUTED)
            y+=89
        # Receita curta do próximo tier disponível, somente quando pertinente.
        if current_tier < 3:
            next_level=current_tier+1
            next_data=HELMET_TIERS[next_level]
            if next_data.get('available'):
                req=' • '.join(f'{n} {self.state.inventory.get(n,0)}/{q}' for n,q in next_data['recipe'].items())
                self.label('PRÓXIMO APRIMORAMENTO', 58, 467, 11, GOLD)
                self.label(self.fit_text(req,10,530),58,489,10,MUTED)
                can=self.state.helmet_generation>=1 and all(self.state.inventory.get(n,0)>=q for n,q in next_data['recipe'].items())
                self.button((58,540,270,42),'INSTALAR TIER '+str(next_level),lambda lv=next_level:self.upgrade_helmet(lv),can)
        self.button((58, 610, 210, 40), 'VOLTAR', self.close_panel, True)

    def upgrade_helmet(self, level):
        ok,msg=self.state.upgrade_helmet(level); self.set_message(msg)
        if ok: self.checkpoint()

    def upgrade_aurora(self, level):
        ok,msg=self.state.upgrade_aurora(level); self.set_message(msg)
        if ok: self.checkpoint()

    def chest(self):
        self.panel_header('PEITORAL', 'AURORA e memória')
        self.box((45,105,520,595),(7,15,22),EDGE)
        self.label('AURORA',70,132,20,GOLD)
        aura=self.state.aurora_bonuses()
        self.label(AURORA_UPGRADES.get(self.state.aurora_level,{}).get('name','AURORA'),70,165,24,TEAL)
        self.label('STATUS: OPERACIONAL',70,198,12,INK)
        self.label(f'HP +{aura["hp"]}   ATQ +{aura["attack"]}',70,228,13,GOLD)
        self.label(f'Taxa Crítica +{aura["crit_rate"]:.0f}%   Dano Crítico +{aura["crit_damage"]:.0%}',70,252,13,GOLD)
        self.label('APRIMORAMENTOS',70,298,16,GOLD)
        for level in (1,2,3):
            data=AURORA_UPGRADES[level]; y=330+(level-1)*105
            available=data.get('available',False) or level <= self.state.aurora_level+1
            self.box((70,y,470,88),(12,24,31) if level <= self.state.aurora_level+1 else (9,17,24),TEAL if level==self.state.aurora_level+1 else EDGE)
            self.label(data['name'],86,y+11,14,INK)
            self.label(f'HP +{data["hp"]} | ATQ +{data["attack"]} | Taxa Crítica +{data["crit_rate"]:.0f}% | Dano Crítico +{data["crit_damage"]:.0%}',86,y+34,10,GOLD)
            req_items=list(data['recipe'].items())
            for ri,(name,qty) in enumerate(req_items[:4]):
                owned=self.state.inventory.get(name,0); col=(135,205,238) if owned>=qty else (224,112,93)
                self.label(f'{name}: {owned}/{qty}',86+((ri%2)*176),y+57+(ri//2)*15,8,col)
            can=level==self.state.aurora_level+1 and data.get('available',False) and all(self.state.inventory.get(n,0)>=q for n,q in data['recipe'].items())
            self.button((422,y+48,102,30),'INSTALAR' if level==self.state.aurora_level+1 else ('ATIVO' if level<=self.state.aurora_level else 'FUTURO'),lambda lv=level:self.upgrade_aurora(lv),can)

        self.box((600,105,555,595),(7,15,22),EDGE)
        self.label('SLOTS DE MEMÓRIA',625,132,20,GOLD)
        max_slots=self.state.max_memory_slots
        for idx in range(TOTAL_MEMORY_SLOTS):
            y=180+idx*88
            val=self.state.memory_slots[idx] if idx < len(self.state.memory_slots) else None
            if idx>=max_slots: status='BLOQUEADO'; color=EDGE
            elif val: status='OCUPADO'; color=TEAL
            else: status='VAZIO'; color=GOLD
            self.box((625,y,500,64),(12,24,31),color)
            self.label(f'SLOT {idx+1}',645,y+14,12,INK); self.label(status,930,y+14,12,color)
            if val: self.label(MEMORY_MODULES[val]['name'],645,y+37,10,MUTED)
        self.label(f'MEMÓRIA {self.state.memory}/{self.state.max_memory}',625,548,14,TEAL)
        self.button((625,610,220,42),'VOLTAR',self.close_panel,True)

    def equipment(self):
        self.panel_header('EQUIPAMENTO', 'As quatro peças do conjunto aparecem aqui na mesma escala conceitual do personagem.')
        attrs = self.state.player_attributes()

        self.box((35, 111, 350, 599), (7, 15, 22), EDGE)
        self.label('VISUAL ATUAL', 59, 133, 14, GOLD)
        self.actor('hero', 210, 276, 1.75, direction='down')
        self.label('Aparência em uso', 59, 334, 16, TEAL)
        self.wrap('O visual do personagem acompanha o equipamento realmente equipado. As peças futuras terão configurações próprias.', 59, 360, 302, 13, MUTED, 18)
        self.label('ATRIBUTOS EFETIVOS', 59, 456, 17, GOLD)
        self.label(f'ATQ {attrs["attack"]}     DEF {attrs["defense"]}', 59, 485, 18, INK)
        self.label(f'AMP {attrs["amp"]:.2f}%     Taxa Crítica {attrs["crit_rate"]:.2f}%', 59, 514, 14, TEAL)
        self.label(f'PREC {attrs["precision"]}     Dano Crítico {attrs["crit_damage"]:.2f}x', 59, 540, 13, GOLD)
        self.label(f'MÍNIMO DE DANO +{attrs["min_damage_bonus"]}', 59, 565, 13, MUTED)

        self.box((408, 111, 757, 599), (7, 15, 22), EDGE)
        self.label('PEÇAS', 432, 132, 20, TEAL)
        pieces = [
            ('gauntlet', 'MANOPLA', f'NEXUS NÍVEL {self.state.gauntlet_nexus_level}' if self.state.gauntlet_nexus_installed else 'PADRÃO', True),
            ('chest', 'PEITORAL', f'TIER {self.state.chest_generation}', True),
            ('helmet', 'ELMO', 'EQUIPADO' if self.state.helmet_equipped else ('GUARDADO' if self.state.helmet_owned else 'NÃO CONSTRUÍDO'), self.state.helmet_equipped),
            ('locomotion', 'MÓDULO DE LOCOMOÇÃO', f'TIER {self.state.locomotion_generation}' if self.state.locomotion_generation else 'NÃO CONSTRUÍDO', bool(self.state.locomotion_equipped)),
        ]
        cards = [
            (432, 158, 350, 252),
            (802, 158, 338, 252),
            (432, 425, 350, 252),
            (802, 425, 338, 252),
        ]
        for (kind, name, status, active), (x, y, w, h) in zip(pieces, cards):
            self.box((x, y, w, h), (15, 24, 31), EDGE)
            self.label(name, x+16, y+14, 15, TEAL if active else MUTED)
            self.draw_gear_piece(kind, x+w/2, y+87, 0.78, active)
            self.label(status, x+16, y+136, 12, GOLD if active else EDGE)
            enabled = kind in ('gauntlet', 'chest') or (kind == 'helmet' and self.state.helmet_owned)
            self.button((x+16, y+173, w-32, 47), 'CONFIGURAR', lambda k=kind: self.equipment_config(k), enabled)

    def status(self):
        self.panel_header('STATUS', 'Informações que a Manopla já consegue consolidar sem revelar dados ocultos do mundo.')
        left = pygame.Rect(35, 111, 535, 590)
        right = pygame.Rect(595, 111, 570, 590)
        self.box(left, (7, 15, 22), EDGE)
        self.box(right, (7, 15, 22), EDGE)

        # Painel esquerdo rolável
        viewport_l = pygame.Rect(58, 145, 485, 500)
        self.canvas.set_clip(viewport_l)
        y = 145 - int(self.ui_scroll.get('status_left', 0))
        self.label('SISTEMAS DO SOBREVIVENTE', 58, y, 19, GOLD); y += 43
        self.label(f'VIDA     {self.state.hp}/{self.state.max_hp}', 58, y, 18, INK); y += 25
        self.bar(58, y, 450, self.state.hp, self.state.max_hp, (203,112,94)); y += 42
        self.label(f'MEMÓRIA  {self.state.memory}/{self.state.max_memory}', 58, y, 18, INK); y += 25
        self.bar(58, y, 450, self.state.memory, max(1,self.state.max_memory), TEAL); y += 48
        self.label(f'LOCAL    {self.state.area["name"]}',58,y,16,TEAL); y+=30
        self.label(f'POSIÇÃO  {self.state.pos[0]}, {self.state.pos[1]}',58,y,15,MUTED); y+=43
        attrs=self.state.player_attributes()
        self.label('ATRIBUTOS DE COMBATE',58,y,16,GOLD); y+=30
        self.label(f'ATQ {attrs["attack"]:g}  |  DEF {attrs["defense"]}  |  AMP {attrs["amp"]:.2f}%',58,y,13,TEAL); y+=24
        self.label(f'PREC {attrs["precision"]}  |  Taxa Crítica {attrs["crit_rate"]:.2f}%  |  Dano Crítico {attrs["crit_damage"]:.2f}x',58,y,12,MUTED); y+=45
        self.label('CONJUNTO DE ARMADURA',58,y,18,GOLD); y+=32
        equip_rows=[
            ('MANOPLA', f'NEXUS N{self.state.gauntlet_nexus_level}' if self.state.gauntlet_nexus_installed else 'PADRÃO'),
            ('PEITORAL', f'TIER {self.state.chest_generation}'),
            ('ELMO', 'EQUIPADO' if self.state.helmet_equipped else ('GUARDADO' if self.state.helmet_owned else 'NÃO CONSTRUÍDO')),
            ('MÓDULO', 'EQUIPADO' if self.state.locomotion_equipped else ('CONSTRUÍDO' if self.state.locomotion_generation else 'NÃO CONSTRUÍDO')),
        ]
        for name,value in equip_rows:
            self.label(name,58,y,13,MUTED); self.label(value,320,y,13,TEAL if 'EQUIPADO' in value or 'NEXUS' in value else GOLD); y+=32
        self.canvas.set_clip(None)
        max_l=max(0,y-(viewport_l.bottom-4))
        self.ui_scroll['status_left']=max(0,min(self.ui_scroll.get('status_left',0),max_l))
        self._draw_scrollbar((553,145,8,500),self.ui_scroll['status_left'],max_l)
        self._register_scrollbar('status_left', (553,145,8,500), self.ui_scroll['status_left'], max_l)

        # Painel direito rolável
        viewport_r=pygame.Rect(618,145,510,455)
        self.canvas.set_clip(viewport_r)
        y=145-int(self.ui_scroll.get('status_right',0))
        self.label('ESTADO DA NAVE',618,y,19,GOLD); y+=43
        if self.state.at_ship() or self.ship_diagnostic_rows:
            rows=self.ship_diagnostic_rows or [{'name':SHIP_SYSTEMS[sid]['name'],'condition':self.state.ship_systems[sid],'status':SHIP_SYSTEMS[sid]['status']} for sid in SHIP_DIAGNOSTIC_ORDER]
            self.label('DECOLAGEM: DISPONÍVEL' if self.state.ship_flight_ready() else 'DECOLAGEM: INDISPONÍVEL',618,y,17,TEAL if self.state.ship_flight_ready() else (224,112,93)); y+=36
            critical=[r['name'] for r in rows if r['condition']<20]
            msg='Falhas atuais: '+', '.join(critical[:4])+('.' if critical else ' nenhuma falha crítica detectada.')
            y=self.wrap(msg,618,y,475,13,MUTED,19)+18
            for row in rows:
                color=TEAL if row['condition']>=60 else GOLD if row['condition']>=20 else (224,112,93)
                self.label(row['name'],618,y,14,INK)
                self.label(f'{row["condition"]}%  {row["status"]}',1015,y,12,color)
                y+=40
        else:
            self.label('DIAGNÓSTICO NÃO EXECUTADO',618,y,17,GOLD); y+=34
            y=self.wrap('Aproxime-se da nave e use o painel físico interno para consultar os sistemas. Detalhes técnicos do ambiente não ficam expostos durante a exploração.',618,y,475,13,MUTED,19)+24
        self.label('PRINCÍPIO DE EXPLORAÇÃO',618,y,19,GOLD); y+=34
        y=self.wrap('A quantidade de criaturas, respawns, coletas e outros dados do ambiente não é exibida automaticamente. O jogador precisa descobrir essas informações por análise, observação e experiência.',618,y,475,13,MUTED,20)+26
        self.label('NEXUS',618,y,19,GOLD); y+=33
        nexus_text='Instalado.' if self.state.gauntlet_nexus_installed else 'Ainda não instalado.'
        y=self.wrap('Estado do NEXUS: '+nexus_text+' A progressão da Manopla é exclusivamente ofensiva e acontece pelo dano causado.',618,y,475,13,MUTED,19)+20
        self.canvas.set_clip(None)
        max_r=max(0,y-(viewport_r.bottom-4))
        self.ui_scroll['status_right']=max(0,min(self.ui_scroll.get('status_right',0),max_r))
        self._draw_scrollbar((1138,145,8,455),self.ui_scroll['status_right'],max_r)
        self._register_scrollbar('status_right', (1138,145,8,455), self.ui_scroll['status_right'], max_r)
        self.label('Role com a roda do mouse ou arraste a barra lateral.', 618, 664, 10, EDGE)
        self.button((58, 686, 250, 40), 'VOLTAR', self.close_panel)

    def pause(self):
        self.label('PAUSA', 440, 220, 40, TEAL)
        self.button((400, 310, 400, 60), 'Continuar', lambda: self.set_mode('world'))
        self.button((400, 390, 400, 60), 'Salvar', self.save)
        self.button((400, 470, 400, 60), 'Sair', lambda: setattr(self, 'running', False))
        self.label('Feche fora do combate para salvar automaticamente.', 330, 563, 16, MUTED)

    def message_hud(self):
        # Display temporário da Manopla: pequeno, legível e deslocado para o canto
        # superior direito para não cobrir o centro do mapa nem a área de combate.
        if self.mode not in ('world', 'battle'):
            return
        if self.message != self._popup_message:
            self._popup_message = self.message
            self._popup_until = self.frame + 4.6
        remaining = self._popup_until - self.frame
        if remaining <= 0:
            return

        fade = 1.0 if remaining > 0.8 else max(0.0, remaining / 0.8)
        alpha = int(224 * fade)
        if self.mode == 'battle':
            panel_w, panel_h = (345, 82)
            x, y = W - panel_w - 28, 18
        else:
            panel_w, panel_h = (355, 96)
            x = W - panel_w - 28
            y = 70
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((4, 12, 18, alpha))
        edge_alpha = int(235 * fade)
        pygame.draw.rect(panel, (*TEAL, edge_alpha), (0, 0, panel_w-1, panel_h-1), 1, border_radius=7)
        pygame.draw.line(panel, (*TEAL, edge_alpha), (17, 17), (182, 17), 1)
        pygame.draw.line(panel, (*TEAL, edge_alpha), (245, 17), (338, 17), 1)
        pygame.draw.rect(panel, (*GOLD, edge_alpha), (17, 11, 4, 13))
        for tick in range(8):
            xx = 24 + tick * 34
            pygame.draw.line(panel, (38, 83, 87, int(130*fade)), (xx, 82), (xx+16, 82), 1)
        self.canvas.blit(panel, (x, y))
        self.label('MANOPLA // DISPLAY DE CAMPO', x+30, y+6, 11 if self.mode == 'battle' else 12, TEAL)
        self.label('LINK LOCAL', x+246, y+6, 9 if self.mode == 'battle' else 10, GOLD)
        cursor = '▌' if int(self.frame * 2) % 2 == 0 else ' '
        self.wrap(f'> {self._popup_message} {cursor}', x+23, y+27, 298, 12 if self.mode == 'battle' else 13, INK, 16 if self.mode == 'battle' else 18)
        self.label('AUTO-CLEAR', x+247, y+(63 if self.mode == 'battle' else 76), 9 if self.mode == 'battle' else 10, MUTED)

    def draw_achievement_alert(self):
        if not self.achievement_alert_text or self.achievement_alert_until <= self.frame:
            if self.achievement_alert_until <= self.frame and self.achievement_alert_kind == 'card':
                self.card_alert_cid = None
            return
        remaining = self.achievement_alert_until - self.frame
        fade = 1.0 if remaining > 0.6 else max(0.0, remaining / 0.6)

        # Desbloqueio de carta recebe um popup maior com uma ilustração da própria
        # carta. O restante dos alertas conserva o formato compacto existente.
        if self.achievement_alert_kind == 'card':
            cid = self.card_alert_cid
            card = CARDS.get(cid or '', {})
            if not card:
                return
            w, h = 790, 410
            x, y = (W-w)//2, 145
            rarity = card.get('rarity', 'Comum')
            style = self.rarity_styles.get(rarity, self.rarity_styles['Comum'])
            alpha = int(244 * fade)
            panel = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (7,15,22,alpha), (0,0,w-1,h-1), border_radius=10)
            pygame.draw.rect(panel, (*style['edge'], alpha), (0,0,w-1,h-1), 2, border_radius=10)
            self.canvas.blit(panel, (x,y))

            self.label('NOVA CARTA DESBLOQUEADA PARA CRIAÇÃO!', x+28, y+22, 22, style['accent'])
            self.label(self.fit_text(format_card_name(card.get('name','Carta')), 18, 430), x+290, y+68, 18, INK)
            self.label(f"{rarity.upper()}  •  {card.get('type','-').upper()}", x+290, y+98, 11, style['accent'])
            self.wrap('A receita desta carta já pode ser encontrada em CARTAS > FABRICAÇÃO.', x+290, y+132, 445, 14, MUTED, 20)
            self.label(f"MEM {card.get('cost',0)}  |  DANO {card.get('damage',(0,0))[0]}–{card.get('damage',(0,0))[1]}", x+290, y+190, 11, TEAL)
            bonus_lines = self.card_bonus_lines(card.get('attributes', {}))
            if bonus_lines:
                self.wrap('  |  '.join(bonus_lines), x+290, y+220, 445, 12, GOLD, 18)
            self._draw_scroll_text_box((x+290, y+258, 450, 95), card.get('description',''), 'card_alert_effect', 11, INK, 16, style['edge'])

            # Prévia visual da carta, usando a mesma moldura e a mesma ilustração
            # da coleção para manter a identidade visual consistente.
            cr = pygame.Rect(x+28, y+62, 235, 320)
            self.card_frame(cr, rarity)
            self.label(self.fit_text(rarity.upper(), 9, 150), cr.x+14, cr.y+14, 9, style['accent'])
            art_box = pygame.Rect(cr.x+12, cr.y+48, cr.width-24, 145)
            pygame.draw.rect(self.canvas, (7,15,22), art_box, border_radius=6)
            pygame.draw.rect(self.canvas, style['edge'], art_box, 1, border_radius=6)
            spr = self.sprites.get((card.get('species'), 0))
            if spr:
                max_w, max_h = art_box.width-18, art_box.height-12
                scale = min(max_w/max(1,spr.get_width()), max_h/max(1,spr.get_height()))
                im = pygame.transform.scale(spr, (max(1,int(spr.get_width()*scale)), max(1,int(spr.get_height()*scale))))
                self.canvas.blit(im, (art_box.centerx-im.get_width()/2, art_box.centery-im.get_height()/2+4))
            self.label(self.fit_text(format_card_name(card.get('name','Carta')), 12, cr.width-24), cr.x+12, cr.y+207, 12, INK)
            self.label(f"MEM {card.get('cost',0)} | {card.get('damage',(0,0))[0]}–{card.get('damage',(0,0))[1]}", cr.x+12, cr.y+232, 9, TEAL)
            self.label('RECEITA DESBLOQUEADA', cr.x+12, cr.y+263, 9, style['accent'])
            self.label('CARTAS > FABRICAÇÃO', cr.x+12, cr.y+279, 9, MUTED)
            return

        w, h = 620, 62
        x = (W-w)//2; y = 92
        panel = pygame.Surface((w,h), pygame.SRCALPHA)
        edge = GOLD if self.achievement_alert_kind == 'unlocked' else TEAL
        alpha=int(232*fade)
        pygame.draw.rect(panel,(8,16,23,alpha),(0,0,w-1,h-1),border_radius=7)
        pygame.draw.rect(panel,(*edge,alpha),(0,0,w-1,h-1),2,border_radius=7)
        label_s=self.font(13).render(self.achievement_alert_text,True,edge); label_s.set_alpha(alpha)
        panel.blit(label_s,(18,11))
        if self.achievement_alert_kind == 'unlocked':
            helper = 'Abra CONQUISTAS para resgatar a recompensa.'
        elif self.achievement_alert_kind == 'claimed':
            helper = 'Recompensa adicionada ao seu histórico.'
        elif self.achievement_alert_kind == 'renown_claimed':
            helper = 'Recompensa de Renome adicionada ao inventário.'
        elif self.achievement_alert_kind == 'mission':
            helper = 'A missão foi registrada como concluída no DIÁRIO.'
        elif self.achievement_alert_kind == 'mission_started':
            helper = 'A missão foi registrada no DIÁRIO.'
        elif self.achievement_alert_kind == 'flight_unlocked':
            helper = 'Os outros mundos da Galáxia Nárion agora podem ser explorados.'
        elif self.achievement_alert_kind == 'helmet_advanced':
            helper = 'O Bestiário agora pode registrar análises aprofundadas de criaturas.'
        elif self.achievement_alert_kind == 'civ_mission_started':
            helper = 'O pedido foi adicionado aos PEDIDOS ativos.'
        elif self.achievement_alert_kind == 'civ_mission_updated':
            helper = 'Um pedido ativo atingiu uma nova etapa.'
        elif self.achievement_alert_kind == 'civ_mission_completed':
            helper = 'A recompensa do pedido foi adicionada ao inventário.'
        else:
            helper = 'Novo registro disponível.'
        reward=self.font(11).render(helper,True,INK); reward.set_alpha(alpha)
        panel.blit(reward,(18,35))
        self.canvas.blit(panel,(x,y))

    def draw_unique_gacha_alert(self):
        cid=self.unique_gacha_card_id
        if not cid or self.unique_gacha_until <= self.frame:
            if self.unique_gacha_until <= self.frame:
                self.unique_gacha_card_id=None; self.unique_gacha_kind=None
            return
        try:
            card,variant_data,_,variant=self.state.card_data(cid)
        except ValueError:
            self.unique_gacha_card_id=None; self.unique_gacha_kind=None; return
        count=int(self.unique_gacha_kind or 1)
        edge={1:(156,167,164),2:(206,141,232),3:(251,211,112)}.get(count,TEAL)
        title={1:'CARTA ÚNICA FABRICADA',2:'CARTA ÚNICA APRIMORADA',3:'CARTA ÚNICA EXCEPCIONAL'}.get(count,'CARTA ÚNICA FABRICADA')
        w,h=760,470; x=(W-w)//2; y=120
        panel=pygame.Surface((w,h),pygame.SRCALPHA); panel.fill((7,12,17,246)); pygame.draw.rect(panel,(*edge,255),(0,0,w-1,h-1),3,border_radius=10)
        self.canvas.blit(panel,(x,y))
        self.label(title,x+28,y+22,23,edge)
        cr=pygame.Rect(x+28,y+66,235,365)
        self.card_frame(cr,'Única')
        self.label('ÚNICA',cr.x+14,cr.y+14,9,edge)
        art_box=pygame.Rect(cr.x+12,cr.y+48,cr.width-24,154)
        pygame.draw.rect(self.canvas,(22,12,10),art_box,border_radius=6)
        pygame.draw.rect(self.canvas,edge,art_box,1,border_radius=6)
        self.draw_element_symbol(card.get('type'),art_box.center,26,glow=True)
        self.label(self.fit_text(format_card_name(card.get('name','Carta Única')),14,cr.width-24),cr.x+12,cr.y+222,14,INK)
        self.label(f"MEM {card.get('cost',0)}  |  DANO {card.get('damage',(0,0))[0]}–{card.get('damage',(0,0))[1]}",cr.x+12,cr.y+251,9,TEAL)
        self.label('ADICIONADA À POOL',cr.x+12,cr.y+282,9,edge)
        self.label(self.fit_text(format_card_name(card.get('name','Carta Única'))+variant_data['label'],19,435),x+295,y+70,19,INK)
        self.label(f"TIPO {card.get('type','-')}  •  {variant.upper()}  •  {count} BUFF{'S' if count != 1 else ''}",x+295,y+104,11,TEAL)
        yy=y+138
        data=self.state.unique_cards.get(cid,{})
        mult=UNIQUE_VARIANT_MULTIPLIERS.get(variant,1.0)
        for buff in data.get('buffs',[]):
            self.wrap(self._unique_buff_text(buff,mult),x+315,yy,390,12,GOLD,17); yy+=31
        momentum_kind=data.get('momentum')
        if momentum_kind in UNIQUE_MOMENTUM_DEFS:
            self.wrap('Momentum - ' + UNIQUE_MOMENTUM_DEFS[momentum_kind]['description'].format(type=card.get('type','-')),x+315,yy,390,11,GOLD,16); yy += 35
        self.label('Carta Única criada e adicionada à Pool de cartas.',x+295,y+335,11,TEAL)
        self.label('A carta está pronta para ser equipada no Slot Único.',x+295,y+358,10,MUTED)
        self.label('Feche o popup para continuar.',x+295,y+410,10,MUTED)

    def draw_craft_notice(self):
        if not self.craft_notice or self.craft_notice_until <= self.frame:
            if self.craft_notice_until <= self.frame:
                self.craft_notice = None; self.craft_notice_until = 0.0
            return
        if self.craft_reward_card_id or self.unique_gacha_card_id:
            return
        remaining=self.craft_notice_until-self.frame
        fade=1.0 if remaining>0.5 else max(0.0,remaining/0.5)
        w,h=600,92; x=(W-w)//2; y=650
        panel=pygame.Surface((w,h),pygame.SRCALPHA); alpha=int(238*fade)
        pygame.draw.rect(panel,(7,14,21,alpha),(0,0,w-1,h-1),border_radius=9)
        pygame.draw.rect(panel,(*GOLD,int(235*fade)),(0,0,w-1,h-1),1,border_radius=9)
        self.canvas.blit(panel,(x,y))
        self.label('OFICINA DE CARTAS',x+20,y+15,11,GOLD)
        self.label(self.fit_text(self.craft_notice,18,560),x+20,y+42,18,INK)

    def draw_craft_reward_popup(self):
        """Exibe a carta recém-fabricada como recompensa, sem alterar o fluxo do álbum."""
        cid = self.craft_reward_card_id
        if not cid or self.craft_reward_until <= self.frame:
            if self.craft_reward_until <= self.frame:
                self.craft_reward_card_id = None
                self.craft_reward_until = 0.0
            return
        try:
            card, variant_data, _, variant = self.state.card_data(cid)
        except ValueError:
            self.craft_reward_card_id = None
            self.craft_reward_until = 0.0
            return
        remaining = self.craft_reward_until - self.frame
        fade = 1.0 if remaining > 0.65 else max(0.0, remaining / 0.65)
        w, h = 760, 470
        x, y = (W - w) // 2, 120
        rarity = card.get('rarity', 'Comum')
        style = self.rarity_styles.get(rarity, self.rarity_styles['Comum'])
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = int(246 * fade)
        pygame.draw.rect(panel, (7, 14, 21, alpha), (0, 0, w - 1, h - 1), border_radius=10)
        pygame.draw.rect(panel, (*style['edge'], alpha), (0, 0, w - 1, h - 1), 2, border_radius=10)
        self.canvas.blit(panel, (x, y))

        self.label('RECOMPENSA FABRICADA', x + 30, y + 24, 24, style['accent'])
        self.label(self.fit_text(format_card_name(card.get('name', 'Carta')), 21, 440), x + 300, y + 66, 21, INK)
        self.label(f"{rarity.upper()}  •  {card.get('type','-').upper()}  •  {variant.upper()}", x + 300, y + 102, 11, style['accent'])
        self.label('A carta foi criada e adicionada à Pool de cartas.', x + 300, y + 134, 12, TEAL)
        self.label(f"MEM {card.get('cost',0)}  |  DANO {card.get('damage',(0,0))[0]}–{card.get('damage',(0,0))[1]}", x + 300, y + 174, 11, TEAL)
        bonus_lines = self.card_bonus_lines(card.get('attributes', {}))
        if bonus_lines:
            self.wrap('  |  '.join(bonus_lines), x + 300, y + 205, 420, 11, GOLD, 17)
        self._draw_scroll_text_box((x + 300, y + 252, 425, 106), card.get('description',''), 'craft_reward_effect', 11, INK, 16, style['edge'])

        cr = pygame.Rect(x + 28, y + 62, 235, 365)
        self.card_frame(cr, rarity)
        self.label(self.fit_text(rarity.upper(), 9, 150), cr.x + 14, cr.y + 14, 9, style['accent'])
        art_box = pygame.Rect(cr.x + 12, cr.y + 48, cr.width - 24, 154)
        pygame.draw.rect(self.canvas, (7, 15, 22), art_box, border_radius=6)
        pygame.draw.rect(self.canvas, style['edge'], art_box, 1, border_radius=6)
        if card.get('rarity') == 'Única':
            self.draw_element_symbol(card.get('type'), art_box.center, 26, glow=True)
        else:
            spr = self.sprites.get((card.get('species'), 0))
            if spr:
                max_w, max_h = art_box.width - 18, art_box.height - 12
                scale = min(max_w / max(1, spr.get_width()), max_h / max(1, spr.get_height()))
                im = pygame.transform.scale(spr, (max(1, int(spr.get_width() * scale)), max(1, int(spr.get_height() * scale))))
                self.canvas.blit(im, (art_box.centerx - im.get_width() / 2, art_box.centery - im.get_height() / 2 + 4))
            self.draw_element_symbol(card.get('type'), (art_box.right - 15, art_box.y + 15), 9)
        self.label(self.fit_text(format_card_name(card.get('name', 'Carta')), 14, cr.width - 24), cr.x + 12, cr.y + 222, 14, INK)
        self.label(f"MEM {card.get('cost',0)}  |  DANO {card.get('damage',(0,0))[0]}–{card.get('damage',(0,0))[1]}", cr.x + 12, cr.y + 251, 9, TEAL)
        self.label('ADICIONADA À POOL', cr.x + 12, cr.y + 282, 9, style['accent'])
        self.label('Feche o popup para continuar.', x + 300, y + 408, 10, MUTED)

    def title_screen(self):
        """Tela inicial minimalista, com espaço profundo e uma pequena paisagem planetária."""
        # Fundo espacial com duas faixas nebulosas discretas.
        self.canvas.fill((5, 10, 17))
        nebula = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.ellipse(nebula, (28, 66, 82, 22), (-170, 260, 980, 310))
        pygame.draw.ellipse(nebula, (79, 50, 83, 16), (430, 160, 960, 340))
        self.canvas.blit(nebula, (0, 0))

        # Estrelas com brilho pulsante determinístico.
        star_glow = pygame.Surface((W, H))
        star_glow.fill((0, 0, 0))
        for i, (x, y, r, phase, speed) in enumerate(self.title_stars):
            pulse = 0.38 + 0.62 * (0.5 + 0.5 * math.sin(self.frame * speed + phase))
            core = int(92 + 135 * pulse)
            # Três camadas simples somadas ao fundo simulam um pequeno bloom.
            glow_r = max(r + 2, int(r * (2.0 + pulse)))
            glow_c = int(16 + 62 * pulse)
            pygame.draw.circle(star_glow, (glow_c, glow_c, min(255, glow_c + 10)), (x, y), glow_r)
            pygame.draw.circle(star_glow, (int(glow_c*1.8), int(glow_c*1.8), min(255, int(glow_c*1.95))), (x, y), max(r+1, int(r*1.35)))
            pygame.draw.circle(star_glow, (core, core, min(255, core + 15)), (x, y), r)
            if r >= 3 and pulse > 0.82:
                pygame.draw.line(star_glow, (core, core, core), (x-r-2, y), (x+r+2, y), 1)
                pygame.draw.line(star_glow, (core, core, core), (x, y-r-2), (x, y+r+2), 1)
        self.canvas.blit(star_glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Pequena composição de planetas sem interface extra.
        # Planeta 1: azul/teal, maior e mais próximo.
        pygame.draw.circle(self.canvas, (34, 82, 104), (238, 530), 96)
        pygame.draw.circle(self.canvas, (47, 112, 127), (220, 510), 73)
        pygame.draw.circle(self.canvas, (68, 136, 141), (204, 496), 32)

        # Planeta 2: quente. É o único planeta com anéis, agora largos e proporcionais.
        ring = pygame.Surface((270, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(ring, (186, 156, 119, 210), (10, 25, 250, 54), 5)
        pygame.draw.ellipse(ring, (94, 75, 67, 190), (0, 17, 270, 72), 2)
        self.canvas.blit(ring, (760, 465))
        pygame.draw.circle(self.canvas, (114, 71, 54), (895, 495), 67)
        pygame.draw.circle(self.canvas, (155, 91, 59), (884, 482), 49)
        pygame.draw.line(self.canvas, (191, 121, 72), (859, 461), (924, 505), 5)

        # Planeta 3: pequeno e pálido ao fundo, sem anéis.
        pygame.draw.circle(self.canvas, (77, 86, 106), (1010, 202), 36)
        pygame.draw.circle(self.canvas, (116, 130, 150), (999, 191), 21)

        # Lua pequena.
        pygame.draw.circle(self.canvas, (122, 126, 132), (1003, 275), 11)
        pygame.draw.circle(self.canvas, (77, 86, 96), (999, 271), 7)

        # Moldura central muito discreta, mantendo a linguagem dos menus.
        pygame.draw.line(self.canvas, EDGE, (280, 124), (920, 124), 1)
        pygame.draw.line(self.canvas, EDGE, (360, 665), (840, 665), 1)

        title = self.font(48).render('CINZAS DE ÓRION', True, GOLD)
        self.canvas.blit(title, (W//2 - title.get_width()//2, 56))
        sub = self.font(14).render('RUMO AO DESCONHECIDO', True, TEAL)
        self.canvas.blit(sub, (W//2 - sub.get_width()//2, 112))

        pulse = 0.70 + 0.30 * (0.5 + 0.5 * math.sin(self.frame * 2.5))
        prompt_color = tuple(int(v * pulse) for v in (230, 234, 226))
        prompt = self.font(20).render('Pressione qualquer tecla para começar', True, prompt_color)
        self.canvas.blit(prompt, (W//2 - prompt.get_width()//2, 684))
        self.label('CONTINUAÇÃO AUTOMÁTICA DO ÚLTIMO SAVE', W//2 - 162, 716, 11, MUTED)

    def start_from_title(self):
        """Recarrega o save persistido e entra na primeira tela apropriada."""
        self.state, self.message = load_campaign(SAVE_DIR, legacy_directories=(ROOT,), current_filename='save.json')
        self.state.refresh_journal()
        self.selected_route_id = getattr(self.state, 'selected_planet', 'veyra')
        self.visual_pos = [float(x) for x in self.state.pos]
        self.sync_sector()
        self.mode = 'opening' if self.state.opening_dialogue_pending else ('game_over' if self.state.game_over else ('ship' if self.state.inside_ship else 'world'))
        self.nav_stack = []
        self.panel_return_mode = 'world'
        self.menu_return_mode = 'world'
        self.set_message('Save carregado.')

    def opening_scene(self):
        self.label('A NAVE // PONTO DE RUPTURA', 70, 54, 22, TEAL)
        self.box((70,120,1060,480),(7,15,22),EDGE)
        self.actor('hero', 250, 410, 1.55, int(self.frame*2), direction='down')
        bubble = pygame.Rect(365, 175, 650, 260)
        pygame.draw.rect(self.canvas,(225,230,220),bubble,border_radius=12)
        pygame.draw.polygon(self.canvas,(225,230,220),[(390,410),(350,455),(450,425)])
        text = ('Foi sofrido escapar... e eu nem sei em que planeta vim parar.\n\n'
                'A nave está quebrada e este lugar parece hostil.\n'
                'Preciso reconstruir o Tanque de Renascimento.\n\n'
                'Seria melhor ter uma segunda chance.')
        self.wrap(text,395,205,585,19,(27,34,39),28)
        self.label('ESPAÇO / ENTER  — continuar', 400, 650, 14, GOLD)

    def finish_opening_scene(self):
        self.state.finish_opening_dialogue()
        self.set_message('MISSÃO ADQUIRIDA: Tanque de Renascimento.')
        self.reset_mode('ship')
        self.checkpoint()

    def game_over_scene(self):
        self.box((110,160,980,470),(7,15,22),(224,112,93))
        self.label('SINAL ENCERRADO', 340, 225, 34, (224,112,93))
        self.wrap('Você ficou fora de combate antes de reconstruir o Tanque de Renascimento.',340,295,520,18,INK,26)
        self.label('ESPAÇO / ENTER  — iniciar nova campanha', 340, 500, 14, GOLD)

    def new_campaign(self):
        self.state = State(new_game=True)
        self.mode = 'opening'
        self.nav_stack = []
        self.selected_route_id = 'veyra'
        self.visual_pos = [float(x) for x in self.state.pos]
        self.set_message('')
        self._sync_navigation_context()

    def draw_language_qte(self):
        q = self.language_qte or {}
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((5,10,14,190)); self.canvas.blit(overlay,(0,0))
        w,h=720,315; x=(W-w)//2; y=220
        self.box((x,y,w,h),(7,15,22),GOLD)
        civ = CIVILIZATIONS.get(q.get('civilization'), {})
        self.label('CALIBRAÇÃO LINGUÍSTICA',x+45,y+34,28,GOLD)
        self.wrap(f'IDIOMA NÃO RECONHECIDO — {civ.get("name","CIVILIZAÇÃO DESCONHECIDA")}',x+45,y+86,620,16,INK,22)
        self.wrap('O Elmo está tentando comparar padrões de som, ritmo e resposta para alimentar a database linguística. Sincronize a Manopla com a faixa central.',x+45,y+132,620,13,MUTED,19)
        left=x+45; width=630; line_y=y+215
        pygame.draw.rect(self.canvas,(15,28,34),(left,line_y,width,14),border_radius=6)
        pygame.draw.rect(self.canvas,(54,110,104),(left+int(width*.42),line_y,int(width*.16),14),border_radius=5)
        phase=(self.frame*float(q.get('speed',2.35)))%1.0
        marker=left+int(width*phase)
        pygame.draw.line(self.canvas,GOLD,(marker,line_y-16),(marker,line_y+30),4)
        self.label(f'PRESSIONE  {q.get("key","F")}  NA FAIXA CENTRAL',left,line_y+43,17,TEAL)
        remaining=max(0.0,float(q.get('until',self.frame))-self.frame)
        self.bar(left,line_y+73,width,remaining,float(q.get('seconds',9.0)),TEAL if remaining>3 else GOLD)
        self.label(f'{remaining:0.1f}s',x+570,y+275,15,GOLD)

    def draw_stasis_qte(self):
        q = self.stasis_qte or {}
        overlay = pygame.Surface((W,H),pygame.SRCALPHA)
        overlay.fill((5,10,14,190)); self.canvas.blit(overlay,(0,0))
        w,h=700,280; x=(W-w)//2; y=235
        pygame.draw.rect(self.canvas,(8,18,24),(x,y,w,h),border_radius=12)
        pygame.draw.rect(self.canvas,GOLD,(x,y,w,h),3,border_radius=12)
        self.label('ESCUDO STASIS', x+55, y+35, 30, GOLD)
        self.wrap(f'ATAQUE FATAL DETECTADO — {q.get("name", "Ataque fatal")}',x+55,y+86,590,17,INK,24)
        self.label(f'PRESSIONE  {q.get("key","F")}  NA FAIXA CENTRAL', x+55, y+145, 18, TEAL)
        left=x+55; width=590; line_y=y+205
        pygame.draw.rect(self.canvas,(15,28,34),(left,line_y,width,14),border_radius=6)
        pygame.draw.rect(self.canvas,(54,110,104),(left+int(width*.42),line_y,int(width*.16),14),border_radius=5)
        phase=(self.frame*float(q.get('speed',2.25)))%1.0
        marker=left+int(width*phase)
        pygame.draw.line(self.canvas,GOLD,(marker,line_y-16),(marker,line_y+30),4)
        remaining=max(0.0,float(q.get('until',self.frame))-self.frame)
        seconds=max(0.1,float(q.get('seconds',10.0)))
        self.bar(left,line_y+42,width,remaining,seconds,TEAL if remaining>seconds*.35 else GOLD)
        self.label(f'{remaining:0.1f}s', x+560, y+252, 16, GOLD)

    def draw(self):
        self.canvas.fill(BG)
        self.buttons = []
        self.scrollbars = {}
        if self.mode == 'gauntlet' and self.card_picker_slot is not None:
            self.card_picker()
        else:
            {'title': self.title_screen, 'opening': self.opening_scene, 'game_over': self.game_over_scene, 'stasis': self.battle_view, 'language_qte': self.world, 'world': self.world, 'battle': self.battle_view, 'album': self.album,
             'craft': self.craft_view, 'inventory': self.inventory, 'equipment': self.equipment, 'tech': self.technology, 'resources': self.resources, 'status': self.status,
             'ship_popup': self.ship_popup_view,
             'ship_mission': self.ship_mission, 'ship_communications': self.ship_communications,
             'victory': self.victory, 'travel': self.travel_scene, 'asteroids': self.asteroid_encounter_scene, 'statistics': self.statistics_view, 'bestiary': self.bestiary, 'pause': self.pause, 'routes': self.routes, 'journal': self.journal, 'ship_diag': self.ship_diagnostic, 'dialogue': self.dialogue, 'mission_choice': self.mission_choice, 'hack': self.hack, 'achievements': self.achievements, 'gauntlet_nexus': self.gauntlet_nexus, 'domain': self.domain_view, 'loadouts': self.loadouts, 'civilization_missions': self.civilization_missions_view, 'gauntlet': self.gauntlet, 'simulator': self.simulator, 'ship': self.ship_interior, 'ship_computer': self.ship_computer, 'cockpit': self.cockpit, 'chest': self.chest, 'helmet_config': self.helmet_config, 'renown': self.renown, 'menu': self.menu}[self.mode]()
        if self.mode != 'title':
            self.message_hud()
        self.draw_achievement_alert()
        self.draw_unique_gacha_alert()
        self.draw_craft_reward_popup()
        self.draw_craft_notice()
        if self.mode == 'battle':
            self.draw_challenge_menu()
        if self.mode == 'stasis':
            self.draw_stasis_qte()
        elif self.mode == 'language_qte':
            self.draw_language_qte()
        ww, wh = self.window.get_size()
        scale = min(ww/W, wh/H)
        size = (max(1, int(W*scale)), max(1, int(H*scale)))
        self.window.fill(BG)
        self.window.blit(pygame.transform.scale(self.canvas, size), ((ww-size[0])//2, (wh-size[1])//2))
        pygame.display.flip()

    def event(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
            return
        if ev.type == pygame.MOUSEWHEEL:
            mx, my = self.mouse()
            delta = -42 * ev.y
            regions = {
                'journal': ('journal', pygame.Rect(635, 238, 503, 410)),
                'journal_list': ('journal_list', pygame.Rect(55, 164, 510, 510)),
                'status_left': ('status_left', pygame.Rect(35, 145, 535, 500)),
                'status_right': ('status_right', pygame.Rect(590, 135, 555, 500)),
                'inventory_materials': ('inventory_materials', pygame.Rect(58, 175, 444, 447)),
                'inventory_details': ('inventory_details', pygame.Rect(590, 175, 540, 447)),
                'resources': ('resources', pygame.Rect(58, 175, 1080, 520)),
                'card_picker': ('card_picker', pygame.Rect(78, 174, 645, 420)),
                'card_picker_preview': ('card_picker_preview', pygame.Rect(922, 215, 165, 215)),
                'gauntlet_nexus': ('gauntlet_nexus', pygame.Rect(35, 318, 1130, 350)),
                'domain': ('domain', pygame.Rect(55,332,720,310)),
                'civilization_missions': ('civilization_missions', pygame.Rect(785,160,330,470)),
                'combat_result': ('combat_result', pygame.Rect(58, 242, 1065, 350)),
                'unique_card_craft': ('unique_card_craft', pygame.Rect(58, 232, 574, 385)),
                'statistics': ('statistics', pygame.Rect(58,190,1080,470)),
                'bestiary': ('bestiary', pygame.Rect(58,150,1080,520)),
                'bestiary_detail': ('bestiary_detail', pygame.Rect(78,470,700,190)),
                'bestiary_list': ('bestiary_list', pygame.Rect(870,165,270,485)),
                'renown': ('renown', pygame.Rect(58,150,1080,520)),
                'routes_right': ('routes_right', pygame.Rect(614,165,512,505)),
                'stellar_destinations': ('stellar_destinations', pygame.Rect(790,198,295,207)),
                'achievements': ('achievements', pygame.Rect(58,174,1068,490)),
                'helmet_config': ('helmet_config', pygame.Rect(58,160,1060,490)),
                'card_effect_0': ('card_effect_0', pygame.Rect(45,390,335,150)),
                'card_effect_1': ('card_effect_1', pygame.Rect(425,390,335,150)),
                'card_effect_2': ('card_effect_2', pygame.Rect(805,390,335,150)),
                'card_bonus_0': ('card_bonus_0', pygame.Rect(45,565,335,43)),
                'card_bonus_1': ('card_bonus_1', pygame.Rect(425,565,335,43)),
                'card_bonus_2': ('card_bonus_2', pygame.Rect(805,565,335,43)),
                'unique_effect_0': ('unique_effect_0', pygame.Rect(45,397,335,125)),
                'unique_effect_1': ('unique_effect_1', pygame.Rect(425,397,335,125)),
                'unique_effect_2': ('unique_effect_2', pygame.Rect(805,397,335,125)),
                'craft_effect_0': ('craft_effect_0', pygame.Rect(54,235,385,45)),
                'craft_effect_1': ('craft_effect_1', pygame.Rect(54,356,385,45)),
                'craft_effect_2': ('craft_effect_2', pygame.Rect(54,477,385,45)),
                'craft_effect_3': ('craft_effect_3', pygame.Rect(54,598,385,45)),
            }
            if self.mode in ('journal','status','inventory','gauntlet_nexus','domain','resources','gauntlet','ship_mission','routes','achievements','helmet_config','album','bestiary','victory','civilization_missions','loadouts'):
                for key, (_, rect) in regions.items():
                    if rect.collidepoint((mx, my)) and key in self.scrollbars:
                        max_scroll = self.scrollbars[key]['max']
                        self.ui_scroll[key] = max(0, min(max_scroll, self.ui_scroll.get(key, 0) + delta))
                        break
            return
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            # Popups de recompensa fecham com qualquer clique e não deixam a
            # interface abaixo receber o clique acidentalmente.
            if self.craft_reward_card_id or self.unique_gacha_card_id:
                self.craft_reward_card_id = None
                self.craft_reward_until = 0.0
                self.unique_gacha_card_id = None
                self.unique_gacha_until = 0.0
                self.unique_gacha_kind = None
                return
            mx, my = self.mouse()
            for key, data in self.scrollbars.items():
                if data['max'] <= 0:
                    continue
                if data['thumb'].collidepoint((mx, my)):
                    self.scroll_drag = key
                    return
                if data['rect'].collidepoint((mx, my)):
                    self._scroll_from_mouse(key, my)
                    return
            for rect, callback, enabled in self.buttons:
                if enabled and rect.collidepoint((mx, my)):
                    callback(); break
            return
        if ev.type == pygame.MOUSEMOTION and self.scroll_drag:
            self._scroll_from_mouse(self.scroll_drag, self.mouse()[1])
            return
        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.scroll_drag = None
            return
        if ev.type != pygame.KEYDOWN:
            return
        if self.mode == 'title':
            self.start_from_title()
            return
        if self.mode == 'gauntlet' and self.card_picker_slot is not None and ev.key == pygame.K_ESCAPE:
            self.close_card_picker()
            return
        if self.mode == 'battle' and self.challenge_menu_open:
            if ev.key == pygame.K_ESCAPE:
                self.challenge_menu_open=False
            return
        if self.mode == 'battle':
            if ev.key == pygame.K_TAB:
                self.selected_battle_target = self.state.cycle_battle_target(1) or self.selected_battle_target
                return
            choices = {pygame.K_1: 'basic', pygame.K_5: 'kit', pygame.K_6: 'flee'}
            choices.update({pygame.K_2+i: cid for i, cid in enumerate(self.state.slots) if cid})
            if ev.key in choices: self.choose(choices[ev.key])
            elif ev.key == pygame.K_7 and self.state.battle and self.state.battle.get('boss'): self.choose('pure_water')
            return
        if self.mode == 'ship_popup':
            if ev.key == pygame.K_ESCAPE:
                self.close_panel(); return
            kind=self.ship_popup_kind or ''
            if kind == 'dobra_core_confirm' and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_dobra_core(); return
            if kind == 'respawn_confirm' and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_respawn_tank(); return
            if kind == 'essence_storage' and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                if int(self.state.inventory.get('Essência',0)) > 0:
                    self._deposit_essence_from_popup()
                return
            return
        if self.mode == 'ship_mission':
            mid=self.ship_mission_id
            mission=self.state.missions.get(mid,{})
            if mid=='ship_hull' and ev.key==pygame.K_SPACE:
                phase=(self.frame*1.6)%1.0
                if .40 <= phase <= .60:
                    mission['progress']=mission.get('progress',0)+1
                    if mission['progress']>=3:
                        ok,msg=self.state.complete_ship_mission(mid); self.set_message(msg); self.close_panel(); self.checkpoint()
                    else: self.set_message(f'Pulso sincronizado. {mission["progress"]}/3.')
                else:
                    self.set_message('Pulso fora da ressonância estrutural.')
                return
            if mid=='ship_power' and ev.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_LEFT,pygame.K_RIGHT):
                vals=mission.setdefault('values',[20,30,25,25]); idx=getattr(self,'ship_power_idx',0)
                if ev.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4): self.ship_power_idx=ev.key-pygame.K_1; return
                delta=-5 if ev.key==pygame.K_LEFT else 5
                j=getattr(self,'ship_power_idx',0); vals[j]=max(0,min(50,vals[j]+delta)); return
            if mid=='ship_propulsion' and ev.key in (pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT):
                key={pygame.K_UP:'up',pygame.K_DOWN:'down',pygame.K_LEFT:'left',pygame.K_RIGHT:'right'}[ev.key]
                seq=mission.get('sequence',['up','right','down','left']); cur=int(mission.get('cursor',0))
                if cur >= len(seq):
                    self.set_message('Sequência de propulsão já concluída. Retome pelo diagnóstico da nave.')
                    return
                if key==seq[cur]:
                    cur+=1; mission['cursor']=cur
                    if cur>=len(seq):
                        ok,msg=self.state.complete_ship_mission(mid); self.set_message(msg); self.close_panel(); self.checkpoint()
                    else: self.set_message('Vetor confirmado.')
                else:
                    mission['cursor']=0; self.set_message('Sequência vetorial inválida. Recomece a calibração.')
                return
            if mid=='ship_ftl' and ev.key==pygame.K_SPACE:
                phase=(self.frame*2.1)%1.0
                if .45 <= phase <= .55:
                    mission['progress']=mission.get('progress',0)+1
                    if mission['progress']>=3:
                        ok,msg=self.state.complete_ship_mission(mid); self.set_message(msg); self.close_panel(); self.checkpoint()
                    else: self.set_message(f'Fase estabilizada. {mission["progress"]}/3.')
                else:
                    self.set_message('Janela de dobra perdida. Recalibrando.')
                return
            if mid=='ship_navigation' and ev.key==pygame.K_SPACE:
                self._ship_navigation_try()
                return
            return

        if self.mode == 'opening':
            if ev.key in (pygame.K_SPACE, pygame.K_RETURN): self.finish_opening_scene()
            return
        if self.mode == 'game_over':
            if ev.key in (pygame.K_SPACE, pygame.K_RETURN): self.new_campaign()
            return
        if self.mode == 'language_qte':
            if ev.key in (pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_q,pygame.K_w,pygame.K_e):
                keymap={pygame.K_a:'A',pygame.K_s:'S',pygame.K_d:'D',pygame.K_f:'F',pygame.K_q:'Q',pygame.K_w:'W',pygame.K_e:'E'}
                q=self.language_qte or {}
                expected=str(q.get('key','F')).upper()
                correct_key=keymap.get(ev.key)==expected
                phase=(self.frame*float(q.get('speed',2.35)))%1.0
                in_window=.42 <= phase <= .58
                if correct_key and in_window:
                    ok,msg=self.state.learn_language(q.get('civilization'))
                    self.language_qte=None
                    self.set_message(msg)
                    self.mode='dialogue'; self.nav_stack=['world']; self._sync_navigation_context()
                    self.checkpoint()
                else:
                    self.state.pending_language_civilization=None; self.state.pending_language_npc_id=None
                    self.language_qte=None
                    self.set_message('CALIBRAÇÃO FALHOU — o padrão não foi sincronizado. Tente novamente em outro contato.')
                    self.reset_mode('world'); self.checkpoint()
            return
        if self.mode == 'stasis':
            if ev.key in (pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_q,pygame.K_w,pygame.K_e):
                keymap={pygame.K_a:'A',pygame.K_s:'S',pygame.K_d:'D',pygame.K_f:'F',pygame.K_q:'Q',pygame.K_w:'W',pygame.K_e:'E'}
                q=self.stasis_qte or {}
                expected=str(q.get('key','F')).upper()
                correct_key=keymap.get(ev.key)==expected
                # O Escudo Stasis exige não apenas a tecla correta, mas a
                # sincronização do cursor com a faixa central de reação.
                phase=(self.frame*float(q.get('speed',2.25)))%1.0
                in_window=.42 <= phase <= .58
                success=bool(correct_key and in_window)
                result=self.state.resolve_stasis(success)
                if success:
                    self.set_message(result.get('message',''))
                    self.stasis_qte=None
                    self.mode='battle'; self.phase='choose'; self.phase_time=0.0; self.result={'win':False}
                else:
                    self.set_message('ESCUDO STASIS FALHOU — o bloqueio não encontrou a janela de sincronização.' if correct_key else 'ESCUDO STASIS FALHOU — tecla incorreta.')
                    self.stasis_qte=None
                    self.reset_mode('game_over' if self.state.game_over else 'ship')
                    if not self.state.game_over:
                        self.checkpoint()
            return
        if self.mode == 'asteroids':
            if ev.key == pygame.K_SPACE:
                self.fire_asteroid_laser()
            return
        if self.mode == 'travel':
            if ev.key == pygame.K_SPACE:
                if self.travel_encounter_pending:
                    self.start_asteroid_encounter()
                else:
                    self.finish_planet_travel()
            return
        if self.mode == 'hack':
            actions = {pygame.K_UP:'up', pygame.K_DOWN:'down', pygame.K_LEFT:'left', pygame.K_RIGHT:'right', pygame.K_SPACE:'breach'}
            if self.state.gauntlet_nexus_hack_diagonal:
                actions.update({pygame.K_KP7:'up_left', pygame.K_KP9:'up_right', pygame.K_KP1:'down_left', pygame.K_KP3:'down_right'})
            if ev.key == pygame.K_ESCAPE:
                self.state.hack=None; self.reset_mode('world'); self.set_message('Intrusão abandonada.')
            elif ev.key in actions:
                self.hack_event(actions[ev.key])
            return
        if ev.key == pygame.K_ESCAPE:
            if self.mode == 'menu':
                self.close_menu()
            elif self.mode == 'world':
                self.open_menu()
            elif self.mode == 'ship':
                self.reset_mode('world'); self.state.leave_ship()
                self.set_message('Você saiu da nave. A escotilha permanece acessível ao lado dela.')
            elif self.mode in ('craft','equipment','inventory','album','routes','journal','tech','resources','status','ship_diag','ship_popup','ship_mission','ship_communications','dialogue','mission_choice','achievements','statistics','bestiary','gauntlet_nexus','domain','gauntlet','ship_computer','cockpit','simulator','chest','renown','travel'):
                self.close_panel()
            elif self.mode == 'victory':
                self.reset_mode('world')
            elif self.mode == 'travel':
                self.travel_target_planet = None
                self.travel_origin_planet = None
                self.travel_time = 0.0
                self.mode = 'cockpit'
                self.nav_stack = []
                self._sync_navigation_context()
            return
        if self.mode == 'dialogue':
            if ev.key in (pygame.K_SPACE, pygame.K_1): self.accept_mission()
            return
        if self.mode == 'mission_choice':
            actions={pygame.K_1:'repair', pygame.K_2:'force', pygame.K_3:'hack'}
            if ev.key in actions: self.mission_action(actions[ev.key])
            return
        if self.mode == 'menu':
            actions={pygame.K_j:lambda:self.open_panel('journal','menu'), pygame.K_m:lambda:self.open_panel('routes','menu'), pygame.K_b:lambda:self.open_panel('album','menu'), pygame.K_i:lambda:self.open_panel('inventory','menu'), pygame.K_g:lambda:self.open_panel('equipment','menu'), pygame.K_t:lambda:self.open_panel('tech','menu'), pygame.K_v:lambda:self.open_panel('status','menu'), pygame.K_l:lambda:self.open_panel('achievements','menu'), pygame.K_y:lambda:self.open_panel('statistics','menu'), pygame.K_n:lambda:self.open_panel('bestiary','menu'), pygame.K_r:lambda:self.open_panel('renown','menu'), pygame.K_F5:self.save, pygame.K_q:lambda:setattr(self,'running',False)}
            if ev.key in actions: actions[ev.key]()
            return
        if self.mode == 'ship':
            actions={pygame.K_e:self.interact, pygame.K_c:lambda:self.open_panel('ship_computer','ship'), pygame.K_v:lambda:self.open_ship_diagnostic('ship'), pygame.K_g:lambda:self.open_panel('equipment','ship'), pygame.K_i:lambda:self.open_panel('inventory','ship'), pygame.K_j:lambda:self.open_panel('journal','ship'), pygame.K_b:lambda:self.open_panel('album','ship'), pygame.K_t:lambda:self.open_panel('tech','ship'), pygame.K_F5:self.save}
            if ev.key in actions: actions[ev.key]()
            return
        if self.mode == 'world':
            actions={pygame.K_e:self.interact, pygame.K_b:lambda:self.open_panel('album','world'), pygame.K_i:lambda:self.open_panel('inventory','world'), pygame.K_j:lambda:self.open_panel('journal','world'), pygame.K_r:self.rest, pygame.K_F5:self.save, pygame.K_m:lambda:self.open_panel('routes','world'), pygame.K_t:lambda:self.open_panel('tech','world'), pygame.K_v:lambda:self.open_panel('status','world'), pygame.K_g:lambda:self.open_panel('equipment','world'), pygame.K_l:lambda:self.open_panel('achievements','world'), pygame.K_y:lambda:self.open_panel('statistics','world'), pygame.K_n:lambda:self.open_panel('bestiary','world'), pygame.K_x:lambda:self.open_panel('gauntlet_nexus','world')}
            if ev.key in actions: actions[ev.key]()
            return
        if self.mode in ('craft','equipment','inventory','album','routes','journal','tech','resources','status','ship_diag','ship_popup','ship_mission','ship_communications','achievements','gauntlet_nexus','domain','gauntlet','ship_computer','cockpit','simulator','chest','helmet_config','renown'):
            if ev.key == pygame.K_F5: self.save()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60)/1000, .1)
            for ev in pygame.event.get():
                self.event(ev)
            self.advance(dt)
            self.draw()
        if not self.state.battle and not self.state.opening_dialogue_pending:
            self.save()
        pygame.quit()


if __name__ == '__main__':
    App().run()
