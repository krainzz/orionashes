"""Estado, combate e persistência; independente da interface Pygame.
Versão de save compatível com 0.6.7."""
import json
import random
import shutil
import time as realtime
from pathlib import Path
from content import (CARDS, OTHER_RECIPES, SPECIES, SPAWNS, NODES, NODE_IDS,
                     SHIP, SIZE, MEMORY_MODULES, CHEST_MEMORY_SLOTS, MEMORY_RECIPES,
                     SHIP_SYSTEMS, SHIP_DIAGNOSTIC_ORDER, PLAYER_COMBAT, CARD_VARIANTS,
                     ACHIEVEMENTS, MISSION_REWARDS, SHIP_INTERIOR, MAX_HP, FACTIONS, BOSSES, HERBS, TYPE_ADVANTAGES, format_card_name, NEXUS_NODES,
                     AURORA_UPGRADES, TOTAL_MEMORY_SLOTS, CHEST_MEMORY_SLOT_UNLOCKS, STELLAR_ROUTES, RENOWN_MILESTONES, RENOWN_REWARDS, GALAXY_ID, GALAXY_NAME, GALAXIES, GALAXY_DISPLAY_ORDER, GALAXY_ROUTE_IDS, GALAXY_CONNECTIONS, GALAXY_RARE_BOSSES, GALAXY_LEGENDARY_BOSSES, CIVILIZATIONS, NEW_060_BOSSES, SHIP_MISSION_DATA, HELMET_DESIGN_ORDER, HELMET_TIERS, HELMET_SCAN_ABILITIES, CREATURE_TYPES, ESSENCE_DROP_RANGES, UNIQUE_CARD_ESSENCE_COST, UNIQUE_VARIANT_MULTIPLIERS, UNIQUE_BUFF_DEFS, UNIQUE_BUFF_COUNT_CHANCES, UNIQUE_MOMENTUM_CHANCE, UNIQUE_MOMENTUM_DEFS, DOMAIN_ELEMENTS, DOMAIN_LEVEL_MAX, DOMAIN_LEVEL_XP, DOMAIN_BONUSES, COMBAT_CHALLENGE_CATALOG, CIVILIZATION_MISSION_TEMPLATES, creature_achievement_id, creature_achievement_data, boss_achievement_id, boss_achievement_data, BOSS_ACHIEVEMENT_TIERS)
from world import SECTORS, ALL_NODE_IDS, fresh_enemies, protected_tile


OBJECTIVES = {
    'survive': {'title': 'Estabelecer um ponto seguro', 'description': 'Verifique a nave e confirme que ela ainda pode servir como abrigo.'},
    'explore': {'title': 'Reconhecer Veyra', 'description': 'Visite os oito setores atualmente conhecidos e registre o terreno.', 'target': 8},
    'records': {'title': 'Catalogar vestígios', 'description': 'Recupere os fragmentos históricos encontrados nas ruínas.', 'target': 3},
    'unknown_signal': {'title': 'Investigar os vestígios de civilização', 'description': 'Aproxime-se das estruturas antigas e descubra se o planeta ainda é habitado.'},
    'settlement': {'title': 'Avistar os Avarin', 'description': 'Observe os assentamentos e descubra as facções que dividem a sociedade local.'},
    'helmet': {'title': 'Reconstruir o elmo', 'description': 'Monte os circuitos necessários e reconstrua o elmo da armadura.'},
    'language': {'title': 'Compreender o Avari', 'description': 'Use o elmo para analisar três registros culturais e completar a primeira leitura do idioma local.', 'target': 3},
    'water_mission': {'title': 'Água para Qaresh', 'description': 'Descubra por que a estação de captação perdeu pressão e escolha como resolver a crise de abastecimento.'},
    'faction_conflict': {'title': 'A Dívida da Fenda', 'description': 'Uma facção rival quer destruir os Guardiões dos Reservatórios. Decida se cumprirá o golpe ou se avisará a facção ameaçada.'},
    'kuvaar': {'title': 'A Sede de Qaresh', 'description': 'Siga o rastro de sal, garanta água pura e enfrente Kuvaar, o Sorvedouro.', 'target': 3},
    'ship': {'title': 'Descobrir como restaurar a nave', 'description': 'A nave está funcional apenas como abrigo. Descubra os componentes necessários para recuperar seus sistemas de voo.'},
    'explore_space': {'title': 'Explore a Galáxia', 'description': 'Com a nave restaurada, viaje pelos mundos conhecidos e prepare-se para ir além da Galáxia Nárion quando novas galáxias forem descobertas.'},
    'ry_investigation': {'title': 'Investigue Vazio de RY', 'description': 'Derrote Kuvaar, Trembe, Ounull e Fagor; depois investigue a história do Vazio de RY conversando com o povo de Nahr.'},
    'dobra_core_install': {'title': 'Potencializar a nave', 'description': 'Instale o Núcleo de Dobra recuperado de RY no motor da nave para habilitar viagens intergalácticas.'},
    'alphor_path': {'title': 'Abrir a Caldeira de Alphor', 'description': 'Derrote os três bosses raros da Galáxia Vharos para revelar o caminho até Alphor, o Balrog de Pyraxis.', 'target': 3},
    'broom_path': {'title': 'Subir à Coroa de Broom', 'description': 'Derrote os três bosses raros da Galáxia Meridion para liberar o acesso à torre de Nerissa.', 'target': 3},
    'laser_project': {'title': 'Projeto: Emissor Laser', 'description': 'Receba o projeto dos Recuperadores de Qaresh nas Oficinas de Sifra.', 'target': 1},
    'travel_repair': {'title': 'Reparar a nave', 'description': 'Recupere Sucata suficiente para reparar os danos causados durante a última viagem.', 'target': 0},
}



def fresh_journal():
    return {
        'entries': [
            {'id': 'arrival', 'title': 'A queda', 'text': 'A fuga terminou neste mundo árido. A nave sobreviveu ao pouso forçado, mas seus sistemas de voo estão comprometidos. Apenas o núcleo do peitoral e a manopla continuam operacionais.', 'time': 0.0},
            {'id': 'armour', 'title': 'Armadura incompleta', 'text': 'O elmo e o módulo de locomoção ficaram para trás durante a fuga. Reconstruí-los exigirá tecnologia, materiais e tempo.', 'time': 0.0},
        ],
        'objectives': {
            'survive': {'status': 'active', 'progress': 0}, 'explore': {'status': 'active', 'progress': 1},
            'records': {'status': 'locked', 'progress': 0}, 'unknown_signal': {'status': 'locked', 'progress': 0},
            'settlement': {'status': 'locked', 'progress': 0}, 'helmet': {'status': 'locked', 'progress': 0},
            'language': {'status': 'locked', 'progress': 0}, 'water_mission': {'status': 'locked', 'progress': 0},
            'faction_conflict': {'status': 'locked', 'progress': 0},
            'kuvaar': {'status': 'locked', 'progress': 0}, 'ship': {'status': 'locked', 'progress': 0},
            'explore_space': {'status': 'locked', 'progress': 0},
            'ry_investigation': {'status': 'locked', 'progress': 0},
            'dobra_core_install': {'status': 'locked', 'progress': 0},
            'alphor_path': {'status': 'locked', 'progress': 0},
            'broom_path': {'status': 'locked', 'progress': 0},
            'laser_project': {'status': 'locked', 'progress': 0},
            'travel_repair': {'status': 'locked', 'progress': 0},
            'respawn_tank': {'status': 'locked', 'progress': 0},
        },
        'seen': ['arrival', 'armour'],
    }

def fresh_society():
    return {'discovered_settlements': [], 'seen_npcs': [], 'first_contact': False}

def fresh_ship_systems():
    return {key: data['condition'] for key, data in SHIP_SYSTEMS.items()}

def fresh_statistics():
    return {
        'kills': {key: 0 for key in SPECIES},
        'collectibles': {},
        'max_damage_dealt': 0,
        'max_damage_taken': 0,
        'missions_completed': 0,
        'missions_failed': 0,
        'cards_crafted': {'normal': 0, 'plus': 0, 'plusplus': 0},
        'battles_started': 0,
        'battles_won': 0,
        'battles_fled': 0,
        'critical_hits': 0,
        'mission_paths': {'repair': 0, 'force': 0, 'hack': 0},
        'bosses_defeated': {},
        'boss_rematches': {},
        'kits_used': 0,
        'combat_challenges_completed': 0,
        'asteroid_encounters': 0,
        'asteroids_destroyed': 0,
    }

def fresh_achievements():
    return {aid: {'unlocked': False, 'claimed': False} for aid in ACHIEVEMENTS}

def fresh_missions():
    return {
        'water_supply': {'status': 'locked', 'path': None, 'reward_claimed': False},
        'kuvaar_hunt': {'status': 'locked', 'stage': 0, 'path': None, 'reward_claimed': False, 'tracking_errors': 0, 'water_source': None},
        'faction_conflict': {'status': 'locked', 'path': None, 'winner': None, 'loser': None, 'winner_card': None, 'loser_card': None, 'reward_claimed': False},
        'explore_galaxy': {'status': 'locked', 'progress': 0, 'galaxies': []},
        'respawn_tank': {'status': 'locked', 'progress': 0, 'reward_claimed': False},
        'ship_hull': {'status': 'available', 'progress': 0},
        'ship_power': {'status': 'available', 'progress': 0, 'values': [20,30,25,25]},
        'ship_propulsion': {'status': 'available', 'progress': 0, 'sequence': ['up','right','down','left'], 'cursor': 0},
        'ship_navigation': {'status': 'available', 'progress': 0},
        'ship_comms': {'status': 'available', 'progress': 0},
        'ship_ftl': {'status': 'available', 'progress': 0, 'cursor': 0},
        'ry_investigation': {'status': 'locked', 'stage': 'bosses', 'progress': 0,
                            'flags': {'kuvaar': False, 'kael': False, 'ounull': False, 'fagor': False},
                            'reward_claimed': False},
        'dobra_core_install': {'status': 'locked', 'progress': 0, 'reward_claimed': False},
        'alphor_path': {'status': 'locked', 'galaxy': 'vharos', 'boss': 'alphor', 'progress': 0,
                        'flags': {bid: False for bid in GALAXY_RARE_BOSSES.get('vharos', ())}, 'reward_claimed': False},
        'broom_path': {'status': 'locked', 'galaxy': 'meridion', 'boss': 'broom', 'progress': 0,
                       'flags': {bid: False for bid in GALAXY_RARE_BOSSES.get('meridion', ())}, 'reward_claimed': False},
        'ship_laser_project': {'status': 'locked', 'progress': 0, 'reward_claimed': False},
        'travel_repair': {'status': 'locked', 'progress': 0, 'required': 0, 'reward_claimed': False},
    }


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def creature_level(spec):
    """Calcula o nível exibido no mapa a partir do overall da criatura."""
    hp = float(spec.get('hp', 1))
    atk = sum(spec.get('attack', (0, 0))) / 2.0
    defense = float(spec.get('defense', 0))
    precision = float(spec.get('precision', 0))
    crit = float(spec.get('crit_rate', 0))
    cdamage = float(spec.get('crit_damage', 1.0))
    score = (hp * 0.18 + atk * 4.0 + defense * 5.0 +
             precision * 1.8 + crit * 0.9 + max(0.0, cdamage - 1.0) * 9.0)
    return max(1, int(round(score / 10.0)))


