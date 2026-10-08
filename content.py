"""Números e conteúdo de Cinzas de Órion 0.7.2."""
VERSION = '0.7.2'
SIZE = 21
MAX_HP = 36

PLANET = {
    'id': 'veyra',
    'name': 'Veyra',
    'description': 'Um mundo árido de dunas, pedra exposta e antigas redes de captação subterrânea.',
}

GALAXY_ID = 'local'
GALAXY_NAME = 'Galáxia Nárion'

STELLAR_ROUTES = [
    dict(id='veyra', name='Veyra', galaxy=GALAXY_ID, known=True, pos=(170,300), atmosphere='Respirável / Árida', temperature='31 °C', moons=2, initial_known_civilizations=['Avarin'], landing_sector='landing'),
    dict(id='orionis', name='Orionis', galaxy=GALAXY_ID, known=False, pos=(310,210), atmosphere='Densa / Ácida', temperature='118 °C', moons=1, initial_known_civilizations=[], landing_sector='orionis_landing'),
    dict(id='kael', name='Kael', galaxy=GALAXY_ID, known=False, pos=(470,275), atmosphere='Respirável / Fria', temperature='-18 °C', moons=0, initial_known_civilizations=[], landing_sector='kael_landing'),
    dict(id='nahr', name='Nahr', galaxy=GALAXY_ID, known=False, pos=(620,365), atmosphere='Irrespirável / Seca', temperature='54 °C', moons=3, initial_known_civilizations=[], landing_sector='nahr_landing'),
    dict(id='elyra', name='Elyra', galaxy=GALAXY_ID, known=False, pos=(390,455), atmosphere='Respirável / Densa', temperature='12 °C', moons=2, initial_known_civilizations=[], landing_sector='elyra_landing'),
]
# Catálogo base. A 0.6.0 acrescenta Vharos e Meridion após a instalação do Núcleo de Dobra.
GALAXIES = {GALAXY_ID: dict(name=GALAXY_NAME)}
# Arenas dos bosses da primeira galáxia. A arena de Nahr começa vazia e
# somente revela RY quando a investigação de seu mapa for concluída.
BOSS_ARENAS = {
    'veyra': 'salt_basin',
    'orionis': 'orionis_thermal_caves',
    'kael': 'kael_frost_caverns',
    'nahr': 'nahr_ry_void',
    'elyra': 'elyra_cloud_caverns',
}

AURORA_UPGRADES = {
    1: dict(name='AURORA Plus', hp=20, attack=2, crit_rate=0.0, crit_damage=0.02,
            recipe={'Sucata':60, 'Núcleo':8, 'Placa':12, 'Carapaça':10}, available=True),
    2: dict(name='AURORA Nova', hp=40, attack=4, crit_rate=1.0, crit_damage=0.04,
            recipe={'Cristal estelar':6, 'Matriz fotônica':4, 'Núcleo de ressonância':6, 'Liga meteórica':20}, available=False),
    3: dict(name='AURORA Ultimate', hp=100, attack=10, crit_rate=4.0, crit_damage=0.10,
            recipe={'Núcleo de Dobra':1, 'Cristal estelar':12, 'Matriz de fase':6, 'Liga meteórica':40}, available=False),
}
# Catálogo visual preparado para os três designs do elmo.
# O Tier 1 utiliza o design Tático; os outros dois permanecem como projetos futuros,
# mas já possuem identidade, preview e suporte de sprite para as quatro direções.
HELMET_DESIGNS = {
    'tactical': dict(name='Elmo Tático', short='TÁTICO', ability='Scan básico e análise cultural.', locked=False, accent=(86,215,197), shell=(62,77,87), visor=(95,220,207)),
    'recon': dict(name='Elmo de Reconhecimento', short='RECONHECIMENTO', ability='Análise ambiental e alcance de detecção ampliado.', locked=True, accent=(236,187,100), shell=(74,79,88), visor=(236,187,100)),
    'combat': dict(name='Elmo de Combate', short='COMBATE', ability='Interface de ameaça e rotinas ofensivas avançadas.', locked=True, accent=(224,112,93), shell=(72,64,68), visor=(224,112,93)),
}
HELMET_DESIGN_ORDER = ('tactical', 'recon', 'combat')

# Progressão funcional do Elmo. Os bônus são do tier atual (não cumulativos).
# O Tier 2 já é alcançável nesta versão por exigir materiais obtidos fora de Veyra,
# dentro da Galáxia Nárion. O Tier 3 permanece reservado para tecnologia futura.
HELMET_TIERS = {
    1: dict(name='Elmo / Tier 1', precision=2, crit_rate=2.0, available=True,
            scan_creatures=True, scan_rocks=False, scan_flora=True, stasis_shield=False,
            recipe={'Sucata':24, 'Núcleo de decodificação':4, 'Célula de energia instável':1}),
    2: dict(name='Elmo / Tier 2', precision=4, crit_rate=5.0, available=True,
            scan_creatures=True, scan_rocks=True, scan_flora=True, stasis_shield=True, stasis_window='threat',
            recipe={'Liga meteórica':5, 'Filamento criônico':5, 'Fibra radicular':5, 'Pelo luminal':5}),
    3: dict(name='Elmo / Tier 3', precision=8, crit_rate=10.0, available=False,
            scan_creatures=True, scan_rocks=True, scan_flora=True, stasis_shield=True, stasis_window='threat',
            recipe={'Matriz fotônica':4, 'Núcleo de ressonância':4, 'Célula mnêmica':4},),
}

HELMET_SCAN_ABILITIES = (
    ('creatures', 'Scan de criaturas'),
    ('rocks', 'Scan de rochas'),
    ('flora', 'Scan de flora'),
)
TOTAL_MEMORY_SLOTS = 4
CHEST_MEMORY_SLOT_UNLOCKS = {1: 2, 2: 3, 3: 4}
RENOWN_MILESTONES = {
    'faction': (25, 50, 100),
    'planet': (50, 150, 300),
    'galaxy': (500, 1500),
}
RENOWN_REWARDS = {
    'faction': ((('Sucata',12),('Placa',5)), (('Núcleo',3),('Sucata',18)), (('Placa',10),('Núcleo',5))),
    'planet': ((('Sucata',20),('Núcleo',5)), (('Placa',12),('Núcleo',8)), (('Núcleo',10),('Placa',20))),
    'galaxy': ((('Núcleo',8),('Placa',15)), (('Núcleo',15),('Sucata',30))),
}
CIVILIZATION = {
    'id': 'avarin',
    'name': 'Avarin',
    'language': 'Avari',
    'culture': 'Uma sociedade moldada pela escassez de água. Memórias, heranças e acordos são preservados em torno dos reservatórios.',
    'visual': 'Tecidos amplos, mantos de filtragem, cerâmica metálica e placas leves para proteção contra poeira e calor.',
}
NAHR_CIVILIZATION = {
    'id': 'nahr_shadows',
    'name': 'Sombras de Nahr',
    'language': 'Nahrim',
    'culture': 'Uma civilização de pequenas sombras escuras e flutuantes. Sua memória coletiva é preservada por ecos, gestos, sinais de luz apagada e ritos de silêncio.',
    'visual': 'Pequenas silhuetas negras, sem forma corporal rígida, que flutuam em baixa altura e se deslocam como manchas vivas no ar.',
}
FACTIONS = {
    'waterkeepers': dict(name='Guardiões dos Reservatórios', short='GUARDIÕES', description='Administram água, bombas e a memória dos acordos entre assentamentos.', leader='Iria', leader_role='Guardiã-Mor dos Reservatórios'),
    'dunewatch': dict(name='Vigias das Dunas', short='VIGIAS', description='Patrulham rotas, protegem assentamentos e controlam travessias perigosas.'),
    'rift_children': dict(name='Filhos da Fenda', short='FILHOS DA FENDA', description='Uma coalizão de clãs das fraturas de Nahar que disputa as rotas de água e acusa os Guardiões de monopolizar os reservatórios.', leader='Tarek', leader_role='Voz da Fenda'),
    'scavengers': dict(name='Recuperadores de Qaresh', short='RECUPERADORES', description='Recolhem tecnologia e sucata nas ruínas, mantendo oficinas e depósitos.'),
    'nahr_shadows': dict(name='Sombras de Nahr', short='SOMBRAS DE NAHR', description='Pequenas sombras flutuantes que registram memória e história por ecos, sinais e ritos de silêncio.', leader='Sombra Oracular', leader_role='Intérprete dos Ritos'),
}
SHIP = (7, 7)
SAFE = 2
SHIP_INTERIOR = {
    'size': (14, 10),
    'start': (6, 6),
    'cockpit': (6, 2),
    'computer': (2, 5),
    'status_panel': (11, 5),
    'simulator': (4, 7),
    'respawn_tank': (3, 7),
    'essence_storage': (9, 7),
    'airlock': (7, 9),
    'solid': {(0, y) for y in range(9)} | {(11, y) for y in range(9)} | {(x, 0) for x in range(12)} | {(x, 8) for x in range(12)},
}
SHIP_SYSTEMS = {
    'hull': dict(name='Casco estrutural', condition=46, status='DEGRADADO', detail='microfraturas e perda parcial da blindagem.', repair='Missão de reparo'),
    'power': dict(name='Distribuição de energia', condition=72, status='ESTÁVEL', detail='o núcleo do peitoral está estável; barramentos secundários estão danificados.', repair='Missão de reparo'),
    'propulsion': dict(name='Propulsão atmosférica', condition=9, status='CRÍTICO', detail='câmaras de impulso e controle vetorial fora de sincronismo.', repair='Missão de reparo'),
    'navigation': dict(name='Navegação estelar', condition=14, status='CORROMPIDA', detail='a matriz estelar perdeu referências e bancos de trajetória.', repair='Sucata ×80'),
    'comms': dict(name='Comunicação', condition=0, status='OFFLINE', detail='módulo de emissão e antena principal indisponíveis.', repair='4 Sentinelas + antena'),
    'ftl': dict(name='Propulsão de dobra', condition=0, status='AUSENTE', detail='nenhum núcleo de dobra compatível foi detectado a bordo.', repair='Missão de reparo'),
}
SHIP_DIAGNOSTIC_ORDER = ('hull', 'power', 'propulsion', 'navigation', 'comms', 'ftl')

SHIP_MISSION_DATA = {
    'ship_hull': dict(system='hull', title='Cicatrizes do Casco', category='NAVE', objective='Mapeie três pontos de tensão do casco e sincronize pulsos de reparo com a frequência estrutural correta.'),
    'ship_power': dict(system='power', title='Equilíbrio de Carga', category='NAVE', objective='Recalibre a distribuição entre os quatro barramentos. O objetivo é estabilizar a rede sem sobrecarregar nenhum circuito.'),
    'ship_propulsion': dict(system='propulsion', title='Vetor de Impulso', category='NAVE', objective='Execute a sequência de vetores indicada pela Manopla para realinhar as câmaras de impulso atmosférico.'),
    'ship_navigation': dict(system='navigation', title='Referência Perdida', category='NAVE', objective='Recupere a referência da matriz estelar no cockpit e restaure o sensor de navegação.'),
    'ship_comms': dict(system='comms', title='Triangulação Silenciosa', category='NAVE', objective='Chegue à antena de comunicação, elimine as quatro Sentinelas Avariadas e conclua a triangulação com os satélites próximos.'),
    'ship_ftl': dict(system='ftl', title='Janela de Dobra', category='NAVE', objective='Ajuste a fase de dobra em três janelas de ressonância. Um acerto fora da zona segura reinicia a tentativa atual.'),
}
PLAYER_COMBAT = {
    'attack': 12, 'defense': 5, 'precision': 10, 'amp': 1.0, 'crit_rate': 5.0, 'crit_damage': 1.50,
    'damage_min': 3, 'damage_max': 5, 'min_damage_bonus': 0, 'crit_rate_bonus': 0.0,
    'crit_damage_bonus': 0.0, 'amp_bonus': 0.0, 'attack_bonus': 0, 'defense_bonus': 0,
    'enemy_crit_rate_reduction': 0.0, 'enemy_crit_damage_reduction': 0.0,
}
CARD_RARITIES = ('Comum', 'Incomum', 'Rara', 'Mítica', 'Lendária', 'Única')
CARD_RARITY_RULES = {
    'Comum': 'Fauna comum, ameaças recorrentes e criaturas de menor complexidade.',
    'Incomum': 'Criaturas mais relevantes taticamente e encontros que exigem maior preparação.',
    'Rara': 'Chefes e criaturas de categoria de ameaça excepcional.',
    'Mítica': 'Cartas ligadas a missões importantes e combates excepcionalmente difíceis.',
    'Lendária': 'Super bosses e momentos críticos da campanha.',
    'Única': 'Cartas especiais obtidas somente por um sistema futuro de fabricação.',
}
# Escala-base de BÔNUS DE ATQ. Estes valores são percentuais do ATQ efetivo,
# evitando que cartas antigas percam valor conforme o personagem evolui.
# Variantes +/++ multiplicam o percentual pelo multiplicador da variante.
CARD_ATTACK_PERCENT_GUIDE = {
    'Comum': (3.0, 3.0),
    'Incomum': (5.0, 5.0),
    'Rara': (10.0, 10.0),
    'Mítica': (15.0, 15.0),
    'Lendária': (20.0, 20.0),
    'Única': (0.0, 0.0),
}

CARD_VARIANTS = {
    'normal': dict(label='', chance=0.950, multiplier=1.00),
    'plus': dict(label='+', chance=0.045, multiplier=1.50),
    'plusplus': dict(label='++', chance=0.005, multiplier=2.00),
}
RELIC_STONE_NAME = 'Núcleo Relíquia'

CREATURE_TYPES = ('Terra', 'Metal', 'Fogo', 'Água', 'Elétrico', 'Planta', 'Luz', 'Trevas')

# DOMÍNIO — progressão individual da Manopla.
# Cada nível usa XP acumulado. O primeiro nível exige 2.000 XP e a progressão
# cresce exponencialmente (30% por nível), tornando os níveis finais deliberadamente
# longos sem criar números fracionários.
DOMAIN_ELEMENTS = ('Água', 'Elétrico', 'Fogo', 'Luz', 'Metal', 'Planta', 'Terra', 'Trevas')
DOMAIN_LEVEL_MAX = 40
DOMAIN_LEVEL_XP = {level: int(round(2000 * (1.30 ** (level - 1)))) for level in range(1, DOMAIN_LEVEL_MAX + 1)}

# Os dez primeiros bônus se repetem quatro vezes, exatamente na ordem da tabela
# definida para a 0.6.9. Cada entrada é (nome exibido, campo lógico, valor).
_DOMAIN_CYCLE = {
    'Fogo': (
        ('Dano Mínimo +1', 'min_damage', 1), ('Ataque +3%', 'attack_pct', 3), ('Dano Crítico +5%', 'crit_damage', 0.05),
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Mínimo +1', 'min_damage', 1),
        ('Ataque +3%', 'attack_pct', 3), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Recebido -1%', 'damage_taken_pct', 1), ('AMP +1%', 'amp', 1),
    ),
    'Água': (
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Taxa Crítica +2%', 'crit_rate', 2), ('Defesa +3%', 'defense_pct', 3),
        ('Ataque +3%', 'attack_pct', 3), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Recebido -1%', 'damage_taken_pct', 1),
        ('Taxa Crítica +2%', 'crit_rate', 2), ('Defesa +3%', 'defense_pct', 3), ('Ataque +3%', 'attack_pct', 3), ('AMP +1%', 'amp', 1),
    ),
    'Planta': (
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Defesa +3%', 'defense_pct', 3), ('Ataque +3%', 'attack_pct', 3),
        ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Recebido -1%', 'damage_taken_pct', 1),
        ('Defesa +3%', 'defense_pct', 3), ('Ataque +3%', 'attack_pct', 3), ('Dano Crítico +5%', 'crit_damage', 0.05), ('AMP +1%', 'amp', 1),
    ),
    'Terra': (
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Defesa +3%', 'defense_pct', 3), ('Ataque +3%', 'attack_pct', 3),
        ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Recebido -1%', 'damage_taken_pct', 1),
        ('Defesa +3%', 'defense_pct', 3), ('Ataque +3%', 'attack_pct', 3), ('Dano Crítico +5%', 'crit_damage', 0.05), ('AMP +1%', 'amp', 1),
    ),
    'Metal': (
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Taxa Crítica +2%', 'crit_rate', 2),
        ('Ataque +3%', 'attack_pct', 3), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Recebido -1%', 'damage_taken_pct', 1),
        ('Dano Crítico +5%', 'crit_damage', 0.05), ('Taxa Crítica +2%', 'crit_rate', 2), ('Ataque +3%', 'attack_pct', 3), ('AMP +1%', 'amp', 1),
    ),
    'Elétrico': (
        ('Dano Mínimo +1', 'min_damage', 1), ('Ataque +3%', 'attack_pct', 3), ('Defesa +3%', 'defense_pct', 3),
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Mínimo +1', 'min_damage', 1),
        ('Ataque +3%', 'attack_pct', 3), ('Defesa +3%', 'defense_pct', 3), ('Dano Recebido -1%', 'damage_taken_pct', 1), ('AMP +1%', 'amp', 1),
    ),
    'Luz': (
        ('Dano Mínimo +1', 'min_damage', 1), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Taxa Crítica +2%', 'crit_rate', 2),
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Mínimo +1', 'min_damage', 1),
        ('Dano Crítico +5%', 'crit_damage', 0.05), ('Taxa Crítica +2%', 'crit_rate', 2), ('Dano Recebido -1%', 'damage_taken_pct', 1), ('AMP +1%', 'amp', 1),
    ),
    'Trevas': (
        ('Dano Mínimo +1', 'min_damage', 1), ('Taxa Crítica +2%', 'crit_rate', 2), ('Dano Crítico +5%', 'crit_damage', 0.05),
        ('Dano Recebido -1%', 'damage_taken_pct', 1), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Mínimo +1', 'min_damage', 1),
        ('Taxa Crítica +2%', 'crit_rate', 2), ('Dano Crítico +5%', 'crit_damage', 0.05), ('Dano Recebido -1%', 'damage_taken_pct', 1), ('AMP +1%', 'amp', 1),
    ),
}
DOMAIN_BONUSES = {
    element: {level: dict(name=_DOMAIN_CYCLE[element][(level - 1) % 10][0], kind=_DOMAIN_CYCLE[element][(level - 1) % 10][1], value=_DOMAIN_CYCLE[element][(level - 1) % 10][2]) for level in range(1, DOMAIN_LEVEL_MAX + 1)}
    for element in DOMAIN_ELEMENTS
}


