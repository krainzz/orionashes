import tempfile
import unittest
from pathlib import Path

from content import CARDS, CREATURE_TYPES, NEXUS_LEVEL_XP, NEXUS_NODES, UNIQUE_CARD_ESSENCE_COST, VERSION
from core import State


class Version066FeatureTests(unittest.TestCase):
    def _ready_card_state(self, cid):
        s = State(1)
        s.inside_ship = False
        s.pos = [20, 20]
        card = CARDS[cid]
        species = card.get("species")
        if species in s.bosses:
            s.bosses[species]["defeated"] = True
        else:
            s.kills[species] = 1
        s.discover(cid)
        for item, qty in card.get("recipe", {}).items():
            if item == "Essência":
                s.inventory[item] = qty
            else:
                s.inventory[item] = qty
        return s

    def test_version_and_card_crafting_anywhere(self):
        self.assertEqual(VERSION, "0.6.9")
        s = self._ready_card_state("basalt_charge")
        self.assertFalse(s.at_ship())
        self.assertIn("Carta fabricada", s.craft("basalt_charge"))

    def test_unique_crafting_anywhere(self):
        s = self._ready_card_state("basalt_charge")
        source = "basalt_charge|normal|1"
        s.crafted.append(source)
        s.inventory["Essência"] = UNIQUE_CARD_ESSENCE_COST
        s.essence_storage = 0
        result, message = s.craft_unique_card(source)
        self.assertIsNotNone(result)
        self.assertIn("Carta Única de Terra criada", message)
        self.assertIn(result["card_id"], s.crafted)
        self.assertNotIn(source, s.crafted)

    def test_slot_replacement_returns_previous_card_to_pool(self):
        s = State(66)
        s.crafted = ["shell|normal|1", "bite|normal|1"]
        s.slots = ["shell|normal|1", None, None]
        self.assertTrue(s.equip("bite|normal|1", 0))
        self.assertIn("shell|normal|1", s.crafted)
        self.assertEqual(s.slots[0], "bite|normal|1")
        ok, _ = s.unequip(0)
        self.assertTrue(ok)
        self.assertIsNone(s.slots[0])

    def test_unique_replacement_is_free(self):
        s = State(66)
        a = "unique|Terra|normal|1"; b = "unique|Terra|plus|2"
        s.unique_cards[a] = {"name":"Carta Única — Terra","element":"Terra","variant":"normal","rarity":"Única","buffs":[],"species":None,"description":""}
        s.unique_cards[b] = {"name":"Carta Única — Terra","element":"Terra","variant":"plus","rarity":"Única","buffs":[],"species":None,"description":""}
        s.crafted = [a,b]
        self.assertTrue(s.equip_unique(a)[0])
        self.assertTrue(s.equip_unique(b)[0])
        self.assertEqual(s.gauntlet_special_slot, b)
        self.assertIn(a, s.crafted)

    def test_nexus_50_level_progression_and_required_bonus_nodes(self):
        self.assertEqual(max(NEXUS_LEVEL_XP), 50)
        self.assertEqual(NEXUS_LEVEL_XP[20], 25_000_000)
        self.assertEqual(NEXUS_LEVEL_XP[50], 100_000_000)
        self.assertTrue(all(isinstance(v, int) for v in NEXUS_LEVEL_XP.values()))
        self.assertEqual([lv for lv,n in ((v["level"],v) for v in NEXUS_NODES.values()) if n.get("kind")=="drop"], [4,5,8,11,14])
        self.assertEqual([lv for lv,n in ((v["level"],v) for v in NEXUS_NODES.values()) if n.get("kind")=="advantage"], [6,10,18,21,27])
        self.assertEqual([lv for lv,n in ((v["level"],v) for v in NEXUS_NODES.values()) if n.get("kind")=="vampirism"], [15,24,32,40,50])
        self.assertTrue(all(NEXUS_NODES[f"nexus_level_{lv:02d}"]["value"] == 1.0 for lv in (20,31,38,47)))

    def test_old_removed_item_cannot_be_crafted(self):
        s = State(66)
        self.assertEqual(s.craft("enhancement_remover"), "Projeto de fabricação desconhecido.")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            s.inventory["Removedor de Aprimoramento"] = 3
            s.save(path, refresh=False)
            loaded, _ = State.load(path)
            self.assertNotIn("Removedor de Aprimoramento", loaded.inventory)

    def test_main_has_clean_card_craft_and_combat_result_ui(self):
        source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
        self.assertIn("can=bool(not self.state.battle and enough_materials and acquisition_ok)", source)
        self.assertNotIn("'DISPONÍVEL NA NAVE'", source)
        self.assertNotIn("'REMOVER ÚNICA'", source)
        self.assertNotIn("'REMOVER CARTA'", source)
        self.assertIn("'EQUIPAR'", source)
        self.assertIn("def victory(self):", source)
        self.assertIn("'VOLTAR AO JOGO'", source)
        self.assertIn("combat_result", source)


if __name__ == "__main__":
    unittest.main()
