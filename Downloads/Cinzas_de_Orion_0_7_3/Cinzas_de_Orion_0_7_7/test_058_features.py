import json
import tempfile
import unittest
from pathlib import Path

from content import BOSSES, CARDS, BOSS_ARENAS, CARD_RARITIES, NAHR_CIVILIZATION, FACTIONS
from core import State
from world import SECTORS


class FixedRng:
    def __init__(self, random_value=0.0, randint_value=35):
        self.random_value = random_value
        self.randint_value = randint_value
    def random(self):
        return self.random_value
    def randint(self, a, b):
        return max(a, min(self.randint_value, b))
    def choice(self, seq):
        return seq[0]


class Version058RYTests(unittest.TestCase):
    def flight_ready(self, state):
        for sid in state.ship_systems:
            state.ship_systems[sid] = 100

    def unlock_nahr_language(self, state):
        state.helmet_owned = True
        state.helmet_equipped = True
        state.helmet_generation = 1
        state.sector = 'nahr_landing'
        state.pos = [12, 7]
        self.assertEqual(state.nahr_language_progress, 0)
        for sid, pos in (('nahr_culture_01', (12, 7)), ('nahr_culture_02', (6, 6)), ('nahr_culture_03', (7, 6))):
            state.sector = {'nahr_culture_01': 'nahr_landing', 'nahr_culture_02': 'nahr_basalt_gardens', 'nahr_culture_03': 'nahr_salt_wastes'}[sid]
            state.pos = list(pos)
            ok, _msg, _changed = state.analyze_nahr_culture()
            self.assertTrue(ok, sid)
        self.assertTrue(state.nahr_language_mastered)

    def prepare_ry_ready(self, state):
        self.flight_ready(state)
        state.has_left_veyra = True
        state.refresh_journal()
        state.statistics['bosses_defeated'].update({'kuvaar': 1, 'kael': 1, 'ounull': 1, 'fagor': 1})
        state.refresh_journal()
        self.assertEqual(state.missions['ry_investigation']['stage'], 'history')
        self.unlock_nahr_language(state)
        state.sector = 'nahr_basalt_gardens'
        state.pos = [5, 6]
        npc = state.area['settlement']['npcs'][0]
        text, _changed = state.interact_npc(npc)
        self.assertIn('história de RY', text)
        self.assertEqual(state.missions['ry_investigation']['stage'], 'boss_ready')
        self.assertTrue(state.boss_available('ry'))

    def equip(self, state, cid, idx=0):
        instance = f'{cid}|normal|1'
        if instance not in state.crafted:
            state.crafted.append(instance)
        if cid not in state.known_cards:
            state.known_cards.append(cid)
        state.slots[idx] = instance
        return instance

    def test_nahr_reserved_boss_arena_is_empty_and_routes_point_to_it(self):
        self.assertEqual(BOSS_ARENAS['nahr'], 'nahr_ry_void')
        arena = SECTORS['nahr_ry_void']
        self.assertTrue(arena['boss_arena'])
        self.assertEqual(arena['spawns'], [])
        self.assertEqual(arena['nodes'], [])
        self.assertEqual(arena['rocks'], set())
        for sid in ('nahr_landing', 'nahr_basalt_gardens', 'nahr_salt_wastes', 'nahr_root_chasm'):
            self.assertTrue(any(lm.get('boss_route_marker') == 'ry' for lm in SECTORS[sid]['landmarks']))

    def test_nahr_civilization_is_shadow_people(self):
        self.assertEqual(NAHR_CIVILIZATION['id'], 'nahr_shadows')
        self.assertIn('sombras', NAHR_CIVILIZATION['culture'].lower())
        self.assertIn('flutu', NAHR_CIVILIZATION['visual'].lower())
        self.assertIn('nahr_shadows', FACTIONS)
        self.assertEqual(SECTORS['nahr_basalt_gardens']['settlement']['civilization'], 'nahr_shadows')
        self.assertEqual(SECTORS['nahr_basalt_gardens']['settlement']['language'], 'Nahrim')

    def test_ry_mission_starts_with_interplanetary_flight_and_four_flags(self):
        s = State(580)
        self.flight_ready(s)
        s.has_left_veyra = True
        changed = s.refresh_journal()
        self.assertTrue(changed)
        mission = s.missions['ry_investigation']
        self.assertEqual(mission['status'], 'active')
        self.assertEqual(mission['stage'], 'bosses')
        self.assertEqual(s.ry_mission_title(), 'Investigue Vazio de RY')
        self.assertEqual(mission['flags'], {'kuvaar': False, 'kael': False, 'ounull': False, 'fagor': False})
        self.assertIn('ry_investigation_unlock', s.journal['seen'])

    def test_ry_mission_updates_to_history_after_all_four_bosses(self):
        s = State(581)
        self.flight_ready(s)
        s.has_left_veyra = True
        s.refresh_journal()
        s.statistics['bosses_defeated'].update({'kuvaar': 1, 'kael': 1, 'ounull': 1, 'fagor': 1})
        self.assertTrue(s.refresh_journal())
        m = s.missions['ry_investigation']
        self.assertEqual(m['progress'], 4)
        self.assertEqual(m['stage'], 'history')
        self.assertEqual(s.ry_mission_title(), 'Investigue a história do Vazio de RY')
        for bid in ('kuvaar', 'kael', 'ounull', 'fagor'):
            self.assertTrue(m['flags'][bid])
        self.assertFalse(s.boss_available('ry'))

    def test_nahr_language_requires_tier1_helmet_and_three_cultural_sources(self):
        s = State(582)
        s.known_planets.append('nahr')
        s.sector = 'nahr_landing'
        s.pos = [5, 6]
        ok, msg, _ = s.analyze_nahr_culture()
        self.assertFalse(ok)
        self.assertIn('Tier 1', msg)
        self.unlock_nahr_language(s)
        self.assertIn('nahr_shadows', s.known_civilizations_by_planet['nahr'])

    def test_nahr_people_explain_ry_and_post_victory_celebrate(self):
        s = State(583)
        self.flight_ready(s)
        s.has_left_veyra = True
        s.refresh_journal()
        self.unlock_nahr_language(s)
        s.sector = 'nahr_basalt_gardens'
        s.pos = [13, 10]
        npc = s.area['settlement']['npcs'][0]
        text, _ = s.interact_npc(npc)
        self.assertIn('personificação da morte', text)
        self.assertIn('bicho-papão', text)
        s.bosses['ry']['defeated'] = True
        text, _ = s.interact_npc(npc)
        self.assertIn('O mal que habitava o vazio foi destruído', text)
        self.assertIn('nossas vidas em paz', text)

    def test_ry_has_legendary_light_card_and_basic_special(self):
        boss = BOSSES['ry']
        card = CARDS['ry']
        self.assertEqual(boss['type'], 'Luz')
        self.assertEqual(boss['name'], 'RY')
        self.assertTrue(boss['legendary'])
        self.assertEqual(tuple(boss['special_attack']), tuple(card['damage']))
        self.assertEqual(boss['special_attack_card'], 'ry')
        self.assertEqual(tuple(boss['basic_attack']), tuple(boss['attack']))
        self.assertEqual(card['name'], 'Fulgor de RY')
        self.assertEqual(card['rarity'], 'Lendária')
        self.assertIn('Auxílio Iluminado - ', card['description'])
        self.assertEqual(card['legendary_ability_id'], 'auxilio_iluminado')
        self.assertEqual(card['attack_bonus_flat_temp'], 1)

    def test_ry_cannot_be_fought_until_history_is_investigated(self):
        s = State(584)
        ok, msg = s.start_boss_battle('ry')
        self.assertFalse(ok)
        self.assertIn('Vazio de RY', msg)
        self.prepare_ry_ready(s)
        ok, msg = s.start_boss_battle('ry')
        self.assertTrue(ok, msg)
        self.assertEqual(s.battle['hp'], BOSSES['ry']['hp'])
        self.assertEqual(s.battle['hp'], BOSSES['ry']['hp'])
        self.assertEqual(s.battle['mana_max'], 24)

    def test_fulgor_adds_cumulative_plus_one_attack(self):
        s = State(585)
        self.prepare_ry_ready(s)
        s.rng = FixedRng(0.99, 30)  # garante acerto e evita crítico pelos 9% efetivos do Fulgor
        inst = self.equip(s, 'ry')
        self.assertTrue(s.start_boss_battle('ry')[0])
        s.memory = 20
        base_atk = s.player_attributes()['attack']
        first = s.action(inst, 'light_core')
        self.assertTrue(first['ok'])
        self.assertEqual(s.player_attributes()['attack'], base_atk + 1)
        second = s.action(inst, 'light_core')
        self.assertTrue(second['ok'])
        self.assertEqual(s.player_attributes()['attack'], base_atk + 2)
        self.assertEqual(s.battle['player_attack_bonus_flat'], 2.0)

    def test_auxilio_iluminado_activates_when_memory_reaches_zero(self):
        s = State(586)
        self.prepare_ry_ready(s)
        inst = self.equip(s, 'ry')
        self.assertTrue(s.start_boss_battle('ry')[0])
        s.rng = FixedRng(0.99, 35)
        s.memory = CARDS['ry']['cost']
        hp_before = s.hp
        result = s.action(inst, 'light_core')
        self.assertTrue(result['ok'])
        self.assertTrue(result.get('legendary_ability', False))
        self.assertEqual(s.hp, hp_before - 1)
        self.assertEqual(s.memory, int(round(s.max_memory * 0.50)))
        self.assertIn('Auxílio Iluminado', result['message'])

    def test_ry_reacts_to_all_six_defined_attack_types(self):
        cases = [
            ('fagor', 'Fogo', 'player_burn_turns', 3),
            ('ounull', 'Água', 'player_drowning_pending', True),
            ('kuvaar', 'Terra', 'boss_reactive_shield', 160),
            ('forge_claw', 'Metal', 'ry_next_attack_critical', True),
            ('root_spear', 'Planta', None, None),
            ('ion_burst', 'Elétrico', 'ry_next_attack_bonus_pct', 50.0),
        ]
        for idx, (cid, typ, key, expected) in enumerate(cases, start=587):
            s = State(idx)
            self.prepare_ry_ready(s)
            s.crafted = []
            s.known_cards = []
            inst = self.equip(s, cid)
            self.assertEqual(CARDS[cid]['type'], typ)
            self.assertTrue(s.start_boss_battle('ry')[0])
            s.rng = FixedRng(0.99, 35)
            s.battle['hp'] = 1300
            result = s.action(inst, 'light_core')
            self.assertTrue(result['ok'])
            if key:
                self.assertEqual(s.battle[key], expected, (cid, result))
            elif typ == 'Planta':
                self.assertGreater(result['boss_heal'], 0, (cid, result))

    def test_ry_victory_grants_signature_drop_and_unlocks_card_recipe_and_nahr_renown(self):
        s = State(588)
        self.prepare_ry_ready(s)
        self.assertTrue(s.start_boss_battle('ry')[0])
        s.rng = FixedRng(0.0, 1)
        s.battle['hp'] = 0
        loot = s.win()
        self.assertTrue(s.bosses['ry']['defeated'])
        self.assertGreaterEqual(s.inventory.get('Núcleo de RY', 0), 1)
        self.assertNotIn('Carta: Fulgor de RY', loot)
        self.assertNotIn('ry|normal|1', s.crafted)
        self.assertIn('ry', s.known_cards)
        self.assertTrue(CARDS['ry'].get('recipe'))
        self.assertTrue(CARDS['ry'].get('craftable'))
        self.assertEqual(s.renown_by_faction['nahr_shadows'], 100)
        self.assertEqual(s.renown_planets['nahr'], 100)
        self.assertIn('ry_defeated', s.journal['seen'])

    def test_058_save_roundtrip_preserves_nahr_progress_and_version(self):
        s = State(589)
        s.nahr_language_progress = 2
        s.nahr_language_mastered = False
        s.nahr_ry_contacted = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            s.save(path, refresh=False)
            data = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(data['version'], 65)
            loaded, msg = State.load(path)
        self.assertFalse(loaded.save_blocked)
        self.assertEqual(loaded.nahr_language_progress, 2)
        self.assertFalse(loaded.nahr_language_mastered)
        self.assertTrue(loaded.nahr_ry_contacted)
        self.assertIn('0.6.9', msg)


if __name__ == '__main__':
    unittest.main()
