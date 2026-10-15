import unittest
from pathlib import Path
from content import UNIQUE_BUFF_DEFS
from core import State

class Hotfix070Tests(unittest.TestCase):
    def test_unique_attack_buff_is_percentage(self):
        self.assertEqual(UNIQUE_BUFF_DEFS['attack']['value'], 4.0)
        s = State(701)
        cid='unique|Terra|normal|1'
        s.unique_cards[cid]={'buffs':[{'kind':'attack'}]}
        s.gauntlet_special_slot=cid
        s.crafted=['shell|normal|1','bite|normal|2','static|normal|1']
        s.slots=['shell|normal|1','bite|normal|2','static|normal|1']
        attrs=s.player_attributes()
        self.assertAlmostEqual(attrs['attack'], 13.68, places=2)


    def test_ui_hotfix_contracts_are_present(self):
        source = Path('main.py').read_text()
        self.assertIn("if self.craft_reward_card_id or self.unique_gacha_card_id:", source)
        self.assertIn("self.craft_reward_card_id = None", source)
        self.assertIn("self._draw_scroll_text_box((922,215,165,215),detail,'card_picker_preview'", source)
        self.assertIn("if self.mode == 'gauntlet' and self.card_picker_slot is not None:", source)
        self.assertIn("self._unique_buff_text", source)
        self.assertIn("return f'+{value:g}% ATQ por carta do tipo'", source)

    def test_unique_equip_replaces_old_slot_without_remover(self):
        s=State(702)
        first='unique|Terra|normal|1'; second='unique|Fogo|plus|2'
        s.unique_cards[first]={'name':'Carta Única — Terra','element':'Terra','variant':'normal','rarity':'Única','buffs':[]}
        s.unique_cards[second]={'name':'Carta Única — Fogo','element':'Fogo','variant':'plus','rarity':'Única','buffs':[]}
        s.crafted=[first,second]
        ok,_=s.equip_unique(first); self.assertTrue(ok)
        ok,_=s.equip_unique(second); self.assertTrue(ok)
        self.assertEqual(s.gauntlet_special_slot, second)

if __name__=='__main__':
    unittest.main()
