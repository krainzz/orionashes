import unittest
from pathlib import Path

from content import CARDS, VERSION, UNIQUE_CARD_ESSENCE_COST
from core import State


class CraftHotfix065Tests(unittest.TestCase):
    def _ready_state(self, cid):
        s = State(1)
        s.inside_ship = True
        card = CARDS[cid]
        species = card.get('species')
        if species in s.bosses:
            s.bosses[species]['defeated'] = True
        else:
            s.kills[species] = 1
        s.discover(cid)
        for item, qty in card.get('recipe', {}).items():
            s.inventory[item] = qty
        return s

    def test_card_buttons_have_a_working_state_craft_path(self):
        s = self._ready_state('basalt_charge')
        before = len(s.crafted)
        msg = s.craft('basalt_charge')
        self.assertTrue(msg.startswith('Carta fabricada'))
        self.assertEqual(len(s.crafted), before + 1)

    def test_craft_can_consume_essence_from_ship_storage(self):
        # Regression guard for the UI/state mismatch: recipe validation and
        # deduction must use the same essence total as the Workshop.
        s = self._ready_state('alphor_fireball')
        recipe = CARDS['alphor_fireball']['recipe']
        essence_cost = recipe.get('Essência', 0)
        if essence_cost:
            s.inventory['Essência'] = 0
            s.essence_storage = essence_cost
            msg = s.craft('alphor_fireball')
            self.assertTrue(msg.startswith('Carta fabricada'))
            self.assertEqual(s.essence_storage, 0)
        else:
            self.skipTest('Recipe has no Essência in current content catalog.')

    def test_main_has_craft_reward_popup_and_card_snapshot(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def draw_craft_reward_popup(self):', source)
        self.assertIn('self.craft_reward_card_id = created', source)
        self.assertIn("'RECOMPENSA FABRICADA'", source)
        self.assertIn('self.draw_craft_reward_popup()', source)

    def test_version_is_066(self):
        self.assertEqual(VERSION, '0.6.9')


if __name__ == '__main__':
    unittest.main()

class CraftHotfix065UiRegressionTests(unittest.TestCase):
    def test_regular_craft_ui_uses_dedicated_handler_and_ship_gate(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def _craft_card_ui(self, cid):', source)
        self.assertIn("self.button((980,y+51,165,40),'FABRICAR',lambda c=cid:self._craft_card_ui(c),can,subtitle)", source)
        self.assertIn("can=bool(not self.state.battle and enough_materials and acquisition_ok)", source)
        self.assertNotIn("'DISPONÍVEL NA NAVE'", source)

    def test_unique_craft_reaches_state_and_popup_path(self):
        s = State(1)
        s.inside_ship = True
        cid = 'basalt_charge'
        card = CARDS[cid]
        s.kills[card['species']] = 1
        s.discover(cid)
        s.crafted.append(cid)
        s.essence_storage = UNIQUE_CARD_ESSENCE_COST
        result, msg = s.craft_unique_card(cid)
        self.assertIsNotNone(result)
        self.assertTrue(msg.startswith('Carta Única de Terra criada'))
        self.assertIn(result['card_id'], s.crafted)
        self.assertNotIn(cid, s.crafted)

    def test_unique_popup_draws_actual_card_preview(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("self.card_frame(cr,'Única')", source)
        self.assertIn("self.draw_element_symbol(card.get('type'),art_box.center,26,glow=True)", source)
        self.assertIn("'CARTA ÚNICA FABRICADA'", source)

    def test_failed_craft_has_visible_feedback_path_in_card_panel(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def _show_craft_notice(self, message, seconds=3.6):', source)
        self.assertNotIn("'Fabricação de cartas disponível junto à nave.'", source)
        self.assertIn("self.draw_craft_notice()", source)

