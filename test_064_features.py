import unittest
from pathlib import Path

import content


class Version064FeatureTests(unittest.TestCase):
    def test_version_is_064(self):
        self.assertEqual(content.VERSION, "0.6.9")

    def test_all_cards_have_visual_keys_except_none(self):
        expected = {
            "shell", "bite", "static", "hound", "burrow", "manta", "stalker", "guard_strike",
            "lithic_sentence", "rift_break", "kuvaar", "fagor", "kael", "ounull", "ry", "ounull_tide",
            "magma_lance", "forge_claw", "ion_burst", "frost_bite", "crystal_ram", "glacial_gust",
            "root_spear", "basalt_charge", "salt_spit", "luminous_ray", "umbra_claw", "spore_burst",
            "ferrous_mite_card", "magnetic_ram_card", "gloom_moth_card", "vesper_cat_card", "charge_ray_card",
            "ion_toad_card", "cinder_strider_card", "magma_beetle_card", "reef_skimmer_card", "tide_serpent_card",
            "spore_hare_card", "mycelial_beast_card", "wind_stalker_card", "leviwing_card", "street_drone_card",
            "plasma_hound_card", "mekron", "nocther", "voltrik", "moryss", "verdak", "gravorn",
            "alphor_fireball", "broom_lightning",
        }
        for cid in expected:
            self.assertTrue(content.CARDS[cid].get("visual_key"), cid)

    def test_basic_name_is_plasma_ray(self):
        source_main = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        source_core = Path(__file__).with_name("core.py").read_text(encoding="utf-8")
        self.assertIn("'RAIO DE PLASMA'", source_main)
        self.assertIn("card_y, card_w, card_h, gap = 535, 210, 118, 10", source_main)
        self.assertIn("'Raio de Plasma'", source_core)
        self.assertNotIn("GOLPE DE MANOPLA", source_main)

    def test_title_screen_and_start_flow_exist(self):
        source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        self.assertIn("self.mode = 'title'", source)
        self.assertIn("def title_screen(self):", source)
        self.assertIn("Pressione qualquer tecla para começar", source)
        self.assertIn("def start_from_title(self):", source)
        self.assertIn("if self.mode == 'title':", source)

    def test_aurora_has_small_additive_glow(self):
        source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        self.assertIn("def draw_aurora_detail", source)
        self.assertIn("special_flags=pygame.BLEND_RGB_ADD", source)
        self.assertIn("pulse =", source)


if __name__ == '__main__':
    unittest.main()
