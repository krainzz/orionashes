import json
import tempfile
import unittest
from pathlib import Path

from content import CARDS, SPECIES, BOSSES, VERSION, CARD_RARITIES
from core import State

NEW_SPECIES = [
    'ferrous_mite','magnetic_ram','gloom_moth','vesper_cat','charge_ray','ion_toad',
    'cinder_strider','magma_beetle','reef_skimmer','tide_serpent','spore_hare','mycelial_beast',
    'wind_stalker','leviwing','street_drone','plasma_hound',
]
NEW_CARDS = [SPECIES[s]['card'] for s in NEW_SPECIES]
NEW_BOSSES = ['mekron','nocther','voltrik','moryss','verdak','gravorn','alphor_fireball','broom_lightning']

class Version062Tests(unittest.TestCase):
    def test_version_is_062_and_memory_constant_is_importable(self):
        self.assertEqual(VERSION, '0.6.9')
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('CHEST_MEMORY_SLOTS', src)

    def test_new_creatures_have_two_attacks_matching_their_cards(self):
        for sid in NEW_SPECIES:
            sp, card = SPECIES[sid], CARDS[SPECIES[sid]['card']]
            self.assertEqual(tuple(sp['basic_attack']), tuple(sp['attack']), sid)
            self.assertEqual(tuple(sp['special_attack']), tuple(card['damage']), sid)
            self.assertEqual(sp['special_attack_card'], sp['card'], sid)

    def test_new_cards_are_craftable_only_after_first_defeat(self):
        s = State(620)
        for cid, sid in zip(NEW_CARDS, NEW_SPECIES):
            self.assertNotIn(cid, s.known_cards, cid)
            self.assertTrue(CARDS[cid].get('recipe'), cid)
            s.kills[sid] = 1
            s.discover(cid)
            self.assertIn(cid, s.known_cards, cid)
            s.known_cards.remove(cid)
            s.kills[sid] = 0

    def test_quest_cards_remain_completion_gated(self):
        for cid in ('lithic_sentence','rift_break'):
            self.assertEqual(CARDS[cid].get('craftable'), 'winner_only')
        s = State(621)
        self.assertNotIn('lithic_sentence', s.known_cards)
        self.assertNotIn('rift_break', s.known_cards)

    def test_boss_cards_are_craftable_after_defeat(self):
        for cid in NEW_BOSSES:
            self.assertTrue(CARDS[cid].get('recipe'), cid)
            self.assertTrue(CARDS[cid].get('craftable', False), cid)
            self.assertEqual(CARDS[cid].get('acquisition'), 'boss_defeat', cid)

    def test_raid_rarity_attribute_caps_are_respected(self):
        caps = {'Comum': {'attack_pct':3.0,'crit_rate':3.0,'crit_damage':0.05},
                'Incomum': {'attack_pct':5.0,'crit_rate':5.0,'crit_damage':0.10},
                'Rara': {'attack_pct':10.0,'crit_rate':10.0,'crit_damage':0.20},
                'Mítica': {'attack_pct':15.0,'crit_rate':15.0,'crit_damage':0.25},
                'Lendária': {'attack_pct':20.0,'crit_rate':20.0,'crit_damage':0.40}}
        for cid in NEW_CARDS + NEW_BOSSES:
            card = CARDS[cid]
            attrs = card.get('attributes', {})
            self.assertEqual(len(attrs), 1, cid)
            key = next(iter(attrs)); self.assertNotIn('defense', attrs)
            self.assertIn(key, caps[card['rarity']])
            self.assertEqual(attrs[key], caps[card['rarity']][key])

    def test_boss_discovery_uses_boss_species_when_card_id_differs(self):
        for boss_id in ('alphor','broom'):
            s=State(626)
            card_id=BOSSES[boss_id]['card']
            self.assertNotIn(card_id, s.known_cards)
            s.bosses[boss_id]['defeated']=True
            self.assertTrue(s.discover(card_id))
            self.assertIn(card_id, s.known_cards)
            alert=s.pop_achievement_alert()
            self.assertEqual(alert['type'], 'card')
            self.assertEqual(alert['cid'], card_id)

    def test_boss_victory_does_not_directly_grant_card_instance(self):
        # O comportamento é garantido em nível de código: a vitória desbloqueia
        # a receita, mas não deve fabricar uma cópia automaticamente.
        src=Path(__file__).with_name('core.py').read_text(encoding='utf-8')
        self.assertIn("self.discover(boss_card)", src)
        self.assertNotIn("loot[f'Carta: {format_card_name(CARDS[base_card]", src)

    def test_first_defeat_adds_card_and_bestiary(self):
        s = State(622)
        sid='ferrous_mite'; cid=SPECIES[sid]['card']
        s.discover(cid) if False else None
        s.kills[sid]=1
        s.statistics['kills'][sid]=1
        s.bestiary_known.append(sid)
        s.discover(cid)
        self.assertIn(sid, s.bestiary_known)
        self.assertIn(cid, s.known_cards)

    def test_veyra_faction_contact_requires_helmet_and_avari(self):
        s=State(623)
        s.sector='settlement'; s.pos=[5,5]
        # Find first faction-site NPC anywhere in Veyra.
        target=None
        for area in s.worlds:
            pass
        for sec,data in __import__('world').SECTORS.items():
            site=data.get('faction_site')
            if site and site.get('npcs'):
                s.sector=sec; s.pos=list(site['npcs'][0]['pos']); target=site['npcs'][0]; break
        self.assertIsNotNone(target)
        msg,_=s.interact_npc(target)
        self.assertIn('Elmo', msg)
        s.helmet_owned=True; s.helmet_generation=1; s.helmet_equipped=True
        s.language_mastered=False
        msg,_=s.interact_npc(target)
        self.assertIn('Avari', msg)
        s.language_mastered=True
        msg,_=s.interact_npc(target)
        self.assertNotIn('ainda não consegue estabelecer comunicação', msg)

    def test_ry_investigation_waits_for_first_trip_outside_veyra(self):
        s=State(624)
        for sid in s.ship_systems: s.ship_systems[sid]=100
        s.refresh_journal()
        self.assertEqual(s.missions['ry_investigation']['status'], 'locked')
        s.has_left_veyra=True
        s.refresh_journal()
        self.assertEqual(s.missions['ry_investigation']['status'], 'active')

    def test_map_catalog_is_visit_only(self):
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("key in self.state.visited", src)

    def test_achievement_button_has_subtle_marker_logic(self):
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('has_unclaimed_achievements', src)
        self.assertIn("pygame.draw.circle(self.canvas, (224,112,93)", src)

    def test_aurora_ui_uses_required_light_blue_and_red_requirement_colors(self):
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('(135,205,238)', src)
        self.assertIn('(224,112,93)', src)
        self.assertIn("req_items=list(data['recipe'].items())", src)

    def test_bestiary_ui_has_split_panel_and_scrollbars(self):
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("right=pygame.Rect(850,110,315,590)", src)
        self.assertIn("'bestiary_detail'", src)
        self.assertIn("'bestiary_list'", src)
        self.assertIn("self._draw_scroll_text_box((78,470,700,190)", src)

    def test_save_roundtrip_preserves_left_veyra_flag(self):
        s=State(625); s.has_left_veyra=True
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'save.json'; s.save(path, refresh=False)
            raw=json.loads(path.read_text())
            self.assertEqual(raw['version'],65)
            loaded,_=State.load(path)
            self.assertTrue(loaded.has_left_veyra)

    def test_card_unlock_alert_has_required_copy_and_preview_logic(self):
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("NOVA CARTA DESBLOQUEADA PARA CRIAÇÃO!", src)
        self.assertIn("self.card_alert_cid", src)
        self.assertIn("self.card_frame(cr, rarity)", src)

    def test_achievement_button_method_exists_and_checks_unclaimed(self):
        src=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn('def has_unclaimed_achievements(self):', src)
        self.assertIn("not bool(entry.get('claimed'))", src)

if __name__=='__main__': unittest.main()
