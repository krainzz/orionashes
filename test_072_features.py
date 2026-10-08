from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / 'main.py'


def test_player_directional_asset_contract():
    source = MAIN.read_text(encoding='utf-8')
    for name in (
        "'down': 'baixo.png'",
        "'up': 'cima.png'",
        "'left': 'esquerda.png'",
        "'right': 'direita.png'",
    ):
        assert name in source
    assert "ROOT / 'assets' / 'player'" in source
    assert 'def _refresh_hero_images' in source
    assert '_1' in source


def test_world_actor_prefers_external_directional_sprite():
    source = MAIN.read_text(encoding='utf-8')
    needle = "raw = self.hero_images.get((hero_direction, frame % 2), self.hero_sprites[(hero_direction, frame % 2)])"
    assert needle in source


def test_combat_floor_uses_stable_horizontal_geometry():
    source = MAIN.read_text(encoding='utf-8')
    assert 'def combat_backdrop(self):' in source
    block = source[source.index('    def combat_backdrop(self):'):source.index('    def draw_kuvaar_water_deposits', source.index('    def combat_backdrop(self):'))]
    assert 'horizon_y = 278' in block
    assert 'floor_mid = 321' in block
    assert 'floor_bottom = 370' in block
    assert '[(285,278),(380,240)' not in block.replace(' ', '')


def test_equipment_assets_are_now_part_of_distribution():
    assets = ROOT / 'assets' / 'equips'
    expected = {'Elmo.png','Peitoral.png','Grevas.png','Manopla.png'}
    assert assets.is_dir()
    assert expected.issubset({p.name for p in assets.glob('*.png')})


def test_release_version_and_save_schema():
    content = (ROOT / 'content.py').read_text(encoding='utf-8')
    core = (ROOT / 'core.py').read_text(encoding='utf-8')
    main = MAIN.read_text(encoding='utf-8')
    assert "VERSION = '0.7.2'" in content
    assert "data['version'] = 72" in core
    assert '0.7.2' in main
