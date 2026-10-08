import unittest
from pathlib import Path

from content import CARDS, CARD_RARITIES, BOSS_ARENAS, BOSSES
from core import State
from world import SECTORS


class Version059HotfixTests(unittest.TestCase):
    def flight_ready(self, state):
        for sid in state.ship_systems:
            state.ship_systems[sid] = 100

    def unlock_nahr_language(self, state):
        state.helmet_owned = True
        state.helmet_equipped = True
        state.helmet_generation = 1
        for sid, sector, pos in (
            ('nahr_culture_01', 'nahr_landing', (12, 7)),
            ('nahr_culture_02', 'nahr_basalt_gardens', (6, 6)),
            ('nahr_culture_03', 'nahr_salt_wastes', (7, 6)),
        ):
            state.sector = sector
            state.pos = list(pos)
            ok, msg, _ = state.analyze_nahr_culture()
            self.assertTrue(ok, msg)
        self.assertTrue(state.nahr_language_mastered)

    def prepare_ry_ready(self, state):
        self.flight_ready(state)
        state.has_left_veyra = True
        state.refresh_journal()
        state.statistics['bosses_defeated'].update({'kuvaar': 1, 'kael': 1, 'ounull': 1, 'fagor': 1})
        state.refresh_journal()
        self.unlock_nahr_language(state)
        state.sector = 'nahr_basalt_gardens'
        state.pos = [13, 10]
        npc = state.area['settlement']['npcs'][0]
        text, _ = state.interact_npc(npc)
        self.assertIn('história de RY', text)
        self.assertTrue(state.boss_available('ry'))

    def equip(self, state, cid):
        inst = f'{cid}|normal|1'
        state.crafted.append(inst)
        state.known_cards.append(cid)
        state.slots[0] = inst
        return inst

    def test_nahr_root_chasm_has_local_fauna_but_ry_void_is_empty(self):
        self.assertGreater(len(SECTORS['nahr_root_chasm']['spawns']), 0)
        self.assertEqual(SECTORS['nahr_ry_void']['spawns'], [])
        self.assertEqual(BOSS_ARENAS['nahr'], 'nahr_ry_void')

    def test_mission_skips_nahr_conversation_when_contact_happened_before_fourth_boss(self):
        s = State(590)
        self.flight_ready(s)
        s.refresh_journal()
        self.unlock_nahr_language(s)
        s.has_left_veyra = True
        s.nahr_ry_contacted = True
        s.statistics['bosses_defeated'].update({'kuvaar': 1, 'kael': 1, 'ounull': 1})
        s.refresh_journal()
        self.assertEqual(s.missions['ry_investigation']['stage'], 'bosses')
        s.statistics['bosses_defeated']['fagor'] = 1
        self.assertTrue(s.refresh_journal())
        mission = s.missions['ry_investigation']
        self.assertEqual(mission['stage'], 'boss_ready')
        self.assertEqual(mission['status'], 'completed')
        self.assertTrue(s.boss_available('ry'))

    def test_ry_special_drop_only_real_battle(self):
        s = State(591)
        self.prepare_ry_ready(s)
        s.start_boss_battle('ry')
        s.battle['hp'] = 0
        s.rng.random = lambda: 0.99
        loot = s.win()
        self.assertEqual(loot.get('Núcleo de Dobra'), 1)
        self.assertEqual(s.inventory.get('Núcleo de Dobra'), 1)

        # A simulation against an already defeated RY never awards the unique real-only drop.
        s.simulator_built = True
        s.inventory['Carga de Simulação'] = 1
        self.assertTrue(s.start_boss_battle('ry', virtual=True)[0])
        s.battle['hp'] = 0
        loot = s.win()
        self.assertNotIn('Núcleo de Dobra', loot)
        self.assertEqual(s.inventory.get('Núcleo de Dobra'), 1)

    def test_all_collectible_cards_have_exact_single_rarity_buff_and_no_defense(self):
        expected = {
            'Comum': {'attack_pct': 3.0, 'crit_rate': 3.0, 'crit_damage': 0.05},
            'Incomum': {'attack_pct': 5.0, 'crit_rate': 5.0, 'crit_damage': 0.10},
            'Rara': {'attack_pct': 10.0, 'crit_rate': 10.0, 'crit_damage': 0.20},
            'Mítica': {'attack_pct': 15.0, 'crit_rate': 15.0, 'crit_damage': 0.25},
            'Lendária': {'attack_pct': 20.0, 'crit_rate': 20.0, 'crit_damage': 0.40},
        }
        for cid, card in CARDS.items():
            self.assertNotIn('defense', card.get('attributes', {}), cid)
            if card.get('enemy_only'):
                continue
            self.assertIn(card['rarity'], expected, cid)
            attrs = card.get('attributes', {})
            self.assertEqual(len(attrs), 1, cid)
            key = next(iter(attrs))
            self.assertIn(key, expected[card['rarity']], cid)
            self.assertEqual(attrs[key], expected[card['rarity']][key], cid)

    def test_requested_card_values_and_effects(self):
        expected = {
            'basalt_charge': (0.3, (12,15), 'attack_pct', 3.0),
            'shell': (0.4, (7,10), 'attack_pct', 3.0),
            'crystal_ram': (0.25, (11,15), 'crit_damage', 0.05),
            'hound': (0.4, (7,10), 'crit_rate', 3.0),
            'manta': (0.35, (9,12), 'crit_damage', 0.05),
            'bite': (0.7, (6,8), 'attack_pct', 3.0),
            'burrow': (0.4, (8,11), 'crit_damage', 0.05),
            'salt_spit': (0.5, (11,15), 'attack_pct', 5.0),
            'kuvaar': (0.65, (14,17), 'attack_pct', 10.0),
            'rift_break': (0.75, (20,22), 'attack_pct', 15.0),
            'lithic_sentence': (0.75, (20,22), 'attack_pct', 15.0),
            'guard_strike': (0.4, (8,11), 'attack_pct', 3.0),
            'static': (0.45, (10,13), 'crit_damage', 0.10),
            'forge_claw': (0.35, (9,12), 'attack_pct', 5.0),
            'magma_lance': (0.45, (9,12), 'attack_pct', 3.0),
            'fagor': (0.70, (15,22), 'attack_pct', 10.0),
            'frost_bite': (0.40, (9,13), 'crit_damage', 0.05),
            'glacial_gust': (0.50, (10,14), 'attack_pct', 5.0),
            'ounull': (0.55, (12,16), 'attack_pct', 10.0),
            'ion_burst': (0.50, (11,14), 'attack_pct', 3.0),
            'spore_burst': (0.45, (10,14), 'attack_pct', 3.0),
            'root_spear': (0.60, (10,13), 'crit_damage', 0.10),
            'kael': (0.50, (8,11), 'crit_damage', 0.20),
            'luminous_ray': (0.45, (11,14), 'attack_pct', 3.0),
            'stalker': (0.50, (10,13), 'attack_pct', 5.0),
            'ry': (0.90, (30,40), 'attack_pct', 20.0),
            'umbra_claw': (0.50, (12,16), 'crit_damage', 0.10),
        }
        for cid, (amp, damage, attr, value) in expected.items():
            card = CARDS[cid]
            self.assertEqual(card['skill_amp'], amp, cid)
            self.assertEqual(tuple(card['damage']), damage, cid)
            self.assertEqual(card['attributes'][attr], value, cid)
        self.assertEqual(CARDS['shell']['shield_pct'], 50.0)
        self.assertEqual(CARDS['bite']['attack_crit_rate_bonus'], 25.0)
        self.assertEqual(CARDS['crystal_ram']['attack_crit_damage_bonus'], 0.05)
        self.assertEqual(CARDS['burrow']['attack_crit_damage_bonus'], 0.20)
        self.assertEqual(CARDS['manta']['next_attack_type_damage_bonus'], 10.0)
        self.assertEqual(CARDS['hound']['combat_min_damage_bonus'], 1)
        self.assertEqual(CARDS['static']['combat_precision_bonus'], 1)
        self.assertEqual(CARDS['guard_strike']['shield_ratio'], 0.20)
        self.assertEqual(CARDS['salt_spit']['defense_reduction_pct'], 5.0)
        self.assertTrue(CARDS['kuvaar']['ignore_enemy_shield'])
        self.assertEqual(CARDS['lithic_sentence']['next_attack_crit_rate_bonus'], 100.0)
        self.assertEqual(CARDS['rift_break']['attack_crit_damage_bonus'], 0.50)
        self.assertEqual(CARDS['forge_claw']['attack_reduction_pct'], 10.0)
        self.assertEqual(CARDS['spore_burst']['next_attack_type'], 'Planta')
        self.assertIn('Auxílio Iluminado - ', CARDS['ry']['description'])

    def test_crit_labels_are_explicit_in_game_ui(self):
        source_main = Path(__file__).with_name('main.py').read_text(encoding='utf8')
        source_core = Path(__file__).with_name('core.py').read_text(encoding='utf8')
        self.assertNotRegex(source_main, r'\bCRIT\b|\bDCRIT\b')
        self.assertNotRegex(source_core, r'\bCRIT\b|\bDCRIT\b')

    def test_fulgor_and_new_legendary_rule_are_unchanged(self):
        card = CARDS['ry']
        self.assertEqual(card['rarity'], 'Lendária')
        self.assertEqual(card['attributes'], {'attack_pct': 20.0})
        self.assertEqual(card['attack_bonus_flat_temp'], 1)
        self.assertEqual(card['legendary_ability_id'], 'auxilio_iluminado')


if __name__ == '__main__':
    unittest.main()
