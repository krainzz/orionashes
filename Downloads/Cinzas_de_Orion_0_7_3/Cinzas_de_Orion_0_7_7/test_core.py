"""Testes sem janela e sem tocar no save real: python -m unittest -v."""
import json
from collections import deque
import tempfile
import unittest
from pathlib import Path
from core import State, load_campaign, OBJECTIVES
from content import FUTURE_RESOURCES, FUTURE_UPGRADES, SHIP_SYSTEMS, CARD_RARITIES, OTHER_RECIPES, MISSION_REWARDS, SHIP_INTERIOR, BOSSES
from content import CARDS, NODES, NODE_IDS, SPAWNS, CARD_VARIANTS, PLAYER_COMBAT, SPECIES, BOSSES, ACHIEVEMENTS, NEXUS_LEVEL_XP, NEXUS_NODES, MAX_HP
from world import SECTORS, ALL_NODE_IDS


def legacy_save(modules=0):
    """Formato real da 0.2, incluindo melhorias permanentes e timers de coleta."""
    return dict(version=2, pos=[7, 8], hp=23, memory=5, modules=modules,
                inventory={'Sucata': 47, 'Núcleo': 8, 'Kit': 3},
                crafted=['shell'], slots=['shell', None, None],
                kills={'scarab': 15, 'lizard': 2, 'drone': 1}, time=800.0,
                nodes=[120.0, 0.0, 900.0, 0.0],
                enemies=[dict(species=s, home=list(p), pos=list(p), dead=i==0, ready=850.0 if i==0 else 0.0)
                         for i, (s, p) in enumerate(SPAWNS)])


