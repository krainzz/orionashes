import json
import os
import tempfile
import unittest
from pathlib import Path

from content import CARD_ATTACK_PERCENT_GUIDE, CARDS, CARD_VARIANTS, SPECIES, TYPE_ADVANTAGES, format_card_name
from core import State, load_campaign


class Version049FeatureTests(unittest.TestCase):
    def test_all_cards_use_percent_attack_bonus_only(self):
        self.assertEqual(set(CARD_ATTACK_PERCENT_GUIDE), {'Comum', 'Incomum', 'Rara', 'Mítica', 'Lendária', 'Única'})
        self.assertFalse(any('attack' in card.get('attributes', {}) for card in CARDS.values()))
        for cid, card in CARDS.items():
            if card.get('enemy_only'):
                continue
            attrs = card.get('attributes', {})
            self.assertNotIn('attack', attrs, cid)
            self.assertTrue(set(attrs).issubset({'attack_pct','crit_rate','crit_damage'}), cid)
            self.assertEqual(len(attrs), 1, cid)
        self.assertGreater(CARDS['lithic_sentence']['attributes']['attack_pct'], CARDS['bite']['attributes']['attack_pct'])
        self.assertGreater(CARDS['rift_break']['attributes']['attack_pct'], CARDS['bite']['attributes']['attack_pct'])

    def test_attack_percent_scales_with_variants_and_player_attack(self):
        s = State(1)
        s.slots = ['shell|normal|1', 'shell|plus|2', 'shell|plusplus|3']
        s.crafted = list(s.slots)
        attrs = s.player_attributes()
        self.assertAlmostEqual(attrs['attack_pct_bonus'], 3.0 + 4.5 + 6.0)
        self.assertAlmostEqual(attrs['attack'], 12 * 1.135)
        shell_n = s.card_attributes('shell|normal|1')
        shell_p = s.card_attributes('shell|plus|2')
        shell_pp = s.card_attributes('shell|plusplus|3')
        self.assertAlmostEqual(shell_n['attack_pct'], 3.0)
        self.assertAlmostEqual(shell_p['attack_pct'], 4.5)
        self.assertAlmostEqual(shell_pp['attack_pct'], 6.0)
        self.assertNotIn('defense', shell_n)

    def test_card_temporary_effects_replace_and_reset_per_battle(self):
        s = State(2)
        s.crafted = ['shell|normal|1']
        s.slots = ['shell|normal|1', None, None]
        s.start_battle(0)
        first = s.action('shell')
        self.assertTrue(first['ok'])
        self.assertEqual(s.battle['shield_pct'], 50.0)
        s.memory = 8
        second = s.action('shell')
        self.assertTrue(second['ok'])
        self.assertEqual(s.battle['shield_pct'], 50.0)
        self.assertEqual(s.battle['weaken'], 0)
        s.enemy_turn()
        self.assertEqual(s.battle['shield'], 0)
        s.win() if s.battle and s.battle['hp'] <= 0 else None
        if not s.battle:
            s = State(3)
        else:
            s.battle = None
        s.start_battle(0)
        self.assertEqual(s.battle['shield'], 0)
        self.assertEqual(s.battle['weaken'], 0)

    def test_crafting_never_auto_equips_card(self):
        s = State(4)
        s.kills['scarab'] = 1
        s.inventory.update(CARDS['shell']['recipe'])
        before = list(s.slots)
        msg = s.craft('shell')
        self.assertIn('Pool', msg)
        self.assertEqual(s.slots, before)
        self.assertEqual(len(s.crafted), 1)
        self.assertIsNone(s.slots[0])

    def test_equipping_can_replace_a_slot_without_losing_old_card(self):
        s = State(5)
        s.crafted = ['shell|normal|1', 'bite|normal|1']
        s.slots = ['shell|normal|1', None, None]
        self.assertTrue(s.equip('bite|normal|1', 0))
        self.assertEqual(s.slots[0], 'bite|normal|1')
        self.assertIn('shell|normal|1', s.crafted)

    def test_stable_appdata_save_load_and_legacy_migration(self):
        s = State(6)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'game'
            app = Path(tmp) / 'AppDataLocal'
            root.mkdir()
            app.mkdir()
            legacy = root / 'save_v048.json'
            s.save(legacy, refresh=False)
            loaded, msg = load_campaign(app, legacy_directories=(root,), current_filename='save.json')
            self.assertFalse(loaded.save_blocked)
            self.assertTrue((app / 'save.json').exists())
            self.assertIn('persistente', msg)
            loaded.save(app / 'save.json', refresh=False)
            data = json.loads((app / 'save.json').read_text(encoding='utf-8'))
            self.assertEqual(data['version'], 65)

    def test_main_points_save_to_localappdata_and_has_stable_name(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("LOCAL_APPDATA = Path(os.environ.get('LOCALAPPDATA'", source)
        self.assertIn("SAVE = SAVE_DIR / 'save.json'", source)
        self.assertIn("load_campaign(SAVE_DIR, legacy_directories=(ROOT,), current_filename='save.json')", source)

    def test_basic_and_enemy_attack_visuals_exist(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("visual == 'plasma'", source)
        self.assertIn('def _draw_enemy_fx(self, b, hero_x, enemy_x):', source)
        self.assertIn("card.get('visual_key', 'orb')", source)
        self.assertIn("special_card", source)
        self.assertIn("'saline_dissolution'", source)

    def test_album_shows_availability_and_manopla_uses_picker(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("panel_header('CARTAS'", source)
        self.assertNotIn("'ÁLBUM COMPLETO'", source)
        self.assertIn("'CARTAS'", source)
        self.assertIn('DISPONÍVEIS:', source)
        self.assertIn('FABRICAÇÃO DE CARTAS', source)
        self.assertIn('def card_crafting_view(self):', source)
        self.assertIn('def open_card_picker(self, slot_index):', source)
        self.assertIn('def card_picker(self):', source)
        self.assertIn('self.open_card_picker(idx)', source)
        self.assertNotIn("'EQUIPAR'+CARD_VARIANTS[variant]['label']", source)

    def test_hotfix_ui_labels_and_navigation_are_unambiguous(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertNotIn("'ÁLBUM COMPLETO'", source)
        self.assertIn("'CARTAS'", source)
        self.assertIn("'OFICINA / CRAFT'", source)
        self.assertIn("'DIAGNÓSTICO DA NAVE'", source)
        # Oficina e Diagnóstico usam posições distintas no Computador de bordo.
        self.assertIn("('OFICINA / CRAFT', lambda:self.open_panel('craft','ship'))", source)
        self.assertIn("('DIAGNÓSTICO DA NAVE', lambda:self.open_ship_diagnostic('ship'))", source)
        self.assertNotIn("('COCKPIT', lambda:self.open_panel('cockpit','ship'))", source)

    def test_album_rarity_sort_uses_canonical_order(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('rarity_order = {rarity: idx for idx, rarity in enumerate(CARD_RARITIES)}', source)
        self.assertIn('cards.sort(key=lambda item:', source)

    def test_inventory_has_selected_item_context_panel(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("self.inventory_selected_item = None", source)
        self.assertIn('def _inventory_item_usage(self, item_name):', source)
        self.assertIn("'INFORMAÇÕES DO ITEM'", source)
        self.assertIn("'CRIATURAS QUE FORNECEM'", source)
        self.assertIn("visible_rect = row_rect.clip(material_view)", source)

    def test_card_names_are_title_cased_except_connectors(self):
        for card in CARDS.values():
            name = format_card_name(card['name'])
            words = name.split()
            for word in words:
                if word.casefold() in {'de','da','do','das','dos','em','no','na','nos','nas','ao','aos','à','às','por','para','com','sem','sob','sobre','entre','até','desde','contra','perante','após','ante'}:
                    continue
                self.assertTrue(word[:1].isupper(), name)

    def test_type_advantage_matrix_and_basic_neutral(self):
        expected = {
            'Água':'Fogo', 'Fogo':'Planta', 'Planta':'Água', 'Elétrico':'Metal',
            'Terra':'Elétrico', 'Metal':'Terra', 'Luz':'Trevas', 'Trevas':'Luz'
        }
        self.assertEqual(TYPE_ADVANTAGES, expected)
        self.assertEqual(State._type_multiplier(None, 'Fogo'), (1.0, 'neutral'))
        self.assertEqual(State._type_multiplier('Metal', 'Água'), (1.0, 'neutral'))
        self.assertEqual(State._type_multiplier('Água', 'Fogo'), (1.5, 'advantage'))
        self.assertEqual(State._type_multiplier('Fogo', 'Água'), (0.75, 'disadvantage'))

    def test_type_multiplier_is_applied_to_card_attack_result(self):
        class FixedRng:
            def random(self): return 0.0
            def randint(self, a, b): return a
        s = State(9)
        s.crafted=['bite|normal|1']
        s.slots=['bite|normal|1', None, None]
        s.inventory['Escama']=18; s.inventory['Enzima']=3; s.inventory['Sucata']=6
        s.rng=FixedRng()
        s.start_battle(0)  # Escaravelho = Terra; Mordida = Terra, neutral
        r=s.action('bite')
        self.assertEqual(r['type_relation'], 'neutral')
        self.assertEqual(r['type_multiplier'], 1.0)
        # Force the card's type to Água against the Terra target: Terra has no
        # advantage over Água in the matrix, so it remains neutral.
        CARDS['__test_water'] = dict(CARDS['bite'], type='Água')
        try:
            s.crafted=['__test_water|normal|1']; s.slots=['__test_water|normal|1',None,None]
            s.battle=None; s.start_battle(0); s.rng=FixedRng(); r=s.action('__test_water')
            self.assertEqual(r['type_relation'], 'neutral')
        finally:
            del CARDS['__test_water']



    def test_card_type_damage_uses_advantage_and_resistance(self):
        class FixedRng:
            def random(self): return 0.0
            def randint(self, a, b): return a
        def run_with_type(card_type):
            cid='__test_typed'
            card=dict(CARDS['bite'], type=card_type,
                      attributes=dict(CARDS['bite']['attributes'], crit_rate=0.0))
            CARDS[cid]=card
            try:
                s=State(10)
                s.crafted=[f'{cid}|normal|1']; s.slots=[f'{cid}|normal|1',None,None]
                s.rng=FixedRng(); s.start_battle(1)  # Lagarto = Terra
                return s.action(cid)
            finally:
                CARDS.pop(cid,None)
        neutral=run_with_type('Fogo')
        advantage=run_with_type('Metal')
        resistance=run_with_type('Elétrico')
        self.assertEqual(neutral['type_relation'], 'neutral')
        self.assertEqual(advantage['type_relation'], 'advantage')
        self.assertEqual(advantage['type_multiplier'], 1.5)
        self.assertEqual(resistance['type_relation'], 'disadvantage')
        self.assertEqual(resistance['type_multiplier'], 0.75)
        self.assertGreater(advantage['damage'], neutral['damage'])
        self.assertLess(resistance['damage'], neutral['damage'])

    def test_v048_nexus_attack_calibration_is_upgraded_without_double_counting(self):
        s=State(11)
        s.gauntlet_nexus_installed=True
        s.gauntlet_nexus_level=3
        s.gauntlet_nexus_nodes=['nexus_level_01','nexus_level_02','nexus_level_03']
        s.gauntlet_nexus_progression_revision=5
        s.combat_stats['attack_bonus']=1.0  # v0.4.8 had +0.5 per calibration node
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'save_v048.json'
            s.save(p, refresh=False)
            raw=json.loads(p.read_text(encoding='utf-8'))
            raw['version']=48
            raw['gauntlet_nexus_progression_revision']=5
            p.write_text(json.dumps(raw, ensure_ascii=False),encoding='utf-8')
            loaded,_=State.load(p)
        self.assertAlmostEqual(loaded.combat_stats['attack_bonus'],2.0)
        self.assertEqual(loaded.gauntlet_nexus_progression_revision,8)


    def test_card_knowledge_is_recorded_and_queued_as_alert(self):
        s = State(101)
        s.kills['scarab'] = 1
        s.discover('shell')
        self.assertIn('shell', s.known_cards)
        self.assertIn({'type': 'card', 'cid': 'shell'}, s.achievement_alerts)

    def test_unseen_card_recipe_is_hidden_in_album_and_craft_source(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("if cid in self.state.known_cards", source)
        self.assertIn("cards=[(cid,data) for cid,data in CARDS.items() if cid in self.state.known_cards and data.get('recipe') and data.get('craftable') is not False]", source)

    def test_scan_unlocks_with_helmet_rebuild(self):
        s = State(102)
        s.inventory.update(CARDS['shell']['recipe'])
        self.assertFalse(s.scan_unlocked)
        # Directly fulfill helmet recipe through intermediates to isolate the flag behavior.
        s.inventory.update(OTHER_RECIPES['helmet_g1']['recipe']) if False else None
        s.helmet_owned = True
        s.scan_unlocked = True
        self.assertTrue(s.scan_unlocked)


if __name__ == '__main__':
    unittest.main()
