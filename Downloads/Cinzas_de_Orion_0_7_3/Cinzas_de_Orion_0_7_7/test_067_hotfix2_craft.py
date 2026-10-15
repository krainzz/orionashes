import unittest
from core import State


class CraftOutputHotfixTests(unittest.TestCase):
    def test_kit_is_received_after_craft(self):
        s = State()
        s.inventory['Sucata'] = 10
        before = dict(s.inventory)
        msg = s.craft('kit')
        self.assertIn('Kit de reparo fabricado', msg)
        self.assertEqual(s.inventory['Sucata'], before['Sucata'] - 3)
        self.assertEqual(s.inventory['Kit'], before.get('Kit', 0) + 1)

    def test_intermediate_items_are_received_after_craft(self):
        s = State()
        s.inventory.update({'Enzima': 2, 'Secreção': 2, 'Sucata': 30, 'Carapaça': 12})
        s.craft('decoder_core')
        s.craft('energy_cell')
        self.assertEqual(s.inventory['Enzima'], 1)
        self.assertEqual(s.inventory['Secreção'], 1)
        self.assertEqual(s.inventory['Núcleo de decodificação'], 1)
        self.assertEqual(s.inventory['Sucata'], 0)
        self.assertEqual(s.inventory['Carapaça'], 0)
        self.assertEqual(s.inventory['Célula de energia instável'], 1)

    def test_pure_water_is_received_and_duplicate_purifier_craft_does_not_consume(self):
        s = State()
        s.inventory.update({'Sucata': 50, 'Filamento': 10, 'Núcleo': 4, 'Placa': 2, 'Água Bruta': 10, 'Cristal de sintonia': 1})
        s.craft('water_purifier')
        before = dict(s.inventory)
        msg = s.craft('water_purifier')
        self.assertIn('já está instalado', msg)
        self.assertEqual(s.inventory, before)
        s.craft('pure_water')
        self.assertEqual(s.inventory['Água Pura'], 5)

    def test_every_consumable_craft_has_a_real_output(self):
        s = State()
        s.inventory.update({
            'Sucata': 500,
            'Placa': 100,
            'Núcleo': 100,
            'Enzima': 100,
            'Secreção': 100,
            'Carapaça': 100,
            'Filamento': 100,
            'Água Bruta': 100,
            'Cristal de sintonia': 100,
            'Microchip': 100,
            'Essência': 1000,
        })
        # Water system first, then each plain inventory-output recipe.
        s.craft('water_purifier')
        checks = [
            ('kit', 'Kit'),
            ('decoder_core', 'Núcleo de decodificação'),
            ('energy_cell', 'Célula de energia instável'),
            ('pure_water', 'Água Pura'),
            ('simulation_charge', 'Carga de Simulação'),
        ]
        s.simulator_unlocked = True
        s.simulator_built = True
        for cid, output in checks:
            before = s.inventory.get(output, 0)
            msg = s.craft(cid)
            self.assertNotIn('Projeto de fabricação sem destino definido', msg)
            self.assertGreater(s.inventory.get(output, 0), before, cid)

    def test_memory_g3_and_locomotion_have_explicit_outputs(self):
        s = State()
        s.chest_generation = 3
        s.memory_owned['advanced'] = 1
        s.inventory.update({'Sucata': 100, 'Núcleo': 100, 'Célula mnêmica': 20, 'Núcleo de ressonância': 5,
                            'Liga meteórica': 10, 'Composto de pressão': 10, 'Filamento criônico': 10})
        before_adv = s.memory_owned['advanced']
        self.assertIn('Circuito de memória fabricado', s.craft('memory_g3'))
        self.assertEqual(s.memory_owned['advanced'], before_adv + 1)
        self.assertIn('Módulo de Locomoção', s.craft('locomotion_g1'))
        self.assertEqual(s.locomotion_generation, 1)
        self.assertTrue(s.locomotion_equipped)


if __name__ == '__main__':
    unittest.main()
