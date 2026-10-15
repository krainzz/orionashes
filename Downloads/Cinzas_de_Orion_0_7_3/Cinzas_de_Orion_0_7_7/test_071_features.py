import json
import tempfile
import unittest
from pathlib import Path

from content import VERSION, FUTURE_UPGRADES
from core import State
from world import SECTORS


class FixedRng:
    def __init__(self, random_value=0.1):
        self.random_value = random_value

    def random(self):
        return self.random_value

    def uniform(self, a, b):
        return (a + b) / 2

    def randint(self, a, b):
        return a


class Version071FeatureTests(unittest.TestCase):
    def setUp(self):
        self.state = State(seed=7, new_game=True)

    def _unlock_laser_project(self):
        self.state.helmet_owned = True
        self.state.helmet_generation = 1
        self.state.language_mastered = True
        self.state.language_mastery['avarin'] = True
        self.state.award_renown('scavengers', 25, reason='teste 0.7.1')
        mira = next(
            npc
            for sector in SECTORS.values()
            if sector.get('settlement')
            for npc in sector['settlement'].get('npcs', [])
            if npc.get('id') == 'avarin_reclaimer'
        )
        self.state.interact_npc(mira)

    def _install_laser(self):
        self._unlock_laser_project()
        for item, qty in {'Sucata': 30, 'Placa': 10, 'Liga meteórica': 4, 'Matriz fotônica': 2}.items():
            self.state.inventory[item] = qty
        self.state.inside_ship = True
        result = self.state.craft('ship_laser')
        self.assertIn('instalado', result.lower())

    def test_version_and_laser_project_catalog(self):
        self.assertEqual(VERSION, '0.7.3')
        self.assertEqual(FUTURE_UPGRADES['ship_laser']['recipe'], {
            'Sucata': 30, 'Placa': 10, 'Liga meteórica': 4, 'Matriz fotônica': 2
        })

    def test_laser_mission_requires_language_and_first_renown_milestone(self):
        self.state.award_renown('scavengers', 24)
        self.assertEqual(self.state.missions['ship_laser_project']['status'], 'locked')
        self.state.language_mastered = True
        self.state.language_mastery['avarin'] = True
        self.state.award_renown('scavengers', 1)
        self.assertEqual(self.state.missions['ship_laser_project']['status'], 'active')
        self.assertFalse(self.state.ship_laser_project_unlocked)

    def test_mira_grants_project_and_install_requires_materials(self):
        self._unlock_laser_project()
        self.assertTrue(self.state.ship_laser_project_unlocked)
        self.assertEqual(self.state.missions['ship_laser_project']['status'], 'completed')
        self.state.inside_ship = True
        self.assertIn('Faltam materiais', self.state.craft('ship_laser'))
        for item, qty in {'Sucata': 30, 'Placa': 10, 'Liga meteórica': 4, 'Matriz fotônica': 2}.items():
            self.state.inventory[item] = qty
        self.assertIn('instalado', self.state.craft('ship_laser').lower())
        self.assertTrue(self.state.ship_laser_installed)

    def test_asteroid_encounter_only_after_laser_and_only_intergalactic(self):
        self.state.dobra_core_installed = True
        self.state.ship_systems = {key: 100 for key in self.state.ship_systems}
        self.state.known_planets += ['dornak']
        self.state.rng = FixedRng(0.1)
        self.assertFalse(self.state.should_trigger_asteroid_encounter('orionis'))
        self.assertFalse(self.state.should_trigger_asteroid_encounter('dornak'))
        self.state.ship_laser_installed = True
        self.assertTrue(self.state.should_trigger_asteroid_encounter('dornak'))
        self.state.rng = FixedRng(0.9)
        self.assertFalse(self.state.should_trigger_asteroid_encounter('dornak'))

    def test_asteroid_reward_damage_and_repair_block_flight(self):
        self._install_laser()
        self.state.dobra_core_installed = True
        self.state.ship_systems = {key: 100 for key in self.state.ship_systems}
        self.state.known_planets += ['dornak']
        self.state.resolve_asteroid_encounter(4, 3)
        self.assertEqual(self.state.inventory['Essência'], 4)
        self.assertEqual(self.state.travel_damage, 3)
        self.assertEqual(self.state.missions['travel_repair']['status'], 'active')
        ok, message = self.state.can_travel_to_planet('dornak')
        self.assertFalse(ok)
        self.assertIn('3 Sucata', message)
        self.state.inventory['Sucata'] = 3
        ok, message = self.state.repair_travel_damage()
        self.assertTrue(ok, message)
        self.assertEqual(self.state.travel_damage, 0)
        self.assertEqual(self.state.inventory['Sucata'], 0)
        self.assertEqual(self.state.missions['travel_repair']['status'], 'completed')

    def test_damage_is_capped_at_six_per_encounter_and_stats_persist(self):
        self._install_laser()
        self.state.resolve_asteroid_encounter(2, 99)
        self.assertEqual(self.state.travel_damage, 6)
        self.assertEqual(self.state.statistics['asteroids_destroyed'], 2)
        self.assertEqual(self.state.statistics['asteroid_encounters'], 1)

    def test_save_roundtrip_version_071_persists_new_state(self):
        self._install_laser()
        self.state.travel_damage = 4
        self.state.missions['travel_repair']['status'] = 'active'
        self.state.missions['travel_repair']['required'] = 4
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'save.json'
            self.state.save(path)
            raw = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(raw['version'], 72)
            self.assertTrue(raw['ship_laser_project_unlocked'])
            self.assertTrue(raw['ship_laser_installed'])
            self.assertEqual(raw['travel_damage'], 4)
            loaded, message = State.load(path)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(message, 'Campanha 0.7.3 carregada.')
            self.assertTrue(loaded.ship_laser_project_unlocked)
            self.assertTrue(loaded.ship_laser_installed)
            self.assertEqual(loaded.travel_damage, 4)
            self.assertEqual(loaded.missions['travel_repair']['required'], 4)

    def test_v070_save_gets_new_defaults_and_can_unlock_laser(self):
        self.state.helmet_owned = True
        self.state.helmet_generation = 1
        self.state.language_mastered = True
        self.state.language_mastery['avarin'] = True
        self.state.renown_by_faction['scavengers'] = 25
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'save.json'
            self.state.save(path)
            raw = json.loads(path.read_text(encoding='utf-8'))
            raw['version'] = 70
            raw.pop('ship_laser_project_unlocked', None)
            raw.pop('ship_laser_installed', None)
            raw.pop('travel_damage', None)
            raw['missions'].pop('ship_laser_project', None)
            raw['missions'].pop('travel_repair', None)
            path.write_text(json.dumps(raw, ensure_ascii=False), encoding='utf-8')
            loaded, message = State.load(path)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('0.7.3', message)
            self.assertEqual(loaded.travel_damage, 0)
            self.assertTrue(loaded.ship_laser_project_unlocked is False)
            self.assertEqual(loaded.missions['ship_laser_project']['status'], 'active')


if __name__ == '__main__':
    unittest.main()
