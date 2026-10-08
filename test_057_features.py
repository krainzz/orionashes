import unittest
from pathlib import Path

from content import BOSSES, CARDS, STELLAR_ROUTES, CARD_RARITIES, boss_achievement_id, boss_achievement_data, BOSS_ACHIEVEMENT_TIERS
from core import State
from world import SECTORS


class SequenceRng:
    def __init__(self, random_values=None, randint_value=None):
        self.random_values = list(random_values or [0.0])
        self.randint_value = randint_value
    def random(self):
        if len(self.random_values) > 1:
            return self.random_values.pop(0)
        return self.random_values[0]
    def randint(self, a, b):
        return a if self.randint_value is None else max(a, min(b, self.randint_value))


class Version057BossTests(unittest.TestCase):
    def test_new_bosses_have_correct_types_rarities_and_cards(self):
        self.assertEqual(BOSSES['fagor']['type'], 'Fogo')
        self.assertEqual(BOSSES['kael']['type'], 'Planta')
        self.assertEqual(BOSSES['ounull']['type'], 'Água')
        for bid in ('fagor', 'kael', 'ounull'):
            self.assertIn(bid, CARDS)
            self.assertEqual(CARDS[bid]['rarity'], 'Rara')
            self.assertEqual(CARDS[bid]['type'], BOSSES[bid]['type'])

    def test_fagor_has_two_leg_bars_and_core_unlocks_only_after_both_legs_fall(self):
        s = State(5701)
        ok, _ = s.start_boss_battle('fagor')
        self.assertTrue(ok)
        self.assertEqual(s.battle['zone_hp'], {'leg_left': 80, 'leg_right': 80, 'magma_core': 140})
        ids = [t['id'] for t in s.battle_targets()]
        self.assertNotIn('magma_core', ids)
        s.battle['zone_hp']['leg_left'] = 0
        self.assertNotIn('magma_core', [t['id'] for t in s.battle_targets()])
        s.battle['zone_hp']['leg_right'] = 0
        self.assertIn('magma_core', [t['id'] for t in s.battle_targets()])
        self.assertEqual(BOSSES['fagor']['target_zones']['magma_core']['damage_multiplier'], 1.80)

    def test_fagor_leg_damage_is_separate_from_main_hp(self):
        s = State(5702)
        s.rng = SequenceRng([0.0, 0.99, 0.99])
        s.start_boss_battle('fagor')
        before = s.battle['hp']
        result = s.action('basic', 'leg_left')
        self.assertTrue(result['ok'])
        self.assertGreater(result['damage'], 0)
        self.assertEqual(s.battle['hp'], before)
        self.assertLess(s.battle['zone_hp']['leg_left'], 80)

    def test_kael_crown_damage_scales_attack_until_exactly_one_at_zero(self):
        s = State(5703)
        s.rng = SequenceRng([0.99, 0.0, 0.99], randint_value=17)
        s.start_boss_battle('kael')
        full = s.enemy_turn()
        self.assertEqual(full['attack_base'], 17)

        s = State(5704)
        s.rng = SequenceRng([0.99, 0.0, 0.99], randint_value=17)
        s.start_boss_battle('kael')
        s.battle['zone_hp']['crown'] = 0
        weakened = s.enemy_turn()
        self.assertEqual(weakened['attack_base'], 1)

    def test_kael_card_uses_player_hp_for_damage_and_next_enemy_attack_reduction(self):
        s = State(5705)
        s.slots[0] = 'kael|normal|1'
        s.hp = 20
        s.rng = SequenceRng([0.0, 0.99, 0.99])
        s.start_boss_battle('kael')
        result = s.action('kael|normal|1', 'trunk')
        self.assertTrue(result['ok'])
        self.assertGreater(result['damage'], 0)
        self.assertEqual(s.battle['enemy_attack_reduction_flat'], 2)

    def test_ounull_has_drowning_special_and_memory_attack_recovery(self):
        self.assertEqual(BOSSES['ounull']['special_attack_card'], 'ounull_tide')
        self.assertEqual(CARDS['ounull_tide']['drowning_chance'], 100.0)
        s = State(5706)
        s.rng = SequenceRng([0.0, 0.0, 0.0, 0.0, 0.0])
        s.start_boss_battle('ounull')
        special = s.enemy_turn()
        self.assertTrue(special['special'])
        self.assertEqual(special['special_card'], 'ounull_tide')
        self.assertTrue(s.battle['player_drowning_pending'])

        s = State(5707)
        s.slots[0] = 'shell|normal|1'
        s.rng = SequenceRng([0.0, 0.99, 0.99])
        s.start_boss_battle('ounull')
        s.battle['hp'] = 250
        s.memory = 8
        s.battle['player_drowning_pending'] = True
        result = s.action('shell|normal|1', 'body')
        self.assertTrue(result['ok'])
        self.assertGreater(result['damage'], 0)
        self.assertGreater(result['boss_heal'], 0)
        self.assertEqual(result['memory_cost'], CARDS['shell']['cost'] * 2)

    def test_new_boss_maps_and_route_warnings_exist(self):
        self.assertTrue(SECTORS['orionis_thermal_caves']['boss_arena'])
        self.assertTrue(SECTORS['orionis_thermal_caves']['lava_style'])
        self.assertTrue(SECTORS['kael_frost_caverns']['boss_arena'])
        self.assertTrue(SECTORS['kael_frost_caverns']['forest_style'])
        self.assertTrue(SECTORS['elyra_cloud_caverns']['boss_arena'])
        self.assertTrue(SECTORS['elyra_cloud_caverns']['water_tiles'])
        self.assertTrue(SECTORS['elyra_cloud_caverns']['island_tiles'])
        for sector in ('orionis_landing', 'orionis_ember_fields', 'orionis_ferro_ravines',
                       'kael_landing', 'kael_crystal_pines', 'kael_glacial_plains',
                       'elyra_landing', 'elyra_luminous_marsh', 'elyra_umbral_grove'):
            self.assertTrue(any(l.get('boss_route_marker') for l in SECTORS[sector]['landmarks']), sector)

    def test_elyra_island_requires_locomotion_to_cross_water(self):
        s = State(5708)
        s.sector = 'elyra_cloud_caverns'
        s.pos = [7, 12]
        self.assertIn((8, 12), SECTORS['elyra_cloud_caverns']['water_tiles'])
        self.assertFalse(s.move(1, 0))
        s.locomotion_generation = 1
        self.assertTrue(s.move(1, 0))

    def test_elyra_boss_gate_does_not_require_locomotion(self):
        gate = next(g for g in SECTORS['elyra_umbral_grove']['exits'] if g.get('boss_id') == 'ounull')
        self.assertFalse(gate.get('requires_locomotion', False))
        s = State(5709)
        s.sector = 'elyra_umbral_grove'
        s.pos = list(gate['at'])
        ok, _ = s.use_nearby_exit()
        self.assertTrue(ok)
        self.assertEqual(s.sector, 'elyra_cloud_caverns')

    def test_card_effect_ui_uses_scrollable_text_box(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def _draw_scroll_text_box', source)
        self.assertIn("f'card_effect_{local_i}'", source)
        self.assertIn("f'craft_effect_{i}'", source)
        for key in ('card_effect_0', 'card_effect_1', 'card_effect_2', 'craft_effect_0'):
            self.assertIn(f"'{key}':", source)


class Version057Hotfix1Tests(unittest.TestCase):
    def test_kael_boss_is_displayed_as_trembe_without_changing_internal_id(self):
        self.assertEqual(BOSSES['kael']['name'], 'Trembe')
        self.assertEqual(CARDS['kael']['name'], 'Vigor de Trembe')

    def test_all_bosses_have_basic_and_special_attack_cards(self):
        for bid, boss in BOSSES.items():
            self.assertIn('basic_attack', boss)
            self.assertIn('special_attack', boss)
            self.assertTrue(boss.get('special_attack_card'))
            self.assertIn(boss['special_attack_card'], CARDS)
            self.assertEqual(tuple(boss['special_attack']), tuple(CARDS[boss['special_attack_card']]['damage']))

    def test_boss_arenas_have_no_creature_spawns(self):
        for sector_id, data in SECTORS.items():
            if data.get('boss_arena'):
                self.assertEqual(data.get('spawns', []), [], sector_id)

    def test_nahr_has_reserved_empty_boss_arena_for_future_ry(self):
        from content import BOSS_ARENAS
        self.assertEqual(BOSS_ARENAS.get('nahr'), 'nahr_ry_void')
        arena = SECTORS['nahr_ry_void']
        self.assertTrue(arena.get('boss_arena'))
        self.assertEqual(arena.get('spawns'), [])
        self.assertEqual(arena.get('nodes'), [])
        self.assertEqual(arena.get('rocks'), set())
        self.assertFalse(SECTORS['nahr_root_chasm'].get('boss_arena', False))

    def test_boss_achievement_chain_and_rewards(self):
        for bid in BOSSES:
            d1 = boss_achievement_data(bid, 1)
            d100 = boss_achievement_data(bid, 100)
            d1000 = boss_achievement_data(bid, 1000)
            self.assertEqual(d1['reward_type'], 'item')
            self.assertEqual(d1['reward_amount'], 5)
            self.assertEqual(d100['reward_variant'], 'normal')
            self.assertEqual(d1000['reward_variant'], 'plus')
            self.assertEqual(d1['category'], 'Combate')

    def test_new_boss_achievements_locked_until_interplanetary_flight(self):
        s = State(5710)
        s.refresh_achievements()
        for bid in ('fagor','kael','ounull'):
            self.assertNotIn(boss_achievement_id(bid,1), s.achievements)
        s.ship_systems = {sid:100 for sid in s.ship_systems}
        s.refresh_achievements()
        for bid in ('fagor','kael','ounull'):
            self.assertIn(boss_achievement_id(bid,1), s.achievements)
            self.assertFalse(s.achievements[boss_achievement_id(bid,1)]['unlocked'])

    def test_boss_achievement_100_and_1000_require_previous_and_virtual_defeats(self):
        s = State(5711)
        s.bosses['fagor']['virtual_defeats'] = 1000
        s.ship_systems = {sid:100 for sid in s.ship_systems}
        s.refresh_achievements()
        a1, a100, a1000 = [boss_achievement_id('fagor',n) for n in (1,100,1000)]
        self.assertFalse(s.achievements[a100]['unlocked'])
        self.assertFalse(s.achievements[a1000]['unlocked'])
        s.achievements[a1]['unlocked'] = True
        s.refresh_achievements()
        self.assertTrue(s.achievements[a100]['unlocked'])
        # Como o contador virtual já está em 1000, a etapa 1000 também pode
        # ser liberada nesta mesma atualização, pois a etapa 100 já foi concluída.
        self.assertTrue(s.achievements[a1000]['unlocked'])


    def test_simulator_only_exposes_defeated_bosses_and_core_gates_virtual_rematches(self):
        from content import BOSSES
        s = State(5713)
        s.simulator_built = True
        s.inventory['Carga de Simulação'] = 1
        ok, _ = s.start_boss_battle('fagor', virtual=True)
        self.assertFalse(ok)
        s.bosses['fagor']['defeated'] = True
        ok, _ = s.start_boss_battle('fagor', virtual=True)
        self.assertTrue(ok)
        self.assertEqual(s.battle['species'], 'fagor')
        self.assertEqual(s.bosses['fagor']['virtual_defeats'], 0)
        s.battle['hp'] = 0
        s.win()
        self.assertEqual(s.bosses['fagor']['virtual_defeats'], 1)
        for bid in BOSSES:
            self.assertIn('basic_attack', BOSSES[bid])
            self.assertTrue(BOSSES[bid].get('special_attack_card'))

    def test_boss_1x_reward_claims_signature_item(self):
        s = State(5712)
        s.ship_systems = {sid:100 for sid in s.ship_systems}
        s.bosses['fagor']['defeated'] = True
        s.statistics['bosses_defeated']['fagor'] = 1
        s.refresh_achievements()
        aid = boss_achievement_id('fagor',1)
        self.assertTrue(s.achievements[aid]['unlocked'])
        before = s.inventory.get('Núcleo Magmático',0)
        ok, _ = s.claim_achievement(aid)
        self.assertTrue(ok)
        self.assertEqual(s.inventory.get('Núcleo Magmático',0), before+5)

    def test_elyra_has_reachable_land_strip_before_water(self):
        data=SECTORS['elyra_cloud_caverns']
        self.assertTrue(data.get('land_strip'))
        for x in range(0,4):
            self.assertNotIn((x,12), data['water_tiles'])
        self.assertIn((4,12), data['water_tiles'])
        self.assertIn((13,12), data['island_tiles'])


if __name__ == '__main__':
    unittest.main()
