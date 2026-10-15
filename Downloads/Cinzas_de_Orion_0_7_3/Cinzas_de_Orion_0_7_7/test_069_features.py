import json
import tempfile
import unittest
from pathlib import Path

from content import VERSION, DOMAIN_ELEMENTS, DOMAIN_LEVEL_XP, DOMAIN_BONUSES
from core import State


class Version069DomainTests(unittest.TestCase):
    def test_version_and_domain_catalog(self):
        self.assertEqual(VERSION, '0.7.0')
        self.assertEqual(DOMAIN_ELEMENTS, ('Água','Elétrico','Fogo','Luz','Metal','Planta','Terra','Trevas'))
        self.assertEqual(len(DOMAIN_LEVEL_XP), 40)
        self.assertEqual(DOMAIN_LEVEL_XP[1], 2000)
        self.assertGreater(DOMAIN_LEVEL_XP[40], DOMAIN_LEVEL_XP[30] * 10)
        self.assertTrue(all(DOMAIN_LEVEL_XP[i] < DOMAIN_LEVEL_XP[i+1] for i in range(1,40)))

    def test_table_matches_requested_cycle(self):
        expected = {
            'Fogo': ['Dano Mínimo +1','Ataque +3%','Dano Crítico +5%','Dano Recebido -1%','Dano Crítico +5%','Dano Mínimo +1','Ataque +3%','Dano Crítico +5%','Dano Recebido -1%','AMP +1%'],
            'Água': ['Dano Recebido -1%','Taxa Crítica +2%','Defesa +3%','Ataque +3%','Dano Crítico +5%','Dano Recebido -1%','Taxa Crítica +2%','Defesa +3%','Ataque +3%','AMP +1%'],
            'Planta': ['Dano Recebido -1%','Defesa +3%','Ataque +3%','Dano Crítico +5%','Dano Crítico +5%','Dano Recebido -1%','Defesa +3%','Ataque +3%','Dano Crítico +5%','AMP +1%'],
            'Terra': ['Dano Recebido -1%','Defesa +3%','Ataque +3%','Dano Crítico +5%','Dano Crítico +5%','Dano Recebido -1%','Defesa +3%','Ataque +3%','Dano Crítico +5%','AMP +1%'],
            'Metal': ['Dano Recebido -1%','Dano Crítico +5%','Taxa Crítica +2%','Ataque +3%','Dano Crítico +5%','Dano Recebido -1%','Dano Crítico +5%','Taxa Crítica +2%','Ataque +3%','AMP +1%'],
            'Elétrico': ['Dano Mínimo +1','Ataque +3%','Defesa +3%','Dano Recebido -1%','Dano Crítico +5%','Dano Mínimo +1','Ataque +3%','Defesa +3%','Dano Recebido -1%','AMP +1%'],
            'Luz': ['Dano Mínimo +1','Dano Crítico +5%','Taxa Crítica +2%','Dano Recebido -1%','Dano Crítico +5%','Dano Mínimo +1','Dano Crítico +5%','Taxa Crítica +2%','Dano Recebido -1%','AMP +1%'],
            'Trevas': ['Dano Mínimo +1','Taxa Crítica +2%','Dano Crítico +5%','Dano Recebido -1%','Dano Crítico +5%','Dano Mínimo +1','Taxa Crítica +2%','Dano Crítico +5%','Dano Recebido -1%','AMP +1%'],
        }
        for element, names in expected.items():
            self.assertEqual([DOMAIN_BONUSES[element][i]['name'] for i in range(1,11)], names)
            for i in range(1,41):
                self.assertEqual(DOMAIN_BONUSES[element][i]['name'], DOMAIN_BONUSES[element][((i-1)%10)+1]['name'])

    def test_domain_xp_and_levels_are_independent(self):
        s = State(seed=1)
        self.assertEqual(s.gain_domain_xp('Fogo', 1999), 0)
        self.assertEqual(s.domain_levels['Fogo'], 0)
        self.assertEqual(s.gain_domain_xp('Fogo', 1), 1)
        self.assertEqual(s.domain_levels['Fogo'], 1)
        self.assertEqual(s.domain_xp['Água'], 0)
        self.assertEqual(s.domain_xp['Fogo'], 2000)

    def test_creature_rarity_grants_correct_domain_xp_including_virtual(self):
        s = State(seed=2)
        self.assertEqual(s._domain_xp_for_creature('scarab'), 20)
        self.assertEqual(s._domain_xp_for_creature('stalker'), 40)
        self.assertEqual(s._domain_xp_for_creature('kuvaar'), 100)
        self.assertEqual(s._domain_xp_for_creature('ry'), 500)
        s.start_battle(0)
        s.battle['hp'] = 1
        result = s.action('basic', 'body')
        self.assertTrue(result['win'])
        s.win()
        self.assertEqual(s.domain_xp['Terra'], 20)
        s.domain_xp['Luz'] = 0
        self.assertEqual(s._award_domain_for_defeat('ry', virtual=True), 500)
        self.assertEqual(s.domain_xp['Luz'], 500)

    def test_player_damage_cannot_exceed_twice_enemy_max_hp_per_event(self):
        s = State(seed=7)
        s.start_battle(0)
        self.assertEqual(s.battle['species'], 'scarab')
        s.battle['hp'] = 2
        # Escaravelho tem 90 HP máximos; o dano de um único evento fica limitado a 180.
        self.assertEqual(s._enemy_damage_cap(10_000, s.battle), 180)
        self.assertEqual(s._enemy_damage_cap(40, s.battle), 40)

    def test_player_attack_uses_damage_cap_for_nexus_xp(self):
        class FixedRng:
            def random(self):
                return 0.5
            def randint(self, a, b):
                return b

        s = State(seed=8)
        s.rng = FixedRng()
        s.gauntlet_nexus_installed = True
        s.combat_stats['attack'] = 1000
        s.combat_stats['crit_rate'] = 0
        s.start_battle(0)
        s.battle['hp'] = 2
        result = s.action('basic', 'body')
        self.assertTrue(result['win'])
        self.assertEqual(result['damage'], 180)
        self.assertEqual(result['nexus_xp_gained'], 180)
        self.assertTrue(result['damage_cap_applied'])

    def test_offensive_domain_applies_only_to_matching_card_element(self):
        s = State(seed=3)
        fire = 'magma_lance|normal|1'
        light = 'luminous_ray|normal|2'
        s.crafted = [fire, light]
        s.slots = [fire, light, None]
        base_fire = s._player_attack_profile(fire)[4]
        s.domain_levels['Fogo'] = 0
        no_domain = s._player_attack_profile(fire)[4]
        self.assertEqual(base_fire, no_domain)
        s.domain_levels['Fogo'] = 2
        with_domain = s._player_attack_profile(fire)[4]
        self.assertAlmostEqual(with_domain, no_domain * 1.03, places=2)
        light_with_fire_domain = s._player_attack_profile(light)[4]
        self.assertAlmostEqual(light_with_fire_domain, s.player_attributes()['attack'], places=2)

    def test_defensive_domain_applies_only_to_matching_element_attack(self):
        class FixedRng:
            def random(self): return 0.5
            def randint(self, a, b): return int((a + b) / 2)
        s = State(seed=5)
        s.rng = FixedRng()
        s.combat_stats['defense'] = 20
        s.start_battle(0)
        # Troca o encontro por uma criatura Água sem alterar a lógica do combate.
        from content import SPECIES
        spec = SPECIES['frost_wolf']
        s.battle.update(species='frost_wolf', hp=spec['hp'], targets=[{'id': tid, 'name': data['name'], 'available': True} for tid, data in spec['target_zones'].items()], target='body', mana=0, mana_max=0, boss=False, virtual=False)
        s.domain_levels['Água'] = 3
        result = s.enemy_turn()
        self.assertEqual(result['attack_type'], 'Água')
        self.assertEqual(result['target_defense'], 21)
        s2 = State(seed=5)
        s2.rng = FixedRng()
        s2.combat_stats['defense'] = 20
        s2.start_battle(0)
        s2.battle.update(species='frost_wolf', hp=spec['hp'], targets=[{'id': tid, 'name': data['name'], 'available': True} for tid, data in spec['target_zones'].items()], target='body', mana=0, mana_max=0, boss=False, virtual=False)
        s2.domain_levels['Água'] = 0
        result2 = s2.enemy_turn()
        self.assertEqual(result2['target_defense'], 20)
        self.assertLessEqual(result['damage'], result2['damage'])

    def test_save_roundtrip_persists_domains(self):
        s = State(seed=4)
        s.gain_domain_xp('Trevas', DOMAIN_LEVEL_XP[3] + 123)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'save.json'
            s.save(path)
            raw = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(raw['version'], 70)
            loaded, _ = State.load(path)
            self.assertEqual(loaded.domain_xp['Trevas'], s.domain_xp['Trevas'])
            self.assertEqual(loaded.domain_levels['Trevas'], 3)
            self.assertEqual(set(loaded.domain_xp), set(DOMAIN_ELEMENTS))


if __name__ == '__main__':
    unittest.main()
