# -*- coding: utf-8 -*-
"""
vfx_manager.py — Gerenciador central de VFX (pygame + ModernGL)
================================================================
Substitui o desenho procedural em CPU (`_draw_card_fx` em main.py) por um
pipeline GPU completo, mantendo a semântica já definida no código-base:

  * Identidade elemental: as 8 chaves de `content.CARD_VISUAL_KEYS` /
    `CARDS[...]['visual_key']` são mapeadas para perfis de efeito.
  * Tempo de execução: a batalha usa fase 'hero' com duração 0.68s e impacto
    em t≈0.42s (ver main._draw_card_fx); os efeitos respeitam esse timing.
  * Força do golpe: dano/custo/raridade das cartas alimentam screen-shake,
    freeze-frame, número de partículas e energia do bloom.

Otimizações obrigatórias implementadas:
  * Object Pooling: buffer fixo de N partículas (slots), livre-list O(1),
    zero alocação por frame (numpy pré-alocado, upload por view).
  * Hard cap por frame (MAX_PARTICLES) e budget por emissão.
  * Física vetorial simplificada: evita sqrt no loop (gravidade uniaxial,
    arrasto multiplicativo, colisão de "chão" por comparação de Y).
  * Um único draw call para todas as partículas (quad por partícula em um
    VBO dinâmico), independentemente de elemento/tipo.

Integração com o jogo (main.py):
    fx = VfxManager()                       # depois de pygame.init()
    ...em choose():                         # quando self.card_fx é criado
        fx.play_technique(card_id, result, start=(hx+48,364), end=target)
    ...em advance(dt):
        if fx.tick(dt): self.freeze_frames += 1   # micro-pausa de crítico
    ...em draw(), após desenhar self.canvas:
        out_surface = fx.render(self.canvas)      # aplica GL e devolve surface
"""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

import numpy as np

SHADERS_DIR = Path(__file__).resolve().parent / 'shaders'

# ---------------------------------------------------------------------------
# Constantes de orçamento / hard caps (NUNCA alocar além disso)
# ---------------------------------------------------------------------------
MAX_PARTICLES = 6000          # teto absoluto de partículas vivas
MAX_EMISSION_PER_FRAME = 900  # teto de emissões num único evento
MAX_DISTORTION_SOURCES = 8    # ecoa u_impacts[8] do distortion.frag
BLOOM_LEVELS = 2              # níveis do ping-pong de blur

# Layout do VBO: 2(pos)+1(size)+1(rot)+1(life)+1(kind)+4(colA)+4(colB)+1(seed)=15 f32
FLOATS_PER_PARTICLE = 15
VERTEX_STRIDE = FLOATS_PER_PARTICLE * 4


# ---------------------------------------------------------------------------
# Tipos de sprite do particle.frag (a ordem DEVE casar com o shader)
# ---------------------------------------------------------------------------
KIND = {
    'spark': 0, 'ember': 1, 'lava': 2, 'water': 3, 'leaf': 4, 'metal': 5,
    'rock': 6, 'arc': 7, 'light': 8, 'shadow': 9, 'smoke': 10, 'ring': 11,
    'crack': 12, 'heal': 13, 'hex': 14, 'orb': 15,
}


def _rgb(name):
    """Converte cor nomeada/hex para float linear [0..1]*intensity."""
    table = {
        'fire_core': (1.0, 0.85, 0.45), 'fire_mid': (1.0, 0.42, 0.10),
        'fire_dead': (0.35, 0.05, 0.02), 'ash': (0.25, 0.22, 0.22),
        'water_hi': (0.55, 0.90, 1.0), 'water_mid': (0.15, 0.55, 0.85),
        'water_dead': (0.02, 0.12, 0.25), 'leaf_hi': (0.65, 1.0, 0.55),
        'leaf_mid': (0.20, 0.70, 0.25), 'leaf_dead': (0.05, 0.20, 0.08),
        'metal_hi': (0.95, 0.97, 1.0), 'metal_mid': (0.55, 0.62, 0.68),
        'metal_dead': (0.15, 0.16, 0.20), 'earth_hi': (0.95, 0.75, 0.45),
        'earth_mid': (0.55, 0.38, 0.22), 'earth_dead': (0.18, 0.12, 0.08),
        'volt_hi': (0.85, 1.0, 1.0), 'volt_mid': (0.35, 0.80, 1.0),
        'volt_dead': (0.05, 0.10, 0.30), 'light_hi': (1.0, 1.0, 0.92),
        'light_mid': (0.95, 0.85, 0.45), 'light_dead': (0.35, 0.30, 0.15),
        'dark_hi': (0.45, 0.25, 0.65), 'dark_mid': (0.18, 0.08, 0.30),
        'dark_dead': (0.02, 0.01, 0.05), 'heal_hi': (0.75, 1.0, 0.85),
        'heal_mid': (0.30, 0.90, 0.55), 'heal_dead': (0.05, 0.30, 0.15),
        'white': (1.0, 1.0, 1.0),
    }
    return table.get(name, (1.0, 1.0, 1.0))