class State:
    def __init__(self, seed=None, new_game=False):
        self.rng = random.Random(seed)
        self.pos = [7, 8]
        self.aurora_level = 0
        self.hp = MAX_HP
        self.memory = 8
        self.memory_owned = {'basic': 2, 'expanded': 0, 'advanced': 0}
        self.chest_generation = 1
        # A Manopla não usa gerações de hardware como os demais equipamentos.
        # O crescimento dela ocorre pelo NEXUS, uma única atualização cognitiva.
        self.gauntlet_generation = 1  # mantido apenas para compatibilidade com saves antigos
        self.gauntlet_nexus_installed = False
        self.gauntlet_nexus_xp = 0
        self.gauntlet_nexus_level = 1
        self.gauntlet_nexus_points = 0  # legado; a progressão atual é automática
        self.gauntlet_nexus_nodes = []
        self.gauntlet_nexus_progression_revision = 8
        self.gauntlet_nexus_drop_bonus_pct = 0.0
        self.gauntlet_nexus_advantage_bonus_pct = 0.0
        self.gauntlet_nexus_vampirism_pct = 0.0
        self.gauntlet_nexus_hack_alert_capacity_bonus = 0
        self.gauntlet_nexus_hack_diagonal = False
        self.gauntlet_nexus_hack_mask_first_firewall = False
        # Domínio elemental: oito progressões independentes, iniciando no nível 0.
        self.domain_xp = {element: 0 for element in DOMAIN_ELEMENTS}
        self.domain_levels = {element: 0 for element in DOMAIN_ELEMENTS}
        self.helmet_generation = 0
        self.helmet_owned = False
        self.helmet_equipped = False
        self.helmet_design = None
        self.locomotion_generation = 0
        self.locomotion_equipped = False
        self.inside_ship = False
        self.ship_pos = list(SHIP_INTERIOR['start'])
        self.opening_dialogue_pending = False
        self.respawn_tank_built = False
        self.essence_storage = 0
        self.game_over = False
        self.communication_revealed = False
        self.combat_stats = dict(PLAYER_COMBAT)
        self.memory_slots = ['basic', 'basic', None, None]
        self.inventory = {'Sucata': 0, 'Kit': 1}
        self.crafted = []
        self.slots = [None, None, None]
        # Slot especial reservado exclusivamente a Cartas Únicas.
        self.gauntlet_special_slot = None
        self.unique_cards = {}
        self.kills = {key: 0 for key in SPECIES}
        self.time = 0.0
        self.collected_nodes = []
        self.sector = 'landing'
        self.visited = ['landing']
        self.worlds = {key: fresh_enemies(key) for key in SECTORS}
        self.battle = None
        self.grace = 0.0
        self.last_loot = {}
        self.save_blocked = False
        self.journal = fresh_journal()
        self.society = fresh_society()
        self.ship_systems = fresh_ship_systems()
        self.language_progress = 0
        self.language_mastered = False
        self.language_mastery = {'avarin': False, 'nahr_shadows': False}
        self.pending_language_civilization = None
        self.pending_language_npc_id = None
        # Nahr usa a mesma lógica de descoberta cultural de Veyra, mas com trilha e idioma próprios.
        self.nahr_language_progress = 0
        self.nahr_language_mastered = False
        self.nahr_ry_contacted = False
        self.has_left_veyra = False
        self.missions = fresh_missions()
        self.renown = 50
        self.renown_events = []
        self.renown_by_faction = {fid: 0 for fid in FACTIONS}
        self.renown_planets = {'veyra': 0}
        self.renown_galaxies = {GALAXY_ID: 0}
        self.renown_claimed = []
        self.known_planets = ['veyra']
        self.selected_planet = 'veyra'
        self.selected_galaxy_id = GALAXY_ID
        self.dobra_core_installed = False
        self.ship_laser_project_unlocked = False
        self.ship_laser_installed = False
        self.travel_damage = 0
        self.known_civilizations_by_planet = {r['id']: list(r.get('initial_known_civilizations', [])) for r in STELLAR_ROUTES}
        self.statistics = fresh_statistics()
        self.achievements = fresh_achievements()
        self.unique_rewards = []
        self.achievement_reward_revision = 5
        self.hack = None
        self.bosses = {bid: {'defeated': False, 'virtual_defeats': 0} for bid in BOSSES}
        self.simulator_unlocked = False
        self.simulator_built = False
        self.water_purifier_built = False
        self.scan_unlocked = False
        self.achievement_alerts = []
        self.known_cards = []
        self.bestiary_known = []
        self.bestiary_scanned = []
        self.helmet_advanced_research_unlocked = False
        self.gauntlet_loadouts = [None, None, None]
        self.civilization_missions = {}
        self.last_challenge_result = None
        self.battle_target = None
        self.gauntlet_stones = [None, None, None, None, None, None]
        # Um novo jogo nasce dentro da nave e inicia a breve conversa de abertura.
        # Saves carregados jamais reutilizam este fluxo.
        if new_game:
            self.inside_ship = True
            self.ship_pos = list(SHIP_INTERIOR['start'])
            self.opening_dialogue_pending = True

    @property
    def max_memory(self):
        return sum(MEMORY_MODULES[m]['capacity'] for m in self.memory_slots if m)

    @property
    def max_memory_slots(self):
        return CHEST_MEMORY_SLOT_UNLOCKS.get(self.chest_generation, TOTAL_MEMORY_SLOTS)

    @property
    def max_hp(self):
        return MAX_HP + int(AURORA_UPGRADES.get(self.aurora_level, {}).get('hp', 0))

    def helmet_bonuses(self):
        data = HELMET_TIERS.get(int(self.helmet_generation))
        if not data:
            return {'precision': 0, 'crit_rate': 0.0}
        return {'precision': int(data.get('precision', 0)), 'crit_rate': float(data.get('crit_rate', 0.0))}

    def helmet_scan_abilities(self):
        tier = HELMET_TIERS.get(int(self.helmet_generation), {})
        return {key: bool(tier.get(f'scan_{key}', False) and self.helmet_equipped) for key, _ in HELMET_SCAN_ABILITIES}

    def stasis_shield_available(self):
        return bool(self.helmet_equipped and int(self.helmet_generation) >= 2 and HELMET_TIERS.get(int(self.helmet_generation), {}).get('stasis_shield', False))

    def essence_total(self):
        return max(0, int(self.inventory.get('Essência', 0))) + max(0, int(self.essence_storage))

    def consume_essence(self, amount):
        amount = max(0, int(amount))
        if self.essence_total() < amount:
            return False
        inv = min(int(self.inventory.get('Essência', 0)), amount)
        self.inventory['Essência'] = int(self.inventory.get('Essência', 0)) - inv
        rest = amount - inv
        if rest:
            self.essence_storage = max(0, int(self.essence_storage) - rest)
        return True

    def deposit_essence(self):
        amount = max(0, int(self.inventory.get('Essência', 0)))
        if amount:
            self.essence_storage += amount
            self.inventory['Essência'] = 0
        return amount

    def finish_opening_dialogue(self):
        if not self.opening_dialogue_pending:
            return False
        self.opening_dialogue_pending = False
        self.inside_ship = True
        self.ship_pos = list(SHIP_INTERIOR['start'])
        mission = self.missions.setdefault('respawn_tank', {'status':'locked','progress':0,'reward_claimed':False})
        if mission.get('status') == 'locked' and not self.respawn_tank_built:
            mission['status'] = 'active'
            self.set_objective('respawn_tank', 'active', 0)
            self.journal_add('respawn_tank_start', 'Tanque de Renascimento', 'O planeta desconhecido parece hostil. Reconstrua um Tanque de Renascimento para garantir uma volta segura à nave caso seu corpo seja destruído.')
            self.mission_started_alert('respawn_tank')
        return True

    def resolve_death(self, reason='Você ficou fora de combate.'):
        if self.respawn_tank_built:
            lost = int(self.inventory.get('Essência', 0) * 0.10)
            self.inventory['Essência'] = max(0, int(self.inventory.get('Essência', 0)) - lost)
            self.battle = None
            self.inside_ship = True
            self.ship_pos = list(SHIP_INTERIOR['start'])
            self.sector = 'landing'
            self.pos = [SHIP[0], SHIP[1] + 1]
            self.hp = self.max_hp
            self.memory = self.max_memory
            self.grace = 4
            self.game_over = False
            self.journal_add(f'death_{int(self.time*1000)}', 'Retorno pelo Tanque', f'{reason} O Tanque de Renascimento restaurou seu corpo na nave. Essências perdidas: {lost}.')
            return {'respawned': True, 'lost_essence': lost, 'game_over': False}
        self.battle = None
        self.hp = 0
        self.memory = 0
        self.game_over = True
        self.inside_ship = False
        self.journal_add(f'death_game_over_{int(self.time*1000)}', 'Fim de transmissão', f'{reason} O Tanque de Renascimento não foi reconstruído.')
        return {'respawned': False, 'lost_essence': 0, 'game_over': True}

    def resolve_stasis(self, success):
        b = self.battle
        if not b:
            return {'success': False, 'damage': 0, 'message': 'Nenhum ataque fatal está pendente.'}
        pending = b.pop('stasis_pending', None)
        if not pending:
            return {'success': False, 'damage': 0, 'message': 'O Escudo Stasis não está armado.'}
        if success:
            self.journal_add(f'stasis_{int(self.time*1000)}', 'Escudo Stasis', f'Você bloqueou {pending.get("name", "um ataque fatal")} no instante correto e recebeu 0 de dano.')
            return {'success': True, 'damage': 0, 'message': 'ESCUDO STASIS: ataque fatal bloqueado. 0 de dano.'}
        defeat = self.resolve_death('O tempo do Escudo Stasis expirou ou o bloqueio falhou.')
        return {'success': False, 'damage': 0, 'message': 'ESCUDO STASIS FALHOU. Você ficou fora de combate.', **defeat}

    def upgrade_helmet(self, level):
        if self.battle or not self.at_ship():
            return False, 'Aprimoramento do Elmo disponível junto à nave.'
        level = int(level)
        if self.helmet_generation < 1:
            return False, 'Reconstrua primeiro o Elmo / Tier 1.'
        if level != self.helmet_generation + 1 or level not in HELMET_TIERS:
            return False, 'Aprimoramento do Elmo indisponível.'
        data = HELMET_TIERS[level]
        if not data.get('available', False):
            return False, 'Este tier do Elmo exige tecnologia ainda não encontrada.'
        recipe = data.get('recipe', {})
        if any(self.inventory.get(item, 0) < qty for item, qty in recipe.items()):
            return False, 'Faltam materiais para o aprimoramento do Elmo.'
        for item, qty in recipe.items():
            self.inventory[item] -= qty
        self.helmet_generation = level
        self.helmet_owned = True
        self.helmet_equipped = True
        self.helmet_design = self.helmet_design or 'tactical'
        self.scan_unlocked = True
        self.journal_add(f'helmet_upgrade_{level}', 'Elmo aprimorado', f'O Elmo foi atualizado para {data["name"]}.')
        # O Tier 2 pode ser adquirido depois de cinco análises já realizadas.
        # Recalcular imediatamente evita obrigar o jogador a iniciar outro encontro.
        self.refresh_advanced_research()
        return True, f'{data["name"]} instalado.'

    def aurora_bonuses(self):
        data = AURORA_UPGRADES.get(self.aurora_level)
        if not data:
            return {'hp': 0, 'attack': 0, 'crit_rate': 0.0, 'crit_damage': 0.0}
        return {k: data[k] for k in ('hp','attack','crit_rate','crit_damage')}

    def upgrade_aurora(self, level):
        if self.battle or not self.at_ship():
            return False, 'Aprimoramento do AURORA disponível junto à nave.'
        level = int(level)
        if level != self.aurora_level + 1 or level not in AURORA_UPGRADES:
            return False, 'Aprimoramento indisponível.'
        data = AURORA_UPGRADES[level]
        if not data.get('available', True):
            return False, 'Este aprimoramento exige tecnologia de outros mundos.'
        recipe = data.get('recipe', {})
        if any(self.inventory.get(item, 0) < qty for item, qty in recipe.items()):
            return False, 'Faltam materiais para o aprimoramento do AURORA.'
        old_max = self.max_hp
        for item, qty in recipe.items():
            self.inventory[item] -= qty
        self.aurora_level = level
        self.hp = min(self.max_hp, self.hp + (self.max_hp - old_max))
        self.journal_add(f'aurora_upgrade_{level}', 'Núcleo AURORA aprimorado', f'O núcleo AURORA foi atualizado para {data["name"]}.')
        return True, f'{data["name"]} instalado.'

    def discover_planet(self, planet_id):
        route = next((r for r in STELLAR_ROUTES if r.get('id') == planet_id), None)
        if not route:
            return False
        self.known_civilizations_by_planet.setdefault(planet_id, list(route.get('initial_known_civilizations', [])))
        if planet_id not in self.known_planets:
            self.known_planets.append(planet_id)
            self.renown_planets.setdefault(planet_id, 0)
            return True
        return False

    def discover_civilization_on_planet(self, planet_id, civilization_name):
        route_ids = {r.get('id') for r in STELLAR_ROUTES}
        if planet_id not in route_ids or not civilization_name:
            return False
        if planet_id not in self.known_planets:
            return False
        known = self.known_civilizations_by_planet.setdefault(planet_id, [])
        if civilization_name not in known:
            known.append(civilization_name)
            return True
        return False

    @staticmethod
    def creature_level(spec):
        return creature_level(spec)

    def planet_for_sector(self, sector_id=None):
        sector_id = sector_id or self.sector
        for route in STELLAR_ROUTES:
            rid = route.get('id')
            landing = route.get('landing_sector')
            if sector_id == landing or (rid != 'veyra' and isinstance(sector_id, str) and sector_id.startswith(rid + '_')):
                return rid
        return 'veyra'

    def visited_planet_ids(self):
        visited = set(self.visited if isinstance(self.visited, list) else [])
        return [route['id'] for route in STELLAR_ROUTES
                if route.get('landing_sector') in visited
                or any(isinstance(sid, str) and sid.startswith(route['id'] + '_') for sid in visited)
                or (route['id'] == 'veyra' and any(sid in visited for sid in SECTORS if sid == 'landing' or sid.startswith('veyra_')))]

    def visited_galaxy_ids(self):
        visited_planets = set(self.visited_planet_ids())
        result = []
        for route in STELLAR_ROUTES:
            if route.get('id') in visited_planets:
                galaxy = route.get('galaxy', GALAXY_ID)
                if galaxy not in result:
                    result.append(galaxy)
        return result

    def galaxy_planet_ids(self, galaxy_id):
        visited = set(self.visited_planet_ids())
        return [route['id'] for route in STELLAR_ROUTES
                if route.get('galaxy', GALAXY_ID) == galaxy_id and route.get('id') in visited]

    def award_renown(self, faction_id, amount, reason='', planet_id=None):
        if faction_id not in FACTIONS or amount <= 0:
            return False
        amount = int(amount)
        planet_id = planet_id or self.current_planet_id()
        route_ids = {r.get('id') for r in STELLAR_ROUTES}
        if planet_id not in route_ids:
            planet_id = 'veyra'
        galaxy_id = next((r.get('galaxy', GALAXY_ID) for r in STELLAR_ROUTES if r.get('id') == planet_id), GALAXY_ID)
        self.renown_by_faction[faction_id] = self.renown_by_faction.get(faction_id, 0) + amount
        self.renown_planets[planet_id] = self.renown_planets.get(planet_id, 0) + amount
        self.renown_galaxies[galaxy_id] = sum(self.renown_planets.get(r['id'], 0) for r in STELLAR_ROUTES if r.get('galaxy', GALAXY_ID) == galaxy_id)
        self.renown_events.append({'faction': faction_id, 'amount': amount, 'reason': reason, 'planet': planet_id, 'galaxy': galaxy_id, 'time': round(self.time,2)})
        self.ensure_laser_project_mission()
        return True

    def renown_milestones(self):
        return {
            'faction': {fid: RENOWN_MILESTONES['faction'] for fid in self.renown_by_faction},
            'planet': {r['id']: RENOWN_MILESTONES['planet'] for r in STELLAR_ROUTES},
            'galaxy': {gid: RENOWN_MILESTONES['galaxy'] for gid in self.renown_galaxies},
        }

    def renown_reward(self, scope, key, milestone_index):
        thresholds = RENOWN_MILESTONES[scope]
        index = int(milestone_index)
        if index < 0 or index >= len(thresholds):
            return None
        claim_id = f'{scope}:{key}:{index}'
        if claim_id in self.renown_claimed:
            return None
        current = self.renown_by_faction.get(key,0) if scope == 'faction' else self.renown_planets.get(key,0) if scope == 'planet' else self.renown_galaxies.get(key,0)
        if current < thresholds[index]:
            return None
        return claim_id

    def renown_reward_items(self, scope, key, milestone_index):
        thresholds = RENOWN_MILESTONES.get(scope, ())
        idx = int(milestone_index)
        if idx < 0 or idx >= len(thresholds):
            return ()
        return tuple(RENOWN_REWARDS.get(scope, ())[idx])

    def claim_renown_reward(self, scope, key, milestone_index):
        claim_id = self.renown_reward(scope, key, milestone_index)
        if not claim_id:
            return False, 'Recompensa de Renome indisponível.'
        items = self.renown_reward_items(scope, key, milestone_index)
        for item, amount in items:
            self.inventory[item] = self.inventory.get(item,0) + amount
        self.renown_claimed.append(claim_id)
        self.achievement_alerts.append({'type':'renown_claimed','rid':claim_id})
        reward_text = ' + '.join(f'{item} ×{amount}' for item, amount in items)
        return True, f'Recompensa de Renome recebida: {reward_text}.'


    @property
    def area(self):
        return SECTORS[self.sector]

    @property
    def enemies(self):
        return self.worlds[self.sector]

    def near_ship_exterior(self):
        return self.area['ship'] is not None and distance(self.pos, self.area['ship']) <= 1

    def at_ship(self):
        return self.inside_ship or self.near_ship_exterior()

    def ship_access(self):
        return self.inside_ship or self.near_ship_exterior()

    def communication_route_visible(self):
        """A rota do Morro da Antena só existe no mapa após o início da missão.

        Depois de concluída, a rota permanece conhecida para permitir o retorno
        ao local da antena.
        """
        return self.missions.get('ship_comms', {}).get('status') in ('active', 'completed')

    def route_visible(self, gate):
        if gate.get('target') == 'comms_ridge':
            return self.communication_route_visible()
        return True

    def nearby_exit(self, radius=1):
        candidates = []
        for order, gate in enumerate(self.area.get('exits', [])):
            dist = distance(self.pos, gate['at'])
            if dist <= radius:
                candidates.append((dist, order, gate))
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2] if candidates else None

    def use_nearby_exit(self, radius=1):
        if self.battle or self.inside_ship:
            return False, 'A saída está indisponível neste momento.'
        gate = self.nearby_exit(radius)
        if not gate:
            return False, 'Nenhuma saída está ao alcance.'
        if not self.route_visible(gate):
            return False, 'A rota da antena permanece desativada. Inicie a missão de Comunicação no diagnóstico da nave.'
        if gate.get('requires_locomotion') and self.locomotion_generation < 1:
            return False, 'O Módulo de Locomoção é necessário para atravessar a água e alcançar este mundo.'
        self.sector = gate['target']
        self.pos = list(gate['arrival'])
        if self.sector not in self.visited:
            self.visited.append(self.sector)
        self.refresh_journal()
        self.grace = 3
        return True, f'Rota confirmada: {SECTORS[self.sector]["name"]}.'

    def enter_ship(self):
        if self.battle or not self.near_ship_exterior():
            return False
        self.inside_ship = True
        self.ship_pos = list(SHIP_INTERIOR['start'])
        self.grace = 2
        return True

    def leave_ship(self):
        if not self.inside_ship:
            return False
        self.inside_ship = False
        self.pos = list(SHIP)
        self.grace = 2
        return True

    def move_ship(self, dx, dy):
        if self.battle or not self.inside_ship or (dx, dy) not in ((1,0),(-1,0),(0,1),(0,-1)):
            return False
        p = [self.ship_pos[0] + dx, self.ship_pos[1] + dy]
        w, h = SHIP_INTERIOR['size']
        if not (0 <= p[0] < w and 0 <= p[1] < h):
            return False
        if tuple(p) in SHIP_INTERIOR['solid']:
            return False
        if tuple(p) in {SHIP_INTERIOR['cockpit'], SHIP_INTERIOR['computer'], SHIP_INTERIOR['status_panel'], SHIP_INTERIOR['airlock']}:
            pass
        self.ship_pos = p
        return True

    def ship_interaction(self):
        if not self.inside_ship:
            return None
        points = {
            'cockpit': SHIP_INTERIOR['cockpit'], 'computer': SHIP_INTERIOR['computer'],
            'status': SHIP_INTERIOR['status_panel'], 'simulator': SHIP_INTERIOR['simulator'],
            'respawn_tank': SHIP_INTERIOR['respawn_tank'], 'essence_storage': SHIP_INTERIOR['essence_storage'],
            'airlock': SHIP_INTERIOR['airlock'],
        }
        for key, point in points.items():
            if distance(self.ship_pos, point) <= 1:
                return key
        return None

    @staticmethod
    def is_unique_card_id(card_id):
        parts = str(card_id).split('|')
        return len(parts) == 4 and parts[0] == 'unique' and parts[1] in CREATURE_TYPES and parts[2] in CARD_VARIANTS

    def is_unique_card(self, card_id):
        return isinstance(card_id, str) and card_id in self.unique_cards and self.is_unique_card_id(card_id)

    @staticmethod
    def unique_card_parts(card_id):
        parts = str(card_id).split('|')
        if len(parts) != 4 or parts[0] != 'unique' or parts[1] not in CREATURE_TYPES or parts[2] not in CARD_VARIANTS:
            raise ValueError('Carta Única inválida.')
        try:
            serial = int(parts[3])
        except (TypeError, ValueError):
            raise ValueError('Carta Única inválida.')
        if serial < 1:
            raise ValueError('Carta Única inválida.')
        return parts[1], parts[2], serial

    @staticmethod
    def card_parts(card_id):
        # IDs legados como 'shell' significam a variante normal.
        if card_id in CARDS:
            return card_id, 'normal', 0
        parts = str(card_id).split('|')
        if len(parts) != 3 or parts[0] not in CARDS or parts[1] not in CARD_VARIANTS:
            raise ValueError('Carta inválida.')
        try:
            serial = int(parts[2])
        except (TypeError, ValueError):
            raise ValueError('Carta inválida.')
        if serial < 1:
            raise ValueError('Carta inválida.')
        return parts[0], parts[1], serial

    def card_data(self, card_id):
        if self.is_unique_card(card_id):
            element, variant, _serial = self.unique_card_parts(card_id)
            data = self.unique_cards[card_id]
            card = {
                'type': element,
                'name': data.get('name', f'Carta Única — {element}'),
                'species': data.get('species'),
                'cost': 0,
                'damage': (0, 0),
                'rarity': 'Única',
                'target_mode': 'none',
                'attributes': {},
                'description': data.get('description', ''),
                'unique_buffs': list(data.get('buffs', [])),
                'unique_momentum': data.get('momentum'),
            }
            return card, CARD_VARIANTS[variant], card_id, variant
        base_id, variant, _ = self.card_parts(card_id)
        return CARDS[base_id], CARD_VARIANTS[variant], base_id, variant

    def card_name(self, card_id):
        card, variant_data, _, _ = self.card_data(card_id)
        return format_card_name(card['name']) + variant_data['label']

    def card_instances(self, base_id=None):
        result = []
        for card_id in self.crafted:
            if self.is_unique_card(card_id):
                continue
            try:
                b_id, _, _ = self.card_parts(card_id)
            except ValueError:
                continue
            if base_id is None or b_id == base_id:
                result.append(card_id)
        return result

    def unique_card_effects(self):
        cid = self.gauntlet_special_slot
        if not self.is_unique_card(cid):
            return []
        element, variant, _serial = self.unique_card_parts(cid)
        mult = float(UNIQUE_VARIANT_MULTIPLIERS.get(variant, 1.0))
        effects = []
        for effect in self.unique_cards.get(cid, {}).get('buffs', []):
            kind = effect.get('kind')
            if kind not in UNIQUE_BUFF_DEFS:
                continue
            effects.append({'kind': kind, 'value': float(UNIQUE_BUFF_DEFS[kind]['value']) * mult})
        return effects

    def card_attributes(self, card_id):
        """Retorna somente BÔNUS permanentes da carta, já escalados pela variante.

        ATQ é percentual nesta versão: `attack_pct` representa uma fração percentual
        do ATQ efetivo do personagem e nunca é convertido para valor flat.
        """
        card, variant_data, _, _ = self.card_data(card_id)
        attrs = dict(card.get('attributes', {}))
        mult = float(variant_data['multiplier'])
        integer_keys = {'defense', 'precision', 'min_damage_bonus'}
        for key, value in list(attrs.items()):
            scaled = float(value) * mult
            attrs[key] = int(scaled + 0.5) if key in integer_keys else round(scaled, 2)
        # Não permitimos que uma definição antiga/reintroduzida gere ATQ flat.
        attrs.pop('attack', None)
        return attrs

    def domain_level_for_xp(self, xp):
        xp = max(0, int(xp or 0))
        level = 0
        for level_id, threshold in sorted(DOMAIN_LEVEL_XP.items()):
            if xp >= threshold:
                level = level_id
            else:
                break
        return min(DOMAIN_LEVEL_MAX, level)

    def domain_bonuses(self, element):
        """Soma os bônus já conquistados pelo Domínio de um elemento."""
        if element not in DOMAIN_ELEMENTS:
            return {'attack_pct': 0.0, 'defense_pct': 0.0, 'crit_rate': 0.0, 'crit_damage': 0.0,
                    'amp': 0.0, 'min_damage': 0, 'damage_taken_pct': 0.0, 'level': 0, 'xp': 0}
        level = max(0, min(DOMAIN_LEVEL_MAX, int(self.domain_levels.get(element, 0) or 0)))
        totals = {'attack_pct': 0.0, 'defense_pct': 0.0, 'crit_rate': 0.0, 'crit_damage': 0.0,
                  'amp': 0.0, 'min_damage': 0, 'damage_taken_pct': 0.0, 'level': level,
                  'xp': int(self.domain_xp.get(element, 0) or 0)}
        for level_id in range(1, level + 1):
            node = DOMAIN_BONUSES[element].get(level_id)
            if not node:
                continue
            kind = node['kind']; value = node['value']
            if kind == 'attack_pct': totals['attack_pct'] += float(value)
            elif kind == 'defense_pct': totals['defense_pct'] += float(value)
            elif kind == 'crit_rate': totals['crit_rate'] += float(value)
            elif kind == 'crit_damage': totals['crit_damage'] += float(value)
            elif kind == 'amp': totals['amp'] += float(value)
            elif kind == 'min_damage': totals['min_damage'] += int(value)
            elif kind == 'damage_taken_pct': totals['damage_taken_pct'] += float(value)
        return totals

    def gain_domain_xp(self, element, amount):
        """Concede XP ao Domínio elemental e atualiza automaticamente os níveis."""
        if element not in DOMAIN_ELEMENTS or amount <= 0:
            return 0
        amount = int(amount)
        current_xp = max(0, int(self.domain_xp.get(element, 0) or 0))
        max_xp = DOMAIN_LEVEL_XP[DOMAIN_LEVEL_MAX]
        new_xp = min(max_xp, current_xp + amount)
        old_level = max(0, min(DOMAIN_LEVEL_MAX, int(self.domain_levels.get(element, 0) or 0)))
        new_level = self.domain_level_for_xp(new_xp)
        self.domain_xp[element] = new_xp
        self.domain_levels[element] = new_level
        return max(0, new_level - old_level)

    def domain_progress(self, element):
        if element not in DOMAIN_ELEMENTS:
            return 0, 2000, 0, 2000
        level = max(0, min(DOMAIN_LEVEL_MAX, int(self.domain_levels.get(element, 0) or 0)))
        xp = max(0, int(self.domain_xp.get(element, 0) or 0))
        if level >= DOMAIN_LEVEL_MAX:
            return xp, xp, level, DOMAIN_LEVEL_XP[DOMAIN_LEVEL_MAX]
        target = DOMAIN_LEVEL_XP[level + 1]
        previous = 0 if level == 0 else DOMAIN_LEVEL_XP[level]
        return max(0, xp - previous), max(1, target - previous), level, target

    def _domain_xp_for_creature(self, species_id):
        """XP de Domínio conforme a raridade da criatura/carta."""
        rarity = self.creature_rarity(species_id)
        return {'Comum': 20, 'Incomum': 40, 'Rara': 100, 'Mítica': 200, 'Lendária': 500}.get(rarity, 20)

    def _award_domain_for_defeat(self, species_id, virtual=False):
        # O XP de Domínio acompanha a derrota da criatura, inclusive no
        # Simulador. O parâmetro virtual permanece apenas por compatibilidade
        # com chamadas antigas e não bloqueia a progressão.
        element = (BOSSES.get(species_id) if species_id in BOSSES else SPECIES.get(species_id, {})).get('type')
        amount = self._domain_xp_for_creature(species_id)
        return amount if element in DOMAIN_ELEMENTS and self.gain_domain_xp(element, amount) is not None else 0

    def _enemy_damage_cap(self, damage, battle=None):
        """Limita um evento de dano a, no máximo, 2x o HP máximo do inimigo.

        O limite usa o HP máximo da espécie/boss, e não o HP restante. Assim,
        um golpe não pode gerar quantidades desproporcionais de dano/XP contra
        inimigos do início do jogo, mas ainda pode exceder o HP restante e
        finalizar o combate normalmente.
        """
        battle = battle or self.battle or {}
        species_id = battle.get('species')
        if not species_id:
            return max(0, int(damage))
        spec = BOSSES.get(species_id) if battle.get('boss') else SPECIES.get(species_id)
        if not spec:
            return max(0, int(damage))
        max_hp = max(1, int(spec.get('hp', 1)))
        return min(max(0, int(damage)), max_hp * 2)

    def player_attributes(self):
        attack_base = float(self.combat_stats.get('attack', 12))
        stats = {
            'attack': attack_base,
            'defense': int(self.combat_stats.get('defense', 5)),
            'precision': int(self.combat_stats.get('precision', 10)),
            'amp': float(self.combat_stats.get('amp', 1.0)) + float(self.combat_stats.get('amp_bonus', 0.0)),
            'crit_rate': float(self.combat_stats.get('crit_rate', 5.0)) + float(self.combat_stats.get('crit_rate_bonus', 0.0)),
            'crit_damage': float(self.combat_stats.get('crit_damage', 1.5)) + float(self.combat_stats.get('crit_damage_bonus', 0.0)),
            'min_damage_bonus': int(self.combat_stats.get('min_damage_bonus', 0)),
            'attack_bonus': float(self.combat_stats.get('attack_bonus', 0.0)),
            'attack_pct_bonus': 0.0,
            'defense_bonus': int(self.combat_stats.get('defense_bonus', 0)),
        }
        # O bônus interno do NEXUS/legado continua separado das cartas.
        stats['attack'] += stats['attack_bonus'] + self.aurora_bonuses()['attack']
        stats['defense'] += stats['defense_bonus']
        stats['crit_rate'] += self.aurora_bonuses()['crit_rate']
        stats['crit_damage'] += self.aurora_bonuses()['crit_damage']
        stats['precision'] += self.helmet_bonuses()['precision']
        stats['crit_rate'] += self.helmet_bonuses()['crit_rate']
        for card_id in self.slots:
            if not card_id:
                continue
            try:
                attrs = self.card_attributes(card_id)
            except ValueError:
                continue
            stats['attack_pct_bonus'] += float(attrs.get('attack_pct', 0.0))
            stats['defense'] += int(attrs.get('defense', 0))
            stats['precision'] += int(attrs.get('precision', 0))
            stats['amp'] += float(attrs.get('amp', 0.0))
            stats['crit_rate'] += float(attrs.get('crit_rate', 0.0))
            stats['crit_damage'] += float(attrs.get('crit_damage', 0.0))
            stats['min_damage_bonus'] += int(attrs.get('min_damage_bonus', 0))
        # A Carta Única aplica seu buff a cada carta equipada do mesmo elemento.
        special_id = self.gauntlet_special_slot
        if self.is_unique_card(special_id):
            element, _, _ = self.unique_card_parts(special_id)
            matching = self.matching_equipped_element_cards(element)
            for effect in self.unique_card_effects():
                kind = effect['kind']
                value = effect['value'] * matching
                if kind == 'attack':
                    # Bônus de ataque de Carta Única são percentuais e escalam
                    # por carta equipada do mesmo tipo.
                    stats['attack_pct_bonus'] += value
                elif kind == 'min_damage':
                    stats['min_damage_bonus'] += int(round(value))
                elif kind == 'crit_rate':
                    stats['crit_rate'] += value
                elif kind == 'crit_damage':
                    stats['crit_damage'] += value / 100.0
                elif kind == 'amp':
                    stats['amp'] += value
        stats['attack'] = round(stats['attack'] * (1.0 + stats['attack_pct_bonus'] / 100.0), 2)
        # Efeito temporário da carta lendária Fulgor de RY.
        battle = self.battle or {}
        stats['attack'] += float(battle.get('player_attack_bonus_flat', 0.0) or 0.0)
        stats['precision'] += int(battle.get('player_precision_bonus_flat', 0) or 0)
        stats['min_damage_bonus'] += int(battle.get('player_min_damage_bonus_flat', 0) or 0)
        # Efeitos temporários aplicados por criaturas afetam somente o combate atual.
        attack_reduction = max(0.0, min(100.0, float(battle.get('player_attack_reduction_pct', 0.0))))
        defense_reduction = max(0.0, min(100.0, float(battle.get('player_defense_reduction_pct', 0.0))))
        precision_reduction = max(0, int(battle.get('player_precision_reduction', 0) or 0))
        if attack_reduction:
            stats['attack'] = round(stats['attack'] * (1.0 - attack_reduction / 100.0), 2)
        if defense_reduction:
            stats['defense'] = max(0, int(round(stats['defense'] * (1.0 - defense_reduction / 100.0))))
        if precision_reduction:
            stats['precision'] = max(0, stats['precision'] - precision_reduction)
        stats['crit_rate'] = max(0.0, min(100.0, stats['crit_rate']))
        stats['crit_damage'] = max(1.0, stats['crit_damage'])
        return stats

    @staticmethod
    def nexus_xp_for_level(level):
        from content import NEXUS_LEVEL_XP
        return NEXUS_LEVEL_XP.get(level)

    def _apply_nexus_level_reward(self, level):
        from content import NEXUS_NODES
        node_id = f'nexus_level_{int(level):02d}'
        node = NEXUS_NODES.get(node_id)
        if not node or node_id in self.gauntlet_nexus_nodes:
            return None
        kind = node.get('kind')
        value = float(node.get('value', 0) or 0)
        if kind == 'stat':
            field = node.get('field')
            if field in self.combat_stats:
                self.combat_stats[field] = float(self.combat_stats.get(field, 0.0)) + value
                if field in ('precision', 'min_damage_bonus'):
                    self.combat_stats[field] = int(round(self.combat_stats[field]))
        elif kind == 'drop':
            self.gauntlet_nexus_drop_bonus_pct = max(0.0, min(50.0, float(self.gauntlet_nexus_drop_bonus_pct) + value))
        elif kind == 'advantage':
            self.gauntlet_nexus_advantage_bonus_pct = max(0.0, min(50.0, float(self.gauntlet_nexus_advantage_bonus_pct) + value))
        elif kind == 'vampirism':
            self.gauntlet_nexus_vampirism_pct = max(0.0, min(5.0, float(self.gauntlet_nexus_vampirism_pct) + value))
        self.gauntlet_nexus_nodes.append(node_id)
        return node

    def gain_gauntlet_xp(self, amount):
        """1 ponto de dano causado pela Manopla = 1 XP do NEXUS."""
        if not self.gauntlet_nexus_installed or amount <= 0:
            return 0
        from content import NEXUS_LEVEL_XP
        max_xp = NEXUS_LEVEL_XP[max(NEXUS_LEVEL_XP)]
        self.gauntlet_nexus_xp = min(max_xp, self.gauntlet_nexus_xp + int(amount))
        level_ups = 0
        while self.gauntlet_nexus_level < max(NEXUS_LEVEL_XP) and self.gauntlet_nexus_xp >= NEXUS_LEVEL_XP[self.gauntlet_nexus_level + 1]:
            self.gauntlet_nexus_level += 1
            node = self._apply_nexus_level_reward(self.gauntlet_nexus_level)
            level_ups += 1
            if node:
                self.journal_add(f'nexus_level_{self.gauntlet_nexus_level}', 'A Manopla aprendeu', f'O NEXUS atingiu o nível {self.gauntlet_nexus_level}: {node["description"]}')
        return level_ups

    def nexus_progress(self):
        from content import NEXUS_LEVEL_XP
        if not self.gauntlet_nexus_installed:
            return 0, NEXUS_LEVEL_XP[2], 1, NEXUS_LEVEL_XP[2]
        if self.gauntlet_nexus_level >= max(NEXUS_LEVEL_XP):
            return 0, 0, self.gauntlet_nexus_level, None
        previous = 0 if self.gauntlet_nexus_level <= 1 else NEXUS_LEVEL_XP.get(self.gauntlet_nexus_level, 0)
        target = NEXUS_LEVEL_XP[self.gauntlet_nexus_level + 1]
        return max(0, self.gauntlet_nexus_xp - previous), target - previous, self.gauntlet_nexus_level, target

    def buy_nexus_node(self, node_id):
        return False, 'A progressão atual do NEXUS é automática: cada nível aplica sua própria melhoria.'

    def journal_add(self, entry_id, title, text):
        if entry_id in self.journal['seen']:
            return False
        self.journal['seen'].append(entry_id)
        self.journal['entries'].append({
            'id': entry_id,
            'title': title,
            'text': text,
            'time': round(self.time, 2),
        })
        return True

    def objective(self, oid):
        return self.journal['objectives'][oid]

    def set_objective(self, oid, status=None, progress=None):
        obj = self.journal['objectives'][oid]
        changed = False
        old_status, old_progress = obj.get('status'), obj.get('progress', 0)
        if status is not None and obj['status'] != status:
            obj['status'] = status
            changed = True
        if progress is not None and obj['progress'] != progress:
            obj['progress'] = progress
            changed = True
        if changed and oid in {'water_mission','faction_conflict','kuvaar','ship','explore_space','ry_investigation','dobra_core_install','alphor_path','broom_path','respawn_tank'}:
            new_status = obj.get('status')
            new_progress = obj.get('progress', 0)
            if new_status == 'completed' and old_status != 'completed':
                self._mission_completed_alert(oid)
            elif new_status == 'active' and old_status in (None, 'locked', 'available'):
                self.mission_started_alert(oid)
            elif old_status != new_status or old_progress != new_progress:
                self.mission_updated_alert(oid)
        return changed

    def renown_label(self):
        if self.renown < 20:
            return 'TEMIDO'
        if self.renown < 40:
            return 'DESCONFIADO'
        if self.renown < 60:
            return 'NEUTRO'
        if self.renown < 80:
            return 'RESPEITADO'
        return 'HONRADO'

    def change_renown(self, delta, reason):
        old = self.renown
        self.renown = max(0, min(100, int(self.renown + delta)))
        if self.renown != old:
            self.renown_events.append({'delta': self.renown - old, 'reason': reason, 'time': round(self.time, 2)})
            return True
        return False

    def nearby_landmarks(self, radius=1):
        """Retorna pontos de interesse próximos, em ordem de interação previsível.

        A prioridade evita que um marco apenas informativo esconda, por estar na
        mesma vizinhança, uma estação/terminal/boss que o jogador realmente
        consegue usar. A distância continua sendo a primeira regra: o ponto
        exato onde o personagem está sempre vence um ponto adjacente.
        """
        candidates = []
        for order, landmark in enumerate(self.area.get('landmarks', [])):
            dist = distance(self.pos, landmark['pos'])
            if dist > radius:
                continue
            if landmark.get('boss_site'):
                priority = 0
            elif landmark.get('mission_site') or landmark.get('hack_site') or landmark.get('diversion'):
                priority = 1
            elif landmark.get('cultural'):
                priority = 2
            else:
                priority = 3
            candidates.append((dist, priority, order, landmark))
        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        return [item[3] for item in candidates]

    def nearby_landmark(self):
        nearby = self.nearby_landmarks(1)
        return nearby[0] if nearby else None

    def analyze_culture(self):
        if self.current_planet_id() == 'nahr':
            return self.analyze_nahr_culture()
        if not self.helmet_equipped:
            return False, 'A análise cultural exige o elmo equipado.', False
        landmark = self.nearby_landmark()
        if not landmark or not landmark.get('cultural'):
            return False, 'Nenhum registro cultural próximo.', False
        sid = landmark['id']
        if sid in self.journal['seen']:
            return False, 'Registro cultural já analisado.', False
        self.journal['seen'].append(sid)
        self.language_progress = min(3, self.language_progress + 1)
        changed = self.journal_add(f'culture_{sid}', 'Análise cultural', f'A Manopla extrai padrões do registro {sid}. Progresso linguístico Avari: {self.language_progress}/3.')
        if self.language_progress >= 3 and not self.language_mastered:
            self.language_mastered = True
            changed |= self.set_objective('language', 'completed', 3)
            changed |= self.journal_add('language_mastered', 'Primeiras palavras', 'Os padrões linguísticos convergem. A Manopla consegue estabelecer uma tradução funcional do Avari. A comunicação com os habitantes de Veyra agora é possível.')
            if self.missions['water_supply']['status'] == 'locked':
                self.missions['water_supply']['status'] = 'available'
                changed |= self.set_objective('water_mission', 'active', 0)
        else:
            changed |= self.set_objective('language', 'active', self.language_progress)
        return True, f'Análise cultural concluída. Progresso linguístico: {self.language_progress}/3.', changed

    def achievement_data(self, aid):
        if aid in ACHIEVEMENTS:
            return ACHIEVEMENTS[aid]
        prefix = 'creature_1000_'
        if isinstance(aid, str) and aid.startswith(prefix):
            return creature_achievement_data(aid[len(prefix):])
        if isinstance(aid, str) and aid.startswith('boss_'):
            parts = aid.split('_', 2)
            if len(parts) == 3:
                try:
                    return boss_achievement_data(parts[2], int(parts[1]))
                except (ValueError, TypeError):
                    pass
        return None

    def ensure_creature_achievement(self, species_id):
        data = creature_achievement_data(species_id)
        if not data:
            return False
        aid = creature_achievement_id(species_id)
        if aid not in self.achievements:
            self.achievements[aid] = {'unlocked': False, 'claimed': False}
            return True
        self.achievements[aid].setdefault('unlocked', False)
        self.achievements[aid].setdefault('claimed', False)
        return False

    def refresh_achievements(self):
        changed = False
        def unlock(aid):
            nonlocal changed
            entry = self.achievements.setdefault(aid, {'unlocked': False, 'claimed': False})
            data = self.achievement_data(aid)
            if data and not entry.get('unlocked'):
                entry['unlocked'] = True
                entry.setdefault('claimed', False)
                self.achievement_alerts.append({'type': 'unlocked', 'aid': aid})
                self.journal_add(f'achievement_{aid}', 'Conquista desbloqueada', f'{data["name"]}: {data["reward"]}.')
                changed = True
        stats = self.statistics
        total_kills = sum(self.kills.values())
        if total_kills >= 1: unlock('first_blood')
        if stats['max_damage_taken'] >= 12: unlock('desert_survivor')
        if stats['collectibles'].get('Sucata', 0) >= 20: unlock('salvager')
        if len(set(self.visited)) >= 7: unlock('pathfinder')
        if self.missions.get('water_supply', {}).get('status') == 'completed': unlock('waterkeeper')
        if self.helmet_equipped: unlock('helmet_rebuilt')
        if stats['mission_paths'].get('hack', 0) >= 1: unlock('clean_intrusion')
        if stats['mission_paths'].get('force', 0) >= 1: unlock('force_of_will')
        known_species = list(dict.fromkeys(list(self.bestiary_known) + [sid for sid, count in self.kills.items() if count > 0 and sid in SPECIES]))
        for species_id in known_species:
            if self.ensure_creature_achievement(species_id):
                changed = True
            aid = creature_achievement_id(species_id)
            if self.kills.get(species_id, 0) >= 1000:
                unlock(aid)
        
        # Conquistas próprias dos bosses. 100 e 1000 usam somente vitórias virtuais,
        # portanto nunca podem ser completadas fora do Simulador de Combate.
        for boss_id in BOSSES:
            eligible = boss_id == 'kuvaar' or self.ship_flight_ready()
            if not eligible:
                continue
            boss_state = self.bosses.get(boss_id, {})
            real_defeats = int(stats.get('bosses_defeated', {}).get(boss_id, 0) or 0)
            virtual_defeats = int(boss_state.get('virtual_defeats', 0) or 0)
            aid1 = boss_achievement_id(boss_id, 1)
            aid100 = boss_achievement_id(boss_id, 100)
            aid1000 = boss_achievement_id(boss_id, 1000)
            self.achievements.setdefault(aid1, {'unlocked': False, 'claimed': False})
            self.achievements.setdefault(aid100, {'unlocked': False, 'claimed': False})
            self.achievements.setdefault(aid1000, {'unlocked': False, 'claimed': False})
            if real_defeats >= 1:
                unlock(aid1)
            if self.achievements.get(aid1, {}).get('unlocked') and virtual_defeats >= 100:
                unlock(aid100)
            if self.achievements.get(aid100, {}).get('unlocked') and virtual_defeats >= 1000:
                unlock(aid1000)

        for aid, variant in (('card_collector_normal','normal'), ('card_collector_plus','plus'), ('card_collector_plusplus','plusplus')):
            if all(any((not self.is_unique_card(c)) and self.card_parts(c)[0] == base and self.card_parts(c)[1] == variant for c in self.crafted) for base in CARDS):
                unlock(aid)
        return changed

    def apply_achievement_reward(self, aid):
        data = self.achievement_data(aid)
        if not data:
            return
        reward_type = data.get('reward_type')
        if reward_type == 'item':
            item = data.get('reward_item')
            amount = int(data.get('reward_amount', 0))
            if item and amount > 0:
                self.inventory[item] = self.inventory.get(item, 0) + amount
        elif reward_type == 'card_variant':
            base_id = data.get('reward_card')
            variant = data.get('reward_variant', 'plus')
            if base_id in CARDS and variant in CARD_VARIANTS:
                if base_id not in self.known_cards:
                    self.known_cards.append(base_id)
                serial = self._next_card_serial(base_id)
                instance_id = f'{base_id}|{variant}|{serial}'
                self.crafted.append(instance_id)
                self.statistics['cards_crafted'][variant] = self.statistics['cards_crafted'].get(variant, 0) + 1
        elif reward_type in ('stat', 'stat_and_unique'):
            field = data.get('reward_stat')
            amount = data.get('reward_amount', 0)
            if field in self.combat_stats:
                self.combat_stats[field] += amount
            if reward_type == 'stat_and_unique' and 'prototype_unique_card' not in self.unique_rewards:
                self.unique_rewards.append('prototype_unique_card')

    def pop_achievement_alert(self):
        if not self.achievement_alerts:
            return None
        return self.achievement_alerts.pop(0)

    @staticmethod
    def _canonical_mission_id(mission_id):
        return {
            'water_mission': 'water_supply',
            'kuvaar': 'kuvaar_hunt',
            'explore_space': 'explore_galaxy',
        }.get(mission_id, mission_id)

    def mission_started_alert(self, mission_id):
        """Enfileira um alerta de missão uma única vez por aquisição."""
        canonical = self._canonical_mission_id(mission_id)
        if any(a.get('type') == 'mission_started' and self._canonical_mission_id(a.get('mid')) == canonical
               for a in self.achievement_alerts if isinstance(a, dict)):
            return False
        self.achievement_alerts.append({'type': 'mission_started', 'mid': canonical})
        return True

    def mission_updated_alert(self, mission_id):
        canonical = self._canonical_mission_id(mission_id)
        if any(a.get('type') == 'mission_updated' and self._canonical_mission_id(a.get('mid')) == canonical
               for a in self.achievement_alerts if isinstance(a, dict)):
            return False
        self.achievement_alerts.append({'type': 'mission_updated', 'mid': canonical})
        return True

    def claim_achievement(self, aid):
        data = self.achievement_data(aid)
        if not data:
            return False, 'Conquista desconhecida.'
        entry = self.achievements.setdefault(aid, {'unlocked': False, 'claimed': False})
        if not entry.get('unlocked'):
            return False, 'A conquista ainda não foi desbloqueada.'
        if entry.get('claimed', False):
            return False, 'A recompensa desta conquista já foi recebida.'
        self.apply_achievement_reward(aid)
        entry['claimed'] = True
        self.achievement_alerts.append({'type': 'claimed', 'aid': aid})
        reward = data['reward']
        return True, f'Conquista recebida: {data["name"]}. Recompensa: {reward}.'

    def ry_mission_title(self):
        from world import SECTORS as _SECTORS
        map_name = _SECTORS.get('nahr_ry_void', {}).get('name', 'Vazio de RY')
        mission = self.missions.get('ry_investigation', {})
        return f'Investigue a história do {map_name}' if mission.get('stage') in ('history', 'boss_ready') else f'Investigue {map_name}'

    def _galaxy_path_key(self, galaxy_id):
        return 'alphor_path' if galaxy_id == 'vharos' else 'broom_path' if galaxy_id == 'meridion' else None

    def galaxy_boss_progress(self, galaxy_id):
        rare = tuple(GALAXY_RARE_BOSSES.get(galaxy_id, ()))
        flags = {bid: bool(self.bosses.get(bid, {}).get('defeated', False)) for bid in rare}
        return flags, sum(flags.values()), len(rare)

    def _sync_galaxy_boss_missions(self, emit_alert=False):
        changed = False
        for galaxy_id, legendary_id in GALAXY_LEGENDARY_BOSSES.items():
            mission_id = self._galaxy_path_key(galaxy_id)
            if not mission_id:
                continue
            mission = self.missions.setdefault(mission_id, {
                'status':'locked', 'galaxy':galaxy_id, 'boss':legendary_id,
                'progress':0, 'flags':{}
            })
            flags, progress, total = self.galaxy_boss_progress(galaxy_id)
            mission['flags'] = flags
            mission['progress'] = progress
            if self.dobra_core_installed:
                if mission.get('status') == 'locked':
                    mission['status'] = 'active'
                    changed |= self.set_objective(mission_id, 'active', progress)
                    changed |= self.journal_add(
                        f'{mission_id}_start', OBJECTIVES[mission_id]['title'],
                        f'A rota para {GALAXIES.get(galaxy_id, {}).get("name", galaxy_id)} foi aberta. {total} bosses raros protegem o acesso ao encontro lendário.'
                    )
                    if emit_alert:
                        self.mission_started_alert(mission_id)
                else:
                    changed |= self.set_objective(mission_id, mission.get('status'), progress)
                if total and progress >= total and mission.get('status') != 'completed':
                    mission['status'] = 'completed'
                    changed |= self.set_objective(mission_id, 'completed', progress)
                    changed |= self.journal_add(
                        f'{mission_id}_ready', OBJECTIVES[mission_id]['title'],
                        f'Todos os bosses raros de {GALAXIES.get(galaxy_id, {}).get("name", galaxy_id)} foram derrotados. {BOSSES[legendary_id]["name"]} pode ser enfrentado.'
                    )
                    self._mission_completed_alert(mission_id)
            else:
                if mission.get('status') != 'locked':
                    mission['status'] = 'locked'
                    changed |= self.set_objective(mission_id, 'locked', progress)
        return changed

    def boss_available(self, boss_id):
        if boss_id not in BOSSES:
            return False
        entry = self.bosses.get(boss_id, {})
        if boss_id != 'ry' and entry.get('defeated', False):
            return False
        if boss_id == 'ry':
            mission = self.missions.get('ry_investigation', {})
            return mission.get('stage') == 'boss_ready' and mission.get('status') == 'completed' and not entry.get('defeated', False)
        boss = BOSSES[boss_id]
        galaxy_id = boss.get('galaxy')
        if boss.get('legendary') and galaxy_id in GALAXY_LEGENDARY_BOSSES:
            _, progress, total = self.galaxy_boss_progress(galaxy_id)
            return bool(self.dobra_core_installed and total and progress >= total)
        return True

    def _sync_ry_mission_flags(self):
        mission = self.missions.setdefault('ry_investigation', fresh_missions()['ry_investigation'])
        defeats = self.statistics.get('bosses_defeated', {})
        flags = mission.setdefault('flags', {})
        changed = False
        for bid in ('kuvaar', 'kael', 'ounull', 'fagor'):
            value = int(defeats.get(bid, 0) or 0) >= 1
            if bool(flags.get(bid, False)) != value:
                flags[bid] = value
                changed = True
        mission['progress'] = sum(1 for bid in ('kuvaar', 'kael', 'ounull', 'fagor') if flags.get(bid))
        if mission.get('status') == 'active' and mission.get('stage') == 'bosses' and mission['progress'] >= 4:
            # Caso o jogador já tenha aprendido Nahrim e conversado com o povo antes
            # de concluir os quatro bosses, a etapa de conversa não precisa ser repetida.
            if self.nahr_language_mastered and self.nahr_ry_contacted:
                mission['stage'] = 'boss_ready'
                mission['status'] = 'completed'
                mission['reward_claimed'] = True
                self.set_objective('ry_investigation', 'completed', 4)
                self._mission_completed_alert('ry_investigation')
                self.journal_add('ry_history_previously_known', 'A história já conhecida', 'Você já havia aprendido Nahrim e conversado com o povo de Nahr antes de derrotar os quatro bosses. A etapa de investigar a história do Vazio de RY foi considerada concluída.')
                changed = True
            else:
                mission['stage'] = 'history'
                self.set_objective('ry_investigation', 'active', 4)
                self.journal_add('ry_bosses_complete', self.ry_mission_title(), 'Kuvaar, Trembe, Ounull e Fagor foram derrotados. A Manopla agora registra que o próximo passo é compreender a história do Vazio de RY e conversar com o povo de Nahr.')
                changed = True
        return changed

    def ensure_ry_investigation_mission(self):
        if not self.ship_flight_ready() or not self.has_left_veyra:
            return False
        mission = self.missions.setdefault('ry_investigation', fresh_missions()['ry_investigation'])
        changed = False
        if mission.get('status') == 'locked':
            mission['status'] = 'active'
            mission['stage'] = 'bosses'
            self.mission_started_alert('ry_investigation')
            changed |= self.journal_add('ry_investigation_unlock', self.ry_mission_title(), 'Uma anomalia foi registrada no Vazio de RY. Para investigar o local, será necessário derrotar primeiro os quatro grandes bosses de Nárion e, depois, compreender a história guardada pelo povo de Nahr.')
            changed = True
        changed |= self._sync_ry_mission_flags()
        if mission.get('stage') == 'bosses':
            changed |= self.set_objective('ry_investigation', 'active', int(mission.get('progress', 0)))
        elif mission.get('stage') == 'history':
            changed |= self.set_objective('ry_investigation', 'active', 4)
        elif mission.get('stage') == 'boss_ready':
            changed |= self.set_objective('ry_investigation', 'completed', 4)
        return changed

    def complete_ry_history(self):
        mission = self.missions.get('ry_investigation', {})
        if mission.get('stage') != 'history' or not self.nahr_language_mastered:
            return False, 'O povo de Nahr ainda não conseguiu comunicar a história do Vazio de RY.', False
        mission['stage'] = 'boss_ready'
        mission['status'] = 'completed'
        mission['progress'] = 4
        mission['reward_claimed'] = True
        self.nahr_ry_contacted = True
        self.statistics['missions_completed'] += 1
        changed = self.set_objective('ry_investigation', 'completed', 4)
        changed |= self.journal_add('ry_history_revealed', 'O Vazio de RY', 'As Sombras de Nahr contam que uma esfera de luz disforme habita o vazio e é tratada como a personificação da morte. RY é um nome sussurrado como o de um bicho-papão que aparece para executar quem deseja. O centro do mapa parece ser o seu domínio.')
        self._mission_completed_alert('ry_investigation')
        return True, 'A história de RY foi revelada. O povo de Nahr aponta para o vazio: a presença que todos temem agora pode ser encontrada.', changed

    def analyze_nahr_culture(self):
        if not self.helmet_equipped or int(self.helmet_generation) < 1:
            return False, 'A análise cultural de Nahr exige o Elmo Tier 1 equipado.', False
        landmark = self.nearby_landmark()
        if not landmark or not landmark.get('cultural') or landmark.get('civilization') != 'nahr_shadows':
            return False, 'Nenhuma fonte cultural de Nahr está próxima.', False
        sid = landmark['id']
        if sid in self.journal['seen']:
            return False, 'Fonte cultural já analisada.', False
        self.journal['seen'].append(sid)
        self.nahr_language_progress = min(3, self.nahr_language_progress + 1)
        changed = self.journal_add(f'culture_{sid}', 'Cultura de Nahr', f'A Manopla extrai padrões da fonte {sid}. Progresso linguístico Nahrim: {self.nahr_language_progress}/3.')
        if self.nahr_language_progress >= 3 and not self.nahr_language_mastered:
            self.nahr_language_mastered = True
            self.discover_civilization_on_planet('nahr', 'nahr_shadows')
            changed |= self.journal_add('nahr_language_mastered', 'O idioma das sombras', 'Os ecos e gestos finalmente formam um padrão estável. A Manopla aprendeu o Nahrim e consegue traduzir as falas das pequenas sombras de Nahr.')
            changed |= self.set_objective('ry_investigation', 'active', int(self.missions.get('ry_investigation', {}).get('progress', 0)))
        else:
            changed |= self.set_objective('ry_investigation', 'active', int(self.missions.get('ry_investigation', {}).get('progress', 0)))
        return True, f'Fonte cultural analisada. Progresso Nahrim: {self.nahr_language_progress}/3.', changed

    def refresh_journal(self, refresh_achievement_state=True):
        changed = False
        changed |= self.ensure_laser_project_mission()
        changed |= self.ensure_travel_repair_mission()
        if self.at_ship() and self.objective('survive')['status'] == 'active':
            changed |= self.set_objective('survive', 'completed', 1)
            changed |= self.journal_add('ship_safe', 'A nave ainda respira', 'O casco está comprometido, mas o abrigo, a bancada e o núcleo de energia continuam utilizáveis. Os sistemas de voo são outra história.')
            changed |= self.set_objective('ship', 'active')
        if 'ruins' in self.visited:
            changed |= self.set_objective('unknown_signal', 'completed', 1)
            changed |= self.journal_add('civilization_trace', 'Sinais de civilização', 'As ruínas não são formações naturais. Há estruturas, inscrições e vestígios tecnológicos de uma sociedade que ainda pode existir em algum lugar deste planeta.')
            changed |= self.set_objective('records', 'active')
            changed |= self.set_objective('settlement', 'active')
        settlement = self.area.get('settlement')
        if settlement and distance(self.pos, settlement['center']) <= settlement['sight_radius']:
            if settlement['id'] not in self.society['discovered_settlements']:
                self.society['discovered_settlements'].append(settlement['id'])
                changed = True
                faction = settlement.get('faction')
                if faction and faction in FACTIONS:
                    community_name = FACTIONS[faction].get('name', faction)
                else:
                    civ = CIVILIZATIONS.get(settlement.get('civilization'), {})
                    community_name = civ.get('name', settlement.get('civilization', 'local'))
                changed |= self.journal_add(
                    'first_sighting',
                    'Primeiro avistamento',
                    f'Você avista o assentamento {settlement["name"]}. Há habitantes, estruturas e atividade organizada. A Manopla identifica a presença da civilização {community_name}. O idioma será interpretado normalmente quando já fizer parte do banco conhecido; caso contrário, o Elmo iniciará uma calibração durante o primeiro contato.',
                )
            changed |= self.set_objective('settlement', 'completed', len(self.society['discovered_settlements']))
        progress = len(set(self.visited))
        changed |= self.set_objective('explore', progress=progress)
        if progress >= 8 and self.objective('explore')['status'] != 'completed':
            changed |= self.set_objective('explore', 'completed', progress)
            changed |= self.journal_add('planet_mapped', 'Veyra começa a se abrir', 'Oito setores acessíveis foram reconhecidos. Os assentamentos locais ocupam apenas uma pequena parte do planeta.')
        fragments = self.inventory.get('Fragmento histórico', 0)
        changed |= self.set_objective('records', progress=min(3, fragments))
        if fragments >= 3 and self.objective('records')['status'] != 'completed':
            changed |= self.set_objective('records', 'completed', 3)
            changed |= self.journal_add('records_complete', 'Arquivo incompleto', 'Três fragmentos foram recuperados. A escrita permanece indecifrável, mas os registros sugerem uma civilização organizada e tecnologicamente avançada.')
        if self.helmet_owned:
            changed |= self.set_objective('helmet', 'completed', 1)
            if self.objective('language')['status'] == 'locked':
                changed |= self.set_objective('language', 'active', self.language_progress)
        elif (self.objective('records')['status'] == 'completed' or self.society['discovered_settlements']):
            changed |= self.set_objective('helmet', 'active', 0)
        if self.language_mastered and self.missions['water_supply']['status'] == 'locked':
            self.missions['water_supply']['status'] = 'available'
            changed |= self.set_objective('water_mission', 'active', 0)
        if self.missions.get('water_supply', {}).get('status') == 'completed' and self.missions.get('kuvaar_hunt', {}).get('status') == 'locked':
            self.missions['kuvaar_hunt']['status'] = 'available'; self.missions['kuvaar_hunt']['stage'] = 0
            changed |= self.set_objective('kuvaar', 'active', 0)
            changed |= self.journal_add('kuvaar_hunt_unlock_auto', 'A sede não terminou', 'A água voltou, mas novos poços continuam secando. A crise parece ter uma causa viva e gigantesca na bacia ao redor de Qaresh.')
        if self.missions.get('water_supply', {}).get('status') == 'completed' and self.missions.get('faction_conflict', {}).get('status') == 'locked':
            self.missions['faction_conflict']['status'] = 'available'
            changed |= self.set_objective('faction_conflict', 'active', 0)
            changed |= self.journal_add('faction_conflict_unlock', 'Sussurros na Fenda', 'Depois que você se envolveu na crise dos reservatórios, uma facção que se opõe aos Guardiões passa a observar seus movimentos. Alguém no Cânion de Nahar parece querer falar com você.')
        changed |= self.ensure_exploration_mission()
        changed |= self.ensure_ry_investigation_mission()
        changed |= self.ensure_dobra_core_mission()
        if refresh_achievement_state:
            changed |= self.refresh_achievements()
        return changed

    def analyze_ship(self):
        if not self.ship_access():
            return None, 'Entre na nave para executar o diagnóstico.', False
        rows = []
        for sid in SHIP_DIAGNOSTIC_ORDER:
            data = SHIP_SYSTEMS[sid]
            condition = int(self.ship_systems.get(sid, data['condition']))
            rows.append({
                'id': sid,
                'name': data['name'],
                'condition': condition,
                'status': data['status'],
                'detail': data['detail'],
                'repair': data.get('repair', 'Sem requisito conhecido.'),
            })
        critical = [row['name'] for row in rows if row['condition'] < 20]
        if critical:
            summary = 'DIAGNÓSTICO: decolagem indisponível. ' + ', '.join(critical[:2]) + (' e outros subsistemas exigem reparo.' if len(critical) > 2 else ' exigem reparo.')
        else:
            summary = 'DIAGNÓSTICO: sistemas de voo dentro dos limites operacionais.'
        changed = self.journal_add(
            'ship_diagnostic',
            'Diagnóstico da nave',
            'A análise da Manopla revela um quadro severo: o núcleo de energia permanece utilizável, mas propulsão e navegação estão danificadas. Comunicação está offline e não há núcleo de dobra compatível detectado.',
        )
        changed |= self.set_objective('ship', 'active')
        return rows, summary, changed

    def move(self, dx, dy):
        if self.battle or (dx, dy) not in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            return False
        # Saídas internas (como Cânion -> Estação) podem ser atravessadas
        # quando o personagem está sobre o tile de acesso e segue a direção.
        for gate in self.area['exits']:
            if tuple(self.pos) == gate['at'] and (dx, dy) == gate['direction']:
                if gate.get('requires_locomotion') and self.locomotion_generation < 1:
                    return False
                self.sector = gate['target']
                self.pos = list(gate['arrival'])
                if self.sector not in self.visited:
                    self.visited.append(self.sector)
                self._refresh_all_civ_missions()
                self.refresh_journal()
                self.grace = 3
                return True
        p = [self.pos[0]+dx, self.pos[1]+dy]
        if all(0 <= v < self.area['size'] for v in p):
            if tuple(p) in self.area.get('water_tiles', set()) and self.locomotion_generation < 1:
                return False
            if tuple(p) not in self.area['rocks'] and not self.npc_at(p) and not self.boss_at(p):
                self.pos = p
                return True
            return False
        return False

    def loose_modules(self, module):
        return self.memory_owned[module] - self.memory_slots.count(module)

    def configure_memory(self, index, module):
        if self.battle or not self.at_ship():
            return 'Reconfigure o peitoral junto à nave, fora do combate.'
        if type(index) is not int or index not in range(TOTAL_MEMORY_SLOTS):
            return 'Encaixe de memória inválido.'
        if index >= self.max_memory_slots:
            return 'Este encaixe ainda está bloqueado pelo Tier atual do peitoral.'
        if module is not None and module not in MEMORY_MODULES:
            return 'Módulo desconhecido.'
        if module is not None and MEMORY_MODULES[module]['generation'] > self.chest_generation:
            return 'Incompatível: atualize o peitoral para G2 na bancada antes de instalar este módulo.'
        if self.memory_slots[index] == module:
            return 'Esse encaixe já está configurado assim.'
        if module is not None and self.loose_modules(module) <= 0:
            return 'Não há uma cópia livre deste módulo no estoque.'
        self.memory_slots[index] = module
        # Capacidade extra não recarrega memória; evita recuperação por trocas.
        self.memory = min(self.memory, self.max_memory)
        return ('Peitoral reconfigurado. O módulo anterior voltou ao estoque. '
                'Descanse para recuperar memória.')

    def tick(self, dt):
        self.time += dt
        self.grace = max(0, self.grace - dt)
        for e in self.enemies:
            if e['dead'] and self.time >= e['ready'] and distance(e['home'], self.pos) >= 3:
                if e.get('mission_id'):
                    continue
                occupied = any(not other['dead'] and other['pos'] == e['home'] for other in self.enemies)
                if not occupied:
                    e.update(dead=False, pos=e['home'].copy())

    def rest(self):
        if not self.at_ship() or self.battle:
            return 'Descanse junto à nave.'
        self.hp, self.memory = self.max_hp, self.max_memory
        return 'Sistemas recuperados. Respawns continuam no tempo normal.'

    def discover(self, cid):
        try:
            base_id = self.card_parts(cid)[0]
        except ValueError:
            return False
        if base_id not in CARDS:
            return False
        card = CARDS[base_id]
        species_id = card.get('species')
        if card.get('acquisition') == 'faction_conflict':
            mission = self.missions.get('faction_conflict', {})
            known = bool(self.card_instances(base_id)) or mission.get('status') == 'completed'
        elif species_id in BOSSES:
            # Algumas cartas de boss possuem ID diferente do boss (ex.:
            # alphor_fireball e broom_lightning). A derrota real do boss é a
            # única condição para abrir a receita.
            known = bool(self.bosses.get(species_id, {}).get('defeated')) or bool(self.card_instances(base_id))
        else:
            known = self.kills.get(species_id, 0) > 0 or bool(self.card_instances(base_id))
        if known and base_id not in self.known_cards:
            self.known_cards.append(base_id)
            self.achievement_alerts.append({'type': 'card', 'cid': base_id})
            self.journal_add(f'card_known_{base_id}', 'Carta conhecida', f"A Manopla registrou uma nova carta: {format_card_name(card['name'])}.")
        return known

    def register_bestiary_encounter(self, species_id):
        # Fauna comum: registra no Bestiário e, quando o Scan do Elmo está
        # disponível, libera também os dados ocultos (incluindo MANA).
        if species_id in SPECIES:
            changed = False
            if self.ensure_creature_achievement(species_id):
                changed = True
            if self.helmet_equipped and self.scan_unlocked and species_id not in self.bestiary_scanned:
                self.bestiary_scanned.append(species_id)
                changed = True
                self.refresh_advanced_research()
            self._refresh_all_civ_missions()
            return changed

        # Bosses não entram na lista de fauna comum do Bestiário, mas o Scan
        # precisa ser reconhecido no encontro para revelar seus dados de combate.
        if species_id in BOSSES:
            if self.helmet_equipped and self.scan_unlocked and species_id not in self.bestiary_scanned:
                self.bestiary_scanned.append(species_id)
                self.refresh_advanced_research()
                self._refresh_all_civ_missions()
                return True
            return False
        return False

    def _next_card_serial(self, base_id):
        serials = []
        for card_id in self.crafted:
            try:
                b_id, _, serial = self.card_parts(card_id)
            except ValueError:
                continue
            if b_id == base_id and serial:
                serials.append(serial)
        return max(serials, default=0) + 1

    def _roll_card_variant(self):
        roll = self.rng.random()
        cursor = 0.0
        for variant in ('normal', 'plus', 'plusplus'):
            cursor += float(CARD_VARIANTS[variant]['chance'])
            if roll < cursor:
                return variant
        return 'plusplus'

    def _roll_unique_buff_count(self):
        roll = self.rng.random(); cursor = 0.0
        for count in (1, 2, 3):
            cursor += float(UNIQUE_BUFF_COUNT_CHANCES[count])
            if roll < cursor:
                return count
        return 3

    def _roll_unique_buff_keys(self, count):
        selected = []
        available = {k: float(v['chance']) for k, v in UNIQUE_BUFF_DEFS.items()}
        for _ in range(max(1, min(3, int(count)))):
            remaining = [(k, w) for k, w in available.items() if k not in selected and w > 0]
            total = sum(w for _, w in remaining)
            if not remaining or total <= 0:
                break
            roll = self.rng.random() * total; cursor = 0.0
            for kind, weight in remaining:
                cursor += weight
                if roll < cursor:
                    selected.append(kind); break
        return selected

    def _roll_unique_momentum(self):
        """Retorna uma Momentum em 5% dos crafts de Carta Única."""
        if self.rng.random() >= float(UNIQUE_MOMENTUM_CHANCE):
            return None
        keys = tuple(UNIQUE_MOMENTUM_DEFS)
        if not keys:
            return None
        idx = min(len(keys) - 1, int(self.rng.random() * len(keys)))
        return keys[idx]

    def unique_card_momentum(self):
        cid = self.gauntlet_special_slot
        if not self.is_unique_card(cid):
            return None
        element, _, _ = self.unique_card_parts(cid)
        kind = self.unique_cards.get(cid, {}).get('momentum')
        if isinstance(kind, dict):
            kind = kind.get('kind')
        if kind not in UNIQUE_MOMENTUM_DEFS:
            return None
        return {'kind': kind, 'element': element, 'description': UNIQUE_MOMENTUM_DEFS[kind]['description'].format(type=element)}

    def matching_equipped_element_cards(self, element):
        if element not in CREATURE_TYPES:
            return 0
        matching = 0
        for equipped in self.slots:
            if not equipped or self.is_unique_card(equipped):
                continue
            try:
                base_id = self.card_parts(equipped)[0]
            except ValueError:
                continue
            if CARDS.get(base_id, {}).get('type') == element:
                matching += 1
        return matching

    def _next_unique_serial(self):
        serials = []
        for cid in self.unique_cards:
            try:
                serials.append(self.unique_card_parts(cid)[2])
            except ValueError:
                pass
        return max(serials, default=0) + 1

    def craft_card(self, cid):
        if self.battle:
            return 'Não é possível fabricar durante um combate.'
        if cid not in CARDS:
            return 'Carta inexistente.'
        card = CARDS[cid]
        if not card.get('recipe') or card.get('craftable') is False:
            return 'Esta carta não pode ser fabricada diretamente.'
        if card.get('acquisition') == 'faction_conflict':
            conflict = self.missions.get('faction_conflict', {})
            if conflict.get('status') != 'completed':
                return 'A origem desta carta ainda não foi registrada pela Manopla.'
            if cid != conflict.get('winner_card'):
                return 'Esta carta só pode ser obtida como consequência direta do conflito das facções.'
        elif not self.discover(cid):
            return 'Derrote esta espécie para analisar a receita.'
        recipe = card.get('recipe', {})
        # Essência pode estar tanto no inventário quanto no Armazenador da nave;
        # a Oficina usa esse mesmo total e o craft também precisa respeitá-lo.
        for i, q in recipe.items():
            available = self.essence_total() if i == 'Essência' else int(self.inventory.get(i, 0))
            if available < q:
                return 'Faltam materiais. Confira as quantidades na receita.'
        for i, q in recipe.items():
            if i == 'Essência':
                if not self.consume_essence(q):
                    return 'Faltam Essências. Confira o total disponível.'
            else:
                self.inventory[i] = int(self.inventory.get(i, 0)) - q
        variant = self._roll_card_variant()
        serial = self._next_card_serial(cid)
        instance_id = f'{cid}|{variant}|{serial}'
        self.crafted.append(instance_id)
        self.statistics['cards_crafted'][variant] = self.statistics['cards_crafted'].get(variant, 0) + 1
        return f'Carta fabricada: {self.card_name(instance_id)} [{card.get("rarity", "Comum")}]. Adicionada à Pool de cartas.'

    def craft_unique_card(self, source_card_id):
        if self.battle:
            return None, 'Não é possível fabricar durante um combate.'
        if not isinstance(source_card_id, str) or self.is_unique_card(source_card_id):
            return None, 'Selecione uma carta elemental como fonte.'
        try:
            base_id, _, _ = self.card_parts(source_card_id)
        except ValueError:
            return None, 'Carta-fonte inválida.'
        if source_card_id not in self.crafted or source_card_id in self.slots:
            return None, 'A carta-fonte precisa estar na Pool de cartas.'
        card = CARDS.get(base_id)
        element = card.get('type') if card else None
        if element not in CREATURE_TYPES:
            return None, 'A carta-fonte precisa possuir um elemento válido.'
        if self.essence_total() < UNIQUE_CARD_ESSENCE_COST:
            return None, f'Faltam Essências. Necessárias: {UNIQUE_CARD_ESSENCE_COST}.'
        self.consume_essence(UNIQUE_CARD_ESSENCE_COST)
        self.crafted.remove(source_card_id)
        variant = self._roll_card_variant()
        count = self._roll_unique_buff_count()
        kinds = self._roll_unique_buff_keys(count)
        momentum = self._roll_unique_momentum()
        serial = self._next_unique_serial()
        cid = f'unique|{element}|{variant}|{serial}'
        buffs = [{'kind': kind} for kind in kinds]
        labels = ', '.join(UNIQUE_BUFF_DEFS[kind]['label'] for kind in kinds)
        self.unique_cards[cid] = {
            'name': f'Carta Única — {element}', 'element': element, 'variant': variant,
            'rarity': 'Única', 'buffs': buffs, 'momentum': momentum, 'species': None,
            'description': f'Carta Única de {element}; {labels}.', 'source_card': source_card_id,
        }
        self.crafted.append(cid)
        self.statistics['cards_crafted'][variant] = self.statistics['cards_crafted'].get(variant, 0) + 1
        momentum_note = f' Momentum: {UNIQUE_MOMENTUM_DEFS[momentum]["description"].format(type=element)}' if momentum else ''
        return {'card_id': cid, 'source_card': source_card_id, 'element': element,
                'variant': variant, 'buff_count': len(buffs), 'buffs': buffs, 'momentum': momentum},                f'Carta Única de {element} criada. {len(buffs)} buff(s): {labels}.{momentum_note}'

    def equip_unique(self, cid):
        if self.battle or not self.is_unique_card(cid) or cid not in self.crafted:
            return False, 'Carta Única indisponível.'
        old = self.gauntlet_special_slot
        if old == cid:
            return True, 'Carta Única já está equipada.'
        self.gauntlet_special_slot = cid
        return True, f'{self.card_name(cid)} equipada no Slot Único.'

    def unequip_unique(self):
        if self.battle:
            return False, 'Não é possível alterar a Manopla durante um combate.'
        if not self.gauntlet_special_slot:
            return False, 'O Slot Único já está vazio.'
        cid = self.gauntlet_special_slot
        self.gauntlet_special_slot = None
        return True, f'{self.card_name(cid)} devolvida à Pool de cartas.'

    def remove_unique(self):
        # Compatibilidade com saves/testes antigos: a UI 0.6.6 não expõe mais
        # Removedor de Aprimoramento. A operação canônica é unequip_unique().
        return self.unequip_unique()

    def craft(self, cid):
        if cid == 'Essência':
            return 'Essência não pode ser fabricada. Ela é obtida ao derrotar criaturas.'
        if cid in CARDS:
            return self.craft_card(cid)
        if self.battle or not self.at_ship():
            return 'Fabricação disponível junto à nave.'
        if cid in MEMORY_RECIPES and self.memory_owned[MEMORY_RECIPES[cid]] >= CHEST_MEMORY_SLOTS:
            return 'Você já possui dois módulos deste tipo. Equipe-os pela tela G.'
        if cid == 'memory_g2' and self.chest_generation < 2:
            return 'Atualize primeiro o peitoral para Tier 2.'
        if cid == 'helmet_g2' and self.helmet_generation < 1:
            return 'Reconstrua primeiro o Elmo / Tier 1.'
        if cid == 'chest_g2' and self.chest_generation >= 2:
            return 'O peitoral já foi atualizado para G2.'
        if cid == 'chest_g3' and self.chest_generation >= 3:
            return 'O peitoral já está no Tier 3.'
        if cid == 'chest_g3' and self.chest_generation < 2:
            return 'Atualize primeiro o peitoral para Tier 2.'
        if cid == 'respawn_tank' and self.respawn_tank_built:
            return 'O Tanque de Renascimento já foi construído.'
        if cid == 'respawn_tank' and self.missions.get('respawn_tank', {}).get('status') != 'active':
            return 'A missão do Tanque de Renascimento ainda não foi iniciada.'
        if cid == 'helmet_g1' and self.helmet_owned:
            return 'O elmo já foi reconstruído.'
        if cid == 'helmet_g2' and self.helmet_generation >= 2:
            return 'O elmo já está no Tier 2.'
        if cid == 'gauntlet_nexus' and self.gauntlet_nexus_installed:
            return 'O NEXUS já foi instalado na Manopla.'
        if cid == 'combat_simulator':
            if not self.simulator_unlocked:
                return 'O projeto do Simulador ainda não foi liberado.'
            if self.simulator_built:
                return 'O Simulador de Combate já está construído.'
        if cid == 'simulation_charge' and not self.simulator_built:
            return 'Construa o Simulador de Combate antes de fabricar cargas.'
        if cid == 'memory_g3' and self.memory_owned.get('advanced', 0) < 1:
            return 'Fabrique primeiro um Módulo avançado.'
        if cid == 'water_purifier' and self.water_purifier_built:
            return 'O Purificador improvisado já está instalado na nave.'
        if cid == 'pure_water' and not self.water_purifier_built:
            return 'Construa o Purificador improvisado antes de produzir Água Pura.'
        if cid == 'locomotion_g1' and self.locomotion_generation >= 1:
            return 'O Módulo de Locomoção já foi instalado.'
        if cid == 'ship_laser' and self.ship_laser_installed:
            return 'O Emissor Laser já está instalado na nave.'
        if cid == 'ship_laser' and not self.ship_laser_project_unlocked:
            return 'O projeto do Emissor Laser ainda não foi adquirido.'
        if cid == 'dobra_core_install':
            return 'Instale o Núcleo de Dobra pelo Cockpit da nave.'
        if cid in OTHER_RECIPES:
            recipe = OTHER_RECIPES[cid]['recipe']
        else:
            from content import FUTURE_UPGRADES
            if cid not in FUTURE_UPGRADES:
                return 'Projeto de fabricação desconhecido.'
            recipe = FUTURE_UPGRADES[cid]['recipe']
        for i, q in recipe.items():
            available = self.essence_total() if i == 'Essência' else int(self.inventory.get(i, 0))
            if available < q:
                return 'Faltam materiais. Confira as quantidades na receita.'
        # Toda receita exposta pela Oficina deve ter um destino definido após o consumo.
        # Isso evita gastar materiais e terminar com um resultado silenciosamente perdido.
        craft_outputs = {
            'kit', 'chest_g2', 'memory_g2', 'memory', 'decoder_core', 'energy_cell',
            'water_purifier', 'pure_water', 'helmet_g1', 'helmet_g2', 'gauntlet_nexus',
            'respawn_tank', 'combat_simulator', 'simulation_charge', 'chest_g3',
            'memory_g3', 'locomotion_g1', 'ship_laser',
        }
        if cid not in craft_outputs:
            return 'Projeto de fabricação sem destino definido.'
        for i, q in recipe.items():
            if i == 'Essência':
                if not self.consume_essence(q):
                    return 'Faltam Essências. Confira o total disponível.'
            else:
                self.inventory[i] -= q
        if cid == 'kit':
            self.inventory['Kit'] = self.inventory.get('Kit', 0) + 1
            return 'Kit de reparo fabricado e adicionado ao inventário.'
        if cid == 'decoder_core':
            self.inventory['Núcleo de decodificação'] = self.inventory.get('Núcleo de decodificação', 0) + 1
            return 'Núcleo de decodificação fabricado e adicionado ao inventário.'
        if cid == 'energy_cell':
            self.inventory['Célula de energia instável'] = self.inventory.get('Célula de energia instável', 0) + 1
            return 'Célula de energia instável fabricada e adicionada ao inventário.'
        if cid == 'gauntlet_nexus':
            self.gauntlet_nexus_installed = True; self.gauntlet_nexus_xp = 0; self.gauntlet_nexus_level = 1; self.gauntlet_nexus_points = 0
            self.gauntlet_nexus_nodes = []; self.gauntlet_nexus_progression_revision = 8
            self.gauntlet_nexus_drop_bonus_pct = 0.0; self.gauntlet_nexus_advantage_bonus_pct = 0.0; self.gauntlet_nexus_vampirism_pct = 0.0
            self.gauntlet_nexus_hack_alert_capacity_bonus = 0; self.gauntlet_nexus_hack_diagonal = False; self.gauntlet_nexus_hack_mask_first_firewall = False
            self._apply_nexus_level_reward(1)
            self.journal_add('nexus_installed', 'Uma mente desperta', 'A atualização NEXUS foi integrada à Manopla. O sistema começa a registrar aprendizado de combate a partir do dano causado. Nível 1: +1 Precisão.')
            return 'NEXUS instalado. A Manopla agora aprende com cada ponto de dano causado.'
        if cid == 'combat_simulator':
            self.simulator_built = True
            self.journal_add('combat_simulator_built', 'Uma arena que não existe', 'O Simulador de Combate foi construído. Bosses derrotados podem ser reproduzidos sob condições virtuais favoráveis.')
            return 'Simulador de Combate construído. O rematch virtual de Kuvaar está disponível mediante uma Carga de Simulação.'
        if cid == 'simulation_charge':
            self.inventory['Carga de Simulação'] = self.inventory.get('Carga de Simulação', 0) + 1
            return 'Carga de Simulação armazenada.'
        if cid == 'respawn_tank':
            self.respawn_tank_built = True
            mission = self.missions.setdefault('respawn_tank', {'status':'active','progress':0,'reward_claimed':False})
            mission['status'] = 'completed'; mission['progress'] = 1; mission['reward_claimed'] = True
            self.statistics['missions_completed'] += 1
            self.set_objective('respawn_tank', 'completed', 1)
            self.journal_add('respawn_tank_built', 'Tanque reconstruído', 'O Tanque de Renascimento voltou a funcionar no interior da nave. Em caso de morte, o corpo poderá ser restaurado aqui com perda de 10% das Essências do inventário.')
            self._mission_completed_alert('respawn_tank')
            return 'Tanque de Renascimento construído. A nave agora pode restaurar seu corpo após uma morte.'
        if cid == 'water_purifier':
            self.water_purifier_built = True
            self.journal_add('water_purifier_built', 'Purificador improvisado', 'Você construiu um sistema artesanal capaz de transformar água bruta em uma pequena reserva de Água Pura. O equipamento permanece instalado na nave.')
            return 'Purificador improvisado construído. Ele permanece instalado na nave e pode produzir Água Pura.'
        if cid == 'pure_water':
            self.inventory['Água Pura'] = self.inventory.get('Água Pura', 0) + 5
            self.journal_add('pure_water_produced', 'Água pura', 'A nave converteu Água Bruta em uma reserva pequena de Água Pura. O recurso é valioso demais para ser desperdiçado.')
            return 'Cinco unidades de Água Pura armazenadas.'
        if cid == 'helmet_g1':
            self.helmet_generation=1; self.helmet_owned=True; self.helmet_equipped=True; self.helmet_design='tactical'; self.scan_unlocked=True
            self.set_objective('helmet','completed',1); self.set_objective('language','active',self.language_progress)
            self.journal_add('helmet_rebuilt','O elmo reconstruído','Os circuitos de análise cultural foram integrados ao elmo. Agora a Manopla pode extrair padrões linguísticos dos registros de Veyra.')
            self.refresh_achievements(); return 'Elmo reconstruído e equipado automaticamente. A análise cultural agora pode ser iniciada.'
        if cid == 'helmet_g2':
            self.helmet_generation=2; self.helmet_owned=True; self.helmet_equipped=True; self.helmet_design=self.helmet_design or 'tactical'; self.scan_unlocked=True
            self.journal_add('helmet_upgraded_g2','Elmo ampliado','O Elmo foi atualizado para Tier 2. O protocolo de Scan de rochas foi integrado e as passivas foram recalibradas.')
            return 'Elmo atualizado para Tier 2.'
        if cid == 'chest_g2':
            self.chest_generation=2; self.memory_slots=(self.memory_slots+[None]*TOTAL_MEMORY_SLOTS)[:TOTAL_MEMORY_SLOTS]; return 'Peitoral atualizado para Tier 2. Terceiro encaixe de memória habilitado.'
        if cid == 'chest_g3':
            self.chest_generation=3; self.memory_slots=(self.memory_slots+[None]*TOTAL_MEMORY_SLOTS)[:TOTAL_MEMORY_SLOTS]; return 'Peitoral atualizado para Tier 3. Quarto encaixe de memória habilitado.'
        if cid == 'memory_g3':
            self.memory_owned['advanced'] = self.memory_owned.get('advanced', 0) + 1
            return 'Circuito de memória fabricado e guardado. Abra G para instalá-lo no peitoral.'
        if cid == 'locomotion_g1':
            self.locomotion_generation = 1
            self.locomotion_equipped = True
            return 'Módulo de Locomoção / Tier 1 instalado e equipado.'
        if cid == 'ship_laser':
            self.ship_laser_installed = True
            self.journal_add('ship_laser_installed', 'Emissor Laser instalado', 'O Emissor Laser foi integrado ao casco da nave. Durante travessias entre galáxias, a defesa poderá interceptar ameaças espaciais.')
            return 'Emissor Laser instalado na nave.'
        self.memory_owned[MEMORY_RECIPES[cid]] += 1
        return 'Módulo guardado. Abra G para instalá-lo no peitoral.'

    def ensure_dobra_core_mission(self):
        """Abre a missão simples de instalação assim que o Núcleo de Dobra entra no inventário.

        A instalação não é outro minigame: o jogador recebe a missão e a próxima
        interação com o Cockpit oferece diretamente a confirmação de instalação.
        """
        mission = self.missions.setdefault('dobra_core_install', {
            'status': 'locked', 'progress': 0, 'reward_claimed': False
        })
        if self.dobra_core_installed:
            if mission.get('status') != 'completed':
                mission['status'] = 'completed'
                mission['progress'] = 1
                self.set_objective('dobra_core_install', 'completed', 1)
            return False
        if int(self.inventory.get('Núcleo de Dobra', 0)) > 0:
            changed = False
            if mission.get('status') == 'locked':
                mission['status'] = 'active'
                mission['progress'] = 0
                changed |= self.set_objective('dobra_core_install', 'active', 0)
                changed |= self.journal_add(
                    'dobra_core_install_unlock',
                    'Núcleo recuperado',
                    'O Núcleo de Dobra recuperado de RY foi reconhecido pela nave. O motor pode ser potencializado. Acesse o Cockpit para confirmar a instalação.'
                )
                self.mission_started_alert('dobra_core_install')
            return changed
        return False

    def install_dobra_core(self):
        if self.battle or not self.at_ship():
            return False, 'A instalação do Núcleo de Dobra precisa ser feita no interior da nave.'
        if self.dobra_core_installed:
            return False, 'O Núcleo de Dobra já está instalado no motor.'
        if int(self.inventory.get('Núcleo de Dobra', 0)) <= 0:
            return False, 'Você precisa possuir o Núcleo de Dobra recuperado de RY.'
        mission = self.missions.setdefault('dobra_core_install', {'status':'active','progress':0,'reward_claimed':False})
        count_mission = mission.get('status') == 'active'
        self.inventory['Núcleo de Dobra'] -= 1
        self.dobra_core_installed = True
        for route in STELLAR_ROUTES:
            if route.get('galaxy') != GALAXY_ID:
                self.discover_planet(route['id'])
        mission['status'] = 'completed'
        mission['progress'] = 1
        self.set_objective('dobra_core_install', 'completed', 1)
        if count_mission:
            self.statistics['missions_completed'] += 1
        self._mission_completed_alert('dobra_core_install')
        self.journal_add('dobra_core_installed', 'A fronteira se abre', 'O Núcleo de Dobra foi acoplado ao motor. A matriz estelar reconhece duas regiões além de Nárion: Vharos e Meridion.')
        mission = self.missions.setdefault('explore_galaxy', {'status':'active','progress':1,'galaxies':[GALAXY_ID]})
        mission['status'] = 'active'
        mission.setdefault('galaxies', [])
        if GALAXY_ID not in mission['galaxies']:
            mission['galaxies'].append(GALAXY_ID)
        mission['progress'] = len(mission['galaxies'])
        self.selected_galaxy_id = 'vharos'
        self.set_objective('explore_space', 'active', mission['progress'])
        self._sync_galaxy_boss_missions(emit_alert=True)
        return True, 'Núcleo de Dobra instalado. A nave foi potencializada; Vharos e Meridion estão disponíveis na Rota Estelar.'

    def equip_helmet(self):
        if not self.helmet_owned:
            return False, 'O elmo ainda não foi reconstruído.'
        self.helmet_equipped = True
        self.helmet_design = self.helmet_design or 'tactical'
        return True, 'Elmo equipado automaticamente. A ação manual foi removida.'

    def equip(self, cid, index):
        if self.battle or index not in range(3):
            return False
        try:
            self.card_parts(cid)
        except ValueError:
            return False
        if cid not in self.crafted or self.is_unique_card(cid):
            return False
        old = self.slots[index]
        source = self.slots.index(cid) if cid in self.slots else None
        if source is not None and source != index:
            self.slots[source] = old
        self.slots[index] = cid
        return True

    def unequip(self, index):
        if self.battle or index not in range(3):
            return False, 'Slot inválido.'
        if not self.slots[index]:
            return False, 'Esse slot já está vazio.'
        removed = self.slots[index]
        self.slots[index] = None
        return True, f'{self.card_name(removed)} devolvida à Pool de cartas.'

    def remove_card(self, index):
        # Compatibilidade com chamadas antigas. A UI 0.6.6 usa unequip().
        return self.unequip(index)

    def npc_tiles(self, sector=None):
        sector = self.sector if sector is None else sector
        data = SECTORS[sector]
        eliminated = self.missions.get('faction_conflict', {}).get('loser') if self.missions.get('faction_conflict', {}).get('status') == 'completed' else None
        npcs = []
        settlement = data.get('settlement')
        if settlement:
            npcs.extend(settlement.get('npcs', []))
        site = data.get('faction_site')
        if site and site.get('faction') != eliminated:
            npcs.extend(site.get('npcs', []))
        return {tuple(npc['pos']) for npc in npcs if npc.get('solid', True) and (not eliminated or npc.get('faction') != eliminated)}

    def npc_at(self, pos, sector=None):
        return tuple(pos) in self.npc_tiles(sector)

    def boss_at(self, pos, sector=None):
        sector = self.sector if sector is None else sector
        data = SECTORS[sector]
        for landmark in data.get('landmarks', []):
            bid = landmark.get('boss_site')
            if bid and self.boss_available(bid) and tuple(pos) == tuple(landmark['pos']):
                return bid
        return None

    def nearby_npc(self):
        data = self.area
        eliminated = self.missions.get('faction_conflict', {}).get('loser') if self.missions.get('faction_conflict', {}).get('status') == 'completed' else None
        candidates = []
        settlement = data.get('settlement')
        if settlement:
            candidates.extend(settlement.get('npcs', []))
        site = data.get('faction_site')
        if site and site.get('faction') != eliminated:
            candidates.extend(site.get('npcs', []))
        for npc in candidates:
            if eliminated and npc.get('faction') == eliminated:
                continue
            if distance(self.pos, npc['pos']) <= 1:
                return npc
        return None

    def knows_language(self, civilization_id):
        if civilization_id == 'avarin':
            return bool(self.language_mastered)
        if civilization_id == 'nahr_shadows':
            return bool(self.nahr_language_mastered)
        return bool(self.language_mastery.get(civilization_id, False))

    def save_loadout(self, index):
        if type(index) is not int or index not in range(3):
            return False, 'Loadout inválido.'
        if self.battle:
            return False, 'Não é possível salvar um Loadout durante o combate.'
        self.gauntlet_loadouts[index] = {'slots': list(self.slots[:3]), 'special': self.gauntlet_special_slot}
        return True, f'Loadout {index + 1} salvo.'

    def equip_loadout(self, index):
        if type(index) is not int or index not in range(3):
            return False, 'Loadout inválido.'
        if self.battle:
            return False, 'Não é possível trocar o Loadout durante o combate.'
        data = self.gauntlet_loadouts[index]
        if not isinstance(data, dict):
            return False, 'Este Loadout ainda não foi configurado.'
        slots = list(data.get('slots', []))[:3] + [None] * 3
        slots = slots[:3]
        for cid in slots:
            if cid is None: continue
            if self.is_unique_card(cid):
                if cid not in self.unique_cards: return False, 'Este Loadout contém uma Carta Única indisponível.'
            elif cid not in self.crafted:
                return False, 'Este Loadout contém uma carta indisponível na Pool.'
        special=data.get('special')
        if special is not None and special not in self.unique_cards:
            return False, 'Este Loadout contém uma Carta Única indisponível.'
        used=[cid for cid in slots if cid]
        if len(used)!=len(set(used)) or (special and special in used):
            return False, 'Este Loadout contém cartas duplicadas.'
        self.slots=slots; self.gauntlet_special_slot=special
        return True, f'Loadout {index + 1} equipado.'

    def refresh_advanced_research(self):
        was=bool(getattr(self,'helmet_advanced_research_unlocked',False))
        unlocked=bool(self.helmet_generation>=2 and len(set(self.bestiary_scanned))>=5)
        self.helmet_advanced_research_unlocked=unlocked
        if unlocked and not was:
            self.journal_add('helmet_advanced_research','Pesquisa avançada','O Elmo cruzou cinco análises completas com o protocolo Tier 2 e liberou uma leitura aprofundada do comportamento das criaturas.')
            self.achievement_alerts.append({'type':'helmet_advanced'})
            return True
        return False

    def _refresh_all_civ_missions(self):
        for civ in list(getattr(self,'civilization_missions',{}).keys()):
            self._refresh_civ_mission_completion(civ)

    def _civilization_context(self, civilization_id):
        from world import SECTORS as _SECTORS
        planet=self.current_planet_id()
        if planet=='veyra':
            ids=['landing','dunes','ruins','outskirts','waterworks','vaults','canyon','comms_ridge']
        else:
            ids=[sid for sid,data in _SECTORS.items() if sid.startswith(planet + '_') or data.get('planet')==planet]
        species=[]; items=[]
        for sid in ids:
            data=_SECTORS.get(sid,{})
            for entry in data.get('spawns',[]):
                if isinstance(entry,(tuple,list)) and entry and entry[0] in SPECIES: species.append(entry[0])
            for node in data.get('nodes',[]):
                item=node.get('item')
                if item and item not in ('Fragmento histórico','Registro cultural'): items.append(item)
        return {'planet':planet,'sectors':list(dict.fromkeys(ids)),'species':list(dict.fromkeys(species)),'items':list(dict.fromkeys(items)),'names':{sid:_SECTORS[sid].get('name',sid) for sid in ids if sid in _SECTORS}}

    def _mission_material_target(self,premium=False):
        return self.rng.randint(7,12) if not premium else self.rng.randint(12,22)

    def refresh_civilization_missions(self,civilization_id,force=False):
        if not civilization_id or not self.knows_language(civilization_id): return False
        now=int(realtime.time())
        state=self.civilization_missions.setdefault(civilization_id,{})
        generated=int(state.get('generated_at',0) or 0)
        if not force and state.get('offers') and now-generated<7200:
            self._refresh_civ_mission_completion(civilization_id)
            return False
        ctx=self._civilization_context(civilization_id)
        templates=list(CIVILIZATION_MISSION_TEMPLATES); self.rng.shuffle(templates)
        count=self.rng.randint(3,5); premium_index=self.rng.randrange(count) if self.rng.random()<0.28 else None
        offers=[]
        for i in range(count):
            tpl=templates[i%len(templates)]; premium=i==premium_index
            m={'id':f'{civilization_id}:{now}:{i}','template':tpl['id'],'kind':tpl['kind'],'premium':premium,'status':'available','generated_at':now,'params':{},'reward':{}}
            if m['kind'] in ('hunt','scan') and ctx['species']:
                sid=self.rng.choice(ctx['species']); target=self.rng.randint(2,4) if m['kind']=='hunt' else 1
                if premium: target += 2 if m['kind']=='hunt' else 0
                m['params']={'species_id':sid,'target':target}; m['description']=tpl['text'].format(target=target,species=SPECIES[sid]['name'])
            elif m['kind'] in ('collect','deliver') and ctx['items']:
                item=self.rng.choice(ctx['items']); target=self._mission_material_target(premium)
                m['params']={'item':item,'target':target}; m['description']=tpl['text'].format(target=target,item=item)
            elif m['kind']=='visit' and ctx['sectors']:
                unvisited=[sid for sid in ctx['sectors'] if sid not in self.visited]
                candidates=unvisited or ctx['sectors']
                sid=self.rng.choice(candidates); m['params']={'sector':sid,'target':1}; m['description']=tpl['text'].format(map_name=ctx['names'].get(sid,sid))
            else:
                item=ctx['items'][0] if ctx['items'] else 'Sucata'; target=self._mission_material_target(premium)
                m['kind']='collect'; m['params']={'item':item,'target':target}; m['description']=f'Colete {target} unidades de {item}.'
            if premium: m['reward']={'Essência':self.rng.randint(10,18),'item':m['params'].get('item','Sucata'),'item_amount':self.rng.randint(12,24)}; m['description']+=' PEDIDO PREMIUM.'
            else: m['reward']={'Essência':self.rng.randint(4,9),'item':m['params'].get('item','Sucata'),'item_amount':self.rng.randint(5,12)}
            offers.append(m)
        state['generated_at']=now; state['offers']=offers; state.setdefault('active',[])
        return True

    def civilization_mission_progress(self,civilization_id,mission):
        p=mission.get('params',{}); base=mission.get('baseline',{}); kind=mission.get('kind'); stats=self.statistics
        if kind=='hunt':
            sid=p.get('species_id'); return max(0,int(stats.get('kills',{}).get(sid,0))-int(base.get('kills',{}).get(sid,0)))
        if kind=='scan':
            sid=p.get('species_id'); return 1 if sid in self.bestiary_scanned and sid not in base.get('scanned',[]) else 0
        if kind=='visit': return 1 if p.get('sector') in self.visited else 0
        if kind in ('collect','deliver'):
            item=p.get('item'); return max(0,int(self.inventory.get(item,0))-int(base.get('inventory',{}).get(item,0)))
        return 0

    def _refresh_civ_mission_completion(self,civilization_id):
        state=self.civilization_missions.get(civilization_id,{})
        changed=False
        for m in state.get('active',[]):
            if m.get('status')!='active': continue
            m['progress']=self.civilization_mission_progress(civilization_id,m)
            if m['progress']>=int(m.get('params',{}).get('target',1)):
                m['status']='ready'; changed=True
                self.achievement_alerts.append({'type':'civ_mission_updated','civilization':civilization_id,'mission_id':m.get('id')})
        return changed

    def accept_civilization_mission(self,civilization_id,mission_id):
        if not self.knows_language(civilization_id): return False,'O idioma ainda não foi calibrado.'
        self.refresh_civilization_missions(civilization_id); state=self.civilization_missions.get(civilization_id,{})
        if len(state.get('active',[]))>=3: return False,'Limite de 3 pedidos ativos atingido.'
        m=next((x for x in state.get('offers',[]) if x.get('id')==mission_id),None)
        if not m or m.get('status')!='available': return False,'Pedido indisponível.'
        m['status']='active'; m['baseline']={'kills':dict(self.statistics.get('kills',{})),'inventory':dict(self.inventory),'scanned':list(self.bestiary_scanned)}; m['progress']=0
        state.setdefault('active',[]).append(m); self.achievement_alerts.append({'type':'civ_mission_started','civilization':civilization_id,'mission_id':mission_id})
        return True,'Pedido aceito.'

    def claim_civilization_mission(self,civilization_id,mission_id):
        self._refresh_civ_mission_completion(civilization_id); state=self.civilization_missions.get(civilization_id,{})
        m=next((x for x in state.get('active',[]) if x.get('id')==mission_id),None)
        if not m: return False,'Pedido não encontrado.'
        if m.get('status')!='ready': return False,'O pedido ainda não foi concluído.'
        p=m.get('params',{}); qty=int(p.get('target',0)); item=p.get('item')
        if m.get('kind')=='deliver':
            if int(self.inventory.get(item,0))<qty: return False,'Os materiais para entrega não estão disponíveis.'
            self.inventory[item]-=qty
        reward=m.get('reward',{}); ritem=reward.get('item','Sucata'); rqty=int(reward.get('item_amount',0)); ess=int(reward.get('Essência',0))
        self.inventory[ritem]=int(self.inventory.get(ritem,0))+rqty; self.inventory['Essência']=int(self.inventory.get('Essência',0))+ess
        m['status']='claimed'; state['active'].remove(m); self.statistics['missions_completed']+=1
        self.achievement_alerts.append({'type':'civ_mission_completed','civilization':civilization_id,'mission_id':mission_id})
        return True,f'Pedido concluído. Recompensa: {rqty} {ritem} e {ess} Essências.'

    def learn_language(self, civilization_id):
        if not civilization_id:
            return False, 'Civilização sem idioma identificável.'
        if civilization_id == 'avarin':
            self.language_mastered = True
            self.language_progress = max(3, int(self.language_progress))
        elif civilization_id == 'nahr_shadows':
            self.nahr_language_mastered = True
            self.nahr_language_progress = max(3, int(self.nahr_language_progress))
        else:
            self.language_mastery[civilization_id] = True
        planet_id = self.current_planet_id()
        changed = self.discover_civilization_on_planet(planet_id, civilization_id)
        data = CIVILIZATIONS.get(civilization_id, {})
        name = data.get('name', civilization_id)
        if changed:
            self.journal_add(f'language_{civilization_id}', 'Idioma calibrado', f'O Elmo calibrou padrões suficientes para reconhecer a língua {data.get("language", "desconhecida")} da civilização {name}.')
        return True, f'Idioma calibrado: {name}.'

    def interact_npc(self, npc):
        changed = False
        site = self.area.get('faction_site')
        is_site_npc = bool(site and any(n.get('id') == npc.get('id') for n in site.get('npcs', [])))
        is_veyra_faction_npc = self.current_planet_id() == 'veyra' and bool(npc.get('faction') in FACTIONS)
        if is_veyra_faction_npc and (not self.helmet_owned or self.helmet_generation < 1 or not self.knows_language('avarin')):
            return ('O Elmo ainda não consegue estabelecer comunicação com esta facção. Primeiro crie o Elmo e conclua a calibração do Avari.', False)
        self.pending_language_civilization = None
        self.pending_language_npc_id = None
        if not is_site_npc:
            settlement = self.area.get('settlement')
            if settlement:
                sid = settlement['id']
                if sid not in self.society['discovered_settlements']:
                    self.society['discovered_settlements'].append(sid)
                    changed = True
                changed |= self.set_objective('settlement', 'completed', max(1, len(self.society['discovered_settlements'])))
        if npc['id'] not in self.society['seen_npcs']:
            self.society['seen_npcs'].append(npc['id'])
            self.society['first_contact'] = True
            changed |= self.journal_add(
                f'npc_{npc["id"]}', 'Primeiro contato',
                'Você se aproxima de um dos habitantes. A figura percebe sua armadura e reage ao estranho viajante.' if self.language_mastered else
                'Você se aproxima de um dos habitantes. A figura percebe sua armadura, recua e responde em um idioma completamente desconhecido. A Manopla registra o encontro, mas ainda não consegue interpretar a fala.',
            )
        civilization_id = npc.get('civilization')
        if civilization_id not in ('avarin', 'nahr_shadows') and civilization_id and not self.knows_language(civilization_id):
            self.pending_language_civilization = civilization_id
            self.pending_language_npc_id = npc.get('id')
            civ = CIVILIZATIONS.get(civilization_id, {})
            cname = civ.get('name', 'civilização desconhecida')
            return (f'{npc["name"]} responde em {cname}. O Elmo não reconhece o idioma. Calibração necessária para estabelecer comunicação.', changed)

        is_nahr = civilization_id == 'nahr_shadows' or npc.get('faction') == 'nahr_shadows'
        if is_nahr:
            if not self.nahr_language_mastered:
                return (f'A pequena sombra paira diante de você. O Nahrim ainda é incompreensível. Função observada: {npc["role"]}.', changed)
            self.nahr_ry_contacted = True
            if self.missions.get('ry_investigation', {}).get('stage') == 'history':
                ok, lore, mission_changed = self.complete_ry_history()
                return (lore, changed or mission_changed)
            if self.bosses.get('ry', {}).get('defeated', False):
                return ('As sombras se agitam em celebração. “O mal que habitava o vazio foi destruído. Agora poderemos seguir nossas vidas em paz.”', changed)
            return ('A sombra se aproxima. “RY é o nome que damos àquilo que vive no vazio. Nós o tratamos como a personificação da morte, um bicho-papão que pode surgir para executar quem quiser.”', changed)
        if civilization_id not in ('avarin', 'nahr_shadows') and civilization_id and not self.knows_language(civilization_id):
            return (f'O habitante observa sua armadura. A língua desconhecida impede a comunicação. Função observada: {npc["role"]}.', changed)
        if npc['id'] == 'avarin_reclaimer':
            laser_mission = self.missions.get('ship_laser_project', {})
            if laser_mission.get('status') == 'active':
                changed |= self.complete_laser_project()
                return ('Mira: "A nave pode se defender das rochas com um emissor laser. O projeto é seu."\n\nPROJETO ADQUIRIDO: EMISSOR LASER', changed)
            if laser_mission.get('status') == 'completed':
                return ('Mira: "O emissor laser já é seu. Instale-o pelo computador da nave quando tiver os componentes."', changed)

        if npc['id'] == 'avarin_waterkeeper' and self.missions['water_supply']['status'] == 'available':
            changed |= self.journal_add('mission_water_offer', 'Um pedido urgente', 'Iria explica que a Estação de Captação perdeu pressão. Os Guardiões dos Reservatórios precisam de alguém capaz de entender a tecnologia antiga da estação.')
            return ('Iria: \"A estação está morrendo. Se puder trabalhar nas máquinas, Qaresh precisa de você.\"\n\nMISSÃO DISPONÍVEL: ÁGUA PARA QARESH', changed)
        if npc['id'] == 'faction_c_leader' and self.missions.get('faction_conflict', {}).get('status') == 'available':
            changed |= self.journal_add('faction_conflict_offer', 'Uma proposta da Fenda', 'Tarek, líder dos Filhos da Fenda, quer usar sua capacidade de intrusão contra os Guardiões dos Reservatórios. Ele oferece uma saída: cumprir o golpe ou virar o jogo avisando Iria.')
            return ('Tarek: \"Os Guardiões controlam os reservatórios. Hoje eles vão se mover confiando numa rede que eu posso fazê-los ignorar. Você só precisa decidir de que lado da emboscada estará.\"\n\nMISSÃO DISPONÍVEL: A DÍVIDA DA FENDA', changed)
        if npc['id'] == 'faction_c_leader' and self.missions.get('faction_conflict', {}).get('status') == 'active':
            return ('Tarek observa você em silêncio. \"Agora, vá até Iria. O próximo movimento é seu.\"', changed)
        if npc['id'] == 'avarin_waterkeeper' and self.missions.get('faction_conflict', {}).get('status') == 'active':
            changed |= self.journal_add('faction_conflict_v_leader_reached', 'Uma decisão diante de Iria', 'Você chegou até Iria. A emboscada dos Filhos da Fenda está prestes a acontecer. Você pode interferir no sistema de comunicação ou contar tudo à Guardiã-Mor.')
            return ('Iria estreita os olhos. \"Você trouxe uma notícia que parece urgente. Fale.\"\n\nDECISÃO DISPONÍVEL: HACK OU ALERTA', changed)
        if npc.get('faction') in FACTIONS:
            faction_name = FACTIONS[npc['faction']]['name']
            return (f'{npc["name"]}: contato estabelecido. Função: {npc["role"]}. Facção: {faction_name}.', changed)
        return (f'{npc["name"]}: contato estabelecido. Função: {npc["role"]}.', changed)

    def _mission_completed_alert(self, mission_id):
        # Todas as missões usam o mesmo canal de alerta visual da Manopla.
        # O título da missão é resolvido na interface para evitar duplicar
        # textos no estado salvo.
        valid_ids = set(SHIP_MISSION_DATA) | {'ship', 'explore_space', 'explore_galaxy', 'water_supply', 'water_mission', 'faction_conflict', 'kuvaar', 'kuvaar_hunt', 'respawn_tank', 'ry_investigation', 'dobra_core_install', 'alphor_path', 'broom_path', 'ship_laser_project', 'travel_repair'}
        canonical = self._canonical_mission_id(mission_id)
        if mission_id in valid_ids and not any(a.get('type') == 'mission' and self._canonical_mission_id(a.get('mid')) == canonical for a in self.achievement_alerts if isinstance(a, dict)):
            self.achievement_alerts.append({'type': 'mission', 'mid': canonical})

    def ship_mission_status(self, mission_id):
        return self.missions.get(mission_id, {}).get('status', 'locked')

    def ensure_laser_project_mission(self):
        mission = self.missions.setdefault('ship_laser_project', {'status':'locked','progress':0,'reward_claimed':False})
        if self.ship_laser_project_unlocked:
            if mission.get('status') != 'completed':
                mission['status'] = 'completed'; mission['progress'] = 1; mission['reward_claimed'] = True
            return False
        if mission.get('status') == 'completed':
            self.ship_laser_project_unlocked = True
            return False
        gate_ok = bool(self.knows_language('avarin')) and int(self.renown_by_faction.get('scavengers', 0)) >= 25
        if gate_ok and mission.get('status') == 'locked':
            mission['status'] = 'active'
            mission['progress'] = 0
            changed = self.set_objective('laser_project', 'active', 0)
            changed |= self.journal_add('laser_project_unlock', 'Projeto: Emissor Laser', 'Os Recuperadores de Qaresh agora confiam em você. Mira, nas Oficinas de Sifra, pode entregar um projeto de defesa para a nave.')
            self.mission_started_alert('ship_laser_project')
            return changed
        return False

    def complete_laser_project(self):
        mission = self.missions.setdefault('ship_laser_project', {'status':'locked','progress':0,'reward_claimed':False})
        if mission.get('status') != 'active':
            return False
        mission['status'] = 'completed'
        mission['progress'] = 1
        mission['reward_claimed'] = True
        self.ship_laser_project_unlocked = True
        self.statistics['missions_completed'] = int(self.statistics.get('missions_completed', 0)) + 1
        changed = self.set_objective('laser_project', 'completed', 1)
        changed |= self.journal_add('laser_project_received', 'Emissor Laser', 'O projeto de um emissor laser portátil para a nave foi adicionado aos Projetos Tecnológicos. A instalação exige componentes avançados e deve ser feita pelo Computador da Nave.')
        self._mission_completed_alert('ship_laser_project')
        return changed

    def ensure_travel_repair_mission(self):
        mission = self.missions.setdefault('travel_repair', {'status':'locked','progress':0,'required':0,'reward_claimed':False})
        damage = max(0, min(6, int(getattr(self, 'travel_damage', 0) or 0)))
        if damage <= 0:
            if mission.get('status') == 'active':
                mission['status'] = 'completed'
                mission['progress'] = 0
                mission['required'] = 0
            return False
        changed = False
        if mission.get('status') != 'active' or int(mission.get('required', 0) or 0) != damage:
            mission['status'] = 'active'
            mission['progress'] = 0
            mission['required'] = damage
            mission['reward_claimed'] = False
            changed |= self.set_objective('travel_repair', 'active', 0)
            changed |= self.journal_add('travel_damage', 'Dano de viagem', f'A nave sofreu {damage} ponto(s) de dano estrutural durante a travessia. Reparo necessário: {damage} Sucata.')
            self.mission_started_alert('travel_repair')
        return changed

    def repair_travel_damage(self):
        damage = max(0, min(6, int(getattr(self, 'travel_damage', 0) or 0)))
        if damage <= 0:
            return False, 'A nave não possui danos de viagem.'
        if int(self.inventory.get('Sucata', 0)) < damage:
            return False, f'Faltam {damage - int(self.inventory.get("Sucata", 0))} Sucata.'
        self.inventory['Sucata'] -= damage
        self.travel_damage = 0
        mission = self.missions.setdefault('travel_repair', {'status':'active','progress':0,'required':damage,'reward_claimed':False})
        mission['status'] = 'completed'
        mission['progress'] = damage
        mission['required'] = damage
        mission['reward_claimed'] = True
        self.statistics['missions_completed'] = int(self.statistics.get('missions_completed', 0)) + 1
        self.set_objective('travel_repair', 'completed', damage)
        self._mission_completed_alert('travel_repair')
        self.journal_add('travel_repaired', 'Nave reparada', f'Os danos estruturais da última viagem foram reparados com {damage} Sucata. A nave está novamente liberada para decolagem.')
        return True, f'Nave reparada. {damage} Sucata utilizada.'

    def should_trigger_asteroid_encounter(self, target_planet_id):
        if not self.ship_laser_installed:
            return False
        current = self.current_planet_id()
        origin_route = next((r for r in STELLAR_ROUTES if r.get('id') == current), None)
        target_route = next((r for r in STELLAR_ROUTES if r.get('id') == target_planet_id), None)
        if not origin_route or not target_route or origin_route.get('galaxy') == target_route.get('galaxy'):
            return False
        return self.rng.random() < 0.30

    def resolve_asteroid_encounter(self, destroyed=0, damage=0):
        destroyed = max(0, int(destroyed))
        damage = max(0, min(6, int(damage)))
        self.statistics['asteroid_encounters'] = int(self.statistics.get('asteroid_encounters', 0)) + 1
        self.statistics['asteroids_destroyed'] = int(self.statistics.get('asteroids_destroyed', 0)) + destroyed
        if destroyed:
            self.inventory['Essência'] = int(self.inventory.get('Essência', 0)) + destroyed
        if damage:
            self.travel_damage = max(0, min(6, int(self.travel_damage) + damage))
            self.ensure_travel_repair_mission()
        self.journal_add(f'asteroid_encounter_{int(self.time*1000)}', 'Travessia perigosa', f'{destroyed} asteroide(s) destruído(s). Dano sofrido: {damage}.')
        return {'destroyed': destroyed, 'damage': damage}

    def ship_flight_ready(self):
        return all(int(self.ship_systems.get(sid, 0)) >= 100 for sid in SHIP_DIAGNOSTIC_ORDER)

    def exploration_mission_title(self):
        """Título da missão de exploração conforme o catálogo de galáxias atual."""
        mission = self.missions.get('explore_galaxy', {})
        return 'Explore o Universo' if mission.get('status') == 'active' and len(GALAXIES) > 1 else 'Explore a Galáxia'

    def ensure_exploration_mission(self):
        """Libera a missão principal assim que todos os seis sistemas ficam operacionais."""
        mission = self.missions.setdefault('explore_galaxy', {'status': 'locked', 'progress': 0, 'galaxies': []})
        changed = False
        if self.ship_flight_ready() and mission.get('status') == 'locked':
            # A cartografia estelar pode listar as rotas conhecidas de todas as
            # galáxias; a instalação do Núcleo de Dobra continua sendo a trava
            # real para a viagem física a Vharos/Meridion.
            for route in STELLAR_ROUTES:
                self.discover_planet(route['id'])
            mission['status'] = 'active'
            mission.setdefault('progress', 0)
            mission.setdefault('galaxies', [])
            changed |= self.set_objective('explore_space', 'active', int(mission.get('progress', 0)))
            changed |= self.journal_add(
                'explore_galaxy_unlocked',
                self.exploration_mission_title(),
                'Todos os sistemas de voo foram restaurados. A nave agora pode deixar Veyra e alcançar os outros mundos conhecidos da Galáxia Nárion.'
            )
            self.mission_started_alert('explore_galaxy')
            self.achievement_alerts.append({'type': 'flight_unlocked'})
            self._sync_galaxy_boss_missions()
        elif mission.get('status') in ('active', 'completed'):
            changed |= self.set_objective('explore_space', mission.get('status'), int(mission.get('progress', 0)))
        return changed

    def current_planet_id(self):
        for route in STELLAR_ROUTES:
            rid = route.get('id')
            if self.sector == route.get('landing_sector'):
                return rid
            if rid != 'veyra' and self.sector.startswith(rid + '_'):
                return rid
        return 'veyra'

    def can_travel_to_planet(self, planet_id):
        if int(getattr(self, 'travel_damage', 0) or 0) > 0:
            damage = int(self.travel_damage)
            return False, f'A nave está danificada. Reparo necessário: {damage} Sucata.'
        if not self.ship_flight_ready():
            return False, 'A nave ainda não está pronta para voo interestelar.'
        route = next((r for r in STELLAR_ROUTES if r.get('id') == planet_id), None)
        if not route:
            return False, 'Destino estelar desconhecido.'
        if route['id'] == self.current_planet_id():
            return False, 'A nave já está neste planeta.'
        if route['id'] not in self.known_planets:
            return False, 'O destino ainda não foi identificado pela Comunicação.'
        current_route = next((r for r in STELLAR_ROUTES if r.get('id') == self.current_planet_id()), None)
        if current_route and route.get('galaxy') != current_route.get('galaxy') and not self.dobra_core_installed:
            return False, 'O motor ainda não possui um Núcleo de Dobra instalado. Outras galáxias permanecem inacessíveis.'
        return True, route

    def arrive_at_planet(self, planet_id):
        ok, route_or_msg = self.can_travel_to_planet(planet_id)
        if not ok:
            return False, route_or_msg
        route = route_or_msg
        self.inside_ship = False
        self.selected_planet = planet_id
        self.sector = route['landing_sector']
        self.pos = [SHIP[0], SHIP[1] + 1]
        if self.sector not in self.visited:
            self.visited.append(self.sector)
        self._refresh_all_civ_missions()
        self.grace = 4
        mission = self.missions.setdefault('explore_galaxy', {'status':'active','progress':0,'galaxies':[]})
        mission.setdefault('galaxies', [])
        galaxy_id = route.get('galaxy', GALAXY_ID)
        if galaxy_id not in mission['galaxies']:
            mission['galaxies'].append(galaxy_id)
            mission['progress'] = len(mission['galaxies'])
        if self.current_planet_id() != 'veyra' or planet_id != 'veyra':
            self.has_left_veyra = True
        self.selected_galaxy_id = galaxy_id
        self.ensure_ry_investigation_mission()
        self._sync_galaxy_boss_missions(emit_alert=True)
        self.refresh_journal()
        return True, f'Pouso confirmado em {route["name"]}. A nave permanece no ponto padrão de chegada.'

    def start_ship_mission(self, mission_id):
        data = SHIP_MISSION_DATA.get(mission_id)
        if not data:
            return False, 'Missão de nave desconhecida.'
        sid = data['system']
        if int(self.ship_systems.get(sid, 0)) >= 100:
            return False, 'Este sistema já está operacional.'
        mission = self.missions.setdefault(mission_id, {'status':'available','progress':0})
        if mission.get('status') == 'active':
            return True, f'Missão em andamento: {data["title"]}.'
        mission['status'] = 'active'
        mission.setdefault('progress', 0)
        if mission_id == 'ship_power':
            mission['values'] = list(mission.get('values', [20,30,25,25]))[:4]
        elif mission_id == 'ship_propulsion':
            mission.setdefault('sequence', ['up','right','down','left'])
            mission.setdefault('cursor', 0)
        elif mission_id == 'ship_ftl':
            mission.setdefault('cursor', 0)
        self.journal_add(mission_id, data['title'], data['objective'])
        self.mission_started_alert(mission_id)
        return True, f'Missão iniciada: {data["title"]}.'

    def complete_ship_mission(self, mission_id):
        data = SHIP_MISSION_DATA.get(mission_id)
        if not data:
            return False, 'Missão desconhecida.'
        mission = self.missions.get(mission_id)
        if not mission or mission.get('status') != 'active':
            return False, 'A missão não está ativa.'
        sid = data['system']
        self.ship_systems[sid] = 100
        mission['status'] = 'completed'
        mission['progress'] = 1
        self.statistics['missions_completed'] += 1
        self.journal_add(f'{mission_id}_complete', f'{data["title"]} concluída', f'{data["title"]} concluída. O sistema {SHIP_SYSTEMS[sid]["name"]} voltou a 100%.')
        self._mission_completed_alert(mission_id)
        if self.ship_flight_ready():
            self.ensure_exploration_mission()
            self.ensure_ry_investigation_mission()
        return True, f'{data["title"]} concluída. {SHIP_SYSTEMS[sid]["name"]}: 100%.'

    def navigation_repair(self):
        mission = self.missions.get('ship_navigation', {})
        if mission.get('status') != 'active':
            return False, 'A interação de reparo do cockpit só existe durante a missão de navegação.'
        cost = 80
        if self.inventory.get('Sucata', 0) < cost:
            return False, 'A Manopla exige 80 unidades de Sucata para reconstruir a referência estelar.'
        self.inventory['Sucata'] -= cost
        return self.complete_ship_mission('ship_navigation')

    def communication_guards_defeated(self):
        enemies = self.worlds.get('comms_ridge', [])
        return sum(1 for e in enemies if e.get('mission_id') == 'ship_comms' and e.get('dead'))

    def communication_repair(self):
        mission = self.missions.get('ship_comms', {})
        if mission.get('status') != 'active':
            return False, 'A antena só pode ser configurada durante a missão de Comunicação.'
        if self.communication_guards_defeated() < 4:
            return False, f'A antena permanece protegida. Sentinelas eliminadas: {self.communication_guards_defeated()}/4.'
        ok, msg = self.complete_ship_mission('ship_comms')
        if ok:
            mission['progress'] = 4
        return ok, msg

    def reveal_communications(self):
        if self.ship_systems.get('comms', 0) < 100:
            return False
        changed = False
        for route in STELLAR_ROUTES:
            if route.get('galaxy', GALAXY_ID) != GALAXY_ID and not self.dobra_core_installed:
                continue
            changed |= self.discover_planet(route['id'])
        self.communication_revealed = True
        if changed:
            self.journal_add('communications_planet_names', 'Nomes no espectro estelar', 'A rede restaurada trouxe referências de todos os planetas catalogados nesta galáxia.')
        return changed

    def mission_site(self):
        landmark = self.nearby_landmark()
        if landmark and landmark.get('mission_site'):
            return landmark['mission_site']
        return None

    def nearby_hack_site(self):
        for landmark in self.nearby_landmarks(1):
            if landmark.get('hack_site'):
                return landmark
        return None

    def nearby_faction_hack_site(self):
        for landmark in self.nearby_landmarks(2):
            if landmark.get('faction_hack'):
                return landmark
        return None

    def accept_mission(self, mission_id):
        mission = self.missions.get(mission_id)
        if not mission or mission['status'] != 'available' or not self.language_mastered:
            return False, 'A missão ainda não está disponível.'
        mission['status'] = 'active'
        self.journal_add('mission_water_start', 'Água para Qaresh', 'Iria confia a você o problema da estação de captação. Os Avarin precisam de ajuda para restaurar a pressão da rede.')
        self.set_objective('water_mission', 'active', 1)
        self.mission_started_alert('water_supply')
        return True, 'Missão aceita: descubra a causa da queda de pressão na estação de captação.'

    def accept_faction_conflict(self):
        mission = self.missions.get('faction_conflict')
        if not mission or mission.get('status') != 'available' or not self.language_mastered:
            return False, 'A proposta dos Filhos da Fenda ainda não está disponível.'
        mission['status'] = 'active'; mission['path'] = None
        self.set_objective('faction_conflict', 'active', 1)
        self.journal_add('faction_conflict_start', 'A Dívida da Fenda', 'Tarek oferece a você a chance de alterar o equilíbrio entre os Guardiões dos Reservatórios e os Filhos da Fenda. Para executar o golpe, você deverá alcançar Iria e invadir a rede de comunicação. A alternativa é avisar Iria antes da emboscada.')
        self.mission_started_alert('faction_conflict')
        return True, 'Missão aceita: encontre Iria, líder dos Guardiões dos Reservatórios.'

    def resolve_faction_conflict(self, path):
        mission = self.missions.get('faction_conflict')
        if not mission or mission.get('status') != 'active':
            return False, 'O conflito entre as facções não está ativo.'
        if path not in ('sabotage', 'warn'):
            return False, 'Decisão inválida.'
        if path == 'sabotage':
            winner, loser = 'rift_children', 'waterkeepers'
            winner_card, loser_card = 'rift_break', 'lithic_sentence'
            text = 'A Manopla injeta uma rota falsa no sistema. A comunicação dos Guardiões é comprometida e a comitiva cai na emboscada. Os Filhos da Fenda vencem o confronto.'
        else:
            winner, loser = 'waterkeepers', 'rift_children'
            winner_card, loser_card = 'lithic_sentence', 'rift_break'
            text = 'Você alerta Iria. Os Guardiões reorganizam suas posições antes da movimentação. A emboscada se transforma numa armadilha contra os Filhos da Fenda, que são derrotados.'
        mission.update(status='completed', path=path, winner=winner, loser=loser, winner_card=winner_card, loser_card=loser_card, reward_claimed=True)
        # A carta do líder derrotado entra na coleção imediatamente, sempre em versão normal.
        base_id = loser_card
        serial = self._next_card_serial(base_id)
        instance_id = f'{base_id}|normal|{serial}'
        self.crafted.append(instance_id)
        # O desfecho torna os dois registros de líderes conhecidos. A carta derrotada
        # entra na coleção; a vencedora permanece como receita futura de craft.
        self.discover(loser_card)
        self.discover(winner_card)
        self.statistics['missions_completed'] += 1
        self.set_objective('faction_conflict', 'completed', 1)
        self.award_renown(winner, 20, f'A Dívida da Fenda concluída em favor de {FACTIONS[winner]["name"]}.')
        self.journal_add(f'faction_conflict_{path}', 'O destino de duas facções', text)
        self.achievement_alerts.append({'type':'mission','mid':'faction_conflict'})
        self.journal_add('faction_conflict_card', 'Carta obtida', f'A queda de {FACTIONS[loser]["name"]} deixou um registro singular: {CARDS[loser_card]["name"]}. A carta do vencedor pode ser fabricada quando os materiais necessários forem reunidos.')
        self.refresh_achievements()
        return True, f'{text} Carta recebida: {CARDS[loser_card]["name"]}.'

    def mission_choices(self, mission_id):
        if mission_id == 'water_supply' and self.missions['water_supply']['status'] == 'active':
            return [('repair', 'RESTAURAR MANUALMENTE', 'Use seus conhecimentos técnicos e entregue o serviço pedido.'),
                    ('force', 'TOMAR À FORÇA', 'Enfrente a guarda do complexo e tome a recompensa sem acordo.'),
                    ('hack', 'INFILTRAR PELA MANOPLA', 'Hackeie o terminal e obtenha a recompensa sem ferir ninguém.') ]
        return []

    def complete_mission(self, mission_id, path):
        mission = self.missions.get(mission_id)
        if not mission or mission['status'] not in ('active', 'resolving'):
            return False, {}, 'Missão indisponível.'
        requirements = {'repair': {'Sucata': 8, 'Placa': 2}} if mission_id == 'water_supply' else {}
        if any(self.inventory.get(name, 0) < qty for name, qty in requirements.get(path, {}).items()):
            req = ' | '.join(f'{name} ×{qty}' for name, qty in requirements.get(path, {}).items())
            return False, {}, 'Faltam materiais para a restauração manual: ' + req
        for name, qty in requirements.get(path, {}).items():
            self.inventory[name] -= qty
        reward = MISSION_REWARDS.get(mission_id, {}).get(path, {})
        for name, qty in reward.items():
            self.inventory[name] = self.inventory.get(name, 0) + qty
        mission['status'] = 'completed'; mission['path'] = path; mission['reward_claimed'] = True
        self.statistics['missions_completed'] += 1
        self.statistics['mission_paths'][path] = self.statistics['mission_paths'].get(path, 0) + 1
        self.set_objective('water_mission', 'completed', 1)
        self.award_renown('waterkeepers', 15, 'Missão Água para Qaresh concluída em favor dos Guardiões dos Reservatórios.')
        self.missions['kuvaar_hunt']['status'] = 'available'
        self.missions['kuvaar_hunt']['stage'] = 1
        self.set_objective('kuvaar', 'active', 0)
        self.journal_add(f'mission_water_{path}', 'Escolha em Qaresh', {'repair':'O abastecimento foi restaurado conforme o pedido dos Guardiões dos Reservatórios.', 'force':'A recompensa foi tomada depois de resistir à guarda do complexo.', 'hack':'A recompensa foi obtida por uma intrusão da Manopla. Nenhum habitante foi ferido.'}[path])
        self.journal_add('kuvaar_hunt_unlock', 'A sede não terminou', 'Os reservatórios estabilizam por pouco tempo. Os Avarin relatam que uma criatura gigantesca continua drenando o lençol freático na bacia ao redor de Qaresh.')
        self._mission_completed_alert('water_supply')
        self.refresh_achievements()
        return True, reward, 'Missão concluída.'

    def accept_boss_mission(self):
        mission = self.missions.get('kuvaar_hunt')
        if not mission or mission['status'] != 'available' or not self.language_mastered:
            return False, 'A investigação de Kuvaar ainda não está disponível.'
        mission['status'] = 'tracking'; mission['stage'] = 1
        self.mission_started_alert('kuvaar_hunt')
        self.journal_add('kuvaar_hunt_start', 'A Sede de Qaresh', 'Iria pede que você investigue a bacia seca. Alguns rastros são falsos; procure o sal cristalizado deixado pela criatura.')
        return True, 'Missão iniciada: siga os rastros de sal através dos setores de Veyra.'

    def inspect_boss_trace(self, landmark):
        mission = self.missions.get('kuvaar_hunt')
        if not mission or mission['status'] not in ('tracking', 'water'):
            return False, 'Nenhum rastro ativo foi solicitado.', False
        if not landmark.get('boss_trace'):
            return False, landmark.get('text', 'Nenhum dado relevante.'), False
        sid = landmark['id']
        if sid in self.journal['seen']:
            return False, 'Este rastro já foi analisado.', False
        self.journal['seen'].append(sid)
        if landmark['boss_trace'] == 'false':
            mission['tracking_errors'] += 1
            self.time += 20
            self.grace = 0
            if self.inventory.get('Sucata', 0) > 0:
                self.inventory['Sucata'] -= 1
            return False, 'Rastro falso. A trilha não corresponde a Kuvaar. Você perdeu tempo, consumiu recursos de campo e atraiu fauna próxima.', True
        true_ids = ('kuvaar_trace_dunes_true', 'kuvaar_trace_outskirts_true', 'kuvaar_trace_canyon_true')
        found = sum(1 for x in self.journal['seen'] if x in true_ids)
        mission['stage'] = found
        self.set_objective('kuvaar', 'active', found)
        if found >= 3:
            mission['status'] = 'water'; mission['stage'] = 3
            self.journal_add('kuvaar_trace_complete', 'A bacia seca', 'Os três rastros verdadeiros convergem para uma depressão colossal. Antes de entrar, você precisará de Água Pura para dissolver a couraça de sal da criatura.')
            return True, 'Rastro confirmado. As pistas convergem para a Bacia Seca de Kuvaar. Prepare Água Pura.', True
        return True, f'Rastro verdadeiro confirmado. Evidências: {found}/3.', True

    def kuvaar_water_options(self):
        mission = self.missions.get('kuvaar_hunt')
        if not mission or mission['status'] != 'water':
            return []
        return [
            ('borrow', 'PEDIR ÁGUA AOS AVARIN', 'Receba uma reserva de 5 Água Pura. Custa 5 pontos de Renome.'),
            ('produce', 'PRODUZIR ÁGUA PURA', 'Construa o Purificador uma vez e depois use Água Bruta + Filamento + Cristal de sintonia para produzir 5 unidades.'),
            ('divert', 'DESVIAR DO RESERVATÓRIO', 'Tome 5 Água Pura sem autorização. Gera um incidente e reduz o Renome.'),
        ]

    def prepare_kuvaar_water(self, path):
        mission = self.missions.get('kuvaar_hunt')
        if not mission or mission['status'] != 'water':
            return False, 'A etapa de preparação da água ainda não está disponível.'
        if path == 'borrow':
            if self.renown < 5:
                return False, 'Você não possui Renome suficiente para pedir esta reserva.'
            self.change_renown(-5, 'Pediu Água Pura emprestada aos Avarin para caçar Kuvaar.')
            self.inventory['Água Pura'] = self.inventory.get('Água Pura', 0) + 5
            mission['water_source'] = 'borrow'; mission['status'] = 'boss_ready'
            return True, 'Cinco unidades de Água Pura foram confiadas a você. A bacia está pronta para ser investigada.'
        if path == 'produce':
            if not self.water_purifier_built:
                return False, 'Construa primeiro o Purificador improvisado na nave.'
            raw = OTHER_RECIPES['pure_water']['recipe']
            if any(self.inventory.get(i, 0) < q for i,q in raw.items()):
                return False, 'Faltam materiais ou Água Bruta para purificar a reserva.'
            for i,q in raw.items(): self.inventory[i] -= q
            self.inventory['Água Pura'] = self.inventory.get('Água Pura', 0) + 5
            mission['water_source'] = 'produce'; mission['status'] = 'boss_ready'
            return True, 'Você produziu Água Pura com seus próprios recursos. A bacia está pronta.'
        if path == 'divert':
            if self.sector != 'waterworks' or not any(l.get('id') == 'kuvaar_diversion' and distance(self.pos,l['pos']) <= 1 for l in self.area.get('landmarks', [])):
                return False, 'A Manopla indica um ponto de desvio nos reservatórios. Vá à estação de captação.'
            self.inventory['Água Pura'] = self.inventory.get('Água Pura', 0) + 5
            mission['water_source'] = 'divert'; mission['status'] = 'boss_ready'
            self.change_renown(-12, 'Desviou Água Pura de um reservatório sem autorização.')
            self.renown_events.append({'delta': 0, 'reason': 'Incidente: desvio não autorizado de água', 'time': round(self.time, 2)})
            self.journal_add('kuvaar_water_diverted', 'Água desviada', 'Você tomou água de um reservatório Avarin sem autorização. Nenhum habitante foi ferido, mas o incidente ficou registrado.')
            return True, 'Reserva desviada. A Manopla registra o incidente. Você já pode seguir para a Bacia Seca.'
        return False, 'Opção inválida.'

    def fail_mission(self, mission_id, reason='Missão fracassada.'):
        mission = self.missions.get(mission_id)
        if not mission or mission.get('status') not in ('active', 'resolving'):
            return False, reason
        mission['status'] = 'failed'
        mission['path'] = None
        mission['reward_claimed'] = False
        self.statistics['missions_failed'] += 1
        objective_id = {'water_supply':'water_mission', 'faction_conflict':'faction_conflict'}.get(mission_id)
        if objective_id:
            self.set_objective(objective_id, 'active' if mission_id == 'water_supply' else 'active', 0)
        self.journal_add(f'mission_{mission_id}_failed_{self.statistics["missions_failed"]}', 'Missão fracassada', reason)
        self.refresh_achievements()
        return True, reason

    def start_force_mission(self):
        if self.missions['water_supply']['status'] != 'active':
            return False
        self.battle = dict(index=None, species='guard', hp=SPECIES['guard']['hp'], shield=0, weaken=0, temporary=True, mission='water_supply', boss=False, virtual=False, targets=[{'id':tid,'name':data['name'],'available':True} for tid,data in SPECIES['guard']['target_zones'].items()], target='body', mana=int(SPECIES['guard'].get('mana_max',0)), mana_max=int(SPECIES['guard'].get('mana_max',0)), enemy_attack_reduction_pct=0.0, enemy_defense_reduction_pct=0.0, enemy_precision_reduction=0, player_next_attack_crit_rate_bonus=0.0, enemy_status_turns=0, enemy_stun_turns=0, enemy_drowning_turns=0, enemy_drowning_damage=0, player_attack_reduction_pct=0.0, player_defense_reduction_pct=0.0, player_precision_reduction=0, player_stun_turns=0, player_drowning_turns=0, player_drowning_damage=0, player_status_turns=0)
        self.statistics['battles_started'] += 1
        return True

    def start_hack(self):
        if self.gauntlet_generation < 1 or self.missions['water_supply']['status'] != 'active':
            return False, 'Acesso de intrusão indisponível.'
        if self.inside_ship:
            return False, 'A intrusão deve ser iniciada a partir de um terminal alvo.'
        terminal = self.nearby_hack_site()
        if not terminal:
            return False, 'A Manopla precisa estar junto de um terminal compatível para iniciar a intrusão.'
        alert_limit = 3 + int(self.gauntlet_nexus_hack_alert_capacity_bonus)
        self.hack = {'cursor': [0, 0], 'access': [(0, 0)], 'firewall': [(1, 0), (1, 1)], 'goal': (2, 2), 'alert': 0, 'alert_limit': alert_limit, 'firewall_mask_used': False, 'turns': 0, 'active': True, 'terminal': terminal['id']}
        return True, f'Link estabelecido pela Manopla. Navegue pelos nós e alcance o núcleo sem atingir {alert_limit} alertas.'

    def start_faction_hack(self):
        mission = self.missions.get('faction_conflict')
        if not mission or mission.get('status') != 'active':
            return False, 'A missão de infiltração não está ativa.'
        if self.inside_ship:
            return False, 'A intrusão deve ser iniciada no terminal da facção alvo.'
        terminal = self.nearby_faction_hack_site()
        if not terminal:
            return False, 'A Manopla precisa estar junto ao sistema de comunicação dos Guardiões.'
        alert_limit = 3 + int(self.gauntlet_nexus_hack_alert_capacity_bonus)
        self.hack = {'cursor':[0,0], 'access':[(0,0)], 'firewall':[(1,0),(1,1)], 'goal':(2,2), 'alert':0, 'alert_limit':alert_limit, 'firewall_mask_used':False, 'turns':0, 'active':True, 'terminal':terminal['id'], 'purpose':'faction_conflict'}
        return True, f'Enlace de comunicação comprometido. Alcance o núcleo sem atingir {alert_limit} alertas.'

    def hack_move(self, dx, dy):
        if not self.hack or not self.hack.get('active'):
            return False
        x, y = self.hack['cursor']; nx, ny = x + dx, y + dy
        diagonal_allowed = bool(self.gauntlet_nexus_hack_diagonal)
        valid_step = (max(abs(dx), abs(dy)) == 1 and (dx != 0 or dy != 0)) if diagonal_allowed else (abs(dx) + abs(dy) == 1)
        if valid_step and 0 <= nx < 3 and 0 <= ny < 3:
            self.hack['cursor'] = [nx, ny]
            return True
        return False

    def hack_breach(self):
        h = self.hack
        if not h or not h.get('active'):
            return dict(ok=False, message='Nenhuma intrusão ativa.')
        current = tuple(h['cursor']); last = h['access'][-1]
        if distance(current, last) != 1 and current != (0, 0):
            return dict(ok=False, message='Nó fora do alcance do acesso atual.')
        h['turns'] += 1
        if current in h['firewall']:
            if self.gauntlet_nexus_hack_mask_first_firewall and not h.get('firewall_mask_used', False):
                h['firewall_mask_used'] = True
                return dict(ok=True, message='Firewall mascarado pelo NEXUS. O alerta permanece inalterado.')
            h['alert'] += 1
            if h['alert'] >= int(h.get('alert_limit', 3)):
                h['active'] = False; self.hack = None
                if h.get('purpose') == 'faction_conflict':
                    self.fail_mission('faction_conflict', 'O sistema de comunicação detectou a intrusão e bloqueou seu acesso. A oportunidade de interferir na emboscada foi perdida.')
                    return dict(ok=False, failed=True, message='Firewall acionado. Intrusão encerrada. A oportunidade de interferir na emboscada foi perdida.')
                self.fail_mission('water_supply', 'O firewall bloqueou a intrusão. A estação permanece inacessível e a missão foi perdida.')
                return dict(ok=False, failed=True, message='Firewall acionado. Intrusão encerrada. Missão fracassada.')
            return dict(ok=True, message=f'Firewall detectado. Alerta {h["alert"]}/{h.get("alert_limit", 3)}.')
        if current not in h['access']:
            h['access'].append(current)
        if current == h['goal']:
            h['active'] = False; self.hack = None
            if h.get('purpose') == 'faction_conflict':
                ok, msg = self.resolve_faction_conflict('sabotage')
                return dict(ok=ok, success=ok, message=(msg + ' Acesso de comunicação comprometido.') if ok else msg)
            ok, reward, msg = self.complete_mission('water_supply', 'hack')
            return dict(ok=ok, success=ok, reward=reward, message=msg + ' Acesso limpo.')
        return dict(ok=True, message='Nó comprometido. Próximo acesso disponível.')

    def collect(self):
        if self.battle:
            return 'Encerre o combate antes de coletar.'
        landmark = self.nearby_landmark()
        if landmark and landmark.get('cultural'):
            ok, msg, _ = self.analyze_culture()
            return msg
        for node in self.area['nodes']:
            if distance(self.pos, node['pos']) <= 1 and node['id'] not in self.collected_nodes:
                if node.get('category') == 'flora' and node.get('scan_required', False) and not self.scan_unlocked:
                    return 'ANÁLISE BOTÂNICA INDISPONÍVEL: a Manopla não consegue classificar este espécime vegetal nem diferenciar estruturas úteis de matéria orgânica sem protocolo de Scan.'
                amount = self.rng.randint(*node['quantity'])
                item = node['item']
                self.inventory[item] = self.inventory.get(item, 0) + amount
                self.statistics['collectibles'][item] = self.statistics['collectibles'].get(item, 0) + amount
                self.collected_nodes.append(node['id'])
                self._refresh_all_civ_missions()
                self.refresh_journal()
                if item == 'Fragmento histórico':
                    return 'Coletou um fragmento histórico. O registro foi adicionado ao diário; Tradução pendente até obter o elmo.'
                return f'Coletou {amount} {item}. Estes destroços foram esgotados definitivamente.'
        if any(distance(self.pos, n['pos']) <= 1 for n in self.area['nodes']):
            return 'Destroços já recolhidos. Materiais no chão não reaparecem.'
        for landmark in self.area['landmarks']:
            if distance(self.pos, landmark['pos']) <= 1:
                return landmark['text']
        return 'Aproxime-se de um depósito brilhante ou da nave.'

    def _combat_challenge_offers(self):
        pool=[c for c in COMBAT_CHALLENGE_CATALOG if c.get('kind') != 'vital_hit' or getattr(self, 'helmet_advanced_research_unlocked', False)]
        offers=[]
        count=min(3,len(pool))
        while len(offers)<count and pool:
            # Alguns testes históricos usam um RNG mínimo sem choice(); a seleção
            # determinística é o fallback apenas para esse tipo de RNG.
            if hasattr(self.rng, 'choice'):
                picked=self.rng.choice(pool)
            else:
                picked=pool[0]
            pool.remove(picked)
            offers.append(dict(picked))
        return offers

    def start_battle(self, index):
        e = self.enemies[index]
        if e['dead'] or self.battle:
            return False
        spec = SPECIES[e['species']]
        self.register_bestiary_encounter(e['species'])
        targets = [{'id': tid, 'name': data['name'], 'available': True} for tid, data in spec.get('target_zones', {}).items()]
        default_target = targets[0]['id'] if targets else 'body'
        self.battle = dict(index=index, species=e['species'], hp=spec['hp'], shield=0, weaken=0,
                           mana=int(spec.get('mana_max', 0)), mana_max=int(spec.get('mana_max', 0)),
                           boss=False, virtual=False, targets=targets, target=default_target,
                           enemy_attack_reduction_pct=0.0, enemy_defense_reduction_pct=0.0, enemy_precision_reduction=0, player_next_attack_crit_rate_bonus=0.0,
                           enemy_status_turns=0, enemy_stun_turns=0, enemy_drowning_turns=0, enemy_drowning_damage=0, enemy_drowning_pending=False,
                           enemy_burn_turns=0, enemy_burn_damage=0,
                           turns=0, challenge_offers=self._combat_challenge_offers(), challenge=None, kits_before=int(self.statistics.get('kits_used',0)), challenge_used_elements=[], challenge_basic_used=False, challenge_player_misses=0, challenge_critical_hits=0, challenge_different_cards=[], challenge_last_damage=0, challenge_vital_hits=0, vital_ruptured=False, vital_zone_hp=0, vital_zone_hp_max=0,
                           broom_charge=0,
                           player_attack_reduction_pct=0.0, player_defense_reduction_pct=0.0,
                           player_precision_reduction=0, player_stun_turns=0, player_drowning_turns=0, player_drowning_damage=0, player_drowning_pending=False,
                           player_burn_turns=0, player_burn_damage=0, player_status_turns=0)
        self.battle_target = 'body'
        self.statistics['battles_started'] += 1
        return True

    def _kuvaar_water_deposit_count(self):
        """Quantidade de depósitos de Água Pura disponíveis no cenário do boss.

        A preparação altera apenas a execução da luta: não modifica HP, ATQ, DEF,
        Precisão ou qualquer outro atributo do Kuvaar.
        1 = confronto direto, sem restaurar os reservatórios.
        2 = reservatórios resolvidos por força ou hack.
        3 = reservatórios efetivamente reparados.
        """
        water = self.missions.get('water_supply', {})
        if water.get('status') != 'completed':
            return 1
        return 3 if water.get('path') == 'repair' else 2

    def start_boss_battle(self, boss_id='kuvaar', virtual=False):
        boss = BOSSES.get(boss_id)
        if not boss or self.battle:
            return False, 'Boss indisponível.'
        if not virtual and not self.boss_available(boss_id):
            if boss_id == 'ry':
                return False, 'O Vazio de RY ainda não revelou a presença que habita seu centro.'
            galaxy_id = boss.get('galaxy')
            missing = [BOSSES[x]['name'] for x in GALAXY_RARE_BOSSES.get(galaxy_id, ()) if not self.bosses.get(x, {}).get('defeated', False)]
            if missing:
                return False, 'Este combate está selado. Derrote os bosses raros restantes: ' + ', '.join(missing) + '.'
            return False, 'Este combate lendário ainda não está disponível.'
        pre_hp, pre_memory = self.hp, self.memory
        if virtual:
            if not self.simulator_built:
                return False, 'O simulador ainda não foi construído.'
            if not self.bosses.get(boss_id, {}).get('defeated', False):
                return False, 'Este boss ainda não foi derrotado no confronto real.'
            if self.inventory.get('Carga de Simulação', 0) <= 0:
                return False, 'Falta uma Carga de Simulação.'
            self.inventory['Carga de Simulação'] -= 1
            self.statistics['boss_rematches'][boss_id] = self.statistics['boss_rematches'].get(boss_id, 0) + 1
            self.hp, self.memory = self.max_hp, self.max_memory

        deposit_count = 3 if virtual else (self._kuvaar_water_deposit_count() if boss_id == 'kuvaar' else 0)
        targets = []
        for tid, data in boss['target_zones'].items():
            targets.append({'id': tid, 'name': data['name'], 'available': not data.get('exposed_only', False)})
        for idx in range(1, deposit_count + 1):
            targets.append({'id': f'water_deposit_{idx}', 'name': f'Depósito de Água {idx}', 'available': True, 'water_deposit': True})
        zone_hp = {tid: int(data['hp']) for tid, data in boss.get('target_zones', {}).items() if data.get('hp_key')}
        zone_hp_max = dict(zone_hp)
        initial_target = boss.get('initial_target') or ('shell' if boss_id == 'kuvaar' else next(iter(boss['target_zones'])))
        if initial_target not in {t['id'] for t in targets}:
            initial_target = next(iter(boss['target_zones']))
        self.register_bestiary_encounter(boss_id)
        self.battle = dict(index=None, species=boss_id, hp=int(boss['hp']), shield=0, weaken=0,
                           mana=int(boss.get('mana_max', 20)), mana_max=int(boss.get('mana_max', 20)),
                           boss=True, virtual=virtual, targets=targets, target=initial_target,
                           zone_hp=zone_hp, zone_hp_max=zone_hp_max,
                           shell_layers=3 if boss_id == 'kuvaar' else 0,
                           exposed_turns=0, water_deposits_remaining=deposit_count,
                           water_deposit_total=deposit_count, used_water_deposits=[],
                           enemy_attack_reduction_pct=0.0, enemy_attack_reduction_flat=0.0,
                           enemy_defense_reduction_pct=0.0, enemy_precision_reduction=0,
                           player_next_attack_crit_rate_bonus=0.0, player_attack_bonus_flat=0.0,
                           boss_reactive_shield=0, ry_next_attack_critical=False, ry_next_attack_bonus_pct=0.0,
                           enemy_status_turns=0, enemy_stun_turns=0, enemy_drowning_turns=0, enemy_drowning_damage=0, enemy_drowning_pending=False,
                           enemy_burn_turns=0, enemy_burn_damage=0,
                           player_attack_reduction_pct=0.0, player_defense_reduction_pct=0.0,
                           player_precision_reduction=0, player_stun_turns=0, player_drowning_turns=0, player_drowning_damage=0, player_drowning_pending=False,
                           player_burn_turns=0, player_burn_damage=0, player_status_turns=0,
                           pre_hp=pre_hp, pre_memory=pre_memory)
        self.battle_target = initial_target
        self.statistics['battles_started'] += 1
        if virtual:
            return True, f'Simulação iniciada contra {boss["name"]}. Condições ideais carregadas.'
        if boss_id == 'kuvaar':
            if deposit_count == 3:
                difficulty_note = 'Os reservatórios foram reparados. Três depósitos de Água Pura estão disponíveis.'
            elif deposit_count == 2:
                difficulty_note = 'Dois depósitos de Água Pura estão disponíveis.'
            else:
                difficulty_note = 'Apenas um depósito de Água Pura está disponível.'
            return True, f'Kuvaar desce da bacia. {difficulty_note} Selecione a parte do corpo ou um depósito de água.'
        if boss_id == 'ry':
            return True, 'RY surge como uma esfera de luz disforme e translúcida. A presença não emite som. O confronto lendário começa.'
        return True, f'{boss["name"]} bloqueia a passagem. Selecione uma parte do corpo para iniciar o confronto.'

    def battle_targets(self):
        b = self.battle
        if not b:
            return []
        if b.get('boss'):
            species = b['species']
            for target in b['targets']:
                if target.get('water_deposit'):
                    used = set(b.get('used_water_deposits', []))
                    target['available'] = target['id'] not in used and b.get('water_deposits_remaining', 0) > 0
                    continue
                data = BOSSES[species]['target_zones'][target['id']]
                available = True
                if data.get('exposed_only'):
                    if species == 'kuvaar':
                        available = b.get('exposed_turns', 0) > 0 or b.get('shell_layers', 3) <= 0
                    elif species == 'fagor':
                        available = b.get('zone_hp', {}).get('leg_left', 1) <= 0 and b.get('zone_hp', {}).get('leg_right', 1) <= 0
                    elif species == 'alphor':
                        available = b.get('zone_hp', {}).get('horn_left', 1) <= 0 and b.get('zone_hp', {}).get('horn_right', 1) <= 0
                    else:
                        available = False
                if data.get('hp_key'):
                    available = available and b.get('zone_hp', {}).get(data['hp_key'], int(data.get('hp', 1))) > 0
                target['available'] = available
        return [t for t in b.get('targets', []) if t.get('available', True)]

    def target_hit_chance(self, target_id):
        """Chance de acerto por parte do corpo, baseada em Precisão e evasão da zona."""
        b = self.battle
        if not b:
            return 0
        options = {t['id'] for t in self.battle_targets()}
        if target_id not in options:
            return 0
        if b.get('boss') and target_id.startswith('water_deposit_'):
            return 100
        spec = BOSSES[b['species']] if b.get('boss') else SPECIES[b['species']]
        zone = spec.get('target_zones', {}).get(target_id, {})
        precision = max(0, int(self.player_attributes().get('precision', 10)))
        evasion = max(0, int(zone.get('evasion', 0)))
        chance = 100.0 - max(0, evasion - precision) * 2.5
        return max(35, min(100, int(round(chance))))

    def _enemy_hit_chance(self, spec):
        precision = max(0, float(spec.get('precision', 10)))
        return max(85, min(100, int(round(88.0 + precision * 0.6))))

    def set_battle_target(self, target_id):
        options = {t['id'] for t in self.battle_targets()}
        if target_id not in options:
            return False
        self.battle['target'] = target_id
        self.battle_target = target_id
        return True

    def cycle_battle_target(self, step=1):
        options = self.battle_targets()
        if not options:
            return None
        ids = [o['id'] for o in options]
        current = self.battle.get('target', ids[0])
        idx = ids.index(current) if current in ids else 0
        target = ids[(idx + step) % len(ids)]
        self.set_battle_target(target)
        return target

    @staticmethod
    def _type_multiplier(attack_type, target_type):
        """Retorna multiplicador e classificação da interação elemental."""
        if not attack_type or not target_type:
            return 1.0, 'neutral'
        if TYPE_ADVANTAGES.get(attack_type) == target_type:
            return 1.5, 'advantage'
        if TYPE_ADVANTAGES.get(target_type) == attack_type:
            return 0.75, 'disadvantage'
        return 1.0, 'neutral'

    def _player_attack_profile(self, kind, next_attack_crit_bonus=0.0):
        """Retorna a faixa da skill e os atributos efetivos do sobrevivente."""
        player = self.player_attributes()
        if kind == 'basic':
            card = {}
            base = (self.combat_stats.get('damage_min', 3), self.combat_stats.get('damage_max', 5))
        else:
            card, variant_data, _, _ = self.card_data(kind)
            base = card.get('damage', (3, 5))
        if isinstance(base, int):
            base = (base, base)
        # O bônus de dano mínimo já está agregado em player_attributes(), a partir
        # das cartas equipadas. Não o some novamente na Skill usada.
        minimum = int(base[0]) + int(player.get('min_damage_bonus', 0))
        maximum = int(base[1]) + int(card.get('max_damage_bonus', 0))
        maximum = max(minimum, maximum)
        skill_amp = float(player.get('amp', 0.0)) + float(card.get('skill_amp', 0.0))
        target_mode = card.get('target_mode', 'single') if kind != 'basic' else 'single'
        effective_crit_rate = max(0.0, min(100.0, float(player['crit_rate']) + float(next_attack_crit_bonus)))
        effective_crit_damage = float(player['crit_damage'])
        # Domínio ofensivo só entra quando a técnica de carta possui o mesmo elemento.
        if kind != 'basic':
            domain = self.domain_bonuses(card.get('type'))
            minimum += int(domain.get('min_damage', 0))
            attack_base = float(player['attack']) * (1.0 + float(domain.get('attack_pct', 0.0)) / 100.0)
            effective_crit_rate = max(0.0, min(100.0, effective_crit_rate + float(domain.get('crit_rate', 0.0))))
            effective_crit_damage += float(domain.get('crit_damage', 0.0))
            skill_amp += float(domain.get('amp', 0.0))
        else:
            attack_base = float(player['attack'])
        momentum = self.unique_card_momentum() if kind != 'basic' else None
        if momentum and card.get('type') == momentum.get('element'):
            count = self.matching_equipped_element_cards(momentum['element'])
            m_kind = momentum.get('kind')
            if m_kind == 'crit_rate':
                effective_crit_rate = max(0.0, min(100.0, effective_crit_rate + 25.0))
            elif m_kind == 'crit_damage':
                effective_crit_damage += 0.50 * count
            elif m_kind == 'amp':
                skill_amp += 5.0 * count
        return minimum, maximum, effective_crit_rate, effective_crit_damage, attack_base, player['amp'], skill_amp, target_mode

    @staticmethod
    def _formula_damage(attack_base, skill_amp, attack_skill, defense):
        # Fórmula central: [ATQ base + (ATQ base × AMP da Skill %) + ATQ da Skill] - DEF.
        value = float(attack_base) + (float(attack_base) * float(skill_amp) / 100.0) + float(attack_skill) - float(defense)
        return max(1, int(value + 0.5))

    @staticmethod
    def _critical_value(damage, multiplier):
        return max(1, int(damage * multiplier + 0.5))

    @staticmethod
    def _card_temporary_effects(card):
        """Estado temporário da carta: substitui, nunca acumula, e vive só neste combate."""
        return {
            'shield': int(card.get('shield', 0)),
            'shield_pct': max(0.0, min(100.0, float(card.get('shield_pct', 0.0)))),
            'weaken': int(card.get('weaken', 0)),
            'enemy_crit_rate_reduction': float(card.get('enemy_crit_rate_reduction', 0.0)),
            'enemy_crit_damage_reduction': float(card.get('enemy_crit_damage_reduction', 0.0)),
        }

    @staticmethod
    def _card_status_values(card):
        return {
            'attack_reduction_pct': max(0.0, float(card.get('attack_reduction_pct', 0.0))),
            'attack_reduction_chance': max(0.0, min(100.0, float(card.get('attack_reduction_chance', 0.0)))),
            # Reservado para tipos que ainda não receberam identidade de efeito.
            'defense_reduction_pct': max(0.0, float(card.get('defense_reduction_pct', 0.0))),
            'defense_reduction_chance': max(0.0, min(100.0, float(card.get('defense_reduction_chance', 0.0)))),
            'precision_reduction': max(0, int(card.get('precision_reduction', 0) or 0)),
            'precision_reduction_chance': max(0.0, min(100.0, float(card.get('precision_reduction_chance', 0.0)))),
            'stun_chance': max(0.0, min(100.0, float(card.get('stun_chance', 0.0)))),
            'drowning_chance': max(0.0, min(100.0, float(card.get('drowning_chance', 0.0)))),
            'status_duration': max(1, int(card.get('status_duration', 1) or 1)),
            'burn_chance': max(0.0, min(100.0, float(card.get('burn_chance', 0.0)))),
            'burn_damage': max(0, int(card.get('burn_damage', 0) or 0)),
            'burn_turns': max(1, int(card.get('burn_turns', 1) or 1)),
            'multi_status_chance': max(0.0, min(100.0, float(card.get('multi_status_chance', 0.0)))),
        }

    def _apply_player_card_status(self, card):
        b = self.battle
        if not b:
            return []
        vals = self._card_status_values(card)
        notes = []
        duration = vals['status_duration']
        if vals['attack_reduction_pct'] and self.rng.random() < vals['attack_reduction_chance'] / 100.0:
            b['enemy_attack_reduction_pct'] = vals['attack_reduction_pct']
            b['enemy_status_turns'] = max(b.get('enemy_status_turns', 0), duration)
            notes.append(f'ATQ inimigo -{vals["attack_reduction_pct"]:.0f}% por {duration} turnos')
        if vals['defense_reduction_pct'] and self.rng.random() < vals['defense_reduction_chance'] / 100.0:
            b['enemy_defense_reduction_pct'] = vals['defense_reduction_pct']
            b['enemy_status_turns'] = max(b.get('enemy_status_turns', 0), duration)
            notes.append(f'DEF inimigo -{vals["defense_reduction_pct"]:.0f}% por {duration} turnos')
        if vals['precision_reduction'] and self.rng.random() < vals['precision_reduction_chance'] / 100.0:
            b['enemy_precision_reduction'] = vals['precision_reduction']
            b['enemy_status_turns'] = max(b.get('enemy_status_turns', 0), duration)
            notes.append(f'PREC inimigo -{vals["precision_reduction"]} por {duration} turnos')
        if vals['stun_chance'] and self.rng.random() < vals['stun_chance'] / 100.0:
            b['enemy_stun_turns'] = max(b.get('enemy_stun_turns', 0), duration)
            notes.append(f'inimigo atordoado por {duration} turno' + ('s' if duration != 1 else ''))
        if vals['drowning_chance'] and self.rng.random() < vals['drowning_chance'] / 100.0:
            # Afogamento não causa dano. Ele dobra o custo do próximo ataque especial.
            b['enemy_drowning_pending'] = True
            notes.append('Afogamento: custo do próximo ataque especial dobrado')
        if vals['burn_chance'] and vals['burn_damage'] and self.rng.random() < vals['burn_chance'] / 100.0:
            # Queimadura não acumula: um novo efeito substitui o anterior.
            b['enemy_burn_turns'] = vals['burn_turns']
            b['enemy_burn_damage'] = vals['burn_damage']
            notes.append(f'Queimadura: {vals["burn_damage"]} de dano por {vals["burn_turns"]} turnos')
        if vals['multi_status_chance'] and self.rng.random() < vals['multi_status_chance'] / 100.0:
            status = self.rng.choice(('Atordoamento', 'Afogamento', 'Cegueira', 'Queimadura'))
            if status == 'Atordoamento':
                b['enemy_stun_turns'] = max(b.get('enemy_stun_turns', 0), duration)
            elif status == 'Afogamento':
                b['enemy_drowning_pending'] = True
            elif status == 'Cegueira':
                b['enemy_precision_reduction'] = 100
                b['enemy_status_turns'] = max(b.get('enemy_status_turns', 0), duration)
            else:
                b['enemy_burn_turns'] = duration
                b['enemy_burn_damage'] = max(1, vals['burn_damage'] or 2)
            notes.append(f'{status} por {duration} turno' + ('s' if duration != 1 else ''))
        return notes

    def _resolve_battle_defeat(self, hit=0):
        b = self.battle
        if not b:
            return
        if b.get('virtual'):
            self._end_virtual_battle()
            self.battle = None
            return
        if b.get('temporary'):
            self.fail_mission(b.get('mission', 'water_supply'), 'O confronto terminou com você fora de combate. Os defensores retomam o controle da estação.')
            self.battle = None
            return
        if b.get('index') is not None:
            e = self.enemies[b['index']]
            e['pos'] = e['home'].copy()
        self.resolve_death('Você ficou fora de combate.')

    def prepare_player_turn(self):
        b = self.battle
        if not b:
            return {'stunned': False, 'damage': 0, 'defeat': False, 'message': ''}
        damage = 0
        if int(b.get('player_burn_turns', 0) or 0) > 0 and int(b.get('player_burn_damage', 0) or 0) > 0:
            damage = int(b.get('player_burn_damage', 0))
            self.hp = max(0, self.hp - damage)
            b['player_burn_turns'] = max(0, int(b.get('player_burn_turns', 0)) - 1)
            if b['player_burn_turns'] <= 0:
                b['player_burn_damage'] = 0
        stunned = int(b.get('player_stun_turns', 0)) > 0
        if stunned:
            b['player_stun_turns'] = max(0, int(b.get('player_stun_turns', 0)) - 1)
        if damage and self.hp == 0:
            self._resolve_battle_defeat(damage)
            return {'stunned': False, 'damage': damage, 'defeat': True, 'message': f'Queimadura causou {damage} de dano.'}
        if stunned:
            msg = 'Você está atordoado e perde este turno.'
            if damage:
                msg = f'Queimadura causou {damage} de dano. ' + msg
        else:
            msg = f'Queimadura causou {damage} de dano.' if damage else ''
        return {'stunned': stunned, 'damage': damage, 'defeat': False, 'message': msg}

    def end_player_turn(self):
        b = self.battle
        if not b:
            return
        status_turns = int(b.get('player_status_turns', 0) or 0)
        if status_turns <= 1:
            b['player_attack_reduction_pct'] = 0.0
            b['player_defense_reduction_pct'] = 0.0
            b['player_precision_reduction'] = 0
        if status_turns > 0:
            b['player_status_turns'] = status_turns - 1

    def _apply_enemy_card_status(self, card):
        b = self.battle
        if not b:
            return []
        vals = self._card_status_values(card)
        notes = []
        duration = vals['status_duration']
        if vals['attack_reduction_pct'] and self.rng.random() < vals['attack_reduction_chance'] / 100.0:
            b['player_attack_reduction_pct'] = vals['attack_reduction_pct']
            b['player_status_turns'] = max(b.get('player_status_turns', 0), duration)
            notes.append(f'Seu ATQ -{vals["attack_reduction_pct"]:.0f}% por {duration} turnos')
        if vals['defense_reduction_pct'] and self.rng.random() < vals['defense_reduction_chance'] / 100.0:
            b['player_defense_reduction_pct'] = vals['defense_reduction_pct']
            b['player_status_turns'] = max(b.get('player_status_turns', 0), duration)
            notes.append(f'Sua DEF -{vals["defense_reduction_pct"]:.0f}% por {duration} turnos')
        if vals['precision_reduction'] and self.rng.random() < vals['precision_reduction_chance'] / 100.0:
            b['player_precision_reduction'] = vals['precision_reduction']
            b['player_status_turns'] = max(b.get('player_status_turns', 0), duration)
            notes.append(f'Sua PREC -{vals["precision_reduction"]} por {duration} turnos')
        if vals['stun_chance'] and self.rng.random() < vals['stun_chance'] / 100.0:
            b['player_stun_turns'] = max(b.get('player_stun_turns', 0), duration)
            notes.append(f'Você ficou atordoado por {duration} turno' + ('s' if duration != 1 else ''))
        if vals['drowning_chance'] and self.rng.random() < vals['drowning_chance'] / 100.0:
            # Afogamento não causa dano. Ele dobra o custo do próximo ataque especial.
            b['player_drowning_pending'] = True
            notes.append('Afogamento: custo do próximo ataque especial dobrado')
        if vals['burn_chance'] and vals['burn_damage'] and self.rng.random() < vals['burn_chance'] / 100.0:
            # Queimadura não acumula: um novo efeito substitui o anterior.
            b['player_burn_turns'] = vals['burn_turns']
            b['player_burn_damage'] = vals['burn_damage']
            notes.append(f'Queimadura: {vals["burn_damage"]} de dano por {vals["burn_turns"]} turnos')
        return notes

    def action(self, kind, target_id=None):
        """Resolve a ação usando faixa de dano, seleção de alvo, críticos e pontos fracos."""
        b = self.battle
        if not b:
            return dict(ok=False, message='Sem combate.')
        if kind == 'flee':
            if self.rng.random() < .70:
                virtual = b.get('virtual', False)
                self._end_virtual_battle()
                self.battle = None
                self.statistics['battles_fled'] += 1
                self.grace = 4
                return dict(ok=True, escape=True, message='Fuga bem-sucedida. Afaste-se do inimigo!')
            return dict(ok=True, message='Fuga falhou! O inimigo vai atacar.', damage=0)
        if kind == 'kit':
            if self.inventory.get('Kit', 0) <= 0:
                return dict(ok=False, message='Você não tem kits de reparo.')
            if self.hp >= MAX_HP:
                return dict(ok=False, message='Vida já está cheia.')
            self.inventory['Kit'] -= 1
            self.statistics['kits_used'] = int(self.statistics.get('kits_used',0)) + 1
            healed = min(16, self.max_hp - self.hp)
            self.hp += healed
            b['turns']=int(b.get('turns',0))+1
            return dict(ok=True, heal=healed, message=f'Kit: +{healed} de vida. O inimigo age em seguida.')
        b['turns']=int(b.get('turns',0))+1
        attack_type = None
        target_id = target_id or b.get('target') or 'body'
        if b.get('boss') and target_id.startswith('water_deposit_'):
            if target_id not in {t['id'] for t in self.battle_targets()}:
                return dict(ok=False, message='Este depósito de Água Pura já foi utilizado.')
            b['used_water_deposits'].append(target_id)
            b['water_deposits_remaining'] = max(0, b.get('water_deposits_remaining', 0) - 1)
            if b.get('shell_layers', 3) > 0:
                b['shell_layers'] -= 1
            b['exposed_turns'] = 999 if b.get('shell_layers', 3) <= 0 else 3
            b['target'] = 'shell'
            self.battle_target = 'shell'
            if b['shell_layers'] <= 0:
                message = 'O depósito se rompe. A Água Pura dissolve a última camada da Couraça de Sal. Kuvaar fica permanentemente exposto!'
            else:
                message = f'O depósito se rompe. A Água Pura dissolve uma camada da Couraça de Sal. Camadas restantes: {b["shell_layers"]}. Kuvaar fica exposto por 3 turnos.'
            return dict(ok=True, damage=0, water=True, water_deposit=True, pass_turn=True,
                        target=target_id, water_deposits_remaining=b['water_deposits_remaining'],
                        message=message)

        pending_next_attack_crit_bonus = max(0.0, float(b.get('player_next_attack_crit_rate_bonus', 0.0)))
        current_card_next_attack_crit_bonus = 0.0
        current_card_attack_crit_rate_bonus = 0.0
        current_card_attack_crit_damage_bonus = 0.0
        pending_next_type = None
        pending_next_type_damage_bonus = 0.0
        current_card = None
        legendary_note = ''
        momentum_note = ''
        momentum_active = False
        momentum_kind = None
        if kind != 'basic':
            if kind not in self.slots and kind in CARDS:
                available = self.card_instances(kind)
                if available:
                    kind = available[0]
            if kind not in self.slots:
                return dict(ok=False, message='Carta não equipada.')
            try:
                card, _, _, _ = self.card_data(kind)
            except ValueError:
                return dict(ok=False, message='Carta não equipada.')
            current_card = card
            current_card_next_attack_crit_bonus = max(0.0, float(card.get('next_attack_crit_rate_bonus', 0.0)))
            current_card_attack_crit_rate_bonus = max(0.0, float(card.get('attack_crit_rate_bonus', 0.0)))
            current_card_attack_crit_damage_bonus = max(0.0, float(card.get('attack_crit_damage_bonus', 0.0)))
            pending_next_type = b.get('player_next_attack_type')
            pending_next_type_damage_bonus = max(0.0, float(b.get('player_next_attack_type_damage_bonus', 0.0) or 0.0))
            attack_type = card.get('type')
            base_cost = int(card['cost'])
            effective_cost = base_cost * (2 if b.get('player_drowning_pending', False) else 1)
            if self.memory < effective_cost:
                return dict(ok=False, message='Memória insuficiente. Use a técnica básica.')
            b['player_drowning_pending_before_attack'] = bool(b.get('player_drowning_pending', False))
            self.memory -= effective_cost
            momentum = self.unique_card_momentum()
            if momentum and attack_type == momentum.get('element'):
                momentum_active = True
                momentum_kind = momentum.get('kind')
                if momentum_kind == 'memory':
                    self.memory = min(self.max_memory, self.memory + 1)
                    momentum_note = ' Momentum: +1 Memória.'
            if b.get('player_drowning_pending', False):
                b['player_drowning_pending'] = False
            # Habilidade passiva de carta lendária: dispara sempre que a Memória chega a 0
            # enquanto Fulgor de RY estiver equipada na Manopla.
            equipped_legendary = None
            for equipped_id in self.slots:
                if not equipped_id:
                    continue
                try:
                    equipped_card, _, _, _ = self.card_data(equipped_id)
                except ValueError:
                    continue
                if equipped_card.get('legendary_ability_id'):
                    equipped_legendary = equipped_card
                    break
            legendary_note = ''
            if self.memory == 0 and equipped_legendary and equipped_legendary.get('legendary_ability_id') == 'auxilio_iluminado':
                self.hp = max(0, self.hp - 1)
                recovered_memory = max(1, int(round(self.max_memory * 0.50)))
                self.memory = min(self.max_memory, recovered_memory)
                legendary_note = f' Auxílio Iluminado: -1 Vida, Memória restaurada para {self.memory}/{self.max_memory}.'
                if self.hp <= 0:
                    defeat = self._resolve_battle_defeat(1)
                    return dict(ok=True, damage=0, memory_cost=effective_cost, legendary_ability=True, defeat=True,
                                message='Fulgor de RY: a Memória chegou a 0.' + legendary_note + ' Você ficou fora de combate.', **(defeat or {}))
            # Efeitos amarelos permanecem nos atributos; os efeitos do ataque abaixo
            # são temporários e substituem o estado anterior, sem qualquer soma.
            b.update(self._card_temporary_effects(card))
            b['player_attack_bonus_flat'] = float(b.get('player_attack_bonus_flat', 0.0)) + float(card.get('attack_bonus_flat_temp', 0.0) or 0.0)
            if card.get('combat_precision_bonus') is not None:
                b['player_precision_bonus_flat'] = int(card.get('combat_precision_bonus', 0) or 0)
            if card.get('combat_min_damage_bonus') is not None:
                b['player_min_damage_bonus_flat'] = int(card.get('combat_min_damage_bonus', 0) or 0)
            if card.get('next_attack_type'):
                b['player_next_attack_type'] = card.get('next_attack_type')
                b['player_next_attack_type_damage_bonus'] = float(card.get('next_attack_type_damage_bonus', 0.0) or 0.0)
            else:
                b['player_next_attack_type'] = None
                b['player_next_attack_type_damage_bonus'] = 0.0
        target_id = target_id or b.get('target') or 'body'
        if target_id not in {t['id'] for t in self.battle_targets()}:
            target_id = self.battle_targets()[0]['id']
        b['target'] = target_id
        if kind == 'basic': b['challenge_basic_used'] = True
        elif current_card and current_card.get('type'):
            b.setdefault('challenge_used_elements', [])
            if current_card.get('type') not in b['challenge_used_elements']: b['challenge_used_elements'].append(current_card.get('type'))
            b.setdefault('challenge_different_cards', [])
            if kind not in b['challenge_different_cards']: b['challenge_different_cards'].append(kind)
            counts=b.setdefault('challenge_same_element_counts', {})
            counts[current_card.get('type')]=int(counts.get(current_card.get('type'),0))+1
        minimum, maximum, crit_rate, crit_damage, attack_base, amp, skill_amp, target_mode = self._player_attack_profile(kind, pending_next_attack_crit_bonus)
        hit_chance = self.target_hit_chance(target_id)
        if self.rng.random() > (hit_chance / 100.0):
            label = 'Raio de Plasma' if kind == 'basic' else self.card_name(kind)
            b['challenge_player_misses'] = int(b.get('challenge_player_misses',0)) + 1
            b['player_next_attack_crit_rate_bonus'] = current_card_next_attack_crit_bonus if current_card else 0.0
            return dict(ok=True, damage=0, miss=True, hit_chance=hit_chance, target=target_id, target_mode=target_mode,
                        crit_rate=crit_rate, next_attack_crit_rate_bonus=b['player_next_attack_crit_rate_bonus'],
                        nexus_xp_gained=0, nexus_level_ups=0, message=f'{label}: ERROU o alvo ({hit_chance}% de chance).')
        rolled_skill = self.rng.randint(minimum, maximum)
        if current_card and b.get('boss') and b.get('species') == 'kael':
            rolled_skill += max(0, int(round(self.hp * float(current_card.get('player_hp_damage_ratio', 0.0) or 0.0))))
        if b.get('boss'):
            zone = BOSSES[b['species']]['target_zones'][target_id]
            exposed = b.get('exposed_turns', 0) > 0 or b.get('shell_layers', 3) <= 0
            target_defense = int(zone['defense'])
            if target_id == 'shell':
                layers = int(b.get('shell_layers', 3))
                target_defense = {3: 30, 2: 24, 1: 17, 0: 7}.get(layers, 7)
        else:
            zone = SPECIES[b['species']].get('target_zones', {}).get(target_id, {})
            target_defense = int(zone.get('defense', SPECIES[b['species']].get('defense', 0)))
        enemy_defense_reduction = max(0.0, min(100.0, float(b.get('enemy_defense_reduction_pct', 0.0))))
        if enemy_defense_reduction:
            target_defense = max(0, int(round(target_defense * (1.0 - enemy_defense_reduction / 100.0))))
        # A parte do corpo influencia somente a chance de acerto e a DEF local.
        # O dano usa exclusivamente a fórmula central do combate.
        base_damage = self._formula_damage(attack_base, skill_amp, rolled_skill, target_defense)
        crit_rate = max(0.0, min(100.0, crit_rate + current_card_attack_crit_rate_bonus))
        crit_damage = max(1.0, crit_damage + current_card_attack_crit_damage_bonus)
        critical = self.rng.random() < (crit_rate / 100.0)
        damage = self._critical_value(base_damage, crit_damage) if critical else base_damage
        attack_spec = BOSSES[b['species']] if b.get('boss') else SPECIES[b['species']]
        target_type = attack_spec.get('type')
        type_multiplier, type_relation = self._type_multiplier(attack_type, target_type)
        if type_relation == 'advantage' and self.gauntlet_nexus_advantage_bonus_pct:
            type_multiplier = 1.5 + min(50.0, float(self.gauntlet_nexus_advantage_bonus_pct)) / 100.0
        damage = max(1, int(damage * type_multiplier + 0.5))
        if pending_next_type:
            if current_card and attack_type == pending_next_type:
                damage = max(1, int(damage * (1.0 + pending_next_type_damage_bonus / 100.0) + 0.5))
            b['player_next_attack_type'] = None
            b['player_next_attack_type_damage_bonus'] = 0.0
        affects_main_hp = True
        if b.get('boss'):
            zone_multiplier = float(zone.get('damage_multiplier', 1.0) or 1.0)
            damage = max(1, int(damage * zone_multiplier + 0.5))
            if b.get('species') == 'ry' and not (current_card and current_card.get('ignore_enemy_shield')) and int(b.get('boss_reactive_shield', 0) or 0) > 0:
                shield = int(b.get('boss_reactive_shield', 0))
                absorbed = min(shield, damage)
                b['boss_reactive_shield'] = shield - absorbed
                damage = max(0, damage - absorbed)
            hp_key = zone.get('hp_key')
            if hp_key:
                b.setdefault('zone_hp', {})[hp_key] = max(0, int(b['zone_hp'].get(hp_key, zone.get('hp', 1))) - damage)
            affects_main_hp = not (b.get('species') == 'fagor' and target_id in ('leg_left','leg_right'))
            if b.get('species') == 'alphor' and target_id in ('horn_left','horn_right'):
                affects_main_hp = False
        executed = False
        if b.get('boss') and b.get('species') == 'broom' and current_card and current_card.get('execution_threshold') is not None and target_id == BOSSES['broom'].get('vital_zone', 'body'):
            threshold = float(current_card.get('execution_threshold', 0.25))
            if b.get('hp', 0) > 0 and b.get('hp', 0) <= int(BOSSES['broom']['hp'] * threshold):
                damage = max(damage, int(b.get('hp', 0)))
                executed = True
        # Limite global por evento: o inimigo nunca pode sofrer mais de 2x seu
        # HP máximo em um único dano aplicado. O HP restante não participa do
        # limite, então golpes finais continuam podendo exceder o HP atual até o teto.
        damage_before_cap = damage
        damage = self._enemy_damage_cap(damage, b)
        damage_cap_applied = damage < damage_before_cap
        if affects_main_hp:
            b['hp'] = max(0, b['hp'] - damage)
        vital_rupture = False
        if (not b.get('boss')) and getattr(self, 'helmet_advanced_research_unlocked', False) and target_id == SPECIES[b['species']].get('vital_zone') and damage > 0 and not b.get('vital_ruptured'):
            b['challenge_vital_hits']=int(b.get('challenge_vital_hits',0))+1
            zone_hp = b.get('vital_zone_hp_max') or max(1, int(round(SPECIES[b['species']].get('hp',1)*0.18)))
            b['vital_zone_hp_max']=zone_hp; b['vital_zone_hp']=max(0,int(b.get('vital_zone_hp',zone_hp))-damage)
            if b['vital_zone_hp']<=0:
                b['vital_ruptured']=True; vital_rupture=True
                vd=SPECIES[b['species']].get('vital_rupture',{})
                if vd.get('kind')=='precision': b['enemy_precision_reduction']=max(int(b.get('enemy_precision_reduction',0)),int(vd.get('value',3)))
                else: b['enemy_attack_reduction_pct']=max(float(b.get('enemy_attack_reduction_pct',0)),float(vd.get('value',15)))
        status_notes = self._apply_player_card_status(card if kind != 'basic' else {}) if kind != 'basic' and damage > 0 else []
        if current_card and damage > 0 and float(current_card.get('shield_ratio', 0.0) or 0.0) > 0:
            b['shield'] = max(0, int(round(damage * float(current_card.get('shield_ratio', 0.0)))))
        heal = 0
        boss_heal = 0
        if kind != 'basic' and current_card and damage > 0:
            heal_ratio = max(0.0, float(current_card.get('heal_ratio', 0.0) or 0.0))
            if heal_ratio:
                heal = min(max(0, self.max_hp - self.hp), int(round(damage * heal_ratio)))
                self.hp += heal
        vampirism_heal = 0
        if damage > 0 and self.gauntlet_nexus_vampirism_pct > 0:
            vampirism_heal = min(max(0, self.max_hp - self.hp), int(round(damage * self.gauntlet_nexus_vampirism_pct / 100.0)))
            self.hp += vampirism_heal
            if vampirism_heal:
                heal += vampirism_heal
        ry_reaction_notes = []
        if b.get('boss') and b.get('species') == 'ry' and current_card and damage > 0:
            if attack_type == 'Fogo':
                b['player_burn_turns'] = int(BOSSES['ry'].get('fire_burn_turns', 3))
                b['player_burn_damage'] = int(BOSSES['ry'].get('fire_burn_damage', 4))
                ry_reaction_notes.append(f'Queimadura: {b["player_burn_damage"]} de dano por {b["player_burn_turns"]} turnos')
            elif attack_type == 'Água':
                b['player_drowning_pending'] = True
                ry_reaction_notes.append('Afogamento: custo do próximo ataque especial dobrado')
            elif attack_type == 'Terra':
                b['boss_reactive_shield'] = int(b.get('boss_reactive_shield', 0)) + int(BOSSES['ry'].get('earth_shield_amount', 160))
                ry_reaction_notes.append(f'Escudo de RY: +{int(BOSSES["ry"].get("earth_shield_amount",160))} de absorção')
            elif attack_type == 'Metal':
                b['ry_next_attack_critical'] = True
                ry_reaction_notes.append('Próximo ataque de RY será CRÍTICO')
            elif attack_type == 'Planta':
                boss_heal = min(BOSSES['ry']['hp'] - b.get('hp', 0), max(1, int(round(damage * float(BOSSES['ry'].get('plant_heal_ratio', 0.20))))))
                if boss_heal:
                    b['hp'] += boss_heal
                    ry_reaction_notes.append(f'RY recuperou {boss_heal} HP')
            elif attack_type == 'Elétrico':
                b['ry_next_attack_bonus_pct'] = 50.0
                ry_reaction_notes.append('Próximo ataque de RY: +50% ATQ')
        if b.get('boss') and b.get('species') == 'kael' and target_id == 'crown':
            # O dano na copa não reduz o HP principal; apenas a sua barra própria.
            pass
        if b.get('boss') and b.get('species') == 'ounull' and kind != 'basic' and current_card and b.get('hp', 0) > 0:
            if damage > 0:
                recovering_ratio = float(BOSSES['ounull'].get('memory_attack_heal_ratio', 0.10))
                recovering_ratio *= 2.0 if b.get('player_drowning_pending_before_attack', False) else 1.0
                missing_hp = max(0, BOSSES['ounull']['hp'] - b['hp'])
                recovered = max(1, int(round(damage * recovering_ratio))) if missing_hp > 0 else 0
                boss_heal = min(missing_hp, recovered)
                b['hp'] = min(BOSSES['ounull']['hp'], b['hp'] + boss_heal)
        # A redução de ATQ de Trembe é calculada pelo HP do jogador no momento do uso.
        kael_ratio = float(current_card.get('player_hp_enemy_attack_reduction', 0.0) or 0.0) if current_card else 0.0
        if current_card and kael_ratio and b.get('boss') and b.get('species') == 'kael':
            b['enemy_attack_reduction_flat'] = max(0, int(round(self.hp * kael_ratio)))
        self.statistics['max_damage_dealt'] = max(self.statistics['max_damage_dealt'], damage)
        if critical:
            self.statistics['critical_hits'] += 1
            b['challenge_critical_hits']=int(b.get('challenge_critical_hits',0))+1
        nexus_level_ups = self.gain_gauntlet_xp(damage)
        label = 'Raio de Plasma' if kind == 'basic' else self.card_name(kind)
        if type_relation == 'advantage':
            type_note = f' VANTAGEM DE {attack_type.upper()}: ×{type_multiplier:.2f}.'
        elif type_relation == 'disadvantage':
            type_note = f' RESISTÊNCIA: {target_type.upper()} reduz o dano para 75%.'
        else:
            type_note = ''
        b['player_next_attack_crit_rate_bonus'] = current_card_next_attack_crit_bonus if current_card else 0.0
        next_attack_note = (f' Próximo ataque: +{b["player_next_attack_crit_rate_bonus"]:.0f}% Taxa Crítica.' if b['player_next_attack_crit_rate_bonus'] else '')
        status_note = (' ' + ' '.join(status_notes) + '.') if status_notes else ''
        extra_note = legendary_note if 'legendary_note' in locals() else ''
        if ry_reaction_notes:
            extra_note += ' ' + ' '.join(ry_reaction_notes) + '.'
        if vital_rupture:
            vd = SPECIES[b['species']].get('vital_rupture', {})
            if vd.get('description'):
                extra_note += ' ' + vd['description']
        if heal:
            extra_note += f' Recuperação: +{heal} Vida.'
        if boss_heal:
            extra_note += f' Ounull recuperou {boss_heal} de HP.'
        if executed:
            extra_note += ' EXECUÇÃO RELÂMPAGO: o alvo atingiu a faixa crítica de 25% de Vida.'
        message = (f'{label}: CRÍTICO! {damage} de dano.' if critical else f'{label}: {damage} de dano.') + type_note + status_note + extra_note + momentum_note + next_attack_note
        return dict(ok=True, damage=damage, raw_damage=rolled_skill, damage_min=minimum, damage_max=maximum,
                    base_damage=base_damage, target_defense=target_defense, attack_base=attack_base,
                    skill_amp=skill_amp, amp=amp, crit_rate=crit_rate, crit_damage=crit_damage, critical=critical,
                    attack_type=attack_type, target_type=target_type, type_multiplier=type_multiplier, type_relation=type_relation,
                    status_notes=status_notes, target=target_id, target_mode=target_mode,
                    memory_cost=effective_cost if kind != 'basic' else 0, heal=heal, vampirism_heal=vampirism_heal, boss_heal=boss_heal,
                    damage_cap_applied=damage_cap_applied, damage_cap=self._enemy_damage_cap(10**18, b),
                    nexus_xp_gained=damage if self.gauntlet_nexus_installed else 0, nexus_level_ups=nexus_level_ups,
                    boss_reactive_shield=int(b.get('boss_reactive_shield',0) or 0),
                    executed=executed, momentum_active=momentum_active, momentum_kind=momentum_kind, vital_rupture=vital_rupture,
                    ry_reaction_notes=ry_reaction_notes, legendary_ability_note=legendary_note,
                    legendary_ability=bool(legendary_note),
                    win=b['hp'] == 0, message=message)

    def set_combat_challenge(self,index):
        b=self.battle
        if not b: return False,'Nenhum combate ativo.'
        if not self.gauntlet_nexus_installed: return False,'O NEXUS da Manopla é necessário para ativar desafios.'
        if int(b.get('turns',0)) > 0: return False,'O desafio deve ser escolhido antes da primeira ação.'
        offers=b.get('challenge_offers',[])
        if type(index) is not int or not (0<=index<len(offers)): return False,'Desafio inválido.'
        if b.get('challenge') is not None: return False,'Um desafio já foi escolhido.'
        b['challenge']=dict(offers[index]); return True,'Desafio ativado.'

    def combat_challenge_status(self):
        b=self.battle
        if not b or not b.get('challenge'): return None
        c=b['challenge']; k=c.get('kind'); progress=False
        if k=='turns_max': progress=int(b.get('turns',0))<=int(c.get('target',0))
        elif k=='no_kit': progress=int(self.statistics.get('kits_used',0))-int(b.get('kits_before',0))==0
        elif k=='no_miss': progress=int(b.get('challenge_player_misses',0))==0
        elif k=='elements': progress=len(b.get('challenge_used_elements',[]))>=int(c.get('target',2))
        elif k=='hp_pct': progress=self.hp>=self.max_hp*int(c.get('target',75))/100.0
        elif k=='memory_pct': progress=self.memory>=self.max_memory*int(c.get('target',50))/100.0
        elif k=='no_basic': progress=not b.get('challenge_basic_used',False)
        elif k=='critical_min': progress=int(b.get('challenge_critical_hits',0))>=int(c.get('target',1))
        elif k=='same_element_attacks':
            counts=b.get('challenge_same_element_counts',{})
            progress=max(counts.values(), default=0)>=int(c.get('target',3))
        elif k=='no_last_damage': progress=int(b.get('challenge_last_damage',0))==0
        elif k=='different_cards': progress=len(b.get('challenge_different_cards',[]))>=int(c.get('target',3))
        elif k=='vital_hit': progress=int(b.get('challenge_vital_hits',0))>=int(c.get('target',1))
        return progress

    def _finalize_combat_challenge(self):
        b=self.battle
        if not b or not b.get('challenge'): self.last_challenge_result=None; return
        ok=bool(self.combat_challenge_status()); c=b['challenge']
        if ok:
            reward=int(c.get('reward',0)); self.inventory['Essência']=int(self.inventory.get('Essência',0))+reward; self.statistics['combat_challenges_completed']=int(self.statistics.get('combat_challenges_completed',0))+1
            self.last_challenge_result={'success':True,'name':c.get('name','Desafio'),'reward':reward}
        else: self.last_challenge_result={'success':False,'name':c.get('name','Desafio'),'reward':0}

    def enemy_turn(self):
        b = self.battle
        spec = BOSSES[b['species']] if b.get('boss') else SPECIES[b['species']]
        player = self.player_attributes()
        effective_spec = dict(spec)
        effective_spec['precision'] = float(spec.get('precision', 10)) + float(b.get('enemy_precision_bonus', 0)) - float(b.get('enemy_precision_reduction', 0))
        attack_reduction = max(0.0, min(100.0, float(b.get('enemy_attack_reduction_pct', 0.0))))
        lo, hi = spec.get('attack', (0, 0))
        if b.get('boss'):
            bonus = int(b.get('enemy_attack_bonus', 0))
            lo, hi = int(lo) + bonus, int(hi) + bonus
            if spec.get('crown_attack_scaling'):
                crown = int(b.get('zone_hp', {}).get('crown', 0)); crown_max = max(1, int(b.get('zone_hp_max', {}).get('crown', 1)))
                ratio = max(0.0, min(1.0, crown / crown_max))
                lo = 1 + int(round((lo - 1) * ratio))
                hi = 1 + int(round((hi - 1) * ratio))
            if spec.get('type') == 'Luz' and b.get('ry_next_attack_bonus_pct', 0):
                factor = 1.0 + float(b.get('ry_next_attack_bonus_pct', 0)) / 100.0
                lo = int(round(lo * factor)); hi = int(round(hi * factor))
                b['ry_next_attack_bonus_pct'] = 0.0
        flat_reduction = max(0, int(b.get('enemy_attack_reduction_flat', 0)))
        b['enemy_attack_reduction_flat'] = 0
        lo = max(1, lo - flat_reduction)
        hi = max(1, hi - flat_reduction)
        effective_spec['attack'] = (max(1, int(round(lo * (1.0 - attack_reduction / 100.0)))), max(1, int(round(hi * (1.0 - attack_reduction / 100.0)))))
        if effective_spec['attack'][1] < effective_spec['attack'][0]:
            effective_spec['attack'] = (effective_spec['attack'][1], effective_spec['attack'][0])
        enemy_hit_chance = self._enemy_hit_chance(effective_spec)

        # Efeitos persistentes acontecem no início do turno. Queimadura causa DoT;
        # Afogamento apenas altera o custo do próximo ataque especial.
        dot_damage = 0
        if int(b.get('enemy_burn_turns', 0) or 0) > 0 and int(b.get('enemy_burn_damage', 0) or 0) > 0:
            dot_damage = int(b.get('enemy_burn_damage', 0))
            b['hp'] = max(0, b['hp'] - dot_damage)
            b['enemy_burn_turns'] = max(0, int(b.get('enemy_burn_turns', 0)) - 1)
            if b['enemy_burn_turns'] <= 0:
                b['enemy_burn_damage'] = 0

        if b.get('enemy_stun_turns', 0) > 0:
            b['enemy_stun_turns'] = max(0, int(b.get('enemy_stun_turns', 0)) - 1)
            if b.get('enemy_status_turns', 0) > 0:
                b['enemy_status_turns'] = max(0, int(b.get('enemy_status_turns', 0)) - 1)
                if b['enemy_status_turns'] == 0:
                    b['enemy_attack_reduction_pct'] = 0.0
                    b['enemy_defense_reduction_pct'] = 0.0
                    b['enemy_precision_reduction'] = 0
            if b['hp'] <= 0:
                return dict(damage=dot_damage, damage_over_time=dot_damage, critical=False, defeat_enemy=True, special=False,
                            message=f'{spec["name"]} sucumbiu à Queimadura.')
            return dict(damage=dot_damage, damage_over_time=dot_damage, stunned=True, special=False,
                        hit_chance=enemy_hit_chance, critical=False, message=(f'{spec["name"]} está atordoado.' + (f' Queimadura causou {dot_damage} de dano.' if dot_damage else '') + ' Sua vez.'))
        if b['hp'] <= 0:
            return dict(damage=dot_damage, damage_over_time=dot_damage, critical=False, defeat_enemy=True, special=False,
                        message=f'{spec["name"]} sucumbiu à Queimadura.')

        # Toda criatura possui exatamente dois ataques: o básico e a técnica da própria carta.
        card = CARDS.get(spec.get('special_attack_card'))
        base_special_cost = int(spec.get('mana_cost', 0) or 0)
        drowning_pending = bool(b.get('enemy_drowning_pending', False))
        special_cost = base_special_cost * (2 if drowning_pending else 1)
        mana_before = int(b.get('mana', spec.get('mana_max', 0)) or 0)
        guaranteed_broom = bool(b.get('boss') and b.get('species') == 'broom' and b.get('broom_charge', 0) >= 2)
        use_special = bool(card and special_cost > 0 and mana_before >= special_cost and
                           (guaranteed_broom or self.rng.random() < float(spec.get('special_chance', 0.0)) / 100.0))
        if b.get('boss') and card is not None and special_cost <= 0:
            use_special = False
        if b.get('species') == 'broom':
            b['broom_charge'] = 0 if use_special else min(2, int(b.get('broom_charge', 0)) + 1)
        if use_special:
            b['mana'] = max(0, mana_before - special_cost)
            if drowning_pending:
                b['enemy_drowning_pending'] = False
            attack_base = self.rng.randint(*effective_spec['attack'])
            skill_attack = self.rng.randint(*card.get('damage', spec.get('special_attack', (0, 0))))
            skill_amp = float(card.get('skill_amp', 0.0))
            special_name = card.get('name', spec.get('special_attack_name', 'Ataque especial'))
            attack_type = card.get('type')
        else:
            attack_base = self.rng.randint(*effective_spec['attack'])
            skill_attack = self.rng.randint(*spec.get('skill_attack', (0, 0)))
            skill_amp = float(spec.get('skill_amp', 0.0))
            special_name = spec.get('name', 'Ataque básico')
            # Todo ataque da criatura pertence ao elemento da própria criatura.
            # O Raio de Plasma continua sem tipo, mas ataques inimigos básicos
            # também ativam a defesa do Domínio correspondente.
            attack_type = spec.get('type')

        if self.rng.random() > (enemy_hit_chance / 100.0):
            b['shield'] = b['shield_pct'] = b['weaken'] = 0
            b['enemy_crit_rate_reduction'] = 0.0
            b['enemy_crit_damage_reduction'] = 0.0
            if b.get('boss') and b.get('exposed_turns', 0) < 999:
                b['exposed_turns'] = max(0, b.get('exposed_turns', 0) - 1)
            status_turns = int(b.get('enemy_status_turns', 0) or 0)
            if status_turns > 0:
                b['enemy_status_turns'] = status_turns - 1
                if b['enemy_status_turns'] == 0:
                    b['enemy_attack_reduction_pct'] = 0.0
                    b['enemy_defense_reduction_pct'] = 0.0
                    b['enemy_precision_reduction'] = 0
            return dict(damage=dot_damage, damage_over_time=dot_damage, miss=True, special=use_special,
                        special_card=spec.get('special_attack_card') if use_special else None, attack_type=attack_type, target_type=spec.get('type'), mana=b.get('mana',0),
                        mana_cost=special_cost if use_special else 0, hit_chance=enemy_hit_chance, critical=False,
                        message=f'{special_name} errou o ataque ({enemy_hit_chance}% de chance). Sua vez.')

        fatal = bool((not b.get('virtual')) and use_special and (spec.get('fatal_attack', False) or (card.get('fatal_attack', False) if card else False)))
        if fatal:
            if self.stasis_shield_available():
                threat_window = spec.get('fatal_window', None) or (card.get('fatal_window', None) if card else None)
                if threat_window is None:
                    threat_window = 5.0 if int(spec.get('threat_level', 1)) >= 4 else 10.0
                expected_key = str(spec.get('fatal_key', 'F')).upper()
                b['stasis_pending'] = {'name': special_name, 'seconds': float(threat_window), 'key': expected_key, 'timing_window': (0.42, 0.58)}
                return dict(damage=0, raw_damage=0, attack_base=attack_base, skill_attack=skill_attack, special=use_special,
                            special_card=spec.get('special_attack_card') if use_special else None, mana=b.get('mana',0), mana_cost=special_cost if use_special else 0,
                            critical=False, crit_rate=0, crit_damage=1.5, target_defense=player['defense'], stasis_triggered=True,
                            stasis_seconds=float(threat_window), stasis_key=expected_key, message=f'{special_name}: ATAQUE FATAL DETECTADO.')
            defeat = self.resolve_death(f'{special_name} foi executado como ataque fatal.')
            return dict(damage=0, raw_damage=0, attack_base=attack_base, skill_attack=skill_attack, special=use_special,
                        special_card=spec.get('special_attack_card') if use_special else None, mana=b.get('mana',0), mana_cost=special_cost if use_special else 0,
                        critical=False, crit_rate=0, crit_damage=1.5, target_defense=player['defense'], defeat=True, **defeat,
                        message=f'{special_name}: ATAQUE FATAL. Você ficou fora de combate.')

        incoming_domain = self.domain_bonuses(attack_type)
        target_defense = int(round(float(player['defense']) * (1.0 + float(incoming_domain.get('defense_pct', 0.0)) / 100.0)))
        raw_formula = self._formula_damage(attack_base, skill_amp, skill_attack, target_defense)
        enemy_crit_rate = max(0.0, float(spec.get('crit_rate', 0.0)) - float(self.combat_stats.get('enemy_crit_rate_reduction', 0.0)) - float(b.get('enemy_crit_rate_reduction', 0.0)))
        enemy_crit_damage = max(1.0, float(spec.get('crit_damage', 1.5)) - float(self.combat_stats.get('enemy_crit_damage_reduction', 0.0)) - float(b.get('enemy_crit_damage_reduction', 0.0)))
        forced_critical = bool(b.get('boss') and b.get('species') == 'ry' and b.get('ry_next_attack_critical', False))
        b['ry_next_attack_critical'] = False
        critical = forced_critical or (self.rng.random() < (enemy_crit_rate / 100.0))
        amplified = self._critical_value(raw_formula, enemy_crit_damage) if critical else raw_formula
        domain_damage_reduced = 0
        domain_reduction = max(0.0, float(incoming_domain.get('damage_taken_pct', 0.0)))
        if domain_reduction:
            reduced = max(1, int(round(amplified * (1.0 - domain_reduction / 100.0))))
            domain_damage_reduced = max(0, amplified - reduced)
            amplified = reduced

        # Métrica pós-combate: estima quanto dano foi mitigado especificamente por
        # técnicas do jogador que reduziram o ATQ inimigo. O cálculo reconstrói
        # a base sem a redução, mantendo DEF/crítico idênticos para não misturar
        # essa métrica com o dano absorvido pelo escudo.
        technique_damage_reduced = 0
        if attack_reduction > 0.0 or flat_reduction > 0:
            reduction_factor = max(0.01, 1.0 - attack_reduction / 100.0)
            unreduced_attack_base = int(round(attack_base / reduction_factor)) + flat_reduction
            unreduced_attack_base = max(1, unreduced_attack_base)
            unreduced_raw = self._formula_damage(unreduced_attack_base, skill_amp, skill_attack, target_defense)
            unreduced_amplified = self._critical_value(unreduced_raw, enemy_crit_damage) if critical else unreduced_raw
            technique_damage_reduced = max(0, int(unreduced_amplified - amplified))

        shield_flat = int(b.get('shield', 0) or 0)
        shield_pct = max(0.0, min(100.0, float(b.get('shield_pct', 0.0) or 0.0)))
        shield_pct_absorb = int(round(amplified * shield_pct / 100.0)) if shield_pct else 0
        shield_absorbed = min(amplified, shield_flat + shield_pct_absorb)
        hit = max(0, amplified - shield_flat - shield_pct_absorb - b['weaken'])
        b['shield'] = b['shield_pct'] = b['weaken'] = 0
        b['enemy_crit_rate_reduction'] = 0.0
        b['enemy_crit_damage_reduction'] = 0.0
        self.hp = max(0, self.hp - hit)
        b['challenge_last_damage'] = int(hit + dot_damage)
        status_notes = self._apply_enemy_card_status(card) if use_special and card else []
        if self.hp > 0:
            self.statistics['max_damage_taken'] = max(self.statistics['max_damage_taken'], hit + dot_damage)
        if b.get('boss') and b.get('exposed_turns', 0) < 999:
            b['exposed_turns'] = max(0, b.get('exposed_turns', 0) - 1)

        if b.get('enemy_status_turns', 0) > 0:
            b['enemy_status_turns'] = max(0, int(b.get('enemy_status_turns', 0)) - 1)
            if b['enemy_status_turns'] == 0:
                b['enemy_attack_reduction_pct'] = 0.0
                b['enemy_defense_reduction_pct'] = 0.0
                b['enemy_precision_reduction'] = 0
        if self.hp == 0:
            defeat_message = (' + '.join(([f'Queimadura: {dot_damage} de dano'] if dot_damage else []) +
                                         [f'{special_name}: {hit} de dano' + (' CRÍTICO.' if critical else '.')]) + ' Você ficou fora de combate.')
            self._resolve_battle_defeat(hit + dot_damage)
            return dict(damage=hit + dot_damage, raw_damage=raw_formula, attack_base=attack_base, skill_attack=skill_attack,
                        special=use_special, special_card=spec.get('special_attack_card') if use_special else None, attack_type=attack_type, target_type=spec.get('type'),
                        mana=b.get('mana',0), mana_cost=special_cost if use_special else 0, critical=critical, crit_rate=enemy_crit_rate, crit_damage=enemy_crit_damage,
                        target_defense=target_defense, defeat=True, status_notes=status_notes,
                        shield_absorbed=shield_absorbed, technique_damage_reduced=technique_damage_reduced, domain_damage_reduced=domain_damage_reduced,
                        message=defeat_message)

        parts = []
        if dot_damage:
            parts.append(f'Queimadura: {dot_damage} de dano.')
        parts.append(f'{special_name}: {hit} de dano' + (' CRÍTICO.' if critical else '.'))
        parts.extend(status_notes)
        return dict(damage=hit + dot_damage, raw_damage=raw_formula, attack_base=attack_base, skill_attack=skill_attack,
                    special=use_special, special_card=spec.get('special_attack_card') if use_special else None,
                    mana=b.get('mana',0), mana_cost=special_cost if use_special else 0, critical=critical, crit_rate=enemy_crit_rate, crit_damage=enemy_crit_damage,
                    target_defense=target_defense, attack_type=attack_type, target_type=spec.get('type'), status_notes=status_notes,
                    shield_absorbed=shield_absorbed, technique_damage_reduced=technique_damage_reduced, domain_damage_reduced=domain_damage_reduced,
                    message=' '.join(parts) + ' Sua vez.')

    def _end_virtual_battle(self):
        b = self.battle
        if not b or not b.get('virtual'):
            return
        self.hp = int(b.get('pre_hp', self.hp))
        self.memory = int(b.get('pre_memory', self.memory))

    def creature_rarity(self, species_id):
        if species_id in BOSSES:
            return CARDS.get(BOSSES[species_id].get('card'), {}).get('rarity', 'Rara')
        return CARDS.get(SPECIES.get(species_id, {}).get('card'), {}).get('rarity', 'Comum')

    def essence_drop_for_creature(self, species_id):
        low, high = ESSENCE_DROP_RANGES.get(self.creature_rarity(species_id), ESSENCE_DROP_RANGES['Comum'])
        return self.rng.randint(low, high)

    def _award_essence(self, species_id, loot):
        amount = self.essence_drop_for_creature(species_id)
        loot['Essência'] = amount
        self.inventory['Essência'] = self.inventory.get('Essência', 0) + amount
        self.statistics['collectibles']['Essência'] = self.statistics['collectibles'].get('Essência', 0) + amount

    def win(self):
        b = self.battle
        species = b['species']
        domain_xp_gained = self._domain_xp_for_creature(species)
        self._finalize_combat_challenge()
        domain_element = (BOSSES.get(species) if species in BOSSES else SPECIES.get(species, {})).get('type')
        domain_level_before = int(self.domain_levels.get(domain_element, 0) or 0)
        if domain_element in DOMAIN_ELEMENTS and domain_xp_gained:
            self.gain_domain_xp(domain_element, domain_xp_gained)
        loot = {}
        if b.get('boss'):
            boss = BOSSES[species]
            for name, chance, lo, hi in boss.get('drops', []):
                if self.rng.random() < chance:
                    amount = self.rng.randint(lo, hi)
                    drop_bonus = max(0.0, min(50.0, float(self.gauntlet_nexus_drop_bonus_pct)))
                    if drop_bonus:
                        amount = max(1, int(round(amount * (1.0 + drop_bonus / 100.0))))
                    loot[name] = amount
                    self.inventory[name] = self.inventory.get(name, 0) + amount
                    self.statistics['collectibles'][name] = self.statistics['collectibles'].get(name, 0) + amount
            self._award_essence(species, loot)
            # O Núcleo de Dobra é uma recompensa única de RY e não aparece no Simulador.
            if species == 'ry' and not b.get('virtual'):
                name, amount = BOSSES['ry'].get('special_drop', ('Núcleo de Dobra', 1))
                loot[name] = loot.get(name, 0) + int(amount)
                self.inventory[name] = self.inventory.get(name, 0) + int(amount)
                self.statistics['collectibles'][name] = self.statistics['collectibles'].get(name, 0) + int(amount)
            self.bosses.setdefault(species, {'defeated': False, 'virtual_defeats': 0})
            self.statistics['battles_won'] += 1
            if not b.get('virtual'):
                self.bosses[species]['defeated'] = True
                self.statistics['bosses_defeated'][species] = self.statistics['bosses_defeated'].get(species, 0) + 1
                if species in GALAXY_RARE_BOSSES.get(BOSSES[species].get('galaxy'), ()) or species in GALAXY_LEGENDARY_BOSSES.values():
                    self._sync_galaxy_boss_missions(emit_alert=True)
                # A carta de boss não é entregue como cópia ao vencer.
                # A vitória apenas desbloqueia sua receita para fabricação.
                boss_card = BOSSES[species].get('card')
                if boss_card in CARDS:
                    self.discover(boss_card)
                if species == 'ry':
                    self.award_renown('nahr_shadows', 100, 'RY derrotado', planet_id='nahr')
                    self.nahr_ry_contacted = True
                    self.ensure_dobra_core_mission()
                    self.journal_add('ry_defeated', 'RY destruído', 'A esfera de luz se desfaz. As Sombras de Nahr celebram: o mal que habitava o vazio foi destruído e seu povo agora pode seguir a vida em paz.')
                elif species == 'kuvaar':
                    mission = self.missions['kuvaar_hunt']
                    mission['status'] = 'completed'; mission['path'] = 'boss'; mission['reward_claimed'] = True
                    self.statistics['missions_completed'] += 1
                    self.set_objective('kuvaar', 'completed', 3)
                    self.journal_add('kuvaar_defeated', 'Kuvaar derrotado', 'A Couraça de Sal se rompeu. A bacia volta a reter umidade. O projeto do Simulador de Combate está disponível para fabricação na nave.')
                    self._mission_completed_alert('kuvaar_hunt')
                else:
                    self.journal_add(f'boss_{species}_defeated', f'{BOSSES[species]["name"]} derrotado', f'{BOSSES[species]["name"]} foi derrotado e sua carta poderá ser analisada pela Manopla.')
                self.simulator_unlocked = True
                self.simulator_built = False
                self.ensure_ry_investigation_mission()
            else:
                self.bosses[species]['virtual_defeats'] = self.bosses[species].get('virtual_defeats', 0) + 1
            self.discover(species)
            self._end_virtual_battle()
            self.battle = None
            self.last_loot = loot
            self.grace = 3
            self.refresh_achievements()
            self._refresh_all_civ_missions()
            return loot
        first_defeat = self.kills.get(species, 0) <= 0
        self.kills[species] = self.kills.get(species, 0) + 1
        self.statistics['kills'][species] = self.statistics['kills'].get(species, 0) + 1
        self.statistics['battles_won'] += 1
        if first_defeat and species in SPECIES:
            if species not in self.bestiary_known:
                self.bestiary_known.append(species)
            self.discover(SPECIES[species].get('card', species))
        if not b.get('temporary'):
            for name, chance, lo, hi in SPECIES[species]['drops']:
                if self.rng.random() < chance:
                    amount = self.rng.randint(lo, hi)
                    drop_bonus = max(0.0, min(50.0, float(self.gauntlet_nexus_drop_bonus_pct)))
                    if drop_bonus:
                        amount = max(1, int(round(amount * (1.0 + drop_bonus / 100.0))))
                    loot[name] = amount
                    self.inventory[name] = self.inventory.get(name, 0) + amount
                    self.statistics['collectibles'][name] = self.statistics['collectibles'].get(name, 0) + amount
            self._award_essence(species, loot)
            e = self.enemies[b['index']]
            e['dead'] = True
            if e.get('mission_id'):
                e['ready'] = float('inf')
                if e.get('mission_id') == 'ship_comms':
                    self.missions.setdefault('ship_comms', {}).setdefault('progress', 0)
                    self.missions['ship_comms']['progress'] = min(4, self.communication_guards_defeated())
            else:
                e['ready'] = self.time + SPECIES[species]['respawn']
        else:
            mission_id = b.get('mission')
            ok, reward, _ = self.complete_mission(mission_id, 'force')
            loot = reward if ok else {}
            self._award_essence(species, loot)
        self.battle = None
        self.last_loot = loot
        self.grace = 3
        self.refresh_achievements()
        self._refresh_all_civ_missions()
        return loot

    @classmethod
    def _normalize_card_save(cls, d):
        raw_crafted = d.get('crafted', [])
        raw_slots = d.get('slots', [None, None, None])
        raw_unique = d.get('unique_cards', {}) if isinstance(d.get('unique_cards'), dict) else {}
        normalized=[]; base_first={}; serials={}; unique_cards={}
        for item in raw_crafted:
            if not isinstance(item, str): continue
            if cls.is_unique_card_id(item):
                data=raw_unique.get(item)
                if not isinstance(data,dict): continue
                try: element,variant,serial=cls.unique_card_parts(item)
                except ValueError: continue
                buffs=[{'kind':e['kind']} for e in data.get('buffs',[]) if isinstance(e,dict) and e.get('kind') in UNIQUE_BUFF_DEFS]
                momentum=data.get('momentum')
                if isinstance(momentum,dict): momentum=momentum.get('kind')
                if momentum not in UNIQUE_MOMENTUM_DEFS: momentum=None
                unique_cards[item]={'name':data.get('name',f'Carta Única — {element}'),'element':element,'variant':variant,'rarity':'Única','buffs':buffs,'momentum':momentum,'species':None,'description':data.get('description',''),'source_card':data.get('source_card')}
                normalized.append(item); continue
            if item in CARDS:
                base_id=item; variant='normal'; serial=serials.get(base_id,0)+1; serials[base_id]=serial
                new_id=f'{base_id}|normal|{serial}'; base_first.setdefault(base_id,new_id); normalized.append(new_id); continue
            try: base_id,variant,serial=cls.card_parts(item)
            except (ValueError,TypeError): continue
            if base_id not in CARDS or variant not in CARD_VARIANTS: continue
            new_id=f'{base_id}|{variant}|{serial}'; normalized.append(new_id); base_first.setdefault(base_id,new_id); serials[base_id]=max(serials.get(base_id,0),serial)
        for item,data in raw_unique.items():
            if item in unique_cards or not isinstance(item,str) or not cls.is_unique_card_id(item) or not isinstance(data,dict): continue
            try: element,variant,serial=cls.unique_card_parts(item)
            except ValueError: continue
            buffs=[{'kind':e['kind']} for e in data.get('buffs',[]) if isinstance(e,dict) and e.get('kind') in UNIQUE_BUFF_DEFS]
            momentum=data.get('momentum')
            if isinstance(momentum,dict): momentum=momentum.get('kind')
            if momentum not in UNIQUE_MOMENTUM_DEFS: momentum=None
            unique_cards[item]={'name':data.get('name',f'Carta Única — {element}'),'element':element,'variant':variant,'rarity':'Única','buffs':buffs,'momentum':momentum,'species':None,'description':data.get('description',''),'source_card':data.get('source_card')}
            normalized.append(item)
        d['crafted']=normalized; d['unique_cards']=unique_cards
        mapped=[]
        for item in raw_slots:
            if item is None: mapped.append(None)
            elif isinstance(item,str) and item in CARDS: mapped.append(base_first.get(item))
            elif isinstance(item,str):
                try: base_id,variant,serial=cls.card_parts(item)
                except (ValueError,TypeError): mapped.append(None); continue
                mapped_id=f'{base_id}|{variant}|{serial}'; mapped.append(mapped_id if mapped_id in normalized and not cls.is_unique_card_id(mapped_id) else base_first.get(base_id))
            else: mapped.append(None)
        d['slots']=(mapped+[None,None,None])[:3]
        special=d.get('gauntlet_special_slot'); d['gauntlet_special_slot']=special if isinstance(special,str) and special in unique_cards else None

    def save(self, path, refresh=True):
        if self.save_blocked:
            raise ValueError('Save de origem inválido: salvamento bloqueado para preservar o arquivo.')
        if self.battle:
            raise ValueError('Salve fora do combate.')
        if refresh:
            self.refresh_journal()
        data = {k: getattr(self, k) for k in ('pos', 'hp', 'memory', 'memory_owned', 'memory_slots', 'inventory', 'aurora_level', 'crafted', 'slots', 'gauntlet_special_slot', 'unique_cards', 'kills', 'time', 'collected_nodes', 'worlds', 'sector', 'visited', 'chest_generation', 'gauntlet_generation', 'helmet_generation', 'helmet_owned', 'helmet_equipped', 'helmet_design', 'locomotion_generation', 'locomotion_equipped', 'journal', 'society', 'ship_systems', 'combat_stats', 'gauntlet_nexus_installed', 'gauntlet_nexus_xp', 'gauntlet_nexus_level', 'gauntlet_nexus_points', 'gauntlet_nexus_nodes', 'gauntlet_nexus_progression_revision', 'gauntlet_nexus_drop_bonus_pct', 'gauntlet_nexus_advantage_bonus_pct', 'gauntlet_nexus_vampirism_pct', 'gauntlet_nexus_hack_alert_capacity_bonus', 'gauntlet_nexus_hack_diagonal', 'gauntlet_nexus_hack_mask_first_firewall', 'domain_xp', 'domain_levels', 'inside_ship', 'ship_pos', 'language_progress', 'language_mastered', 'language_mastery', 'nahr_language_progress', 'nahr_language_mastered', 'nahr_ry_contacted', 'has_left_veyra', 'pending_language_civilization', 'pending_language_npc_id', 'dobra_core_installed', 'ship_laser_project_unlocked', 'ship_laser_installed', 'travel_damage', 'selected_galaxy_id', 'missions', 'renown', 'renown_events', 'renown_by_faction', 'renown_planets', 'renown_galaxies', 'renown_claimed', 'known_planets', 'selected_planet', 'known_civilizations_by_planet', 'statistics', 'achievements', 'unique_rewards', 'achievement_reward_revision', 'bosses', 'simulator_unlocked', 'simulator_built', 'water_purifier_built', 'scan_unlocked', 'achievement_alerts', 'known_cards', 'bestiary_known', 'bestiary_scanned', 'gauntlet_stones', 'communication_revealed', 'opening_dialogue_pending', 'respawn_tank_built', 'essence_storage', 'game_over', 'helmet_advanced_research_unlocked', 'gauntlet_loadouts', 'civilization_missions')}
        data['version'] = 72
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Mantém um backup do último save válido antes de sobrescrever o principal.
        # Se o save.json atual estiver corrompido, preservamos o bkp.json existente
        # em vez de substituir um backup válido por um arquivo inválido.
        if path.name.lower() == 'save.json' and path.exists():
            backup = path.with_name('bkp.json')
            existing_state, _ = type(self).load(path)
            if not existing_state.save_blocked:
                shutil.copy2(path, backup)
        temp = path.with_name(path.name + '.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(path)

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            return cls(new_game=True), 'Novo jogo iniciado. A nave aguarda dentro de você.'
        try:
            d = json.loads(path.read_text(encoding='utf-8'))
            require = cls._require
            require(isinstance(d, dict), 'estrutura')
            version = d.get('version')
            # Compatibilidade progressiva: qualquer versão inteira a partir do primeiro
            # formato persistente conhecido pode ser migrada pelo normalizador abaixo.
            # Isso evita que uma nova versão de conteúdo torne o save imediatamente
            # bloqueado só porque o número da versão mudou.
            require(type(version) is int and version >= 2, 'versão')
            if version == 2:
                require(type(d.get('modules')) is int and 0 <= d['modules'] <= 2, 'melhorias antigas')
                require(isinstance(d.get('nodes'), list) and len(d['nodes']) == len(NODES), 'coletas antigas')
                require(all(cls._time(v) for v in d['nodes']), 'tempos de coleta')
                count = d['modules']
                d['memory_owned'] = {'basic': 2, 'expanded': count}
                d['memory_slots'] = ['expanded'] * count + ['basic'] * (2-count)
                d['collected_nodes'] = [nid for nid, stamp in zip(NODE_IDS, d['nodes']) if stamp > 0]
            if version < 4:
                require(isinstance(d.get('enemies'), list) and len(d['enemies']) == len(SPAWNS), 'inimigos antigos')
                d['sector'] = 'landing'
                d['visited'] = ['landing']
                d['chest_generation'] = 1
                d['memory_owned']['advanced'] = 0
                d['worlds'] = {key: fresh_enemies(key) for key in SECTORS}
                d['worlds']['landing'][:len(SPAWNS)] = d['enemies']
            if version < 41:
                d['journal'] = fresh_journal()
                d['journal']['objectives']['explore']['progress'] = min(7, len(set(d.get('visited', ['landing']))))
                fragments = d.get('inventory', {}).get('Fragmento histórico', 0)
                d['journal']['objectives']['records']['progress'] = min(3, fragments)
                if 'ruins' in d.get('visited', []):
                    d['journal']['objectives']['unknown_signal']['status'] = 'completed'
                    d['journal']['objectives']['records']['status'] = 'active'
                if d.get('sector') == 'landing' and d.get('pos') is not None:
                    px, py = d['pos']
                    ship = SECTORS['landing']['ship']
                    if distance((px, py), ship) <= 1:
                        d['journal']['objectives']['survive']['status'] = 'completed'
                        d['journal']['objectives']['ship']['status'] = 'active'
                if len(set(d.get('visited', []))) == len(SECTORS):
                    d['journal']['objectives']['explore']['status'] = 'completed'
                if fragments >= 3:
                    d['journal']['objectives']['records']['status'] = 'completed'
                d['journal']['seen'] = ['arrival', 'armour']
            if version < 42:
                d['society'] = fresh_society()
                # 0.4.1 já possui um diário válido; apenas acrescentamos o novo objetivo social.
                if 'settlement' not in d['journal']['objectives']:
                    d['journal']['objectives']['settlement'] = fresh_journal()['objectives']['settlement']
                if 'ruins' in d.get('visited', []):
                    d['journal']['objectives']['settlement']['status'] = 'active'
            if version < 43:
                d['gauntlet_generation'] = 1
                d['helmet_generation'] = 0
                d['helmet_owned'] = False
                d['helmet_equipped'] = False
                d['locomotion_generation'] = 0
                d['locomotion_equipped'] = False

            if version < 45:
                # Expande os saves antigos para os sete mapas atuais, preservando estados já conhecidos.
                old_worlds = d.get('worlds', {}) if isinstance(d.get('worlds'), dict) else {}
                new_worlds = {key: fresh_enemies(key) for key in SECTORS}
                for sector, old_enemies in old_worlds.items():
                    if sector in new_worlds:
                        for idx, old_enemy in enumerate(old_enemies[:len(new_worlds[sector])]):
                            new_worlds[sector][idx].update(old_enemy)
                d['worlds'] = new_worlds
                d['inside_ship'] = False
                d['ship_pos'] = list(SHIP_INTERIOR['start'])
                d['language_progress'] = 0
                d['language_mastered'] = False
                d['missions'] = fresh_missions()
                d['renown'] = 50
                d['renown_events'] = []
                stats = fresh_statistics()
                old_stats = d.get('statistics') if isinstance(d.get('statistics'), dict) else {}
                stats.update({k: old_stats[k] for k in stats if k in old_stats and k not in ('kills','cards_crafted','mission_paths')})
                stats['kills'].update(d.get('kills', {}))
                stats['kills'].update(old_stats.get('kills', {}) if isinstance(old_stats.get('kills'), dict) else {})
                stats['collectibles'].update(old_stats.get('collectibles', {}) if isinstance(old_stats.get('collectibles'), dict) else {})
                stats['cards_crafted'].update(old_stats.get('cards_crafted', {}) if isinstance(old_stats.get('cards_crafted'), dict) else {})
                stats['mission_paths'].update(old_stats.get('mission_paths', {}) if isinstance(old_stats.get('mission_paths'), dict) else {})
                d['statistics'] = stats
                d['achievements'] = fresh_achievements()
                d['unique_rewards'] = []
                journal = fresh_journal()
                old_journal = d.get('journal') if isinstance(d.get('journal'), dict) else {}
                journal['entries'] = old_journal.get('entries', journal['entries'])
                journal['seen'] = old_journal.get('seen', journal['seen'])
                if isinstance(old_journal.get('objectives'), dict):
                    for oid, obj in old_journal['objectives'].items():
                        if oid in journal['objectives']:
                            journal['objectives'][oid] = obj
                d['journal'] = journal
            if version < 46:
                old_missions = d.get('missions') if isinstance(d.get('missions'), dict) else {}
                new_missions = fresh_missions()
                if isinstance(old_missions.get('water_supply'), dict):
                    new_missions['water_supply'].update(old_missions['water_supply'])
                if new_missions['water_supply'].get('status') == 'completed':
                    new_missions['kuvaar_hunt']['status'] = 'available'
                d['missions'] = new_missions
                stats = d.get('statistics') if isinstance(d.get('statistics'), dict) else {}
                stats.setdefault('bosses_defeated', {})
                stats.setdefault('boss_rematches', {})
                d['statistics'] = stats
                d['bosses'] = {bid: {'defeated': False, 'virtual_defeats': 0} for bid in BOSSES}
                d['simulator_unlocked'] = False
                d['simulator_built'] = False
                if d['missions']['water_supply'].get('status') == 'completed':
                    d['simulator_unlocked'] = False
                d.setdefault('inventory', {})
            if version < 47:
                # A 0.4.7 muda apenas o modo de resgate: saves anteriores já passaram
                # pelas revisões 2/3 acima e já carregam os valores finais das conquistas.
                # Aqui apenas convertemos o estado antigo (desbloqueada = já premiada)
                # para o novo estado de resgate manual, sem duplicar nem remover bônus.
                achievements = d.get('achievements') if isinstance(d.get('achievements'), dict) else fresh_achievements()
                normalized = fresh_achievements()
                for aid in ACHIEVEMENTS:
                    old_entry = achievements.get(aid, {}) if isinstance(achievements, dict) else {}
                    was_unlocked = bool(old_entry.get('unlocked', False))
                    normalized[aid]['unlocked'] = was_unlocked
                    normalized[aid]['claimed'] = was_unlocked
                d['achievements'] = normalized
                d['achievement_alerts'] = []
                d['scan_unlocked'] = bool(d.get('scan_unlocked', False))
            if version < 48:
                old_missions = d.get('missions') if isinstance(d.get('missions'), dict) else {}
                new_missions = fresh_missions()
                for key in ('water_supply', 'kuvaar_hunt'):
                    if isinstance(old_missions.get(key), dict):
                        new_missions[key].update(old_missions[key])
                d['missions'] = new_missions
                d.setdefault('journal', {}).setdefault('objectives', {})
                d['journal']['objectives']['faction_conflict'] = fresh_journal()['objectives']['faction_conflict']
                d.setdefault('statistics', {}).setdefault('missions_completed', 0)

            # Compatibilidade retroativa de mundo: versões anteriores à 0.5.1
            # não possuíam o setor de comunicação. Quando um setor atual não
            # existir no save, criamos apenas seus inimigos iniciais; todo o
            # progresso dos setores já existentes permanece intacto.
            if not isinstance(d.get('worlds'), dict):
                d['worlds'] = {}
            for _sector in SECTORS:
                if _sector not in d['worlds']:
                    d['worlds'][_sector] = fresh_enemies(_sector)

            d.setdefault('achievement_alerts', [])
            if not isinstance(d.get('achievement_alerts'), list):
                d['achievement_alerts'] = []
            d.setdefault('scan_unlocked', False)
            d.setdefault('opening_dialogue_pending', False)
            d.setdefault('respawn_tank_built', False)
            d.setdefault('essence_storage', 0)
            d.setdefault('game_over', False)
            d['opening_dialogue_pending'] = False
            try: d['essence_storage'] = max(0, int(d.get('essence_storage', 0)))
            except (TypeError, ValueError): d['essence_storage'] = 0
            d.setdefault('known_cards', [])
            d.setdefault('nahr_language_progress', 0)
            d.setdefault('nahr_language_mastered', False)
            d.setdefault('nahr_ry_contacted', False)
            d.setdefault('has_left_veyra', False)
            if not d.get('has_left_veyra'):
                d['has_left_veyra'] = any(str(sec) != 'landing' and str(sec) != 'veyra' and (str(sec).startswith(('orionis','kael','nahr','elyra')) or str(sec) in SECTORS) for sec in d.get('visited', []))
            d.setdefault('bestiary_known', [])
            d.setdefault('bestiary_scanned', [])
            d['helmet_advanced_research_unlocked'] = bool(d.get('helmet_advanced_research_unlocked', False))
            d['gauntlet_loadouts'] = d.get('gauntlet_loadouts') if isinstance(d.get('gauntlet_loadouts'), list) else [None,None,None]
            d['gauntlet_loadouts'] = (d['gauntlet_loadouts'] + [None,None,None])[:3]
            d['gauntlet_loadouts'] = [x if isinstance(x, dict) and isinstance(x.get('slots'), list) else None for x in d['gauntlet_loadouts']]
            d['civilization_missions'] = d.get('civilization_missions') if isinstance(d.get('civilization_missions'), dict) else {}
            d.setdefault('helmet_advanced_research_unlocked', False)

            # Builds 0.4.3 anteriores ao diagnóstico ainda não possuem este campo.
            d.setdefault('bosses', {bid: {'defeated': False, 'virtual_defeats': 0} for bid in BOSSES})
            for bid in BOSSES:
                d['bosses'].setdefault(bid, {'defeated': False, 'virtual_defeats': 0})
            d.setdefault('simulator_unlocked', False)
            d.setdefault('simulator_built', False)
            d.setdefault('water_purifier_built', False)
            d.setdefault('gauntlet_stones', [None, None, None, None, None, None])
            if not isinstance(d.get('gauntlet_stones'), list):
                d['gauntlet_stones'] = [None, None, None, None, None, None]
            d['gauntlet_stones'] = (d['gauntlet_stones'] + [None, None, None, None, None, None])[:6]
            # Corrige saves 0.4.6 intermediários criados antes do objetivo Kuvaar existir no diário.
            fresh = fresh_journal()
            d.setdefault('journal', fresh)
            d.setdefault('journal', {}).setdefault('objectives', {})
            for oid, obj in fresh['objectives'].items():
                d['journal']['objectives'].setdefault(oid, obj.copy())
            d.setdefault('ship_systems', fresh_ship_systems())
            d.setdefault('communication_revealed', False)
            # 0.5.1 adiciona seis missões de reparo da nave sem invalidar campanhas anteriores.
            current_missions = d.get('missions') if isinstance(d.get('missions'), dict) else {}
            ship_defaults = fresh_missions()
            for _mid in ('ship_hull','ship_power','ship_propulsion','ship_navigation','ship_comms','ship_ftl'):
                if not isinstance(current_missions.get(_mid), dict):
                    current_missions[_mid] = ship_defaults[_mid].copy()
                else:
                    merged = ship_defaults[_mid].copy(); merged.update(current_missions[_mid]); current_missions[_mid] = merged
            if not isinstance(current_missions.get('explore_galaxy'), dict):
                current_missions['explore_galaxy'] = ship_defaults['explore_galaxy'].copy()
            else:
                merged = ship_defaults['explore_galaxy'].copy(); merged.update(current_missions['explore_galaxy']); current_missions['explore_galaxy'] = merged
            d['missions'] = current_missions
            # Converte uma posição antiga do interior para a nova malha visual, quando necessário.
            if isinstance(d.get('ship_pos'), list) and len(d['ship_pos']) == 2:
                old_positions = {(6,6),(9,2),(3,4),(9,5),(3,6),(6,8)}
                if tuple(d['ship_pos']) in old_positions:
                    d['ship_pos'] = list(SHIP_INTERIOR['start'])
            d.setdefault('gauntlet_generation', 1)
            d.setdefault('helmet_design', 'tactical' if d.get('helmet_owned') else None)
            if d.get('helmet_owned'):
                d['helmet_equipped'] = True
                if d.get('helmet_design') not in HELMET_DESIGN_ORDER:
                    d['helmet_design'] = 'tactical'
            d.setdefault('gauntlet_nexus_installed', False)
            d.setdefault('gauntlet_nexus_xp', 0)
            d.setdefault('gauntlet_nexus_level', 1)
            d.setdefault('gauntlet_nexus_points', 0)
            d.setdefault('gauntlet_nexus_nodes', [])
            d.setdefault('gauntlet_nexus_progression_revision', 1)
            d.setdefault('gauntlet_nexus_drop_bonus_pct', 0.0)
            d.setdefault('gauntlet_nexus_advantage_bonus_pct', 0.0)
            d.setdefault('gauntlet_nexus_vampirism_pct', 0.0)
            d.setdefault('gauntlet_nexus_hack_alert_capacity_bonus', 0)
            d.setdefault('gauntlet_nexus_hack_diagonal', False)
            d.setdefault('gauntlet_nexus_hack_mask_first_firewall', False)
            for aid in ACHIEVEMENTS:
                d.setdefault('achievements', {}).setdefault(aid, {'unlocked': False, 'claimed': False})
                d['achievements'][aid].setdefault('claimed', False)
            nexus_revision = int(d.get('gauntlet_nexus_progression_revision', 1) or 1)
            original_nexus_revision = nexus_revision
            if nexus_revision < 3:
                legacy_nodes = d.get('gauntlet_nexus_nodes') if isinstance(d.get('gauntlet_nexus_nodes'), list) else []
                from content import NEXUS_LEVEL_XP
                xp = max(0, int(d.get('gauntlet_nexus_xp', 0) or 0))
                level = 1
                if bool(d.get('gauntlet_nexus_installed', False)):
                    for level_id, threshold in sorted(NEXUS_LEVEL_XP.items()):
                        if xp >= threshold:
                            level = level_id
                        else:
                            break
                d['gauntlet_nexus_level'] = level
                d['gauntlet_nexus_points'] = 0
                d['gauntlet_nexus_nodes'] = []
                d['gauntlet_nexus_hack_alert_capacity_bonus'] = 0
                d['gauntlet_nexus_hack_diagonal'] = False
                d['gauntlet_nexus_hack_mask_first_firewall'] = False
                d['_legacy_nexus_nodes_snapshot'] = legacy_nodes
                d['_nexus_migration_previous_revision'] = nexus_revision
                d['_nexus_migration_level'] = level
                d['gauntlet_nexus_progression_revision'] = 3
            if nexus_revision < 4:
                from content import NEXUS_LEVEL_XP
                xp = max(0, int(d.get('gauntlet_nexus_xp', 0) or 0))
                level = 1
                if bool(d.get('gauntlet_nexus_installed', False)):
                    for level_id, threshold in sorted(NEXUS_LEVEL_XP.items()):
                        if xp >= threshold:
                            level = level_id
                        else:
                            break
                d['gauntlet_nexus_level'] = level
                d['gauntlet_nexus_points'] = 0
                d['gauntlet_nexus_nodes'] = []
                d['gauntlet_nexus_hack_alert_capacity_bonus'] = 0
                d['gauntlet_nexus_hack_diagonal'] = False
                d['gauntlet_nexus_hack_mask_first_firewall'] = False
                d['_nexus_migration_previous_revision'] = nexus_revision
                d['_nexus_migration_level'] = level
                d['gauntlet_nexus_progression_revision'] = 4
            if nexus_revision < 5:
                # A revisão 4 foi a tabela anterior de nós. Removemos seus efeitos
                # antes de reconstruir a tabela 5 usando o mesmo XP acumulado.
                if isinstance(d.get('combat_stats'), dict):
                    legacy_v4 = {
                        'nexus_level_01': ('precision', 1),
                        'nexus_level_02': ('attack_bonus', 0.5),
                        'nexus_level_03': ('attack_bonus', 0.5),
                        'nexus_level_05': ('hack_alert_capacity_bonus', 1),
                        'nexus_level_06': ('crit_rate_bonus', 0.5),
                        'nexus_level_07': ('precision', 1),
                        'nexus_level_09': ('attack_bonus', 0.5),
                        'nexus_level_11': ('min_damage_bonus', 1),
                        'nexus_level_13': ('precision', 1),
                        'nexus_level_14': ('crit_damage_bonus', 0.05),
                        'nexus_level_17': ('attack_bonus', 0.5),
                        'nexus_level_18': ('min_damage_bonus', 1),
                        'nexus_level_19': ('attack_bonus', 0.5),
                        'nexus_level_20': ('amp_bonus', 0.10),
                    }
                    legacy_nodes = d.get('gauntlet_nexus_nodes') if isinstance(d.get('gauntlet_nexus_nodes'), list) else []
                    for node_id in legacy_nodes:
                        if node_id not in legacy_v4:
                            continue
                        field, value = legacy_v4[node_id]
                        if field in d['combat_stats']:
                            d['combat_stats'][field] = float(d['combat_stats'].get(field, 0)) - float(value)
                            if field in ('precision', 'min_damage_bonus'):
                                d['combat_stats'][field] = max(0, int(round(d['combat_stats'][field])))
                    hack_total = sum(1 for node_id in legacy_nodes if node_id == 'nexus_level_05')
                    d['gauntlet_nexus_hack_alert_capacity_bonus'] = max(0, int(d.get('gauntlet_nexus_hack_alert_capacity_bonus', 0)) - hack_total)
                d['_nexus_migration_previous_revision'] = nexus_revision
                d['_nexus_migration_level'] = int(d.get('gauntlet_nexus_level', 1) or 1)
                d['gauntlet_nexus_progression_revision'] = 5
            else:
                d['gauntlet_nexus_progression_revision'] = 5

            # Corrige saves que ficaram na casa do ponto de entrada antigo da nave.
            if d.get('inside_ship') and d.get('ship_pos') == [6, 7]:
                d['ship_pos'] = list(SHIP_INTERIOR['start'])
            # Combate por atributos/amp/crítico. Saves anteriores recebem os defaults
            # e qualquer campo novo ausente é preenchido, preservando alterações antigas.
            combat_defaults = dict(PLAYER_COMBAT)
            # Saves antigos podem não conter as novas espécies de Veyra.
            old_kills = d.get('kills') if isinstance(d.get('kills'), dict) else {}
            d['kills'] = {**{key: 0 for key in SPECIES}, **old_kills}
            existing_combat = d.get('combat_stats')
            if isinstance(existing_combat, dict):
                combat_defaults.update(existing_combat)
            # A revisão 0.4.5 anterior concedia atributos por várias conquistas.
            # Converte esses bônus antigos para o novo modelo: apenas os três
            # marcos de coleção de cartas permanecem com recompensa de atributo.
            reward_revision = int(d.get('achievement_reward_revision', 1)) if isinstance(d.get('achievement_reward_revision', 1), (int, float)) else 1
            if reward_revision < 2:
                legacy_stat_rewards = {
                    'first_blood': ('defense_bonus', 1),
                    'desert_survivor': ('defense_bonus', 1),
                    'salvager': ('attack_bonus', 1),
                    'pathfinder': ('crit_rate_bonus', 1.0),
                    'waterkeeper': ('defense_bonus', 1),
                    'helmet_rebuilt': ('attack_bonus', 1),
                    'clean_intrusion': ('crit_rate_bonus', 1.0),
                    'force_of_will': ('attack_bonus', 1),
                    'card_collector_normal': ('attack_bonus', 1),
                    'card_collector_plus': ('crit_rate_bonus', 1.0),
                }
                for aid, (field, value) in legacy_stat_rewards.items():
                    if isinstance(d.get('achievements'), dict) and d['achievements'].get(aid, {}).get('unlocked'):
                        combat_defaults[field] = max(0, combat_defaults.get(field, 0) - value)
                # Reaplica somente os bônus de atributos previstos nesta revisão.
                if isinstance(d.get('achievements'), dict):
                    if d['achievements'].get('card_collector_normal', {}).get('unlocked'):
                        combat_defaults['attack_bonus'] += 1
                    if d['achievements'].get('card_collector_plus', {}).get('unlocked'):
                        combat_defaults['defense_bonus'] += 1
                    if d['achievements'].get('card_collector_plusplus', {}).get('unlocked'):
                        combat_defaults['crit_rate_bonus'] += 1.0
                d['achievement_reward_revision'] = 2
            else:
                d['achievement_reward_revision'] = reward_revision
            # Revisão 0.4.5: converte os bônus de coleção para a recompensa final:
            # normal = ATQ +10, + = Dano Crítico +6%, ++ = AMP +5%.
            reward_revision = int(d.get('achievement_reward_revision', 1)) if isinstance(d.get('achievement_reward_revision', 1), (int, float)) else 1
            if reward_revision < 3:
                achievements = d.get('achievements') if isinstance(d.get('achievements'), dict) else {}
                # Remove os bônus de coleção das revisões anteriores.
                if achievements.get('card_collector_normal', {}).get('unlocked'):
                    combat_defaults['attack_bonus'] = max(0, int(combat_defaults.get('attack_bonus', 0)) - 1)
                if achievements.get('card_collector_plus', {}).get('unlocked'):
                    combat_defaults['defense_bonus'] = max(0, int(combat_defaults.get('defense_bonus', 0)) - 1)
                if achievements.get('card_collector_plusplus', {}).get('unlocked'):
                    combat_defaults['crit_rate_bonus'] = max(0.0, float(combat_defaults.get('crit_rate_bonus', 0.0)) - 1.0)
                # Aplica os bônus definitivos somente se a respectiva conquista já estiver concluída.
                if achievements.get('card_collector_normal', {}).get('unlocked'):
                    combat_defaults['attack_bonus'] += 10
                if achievements.get('card_collector_plus', {}).get('unlocked'):
                    combat_defaults['crit_damage_bonus'] += 0.06
                if achievements.get('card_collector_plusplus', {}).get('unlocked'):
                    combat_defaults['amp_bonus'] += 5.0
                d['achievement_reward_revision'] = 3
            else:
                d['achievement_reward_revision'] = reward_revision
            if version < 47:
                d['achievement_reward_revision'] = 4
            nexus_migration_level = d.pop('_nexus_migration_level', None)
            nexus_previous_revision = int(d.pop('_nexus_migration_previous_revision', 0) or 0)
            legacy_nodes_snapshot = d.pop('_legacy_nexus_nodes_snapshot', [])
            if nexus_migration_level is not None:
                if nexus_previous_revision < 3 and isinstance(legacy_nodes_snapshot, list):
                    legacy_bonus = {
                        'impact_calibration': ('attack_bonus', 1.0), 'impact_calibration_2': ('attack_bonus', 1.0), 'impact_calibration_3': ('attack_bonus', 1.0),
                        'precision_targeting_1': ('precision', 1), 'precision_targeting_2': ('precision', 1),
                        'precision_routines_1': ('crit_rate_bonus', 0.5), 'precision_routines_2': ('crit_rate_bonus', 0.5),
                        'kinetic_floor_1': ('min_damage_bonus', 1), 'kinetic_floor_2': ('min_damage_bonus', 1),
                        'critical_feedback_1': ('crit_damage_bonus', 0.05), 'critical_feedback_2': ('crit_damage_bonus', 0.05),
                        'resonant_amp': ('amp_bonus', 0.10), 'reactive_plating': ('defense_bonus', 1),
                    }
                    for nid in legacy_nodes_snapshot:
                        if nid in legacy_bonus:
                            field, value = legacy_bonus[nid]
                            combat_defaults[field] = float(combat_defaults.get(field, 0.0)) - float(value)
                            if field in ('precision', 'min_damage_bonus', 'defense_bonus'):
                                combat_defaults[field] = max(0, int(round(combat_defaults[field])))
                elif nexus_previous_revision == 3 and d.get('gauntlet_nexus_installed', False):
                    # A revisão 3 distribuía os antigos bônus por praticamente todos os
                    # níveis. Removemos apenas esses efeitos para reconstruir a revisão 5.
                    old_v3 = {
                        1: ('precision', 1), 2: ('attack_bonus', 0.5), 3: ('attack_bonus', 0.5),
                        4: ('crit_rate_bonus', 0.5), 6: ('min_damage_bonus', 1), 7: ('precision', 1),
                        8: ('crit_damage_bonus', 0.05), 9: ('attack_bonus', 0.5), 11: ('crit_rate_bonus', 0.5),
                        12: ('min_damage_bonus', 1), 13: ('precision', 1), 14: ('crit_damage_bonus', 0.05),
                        16: ('attack_bonus', 0.5), 17: ('crit_rate_bonus', 0.5), 18: ('min_damage_bonus', 1),
                        19: ('attack_bonus', 0.5), 20: ('amp_bonus', 0.10),
                    }
                    for level_id in range(1, int(nexus_migration_level) + 1):
                        if level_id in old_v3:
                            field, value = old_v3[level_id]
                            combat_defaults[field] = float(combat_defaults.get(field, 0.0)) - float(value)
                            if field in ('precision', 'min_damage_bonus'):
                                combat_defaults[field] = max(0, int(round(combat_defaults[field])))

                d['gauntlet_nexus_nodes'] = []
                if nexus_previous_revision < 5 and d.get('gauntlet_nexus_installed', False):
                    for level_id in range(1, int(nexus_migration_level) + 1):
                        node = NEXUS_NODES.get(f'nexus_level_{level_id:02d}')
                        if not node:
                            continue
                        d['gauntlet_nexus_nodes'].append(f'nexus_level_{level_id:02d}')
                        if node.get('kind') == 'stat':
                            field = node.get('field'); value = float(node.get('value', 0))
                            combat_defaults[field] = float(combat_defaults.get(field, 0.0)) + value
                            if field in ('precision','min_damage_bonus'):
                                combat_defaults[field] = int(round(combat_defaults[field]))
                        elif node.get('kind') == 'hack':
                            field = node.get('field')
                            if field == 'hack_alert_capacity_bonus':
                                d['gauntlet_nexus_hack_alert_capacity_bonus'] += int(node.get('value', 0))
                            elif field == 'hack_diagonal':
                                d['gauntlet_nexus_hack_diagonal'] = bool(node.get('value', 0))
                            elif field == 'hack_mask_first_firewall':
                                d['gauntlet_nexus_hack_mask_first_firewall'] = bool(node.get('value', 0))

            if version < 49:
                # 0.4.9: os quatro marcos de Calibração de Impacto passaram de
                # +0,5 ATQ para +1 ATQ. Saves 0.4.8 na revisão 5 já possuem
                # esses bônus aplicados em combat_stats; acrescentamos apenas
                # a diferença de +0,5 por marco efetivamente alcançado.
                if version == 48 and original_nexus_revision == 5 and isinstance(d.get('combat_stats'), dict):
                    reached = set(d.get('gauntlet_nexus_nodes', []))
                    for node_id in ('nexus_level_02', 'nexus_level_03', 'nexus_level_09', 'nexus_level_17'):
                        if node_id in reached:
                            combat_defaults['attack_bonus'] = float(combat_defaults.get('attack_bonus', 0.0)) + 0.5
                d['gauntlet_nexus_progression_revision'] = 6
            else:
                d['gauntlet_nexus_progression_revision'] = max(6, int(d.get('gauntlet_nexus_progression_revision', 6) or 6))

            # Hotfix da 0.4.9: níveis 12 e 19 do NEXUS agora concedem +1% de Taxa Crítica e +2% de Dano Crítico.
            nexus_revision = int(d.get('gauntlet_nexus_progression_revision', 1) or 1)
            if nexus_revision < 7:
                reached = set(d.get('gauntlet_nexus_nodes', []))
                if d.get('gauntlet_nexus_installed', False):
                    if 'nexus_level_12' in reached:
                        combat_defaults['crit_rate_bonus'] = float(combat_defaults.get('crit_rate_bonus', 0.0)) + 0.5
                    if 'nexus_level_19' in reached:
                        combat_defaults['crit_damage_bonus'] = max(0.0, float(combat_defaults.get('crit_damage_bonus', 0.0)) - 0.03)
                d['gauntlet_nexus_progression_revision'] = 7
            else:
                d['gauntlet_nexus_progression_revision'] = max(7, nexus_revision)
            # 0.6.6: expande o NEXUS para 50 níveis e substitui os antigos
            # marcos de Hack por Drop, Dano de Vantagem e Vampirismo.
            nexus_revision = int(d.get('gauntlet_nexus_progression_revision', 7) or 7)
            if nexus_revision < 8:
                old_level = max(1, min(20, int(d.get('gauntlet_nexus_level', 1) or 1)))
                installed = bool(d.get('gauntlet_nexus_installed', False))
                if installed:
                    old_stat_nodes = {
                        1: ('precision', 1), 2: ('attack_bonus', 1.0), 3: ('attack_bonus', 1.0),
                        7: ('precision', 1), 9: ('attack_bonus', 1.0), 12: ('crit_rate_bonus', 1.0),
                        13: ('precision', 1), 16: ('min_damage_bonus', 1), 17: ('attack_bonus', 1.0),
                        19: ('crit_damage_bonus', 0.02), 20: ('amp_bonus', 0.10),
                    }
                    for level_id in range(1, old_level + 1):
                        if level_id in old_stat_nodes:
                            field, value = old_stat_nodes[level_id]
                            combat_defaults[field] = float(combat_defaults.get(field, 0.0)) - float(value)
                            if field in ('precision', 'min_damage_bonus'):
                                combat_defaults[field] = max(0, int(round(combat_defaults[field])))
                    d['gauntlet_nexus_drop_bonus_pct'] = 0.0
                    d['gauntlet_nexus_advantage_bonus_pct'] = 0.0
                    d['gauntlet_nexus_vampirism_pct'] = 0.0
                    d['gauntlet_nexus_hack_alert_capacity_bonus'] = 0
                    d['gauntlet_nexus_hack_diagonal'] = False
                    d['gauntlet_nexus_hack_mask_first_firewall'] = False
                    d['gauntlet_nexus_nodes'] = []
                    for level_id in range(1, old_level + 1):
                        node = NEXUS_NODES.get(f'nexus_level_{level_id:02d}')
                        if not node:
                            continue
                        d['gauntlet_nexus_nodes'].append(f'nexus_level_{level_id:02d}')
                        kind = node.get('kind'); value = float(node.get('value', 0) or 0)
                        if kind == 'stat':
                            field = node.get('field')
                            if field in combat_defaults:
                                combat_defaults[field] = float(combat_defaults.get(field, 0.0)) + value
                                if field in ('precision', 'min_damage_bonus'):
                                    combat_defaults[field] = int(round(combat_defaults[field]))
                        elif kind == 'drop':
                            d['gauntlet_nexus_drop_bonus_pct'] = min(50.0, d['gauntlet_nexus_drop_bonus_pct'] + value)
                        elif kind == 'advantage':
                            d['gauntlet_nexus_advantage_bonus_pct'] = min(50.0, d['gauntlet_nexus_advantage_bonus_pct'] + value)
                        elif kind == 'vampirism':
                            d['gauntlet_nexus_vampirism_pct'] = min(5.0, d['gauntlet_nexus_vampirism_pct'] + value)
                else:
                    d['gauntlet_nexus_nodes'] = []
                    d['gauntlet_nexus_drop_bonus_pct'] = 0.0
                    d['gauntlet_nexus_advantage_bonus_pct'] = 0.0
                    d['gauntlet_nexus_vampirism_pct'] = 0.0
                d['gauntlet_nexus_progression_revision'] = 8
            else:
                d['gauntlet_nexus_progression_revision'] = max(8, nexus_revision)
            try: d['gauntlet_nexus_drop_bonus_pct'] = max(0.0, min(50.0, float(d.get('gauntlet_nexus_drop_bonus_pct', 0.0))))
            except (TypeError, ValueError): d['gauntlet_nexus_drop_bonus_pct'] = 0.0
            try: d['gauntlet_nexus_advantage_bonus_pct'] = max(0.0, min(50.0, float(d.get('gauntlet_nexus_advantage_bonus_pct', 0.0))))
            except (TypeError, ValueError): d['gauntlet_nexus_advantage_bonus_pct'] = 0.0
            try: d['gauntlet_nexus_vampirism_pct'] = max(0.0, min(5.0, float(d.get('gauntlet_nexus_vampirism_pct', 0.0))))
            except (TypeError, ValueError): d['gauntlet_nexus_vampirism_pct'] = 0.0
            # Saves antigos não tinham registro explícito de conhecimento; inferimos
            # apenas o que já era objetivamente conhecido, sem criar alertas retroativos.
            inferred_cards = []
            for cid, card in CARDS.items():
                if card.get('acquisition') == 'faction_conflict':
                    known = bool(d.get('missions', {}).get('faction_conflict', {}).get('status') == 'completed') or any(str(c).startswith(cid + '|') for c in d.get('crafted', []))
                elif cid == 'kuvaar':
                    known = bool(d.get('bosses', {}).get('kuvaar', {}).get('defeated')) or any(str(c).startswith(cid + '|') for c in d.get('crafted', []))
                else:
                    known = int(d.get('kills', {}).get(card.get('species'), 0)) > 0 or any(str(c).startswith(cid + '|') for c in d.get('crafted', []))
                if known:
                    inferred_cards.append(cid)
            d['known_cards'] = sorted(set(d.get('known_cards', [])) | set(inferred_cards))
            d['bestiary_known'] = sorted({sid for sid,v in d.get('kills', {}).items() if int(v) > 0 and sid in SPECIES})
            d['bestiary_scanned'] = sorted(set(d.get('bestiary_scanned', [])) & set(d['bestiary_known']))
            # Conquistas de 1000 abates são reveladas somente para criaturas já conhecidas.
            loaded_achievements = d.get('achievements') if isinstance(d.get('achievements'), dict) else {}
            for _sid in d.get('bestiary_known', []):
                if _sid in SPECIES:
                    _aid = creature_achievement_id(_sid)
                    loaded_achievements.setdefault(_aid, {'unlocked': False, 'claimed': False})
            d['achievements'] = loaded_achievements
            d['combat_stats'] = combat_defaults
            d.setdefault('inside_ship', False)
            d.setdefault('ship_pos', list(SHIP_INTERIOR['start']))
            d.setdefault('language_progress', 0)
            d.setdefault('language_mastered', False)
            defaults_missions = fresh_missions()
            existing_missions = d.get('missions') if isinstance(d.get('missions'), dict) else {}
            for _mid, _mdata in defaults_missions.items():
                existing_missions.setdefault(_mid, _mdata)
            d['missions'] = existing_missions
            d.setdefault('renown', 50)
            d.setdefault('renown_events', [])
            d.setdefault('aurora_level', 0)
            d.setdefault('renown_by_faction', {fid: 0 for fid in FACTIONS})
            for fid in FACTIONS: d['renown_by_faction'].setdefault(fid, 0)
            d.setdefault('renown_planets', {'veyra': 0})
            d.setdefault('renown_galaxies', {GALAXY_ID: 0})
            d.setdefault('renown_claimed', [])
            d.setdefault('known_planets', ['veyra'])
            d.setdefault('selected_planet', 'veyra')
            default_civs = {r['id']: list(r.get('initial_known_civilizations', [])) for r in STELLAR_ROUTES}
            existing_civs = d.get('known_civilizations_by_planet') if isinstance(d.get('known_civilizations_by_planet'), dict) else {}
            for _rid, _civs in default_civs.items():
                existing_civs.setdefault(_rid, _civs if _rid in d.get('known_planets', []) else [])
            d['known_civilizations_by_planet'] = existing_civs
            valid_route_ids = {r['id'] for r in STELLAR_ROUTES}
            raw_known_planets = d.get('known_planets') if isinstance(d.get('known_planets'), list) else []
            d['known_planets'] = list(dict.fromkeys(pid for pid in raw_known_planets if isinstance(pid, str)))
            if 'veyra' not in d['known_planets']:
                d['known_planets'].insert(0, 'veyra')
            # Um planeta ainda desconhecido para esta build não deve invalidar o save;
            # quando a versão que o conhece for aberta, o ID continua disponível.
            if not isinstance(d.get('selected_planet'), str):
                d['selected_planet'] = 'veyra'
            d.setdefault('statistics', fresh_statistics())
            stats_defaults = fresh_statistics(); stats_defaults.update(d['statistics'])
            stats_defaults['kills'] = {**fresh_statistics()['kills'], **d['statistics'].get('kills', {})}
            stats_defaults['cards_crafted'] = {**fresh_statistics()['cards_crafted'], **d['statistics'].get('cards_crafted', {})}
            stats_defaults['mission_paths'] = {**fresh_statistics()['mission_paths'], **d['statistics'].get('mission_paths', {})}
            for skey in ('battles_started','battles_won','battles_fled','critical_hits','max_damage_dealt','max_damage_taken','missions_completed','missions_failed'):
                stats_defaults[skey] = max(0, int(stats_defaults.get(skey, 0)))
            d['statistics'] = stats_defaults
            d.setdefault('achievements', fresh_achievements())
            d.setdefault('unique_rewards', [])
            d.setdefault('achievement_reward_revision', 4)
            d['achievement_reward_revision'] = max(4, int(d.get('achievement_reward_revision', 4) or 4))
            d.setdefault('society', fresh_society())
            d.setdefault('crafted', [])
            d.setdefault('slots', [None, None, None])
            d.setdefault('gauntlet_special_slot', None)
            d.setdefault('unique_cards', {})
            cls._normalize_card_save(d)
            d['memory_slots'] = (list(d.get('memory_slots') or []) + [None]*TOTAL_MEMORY_SLOTS)[:TOTAL_MEMORY_SLOTS]

            # Camada de compatibilidade resiliente. Saves legítimos podem trazer
            # coleções incompletas porque a lista de espécies/mapas cresce ao longo do
            # projeto. Reconstituímos somente o que falta ou está estruturalmente inválido,
            # preservando os valores válidos que já existiam.
            defaults_state = cls()

            # Localização atual. Nunca deixamos uma posição inválida impedir a abertura.
            if not isinstance(d.get('sector'), str) or d.get('sector') not in SECTORS:
                d['sector'] = 'landing'
            area_size = int(SECTORS[d['sector']]['size'])
            if (not isinstance(d.get('pos'), list) or len(d['pos']) != 2 or
                    any(type(v) is not int or v < 0 or v >= area_size for v in d['pos'])):
                d['pos'] = [SHIP[0], min(SHIP[1] + 1, area_size - 1)]
            visited = d.get('visited') if isinstance(d.get('visited'), list) else []
            d['visited'] = []
            for sid in visited:
                if sid in SECTORS and sid not in d['visited']:
                    d['visited'].append(sid)
            if d['sector'] not in d['visited']:
                d['visited'].append(d['sector'])

            # Sistemas da nave.
            raw_ship = d.get('ship_systems') if isinstance(d.get('ship_systems'), dict) else {}
            d['ship_systems'] = {}
            for sid, data in SHIP_SYSTEMS.items():
                value = raw_ship.get(sid, data.get('condition', 0))
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    value = int(data.get('condition', 0))
                d['ship_systems'][sid] = max(0, min(100, value))

            # Mundos: setores ausentes entram frescos; setores existentes preservam
            # somente inimigos que correspondem à origem atual daquele spawn.
            raw_worlds = d.get('worlds') if isinstance(d.get('worlds'), dict) else {}
            normalized_worlds = {}
            for sid, sector_data in SECTORS.items():
                base = fresh_enemies(sid)
                saved_enemies = raw_worlds.get(sid)
                if isinstance(saved_enemies, list):
                    for idx, saved in enumerate(saved_enemies[:len(base)]):
                        if not isinstance(saved, dict):
                            continue
                        expected = base[idx]
                        if saved.get('species') != expected.get('species') or saved.get('home') != expected.get('home'):
                            continue
                        if isinstance(saved.get('pos'), list) and len(saved['pos']) == 2 and all(type(v) is int for v in saved['pos']) and all(0 <= v < sector_data['size'] for v in saved['pos']):
                            base[idx]['pos'] = saved['pos']
                        if type(saved.get('dead')) is bool:
                            base[idx]['dead'] = saved['dead']
                        if cls._time(saved.get('ready')):
                            base[idx]['ready'] = saved['ready']
                        if saved.get('mission_id'):
                            base[idx]['mission_id'] = saved['mission_id']
                            base[idx]['mission_persistent'] = bool(saved.get('mission_persistent', True))
                normalized_worlds[sid] = base
            # Preserva setores desconhecidos para que uma build intermediária não
            # destrua conteúdo introduzido por uma versão futura. Eles continuam
            # invisíveis para a interface atual, mas permanecem no save.
            for sid, saved_enemies in raw_worlds.items():
                if sid not in normalized_worlds and isinstance(sid, str) and isinstance(saved_enemies, list):
                    normalized_worlds[sid] = saved_enemies
            d['worlds'] = normalized_worlds

            # Contadores de abates e estatísticas globais.
            raw_kills = d.get('kills') if isinstance(d.get('kills'), dict) else {}
            d['kills'] = {str(sid): (max(0, int(value)) if isinstance(value, (int, float)) else 0)
                          for sid, value in raw_kills.items() if isinstance(sid, str)}
            for sid in SPECIES:
                d['kills'].setdefault(sid, 0)
            raw_stats = d.get('statistics') if isinstance(d.get('statistics'), dict) else {}
            stats_defaults = fresh_statistics()
            for key in ('max_damage_dealt','max_damage_taken','missions_completed','missions_failed','battles_started','battles_won','battles_fled','critical_hits','kits_used','combat_challenges_completed','asteroid_encounters','asteroids_destroyed'):
                value = raw_stats.get(key, stats_defaults[key])
                try:
                    stats_defaults[key] = max(0, int(value))
                except (TypeError, ValueError):
                    stats_defaults[key] = 0
            raw_collectibles = raw_stats.get('collectibles') if isinstance(raw_stats.get('collectibles'), dict) else {}
            stats_defaults['collectibles'] = {str(k): max(0, int(v)) for k,v in raw_collectibles.items() if isinstance(k,str) and isinstance(v,(int,float))}
            raw_cards = raw_stats.get('cards_crafted') if isinstance(raw_stats.get('cards_crafted'), dict) else {}
            for key in stats_defaults['cards_crafted']:
                try: stats_defaults['cards_crafted'][key] = max(0, int(raw_cards.get(key, 0)))
                except (TypeError, ValueError): stats_defaults['cards_crafted'][key] = 0
            raw_paths = raw_stats.get('mission_paths') if isinstance(raw_stats.get('mission_paths'), dict) else {}
            for key in stats_defaults['mission_paths']:
                try: stats_defaults['mission_paths'][key] = max(0, int(raw_paths.get(key, 0)))
                except (TypeError, ValueError): stats_defaults['mission_paths'][key] = 0
            raw_stat_kills = raw_stats.get('kills') if isinstance(raw_stats.get('kills'), dict) else {}
            stats_defaults['kills'] = {str(k): max(0, int(v)) for k, v in raw_stat_kills.items()
                                       if isinstance(k, str) and isinstance(v, (int, float))}
            for sid in SPECIES:
                stats_defaults['kills'].setdefault(sid, d['kills'].get(sid, 0))
            raw_bosses_def = raw_stats.get('bosses_defeated') if isinstance(raw_stats.get('bosses_defeated'), dict) else {}
            raw_bosses_rem = raw_stats.get('boss_rematches') if isinstance(raw_stats.get('boss_rematches'), dict) else {}
            stats_defaults['bosses_defeated'] = {str(k): max(0,int(v)) for k,v in raw_bosses_def.items() if isinstance(k,str) and isinstance(v,(int,float))}
            stats_defaults['boss_rematches'] = {str(k): max(0,int(v)) for k,v in raw_bosses_rem.items() if isinstance(k,str) and isinstance(v,(int,float))}
            d['statistics'] = stats_defaults

            # Missões: preservamos cada estado existente e completamos somente entradas ausentes.
            raw_missions = d.get('missions') if isinstance(d.get('missions'), dict) else {}
            mission_defaults = fresh_missions()
            for mid, mdefault in mission_defaults.items():
                current = raw_missions.get(mid)
                if isinstance(current, dict):
                    merged = dict(mdefault); merged.update(current); raw_missions[mid] = merged
                else:
                    raw_missions[mid] = dict(mdefault)
            d['missions'] = raw_missions

            # Catálogos dinâmicos: IDs desconhecidos são preservados como texto.
            # A interface atual só renderiza os itens que ela conhece, mas o save
            # não perde descobertas quando uma build intermediária é usada.
            d['known_cards'] = list(dict.fromkeys(c for c in (d.get('known_cards') or []) if isinstance(c, str)))
            d['bestiary_known'] = list(dict.fromkeys(c for c in (d.get('bestiary_known') or []) if isinstance(c, str)))
            d['bestiary_scanned'] = list(dict.fromkeys(c for c in (d.get('bestiary_scanned') or []) if isinstance(c, str)))

            # Planetas conhecidos e planeta selecionado. IDs futuros são preservados;
            # esta build simplesmente não os apresenta até existir o catálogo correspondente.
            route_ids = {r['id'] for r in STELLAR_ROUTES}
            known = [pid for pid in (d.get('known_planets') or []) if isinstance(pid, str)]
            if 'veyra' not in known:
                known.insert(0, 'veyra')
            d['known_planets'] = list(dict.fromkeys(known))
            selected = d.get('selected_planet')
            d['selected_planet'] = selected if isinstance(selected, str) else 'veyra'
            raw_civs = d.get('known_civilizations_by_planet') if isinstance(d.get('known_civilizations_by_planet'), dict) else {}
            d['known_civilizations_by_planet'] = {str(k): list(dict.fromkeys(v for v in vals if isinstance(v, str)))
                                                  for k, vals in raw_civs.items() if isinstance(k, str) and isinstance(vals, list)}
            for route in STELLAR_ROUTES:
                rid = route['id']
                if rid not in d['known_civilizations_by_planet']:
                    d['known_civilizations_by_planet'][rid] = list(route.get('initial_known_civilizations', []))

            # AURORA/elmo e módulos permanecem em estados válidos mesmo em saves antigos.
            d['aurora_level'] = max(0, min(3, int(d.get('aurora_level', 0)))) if isinstance(d.get('aurora_level', 0), (int,float)) else 0
            try:
                d['helmet_generation'] = max(0, min(3, int(d.get('helmet_generation', 1 if d.get('helmet_owned') else 0))))
            except (TypeError, ValueError):
                d['helmet_generation'] = 1 if d.get('helmet_owned') else 0
            d['helmet_owned'] = bool(d.get('helmet_owned', False))
            d['helmet_equipped'] = bool(d.get('helmet_equipped', False)) or d['helmet_owned']
            d['helmet_design'] = d.get('helmet_design') if d.get('helmet_design') in HELMET_DESIGN_ORDER else ('tactical' if d['helmet_owned'] else None)
            d['locomotion_generation'] = 1 if int(d.get('locomotion_generation', 0) or 0) > 0 else 0
            d['locomotion_equipped'] = bool(d.get('locomotion_equipped', False))

            # Valores básicos: preenchemos apenas o que estiver ausente.
            # Valores existentes continuam sujeitos ao validador; assim, um save
            # realmente corrompido não é silenciosamente convertido em outro estado.
            raw_memory_owned = d.get('memory_owned')
            d['memory_owned'] = dict(defaults_state.memory_owned) | (raw_memory_owned if isinstance(raw_memory_owned, dict) else {})
            raw_memory_slots = d.get('memory_slots')
            if isinstance(raw_memory_slots, list):
                d['memory_slots'] = (list(raw_memory_slots) + [None] * TOTAL_MEMORY_SLOTS)[:TOTAL_MEMORY_SLOTS]
            else:
                d['memory_slots'] = list(defaults_state.memory_slots)
            if not isinstance(d.get('chest_generation'), int) or d['chest_generation'] not in (1, 2, 3):
                d['chest_generation'] = defaults_state.chest_generation
            if not isinstance(d.get('gauntlet_generation'), int) or d['gauntlet_generation'] < 1:
                d['gauntlet_generation'] = defaults_state.gauntlet_generation
            if not isinstance(d.get('gauntlet_nexus_installed'), bool):
                d['gauntlet_nexus_installed'] = defaults_state.gauntlet_nexus_installed
            if not isinstance(d.get('gauntlet_nexus_xp'), int) or d['gauntlet_nexus_xp'] < 0:
                d['gauntlet_nexus_xp'] = defaults_state.gauntlet_nexus_xp
            if not isinstance(d.get('gauntlet_nexus_level'), int) or not (1 <= d['gauntlet_nexus_level'] <= 20):
                d['gauntlet_nexus_level'] = defaults_state.gauntlet_nexus_level
            if not isinstance(d.get('gauntlet_nexus_points'), int) or d['gauntlet_nexus_points'] < 0:
                d['gauntlet_nexus_points'] = defaults_state.gauntlet_nexus_points
            if not isinstance(d.get('gauntlet_nexus_nodes'), list):
                d['gauntlet_nexus_nodes'] = list(defaults_state.gauntlet_nexus_nodes)
            if not isinstance(d.get('gauntlet_nexus_progression_revision'), int) or d['gauntlet_nexus_progression_revision'] < 8:
                d['gauntlet_nexus_progression_revision'] = max(8, defaults_state.gauntlet_nexus_progression_revision)
            if not isinstance(d.get('gauntlet_nexus_hack_alert_capacity_bonus'), int) or d['gauntlet_nexus_hack_alert_capacity_bonus'] < 0:
                d['gauntlet_nexus_hack_alert_capacity_bonus'] = defaults_state.gauntlet_nexus_hack_alert_capacity_bonus
            if not isinstance(d.get('gauntlet_nexus_hack_diagonal'), bool):
                d['gauntlet_nexus_hack_diagonal'] = defaults_state.gauntlet_nexus_hack_diagonal
            if not isinstance(d.get('gauntlet_nexus_hack_mask_first_firewall'), bool):
                d['gauntlet_nexus_hack_mask_first_firewall'] = defaults_state.gauntlet_nexus_hack_mask_first_firewall
            if not isinstance(d.get('memory'), (int, float)):
                d['memory'] = defaults_state.memory
            else:
                d['memory'] = int(d['memory'])

            # Carregamento resiliente: a estrutura persistida é tratada como dados de
            # campanha, não como um contrato rígido que pode invalidar todo o progresso
            # quando uma versão acrescenta campos, mapas, criaturas ou missões.
            defaults_state = cls()

            # Localização.
            if not isinstance(d.get('sector'), str) or d.get('sector') not in SECTORS:
                d['sector'] = 'landing'
            area_size = int(SECTORS[d['sector']].get('size', SIZE))
            pos = d.get('pos')
            if not isinstance(pos, list) or len(pos) != 2 or any(type(v) is not int for v in pos):
                pos = list(SHIP)
            d['pos'] = [max(0, min(area_size - 1, int(pos[0]))), max(0, min(area_size - 1, int(pos[1])))]
            raw_visited = d.get('visited') if isinstance(d.get('visited'), list) else []
            d['visited'] = list(dict.fromkeys(v for v in raw_visited if isinstance(v, str) and (v in SECTORS or v.startswith(tuple(r['id'] + '_' for r in STELLAR_ROUTES)))))
            if d['sector'] not in d['visited']:
                d['visited'].append(d['sector'])
            if 'landing' not in d['visited']:
                d['visited'].append('landing')

            # Mundos: current sectors são reconstruídos a partir do catálogo,
            # preservando posições/respawn válidos. Setores desconhecidos permanecem
            # no save para evitar perda de dados ao voltar de uma versão futura.
            raw_worlds = d.get('worlds') if isinstance(d.get('worlds'), dict) else {}
            normalized_worlds = {}
            for sid, sector_data in SECTORS.items():
                base = fresh_enemies(sid)
                saved_enemies = raw_worlds.get(sid)
                if isinstance(saved_enemies, list):
                    for idx, saved in enumerate(saved_enemies[:len(base)]):
                        if not isinstance(saved, dict):
                            continue
                        expected = base[idx]
                        if saved.get('species') != expected.get('species') or saved.get('home') != expected.get('home'):
                            continue
                        pos_e = saved.get('pos')
                        if isinstance(pos_e, list) and len(pos_e) == 2 and all(type(v) is int for v in pos_e):
                            base[idx]['pos'] = [max(0, min(int(sector_data['size']) - 1, pos_e[0])), max(0, min(int(sector_data['size']) - 1, pos_e[1]))]
                        if type(saved.get('dead')) is bool:
                            base[idx]['dead'] = saved['dead']
                        if cls._time(saved.get('ready')):
                            base[idx]['ready'] = saved['ready']
                        if isinstance(saved.get('mission_id'), str):
                            base[idx]['mission_id'] = saved['mission_id']
                            base[idx]['mission_persistent'] = bool(saved.get('mission_persistent', True))
                normalized_worlds[sid] = base
            for sid, saved_enemies in raw_worlds.items():
                if sid not in normalized_worlds and isinstance(sid, str) and isinstance(saved_enemies, list):
                    normalized_worlds[sid] = saved_enemies
            d['worlds'] = normalized_worlds

            # Sistemas da nave: completa os atuais e preserva chaves futuras.
            raw_ship = d.get('ship_systems') if isinstance(d.get('ship_systems'), dict) else {}
            ship_norm = dict(raw_ship)
            for sid, data in SHIP_SYSTEMS.items():
                try:
                    value = int(raw_ship.get(sid, data.get('condition', 0)))
                except (TypeError, ValueError):
                    value = int(data.get('condition', 0))
                ship_norm[sid] = max(0, min(100, value))
            d['ship_systems'] = ship_norm

            # Inventário e contadores.
            raw_inventory = d.get('inventory') if isinstance(d.get('inventory'), dict) else {}
            d['inventory'] = {str(k): max(0, int(v)) for k, v in raw_inventory.items() if isinstance(k, str) and isinstance(v, (int, float))}
            raw_kills = d.get('kills') if isinstance(d.get('kills'), dict) else {}
            d['kills'] = {sid: max(0, int(raw_kills.get(sid, 0))) if isinstance(raw_kills.get(sid, 0), (int, float)) else 0 for sid in SPECIES}
            d['collected_nodes'] = list(dict.fromkeys(v for v in (d.get('collected_nodes') or []) if isinstance(v, str) and v in ALL_NODE_IDS))

            # Stats: defaults + dados existentes, sem exigir que novas categorias sejam
            # conhecidas pela build atual.
            raw_stats = d.get('statistics') if isinstance(d.get('statistics'), dict) else {}
            stats = dict(fresh_statistics()); stats.update(raw_stats)
            for key in ('max_damage_dealt','max_damage_taken','missions_completed','missions_failed','battles_started','battles_won','battles_fled','critical_hits','kits_used','combat_challenges_completed','asteroid_encounters','asteroids_destroyed'):
                try: stats[key] = max(0, int(raw_stats.get(key, stats[key])))
                except (TypeError, ValueError): stats[key] = 0
            raw_collect = raw_stats.get('collectibles') if isinstance(raw_stats.get('collectibles'), dict) else {}
            stats['collectibles'] = {str(k): max(0, int(v)) for k, v in raw_collect.items() if isinstance(k, str) and isinstance(v, (int, float))}
            raw_cards_stats = raw_stats.get('cards_crafted') if isinstance(raw_stats.get('cards_crafted'), dict) else {}
            cards_stats = dict(fresh_statistics()['cards_crafted']); cards_stats.update(raw_cards_stats); stats['cards_crafted'] = cards_stats
            raw_paths = raw_stats.get('mission_paths') if isinstance(raw_stats.get('mission_paths'), dict) else {}
            paths_stats = dict(fresh_statistics()['mission_paths']); paths_stats.update(raw_paths); stats['mission_paths'] = paths_stats
            raw_stat_kills = raw_stats.get('kills') if isinstance(raw_stats.get('kills'), dict) else {}
            # Estatísticas futuras: preserva IDs de criaturas que a build atual ainda não
            # conhece, sem deixar de completar as espécies atuais.
            stats_kills = dict(fresh_statistics()['kills'])
            for sid in SPECIES:
                value = raw_stat_kills.get(sid, d['kills'].get(sid, 0))
                if isinstance(value, (int, float)):
                    stats_kills[sid] = max(0, int(value))
            for sid, value in raw_stat_kills.items():
                if isinstance(sid, str) and sid not in stats_kills and isinstance(value, (int, float)):
                    stats_kills[sid] = max(0, int(value))
            stats['kills'] = stats_kills
            for bucket in ('bosses_defeated','boss_rematches'):
                raw_bucket = raw_stats.get(bucket) if isinstance(raw_stats.get(bucket), dict) else {}
                stats[bucket] = {str(k): max(0, int(v)) for k,v in raw_bucket.items() if isinstance(k, str) and isinstance(v,(int,float))}
            d['statistics'] = stats

            # Missões: completa apenas o que a build conhece e preserva missões futuras.
            raw_missions = d.get('missions') if isinstance(d.get('missions'), dict) else {}
            mission_defaults = fresh_missions()
            for mid, mdefault in mission_defaults.items():
                current = raw_missions.get(mid)
                if isinstance(current, dict):
                    merged = dict(mdefault); merged.update(current); raw_missions[mid] = merged
                else:
                    raw_missions[mid] = dict(mdefault)
            d['missions'] = raw_missions

            # Diário e sociedade. Mantemos entradas válidas e completamos novos campos.
            fresh_j = fresh_journal()
            journal = d.get('journal') if isinstance(d.get('journal'), dict) else {}
            merged_j = dict(fresh_j); merged_j.update(journal)
            entries = journal.get('entries') if isinstance(journal.get('entries'), list) else fresh_j['entries']
            merged_j['entries'] = [e for e in entries if isinstance(e, dict) and isinstance(e.get('id'), str)] or list(fresh_j['entries'])
            merged_j['seen'] = list(dict.fromkeys(v for v in (journal.get('seen') or []) if isinstance(v, str)))
            objectives = dict(fresh_j.get('objectives', {})); existing_obj = journal.get('objectives') if isinstance(journal.get('objectives'), dict) else {}
            objectives.update({k:v for k,v in existing_obj.items() if isinstance(k,str) and isinstance(v,dict)})
            for oid, obj in list(objectives.items()):
                if not isinstance(obj, dict): objectives[oid] = {'status':'locked','progress':0}; continue
                status = obj.get('status', 'locked')
                if status not in ('locked','active','completed'): status = 'locked'
                try: progress = max(0, int(obj.get('progress', 0)))
                except (TypeError, ValueError): progress = 0
                obj['status'], obj['progress'] = status, progress
            merged_j['objectives'] = objectives; d['journal'] = merged_j
            society_default = fresh_society(); society = d.get('society') if isinstance(d.get('society'), dict) else {}
            society_default.update(society)
            for key in ('discovered_settlements','seen_npcs'):
                vals = society.get(key); society_default[key] = list(dict.fromkeys(v for v in (vals if isinstance(vals,list) else []) if isinstance(v,str)))
            society_default['first_contact'] = bool(society.get('first_contact', False)); d['society'] = society_default

            # Planetas/galáxias: somente o catálogo conhecido pela versão atual é
            # selecionável, mas chaves adicionais de renome são preservadas.
            route_ids = {r['id'] for r in STELLAR_ROUTES}
            known_raw = d.get('known_planets') if isinstance(d.get('known_planets'), list) else []
            d['known_planets'] = list(dict.fromkeys(pid for pid in known_raw if isinstance(pid, str)))
            if not d.get('dobra_core_installed', False):
                local_ids = set(GALAXY_ROUTE_IDS.get(GALAXY_ID, ()))
                d['known_planets'] = [pid for pid in d['known_planets'] if pid in local_ids]
            if 'veyra' not in d['known_planets']: d['known_planets'].insert(0, 'veyra')
            d['selected_planet'] = d.get('selected_planet') if isinstance(d.get('selected_planet'), str) else 'veyra'
            raw_civs = d.get('known_civilizations_by_planet') if isinstance(d.get('known_civilizations_by_planet'), dict) else {}
            civs_norm = dict(raw_civs)
            for route in STELLAR_ROUTES:
                rid=route['id']; vals=raw_civs.get(rid, route.get('initial_known_civilizations', [])); civs_norm[rid]=list(dict.fromkeys(v for v in (vals if isinstance(vals,list) else []) if isinstance(v,str)))
            d['known_civilizations_by_planet']=civs_norm
            for key in ('renown_by_faction','renown_planets','renown_galaxies'):
                raw = d.get(key) if isinstance(d.get(key), dict) else {}
                d[key] = {str(k): max(0, int(v)) for k,v in raw.items() if isinstance(k,str) and isinstance(v,(int,float))}
            for fid in FACTIONS: d['renown_by_faction'].setdefault(fid, 0)
            for route in STELLAR_ROUTES: d['renown_planets'].setdefault(route['id'], 0)
            for gid in GALAXIES: d['renown_galaxies'].setdefault(gid, 0)
            try: d['renown'] = max(0, min(100, int(d.get('renown', 50))))
            except (TypeError, ValueError): d['renown'] = 50
            d['renown_events'] = d.get('renown_events') if isinstance(d.get('renown_events'), list) else []
            d['renown_claimed'] = list(dict.fromkeys(v for v in (d.get('renown_claimed') or []) if isinstance(v,str)))

            # Equipamentos.
            d['aurora_level'] = max(0, min(3, int(d.get('aurora_level', 0)))) if isinstance(d.get('aurora_level', 0),(int,float)) else 0
            d['helmet_owned'] = bool(d.get('helmet_owned', False)); d['helmet_equipped'] = bool(d.get('helmet_equipped', False)) or d['helmet_owned']
            try:
                d['helmet_generation'] = max(0, min(3, int(d.get('helmet_generation', 1 if d['helmet_owned'] else 0))))
            except (TypeError, ValueError):
                d['helmet_generation'] = 1 if d['helmet_owned'] else 0
            d['helmet_design'] = d.get('helmet_design') if d.get('helmet_design') in HELMET_DESIGN_ORDER else ('tactical' if d['helmet_owned'] else None)
            try: d['chest_generation'] = int(d.get('chest_generation', 1))
            except (TypeError, ValueError): d['chest_generation'] = 1
            d['chest_generation'] = max(1, min(3,d['chest_generation']))
            try: d['gauntlet_generation'] = max(1,int(d.get('gauntlet_generation',1)))
            except (TypeError, ValueError): d['gauntlet_generation']=1
            d['locomotion_generation'] = max(0, int(d.get('locomotion_generation',0))) if isinstance(d.get('locomotion_generation',0),(int,float)) else 0
            d['locomotion_equipped'] = bool(d.get('locomotion_equipped',False))

            # Idioma de Nahr é separado do Avari e migra de forma segura de saves anteriores.
            try: d['nahr_language_progress'] = max(0, min(3, int(d.get('nahr_language_progress', 0))))
            except (TypeError, ValueError): d['nahr_language_progress'] = 0
            d['nahr_language_mastered'] = bool(d.get('nahr_language_mastered', False))
            raw_langs = d.get('language_mastery') if isinstance(d.get('language_mastery'), dict) else {}
            d['language_mastery'] = {str(k): bool(v) for k,v in raw_langs.items() if isinstance(k, str)}
            d['language_mastery'].setdefault('avarin', bool(d.get('language_mastered', False)))
            d['language_mastery'].setdefault('nahr_shadows', bool(d.get('nahr_language_mastered', False)))
            d['pending_language_civilization'] = d.get('pending_language_civilization') if d.get('pending_language_civilization') in CIVILIZATIONS else None
            d['pending_language_npc_id'] = d.get('pending_language_npc_id') if isinstance(d.get('pending_language_npc_id'), str) else None
            d['selected_galaxy_id'] = d.get('selected_galaxy_id') if d.get('selected_galaxy_id') in GALAXIES else GALAXY_ID
            # Domínios: migração segura de saves anteriores a 0.6.9.
            raw_domain_xp = d.get('domain_xp') if isinstance(d.get('domain_xp'), dict) else {}
            raw_domain_levels = d.get('domain_levels') if isinstance(d.get('domain_levels'), dict) else {}
            d['domain_xp'] = {element: max(0, min(DOMAIN_LEVEL_XP[DOMAIN_LEVEL_MAX], int(raw_domain_xp.get(element, 0) or 0))) for element in DOMAIN_ELEMENTS}
            d['domain_levels'] = {element: max(0, min(DOMAIN_LEVEL_MAX, self_level if isinstance((self_level := raw_domain_levels.get(element, 0)), (int, float)) else 0)) for element in DOMAIN_ELEMENTS}
            for element in DOMAIN_ELEMENTS:
                calculated = 0
                for _level, _threshold in sorted(DOMAIN_LEVEL_XP.items()):
                    if d['domain_xp'][element] >= _threshold: calculated = _level
                    else: break
                d['domain_levels'][element] = calculated
            d['nahr_ry_contacted'] = bool(d.get('nahr_ry_contacted', False))
            # Memória, NEXUS e flags simples.
            raw_owned=d.get('memory_owned') if isinstance(d.get('memory_owned'),dict) else {}
            mo=dict(defaults_state.memory_owned)
            for key in mo:
                try: mo[key]=max(0,int(raw_owned.get(key,mo[key])))
                except (TypeError,ValueError): pass
            d['memory_owned']=mo
            raw_slots=d.get('memory_slots') if isinstance(d.get('memory_slots'),list) else list(defaults_state.memory_slots)
            valid_slots=[]
            for value in raw_slots[:TOTAL_MEMORY_SLOTS]: valid_slots.append(value if value in MEMORY_MODULES else None)
            d['memory_slots']=(valid_slots+[None]*TOTAL_MEMORY_SLOTS)[:TOTAL_MEMORY_SLOTS]
            for key, default in (('gauntlet_nexus_installed',False),('gauntlet_nexus_hack_diagonal',False),('gauntlet_nexus_hack_mask_first_firewall',False),('inside_ship',False),('language_mastered',False),('simulator_unlocked',False),('simulator_built',False),('water_purifier_built',False),('scan_unlocked',False),('communication_revealed',False),('dobra_core_installed',False),('ship_laser_project_unlocked',False),('ship_laser_installed',False)):
                d[key]=bool(d.get(key,default))
            try: d['gauntlet_nexus_xp']=max(0,int(d.get('gauntlet_nexus_xp',0)))
            except (TypeError,ValueError): d['gauntlet_nexus_xp']=0
            try: d['gauntlet_nexus_level']=max(1,min(50,int(d.get('gauntlet_nexus_level',1))))
            except (TypeError,ValueError): d['gauntlet_nexus_level']=1
            d['gauntlet_nexus_points']=0
            nodes=d.get('gauntlet_nexus_nodes') if isinstance(d.get('gauntlet_nexus_nodes'),list) else []
            d['gauntlet_nexus_nodes']=list(dict.fromkeys(v for v in nodes if isinstance(v,str) and v in NEXUS_NODES))
            try: d['gauntlet_nexus_progression_revision']=max(8,int(d.get('gauntlet_nexus_progression_revision',8)))
            except (TypeError,ValueError): d['gauntlet_nexus_progression_revision']=8
            try: d['gauntlet_nexus_hack_alert_capacity_bonus']=max(0,int(d.get('gauntlet_nexus_hack_alert_capacity_bonus',0)))
            except (TypeError,ValueError): d['gauntlet_nexus_hack_alert_capacity_bonus']=0
            if isinstance(d.get('ship_pos'),list) and len(d['ship_pos'])==2 and all(type(v) is int for v in d['ship_pos']):
                d['ship_pos']=[max(0,min(11,d['ship_pos'][0])),max(0,min(8,d['ship_pos'][1]))]
            else: d['ship_pos']=list(SHIP_INTERIOR['start'])

            # HP/memória e demais primitivos.
            try: d['hp']=max(0,min(MAX_HP + int(AURORA_UPGRADES.get(d['aurora_level'],{}).get('hp',0)),int(d.get('hp',MAX_HP))))
            except (TypeError,ValueError): d['hp']=MAX_HP
            max_mem=sum(MEMORY_MODULES[m]['capacity'] for m in d['memory_slots'] if m in MEMORY_MODULES)
            try: d['memory']=max(0,min(max_mem,int(d.get('memory',max_mem))))
            except (TypeError,ValueError): d['memory']=max_mem
            try: d['time']=max(0.0,float(d.get('time',0.0)))
            except (TypeError,ValueError): d['time']=0.0
            d['inside_ship']=bool(d.get('inside_ship',False))
            d['gauntlet_stones']=(list(d.get('gauntlet_stones') or [])+[None]*6)[:6]
            d['gauntlet_stones']=[v if v is None or isinstance(v,str) else None for v in d['gauntlet_stones']]

            # Inconsistências conhecidas de equipamento continuam sendo bloqueadas;
            # campos ausentes de versões futuras continuam sendo preenchidos.
            raw_owned_check = d.get('memory_owned') if isinstance(d.get('memory_owned'), dict) else {}
            raw_slots_check = d.get('memory_slots') if isinstance(d.get('memory_slots'), list) else []
            if raw_slots_check:
                counts = {}
                for module in raw_slots_check:
                    if module is None:
                        continue
                    if module not in MEMORY_MODULES:
                        # Um módulo totalmente novo pode existir em um save futuro;
                        # ele não pode ser interpretado pela build atual.
                        continue
                    counts[module] = counts.get(module, 0) + 1
                for module, used in counts.items():
                    try:
                        owned = int(raw_owned_check.get(module, 0))
                    except (TypeError, ValueError):
                        owned = 0
                    if used > owned:
                        raise ValueError('Save inválido: módulos equipados excedem o estoque.')
                chest_check = int(d.get('chest_generation', 1)) if isinstance(d.get('chest_generation', 1), (int, float)) else 1
                if 'advanced' in raw_slots_check and chest_check < 3:
                    raise ValueError('Save inválido: módulo avançado incompatível com o Peitoral atual.')

            # Catálogos: preservamos IDs futuros como texto; a interface atual só exibe
            # aqueles que existem na build.
            d['known_cards']=list(dict.fromkeys(v for v in (d.get('known_cards') or []) if isinstance(v,str)))
            d['bestiary_known']=list(dict.fromkeys(v for v in (d.get('bestiary_known') or []) if isinstance(v,str)))
            d['bestiary_scanned']=list(dict.fromkeys(v for v in (d.get('bestiary_scanned') or []) if isinstance(v,str)))
            d['unique_rewards']=list(dict.fromkeys(v for v in (d.get('unique_rewards') or []) if isinstance(v,str)))
            d['achievement_alerts']=[v for v in (d.get('achievement_alerts') or []) if isinstance(v,dict)]
            achievements = d.get('achievements') if isinstance(d.get('achievements'),dict) else {}
            achievement_defaults=fresh_achievements(); achievement_defaults.update(achievements)
            for aid, entry in list(achievement_defaults.items()):
                if not isinstance(entry,dict): achievement_defaults[aid]={'unlocked':False,'claimed':False}; continue
                entry['unlocked']=bool(entry.get('unlocked',False)); entry['claimed']=bool(entry.get('claimed',False))
            d['achievements']=achievement_defaults
            d['bosses'] = d.get('bosses') if isinstance(d.get('bosses'),dict) else {}
            for bid in BOSSES:
                entry=d['bosses'].get(bid) if isinstance(d['bosses'].get(bid),dict) else {}
                d['bosses'][bid]={'defeated':bool(entry.get('defeated',False)),'virtual_defeats':max(0,int(entry.get('virtual_defeats',0))) if isinstance(entry.get('virtual_defeats',0),(int,float)) else 0}

            d['language_mastery'] = d.get('language_mastery') if isinstance(d.get('language_mastery'), dict) else {}
            d['language_mastery'].setdefault('avarin', bool(d.get('language_mastered', False)))
            d['language_mastery'].setdefault('nahr_shadows', bool(d.get('nahr_language_mastered', False)))
            d['pending_language_civilization'] = d.get('pending_language_civilization') if d.get('pending_language_civilization') in CIVILIZATIONS else None
            d['pending_language_npc_id'] = d.get('pending_language_npc_id') if isinstance(d.get('pending_language_npc_id'), str) else None
            d['dobra_core_installed'] = bool(d.get('dobra_core_installed', False))
            d['ship_laser_project_unlocked'] = bool(d.get('ship_laser_project_unlocked', False))
            d['ship_laser_installed'] = bool(d.get('ship_laser_installed', False))
            try: d['travel_damage'] = max(0, min(6, int(d.get('travel_damage', 0))))
            except (TypeError, ValueError): d['travel_damage'] = 0
            if isinstance(d.get('inventory'), dict):
                d['inventory'].pop('Removedor de Aprimoramento', None)
            d['selected_galaxy_id'] = d.get('selected_galaxy_id') if d.get('selected_galaxy_id') in GALAXIES else GALAXY_ID

            state = cls()
            for key in ('pos', 'hp', 'memory', 'memory_owned', 'memory_slots', 'inventory', 'aurora_level', 'crafted', 'slots', 'kills', 'time', 'collected_nodes', 'worlds', 'sector', 'visited', 'chest_generation', 'gauntlet_generation', 'helmet_generation', 'helmet_owned', 'helmet_equipped', 'helmet_design', 'locomotion_generation', 'locomotion_equipped', 'journal', 'society', 'ship_systems', 'combat_stats', 'gauntlet_nexus_installed', 'gauntlet_nexus_xp', 'gauntlet_nexus_level', 'gauntlet_nexus_points', 'gauntlet_nexus_nodes', 'gauntlet_nexus_progression_revision', 'gauntlet_nexus_drop_bonus_pct', 'gauntlet_nexus_advantage_bonus_pct', 'gauntlet_nexus_vampirism_pct', 'gauntlet_nexus_hack_alert_capacity_bonus', 'gauntlet_nexus_hack_diagonal', 'gauntlet_nexus_hack_mask_first_firewall', 'domain_xp', 'domain_levels', 'inside_ship', 'ship_pos', 'language_progress', 'language_mastered', 'language_mastery', 'nahr_language_progress', 'nahr_language_mastered', 'nahr_ry_contacted', 'has_left_veyra', 'pending_language_civilization', 'pending_language_npc_id', 'dobra_core_installed', 'ship_laser_project_unlocked', 'ship_laser_installed', 'travel_damage', 'selected_galaxy_id', 'missions', 'renown', 'renown_events', 'renown_by_faction', 'renown_planets', 'renown_galaxies', 'renown_claimed', 'known_planets', 'selected_planet', 'known_civilizations_by_planet', 'statistics', 'achievements', 'unique_rewards', 'achievement_reward_revision', 'bosses', 'simulator_unlocked', 'simulator_built', 'water_purifier_built', 'scan_unlocked', 'achievement_alerts', 'known_cards', 'bestiary_known', 'bestiary_scanned', 'gauntlet_stones', 'opening_dialogue_pending', 'respawn_tank_built', 'essence_storage', 'game_over'):
                setattr(state, key, d[key])
            state.unique_cards = d.get('unique_cards', {})
            state.gauntlet_special_slot = d.get('gauntlet_special_slot')
            state.communication_revealed = bool(d.get('communication_revealed', False))
            state.ensure_exploration_mission()
            state.ensure_ry_investigation_mission()
            state.ensure_laser_project_mission()
            state.ensure_travel_repair_mission()
            state._sync_galaxy_boss_missions()
            state.refresh_journal(refresh_achievement_state=False)
            if version < 56:
                state.opening_dialogue_pending = False
                if state.respawn_tank_built:
                    state.missions.setdefault('respawn_tank', {'status':'completed','progress':1,'reward_claimed':True})['status'] = 'completed'
                    state.set_objective('respawn_tank', 'completed', 1)
                else:
                    state.missions.setdefault('respawn_tank', {'status':'locked','progress':0,'reward_claimed':False})
                    if state.missions['respawn_tank'].get('status') == 'locked':
                        state.missions['respawn_tank']['status'] = 'active'
                        state.set_objective('respawn_tank', 'active', 0)
            # Saves 0.5.5/format 56 já possuem Tanque e Armazenador, mas nunca
            # devem reabrir a introdução ao serem carregados.
            if version < 58:
                state.opening_dialogue_pending = False
            if version < 72:
                message = 'Save convertido para 0.7.7. Progresso preservado e nova interface de combate habilitada.'
            elif version > 72:
                message = 'Save de versão futura carregado com compatibilidade segura.'
            else:
                message = 'Campanha 0.7.7 carregada.'
            return state, message
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            state = cls()
            state.save_blocked = True
            return state, 'Save inválido ou incompatível. Arquivo preservado; salvamento bloqueado. Consulte o README.'

    @staticmethod
    def _require(condition, field):
        if not condition:
            raise ValueError('Save inválido: ' + field)

    @staticmethod
    def _time(value):
        return type(value) in (int, float) and 0 <= value < 1e12


def load_campaign(directory, legacy_directories=None, current_filename='save.json'):
    """Carrega o save persistente e migra formatos antigos uma única vez.

    O save atual fica em um nome estável (`save.json`) para que versões futuras
    sobrescrevam o mesmo arquivo, em vez de criar um save por versão.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    current = directory / current_filename
    if current.exists():
        state, message = State.load(current)
        if not state.save_blocked:
            return state, message
        # Se o save principal estiver corrompido/incompatível, tenta o backup
        # antes de desistir, preservando o arquivo principal para inspeção.
        backup = directory / 'bkp.json'
        if backup.exists():
            backup_state, backup_message = State.load(backup)
            if not backup_state.save_blocked:
                return backup_state, 'Save principal inválido; backup bkp.json carregado. ' + backup_message
        return state, message

    legacy_dirs = [directory]
    for legacy in legacy_directories or ():
        legacy_path = Path(legacy)
        if legacy_path not in legacy_dirs:
            legacy_dirs.append(legacy_path)
    legacy_names = ('save.json', 'bkp.json', 'save_v049.json', 'save_v048.json', 'save_v047.json', 'save_v046.json', 'save_v043.json',
                    'save_v042.json', 'save_v041.json', 'save_v04.json', 'save_v03.json', 'save_v02.json')
    previous = next((d / name for d in legacy_dirs for name in legacy_names if (d / name).exists()), None)
    if previous is None:
        return State.load(current)

    state, message = State.load(previous)
    if not state.save_blocked:
        try:
            state.save(current, refresh=False)
            message += f' Progresso migrado para o save persistente: {current.name}.'
        except OSError:
            message += ' Não foi possível gravar o novo save no diretório persistente.'
    return state, message
