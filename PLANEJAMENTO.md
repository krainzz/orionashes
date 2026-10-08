## 0.6.0 - CONCLUÍDA: expansão intergaláctica

- Núcleo de Dobra instalável no motor da nave e viagens liberadas para Vharos e Meridion.
- Oito novos planetas, dezesseis novas criaturas, seis bosses raros e dois bosses lendários.
- Alphor em Pyraxis com vulcão e mecânica de chifres/Núcleo Ígneo.
- Broom em Nerissa com cidade multicivilizacional e ataque fatal protegido pelo QTE do Escudo Stasis.
- Calibração linguística por QTE para civilizações desconhecidas.
- Persistência e migração de save preservadas.

## 0.5.9 - Hotfixes e rebalanceamento

- Fenda das Raízes povoada com fauna local; Vazio de RY permanece vazio até sua revelação.
- Missão de RY reconhece contato prévio com as Sombras de Nahr e pula a etapa de conversa quando já cumprida.
- RY concede Núcleo de Dobra apenas na primeira vitória real.
- Cartas sem benefício permanente de DEF e com um único buff de atributo conforme a raridade.
- Taxa Crítica e Dano Crítico escritos por extenso na interface.
- AMP, dano e efeitos das Cartas atualizados conforme a revisão 0.5.9.

# CINZAS DE ÓRION — ROADMAP MESTRE

Documento de acompanhamento do desenvolvimento. Atualizado para a versão 0.5.9.

## Visão do jogo

RPG de exploração espacial com combate por turnos, cartas de poder, coleta, crafting, evolução da armadura, exploração de civilizações, decisões com consequências e progressão por dezenas de galáxias.

O protagonista é um herói tecnológico sobrevivente de uma invasão. Restam a ele a fonte de energia do Peitoral e a Manopla. Ao longo da campanha ele reconstruirá o Elmo e o Módulo de Locomoção, restaurará a nave e eventualmente retornará à galáxia natal.

## Estado consolidado atual

### 0.4.x — Fundação jogável

**Incluído**
- combate por turnos;
- cartas equipáveis na Manopla;
- 3 slots normais + 1 slot especial futuro;
- memória e módulos de memória;
- crafting e coleta persistente;
- setores exploráveis e transições;
- nave como abrigo/oficina e interior da nave;
- Diário e objetivos;
- civilização Avarin em Veyra, assentamento Qaresh e NPCs com física;
- primeiro sistema de missões;
- primeira missão com soluções de reparo, confronto e hack;
- Renome por facção/planeta/galáxia com milestones e resgates;
- achievements e estatísticas;
- dano variável, críticos e atributos ATQ/DEF/AMP/CRIT/DCRIT;
- raridades de cartas e variantes Normal/+ /++;
- NEXUS como progressão cognitiva da Manopla;
- Removedor de Aprimoramento;
- diagnóstico e interior funcional da nave;
- infraestrutura de instalação persistente do Pygame.

### Regras de informação já estabelecidas

- O jogador não vê atributos técnicos dos inimigos durante o combate antes do Scan.
- O jogador vê apenas a barra de HP do inimigo, sem número, antes do Scan.
- Atributos do próprio personagem ficam disponíveis no Status.
- Coletáveis, contagem de fauna, respawns e detalhes técnicos não ficam expostos permanentemente na HUD.
- A Manopla usa um painel digital diegético para mensagens temporárias.

### Regras de progressão já estabelecidas

**Cartas**
- Comum: fauna recorrente e simples.
- Incomum: fauna mais perigosa ou relevante.
- Rara: bosses de mundo/missão.
- Mítica: criaturas sem respawn.
- Lendária: figuras importantes da história.
- Única: exclusivas do futuro slot especial.

Cada carta pode existir em Normal / + / ++.
- Normal: 95% de chance no craft da variante.
- +: 4,5%.
- ++: 0,5%.

As cartas devem conceder apenas os atributos que realmente possuírem.

**Atributos**
- ATQ: poder ofensivo base.
- DEF: resistência do personagem/inimigo.
- AMP: modificador percentual extremamente raro.
- Taxa Crítica: chance de crítico.
- Dano Crítico: multiplicador do crítico.
- Dano Mínimo: modificador futuro para elevar o piso da faixa de dano.

Fórmula-base do dano planejada:

`[ATQ base + (ATQ base × AMP efetivo da Skill) + ATQ da Skill] − DEF`

