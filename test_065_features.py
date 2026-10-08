import tempfile
import unittest
from pathlib import Path

from content import CREATURE_TYPES, CARDS, UNIQUE_MOMENTUM_CHANCE, UNIQUE_MOMENTUM_DEFS, VERSION
from core import State


class FixedRng:
    def __init__(self, values=None, randint_value=None):
        self.values=list(values or [])
        self.randint_value=randint_value
    def random(self):
        return self.values.pop(0) if self.values else 0.0
    def randint(self,a,b):
        if self.randint_value is None:
            return a
        return max(a,min(b,int(self.randint_value)))


class Version065MomentumTests(unittest.TestCase):
    def test_version_and_momentum_catalog(self):
        self.assertEqual(VERSION, '0.6.9')
        self.assertAlmostEqual(UNIQUE_MOMENTUM_CHANCE, 0.05)
        self.assertEqual(set(UNIQUE_MOMENTUM_DEFS), {'crit_rate','crit_damage','memory','amp'})
        self.assertEqual(set(CREATURE_TYPES), {'Terra','Metal','Fogo','Água','Elétrico','Planta','Luz','Trevas'})

    def test_momentum_roll_is_independent_and_optional(self):
        s=State(1)
        s.rng=FixedRng([0.10])
        self.assertIsNone(s._roll_unique_momentum())
        s.rng=FixedRng([0.01,0.0])
        self.assertEqual(s._roll_unique_momentum(), 'crit_rate')
        s.rng=FixedRng([0.01,0.26])
        self.assertEqual(s._roll_unique_momentum(), 'crit_damage')
        s.rng=FixedRng([0.01,0.51])
        self.assertEqual(s._roll_unique_momentum(), 'memory')
        s.rng=FixedRng([0.01,0.76])
        self.assertEqual(s._roll_unique_momentum(), 'amp')

    def _prepare_unique(self, momentum='crit_rate'):
        s=State(1)
        s.inside_ship=True
        s.crafted=['shell|normal|1','bite|normal|2']
        s.slots=['shell|normal|1','bite|normal|2',None]
        cid='unique|Terra|normal|1'
        s.crafted.append(cid)
        s.unique_cards[cid]={'name':'Carta Única — Terra','element':'Terra','variant':'normal','rarity':'Única','buffs':[],'momentum':momentum,'species':None,'description':'','source_card':'shell|normal|1'}
        s.gauntlet_special_slot=cid
        return s

    def test_momentum_crit_rate_applies_only_to_matching_element_attack(self):
        s=self._prepare_unique('crit_rate')
        profile=s._player_attack_profile('shell|normal|1')
        self.assertEqual(profile[2], 30.0)  # base 5 + Momentum 25
        s.gauntlet_special_slot=None
        self.assertEqual(s._player_attack_profile('shell|normal|1')[2], 5.0)

    def test_momentum_crit_damage_and_amp_scale_by_matching_cards(self):
        s=self._prepare_unique('crit_damage')
        profile=s._player_attack_profile('shell|normal|1')
        self.assertAlmostEqual(profile[3], 2.50)  # 1.50 base + 0.50 per Terra card
        s.unique_cards['unique|Terra|normal|1']['momentum']='amp'
        profile=s._player_attack_profile('shell|normal|1')
        self.assertAlmostEqual(profile[6], 11.4)  # 1 global + 5 skill + 5 momentum? shell skill has 4.0
        # The actual skill AMP is reported in profile[6], and should include +5% per matching card.
        self.assertGreaterEqual(profile[6], 10.0)

    def test_momentum_memory_recovers_one_point_when_matching_attack_is_used(self):
        s=self._prepare_unique('memory')
        s.start_battle(0)
        s.memory=s.max_memory
        before=s.memory
        # Fixed RNG: target hit, fixed skill roll, noncritical.
        s.rng=FixedRng([0.0, 0.0, 0.99, 0.99, 0.99], randint_value=1)
        result=s.action('shell|normal|1','body')
        self.assertTrue(result['ok'])
        self.assertEqual(result['momentum_kind'],'memory')
        self.assertEqual(s.memory, min(s.max_memory, before-int(CARDS['shell']['cost'])+1))

    def test_momentum_persists_and_old_unique_cards_default_to_none(self):
        s=self._prepare_unique('amp')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'save.json'
            s.save(path, refresh=False)
            loaded,msg=State.load(path)
        self.assertEqual(loaded.unique_cards['unique|Terra|normal|1'].get('momentum'), 'amp')
        self.assertIn('0.6.9', msg)

    def test_main_declares_all_element_symbols_and_hack(self):
        source=Path(__file__).with_name('main.py').read_text(encoding='utf-8')
        for element in ('Fogo','Água','Planta','Terra','Metal','Elétrico','Luz','Trevas'):
            self.assertIn(f"'{element}'", source)
        self.assertIn('def draw_element_symbol(self, element, center, size, glow=False):', source)
        self.assertIn('def hack_inventory(self):', source)
        self.assertIn("+ 20000", source)
        self.assertIn("+ 100", source)


if __name__ == '__main__':
    unittest.main()
