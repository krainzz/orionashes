import json
import tempfile
import unittest
from pathlib import Path

from content import CARDS, CARD_RARITIES, SPECIES, BOSSES, BOSS_ARENAS, STELLAR_ROUTES, CREATURE_MANA_PROFILES, GALAXIES, CREATURE_TYPES, TYPE_ADVANTAGES
from core import State
from world import SECTORS


class _Rng:
    """RNG determinístico para validar escolha de ataque especial."""
    def __init__(self, value=0.99, randint_value=4):
        self.value = value
        self.randint_value = randint_value
    def random(self):
        return self.value
    def randint(self, a, b):
        return max(a, min(self.randint_value, b))
    def choice(self, seq):
        return seq[0]


class Version053FeatureTests(unittest.TestCase):
    def test_all_species_have_basic_and_exact_card_special_with_mana_profile(self):
        for sid, spec in SPECIES.items():
            cid = spec['card']
            self.assertIn(cid, CARDS, sid)
            card = CARDS[cid]
            self.assertIn(card['rarity'], CREATURE_MANA_PROFILES)
            self.assertEqual(tuple(spec['basic_attack']), tuple(spec['attack']), sid)
            self.assertEqual(tuple(spec['special_attack']), tuple(card['damage']), sid)
            self.assertEqual(spec['special_attack_card'], cid, sid)
            self.assertGreaterEqual(spec['mana_max'], spec['mana_cost'] * 3, sid)
            self.assertLessEqual(spec['mana_max'], spec['mana_cost'] * 4 + (spec['mana_cost'] - 1), sid)
            self.assertIn(spec['special_chance'], (20.0, 40.0, 60.0), sid)
        for bid, boss in BOSSES.items():
            self.assertIn(boss['card'], CARDS, bid)
            special_card = CARDS[boss.get('special_attack_card', boss['card'])]
            self.assertEqual(tuple(boss['special_attack']), tuple(special_card['damage']), bid)
            self.assertGreater(boss['special_chance'], 0.0, bid)
            self.assertGreaterEqual(boss['mana_max'], boss['mana_cost'] * 3, bid)
            self.assertLessEqual(boss['mana_max'], 24 if bid != 'ry' else 24, bid)

    def test_mana_profiles_and_special_chances_match_rarity(self):
        for rarity, profile in CREATURE_MANA_PROFILES.items():
            self.assertEqual(profile['special_chance'], {'Comum': 20.0, 'Incomum': 40.0, 'Rara': 60.0}[rarity])
            self.assertGreaterEqual(profile['mana_max'] / profile['mana_cost'], 3.0)
        counts = {}
        for spec in SPECIES.values():
            rarity = CARDS[spec['card']]['rarity']
            counts[rarity] = counts.get(rarity, 0) + 1
        self.assertGreater(counts.get('Comum', 0), counts.get('Incomum', 0))

    def test_enemy_special_uses_mana_and_exact_card_values(self):
        s = State(101)
        s.start_battle(0)  # Escaravelho = Comum, 20%, custo 2.
        s.combat_stats['enemy_crit_rate_reduction'] = 100.0
        s.rng = _Rng(0.10, 4)  # escolhe especial e acerta; sem crítico pelo perfil reduzido.
        before = s.battle['mana']
        result = s.enemy_turn()
        self.assertTrue(result['special'])
        self.assertEqual(result['special_card'], SPECIES['scarab']['card'])
        self.assertEqual(result['mana'], before - SPECIES['scarab']['mana_cost'])
        self.assertEqual((result['skill_attack'], result['skill_attack']), (7, 7))
        self.assertEqual(result['special'], True)

    def test_enemy_returns_to_basic_after_mana_is_exhausted(self):
        s = State(102)
        s.start_battle(0)
        s.battle['mana'] = 1  # abaixo do custo 2 do especial.
        s.combat_stats['enemy_crit_rate_reduction'] = 100.0
        s.rng = _Rng(0.0, 4)
        result = s.enemy_turn()
        self.assertFalse(result['special'])
        self.assertIsNone(result['special_card'])
        self.assertEqual(s.battle['mana'], 1)

    def test_silica_charge_is_plus_one_minimum_damage_until_end_of_combat(self):
        self.assertEqual(CARDS['hound']['combat_min_damage_bonus'], 1)
        self.assertEqual(CARDS['hound']['attributes'].get('crit_rate', 0.0), 3.0)
        s = State(109)
        s.crafted = ['hound|normal|1']
        s.slots = ['hound|normal|1', None, None]
        s.start_battle(0)
        s.rng = _Rng(0.0, 4)
        first = s.action('hound')
        self.assertTrue(first['ok'])
        self.assertEqual(s.battle['player_min_damage_bonus_flat'], 1)
        second = s.action('hound')
        self.assertTrue(second['ok'])
        self.assertEqual(s.battle['player_min_damage_bonus_flat'], 1)

    def test_unknown_cards_are_filtered_from_album_and_workshop_source(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("cards=[(cid, card, 'regular') for cid, card in CARDS.items() if cid in self.state.known_cards]", source)
        self.assertIn("cards=[(cid,data) for cid,data in CARDS.items() if cid in self.state.known_cards and data.get('recipe') and data.get('craftable') is not False]", source)
        self.assertNotIn("cards=list(CARDS.items())", source)
        self.assertNotIn("entries = list(CARDS.items())", source)

    def test_defined_type_effects_only(self):
        # A identidade de efeito dos tipos já definidos é limitada ao que foi
        # estabelecido: Elétrico/Atordoamento, Água/Afogamento, Metal/redução
        # de ATQ, Terra/defesa e Fogo/DoT. Os demais tipos permanecem sem
        # efeito tático específico por enquanto.
        self.assertEqual(set(CREATURE_TYPES), {'Terra','Metal','Fogo','Água','Elétrico','Planta','Luz','Trevas'})
        self.assertEqual(TYPE_ADVANTAGES['Água'], 'Fogo')
        self.assertEqual(TYPE_ADVANTAGES['Fogo'], 'Planta')
        self.assertEqual(TYPE_ADVANTAGES['Planta'], 'Água')
        self.assertEqual(TYPE_ADVANTAGES['Elétrico'], 'Metal')
        self.assertEqual(TYPE_ADVANTAGES['Terra'], 'Elétrico')
        self.assertEqual(TYPE_ADVANTAGES['Metal'], 'Terra')
        self.assertEqual(TYPE_ADVANTAGES['Luz'], 'Trevas')
        self.assertEqual(TYPE_ADVANTAGES['Trevas'], 'Luz')

        self.assertEqual(CARDS['shell']['type'], 'Terra')
        self.assertEqual(CARDS['shell']['shield_pct'], 50.0)
        self.assertEqual(CARDS['static']['type'], 'Metal')
        self.assertEqual(CARDS['static']['combat_precision_bonus'], 1)
        self.assertEqual(CARDS['ion_burst']['type'], 'Elétrico')
        self.assertEqual(CARDS['ion_burst']['stun_chance'], 30.0)
        self.assertEqual(CARDS['ion_burst']['status_duration'], 1)
        self.assertEqual(CARDS['glacial_gust']['type'], 'Água')
        self.assertNotIn('drowning_chance', CARDS['glacial_gust'])
        self.assertEqual(CARDS['magma_lance']['type'], 'Fogo')
        self.assertEqual(CARDS['magma_lance']['burn_chance'], 30.0)
        self.assertEqual(CARDS['magma_lance']['burn_damage'], 2)
        self.assertEqual(CARDS['magma_lance']['burn_turns'], 2)
        for cid in ('burrow','stalker','root_spear','crystal_ram','umbra_claw'):
            for forbidden in ('defense_reduction_pct','defense_reduction_chance','precision_reduction','precision_reduction_chance','attack_reduction_pct','attack_reduction_chance'):
                self.assertNotIn(forbidden, CARDS[cid], f'{cid}: {forbidden}')
        for cid in CARDS:
            self.assertIn(CARDS[cid]['type'], CREATURE_TYPES, cid)
        for sid, spec in SPECIES.items():
            self.assertIn(spec['type'], CREATURE_TYPES, sid)
        for bid, boss in BOSSES.items():
            self.assertIn(boss['type'], CREATURE_TYPES, bid)

    def test_water_drowning_doubles_next_special_mana_without_damage(self):
        s = State(106)
        s.start_battle(0)
        # Simulate the player's Água card directly so the enemy receives Afogamento.
        b = s.battle
        b['enemy_drowning_pending'] = True
        b['mana'] = 6
        s.combat_stats['enemy_crit_rate_reduction'] = 100.0
        s.rng = _Rng(0.10, 4)
        hp_before = b['hp']
        result = s.enemy_turn()
        self.assertTrue(result['special'])
        self.assertEqual(result['mana_cost'], SPECIES['scarab']['mana_cost'] * 2)
        self.assertEqual(b['mana'], 6 - SPECIES['scarab']['mana_cost'] * 2)
        self.assertEqual(b['hp'], hp_before)
        self.assertFalse(b['enemy_drowning_pending'])

    def test_water_drowning_waits_until_special_is_used(self):
        s = State(107)
        s.start_battle(0)
        s.battle['enemy_drowning_pending'] = True
        s.battle['mana'] = 8
        s.combat_stats['enemy_crit_rate_reduction'] = 100.0
        # RNG makes the special fail its chance, so it uses basic and keeps Afogamento pending.
        s.rng = _Rng(0.99, 4)
        result = s.enemy_turn()
        self.assertFalse(result['special'])
        self.assertEqual(s.battle['mana'], 8)
        self.assertTrue(s.battle['enemy_drowning_pending'])

    def test_enemy_fire_burn_is_damage_over_time(self):
        s = State(108)
        s.start_battle(0)
        s.battle['species'] = 'salamander_igneous'
        s.battle['hp'] = SPECIES['salamander_igneous']['hp']
        s.battle['mana'] = SPECIES['salamander_igneous']['mana_max']
        # Force the creature to use the special and apply burn.
        class BurnRng(_Rng):
            def __init__(self):
                self.values = iter([0.10, 0.0, 0.99, 0.10])
                self.randint_value = 4
            def random(self):
                return next(self.values)
        s.combat_stats['enemy_crit_rate_reduction'] = 100.0
        s.rng = BurnRng()
        result = s.enemy_turn()
        self.assertTrue(result['special'])
        self.assertTrue(any('Queimadura' in n for n in result['status_notes']))
        self.assertEqual(s.battle['player_burn_turns'], 2)
        self.assertEqual(s.battle['player_burn_damage'], 2)
        hp_before = s.hp
        prep = s.prepare_player_turn()
        self.assertEqual(prep['damage'], 2)
        self.assertEqual(s.hp, hp_before - 2)

    def test_card_rarity_distribution_matches_053_rules(self):
        counts = {rarity: sum(1 for card in CARDS.values() if card.get('rarity') == rarity) for rarity in CARD_RARITIES}
        self.assertGreater(counts['Comum'], counts['Incomum'])
        self.assertEqual(counts['Rara'], 11)
        self.assertEqual(CARDS['kuvaar']['rarity'], 'Rara')
        self.assertEqual(CARDS['kuvaar']['species'], 'kuvaar')
        self.assertEqual(counts['Lendária'], 3)
        self.assertEqual(counts['Única'], 0)
        self.assertEqual(CARDS['ry']['rarity'], 'Lendária')
        self.assertEqual(CARDS['ry']['type'], 'Luz')
        for cid in ('lithic_sentence', 'rift_break'):
            self.assertEqual(CARDS[cid]['rarity'], 'Mítica')
        # As Míticas atuais estão ligadas ao conflito de facções, não à fauna comum.
        for cid, card in CARDS.items():
            if card.get('rarity') == 'Mítica':
                self.assertEqual(card.get('acquisition'), 'faction_conflict', cid)

    def test_bosses_are_scannable_for_hidden_mana_without_entering_fauna_catalog(self):
        s = State(103)
        self.assertNotIn('kuvaar', s.bestiary_known)
        self.assertNotIn('kuvaar', s.bestiary_scanned)
        s.helmet_owned = True
        s.helmet_equipped = True
        s.scan_unlocked = True
        self.assertTrue(s.register_bestiary_encounter('kuvaar'))
        self.assertIn('kuvaar', s.bestiary_scanned)
        self.assertNotIn('kuvaar', s.bestiary_known)
        ok, _ = s.start_boss_battle('kuvaar')
        self.assertTrue(ok)
        self.assertEqual(s.battle['mana_max'], BOSSES['kuvaar']['mana_max'])

    def test_boss_mana_is_not_visible_to_ui_before_scan(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        battle = source[source.index('    def battle_view(self):'):source.index('    def select_battle_target(self, target_id):')]
        self.assertIn("if boss and self.state.helmet_equipped and self.state.scan_unlocked:", battle)
        self.assertRegex(battle, r"(?:if|elif) scanned:\s+mana_now")
        # Não deve existir uma barra de mana sempre desenhada ao lado do HP.
        self.assertGreaterEqual(battle.count('self.bar('), 3)

    def test_inventory_details_and_renown_are_scrollable_and_aggregate_stats_stay_compact(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        inv = source[source.index('    def inventory(self):'):source.index('    def renown(self):')]
        self.assertIn("'inventory_details'", inv)
        self.assertIn("_register_scrollbar('inventory_details'", inv)
        renown = source[source.index('    def renown(self):'):source.index('    def claim_renown(self,scope,key,index):')]
        self.assertIn('visited_galaxy_ids()', renown)
        self.assertIn('galaxy_planet_ids(gid)', renown)
        self.assertIn("_register_scrollbar('renown'", renown)
        stats = source[source.index('    def statistics_view(self):'):source.index('    def bestiary(self):')]
        self.assertNotIn("SPECIES[k]['name']", stats)
        self.assertNotIn("SECTORS[sid]['name']", stats)
        self.assertNotIn('_mission_catalog()', stats)

    def test_renown_scales_across_visited_galaxies_and_planets(self):
        from content import STELLAR_ROUTES
        s = State(104)
        original = {route['id']: route.get('galaxy') for route in STELLAR_ROUTES}
        had_galaxy = 'test_future_galaxy' in GALAXIES
        old_galaxy = GALAXIES.get('test_future_galaxy')
        try:
            GALAXIES['test_future_galaxy'] = {'name': 'Galáxia Futura'}
            for route in STELLAR_ROUTES:
                if route['id'] == 'orionis':
                    route['galaxy'] = 'test_future_galaxy'
            s.visited.append('orionis_landing')
            self.assertIn('orionis', s.visited_planet_ids())
            self.assertIn('test_future_galaxy', s.visited_galaxy_ids())
            self.assertTrue(s.award_renown('waterkeepers', 40, 'teste', planet_id='orionis'))
            self.assertEqual(s.renown_planets['orionis'], 40)
            self.assertEqual(s.renown_galaxies['test_future_galaxy'], 40)
            self.assertIn('orionis', s.galaxy_planet_ids('test_future_galaxy'))
        finally:
            for route in STELLAR_ROUTES:
                if route['id'] in original:
                    route['galaxy'] = original[route['id']]
            if had_galaxy:
                GALAXIES['test_future_galaxy'] = old_galaxy
            else:
                GALAXIES.pop('test_future_galaxy', None)

    def test_boss_arenas_match_planets_with_bosses(self):
        expected = {'veyra', 'orionis', 'kael', 'nahr', 'elyra','dornak','nyxara','zereth','pyraxis','thalassene','mycelon','tethra','nerissa'}
        self.assertEqual(set(BOSS_ARENAS), expected)
        for planet_id, arena_id in BOSS_ARENAS.items():
            self.assertIn(arena_id, SECTORS)
            self.assertTrue(SECTORS[arena_id].get('boss_arena'), (planet_id, arena_id))

    def test_save_roundtrip_and_future_schema_remain_loadable(self):
        base = State(105)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            base.save(path, refresh=False)
            data = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(data['version'], 65)
            data['version'] = 999
            data['worlds'].pop('orionis_landing', None)
            data['known_cards'].append('carta_futura')
            data.setdefault('statistics', {}).setdefault('kills', {})['criatura_futura'] = 17
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            loaded, msg = State.load(path)
        self.assertFalse(loaded.save_blocked)
        self.assertIn('versão futura', msg)
        self.assertIn('orionis_landing', loaded.worlds)
        self.assertIn('carta_futura', loaded.known_cards)
        self.assertEqual(loaded.statistics['kills'].get('criatura_futura'), 17)

    def test_enemy_defeat_phase_switches_back_to_hero_before_victory(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = source[source.index('    def advance(self, dt):'):source.index('    def settlement_structure(self, kind, x, y):')]
        self.assertIn("self.result['win'] = True", block)
        self.assertIn("self.phase = 'hero'", block)


if __name__ == '__main__':
    unittest.main()
