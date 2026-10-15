import unittest
from pathlib import Path

import content


class Version068FeatureTests(unittest.TestCase):
    def test_version_is_068(self):
        self.assertEqual(content.VERSION, '0.6.9')

    def test_single_instance_workshop_filter_exists(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def _craft_is_single_instance_built(self, cid):', source)
        for cid in ('gauntlet_nexus', 'helmet_g1', 'helmet_g2', 'chest_g2', 'chest_g3', 'locomotion_g1', 'respawn_tank', 'combat_simulator', 'water_purifier'):
            self.assertIn(repr(cid), source[source.index('def _craft_is_single_instance_built'):source.index('def craft_entries', source.index('def _craft_is_single_instance_built'))])
        block = source[source.index('def craft_entries'):source.index('def _craft_category', source.index('def craft_entries'))]
        self.assertIn('if self._craft_is_single_instance_built(cid): continue', block)

    def test_combat_slots_show_cards_and_tooltip_unique_effects(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = source[source.index('def battle_view'):source.index('def select_battle_target', source.index('def battle_view'))]
        self.assertIn('card_y, card_w, card_h, gap = 535, 210, 118, 10', block)
        self.assertIn("self.draw_element_symbol(card.get('type'), (art.right-10, art.y+10), 5)", block)
        self.assertIn("self.wrap(card.get('description','Sem descrição.'),tx+14,ty+34,557,10,INK,13)", block)
        self.assertIn("EFEITOS DA CARTA ÚNICA", block)
        self.assertIn("'Momentum - '+UNIQUE_MOMENTUM_DEFS[momentum]['description'].format(type=element)", block)
        self.assertIn("self.button((util_x,545,147,34)", block)
        self.assertIn("self.button((util_x,587,147,34)", block)
        self.assertNotIn('TAB  alternar ponto de impacto', block)

    def test_basic_slot_is_neutral(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = source[source.index('if idx == 0:'):source.index('slot_idx=idx-1', source.index('if idx == 0:'))]
        self.assertIn("'RAIO DE PLASMA'", block)
        self.assertNotIn("draw_element_symbol('Elétrico'", block)

    def test_staged_combat_narration_is_present(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        for phrase in ('Você usou {action_name}.', '{enemy_name} utilizou {enemy_attack}.'):
            self.assertIn(phrase, source)
        self.assertIn('self.phase_time >= .66', source)
        self.assertIn('self.phase_time >= 1.08', source)


if __name__ == '__main__':
    unittest.main()
