import unittest
from pathlib import Path

from content import VERSION


class Version067FeatureTests(unittest.TestCase):
    def test_version_is_067(self):
        self.assertEqual(VERSION, '0.6.9')

    def test_collection_contains_only_regular_cards(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = source[source.index('    def card_collection_view(self):'):source.index('    def card_crafting_view(self):')]
        self.assertIn("cards=[(cid, card, 'regular') for cid, card in CARDS.items() if cid in self.state.known_cards]", block)
        self.assertNotIn('unique_ids=', block)
        self.assertNotIn("cards += [(cid, self.state.card_data(cid)[0], 'unique')]", block)

    def test_unique_icons_are_compact(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("self.draw_element_symbol(card.get('type'), art_box.center, 12, glow=True)", source)
        self.assertIn("self.draw_element_symbol(card.get('type'),art_box.center,26,glow=True)", source)

    def test_victory_is_categorized_and_keeps_hero_portrait(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        start=source.index('    def victory(self):')
        end=source.index('    def install_dobra_core_ui(self):', start)
        block=source[start:end]
        for header in ('TURNOS','ATAQUE','CRÍTICO','DEFESA'):
            self.assertIn(f"rows.append(('header','{header}'))", block)
        self.assertIn("'turns'", source[source.index('    def _new_combat_summary(self):'):source.index('    def _record_player_combat_result', source.index('    def _new_combat_summary(self):'))])
        self.assertIn("Dano médio por turno", block)
        self.assertIn("self.actor('hero',962,535,3.25,int(self.frame*5),pose='combat')", block)
        self.assertIn("'VOLTAR AO JOGO'", block)
        self.assertIn("self._register_scrollbar('combat_result'", block)

    def test_battle_damage_feedback_has_relation_labels_and_distinct_colors(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = source[source.index('    def battle_view(self):'):source.index('    def victory(self):')]
        self.assertIn("damage_color = (248, 211, 95)", block)
        self.assertIn("damage_color = (92, 232, 178)", block)
        self.assertIn("damage_color = (226, 126, 184)", block)
        self.assertIn("'VANTAGEM'", block)
        self.assertIn("'DESVANTAGEM'", block)
        self.assertIn("'CRÍTICO!'", block)


if __name__ == '__main__':
    unittest.main()