# Economia das Cartas Únicas. Essência não possui receita: só entra por combate.
ESSENCE_DROP_RANGES = {
    'Comum': (4, 10),
    'Incomum': (12, 18),
    'Rara': (20, 50),
    'Mítica': (70, 100),
    'Lendária': (200, 500),
}
UNIQUE_CARD_ESSENCE_COST = 2000
UNIQUE_VARIANT_MULTIPLIERS = {'normal': 1.0, 'plus': 2.0, 'plusplus': 3.0}
UNIQUE_BUFF_DEFS = {
    'attack': {'label': 'ATQ', 'chance': 0.66, 'value': 4.0},
    'min_damage': {'label': 'Dano Mínimo', 'chance': 0.25, 'value': 2.0},
    'crit_rate': {'label': 'Taxa Crítica', 'chance': 0.04, 'value': 5.0},
    'crit_damage': {'label': 'Dano Crítico', 'chance': 0.04, 'value': 10.0},
    'amp': {'label': 'AMP', 'chance': 0.01, 'value': 1.0},
}
UNIQUE_BUFF_COUNT_CHANCES = {1: 0.75, 2: 0.24, 3: 0.01}

# Habilidade extra opcional das Cartas Únicas.
# Momentum não substitui nenhum buff normal e possui 5% de chance independente.
UNIQUE_MOMENTUM_CHANCE = 0.05
UNIQUE_MOMENTUM_DEFS = {
    'crit_rate': {
        'label': 'Taxa Crítica por tipo',
        'description': 'Toda vez que utilizar um ataque do tipo {type}, este ataque terá 25% de Taxa Crítica.',
    },
    'crit_damage': {
        'label': 'Dano Crítico por cartas',
        'description': 'Toda vez que utilizar um ataque do tipo {type}, este ataque terá 50% de Dano Crítico para cada carta de {type} equipada.',
    },
    'memory': {
        'label': 'Recuperação de Memória',
        'description': 'Toda vez que utilizar um ataque do tipo {type}, recupere 1 ponto de Memória.',
    },
    'amp': {
        'label': 'AMP por cartas',
        'description': 'Toda vez que utilizar um ataque do tipo {type}, este ataque terá 5% a mais de AMP para cada carta de {type} equipada.',
    },
}

# Interações de tipos para ataques de cartas. Tipos que não participam desta
# matriz permanecem neutros por enquanto.
TYPE_ADVANTAGES = {
    'Água': 'Fogo',
    'Fogo': 'Planta',
    'Planta': 'Água',
    'Elétrico': 'Metal',
    'Terra': 'Elétrico',
    'Metal': 'Terra',
    'Luz': 'Trevas',
    'Trevas': 'Luz',
}

CARD_LOWERCASE_CONNECTORS = {
    'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na', 'nos', 'nas',
    'ao', 'aos', 'à', 'às', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
    'entre', 'até', 'desde', 'contra', 'perante', 'após', 'ante',
}

def format_card_name(name):
    """Padroniza nomes de cartas em Title Case, preservando conectores."""
    words = str(name).split()
    if not words:
        return str(name)
    out = []
    for i, word in enumerate(words):
        clean = word.strip()
        if i > 0 and clean.casefold() in CARD_LOWERCASE_CONNECTORS:
            out.append(clean.casefold())
        else:
            if clean.casefold() == 'ry':
                out.append('RY')
            else:
                out.append(clean[:1].upper() + clean[1:].lower())
    return ' '.join(out)

HERBS = {
    'Erva-sílica': dict(name='Erva-sílica', description='Folha resistente à aridez extrema. Utilidade ainda não determinada.'),
    'Folha de Nara': dict(name='Folha de Nara', description='Folhagem de superfície fina, encontrada junto a fissuras de solo protegido.'),
    'Musgo azul de Veyra': dict(name='Musgo azul de Veyra', description='Colônia pigmentada que retém umidade em microestruturas cristalinas.'),
    'Flor salina': dict(name='Flor salina', description='Estrutura floral rara que cresce próxima a concentrações naturais de sal.'),
    'Lótus de Cinza': dict(name='Lótus de Cinza', description='Planta de pétalas espessas que resiste ao calor químico de Orionis.'),
    'Flor de Sílica Rubra': dict(name='Flor de Sílica Rubra', description='Estrutura floral mineralizada que cresce em fissuras quentes de Orionis.'),
    'Musgo de Geada': dict(name='Musgo de Geada', description='Colônia vegetal que armazena água congelada em microfibras.'),
    'Líquen Prismático': dict(name='Líquen Prismático', description='Líquen translúcido que dispersa a luz sobre rochas geladas.'),
    'Trepa-basáltica': dict(name='Trepa-basáltica', description='Cipó rígido que se fixa a superfícies vulcânicas de Nahr.'),
    'Flor de Sal Negro': dict(name='Flor de Sal Negro', description='Flor mineral escura que cresce junto a depósitos salinos profundos.'),
    'Orquídea Fotônica': dict(name='Orquídea Fotônica', description='Planta luminosa que armazena energia em estruturas semelhantes a pétalas.'),
    'Fungo Velado': dict(name='Fungo Velado', description='Fungo de atmosfera densa que mantém esporos protegidos por uma membrana fina.'),
}

SPECIES = {
    'scarab': dict(type='Terra', name='Escaravelho de sílica', hp=90, attack=(4, 5), skill_attack=(0, 1), defense=4, precision=10, amp=0.0,
                   target_zones={'body':dict(name='Carapaça', defense=4, evasion=0), 'head':dict(name='Cabeça', defense=3, evasion=11), 'leg':dict(name='Patas', defense=2, evasion=11)},
                   crit_rate=2.0, crit_damage=1.30, respawn=60, card='shell', vital_zone='head', color=(191,114,65),
                   drops=[('Carapaça', .75, 1, 2), ('Núcleo', .20, 1, 1), ('Sucata', .55, 1, 2)]),
    'lizard': dict(type='Terra', name='Lagarto das dunas', hp=108, attack=(5, 6), skill_attack=(1, 1), defense=5, precision=11, amp=0.0,
                   target_zones={'body':dict(name='Tronco', defense=5, evasion=0), 'head':dict(name='Cabeça', defense=4, evasion=9), 'tail':dict(name='Cauda', defense=3, evasion=11)},
                   crit_rate=3.0, crit_damage=1.35, respawn=120, card='bite', vital_zone='head', color=(136,164,104),
                   drops=[('Escama', .65, 1, 2), ('Enzima', .22, 1, 1), ('Sucata', .55, 1, 2)]),
    'drone': dict(type='Metal', name='Sentinela avariada', hp=120, attack=(5, 7), skill_attack=(1, 1), defense=6, precision=11, amp=0.0,
                  target_zones={'body':dict(name='Chassi', defense=6, evasion=0), 'sensor':dict(name='Sensor óptico', defense=4, evasion=10), 'arm':dict(name='Braço mecânico', defense=5, evasion=11)},
                  crit_rate=4.0, crit_damage=1.40, respawn=240, card='static', vital_zone='sensor', color=(120,154,172),
                  drops=[('Placa', .60, 1, 2), ('Microchip', .08, 1, 1), ('Sucata', .70, 1, 2)]),
    'hound': dict(type='Terra', name='Cão de sílica', hp=118, attack=(5, 7), skill_attack=(1, 1), defense=6, precision=11, amp=0.0,
                  target_zones={'body':dict(name='Tronco', defense=6, evasion=0), 'head':dict(name='Cabeça', defense=5, evasion=9), 'leg':dict(name='Pata dianteira', defense=4, evasion=11)},
                  crit_rate=3.0, crit_damage=1.35, respawn=150, card='hound', vital_zone='head', color=(170,115,81),
                  drops=[('Presa', .65, 1, 2), ('Glândula', .10, 1, 1), ('Sucata', .60, 1, 2)]),
    'burrower': dict(type='Terra', name='Escavador vítreo', hp=145, attack=(6, 8), skill_attack=(1, 1), defense=8, precision=13, amp=0.0,
                     target_zones={'body':dict(name='Carapaça', defense=8, evasion=0), 'head':dict(name='Cabeça', defense=6, evasion=13), 'drill':dict(name='Broca', defense=5, evasion=17)},
                     crit_rate=4.0, crit_damage=1.40, respawn=210, card='burrow', vital_zone='head', color=(113,137,129),
                     drops=[('Placa vítrea', .55, 1, 2), ('Secreção', .18, 1, 1), ('Sucata', .65, 1, 2)]),
    'guard': dict(type='Metal', name='Guardião Avarin', hp=155, attack=(6, 8), skill_attack=(1, 1), defense=7, precision=13, amp=0.0,
                  target_zones={'body':dict(name='Peitoral', defense=7, evasion=0), 'head':dict(name='Cabeça', defense=5, evasion=13), 'arm':dict(name='Braço armado', defense=4, evasion=17)},
                  crit_rate=4.0, crit_damage=1.40, respawn=999999, card='guard_strike', vital_zone='head', color=(86,94,100), drops=[]),
    'manta': dict(type='Terra', name='Manta de poeira', hp=155, attack=(6, 8), skill_attack=(1, 1), defense=8, precision=13, amp=0.0,
                  target_zones={'body':dict(name='Corpo', defense=8, evasion=0), 'head':dict(name='Olho', defense=6, evasion=14), 'wing':dict(name='Ala', defense=5, evasion=17)},
                  crit_rate=4.0, crit_damage=1.40, respawn=300, card='manta', vital_zone='head', color=(159,126,92),
                  drops=[('Membrana', .60, 1, 2), ('Filamento', .08, 1, 1), ('Sucata', .70, 1, 3)]),
    'stalker': dict(type='Luz', name='Predador prismático', hp=185, attack=(7, 9), skill_attack=(1, 2), defense=9, precision=15, amp=0.0,
                    target_zones={'body':dict(name='Tronco', defense=9, evasion=0), 'head':dict(name='Cabeça', defense=7, evasion=20), 'crystal':dict(name='Núcleo prismático', defense=5, evasion=28), 'limb':dict(name='Membro', defense=6, evasion=24)},
                    crit_rate=4.0, crit_damage=1.40, respawn=360, card='stalker', vital_zone='crystal', color=(116,143,149),
                    drops=[('Fragmento prismático', .65, 1, 2), ('Saliva condutora', .08, 1, 1), ('Sucata', .72, 1, 3)]),

    # ORIONIS — fauna adaptada ao calor químico e à metalurgia natural.
    'salamander_igneous': dict(type='Fogo', name='Salamandra ígnea', hp=150, attack=(7,9), skill_attack=(1,2), defense=7, precision=13, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=7, evasion=0), 'head':dict(name='Cabeça', defense=6, evasion=13), 'crest':dict(name='Crista térmica', defense=5, evasion=17)},
        crit_rate=4.0, crit_damage=1.40, respawn=210, card='magma_lance', vital_zone='head', color=(207,91,57),
        drops=[('Cinza ígnea', .70, 1, 2), ('Escama térmica', .22, 1, 1), ('Liga meteórica', .45, 1, 2)]),
    'ironback_crab': dict(type='Metal', name='Caranguejo ferrídeo', hp=178, attack=(8,10), skill_attack=(1,2), defense=9, precision=14, amp=0.0,
        target_zones={'body':dict(name='Carapaça', defense=9, evasion=0), 'head':dict(name='Cabeça', defense=7, evasion=12), 'claw':dict(name='Pinça', defense=6, evasion=18)},
        crit_rate=4.5, crit_damage=1.40, respawn=240, card='forge_claw', vital_zone='head', color=(104,116,124),
        drops=[('Liga ferrídea', .72, 1, 2), ('Placa térmica', .25, 1, 1), ('Liga meteórica', .55, 1, 2)]),
    'ion_wasp': dict(type='Elétrico', name='Vespa iônica', hp=164, attack=(9,11), skill_attack=(1,2), defense=7, precision=16, amp=0.0,
        target_zones={'body':dict(name='Abdômen', defense=7, evasion=0), 'head':dict(name='Olho', defense=5, evasion=20), 'wing':dict(name='Asa', defense=4, evasion=24)},
        crit_rate=5.0, crit_damage=1.45, respawn=180, card='ion_burst', vital_zone='head', color=(105,181,206),
        drops=[('Núcleo iônico', .50, 1, 2), ('Ferrão condutor', .16, 1, 1), ('Núcleo de ressonância', .16, 1, 1)]),

    # KAEL — fauna de gelo, vento e cristal.
    'frost_wolf': dict(type='Água', name='Lobo de geada', hp=176, attack=(8,10), skill_attack=(1,2), defense=8, precision=15, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=8, evasion=0), 'head':dict(name='Focinho', defense=6, evasion=14), 'leg':dict(name='Pata', defense=5, evasion=19)},
        crit_rate=4.5, crit_damage=1.42, respawn=200, card='frost_bite', vital_zone='head', color=(109,151,183),
        drops=[('Pelo criônico', .72, 1, 2), ('Garra gélida', .20, 1, 1), ('Filamento criônico', .50, 1, 2)]),
    'crystal_grazer': dict(type='Terra', name='Pastador cristalino', hp=196, attack=(9,11), skill_attack=(1,2), defense=10, precision=13, amp=0.0,
        target_zones={'body':dict(name='Carapaça', defense=10, evasion=0), 'head':dict(name='Cabeça', defense=8, evasion=14), 'horn':dict(name='Chifre', defense=6, evasion=21)},
        crit_rate=4.0, crit_damage=1.45, respawn=240, card='crystal_ram', vital_zone='horn', color=(116,153,179),
        drops=[('Cristal de gelo', .75, 1, 2), ('Fragmento luminescente', .18, 1, 1), ('Cristal estelar', .18, 1, 1)]),
    'glacial_eel': dict(type='Água', name='Enguia glacial', hp=184, attack=(9,12), skill_attack=(1,2), defense=8, precision=16, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=8, evasion=0), 'head':dict(name='Cabeça', defense=6, evasion=16), 'fin':dict(name='Barbatana', defense=5, evasion=22)},
        crit_rate=5.0, crit_damage=1.44, respawn=190, card='glacial_gust', vital_zone='head', color=(72,159,182),
        drops=[('Gel criônico', .70, 1, 2), ('Barbatana fria', .20, 1, 1), ('Composto de pressão', .42, 1, 2)]),

    # NAHR — vida vegetal agressiva e organismos de solo basáltico.
    'root_scorpion': dict(type='Planta', name='Escorpião de raízes', hp=188, attack=(9,11), skill_attack=(1,2), defense=9, precision=15, amp=0.0,
        target_zones={'body':dict(name='Carapaça', defense=9, evasion=0), 'head':dict(name='Cabeça', defense=7, evasion=14), 'tail':dict(name='Ferrão', defense=6, evasion=21)},
        crit_rate=5.0, crit_damage=1.45, respawn=220, card='root_spear', vital_zone='head', color=(86,123,69),
        drops=[('Fibra radicular', .72, 1, 2), ('Seiva cáustica', .20, 1, 1), ('Célula mnêmica', .08, 1, 1)]),
    'basalt_tortoise': dict(type='Terra', name='Tartaruga basáltica', hp=218, attack=(10,12), skill_attack=(1,2), defense=12, precision=12, amp=0.0,
        target_zones={'body':dict(name='Casco', defense=12, evasion=0), 'head':dict(name='Cabeça', defense=8, evasion=12), 'leg':dict(name='Pata', defense=6, evasion=19)},
        crit_rate=3.5, crit_damage=1.42, respawn=260, card='basalt_charge', vital_zone='head', color=(98,87,79),
        drops=[('Fragmento basáltico', .76, 1, 2), ('Pó vulcânico', .25, 1, 1), ('Composto de pressão', .35, 1, 2)]),
    'salt_spider': dict(type='Terra', name='Aranha salina', hp=202, attack=(10,13), skill_attack=(1,2), defense=9, precision=17, amp=0.0,
        target_zones={'body':dict(name='Abdômen', defense=9, evasion=0), 'head':dict(name='Olhos', defense=6, evasion=20), 'leg':dict(name='Pata', defense=5, evasion=24)},
        crit_rate=5.5, crit_damage=1.46, respawn=210, card='salt_spit', vital_zone='head', color=(190,181,163),
        drops=[('Cristal salino', .78, 1, 2), ('Fio calcificado', .18, 1, 1), ('Cristal de sintonia', .18, 1, 1)]),

    # ELYRA — fauna de atmosfera densa e bioluminescência.
    'luminous_stag': dict(type='Luz', name='Cervo luminal', hp=214, attack=(10,12), skill_attack=(1,2), defense=9, precision=16, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=9, evasion=0), 'head':dict(name='Cabeça', defense=7, evasion=15), 'horn':dict(name='Chifre', defense=5, evasion=22)},
        crit_rate=5.0, crit_damage=1.48, respawn=220, card='luminous_ray', vital_zone='head', color=(150,201,184),
        drops=[('Pelo luminal', .74, 1, 2), ('Fragmento fotônico', .20, 1, 1), ('Matriz fotônica', .10, 1, 1)]),
    'shadow_panther': dict(type='Trevas', name='Pantera umbrina', hp=228, attack=(11,13), skill_attack=(1,2), defense=10, precision=18, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=10, evasion=0), 'head':dict(name='Cabeça', defense=7, evasion=18), 'claw':dict(name='Garra', defense=6, evasion=25)},
        crit_rate=6.0, crit_damage=1.50, respawn=240, card='umbra_claw', vital_zone='head', color=(74,65,92),
        drops=[('Pelo sombrio', .70, 1, 2), ('Garra de sombra', .22, 1, 1), ('Matriz fotônica', .12, 1, 1)]),
    'spore_manta': dict(type='Planta', name='Manta esporal', hp=220, attack=(10,13), skill_attack=(1,2), defense=9, precision=15, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=9, evasion=0), 'head':dict(name='Núcleo', defense=7, evasion=18), 'wing':dict(name='Asa', defense=5, evasion=23)},
        crit_rate=4.5, crit_damage=1.46, respawn=200, card='spore_burst', vital_zone='head', color=(100,138,118),
        drops=[('Esporo denso', .76, 1, 2), ('Membrana úmida', .22, 1, 1), ('Célula mnêmica', .10, 1, 1)]),

}