`AMP efetivo = AMP do personagem + AMP da Skill`

AMP deve ser raro e difícil de acumular. O personagem inicia com 1% vindo do Peitoral.

**NEXUS**
- atualização única da Manopla;
- ganha XP pelo dano causado;
- progressão muito longa;
- melhorias somente ofensivas;
- pequenos ganhos por nível;
- progressão automática, sem pontos para gastar;
- quatro níveis funcionam apenas como marcos cognitivos, sem bônus direto;
- níveis 5, 10 e 15 reservam melhorias para o futuro sistema de hack;
- curva atual: nível 20 em 25.000.000 XP acumulados.

**Coleção completa de cartas**
- todas as cartas normais: ATQ +10;
- todas as cartas +: Dano Crítico +6%;
- todas as cartas ++: AMP +5% + futura recompensa de Carta Única.

**Conquistas gerais**
- recompensas simples de coleta/farm;
- sem acúmulo relevante de poder no início;
- histórico de estatísticas permanentes;
- níveis de coleção permanecem como exceção de recompensa poderosa.

## 0.4.5 — marco anterior já consolidado

O primeiro arco social de Veyra já possui:
- assentamentos;
- NPCs Avarin de perfis diferentes;
- idioma ainda limitado até o uso do Elmo;
- craft e equipamento do Elmo G1;
- análise cultural inicial;
- missão de abastecimento de água;
- três abordagens para resolver a missão;
- primeiros registros de Renome e Incidentes;
- hack integrado à Manopla;
- nave com interior, cockpit, computador e painel de reparos;
- achievements e estatísticas;
- fauna adicional para Veyra.

## 0.4.6 — CONCLUÍDA: Kuvaar, combate tático e Simulador

Implementada e consolidada: seleção explícita de alvo, pontos fracos em boss, Kuvaar, rastros, Água Pura, Bacia Seca, Simulador de Combate e rematches virtuais. O combate comum continua com alvo único; a infraestrutura de `target_mode` já prepara cartas multitarget futuras.

### Próxima etapa — 0.4.7 / Renome e consequências

### Bloco A — Renome por facção
- Renome separado por facção/assentamento/região.
- Barra visual no Status, sem poluir a exploração.
- Faixas qualitativas de relação para uso posterior, sem depender apenas de um número exposto.
- Alterações de diálogo e acesso serão consequência de estado social, não apenas de uma pontuação.

### Bloco B — Notoriedade
- registrar quanto uma ação é conhecida naquela sociedade;
- diferenciar uma ação testemunhada de uma ação escondida;
- permitir que uma ação tenha pouca notoriedade local mesmo alterando o estado real do mundo.

### Bloco C — Incidentes persistentes
Cada incidente deve registrar:
- ação;
- local;
- envolvidos;
- testemunhas;
- sensores/registros;
- transmissão ou não;
- consequência já aplicada.

O sistema não deve duplicar alterações ao recarregar um save.

### Bloco D — Missões com estados mais completos
Estados planejados:
- disponível;
- ativa;
- concluída conforme pedido;
- resolvida por alternativa;
- falhada;
- abandonada;
- indisponível por consequência.

### Bloco E — consequências de assentamento
- NPC pode mudar de posição;
- serviço pode abrir/fechar;
- vigilância pode aumentar;
- recompensa pode mudar;
- missão pode ser substituída ou encerrada;
- morte de NPC importante pode alterar a linha de missão.

## 0.4.7 — expansão dos caminhos de resolução

Possíveis focos, conforme a prioridade escolhida durante o desenvolvimento:
- furtividade física;
- roubo estruturado;
- negociação;
- confronto com defesa organizada;
- estados de acesso a instalações;
- testemunhas e alarmes;
- primeiros efeitos concretos de reputação nas cidades.

## 0.4.8 — Hack 1.0

- minijogo tático de invasão;
- progressão de ferramentas da Manopla;
- firewalls de complexidade crescente;
- terminais, fechaduras, redes locais e drones;
- recompensas diferentes de combate físico;
- falhas com alerta/bloqueio/combate;
- integração com incidentes e notoriedade.

O hack representa operações fictícias dentro do jogo e não interage com sistemas externos reais.

## 0.5.0 — Peitoral, Renome, Bestiário e Rota Estelar inicial

