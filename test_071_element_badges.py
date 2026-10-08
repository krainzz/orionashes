import unittest
from pathlib import Path


class ElementBadgeAssetTests(unittest.TestCase):
    def test_all_element_badges_are_packaged(self):
        root = Path(__file__).resolve().parent / "assets" / "elements"
        expected = {
            "fogo.png", "agua.png", "planta.png", "terra.png",
            "metal.png", "eletrico.png", "luz.png", "trevas.png",
        }
        self.assertTrue(root.is_dir())
        self.assertEqual({p.name for p in root.glob("*.png")}, expected)
        for name in expected:
            self.assertGreater((root / name).stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
