import tempfile
import unittest
from pathlib import Path

from core import State
from content import GALAXIES, GALAXY_DISPLAY_ORDER, STELLAR_ROUTES


class Version061HotfixTests(unittest.TestCase):
    def test_dobra_core_mission_unlocks_after_ry_drop(self):
        s = State(seed=1)
        self.assertEqual(s.missions['dobra_core_install']['status'], 'locked')
        s.inventory['Núcleo de Dobra'] = 1
        changed = s.ensure_dobra_core_mission()
        self.assertTrue(changed)
        self.assertEqual(s.missions['dobra_core_install']['status'], 'active')
        self.assertEqual(s.objective('dobra_core_install')['status'], 'active')

    def test_dobra_core_install_consumes_item_and_completes_mission(self):
        s = State(seed=1)
        s.inside_ship = True
        s.inventory['Núcleo de Dobra'] = 1
        s.ensure_dobra_core_mission()
        before = s.statistics['missions_completed']
        ok, msg = s.install_dobra_core()
        self.assertTrue(ok)
        self.assertIn('instalado', msg)
        self.assertEqual(s.inventory.get('Núcleo de Dobra', 0), 0)
        self.assertTrue(s.dobra_core_installed)
        self.assertEqual(s.missions['dobra_core_install']['status'], 'completed')
        self.assertEqual(s.objective('dobra_core_install')['status'], 'completed')
        self.assertEqual(s.statistics['missions_completed'], before + 1)
        self.assertEqual(len(s.known_planets), 9)  # Veyra + 8 new intergalactic worlds

    def test_installation_requires_item_and_does_not_consume_without_it(self):
        s = State(seed=1)
        s.inside_ship = True
        ok, _ = s.install_dobra_core()
        self.assertFalse(ok)
        self.assertFalse(s.dobra_core_installed)

    def test_old_save_without_new_objective_receives_compatible_objective(self):
        s = State(seed=1)
        s.inventory['Núcleo de Dobra'] = 1
        # Simulate a 0.6.0-style in-memory journal that did not yet know the hotfix objective.
        s.journal['objectives'].pop('dobra_core_install', None)
        s.journal['objectives']['dobra_core_install'] = {'status': 'locked', 'progress': 0}
        self.assertEqual(s.ensure_dobra_core_mission(), True)
        self.assertEqual(s.missions['dobra_core_install']['status'], 'active')

    def test_galaxy_selector_catalog_keeps_hierarchical_groups(self):
        self.assertEqual(tuple(GALAXY_DISPLAY_ORDER), ('local', 'vharos', 'meridion'))
        groups = {gid: [r['id'] for r in STELLAR_ROUTES if r.get('galaxy') == gid] for gid in GALAXY_DISPLAY_ORDER}
        self.assertEqual(len(groups['local']), 5)
        self.assertEqual(len(groups['vharos']), 4)
        self.assertEqual(len(groups['meridion']), 4)
        self.assertEqual(set(groups), set(GALAXIES))

    def test_save_format_stays_compatible_with_060(self):
        s = State(seed=1)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'save.json'
            s.save(path)
            data = __import__('json').loads(path.read_text(encoding='utf-8'))
            self.assertEqual(data['version'], 65)
            loaded, _ = State.load(path)
            self.assertIsInstance(loaded, State)
            self.assertIn('dobra_core_install', loaded.missions)
            self.assertIn('dobra_core_install', loaded.journal['objectives'])


if __name__ == '__main__':
    unittest.main()
