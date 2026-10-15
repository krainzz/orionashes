# Pipeline ModernGL 3.3+ para HUD, Cartas TCG Neon 0.7.7, Cristal Direcional, Nave e Titulo
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHADER_DIR = ROOT / "assets" / "shaders"


class CombatHUDRenderer:
    def __init__(self, size=(1200, 800), enabled=True):
        self.width, self.height = map(int, size)
        self.enabled = bool(enabled)
        self.available = False
        self.error = None
        self._ctx = None
        self._mgl = None
        self._program = None
        self._vao = None
        self._hero_program = None
        self._hero_vao = None
        self._title_program = None
        self._title_vao = None
        self._ship_program = None
        self._ship_vao = None
        self._card_program = None
        self._card_vao = None
        self._card_cache = {}
        self._input = None
        self._output = None
        self._fbo = None
        if self.enabled:
            self._initialize()

    def _initialize(self):
        try:
            import moderngl
            self._mgl = moderngl
            try:
                self._ctx = moderngl.create_standalone_context(require=330)
            except Exception as first_error:
                try:
                    self._ctx = moderngl.create_standalone_context(require=330, backend="egl")
                except Exception:
                    raise first_error
            self._program = self._ctx.program(
                vertex_shader=(SHADER_DIR / "combat_hud.vert.glsl").read_text(encoding="utf-8"),
                fragment_shader=(SHADER_DIR / "combat_hud.frag.glsl").read_text(encoding="utf-8"),
            )
            self._vao = self._ctx.vertex_array(self._program, [])

            hero_vert = SHADER_DIR / "hero_crystal.vert.glsl"
            hero_frag = SHADER_DIR / "hero_crystal.frag.glsl"
            if hero_vert.exists() and hero_frag.exists():
                self._hero_program = self._ctx.program(
                    vertex_shader=hero_vert.read_text(encoding="utf-8"),
                    fragment_shader=hero_frag.read_text(encoding="utf-8"),
                )
                self._hero_vao = self._ctx.vertex_array(self._hero_program, [])

            title_vert = SHADER_DIR / "title_cosmos.vert.glsl"
            title_frag = SHADER_DIR / "title_cosmos.frag.glsl"
            if title_vert.exists() and title_frag.exists():
                self._title_program = self._ctx.program(
                    vertex_shader=title_vert.read_text(encoding="utf-8"),
                    fragment_shader=title_frag.read_text(encoding="utf-8"),
                )
                self._title_vao = self._ctx.vertex_array(self._title_program, [])

            ship_frag = SHADER_DIR / "ship_interior.frag.glsl"
            if hero_vert.exists() and ship_frag.exists():
                self._ship_program = self._ctx.program(
                    vertex_shader=hero_vert.read_text(encoding="utf-8"),
                    fragment_shader=ship_frag.read_text(encoding="utf-8"),
                )
                self._ship_vao = self._ctx.vertex_array(self._ship_program, [])

            card_frag = SHADER_DIR / "tcg_card.frag.glsl"
            if hero_vert.exists() and card_frag.exists():
                self._card_program = self._ctx.program(
                    vertex_shader=hero_vert.read_text(encoding="utf-8"),
                    fragment_shader=card_frag.read_text(encoding="utf-8"),
                )
                self._card_vao = self._ctx.vertex_array(self._card_program, [])

            self._create_targets()
            self.available = True
        except Exception as exc:
            self.error = f"Pos-processamento do HUD indisponivel: {exc}"
            self.available = False
            self._release_gpu()

    def _create_targets(self):
        for attr in ("_input", "_output", "_fbo"):
            obj = getattr(self, attr, None)
            if obj is not None:
                try:
                    obj.release()
                except Exception:
                    pass
        self._input = self._ctx.texture((self.width, self.height), 4, dtype="f1")
        self._input.filter = (self._mgl.LINEAR, self._mgl.LINEAR)
        self._input.repeat_x = False
        self._input.repeat_y = False
        self._output = self._ctx.texture((self.width, self.height), 4, dtype="f1")
        self._output.filter = (self._mgl.LINEAR, self._mgl.LINEAR)
        self._output.repeat_x = False
        self._output.repeat_y = False
        self._fbo = self._ctx.framebuffer(color_attachments=[self._output])

    def apply(self, surface, *, time=0.0, curvature=0.008, glow=0.48):
        if not self.available:
            return surface
        try:
            import pygame
            width, height = surface.get_size()
            if (width, height) != (self.width, self.height):
                self.width, self.height = width, height
                self._create_targets()
            self._input.write(pygame.image.tostring(surface, "RGBA", True), alignment=1)
            self._fbo.use()
            self._ctx.viewport = (0, 0, self.width, self.height)
            self._ctx.disable(self._mgl.BLEND | self._mgl.DEPTH_TEST)
            self._fbo.clear(0.0, 0.0, 0.0, 0.0)
            self._input.use(location=0)
            p = self._program
            p["u_hud"].value = 0
            p["u_resolution"].value = (float(self.width), float(self.height))
            p["u_time"].value = float(time)
            p["u_curvature"].value = max(0.0, min(0.04, float(curvature)))
            p["u_glow"].value = max(0.0, min(1.5, float(glow)))
            self._vao.render(mode=self._mgl.TRIANGLES, vertices=3)
            raw = self._fbo.read(components=4, alignment=1)
            return pygame.image.fromstring(raw, (self.width, self.height), "RGBA", True).convert_alpha()
        except Exception as exc:
            self.error = f"Falha no pos-processamento do HUD: {exc}"
            self.available = False
            self._release_gpu()
            return surface

    def apply_tcg_card_glow(self, card_surface, *, rarity_color=(255, 255, 255), name_bar_rect=(8, 48, 194, 22), time=0.0, cache_tag=None):
        if not self.available or self._card_program is None or self._card_vao is None:
            return card_surface
        try:
            import pygame
            w, h = card_surface.get_size()
            if w <= 0 or h <= 0:
                return card_surface
            time_step = int(float(time) * 10.0)
            if cache_tag is not None:
                ckey = (cache_tag, w, h, tuple(rarity_color[:3]), tuple(name_bar_rect), time_step)
                if ckey in self._card_cache:
                    return self._card_cache[ckey]

            bx, by, bw, bh = name_bar_rect
            u_x0 = float(bx) / max(1.0, float(w))
            u_x1 = float(bx + bw) / max(1.0, float(w))
            u_y0 = 1.0 - float(by + bh) / max(1.0, float(h))
            u_y1 = 1.0 - float(by) / max(1.0, float(h))

            tex_in = self._ctx.texture((w, h), 4, pygame.image.tostring(card_surface, "RGBA", True))
            tex_in.filter = (self._mgl.LINEAR, self._mgl.LINEAR)
            tex_out = self._ctx.texture((w, h), 4, dtype="f1")
            tex_out.filter = (self._mgl.LINEAR, self._mgl.LINEAR)
            fbo = self._ctx.framebuffer(color_attachments=[tex_out])
            fbo.use()
            self._ctx.viewport = (0, 0, w, h)
            self._ctx.disable(self._mgl.BLEND | self._mgl.DEPTH_TEST)
            fbo.clear(0.0, 0.0, 0.0, 0.0)
            tex_in.use(location=0)

            p = self._card_program
            p["u_card"].value = 0
            p["u_resolution"].value = (float(w), float(h))
            p["u_time"].value = float(time)
            p["u_rarity_color"].value = tuple(float(c) / 255.0 for c in rarity_color[:3])
            p["u_name_bar_uv"].value = (u_x0, u_y0, u_x1, u_y1)
            self._card_vao.render(mode=self._mgl.TRIANGLES, vertices=3)
            raw = fbo.read(components=4, alignment=1)
            fbo.release()
            tex_in.release()
            tex_out.release()

            result = pygame.image.fromstring(raw, (w, h), "RGBA", True).convert_alpha()
            if cache_tag is not None:
                if len(self._card_cache) > 48:
                    self._card_cache.clear()
                self._card_cache[ckey] = result
            return result
        except Exception:
            return card_surface

    def apply_hero_crystal_glow(self, surface, *, time=0.0, crystal_uv=(0.5, 0.5), glow_color=(87, 225, 205), direction=0):
        if not self.available or self._hero_program is None or self._hero_vao is None:
            return surface
        try:
            import pygame
            w, h = surface.get_size()
            if w <= 0 or h <= 0:
                return surface
            tex_in = self._ctx.texture((w, h), 4, pygame.image.tostring(surface, "RGBA", True))
            tex_in.filter = (self._mgl.NEAREST, self._mgl.NEAREST)
            tex_out = self._ctx.texture((w, h), 4, dtype="f1")
            tex_out.filter = (self._mgl.NEAREST, self._mgl.NEAREST)
            fbo = self._ctx.framebuffer(color_attachments=[tex_out])
            fbo.use()
            self._ctx.viewport = (0, 0, w, h)
            self._ctx.disable(self._mgl.BLEND | self._mgl.DEPTH_TEST)
            fbo.clear(0.0, 0.0, 0.0, 0.0)
            tex_in.use(location=0)
            p = self._hero_program
            p["u_sprite"].value = 0
            p["u_resolution"].value = (float(w), float(h))
            p["u_time"].value = float(time)
            p["u_crystal_uv"].value = (float(crystal_uv[0]), float(crystal_uv[1]))
            p["u_glow_color"].value = tuple(float(c) / 255.0 for c in glow_color[:3])
            if "direction" in p:
                p["direction"].value = int(direction)
            self._hero_vao.render(mode=self._mgl.TRIANGLES, vertices=3)
            raw = fbo.read(components=4, alignment=1)
            fbo.release()
            tex_in.release()
            tex_out.release()
            return pygame.image.fromstring(raw, (w, h), "RGBA", True).convert_alpha()
        except Exception:
            return surface

    def apply_ship_interior_glow(self, surface, *, time=0.0, tank_pos=(465, 575), status_pos=(875, 415)):
        if not self.available or self._ship_program is None or self._ship_vao is None:
            return surface
        try:
            import pygame
            width, height = surface.get_size()
            if (width, height) != (self.width, self.height):
                self.width, self.height = width, height
                self._create_targets()
            self._input.write(pygame.image.tostring(surface, "RGBA", True), alignment=1)
            self._fbo.use()
            self._ctx.viewport = (0, 0, self.width, self.height)
            self._ctx.disable(self._mgl.BLEND | self._mgl.DEPTH_TEST)
            self._fbo.clear(0.0, 0.0, 0.0, 1.0)
            self._input.use(location=0)
            p = self._ship_program
            p["u_scene"].value = 0
            p["u_resolution"].value = (float(self.width), float(self.height))
            p["u_time"].value = float(time)
            p["u_tank_uv"].value = (float(tank_pos[0]) / self.width, 1.0 - float(tank_pos[1]) / self.height)
            p["u_status_uv"].value = (float(status_pos[0]) / self.width, 1.0 - float(status_pos[1]) / self.height)
            self._ship_vao.render(mode=self._mgl.TRIANGLES, vertices=3)
            raw = self._fbo.read(components=4, alignment=1)
            return pygame.image.fromstring(raw, (self.width, self.height), "RGBA", True).convert()
        except Exception:
            return surface

    def render_title_screen(self, ui_surface, *, time=0.0):
        if not self.available or self._title_program is None or self._title_vao is None:
            return None
        try:
            import pygame
            width, height = ui_surface.get_size()
            if (width, height) != (self.width, self.height):
                self.width, self.height = width, height
                self._create_targets()
            self._input.write(pygame.image.tostring(ui_surface, "RGBA", True), alignment=1)
            self._fbo.use()
            self._ctx.viewport = (0, 0, self.width, self.height)
            self._ctx.disable(self._mgl.BLEND | self._mgl.DEPTH_TEST)
            self._fbo.clear(0.0, 0.0, 0.0, 1.0)
            self._input.use(location=0)
            p = self._title_program
            p["u_ui"].value = 0
            p["u_resolution"].value = (float(self.width), float(self.height))
            p["u_time"].value = float(time)
            self._title_vao.render(mode=self._mgl.TRIANGLES, vertices=3)
            raw = self._fbo.read(components=4, alignment=1)
            return pygame.image.fromstring(raw, (self.width, self.height), "RGBA", True).convert()
        except Exception:
            return None

    def _release_gpu(self):
        for attr in ("_vao", "_program", "_hero_vao", "_hero_program", "_title_vao", "_title_program", "_ship_vao", "_ship_program", "_card_vao", "_card_program", "_fbo", "_input", "_output"):
            obj = getattr(self, attr, None)
            if obj is not None:
                try:
                    obj.release()
                except Exception:
                    pass
                setattr(self, attr, None)
        if self._ctx is not None:
            try:
                self._ctx.release()
            except Exception:
                pass
            self._ctx = None

    def close(self):
        self._release_gpu()
        self.available = False
