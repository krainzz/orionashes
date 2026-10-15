import unittest
from pathlib import Path

class Version068Hotfix3StatsTests(unittest.TestCase):
    def test_result_defense_metrics_and_font_size(self):
        source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        block = source[source.index("def victory"):source.index("def install_dobra_core_ui", source.index("def victory"))]
        for phrase in (
            "Cura por Vampirismo",
            "Dano protegido por escudo",
            "Dano reduzido por técnicas",
            "self.label(text,view.x,yy,14,GOLD)",
            "self.fit_text(text,12,view.width-20)",
        ):
            self.assertIn(phrase, block)

    def test_summary_tracks_new_defensive_metrics(self):
        source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        block = source[source.index("def _new_combat_summary"):source.index("def engage", source.index("def _new_combat_summary"))]
        for key in ("vampirism_healing", "shield_absorbed", "technique_damage_reduced"):
            self.assertIn(repr(key), block)

    def test_enemy_result_reports_mitigation_metrics(self):
        source = Path(__file__).with_name("core.py").read_text(encoding="utf-8")
        block = source[source.index("def enemy_turn"):source.index("def _end_virtual_battle", source.index("def enemy_turn"))]
        self.assertIn("shield_absorbed=shield_absorbed", block)
        self.assertIn("technique_damage_reduced=technique_damage_reduced", block)

if __name__ == "__main__":
    unittest.main()