**Cockpit**
- Rota Estelar aberta somente no Cockpit físico;
- planetas selecionáveis por clique;
- destinos ainda desconhecidos aparecem como `???`;
- descoberta nominal preparada para eventos de exploração e narrativa.

**Peitoral / AURORA**
- tela própria do Peitoral;
- slots de memória com estados VAZIO / OCUPADO / BLOQUEADO;
- slots liberados conforme os Tiers do Peitoral;
- AURORA Plus, Nova e Ultimate com bônus substitutivos;
- Plus fabricável em Veyra, níveis seguintes reservados a tecnologia futura.

**Renome**
- reputação individual por facção;
- totais agregados por planeta e galáxia;
- missões concedem Renome à facção beneficiada;
- milestones com recompensas resgatáveis.

**Bestiário / Scan**
- tipo e mapas conhecidos antes do Scan;
- atributos e HP após Scan e novo encontro;
- nível calculado da criatura visível no mapa após o Scan.

## 0.5.x — Módulo de Locomoção

- dash;
- extensão dos slots de memória;
- melhorias de mobilidade;
- acesso a terrenos/obstáculos;
- evolução visual própria da peça;
- progressão separada do NEXUS e do Elmo.

Nome oficial atual: **Módulo de Locomoção**.

## Navegação e restauração da nave

### Etapa 1 — reparo em componentes
Sistemas separados:
- Casco;
- Distribuição de Energia;
- Propulsão;
- Navegação;
- Comunicação.

### Etapa 2 — primeiro voo
- cockpit;
- seleção de destino;
- consumo de combustível;
- animação curta de viagem;
- pouso em setor inicial do planeta destino.

### Etapa 3 — dobra intergaláctica
- núcleo/motor de dobra;
- estabilização;
- recurso de salto raro;
- travessia entre galáxias.

A nave deve salvar galáxia, planeta, setor e estado de cada mundo.

## Universo de 30–40 galáxias

Objetivo de escala:
- aproximadamente 30–40 galáxias;
- média de 5–6 planetas por galáxia;
- a maioria dos planetas possui fauna;
- apenas alguns possuem civilizações;
- mundos extremos devem ser raros.

### Estrutura para diferenciar planetas
Não usar uma grade repetitiva de “gelo/fogo/terra/água”. Cada planeta será definido pela combinação de:
- composição;
- atmosfera;
- gravidade;
- ciclo climático;
- biosfera;
- fenômenos naturais;
- anomalias;
- ruínas;
- civilizações;
- tecnologia;
- recursos;
- ameaças;
- importância narrativa.

A maioria dos planetas deve combinar características em vez de representar um único elemento.

## Civilizações e idiomas

Cada civilização deve ter identidade própria em:
- arquitetura;
- vestuário;
- tecnologia;
- organização social;
- economia;
- relação com o ambiente;
- estrutura linguística;
- crenças/valores quando relevantes.

Os nomes atuais de Veyra permanecem como base:
- planeta: **Veyra**;
- povo: **Avarin**;
- idioma: **Avari**;
- assentamento: **Qaresh**.

## Armadura e representação visual

Peças futuras:
- Peitoral;
- Manopla;
- Elmo;
- Módulo de Locomoção.

A tela de Equipamento deve mostrar as peças como objetos visualmente reconhecíveis.

Quando o sistema gráfico definitivo for criado, a representação poderá mostrar:
- geração da peça;
- estado equipado;
- encaixes;
- módulos/pedras especiais;
- detalhes de evolução.

## Pedras especiais — nome ainda em aberto

Termos provisórios:
- Núcleo de Éon;
- Relíquia de Singularidade;
- Fragmento de Ascensão;
- Prisma Arcaico.

Esses itens devem ser muito raros, ligados a missões difíceis e capazes de produzir bônus excepcionais.

## Card especial e final da campanha

O slot especial da Manopla será reservado às cartas **Únicas**.

Essas cartas terão regras próprias e devem representar eventos, entidades ou poderes que não façam parte do ciclo comum de farm.

No longo prazo:
- novas galáxias;
- civilizações e conflitos;
- progressão dos equipamentos;
- cartas raras/míticas/lendárias/únicas;
- retorno à galáxia natal;
- encerramento do arco da raça conquistadora do planeta natal.

## Princípios para todas as próximas versões

