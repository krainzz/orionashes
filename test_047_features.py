import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

from content import CARDS, CREATURE_TYPES, HERBS, SPECIES
from core import State
from world import SECTORS

try:
    from main import App
    PYGAME_AVAILABLE = True
except ModuleNotFoundError as exc:
    if exc.name != 'pygame':
        raise
    App = None
    PYGAME_AVAILABLE = False


class Version047FeatureTests(unittest.TestCase):
    def test_all_species_and_cards_have_matching_types(self):
        for sid, spec in SPECIES.items():
            self.assertIn(spec.get('type'), CREATURE_TYPES, sid)
            card_id = spec.get('card')
            if card_id:
                self.assertIn(card_id, CARDS)
                self.assertEqual(CARDS[card_id].get('type'), spec.get('type'))
        self.assertEqual(len(HERBS), 12)

    def test_every_creature_has_a_defined_vital_zone_without_changing_current_zones(self):
        for sid, spec in SPECIES.items():
            vital_id = spec.get('vital_zone')
            self.assertIn(vital_id, spec.get('target_zones', {}), sid)
            vital_flags = [zid for zid, zone in spec.get('target_zones', {}).items() if zone.get('vital')]
            self.assertEqual(vital_flags, [vital_id], sid)
        # Current boss uses a vital point too; its behavior remains unchanged for now.
        from content import BOSSES
        self.assertIn(BOSSES['kuvaar'].get('vital_zone'), BOSSES['kuvaar'].get('target_zones', {}))
        self.assertTrue(BOSSES['kuvaar']['target_zones'][BOSSES['kuvaar']['vital_zone']].get('vital'))

    def test_resources_button_moved_to_technology_panel_and_grid_removed(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        menu_section = source[source.index('    def menu(self):'):source.index('    def _mission_catalog(self, category=None):')]
        tech_section = source[source.index('    def technology(self):'):source.index('    def resource_catalog(self):')]
        self.assertNotIn("'RECURSOS', lambda: self.open_panel('resources')", menu_section)
        self.assertIn("self.open_panel('resources', 'tech')", tech_section)
        self.assertNotIn("pygame.draw.lines(s, tuple(max(0,c-12)", source)

    def test_achievement_requires_manual_claim_and_alerts(self):
        state = State()
        state.kills['scarab'] = 1
        self.assertTrue(state.refresh_achievements())
        entry = state.achievements['first_blood']
        self.assertTrue(entry['unlocked'])
        self.assertFalse(entry['claimed'])
        self.assertEqual(state.inventory.get('Sucata', 0), 0)
        alert = state.pop_achievement_alert()
        self.assertEqual(alert['type'], 'unlocked')
        ok, msg = state.claim_achievement('first_blood')
        self.assertTrue(ok)
        self.assertTrue(state.achievements['first_blood']['claimed'])
        self.assertEqual(state.inventory.get('Sucata', 0), 3)
        claimed_alert = state.pop_achievement_alert()
        self.assertEqual(claimed_alert['type'], 'claimed')
        ok, _ = state.claim_achievement('first_blood')
        self.assertFalse(ok)

    def test_flora_is_locked_without_scan_and_collectable_with_scan(self):
        state = State()
        flora_node = next(n for data in SECTORS.values() for n in data['nodes'] if n.get('category') == 'flora')
        sector = next(sid for sid, data in SECTORS.items() if flora_node in data['nodes'])
        state.sector = sector
        state.pos = list(flora_node['pos'])
        before = state.inventory.get(flora_node['item'], 0)
        msg = state.collect()
        self.assertIn('ANÁLISE BOTÂNICA INDISPONÍVEL', msg)
        self.assertNotIn(flora_node['id'], state.collected_nodes)
        self.assertEqual(state.inventory.get(flora_node['item'], 0), before)
        state.scan_unlocked = True
        msg = state.collect()
        self.assertTrue(msg.startswith('Coletou'))
        self.assertIn(flora_node['id'], state.collected_nodes)
        self.assertGreater(state.inventory.get(flora_node['item'], 0), before)

    def test_save_roundtrip_preserves_manual_claim_and_scan_state(self):
        state = State()
        state.achievements['first_blood'] = {'unlocked': True, 'claimed': True}
        state.inventory['Sucata'] = 7
        state.scan_unlocked = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save_v047.json'
            state.save(path, refresh=False)
            loaded, msg = State.load(path)
        self.assertIn('0.6.9', msg)
        self.assertTrue(loaded.achievements['first_blood']['claimed'])
        self.assertEqual(loaded.inventory['Sucata'], 7)
        self.assertTrue(loaded.scan_unlocked)

    @unittest.skipUnless(PYGAME_AVAILABLE, 'pygame não instalado no ambiente de teste')
    def test_workshop_successor_visibility_uses_immediate_previous_tier(self):
        app = App()
        try:
            app.state.helmet_generation = 0
            app.state.chest_generation = 1
            app.state.memory_owned['advanced'] = 0
            ids = {cid for cid, _ in app.craft_entries()}
            self.assertNotIn('helmet_g2', ids)
            self.assertNotIn('chest_g3', ids)
            self.assertNotIn('memory_g3', ids)

            app.state.helmet_generation = 1
            app.state.chest_generation = 2
            app.state.memory_owned['advanced'] = 1
            ids = {cid for cid, _ in app.craft_entries()}
            self.assertIn('helmet_g2', ids)
            self.assertIn('chest_g3', ids)
            self.assertIn('memory_g3', ids)
        finally:
            import pygame
            pygame.quit()

    @unittest.skipUnless(PYGAME_AVAILABLE, 'pygame não instalado no ambiente de teste')
    def test_resource_catalog_is_sorted_and_does_not_fake_future_locations(self):
        app = App()
        try:
            rows = app.resource_catalog()
            names = [name for name, _ in rows]
            self.assertEqual(names, sorted(names, key=str.casefold))
            self.assertTrue(any(name in HERBS for name in names))
            self.assertFalse(any(entry['sources'] == {'Dados futuros'} for _, entry in rows))
            boss_rows = [(name, entry) for name, entry in rows if entry.get('boss')]
            self.assertTrue(boss_rows)
            for _, entry in boss_rows:
                self.assertNotIn('Mundos futuros', entry['locations'])
        finally:
            import pygame
            pygame.quit()

    @unittest.skipUnless(PYGAME_AVAILABLE, 'pygame não instalado no ambiente de teste')
    def test_unanalyzed_card_does_not_expose_type_in_workshop(self):
        app = App()
        try:
            captured = []
            app.box = lambda *args, **kwargs: None
            app.button = lambda *args, **kwargs: None
            app.label = lambda value, *args, **kwargs: captured.append(str(value))
            app.wrap = lambda value, *args, **kwargs: 0
            app.craft_view()
            type_name = CARDS[next(iter(CARDS))]['type']
            # No explicit type label may reveal a creature type while its card is unknown.
            self.assertNotIn(f'TIPO: {type_name}', [v.upper() for v in captured])
        finally:
            import pygame
            pygame.quit()


if __name__ == '__main__':
    unittest.main()
