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
    assert 'def _compose_external_hero' in source
    assert 'external = self._compose_external_hero(external_direction, frame)' in source
    assert 'raw = self.hero_sprites[(hero_direction, frame % 2)]' in source


def test_external_player_art_is_stretched_to_expected_canvas():
    source = MAIN.read_text(encoding='utf-8')
    assert 'PLAYER_SPRITE_SIZE = (44, 85)' in source
    assert 'pygame.transform.scale(first, PLAYER_SPRITE_SIZE)' in source
    assert 'pygame.transform.scale(second, PLAYER_SPRITE_SIZE)' in source


def test_equipment_layers_are_composed_from_equipped_state():
    source = MAIN.read_text(encoding='utf-8')
    assert "ROOT / 'assets' / 'player' / 'equips'" in source
    assert "'locomotion': 'grevas'" in source
    assert "'chest': 'peitoral'" in source
    assert "'helmet': 'elmo'" in source
    assert "'gauntlet': 'manopla'" in source
    assert "for piece in ('locomotion', 'chest', 'helmet', 'gauntlet')" in source
    assert "return bool(getattr(self.state, 'helmet_equipped', False))" in source
    assert "return bool(getattr(self.state, 'locomotion_equipped', False))" in source


def test_equipment_and_victory_use_external_front_sprite_when_available():
    source = MAIN.read_text(encoding='utf-8')
    assert "self.actor('hero', 210, 276, 1.35, direction='down')" in source
    assert "pose='combat',external_appearance=True" in source.replace(' ', '')
    victory_block = source[source.index('    def victory(self):'):source.index('    def install_dobra_core_ui', source.index('    def victory(self):'))]
    assert 'external_appearance=True' in victory_block


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
    assert "VERSION = '0.7.3'" in content
    assert "data['version'] = 72" in core
    assert '0.7.3' in main
