import unittest
from core import State
from content import SHIP_DIAGNOSTIC_ORDER


class Hotfix056TwoTests(unittest.TestCase):
    def test_flight_unlock_queues_specific_exploration_alert(self):
        s = State(seed=7, new_game=True)
        s.achievement_alerts.clear()
        for sid in SHIP_DIAGNOSTIC_ORDER:
            s.ship_systems[sid] = 100
        s.ensure_exploration_mission()
        self.assertIn({'type': 'flight_unlocked'}, s.achievement_alerts)
        self.assertTrue(s.missions['explore_galaxy']['status'] == 'active')

    def test_all_essence_crafts_use_inventory_plus_storage(self):
        s = State(seed=8, new_game=True)
        s.inside_ship = True
        s.respawn_tank_built = False
        s.missions['respawn_tank']['status'] = 'active'
        s.inventory['Essência'] = 20
        s.essence_storage = 30
        msg = s.craft('respawn_tank')
        self.assertIn('Tanque de Renascimento construído', msg)
        self.assertEqual(s.inventory.get('Essência', 0), 0)
        self.assertEqual(s.essence_storage, 0)

import json
import tempfile
import unittest
from pathlib import Path

from content import HELMET_TIERS, SHIP_INTERIOR, SPECIES
from core import State


class Version056FeatureTests(unittest.TestCase):
    def test_fresh_game_opens_inside_ship_and_finishes_into_respawn_mission(self):
        s = State(new_game=True)
        self.assertTrue(s.inside_ship)
        self.assertTrue(s.opening_dialogue_pending)
        self.assertEqual(tuple(s.ship_pos), tuple(SHIP_INTERIOR['start']))
        self.assertEqual(s.missions['respawn_tank']['status'], 'locked')
        self.assertTrue(s.finish_opening_dialogue())
        self.assertFalse(s.opening_dialogue_pending)
        self.assertEqual(s.missions['respawn_tank']['status'], 'active')
        self.assertEqual(s.journal['objectives']['respawn_tank']['status'], 'active')
        self.assertTrue(any(a.get('type') == 'mission_started' and a.get('mid') == 'respawn_tank' for a in s.achievement_alerts))

    def test_loaded_save_never_reopens_new_game_dialogue(self):
        s = State(new_game=True); s.finish_opening_dialogue()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            s.save(path, refresh=False)
            loaded, _ = State.load(path)
        self.assertFalse(loaded.opening_dialogue_pending)

    def test_essence_storage_is_a_safe_pool_and_unique_craft_uses_combined_total(self):
        s = State(1)
        s.crafted.append('shell|normal|1')
        s.inventory['Essência'] = 800
        s.essence_storage = 1200
        self.assertEqual(s.essence_total(), 2000)
        self.assertTrue(s.consume_essence(1500))
        self.assertEqual(s.inventory['Essência'], 0)
        self.assertEqual(s.essence_storage, 500)
        s.inventory['Essência'] = 800
        s.essence_storage = 1200
        s.unique_card_source = None if not hasattr(s, 'unique_card_source') else s.unique_card_source
        result, message = s.craft_unique_card('shell|normal|1')
        self.assertIsInstance(message, str)
        self.assertIn('Carta Única', message)
        self.assertEqual(s.essence_total(), 0)
        self.assertFalse('shell|normal|1' in s.crafted)
        self.assertEqual(len(s.unique_cards), 1)


    def test_fatal_attack_without_stasis_is_immediately_fatal_and_tier_2_opens_qte(self):
        original = dict(SPECIES['scarab'])
        try:
            SPECIES['scarab']['fatal_attack'] = True
            SPECIES['scarab']['fatal_window'] = 5.0
            SPECIES['scarab']['fatal_key'] = 'F'
            SPECIES['scarab']['threat_level'] = 4
            s = State(1)
            s.start_battle(0)
            class Rng:
                def random(self): return 0.0
                def randint(self, a, b): return a
            s.rng = Rng()
            fatal = s.enemy_turn()
            self.assertTrue(fatal['defeat'])
            self.assertTrue(s.game_over)

            s = State(1)
            s.helmet_owned = True; s.helmet_equipped = True; s.helmet_generation = 2
            s.start_battle(0)
            s.rng = Rng()
            qte = s.enemy_turn()
            self.assertTrue(qte['stasis_triggered'])
            self.assertEqual(qte['damage'], 0)
            self.assertEqual(qte['stasis_seconds'], 5.0)
            self.assertEqual(qte['stasis_key'], 'F')
            self.assertFalse(s.game_over)
        finally:
            SPECIES['scarab'].clear(); SPECIES['scarab'].update(original)

    def test_respawn_tank_recipe_is_visible_only_after_opening_mission_is_active(self):
        s = State(new_game=True)
        self.assertNotEqual(s.missions['respawn_tank']['status'], 'active')
        s.finish_opening_dialogue()
        self.assertEqual(s.missions['respawn_tank']['status'], 'active')
        s.inventory['Essência'] = 50
        msg = s.craft('respawn_tank')
        self.assertIn('construído', msg)
        self.assertTrue(s.respawn_tank_built)
        self.assertEqual(s.inventory.get('Essência',0), 0)

    def test_essence_deposit_moves_only_inventory_and_does_not_change_storage_twice(self):
        s = State(1)
        s.inventory['Essência'] = 37
        s.essence_storage = 11
        self.assertEqual(s.deposit_essence(), 37)
        self.assertEqual(s.inventory['Essência'], 0)
        self.assertEqual(s.essence_storage, 48)
        self.assertEqual(s.deposit_essence(), 0)
        self.assertEqual(s.essence_storage, 48)

    def test_death_with_tank_loses_ten_percent_only_from_inventory(self):
        s = State(1)
        s.respawn_tank_built = True
        s.inventory['Essência'] = 105
        s.essence_storage = 800
        s.hp = 0
        result = s.resolve_death('Teste')
        self.assertTrue(result['respawned'])
        self.assertEqual(result['lost_essence'], 10)
        self.assertEqual(s.inventory['Essência'], 95)
        self.assertEqual(s.essence_storage, 800)
        self.assertTrue(s.inside_ship)
        self.assertFalse(s.game_over)
        self.assertEqual(s.hp, s.max_hp)

    def test_death_without_tank_is_game_over(self):
        s = State(1)
        s.inventory['Essência'] = 500
        result = s.resolve_death('Teste')
        self.assertTrue(result['game_over'])
        self.assertTrue(s.game_over)
        self.assertFalse(s.inside_ship)
        self.assertEqual(s.inventory['Essência'], 500)

    def test_stasis_is_only_available_from_equipped_helmet_tier_2(self):
        s = State(1)
        self.assertFalse(s.stasis_shield_available())
        s.helmet_owned = True; s.helmet_equipped = True; s.helmet_generation = 1
        self.assertFalse(s.stasis_shield_available())
        s.helmet_generation = 2
        self.assertTrue(s.stasis_shield_available())
        self.assertTrue(HELMET_TIERS[2]['stasis_shield'])

    def test_stasis_success_blocks_pending_fatal_attack_without_damage(self):
        s = State(1)
        s.helmet_owned = True; s.helmet_equipped = True; s.helmet_generation = 2
        s.hp = 7
        s.battle = {'stasis_pending': {'name':'Execução Sísmica','seconds':5.0,'key':'F'}}
        result = s.resolve_stasis(True)
        self.assertTrue(result['success'])
        self.assertEqual(result['damage'], 0)
        self.assertEqual(s.hp, 7)
        self.assertFalse(s.battle.get('stasis_pending'))

    def test_stasis_failure_resolves_as_normal_death(self):
        s = State(1)
        s.helmet_owned = True; s.helmet_equipped = True; s.helmet_generation = 2
        s.respawn_tank_built = True
        s.inventory['Essência'] = 100
        s.battle = {'stasis_pending': {'name':'Execução Sísmica','seconds':5.0,'key':'F'}}
        result = s.resolve_stasis(False)
        self.assertFalse(result['success'])
        self.assertTrue(result['respawned'])
        self.assertEqual(s.inventory['Essência'], 90)
        self.assertTrue(s.inside_ship)

    def test_propulsion_repair_can_be_reopened_without_losing_sequence_cursor(self):
        s = State(1)
        ok, _ = s.start_ship_mission('ship_propulsion')
        self.assertTrue(ok)
        s.missions['ship_propulsion']['cursor'] = 2
        ok2, _ = s.start_ship_mission('ship_propulsion')
        self.assertTrue(ok2)
        self.assertEqual(s.missions['ship_propulsion']['cursor'], 2)

    def test_propulsion_mission_preserves_progress_in_save(self):
        s = State(1)
        s.start_ship_mission('ship_propulsion')
        s.missions['ship_propulsion']['cursor'] = 2
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            s.save(path, refresh=False)
            loaded, _ = State.load(path)
        self.assertEqual(loaded.missions['ship_propulsion']['cursor'], 2)

    def test_all_known_ship_missions_emit_acquisition_alert_once(self):
        s = State(1)
        for mid in ('ship_hull','ship_power','ship_propulsion','ship_navigation','ship_comms','ship_ftl'):
            s.missions[mid]['status'] = 'available'
            s.start_ship_mission(mid)
        mids = [a.get('mid') for a in s.achievement_alerts if a.get('type') == 'mission_started']
        self.assertEqual(set(mids), {'ship_hull','ship_power','ship_propulsion','ship_navigation','ship_comms','ship_ftl'})

if __name__ == '__main__':
    unittest.main()
