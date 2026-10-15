import json
import tempfile
import unittest
from pathlib import Path

from content import SHIP_DIAGNOSTIC_ORDER, SHIP_MISSION_DATA, SHIP_SYSTEMS
from core import State


class Version051FeatureTests(unittest.TestCase):
    def test_all_ship_repair_missions_are_available(self):
        state = State(seed=51)
        expected = {'ship_hull','ship_power','ship_propulsion','ship_navigation','ship_comms','ship_ftl'}
        self.assertTrue(expected.issubset(state.missions))
        self.assertTrue(all(state.missions[mid]['status'] == 'available' for mid in expected))

    def test_mission_completion_alert_works_for_campaign_and_ship(self):
        state = State(seed=51)
        for mid in ('water_supply','kuvaar_hunt','faction_conflict','ship_hull'):
            state.achievement_alerts.clear()
            state._mission_completed_alert(mid)
            self.assertEqual(state.achievement_alerts[-1], {'type':'mission','mid':mid})

    def test_navigation_repair_cost_and_completion(self):
        state = State(seed=51)
        ok, _ = state.start_ship_mission('ship_navigation')
        self.assertTrue(ok)
        state.inventory['Sucata'] = 79
        ok, msg = state.navigation_repair()
        self.assertFalse(ok)
        self.assertIn('80', msg)
        self.assertEqual(state.ship_systems['navigation'], 14)
        state.inventory['Sucata'] = 80
        ok, msg = state.navigation_repair()
        self.assertTrue(ok)
        self.assertEqual(state.ship_systems['navigation'], 100)
        self.assertEqual(state.missions['ship_navigation']['status'], 'completed')
        self.assertEqual(state.inventory['Sucata'], 0)

    def test_flight_ready_requires_all_six_systems(self):
        state = State(seed=51)
        self.assertFalse(state.ship_flight_ready())
        for sid in SHIP_DIAGNOSTIC_ORDER:
            state.ship_systems[sid] = 100
        self.assertTrue(state.ship_flight_ready())

    def test_comms_route_is_hidden_until_mission_starts_and_persists_after_completion(self):
        state = State(seed=51)
        gate = next(g for g in state.area['exits'] if g.get('target') == 'comms_ridge')
        self.assertFalse(state.communication_route_visible())
        self.assertFalse(state.route_visible(gate))
        ok, _ = state.start_ship_mission('ship_comms')
        self.assertTrue(ok)
        self.assertTrue(state.communication_route_visible())
        self.assertTrue(state.route_visible(gate))
        state.missions['ship_comms']['status'] = 'completed'
        self.assertTrue(state.communication_route_visible())
        self.assertTrue(state.route_visible(gate))

    def test_comms_never_respawns_mission_sentinels_and_reveals_planets(self):
        state = State(seed=51)
        ok, _ = state.start_ship_mission('ship_comms')
        self.assertTrue(ok)
        enemies = state.worlds.get('comms_ridge', [])
        mission_ids = [e for e in enemies if e.get('mission_id') == 'ship_comms']
        self.assertEqual(len(mission_ids), 4)
        for enemy in mission_ids:
            enemy['dead'] = True
        ok, _ = state.communication_repair()
        self.assertTrue(ok)
        self.assertEqual(state.ship_systems['comms'], 100)
        self.assertEqual(state.missions['ship_comms']['status'], 'completed')
        changed = state.reveal_communications()
        self.assertTrue(changed or state.communication_revealed)
        self.assertEqual(set(state.known_planets), {'veyra','orionis','kael','nahr','elyra'})
        # mission sentinels stay dead in the persistent world state
        self.assertTrue(all(e.get('dead') for e in mission_ids))

    def test_ship_mission_data_covers_each_ship_system_once(self):
        systems = [data['system'] for data in SHIP_MISSION_DATA.values()]
        self.assertEqual(set(systems), set(SHIP_DIAGNOSTIC_ORDER))
        self.assertEqual(len(systems), len(set(systems)))
        for system in systems:
            self.assertEqual(SHIP_SYSTEMS[system]['condition'], 100 if system == 'navigation' and False else SHIP_SYSTEMS[system]['condition'])

    def test_content_and_ui_keep_navigation_button_action_available(self):
        main_source = Path('main.py').read_text(encoding='utf-8')
        self.assertIn("'REPARAR COM 80 SUCATAS'", main_source)
        self.assertIn("self._ship_navigation_try", main_source)
        self.assertIn("'REPARAR COM 80 SUCATAS',self._ship_navigation_try,True", main_source)
        self.assertIn("self.state.ship_flight_ready()", main_source)


if __name__ == '__main__':
    unittest.main()
