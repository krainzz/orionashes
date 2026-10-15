import json
import tempfile
import unittest
from pathlib import Path

from content import BOSSES, CARDS
from core import State, load_campaign


class Version048FeatureTests(unittest.TestCase):
    def _prepare_conflict(self, path='warn'):
        s = State(123)
        s.language_mastered = True
        s.missions['water_supply'].update(status='completed', path='repair', reward_claimed=True)
        s.refresh_journal(refresh_achievement_state=False)
        self.assertEqual(s.missions['faction_conflict']['status'], 'available')
        ok, _ = s.accept_faction_conflict()
        self.assertTrue(ok)
        ok, msg = s.resolve_faction_conflict(path)
        self.assertTrue(ok, msg)
        return s

    def test_fresh_journal_has_faction_conflict_objective(self):
        s = State()
        self.assertIn('faction_conflict', s.journal['objectives'])
        self.assertEqual(s.journal['objectives']['faction_conflict']['status'], 'locked')

    def test_conflict_unlocks_after_water_mission_and_offers_two_outcomes(self):
        s = State(2)
        s.language_mastered = True
        s.missions['water_supply'].update(status='completed', path='repair', reward_claimed=True)
        s.refresh_journal(refresh_achievement_state=False)
        self.assertEqual(s.missions['faction_conflict']['status'], 'available')
        ok, msg = s.accept_faction_conflict()
        self.assertTrue(ok, msg)
        self.assertEqual(s.missions['faction_conflict']['status'], 'active')

        warn = State(3)
        warn.language_mastered = True
        warn.missions['water_supply'].update(status='completed', path='repair', reward_claimed=True)
        warn.refresh_journal(refresh_achievement_state=False)
        warn.accept_faction_conflict()
        ok, msg = warn.resolve_faction_conflict('warn')
        self.assertTrue(ok, msg)
        self.assertEqual(warn.missions['faction_conflict']['winner'], 'waterkeepers')
        self.assertEqual(warn.missions['faction_conflict']['loser'], 'rift_children')
        self.assertTrue(any(warn.card_parts(c)[0] == 'rift_break' for c in warn.crafted))

        sabotage = State(4)
        sabotage.language_mastered = True
        sabotage.missions['water_supply'].update(status='completed', path='repair', reward_claimed=True)
        sabotage.refresh_journal(refresh_achievement_state=False)
        sabotage.accept_faction_conflict()
        ok, msg = sabotage.resolve_faction_conflict('sabotage')
        self.assertTrue(ok, msg)
        self.assertEqual(sabotage.missions['faction_conflict']['winner'], 'rift_children')
        self.assertEqual(sabotage.missions['faction_conflict']['loser'], 'waterkeepers')
        self.assertTrue(any(sabotage.card_parts(c)[0] == 'lithic_sentence' for c in sabotage.crafted))

    def test_leader_cards_are_mythic_earth_non_defensive_and_kuvaar_gated(self):
        for cid in ('lithic_sentence', 'rift_break'):
            card = CARDS[cid]
            self.assertEqual(card['rarity'], 'Mítica')
            self.assertEqual(card['type'], 'Terra')
            self.assertEqual(card['attributes'].get('defense', 0), 0)
            self.assertIn('Núcleo de Kuvaar', card['recipe'])
            self.assertGreaterEqual(card['recipe']['Núcleo de Kuvaar'], 1)
        self.assertEqual(CARDS['lithic_sentence']['recipe']['Núcleo de Kuvaar'], 1)
        self.assertEqual(CARDS['rift_break']['recipe']['Núcleo de Kuvaar'], 1)

    def test_winner_card_is_craftable_only_after_conflict_and_loser_card_is_reward_only(self):
        s = State(5)
        s.language_mastered = True
        # Before the conflict, both cards are explicitly unavailable.
        for cid in ('lithic_sentence', 'rift_break'):
            s.inventory.update(CARDS[cid]['recipe'])
            self.assertIn('origem desta carta', s.craft(cid).lower())
        s.inventory.clear()
        s.inventory.update({'Núcleo de Kuvaar': 1, 'Cristal de Sal': 12, 'Sucata': 36, 'Placa': 18, 'Carapaça': 16})
        s.missions['water_supply'].update(status='completed', path='repair')
        s.refresh_journal(refresh_achievement_state=False)
        s.accept_faction_conflict()
        s.resolve_faction_conflict('warn')
        # rift_break is the loser and cannot be crafted; lithic_sentence is the winner.
        deny = s.craft('rift_break')
        self.assertIn('consequência direta', deny.lower())
        crafted_before = list(s.crafted)
        ok_message = s.craft('lithic_sentence')
        self.assertIn('Sentença Litônica', ok_message)
        self.assertGreater(len(s.crafted), len(crafted_before))

    def test_faction_hack_starts_only_at_communication_terminal(self):
        s = State(6)
        s.language_mastered = True
        s.missions['water_supply'].update(status='completed', path='repair')
        s.refresh_journal(refresh_achievement_state=False)
        s.accept_faction_conflict()
        s.sector = 'ruins'
        s.pos = [12, 10]
        ok, msg = s.start_faction_hack()
        self.assertTrue(ok, msg)
        self.assertEqual(s.hack.get('purpose'), 'faction_conflict')
        self.assertEqual(s.hack.get('terminal'), 'water_comms_terminal')

    def test_hack_success_and_failure_resolve_or_fail_conflict(self):
        s = State(7)
        s.language_mastered = True
        s.missions['water_supply'].update(status='completed', path='repair')
        s.refresh_journal(refresh_achievement_state=False)
        s.accept_faction_conflict()
        s.sector = 'ruins'; s.pos = [12, 10]
        ok, _ = s.start_faction_hack(); self.assertTrue(ok)
        h = s.hack
        # Follow a path that reaches the goal without firewalls: right, right, down, down.
        for tid in ((0, 1), (0, 2), (1, 2), (2, 2)):
            s.hack['cursor'] = list(tid)
            result = s.hack_breach()
        self.assertTrue(result.get('success'))
        self.assertEqual(s.missions['faction_conflict']['status'], 'completed')
        self.assertEqual(s.missions['faction_conflict']['path'], 'sabotage')

        f = State(8)
        f.language_mastered = True
        f.missions['water_supply'].update(status='completed', path='repair')
        f.refresh_journal(refresh_achievement_state=False)
        f.accept_faction_conflict(); f.sector='ruins'; f.pos=[12,10]
        ok, _ = f.start_faction_hack(); self.assertTrue(ok)
        # Repeatedly breach a firewall until the limit is reached.
        for _ in range(int(f.hack['alert_limit'])):
            f.hack['cursor'] = [1,0]
            f.hack_breach()
        self.assertEqual(f.missions['faction_conflict']['status'], 'failed')

    def test_kuvaar_base_stats_and_visual_fx_mapping_are_not_repurposed(self):
        self.assertEqual(BOSSES['kuvaar']['hp'], 320)
        self.assertEqual(BOSSES['kuvaar']['defense'], 30)
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("'monolith_sentence'", source)
        self.assertIn("'rift_break'", source)
        self.assertIn("self._draw_card_fx(b, hero_x, enemy_x)", source)

    def test_nexus_craft_is_explicitly_available_from_technology_when_ready(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("PRONTO PARA FABRICAÇÃO", source)
        self.assertIn("FABRICAR NEXUS", source)
        self.assertIn("self._craft_from_technology_nexus", source)
        self.assertEqual(CARDS.get('kuvaar', {}).get('type', 'Terra'), 'Terra')
        s = State(9)
        s.inventory.update({'Sucata': 8, 'Núcleo': 1, 'Placa': 1})
        self.assertFalse(s.gauntlet_nexus_installed)
        # O método de domínio continua exigindo proximidade da nave; a UI agora
        # deixa essa condição explícita em vez de esconder o projeto.
        s.inside_ship = True
        msg = s.craft('gauntlet_nexus')
        self.assertTrue(s.gauntlet_nexus_installed)
        self.assertIn('NEXUS instalado', msg)

    def test_fabrication_has_resources_button_instead_of_rest(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("'RECURSOS'", source)
        self.assertIn("open_panel('resources','craft')", source)
        self.assertNotIn("'R  Descansar e salvar', self.rest", source)

    def test_equipment_visual_is_fixed_to_front(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("self.actor('hero', 210, 276, 1.35, direction='down')", source)

    def test_side_head_has_distinct_left_and_right_orientation(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("if direction == 'right':", source)
        self.assertIn("pygame.draw.polygon(s, PX_SKIN, [(29, 9), (28, 5), (22, 4), (19, 8), (21, 13), (25, 15), (28, 13)]", source)


    def test_version_48_save_roundtrip_and_47_migration(self):
        s = self._prepare_conflict('warn')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            current = tmp / 'save_v048.json'
            s.save(current, refresh=False)
            raw = json.loads(current.read_text(encoding='utf-8'))
            self.assertEqual(raw['version'], 65)
            loaded, msg = State.load(current)
            self.assertIn('0.6.9', msg)
            self.assertEqual(loaded.missions['faction_conflict']['path'], 'warn')
            self.assertEqual(loaded.missions['faction_conflict']['loser'], 'rift_children')

            legacy = tmp / 'save_v047.json'
            legacy_data = raw.copy()
            legacy_data['version'] = 47
            legacy_data['missions'] = {k:v for k,v in raw['missions'].items() if k != 'faction_conflict'}
            legacy.write_text(json.dumps(legacy_data, ensure_ascii=False), encoding='utf-8')
            current.unlink()
            migrated, msg = load_campaign(tmp)
            self.assertFalse(migrated.save_blocked)
            self.assertIn('0.6.9', msg)
            self.assertTrue((tmp / 'save.json').exists())
            self.assertIn('faction_conflict', migrated.missions)


if __name__ == '__main__':
    unittest.main()
