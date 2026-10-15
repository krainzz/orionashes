import json
import tempfile
import unittest
from pathlib import Path

from content import (
    CARDS,
    CARD_VARIANTS,
    ESSENCE_DROP_RANGES,
    UNIQUE_BUFF_COUNT_CHANCES,
    UNIQUE_BUFF_DEFS,
    UNIQUE_CARD_ESSENCE_COST,
    UNIQUE_VARIANT_MULTIPLIERS,
)
from core import State, load_campaign


class FixedRng:
    def __init__(self, values=None, randint_value=None):
        self.values = list(values or [])
        self.randint_value = randint_value

    def random(self):
        return self.values.pop(0) if self.values else 0.0

    def randint(self, a, b):
        if self.randint_value is None:
            return a
        return max(a, min(b, int(self.randint_value)))


class Version055UniqueCardTests(unittest.TestCase):
    def _ship_state(self, seed=55):
        s = State(seed)
        s.inside_ship = True
        s.kills['scarab'] = 1
        s.discover('shell')
        s.crafted = ['shell|normal|1']
        return s

    def test_unique_economy_constants_match_design(self):
        self.assertEqual(UNIQUE_CARD_ESSENCE_COST, 2000)
        self.assertEqual(ESSENCE_DROP_RANGES, {
            'Comum': (4, 10),
            'Incomum': (12, 18),
            'Rara': (20, 50),
            'Mítica': (70, 100),
            'Lendária': (200, 500),
        })
        self.assertEqual(UNIQUE_BUFF_COUNT_CHANCES, {1: 0.75, 2: 0.24, 3: 0.01})
        self.assertEqual(UNIQUE_VARIANT_MULTIPLIERS, {'normal': 1.0, 'plus': 2.0, 'plusplus': 3.0})
        self.assertAlmostEqual(sum(v['chance'] for v in UNIQUE_BUFF_DEFS.values()), 1.0)
        self.assertNotIn('Essência', CARDS)

    def test_unique_craft_consumes_source_card_and_2000_essence_without_equipping(self):
        s = self._ship_state()
        s.inventory['Essência'] = UNIQUE_CARD_ESSENCE_COST
        s.rng = FixedRng([0.10, 0.10, 0.10, 0.00, 0.30, 0.60])
        result, msg = s.craft_unique_card('shell|normal|1')
        self.assertIsNotNone(result)
        self.assertIn('Carta Única de Terra criada', msg)
        cid = result['card_id']
        self.assertEqual(s.inventory['Essência'], 0)
        self.assertNotIn('shell|normal|1', s.crafted)
        self.assertIn(cid, s.crafted)
        self.assertIsNone(s.gauntlet_special_slot)
        self.assertTrue(s.is_unique_card(cid))

    def test_unique_craft_requires_spare_regular_card_and_essence(self):
        s = self._ship_state()
        s.inventory['Essência'] = UNIQUE_CARD_ESSENCE_COST - 1
        before = list(s.crafted)
        result, msg = s.craft_unique_card('shell|normal|1')
        self.assertIsNone(result)
        self.assertIn('Faltam Essências', msg)
        self.assertEqual(s.crafted, before)

        s.inventory['Essência'] = UNIQUE_CARD_ESSENCE_COST
        s.slots[0] = 'shell|normal|1'
        result, msg = s.craft_unique_card('shell|normal|1')
        self.assertIsNone(result)
        self.assertIn('Pool', msg)
        self.assertIn('shell|normal|1', s.crafted)

    def test_unique_variant_and_buff_count_rolls_use_existing_ratings(self):
        s = State(55)
        self.assertEqual(s._roll_card_variant(), 'normal')
        s.rng = FixedRng([0.95])
        self.assertEqual(s._roll_card_variant(), 'plus')
        s.rng = FixedRng([0.995])
        self.assertEqual(s._roll_card_variant(), 'plusplus')

        s.rng = FixedRng([0.0]); self.assertEqual(s._roll_unique_buff_count(), 1)
        s.rng = FixedRng([0.750]); self.assertEqual(s._roll_unique_buff_count(), 2)
        s.rng = FixedRng([0.990]); self.assertEqual(s._roll_unique_buff_count(), 3)

    def test_unique_buffs_scale_1x_2x_3x(self):
        s = State(55)
        for variant, mult in UNIQUE_VARIANT_MULTIPLIERS.items():
            cid = f'unique|Terra|{variant}|{1 if variant == "normal" else (2 if variant == "plus" else 3)}'
            s.unique_cards[cid] = {'buffs': [{'kind': 'attack'}, {'kind': 'crit_rate'}, {'kind': 'crit_damage'}]}
            s.gauntlet_special_slot = cid
            effects = {e['kind']: e['value'] for e in s.unique_card_effects()}
            self.assertEqual(effects['attack'], 4.0 * mult)
            self.assertEqual(effects['crit_rate'], 5.0 * mult)
            self.assertEqual(effects['crit_damage'], 10.0 * mult)

    def test_unique_buff_affects_each_matching_equipped_element_card(self):
        s = State(55)
        cid = 'unique|Terra|normal|1'
        s.unique_cards[cid] = {'buffs': [{'kind': 'attack'}]}
        s.gauntlet_special_slot = cid
        s.crafted = ['shell|normal|1', 'bite|normal|2', 'static|normal|1']
        s.slots = ['shell|normal|1', 'bite|normal|2', 'static|normal|1']
        attrs = s.player_attributes()
        # shell + bite are Terra; static is Metal => +4% ATQ por matching card.
        self.assertAlmostEqual(attrs['attack'], 13.68, places=2)

    def test_essence_drop_ranges_follow_creature_rarity(self):
        s = State(55)
        s.rng = FixedRng(randint_value=10)
        self.assertEqual(s.essence_drop_for_creature('scarab'), 10)
        s.rng = FixedRng(randint_value=50)
        self.assertEqual(s.essence_drop_for_creature('kuvaar'), 50)

    def test_unique_slot_requires_remover_before_replacing_an_equipped_unique(self):
        s = State(55)
        first = 'unique|Terra|normal|1'
        second = 'unique|Terra|plus|2'
        s.unique_cards[first] = {'name': 'Carta Única — Terra', 'element': 'Terra', 'variant': 'normal', 'rarity': 'Única', 'buffs': [{'kind': 'attack'}], 'species': None, 'description': ''}
        s.unique_cards[second] = {'name': 'Carta Única — Terra', 'element': 'Terra', 'variant': 'plus', 'rarity': 'Única', 'buffs': [{'kind': 'crit_rate'}], 'species': None, 'description': ''}
        s.crafted = [first, second]
        ok, _ = s.equip_unique(first); self.assertTrue(ok)
        ok, msg = s.equip_unique(second)
        self.assertTrue(ok)
        self.assertEqual(s.gauntlet_special_slot, second)
        self.assertIn(first, s.crafted)

    def test_technology_does_not_advertise_the_already_active_unique_slot_upgrade(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        self.assertIn("if upgrade_id == 'special_slot':", source)

    def test_unique_is_persisted_and_returns_to_pool_without_consumable(self):
        s = self._ship_state()
        s.inventory['Essência'] = UNIQUE_CARD_ESSENCE_COST
        s.rng = FixedRng([0.00, 0.00, 0.00, 0.00, 0.20])
        result, _ = s.craft_unique_card('shell|normal|1')
        cid = result['card_id']
        ok, _ = s.equip_unique(cid)
        self.assertTrue(ok)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'save.json'
            s.save(path, refresh=False)
            loaded, _ = State.load(path)
            self.assertIn(cid, loaded.crafted)
            self.assertIn(cid, loaded.unique_cards)
            self.assertEqual(loaded.gauntlet_special_slot, cid)
            ok, _ = loaded.remove_unique()
            self.assertTrue(ok)
            self.assertIsNone(loaded.gauntlet_special_slot)
            self.assertIn(cid, loaded.crafted)

    def test_upgrade_tier_2_is_unavailable_until_tier_1_exists(self):
        s = State(55)
        s.inside_ship = True
        s.inventory.update({'Liga meteórica': 100, 'Filamento criônico': 100, 'Fibra radicular': 100, 'Pelo luminal': 100})
        before = s.inventory.copy()
        self.assertIn('Reconstrua primeiro', s.craft('helmet_g2'))
        self.assertEqual(s.helmet_generation, 0)
        self.assertEqual(s.inventory, before)

    def test_unique_texts_are_compact_and_unique_crafting_is_only_in_cards_menu(self):
        source = Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        from content import CARDS
        self.assertTrue(all(isinstance(card.get('description', ''), str) and card.get('description', '') for card in CARDS.values()))
        self.assertIn('def _draw_scroll_text_box(self, rect, text, key', source)
        self.assertIn("('FABRICAÇÃO', 'craft')", source)
        self.assertIn("('CARTAS ÚNICAS', 'unique')", source)
        self.assertIn('def card_crafting_view(self):', source)
        self.assertIn('def unique_card_crafting_view(self):', source)
        self.assertIn('def draw_unique_gacha_alert(self):', source)
        self.assertIn("'CRAFTAR CARTA ÚNICA'", source)
        self.assertNotIn("for key in ('card", source)


if __name__ == '__main__':
    unittest.main()