1. Informação técnica deve ser descoberta progressivamente, não exibida toda de uma vez.
2. O poder permanente deve ser caro, demorado ou raro.
3. O início do jogo não deve permitir acúmulo rápido de atributos.
4. Cada nova mecânica deve ter função no mundo, e não apenas existir como menu.
5. NPCs possuem física própria e ocupam espaço físico.
6. WASD/Setas continuam reservados para movimentação quando aplicável; atalhos de menu não devem usar WASD.
7. Saves devem migrar sem duplicar bônus ou efeitos de acontecimentos.
8. Novos materiais importantes não devem ficar todos disponíveis no primeiro planeta.
9. Planetas devem ser diferentes por combinação de características, não por elemento único.
10. O jogador deve conseguir interpretar o mundo pelas descobertas antes de receber todos os números.


### 0.4.6 — estado atual
A revisão atual inclui layout de combate reorganizado, boss Kuvaar destacado no mapa, alerta de zona de perigo e Simulador de Combate como gadget que precisa ser fabricado após a primeira vitória.


### Revisão de dano por zona (0.4.6)
Precisão/Evasão determina somente a chance de acerto. Depois do acerto, a zona corporal altera apenas a Defesa local. Não existe multiplicador de dano escondido por zona; o dano segue exclusivamente a fórmula central.

## 0.5.0 HOTFIX 3 — Cockpit
- Galáxia inicial: **Galáxia Nárion**.
- Cinco planetas visitáveis na configuração atual.
- Painel do Cockpit: nome, atmosfera, temperatura média, luas, civilizações conhecidas e status de voo compacto.


## 0.5.1 — Missões de reparo da nave
- Seis sistemas de voo possuem missões de diagnóstico/reparo independentes e estados persistentes.
- As missões podem ser iniciadas a qualquer momento; não dependem de concluir linhas de facções.
- Casco: sincronização de pulsos estruturais.
- Energia: balanceamento de quatro barramentos.
- Propulsão atmosférica: sequência vetorial.
- Navegação estelar: reparo físico do Cockpit por 80 Sucatas.
- Comunicação: quatro Sentinelas Avariadas no Morro da Antena + triangulação com satélites.
- Dobra: estabilização de janelas de ressonância.
- Ao atingir 100% em todos os sistemas, o diagnóstico sinaliza decolagem disponível.

## 0.5.7 — Primeiros bosses da Galáxia Nárion
- Implementados Fagor (Orionis), Kael (Kael) e Ounull (Elyra), cada um com mecânica própria e Carta Rara correspondente.
- Nahr permanece reservado para expansão futura de boss.
- Rotas para arenas exibem indicador de aproximação e as arenas possuem identidade visual própria.
- Cartas agora suportam descrições longas dentro de áreas com rolagem independente.

## 0.5.8 — RY e a primeira Carta Lendária
- Nahr recebe a área **Vazio de RY**, inicialmente vazia e sem spawns, nós ou rochas.
- Os quatro mapas anteriores de Nahr indicam a localização dessa área de boss.
- A missão **Investigue Vazio de RY** surge quando a viagem interplanetária é habilitada e possui flags para Kuvaar, Trembe, Ounull e Fagor.
- Após as quatro derrotas, a missão passa a **Investigue a história do Vazio de RY** e exige comunicação com as Sombras de Nahr.
- As Sombras de Nahr são pequenas sombras escuras e flutuantes que utilizam o idioma Nahrim; o idioma exige Elmo Tier 1 e três fontes culturais investigadas no planeta.
- RY é o primeiro boss Lendário, do tipo Luz, com uma barra robusta e reações distintas a Fogo, Água, Terra, Metal, Planta e Elétrico.
- **Fulgor de RY** é a primeira Carta Lendária e inaugura o sistema de habilidade exclusiva das cartas lendárias.
- **Auxílio Iluminado** recupera 50% da Memória quando ela chega a 0, cobrando 1 ponto de Vida, enquanto a carta estiver equipada.
- A cada uso de Fulgor de RY, o jogador recebe +1 ATQ até o final do combate, de forma cumulativa.
- A derrota de RY entrega a carta, o drop do boss e Renome com as Sombras de Nahr; contatos posteriores celebram a destruição do mal do vazio.


## 0.6.1 — Hotfix
- Rota Estelar com seleção hierárquica de galáxias/planetas no padrão visual do Renome.
- Missão simples de instalação do Núcleo de Dobra após a vitória real contra RY, com confirmação no Cockpit.
