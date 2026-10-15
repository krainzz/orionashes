import json
import tempfile
import unittest
from pathlib import Path

from content import CARDS, HELMET_TIERS, SPECIES, ACHIEVEMENTS, creature_achievement_id, creature_achievement_data
from core import State


class Version054FeatureTests(unittest.TestCase):
    def test_helmet_tiers_use_current_tier_only_and_g2_has_first_galaxy_non_veyra_recipe(self):
        self.assertEqual((HELMET_TIERS[1]['precision'], HELMET_TIERS[1]['crit_rate']), (2, 2.0))
        self.assertEqual((HELMET_TIERS[2]['precision'], HELMET_TIERS[2]['crit_rate']), (4, 5.0))
        self.assertEqual((HELMET_TIERS[3]['precision'], HELMET_TIERS[3]['crit_rate']), (8, 10.0))
        recipe = HELMET_TIERS[2]['recipe']
        self.assertEqual(set(recipe), {'Liga meteórica','Filamento criônico','Fibra radicular','Pelo luminal'})

        s = State(1)
        s.helmet_generation = 1
        s.helmet_owned = True
        s.helmet_equipped = True
        s.combat_stats['precision'] = 10
        s.combat_stats['crit_rate'] = 5.0
        self.assertEqual(s.player_attributes()['precision'], 12)
        self.assertEqual(s.player_attributes()['crit_rate'], 7.0)
        s.helmet_generation = 2
        self.assertEqual(s.player_attributes()['precision'], 14)
        self.assertEqual(s.player_attributes()['crit_rate'], 10.0)

    def test_helmet_g2_upgrade_consumes_materials_and_unlocks_rock_scan(self):
        s = State(2)
        s.pos=[7,8]
        s.helmet_generation=1; s.helmet_owned=True; s.helmet_equipped=True; s.scan_unlocked=True
        s.inventory.update({k:v for k,v in HELMET_TIERS[2]['recipe'].items()})
        before=dict(s.inventory)
        ok,msg=s.upgrade_helmet(2)
        self.assertTrue(ok,msg)
        self.assertEqual(s.helmet_generation,2)
        self.assertTrue(s.helmet_scan_abilities()['rocks'])
        for item,q in HELMET_TIERS[2]['recipe'].items():
            self.assertEqual(s.inventory[item], before[item]-q)

    def test_creature_achievement_is_revealed_on_first_encounter_and_rewards_plus_card_at_1000(self):
        s = State(3)
        aid=creature_achievement_id('scarab')
        self.assertNotIn(aid,s.achievements)
        s.start_battle(0)
        self.assertIn(aid,s.achievements)
        self.assertFalse(s.achievements[aid]['unlocked'])
        s.battle=None
        s.kills['scarab']=999
        s.refresh_achievements()
        self.assertFalse(s.achievements[aid]['unlocked'])
        s.kills['scarab']=1000
        s.refresh_achievements()
        self.assertTrue(s.achievements[aid]['unlocked'])
        ok,msg=s.claim_achievement(aid)
        self.assertTrue(ok,msg)
        plus=[c for c in s.crafted if c.startswith('shell|plus|')]
        self.assertEqual(len(plus),1)
        self.assertEqual(s.statistics['cards_crafted']['plus'],1)
        ok,msg=s.claim_achievement(aid)
        self.assertFalse(ok)
        self.assertIn('já foi recebida',msg)

    def test_creature_achievement_save_roundtrip_preserves_dynamic_entry(self):
        s=State(4)
        s.start_battle(0)
        aid=creature_achievement_id('scarab')
        s.battle = None
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'save.json'
            s.save(p,refresh=False)
            loaded,msg=State.load(p)
        self.assertIn(aid,loaded.achievements)
        self.assertFalse(loaded.save_blocked)

    def test_routes_and_achievements_ui_use_scrollable_list_layout(self):
        source=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        routes=source[source.index('    def routes(self):'):source.index('    def combat_backdrop',source.index('    def routes(self):'))]
        self.assertIn("self.ui_scroll['routes_right']",routes)
        self.assertIn("_register_scrollbar('routes_right'",routes)
        ach=source[source.index('    def achievements(self):'):source.index('    def panel_header',source.index('    def achievements(self):'))]
        self.assertIn("achievement_category",ach)
        self.assertIn("_register_scrollbar('achievements'",ach)

    def test_helmet_config_is_reached_by_equipment_config_and_shows_scan_sections(self):
        source=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("kind == 'helmet' and self.state.helmet_owned",source)
        self.assertIn("self.open_panel('helmet_config')",source)
        self.assertIn('Scan de criaturas',source)
        self.assertIn('Scan de rochas',source)
        self.assertIn('Scan de flora',source)


if __name__=='__main__':
    unittest.main()
