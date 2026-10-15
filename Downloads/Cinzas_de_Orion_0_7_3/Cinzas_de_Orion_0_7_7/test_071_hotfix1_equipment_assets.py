from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / 'main.py'


def test_equipment_asset_references_are_exact():
    source = MAIN.read_text(encoding='utf-8')
    expected = {
        "'helmet': 'Elmo.png'",
        "'chest': 'Peitoral.png'",
        "'locomotion': 'Grevas.png'",
        "'gauntlet': 'Manopla.png'",
    }
    for item in expected:
        assert item in source


def test_equipment_images_are_loaded_from_assets_equips():
    source = MAIN.read_text(encoding='utf-8')
    assert "ROOT / 'assets' / 'equips'" in source
    assert 'self.equipment_images = {}' in source
    assert 'pygame.image.load(str(image_path)).convert_alpha()' in source


def test_procedural_fallback_remains_after_official_asset_branch():
    source = MAIN.read_text(encoding='utf-8')
    branch = source.index("official = getattr(self, 'equipment_images', {}).get(kind)")
    fallback = source.index("if kind == 'helmet':", branch)
    assert fallback > branch
    assert "self.canvas.blit(image" in source[branch:fallback]