# Marca explicitamente a zona vital de cada criatura. O marcador é apenas de dados
# nesta versão; nenhuma regra de execução/one-hit-kill é aplicada ainda.
for _spec in SPECIES.values():
    _vital_id = _spec.get('vital_zone')
    for _zone_id, _zone in _spec.get('target_zones', {}).items():
        _zone['vital'] = (_zone_id == _vital_id)



BOSSES = {
    'kuvaar': {
        'type': 'Terra',
        'name': 'Kuvaar, o Sorvedouro',
        'hp': 320,
        'attack': (6, 8),
        'skill_attack': (1, 2),
        'defense': 30,
        'precision': 16,
        'amp': 0.0,
        'crit_rate': 4.0,
        'crit_damage': 1.40,
        'card': 'kuvaar', 'vital_zone': 'ventral',
        'rare': True,
        'description': 'Uma criatura colossal cuja Couraça de Sal absorve umidade. A carapaça cristalizada dificulta qualquer ataque direto.',
        'target_zones': {
            'head': dict(name='Cabeça', defense=24, evasion=15, exposed_only=False),
            'shell': dict(name='Couraça de Sal', defense=30, evasion=0, exposed_only=False),
            'ventral': dict(name='Fenda Ventral', defense=10, evasion=30, exposed_only=True, vital=True),
        },
        'special_attack_card': 'kuvaar', 'mana_cost': 6, 'special_chance': 60.0,
        'drops': [
            ('Núcleo de Kuvaar', 1.00, 1, 1),
            ('Cristal de Sal', 0.85, 1, 2),
            ('Sucata', 0.75, 2, 4),
        ],
    },
    'fagor': {
        'type': 'Fogo', 'name': 'Fagor', 'hp': 360, 'attack': (10, 13), 'skill_attack': (2, 3),
        'defense': 22, 'precision': 16, 'amp': 0.0, 'crit_rate': 4.5, 'crit_damage': 1.45,
        'card': 'fagor', 'vital_zone': 'magma_core', 'rare': True,
        'description': 'Um colosso de pedra vulcânica. Duas pernas sustentam o corpo enquanto um Núcleo de Magma pulsa no centro.',
        'special_attack_card': 'fagor', 'mana_cost': 6, 'special_chance': 35.0,
        'target_zones': {
            'body': dict(name='Corpo de Pedra', defense=22, evasion=0),
            'leg_left': dict(name='Perna Esquerda', defense=14, evasion=13, hp_key='leg_left', hp=80),
            'leg_right': dict(name='Perna Direita', defense=14, evasion=13, hp_key='leg_right', hp=80),
            'magma_core': dict(name='Núcleo de Magma', defense=5, evasion=7, hp_key='core', hp=140, exposed_only=True, damage_multiplier=1.80, vital=True),
        },
        'drops': [('Pedra Ígnea', .85, 2, 4), ('Núcleo Magmático', 1.0, 1, 1), ('Cinza ígnea', .70, 3, 6)],
    },
    'kael': {
        'type': 'Planta', 'name': 'Trembe', 'hp': 300, 'attack': (13, 17), 'skill_attack': (2, 3),
        'defense': 18, 'precision': 15, 'amp': 0.0, 'crit_rate': 4.0, 'crit_damage': 1.45,
        'card': 'kael', 'vital_zone': 'trunk', 'rare': True,
        'description': 'Uma árvore colossal enraizada em uma clareira. A copa concentra a força ofensiva da criatura.',
        'special_attack_card': 'kael', 'mana_cost': 5, 'special_chance': 40.0, 'crown_attack_scaling': True,
        'target_zones': {
            'crown': dict(name='Copa', defense=14, evasion=12, hp_key='crown', hp=120),
            'trunk': dict(name='Tronco', defense=18, evasion=3, hp_key='trunk', hp=300, vital=True),
        },
        'drops': [('Núcleo de Madeira Ancestral', 1.0, 1, 1), ('Seiva concentrada', .85, 2, 5), ('Fibra radicular', .75, 3, 6)],
    },
    'ounull': {
        'type': 'Água', 'name': 'Ounull', 'hp': 310, 'attack': (9, 12), 'skill_attack': (2, 3),
        'defense': 19, 'precision': 16, 'amp': 0.0, 'crit_rate': 4.0, 'crit_damage': 1.45,
        'card': 'ounull', 'vital_zone': 'body', 'rare': True, 'special_attack_card': 'ounull_tide', 'mana_cost': 5, 'special_chance': 45.0,
        'memory_attack_heal_ratio': 0.10,
        'description': 'Uma entidade aquática que controla a água do lago ao redor da ilha. Cada ataque especial aumenta a ameaça de Afogamento.',
        'target_zones': {'body': dict(name='Corpo Aquático', defense=19, evasion=0, vital=True)},
        'drops': [('Núcleo de Ounull', 1.0, 1, 1), ('Pérola de Maré', .80, 2, 5), ('Membrana úmida', .75, 3, 6)],
    },
    'ry': {
        'type': 'Luz', 'name': 'RY', 'hp': 1400, 'attack': (17, 21), 'skill_attack': (3, 5),
        'defense': 28, 'precision': 20, 'amp': 0.0, 'crit_rate': 8.0, 'crit_damage': 1.60,
        'card': 'ry', 'vital_zone': 'light_core', 'rare': False, 'legendary': True, 'special_attack_card': 'ry',
        'mana_cost': 8, 'mana_max': 24, 'special_chance': 50.0,
        'earth_shield_amount': 160, 'plant_heal_ratio': 0.20, 'fire_burn_damage': 4, 'fire_burn_turns': 3,
        'description': 'Uma esfera de luz disforme e translúcida. O povo de Nahr a trata como a personificação da morte, um ser que surge para executar quem desejar.',
        'target_zones': {
            'light_core': dict(name='Núcleo de Luz', defense=28, evasion=6, hp_key='main', hp=1400, vital=True),
        },
        'drops': [('Núcleo de RY', 1.0, 1, 1), ('Fragmento Luminal', .80, 2, 4), ('Essência de Luz', .70, 2, 5)],
        'special_drop': ('Núcleo de Dobra', 1),
    },
}

