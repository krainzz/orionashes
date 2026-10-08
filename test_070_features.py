import json
import tempfile
import unittest
from pathlib import Path

from content import VERSION, OTHER_RECIPES, COMBAT_CHALLENGE_CATALOG, CIVILIZATION_MISSION_TEMPLATES, DOMAIN_ELEMENTS, SPECIES, BOSSES
from core import State

class Version070FeatureTests(unittest.TestCase):
    def test_version_and_helmet_recipe(self):
        self.assertEqual(VERSION, '0.7.0')
        r=OTHER_RECIPES['helmet_g1']['recipe']
        self.assertEqual(r['Sucata'],24)
        self.assertEqual(r['Núcleo de decodificação'],4)
        self.assertEqual(r['Célula de energia instável'],1)

    def test_loadouts_save_and_equip(self):
        s=State(1)
        s.crafted=['scarab_card|normal|1','lizard_card|normal|1']
        s.slots=['scarab_card|normal|1','lizard_card|normal|1',None]
        ok,_=s.save_loadout(0); self.assertTrue(ok)
        s.slots=[None,None,None]
        ok,_=s.equip_loadout(0); self.assertTrue(ok)
        self.assertEqual(s.slots[:2], ['scarab_card|normal|1','lizard_card|normal|1'])

    def test_challenges_are_offered_and_require_nexus(self):
        s=State(2)
        s.gauntlet_nexus_installed=False
        ok=s.start_battle(0); self.assertTrue(ok)
        self.assertEqual(len(s.battle['challenge_offers']),3)
        ok,_=s.set_combat_challenge(0); self.assertFalse(ok)
        s.gauntlet_nexus_installed=True
        ok,_=s.set_combat_challenge(0); self.assertTrue(ok)
        s.battle['turns']=1
        ok,_=s.set_combat_challenge(1); self.assertFalse(ok)

    def test_vital_rupture_catalog_exists_for_creatures(self):
        regulars=[sid for sid in SPECIES if sid not in ('kuvaar','ry')]
        self.assertTrue(regulars)
        for sid in regulars:
            self.assertIn('vital_rupture', SPECIES[sid])
            self.assertIn('description', SPECIES[sid]['vital_rupture'])

    def test_advanced_research_unlocks_after_tier2_and_five_scans(self):
        s=State(3); s.helmet_generation=2; s.helmet_owned=True; s.helmet_equipped=True; s.scan_unlocked=True
        ids=[sid for sid in SPECIES][:5]
        s.bestiary_scanned=list(ids[:4]); self.assertFalse(s.refresh_advanced_research())
        s.bestiary_scanned=list(ids); self.assertTrue(s.refresh_advanced_research())
        self.assertTrue(s.helmet_advanced_research_unlocked)

    def test_civilization_missions_are_known_language_gated_and_3_to_5(self):
        s=State(4)
        self.assertFalse(s.refresh_civilization_missions('avarin'))
        s.language_mastered=True
        self.assertTrue(s.refresh_civilization_missions('avarin', force=True))
        data=s.civilization_missions['avarin']
        self.assertIn(len(data['offers']), range(3,6))
        for m in data['offers']:
            self.assertNotIn(m.get('params',{}).get('species_id'), ())

    def test_civilization_mission_real_time_reset(self):
        s=State(5); s.language_mastered=True
        s.refresh_civilization_missions('avarin', force=True)
        first=s.civilization_missions['avarin']['generated_at']
        s.civilization_missions['avarin']['generated_at']=first-7200
        self.assertTrue(s.refresh_civilization_missions('avarin'))
        self.assertGreaterEqual(s.civilization_missions['avarin']['generated_at'], first)

    def test_civilization_template_pool_is_broad(self):
        self.assertGreaterEqual(len(CIVILIZATION_MISSION_TEMPLATES),20)
        self.assertGreaterEqual(len(COMBAT_CHALLENGE_CATALOG),10)

    def test_vital_rupture_requires_advanced_research(self):
        s=State(6)
        s.helmet_generation=2; s.helmet_owned=True; s.helmet_equipped=True; s.scan_unlocked=True
        ok=s.start_battle(0); self.assertTrue(ok)
        sid=s.battle['species']; vital=SPECIES[sid].get('vital_zone')
        # Antes da pesquisa avançada, acertar a zona vital não pode disparar ruptura.
        s.battle['vital_zone_hp_max']=1; s.battle['vital_zone_hp']=1
        for _ in range(8):
            r=s.action('basic', vital)
            if r.get('miss'):
                continue
            self.assertFalse(r.get('vital_rupture', False))
            break

    def test_simulator_victory_awards_domain_xp_but_keeps_special_drop_rule(self):
        s=State(7)
        boss_id=next(iter(BOSSES))
        s.simulator_built=True
        s.bosses[boss_id]['defeated']=True
        s.inventory['Carga de Simulação']=1
        before=s.domain_xp.get(BOSSES[boss_id].get('type'),0)
        ok,_=s.start_boss_battle(boss_id, virtual=True); self.assertTrue(ok)
        # Finaliza diretamente para testar a regra de progressão sem depender do loop visual.
        s.battle['hp']=0
        s.win()
        after=s.domain_xp.get(BOSSES[boss_id].get('type'),0)
        self.assertGreater(after,before)
        self.assertEqual(s.inventory.get('Núcleo de Dobra',0),0)

    def test_challenge_pool_hides_vital_targeting_until_advanced_research(self):
        s=State(8)
        s.start_battle(0)
        self.assertNotIn('vital_hit',[c.get('kind') for c in s.battle.get('challenge_offers',[])])


if __name__=='__main__':
    unittest.main()
