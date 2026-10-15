"""Tests for the optional ModernGL combat FX rendering layer."""
from pathlib import Path

from combat_fx import CombatFXRenderer, FX_PRESETS, ELEMENT_PRESETS, CRITICAL_SHOCKWAVE, SUPREME_SHOCKWAVE


def test_fx_presets_cover_elements_and_specials():
    assert set(ELEMENT_PRESETS) == {'Fogo', 'Água', 'Planta', 'Terra', 'Metal', 'Elétrico', 'Luz', 'Trevas'}
    assert {'physical', 'fire', 'water', 'plant', 'earth', 'metal', 'electric', 'light', 'dark', 'shield', 'heal'} <= set(FX_PRESETS)
    for preset in FX_PRESETS.values():
        assert preset['duration'] > 0
        assert len(preset['color']) == 3
        assert 0 <= preset['particles'] <= 160


def test_trigger_and_visual_clock_do_not_depend_on_gpu():
    renderer = CombatFXRenderer(enabled=False)
    event = renderer.trigger('fire', (200, 300), (700, 400), critical=True)
    assert event['preset'] == 'fire'
    assert event['shock']['duration'] == CRITICAL_SHOCKWAVE['duration']
    renderer.update(0.1)
    assert 0.09 < renderer.events[0]['age'] < 0.11
    renderer.update(2.0)
    assert renderer.events == []


def test_supreme_uses_stronger_shockwave():
    renderer = CombatFXRenderer(enabled=False)
    e = renderer.trigger('light', supreme=True)
    assert e['shock']['intensity'] > CRITICAL_SHOCKWAVE['intensity']
    assert e['shock']['duration'] == SUPREME_SHOCKWAVE['duration']


def test_fallback_returns_original_surface_when_gpu_disabled():
    renderer = CombatFXRenderer(enabled=False)
    surface = object()
    assert renderer.apply(surface) is surface


def test_preset_configuration_is_exposed_and_validated():
    renderer = CombatFXRenderer(enabled=False)
    renderer.configure('fire', duration=1.2, color=(250, 80, 20), particles=95)
    assert renderer.presets['fire']['duration'] == 1.2
    assert renderer.presets['fire']['color'] == (250, 80, 20)
    assert renderer.presets['fire']['particles'] == 95
    try:
        renderer.configure('fire', duration=0)
    except ValueError:
        pass
    else:
        raise AssertionError('duration zero should be rejected')


def test_glsl_shaders_include_instancing_lights_and_postprocess():
    root = Path(__file__).resolve().parent / 'assets' / 'shaders'
    particle_vert = (root / 'combat_particles.vert.glsl').read_text(encoding='utf-8')
    post_frag = (root / 'combat_post.frag.glsl').read_text(encoding='utf-8')
    assert 'gl_InstanceID' in particle_vert
    assert 'u_preset == 0' in particle_vert and 'u_preset == 1' in particle_vert and 'u_preset == 2' in particle_vert
    assert 'u_light_pos_radius' in post_frag and 'u_shock_enabled' in post_frag and 'u_chromatic_intensity' in post_frag


def test_app_integration_only_triggers_visual_fx():
    source = (Path(__file__).resolve().parent / 'main.py').read_text(encoding='utf-8')
    assert 'self._trigger_gpu_combat_fx(\'player\'' in source
    assert "self._trigger_gpu_combat_fx('enemy'" in source
    assert 'processed = self.combat_fx_renderer.apply(self.canvas)' in source
    assert 'renderer.update(dt)' in source