CARDS = {
    'shell': dict(type='Terra', name='Impacto de Sílica', species='scarab', cost=2, damage=(7, 10), skill_amp=0.4, rarity='Comum', target_mode='single',
                  shield_pct=50.0, attributes={'attack_pct':3.0},
                  description='7–10 Ataque da Skill; bloqueia 50% do próximo ataque.', recipe={'Carapaça':12,'Núcleo':2,'Sucata':4}),
    'bite': dict(type='Terra', name='Mordida de Areia', species='lizard', cost=2, damage=(6, 8), skill_amp=0.7, rarity='Comum', target_mode='single',
                 attack_crit_rate_bonus=25.0, attributes={'attack_pct':3.0},
                 description='6–8 Ataque da Skill; esse ataque tem +25% de Taxa Crítica.', recipe={'Escama':18,'Enzima':3,'Sucata':6}),
    'static': dict(type='Metal', name='Faísca Residual', species='drone', cost=3, damage=(10, 13), skill_amp=0.45, rarity='Incomum', target_mode='multi',
                   combat_precision_bonus=1, attributes={'crit_damage':0.05},
                   description='10–13 Ataque da Skill; +1 de Precisão até o fim do combate (Efeito não cumulativo).', recipe={'Placa':24,'Microchip':4,'Sucata':10}),
    'hound': dict(type='Terra', name='Investida de Sílica', species='hound', cost=3, damage=(7, 10), skill_amp=0.4, rarity='Comum', target_mode='single',
                  combat_min_damage_bonus=1, attributes={'crit_rate':3.0},
                  description='7–10 Ataque da Skill; +1 de Dano Mínimo até o fim do combate (Efeito não cumulativo).', recipe={'Presa':16,'Glândula':2,'Sucata':8}),
    'burrow': dict(type='Terra', name='Ruptura Vítrea', species='burrower', cost=4, damage=(8, 11), skill_amp=0.4, rarity='Comum', target_mode='single',
                   attack_crit_damage_bonus=0.2, attributes={'crit_damage':0.05},
                   description='8–11 Ataque da Skill; esse ataque tem +20% de Dano Crítico.', recipe={'Placa vítrea':14,'Secreção':2,'Sucata':10}),
    'manta': dict(type='Terra', name='Mergulho de Poeira', species='manta', cost=3, damage=(9, 12), skill_amp=0.35, rarity='Comum', target_mode='single',
                  next_attack_type='Terra', next_attack_type_damage_bonus=10.0, attributes={'crit_damage':0.05},
                  description='9–12 Ataque da Skill; se seu próximo ataque for de Terra, o oponente sofre 10% a mais de dano.', recipe={'Membrana':12,'Filamento':2,'Sucata':10}),
    'stalker': dict(type='Luz', name='Rasgo Prismático', species='stalker', cost=5, damage=(10, 13), skill_amp=0.5, rarity='Incomum', target_mode='single',
                    multi_status_chance=30.0, attributes={'attack_pct':5.0},
                    description='10–13 Ataque da Skill; esse ataque tem 30% de chance de causar Atordoamento, Afogamento, Cegueira ou Queimadura por 1 turno.', recipe={'Fragmento prismático':12,'Saliva condutora':2,'Sucata':12}),
    'guard_strike': dict(type='Metal', name='Golpe de Guarda', species='guard', cost=3, damage=(8, 11), skill_amp=0.4, rarity='Comum', target_mode='single',
                         shield_ratio=0.2, attributes={'attack_pct':3.0},
                         description='8–11 Ataque da Skill; esse ataque converte 20% do dano causado como escudo para o usuário.',
                         recipe={'Placa':16,'Sucata':8}, visual_key='guard_strike'),
    # Líderes das facções: ambas as cartas são Míticas, de tipo Terra.
    # O líder derrotado é entregue como carta normal na resolução do conflito.
    # A carta do vencedor permanece como receita de craft de alto custo e exige Núcleo de Kuvaar.
    'lithic_sentence': dict(type='Terra', name='Sentença Litônica', species='avarin_guard', character='Iria', faction='waterkeepers',
                            acquisition='faction_conflict', craftable='winner_only', cost=5, damage=(20, 22), skill_amp=0.75, rarity='Mítica', target_mode='single',
                            next_attack_crit_rate_bonus=100.0, attributes={'attack_pct':15.0},
                            description='20–22 Ataque da Skill; seu próximo ataque terá +100% de Taxa Crítica.',
                            recipe={'Núcleo de Kuvaar':1,'Cristal de Sal':12,'Sucata':36,'Placa':18}, visual_key='lithic_sentence'),
    'rift_break': dict(type='Terra', name='Ruptura da Fenda', species='avarin_guard', character='Tarek', faction='rift_children',
                       acquisition='faction_conflict', craftable='winner_only', cost=5, damage=(20, 22), skill_amp=0.75, rarity='Mítica', target_mode='single',
                       attack_crit_damage_bonus=0.5, attributes={'attack_pct':15.0},
                       description='20–22 Ataque da Skill; esse ataque tem +50% de Dano Crítico.',
                       recipe={'Núcleo de Kuvaar':1,'Cristal de Sal':12,'Sucata':36,'Carapaça':16}, visual_key='rift_break'),
    'kuvaar': dict(type='Terra', name='Dissolução Salina', species='kuvaar', cost=6, damage=(14, 17), skill_amp=0.65, rarity='Rara', target_mode='multi', ignore_enemy_shield=True, attributes={'attack_pct':10.0},
                   description='14–17 Ataque da Skill contra múltiplos alvos; esse ataque ignora qualquer escudo do oponente.',
                   recipe={'Núcleo de Kuvaar':1,'Cristal de Sal':6,'Sucata':18}, acquisition='boss_defeat', craftable=True),

    'fagor': dict(type='Fogo', name='Coração de Fagor', species='fagor', cost=7, damage=(15, 22), skill_amp=0.7, rarity='Rara', target_mode='multi', attributes={'attack_pct':10.0},
        description='15–22 Ataque da Skill contra múltiplos alvos.', recipe={'Núcleo Magmático':1,'Pedra Ígnea':6,'Cinza ígnea':12}, acquisition='boss_defeat', craftable=True),
    'kael': dict(type='Planta', name='Vigor de Trembe', species='kael', cost=6, damage=(8, 11), skill_amp=0.5, rarity='Rara', target_mode='single',
        player_hp_damage_ratio=0.10, player_hp_enemy_attack_reduction=0.10,
        attributes={'crit_damage':0.15},
        description='8–11 Ataque da Skill; adiciona 10% do seu HP atual ao dano e reduz o ATQ do próximo ataque inimigo em 10% do seu HP atual.', recipe={'Núcleo de Madeira Ancestral':1,'Seiva concentrada':5,'Fibra radicular':10}, acquisition='boss_defeat', craftable=True),
    'ounull': dict(type='Água', name='Fluxo de Ounull', species='ounull', cost=6, damage=(12, 16), skill_amp=0.55, rarity='Rara', target_mode='single', heal_ratio=0.01,
        attributes={'attack_pct':10.0},
        description='12–16 Ataque da Skill; recupera 1% do dano causado em HP.', recipe={'Núcleo de Ounull':1,'Pérola de Maré':5,'Membrana úmida':10}, acquisition='boss_defeat', craftable=True),
    'ry': dict(type='Luz', name='Fulgor de RY', species='ry', cost=9, damage=(30, 40), skill_amp=0.9, rarity='Lendária', target_mode='single',
        acquisition='boss_defeat', craftable=True, recipe={'Núcleo de RY':1,'Fragmento Luminal':6,'Essência de Luz':4},
        attack_bonus_flat_temp=1, legendary_ability_id='auxilio_iluminado',
        legendary_ability='Auxílio Iluminado - Se a Memória chegar a 0 enquanto esta carta estiver equipada na Manopla, você perde 1 ponto de Vida e recupera 50% do total da sua Memória.',
        attributes={'attack_pct':20.0},
        description='30–40 Ataque da Skill; concede +1 ATQ até o final do combate, cumulativo a cada uso. Auxílio Iluminado - Se a Memória chegar a 0 enquanto esta carta estiver equipada na Manopla, você perde 1 ponto de Vida e recupera 50% do total da sua Memória.'),
    'ounull_tide': dict(type='Água', name='Maré de Ounull', species='ounull', cost=0, damage=(6,9), skill_amp=0.35, rarity='Rara', target_mode='single', drowning_chance=100.0, enemy_only=True,
        attributes={'attack_pct':0.0,'defense':0,'amp':0.0,'crit_rate':0.0,'crit_damage':0.0,'min_damage_bonus':0,'precision':0},
        description='6–9 Ataque da Skill; causa Afogamento e dobra o custo do próximo ataque especial.', craftable=False),
    'magma_lance': dict(type='Fogo', name='Lança Magmática', species='salamander_igneous', cost=3, damage=(9, 12), skill_amp=0.45, rarity='Comum', target_mode='single',
        burn_chance=30.0, burn_damage=2, burn_turns=2, attributes={'attack_pct':3.0},
        description='9–12 Ataque da Skill; esse ataque tem 30% de chance de causar Queimadura por 2 turnos.', recipe={'Cinza ígnea':18,'Escama térmica':3,'Liga meteórica':6}, visual_key='magma'),
    'forge_claw': dict(type='Metal', name='Pinça de Forja', species='ironback_crab', cost=3, damage=(9, 12), skill_amp=0.35, rarity='Incomum', target_mode='single',
        attack_reduction_pct=10.0, attack_reduction_chance=100.0, status_duration=1, attributes={'attack_pct':5.0},
        description='9–12 Ataque da Skill; reduz o próximo ATQ inimigo em 10%.', recipe={'Liga ferrídea':18,'Placa térmica':3,'Liga meteórica':6}, visual_key='forge'),
    'ion_burst': dict(type='Elétrico', name='Estouro Iônico', species='ion_wasp', cost=5, damage=(11, 14), skill_amp=0.5, rarity='Comum', target_mode='multi',
        stun_chance=30.0, status_duration=1, attributes={'attack_pct':3.0},
        description='11–14 Ataque da Skill; esse ataque tem 30% de chance de causar Atordoamento por 1 turno.', recipe={'Núcleo iônico':8,'Ferrão condutor':3,'Núcleo de ressonância':2}, visual_key='ion'),
    'frost_bite': dict(type='Água', name='Mordida Glacial', species='frost_wolf', cost=3, damage=(9, 13), skill_amp=0.4, rarity='Comum', target_mode='single',
        next_attack_type='Água', next_attack_type_damage_bonus=10.0, attributes={'crit_damage':0.05},
        description='9–13 Ataque da Skill; se seu próximo ataque for de Água, o oponente sofre 10% a mais de dano.', recipe={'Pelo criônico':18,'Garra gélida':3,'Filamento criônico':5}, visual_key='frost'),
    'crystal_ram': dict(type='Terra', name='Investida de Cristal', species='crystal_grazer', cost=5, damage=(11, 15), skill_amp=0.25, rarity='Comum', target_mode='single',
        attack_crit_damage_bonus=0.05, attributes={'crit_damage':0.05},
        description='11–15 Ataque da Skill; esse ataque tem +5% de Dano Crítico.', recipe={'Cristal de gelo':20,'Fragmento luminescente':3,'Cristal estelar':2}, visual_key='ice_crystal'),
    'glacial_gust': dict(type='Água', name='Rajada Glacial', species='glacial_eel', cost=4, damage=(10, 14), skill_amp=0.5, rarity='Incomum', target_mode='single',
        attributes={'attack_pct':5.0},
        description='10–14 Ataque da Skill.', recipe={'Gel criônico':18,'Barbatana fria':3,'Composto de pressão':6}, visual_key='frost_wind'),
    'root_spear': dict(type='Planta', name='Lança de Raiz', species='root_scorpion', cost=4, damage=(10, 13), skill_amp=0.6, rarity='Incomum', target_mode='single',
        attributes={'crit_damage':0.1},
        description='10–13 Ataque da Skill.', recipe={'Fibra radicular':18,'Seiva cáustica':3,'Célula mnêmica':2}, visual_key='root'),
    'basalt_charge': dict(type='Terra', name='Carga Basáltica', species='basalt_tortoise', cost=4, damage=(12, 15), skill_amp=0.3, rarity='Comum', target_mode='single',
        attributes={'attack_pct':3.0},
        description='12–15 Ataque da Skill.', recipe={'Fragmento basáltico':20,'Pó vulcânico':3,'Composto de pressão':5}, visual_key='basalt'),
    'salt_spit': dict(type='Terra', name='Jato Salino', species='salt_spider', cost=5, damage=(11, 15), skill_amp=0.5, rarity='Incomum', target_mode='single',
        defense_reduction_pct=5.0, defense_reduction_chance=100.0, status_duration=1, attributes={'attack_pct':5.0},
        description='11–15 Ataque da Skill; o oponente perde 5% de DEF.', recipe={'Cristal salino':20,'Fio calcificado':3,'Cristal de sintonia':2}, visual_key='salt_spit'),
    'luminous_ray': dict(type='Luz', name='Raio Luminal', species='luminous_stag', cost=3, damage=(11, 14), skill_amp=0.45, rarity='Comum', target_mode='single',
        attributes={'attack_pct':3.0},
        description='11–14 Ataque da Skill.', recipe={'Pelo luminal':18,'Fragmento fotônico':3,'Matriz fotônica':2}, visual_key='luminous'),
    'umbra_claw': dict(type='Trevas', name='Garra Umbrina', species='shadow_panther', cost=5, damage=(12, 16), skill_amp=0.5, rarity='Incomum', target_mode='single',
        attributes={'crit_damage':0.05},
        description='12–16 Ataque da Skill.', recipe={'Pelo sombrio':20,'Garra de sombra':3,'Matriz fotônica':2}, visual_key='umbra'),
    'spore_burst': dict(type='Planta', name='Explosão Esporal', species='spore_manta', cost=3, damage=(10, 14), skill_amp=0.45, rarity='Comum', target_mode='multi',
        next_attack_type='Planta', next_attack_type_damage_bonus=10.0, attributes={'attack_pct':3.0},
        description='10–14 Ataque da Skill; se seu próximo ataque for de Planta, o oponente sofre 10% a mais de dano.', recipe={'Esporo denso':20,'Membrana úmida':3,'Célula mnêmica':2}, visual_key='spore'),

}

# Regras de atributos das cartas a partir da 0.5.9: DEF, PREC, Dano Mínimo e AMP
# não são benefícios permanentes de cartas. Cada carta coletável recebe somente
# um dos três buffs de atributo permitidos pela sua raridade.
_CARD_RARITY_ATTRIBUTE_CAPS = {
    'Comum': {'attack_pct': 3.0, 'crit_rate': 3.0, 'crit_damage': 0.05},
    'Incomum': {'attack_pct': 5.0, 'crit_rate': 5.0, 'crit_damage': 0.10},
    'Rara': {'attack_pct': 10.0, 'crit_rate': 10.0, 'crit_damage': 0.20},
    'Mítica': {'attack_pct': 15.0, 'crit_rate': 15.0, 'crit_damage': 0.25},
    'Lendária': {'attack_pct': 20.0, 'crit_rate': 20.0, 'crit_damage': 0.40},
}

# Revalida as cartas coletáveis contra a regra de um único buff de atributo.
for _cid, _card in CARDS.items():
    if _card.get('enemy_only'):
        _card['attributes'] = {}
        continue
    _rarity = _card.get('rarity')
    _caps = _CARD_RARITY_ATTRIBUTE_CAPS.get(_rarity)
    if _caps:
        _existing = _card.get('attributes', {})
        _preferred = next((k for k in ('attack_pct','crit_rate','crit_damage') if float(_existing.get(k,0) or 0) > 0), 'attack_pct')
        _card['attributes'] = {_preferred: float(_caps[_preferred])}

# Normaliza o nome persistido de todas as cartas para que o catálogo interno,
# o Album, a Oficina e a Manopla compartilhem exatamente a mesma grafia.
for _card in CARDS.values():
    _card['name'] = format_card_name(_card.get('name', ''))

# Perfil explícito de combate dos bosses: cada boss possui ataque básico e ataque especial.
# O especial usa a mesma carta técnica registrada no catálogo do boss.
for _bid, _boss in BOSSES.items():
    _special_cid = _boss.get('special_attack_card') or _boss.get('card')
    _special_card = CARDS.get(_special_cid)
    _boss['basic_attack'] = tuple(_boss.get('attack', (0, 0)))
    if _special_card:
        _boss['special_attack'] = tuple(_special_card.get('damage', (0, 0)))
        _boss['special_attack_name'] = _special_card.get('name', 'Ataque especial')

# Perfil de combate das criaturas. A barra não é exibida no combate; o Scan
# do elmo é quem revela a reserva, o custo e a chance do ataque especial.
CREATURE_MANA_PROFILES = {
    'Comum': dict(mana_max=8, mana_cost=2, special_chance=20.0),
    'Incomum': dict(mana_max=9, mana_cost=3, special_chance=40.0),
    'Rara': dict(mana_max=20, mana_cost=4, special_chance=60.0),
}
for _sid, _spec in SPECIES.items():
    _cid = _spec.get('card')
    _card = CARDS.get(_cid) if _cid else None
    if _card is None:
        continue
    _profile = dict(CREATURE_MANA_PROFILES.get(_card.get('rarity'), CREATURE_MANA_PROFILES['Comum']))
    _spec.update({
        'basic_attack': tuple(_spec.get('attack', (0, 0))),
        'special_attack': tuple(_card.get('damage', (0, 0))),
        'special_attack_card': _cid,
        'special_attack_name': _card.get('name', ''),
        **_profile,
    })
for _bid, _boss in BOSSES.items():
    _cid = _boss.get('card')
    _card = CARDS.get(_cid) if _cid else None
    _special_cid = _boss.get('special_attack_card') or _cid
    _special_card = CARDS.get(_special_cid) if _special_cid else None
    _profile = dict(CREATURE_MANA_PROFILES['Rara'])
    _profile['mana_cost'] = int(_boss.get('mana_cost', 4) or 4)
    _profile['mana_max'] = max(20, _profile['mana_cost'] * 3)
    _profile['special_chance'] = float(_boss.get('special_chance', 60.0) or 60.0)
    _boss.update({
        'basic_attack': tuple(_boss.get('attack', (0, 0))),
        'special_attack': tuple(_special_card.get('damage', _boss.get('skill_attack', (0, 0)))) if _special_card else tuple(_boss.get('skill_attack', (0, 0))),
        'special_attack_card': _special_cid,
        'special_attack_name': _special_card.get('name', '') if _special_card else '',
        **_profile,
    })

GAUNTLET_NEXUS = {
    'name': 'NEXUS — Núcleo Cognitivo de Combate',
    'recipe': {'Sucata': 8, 'Núcleo': 1, 'Placa': 1},
    'description': 'Habilita a senciência da manopla',
}
# XP acumulada para alcançar cada nível do NEXUS.
# A progressão é deliberadamente muito longa: dano causado continua valendo 1 XP,
# mas o nível máximo exige 25 milhões de dano acumulado.
NEXUS_LEVEL_XP = {
    # Níveis 1–20 preservados exatamente do balanceamento anterior.
    2: 15_000,
    3: 40_000,
    4: 90_000,
    5: 180_000,
    6: 320_000,
    7: 520_000,
    8: 800_000,
    9: 1_200_000,
    10: 1_700_000,
    11: 2_400_000,
    12: 3_300_000,
    13: 4_500_000,
    14: 6_000_000,
    15: 7_800_000,
    16: 10_000_000,
    17: 12_700_000,
    18: 15_900_000,
    19: 20_000_000,
    20: 25_000_000,
    # Expansão 0.6.6: progressão linear controlada até 100 milhões de XP.
    21: 27_500_000, 22: 30_000_000, 23: 32_500_000, 24: 35_000_000, 25: 37_500_000,
    26: 40_000_000, 27: 42_500_000, 28: 45_000_000, 29: 47_500_000, 30: 50_000_000,
    31: 52_500_000, 32: 55_000_000, 33: 57_500_000, 34: 60_000_000, 35: 62_500_000,
    36: 65_000_000, 37: 67_500_000, 38: 70_000_000, 39: 72_500_000, 40: 75_000_000,
    41: 77_500_000, 42: 80_000_000, 43: 82_500_000, 44: 85_000_000, 45: 87_500_000,
    46: 90_000_000, 47: 92_500_000, 48: 95_000_000, 49: 97_500_000, 50: 100_000_000,
}

