"""Regressions for the separate futuristic ModernGL combat HUD."""
from pathlib import Path

from combat_hud import CombatHUDRenderer

ROOT = Path(__file__).resolve().parent


def test_hud_shaders_exist_and_expose_lens_and_glow_controls():
    shaders = ROOT / "assets" / "shaders"
    vert = (shaders / "combat_hud.vert.glsl").read_text(encoding="utf-8")
    frag = (shaders / "combat_hud.frag.glsl").read_text(encoding="utf-8")
    assert "gl_VertexID" in vert
    assert "u_curvature" in frag
    assert "u_glow" in frag
    assert "warpedUV" in frag
    assert "glowRGB" in frag
    assert "fragColor = vec4(rgb, alpha)" in frag


def test_hud_renderer_is_optional_and_falls_back_without_gpu():
    renderer = CombatHUDRenderer(enabled=False)
    placeholder = object()
    assert renderer.apply(placeholder, time=3.5) is placeholder
    assert renderer.available is False
    renderer.close()


def test_hud_fbo_is_separate_from_scene_processing():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    assert "self._battle_view_layers(base_canvas, hud_surface)" in source
    assert "self.canvas = base_canvas" in source
    assert "self.canvas = hud_surface" in source
    assert "hud_renderer.apply(hud_surface, time=self.frame)" in source
    assert source.index("self.combat_fx_renderer.apply(self.canvas)") < source.index("hud_renderer.apply(hud_surface, time=self.frame)")


def test_hud_style_keeps_existing_action_hitboxes_and_card_tooltips():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    assert "self.buttons.append((rect, callback, enabled))" in source
    assert "hover_card=next" in source
    assert "self.wrap(card.get('description'" in source
    assert "self._draw_combat_hud_button" in source
    assert "TARGET_LOCK" in source


def test_release_version_is_073_without_save_schema_change():
    content = (ROOT / "content.py").read_text(encoding="utf-8")
    core = (ROOT / "core.py").read_text(encoding="utf-8")
    assert "VERSION = '0.7.3'" in content
    assert "data['version'] = 72" in core
