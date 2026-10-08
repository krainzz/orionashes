from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / 'main.py'

def test_equipment_assets_use_lazy_refresh():
    source = MAIN.read_text(encoding='utf-8')
    assert 'def _refresh_equipment_images' in source
    assert 'self._refresh_equipment_images()' in source
    assert "ROOT / 'assets' / 'equips'" in source


def test_official_asset_names_are_exact():
    source = MAIN.read_text(encoding='utf-8')
    for item in (
        "'helmet': 'Elmo.png'",
        "'chest': 'Peitoral.png'",
        "'locomotion': 'Grevas.png'",
        "'gauntlet': 'Manopla.png'",
    ):
        assert item in source


def test_equipment_assets_are_packaged_in_current_release():
    assets = ROOT / 'assets' / 'equips'
    expected = {'Elmo.png','Peitoral.png','Grevas.png','Manopla.png'}
    assert assets.is_dir()
    assert expected.issubset({p.name for p in assets.glob('*.png')})
    for name in expected:
        assert (assets / name).stat().st_size > 1000