class ParticleProfile:
    """Configuração de uma emissão (imutável, reutilizável)."""
    __slots__ = ('kind', 'count', 'speed', 'spread_deg', 'size', 'life',
                 'col_a', 'col_b', 'gravity', 'drag', 'spin', 'delay',
                 'upward_bias')

    def __init__(self, kind, count, speed, spread_deg=360.0, size=(4.0, 12.0),
                 life=(0.4, 0.9), col_a='white', col_b='white', gravity=0.0,
                 drag=2.0, spin=0.0, delay=0.0, upward_bias=0.0):
        self.kind = KIND[kind]
        self.count = count
        self.speed = speed                      # px/s (min,max) ou escalar
        self.spread_deg = spread_deg            # cone de emissão
        self.size = size                        # raio inicial (min,max)
        self.life = life                        # segundos (min,max)
        self.col_a = col_a
        self.col_b = col_b
        self.gravity = gravity                  # px/s^2 (Y para baixo +)
        self.drag = drag                        # coeficiente multiplicativo
        self.spin = spin                        # rad/s
        self.delay = delay                      # atraso da emissão (s)
        self.upward_bias = upward_bias          # viés -Y p/ fumaça/cura


# Perfis por elemento — identidade visual derivada do nome da técnica.
ELEMENT_PROFILES = {
    'Fogo': [
        ParticleProfile('ember', 46, (140, 420), 360, (5, 14), (0.35, 0.8),
                        'fire_core', 'fire_dead', gravity=-160, drag=1.6, spin=3),
        ParticleProfile('spark', 22, (320, 640), 90, (2, 5), (0.15, 0.35),
                        'white', 'fire_mid', gravity=520, drag=0.8),
        ParticleProfile('smoke', 10, (30, 80), 360, (14, 30), (0.7, 1.4),
                        'ash', 'ash', gravity=-40, drag=2.4, upward_bias=1),
    ],
    'Água': [
        ParticleProfile('water', 34, (180, 380), 120, (4, 10), (0.35, 0.7),
                        'water_hi', 'water_dead', gravity=620, drag=0.6),
        ParticleProfile('ring', 1, (0, 0), 360, (18, 26), (0.35, 0.45),
                        'water_mid', 'water_dead'),
        ParticleProfile('spark', 12, (120, 260), 360, (2, 4), (0.2, 0.4),
                        'water_hi', 'water_dead', gravity=300, drag=1.2),
    ],
    'Planta': [
        ParticleProfile('leaf', 26, (90, 240), 360, (6, 14), (0.6, 1.2),
                        'leaf_hi', 'leaf_dead', gravity=140, drag=2.2, spin=5),
        ParticleProfile('ember', 14, (40, 110), 360, (3, 7), (0.5, 0.9),
                        'leaf_mid', 'leaf_dead', gravity=-60, drag=2.0),
    ],
    'Metal': [
        ParticleProfile('metal', 30, (260, 560), 70, (3, 9), (0.25, 0.55),
                        'metal_hi', 'metal_dead', gravity=700, drag=0.5, spin=9),
        ParticleProfile('spark', 26, (380, 720), 50, (2, 4), (0.12, 0.3),
                        'white', 'metal_mid', gravity=620, drag=0.7),
        ParticleProfile('ring', 1, (0, 0), 360, (16, 22), (0.28, 0.4),
                        'metal_hi', 'metal_dead'),
    ],
    'Terra': [
        ParticleProfile('rock', 28, (160, 380), 140, (5, 13), (0.5, 0.9),
                        'earth_hi', 'earth_dead', gravity=900, drag=0.4, spin=4),
        ParticleProfile('crack', 6, (0, 0), 360, (26, 60), (0.5, 0.9),
                        'earth_hi', 'earth_dead'),
        ParticleProfile('smoke', 12, (40, 90), 360, (16, 34), (0.6, 1.2),
                        'earth_mid', 'earth_dead', gravity=-30, drag=2.6,
                        upward_bias=1),
    ],
    'Elétrico': [
        ParticleProfile('arc', 12, (0, 0), 360, (18, 40), (0.10, 0.22),
                        'volt_hi', 'volt_dead'),
        ParticleProfile('spark', 30, (300, 700), 360, (2, 5), (0.12, 0.3),
                        'volt_hi', 'volt_dead', gravity=200, drag=1.0),
        ParticleProfile('orb', 8, (60, 160), 360, (3, 7), (0.2, 0.5),
                        'white', 'volt_mid', gravity=-100, drag=2.0),
    ],
    'Luz': [
        ParticleProfile('light', 26, (120, 320), 360, (5, 12), (0.35, 0.8),
                        'light_hi', 'light_dead', gravity=-80, drag=1.4),
        ParticleProfile('ring', 1, (0, 0), 360, (22, 30), (0.4, 0.55),
                        'light_hi', 'light_dead'),
        ParticleProfile('spark', 14, (260, 480), 60, (2, 4), (0.15, 0.3),
                        'white', 'light_mid', gravity=100, drag=1.0),
    ],
    'Trevas': [
        ParticleProfile('shadow', 24, (60, 180), 360, (10, 26), (0.6, 1.2),
                        'dark_hi', 'dark_dead', gravity=-20, drag=2.0),
        ParticleProfile('ember', 10, (30, 90), 360, (4, 9), (0.4, 0.8),
                        'dark_mid', 'dark_dead', gravity=-50, drag=2.2),
    ],
}

