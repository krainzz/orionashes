"""GPU-driven combat rendering effects for Cinzas de Órion.

This module is deliberately visual-only. It never receives or mutates combat state,
attributes, damage, mana, turns, or save data. If ModernGL / a compatible GL 3.3
context is unavailable, ``apply`` returns the original Pygame surface unchanged.

Configuration lives in ``FX_PRESETS``; tune duration, color, light intensity,
particle count, radius, and critical shockwave behavior there or use ``configure``.
"""
from __future__ import annotations

import math
import os
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHADER_DIR = ROOT / "assets" / "shaders"

# Values are intentionally easy to edit. Colors use familiar 0-255 RGB values.
FX_PRESETS = {
    "physical": {"duration": 0.72, "color": (116, 222, 244), "intensity": 0.62, "light_radius": 210.0, "particles": 28, "shockwave": False, "shock_intensity": 0.0},
    "fire":     {"duration": 0.95, "color": (255, 92, 38),  "intensity": 1.05, "light_radius": 270.0, "particles": 72, "shockwave": False, "shock_intensity": 0.0},
    "water":    {"duration": 0.86, "color": (65, 190, 235),  "intensity": 0.78, "light_radius": 245.0, "particles": 54, "shockwave": False, "shock_intensity": 0.0},
    "plant":    {"duration": 0.95, "color": (102, 222, 112), "intensity": 0.78, "light_radius": 240.0, "particles": 58, "shockwave": False, "shock_intensity": 0.0},
    "earth":    {"duration": 0.78, "color": (200, 164, 112), "intensity": 0.70, "light_radius": 220.0, "particles": 42, "shockwave": False, "shock_intensity": 0.0},
    "metal":    {"duration": 0.72, "color": (185, 207, 220), "intensity": 0.73, "light_radius": 225.0, "particles": 40, "shockwave": False, "shock_intensity": 0.0},
    "electric": {"duration": 0.66, "color": (110, 226, 255), "intensity": 1.10, "light_radius": 275.0, "particles": 64, "shockwave": False, "shock_intensity": 0.0},
    "light":    {"duration": 0.92, "color": (255, 247, 180), "intensity": 1.00, "light_radius": 280.0, "particles": 58, "shockwave": False, "shock_intensity": 0.0},
    "dark":     {"duration": 0.88, "color": (170, 111, 235), "intensity": 0.82, "light_radius": 250.0, "particles": 56, "shockwave": False, "shock_intensity": 0.0},
    "shield":   {"duration": 0.78, "color": (80, 222, 245),  "intensity": 0.95, "light_radius": 205.0, "particles": 72, "shockwave": False, "shock_intensity": 0.0},
    "heal":     {"duration": 1.08, "color": (120, 255, 174), "intensity": 0.85, "light_radius": 230.0, "particles": 76, "shockwave": False, "shock_intensity": 0.0},
}

ELEMENT_PRESETS = {
    "Fogo": "fire", "Água": "water", "Planta": "plant", "Terra": "earth",
    "Metal": "metal", "Elétrico": "electric", "Luz": "light", "Trevas": "dark",
}

# Critical/supreme impact overrides. The base preset settings remain editable.
CRITICAL_SHOCKWAVE = {"duration": 0.48, "intensity": 0.85, "chromatic": 1.8}
SUPREME_SHOCKWAVE = {"duration": 0.62, "intensity": 1.2, "chromatic": 2.5}
MAX_GPU_PARTICLES = 160
MAX_POINT_LIGHTS = 8


