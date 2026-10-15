import json
import tempfile
import unittest
from pathlib import Path

from content import (
    VERSION, CARD_RARITIES, CARDS, SPECIES, BOSSES, BOSS_ARENAS,
    GALAXIES, GALAXY_ROUTE_IDS, GALAXY_RARE_BOSSES, GALAXY_LEGENDARY_BOSSES,
    STELLAR_ROUTES, CIVILIZATIONS,
)
from core import State
from world import SECTORS


class _SequenceRng:
    def __init__(self, values, randint_value=10):
        self.values = list(values)
        self.randint_value = randint_value
    def random(self):
        return self.values.pop(0) if self.values else 0.0
    def randint(self, a, b):
        return max(a, min(self.randint_value, b))
    def choice(self, seq):
        return seq[0]


class Version060FeatureTests(unittest.TestCase):
    def test_version_has_two_new_galaxies_with_four_planets_each(self):
        self.assertEqual(VERSION, '0.6.9')
        self.assertIn('vharos', GALAXIES)
        self.assertIn('meridion', GALAXIES)
        self.assertEqual(len(GALAXY_ROUTE_IDS['vharos']), 4)
        self.assertEqual(len(GALAXY_ROUTE_IDS['meridion']), 4)
        self.assertEqual(set(GALAXY_RARE_BOSSES['vharos']) | {'alphor'},
                         {'mekron', 'nocther', 'voltrik', 'alphor'})
        self.assertEqual(set(GALAXY_RARE_BOSSES['meridion']) | {'broom'},
                         {'moryss', 'verdak', 'gravorn', 'broom'})
        for planet in GALAXY_ROUTE_IDS['vharos'] + GALAXY_ROUTE_IDS['meridion']:
            maps = [key for key in SECTORS if key == next(r['landing_sector'] for r in STELLAR_ROUTES if r['id'] == planet)
                    or key.startswith(planet + '_')]
            self.assertEqual(len(maps), 4, planet)
            self.assertTrue(SECTORS[maps[0]].get('ship') is not None)

    def test_dobra_core_is_installed_at_ship_and_unlocks_cross_galaxy_travel(self):
        s = State(600)
        for sid in s.ship_systems:
            s.ship_systems[sid] = 100
        s.ensure_exploration_mission()
        self.assertFalse(s.can_travel_to_planet('dornak')[0])
        s.inventory['Núcleo de Dobra'] = 1
        ok, msg = s.install_dobra_core()
        self.assertTrue(ok, msg)
        self.assertTrue(s.dobra_core_installed)
        self.assertEqual(s.inventory['Núcleo de Dobra'], 0)
        self.assertTrue(s.can_travel_to_planet('dornak')[0])
        self.assertTrue(s.can_travel_to_planet('thalassene')[0])
        self.assertEqual(s.selected_galaxy_id, 'vharos')

    def test_legendary_bosses_are_locked_until_all_three_galaxy_rare_bosses_are_defeated(self):
        s = State(601)
        s.dobra_core_installed = True
        self.assertFalse(s.boss_available('alphor'))
        self.assertFalse(s.boss_available('broom'))
        for bid in GALAXY_RARE_BOSSES['vharos']:
            s.bosses[bid]['defeated'] = True
        self.assertTrue(s.boss_available('alphor'))
        self.assertFalse(s.boss_available('broom'))
        for bid in GALAXY_RARE_BOSSES['meridion']:
            s.bosses[bid]['defeated'] = True
        self.assertTrue(s.boss_available('broom'))

    def test_new_fauna_follow_the_existing_two_attack_mana_contract(self):
        new_species = {
            'ferrous_mite','magnetic_ram','gloom_moth','vesper_cat','charge_ray','ion_toad',
            'cinder_strider','magma_beetle','reef_skimmer','tide_serpent','spore_hare','mycelial_beast',
            'wind_stalker','leviwing','street_drone','plasma_hound',
        }
        self.assertEqual(len(new_species), 16)
        rarity_profile = {'Comum': (8,2,20.0), 'Incomum': (9,3,40.0)}
        for sid in new_species:
            spec = SPECIES[sid]
            card = CARDS[spec['card']]
            mana_max, mana_cost, chance = rarity_profile[card['rarity']]
            self.assertEqual(tuple(spec['basic_attack']), tuple(spec['attack']))
            self.assertEqual(tuple(spec['special_attack']), tuple(card['damage']))
            self.assertEqual(spec['special_attack_card'], spec['card'])
            self.assertEqual(spec['mana_max'], mana_max)
            self.assertEqual(spec['mana_cost'], mana_cost)
            self.assertEqual(spec['special_chance'], chance)

    def test_new_cards_use_only_the_allowed_single_rarity_attribute_and_never_defense(self):
        new_card_ids = [
            'ferrous_mite_card','magnetic_ram_card','gloom_moth_card','vesper_cat_card','charge_ray_card','ion_toad_card',
            'cinder_strider_card','magma_beetle_card','reef_skimmer_card','tide_serpent_card','spore_hare_card','mycelial_beast_card',
            'wind_stalker_card','leviwing_card','street_drone_card','plasma_hound_card',
            'mekron','nocther','voltrik','moryss','verdak','gravorn','alphor_fireball','broom_lightning',
        ]
        caps = {'Comum': {'attack_pct': 3.0, 'crit_rate': 3.0, 'crit_damage': 0.05},
                'Incomum': {'attack_pct': 5.0, 'crit_rate': 5.0, 'crit_damage': 0.10},
                'Rara': {'attack_pct': 10.0, 'crit_rate': 10.0, 'crit_damage': 0.20},
                'Mítica': {'attack_pct': 15.0, 'crit_rate': 15.0, 'crit_damage': 0.25},
                'Lendária': {'attack_pct': 20.0, 'crit_rate': 20.0, 'crit_damage': 0.40}}
        for cid in new_card_ids:
            card = CARDS[cid]
            attrs = card.get('attributes', {})
            self.assertEqual(len(attrs), 1, cid)
            self.assertNotIn('defense', attrs, cid)
            self.assertIn(next(iter(attrs)), caps[card['rarity']], cid)
            self.assertEqual(attrs[next(iter(attrs))], caps[card['rarity']][next(iter(attrs))], cid)

    def test_alphor_volcano_boss_requires_both_horns_to_expose_fire_core_and_uses_multi_target_fireball(self):
        s = State(602)
        s.dobra_core_installed = True
        for bid in GALAXY_RARE_BOSSES['vharos']:
            s.bosses[bid]['defeated'] = True
        ok, msg = s.start_boss_battle('alphor')
        self.assertTrue(ok, msg)
        target_ids = {t['id'] for t in s.battle_targets()}
        self.assertNotIn('fire_core', target_ids)
        hp_before = s.battle['hp']
        s.rng = _SequenceRng([0.0, 0.0, 0.0], randint_value=12)
        result = s.action('basic', 'horn_left')
        self.assertTrue(result['ok'])
        self.assertEqual(s.battle['hp'], hp_before)
        self.assertLess(s.battle['zone_hp']['horn_left'], s.battle['zone_hp_max']['horn_left'])
        s.battle['zone_hp']['horn_left'] = 0
        s.battle['zone_hp']['horn_right'] = 0
        self.assertIn('fire_core', {t['id'] for t in s.battle_targets()})
        fireball = CARDS['alphor_fireball']
        self.assertEqual(fireball['target_mode'], 'multi')
        self.assertIn('bola de fogo', fireball['description'].lower())
        self.assertEqual(fireball['attributes'], {'attack_pct': 20.0})
        self.assertEqual(BOSS_ARENAS['pyraxis'], 'pyraxis_caldera')
        self.assertTrue(SECTORS['pyraxis_caldera']['boss_arena'])

    def test_broom_samurai_telegraphs_fatal_lightning_after_two_basic_turns_with_stasis_qte(self):
        s = State(603)
        s.dobra_core_installed = True
        s.helmet_owned = True
        s.helmet_equipped = True
        s.helmet_generation = 2
        for bid in GALAXY_RARE_BOSSES['meridion']:
            s.bosses[bid]['defeated'] = True
        ok, msg = s.start_boss_battle('broom')
        self.assertTrue(ok, msg)
        # Dois turnos que não escolhem o especial fazem a carga chegar a 2.
        s.rng = _SequenceRng([0.99, 0.99, 0.99, 0.99, 0.0], randint_value=10)
        s.hp = s.max_hp
        first = s.enemy_turn()
        s.hp = 9999
        second = s.enemy_turn()
        s.hp = s.max_hp
        self.assertFalse(first['special'])
        self.assertFalse(second['special'])
        self.assertEqual(s.battle['broom_charge'], 2)
        s.hp = s.max_hp
        fatal = s.enemy_turn()
        self.assertTrue(fatal['special'])
        self.assertTrue(fatal['stasis_triggered'])
        self.assertEqual(fatal['stasis_key'], 'Q')
        self.assertEqual(s.battle['stasis_pending']['key'], 'Q')
        self.assertEqual(CARDS['broom_lightning']['target_mode'], 'single')
        self.assertEqual(CARDS['broom_lightning']['execution_threshold'], 0.25)
        self.assertTrue(BOSSES['broom']['fatal_attack'])
        blocked = s.resolve_stasis(True)
        self.assertTrue(blocked['success'])
        self.assertEqual(s.hp, s.max_hp)

    def test_nerissa_city_uses_multiple_maps_and_contains_known_and_unknown_civilizations(self):
        maps = {'nerissa_landing', 'nerissa_bazaar', 'nerissa_transit_district', 'nerissa_tower_crown'}
        self.assertTrue({'nerissa_landing', 'nerissa_bazaar', 'nerissa_transit_district'}.issubset(SECTORS))
        civs = set()
        for key in maps - {'nerissa_tower_crown'}:
            settlement = SECTORS[key].get('settlement')
            if settlement:
                civs.update(n.get('civilization') for n in settlement.get('npcs', []))
        self.assertIn('avarin', civs)
        self.assertIn('nahr_shadows', civs)
        self.assertIn('dran', civs)
        self.assertIn('velkari', civs)
        self.assertIn('nyxen', civs)
        self.assertIn('mycelari', civs)
        self.assertIn('tethran', civs)
        self.assertTrue(SECTORS['nerissa_tower_crown']['boss_arena'])
        self.assertEqual(BOSS_ARENAS['nerissa'], 'nerissa_tower_crown')

    def test_unknown_city_language_requires_calibration_and_becomes_normal_after_success(self):
        s = State(604)
        s.discover_planet('nerissa')
        s.sector = 'nerissa_transit_district'
        s.pos = [10, 9]
        npc = s.nearby_npc()
        self.assertIsNotNone(npc)
        self.assertEqual(npc['civilization'], 'tethran')
        message, _ = s.interact_npc(npc)
        self.assertIn('Calibração necessária', message)
        self.assertEqual(s.pending_language_civilization, 'tethran')
        self.assertFalse(s.knows_language('tethran'))
        ok, _ = s.learn_language('tethran')
        self.assertTrue(ok)
        self.assertTrue(s.knows_language('tethran'))
        message, _ = s.interact_npc(npc)
        self.assertIn('contato estabelecido', message)
        self.assertIsNone(s.pending_language_civilization)
        # Civilizações já conhecidas não entram no novo QTE linguístico.
        s.pos = [12, 9]
        known_npc = s.area['settlement']['npcs'][0]
        message, _ = s.interact_npc(known_npc)
        self.assertNotIn('Calibração necessária', message)

    def test_060_save_roundtrip_preserves_dobra_language_and_galaxy_selection(self):
        s = State(605)
        for sid in s.ship_systems:
            s.ship_systems[sid] = 100
        s.inventory['Núcleo de Dobra'] = 1
        s.ensure_exploration_mission()
        s.install_dobra_core()
        s.discover_planet('nerissa')
        s.language_mastery['tethran'] = True
        s.selected_galaxy_id = 'meridion'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            s.save(path, refresh=False)
            data = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(data['version'], 65)
            loaded, _ = State.load(path)
        self.assertTrue(loaded.dobra_core_installed)
        self.assertTrue(loaded.language_mastery['tethran'])
        self.assertEqual(loaded.selected_galaxy_id, 'meridion')

    def test_ui_contains_clean_060_navigation_surfaces(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('GALAXY_DISPLAY_ORDER', source)
        self.assertIn('NÚCLEO DE DOBRA DETECTADO', source)
        self.assertIn('INSTALAR', source)
        self.assertIn('CALIBRAÇÃO LINGUÍSTICA', source)
        self.assertIn('ATAQUE FATAL DETECTADO', source)
        self.assertIn('city_gate', source)
        self.assertIn('pyraxis', source)


if __name__ == '__main__':
    unittest.main()
