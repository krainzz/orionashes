import unittest
from pathlib import Path

from content import VERSION


class Version064FeatureTests(unittest.TestCase):
    def test_version_is_064(self):
        self.assertEqual(VERSION, '0.6.9')

    def test_plasma_attack_uses_native_additive_blend(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def _draw_basic_gauntlet_attack(self, start, end, tip, progress, elapsed):', source)
        self.assertIn('pygame.BLEND_RGB_ADD', source)
        self.assertIn("self._draw_basic_gauntlet_attack(start, end, (px, py), p, t)", source)
        self.assertIn('pygame.draw.line(beam, (255, 255, 255)', source)
        self.assertIn('Partículas e halo no emissor.', source)
        self.assertIn('Raio de Plasma', source)

    def test_basic_card_fx_uses_plasma_visual(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("visual == 'plasma'", source)
        self.assertNotIn("pygame.draw.line(self.canvas, color, start, (px, py), 4)", source)

    def test_character_base_dimensions_are_documented_in_code(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('pygame.Surface((44, 58)', source)
        self.assertIn('pygame.Surface((84, 66)', source)
        self.assertIn("self.actor('hero', hero_x, 414, 1.95", source)


if __name__ == '__main__':
    unittest.main()