class CombatFXRenderer:
    """ModernGL post-process + instanced GPU particles for the 1200x800 canvas."""

    def __init__(self, size=(1200, 800), enabled=True):
        self.width, self.height = map(int, size)
        self.enabled = bool(enabled)
        self.available = False
        self.error = None
        self.events = []
        self.presets = {name: dict(values) for name, values in FX_PRESETS.items()}
        self._ctx = None
        self._moderngl = None
        self._scene_texture = None
        self._output_texture = None
        self._framebuffer = None
        self._composite_program = None
        self._particle_program = None
        self._composite_vao = None
        self._particle_vao = None
        if self.enabled:
            self._initialize_gpu()

    def configure(self, preset, **values):
        """Override preset fields at runtime; changes affect future triggers only."""
        if preset not in self.presets:
            raise KeyError(f"Preset de efeito desconhecido: {preset}")
        allowed = {"duration", "color", "intensity", "light_radius", "particles", "shockwave", "shock_intensity"}
        unknown = set(values) - allowed
        if unknown:
            raise ValueError(f"Configuração não suportada: {', '.join(sorted(unknown))}")
        merged = dict(self.presets[preset])
        merged.update(values)
        if "duration" in merged and float(merged["duration"]) <= 0:
            raise ValueError("duration deve ser maior que zero")
        if "particles" in merged:
            merged["particles"] = max(0, min(MAX_GPU_PARTICLES, int(merged["particles"])))
        if "color" in merged:
            color = tuple(int(max(0, min(255, c))) for c in merged["color"])
            if len(color) != 3:
                raise ValueError("color deve ser RGB, por exemplo (255, 120, 60)")
            merged["color"] = color
        self.presets[preset] = merged

    def trigger(self, preset="physical", start=(480, 360), end=(720, 350), *, critical=False, supreme=False, duration=None, color=None, intensity=None):
        """Start a purely visual burst. Coordinates are in the 1200x800 canvas."""
        preset = preset if preset in self.presets else "physical"
        cfg = dict(self.presets[preset])
        if duration is not None:
            cfg["duration"] = max(0.05, float(duration))
        if color is not None:
            cfg["color"] = tuple(int(max(0, min(255, c))) for c in color[:3])
        if intensity is not None:
            cfg["intensity"] = max(0.0, float(intensity))
        shock = None
        if supreme:
            shock = dict(SUPREME_SHOCKWAVE)
        elif critical:
            shock = dict(CRITICAL_SHOCKWAVE)
        elif cfg.get("shockwave"):
            shock = {"duration": cfg["duration"] * 0.7, "intensity": float(cfg.get("shock_intensity", 0.6)), "chromatic": 1.0}
        event = {
            "preset": preset, "start": tuple(map(float, start)), "end": tuple(map(float, end)),
            "age": 0.0, "duration": float(cfg["duration"]), "color": tuple(cfg["color"]),
            "intensity": float(cfg["intensity"]), "light_radius": float(cfg["light_radius"]),
            "particles": max(0, min(MAX_GPU_PARTICLES, int(cfg["particles"]))), "shock": shock,
        }
        self.events.append(event)
        # Avoid a burst backlog when attacks are triggered in rapid succession.
        self.events = self.events[-MAX_POINT_LIGHTS:]
        return event

    def clear(self):
        self.events.clear()

    def update(self, dt):
        dt = max(0.0, float(dt))
        for event in self.events:
            event["age"] += dt
        self.events = [e for e in self.events if e["age"] < max(e["duration"], (e["shock"] or {}).get("duration", 0.0))]

    def apply(self, surface):
        """Return a processed Pygame Surface; return the original on any GPU error."""
        if not self.available or not self.events:
            return surface
        try:
            return self._render(surface)
        except Exception as exc:  # Keep the battle playable if a driver/context fails.
            self.error = f"Falha no renderizador GPU: {exc}"
            self.available = False
            self._release_gpu()
            return surface

    def _initialize_gpu(self):
        try:
            import moderngl
            self._moderngl = moderngl
            # Standalone/off-screen context deliberately avoids changing Pygame's
            # existing software-rendered display surface or its established layout.
            try:
                self._ctx = moderngl.create_standalone_context(require=330)
            except Exception as first_error:
                # EGL is often available on Linux/CI systems without an X11 window.
                try:
                    self._ctx = moderngl.create_standalone_context(require=330, backend="egl")
                except Exception:
                    raise first_error
            self._composite_program = self._ctx.program(
                vertex_shader=(SHADER_DIR / "combat_post.vert.glsl").read_text(encoding="utf-8"),
                fragment_shader=(SHADER_DIR / "combat_post.frag.glsl").read_text(encoding="utf-8"),
            )
            self._particle_program = self._ctx.program(
                vertex_shader=(SHADER_DIR / "combat_particles.vert.glsl").read_text(encoding="utf-8"),
                fragment_shader=(SHADER_DIR / "combat_particles.frag.glsl").read_text(encoding="utf-8"),
            )
            # Vertex shaders use gl_VertexID/gl_InstanceID; no input VBO is needed.
            self._composite_vao = self._ctx.vertex_array(self._composite_program, [])
            self._particle_vao = self._ctx.vertex_array(self._particle_program, [])
            self._create_targets()
            self.available = True
        except Exception as exc:
            self.error = f"ModernGL indisponível: {exc}"
            self.available = False
            self._release_gpu()

    def _create_targets(self):
        if self._scene_texture is not None:
            self._scene_texture.release()
        if self._output_texture is not None:
            self._output_texture.release()
        if self._framebuffer is not None:
            self._framebuffer.release()
        self._scene_texture = self._ctx.texture((self.width, self.height), 4, dtype="f1")
        self._scene_texture.filter = (self._moderngl.NEAREST, self._moderngl.NEAREST)
        self._scene_texture.repeat_x = False
        self._scene_texture.repeat_y = False
        self._output_texture = self._ctx.texture((self.width, self.height), 4, dtype="f1")
        self._output_texture.filter = (self._moderngl.NEAREST, self._moderngl.NEAREST)
        self._framebuffer = self._ctx.framebuffer(color_attachments=[self._output_texture])

    def _render(self, surface):
        import pygame
        width, height = surface.get_size()
        if (width, height) != (self.width, self.height):
            self.width, self.height = width, height
            self._create_targets()
        # OpenGL texture data is bottom-up. Pygame's ``flipped=True`` bridges that.
        self._scene_texture.write(pygame.image.tostring(surface, "RGBA", True), alignment=1)
        ctx, mgl = self._ctx, self._moderngl
        self._framebuffer.use()
        ctx.viewport = (0, 0, self.width, self.height)
        ctx.disable(mgl.BLEND)
        p = self._composite_program
        p["u_scene"].value = 0
        self._scene_texture.use(location=0)
        p["u_resolution"].value = (float(self.width), float(self.height))

        lights = []
        newest_shock = None
        for event in self.events:
            sx, sy = event["start"]
            ex, ey = event["end"]
            progress = min(1.0, max(0.0, event["age"] / 0.42))
            lx = sx + (ex - sx) * progress
            ly = sy + (ey - sy) * progress
            age_fade = max(0.0, 1.0 - event["age"] / max(event["duration"], 0.001))
            pulse = 0.82 + 0.18 * math.sin(event["age"] * 27.0)
            lights.append((lx, ly, event["light_radius"], event["intensity"] * age_fade * pulse, *(c / 255.0 for c in event["color"]), 1.0))
            shock = event.get("shock")
            if shock and event["age"] < shock["duration"] and (newest_shock is None or event["age"] < newest_shock["age"]):
                newest_shock = {**event, "shock": shock}
        lights = lights[-MAX_POINT_LIGHTS:]
        p["u_light_count"].value = len(lights)
        # Upload packed uniform arrays in one call each; all unused slots are zero.
        light_pos = []
        light_col = []
        for i in range(MAX_POINT_LIGHTS):
            if i < len(lights):
                light = lights[i]
                light_pos.extend(light[0:4])
                light_col.extend(light[4:8])
            else:
                light_pos.extend((0.0, 0.0, 1.0, 0.0))
                light_col.extend((0.0, 0.0, 0.0, 0.0))
        p["u_light_pos_radius"].write(struct.pack("32f", *light_pos))
        p["u_light_color"].write(struct.pack("32f", *light_col))
        if newest_shock is None:
            p["u_shock_enabled"].value = 0
            p["u_shock_origin"].value = (0.0, 0.0)
            p["u_shock_age"].value = 0.0
            p["u_shock_duration"].value = 1.0
            p["u_shock_intensity"].value = 0.0
            p["u_chromatic_intensity"].value = 0.0
        else:
            sx, sy = newest_shock["end"]
            shock = newest_shock["shock"]
            p["u_shock_enabled"].value = 1
            p["u_shock_origin"].value = (sx, sy)
            p["u_shock_age"].value = newest_shock["age"]
            p["u_shock_duration"].value = float(shock["duration"])
            p["u_shock_intensity"].value = float(shock["intensity"])
            p["u_chromatic_intensity"].value = float(shock["chromatic"])
        self._composite_vao.render(mode=mgl.TRIANGLES, vertices=3)

        # The particles are generated procedurally in the vertex shader and drawn
        # as instanced quads; no Python-side per-particle simulation is needed.
        ctx.enable(mgl.BLEND)
        ctx.blend_func = (mgl.SRC_ALPHA, mgl.ONE)
        q = self._particle_program
        q["u_resolution"].value = (float(self.width), float(self.height))
        preset_ids = {"fire": 0, "shield": 1, "heal": 2, "water": 3, "plant": 4, "earth": 5, "metal": 6, "electric": 7, "light": 8, "dark": 9, "physical": 10}
        for event in self.events:
            count = event["particles"]
            if count <= 0:
                continue
            q["u_origin"].value = event["end"]
            q["u_age"].value = event["age"]
            q["u_duration"].value = event["duration"]
            r, g, b = event["color"]
            q["u_color"].value = (r / 255.0, g / 255.0, b / 255.0, 1.0)
            q["u_intensity"].value = event["intensity"]
            q["u_preset"].value = preset_ids.get(event["preset"], 10)
            q["u_particle_count"].value = count
            self._particle_vao.render(mode=mgl.TRIANGLES, vertices=6, instances=count)
        ctx.disable(mgl.BLEND)
        raw = self._framebuffer.read(components=4, alignment=1)
        return pygame.image.fromstring(raw, (self.width, self.height), "RGBA", True).convert()

    def _release_gpu(self):
        for name in ("_composite_vao", "_particle_vao", "_composite_program", "_particle_program", "_framebuffer", "_scene_texture", "_output_texture"):
            obj = getattr(self, name, None)
            if obj is not None:
                try:
                    obj.release()
                except Exception:
                    pass
                setattr(self, name, None)
        if self._ctx is not None:
            try:
                self._ctx.release()
            except Exception:
                pass
            self._ctx = None

    def close(self):
        self._release_gpu()
        self.available = False
