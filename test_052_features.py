import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

from content import (
    CARDS, CREATURE_TYPES, GALAXIES, HELMET_DESIGNS, HELMET_DESIGN_ORDER,
    STELLAR_ROUTES, TYPE_ADVANTAGES, BOSS_ARENAS,
)
from core import State
from world import SECTORS


class Version052FeatureTests(unittest.TestCase):
    def test_space_replaces_enter_for_continue_and_skip_prompts(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("pygame.K_RETURN", source)
        self.assertIn("pygame.K_SPACE", source)

    def test_all_ship_repairs_unlock_exploration_and_current_destinations(self):
        s = State(52)
        for sid in s.ship_systems:
            s.ship_systems[sid] = 100
        changed = s.ensure_exploration_mission()
        self.assertTrue(changed)
        self.assertEqual(s.missions['explore_galaxy']['status'], 'active')
        self.assertEqual(s.journal['objectives']['explore_space']['status'], 'active')
        self.assertEqual(set(s.known_planets), {r['id'] for r in STELLAR_ROUTES})
        self.assertEqual(s.exploration_mission_title(), 'Explore o Universo')

    def test_planet_travel_uses_fixed_landing_and_can_return_to_veyra(self):
        s = State(53)
        for sid in s.ship_systems:
            s.ship_systems[sid] = 100
        s.ensure_exploration_mission()
        ok, _ = s.arrive_at_planet('orionis')
        self.assertTrue(ok)
        self.assertEqual(s.sector, 'orionis_landing')
        self.assertEqual(s.pos, [7, 8])
        self.assertEqual(s.current_planet_id(), 'orionis')
        ok, _ = s.arrive_at_planet('veyra')
        self.assertTrue(ok)
        self.assertEqual(s.sector, 'landing')
        self.assertEqual(s.pos, [7, 8])
        self.assertEqual(s.current_planet_id(), 'veyra')

    def test_exploration_mission_uses_universe_title_after_flight_is_ready(self):
        s = State(54)
        self.assertEqual(s.exploration_mission_title(), 'Explore a Galáxia')
        for sid in s.ship_systems:
            s.ship_systems[sid] = 100
        s.ensure_exploration_mission()
        self.assertEqual(s.exploration_mission_title(), 'Explore o Universo')

    def test_each_new_planet_has_four_maps_and_fixed_ship_landing(self):
        for route in STELLAR_ROUTES:
            if route['id'] == 'veyra':
                continue
            rid = route['id']
            maps = [key for key in SECTORS if key == route['landing_sector'] or key.startswith(rid + '_')]
            expected_map_count = 5 if rid == 'nahr' else 4
            self.assertEqual(len(maps), expected_map_count, rid)
            self.assertEqual(SECTORS[route['landing_sector']]['ship'], (7, 7), rid)
            for key in maps:
                if key == 'nahr_ry_void':
                    self.assertEqual(SECTORS[key]['nodes'], [])
                    self.assertEqual(SECTORS[key]['rocks'], set())
                    self.assertEqual(SECTORS[key].get('spawns', []), [])
                    continue
                self.assertNotEqual(SECTORS[key]['nodes'], [])
                self.assertGreater(len(SECTORS[key]['rocks']), 0)
                if not SECTORS[key].get('boss_arena'):
                    self.assertGreaterEqual(len(SECTORS[key]['spawns']), 0)
                else:
                    self.assertEqual(SECTORS[key].get('spawns', []), [])

    def test_new_fauna_cards_types_and_progression_are_defined(self):
        new_species = {
            'salamander_igneous','ironback_crab','ion_wasp','frost_wolf','crystal_grazer','glacial_eel',
            'root_scorpion','basalt_tortoise','salt_spider','luminous_stag','shadow_panther','spore_manta'
        }
        self.assertEqual(len(new_species), 12)
        for sid in new_species:
            from content import SPECIES
            spec = SPECIES[sid]
            self.assertIn(spec['type'], CREATURE_TYPES)
            self.assertIn(spec['card'], CARDS)
            self.assertEqual(CARDS[spec['card']]['type'], spec['type'])
        levels = []
        from core import creature_level
        from content import SPECIES
        for sid in new_species:
            levels.append(creature_level(SPECIES[sid]))
        self.assertGreaterEqual(min(levels), 12)
        self.assertLessEqual(max(levels), 18)

    def test_new_planet_flora_requires_scan_and_no_new_map_has_quests(self):
        for route in STELLAR_ROUTES:
            if route['id'] == 'veyra':
                continue
            rid = route['id']
            for key, data in SECTORS.items():
                if key == route['landing_sector'] or key.startswith(rid + '_'):
                    for node in data['nodes']:
                        if node.get('category') == 'flora':
                            self.assertTrue(node.get('scan_required'), (rid, key, node['id']))
                    self.assertFalse(any(m.get('quest') for m in data.get('landmarks', [])), (rid, key))

    def test_helmet_craft_is_automatic_and_design_catalog_is_ready(self):
        s = State(55)
        s.pos = [7, 8]
        s.inventory.update({'Sucata': 30, 'Núcleo de decodificação': 5, 'Célula de energia instável': 1})
        msg = s.craft('helmet_g1')
        self.assertIn('equipado automaticamente', msg)
        self.assertTrue(s.helmet_owned)
        self.assertTrue(s.helmet_equipped)
        self.assertEqual(s.helmet_design, 'tactical')
        self.assertEqual(HELMET_DESIGN_ORDER, ('tactical', 'recon', 'combat'))
        self.assertEqual(set(HELMET_DESIGNS), set(HELMET_DESIGN_ORDER))

    def test_save_roundtrip_is_version_052(self):
        s = State(56)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            s.save(path, refresh=False)
            raw = path.read_text(encoding='utf-8')
            self.assertIn('"version": 65', raw)
            loaded, msg = State.load(path)
        self.assertFalse(loaded.save_blocked)
        self.assertIn('0.6.9', msg)

    def test_current_main_has_travel_scene_and_standard_helmet_config_button(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("'travel': self.travel_scene", source)
        self.assertIn('def travel_scene(self):', source)
        self.assertNotIn('RETIRAR ELMO', source)
        self.assertNotIn('EQUIPAR ELMO', source)
        self.assertNotIn('DESIGNS PREPARADOS', source)
        self.assertIn("'helmet', 'ELMO'", source)
        self.assertIn("kind == 'helmet' and self.state.helmet_owned", source)
        self.assertIn('automaticamente', source.lower())


    def test_statistics_are_aggregate_and_do_not_list_each_creature_map_or_mission(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        stats_block = source[source.index('    def statistics_view(self):'):source.index('    def bestiary(self):')]
        self.assertNotIn("[(SPECIES[k]['name']", stats_block)
        self.assertNotIn("[(SECTORS[sid]['name']", stats_block)
        self.assertNotIn("self._mission_catalog()", stats_block)

    def test_each_planet_has_one_reserved_boss_arena(self):
        self.assertEqual(set(BOSS_ARENAS), {'veyra','orionis','kael','nahr','elyra','dornak','nyxara','zereth','pyraxis','thalassene','mycelon','tethra','nerissa'})
        for rid, sid in BOSS_ARENAS.items():
            self.assertIn(sid, SECTORS)
            self.assertTrue(SECTORS[sid].get('boss_arena'))
            if rid == 'veyra':
                self.assertEqual(sid, 'salt_basin')
            else:
                self.assertEqual(sid.split('_', 1)[0], rid)

    def test_loader_accepts_legacy_and_future_version_with_schema_gaps(self):
        import json
        with tempfile.TemporaryDirectory() as base_tmp:
            base_path = Path(base_tmp) / 'base.json'
            State().save(base_path, refresh=False)
            base = json.loads(base_path.read_text(encoding='utf-8'))
        base['version'] = 999
        # Simula o tipo de lacunas que aparecem quando a lista de conteúdo cresce.
        base.get('worlds', {}).pop('orionis_landing', None)
        base.get('statistics', {}).get('kills', {}).pop('salamander_igneous', None)
        base.get('known_cards', []).append('nao_existe')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            path.write_text(json.dumps(base, ensure_ascii=False), encoding='utf-8')
            state, msg = State.load(path)
        self.assertFalse(state.save_blocked)
        self.assertIn('versão futura', msg)
        self.assertIn('orionis_landing', state.worlds)
        self.assertIn('salamander_igneous', state.statistics['kills'])
        self.assertIn('nao_existe', state.known_cards)

    def test_backup_is_not_replaced_by_a_corrupted_current_save(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            state = State()
            state.save(directory / 'save.json', refresh=False)
            state.hp = 30
            state.save(directory / 'save.json', refresh=False)
            backup_before = json.loads((directory / 'bkp.json').read_text(encoding='utf-8'))
            (directory / 'save.json').write_text('{invalid', encoding='utf-8')
            loaded, _ = State.load(directory / 'bkp.json')
            loaded.hp = 29
            loaded.save(directory / 'save.json', refresh=False)
            backup_after = json.loads((directory / 'bkp.json').read_text(encoding='utf-8'))
            self.assertEqual(backup_after['hp'], backup_before['hp'])

if __name__ == '__main__':
    unittest.main()