NEXUS_NODES = {
    'nexus_level_01': dict(name='Aquisição de alvo I', description='+1 Precisão.', level=1, kind='stat', field='precision', value=1),
    'nexus_level_02': dict(name='Calibração de impacto I', description='+1 ATQ.', level=2, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_03': dict(name='Calibração de impacto II', description='+1 ATQ.', level=3, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_04': dict(name='Protocolo de coleta I', description='+10% de aumento de drop.', level=4, kind='drop', field='drop_bonus_pct', value=10.0),
    'nexus_level_05': dict(name='Protocolo de coleta II', description='+10% de aumento de drop.', level=5, kind='drop', field='drop_bonus_pct', value=10.0),
    'nexus_level_06': dict(name='Leitura de fraqueza I', description='+10% de dano de vantagem.', level=6, kind='advantage', field='advantage_bonus_pct', value=10.0),
    'nexus_level_07': dict(name='Aquisição de alvo II', description='+1 Precisão.', level=7, kind='stat', field='precision', value=1),
    'nexus_level_08': dict(name='Protocolo de coleta III', description='+10% de aumento de drop.', level=8, kind='drop', field='drop_bonus_pct', value=10.0),
    'nexus_level_09': dict(name='Calibração de impacto III', description='+1 ATQ.', level=9, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_10': dict(name='Leitura de fraqueza II', description='+10% de dano de vantagem.', level=10, kind='advantage', field='advantage_bonus_pct', value=10.0),
    'nexus_level_11': dict(name='Protocolo de coleta IV', description='+10% de aumento de drop.', level=11, kind='drop', field='drop_bonus_pct', value=10.0),
    'nexus_level_12': dict(name='Janela crítica I', description='+1% Taxa Crítica.', level=12, kind='stat', field='crit_rate_bonus', value=1.0),
    'nexus_level_13': dict(name='Aquisição de alvo III', description='+1 Precisão.', level=13, kind='stat', field='precision', value=1),
    'nexus_level_14': dict(name='Protocolo de coleta V', description='+10% de aumento de drop.', level=14, kind='drop', field='drop_bonus_pct', value=10.0),
    'nexus_level_15': dict(name='Vínculo hemático I', description='+1% Vampirismo.', level=15, kind='vampirism', field='vampirism_pct', value=1.0),
    'nexus_level_16': dict(name='Piso cinético I', description='+1 Dano Mínimo.', level=16, kind='stat', field='min_damage_bonus', value=1),
    'nexus_level_17': dict(name='Calibração de impacto IV', description='+1 ATQ.', level=17, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_18': dict(name='Leitura de fraqueza III', description='+10% de dano de vantagem.', level=18, kind='advantage', field='advantage_bonus_pct', value=10.0),
    'nexus_level_19': dict(name='Retroalimentação crítica I', description='+2% Dano Crítico.', level=19, kind='stat', field='crit_damage_bonus', value=0.02),
    'nexus_level_20': dict(name='Ressonância adaptativa I', description='+1% AMP.', level=20, kind='stat', field='amp_bonus', value=1.0),
    'nexus_level_21': dict(name='Leitura de fraqueza IV', description='+10% de dano de vantagem.', level=21, kind='advantage', field='advantage_bonus_pct', value=10.0),
    'nexus_level_22': dict(name='Calibração de impacto V', description='+1 ATQ.', level=22, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_23': dict(name='Aquisição de alvo IV', description='+1 Precisão.', level=23, kind='stat', field='precision', value=1),
    'nexus_level_24': dict(name='Vínculo hemático II', description='+1% Vampirismo.', level=24, kind='vampirism', field='vampirism_pct', value=1.0),
    'nexus_level_25': dict(name='Janela crítica II', description='+1% Taxa Crítica.', level=25, kind='stat', field='crit_rate_bonus', value=1.0),
    'nexus_level_26': dict(name='Calibração de impacto VI', description='+1 ATQ.', level=26, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_27': dict(name='Leitura de fraqueza V', description='+10% de dano de vantagem.', level=27, kind='advantage', field='advantage_bonus_pct', value=10.0),
    'nexus_level_28': dict(name='Retroalimentação crítica II', description='+2% Dano Crítico.', level=28, kind='stat', field='crit_damage_bonus', value=0.02),
    'nexus_level_29': dict(name='Aquisição de alvo V', description='+1 Precisão.', level=29, kind='stat', field='precision', value=1),
    'nexus_level_30': dict(name='Calibração de impacto VII', description='+1 ATQ.', level=30, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_31': dict(name='Ressonância adaptativa II', description='+1% AMP.', level=31, kind='stat', field='amp_bonus', value=1.0),
    'nexus_level_32': dict(name='Vínculo hemático III', description='+1% Vampirismo.', level=32, kind='vampirism', field='vampirism_pct', value=1.0),
    'nexus_level_33': dict(name='Janela crítica III', description='+1% Taxa Crítica.', level=33, kind='stat', field='crit_rate_bonus', value=1.0),
    'nexus_level_34': dict(name='Aquisição de alvo VI', description='+1 Precisão.', level=34, kind='stat', field='precision', value=1),
    'nexus_level_35': dict(name='Calibração de impacto VIII', description='+1 ATQ.', level=35, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_36': dict(name='Piso cinético II', description='+1 Dano Mínimo.', level=36, kind='stat', field='min_damage_bonus', value=1),
    'nexus_level_37': dict(name='Retroalimentação crítica III', description='+2% Dano Crítico.', level=37, kind='stat', field='crit_damage_bonus', value=0.02),
    'nexus_level_38': dict(name='Ressonância adaptativa III', description='+1% AMP.', level=38, kind='stat', field='amp_bonus', value=1.0),
    'nexus_level_39': dict(name='Aquisição de alvo VII', description='+1 Precisão.', level=39, kind='stat', field='precision', value=1),
    'nexus_level_40': dict(name='Vínculo hemático IV', description='+1% Vampirismo.', level=40, kind='vampirism', field='vampirism_pct', value=1.0),
    'nexus_level_41': dict(name='Calibração de impacto IX', description='+1 ATQ.', level=41, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_42': dict(name='Janela crítica IV', description='+1% Taxa Crítica.', level=42, kind='stat', field='crit_rate_bonus', value=1.0),
    'nexus_level_43': dict(name='Piso cinético III', description='+1 Dano Mínimo.', level=43, kind='stat', field='min_damage_bonus', value=1),
    'nexus_level_44': dict(name='Retroalimentação crítica IV', description='+2% Dano Crítico.', level=44, kind='stat', field='crit_damage_bonus', value=0.02),
    'nexus_level_45': dict(name='Aquisição de alvo VIII', description='+1 Precisão.', level=45, kind='stat', field='precision', value=1),
    'nexus_level_46': dict(name='Calibração de impacto X', description='+1 ATQ.', level=46, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_47': dict(name='Ressonância adaptativa IV', description='+1% AMP.', level=47, kind='stat', field='amp_bonus', value=1.0),
    'nexus_level_48': dict(name='Janela crítica V', description='+1% Taxa Crítica.', level=48, kind='stat', field='crit_rate_bonus', value=1.0),
    'nexus_level_49': dict(name='Calibração de impacto XI', description='+1 ATQ.', level=49, kind='stat', field='attack_bonus', value=1.0),
    'nexus_level_50': dict(name='Vínculo hemático V', description='+1% Vampirismo.', level=50, kind='vampirism', field='vampirism_pct', value=1.0),
}

OTHER_RECIPES = {
    'kit': dict(name='Kit de reparo', recipe={'Sucata':3}, description='Consumível: restaura 16 de vida.'),
    'chest_g2': dict(name='Atualizar peitoral / Tier 2', recipe={'Sucata':24,'Placa':6,'Núcleo':2}, description='Habilita módulos G2; mantém os dois encaixes de memória.'),
    'memory_g2': dict(name='Módulo avançado / 10 unidades', recipe={'Sucata':18,'Núcleo':4,'Enzima':2}, description='Exige peitoral G2 para instalar. Máximo: 2 cópias.'),
    'memory': dict(name='Módulo expandido / 7 unidades', recipe={'Sucata':12,'Núcleo':3}, description='Guarde no estoque e instale no peitoral pela tela G. Máximo: 2 cópias.'),
    'decoder_core': dict(name='Núcleo de decodificação', recipe={'Enzima':1,'Secreção':1}, description='Componente intermediário obtido pela combinação de dois drops difíceis: enzima do Lagarto das dunas e secreção do Escavador vítreo.'),
    'energy_cell': dict(name='Célula de energia instável', recipe={'Sucata':30,'Carapaça':12}, description='Célula provisória alimentada por sucata coletada e carapaças de escaravelho; exige uma reserva considerável de material comum.'),
    'water_purifier': dict(name='Purificador improvisado', recipe={'Sucata':24,'Filamento':8,'Núcleo':4,'Placa':2}, description='Sistema artesanal capaz de transformar água bruta em uma pequena reserva de água pura.'),
    'pure_water': dict(name='Água Pura', recipe={'Água Bruta':10,'Filamento':2,'Cristal de sintonia':1}, description='Reserva extremamente valiosa para a missão de Kuvaar. Produz 5 unidades.'),
    'helmet_g1': dict(name='Elmo / Tier 1', recipe={'Sucata':24,'Núcleo de decodificação':4,'Célula de energia instável':1}, description='Reconstrói o elmo e habilita análise cultural, aprendizado do Avari e futuras rotinas de Scan.'),
    'helmet_g2': dict(name='Elmo / Tier 2', recipe=HELMET_TIERS[2]['recipe'], description='Aprimora o Elmo para Tier 2, amplia as passivas e habilita o Scan de rochas.'),
    'gauntlet_nexus': dict(name=GAUNTLET_NEXUS['name'], recipe=GAUNTLET_NEXUS['recipe'], description=GAUNTLET_NEXUS['description']),
    'respawn_tank': dict(name='Tanque de Renascimento', recipe={'Essência':50}, description='Instala uma unidade de renascimento na nave. Permite retornar à nave após uma morte com perda de 10% das Essências do inventário.'),
    'combat_simulator': dict(name='Simulador de Combate', recipe={'Núcleo de Kuvaar':1,'Microchip':6,'Núcleo':4,'Placa':6}, description='Constrói um ambiente virtual capaz de reproduzir bosses já derrotados sob condições ideais.'),
    'simulation_charge': dict(name='Carga de Simulação', recipe={'Microchip':2,'Núcleo':1,'Cristal de sintonia':1}, description='Consumível técnico: uma carga inicia um rematch virtual contra um boss já derrotado.'),
}

SPAWNS = [('scarab',(4,6)),('scarab',(5,10)),('scarab',(10,8)),('lizard',(3,10)),('lizard',(11,4)),('drone',(12,11))]
NODES = [(6,9),(8,5),(4,8),(10,10)]
NODE_IDS = ['dunas_sucata_01','dunas_sucata_02','dunas_sucata_03','dunas_sucata_04']
MEMORY_MODULES = {'basic':dict(name='Módulo básico',capacity=4,generation=1), 'expanded':dict(name='Módulo expandido',capacity=7,generation=1)}
MEMORY_MODULES['advanced']=dict(name='Módulo avançado',capacity=10,generation=2)
MEMORY_RECIPES = {'memory':'expanded','memory_g2':'advanced'}
CHEST_MEMORY_SLOTS = 2

FUTURE_RESOURCES = {
    'Essência':'Essência obtida em combate e encontros espaciais. Não pode ser fabricada e é usada em Cartas Únicas.',
    'Liga meteórica':'Veios de metal condensado em zonas de queda orbital e ruínas industriais.',
    'Célula mnêmica':'Material raro encontrado em estruturas que preservam dados e memória.',
    'Núcleo de ressonância':'Componente de alta energia associado a fenômenos anômalos.',
    'Cristal de sintonia':'Cristais capazes de conduzir sinais complexos e padrões linguísticos.',
    'Filamento criônico':'Fibra estável em ambientes de temperatura extrema.',
    'Composto de pressão':'Liga flexível criada em instalações de alta pressão.',
    'Matriz fotônica':'Conjunto ótico usado por tecnologias avançadas de processamento.',
    'Núcleo de Dobra':'Componente excepcional; necessário apenas para tecnologias intergalácticas.',
    'Cinza ígnea':'Resíduo mineralizado de organismos adaptados ao calor químico de Orionis.',
    'Escama térmica':'Escama que retém calor em estruturas microscópicas.',
    'Liga ferrídea':'Metal orgânico endurecido por processos naturais de Orionis.',
    'Placa térmica':'Peça metálica capaz de operar em temperaturas extremas.',
    'Núcleo iônico':'Material energético produzido por fauna eletrocondutora.',
    'Ferrão condutor':'Estrutura biológica que concentra cargas iônicas.',
    'Pelo criônico':'Fibra resistente a ciclos extremos de congelamento e descongelamento.',
    'Garra gélida':'Queratina cristalizada de predadores de Kael.',
    'Cristal de gelo':'Cristal formado sob pressão e frio prolongado.',
    'Fragmento luminescente':'Cristal frio com emissão persistente de luz.',
    'Gel criônico':'Fluido que permanece estável abaixo de zero.',
    'Barbatana fria':'Membrana especializada para água glacial.',
    'Fibra radicular':'Fibra vegetal resistente de Nahr.',
    'Seiva cáustica':'Fluido vegetal altamente reativo.',
    'Fragmento basáltico':'Pedaço denso de rocha vulcânica.',
    'Pó vulcânico':'Mineral fino acumulado em campos basálticos.',
    'Cristal salino':'Cristal de alta pureza produzido por organismos de Nahr.',
    'Fio calcificado':'Filamento endurecido pela deposição de sais.',
    'Pelo luminal':'Fibra bioluminescente de fauna de Elyra.',
    'Fragmento fotônico':'Material que conserva energia luminosa.',
    'Pelo sombrio':'Fibra que absorve parte do espectro visível.',
    'Garra de sombra':'Estrutura biológica densa e de baixa reflexão.',
    'Esporo denso':'Concentrado orgânico de alta resistência.',
    'Membrana úmida':'Tecido orgânico estabilizado em atmosfera densa.',
    'Pedra Ígnea':'Rocha vulcânica extremamente densa, retirada das áreas mais quentes de Orionis.',
    'Núcleo Magmático':'Núcleo mineral superaquecido extraído do coração de Fagor.',
    'Núcleo de Madeira Ancestral':'Fragmento mineral-orgânico preservado no tronco de Kael.',
    'Seiva concentrada':'Seiva vegetal compactada em estruturas de altíssima energia.',
    'Núcleo de Ounull':'Concentrado aquático estabilizado após a derrota de Ounull.',
    'Pérola de Maré':'Pérola formada pela pressão e circulação de água ao redor da ilha.',
    'Núcleo de RY':'Fragmento condensado da entidade luminosa derrotada no Vazio de RY.',
    'Fragmento Luminal':'Partícula residual de luz deixada pela presença de RY.',
    'Essência de Luz':'Essência energética de alta pureza concentrada no rastro de RY.',

}
FUTURE_UPGRADES = {
    'combat_simulator': dict(name='Simulador de Combate', slot='NAVE', effect='Reproduz virtualmente bosses já derrotados sob condições favoráveis.', recipe=OTHER_RECIPES['combat_simulator']['recipe'], source='Desbloqueado após a primeira vitória de boss.'),
    'helmet_g1': dict(name='Elmo / Tier 1', slot='ELMO', effect='Análise cultural e tradução funcional do idioma local.', recipe=OTHER_RECIPES['helmet_g1']['recipe'], source='Projeto atual — Veyra.'),
    'gauntlet_nexus': dict(name=GAUNTLET_NEXUS['name'], slot='MANOPLA', effect='Habilita a senciência da manopla.', recipe=GAUNTLET_NEXUS['recipe'], source='Projeto inicial — Veyra.'),
    'chest_g3': dict(name='Peitoral / Tier 3', slot='PEITORAL', effect='Maior estabilidade do núcleo e acesso a módulos de memória de alta capacidade.', recipe={'Placa':18,'Núcleo':5,'Liga meteórica':8,'Célula mnêmica':2}, source='Projeto avançado — outros mundos.'),
    'helmet_g2': dict(name='Elmo / Tier 2', slot='ELMO', effect='Passivas ampliadas e Scan de rochas.', recipe=HELMET_TIERS[2]['recipe'], source='Primeira galáxia — materiais fora de Veyra.'),
    'locomotion_g1': dict(name='Módulo de Locomoção / Tier 1', slot='LOCOMOÇÃO', effect='Dash, mobilidade ampliada e expansão da memória operacional.', recipe={'Sucata':40,'Liga meteórica':6,'Composto de pressão':3,'Filamento criônico':2}, source='Projeto avançado — outros mundos.'),
    'memory_g3': dict(name='Circuito de memória / 12 unidades', slot='MEMÓRIA', effect='Aumenta a reserva operacional além dos circuitos atuais.', recipe={'Núcleo':5,'Sucata':30,'Célula mnêmica':2,'Núcleo de ressonância':1}, source='Projeto avançado — tecnologia não encontrada em Veyra.'),
    'ship_laser': dict(name='Emissor Laser', slot='NAVE', effect='Instala uma defesa laser para interceptar asteroides durante viagens entre galáxias.', recipe={'Sucata':30,'Placa':10,'Liga meteórica':4,'Matriz fotônica':2}, source='Projeto dos Recuperadores de Qaresh — primeiro nível de Renome e idioma Avari.'),
}

MISSION_REWARDS = {
    'kuvaar_hunt': {
        'boss': {'Núcleo de Kuvaar':1, 'Cristal de Sal':6},
    },
    'water_supply': {
        'repair': {'Válvula hidráulica':1,'Liga meteórica':2,'Placa':3},
        'force': {'Válvula hidráulica':1,'Liga meteórica':2,'Placa':2},
        'hack': {'Válvula hidráulica':1,'Liga meteórica':1,'Cristal de sintonia':1},
    }
}

ACHIEVEMENTS = {
    # As conquistas comuns concedem apenas pequenas quantidades de materiais
    # de uso recorrente, acelerando o farm sem substituir o combate/coleta.
    'first_blood': dict(category='Combate', name='Primeiro sangue', description='Derrote sua primeira criatura.', condition='kill_total', target=1, reward='Sucata ×3', reward_type='item', reward_item='Sucata', reward_amount=3),
    'desert_survivor': dict(category='Combate', name='Sobrevivente das dunas', description='Sofra 12 ou mais de dano em um único golpe e permaneça vivo.', condition='max_damage_taken', target=12, reward='Carapaça ×2', reward_type='item', reward_item='Carapaça', reward_amount=2),
    'salvager': dict(category='Exploração', name='Recuperador', description='Acumule 20 unidades de sucata coletadas.', condition='collectible', item='Sucata', target=20, reward='Escama ×3', reward_type='item', reward_item='Escama', reward_amount=3),
    'pathfinder': dict(category='Exploração', name='Cartógrafo de Veyra', description='Visite todos os mapas atualmente conhecidos de Veyra.', condition='visited_all', target=7, reward='Sucata ×4', reward_type='item', reward_item='Sucata', reward_amount=4),
    'waterkeeper': dict(category='Campanha', name='Água de volta', description='Solucione a primeira crise de abastecimento de Qaresh.', condition='missions_completed', target=1, reward='Placa ×2', reward_type='item', reward_item='Placa', reward_amount=2),
    'helmet_rebuilt': dict(category='Tecnologia', name='Visão recuperada', description='Reconstrua e equipe o elmo da armadura.', condition='helmet_equipped', target=1, reward='Sucata ×4', reward_type='item', reward_item='Sucata', reward_amount=4),
    'clean_intrusion': dict(category='Combate', name='Mãos limpas', description='Resolva uma missão por hack sem ferir nenhum habitante.', condition='mission_path', path='hack', target=1, reward='Escama ×2', reward_type='item', reward_item='Escama', reward_amount=2),
    'force_of_will': dict(category='Combate', name='Aço contra aço', description='Resolva uma missão por confronto direto.', condition='mission_path', path='force', target=1, reward='Carapaça ×3', reward_type='item', reward_item='Carapaça', reward_amount=3),
    # Somente a coleção integral de cartas concede atributos permanentes.
    'card_collector_normal': dict(category='Coleção', name='Arquivo completo', description='Possua pelo menos uma cópia normal de todas as cartas conhecidas.', condition='cards_variant', variant='normal', reward='ATQ +10', reward_type='stat', reward_stat='attack_bonus', reward_amount=10),
    'card_collector_plus': dict(category='Coleção', name='Arquivo aprimorado', description='Possua pelo menos uma cópia + de todas as cartas conhecidas.', condition='cards_variant', variant='plus', reward='Dano Crítico +6%', reward_type='stat', reward_stat='crit_damage_bonus', reward_amount=0.06),
    'card_collector_plusplus': dict(category='Coleção', name='Arquivo perfeito', description='Possua pelo menos uma cópia ++ de todas as cartas conhecidas.', condition='cards_variant', variant='plusplus', reward='AMP +5% + Carta Única futura desbloqueada', reward_type='stat_and_unique', reward_stat='amp_bonus', reward_amount=5.0),
}

# ============================================================================
# 0.6.0 — EXPANSÃO INTERGALÁCTICA
# Conteúdo novo adicionado como extensão dos catálogos existentes. As regras
# fundamentais de combate, cartas, tipos e raridades permanecem inalteradas.
# ============================================================================
# 0.7.0 — Desafios de combate e pedidos de civilizações
COMBAT_CHALLENGE_CATALOG = (
    dict(id='quick_win', name='PROTOCOLO DE IMPACTO', description='Vença o combate em até 6 turnos.', kind='turns_max', target=6, reward=20),
    dict(id='no_kit', name='INTEGRIDADE', description='Vença sem utilizar Kit de reparo.', kind='no_kit', target=0, reward=18),
    dict(id='perfect_accuracy', name='PRECISÃO ABSOLUTA', description='Vença sem errar nenhum ataque.', kind='no_miss', target=0, reward=22),
    dict(id='versatility', name='VERSATILIDADE', description='Utilize ataques de pelo menos 2 elementos diferentes.', kind='elements', target=2, reward=24),
    dict(id='combat_integrity', name='MARGEM DE SEGURANÇA', description='Finalize o combate com pelo menos 75% da Vida.', kind='hp_pct', target=75, reward=24),
    dict(id='memory_economy', name='ECONOMIA MNÊMICA', description='Finalize o combate com pelo menos 50% da Memória.', kind='memory_pct', target=50, reward=20),
    dict(id='no_plasma', name='PROTOCOLO TÉCNICO', description='Vença sem utilizar o Raio de Plasma.', kind='no_basic', target=0, reward=25),
    dict(id='critical_protocol', name='JANELA CRÍTICA', description='Vença realizando pelo menos 1 acerto crítico.', kind='critical_min', target=1, reward=26),
    dict(id='elemental_focus', name='FOCO ELEMENTAL', description='Use pelo menos 3 técnicas de cartas do mesmo elemento.', kind='same_element_attacks', target=3, reward=24),
    dict(id='safe_finish', name='FINAL LIMPO', description='Vença sem receber dano direto no último turno inimigo.', kind='no_last_damage', target=0, reward=22),
    dict(id='mixed_arsenal', name='ARSENAL DIVERSIFICADO', description='Utilize pelo menos 3 cartas diferentes durante o confronto.', kind='different_cards', target=3, reward=28),
    dict(id='vital_targeting', name='PONTO VITAL', description='Cause dano no ponto vital pelo menos uma vez.', kind='vital_hit', target=1, reward=20),
)

CIVILIZATION_MISSION_TEMPLATES = (
    dict(id='hunt_one', kind='hunt', text='Derrote {target} {species}.'),
    dict(id='hunt_two', kind='hunt', text='Elimine {target} {species}.'),
    dict(id='hunt_clean', kind='hunt', text='Reduza a presença de {species}: {target} abates.'),
    dict(id='hunt_patrol', kind='hunt', text='Faça uma patrulha contra {species}: {target} encontros vencidos.'),
    dict(id='hunt_pack', kind='hunt', text='Intercepte um pequeno grupo de {species}: {target} abates.'),
    dict(id='hunt_sweep', kind='hunt', text='Limpe uma rota de {species}: {target} criaturas eliminadas.'),
    dict(id='collect', kind='collect', text='Colete {target} unidades de {item}.'),
    dict(id='collect_more', kind='collect', text='Recupere {target} unidades de {item} para os estoques locais.'),
    dict(id='collect_route', kind='collect', text='Reforce a reserva de {item}: {target} unidades.'),
    dict(id='collect_supply', kind='collect', text='Abasteça o posto com {target} unidades de {item}.'),
    dict(id='collect_salvage', kind='collect', text='Recupere {target} unidades de {item} em depósitos locais.'),
    dict(id='collect_relay', kind='collect', text='Recupere {target} unidades de {item} para a rede de transporte.'),
    dict(id='scan', kind='scan', text='Analise {target} espécimes de {species}.'),
    dict(id='scan_field', kind='scan', text='Complete uma leitura de campo em {target} {species}.'),
    dict(id='scan_track', kind='scan', text='Registre padrões de {species}: {target} análise(s).'),
    dict(id='visit', kind='visit', text='Visite o mapa {map_name}.'),
    dict(id='visit_patrol', kind='visit', text='Faça uma passagem pelo mapa {map_name}.'),
    dict(id='visit_route', kind='visit', text='Verifique a rota local que passa por {map_name}.'),
    dict(id='deliver', kind='deliver', text='Entregue {target} unidades de {item}.'),
    dict(id='deliver_stock', kind='deliver', text='Leve {target} unidades de {item} até o estoque.'),
    dict(id='deliver_workshop', kind='deliver', text='Abasteça a oficina com {target} unidades de {item}.'),
    dict(id='mixed_hunt', kind='hunt', text='Faça uma varredura de {target} encontros com {species}.'),
    dict(id='patrol_collect', kind='collect', text='Durante a patrulha, recupere {target} unidades de {item}.'),
    dict(id='field_supply', kind='collect', text='Reforce um ponto de campo com {target} unidades de {item}.'),
)

# Ruptura de Ponto Vital: criaturas comuns possuem uma zona vital destrutível.
# O efeito é intencionalmente simples e coerente com o atributo da área atingida.
for _sid, _spec in SPECIES.items():
    _vital = _spec.get('vital_zone')
    if not _vital:
        continue
    _type = _spec.get('type')
    _zones = _spec.get('target_zones', {})
    if _vital not in _zones:
        continue
    _zone_name = _zones[_vital].get('name', _vital)
    if _vital in ('head', 'sensor') or any(token in str(_zone_name).lower() for token in ('olho','sensor','cabeça','mandíbula','boca','rosto')):
        _spec['vital_rupture'] = dict(kind='precision', value=3, description=f'Ruptura de {_zone_name}: Precisão do inimigo reduzida em 3 pontos.')
    elif _vital in ('core', 'sac') or any(token in str(_zone_name).lower() for token in ('núcleo','bolsa','saco')):
        _spec['vital_rupture'] = dict(kind='attack_pct', value=20, description=f'Ruptura de {_zone_name}: ATQ do inimigo reduzido em 20%.')
    else:
        _spec['vital_rupture'] = dict(kind='attack_pct', value=15, description=f'Ruptura de {_zone_name}: ATQ do inimigo reduzido em 15%.')

GALAXY_DISPLAY_ORDER = (GALAXY_ID, 'vharos', 'meridion')
GALAXY_DATA_060 = {
    'vharos': dict(
        id='vharos', name='Galáxia Vharos', description='Uma região de mundos minerais e tempestades carregadas, onde estruturas naturais parecem ter sido moldadas por forças magnéticas e gravitacionais.',
        theme='Frentes minerais, subsolo profundo e fenômenos de carga.',
    ),
    'meridion': dict(
        id='meridion', name='Galáxia Meridion', description='Uma galáxia de rotas antigas e mundos densamente habitados, com ecossistemas úmidos e corredores de trânsito interestelar.',
        theme='Oceanos rasos, florestas orgânicas, cânions de vento e uma cidade cosmopolita.',
    ),
}
GALAXIES.update({k: dict(v) for k,v in GALAXY_DATA_060.items()})

NEW_STELLAR_ROUTES_060 = [
    dict(id='dornak', name='Dornak', galaxy='vharos', known=False, pos=(150,255), atmosphere='Respirável / Metálica', temperature='42 °C', moons=1, initial_known_civilizations=[], landing_sector='dornak_landing'),
    dict(id='nyxara', name='Nyxara', galaxy='vharos', known=False, pos=(330,190), atmosphere='Densa / Escura', temperature='-6 °C', moons=2, initial_known_civilizations=[], landing_sector='nyxara_landing'),
    dict(id='zereth', name='Zereth', galaxy='vharos', known=False, pos=(515,275), atmosphere='Iônica / Instável', temperature='67 °C', moons=4, initial_known_civilizations=[], landing_sector='zereth_landing'),
    dict(id='pyraxis', name='Pyraxis', galaxy='vharos', known=False, pos=(380,430), atmosphere='Irrespirável / Vulcânica', temperature='289 °C', moons=0, initial_known_civilizations=[], landing_sector='pyraxis_landing'),
    dict(id='thalassene', name='Thalassene', galaxy='meridion', known=False, pos=(150,255), atmosphere='Respirável / Úmida', temperature='24 °C', moons=3, initial_known_civilizations=[], landing_sector='thalassene_landing'),
    dict(id='mycelon', name='Mycelon', galaxy='meridion', known=False, pos=(330,190), atmosphere='Densa / Esporal', temperature='18 °C', moons=1, initial_known_civilizations=[], landing_sector='mycelon_landing'),
    dict(id='tethra', name='Tethra', galaxy='meridion', known=False, pos=(515,275), atmosphere='Fina / Ventosa', temperature='9 °C', moons=2, initial_known_civilizations=[], landing_sector='tethra_landing'),
    dict(id='nerissa', name='Nerissa', galaxy='meridion', known=False, pos=(380,430), atmosphere='Respirável / Urbana', temperature='21 °C', moons=1, initial_known_civilizations=[], landing_sector='nerissa_landing'),
]
STELLAR_ROUTES.extend(NEW_STELLAR_ROUTES_060)
GALAXY_ROUTE_IDS = {gid: [r['id'] for r in STELLAR_ROUTES if r.get('galaxy') == gid] for gid in GALAXY_DISPLAY_ORDER}
GALAXY_CONNECTIONS = {
    'local': (('veyra','orionis'),('orionis','kael'),('kael','nahr'),('kael','elyra'),('elyra','veyra')),
    'vharos': (('dornak','nyxara'),('nyxara','zereth'),('zereth','pyraxis'),('pyraxis','dornak')),
    'meridion': (('thalassene','mycelon'),('mycelon','tethra'),('tethra','nerissa'),('nerissa','thalassene')),
}
BOSS_ARENAS.update({
    'dornak':'dornak_core_mine', 'nyxara':'nyxara_abyssal_burrow', 'zereth':'zereth_skyspine', 'pyraxis':'pyraxis_caldera',
    'thalassene':'thalassene_tidemaw', 'mycelon':'mycelon_heartgrove', 'tethra':'tethra_monolith', 'nerissa':'nerissa_tower_crown',
})

CIVILIZATIONS_060 = {
    'dran': dict(id='dran', name='Draan', language='Draen', culture='Uma linhagem mineradora que trata metal, memória industrial e contratos de troca como patrimônio coletivo.', visual='Trajes reforçados, placas metálicas leves e máscaras de filtragem magnética.'),
    'nyxen': dict(id='nyxen', name='Nyxen', language='Nyx', culture='Uma população noturna que organiza sua memória por marcas luminescentes e mapas do céu vistos de cavernas profundas.', visual='Mantos escuros, adornos bioluminescentes e pequenos emissores de luz.'),
    'velkari': dict(id='velkari', name='Velkari', language='Velkar', culture='Navegadores de águas rasas e plataformas flutuantes, especializados em rotas de maré e comércio entre ilhas.', visual='Roupas leves impermeáveis, fibras marinhas e peças de navegação.'),
    'mycelari': dict(id='mycelari', name='Mycelari', language='Mycel', culture='Comunidades simbióticas que registram histórias por redes de esporos e padrões de crescimento vegetal.', visual='Tecidos orgânicos, placas porosas e adornos feitos de fibras fúngicas.'),
    'tethran': dict(id='tethran', name='Tethran', language='Tethri', culture='Clãs nômades das correntes de ar que constroem torres de navegação e trocam mapas de vento.', visual='Capuzes aerodinâmicos, faixas longas e equipamentos de escalada.'),
    'nerissans': dict(id='nerissans', name='Consórcio Nerissano', language='Neris', culture='Uma sociedade urbana cosmopolita formada por múltiplas espécies, com comércio, transporte e diplomacia interplanetária.', visual='Indumentária variada; cada distrito mistura estilos, materiais e símbolos de vários mundos.'),
}
CIVILIZATIONS = {'avarin': CIVILIZATION, 'nahr_shadows': NAHR_CIVILIZATION, **CIVILIZATIONS_060}

# Fauna nova: 2 espécies regulares por planeta, mantendo a estrutura de duas
# ações (básico + técnica) e as partes corporais já usadas no combate.
SPECIES.update({
    'ferrous_mite': dict(type='Metal', name='Ácaro Ferrídeo', hp=176, attack=(7,9), skill_attack=(2,3), defense=8, precision=14, amp=0.0,
        target_zones={'body':dict(name='Carapaça', defense=8, evasion=0),'head':dict(name='Mandíbula', defense=6, evasion=12),'core':dict(name='Núcleo magnético', defense=5, evasion=20)},
        crit_rate=4.0, crit_damage=1.42, respawn=220, card='ferrous_mite_card', vital_zone='core', color=(118,130,139), drops=[('Liga ferrídea',.65,1,2),('Sucata',.72,1,3)]),
    'magnetic_ram': dict(type='Terra', name='Carneiro Magnético', hp=192, attack=(8,10), skill_attack=(2,3), defense=9, precision=13, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=9, evasion=0),'head':dict(name='Chifres', defense=6, evasion=15),'leg':dict(name='Pata', defense=6, evasion=12)},
        crit_rate=4.0, crit_damage=1.40, respawn=240, card='magnetic_ram_card', vital_zone='head', color=(112,111,104), drops=[('Composto de pressão',.60,1,2),('Liga ferrídea',.30,1,1)]),
    'gloom_moth': dict(type='Trevas', name='Mariposa do Breu', hp=158, attack=(7,9), skill_attack=(2,3), defense=6, precision=16, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=6, evasion=0),'head':dict(name='Cabeça', defense=4, evasion=16),'wing':dict(name='Ala', defense=4, evasion=19)},
        crit_rate=6.0, crit_damage=1.45, respawn=210, card='gloom_moth_card', vital_zone='head', color=(73,69,83), drops=[('Pelo sombrio',.58,1,2),('Garra de sombra',.18,1,1)]),
    'vesper_cat': dict(type='Trevas', name='Felino Vespertino', hp=205, attack=(8,11), skill_attack=(2,4), defense=7, precision=17, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=7, evasion=0),'head':dict(name='Rosto', defense=5, evasion=17),'claw':dict(name='Garra', defense=4, evasion=21)},
        crit_rate=6.0, crit_damage=1.48, respawn=260, card='vesper_cat_card', vital_zone='head', color=(61,54,76), drops=[('Garra de sombra',.55,1,2),('Pelo sombrio',.40,1,2)]),
    'charge_ray': dict(type='Elétrico', name='Raia de Carga', hp=170, attack=(8,10), skill_attack=(2,3), defense=7, precision=17, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=7, evasion=0),'head':dict(name='Sensor', defense=5, evasion=16),'fin':dict(name='Barbatana', defense=5, evasion=19)},
        crit_rate=6.0, crit_damage=1.45, respawn=220, card='charge_ray_card', vital_zone='head', color=(72,126,153), drops=[('Núcleo iônico',.62,1,2),('Ferrão condutor',.18,1,1)]),
    'ion_toad': dict(type='Elétrico', name='Sapo Iônico', hp=214, attack=(8,11), skill_attack=(2,4), defense=8, precision=15, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=8, evasion=0),'head':dict(name='Cabeça', defense=6, evasion=15),'sac':dict(name='Saco de carga', defense=5, evasion=20)},
        crit_rate=5.0, crit_damage=1.46, respawn=250, card='ion_toad_card', vital_zone='sac', color=(77,132,101), drops=[('Núcleo iônico',.66,1,2),('Cristal de sintonia',.12,1,1)]),
    'cinder_strider': dict(type='Fogo', name='Corredor de Brasa', hp=185, attack=(9,11), skill_attack=(2,4), defense=7, precision=15, amp=0.0,
        target_zones={'body':dict(name='Carapaça', defense=7, evasion=0),'head':dict(name='Cabeça', defense=5, evasion=15),'leg':dict(name='Perna', defense=5, evasion=18)},
        crit_rate=5.0, crit_damage=1.44, respawn=210, card='cinder_strider_card', vital_zone='head', color=(159,73,48), drops=[('Cinza ígnea',.70,1,2),('Pó vulcânico',.35,1,2)]),
    'magma_beetle': dict(type='Fogo', name='Besouro Magmático', hp=228, attack=(9,12), skill_attack=(3,4), defense=10, precision=14, amp=0.0,
        target_zones={'body':dict(name='Carapaça', defense=10, evasion=0),'head':dict(name='Cabeça', defense=7, evasion=15),'core':dict(name='Bolsa magmática', defense=6, evasion=22)},
        crit_rate=5.0, crit_damage=1.48, respawn=280, card='magma_beetle_card', vital_zone='core', color=(122,61,44), drops=[('Núcleo Magmático',.22,1,1),('Pó vulcânico',.65,1,2)]),
    'reef_skimmer': dict(type='Água', name='Deslizador de Recife', hp=180, attack=(7,9), skill_attack=(2,3), defense=6, precision=15, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=6, evasion=0),'head':dict(name='Boca', defense=5, evasion=14),'fin':dict(name='Aleta', defense=4, evasion=18)},
        crit_rate=4.0, crit_damage=1.42, respawn=190, card='reef_skimmer_card', vital_zone='head', color=(72,145,171), drops=[('Pérola de Maré',.22,1,1),('Membrana úmida',.60,1,2)]),
    'tide_serpent': dict(type='Água', name='Serpente de Maré', hp=222, attack=(8,11), skill_attack=(2,4), defense=7, precision=16, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=7, evasion=0),'head':dict(name='Cabeça', defense=5, evasion=16),'crest':dict(name='Crista', defense=5, evasion=19)},
        crit_rate=5.0, crit_damage=1.46, respawn=260, card='tide_serpent_card', vital_zone='head', color=(60,119,146), drops=[('Barbatana fria',.54,1,2),('Pérola de Maré',.16,1,1)]),
    'spore_hare': dict(type='Planta', name='Lebre Esporal', hp=168, attack=(7,9), skill_attack=(2,3), defense=6, precision=16, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=6, evasion=0),'head':dict(name='Cabeça', defense=4, evasion=15),'ear':dict(name='Orelha', defense=3, evasion=20)},
        crit_rate=5.0, crit_damage=1.42, respawn=200, card='spore_hare_card', vital_zone='head', color=(82,126,73), drops=[('Esporo denso',.62,1,2),('Fibra radicular',.30,1,2)]),
    'mycelial_beast': dict(type='Planta', name='Fera Micelial', hp=238, attack=(9,11), skill_attack=(3,4), defense=9, precision=14, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=9, evasion=0),'head':dict(name='Cogumelo central', defense=6, evasion=17),'root':dict(name='Raiz', defense=6, evasion=19)},
        crit_rate=5.0, crit_damage=1.48, respawn=290, card='mycelial_beast_card', vital_zone='head', color=(80,111,79), drops=[('Seiva cáustica',.24,1,1),('Esporo denso',.70,1,3)]),
    'wind_stalker': dict(type='Terra', name='Rastreador de Vendaval', hp=176, attack=(8,10), skill_attack=(2,3), defense=7, precision=18, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=7, evasion=0),'head':dict(name='Cabeça', defense=5, evasion=18),'wing':dict(name='Membro de vento', defense=5, evasion=21)},
        crit_rate=5.0, crit_damage=1.45, respawn=220, card='wind_stalker_card', vital_zone='head', color=(103,117,128), drops=[('Composto de pressão',.60,1,2),('Filamento criônico',.18,1,1)]),
    'leviwing': dict(type='Luz', name='Asa Leviatã', hp=214, attack=(8,11), skill_attack=(2,4), defense=7, precision=17, amp=0.0,
        target_zones={'body':dict(name='Corpo', defense=7, evasion=0),'head':dict(name='Olho', defense=5, evasion=17),'wing':dict(name='Asa', defense=5, evasion=20)},
        crit_rate=6.0, crit_damage=1.50, respawn=270, card='leviwing_card', vital_zone='head', color=(123,161,176), drops=[('Fragmento luminescente',.62,1,2),('Pelo luminal',.30,1,1)]),
    'street_drone': dict(type='Metal', name='Drone de Rua', hp=185, attack=(8,10), skill_attack=(2,3), defense=8, precision=17, amp=0.0,
        target_zones={'body':dict(name='Chassi', defense=8, evasion=0),'sensor':dict(name='Sensor', defense=5, evasion=17),'arm':dict(name='Braço', defense=6, evasion=19)},
        crit_rate=5.0, crit_damage=1.45, respawn=240, card='street_drone_card', vital_zone='sensor', color=(106,121,132), drops=[('Microchip',.20,1,1),('Placa',.65,1,2)]),
    'plasma_hound': dict(type='Elétrico', name='Cão de Plasma', hp=224, attack=(9,11), skill_attack=(2,4), defense=7, precision=18, amp=0.0,
        target_zones={'body':dict(name='Tronco', defense=7, evasion=0),'head':dict(name='Cabeça', defense=5, evasion=18),'core':dict(name='Núcleo', defense=5, evasion=21)},
        crit_rate=6.0, crit_damage=1.48, respawn=260, card='plasma_hound_card', vital_zone='core', color=(76,129,158), drops=[('Núcleo iônico',.62,1,2),('Ferrão condutor',.25,1,1)]),
})