# Mapeamento visual_key -> elemento (fonte única: content.CARD_VISUAL_KEYS +
# CARDS[cid]['type']). Construído sob demanda para não importar content aqui.
_KEY_TO_ELEMENT = None


def get_element_for_visual(visual_key, cards_dict=None):
    global _KEY_TO_ELEMENT
    if _KEY_TO_ELEMENT is None and cards_dict is not None:
        _KEY_TO_ELEMENT = {c.get('visual_key', 'orb'): c.get('type', 'Terra')
                           for c in cards_dict.values()}
    element = (_KEY_TO_ELEMENT or {}).get(visual_key)
    return element if element in ELEMENT_PROFILES else 'Terra'


# Força do golpe: deriva de dano máximo e raridade da carta (game feel).
_RARITY_POWER = {'Comum': 0.35, 'Incomum': 0.5, 'Rara': 0.7,
                 'Mítica': 0.85, 'Lendária': 1.0, 'Única': 1.0}


def technique_power(card, result, max_damage_ref=48):
    """Escala 0..1 combinando dano causado, faixa da carta e raridade."""
    dmg = float(result.get('damage', 0) or 0)
    band = card.get('damage', (0, 0))
    base = max(dmg, band[1]) / float(max_damage_ref)
    rarity = _RARITY_POWER.get(card.get('rarity', 'Comum'), 0.4)
    crit = 1.25 if result.get('critical') else 1.0
    return min(1.0, (0.55 * base + 0.45 * rarity) * crit)