class ProgressionTests(unittest.TestCase):
    def test_only_basic_at_start(self):
        s = State(1); s.start_battle(0)
        self.assertFalse(s.action('shell')['ok'])
        self.assertIn(s.action('basic')['damage'], range(11, 14))
        self.assertEqual(s.memory, 8)

    def test_crafting_requires_analysis_and_consumes_materials(self):
        s = State(1); s.inventory.update(CARDS['shell']['recipe'])
        self.assertIn('Derrote', s.craft('shell'))
        s.kills['scarab'] = 1; s.craft('shell')
        self.assertTrue(s.card_instances('shell'))
        self.assertEqual(s.card_parts(s.crafted[-1])[0], 'shell')
        self.assertEqual(s.card_parts(s.crafted[-1])[1] in CARD_VARIANTS, True)
        self.assertIsNone(s.slots[0])
        self.assertIsNone(s.slots[1])
        s.equip(s.crafted[-1], 0)
        self.assertEqual(s.card_parts(s.slots[0])[0], 'shell')
        self.assertEqual(s.inventory['Carapaça'], 0)
        # A mesma carta pode ser fabricada novamente para buscar uma variante melhor.
        s.inventory.update(CARDS['shell']['recipe'])
        self.assertIn('Carta fabricada', s.craft('shell'))
        self.assertEqual(len(s.card_instances('shell')), 2)

    def test_card_effect_and_no_free_bestiary_bonus(self):
        s = State(2); s.crafted = ['shell']; s.slots[0] = 'shell'
        s.kills['scarab'] = 100; s.start_battle(0)
        self.assertGreater(s.action('shell')['damage'], 0)
        self.assertEqual(s.memory, 6)
        self.assertLessEqual(s.enemy_turn()['damage'], 2)
        self.assertEqual(s.battle['shield'], 0)
        s.memory = 1
        self.assertFalse(s.action('shell')['ok'])
        self.assertEqual(s.memory, 1)

    def test_respawn_timer_safe_distance_and_rest(self):
        s = State(2); s.start_battle(0)
        while s.battle['hp'] > 0:
            s.action('basic')
        s.win(); s.rest(); s.tick(59)
        self.assertTrue(s.enemies[0]['dead'])
        s.pos = s.enemies[0]['home'].copy(); s.tick(1)
        self.assertTrue(s.enemies[0]['dead'])
        s.pos = [7, 8]; s.tick(.1)
        self.assertFalse(s.enemies[0]['dead'])

    def test_finite_collection_survives_time_rest_and_reload(self):
        s = State(2); s.pos = list(NODES[0])
        self.assertIn('Coletou', s.collect())
        amount = s.inventory['Sucata']; s.tick(10000)
        self.assertIn('já recolhidos', s.collect())
        self.assertEqual(s.inventory['Sucata'], amount)
        s.pos = [7, 8]; s.rest()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'; s.save(p)
            loaded, _ = State.load(p); loaded.pos = list(NODES[0])
            self.assertIn('já recolhidos', loaded.collect())
            self.assertEqual(loaded.inventory['Sucata'], amount)
            self.assertEqual(loaded.collected_nodes, [NODE_IDS[0]])

    def test_craft_module_stores_it_without_changing_capacity(self):
        s = State(1); s.inventory.update({'Sucata': 100, 'Núcleo': 100})
        s.craft('memory')
        self.assertEqual(s.memory_owned['expanded'], 1)
        self.assertEqual(s.max_memory, 8)
        self.assertEqual(s.loose_modules('expanded'), 1)
        self.assertEqual(s.inventory['Sucata'], 88)
        self.assertEqual(s.inventory['Núcleo'], 97)
        s.craft('memory'); before = s.inventory.copy(); s.craft('memory')
        self.assertEqual(s.memory_owned['expanded'], 2)
        self.assertEqual(s.inventory, before)

    def test_remove_replace_conserves_modules_without_refilling(self):
        s = State(1); s.memory_owned['expanded'] = 1; s.memory = 3
        s.configure_memory(0, 'expanded')
        self.assertEqual(s.max_memory, 11); self.assertEqual(s.memory, 3)
        self.assertEqual(s.loose_modules('basic'), 1)
        self.assertEqual(s.loose_modules('expanded'), 0)
        self.assertIn('cópia livre', s.configure_memory(1, 'expanded'))
        s.rest(); self.assertEqual(s.memory, 11)
        s.configure_memory(0, None)
        self.assertEqual(s.memory, 4); self.assertEqual(s.max_memory, 4)
        s.configure_memory(1, None)
        self.assertEqual(s.memory, 0); self.assertEqual(s.max_memory, 0)
        s.configure_memory(0, 'expanded')
        self.assertEqual(s.memory, 0)
        self.assertEqual(s.memory_owned, {'basic': 2, 'expanded': 1, 'advanced': 0})

    def test_configuration_requires_ship_and_no_combat(self):
        s = State(2); s.pos = [0, 0]
        self.assertIn('junto à nave', s.configure_memory(0, None))
        s.pos = [7, 8]; s.start_battle(0)
        self.assertIn('fora do combate', s.configure_memory(0, None))
        self.assertEqual(s.memory_slots, ['basic', 'basic', None, None])

    def test_zero_memory_still_allows_basic_attack(self):
        s = State(1); s.configure_memory(0, None); s.configure_memory(1, None)
        s.start_battle(0)
        self.assertTrue(s.action('basic')['ok'])
        self.assertEqual(s.memory, 0)

    def test_card_swap(self):
        s = State(1); s.crafted = ['shell', 'bite']; s.slots = ['shell', 'bite', None]
        self.assertTrue(s.equip('shell', 1))
        self.assertEqual(s.slots, ['bite', 'shell', None])
        # Desde 0.6.6, retirar/equipar é gratuito; não existe mais Removedor de Aprimoramento.
        self.assertEqual(s.craft('enhancement_remover'), 'Projeto de fabricação desconhecido.')
        ok, _ = s.unequip(1)
        self.assertTrue(ok)
        self.assertEqual(s.slots, ['bite', None, None])
        s.equip('bite', 1)
        self.assertEqual(s.slots, [None, 'bite', None])

    def test_save_preserves_modules_and_cooldowns(self):
        s = State(2); s.memory_owned['expanded'] = 1; s.configure_memory(0, 'expanded')
        s.enemies[0].update(dead=True, ready=60); s.time = 20
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'; s.save(p); loaded, msg = State.load(p)
            self.assertIn('carregada', msg)
            self.assertEqual(loaded.memory_owned, s.memory_owned)
            self.assertEqual(loaded.memory_slots, s.memory_slots)
            self.assertEqual(loaded.enemies, s.enemies)
            self.assertEqual(loaded.time, 20)

    def test_migration_preserves_progress_for_all_old_upgrade_counts(self):
        for modules in range(3):
            with self.subTest(modules=modules), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp); old = directory/'save_v02.json'
                fixture = legacy_save(modules); old.write_text(json.dumps(fixture))
                before = old.read_bytes(); s, msg = load_campaign(directory)
                self.assertIn('convertido', msg); self.assertFalse(s.save_blocked)
                self.assertEqual(s.max_memory, 8+3*modules)
                self.assertEqual(s.memory, fixture['memory'])
                self.assertEqual(s.memory_owned, {'basic': 2, 'expanded': modules, 'advanced': 0})
                for key in ('hp', 'pos', 'inventory', 'time'):
                    self.assertEqual(getattr(s, key), fixture[key])
                for species, count in fixture['kills'].items():
                    self.assertEqual(s.kills[species], count)
                self.assertEqual(s.card_parts(s.slots[0])[0], 'shell')
                self.assertEqual(s.collected_nodes, [NODE_IDS[0], NODE_IDS[2]])
                self.assertEqual(s.enemies[:len(SPAWNS)], fixture['enemies'])
                self.assertEqual(old.read_bytes(), before)
                self.assertTrue((directory/'save.json').exists())
                again, _ = load_campaign(directory)
                self.assertEqual(again.memory_owned, s.memory_owned)
                self.assertEqual(old.read_bytes(), before)

    def test_invalid_current_save_is_not_overwritten_or_replaced_by_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); current = directory/'save_v047.json'
            current.write_text('{invalid')
            (directory/'save_v02.json').write_text(json.dumps(legacy_save(1)))
            s, _ = load_campaign(directory)
            self.assertTrue(s.save_blocked)
            with self.assertRaises(ValueError):
                s.save(current)
            self.assertEqual(current.read_text(), '{invalid')

    def test_duplicate_memory_module_in_save_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'save.json'; s = State(); s.save(path)
            data = json.loads(path.read_text()); data['memory_owned']['expanded'] = 1
            data['memory_slots'] = ['expanded', 'expanded']
            path.write_text(json.dumps(data))
            loaded, _ = State.load(path)
            self.assertTrue(loaded.save_blocked)

    def test_loot_remains_available_after_all_map_resources_depleted(self):
        s = State(3); s.collected_nodes = sorted(ALL_NODE_IDS); scrap = 0
        s.start_battle(0)
        self.assertTrue(s.action('flee')['escape'])
        self.assertEqual(sum(s.kills.values()), 0)
        for _ in range(100):
            s.enemies[0]['dead'] = False; s.start_battle(0); s.battle['hp'] = 0
            scrap += s.win().get('Sucata', 0)
        self.assertGreater(scrap, 0)
        self.assertEqual(set(s.collected_nodes), ALL_NODE_IDS)

    def test_sector_crossing_and_return_do_not_reset_resources_or_timers(self):
        s = State(1)
        s.enemies[0].update(dead=True, ready=200)
        s.collected_nodes.append(NODE_IDS[0])
        s.pos = [20, 10]
        self.assertTrue(s.move(1, 0)); self.assertEqual(s.sector, 'dunes')
        self.assertEqual(s.pos, [0, 10])
        s.tick(50)
        self.assertTrue(s.move(-1, 0)); self.assertEqual(s.sector, 'landing')
        self.assertTrue(s.enemies[0]['dead']); self.assertEqual(s.enemies[0]['ready'], 200)
        self.assertIn(NODE_IDS[0], s.collected_nodes)
        s.pos = [20, 10]; s.move(1, 0); s.pos = [10, 0]
        self.assertTrue(s.move(0, -1)); self.assertEqual(s.sector, 'ruins')
        self.assertTrue(s.move(0, 1)); self.assertEqual(s.sector, 'dunes')
        self.assertEqual(s.visited, ['landing', 'dunes', 'ruins'])

    def test_no_exit_through_unmarked_edge_or_during_battle(self):
        s = State(); s.pos = [20, 11]
        self.assertFalse(s.move(1, 0)); self.assertEqual(s.sector, 'landing')
        self.assertEqual(s.pos, [20, 11])
        s.pos = [20, 10]; s.start_battle(0)
        self.assertFalse(s.move(1, 0)); self.assertEqual(s.sector, 'landing')

    def test_other_sectors_have_no_invisible_ship_at_old_coordinates(self):
        s = State(); s.sector = 'dunes'; s.pos = [7, 8]; s.hp = 10
        s.inventory['Sucata'] = 100
        self.assertFalse(s.at_ship())
        s.rest(); self.assertEqual(s.hp, 10)
        self.assertIn('junto à nave', s.craft('kit'))
        self.assertIn('junto à nave', s.configure_memory(0, None))

    def test_advanced_module_requires_chest_upgrade_and_keeps_two_slots(self):
        s = State(); s.inventory.update({'Sucata': 200, 'Núcleo': 100, 'Placa': 100, 'Enzima': 100})
        before = s.inventory.copy(); before_slots = s.memory_slots.copy()
        self.assertIn('Atualize primeiro', s.craft('memory_g2'))
        self.assertEqual(s.inventory, before)
        self.assertEqual(s.memory_slots, before_slots)
        self.assertEqual(s.loose_modules('advanced'), 0)
        s.craft('chest_g2'); self.assertEqual(s.chest_generation, 2)
        self.assertEqual(s.memory_slots, before_slots)
        self.assertEqual(s.memory, 8)
        s.craft('memory_g2')
        s.configure_memory(0, 'advanced')
        self.assertEqual(s.max_memory, 14); self.assertEqual(len(s.memory_slots), 4)
        before_items = s.inventory.copy(); s.craft('chest_g2')
        self.assertEqual(s.inventory, before_items)
        s.craft('memory_g2'); s.configure_memory(1, 'advanced')
        self.assertEqual(s.max_memory, 20)
        s.rest(); self.assertEqual(s.memory, 20)

    def test_incompatible_equipment_in_save_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'; s = State(); s.save(p)
            data = json.loads(p.read_text()); data['memory_owned']['advanced'] = 1
            data['memory_slots'][0] = 'advanced'
            p.write_text(json.dumps(data)); loaded, _ = State.load(p)
            self.assertTrue(loaded.save_blocked)

    def test_records_are_finite_untranslated_and_persist_between_sectors(self):
        s = State(); s.sector = 'ruins'; s.visited += ['ruins']; s.pos = [8, 6]
        self.assertIn('Tradução pendente', s.collect())
        self.assertEqual(s.inventory['Fragmento histórico'], 1)
        s.collect(); self.assertEqual(s.inventory['Fragmento histórico'], 1)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'; s.save(p); loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(loaded.sector, 'ruins')
            self.assertEqual(loaded.inventory['Fragmento histórico'], 1)
            self.assertIn('já recolhidos', loaded.collect())

    def test_legacy_v03_migration_preserves_removed_modules_and_inventory(self):
        data = legacy_save(1); data['version'] = 3
        del data['modules']; del data['nodes']
        data.update(memory_owned={'basic':2,'expanded':1}, memory_slots=['expanded',None],
                    collected_nodes=[NODE_IDS[1]])
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); p = directory/'save_v03.json'; p.write_text(json.dumps(data))
            before = p.read_bytes(); s, _ = load_campaign(directory)
            self.assertFalse(s.save_blocked); self.assertEqual(s.max_memory, 7)
            self.assertEqual(s.memory_slots, ['expanded', None, None, None])
            self.assertEqual({k:v for k,v in s.inventory.items() if v != 0}, data['inventory'])
            self.assertEqual(s.chest_generation, 1); self.assertEqual(s.sector, 'landing')
            self.assertEqual(p.read_bytes(), before)

    def test_all_exits_collectibles_and_spawns_are_reachable(self):
        for key, data in SECTORS.items():
            with self.subTest(sector=key):
                start = data['exits'][0]['at']; visited = {start}; todo = deque([start])
                while todo:
                    x, y = todo.popleft()
                    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        p = (x+dx,y+dy)
                        if all(0 <= v < data['size'] for v in p) and p not in data['rocks'] and p not in visited:
                            visited.add(p); todo.append(p)
                for gate in data['exits']:
                    self.assertIn(gate['at'], visited)
                    self.assertTrue(any(g['target']==key and g['arrival']==gate['at'] and g['at']==gate['arrival']
                                        for g in SECTORS[gate['target']]['exits']))
                for node in data['nodes']:
                    self.assertIn(node['pos'], visited)
                for spawn in data['spawns']:
                    home = spawn.get('pos') if isinstance(spawn, dict) else spawn[1]
                    self.assertIn(home, visited)

    def test_defeat_in_ruins_returns_to_ship_with_respawn_tank(self):
        s = State(1); s.sector = 'ruins'; s.visited.append('ruins'); s.hp = 1
        s.respawn_tank_built = True
        s.worlds['dunes'][0].update(dead=True, ready=300)
        s.start_battle(0); self.assertTrue(s.enemy_turn()['defeat'])
        self.assertTrue(s.inside_ship); self.assertEqual(tuple(s.ship_pos), (6, 6))
        self.assertEqual(s.sector, 'landing'); self.assertEqual(s.pos, [7, 8])
        self.assertTrue(s.worlds['dunes'][0]['dead'])


    def test_journal_starts_with_survival_and_exploration_objectives(self):
        s = State()
        self.assertIn('arrival', s.journal['seen'])
        self.assertEqual(s.journal['objectives']['survive']['status'], 'active')
        self.assertEqual(s.journal['objectives']['explore']['progress'], 1)
        self.assertEqual(s.journal['objectives']['records']['status'], 'locked')
        self.assertEqual(s.journal['objectives']['records']['progress'], 0)

    def test_journal_unlocks_ship_and_ruins_objectives_without_language(self):
        s = State()
        self.assertTrue(s.refresh_journal())
        self.assertEqual(s.journal['objectives']['survive']['status'], 'completed')
        self.assertEqual(s.journal['objectives']['ship']['status'], 'active')
        s.visited = ['landing', 'dunes', 'ruins']
        s.sector = 'ruins'
        self.assertTrue(s.refresh_journal())
        self.assertEqual(s.journal['objectives']['unknown_signal']['status'], 'completed')
        self.assertEqual(s.journal['objectives']['records']['status'], 'active')
        self.assertTrue(any(e['id'] == 'civilization_trace' for e in s.journal['entries']))

    def test_journal_progress_persists(self):
        s = State()
        s.visited = ['landing', 'dunes', 'ruins']
        s.sector = 'ruins'
        s.inventory['Fragmento histórico'] = 2
        s.refresh_journal()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'
            s.save(p)
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(loaded.journal['objectives']['explore']['status'], 'active')
            self.assertEqual(loaded.journal['objectives']['explore']['progress'], 3)
            self.assertEqual(loaded.journal['objectives']['records']['progress'], 2)
            self.assertEqual(loaded.journal['objectives']['records']['status'], 'active')

    def test_v042_society_starts_without_discovered_settlements(self):
        s = State()
        self.assertEqual(s.society['discovered_settlements'], [])
        self.assertEqual(s.society['seen_npcs'], [])
        self.assertFalse(s.society['first_contact'])
        self.assertIn('settlement', s.journal['objectives'])
        self.assertEqual(s.journal['objectives']['settlement']['status'], 'locked')

    def test_settlement_sighting_and_npc_contact_persist(self):
        s = State()
        s.sector = 'ruins'
        s.visited = ['landing', 'dunes', 'ruins']
        s.pos = [10, 14]
        self.assertTrue(s.refresh_journal())
        self.assertEqual(s.journal['objectives']['settlement']['status'], 'active')
        s.pos = [17, 11]
        self.assertTrue(s.refresh_journal())
        self.assertEqual(s.journal['objectives']['settlement']['status'], 'completed')
        self.assertIn('qaresh', s.society['discovered_settlements'])
        npc = s.nearby_npc()
        self.assertIsNone(npc)
        s.pos = [16, 9]
        npc = s.nearby_npc()
        self.assertIsNotNone(npc)
        message, changed = s.interact_npc(npc)
        self.assertFalse(changed)
        self.assertFalse(s.society['first_contact'])
        self.assertNotIn(npc['id'], s.society['seen_npcs'])
        self.assertIn('Elmo', message)
        s.helmet_owned=True; s.helmet_generation=1; s.helmet_equipped=True; s.language_mastered=True
        message, changed = s.interact_npc(npc)
        self.assertTrue(changed)
        self.assertTrue(s.society['first_contact'])
        self.assertIn(npc['id'], s.society['seen_npcs'])
        self.assertIn('contato estabelecido', message)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'
            s.save(p)
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('qaresh', loaded.society['discovered_settlements'])
            self.assertIn(npc['id'], loaded.society['seen_npcs'])
            self.assertTrue(loaded.society['first_contact'])

    def test_npcs_are_solid_and_block_movement(self):
        s = State()
        s.sector = 'ruins'
        s.visited = ['landing', 'dunes', 'ruins']
        s.pos = [12, 9]
        self.assertTrue(s.npc_at([13, 9]))
        self.assertIsNotNone(s.nearby_npc())
        self.assertFalse(s.move(1, 0))
        self.assertEqual(s.pos, [12, 9])

    def test_qaresh_npcs_do_not_overlap_collectibles(self):
        settlement = SECTORS['ruins']['settlement']
        npc_tiles = {tuple(npc['pos']) for npc in settlement['npcs']}
        collectible_tiles = {tuple(node['pos']) for node in SECTORS['ruins']['nodes']}
        self.assertTrue(npc_tiles.isdisjoint(collectible_tiles))

    def test_v041_file_is_migrated_to_v042_and_adds_society_state(self):
        s = State()
        s.visited = ['landing', 'dunes', 'ruins']
        s.sector = 'ruins'
        s.pos = [10, 14]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            p = directory/'save_v041.json'
            data = {k: getattr(s, k) for k in ('pos', 'hp', 'memory', 'memory_owned', 'memory_slots', 'inventory', 'crafted', 'slots', 'kills', 'time', 'collected_nodes', 'worlds', 'sector', 'visited', 'chest_generation', 'journal')}
            data['version'] = 41
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            loaded, msg = load_campaign(directory)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('0.6.9', msg)
            self.assertTrue((directory/'save.json').exists())
            self.assertIn('settlement', loaded.journal['objectives'])
            self.assertEqual(loaded.journal['objectives']['settlement']['status'], 'active')
            self.assertEqual(loaded.society['discovered_settlements'], [])

    def test_v04_file_is_migrated_to_v042_without_losing_progress(self):
        s = State()
        s.inventory['Sucata'] = 47
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            p = directory/'save_v04.json'
            data = {k: getattr(s, k) for k in ('pos', 'hp', 'memory', 'memory_owned', 'memory_slots', 'inventory', 'crafted', 'slots', 'kills', 'time', 'collected_nodes', 'worlds', 'sector', 'visited', 'chest_generation')}
            data['version'] = 4
            raw = json.dumps(data, ensure_ascii=False, indent=2)
            p.write_text(raw, encoding='utf-8')
            loaded, msg = load_campaign(directory)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('0.6.9', msg)
            self.assertTrue((directory/'save.json').exists())
            self.assertEqual(loaded.inventory['Sucata'], 47)
            self.assertEqual(p.read_text(encoding='utf-8'), raw)



    def test_v044_state_has_future_equipment_layers(self):
        s = State()
        self.assertEqual(s.gauntlet_generation, 1)
        self.assertEqual(s.helmet_generation, 0)
        self.assertEqual(s.locomotion_generation, 0)
        self.assertFalse(s.helmet_equipped)
        s.helmet_generation = 1
        s.helmet_owned = True
        s.helmet_equipped = True
        self.assertTrue(s.helmet_equipped)

    def test_future_upgrade_catalog_requires_resources_not_available_in_veyra(self):
        self.assertIn('helmet_g1', FUTURE_UPGRADES)
        self.assertIn('locomotion_g1', FUTURE_UPGRADES)
        self.assertIn('Célula mnêmica', FUTURE_RESOURCES)
        self.assertIn('Cristal de sintonia', FUTURE_RESOURCES)
        future_materials = set(FUTURE_RESOURCES)
        for upgrade_id, data in FUTURE_UPGRADES.items():
            if upgrade_id in ('helmet_g1', 'gauntlet_nexus', 'combat_simulator'):
                continue
            self.assertTrue(any(material in future_materials for material in data['recipe']))

    def test_v042_file_migrates_to_v044_and_preserves_new_defaults(self):
        s = State()
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            data={k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','journal','society')}
            data['version']=42
            p=directory/'save_v042.json'
            p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            loaded,msg=load_campaign(directory)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('0.6.9',msg)
            self.assertTrue((directory/'save.json').exists())
            self.assertEqual(loaded.gauntlet_generation,1)
            self.assertEqual(loaded.helmet_generation,0)
            self.assertEqual(loaded.locomotion_generation,0)




    def test_ship_diagnostic_reports_flight_damage_and_persists(self):
        s = State()
        self.assertTrue(s.at_ship())
        rows, summary, changed = s.analyze_ship()
        self.assertTrue(changed)
        self.assertEqual(len(rows), len(SHIP_SYSTEMS))
        self.assertIn('decolagem indisponível', summary.lower())
        self.assertTrue(any(r['id'] == 'propulsion' and r['condition'] < 20 for r in rows))
        self.assertIn('ship_diagnostic', s.journal['seen'])
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'
            s.save(p)
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(loaded.ship_systems, s.ship_systems)

    def test_old_v044_without_ship_systems_gets_default_diagnostic(self):
        s = State()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'
            data={k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society')}
            data['version']=43
            p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(loaded.ship_systems, {k:v['condition'] for k,v in SHIP_SYSTEMS.items()})

    def test_helmet_equipped_state_roundtrips_through_save(self):
        s = State(); s.helmet_generation = 1; s.helmet_owned = True; s.helmet_equipped = True
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'
            s.save(p)
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertTrue(loaded.helmet_owned)
            self.assertTrue(loaded.helmet_equipped)
            self.assertEqual(loaded.helmet_generation, 1)



class CombatAndCardTests(unittest.TestCase):
    class FixedRng:
        def __init__(self, randint_value=3, random_value=0.99):
            self.randint_value = randint_value
            self.random_value = random_value
        def randint(self, a, b):
            return max(a, min(self.randint_value, b))
        def random(self):
            return self.random_value
        def choice(self, seq):
            return seq[0]

    def test_player_damage_has_range_and_crit_metadata(self):
        s = State(11)
        s.rng = self.FixedRng(5, 0.99)
        s.start_battle(0)
        result = s.action('basic')
        self.assertTrue(result['ok'])
        self.assertEqual(result['damage_min'], 3)
        self.assertEqual(result['damage_max'], 5)
        self.assertFalse(result['critical'])
        self.assertEqual(result['damage'], 13)  # 12 ATQ + 5 Skill - 4 DEF = 13

    def test_player_critical_uses_multiplier(self):
        s = State(12)
        s.rng = self.FixedRng(5, 0.0)
        s.start_battle(0)
        result = s.action('basic')
        self.assertTrue(result['critical'])
        self.assertEqual(result['raw_damage'], 5)
        self.assertEqual(result['damage'], 20)  # (12 + 1% AMP + 5 - 4), depois ×1,5

    def test_min_damage_bonus_raises_floor_without_forcing_maximum(self):
        s = State(13)
        s.combat_stats['min_damage_bonus'] = 2
        s.rng = self.FixedRng(5, 0.99)
        s.start_battle(0)
        result = s.action('basic')
        self.assertEqual((result['damage_min'], result['damage_max']), (5, 5))
        self.assertEqual(result['damage'], 13)  # 12 ATQ + 5 Skill - 4 DEF = 13

    def test_enemy_critical_can_be_reduced_by_player_stat(self):
        s = State(14)
        s.combat_stats['enemy_crit_rate_reduction'] = 100
        s.start_battle(0)
        s.battle['mana'] = 0
        s.rng = self.FixedRng(4, 0.0)
        s.hp = 36
        result = s.enemy_turn()
        self.assertFalse(result['critical'])
        self.assertEqual(result['damage'], 1)  # 5 ATQ + 0 Skill - 5 DEF

    def test_card_rarity_catalog_is_complete_and_seeded_cards_have_tiers(self):
        self.assertEqual(CARD_RARITIES, ('Comum', 'Incomum', 'Rara', 'Mítica', 'Lendária', 'Única'))
        self.assertEqual(CARDS['shell']['rarity'], 'Comum')
        self.assertEqual(CARDS['bite']['rarity'], 'Comum')
        self.assertEqual(CARDS['static']['rarity'], 'Incomum')

    def test_v043_file_migrates_to_v044_with_combat_defaults(self):
        s = State()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            data = {k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems')}
            data['version'] = 43
            p = directory/'save_v043.json'
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            loaded, msg = load_campaign(directory)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('0.6.9', msg)
            self.assertTrue((directory/'save.json').exists())
            self.assertEqual(loaded.combat_stats['damage_min'], 3)
            self.assertEqual(loaded.combat_stats['damage_max'], 5)
            self.assertEqual(loaded.combat_stats['crit_rate'], 5.0)
            self.assertEqual(loaded.combat_stats['crit_damage'], 1.50)

    def test_player_starts_with_one_percent_amp_and_attributes(self):
        s = State(21)
        attrs = s.player_attributes()
        self.assertEqual(attrs['attack'], 12)
        self.assertEqual(attrs['defense'], 5)
        self.assertEqual(attrs['amp'], 1.0)
        self.assertEqual(attrs['crit_rate'], 5.0)
        self.assertEqual(attrs['crit_damage'], 1.50)

    def test_initial_enemies_have_no_amp_and_low_critical_profile(self):
        for sp in SPECIES.values():
            self.assertEqual(sp.get('amp', 0.0), 0.0)
            self.assertLessEqual(sp.get('crit_rate', 0.0), 6.0)
            self.assertLessEqual(sp.get('crit_damage', 1.0), 1.50)

    def test_every_seeded_card_grants_at_least_one_attribute(self):
        for cid, card in CARDS.items():
            if card.get('enemy_only'):
                continue
            attrs = card.get('attributes', {})
            total = sum(float(v) for v in attrs.values())
            self.assertGreater(total, 0.0, cid)
            if cid in ('lithic_sentence', 'rift_break'):
                self.assertEqual(card.get('rarity'), 'Mítica')
        self.assertEqual(CARDS['kuvaar'].get('rarity'), 'Rara')

    def test_card_variants_use_exact_crafting_probabilities(self):
        s = State(22)
        s.pos = [7, 8]
        s.kills['scarab'] = 1
        s.inventory.update(CARDS['shell']['recipe'])
        s.rng = self.FixedRng(3, 0.949)
        result = s.craft('shell')
        self.assertIn('Impacto de Sílica', result)
        self.assertEqual(s.card_parts(s.crafted[-1])[1], 'normal')
        s.inventory.update(CARDS['shell']['recipe'])
        s.rng = self.FixedRng(3, 0.974)
        s.craft('shell')
        self.assertEqual(s.card_parts(s.crafted[-1])[1], 'plus')
        s.inventory.update(CARDS['shell']['recipe'])
        s.rng = self.FixedRng(3, 0.999)
        s.craft('shell')
        self.assertEqual(s.card_parts(s.crafted[-1])[1], 'plusplus')
        self.assertAlmostEqual(sum(v['chance'] for v in CARD_VARIANTS.values()), 1.0)

    def test_card_variants_scale_attribute_bonuses_without_changing_rarity(self):
        s = State(23)
        normal = 'shell|normal|1'
        plus = 'shell|plus|1'
        double = 'shell|plusplus|1'
        a_normal = s.card_attributes(normal)
        a_plus = s.card_attributes(plus)
        a_double = s.card_attributes(double)
        self.assertEqual(CARDS['shell']['rarity'], 'Comum')
        self.assertAlmostEqual(a_normal['attack_pct'], 3.0)
        self.assertAlmostEqual(a_plus['attack_pct'], 4.5)
        self.assertAlmostEqual(a_double['attack_pct'], 6.0)
        self.assertNotIn('defense', a_normal)

    def test_equipped_card_attributes_are_added_to_player(self):
        s = State(24)
        s.crafted = ['shell|normal|1', 'bite|normal|1']
        s.slots = ['shell|normal|1', 'bite|normal|1', None]
        attrs = s.player_attributes()
        self.assertAlmostEqual(attrs['attack'], 12.72)
        self.assertEqual(attrs['defense'], 5)
        self.assertAlmostEqual(attrs['crit_rate'], 5.0)

    def test_card_min_damage_bonus_is_applied_only_once(self):
        s = State(26)
        s.crafted = ['hound|normal|1']
        s.slots = ['hound|normal|1', None, None]
        s.start_battle(0)
        s.rng = self.FixedRng(7, 0.99)
        result = s.action('hound')
        self.assertEqual(result['damage_min'], 8)  # 7 da skill + 1 de bônus da carta.
        self.assertEqual(result['damage_max'], 10)

    def test_damage_formula_uses_attack_skill_amp_skill_and_defense(self):
        s = State(25)
        s.rng = self.FixedRng(4, 0.99)
        s.start_battle(0)
        result = s.action('shell') if False else None
        s.crafted = ['shell|normal|1']
        s.slots = ['shell|normal|1', None, None]
        result = s.action('shell')
        expected = int((12.36 + (12.36 * 1.40 / 100.0) + 7 - 4) + 0.5)
        self.assertEqual(result['base_damage'], expected)
        self.assertAlmostEqual(result['attack_base'], 12.36)
        self.assertEqual(result['target_defense'], 4)

    def test_old_v044_card_save_is_normalized_to_card_instances(self):
        s = State()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'
            data = {k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems')}
            data['version'] = 44
            data['crafted'] = ['shell']
            data['slots'] = ['shell', None, None]
            data['combat_stats'] = dict(PLAYER_COMBAT)
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(loaded.card_parts(loaded.crafted[0])[:2], ('shell','normal'))
            self.assertEqual(loaded.card_parts(loaded.slots[0])[:2], ('shell','normal'))



class Revised045Tests(unittest.TestCase):
    class FixedRng:
        def __init__(self, randint_value=1, random_value=0.0):
            self.randint_value = randint_value
            self.random_value = random_value
        def randint(self, a, b):
            return max(a, min(self.randint_value, b))
        def random(self):
            return self.random_value
        def choice(self, seq):
            return seq[0]

    def test_non_collection_achievements_never_grant_attribute_power(self):
        s = State()
        before = dict(s.combat_stats)
        s.kills['scarab'] = 1
        s.refresh_achievements()
        self.assertEqual(s.combat_stats['attack_bonus'], before['attack_bonus'])
        self.assertEqual(s.combat_stats['defense_bonus'], before['defense_bonus'])
        self.assertEqual(s.combat_stats['crit_rate_bonus'], before['crit_rate_bonus'])
        self.assertEqual(s.inventory.get('Sucata', 0), 0)
        unlocked_alert = s.pop_achievement_alert()
        self.assertEqual(unlocked_alert['type'], 'unlocked')
        self.assertEqual(unlocked_alert['aid'], 'first_blood')
        ok, msg = s.claim_achievement('first_blood')
        self.assertTrue(ok, msg)
        self.assertEqual(s.inventory.get('Sucata', 0), 3)
        claimed_alert = s.pop_achievement_alert()
        self.assertEqual(claimed_alert['type'], 'claimed')
        self.assertEqual(claimed_alert['aid'], 'first_blood')
        ok, _ = s.claim_achievement('first_blood')
        self.assertFalse(ok)

    def test_achievement_catalog_keeps_attribute_rewards_only_on_card_collection(self):
        for aid, data in ACHIEVEMENTS.items():
            if aid.startswith('card_collector_'):
                self.assertIn(data.get('reward_type'), ('stat', 'stat_and_unique'))
            else:
                self.assertEqual(data.get('reward_type'), 'item', aid)
                self.assertIn(data.get('reward_item'), ('Sucata', 'Carapaça', 'Escama', 'Placa'))
                self.assertLessEqual(int(data.get('reward_amount', 0)), 4)

    def test_legacy_045_achievement_attribute_rewards_are_removed_on_revision_migration(self):
        s = State()
        # Simula um save 0.4.5 anterior à revisão: vários feitos comuns já
        # tinham concedido atributos, enquanto a coleção normal também existia.
        s.combat_stats['attack_bonus'] = 4   # salvager + helmet + force + collector normal
        s.combat_stats['defense_bonus'] = 3   # first blood + desert survivor + waterkeeper
        s.combat_stats['crit_rate_bonus'] = 3.0 # pathfinder + clean intrusion + collector plus
        for aid in ('first_blood','desert_survivor','salvager','pathfinder','waterkeeper','helmet_rebuilt','clean_intrusion','force_of_will','card_collector_normal','card_collector_plus'):
            s.achievements[aid]['unlocked'] = True
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save_v047.json'
            data = {k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems','combat_stats','inside_ship','ship_pos','language_progress','language_mastered','missions','renown','renown_events','statistics','achievements','unique_rewards')}
            data['version'] = 45
            # Os campos NEXUS/revisão não existiam no save anterior.
            p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertEqual(loaded.combat_stats['attack_bonus'], 10)
            self.assertEqual(loaded.combat_stats['defense_bonus'], 0)
            self.assertAlmostEqual(loaded.combat_stats['crit_damage_bonus'], 0.06)
            self.assertEqual(loaded.combat_stats['crit_rate_bonus'], 0.0)
            self.assertAlmostEqual(loaded.combat_stats['amp_bonus'], 0.0)
            self.assertEqual(loaded.achievement_reward_revision, 4)

    def test_card_collection_levels_are_the_only_attribute_rewards(self):
        s = State()
        serial = 1
        for base in CARDS:
            s.crafted.append(f'{base}|normal|{serial}'); serial += 1
        s.refresh_achievements()
        self.assertEqual(s.combat_stats['attack_bonus'], 0)
        self.assertEqual(s.combat_stats['defense_bonus'], 0)
        self.assertEqual(s.combat_stats['crit_rate_bonus'], 0.0)
        self.assertEqual(s.combat_stats['crit_damage_bonus'], 0.0)
        self.assertTrue(s.achievements['card_collector_normal']['unlocked'])
        ok, _ = s.claim_achievement('card_collector_normal')
        self.assertTrue(ok)
        self.assertEqual(s.combat_stats['attack_bonus'], 10)
        s = State()
        serial = 1
        for base in CARDS:
            for variant in ('normal','plus'):
                s.crafted.append(f'{base}|{variant}|{serial}'); serial += 1
        s.refresh_achievements()
        self.assertEqual(s.combat_stats['attack_bonus'], 0)
        self.assertTrue(s.achievements['card_collector_normal']['unlocked'])
        self.assertTrue(s.achievements['card_collector_plus']['unlocked'])
        s.claim_achievement('card_collector_normal')
        s.claim_achievement('card_collector_plus')
        self.assertEqual(s.combat_stats['attack_bonus'], 10)
        self.assertEqual(s.combat_stats['defense_bonus'], 0)
        self.assertAlmostEqual(s.combat_stats['crit_damage_bonus'], 0.06)
        s = State()
        serial = 1
        for base in CARDS:
            for variant in ('normal','plus','plusplus'):
                s.crafted.append(f'{base}|{variant}|{serial}'); serial += 1
        s.refresh_achievements()
        self.assertEqual(s.combat_stats['attack_bonus'], 0)
        self.assertAlmostEqual(s.combat_stats['crit_damage_bonus'], 0.0)
        self.assertAlmostEqual(s.combat_stats['amp_bonus'], 0.0)
        for aid in ('card_collector_normal','card_collector_plus','card_collector_plusplus'):
            ok, _ = s.claim_achievement(aid)
            self.assertTrue(ok)
        self.assertEqual(s.combat_stats['attack_bonus'], 10)
        self.assertEqual(s.combat_stats['defense_bonus'], 0)
        self.assertAlmostEqual(s.combat_stats['crit_damage_bonus'], 0.06)
        self.assertEqual(s.combat_stats['crit_rate_bonus'], 0.0)
        self.assertAlmostEqual(s.combat_stats['amp_bonus'], 5.0)
        self.assertIn('prototype_unique_card', s.unique_rewards)

    def test_ship_entry_starts_away_from_airlock_and_inside_e_does_not_reset(self):
        s = State()
        s.enter_ship()
        self.assertEqual(s.ship_pos, [6, 6])
        self.assertEqual(s.ship_interaction(), None)
        # Ponto antigo [6,7] fica adjacente à escotilha; a migração deve corrigir.
        s.ship_pos = [6, 7]
        self.assertIsNone(s.ship_interaction())

    def test_nexus_installation_converts_damage_to_xp_and_levels(self):
        s = State(2)
        s.inventory.update({'Sucata':8, 'Núcleo':1, 'Placa':1})
        self.assertIn('NEXUS instalado', s.craft('gauntlet_nexus'))
        self.assertTrue(s.gauntlet_nexus_installed)
        s.start_battle(0)
        s.rng = self.FixedRng(randint_value=5, random_value=1.0)
        result = s.action('basic')
        self.assertEqual(result['nexus_xp_gained'], result['damage'])
        self.assertEqual(s.gauntlet_nexus_xp, result['damage'])
        self.assertEqual(s.gauntlet_nexus_level, 1)
        self.assertEqual(s.gauntlet_nexus_points, 0)
        self.assertEqual(s.gain_gauntlet_xp(15_000 - s.gauntlet_nexus_xp), 1)
        self.assertEqual(s.gauntlet_nexus_level, 2)
        self.assertEqual(s.gauntlet_nexus_points, 0)

    def test_nexus_progression_is_small_automatic_and_includes_hack_levels(self):
        s=State(); s.inventory.update({'Sucata':8,'Núcleo':1,'Placa':1})
        self.assertIn('NEXUS instalado', s.craft('gauntlet_nexus'))
        self.assertEqual(s.gauntlet_nexus_level,1)
        self.assertEqual(s.player_attributes()['precision'],11)
        self.assertAlmostEqual(s.player_attributes()['attack'],12.0)
        s.gain_gauntlet_xp(40_000)
        self.assertEqual(s.gauntlet_nexus_level,3)
        self.assertAlmostEqual(s.player_attributes()['attack'],14.0)
        self.assertEqual(s.gauntlet_nexus_points,0)
        self.assertFalse(any(n.get('kind')=='hack' for n in NEXUS_NODES.values()))
        self.assertEqual(max(NEXUS_LEVEL_XP), 50)
        self.assertEqual([NEXUS_NODES[f'nexus_level_{lv:02d}']['kind'] for lv in (4,6,8,11,14,18)], ['drop','advantage','drop','drop','drop','advantage'])
        s.gain_gauntlet_xp(140_000)  # chega ao nível 5
        self.assertEqual(s.gauntlet_nexus_level,5)
        self.assertEqual(s.gauntlet_nexus_drop_bonus_pct,20.0)


    def test_nexus_state_roundtrips_through_save(self):
        s=State(); s.inventory.update({'Sucata':8,'Núcleo':1,'Placa':1}); s.craft('gauntlet_nexus'); s.gain_gauntlet_xp(40_000)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'save.json'; s.save(p); loaded,_=State.load(p)
            self.assertTrue(loaded.gauntlet_nexus_installed)
            self.assertEqual(loaded.gauntlet_nexus_xp,40_000)
            self.assertEqual(loaded.gauntlet_nexus_level,3)
            self.assertEqual(loaded.gauntlet_nexus_points,0)
            self.assertEqual(loaded.gauntlet_nexus_progression_revision,8)
            self.assertEqual(loaded.gauntlet_nexus_nodes,['nexus_level_01','nexus_level_02','nexus_level_03'])
            self.assertEqual(loaded.gauntlet_nexus_progression_revision,8)


    def test_card_removal_is_free(self):
        s=State(); s.crafted=['shell','bite']; s.slots=['shell','bite',None]
        ok,msg=s.remove_card(0); self.assertTrue(ok); self.assertIsNone(s.slots[0])
        self.assertNotIn('Removedor de Aprimoramento', s.inventory)

    def test_loading_current_revision_without_nexus_fields_keeps_save_compatible(self):
        s=State()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'legacy.json'
            data={k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems','combat_stats','inside_ship','ship_pos','language_progress','language_mastered','missions','renown','renown_events','statistics','achievements','unique_rewards')}
            data['version']=45
            p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            loaded,_=State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertFalse(loaded.gauntlet_nexus_installed)
            self.assertEqual(loaded.gauntlet_nexus_level,1)


class Version045FeatureTests(unittest.TestCase):
    class FixedRng:
        def __init__(self, randint_value=1, random_value=0.0):
            self.randint_value = randint_value
            self.random_value = random_value
        def randint(self, a, b):
            return max(a, min(self.randint_value, b))
        def random(self):
            return self.random_value
        def choice(self, seq):
            return seq[0]

    def test_enemy_durability_was_increased_without_buffing_basic_enemy_damage(self):
        expected_hp = {'scarab': 90, 'lizard': 108, 'drone': 120, 'hound': 118, 'burrower': 145, 'guard': 155, 'manta': 155, 'stalker': 185}
        for sid, hp in expected_hp.items():
            self.assertEqual(SPECIES[sid]['hp'], hp)
            self.assertEqual(SPECIES[sid].get('amp', 0.0), 0.0)
            self.assertLessEqual(SPECIES[sid].get('crit_rate', 0.0), 4.0)
            self.assertLessEqual(SPECIES[sid].get('crit_damage', 1.0), 1.40)


    def test_collection_rewards_match_final_design(self):
        s = State()
        serial = 1
        for base in CARDS:
            s.crafted.append(f'{base}|normal|{serial}'); serial += 1
        s.refresh_achievements()
        self.assertTrue(s.achievements['card_collector_normal']['unlocked'])
        self.assertEqual(s.combat_stats['attack_bonus'], 0)
        self.assertEqual(s.combat_stats['defense_bonus'], 0)
        s.claim_achievement('card_collector_normal')
        self.assertEqual(s.combat_stats['attack_bonus'], 10)
        s = State(); serial = 1
        for base in CARDS:
            for variant in ('normal','plus'):
                s.crafted.append(f'{base}|{variant}|{serial}'); serial += 1
        s.refresh_achievements()
        self.assertAlmostEqual(s.combat_stats['crit_damage_bonus'], 0.0)
        s.claim_achievement('card_collector_normal')
        s.claim_achievement('card_collector_plus')
        self.assertAlmostEqual(s.combat_stats['crit_damage_bonus'], 0.06)
        s = State(); serial = 1
        for base in CARDS:
            for variant in ('normal','plus','plusplus'):
                s.crafted.append(f'{base}|{variant}|{serial}'); serial += 1
        s.refresh_achievements()
        self.assertAlmostEqual(s.combat_stats['amp_bonus'], 0.0)
        for aid in ('card_collector_normal','card_collector_plus','card_collector_plusplus'):
            s.claim_achievement(aid)
        self.assertAlmostEqual(s.combat_stats['amp_bonus'], 5.0)

    def test_nexus_has_only_offensive_nodes_and_long_progression(self):
        self.assertEqual(max(NEXUS_LEVEL_XP), 50)
        self.assertEqual(NEXUS_LEVEL_XP[20], 25_000_000)
        self.assertEqual(NEXUS_LEVEL_XP[50], 100_000_000)
        self.assertGreater(NEXUS_LEVEL_XP[20], 20_000_000)
        self.assertLessEqual(NEXUS_LEVEL_XP[20], 30_000_000)
        self.assertTrue(all(node.get('field') != 'defense_bonus' for node in NEXUS_NODES.values()))
        self.assertEqual(sum(1 for node in NEXUS_NODES.values() if node.get('kind')=='drop'),5)
        self.assertEqual(sum(1 for node in NEXUS_NODES.values() if node.get('kind')=='advantage'),5)
        self.assertEqual(sum(1 for node in NEXUS_NODES.values() if node.get('kind')=='vampirism'),5)
        self.assertEqual([NEXUS_NODES[f'nexus_level_{lv:02d}']['value'] for lv in (4,6,15,50)], [10.0,10.0,1.0,1.0])
        self.assertEqual(NEXUS_NODES['nexus_level_01']['description'], '+1 Precisão.')
        self.assertAlmostEqual(float(NEXUS_NODES['nexus_level_02']['value']), 1.0)
        self.assertAlmostEqual(float(NEXUS_NODES['nexus_level_03']['value']), 1.0)

    def test_nexus_revision4_is_sparse_and_auto_applies_without_points(self):
        s=State(); s.inventory.update({'Sucata':8,'Núcleo':1,'Placa':1})
        self.assertIn('NEXUS instalado', s.craft('gauntlet_nexus'))
        self.assertEqual(s.gauntlet_nexus_progression_revision,8)
        s.gain_gauntlet_xp(180_000)  # nível 5
        attrs=s.player_attributes()
        self.assertEqual(s.gauntlet_nexus_level,5)
        self.assertEqual(attrs['precision'],11)
        self.assertAlmostEqual(attrs['attack'],14.0)
        self.assertAlmostEqual(attrs['crit_rate'],5.0)
        self.assertEqual(s.gauntlet_nexus_drop_bonus_pct,20.0)
        self.assertEqual(s.gauntlet_nexus_advantage_bonus_pct,0.0)
        self.assertEqual(s.gauntlet_nexus_points,0)

    def test_nexus_xp_stops_at_maximum(self):
        s=State(); s.inventory.update({'Sucata':8,'Núcleo':1,'Placa':1}); s.craft('gauntlet_nexus')
        s.gain_gauntlet_xp(30_000_000)
        self.assertEqual(s.gauntlet_nexus_xp,30_000_000)
        self.assertEqual(s.gauntlet_nexus_level,22)

    def test_v3_nexus_save_is_recalibrated_to_sparse_revision4(self):
        s=State(); s.inventory.update({'Sucata':8,'Núcleo':1,'Placa':1}); s.craft('gauntlet_nexus')
        s.gauntlet_nexus_progression_revision=3
        s.gauntlet_nexus_xp=180_000
        s.gauntlet_nexus_level=5
        s.gauntlet_nexus_nodes=['nexus_level_%02d'%i for i in range(1,6)]
        s.combat_stats['crit_rate_bonus']=0.5  # bônus exclusivo da antiga revisão 3 no nível 4
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'save.json'; s.save(p); data=json.loads(p.read_text(encoding='utf-8')); data['gauntlet_nexus_progression_revision']=3
            p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            loaded,_=State.load(p)
            self.assertEqual(loaded.gauntlet_nexus_progression_revision,8)
            self.assertEqual(loaded.gauntlet_nexus_nodes,[f'nexus_level_{i:02d}' for i in range(1,6)])
            self.assertAlmostEqual(loaded.combat_stats['crit_rate_bonus'],0.0)
            self.assertEqual(loaded.gauntlet_nexus_hack_alert_capacity_bonus,0)

    def test_nexus_revision4_save_rebuilds_the_new_sparse_table_without_stacking_bonus(self):
        s = State(); s.inventory.update({'Sucata':8,'Núcleo':1,'Placa':1}); s.craft('gauntlet_nexus')
        s.gauntlet_nexus_progression_revision = 4
        s.gauntlet_nexus_xp = 180_000
        s.gauntlet_nexus_level = 5
        s.gauntlet_nexus_nodes = [f'nexus_level_{i:02d}' for i in range(1, 6)]
        # Estado equivalente ao NEXUS antigo no nível 5 da revisão 4:
        # +1 Precisão, +1 ATQ, +0,5% CRIT e +1 tolerância de alerta.
        s.combat_stats['precision'] = 11
        s.combat_stats['attack_bonus'] = 1.0
        s.combat_stats['crit_rate_bonus'] = 0.0
        s.gauntlet_nexus_hack_alert_capacity_bonus = 1
        data_keys = ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems','combat_stats','gauntlet_nexus_installed','gauntlet_nexus_xp','gauntlet_nexus_level','gauntlet_nexus_points','gauntlet_nexus_nodes','gauntlet_nexus_progression_revision','gauntlet_nexus_hack_alert_capacity_bonus','gauntlet_nexus_hack_diagonal','gauntlet_nexus_hack_mask_first_firewall','inside_ship','ship_pos','language_progress','language_mastered','missions','renown','renown_events','statistics','achievements','unique_rewards','achievement_reward_revision')
        data={k:getattr(s,k) for k in data_keys}; data['version']=46
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'save.json'; p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            loaded,_=State.load(p)
            self.assertEqual(loaded.gauntlet_nexus_progression_revision,8)
            self.assertEqual(loaded.gauntlet_nexus_level,5)
            self.assertEqual(loaded.gauntlet_nexus_nodes,[f'nexus_level_{i:02d}' for i in range(1,6)])
            attrs=loaded.player_attributes()
            self.assertEqual(attrs['precision'],11)
            self.assertAlmostEqual(attrs['attack'],14.0)
            self.assertAlmostEqual(attrs['crit_rate'],5.0)
            self.assertEqual(loaded.gauntlet_nexus_hack_alert_capacity_bonus,0)


    def test_global_amp_is_added_to_skill_amp(self):
        s = State(44)
        s.combat_stats['amp'] = 1.0
        s.start_battle(0)
        s.rng = self.FixedRng(5, 1.0)
        result = s.action('basic')
        self.assertEqual(result['skill_amp'], 1.0)
        self.assertGreaterEqual(result['damage'], 1)


    def test_nexus_progression_recalibrates_old_save_by_accumulated_xp(self):
        s=State(); s.gauntlet_nexus_installed=True; s.gauntlet_nexus_xp=165_000; s.gauntlet_nexus_level=20; s.gauntlet_nexus_points=19; s.gauntlet_nexus_nodes=['impact_calibration','precision_routines_1']
        s.combat_stats['attack_bonus']=1.0; s.combat_stats['crit_rate_bonus']=0.5
        data={k:getattr(s,k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems','combat_stats','gauntlet_nexus_installed','gauntlet_nexus_xp','gauntlet_nexus_level','gauntlet_nexus_points','gauntlet_nexus_nodes','gauntlet_nexus_progression_revision','inside_ship','ship_pos','language_progress','language_mastered','missions','renown','renown_events','statistics','achievements','unique_rewards','achievement_reward_revision')}
        data['version']=46; data['gauntlet_nexus_progression_revision']=2
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'save.json'; p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8'); loaded,_=State.load(p)
            self.assertEqual(loaded.gauntlet_nexus_xp,165_000)
            self.assertEqual(loaded.gauntlet_nexus_level,4)
            self.assertEqual(loaded.gauntlet_nexus_progression_revision,8)
            self.assertEqual(loaded.gauntlet_nexus_points,0)
            self.assertEqual(loaded.gauntlet_nexus_nodes,['nexus_level_01','nexus_level_02','nexus_level_03','nexus_level_04'])


    def test_old_defensive_nexus_node_is_removed_on_load(self):
        s = State(); s.gauntlet_nexus_installed = True
        s.gauntlet_nexus_nodes = ['reactive_plating']
        s.combat_stats['defense_bonus'] = 1
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'save.json'
            data = {k: getattr(s, k) for k in ('pos','hp','memory','memory_owned','memory_slots','inventory','crafted','slots','kills','time','collected_nodes','worlds','sector','visited','chest_generation','gauntlet_generation','helmet_generation','helmet_owned','helmet_equipped','locomotion_generation','locomotion_equipped','journal','society','ship_systems','combat_stats','gauntlet_nexus_installed','gauntlet_nexus_xp','gauntlet_nexus_level','gauntlet_nexus_points','gauntlet_nexus_nodes','inside_ship','ship_pos','language_progress','language_mastered','missions','renown','renown_events','statistics','achievements','unique_rewards','achievement_reward_revision')}
            data['version'] = 45
            p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertNotIn('reactive_plating', loaded.gauntlet_nexus_nodes)
            self.assertEqual(loaded.combat_stats['defense_bonus'], 0)


    def test_nexus_hack_protocols_are_applied(self):
        s=State(); s.sector='waterworks'; s.visited=['landing','waterworks']; s.missions['water_supply']['status']='active'
        s.gauntlet_nexus_installed=True; s.gauntlet_nexus_level=15; s.gauntlet_nexus_hack_alert_capacity_bonus=1; s.gauntlet_nexus_hack_diagonal=True; s.gauntlet_nexus_hack_mask_first_firewall=True
        site=next(l for l in s.area['landmarks'] if l.get('hack_site')); s.pos=list(site['pos'])
        ok,msg=s.start_hack(); self.assertTrue(ok,msg); self.assertEqual(s.hack['alert_limit'],4); self.assertTrue(s.hack_move(1,1))

    def test_initial_fauna_attack_ranges_are_kept_moderate(self):
        expected_attack = {
            'scarab': (4, 5), 'lizard': (5, 6), 'drone': (5, 7), 'hound': (5, 7),
            'burrower': (6, 8), 'guard': (6, 8), 'manta': (6, 8), 'stalker': (7, 9),
        }
        for sid, attack in expected_attack.items():
            self.assertEqual(SPECIES[sid]['attack'], attack)
            self.assertEqual(SPECIES[sid].get('amp', 0.0), 0.0)
            self.assertLessEqual(SPECIES[sid].get('crit_rate', 0.0), 4.0)
            self.assertLessEqual(SPECIES[sid].get('crit_damage', 1.0), 1.40)

    def test_ship_has_internal_map_and_three_interaction_points(self):
        s = State()
        self.assertTrue(s.enter_ship())
        self.assertTrue(s.inside_ship)
        for key in ('cockpit', 'computer', 'status'):
            s.ship_pos = list(SHIP_INTERIOR[key if key != 'status' else 'status_panel'])
            self.assertEqual(s.ship_interaction(), key)
        s.ship_pos = [1, 1]
        self.assertFalse(s.move_ship(0, -1))
        self.assertTrue(s.leave_ship())
        self.assertFalse(s.inside_ship)

    def test_helmet_recipe_is_gated_by_the_two_intermediates(self):
        s = State()
        self.assertEqual(OTHER_RECIPES['helmet_g1']['recipe'], {'Sucata':30, 'Núcleo de decodificação':5, 'Célula de energia instável':1})
        self.assertEqual(OTHER_RECIPES['decoder_core']['recipe'], {'Enzima':1, 'Secreção':1})
        self.assertEqual(OTHER_RECIPES['energy_cell']['recipe'], {'Sucata':30, 'Carapaça':12})
        s.inventory['Sucata'] = 30
        self.assertIn('Faltam materiais', s.craft('helmet_g1'))
        s.inventory.update({'Enzima':1, 'Secreção':1})
        self.assertIn('Núcleo de decodificação fabricado', s.craft('decoder_core'))
        s.inventory.update({'Sucata':30, 'Carapaça':12})
        self.assertIn('Célula de energia instável fabricada', s.craft('energy_cell'))
        s.inventory['Sucata'] = 30
        s.inventory['Núcleo de decodificação'] = 5
        s.inventory['Célula de energia instável'] = 1
        self.assertIn('Elmo reconstruído', s.craft('helmet_g1'))
        self.assertTrue(s.helmet_owned)
        self.assertTrue(s.helmet_equipped)

    def test_helmet_enables_cultural_analysis_and_unlocks_water_mission(self):
        s = State()
        s.helmet_generation = 1
        s.helmet_owned = True
        s.helmet_equipped = True
        for sector, pos in [('ruins', (10,5)), ('outskirts', (10,7)), ('waterworks', (7,6))]:
            s.sector = sector
            s.pos = list(pos)
            ok, _, changed = s.analyze_culture()
            self.assertTrue(ok)
        self.assertTrue(s.language_mastered)
        self.assertEqual(s.language_progress, 3)
        self.assertEqual(s.missions['water_supply']['status'], 'available')
        self.assertEqual(s.journal['objectives']['water_mission']['status'], 'active')

    def _activate_water_mission(self):
        s = State()
        s.language_mastered = True
        s.missions['water_supply']['status'] = 'active'
        s.journal['objectives']['water_mission']['status'] = 'active'
        return s

    def test_water_mission_repair_path_completes_without_changing_renown_yet(self):
        s = self._activate_water_mission()
        s.inventory.update({'Sucata':8, 'Placa':2})
        before = s.renown
        ok, reward, msg = s.complete_mission('water_supply', 'repair')
        self.assertTrue(ok)
        self.assertEqual(s.missions['water_supply']['path'], 'repair')
        self.assertEqual(s.renown, before)
        self.assertEqual(s.statistics['mission_paths']['repair'], 1)
        self.assertIn('Válvula hidráulica', reward)

    def test_water_mission_force_path_uses_combat_and_completes(self):
        s = self._activate_water_mission()
        self.assertTrue(s.start_force_mission())
        self.assertTrue(s.battle and s.battle.get('temporary'))
        s.battle['hp'] = 0
        reward = s.win()
        self.assertEqual(s.missions['water_supply']['status'], 'completed')
        self.assertEqual(s.missions['water_supply']['path'], 'force')
        self.assertEqual(s.statistics['mission_paths']['force'], 1)
        self.assertIn('Válvula hidráulica', reward)
        self.assertEqual(s.renown, 50)

    def test_water_mission_hack_path_requires_terminal_and_can_finish_cleanly(self):
        s = self._activate_water_mission()
        s.sector = 'waterworks'; s.pos = [13, 8]
        ok, msg = s.start_hack()
        self.assertTrue(ok, msg)
        for pos in [(0,1),(0,2),(1,2),(2,2)]:
            s.hack_move(pos[0] - s.hack['cursor'][0], pos[1] - s.hack['cursor'][1])
            result = s.hack_breach()
        self.assertTrue(result.get('success'))
        self.assertEqual(s.missions['water_supply']['path'], 'hack')
        self.assertEqual(s.statistics['mission_paths']['hack'], 1)
        self.assertEqual(s.renown, 50)

    def test_water_mission_hack_failure_marks_the_mission_failed(self):
        s = self._activate_water_mission()
        s.sector = 'waterworks'; s.pos = [13, 8]
        ok, _ = s.start_hack(); self.assertTrue(ok)
        s.hack_move(1,0)
        self.assertEqual(s.hack_breach()['ok'], True)
        self.assertEqual(s.hack_breach()['ok'], True)
        result = s.hack_breach()
        self.assertTrue(result.get('failed'))
        self.assertEqual(s.missions['water_supply']['status'], 'failed')
        self.assertEqual(s.statistics['missions_failed'], 1)

    def test_statistics_track_lifetime_enemy_drops(self):
        s = State(33); s.rng = self.FixedRng(1, 0.0); s.start_battle(0); s.battle['hp'] = 0
        loot = s.win()
        for item, qty in loot.items():
            self.assertEqual(s.statistics['collectibles'][item], qty)

    def test_card_collection_achievements_unlock_the_future_unique_reward(self):
        s = State()
        serial = 1
        for base in CARDS:
            for variant in ('normal','plus','plusplus'):
                s.crafted.append(f'{base}|{variant}|{serial}')
                serial += 1
        s.refresh_achievements()
        self.assertTrue(s.achievements['card_collector_normal']['unlocked'])
        self.assertTrue(s.achievements['card_collector_plus']['unlocked'])
        self.assertTrue(s.achievements['card_collector_plusplus']['unlocked'])
        self.assertEqual(s.unique_rewards, [])
        for aid in ('card_collector_normal','card_collector_plus','card_collector_plusplus'):
            ok, _ = s.claim_achievement(aid)
            self.assertTrue(ok)
        self.assertIn('prototype_unique_card', s.unique_rewards)

    def test_all_sectors_keep_npcs_solid_and_disjoint_from_nodes(self):
        for sector, data in SECTORS.items():
            settlement = data.get('settlement')
            if not settlement:
                continue
            npc_tiles = {tuple(n['pos']) for n in settlement['npcs']}
            self.assertTrue(all(n.get('solid', True) for n in settlement['npcs']))
            node_tiles = {tuple(n['pos']) for n in data['nodes']}
            self.assertTrue(npc_tiles.isdisjoint(node_tiles), sector)




class V046BossAndCombatTests(unittest.TestCase):
    def test_battle_has_selectable_target(self):
        s = State(1)
        self.assertTrue(s.start_battle(0))
        self.assertEqual(s.battle_target, 'body')
        self.assertTrue(s.set_battle_target('body'))
        self.assertFalse(s.set_battle_target('nonexistent'))

    def test_kuvaar_requires_water_and_has_weakpoint_targets(self):
        s = State(2)
        s.language_mastered = True
        s.missions['kuvaar_hunt']['status'] = 'boss_ready'
        s.inventory['Água Pura'] = 3
        ok, msg = s.start_boss_battle('kuvaar')
        self.assertTrue(ok, msg)
        ids = [x['id'] for x in s.battle_targets()]
        self.assertIn('shell', ids); self.assertIn('head', ids); self.assertNotIn('ventral', ids)
        self.assertIn('water_deposit_1', ids)
        s.set_battle_target('water_deposit_1')
        result = s.action('basic', 'water_deposit_1')
        self.assertTrue(result['ok'])
        self.assertEqual(s.battle['shell_layers'], 2)
        self.assertGreater(s.battle['exposed_turns'], 0)
        self.assertIn('ventral', [x['id'] for x in s.battle_targets()])

    def test_kuvaar_real_battle_can_finish_and_unlock_simulator(self):
        s = State(3)
        s.language_mastered = True
        s.missions['kuvaar_hunt']['status'] = 'boss_ready'
        s.inventory['Água Pura'] = 5
        ok, _ = s.start_boss_battle('kuvaar')
        self.assertTrue(ok)
        s.battle['hp'] = 1
        s.action('basic', 'head')
        s.win()
        self.assertTrue(s.bosses['kuvaar']['defeated'])
        self.assertTrue(s.simulator_unlocked)
        self.assertEqual(s.missions['kuvaar_hunt']['status'], 'completed')

    def test_virtual_kuvaar_uses_best_conditions_and_charge(self):
        s = State(4)
        s.bosses['kuvaar']['defeated'] = True
        s.simulator_unlocked = True
        s.simulator_built = True
        s.inventory['Carga de Simulação'] = 1
        s.hp = 4; s.memory = 0
        ok, msg = s.start_boss_battle('kuvaar', virtual=True)
        self.assertTrue(ok, msg)
        self.assertEqual(s.hp, MAX_HP)
        self.assertEqual(s.memory, s.max_memory)
        self.assertEqual(s.battle['water_deposit_total'], 3)
        self.assertEqual(s.inventory['Carga de Simulação'], 0)

    def test_old_save_migrates_to_046_missions(self):
        s = State(5)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'save.json'; s.save(p)
            data = json.loads(p.read_text()); data['version'] = 45
            data['missions'] = {'water_supply': {'status':'completed','path':'repair','reward_claimed':True}}
            p.write_text(json.dumps(data, ensure_ascii=False))
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('kuvaar_hunt', loaded.missions)
            self.assertEqual(loaded.missions['water_supply']['status'], 'completed')


    def test_boss_tile_is_solid_until_boss_is_defeated(self):
        s = State(13)
        s.sector = 'salt_basin'
        s.pos = [14, 11]
        self.assertEqual(s.boss_at([15, 11]), 'kuvaar')
        self.assertFalse(s.move(1, 0))
        self.assertEqual(s.pos, [14, 11])
        s.bosses['kuvaar']['defeated'] = True
        self.assertIsNone(s.boss_at([15, 11]))
        self.assertTrue(s.move(1, 0))
        self.assertEqual(s.pos, [15, 11])

    def test_simulator_is_only_a_craftable_project_after_real_boss_victory(self):
        s = State(14)
        s.inventory.update({'Núcleo de Kuvaar': 1, 'Microchip': 6, 'Núcleo': 4, 'Placa': 6})
        self.assertIn('liberado', s.craft('combat_simulator').lower())
        s.bosses['kuvaar']['defeated'] = True
        s.simulator_unlocked = True
        self.assertFalse(s.simulator_built)
        msg = s.craft('combat_simulator')
        self.assertIn('Simulador de Combate construído', msg)
        self.assertTrue(s.simulator_built)
        s.inventory.update({'Microchip': 2, 'Núcleo': 1, 'Cristal de sintonia': 1})
        self.assertIn('Carga de Simulação armazenada', s.craft('simulation_charge'))

class V046AdditionalTests(unittest.TestCase):
    def test_kuvaar_water_production_persists_purifier(self):
        s = State(6)
        s.language_mastered = True
        s.missions['kuvaar_hunt']['status'] = 'water'
        s.inventory.update({'Sucata': 24, 'Filamento': 10, 'Núcleo': 4, 'Placa': 2, 'Água Bruta': 10, 'Cristal de sintonia': 1})
        self.assertTrue(s.craft('water_purifier').startswith('Purificador'))
        before = dict(s.inventory)
        msg = s.craft('pure_water')
        self.assertIn('Cinco unidades', msg)
        self.assertTrue(s.water_purifier_built)
        self.assertEqual(s.inventory.get('Água Pura', 0), 5)
        self.assertEqual(s.inventory['Sucata'], before['Sucata'])

    def test_false_kuvaar_trace_consumes_time_and_removes_grace(self):
        s = State(7)
        s.sector = 'dunes'
        s.missions['kuvaar_hunt']['status'] = 'tracking'
        landmark = next(l for l in s.area['landmarks'] if l.get('boss_trace') == 'false')
        start = s.time
        s.grace = 4
        s.inventory['Sucata'] = 1
        ok, msg, changed = s.inspect_boss_trace(landmark)
        self.assertFalse(ok)
        self.assertTrue(changed)
        self.assertEqual(s.time, start + 20)
        self.assertEqual(s.grace, 0)
        self.assertEqual(s.inventory['Sucata'], 0)
        self.assertIn('falso', msg)

    def test_three_true_traces_unlock_water_stage(self):
        s = State(8)
        s.missions['kuvaar_hunt']['status'] = 'tracking'
        for sector, landmark_id in [('dunes','kuvaar_trace_dunes_true'), ('outskirts','kuvaar_trace_outskirts_true'), ('canyon','kuvaar_trace_canyon_true')]:
            s.sector = sector
            lm = next(l for l in s.area['landmarks'] if l['id'] == landmark_id)
            ok, _, _ = s.inspect_boss_trace(lm)
            self.assertTrue(ok)
        self.assertEqual(s.missions['kuvaar_hunt']['status'], 'water')
        self.assertEqual(s.missions['kuvaar_hunt']['stage'], 3)

    def test_real_kuvaar_uses_battlefield_water_deposits(self):
        s = State(9)
        ok, _ = s.start_boss_battle('kuvaar')
        self.assertTrue(ok)
        self.assertEqual(s.battle['water_deposit_total'], 1)
        self.assertEqual(s.inventory.get('Água Pura', 0), 0)
        self.assertTrue(s.action('basic', 'water_deposit_1')['ok'])
        self.assertEqual(s.battle['water_deposits_remaining'], 0)

    def test_virtual_kuvaar_uses_three_water_deposits_without_real_water(self):
        s = State(10)
        s.bosses['kuvaar']['defeated'] = True
        s.simulator_built = True
        s.inventory.update({'Carga de Simulação': 1, 'Água Pura': 2})
        ok, _ = s.start_boss_battle('kuvaar', virtual=True)
        self.assertTrue(ok)
        self.assertEqual(s.inventory['Carga de Simulação'], 0)
        self.assertEqual(s.inventory['Água Pura'], 2)
        self.assertEqual(s.battle['water_deposit_total'], 3)


class V046CompatibilityTests(unittest.TestCase):
    def test_v046_save_missing_kuvaar_objective_is_repaired_on_load(self):
        s = State(11)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'save_v047.json'
            s.save(p, refresh=False)
            data = json.loads(p.read_text(encoding='utf-8'))
            del data['journal']['objectives']['kuvaar']
            data['version'] = 46
            p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            loaded, _ = State.load(p)
            self.assertFalse(loaded.save_blocked)
            self.assertIn('kuvaar', loaded.journal['objectives'])

    def test_kuvaar_shell_defense_falls_with_each_water_deposit(self):
        s = State(12)
        s.missions['water_supply']['status'] = 'completed'
        s.missions['water_supply']['path'] = 'repair'
        ok, _ = s.start_boss_battle('kuvaar')
        self.assertTrue(ok)
        self.assertEqual(s.battle['water_deposit_total'], 3)
        for idx, (expected_layers, expected_def) in enumerate([(2,24),(1,17),(0,7)], 1):
            target = f'water_deposit_{idx}'
            self.assertTrue(s.set_battle_target(target))
            attack = s.action('basic', target)
            self.assertTrue(attack['ok'])
            self.assertEqual(s.battle['shell_layers'], expected_layers)
            if expected_layers > 0:
                s.set_battle_target('shell')
                hit = s.action('basic', 'shell')
                self.assertEqual(hit['target_defense'], expected_def)
                s.battle['exposed_turns'] = 3

    def test_kuvaar_can_start_before_preparation_without_attribute_penalty(self):
        s = State(13)
        ok, message = s.start_boss_battle('kuvaar')
        self.assertTrue(ok)
        self.assertEqual(s.battle['hp'], BOSSES['kuvaar']['hp'])
        self.assertEqual(s.battle['water_deposit_total'], 1)
        self.assertNotIn('zone_defense_bonus', s.battle)
        self.assertNotIn('enemy_attack_bonus', s.battle)
        self.assertIn('apenas um depósito', message.lower())

    def test_kuvaar_repaired_reservoirs_give_maximum_deposits_without_buffing_boss(self):
        s = State(14)
        s.missions['water_supply']['status'] = 'completed'
        s.missions['water_supply']['path'] = 'repair'
        ok, _ = s.start_boss_battle('kuvaar')
        self.assertTrue(ok)
        self.assertEqual(s.battle['water_deposit_total'], 3)
        self.assertEqual(s.battle['hp'], BOSSES['kuvaar']['hp'])
        self.assertEqual(BOSSES['kuvaar']['defense'], 30)



class Final046CombatTests(unittest.TestCase):
    def test_floor_landmarks_are_directly_interactable(self):
        s = State(21)
        s.sector = 'waterworks'
        s.pos = [12, 7]
        self.assertEqual(s.nearby_landmark()['id'], 'water_pump')
        s.pos = [13, 7]
        self.assertEqual(s.nearby_landmark()['id'], 'water_terminal')
        s.pos = [11, 17]
        self.assertEqual(s.nearby_landmark()['id'], 'kuvaar_diversion')

    def test_nearby_landmarks_prioritize_exact_tile_before_adjacent_interactable(self):
        s = State(22)
        s.sector = 'waterworks'
        s.pos = [12, 7]
        ordered = [x['id'] for x in s.nearby_landmarks(1)]
        self.assertEqual(ordered[0], 'water_pump')
        self.assertIn('water_terminal', ordered)

    def test_every_enemy_zone_has_reasonable_precision_targeting_data(self):
        for sid, spec in SPECIES.items():
            self.assertTrue(0 <= spec['precision'] <= 100, sid)
            for zone in spec['target_zones'].values():
                self.assertTrue(0 <= zone['evasion'] <= 100)
                self.assertIn('defense', zone)
        for bid, boss in BOSSES.items():
            self.assertTrue(0 <= boss['precision'] <= 100, bid)
            for zone in boss['target_zones'].values():
                self.assertTrue(0 <= zone['evasion'] <= 100, bid)

    def test_all_enemies_have_target_zones_and_precision(self):
        for sid, spec in SPECIES.items():
            self.assertIn('precision', spec, sid)
            self.assertGreaterEqual(spec['precision'], 0)
            self.assertGreaterEqual(len(spec.get('target_zones', {})), 3, sid)
            self.assertTrue(all('defense' in z and 'evasion' in z for z in spec['target_zones'].values()), sid)

    def test_precision_changes_hit_chance_by_body_part(self):
        s = State(7)
        s.start_battle(0)
        self.assertEqual(set(t['id'] for t in s.battle_targets()), {'body','head','leg'})
        self.assertGreaterEqual(s.target_hit_chance('body'), 98)
        self.assertGreaterEqual(s.target_hit_chance('head'), 98)
        self.assertGreaterEqual(s.target_hit_chance('leg'), 98)
        s.combat_stats['precision'] = 0
        self.assertEqual(s.target_hit_chance('body'), 100)
        self.assertLess(s.target_hit_chance('leg'), 100)

    def test_target_zone_changes_only_defense_in_damage_formula(self):
        s = State(9)
        s.start_battle(0)
        s.combat_stats['crit_rate'] = 0.0
        class FixedRng:
            def __init__(self, randint_value=5, random_value=0.0):
                self.randint_value = randint_value; self.random_value = random_value
            def randint(self, a, b): return max(a, min(self.randint_value, b))
            def random(self): return self.random_value
            def choice(self, seq): return seq[0]
        s.rng = FixedRng(5, 0.0)
        body = s.action('basic', 'body')
        s.battle = None
        s.start_battle(0)
        s.combat_stats['crit_rate'] = 0.0
        s.rng = FixedRng(5, 0.0)
        leg = s.action('basic', 'leg')
        self.assertEqual(body['target_defense'], 4)
        self.assertEqual(leg['target_defense'], 2)
        expected_body = s._formula_damage(12, 1.0, 5, 4)
        expected_leg = s._formula_damage(12, 1.0, 5, 2)
        self.assertEqual(body['base_damage'], expected_body)
        self.assertEqual(leg['base_damage'], expected_leg)
        self.assertEqual(body['damage'], expected_body)
        self.assertEqual(leg['damage'], expected_leg)

    def test_body_zone_has_no_hidden_damage_multiplier_fields(self):
        for spec in list(SPECIES.values()) + list(BOSSES.values()):
            for zone in spec.get('target_zones', {}).values():
                self.assertNotIn('multiplier', zone)

    def test_precision_card_attribute_scales_as_integer(self):
        s = State(13)
        CARDS['temp_precision_test'] = dict(name='Teste Precisão', species='scarab', cost=1, damage=(1,1), skill_amp=0.0, rarity='Comum', target_mode='single', attributes={'precision':1,'attack':0,'defense':0,'amp':0.0,'crit_rate':0.0,'crit_damage':0.0,'min_damage_bonus':0}, recipe={})
        try:
            attrs = s.card_attributes('temp_precision_test|plus|1')
            self.assertEqual(attrs['precision'], 2)
        finally:
            CARDS.pop('temp_precision_test', None)

    def test_enemy_precision_is_used_for_enemy_hit_chance(self):
        s = State(11)
        s.start_battle(0)
        self.assertEqual(s._enemy_hit_chance(SPECIES['scarab']), 94)
        self.assertEqual(s._enemy_hit_chance(BOSSES['kuvaar']), 98)

    def test_ground_exits_are_interactable_with_e(self):
        s = State(21)
        s.sector = 'canyon'; s.pos = [2, 18]
        gate = s.nearby_exit(0)
        self.assertIsNotNone(gate)
        ok, message = s.use_nearby_exit(0)
        self.assertTrue(ok)
        self.assertEqual(s.sector, 'waterworks')
        self.assertEqual(s.pos, [19, 17])
        self.assertIn('Estação de Captação', message)


    def test_adjacent_ground_exit_is_interactable_with_e(self):
        s = State(23)
        s.sector = 'canyon'; s.pos = [3, 18]
        gate = s.nearby_exit(1)
        self.assertIsNotNone(gate)
        ok, message = s.use_nearby_exit(1)
        self.assertTrue(ok)
        self.assertEqual(s.sector, 'waterworks')
        self.assertEqual(s.pos, [19, 17])
        self.assertIn('Estação de Captação', message)

    def test_gauntlet_stones_have_six_persistent_slots(self):
        s = State(22)
        self.assertEqual(s.gauntlet_stones, [None, None, None, None, None, None])
        s.gauntlet_stones[4] = 'Núcleo de Éon'
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'save.json'
            s.save(path, refresh=False)
            loaded, _ = State.load(path)
            self.assertEqual(loaded.gauntlet_stones, [None, None, None, None, 'Núcleo de Éon', None])

    def test_gauntlet_stones_legacy_three_slot_save_expands_to_six(self):
        s = State(23)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'legacy.json'
            s.save(path, refresh=False)
            data = json.loads(path.read_text(encoding='utf-8'))
            data['gauntlet_stones'] = [None, 'Núcleo de Éon', None]
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            loaded, _ = State.load(path)
            self.assertEqual(loaded.gauntlet_stones, [None, 'Núcleo de Éon', None, None, None, None])

    def test_boss_route_marker_exists_in_canyon(self):
        marker = next((lm for lm in SECTORS['canyon']['landmarks'] if lm.get('boss_route_marker') == 'kuvaar'), None)
        self.assertIsNotNone(marker)
        self.assertEqual(marker['pos'], (21, 5))


if __name__ == '__main__':
    unittest.main()

class V047KuvaarWaterExecutionTests(unittest.TestCase):
    def _start(self, path=None):
        s = State(700 + (0 if path is None else len(path)))
        if path is not None:
            s.missions['water_supply']['status'] = 'completed'
            s.missions['water_supply']['path'] = path
        ok, msg = s.start_boss_battle('kuvaar')
        self.assertTrue(ok, msg)
        return s

    def test_kuvaar_base_attributes_are_not_rebalanced_by_preparation(self):
        for path in (None, 'force', 'hack', 'repair'):
            s = self._start(path)
            b = s.battle
            self.assertEqual(b['hp'], BOSSES['kuvaar']['hp'])
            self.assertNotIn('enemy_attack_bonus', b)
            self.assertNotIn('enemy_precision_bonus', b)
            self.assertNotIn('zone_defense_bonus', b)

    def test_water_deposits_scale_only_with_water_supply_quest_path(self):
        self.assertEqual(self._start(None).battle['water_deposit_total'], 1)
        self.assertEqual(self._start('force').battle['water_deposit_total'], 2)
        self.assertEqual(self._start('hack').battle['water_deposit_total'], 2)
        self.assertEqual(self._start('repair').battle['water_deposit_total'], 3)

    def test_attacking_water_deposit_dissolves_one_shell_layer_and_exposes(self):
        s = self._start('repair')
        s.set_battle_target('water_deposit_1')
        result = s.action('basic', 'water_deposit_1')
        self.assertTrue(result['ok'])
        self.assertTrue(result['water_deposit'])
        self.assertEqual(result['damage'], 0)
        self.assertEqual(s.battle['shell_layers'], 2)
        self.assertEqual(s.battle['water_deposits_remaining'], 2)
        self.assertGreater(s.battle['exposed_turns'], 0)
        self.assertEqual(s.battle['target'], 'shell')

    def test_direct_fight_needs_no_pure_water_inventory(self):
        s = self._start(None)
        self.assertEqual(s.inventory.get('Água Pura', 0), 0)
        self.assertEqual(s.battle['water_deposit_total'], 1)
        self.assertIn('water_deposit_1', [t['id'] for t in s.battle_targets()])

    def test_only_remaining_water_deposits_can_be_targeted(self):
        s = self._start('repair')
        self.assertTrue(s.set_battle_target('water_deposit_1'))
        self.assertTrue(s.action('basic', 'water_deposit_1')['ok'])
        ids = [t['id'] for t in s.battle_targets()]
        self.assertNotIn('water_deposit_1', ids)
        self.assertIn('water_deposit_2', ids)
        self.assertIn('water_deposit_3', ids)