# Convenção de vitalidade: as zonas vitais novas seguem o marcador explícito
# usado pela camada de combate para exibição/análise.
for _sid in (
    'ferrous_mite','magnetic_ram','gloom_moth','vesper_cat','charge_ray','ion_toad',
    'cinder_strider','magma_beetle','reef_skimmer','tide_serpent','spore_hare','mycelial_beast',
    'wind_stalker','leviwing','street_drone','plasma_hound',
):
    _spec = SPECIES[_sid]
    _vital = _spec.get('vital_zone')
    if _vital in _spec.get('target_zones', {}):
        _spec['target_zones'][_vital]['vital'] = True

# Cartas das 16 criaturas novas. Cada carta recebe exatamente um bônus
# permanente compatível com sua raridade. Os efeitos de combate continuam
# sendo opcionais e não concedem DEF permanente.
def _card060(cid, name, species, rarity, damage, amp, attr_key, attr_value, card_type=None, **extra):
    attrs = {attr_key: attr_value}
    effect = extra.pop('effect', {}) or {}
    base = dict(name=format_card_name(name), type=card_type or SPECIES[species]['type'], rarity=rarity, cost=extra.pop('cost', 3), damage=damage,
                skill_amp=amp, species=species, target_mode=extra.pop('target_mode','single'), attributes=attrs,
                description=extra.pop('description', 'Técnica da criatura registrada no banco de combate.'))
    # Efeitos de combate usam as chaves já consumidas pelo motor central.
    # Mantemos tudo no mesmo nível do dicionário da carta, como nas cartas 0.5.9.
    base.update(effect)
    base.update(extra)
    return base