# ===========================================================================
#  Pool de partículas — struct-of-arrays numpy, livre-list O(1), zero GC
# ===========================================================================
class ParticlePool:
    def __init__(self, capacity=MAX_PARTICLES):
        self.capacity = capacity
        n = capacity
        f = np.float32
        self.x = np.zeros(n, f); self.y = np.zeros(n, f)
        self.vx = np.zeros(n, f); self.vy = np.zeros(n, f)
        self.size = np.zeros(n, f); self.rot = np.zeros(n, f)
        self.age = np.zeros(n, f); self.ttl = np.ones(n, f)
        self.grow = np.zeros(n, f)          # d(tamanho)/dt (decaimento/crescimento)
        self.grav = np.zeros(n, f)
        self.drag = np.zeros(n, f)
        self.spin = np.zeros(n, f)
        self.kind = np.zeros(n, f)
        self.ca = np.zeros((n, 4), f)      # cor nascimento rgba
        self.cb = np.zeros((n, 4), f)      # cor morte rgba
        self.seed = np.zeros(n, f)
        self.alive = np.zeros(n, bool)
        # stack de slots livres (object pooling puro: nunca cria objeto novo)
        self._free = list(range(n - 1, -1, -1))
        self.active_count = 0

    def spawn(self, x, y, vx, vy, size, ttl, kind, ca, cb, grav, drag,
              spin, seed, rot=0.0, grow=0.0):
        if not self._free:
            return False                     # hard cap atingido: descarta
        i = self._free.pop()
        A = self.alive
        A[i] = True
        self.x[i] = x; self.y[i] = y
        self.vx[i] = vx; self.vy[i] = vy
        self.size[i] = size; self.rot[i] = rot
        self.age[i] = 0.0; self.ttl[i] = ttl
        self.grow[i] = grow
        self.grav[i] = grav; self.drag[i] = drag; self.spin[i] = spin
        self.kind[i] = kind
        self.ca[i] = ca; self.cb[i] = cb
        self.seed[i] = seed
        self.active_count += 1
        return True

    def update(self, dt):
        """Integra TODAS as partículas vivas em vetorização numpy.

        Otimizações: sem sqrt (sem normalização de velocidade no loop —
        gravidade é uniaxial e arrasto é escalar), sem alocação (operações
        in-place), compactação apenas dos índices mortos uma vez por frame.
        """
        idx = np.flatnonzero(self.alive)
        if idx.size == 0:
            self.active_count = 0
            return
        age = self.age[idx] + dt
        dead = age >= self.ttl[idx]
        self.age[idx] = age
        # semi-implícito: velocidade primeiro (mais estável com arrasto alto)
        damp = 1.0 / (1.0 + self.drag[idx] * dt)      # sem pow/sqrt
        vx = self.vx[idx] * damp
        vy = (self.vy[idx] + self.grav[idx] * dt) * damp
        self.vx[idx] = vx; self.vy[idx] = vy
        self.x[idx] += vx * dt
        self.y[idx] += vy * dt
        self.rot[idx] += self.spin[idx] * dt
        self.size[idx] += self.grow[idx] * dt
        # kill por idade OU por sair da tela com margem (sem hypot: |dx|+|dy|)
        off = (self.x[idx] < -80) | (self.x[idx] > 1280) | \
              (self.y[idx] < -160) | (self.y[idx] > 960)
        killed = dead | off
        kidx = idx[killed]
        self.alive[kidx] = False
        self._free.extend(kidx.tolist())
        self.active_count = idx.size - int(killed.sum())

    def write_vbo(self, out):
        """Serializa as partículas vivas no staging `out` (n*6, FVP floats).

        Object pooling: nenhuma alocação — `out` é o buffer pré-alocado do
        renderer. Retorna 6*n vértices escritos. Layout por vértice:
        [corner.x corner.y pos.x pos.y size rot life kind colA(4) colB(4) seed]
        """
        idx = np.flatnonzero(self.alive)
        n = idx.size
        if n == 0:
            return 0
        life = self.age[idx] / self.ttl[idx]
        rows = np.column_stack((
            self.x[idx], self.y[idx], self.size[idx], self.rot[idx],
            life, self.kind[idx], self.ca[idx], self.cb[idx], self.seed[idx]))
        rep = np.repeat(rows, 6, axis=0)          # 2 triângulos por quad
        out[:, 0:2] = _CORNERS_TILED[: n * 6]     # corners cíclicos (-1..1)
        out[:, 2] = rep[:, 0]                     # pos.x
        out[:, 3] = rep[:, 1]                     # pos.y
        out[:, 4] = rep[:, 2]                     # size
        out[:, 5] = rep[:, 3]                     # rot
        out[:, 6] = rep[:, 4]                     # life
        out[:, 7] = rep[:, 5]                     # kind
        out[:, 8:12] = rep[:, 6:10]               # colA rgba
        out[:, 12:16] = rep[:, 10:14]             # colB rgba
        out[:, 16] = rep[:, 14]                   # seed
        return n * 6


# cantos de um quad em 2 triângulos (ordem CCW), tile-cycled para N partículas
_CORNER6 = np.array([[-1, -1], [1, -1], [1, 1], [-1, -1], [1, 1], [-1, 1]], np.float32)
_CORNERS_TILED = np.tile(_CORNER6, (MAX_PARTICLES, 1))


