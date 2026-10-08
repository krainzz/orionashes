"""Mapas externos de Veyra e conteúdo físico das primeiras civilizações."""
from content import SPAWNS, NODES, NODE_IDS, SHIP, PLANET, CIVILIZATION, NAHR_CIVILIZATION, BOSS_ARENAS


def salvage(prefix, positions, item='Sucata', quantity=(1, 2)):
    return [dict(id=f'{prefix}_{i+1:02}', pos=p, item=item, quantity=quantity) for i, p in enumerate(positions)]

# Nós de flora: coleta condicionada ao Scan e visual próprio no mapa.
def flora(prefix, positions, herb_id, style='alien'):
    return [dict(id=f'{prefix}_{i+1:02}', pos=p, item=herb_id, quantity=(1, 1), category='flora', scan_required=True, flora_style=style) for i, p in enumerate(positions)]


OLD_ROCKS = {(2, 2), (3, 2), (11, 2), (2, 12), (12, 6), (10, 12), (4, 12), (1, 8), (12, 13), (4, 3)}

SECTORS = {
    'landing': dict(
        name='Local de aterrissagem', size=21, tint=(126, 90, 66), ship=SHIP,
        rocks=OLD_ROCKS | {(16, 4), (18, 8), (17, 17), (8, 18), (14, 16)},
        nodes=[dict(id=nid, pos=p, item='Sucata', quantity=(1, 2)) for nid, p in zip(NODE_IDS, NODES)] + salvage('pouso_extra', [(16, 8), (14, 17)]),
        spawns=SPAWNS + [('scarab', (16, 14)), ('scarab', (18, 5))],
        exits=[dict(at=(20, 10), direction=(1, 0), target='dunes', arrival=(0, 10), key='D / direita'),
               dict(at=(0, 10), direction=(-1, 0), target='comms_ridge', arrival=(20, 10), key='A / antena')],
        landmarks=[], description='Sua nave está danificada. Explore o planeta desconhecido.'),
    'dunes': dict(
        name='Corredor das dunas', size=23, tint=(145, 107, 69), ship=None,
        rocks={(3, 3), (4, 3), (7, 5), (10, 7), (15, 3), (18, 8), (5, 16), (13, 16), (18, 18), (9, 19)},
        nodes=salvage('corredor', [(5, 9), (15, 9), (15, 16), (8, 3)]) + flora('dunas_erva_silica', [(9, 5), (20, 16)], 'Erva-sílica') + flora('dunas_folha_nara', [(14, 4)], 'Folha de Nara'),
        spawns=[('lizard', (7, 12)), ('scarab', (12, 5)), ('lizard', (17, 13)), ('scarab', (6, 18)), ('hound', (19, 14)), ('hound', (11, 17))],
        exits=[dict(at=(0, 10), direction=(-1, 0), target='landing', arrival=(20, 10), key='A / esquerda'),
               dict(at=(10, 0), direction=(0, -1), target='ruins', arrival=(10, 20), key='W / cima'),
               dict(at=(22, 12), direction=(1, 0), target='outskirts', arrival=(0, 12), key='D / leste')],
        landmarks=[dict(id='mark_dunes_01', pos=(15, 5), text='Marcas de uma civilização local. O idioma ainda é desconhecido.'),
                    dict(id='kuvaar_trace_dunes_false', pos=(11, 8), text='A areia está úmida, mas não há cristalização salina. A trilha parece falsa.', boss_trace='false'),
                    dict(id='kuvaar_trace_dunes_true', pos=(20, 10), text='Cristais de sal formam placas nas pedras. O rastro parece ter sido deixado por algo enorme.', boss_trace='true')],
        settlement={
            'id': 'dunewatch', 'name': 'Posto Nahar', 'civilization': CIVILIZATION['id'], 'language': CIVILIZATION['language'],
            'center': (18, 8), 'sight_radius': 6, 'faction': 'dunewatch',
            'structures': [{'type': 'watch', 'pos': (18, 8)}, {'type': 'shade', 'pos': (17, 6)}, {'type': 'dwelling', 'pos': (20, 9)}],
            'npcs': [
                {'id': 'avarin_watcher', 'name': 'Teren', 'role': 'Vigia das Dunas', 'faction': 'dunewatch', 'pos': (17, 9), 'kind': 'avarin_guard', 'solid': True},
                {'id': 'avarin_runner', 'name': 'Sora', 'role': 'Mensageira de Rota', 'faction': 'dunewatch', 'pos': (19, 6), 'kind': 'avarin', 'solid': True},
            ],
            'description': 'Um pequeno posto de vigia controla uma rota antiga. Os Vigias das Dunas mantêm contato entre Qaresh e os assentamentos menores.'},
        description='Vestígios de rotas antigas atravessam as dunas. O Posto Nahar vigia uma das passagens.'),
    'ruins': dict(
        name='Vestígios de uma civilização', size=21, tint=(108, 93, 84), ship=None,
        rocks={(4, 5), (5, 5), (6, 5), (15, 6), (16, 6), (4, 14), (5, 14), (14, 14), (15, 14)},
        nodes=salvage('ruinas_sucata', [(8, 15), (15, 10)]) + [dict(id=f'registro_{i+1:02}', pos=p, item='Fragmento histórico', quantity=(1, 1)) for i, p in enumerate([(8, 6), (12, 8), (7, 11)])],
        spawns=[('drone', (12, 12)), ('scarab', (5, 9)), ('lizard', (16, 16)), ('burrower', (9, 16))],
        exits=[dict(at=(10, 20), direction=(0, 1), target='dunes', arrival=(10, 0), key='S / baixo'),
               dict(at=(20, 10), direction=(1, 0), target='waterworks', arrival=(0, 10), key='D / leste')],
        landmarks=[
            dict(id='cultural_ruins_01', pos=(10, 5), text='Inscrição preservada em uma placa de pedra. A tradução dependerá do elmo com análise linguística.', cultural=True),
            dict(id='ruins_trace', pos=(12, 5), text='Os símbolos repetem padrões de armazenamento, troca e pertencimento. Ainda não há tradução disponível.'),
            dict(id='water_comms_terminal', pos=(12, 10), text='Terminal de comunicações do núcleo de Qaresh. A rede local mantém os avisos de rota e movimentação dos Guardiões dos Reservatórios.', faction_hack='waterkeepers'),
        ],
        settlement={
            'id': 'qaresh', 'name': 'Qaresh', 'civilization': CIVILIZATION['id'], 'language': CIVILIZATION['language'],
            'center': (14, 8), 'sight_radius': 7, 'faction': 'waterkeepers',
            'structures': [{'type': 'reservoir', 'pos': (14, 8)}, {'type': 'dwelling', 'pos': (12, 8)}, {'type': 'dwelling', 'pos': (15, 10)}, {'type': 'shade', 'pos': (13, 6)}, {'type': 'watch', 'pos': (17, 8)}],
            'npcs': [
                {'id': 'avarin_waterkeeper', 'name': 'Iria', 'role': 'Guardiã de água', 'faction': 'waterkeepers', 'pos': (13, 9), 'kind': 'avarin', 'solid': True},
                {'id': 'avarin_watch', 'name': 'Sarek', 'role': 'Vigia das dunas', 'faction': 'dunewatch', 'pos': (16, 9), 'kind': 'avarin_guard', 'solid': True},
                {'id': 'avarin_scavenger', 'name': 'Naevi', 'role': 'Coletora de sucata', 'faction': 'scavengers', 'pos': (16, 7), 'kind': 'avarin', 'solid': True},
            ],
            'description': 'Qaresh é um pequeno posto de captação e abrigo. Os Avarin vivem ao redor de reservatórios subterrâneos e coberturas contra as tempestades de poeira.'},
        description='Colete registros e observe o assentamento de Qaresh. Os habitantes estão próximos, mas seu idioma ainda é incompreensível.'),
    'outskirts': dict(
        name='Cinturão de Qaresh', size=23, tint=(120, 98, 71), ship=None,
        rocks={(3, 5), (5, 7), (7, 4), (12, 7), (17, 4), (20, 8), (15, 15), (5, 17), (10, 19), (19, 17)},
        nodes=salvage('cinturao', [(6, 12), (14, 8), (18, 14), (10, 4)]) + flora('cinturao_musgo', [(8, 9), (19, 12)], 'Musgo azul de Veyra'),
        spawns=[('hound', (5, 10)), ('burrower', (10, 13)), ('lizard', (17, 11)), ('hound', (20, 15)), ('scarab', (15, 18))],
        exits=[dict(at=(0, 12), direction=(-1, 0), target='dunes', arrival=(22, 12), key='A / oeste'),
               dict(at=(22, 6), direction=(1, 0), target='canyon', arrival=(0, 11), key='D / cânion')],
        landmarks=[dict(id='cultural_outskirts_01', pos=(10, 7), text='Uma fileira de placas indica ritos de passagem entre famílias Avarin. A Manopla registra padrões culturais.', cultural=True),
                    dict(id='kuvaar_trace_outskirts_false', pos=(8, 15), text='Ranhuras de arrasto terminam em uma toca de fauna comum. O tamanho não corresponde ao rastro procurado.', boss_trace='false'),
                    dict(id='kuvaar_trace_outskirts_true', pos=(18, 9), text='A pedra está coberta por uma crosta branca e pegajosa. O mesmo sal aparece em três pontos sucessivos.', boss_trace='true')],
        settlement={
            'id': 'reclaimers_camp', 'name': 'Oficinas de Sifra', 'civilization': CIVILIZATION['id'], 'language': CIVILIZATION['language'],
            'center': (14, 10), 'sight_radius': 6, 'faction': 'scavengers',
            'structures': [{'type': 'dwelling', 'pos': (13, 10)}, {'type': 'shade', 'pos': (15, 8)}, {'type': 'watch', 'pos': (17, 10)}],
            'npcs': [
                {'id': 'avarin_reclaimer', 'name': 'Mira', 'role': 'Recuperadora', 'faction': 'scavengers', 'pos': (14, 9), 'kind': 'avarin', 'solid': True},
                {'id': 'avarin_tinker', 'name': 'Oren', 'role': 'Técnico de oficina', 'faction': 'scavengers', 'pos': (16, 11), 'kind': 'avarin', 'solid': True},
            ],
            'description': 'As Oficinas de Sifra são mantidas pelos Recuperadores, que desmontam sucata e procuram tecnologia esquecida nas ruínas.'},
        description='Uma borda de Qaresh onde a sucata é separada, reparada e revendida.'),
    'waterworks': dict(
        name='Estação de Captação', size=21, tint=(97, 112, 99), ship=None,
        rocks={(3, 3), (5, 5), (17, 4), (18, 8), (4, 15), (7, 17), (14, 14), (17, 16)},
        nodes=salvage('captacao', [(5, 9), (8, 13), (18, 12)]) + flora('captacao_folha_nara', [(4, 9)], 'Folha de Nara') + [dict(id='cultural_register_01', pos=(7, 6), item='Registro cultural', quantity=(1, 1)), dict(id='raw_water_01', pos=(6, 16), item='Água Bruta', quantity=(3, 5)), dict(id='raw_water_02', pos=(10, 4), item='Água Bruta', quantity=(3, 5)), dict(id='raw_water_03', pos=(18, 18), item='Água Bruta', quantity=(3, 5))],
        spawns=[('drone', (5, 12)), ('burrower', (15, 10)), ('hound', (12, 16)), ('guard', (15, 8))],
        exits=[dict(at=(0, 10), direction=(-1, 0), target='ruins', arrival=(20, 10), key='A / oeste'),
               dict(at=(10, 20), direction=(0, 1), target='vaults', arrival=(10, 0), key='S / galerias'),
               dict(at=(19, 17), direction=(1, 0), target='canyon', arrival=(2, 18), key='D / cânion')],
        landmarks=[
            dict(id='cultural_water_01', pos=(7, 6), text='Registro visual de um ritual em torno das bombas de água. A análise cultural pode extrair padrões linguísticos.', cultural=True),
            dict(id='water_pump', pos=(12, 7), text='Conjunto de bombas de captação. A pressão caiu abaixo do nível operacional.', mission_site='water_supply'),
            dict(id='water_terminal', pos=(13, 7), text='Terminal de controle da estação. A porta de acesso responde a protocolos de baixa intensidade; a Manopla consegue tentar uma intrusão.', hack_site='water_supply'),
            dict(id='kuvaar_diversion', pos=(11, 17), text='Válvula secundária de desvio. Um bypass manual poderia redirecionar uma reserva sem autorização.', diversion=True),
        ],
        settlement={
            'id': 'waterworks_station', 'name': 'Complexo Neris', 'civilization': CIVILIZATION['id'], 'language': CIVILIZATION['language'],
            'center': (15, 7), 'sight_radius': 6, 'faction': 'waterkeepers',
            'structures': [{'type': 'reservoir', 'pos': (15, 7)}, {'type': 'dwelling', 'pos': (17, 7)}, {'type': 'watch', 'pos': (16, 5)}],
            'npcs': [
                {'id': 'avarin_engineer', 'name': 'Tavi', 'role': 'Engenheiro de captação', 'faction': 'waterkeepers', 'pos': (14, 6), 'kind': 'avarin', 'solid': True},
                {'id': 'avarin_guard_water', 'name': 'Kesh', 'role': 'Guarda do complexo', 'faction': 'dunewatch', 'pos': (17, 8), 'kind': 'avarin_guard', 'solid': True},
            ],
            'description': 'O Complexo Neris distribui água de reservas subterrâneas para Qaresh. O abastecimento caiu e o problema ameaça os assentamentos próximos.'},
        description='Uma estação de captação que mantém os assentamentos próximos vivos. Algo interrompeu o fluxo de água.'),
    'canyon': dict(
        name='Cânion de Nahar', size=24, tint=(98, 79, 69), ship=None,
        rocks={(4, 3), (6, 3), (9, 4), (13, 6), (17, 4), (19, 9), (7, 12), (11, 14), (16, 15), (20, 18), (5, 20)},
        nodes=salvage('canyon_sucata', [(4, 9), (9, 8), (17, 12), (13, 19)]) + salvage('canyon_scrap', [(6, 17), (20, 5)]) + flora('canyon_floral', [(8, 6), (16, 16)], 'Flor salina'),
        spawns=[('manta', (7, 8)), ('hound', (10, 11)), ('manta', (18, 11)), ('lizard', (15, 18)), ('scarab', (21, 14))],
        exits=[dict(at=(0, 11), direction=(-1, 0), target='outskirts', arrival=(22, 6), key='A / oeste'),
               dict(at=(23, 19), direction=(1, 0), target='vaults', arrival=(1, 3), key='D / galerias'),
               dict(at=(2, 18), direction=(-1, 0), target='waterworks', arrival=(19, 17), key='A / estação'),
               dict(at=(23, 5), direction=(1, 0), target='salt_basin', arrival=(0, 11), key='D / bacia', boss_gate=True, boss_id='kuvaar')],
        landmarks=[
            dict(id='cultural_canyon_01', pos=(12, 9), text='Marcas de patrulha foram esculpidas nas paredes do cânion. A análise cultural pode revelar sua função.', cultural=True),
            dict(id='kuvaar_trace_canyon_false', pos=(5, 15), text='Uma trilha termina em um ninho vazio. A areia está intacta demais para ter sido criada pela criatura procurada.', boss_trace='false'),
            dict(id='kuvaar_trace_canyon_true', pos=(14, 18), text='O paredão foi raspado por uma massa colossal. Sal seco ocupa as fissuras até a base do cânion.', boss_trace='true'),
            dict(id='kuvaar_basin_marker', pos=(21, 5), text='O rastro de sal segue para o lado leste. Uma abertura profunda conduz à Bacia de Kuvaar.', boss_route_marker='kuvaar'),
            dict(id='canyon_terminal', pos=(18, 6), text='Um terminal sem alimentação mostra conectores compatíveis com a Manopla. A rede parece ter sido isolada.', hack_site='water_supply'),
        ],
        settlement={
            'id': 'nahar_post', 'name': 'Posto Nahar', 'civilization': CIVILIZATION['id'], 'language': CIVILIZATION['language'],
            'center': (18, 7), 'sight_radius': 6, 'faction': 'dunewatch',
            'structures': [{'type': 'watch', 'pos': (18, 7)}, {'type': 'shade', 'pos': (16, 6)}, {'type': 'dwelling', 'pos': (20, 7)}],
            'npcs': [
                {'id': 'avarin_canyon_veteran', 'name': 'Veya', 'role': 'Veterana dos Cânions', 'faction': 'dunewatch', 'pos': (17, 8), 'kind': 'avarin_guard', 'solid': True},
                {'id': 'avarin_canyon_scout', 'name': 'Haran', 'role': 'Batedor do Cânion', 'faction': 'dunewatch', 'pos': (20, 6), 'kind': 'avarin', 'solid': True},
            ],
            'description': 'O posto protege os túneis que levam às galerias antigas. Os Vigias conhecem rotas que não aparecem nos mapas de Qaresh.'},
        faction_site={
            'id': 'rift_camp', 'name': 'Acampamento da Fenda', 'faction': 'rift_children',
            'center': (9, 18), 'sight_radius': 5,
            'structures': [{'type': 'shade', 'pos': (9, 18)}, {'type': 'dwelling', 'pos': (11, 18)}, {'type': 'watch', 'pos': (10, 20)}],
            'npcs': [
                {'id': 'faction_c_leader', 'name': 'Tarek', 'role': 'Voz da Fenda', 'faction': 'rift_children', 'pos': (9, 17), 'kind': 'avarin', 'solid': True},
                {'id': 'faction_c_guard', 'name': 'Rava', 'role': 'Guarda da Fenda', 'faction': 'rift_children', 'pos': (11, 19), 'kind': 'avarin_guard', 'solid': True},
            ],
            'description': 'Um acampamento escondido entre as fraturas do cânion. Os Filhos da Fenda observam rotas de água sem se integrar aos postos oficiais.'},
        description='Um cânion estreito onde antigas patrulhas esculpiram rotas nas paredes. Há sinais de movimento recente.'),
    'comms_ridge': dict(
        name='Morro da Antena', size=21, tint=(78, 96, 103), ship=None,
        rocks={(3,4),(5,9),(8,3),(12,6),(15,4),(17,10),(7,15),(11,18),(16,16)},
        nodes=salvage('comms_scrap', [(4,6),(15,7),(18,15)]),
        spawns=[
            {'species':'drone','pos':(7,10),'mission_id':'ship_comms'},
            {'species':'drone','pos':(12,9),'mission_id':'ship_comms'},
            {'species':'drone','pos':(8,14),'mission_id':'ship_comms'},
            {'species':'drone','pos':(14,15),'mission_id':'ship_comms'},
            ('scarab',(17,6)),('hound',(5,14)),
        ],
        exits=[dict(at=(20,10), direction=(1,0), target='landing', arrival=(0,10), key='D / nave')],
        landmarks=[dict(id='comms_antenna', pos=(10,5), text='Antena de comunicação de longo alcance. Quatro Sentinelas Avariadas protegem o conjunto.', ship_mission_site='ship_comms')],
        settlement=None,
        description='Um morro isolado concentra uma antiga antena de comunicação. O sinal é fraco, mas ainda há satélites próximos respondendo.'),
    'salt_basin': dict(
        name='Bacia Seca de Kuvaar', boss_arena=True, size=25, tint=(137, 119, 90), ship=None,
        rocks={(3, 4), (5, 6), (8, 3), (11, 5), (15, 4), (20, 6), (4, 11), (9, 14), (15, 17), (21, 15), (7, 20), (18, 21)},
        nodes=salvage('basin_scrap', [(5, 9), (12, 7), (20, 11), (16, 19)]),
        spawns=[],
        exits=[dict(at=(0, 11), direction=(-1, 0), target='canyon', arrival=(23, 5), key='A / cânion')],
        landmarks=[dict(id='kuvaar_basin_site', pos=(15, 11), text='Uma depressão gigantesca corta o terreno. Cristais de sal cobrem a bacia como uma crosta branca. O rastro termina aqui.', boss_site='kuvaar'),
                   dict(id='kuvaar_salt_pool', pos=(11, 10), text='Uma poça seca guarda camadas de sal compactado. A criatura parece ter absorvido quase toda a umidade local.')],
        settlement=None,
        description='Uma bacia circular onde o solo foi drenado a ponto de cristalizar o sal. O silêncio aqui parece anormal.'),
    'vaults': dict(
        name='Galerias de Sifra', size=22, tint=(74, 83, 88), ship=None,
        rocks={(3, 4), (5, 6), (8, 3), (12, 5), (16, 4), (18, 8), (4, 12), (9, 13), (15, 15), (18, 18), (6, 18)},
        nodes=salvage('vault_sucata', [(3, 8), (8, 6), (13, 10), (18, 13)]) + salvage('vault_circuit', [(11, 18), (19, 5)]) + flora('vault_ervas', [(5, 16), (19, 11)], 'Erva-sílica'),
        spawns=[('stalker', (6, 9)), ('burrower', (10, 10)), ('drone', (15, 7)), ('manta', (17, 13)), ('stalker', (14, 17))],
        exits=[dict(at=(10, 0), direction=(0, -1), target='waterworks', arrival=(10, 20), key='W / estação'),
               dict(at=(1, 3), direction=(-1, 0), target='canyon', arrival=(23, 19), key='A / cânion')],
        landmarks=[dict(id='cultural_vault_01', pos=(7, 5), text='Painéis gravados organizam nomes de famílias e rotas de extração. O conteúdo parece valioso para a compreensão do Avari.', cultural=True),
                   dict(id='vault_archive', pos=(12, 16), text='Arquivo antigo isolado. O conector de dados parece conter registros da época das primeiras reservas.', cultural=True)],
        settlement={
            'id': 'sifra_vaults', 'name': 'Galerias de Sifra', 'civilization': CIVILIZATION['id'], 'language': CIVILIZATION['language'],
            'center': (16, 10), 'sight_radius': 6, 'faction': 'scavengers',
            'structures': [{'type': 'dwelling', 'pos': (15, 10)}, {'type': 'shade', 'pos': (17, 8)}, {'type': 'watch', 'pos': (18, 11)}],
            'npcs': [
                {'id': 'avarin_archivist', 'name': 'Daro', 'role': 'Arquivista Recuperador', 'faction': 'scavengers', 'pos': (15, 9), 'kind': 'avarin', 'solid': True},
                {'id': 'avarin_diver', 'name': 'Kiva', 'role': 'Exploradora de galerias', 'faction': 'scavengers', 'pos': (17, 11), 'kind': 'avarin', 'solid': True},
            ],
            'description': 'As Galerias de Sifra guardam estoques e arquivos recuperados. Os Recuperadores disputam espaço com fauna que ocupa túneis abandonados.'},
        description='Galerias subterrâneas onde os Recuperadores armazenam tecnologia e registros antigos.'),

    # ------------------------------------------------------------------
    # ORIONIS — calor químico, metal natural e cavernas termais
    # ------------------------------------------------------------------
    'orionis_landing': dict(
        name='Bacia de Escória', size=23, tint=(126, 72, 61), ship=SHIP,
        rocks={(2,3),(5,5),(10,3),(16,4),(20,7),(4,13),(9,16),(14,12),(19,17),(7,20),(17,20)},
        nodes=salvage('orionis_pouso', [(4,8),(15,8),(19,14)]) +
              flora('orionis_lotus', [(8,5),(17,11)], 'Lótus de Cinza', 'fiery') +
              flora('orionis_rubra', [(5,17)], 'Flor de Sílica Rubra', 'fiery'),
        spawns=[('salamander_igneous',(12,15)),('ironback_crab',(18,8)),('ion_wasp',(9,10))],
        exits=[dict(at=(22,11),direction=(1,0),target='orionis_ember_fields',arrival=(0,11),key='D / campos'),
               dict(at=(11,0),direction=(0,-1),target='orionis_ferro_ravines',arrival=(11,22),key='W / ravinas')],
        landmarks=[dict(id='fagor_route_marker', pos=(20,10), text='Sinais de calor intenso apontam para os campos e, além deles, para a Caverna Ígnea de Fagor.', boss_route_marker='fagor')], description='A nave encontrou um vale quente coberto por escória mineral. A atmosfera é agressiva, mas o terreno parece rico em materiais.'),
    'orionis_ember_fields': dict(
        name='Campos de Cinza', size=23, tint=(136, 76, 54), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,10),(5,14),(11,13),(16,16),(8,19),(19,19)},
        nodes=salvage('orionis_cinza', [(5,8),(14,7),(18,14)]) +
              flora('orionis_lotus2', [(8,9),(15,18)], 'Lótus de Cinza', 'fiery') +
              flora('orionis_rubra2', [(4,18),(20,6)], 'Flor de Sílica Rubra', 'fiery'),
        spawns=[('salamander_igneous',(8,13)),('ion_wasp',(15,10)),('ironback_crab',(19,16)),('salamander_igneous',(12,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='orionis_landing',arrival=(22,11),key='A / pouso'),
               dict(at=(22,12),direction=(1,0),target='orionis_ferro_ravines',arrival=(0,12),key='D / ravinas')],
        landmarks=[dict(id='fagor_boss_marker', pos=(20,19), text='O solo vibra com calor. Uma caverna larga se abre adiante, e algo gigantesco ocupa seu interior.', boss_route_marker='fagor')], description='Cinzas quentes se acumulam em campos abertos. Clarões sob o solo revelam atividade geotérmica constante.'),
    'orionis_ferro_ravines': dict(
        name='Ravinas Ferrídeas', size=23, tint=(92, 79, 74), ship=None,
        rocks={(2,5),(5,3),(7,8),(12,4),(15,9),(19,5),(4,15),(10,17),(16,18),(21,14)},
        nodes=salvage('orionis_ferro', [(4,10),(12,11),(18,8),(17,18)]) +
              flora('orionis_ravina_lotus', [(6,6),(20,16)], 'Flor de Sílica Rubra', 'fiery'),
        spawns=[('ironback_crab',(7,12)),('salamander_igneous',(14,8)),('ion_wasp',(18,12)),('ironback_crab',(12,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='orionis_ember_fields',arrival=(22,12),key='A / campos'),
               dict(at=(11,22),direction=(0,1),target='orionis_landing',arrival=(11,0),key='S / pouso'),
               dict(at=(22,20),direction=(1,0),target='orionis_thermal_caves',arrival=(0,10),key='D / cavernas', boss_gate=True, boss_id='fagor')],
        landmarks=[dict(id='fagor_gate_marker', pos=(20,18), text='A entrada adiante conduz à Caverna Ígnea de Fagor. Algo colossal se move além das paredes.', boss_route_marker='fagor')], description='Grandes paredes de minério cortam o terreno. Veios metálicos parecem ter sido formados por processos naturais.'),
    'orionis_thermal_caves': dict(
        name='Caverna Ígnea de Fagor', boss_arena=True, size=25, tint=(82, 55, 49), ship=None, lava_style=True,
        rocks={(2,4),(5,8),(8,3),(12,6),(17,4),(21,8),(4,15),(9,19),(15,16),(20,14),(22,20),(6,22)},
        nodes=salvage('orionis_caverna_fagor', [(4,10),(12,9),(20,12)]) + flora('orionis_fagor_lotus', [(7,17),(18,6)], 'Lótus de Cinza', 'fiery'),
        spawns=[],
        exits=[dict(at=(0,10),direction=(-1,0),target='orionis_ferro_ravines',arrival=(22,20),key='A / ravinas')],
        landmarks=[dict(id='fagor_site', pos=(15,12), text='Uma massa de pedra colossal bloqueia o centro da caverna. Veios vermelhos convergem para um núcleo de magma exposto no corpo.', boss_site='fagor')],
        description='Uma caverna larga e aquecida por veios vulcânicos. O teto é alto, o piso é irregular e o centro da galeria foi tomado por Fagor.'),

    # ------------------------------------------------------------------
    # KAEL — gelo, vento e formações cristalinas
    # ------------------------------------------------------------------
    'kael_landing': dict(
        name='Planície de Geada', size=23, tint=(77, 111, 128), ship=SHIP,
        rocks={(2,4),(5,6),(10,3),(15,5),(20,4),(4,14),(9,13),(14,16),(19,15),(7,20),(17,20)},
        nodes=salvage('kael_pouso', [(4,9),(15,8),(18,14)]) +
              flora('kael_musgo', [(7,5),(17,12)], 'Musgo de Geada', 'icy') +
              flora('kael_liquen', [(5,17)], 'Líquen Prismático', 'icy'),
        spawns=[('frost_wolf',(11,15)),('crystal_grazer',(18,8)),('glacial_eel',(8,10))],
        exits=[dict(at=(22,11),direction=(1,0),target='kael_crystal_pines',arrival=(0,11),key='D / bosques'),
               dict(at=(11,0),direction=(0,-1),target='kael_glacial_plains',arrival=(11,22),key='W / planícies')],
        landmarks=[dict(id='kael_route_marker', pos=(20,10), text='A trilha segue para uma região de mata cristalina. Há sinais de uma criatura colossal mais adiante.', boss_route_marker='kael')], description='A nave pousou em uma faixa de gelo estável. Cristais naturais refletem a luz da atmosfera fria.'),
    'kael_crystal_pines': dict(
        name='Bosques Cristalinos', size=23, tint=(68, 103, 112), ship=None,
        rocks={(3,3),(6,5),(11,4),(16,3),(20,8),(5,12),(9,16),(15,13),(19,17),(12,20)},
        nodes=salvage('kael_cristal', [(5,8),(14,7),(18,14)]) +
              flora('kael_musgo2', [(8,10),(17,18)], 'Musgo de Geada', 'icy') +
              flora('kael_liquen2', [(4,18),(20,6)], 'Líquen Prismático', 'icy'),
        spawns=[('frost_wolf',(8,13)),('glacial_eel',(14,10)),('crystal_grazer',(19,15)),('frost_wolf',(12,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='kael_landing',arrival=(22,11),key='A / pouso'),
               dict(at=(22,12),direction=(1,0),target='kael_glacial_plains',arrival=(0,12),key='D / planícies')],
        landmarks=[dict(id='kael_gate_marker', pos=(20,18), text='Além das formações cristalinas, a trilha desce em direção à Clareira de Trembe.', boss_route_marker='kael')], description='Formações cristalinas crescem como árvores minerais e criam corredores naturais entre áreas de gelo.'),
    'kael_glacial_plains': dict(
        name='Planícies Glaciais', size=23, tint=(83, 126, 148), ship=None,
        rocks={(2,5),(5,3),(8,7),(12,5),(16,8),(20,4),(4,15),(10,16),(15,18),(21,14)},
        nodes=salvage('kael_planicies', [(4,10),(12,10),(18,8),(17,18)]) +
              flora('kael_planicie_musgo', [(6,6),(20,16)], 'Musgo de Geada', 'icy'),
        spawns=[('crystal_grazer',(7,12)),('frost_wolf',(14,8)),('glacial_eel',(18,12)),('crystal_grazer',(12,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='kael_crystal_pines',arrival=(22,12),key='A / bosques'),
               dict(at=(11,22),direction=(0,1),target='kael_landing',arrival=(11,0),key='S / pouso'),
               dict(at=(22,20),direction=(1,0),target='kael_frost_caverns',arrival=(0,10),key='D / cavernas', boss_gate=True, boss_id='kael')],
        landmarks=[dict(id='kael_boss_marker', pos=(20,19), text='A mata adiante fica silenciosa demais. Uma clareira dominada por uma árvore colossal aguarda além da entrada.', boss_route_marker='kael')], description='Uma planície aberta de gelo compacto. O vento corta o terreno e desloca pequenos cristais pela superfície.'),
    'kael_frost_caverns': dict(
        name='Clareira de Trembe', boss_arena=True, size=25, tint=(55, 86, 62), ship=None, forest_style=True,
        rocks={(2,5),(5,3),(9,7),(13,4),(18,6),(22,4),(4,15),(8,19),(15,17),(20,14),(22,21)},
        nodes=salvage('kael_clareira', [(4,10),(11,8),(20,11)]) + flora('kael_clareira_flora', [(6,6),(9,12),(17,7),(20,18)], 'Fibra radicular', 'luminous'),
        spawns=[],
        exits=[dict(at=(0,10),direction=(-1,0),target='kael_glacial_plains',arrival=(22,20),key='A / planícies')],
        landmarks=[dict(id='kael_site', pos=(15,12), text='Uma árvore gigantesca cobre a clareira. A copa ocupa boa parte do teto e o tronco parece atravessar o próprio solo.', boss_site='kael')],
        description='Uma mata densa tomou uma antiga clareira. Raízes grossas cruzam o chão e a luz desaparece sob a copa de Trembe.'),

    # ------------------------------------------------------------------
    # NAHR — basaltos, sal profundo e flora agressiva
    # ------------------------------------------------------------------
    'nahr_landing': dict(
        name='Margem Basáltica', size=23, tint=(86, 72, 66), ship=SHIP,
        rocks={(2,3),(5,5),(10,4),(15,4),(20,7),(4,13),(9,16),(14,12),(19,17),(7,20),(17,20)},
        nodes=salvage('nahr_pouso', [(4,8),(15,8),(19,14)]) +
              flora('nahr_trepa', [(8,5),(17,11)], 'Trepa-basáltica', 'basalt') +
              flora('nahr_salne', [(5,17)], 'Flor de Sal Negro', 'basalt'),
        spawns=[('root_scorpion',(12,15)),('basalt_tortoise',(18,8)),('salt_spider',(9,10))],
        exits=[dict(at=(22,11),direction=(1,0),target='nahr_basalt_gardens',arrival=(0,11),key='D / jardins'),
               dict(at=(11,0),direction=(0,-1),target='nahr_salt_wastes',arrival=(11,22),key='W / ermos')],
        landmarks=[
            dict(id='ry_route_marker_01', pos=(20,10), text='A direção do vazio mais profundo de Nahr é registrada pela Manopla. Além dos jardins existe uma região ainda não explicada.', boss_route_marker='ry'),
            dict(id='nahr_culture_01', pos=(12,7), text='Um conjunto de pedras negras forma um pequeno círculo suspenso por forças desconhecidas. O padrão parece registrar símbolos fundamentais do povo de Nahr.', cultural=True, civilization='nahr_shadows'),
        ],
        settlement=None, description='A nave pousou junto a uma formação de basalto escuro. Fendas no solo abrigam raízes e cristais de sal; pequenos vultos negros podem ser vistos ao longe.') ,
    'nahr_basalt_gardens': dict(
        name='Jardins Basálticos', size=23, tint=(74, 80, 67), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,10),(5,14),(11,13),(16,16),(8,19),(19,19)},
        nodes=salvage('nahr_jardins', [(5,8),(14,7),(18,14)]) +
              flora('nahr_trepa2', [(8,9),(15,18)], 'Trepa-basáltica', 'basalt') +
              flora('nahr_salne2', [(4,18),(20,6)], 'Flor de Sal Negro', 'basalt'),
        spawns=[('root_scorpion',(8,13)),('salt_spider',(15,10)),('basalt_tortoise',(19,16)),('root_scorpion',(12,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='nahr_landing',arrival=(22,11),key='A / pouso'),
               dict(at=(22,12),direction=(1,0),target='nahr_salt_wastes',arrival=(0,12),key='D / ermos')],
        landmarks=[
            dict(id='ry_route_marker_02', pos=(20,18), text='Marcas antigas apontam para as profundezas de Nahr. A área associada à presença desconhecida fica além dos ermos.', boss_route_marker='ry'),
            dict(id='nahr_culture_02', pos=(6,6), text='Sombras menores orbitam uma pedra escura gravada. Os símbolos se repetem em ritmos que lembram uma língua registrada por movimento e eco.', cultural=True, civilization='nahr_shadows'),
        ],
        settlement={
            'id':'nahr_shadow_haven', 'name':'Refúgio da Penumbra', 'civilization':NAHR_CIVILIZATION['id'], 'language':NAHR_CIVILIZATION['language'],
            'center':(14,11), 'sight_radius':6, 'faction':'nahr_shadows', 'architecture':'shadow',
            'structures':[{'type':'shadow_node','pos':(14,11)}, {'type':'shadow_node','pos':(12,12)}, {'type':'shadow_obelisk','pos':(16,10)}],
            'npcs':[
                {'id':'nahr_shadow_keeper','name':'Sombra do Eco','role':'Guardião dos Ecos','faction':'nahr_shadows','pos':(13,10),'kind':'nahr_shadow','civilization':'nahr_shadows','solid':True},
                {'id':'nahr_shadow_speaker','name':'Sombra Oracular','role':'Intérprete dos Ritos','faction':'nahr_shadows','pos':(15,10),'kind':'nahr_shadow','civilization':'nahr_shadows','solid':True},
                {'id':'nahr_shadow_watcher','name':'Sombra Errante','role':'Vigia do Limiar','faction':'nahr_shadows','pos':(14,12),'kind':'nahr_shadow','civilization':'nahr_shadows','solid':True},
            ],
            'description':'Pequenas sombras escuras e flutuantes se reúnem ao redor de formações minerais negras. Seu povo registra a história por ecos, gestos e sinais de luz apagada.'},
        description='Raízes grossas percorrem placas de basalto como veias. Entre as formações minerais, pequenas sombras flutuam silenciosamente sobre o solo.') ,
    'nahr_salt_wastes': dict(
        name='Ermos de Sal', size=23, tint=(126, 119, 101), ship=None,
        rocks={(2,5),(5,3),(8,7),(12,5),(16,8),(20,4),(4,15),(10,16),(15,18),(21,14)},
        nodes=salvage('nahr_sais', [(4,10),(12,10),(18,8),(17,18)]) +
              flora('nahr_ermo_salne', [(6,6),(20,16)], 'Flor de Sal Negro', 'basalt'),
        spawns=[('salt_spider',(7,12)),('basalt_tortoise',(14,8)),('root_scorpion',(18,12)),('salt_spider',(12,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='nahr_basalt_gardens',arrival=(22,12),key='A / jardins'),
               dict(at=(11,22),direction=(0,1),target='nahr_landing',arrival=(11,0),key='S / pouso'),
               dict(at=(22,20),direction=(1,0),target='nahr_root_chasm',arrival=(0,10),key='D / fenda')],
        landmarks=[
            dict(id='ry_route_marker_03', pos=(20,18), text='O caminho para a Fenda das Raízes continua na direção do vazio. A Manopla não identifica atividade comum adiante.', boss_route_marker='ry'),
            dict(id='nahr_culture_03', pos=(7,6), text='Uma parede baixa de sal negro contém três sequências de marcas. Elas parecem representar memória, silêncio e passagem, conceitos recorrentes na cultura local.', cultural=True, civilization='nahr_shadows'),
        ],
        settlement=None, description='Uma faixa de sal compactado cobre o solo. Depósitos claros se quebram em placas quando a fauna passa, enquanto marcas antigas indicam uma rota usada pelas sombras.') ,
    'nahr_root_chasm': dict(
        name='Fenda das Raízes', size=21, tint=(69, 76, 64), ship=None,
        rocks={(3,3),(5,6),(8,4),(12,5),(16,3),(18,8),(4,13),(9,14),(14,16),(18,17)},
        nodes=salvage('nahr_fenda', [(5,9),(11,8),(16,12)]) +
              flora('nahr_fenda_trepa', [(7,11),(15,15)], 'Trepa-basáltica', 'basalt'),
        spawns=[('root_scorpion',(6,10)),('basalt_tortoise',(13,6)),('salt_spider',(17,14)),('root_scorpion',(10,17))],
        exits=[dict(at=(0,10),direction=(-1,0),target='nahr_salt_wastes',arrival=(22,20),key='A / ermos'),
               dict(at=(20,10),direction=(1,0),target='nahr_ry_void',arrival=(0,12),key='D / vazio de RY')],
        landmarks=[
            dict(id='ry_route_marker_04', pos=(18,13), text='Uma abertura sem ruído conduz a um setor reservado. A fauna local ainda habita as raízes profundas da fenda.', boss_route_marker='ry'),
        ],
        settlement=None, description='Uma abertura profunda conduz a corredores dominados por raízes que atravessam as paredes de basalto. Fauna de Nahr percorre os corredores entre as raízes, enquanto um caminho silencioso leva a um vazio sem presença aparente.') ,
    'nahr_ry_void': dict(
        name='Vazio de RY', boss_arena=True, size=25, tint=(72, 71, 81), ship=None,
        rocks=set(), nodes=[], spawns=[],
        exits=[dict(at=(0,12),direction=(-1,0),target='nahr_root_chasm',arrival=(20,10),key='A / fenda')],
        landmarks=[dict(id='ry_site', pos=(12,12), text='O centro do vazio permanece completamente silencioso. Nada pode ser identificado aqui... por enquanto.', boss_site='ry')],
        settlement=None, description='Um salão vazio e circular, sem pedras, raízes ou criaturas. O espaço parece ter sido deixado intencionalmente livre para alguma presença que ainda não se revelou.') ,

    # ------------------------------------------------------------------
    # ELYRA — atmosfera densa, luz orgânica e zonas umbrías
    # ------------------------------------------------------------------
    'elyra_landing': dict(
        name='Pântano Luminal', size=23, tint=(65, 91, 88), ship=SHIP,
        rocks={(2,4),(5,6),(10,3),(15,5),(20,4),(4,14),(9,13),(14,16),(19,15),(7,20),(17,20)},
        nodes=salvage('elyra_pouso', [(4,9),(15,8),(18,14)]) +
              flora('elyra_orquidea', [(7,5),(17,12)], 'Orquídea Fotônica', 'luminous') +
              flora('elyra_fungo', [(5,17)], 'Fungo Velado', 'luminous'),
        spawns=[('luminous_stag',(11,15)),('shadow_panther',(18,8)),('spore_manta',(8,10))],
        exits=[dict(at=(22,11),direction=(1,0),target='elyra_luminous_marsh',arrival=(0,11),key='D / brejo'),
               dict(at=(11,0),direction=(0,-1),target='elyra_umbral_grove',arrival=(11,22),key='W / bosque')],
        landmarks=[dict(id='ounull_route_marker', pos=(20,10), text='A água se acumula em direção ao bosque. Uma ilha distante parece esconder alguma presença.', boss_route_marker='ounull')], description='Neblina espessa cobre a superfície do pântano. Plantas luminosas criam pequenos corredores visíveis à distância.'),
    'elyra_luminous_marsh': dict(
        name='Brejo Luminescente', size=23, tint=(60, 96, 84), ship=None,
        rocks={(3,3),(6,5),(11,4),(16,3),(20,8),(5,12),(9,16),(15,13),(19,17),(12,20)},
        nodes=salvage('elyra_brejo', [(5,8),(14,7),(18,14)]) +
              flora('elyra_orquidea2', [(8,10),(17,18)], 'Orquídea Fotônica', 'luminous') +
              flora('elyra_fungo2', [(4,18),(20,6)], 'Fungo Velado', 'luminous'),
        spawns=[('luminous_stag',(8,13)),('spore_manta',(14,10)),('shadow_panther',(19,15)),('luminous_stag',(12,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='elyra_landing',arrival=(22,11),key='A / pouso'),
               dict(at=(22,12),direction=(1,0),target='elyra_umbral_grove',arrival=(0,12),key='D / bosque')],
        landmarks=[dict(id='ounull_gate_marker', pos=(20,18), text='A névoa esconde o caminho até o lago onde Ounull permanece. O acesso final exige travessia sobre a água.', boss_route_marker='ounull')], description='Águas rasas refletem pontos de luz biológica. A fauna se desloca silenciosamente entre a vegetação densa.'),
    'elyra_umbral_grove': dict(
        name='Bosque Umbrio', size=23, tint=(55, 65, 72), ship=None,
        rocks={(2,5),(5,3),(8,7),(12,5),(16,8),(20,4),(4,15),(10,16),(15,18),(21,14)},
        nodes=salvage('elyra_bosque', [(4,10),(12,10),(18,8),(17,18)]) +
              flora('elyra_bosque_fungo', [(6,6),(20,16)], 'Fungo Velado', 'luminous'),
        spawns=[('shadow_panther',(7,12)),('spore_manta',(14,8)),('luminous_stag',(18,12)),('shadow_panther',(12,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='elyra_luminous_marsh',arrival=(22,12),key='A / brejo'),
               dict(at=(11,22),direction=(0,1),target='elyra_landing',arrival=(11,0),key='S / pouso'),
               dict(at=(22,20),direction=(1,0),target='elyra_cloud_caverns',arrival=(0,5),key='D / lago', boss_gate=True, boss_id='ounull')],
        landmarks=[dict(id='ounull_gate_final', pos=(20,18), text='O lago se abre adiante. O acesso à ilha exige o Módulo de Locomoção.', boss_route_marker='ounull')], description='Árvores e raízes formam um teto natural. A luz exterior desaparece em alguns corredores do bosque.'),
    'elyra_cloud_caverns': dict(
        name='Ilhota de Ounull', boss_arena=True, size=25, tint=(55, 91, 98), ship=None,
        rocks={(2,3),(5,6),(8,20),(20,4),(22,18)},
        water_tiles={(x,y) for x in range(25) for y in range(25) if 4 <= x <= 21 and 2 <= y <= 22 and not (9 <= x <= 17 and 9 <= y <= 16)},
        land_strip={(x,y) for x in range(0,4) for y in range(2,23)},
        nodes=salvage('elyra_ounull_lago', [(4,6),(21,10),(5,19)]) + flora('elyra_ounull_flora', [(6,12),(19,8),(4,20)], 'Orquídea Fotônica', 'luminous'),
        spawns=[],
        exits=[dict(at=(0,5),direction=(-1,0),target='elyra_umbral_grove',arrival=(22,20),key='A / bosque')],
        landmarks=[dict(id='ounull_island', pos=(13,12), text='A água se abre ao redor de uma pequena ilha. Uma entidade aquática permanece no centro da superfície seca.', boss_site='ounull')],
        island_tiles={(x,y) for x in range(9,18) for y in range(9,17)},
        description='Um lago profundo domina a caverna. Uma faixa de terra permite a chegada ao lago; além dela, somente água separa o jogador da pequena ilha central.'),
}

SECTORS_060 = {
    # ------------------------------------------------------------------
    # GALÁXIA VHAROS — mundos minerais, trevas e tempestades elétricas
    # ------------------------------------------------------------------
    'dornak_landing': dict(name='Dornak — Planalto de Ferro', size=23, tint=(83,88,91), ship=SHIP,
        rocks={(2,3),(5,6),(10,4),(15,5),(20,8),(5,14),(9,18),(15,16),(19,19)},
        nodes=salvage('dornak_landing',[(4,8),(14,9),(18,14)]) + flora('dornak_lichen',[(8,5),(17,12)],'Líquen Prismático'),
        spawns=[('ferrous_mite',(8,13)),('magnetic_ram',(17,8)),('ferrous_mite',(13,17))],
        exits=[dict(at=(22,11),direction=(1,0),target='dornak_forge_plateaus',arrival=(0,11),key='D / planaltos'),dict(at=(11,0),direction=(0,-1),target='dornak_core_mine',arrival=(11,22),key='W / mina')],
        landmarks=[dict(id='mekron_marker_01',pos=(20,10),text='Ondulações magnéticas concentram-se sob o planalto. Um colosso metálico parece usar as galerias profundas como abrigo.',boss_route_marker='mekron')], settlement=None,
        description='Placas metálicas naturais afloram do solo como veias. A bússola da Manopla oscila de forma constante.'),
    'dornak_forge_plateaus': dict(name='Dornak — Terraços da Forja', size=23, tint=(96,91,86), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,11),(4,14),(10,13),(16,17),(8,19)},
        nodes=salvage('dornak_forge',[(5,8),(14,7),(18,15)]) + flora('dornak_forge_lichen',[(7,10),(18,18)],'Líquen Prismático'),
        spawns=[('magnetic_ram',(8,12)),('ferrous_mite',(14,10)),('magnetic_ram',(18,16)),('ferrous_mite',(11,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='dornak_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='dornak_core_mine',arrival=(0,12),key='D / mina')],
        landmarks=[dict(id='mekron_marker_02',pos=(20,18),text='Fragmentos metálicos foram prensados como se algo muito pesado passasse por aqui.',boss_route_marker='mekron')], settlement=None,
        description='Terraços naturais lembram bancadas de uma forja colossal. O metal do chão responde a campos invisíveis.'),
    'dornak_core_mine': dict(name='Dornak — Mina do Núcleo', boss_arena=True, size=25, tint=(59,64,70), ship=None,
        rocks={(3,4),(6,7),(10,3),(16,5),(21,8),(4,14),(9,18),(16,16),(21,19)}, spawns=[], nodes=salvage('dornak_mine',[(5,10),(12,6),(19,12)]),
        exits=[dict(at=(11,22),direction=(0,1),target='dornak_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='dornak_forge_plateaus',arrival=(22,12),key='D / terraços')],
        landmarks=[dict(id='mekron_site',pos=(14,12),text='O teto da mina pulsa como um campo magnético vivo. Mekron ergue-se no centro do corredor.',boss_site='mekron')], settlement=None,
        description='Uma câmara profunda onde magnetismo e metal se fundem em uma paisagem impossível.'),

    'nyxara_landing': dict(name='Nyxara — Crepúsculo Perpétuo', size=23, tint=(58,60,74), ship=SHIP,
        rocks={(3,4),(7,5),(12,3),(17,5),(20,9),(4,13),(9,17),(15,15),(19,19)}, nodes=salvage('nyxara_landing',[(5,8),(14,8),(18,14)]) + flora('nyxara_light',[(8,6),(17,13)],'Flor de Sal Negro'),
        spawns=[('gloom_moth',(9,12)),('vesper_cat',(17,8)),('gloom_moth',(13,17))],
        exits=[dict(at=(22,11),direction=(1,0),target='nyxara_twilight_grotto',arrival=(0,11),key='D / grutas'),dict(at=(11,0),direction=(0,-1),target='nyxara_abyssal_burrow',arrival=(11,22),key='W / abismo')],
        landmarks=[dict(id='nocther_marker_01',pos=(20,10),text='A luz some em um padrão circular. Uma criatura grande deixa marcas nas paredes de pedra negra.',boss_route_marker='nocther')], settlement=None,
        description='Nyxara permanece sob uma penumbra contínua. O céu parece sempre alguns minutos antes da noite.'),
    'nyxara_twilight_grotto': dict(name='Nyxara — Grutas do Crepúsculo', size=23, tint=(55,57,69), ship=None,
        rocks={(2,5),(6,3),(10,7),(16,4),(21,8),(4,15),(11,14),(17,18),(8,20)}, nodes=salvage('nyxara_grotto',[(5,9),(13,8),(18,15)]) + flora('nyxara_grotto_flora',[(8,11),(19,17)],'Flor de Sal Negro'),
        spawns=[('gloom_moth',(8,13)),('vesper_cat',(15,10)),('gloom_moth',(18,16)),('vesper_cat',(11,19))],
        exits=[dict(at=(0,11),direction=(-1,0),target='nyxara_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='nyxara_abyssal_burrow',arrival=(0,12),key='D / abismo')],
        landmarks=[dict(id='nocther_marker_02',pos=(20,17),text='As paredes possuem marcas paralelas. Algo com garras longas atravessou a gruta em alta velocidade.',boss_route_marker='nocther')], settlement=None,
        description='Cavernas iluminadas apenas por linhas minerais muito fracas. O som é absorvido por uma camada de poeira escura.'),
    'nyxara_abyssal_burrow': dict(name='Nyxara — Toca Abissal', boss_arena=True, size=25, tint=(43,44,54), ship=None,
        rocks={(2,4),(5,7),(9,5),(15,4),(21,8),(4,15),(10,18),(16,17),(21,20)}, nodes=salvage('nyxara_abyss',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(11,22),direction=(0,1),target='nyxara_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='nyxara_twilight_grotto',arrival=(22,12),key='D / grutas')],
        landmarks=[dict(id='nocther_site',pos=(14,12),text='Dois pontos violetas surgem no escuro. Nocther observa em silêncio a partir do fundo da toca.',boss_site='nocther')], settlement=None,
        description='Uma toca circular absorve quase toda a luz. A presença de Nocther altera a temperatura do ar ao redor.'),

    'zereth_landing': dict(name='Zereth — Nuvens de Carga', size=23, tint=(72,83,91), ship=SHIP,
        rocks={(2,3),(6,5),(12,4),(17,6),(20,9),(4,14),(9,17),(16,15),(19,19)}, nodes=salvage('zereth_landing',[(5,8),(14,9),(18,14)]) + flora('zereth_stormflora',[(8,6),(17,13)],'Orquídea Fotônica'),
        spawns=[('charge_ray',(8,13)),('ion_toad',(17,9)),('charge_ray',(14,17))],
        exits=[dict(at=(22,11),direction=(1,0),target='zereth_cloudstep',arrival=(0,11),key='D / plataforma'),dict(at=(11,0),direction=(0,-1),target='zereth_skyspine',arrival=(11,22),key='W / coluna')],
        landmarks=[dict(id='voltrik_marker_01',pos=(20,10),text='Relâmpagos atingem sempre o mesmo eixo. A Manopla detecta atividade orgânica no centro da tempestade.',boss_route_marker='voltrik')], settlement=None,
        description='Nuvens carregadas formam rios no céu. Toda superfície metálica da nave acumula carga em poucos minutos.'),
    'zereth_cloudstep': dict(name='Zereth — Passagens da Tempestade', size=23, tint=(66,78,88), ship=None,
        rocks={(3,4),(7,3),(11,6),(16,5),(20,10),(5,14),(10,14),(15,17),(8,20)}, nodes=salvage('zereth_cloudstep',[(5,9),(13,7),(18,15)]) + flora('zereth_cloudflora',[(7,11),(18,18)],'Orquídea Fotônica'),
        spawns=[('ion_toad',(8,12)),('charge_ray',(15,10)),('ion_toad',(18,16)),('charge_ray',(11,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='zereth_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='zereth_skyspine',arrival=(0,12),key='D / coluna')],
        landmarks=[dict(id='voltrik_marker_02',pos=(20,18),text='Uma torre natural se ergue no horizonte. Descargas convergem para seu topo.',boss_route_marker='voltrik')], settlement=None,
        description='Plataformas de rocha suspensa se conectam por pontes naturais. A atmosfera vibra a cada descarga.'),
    'zereth_skyspine': dict(name='Zereth — Coluna Celeste', boss_arena=True, size=25, tint=(56,68,79), ship=None,
        rocks={(3,4),(7,6),(10,3),(16,4),(21,8),(4,15),(10,18),(17,16),(21,20)}, nodes=salvage('zereth_spine',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(11,22),direction=(0,1),target='zereth_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='zereth_cloudstep',arrival=(22,12),key='D / nuvens')],
        landmarks=[dict(id='voltrik_site',pos=(14,12),text='O centro da coluna é um mar de raios. Voltrik toma forma entre as descargas.',boss_site='voltrik')], settlement=None,
        description='Uma coluna de rocha e energia atravessa as nuvens. A arena do boss é o ponto de maior concentração elétrica.'),

    # Pyraxis / Alphor
    'pyraxis_landing': dict(name='Pyraxis — Campo de Cinzas', size=23, tint=(116,64,51), ship=SHIP,
        rocks={(2,4),(6,5),(11,3),(16,5),(20,9),(4,14),(9,18),(15,16),(19,19)}, nodes=salvage('pyraxis_landing',[(5,8),(14,9),(18,14)]) + flora('pyraxis_flora',[(8,6),(17,12)],'Lótus de Cinza','fiery'),
        spawns=[('cinder_strider',(8,13)),('magma_beetle',(17,9)),('cinder_strider',(13,18))],
        exits=[dict(at=(22,11),direction=(1,0),target='pyraxis_vent_fields',arrival=(0,11),key='D / caldeiras'),dict(at=(11,0),direction=(0,-1),target='pyraxis_caldera',arrival=(11,22),key='W / vulcão')],
        landmarks=[dict(id='alphor_marker_01',pos=(20,10),text='A crosta se abre em fendas laranjas. O calor aumenta na direção de um vulcão ativo.',boss_route_marker='alphor')], settlement=None,
        description='Pyraxis é um mundo de crostas quebradas e rios de magma subterrâneo.'),
    'pyraxis_vent_fields': dict(name='Pyraxis — Campos de Ventos Ígneos', size=23, tint=(131,68,49), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,10),(5,14),(10,13),(16,17),(8,19)}, nodes=salvage('pyraxis_vents',[(5,9),(13,7),(18,15)]) + flora('pyraxis_vents_flora',[(7,11),(18,18)],'Lótus de Cinza','fiery'),
        spawns=[('magma_beetle',(8,13)),('cinder_strider',(15,10)),('magma_beetle',(18,16)),('cinder_strider',(11,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='pyraxis_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='pyraxis_caldera',arrival=(0,12),key='D / vulcão')],
        landmarks=[dict(id='alphor_marker_02',pos=(20,18),text='Línguas de fogo sobem de uma fissura. A silhueta de algo com chifres cruza a fumaça.',boss_route_marker='alphor')], settlement=None,
        description='Campos de chaminés vulcânicas cobrem o terreno. O ar é quente demais para permanecer parado por muito tempo.'),
    'pyraxis_caldera': dict(name='Pyraxis — Caldeira de Alphor', boss_arena=True, size=25, tint=(104,55,47), ship=None,
        rocks={(2,4),(6,7),(10,3),(16,4),(21,8),(4,15),(10,18),(16,17),(21,20)}, nodes=salvage('pyraxis_caldera',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(11,22),direction=(0,1),target='pyraxis_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='pyraxis_vent_fields',arrival=(22,12),key='D / campos')],
        landmarks=[dict(id='alphor_site',pos=(14,12),text='O vulcão abre uma cratera gigantesca. Alphor ergue-se entre rios de fogo.',boss_site='alphor'), dict(id='alphor_volcano',pos=(11,8),text='A encosta interna do vulcão permanece em erupção constante.',feature='volcano')], settlement=None,
        description='Uma caldeira colossal com crateras, fluxos de magma e fumaça espessa. Aqui vive o Balrog Alphor.'),

    # ------------------------------------------------------------------
    # GALÁXIA MERIDION — oceano, fungos, vento e cidade cosmopolita
    # ------------------------------------------------------------------
    'thalassene_landing': dict(name='Thalassene — Recifes Rasos', size=23, tint=(59,105,119), ship=SHIP,
        rocks={(2,4),(6,5),(11,3),(16,5),(20,9),(4,14),(9,18),(15,16),(19,19)}, nodes=salvage('thalassene_landing',[(5,8),(14,9),(18,14)]) + flora('thalassene_flora',[(8,6),(17,12)],'Fungo Velado','luminous'),
        spawns=[('reef_skimmer',(8,13)),('tide_serpent',(17,9)),('reef_skimmer',(13,18))],
        exits=[dict(at=(22,11),direction=(1,0),target='thalassene_reef_flats',arrival=(0,11),key='D / recifes'),dict(at=(11,0),direction=(0,-1),target='thalassene_tidemaw',arrival=(11,22),key='W / fossa')],
        landmarks=[dict(id='moryss_marker_01',pos=(20,10),text='Correntes profundas partem do recife. Um rastro enorme segue para a fossa.',boss_route_marker='moryss')], settlement=None,
        description='Água rasa sobre placas de coral mineralizado. A nave pousou sobre uma plataforma estabilizada entre recifes.'),
    'thalassene_reef_flats': dict(name='Thalassene — Planícies de Recife', size=23, tint=(56,111,126), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,10),(5,14),(10,13),(16,17),(8,19)}, nodes=salvage('thalassene_reef',[(5,9),(13,7),(18,15)]) + flora('thalassene_reef_flora',[(7,11),(18,18)],'Fungo Velado','luminous'),
        spawns=[('tide_serpent',(8,13)),('reef_skimmer',(15,10)),('tide_serpent',(18,16)),('reef_skimmer',(11,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='thalassene_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='thalassene_tidemaw',arrival=(0,12),key='D / fossa')],
        landmarks=[dict(id='moryss_marker_02',pos=(20,18),text='Marcas largas de mandíbula aparecem no recife. Algo abriu caminho por dentro da pedra coralina.',boss_route_marker='moryss')], settlement=None,
        description='Planícies de recife conectadas por canais. O som da água é constante e o solo é instável.'),
    'thalassene_tidemaw': dict(name='Thalassene — Fossa da Maré', boss_arena=True, size=25, tint=(44,84,100), ship=None,
        rocks={(2,4),(6,7),(10,3),(16,4),(21,8),(4,15),(10,18),(16,17),(21,20)}, nodes=salvage('thalassene_tidemaw',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(11,22),direction=(0,1),target='thalassene_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='thalassene_reef_flats',arrival=(22,12),key='D / recifes')],
        landmarks=[dict(id='moryss_site',pos=(14,12),text='As águas se levantam em torno de uma mandíbula colossal. Moryss observa do fundo da fossa.',boss_site='moryss')], settlement=None,
        description='Uma cavidade oceânica profunda onde uma criatura de maré controla as correntes ao redor.'),

    'mycelon_landing': dict(name='Mycelon — Floresta Esporal', size=23, tint=(63,94,69), ship=SHIP,
        rocks={(2,4),(6,5),(11,3),(16,5),(20,9),(4,14),(9,18),(15,16),(19,19)}, nodes=salvage('mycelon_landing',[(5,8),(14,9),(18,14)]) + flora('mycelon_flora',[(8,6),(17,12)],'Fungo Velado','luminous'),
        spawns=[('spore_hare',(8,13)),('mycelial_beast',(17,9)),('spore_hare',(13,18))],
        exits=[dict(at=(22,11),direction=(1,0),target='mycelon_sporewood',arrival=(0,11),key='D / floresta'),dict(at=(11,0),direction=(0,-1),target='mycelon_heartgrove',arrival=(11,22),key='W / coração')],
        landmarks=[dict(id='verdak_marker_01',pos=(20,10),text='Esporos formam um corredor em direção a uma clareira central. A Manopla detecta uma massa vegetal anormal.',boss_route_marker='verdak')], settlement=None,
        description='Uma floresta de fungos gigantes transforma a luz em uma névoa verde permanente.'),
    'mycelon_sporewood': dict(name='Mycelon — Bosque de Esporos', size=23, tint=(57,88,62), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,10),(5,14),(10,13),(16,17),(8,19)}, nodes=salvage('mycelon_sporewood',[(5,9),(13,7),(18,15)]) + flora('mycelon_sporeflora',[(7,11),(18,18)],'Fungo Velado','luminous'),
        spawns=[('mycelial_beast',(8,13)),('spore_hare',(15,10)),('mycelial_beast',(18,16)),('spore_hare',(11,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='mycelon_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='mycelon_heartgrove',arrival=(0,12),key='D / coração')],
        landmarks=[dict(id='verdak_marker_02',pos=(20,18),text='As raízes engrossam em direção à clareira. Um pulso orgânico atravessa o solo.',boss_route_marker='verdak')], settlement=None,
        description='Cogumelos gigantes bloqueiam a visão e raízes formam passagens naturais. O chão parece respirar.'),
    'mycelon_heartgrove': dict(name='Mycelon — Bosque do Coração', boss_arena=True, size=25, tint=(49,77,55), ship=None,
        rocks={(2,4),(6,7),(10,3),(16,4),(21,8),(4,15),(10,18),(16,17),(21,20)}, nodes=salvage('mycelon_heart',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(11,22),direction=(0,1),target='mycelon_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='mycelon_sporewood',arrival=(22,12),key='D / bosque')],
        landmarks=[dict(id='verdak_site',pos=(14,12),text='Uma árvore-fungo gigantesca ocupa a clareira. Verdak emerge do emaranhado de raízes.',boss_site='verdak')], settlement=None,
        description='O maior organismo de Mycelon forma uma arena circular, conectando o solo e o teto por uma única estrutura.'),

    'tethra_landing': dict(name='Tethra — Baixo Céu', size=23, tint=(76,90,102), ship=SHIP,
        rocks={(2,4),(6,5),(11,3),(16,5),(20,9),(4,14),(9,18),(15,16),(19,19)}, nodes=salvage('tethra_landing',[(5,8),(14,9),(18,14)]) + flora('tethra_flora',[(8,6),(17,12)],'Líquen Prismático'),
        spawns=[('wind_stalker',(8,13)),('leviwing',(17,9)),('wind_stalker',(13,18))],
        exits=[dict(at=(22,11),direction=(1,0),target='tethra_wind_canyons',arrival=(0,11),key='D / cânions'),dict(at=(11,0),direction=(0,-1),target='tethra_monolith',arrival=(11,22),key='W / monólito')],
        landmarks=[dict(id='gravorn_marker_01',pos=(20,10),text='O vento muda de direção a cada alguns segundos. Pedaços de pedra seguem a mesma trajetória, como se obedecessem a um corpo invisível.',boss_route_marker='gravorn')], settlement=None,
        description='A atmosfera fina deixa o horizonte enorme. Correntes de ar rasgam os vales entre monólitos naturais.'),
    'tethra_wind_canyons': dict(name='Tethra — Cânions do Vento', size=23, tint=(70,82,95), ship=None,
        rocks={(3,4),(7,3),(12,6),(17,5),(20,10),(5,14),(10,13),(16,17),(8,19)}, nodes=salvage('tethra_canyons',[(5,9),(13,7),(18,15)]) + flora('tethra_windflora',[(7,11),(18,18)],'Líquen Prismático'),
        spawns=[('leviwing',(8,13)),('wind_stalker',(15,10)),('leviwing',(18,16)),('wind_stalker',(11,18))],
        exits=[dict(at=(0,11),direction=(-1,0),target='tethra_landing',arrival=(22,11),key='A / pouso'),dict(at=(22,12),direction=(1,0),target='tethra_monolith',arrival=(0,12),key='D / monólito')],
        landmarks=[dict(id='gravorn_marker_02',pos=(20,18),text='Grandes marcas circulares cortam a pedra. Um objeto de massa enorme foi arrastado pelo cânion.',boss_route_marker='gravorn')], settlement=None,
        description='Cânions longos servem como túneis de vento. O deslocamento exige atenção às correntes.'),
    'tethra_monolith': dict(name='Tethra — Monólito Suspenso', boss_arena=True, size=25, tint=(61,71,83), ship=None,
        rocks={(2,4),(6,7),(10,3),(16,4),(21,8),(4,15),(10,18),(16,17),(21,20)}, nodes=salvage('tethra_monolith',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(11,22),direction=(0,1),target='tethra_landing',arrival=(11,0),key='S / pouso'),dict(at=(0,12),direction=(-1,0),target='tethra_wind_canyons',arrival=(22,12),key='D / cânions')],
        landmarks=[dict(id='gravorn_site',pos=(14,12),text='O monólito flutua a poucos centímetros do chão. Gravorn assume a forma de uma massa rochosa ambulante.',boss_site='gravorn')], settlement=None,
        description='Uma pedra colossal suspensa por um fenômeno gravitacional anômalo. O boss domina o centro da arena.'),

    # Nerissa: cidade distribuída em 3 mapas, com habitantes de várias origens.
    'nerissa_landing': dict(name='Nerissa — Porto de Chegada', size=23, tint=(83,88,98), ship=SHIP,
        rocks={(2,4),(5,7),(8,3),(16,5),(20,8),(4,14),(9,18),(15,16),(19,19)}, nodes=salvage('nerissa_port',[(5,9),(14,8),(18,14)]),
        spawns=[('street_drone',(8,13)),('plasma_hound',(17,9)),('street_drone',(13,18))],
        exits=[dict(at=(22,11),direction=(1,0),target='nerissa_bazaar',arrival=(0,12),key='D / cidade'),dict(at=(11,0),direction=(0,-1),target='nerissa_tower_crown',arrival=(11,22),key='W / torre',boss_gate=True,boss_id='broom')],
        landmarks=[dict(id='nerissa_port_terminal',pos=(20,9),text='Terminais exibem símbolos de dezenas de mundos. Há registros de comerciantes, refugiados e tripulações de várias origens.',feature='city'),
                   dict(id='nerissa_broom_marker',pos=(20,18),text='Um arranha-céu se ergue no centro da cidade. O topo recebe descargas elétricas quase periódicas.',boss_route_marker='broom')],
        settlement={'id':'nerissa_port','name':'Porto de Nerissa','civilization':'nerissans','language':'Neris','center':(14,9),'sight_radius':8,
            'structures':[{'type':'city_gate','pos':(14,9)},{'type':'dwelling','pos':(11,8)},{'type':'watch','pos':(17,10)}],
            'npcs':[
                {'id':'nerissa_avarin','name':'Lira Voss','role':'Comerciante Avarin','faction':None,'pos':(12,9),'kind':'avarin','civilization':'avarin','solid':True,'dialogue':'Ela vende filtros de água e reconhece imediatamente os equipamentos Avarin.'},
                {'id':'nerissa_dran','name':'Korr','role':'Mecânico Draan','faction':None,'pos':(15,8),'kind':'avarin_guard','civilization':'dran','solid':True,'dialogue':'Ele aponta para uma caixa de componentes magnéticos e aguarda alguma forma de tradução.'},
                {'id':'nerissa_nahr','name':'Sombra de Viajante','role':'Mensageira de Nahr','faction':None,'pos':(16,11),'kind':'nahr_shadow','civilization':'nahr_shadows','solid':True,'dialogue':'A pequena sombra faz os mesmos gestos silenciosos que você já conhece de Nahr.'},
            ],'description':'Um porto urbano mistura habitantes de muitos mundos. A cidade é organizada por distritos e espécies, não por uma única origem.'},
        description='O porto de Nerissa concentra embarcações de diversos planetas e funciona como entrada para a cidade.'),
    'nerissa_bazaar': dict(name='Nerissa — Bazar dos Mundos', size=25, tint=(88,79,95), ship=None,
        rocks={(2,5),(6,3),(11,5),(17,4),(22,8),(4,15),(9,19),(15,17),(21,21)}, nodes=salvage('nerissa_bazaar_nodes',[(5,10),(12,7),(19,14)]),
        spawns=[('street_drone',(8,13)),('plasma_hound',(15,10)),('street_drone',(19,17)),('plasma_hound',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='nerissa_landing',arrival=(22,11),key='A / porto'),dict(at=(24,12),direction=(1,0),target='nerissa_tower_crown',arrival=(0,12),key='D / torre',boss_gate=True,boss_id='broom')],
        landmarks=[dict(id='nerissa_market',pos=(13,10),text='Barracas mostram artefatos de Dornak, fibras de Mycelon, conchas de Thalassene e símbolos de Nahr. É o maior ponto de encontro interplanetário conhecido.',feature='city')],
        settlement={'id':'nerissa_bazaar_settlement','name':'Bazar dos Mundos','civilization':'nerissans','language':'Neris','center':(13,10),'sight_radius':9,
            'structures':[{'type':'city_gate','pos':(13,10)},{'type':'shade','pos':(10,8)},{'type':'watch','pos':(17,11)},{'type':'dwelling','pos':(14,14)}],
            'npcs':[
                {'id':'nerissa_velkari','name':'Seli','role':'Navegadora Velkari','faction':None,'pos':(10,10),'kind':'avarin','civilization':'velkari','solid':True,'dialogue':'Ela descreve as marés comerciais de Thalassene e pergunta sobre outras rotas.'},
                {'id':'nerissa_nyxen','name':'Nyr','role':'Cartógrafo Nyxen','faction':None,'pos':(16,9),'kind':'avarin','civilization':'nyxen','solid':True,'dialogue':'Ele guarda mapas de Nyxara e demonstra conhecer rotas de cavernas desconhecidas.'},
                {'id':'nerissa_mycelari','name':'Oru','role':'Cultivador Mycelari','faction':None,'pos':(15,13),'kind':'avarin','civilization':'mycelari','solid':True,'dialogue':'Ele transporta cápsulas de esporos e tenta registrar sua armadura como um organismo estranho.'},
            ],'description':'Um mercado enorme reúne idiomas, moedas, técnicas e objetos de dezenas de mundos.'},
        description='O bazar ocupa quarteirões inteiros. Comerciantes de vários planetas dividem as mesmas ruas.'),
    'nerissa_tower_crown': dict(name='Nerissa — Coroa da Torre', boss_arena=True, size=25, tint=(52,58,72), ship=None,
        rocks={(2,4),(7,7),(11,3),(16,5),(21,8),(4,16),(9,19),(16,17),(21,20)}, nodes=salvage('nerissa_tower_nodes',[(5,11),(12,7),(19,13)]), spawns=[],
        exits=[dict(at=(0,12),direction=(-1,0),target='nerissa_bazaar',arrival=(24,12),key='A / bazar'),dict(at=(11,22),direction=(0,1),target='nerissa_landing',arrival=(11,0),key='S / porto')],
        landmarks=[dict(id='broom_tower',pos=(14,11),text='O topo do arranha-céu recebe um raio vertical. Broom permanece imóvel entre os cabos de energia da cidade.',boss_site='broom'), dict(id='nerissa_city_tower',pos=(11,9),text='A cidade inteira se espalha abaixo da torre.',feature='tower')], settlement=None,
        description='A cobertura da maior torre de Nerissa. O boss Broom aguarda no topo, acima das luzes da cidade.'),
}

# Cada planeta da expansão mantém a estrutura de quatro mapas usada na progressão
# existente: pouso -> área intermediária -> área avançada -> arena reservada.
# Os mapas adicionais não criam sistemas novos; apenas ampliam exploração e fauna.
SECTORS_060.update({
    'dornak_deep_shaft': dict(name='Dornak — Poço Profundo', size=24, tint=(72,76,80), ship=None,
        rocks={(3,4),(6,7),(11,4),(16,5),(21,9),(5,14),(10,17),(17,16),(20,20)},
        nodes=salvage('dornak_deep',[(5,10),(13,7),(19,15)]) + flora('dornak_deep_lichen',[(8,12),(17,18)],'Líquen Prismático'),
        spawns=[('ferrous_mite',(8,13)),('magnetic_ram',(15,9)),('ferrous_mite',(18,16)),('magnetic_ram',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='dornak_forge_plateaus',arrival=(22,12),key='A / terraços'),dict(at=(23,12),direction=(1,0),target='dornak_core_mine',arrival=(0,12),key='D / mina')],
        landmarks=[dict(id='mekron_marker_03',pos=(20,10),text='O poço desce até uma rede de galerias em que o magnetismo quase imobiliza pequenos fragmentos metálicos.',boss_route_marker='mekron')], settlement=None,
        description='Um eixo vertical convertido em corredor subterrâneo. Quanto mais fundo, mais forte a atração magnética.'),
    'nyxara_silent_depths': dict(name='Nyxara — Profundezas Silenciosas', size=24, tint=(49,50,61), ship=None,
        rocks={(3,4),(7,5),(12,3),(17,6),(21,9),(5,14),(10,16),(16,18),(20,20)},
        nodes=salvage('nyxara_depths',[(5,10),(13,7),(19,15)]) + flora('nyxara_depthflora',[(8,12),(17,18)],'Flor de Sal Negro'),
        spawns=[('gloom_moth',(8,13)),('vesper_cat',(15,9)),('gloom_moth',(18,16)),('vesper_cat',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='nyxara_twilight_grotto',arrival=(22,12),key='A / grutas'),dict(at=(23,12),direction=(1,0),target='nyxara_abyssal_burrow',arrival=(0,12),key='D / abismo')],
        landmarks=[dict(id='nocther_marker_03',pos=(20,18),text='O som desaparece completamente por alguns metros. Marcas de garras interrompem a poeira em linhas perfeitas.',boss_route_marker='nocther')], settlement=None,
        description='Uma galeria onde até passos parecem abafados. Pequenas fontes de luz biológica orientam a descida.'),
    'zereth_storm_tunnel': dict(name='Zereth — Túnel de Tempestade', size=24, tint=(62,73,84), ship=None,
        rocks={(3,4),(7,4),(11,6),(16,5),(21,9),(5,14),(10,16),(17,18),(20,20)},
        nodes=salvage('zereth_tunnel',[(5,10),(13,7),(19,15)]) + flora('zereth_tunnelflora',[(8,12),(17,17)],'Orquídea Fotônica'),
        spawns=[('charge_ray',(8,13)),('ion_toad',(15,9)),('charge_ray',(18,16)),('ion_toad',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='zereth_cloudstep',arrival=(22,12),key='A / passagens'),dict(at=(23,12),direction=(1,0),target='zereth_skyspine',arrival=(0,12),key='D / coluna')],
        landmarks=[dict(id='voltrik_marker_03',pos=(20,18),text='O túnel canaliza descargas para um único eixo. Cada trovão coincide com uma vibração no solo.',boss_route_marker='voltrik')], settlement=None,
        description='Uma passagem fechada que conduz a eletricidade atmosférica para a coluna central de Zereth.'),
    'pyraxis_lava_ravine': dict(name='Pyraxis — Ravina da Lava', size=24, tint=(122,61,48), ship=None,
        rocks={(3,4),(7,4),(11,6),(16,5),(21,9),(5,14),(10,16),(17,18),(20,20)},
        nodes=salvage('pyraxis_ravine',[(5,10),(13,7),(19,15)]) + flora('pyraxis_ravineflora',[(8,12),(17,17)],'Lótus de Cinza','fiery'),
        spawns=[('cinder_strider',(8,13)),('magma_beetle',(15,9)),('cinder_strider',(18,16)),('magma_beetle',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='pyraxis_vent_fields',arrival=(22,12),key='A / campos'),dict(at=(23,12),direction=(1,0),target='pyraxis_caldera',arrival=(0,12),key='D / caldeira')],
        landmarks=[dict(id='alphor_marker_03',pos=(20,18),text='Uma ravina aberta expõe um rio de magma. O som de uma criatura enorme vem do interior da montanha.',boss_route_marker='alphor')], settlement=None,
        description='Uma garganta atravessada por canais de magma exposto. O caminho até a caldeira passa entre paredes incandescentes.'),
    'thalassene_tide_caves': dict(name='Thalassene — Cavernas da Maré', size=24, tint=(50,94,108), ship=None,
        rocks={(3,4),(7,4),(11,6),(16,5),(21,9),(5,14),(10,16),(17,18),(20,20)},
        nodes=salvage('thalassene_caves',[(5,10),(13,7),(19,15)]) + flora('thalassene_caveflora',[(8,12),(17,17)],'Fungo Velado','luminous'),
        spawns=[('reef_skimmer',(8,13)),('tide_serpent',(15,9)),('reef_skimmer',(18,16)),('tide_serpent',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='thalassene_reef_flats',arrival=(22,12),key='A / recifes'),dict(at=(23,12),direction=(1,0),target='thalassene_tidemaw',arrival=(0,12),key='D / fossa')],
        landmarks=[dict(id='moryss_marker_03',pos=(20,18),text='As águas formam bolsões que sobem e descem como respiração. O rastro da criatura termina na fossa.',boss_route_marker='moryss')], settlement=None,
        description='Cavernas inundadas parcialmente pela maré, com plataformas secas entre canais de água profunda.'),
    'mycelon_spore_chambers': dict(name='Mycelon — Câmaras de Esporos', size=24, tint=(54,83,60), ship=None,
        rocks={(3,4),(7,4),(11,6),(16,5),(21,9),(5,14),(10,16),(17,18),(20,20)},
        nodes=salvage('mycelon_chambers',[(5,10),(13,7),(19,15)]) + flora('mycelon_chamberflora',[(8,12),(17,17)],'Fungo Velado','luminous'),
        spawns=[('spore_hare',(8,13)),('mycelial_beast',(15,9)),('spore_hare',(18,16)),('mycelial_beast',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='mycelon_sporewood',arrival=(22,12),key='A / bosque'),dict(at=(23,12),direction=(1,0),target='mycelon_heartgrove',arrival=(0,12),key='D / coração')],
        landmarks=[dict(id='verdak_marker_03',pos=(20,18),text='As câmaras estão cobertas por casulos de esporo. O pulso da raiz-mãe atravessa as paredes.',boss_route_marker='verdak')], settlement=None,
        description='Salões orgânicos onde o ar se enche de partículas luminosas. O centro da colônia está logo adiante.'),
    'tethra_wind_bridge': dict(name='Tethra — Ponte do Vento', size=24, tint=(68,80,94), ship=None,
        rocks={(3,4),(7,4),(11,6),(16,5),(21,9),(5,14),(10,16),(17,18),(20,20)},
        nodes=salvage('tethra_bridge',[(5,10),(13,7),(19,15)]) + flora('tethra_bridgeflora',[(8,12),(17,17)],'Líquen Prismático'),
        spawns=[('wind_stalker',(8,13)),('leviwing',(15,9)),('wind_stalker',(18,16)),('leviwing',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='tethra_wind_canyons',arrival=(22,12),key='A / cânions'),dict(at=(23,12),direction=(1,0),target='tethra_monolith',arrival=(0,12),key='D / monólito')],
        landmarks=[dict(id='gravorn_marker_03',pos=(20,18),text='Uma ponte natural suspende-se sobre uma queda sem fundo. Pedras flutuam seguindo o mesmo eixo do monólito.',boss_route_marker='gravorn')], settlement=None,
        description='Uma passagem estreita de pedra suspensa sobre um abismo de vento. Cada rajada altera a sensação de gravidade.'),
    'nerissa_transit_district': dict(name='Nerissa — Distrito de Trânsito', size=25, tint=(78,83,99), ship=None,
        rocks={(2,5),(6,3),(11,5),(17,4),(22,8),(4,15),(9,19),(15,17),(21,21)}, nodes=salvage('nerissa_transit_nodes',[(5,10),(12,7),(19,14)]),
        spawns=[('street_drone',(8,13)),('plasma_hound',(15,10)),('street_drone',(19,17)),('plasma_hound',(11,19))],
        exits=[dict(at=(0,12),direction=(-1,0),target='nerissa_bazaar',arrival=(24,12),key='A / bazar'),dict(at=(24,12),direction=(1,0),target='nerissa_tower_crown',arrival=(0,12),key='D / torre')],
        landmarks=[dict(id='nerissa_transit_hub',pos=(13,10),text='Trilhos, elevadores e passarelas ligam diferentes níveis da cidade. Idiomas desconhecidos aparecem nos painéis ao lado de símbolos universais.',feature='city')],
        settlement={'id':'nerissa_transit_settlement','name':'Distrito de Trânsito','civilization':'nerissans','language':'Neris','center':(13,10),'sight_radius':10,
            'structures':[{'type':'city_gate','pos':(13,10)},{'type':'city_block','pos':(10,8)},{'type':'city_block','pos':(17,9)},{'type':'watch','pos':(15,14)}],
            'npcs':[
                {'id':'nerissa_tethran','name':'Vael','role':'Mensageiro Tethran','faction':None,'pos':(10,10),'kind':'avarin','civilization':'tethran','solid':True,'dialogue':'O mensageiro mostra uma rota aérea e tenta negociar sem um tradutor comum.'},
                {'id':'nerissa_nyxen_2','name':'Syr','role':'Viajante Nyxen','faction':None,'pos':(16,10),'kind':'avarin','civilization':'nyxen','solid':True,'dialogue':'A viajante aponta para os sinais luminosos do terminal e espera sua resposta.'},
                {'id':'nerissa_dran_2','name':'Rokk','role':'Técnico Draan','faction':None,'pos':(13,14),'kind':'avarin','civilization':'dran','solid':True,'dialogue':'Ele oferece uma peça metálica e repete uma frase curta, ainda indecifrável para o elmo.'},
            ],'description':'Uma área de conexão entre os bairros. Pessoas de várias civilizações atravessam o mesmo corredor a todo instante.'},
        description='O maior entroncamento urbano de Nerissa conecta plataformas, elevadores e linhas de transporte da cidade. Leva diretamente à torre central.'),
})

# Reencadeamento dos planetas: as quatro áreas permanecem conectadas em circuito,
# mas a arena reservada deixa de ter acesso direto a partir do pouso.
_060_CHAINS = {
    'dornak': ('dornak_landing','dornak_forge_plateaus','dornak_deep_shaft','dornak_core_mine'),
    'nyxara': ('nyxara_landing','nyxara_twilight_grotto','nyxara_silent_depths','nyxara_abyssal_burrow'),
    'zereth': ('zereth_landing','zereth_cloudstep','zereth_storm_tunnel','zereth_skyspine'),
    'pyraxis': ('pyraxis_landing','pyraxis_vent_fields','pyraxis_lava_ravine','pyraxis_caldera'),
    'thalassene': ('thalassene_landing','thalassene_reef_flats','thalassene_tide_caves','thalassene_tidemaw'),
    'mycelon': ('mycelon_landing','mycelon_sporewood','mycelon_spore_chambers','mycelon_heartgrove'),
    'tethra': ('tethra_landing','tethra_wind_canyons','tethra_wind_bridge','tethra_monolith'),
    'nerissa': ('nerissa_landing','nerissa_bazaar','nerissa_transit_district','nerissa_tower_crown'),
}
for _planet, (_land, _mid, _deep, _boss_arena) in _060_CHAINS.items():
    _boss_id = next((bid for bid, aid in BOSS_ARENAS.items() if aid == _boss_arena), _planet)
    _L = SECTORS_060[_land]; _M = SECTORS_060[_mid]; _D = SECTORS_060[_deep]; _B = SECTORS_060[_boss_arena]
    # Circuito fechado: pouso <-> intermediária <-> arena <-> avançada <-> pouso.
    # Os portais para a arena estão apenas nas áreas avançada/intermediária; o
    # boss continua bloqueado pela regra de progressão em core.boss_available().
    _L['exits'] = [
        dict(at=(22,11),direction=(1,0),target=_mid,arrival=(0,11),key=_L['exits'][0].get('key','D / área')),
        dict(at=(11,0),direction=(0,-1),target=_deep,arrival=(11,23),key=_L['exits'][1].get('key','W / rota')),
    ]
    _M['exits'] = [
        dict(at=(0,11),direction=(-1,0),target=_land,arrival=(22,11),key=_M['exits'][0].get('key','A / pouso')),
        dict(at=(22,12),direction=(1,0),target=_boss_arena,arrival=(0,12),key=_M['exits'][1].get('key','D / arena'),boss_gate=True,boss_id=_boss_id),
    ]
    _D['exits'] = [
        dict(at=(11,23),direction=(0,1),target=_land,arrival=(11,0),key='S / pouso'),
        dict(at=(23,12),direction=(1,0),target=_boss_arena,arrival=(24,12),key='D / arena',boss_gate=True,boss_id=_boss_id),
    ]
    _B['exits'] = [
        dict(at=(0,12),direction=(-1,0),target=_mid,arrival=(22,12),key='A / área intermediária'),
        dict(at=(24,12),direction=(1,0),target=_deep,arrival=(23,12),key='D / rota avançada'),
    ]
del _planet, _land, _mid, _deep, _boss_arena, _boss_id, _L, _M, _D, _B

SECTORS.update(SECTORS_060)

# Portas dos chefes da 0.6.0: primeiro os três Raros do planeta; depois o Lendário da galáxia.
_BOSS_ARENA_GATES_060 = {
    'mekron': 'dornak_core_mine',
    'nocther': 'nyxara_abyssal_burrow',
    'voltrik': 'zereth_skyspine',
    'alphor': 'pyraxis_caldera',
    'moryss': 'thalassene_tidemaw',
    'verdak': 'mycelon_heartgrove',
    'gravorn': 'tethra_monolith',
    'broom': 'nerissa_tower_crown',
}
for _boss_id, _arena_id in _BOSS_ARENA_GATES_060.items():
    for _sector in SECTORS.values():
        for _exit in _sector.get('exits', []):
            if _exit.get('target') == _arena_id:
                _exit['boss_gate'] = True
                _exit['boss_id'] = _boss_id
del _boss_id, _arena_id, _sector, _exit



ALL_NODE_IDS = {n['id'] for data in SECTORS.values() for n in data['nodes']}


def fresh_enemies(sector):
    enemies = []
    for entry in SECTORS[sector]['spawns']:
        if isinstance(entry, dict):
            species = entry['species']; p = entry['pos']
            enemy = dict(species=species, home=list(p), pos=list(p), dead=False, ready=0.0)
            if entry.get('mission_id'):
                enemy['mission_id'] = entry['mission_id']
                enemy['mission_persistent'] = True
            enemies.append(enemy)
        else:
            species, p = entry[:2]
            enemy = dict(species=species, home=list(p), pos=list(p), dead=False, ready=0.0)
            if len(entry) > 2 and entry[2]:
                enemy['mission_id'] = entry[2]
                enemy['mission_persistent'] = True
            enemies.append(enemy)
    return enemies


def protected_tile(sector, pos):
    data = SECTORS[sector]
    distance = lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1])
    return ((data['ship'] is not None and distance(pos, data['ship']) <= 2)
            or any(distance(pos, gate['at']) <= 2 for gate in data['exits']))