CARDS.update({
    'ferrous_mite_card': _card060('ferrous_mite_card','Corte Ferrídeo','ferrous_mite','Comum',(9,12),0.40,'attack_pct',3.0, cost=3, effect={'attack_reduction_pct':10, 'attack_reduction_chance':100}, description='Golpe que reduz em 10% o ATQ do próximo ataque inimigo.', recipe={'Liga ferrídea':6,'Sucata':8}),
    'magnetic_ram_card': _card060('magnetic_ram_card','Aríete Magnético','magnetic_ram','Comum',(10,13),0.42,'crit_rate',3.0, cost=3, effect={'shield_ratio':0.15}, description='O impacto converte 15% do dano causado em escudo para o usuário.', recipe={'Composto de pressão':6,'Liga ferrídea':2}),
    'gloom_moth_card': _card060('gloom_moth_card','Asa do Breu','gloom_moth','Comum',(9,12),0.40,'crit_damage',0.05, cost=3, effect={'attack_crit_damage_bonus':0.15}, description='Este ataque recebe +15% de Dano Crítico.', recipe={'Pelo sombrio':7,'Garra de sombra':1}),
    'vesper_cat_card': _card060('vesper_cat_card','Garra Vespertina','vesper_cat','Incomum',(12,16),0.48,'attack_pct',5.0, cost=4, effect={'attack_crit_rate_bonus':20.0}, description='Este ataque recebe +20% de Taxa Crítica.', recipe={'Garra de sombra':5,'Pelo sombrio':4}),
    'charge_ray_card': _card060('charge_ray_card','Arco de Carga','charge_ray','Comum',(9,13),0.43,'crit_rate',3.0, cost=3, effect={'stun_chance':25,'status_duration':1}, description='25% de chance de causar Atordoamento por 1 turno.', recipe={'Núcleo iônico':7,'Ferrão condutor':1}),
    'ion_toad_card': _card060('ion_toad_card','Salto Iônico','ion_toad','Incomum',(12,17),0.50,'crit_damage',0.10, cost=4, effect={'stun_chance':40,'status_duration':1}, description='40% de chance de causar Atordoamento por 1 turno.', recipe={'Núcleo iônico':8,'Cristal de sintonia':1}),
    'cinder_strider_card': _card060('cinder_strider_card','Passo Incandescente','cinder_strider','Comum',(10,14),0.44,'attack_pct',3.0, cost=3, effect={'burn_chance':30,'burn_damage':2,'burn_turns':2}, description='30% de chance de causar Queimadura por 2 turnos.', recipe={'Cinza ígnea':7,'Pó vulcânico':4}),
    'magma_beetle_card': _card060('magma_beetle_card','Mordida de Escória','magma_beetle','Incomum',(13,17),0.52,'attack_pct',5.0, cost=4, effect={'burn_chance':40,'burn_damage':3,'burn_turns':2}, description='40% de chance de causar Queimadura por 2 turnos.', recipe={'Núcleo Magmático':1,'Pó vulcânico':6,'Cinza ígnea':4}),
    'reef_skimmer_card': _card060('reef_skimmer_card','Corte de Maré','reef_skimmer','Comum',(9,12),0.42,'crit_rate',3.0, cost=3, effect={'drowning_chance':50}, description='50% de chance de causar Afogamento. O próximo ataque especial do alvo custa o dobro.', recipe={'Pérola de Maré':1,'Membrana úmida':8}),
    'tide_serpent_card': _card060('tide_serpent_card','Presa Abissal','tide_serpent','Incomum',(12,16),0.48,'crit_damage',0.10, cost=4, effect={'drowning_chance':100}, description='Causa Afogamento. O próximo ataque especial do alvo custa o dobro.', recipe={'Barbatana fria':6,'Pérola de Maré':1}),
    'spore_hare_card': _card060('spore_hare_card','Estouro Esporal II','spore_hare','Comum',(9,13),0.43,'attack_pct',3.0, cost=3, effect={'next_attack_type':'Planta','next_attack_type_damage_bonus':10.0}, description='Se seu próximo ataque for de Planta, ele causa 10% a mais de dano.', recipe={'Esporo denso':7,'Fibra radicular':2}),
    'mycelial_beast_card': _card060('mycelial_beast_card','Garras Miceliais','mycelial_beast','Incomum',(13,18),0.50,'crit_rate',5.0, cost=4, target_mode='multi', effect={'next_attack_type':'Planta','next_attack_type_damage_bonus':15.0}, description='Atinge múltiplos alvos. Se seu próximo ataque for de Planta, ele causa 15% a mais de dano.', recipe={'Esporo denso':8,'Seiva cáustica':1,'Fibra radicular':2}),
    'wind_stalker_card': _card060('wind_stalker_card','Talho de Vendaval','wind_stalker','Comum',(10,14),0.44,'crit_damage',0.05, cost=3, effect={'shield_ratio':0.15}, description='O impacto converte 15% do dano causado em escudo para o usuário.', recipe={'Composto de pressão':7,'Filamento criônico':1}),
    'leviwing_card': _card060('leviwing_card','Mergulho de Luz','leviwing','Incomum',(12,16),0.49,'attack_pct',5.0, cost=4, effect={'heal_ratio':0.03}, description='Recupera 3% do dano causado em Vida.', recipe={'Fragmento luminescente':7,'Pelo luminal':1}),
    'street_drone_card': _card060('street_drone_card','Pulso de Rua','street_drone','Comum',(9,12),0.41,'crit_rate',3.0, cost=3, effect={'attack_reduction_pct':10, 'attack_reduction_chance':100}, description='Reduz em 10% o ATQ do próximo ataque inimigo.', recipe={'Placa':8,'Microchip':1,'Sucata':8}),
    'plasma_hound_card': _card060('plasma_hound_card','Caçada Prismática','plasma_hound','Incomum',(13,18),0.50,'crit_damage',0.10, cost=4, effect={'stun_chance':40,'status_duration':1}, description='40% de chance de causar Atordoamento por 1 turno.', recipe={'Núcleo iônico':8,'Ferrão condutor':2}),
})

# A extensão 0.6.0 foi adicionada depois da normalização geral de combate da 0.5.9.
# Reaplicamos aqui o mesmo contrato básico+especial+mana para as 16 espécies novas,
# sem criar uma regra de combate diferente para elas.
for _sid in (
    'ferrous_mite','magnetic_ram','gloom_moth','vesper_cat','charge_ray','ion_toad',
    'cinder_strider','magma_beetle','reef_skimmer','tide_serpent','spore_hare','mycelial_beast',
    'wind_stalker','leviwing','street_drone','plasma_hound',
):
    _spec = SPECIES[_sid]
    _cid = _spec.get('card')
    _card = CARDS.get(_cid, {})
    _profile = dict(CREATURE_MANA_PROFILES.get(_card.get('rarity'), CREATURE_MANA_PROFILES['Comum']))
    _spec.update({
        'basic_attack': tuple(_spec.get('attack', (0,0))),
        'special_attack': tuple(_card.get('damage', _spec.get('skill_attack',(0,0)))),
        'special_attack_card': _cid,
        'special_attack_name': _card.get('name', ''),
        **_profile,
    })