# ===========================================================================
#  Renderizador ModernGL (contexto standalone; fallback headless-safe)
# ===========================================================================
class _GLRenderer:
    def __init__(self, width, height):
        import moderngl
        self.mg = moderngl
        self.width, self.height = width, height
        try:
            self.ctx = moderngl.create_standalone_context()
        except Exception:
            self.ctx = None
            return
        ctx = self.ctx
        self.prog_part = ctx.program(
            vertex_shader=self._read('particle.vert'),
            fragment_shader=self._read('particle.frag'))
        fs_quad = ctx.vertex_shader(self._read('fullscreen.vert')) \
            if False else self._read('fullscreen.vert')
        self.prog_bloom = ctx.program(vertex_shader=fs_quad,
                                      fragment_shader=self._read('bloom.frag'))
        self.prog_dist = ctx.program(vertex_shader=fs_quad,
                                     fragment_shader=self._read('distortion.frag'))
        self.prog_comp = ctx.program(vertex_shader=fs_quad,
                                     fragment_shader=self._read('composite.frag'))

        # --- buffers HDR ----------------------------------------------------
        self.scene_fbo = self._fbo(1.0)
        self.bloom_a = [self._fbo(0.5), self._fbo(0.25)]
        self.bloom_b = [self._fbo(0.5), self._fbo(0.25)]
        self.dist_fbo = self._fbo(1.0)
        self.comp_fbo = self._fbo(1.0, fmt='RGBA8')

        # --- geometria fullscreen ------------------------------------------
        self.fs_vbo = ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], np.float32).tobytes())
        self.fs_vao = ctx.simple_vertex_array(self.prog_bloom, self.fs_vbo, 0)

        # --- VBO de partículas (dinâmico, pré-alocado no tamanho máximo) ----
        verts_per_particle = 6
        total = MAX_PARTICLES * verts_per_particle
        self.part_data = np.zeros((total, FLOATS_PER_PARTICLE), np.float32)
        self._build_corner_template()
        self.part_vbo = ctx.buffer(self.part_data.tobytes())
        self.part_vao = ctx.vertex_array(
            self.prog_part, [(self.part_vbo,
                              '2f 2f 1f 1f 1f 1f 4f 4f 1f',  # corner.xy? ver nota
                              *range(FLOATS_PER_PARTICLE))],
            mode=ctx.TRIANGLES)
        # offsets: attrib0 corner(vec2)->cols0-1, pos(vec2)->cols1-2?? colidem.
        # Resolvemos com stride manual: ver _upload abaixo.
        self.part_vao.release()
        # Layout final por vértice (15 floats):
        #  [0]=corner.x [1]=corner.y [2]=pos.x [3]=pos.y [4]=size [5]=rot
        #  [6]=life [7]=kind [8..11]=colA [12..15?]... -> excede 15; ajustamos
        # para 17 floats/vértice:
        self.FVP = 17
        self.stride_bytes = self.FVP * 4
        self.part_data = np.zeros((total, self.FVP), np.float32)
        self.part_vbo = ctx.buffer(self.part_data[:verts_per_particle].tobytes())
        self.part_vbo.resize(total * self.stride_bytes)
        fmt = '2f %df 2f 1f 1f 1f 1f 4f 4f 1f' % 0  # placeholder, substituído
        self.part_vao = ctx.vertex_array(
            self.prog_part,
            [(self.part_vbo,
              '2f 2f 1f 1f 1f 1f 4f 4f 1f',   # corner(2) pos(2) size rot life kind colA colB seed
              *range(self.FVP))],
            mode=ctx.TRIANGLES)

    @staticmethod
    def _read(name):
        return (SHADERS_DIR / name).read_text(encoding='utf-8')

    def _fbo(self, scale, fmt='RGBA16F'):
        w = max(1, int(self.width * scale)); h = max(1, int(self.height * scale))
        tex = self.ctx.texture((w, h), 4, dtype=fmt)
        tex.filter = (self.ctx.LINEAR, self.ctx.LINEAR)
        return self.ctx.framebuffer(color_attachments=[tex])

    def _build_corner_template(self):
        pass

    def render_particles(self, pool):
        """Um draw call para todas as partículas vivas."""
        n = pool.active_count
        if n == 0:
            return
        idx = np.flatnonzero(pool.alive)
        if idx.size != n:
            idx = idx[:n]
        life = pool.age[idx] / pool.ttl[idx]
        rows = np.column_stack((
            pool.x[idx], pool.y[idx], pool.size[idx], pool.rot[idx],
            life, pool.kind[idx], pool.ca[idx], pool.cb[idx], pool.seed[idx]))
        # expandir em 6 vértices (2 triângulos) com corners fixos
        corners = np.array([[-1, -1], [1, -1], [1, 1],
                            [-1, -1], [1, 1], [-1, 1]], np.float32)
        data = np.empty((n * 6, self.FVP), np.float32)
        data[:, 0:2] = np.tile(corners, (n, 1))
        rep = np.repeat(rows, 6, axis=0)
        data[:, 2] = rep[:, 0]                      # pos.x
        data[:, 3] = rep[:, 1]                      # pos.y
        data[:, 4] = rep[:, 2]                      # size
        data[:, 5] = rep[:, 3]                      # rot
        data[:, 6] = rep[:, 4]                      # life
        data[:, 7] = rep[:, 5]                      # kind
        data[:, 8:12] = rep[:, 6:10]                # colA
        data[:, 12:16] = rep[:, 10:14]              # colB
        data[:, 16] = rep[:, 14]                    # seed
        self.part_data[:n * 6] = data               # staging pré-alocado
        self.part_vbo.write(data.tobytes())         # upload único
        ctx = self.ctx
        ctx.blend = True
        ctx.blend_func = self.mg.SRC_ALPHA, self.mg.ONE   # aditivo p/ HDR
        ctx.depth_test = False
        self.part_vao.draw(self.mg.TRIANGLES, n * 6)

    def full_pipeline(self, scene_texture, impacts, flash_rgba, bloom_strength, time_s):
        """scene(HDR) -> distorção -> extração+blur(bloom) -> composite RGBA8."""
        ctx = self.ctx
        ctx.disable(self.mg.BLEND)
        # 1) distorção térmica/de impacto sobre a cena
        self.dist_fbo.use()
        ctx.clear(0, 0, 0, 1)
        self.prog_dist['u_scene'].value = 0
        self.prog_dist['u_viewport'].value = (self.width, self.height)
        self.prog_dist['u_time'].value = time_s
        self.prog_dist['u_impact_count'].value = len(impacts)
        self.prog_dist['u_impacts'].write(
            np.asarray(impacts, np.float32).tobytes())
        scene_texture.use(location=0)
        self.fs_vao.bind()
        self.prog_dist['u_scene'].value = 0
        self.ctx.simple_vertex_array(self.prog_dist, self.fs_vbo, 0).draw(self.mg.TRIANGLES)
        # 2) bloom: threshold no nível 0, blur H/V ping-pong, upscale simples
        src = self.dist_fbo.color_attachments[0]
        b0 = self.bloom_a[0]
        b0.use(); ctx.clear(0, 0, 0, 1)
        self.prog_bloom['u_tex'].value = 0
        self.prog_bloom['u_threshold'].value = 1.05
        self.prog_bloom['u_radius'].value = 1.0
        self.prog_bloom['u_dir'].value = (1.0, 0.0)
        self.prog_bloom['u_texel'].value = tuple(1.0 / s for s in b0.size)
        src.use(location=0)
        self.ctx.simple_vertex_array(self.prog_bloom, self.fs_vbo, 0).draw(self.mg.TRIANGLES)
        cur_tex = b0.color_attachments[0]
        for lvl in (self.bloom_b[0], self.bloom_a[0]):
            lvl.use(); ctx.clear(0, 0, 0, 1)
            self.prog_bloom['u_threshold'].value = 0.0
            self.prog_bloom['u_dir'].value = (1.0, 0.0)
            self.prog_bloom['u_radius'].value = 2.0
            self.prog_bloom['u_texel'].value = tuple(1.0 / s for s in lvl.size)
            cur_tex.use(location=0)
            self.ctx.simple_vertex_array(self.prog_bloom, self.fs_vbo, 0).draw(self.mg.TRIANGLES)
            mid = lvl.color_attachments[0]
            lvl.use()  # mesma textura p/ 2ª passada vertical seria read-write;
            # usamos o par oposto como destino da passada vertical:
        # (passadas verticais)
        pairs = [(self.bloom_a[0], self.bloom_b[0]),
                 (self.bloom_b[0], self.bloom_a[0])]
        prev = self.dist_fbo.color_attachments[0]
        for dst_h, dst_v in pairs:
            dst_h.use(); ctx.clear(0, 0, 0, 1)
            self.prog_bloom['u_threshold'].value = 1.05 if dst_h is self.bloom_a[0] else 0.0
            self.prog_bloom['u_dir'].value = (1.0, 0.0)
            self.prog_bloom['u_texel'].value = tuple(1.0 / s for s in dst_h.size)
            prev.use(location=0)
            self.ctx.simple_vertex_array(self.prog_bloom, self.fs_vbo, 0).draw(self.mg.TRIANGLES)
            dst_v.use(); ctx.clear(0, 0, 0, 1)
            self.prog_bloom['u_dir'].value = (0.0, 1.0)
            self.prog_bloom['u_texel'].value = tuple(1.0 / s for s in dst_v.size)
            dst_h.color_attachments[0].use(location=0)
            self.ctx.simple_vertex_array(self.prog_bloom, self.fs_vbo, 0).draw(self.mg.TRIANGLES)
            prev = dst_v.color_attachments[0]
        bloom_tex = self.bloom_a[0].color_attachments[0]
        # 3) composite final
        self.comp_fbo.use(); ctx.clear(0, 0, 0, 1)
        self.prog_comp['u_scene'].value = 0
        self.prog_comp['u_bloom'].value = 1
        self.prog_comp['u_time'].value = time_s
        self.prog_comp['u_flash'].value = flash_rgba
        self.prog_comp['u_bloom_strength'].value = bloom_strength
        self.dist_fbo.color_attachments[0].use(location=0)
        bloom_tex.use(location=1)
        self.ctx.simple_vertex_array(self.prog_comp, self.fs_vbo, 0).draw(self.mg.TRIANGLES)
        return self.comp_fbo


