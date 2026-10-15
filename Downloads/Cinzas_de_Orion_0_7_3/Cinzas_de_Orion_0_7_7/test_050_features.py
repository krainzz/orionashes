import json
import tempfile
import unittest
from pathlib import Path

from content import AURORA_UPGRADES, RENOWN_MILESTONES, STELLAR_ROUTES, CARD_RARITIES, SHIP_INTERIOR, FACTIONS
from core import State


class Version050FeatureTests(unittest.TestCase):
    def test_main_menu_and_computer_are_spaced_without_duplicate_routes(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("self.box((50, 86, 1100, 626)", source)
        self.assertIn("('CAMPANHA', 80", source)
        self.assertIn("('REGISTROS', 440", source)
        self.assertIn("('SISTEMAS', 800", source)
        self.assertIn("('OFICINA / CRAFT', lambda:self.open_panel('craft','ship'))", source)
        self.assertIn("('DIAGNÓSTICO DA NAVE', lambda:self.open_ship_diagnostic('ship'))", source)
        self.assertNotIn("('COCKPIT', lambda:self.open_panel('cockpit','ship'))", source)
        self.assertNotIn("pygame.K_m:lambda:self.open_panel('routes','ship')", source)

    def test_stellar_route_unknown_remains_unknown_when_selected(self):
        s = State()
        unknown = next(route for route in STELLAR_ROUTES if not route['known'])
        self.assertNotIn(unknown['id'], s.known_planets)
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("route['name'] if route_id in self.state.known_planets else 'Destino não identificado: ???'", source)
        self.assertIn("name=r['name'] if known else '???'", source)

    def test_cockpit_is_physical_station_only_and_state_keeps_selected_planet(self):
        s = State()
        self.assertEqual(s.ship_pos, list(SHIP_INTERIOR['start']))
        self.assertFalse(s.inside_ship)
        self.assertEqual(SHIP_INTERIOR['cockpit'], (6,2))
        s.inside_ship = True
        s.ship_pos = list(SHIP_INTERIOR['cockpit'])
        self.assertEqual(s.ship_interaction(), 'cockpit')
        s.selected_planet = 'veyra'
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'save.json'
            s.save(p, refresh=False)
            loaded, _ = State.load(p)
        self.assertEqual(loaded.selected_planet, 'veyra')

    def test_aurora_plus_uses_only_veyra_materials(self):
        # O primeiro aprimoramento deve ser realmente fabricável com drops do planeta inicial.
        veyra_drops = set()
        from content import SPECIES
        for spec in SPECIES.values():
            veyra_drops.update(drop[0] for drop in spec.get('drops', []))
        self.assertTrue(AURORA_UPGRADES[1]['recipe'])
        self.assertTrue(set(AURORA_UPGRADES[1]['recipe']).issubset(veyra_drops))

    def test_aurora_upgrades_are_non_cumulative_and_gate_by_availability(self):
        s = State()
        s.pos = [0,0]
        self.assertEqual(s.aurora_bonuses(), {'hp': 0, 'attack': 0, 'crit_rate': 0.0, 'crit_damage': 0.0})
        self.assertEqual(s.max_hp, 36)
        self.assertFalse(s.upgrade_aurora(1)[0])  # inicial: ainda não está junto à nave
        s.inventory.update(AURORA_UPGRADES[1]['recipe'])
        from content import SHIP
        s.pos = list(SHIP)
        ok, msg = s.upgrade_aurora(1)
        self.assertTrue(ok, msg)
        self.assertEqual(s.max_hp, 56)
        self.assertEqual(s.player_attributes()['attack'], 14)
        self.assertEqual(s.player_attributes()['crit_damage'], 1.52)
        # Future tiers are blocked even with all materials because they are not yet available in 0.5.
        s.inventory.update(AURORA_UPGRADES[2]['recipe'])
        ok, msg = s.upgrade_aurora(2)
        self.assertFalse(ok)
        self.assertIn('outros mundos', msg.lower())

    def test_aurora_current_bonus_replaces_previous_values(self):
        s = State(); s.aurora_level = 2
        bonus = s.aurora_bonuses()
        self.assertEqual(bonus['hp'], 40)
        self.assertEqual(bonus['attack'], 4)
        self.assertEqual(bonus['crit_rate'], 1.0)
        self.assertEqual(bonus['crit_damage'], 0.04)
        s.aurora_level = 3
        bonus = s.aurora_bonuses()
        self.assertEqual(bonus['hp'], 100)
        self.assertEqual(bonus['attack'], 10)
        self.assertEqual(bonus['crit_rate'], 4.0)
        self.assertEqual(bonus['crit_damage'], 0.10)

    def test_memory_slots_are_locked_by_chest_tier(self):
        s = State()
        self.assertEqual(s.max_memory_slots, 2)
        s.chest_generation = 2
        self.assertEqual(s.max_memory_slots, 3)
        self.assertIn('bloqueado', s.configure_memory(3, None).lower())
        s.chest_generation = 3
        self.assertEqual(s.max_memory_slots, 4)
        s.memory_owned['expanded'] = 1
        self.assertNotIn('bloqueado', s.configure_memory(3, 'expanded').lower())

    def test_renown_award_updates_faction_planet_and_galaxy(self):
        s = State()
        self.assertTrue(s.award_renown('waterkeepers', 25, 'teste'))
        self.assertEqual(s.renown_by_faction['waterkeepers'], 25)
        self.assertEqual(s.renown_planets['veyra'], 25)
        self.assertEqual(s.renown_galaxies['local'], 25)
        self.assertEqual(s.renown_reward('faction', 'waterkeepers', 0), 'faction:waterkeepers:0')
        self.assertEqual(s.renown_reward('planet', 'veyra', 0), None)
        ok, msg = s.claim_renown_reward('faction', 'waterkeepers', 0)
        self.assertTrue(ok, msg)
        self.assertIn('renown_claimed', [a['type'] for a in s.achievement_alerts])
        self.assertIsNone(s.renown_reward('faction', 'waterkeepers', 0))

    def test_renown_milestones_include_faction_planet_and_galaxy(self):
        self.assertEqual(RENOWN_MILESTONES['faction'], (25, 50, 100))
        self.assertEqual(RENOWN_MILESTONES['planet'], (50, 150, 300))
        self.assertEqual(RENOWN_MILESTONES['galaxy'], (500, 1500))
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("self.label('MILESTONES'", source)
        self.assertIn("lambda idx=i:self.claim_renown('planet',selected_id,idx)", source)

    def test_renown_is_not_rendered_as_the_old_status_bar(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        status = source[source.index('    def status(self):'):source.index('    def pause(self):')]
        self.assertNotIn('self.state.renown_label()', status)
        self.assertIn("self.label('ESTADO DA NAVE'", status)

    def test_map_creature_labels_show_name_and_scan_level(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("text=spec['name'] if not self.state.scan_unlocked else f'{spec[\"name\"]}  NV {creature_level(spec)}'", source)
        self.assertIn("pygame.draw.rect(self.canvas,(5,8,11),rect,border_radius=3)", source)
        self.assertIn("BOSSES[species]", source)

    def test_current_known_planet_state_is_persisted(self):
        s = State()
        s.known_planets.append('orionis')
        s.renown_planets['orionis'] = 7
        s.selected_planet = 'orionis'
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'save.json'; s.save(p, refresh=False)
            raw=json.loads(p.read_text(encoding='utf-8'))
            loaded,_=State.load(p)
        self.assertEqual(raw['version'], 65)
        self.assertIn('orionis', loaded.known_planets)
        self.assertEqual(loaded.renown_planets['orionis'], 7)
        self.assertEqual(loaded.selected_planet, 'orionis')


if __name__ == '__main__':
    unittest.main()

class Version050CockpitHotfixTests(unittest.TestCase):
    def test_galaxy_has_five_visitables_and_named_galaxy(self):
        from content import GALAXY_NAME
        self.assertEqual(GALAXY_NAME, 'Galáxia Nárion')
        local_routes = [r for r in STELLAR_ROUTES if r.get('galaxy') == 'local']
        self.assertEqual(len(local_routes), 5)
        self.assertEqual(len(STELLAR_ROUTES), 13)
        self.assertEqual(STELLAR_ROUTES[0]['name'], 'Veyra')

    def test_planet_metadata_and_dynamic_civilizations(self):
        s = State()
        self.assertIn('Avarin', s.known_civilizations_by_planet['veyra'])
        s.known_planets.append('orionis')
        self.assertEqual(s.known_civilizations_by_planet['orionis'], [])
        self.assertTrue(s.discover_civilization_on_planet('orionis', 'Civ X'))
        self.assertEqual(s.known_civilizations_by_planet['orionis'], ['Civ X'])

    def test_selected_unknown_planet_keeps_name_hidden_and_known_shows_name(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("sel_name=selected['name'] if known else '???'", source)
        self.assertTrue("galaxy_surface=self.font(11).render(GALAXY_NAME.upper(),True,MUTED)" in source or "GALAXIES.get(selected_gid,{}).get('name'" in source)
        self.assertIn("'ATMOSFERA'", source)
        self.assertIn("'CIVILIZAÇÕES CONHECIDAS'", source)
        self.assertTrue("self.button((775,615,325,48)" in source or "flight_y=625" in source)

    def test_removed_routes_are_not_in_the_galaxy(self):
        ids = {r['id'] for r in STELLAR_ROUTES}
        self.assertNotIn('silex', ids)
        self.assertNotIn('thren', ids)
