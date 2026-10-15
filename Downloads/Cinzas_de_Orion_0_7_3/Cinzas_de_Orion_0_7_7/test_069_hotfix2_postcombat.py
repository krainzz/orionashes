import unittest
from pathlib import Path

from content import DOMAIN_ELEMENTS, DOMAIN_LEVEL_MAX, DOMAIN_LEVEL_XP


class Version069Hotfix2PostCombatTests(unittest.TestCase):
    def test_feature_name_is_domain_only_in_current_ui(self):
        main = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        content = Path(__file__).with_name('content.py').read_text(encoding='utf-8')
        self.assertIn("self.panel_header('DOMÍNIO'", main)
        self.assertNotIn('DOMÍNIO ELEMENTAL', main)
        self.assertNotIn('DOMÍNIO ELEMENTAL', content)

    def test_engagement_captures_nexus_and_matching_domain_xp(self):
        main = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = main[main.index('def engage'):main.index('def _combat_player_action_name')]
        for phrase in ('nexus_xp_before', 'domain_element', 'domain_xp_before'):
            self.assertIn(phrase, block)

    def test_victory_records_xp_deltas_and_remaining_to_next(self):
        main = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        victory_flow = main[main.index("if self.result.get('win'):"):main.index("if was_virtual:", main.index("if self.result.get('win'):"))]
        for phrase in ('nexus_xp_gained', 'nexus_xp_total', 'nexus_xp_to_next', 'domain_xp_gained', 'domain_xp_total', 'domain_xp_to_next'):
            self.assertIn(phrase, victory_flow)

    def test_victory_displays_progress_before_attack(self):
        main = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        block = main[main.index('def victory'):main.index('def install_dobra_core_ui', main.index('def victory'))]
        nexus_pos = block.index("rows.append(('header','NEXUS'))")
        turns_pos = block.index("rows.append(('header','TURNOS'))")
        attack_pos = block.index("rows.append(('header','ATAQUE'))")
        self.assertLess(nexus_pos, turns_pos)
        self.assertLess(turns_pos, attack_pos)
        for phrase in ('XP adquirida:', 'XP total:', 'Falta para o próximo nível:'):
            self.assertGreaterEqual(block.count(phrase), 2)

    def test_domain_progress_metadata_matches_catalog(self):
        self.assertEqual(len(DOMAIN_ELEMENTS), 8)
        self.assertEqual(max(DOMAIN_LEVEL_XP), DOMAIN_LEVEL_MAX)
        self.assertEqual(DOMAIN_LEVEL_XP[1], 2000)


if __name__ == '__main__':
    unittest.main()