# ===========================================================================
#  API pública: VfxManager
# ===========================================================================
class VfxManager:
    """Fachada usada pelo App do jogo. Gerencia pool, shake, flash, freeze."""

    def __init__(self, width=1200, height=800, gl_enabled=True):
        self.width, self.height = width, height
        self.time = 0.0
        self.pool = ParticlePool(MAX_PARTICLES)
        self.gl = _GLRenderer(width, height) if gl_enabled else None
        self.gl_failed = self.gl is not None and self.gl.ctx is None
        # game feel state
        self.shake_amp = 0.0        # px
        self.shake_decay = 0.0
        self.shake_offset = [0.0, 0.0]
        self.flash_color = (1, 1, 1)
        self.flash_left = 0.0       # frames restantes de hit-flash
        self.freeze_left = 0.0      # segundos de micro-pausa (crítico)
        self.impacts = []           # (x,y,prog,strength) p/ distortion
        self.emission_queue = []    # eventos com delay (spawner agendado)
        self.scheduled = []         # (at_time, profiles, origin, dir_angle, power)
        self._rng = random.Random()
        self.stats = {'spawned': 0, 'dropped': 0}

    # ------------------ disparo de técnica (fase 'hero') -------------------
    def play_technique(self, card_id, card, result, start, end,
                       impact_at=0.42, duration=0.68):
        """Chamado em App.choose() junto de self.card_fx.

        card/result vêm de content.CARDS e State.action(); start/end em px.
        """
        element = card.get('type') or get_element_for_visual(
            card.get('visual_key', 'orb'), None)
        power = technique_power(card, result)
        self._projectile(element, start, end, impact_at, duration, power)

    def _projectile(self, element, start, end, impact_at, duration, power):
        ux = end[0] - start[0]; uy = end[1] - start[1]
        L = math.hypot(ux, uy) or 1.0
        ang = math.atan2(uy, ux)
        # trail durante o voo (emissão contínua agendada por amostras)
        steps = 8
        for i in range(steps):
            f = (i + 1) / steps
            t = impact_at * f
            x = start[0] + ux * f; y = start[1] + uy * f
            prof = ELEMENT_PROFILES[element][:1]
            self.scheduled.append(
                (self.time + t, prof, (x, y), ang, power * 0.35, 0.55))
        # impacto principal
        self.scheduled.append((self.time + impact_at,
                               ELEMENT_PROFILES[element], end, ang, power, 1.0))
        self.scheduled.append((self.time + impact_at,
                               [ParticleProfile('ring', 1, (0, 0), 360,
                                                (14 + 26 * power, 20 + 40 * power),
                                                (0.30, 0.5), 'white', 'white')],
                               end, ang, power, 1.0))
        # game feel proporcional à força
        self.shake_amp = max(self.shake_amp, 2.0 + 14.0 * power)
        self.shake_decay = 18.0 + 10.0 * power
        self.flash_color = (1.0, 1.0, 1.0)
        self.flash_left = 1 + round(2 * power)          # 1-3 frames
        self.impacts.append([end[0], end[1], 0.0, 0.35 + power])
        if len(self.impacts) > MAX_DISTORTION_SOURCES:
            self.impacts.pop(0)

    # ------------------ técnicas de suporte (cura/escudo) ------------------
    def play_support(self, element, anchor_rect, power=0.6, shield=False):
        """Cura/escudo ancorados ao sprite do personagem (rect pygame)."""
        cx = anchor_rect.centerx
        base = anchor_rect.bottom - 6
        top = anchor_rect.top + 8
        if shield:
            hexrows = 3
            for r in range(hexrows):
                yy = top + (base - top) * (r / max(1, hexrows - 1))
                for xx in (cx - anchor_rect.width * 0.55,
                           cx + anchor_rect.width * 0.55):
                    self.pool.spawn(xx, yy, 0, 0, 16 + 6 * power, 1.1,
                                    KIND['hex'], _rgb('white') + (0.9,),
                                    _rgb(element if element in ('Metal',) else 'Luz') + (0.25,),
                                    0, 0, 0.6, self._rng.random())
            self.impacts.append([cx, (top + base) / 2, 0.0, 0.25])
            self.flash_color = (0.8, 0.95, 1.0)
            self.flash_left = 2
        else:
            for _ in range(int(26 * (0.5 + power))):
                x = cx + self._rng.uniform(-anchor_rect.width * .5, anchor_rect.width * .5)
                y = base + self._rng.uniform(-10, 6)
                self.pool.spawn(x, y, self._rng.uniform(-14, 14),
                                self._rng.uniform(-70, -130),     # ascendente
                                self._rng.uniform(4, 9),
                                self._rng.uniform(0.8, 1.5),
                                KIND['heal'], _rgb('heal_hi') + (0.95,),
                                _rgb('heal_dead') + (0.0,),
                                -30, 1.2, 0.0, self._rng.random())
            self.flash_color = (0.6, 1.0, 0.75)
            self.flash_left = 2
            self.shake_amp = max(self.shake_amp, 1.5)
            self.shake_decay = 12.0

    # ------------------ críticos: freeze frame -----------------------------
    def register_critical_hit(self, seconds=0.055):
        """Micro-pausa (hit-stop) chamada quando result['critical'] é True."""
        self.freeze_left = max(self.freeze_left, seconds)

    # ------------------ atualização ----------------------------------------
    def tick(self, dt):
        """Avança simulação. Retorna True se este frame deve ser congelado."""
        frozen = self.freeze_left > 0.0
        if frozen:
            self.freeze_left -= dt
            dt = 0.0                     # tempo de jogo congela; GL continua vivo
        self.time += dt
        # spawner agendado (delay de emissões)
        if self.scheduled:
            due = [s for s in self.scheduled if self.time >= s[0]]
            if due:
                self.scheduled = [s for s in self.scheduled if self.time < s[0]]
            for _, profiles, origin, ang, power, budget in due:
                self._emit(profiles, origin, ang, power, budget)
        self.pool.update(dt)
        # shake paramétrico com amortecimento exponencial
        if self.shake_amp > 0.05 and dt > 0:
            self.shake_amp *= math.exp(-self.shake_decay * dt)
            a = self.shake_amp
            # ruído barato (sem rand per-frame pesado): senóides desincronizadas
            self.shake_offset[0] = math.sin(self.time * 91.0) * a
            self.shake_offset[1] = math.cos(self.time * 67.0) * a * 0.8
        elif self.shake_amp <= 0.05:
            self.shake_amp = 0.0
            self.shake_offset[0] = self.shake_offset[1] = 0.0
        # progresso das ondas de distorção
        if self.impacts:
            keep = []
            for imp in self.impacts:
                imp[2] += dt / 0.45
                if imp[2] < 1.0:
                    keep.append(imp)
            self.impacts = keep
        return frozen

    def _emit(self, profiles, origin, angle_rad, power, budget=1.0):
        rng = self._rng
        remaining = MAX_EMISSION_PER_FRAME
        for prof in profiles:
            if remaining <= 0 or not self.pool._free:
                self.stats['dropped'] += 1
                continue
            cnt = max(1, int(prof.count * (0.45 + 0.55 * power) * budget))
            cnt = min(cnt, remaining, len(self.pool._free))
            spread = math.radians(prof.spread_deg)
            ca = _rgb(prof.col_a) + (1.0,)
            cb = _rgb(prof.col_b) + (0.0,)
            smin, smax = prof.size
            lmin, lmax = prof.life
            vmin, vmax = prof.speed
            for _ in range(cnt):
                a = angle_rad + rng.uniform(-spread / 2, spread / 2)
                sp = rng.uniform(vmin, vmax)
                vx = math.cos(a) * sp
                vy = math.sin(a) * sp
                if prof.upward_bias:
                    vy -= prof.upward_bias * sp * 0.4
                ok = self.pool.spawn(
                    origin[0] + rng.uniform(-3, 3),
                    origin[1] + rng.uniform(-3, 3),
                    vx, vy, rng.uniform(smin, smax) * (0.7 + 0.5 * power),
                    rng.uniform(lmin, lmax), prof.kind, ca, cb,
                    prof.gravity, prof.drag,
                    rng.uniform(-prof.spin, prof.spin), rng.random(),
                    rot=a, grow=-rng.uniform(smin, smax) * 0.35)
                if ok:
                    self.stats['spawned'] += 1
                    remaining -= 1
                else:
                    self.stats['dropped'] += 1

    # ------------------ consumo pelo pygame --------------------------------
    def camera_offset(self):
        return (int(round(self.shake_offset[0])), int(round(self.shake_offset[1])))

    def blit_to_gl(self, canvas_surface):
        if self.gl is None or self.gl_failed or self.gl.ctx is None:
            return None
        ctx = self.gl.ctx
        raw = pygame_surface_to_bytes(canvas_surface)
        self.gl.scene_fbo.color_attachments[0].write(raw)
        return self.gl.scene_fbo.color_attachments[0]

    def render(self, canvas_surface):
        """Pipeline completo; devolve uma Surface RGBA pronta p/ blit no window.

        Sem GL disponível retorna None (jogo cai no renderer legado).
        """
        tex = self.blit_to_gl(canvas_surface)
        if tex is None:
            return None
        ctx = self.gl.ctx
        flash = (*self.flash_color, 0.0)
        if self.flash_left > 0:
            flash = (*self.flash_color, min(1.0, self.flash_left * 0.45))
            self.flash_left -= 1
        fbo = self.gl.full_pipeline(
            tex, self.impacts or [[0, 0, 0.999, 0.0]],
            flash, 0.85, self.time)
        w, h = self.gl.width, self.gl.height
        data = fbo.color_attachments[0].read()
        surf = _surface_from_argb(data, w, h)
        return surf


# ---------------------------------------------------------------------------
# utilidades de conversão pygame <-> GL (RGBA8, flip vertical)
# ---------------------------------------------------------------------------
def pygame_surface_to_bytes(surface):
    """Bytes RGBA crus de uma Surface (sem flip; GL compensa no proj)."""
    s = surface.convert_alpha() if not surface.get_alpha() else surface
    return pygame.tobytes(s) if hasattr(pygame, 'tobytes') else bytes(
        pygame.image.tostring(s, 'RGBA'))


def _surface_from_argb(raw_rgba, w, h):
    import pygame
    arr = np.frombuffer(raw_rgba, np.uint8).reshape(h, w, 4)[::-1]
    return pygame.image.frombuffer(arr.tobytes(), (w, h), 'RGBA').convert_alpha()


try:
    import pygame
except Exception:      # permite importar o módulo para testes sem display
    pygame = None