# Os 6 bosses raros necessários para a progressão existem antes dos dois
# lendários; os tipos novos Metal/Trevas/Elétrico recebem prioridade no primeiro arco.
BOSSES.update({
    'mekron': dict(type='Metal', name='Mekron, o Colosso Magnético', hp=520, attack=(12,15), skill_attack=(4,6), defense=24, precision=18, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Blindagem',defense=24,evasion=0),'head':dict(name='Sensor Central',defense=18,evasion=17),'core':dict(name='Núcleo Magnético',defense=16,evasion=23)},
        crit_rate=7.0, crit_damage=1.58, card='mekron', vital_zone='core', special_attack_card='mekron', drops=[('Núcleo iônico',.75,2,4),('Liga ferrídea',1.0,3,5),('Placa',.65,2,4)],
        rare=True, galaxy='vharos', auto_card_drop=True),
    'nocther': dict(type='Trevas', name='Nocther, o Predador do Eclipse', hp=500, attack=(13,16), skill_attack=(4,7), defense=22, precision=20, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Torso',defense=22,evasion=0),'mask':dict(name='Máscara',defense=16,evasion=18),'claw':dict(name='Garra',defense=14,evasion=25)},
        crit_rate=8.0, crit_damage=1.62, card='nocther', vital_zone='mask', special_attack_card='nocther', drops=[('Pelo sombrio',.90,2,4),('Garra de sombra',1.0,2,4),('Núcleo de ressonância',.18,1,1)],
        rare=True, galaxy='vharos', auto_card_drop=True),
    'voltrik': dict(type='Elétrico', name='Voltrik, a Tempestade Viva', hp=540, attack=(12,16), skill_attack=(4,7), defense=20, precision=22, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Corpo',defense=20,evasion=0),'horn':dict(name='Antena',defense=14,evasion=20),'core':dict(name='Núcleo de Carga',defense=13,evasion=24)},
        crit_rate=9.0, crit_damage=1.60, card='voltrik', vital_zone='core', special_attack_card='voltrik', drops=[('Núcleo iônico',1.0,3,5),('Ferrão condutor',.85,2,4),('Cristal de sintonia',.20,1,1)],
        rare=True, galaxy='vharos', auto_card_drop=True),
    'moryss': dict(type='Água', name='Moryss, a Boca da Maré', hp=530, attack=(12,15), skill_attack=(4,6), defense=21, precision=18, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Corpo',defense=21,evasion=0),'head':dict(name='Mandíbula',defense=16,evasion=19),'fin':dict(name='Aleta dorsal',defense=14,evasion=22)},
        crit_rate=7.0, crit_damage=1.56, card='moryss', vital_zone='head', special_attack_card='moryss', drops=[('Pérola de Maré',.55,1,2),('Barbatana fria',1.0,2,4),('Cristal de sintonia',.25,1,1)],
        rare=True, galaxy='meridion', auto_card_drop=True),
    'verdak': dict(type='Planta', name='Verdak, o Coração Esporal', hp=560, attack=(11,15), skill_attack=(4,7), defense=23, precision=17, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Tronco',defense=23,evasion=0),'crown':dict(name='Copa',defense=17,evasion=18),'root':dict(name='Raiz-mãe',defense=14,evasion=21)},
        crit_rate=7.0, crit_damage=1.58, card='verdak', vital_zone='crown', special_attack_card='verdak', drops=[('Esporo denso',1.0,3,5),('Fibra radicular',.95,2,4),('Seiva concentrada',.20,1,1)],
        rare=True, galaxy='meridion', auto_card_drop=True),
    'gravorn': dict(type='Terra', name='Gravorn, o Monólito Errante', hp=590, attack=(13,17), skill_attack=(4,6), defense=26, precision=16, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Maciço',defense=26,evasion=0),'face':dict(name='Face',defense=19,evasion=16),'joint':dict(name='Articulação',defense=16,evasion=23)},
        crit_rate=6.0, crit_damage=1.55, card='gravorn', vital_zone='face', special_attack_card='gravorn', drops=[('Fragmento basáltico',1.0,3,5),('Composto de pressão',.65,2,3),('Núcleo de ressonância',.18,1,1)],
        rare=True, galaxy='meridion', auto_card_drop=True),
    'alphor': dict(type='Fogo', name='Alphor, o Balrog', hp=1650, attack=(16,21), skill_attack=(6,9), defense=30, precision=19, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={
            'body':dict(name='Corpo Demoníaco',defense=30,evasion=0),
            'horn_left':dict(name='Chifre Esquerdo',defense=22,evasion=19,hp_key='horn_left',hp=180),
            'horn_right':dict(name='Chifre Direito',defense=22,evasion=19,hp_key='horn_right',hp=180),
            'fire_core':dict(name='Núcleo Ígneo',defense=18,evasion=25,hp_key='fire_core',hp=300,exposed_only=True,damage_multiplier=1.15),
        },
        initial_target='body', crit_rate=10.0, crit_damage=1.68, card='alphor_fireball', vital_zone='fire_core', special_attack_card='alphor_fireball',
        drops=[('Núcleo Magmático',1.0,2,3),('Cinza ígnea',1.0,5,8),('Fragmento basáltico',.75,2,4)], legendary=True, galaxy='vharos', gate_rare=('mekron','nocther','voltrik'), auto_card_drop=True,
        mechanic='Os dois chifres precisam ser rompidos para expor o Núcleo Ígneo. A técnica é uma bola de fogo contra todos os alvos.'),
    'broom': dict(type='Elétrico', name='Broom, o Samurai Celeste', hp=1500, attack=(17,22), skill_attack=(7,10), defense=28, precision=24, mana_max=24, mana_cost=8,
        special_chance=60.0, target_zones={'body':dict(name='Corpo',defense=28,evasion=0),'blade_arm':dict(name='Braço de Lâmina',defense=22,evasion=17),'visor':dict(name='Visor',defense=18,evasion=21)},
        initial_target='body', crit_rate=11.0, crit_damage=1.72, card='broom_lightning', vital_zone='body', special_attack_card='broom_lightning',
        drops=[('Núcleo iônico',1.0,3,5),('Núcleo de ressonância',.75,1,2),('Liga meteórica',.55,2,3)], legendary=True, galaxy='meridion', gate_rare=('moryss','verdak','gravorn'), auto_card_drop=True,
        fatal_attack=True, fatal_window=7.0, fatal_key='Q', mechanic='A técnica fatal é telegrafada após duas ações básicas de Broom. O Escudo Stasis pode bloquear o golpe na janela QTE.'),
})

# Cartas de boss. As raras seguem a regra fixa de um único atributo; as duas
# lendárias seguem o mesmo princípio e incorporam suas técnicas características.
CARDS.update({
    'mekron': dict(name='Pulso Ferrídeo', type='Metal', rarity='Rara', cost=4, damage=(16,21), skill_amp=.65, species='mekron', target_mode='single', attributes={'crit_rate':10.0}, description='Pulso magnético concentrado do Colosso.', acquisition='boss_defeat', craftable=True, recipe={'Núcleo iônico':1,'Liga ferrídea':4,'Placa':10}),
    'nocther': dict(name='Eclipse Predatório', type='Trevas', rarity='Rara', cost=4, damage=(15,20), skill_amp=.66, species='nocther', target_mode='single', attributes={'crit_damage':.20}, description='O eclipse comprime luz e sombra em um único impacto.', acquisition='boss_defeat', craftable=True, recipe={'Pelo sombrio':4,'Garra de sombra':2,'Núcleo de ressonância':1}),
    'voltrik': dict(name='Arco Tempestuoso', type='Elétrico', rarity='Rara', cost=4, damage=(17,22), skill_amp=.70, species='voltrik', target_mode='single', attributes={'attack_pct':10.0}, stun_chance=30, status_duration=1, description='Arco de carga com 30% de chance de Atordoamento por 1 turno.', acquisition='boss_defeat', craftable=True, recipe={'Núcleo iônico':2,'Ferrão condutor':3,'Cristal de sintonia':1}),
    'moryss': dict(name='Maré Reversa', type='Água', rarity='Rara', cost=4, damage=(16,21), skill_amp=.65, species='moryss', target_mode='single', attributes={'attack_pct':10.0}, drowning_chance=100, description='Aplica Afogamento: o próximo ataque especial do oponente custa o dobro.', acquisition='boss_defeat', craftable=True, recipe={'Pérola de Maré':2,'Barbatana fria':4,'Cristal de sintonia':1}),
    'verdak': dict(name='Esporo Predador', type='Planta', rarity='Rara', cost=5, damage=(15,20), skill_amp=.62, species='verdak', target_mode='multi', attributes={'crit_damage':.20}, description='Nuvem de esporos que atinge todos os alvos.', acquisition='boss_defeat', craftable=True, recipe={'Esporo denso':4,'Fibra radicular':4,'Seiva concentrada':2}),
    'gravorn': dict(name='Impacto Monolítico', type='Terra', rarity='Rara', cost=5, damage=(18,23), skill_amp=.72, species='gravorn', target_mode='single', attributes={'attack_pct':10.0}, description='Golpe denso que concentra a massa do monólito.', acquisition='boss_defeat', craftable=True, recipe={'Fragmento basáltico':4,'Composto de pressão':3,'Núcleo de ressonância':1}),
    'alphor_fireball': dict(name='Bola de Fogo de Alphor', type='Fogo', rarity='Lendária', cost=8, damage=(36,48), skill_amp=.90, species='alphor', target_mode='multi', attributes={'attack_pct':20.0}, description='Uma bola de fogo colossal explode sobre todos os alvos.', acquisition='boss_defeat', craftable=True, recipe={'Núcleo Magmático':2,'Cinza ígnea':8,'Fragmento basáltico':4}),
    'broom_lightning': dict(name='Raio de Broom', type='Elétrico', rarity='Lendária', cost=8, damage=(34,44), skill_amp=.95, species='broom', target_mode='single', attributes={'crit_damage':.40}, execution_threshold=.25, description='Um raio cai sobre um único alvo. Abaixo de 25% da Vida do alvo, executa-o imediatamente.', acquisition='boss_defeat', craftable=True, recipe={'Núcleo iônico':3,'Núcleo de ressonância':2,'Liga meteórica':4}),
})
# Identidade visual das técnicas. Cada técnica possui uma linguagem visual própria,
# coerente com seu nome/efeito, sem alterar dano, custo, raridade ou regras de combate.
# O campo é consumido apenas pelo renderizador visual da batalha.
CARD_VISUAL_KEYS = {
    'shell': 'silica_shard',
    'bite': 'sand_bite',
    'static': 'electric_burst',
    'hound': 'silica_charge',
    'burrow': 'glass_break',
    'manta': 'dust_dive',
    'stalker': 'prism_rend',
    'guard_strike': 'guard_strike',
    'lithic_sentence': 'monolith_sentence',
    'rift_break': 'rift_break',
    'kuvaar': 'saline_dissolution',
    'fagor': 'fireball',
    'kael': 'root_vigor',
    'ounull': 'water_flux',
    'ry': 'luminous_fulgor',
    'ounull_tide': 'water_tide',
    'magma_lance': 'magma_spear',
    'forge_claw': 'forge_pincer',
    'ion_burst': 'ion_burst',
    'frost_bite': 'frost_bite',
    'crystal_ram': 'crystal_fragment',
    'glacial_gust': 'frost_wind',
    'root_spear': 'root_spear',
    'basalt_charge': 'basalt_boulder',
    'salt_spit': 'salt_spit',
    'luminous_ray': 'luminous_ray',
    'umbra_claw': 'umbra_claw',
    'spore_burst': 'spore_cloud',
    'ferrous_mite_card': 'iron_cut',
    'magnetic_ram_card': 'magnetic_ram',
    'gloom_moth_card': 'gloom_wing',
    'vesper_cat_card': 'vesper_claw',
    'charge_ray_card': 'charge_arc',
    'ion_toad_card': 'ion_jump',
    'cinder_strider_card': 'ember_dash',
    'magma_beetle_card': 'scoria_bite',
    'reef_skimmer_card': 'tide_cut',
    'tide_serpent_card': 'abyss_fang',
    'spore_hare_card': 'spore_burst',
    'mycelial_beast_card': 'mycelial_claws',
    'wind_stalker_card': 'wind_slash',
    'leviwing_card': 'light_dive',
    'street_drone_card': 'street_pulse',
    'plasma_hound_card': 'prismatic_hunt',
    'mekron': 'magnetic_pulse',
    'nocther': 'eclipse',
    'voltrik': 'storm_arc',
    'moryss': 'reverse_tide',
    'verdak': 'predator_spore',
    'gravorn': 'monolithic_impact',
    'alphor_fireball': 'fireball_colossal',
    'broom_lightning': 'broom_lightning',
}
for _cid, _visual in CARD_VISUAL_KEYS.items():
    if _cid in CARDS:
        CARDS[_cid]['visual_key'] = _visual

# Reaponta os catálogos dos bosses após a extensão dos cartões.
for _bid, _boss in BOSSES.items():
    if _boss.get('special_attack_card') and _boss['special_attack_card'] in CARDS:
        _boss['special_attack'] = tuple(CARDS[_boss['special_attack_card']].get('damage', _boss.get('skill_attack',(0,0))))
        _boss['special_attack_name'] = CARDS[_boss['special_attack_card']].get('name', _boss.get('special_attack_name',''))

GALAXY_RARE_BOSSES = {
    'vharos': ('mekron','nocther','voltrik'),
    'meridion': ('moryss','verdak','gravorn'),
}
GALAXY_LEGENDARY_BOSSES = {'vharos':'alphor', 'meridion':'broom'}
NEW_060_BOSSES = tuple(GALAXY_RARE_BOSSES['vharos'] + GALAXY_RARE_BOSSES['meridion'] + ('alphor','broom'))
for _bid in NEW_060_BOSSES:
    _boss = BOSSES.get(_bid, {})
    _boss.setdefault('basic_attack', tuple(_boss.get('attack', (0, 0))))

# Recurso/técnica de instalação do motor. O item é o mesmo drop garantido de RY;
# não é duplicado, fabricado ou gerado pelo simulador.
OTHER_RECIPES['dobra_core_install'] = dict(name='Instalar Núcleo de Dobra', recipe={'Núcleo de Dobra':1}, description='Instala o núcleo recuperado de RY no motor da nave e habilita a dobra espacial intergaláctica.')
FUTURE_UPGRADES['dobra_core_install'] = dict(name='Motor de Dobra — Núcleo instalado', slot='NAVE', effect='Habilita viagens para outras galáxias.', recipe=OTHER_RECIPES['dobra_core_install']['recipe'], source='Núcleo de Dobra obtido após a derrota real de RY.')


def creature_achievement_id(species_id):
    return f'creature_1000_{species_id}'

def creature_achievement_data(species_id):
    spec = SPECIES.get(species_id)
    if not spec:
        return None
    card_id = spec.get('card')
    card = CARDS.get(card_id, {})
    card_name = format_card_name(card.get('name', spec.get('name', species_id)))
    return dict(
        category='Combate',
        name=f'Derrotar 1000 {spec["name"]}',
        description=f'Derrote {spec["name"]} 1000 vezes.',
        condition='species_kills', species=species_id, target=1000,
        reward=f'Carta + de {card_name}', reward_type='card_variant',
        reward_card=card_id, reward_variant='plus'
    )


# Garantia de compatibilidade da Ruptura de Ponto Vital: este complemento é
# aplicado depois de TODOS os SPECIES.update da 0.6.0/0.7.0.
# Cada criatura que possui zona vital recebe o efeito correspondente à natureza
# dessa zona. A disponibilidade da mecânica em combate é controlada pelo Elmo.
for _sid, _spec in SPECIES.items():
    _vital = _spec.get('vital_zone')
    if not _vital or 'vital_rupture' in _spec:
        continue
    _zones = _spec.get('target_zones', {})
    if _vital not in _zones:
        continue
    _zone_name = str(_zones[_vital].get('name', _vital))
    _zone_lower = _zone_name.lower()
    if _vital in ('head', 'sensor') or any(token in _zone_lower for token in ('olho', 'sensor', 'cabeça', 'mandíbula', 'boca', 'rosto')):
        _spec['vital_rupture'] = dict(
            kind='precision',
            value=3,
            description=f'Ruptura de {_zone_name}: Precisão do inimigo reduzida em 3 pontos.'
        )
    elif _vital in ('core', 'sac') or any(token in _zone_lower for token in ('núcleo', 'bolsa', 'saco')):
        _spec['vital_rupture'] = dict(
            kind='attack_pct',
            value=20,
            description=f'Ruptura de {_zone_name}: ATQ do inimigo reduzido em 20%.'
        )
    else:
        _spec['vital_rupture'] = dict(
            kind='attack_pct',
            value=15,
            description=f'Ruptura de {_zone_name}: ATQ do inimigo reduzido em 15%.'
        )

BOSS_ACHIEVEMENT_TIERS = (1, 100, 1000)

def boss_achievement_id(boss_id, target):
    return f'boss_{int(target)}_{boss_id}'

def boss_achievement_data(boss_id, target):
    boss = BOSSES.get(boss_id)
    if not boss or int(target) not in BOSS_ACHIEVEMENT_TIERS:
        return None
    card_id = boss.get('card')
    card = CARDS.get(card_id, {})
    card_name = format_card_name(card.get('name', boss.get('name', boss_id)))
    signature = next((drop[0] for drop in boss.get('drops', []) if float(drop[1]) >= 1.0), None)
    name = boss.get('name', boss_id)
    if int(target) == 1:
        reward = f'{signature} ×5' if signature else 'Recompensa de boss'
        reward_type, reward_item, reward_amount = 'item', signature, 5
    elif int(target) == 100:
        reward = f'Carta normal de {card_name}'
        reward_type, reward_item, reward_amount = 'card_variant', None, 0
    else:
        reward = f'Carta + de {card_name}'
        reward_type, reward_item, reward_amount = 'card_variant', None, 0
    return dict(
        category='Combate',
        name=(f'Derrotar {name}' if int(target) == 1 else f'Derrotar {name} {int(target)} vezes'),
        description=(
            f'Derrote {name} uma vez.' if int(target) == 1 else
            f'Derrote {name} {int(target)} vezes no Simulador de Combate.'
        ),
        condition='boss_defeats', boss=boss_id, target=int(target),
        reward=reward, reward_type=reward_type, reward_item=reward_item, reward_amount=reward_amount,
        reward_card=card_id if reward_type == 'card_variant' else None,
        reward_variant='normal' if int(target) == 100 else 'plus' if int(target) == 1000 else None,
    )

