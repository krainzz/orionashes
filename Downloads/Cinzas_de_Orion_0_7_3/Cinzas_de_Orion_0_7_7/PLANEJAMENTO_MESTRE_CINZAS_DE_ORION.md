## 0.6.0 - CONCLUÍDA: expansão intergaláctica

- Núcleo de Dobra instalado no motor da nave para acesso a duas novas galáxias.
- Vharos e Meridion adicionadas com quatro planetas cada, fauna própria e arenas reservadas.
- Alphor e Broom implementados como bosses lendários com gates de três bosses raros por galáxia.
- Nerissa recebeu cidade multicivilizacional e calibração de idiomas desconhecidos por QTE.
- Estado novo persistido sem quebrar a migração de saves anteriores.

## 0.5.9 - Hotfixes e rebalanceamento

- Fenda das Raízes povoada com fauna local; Vazio de RY permanece vazio até sua revelação.
- Missão de RY reconhece contato prévio com as Sombras de Nahr e pula a etapa de conversa quando já cumprida.
- RY concede Núcleo de Dobra apenas na primeira vitória real.
- Cartas sem benefício permanente de DEF e com um único buff de atributo conforme a raridade.
- Taxa Crítica e Dano Crítico escritos por extenso na interface.
- AMP, dano e efeitos das Cartas atualizados conforme a revisão 0.5.9.

# CINZAS DE ÓRION — ROADMAP MESTRE

Documento de acompanhamento do desenvolvimento. **Atualizado para a versão 0.5.9.**

## Visão do jogo

RPG de exploração espacial com combate por turnos, cartas de poder, coleta, crafting, evolução da armadura, exploração de civilizações, decisões com consequências e progressão por dezenas de galáxias.

O protagonista é um herói tecnológico sobrevivente de uma invasão. Restam a ele a fonte de energia do Peitoral e a Manopla. Ao longo da campanha ele reconstruirá o Elmo e o Módulo de Locomoção, restaurará a nave e eventualmente retornará à galáxia natal.

## Estado consolidado — até 0.5.0

### Sistemas jogáveis
- Combate por turnos.
- Dano variável em faixas X–Y.
- Críticos com Taxa Crítica e Dano Crítico separados.
- Atributos ATQ, DEF, AMP, CRIT e DCRIT.
- Fórmula-base: `[ATQ base + (ATQ base × AMP efetivo da Skill) + ATQ da Skill] − DEF`.
- AMP global inicial de 1% proveniente do Peitoral.
- Cartas com 3 slots normais + 1 slot especial futuro.
- Cartas em seis raridades: Comum, Incomum, Rara, Mítica, Lendária e Única.
- Variantes de cada carta: Normal / + / ++ em 95% / 4,5% / 0,5%.
- Cartas concedem somente atributos não nulos.
- Removedor de Aprimoramento para retirar cartas dos slots.
- NEXUS como evolução cognitiva única da Manopla, alimentada por dano causado, com progressão muito longa e somente ofensiva.
- Diário, objetivos, estatísticas e achievements.
- Nave como abrigo e interior navegável.
- Cockpit, computador, painel de status e Simulador de Combate.
- Civilização Avarin de Veyra, facções, NPCs com física e idioma Avari.
- Elmo G1, análise cultural e desbloqueio do idioma.
- Missões com mais de um caminho de resolução.
- Hack integrado à Manopla.
- Renome visual no Status.
- Primeiro boss: **Kuvaar, o Sorvedouro**.
- Seleção explícita de alvo e partes do corpo/pontos fracos.
- Barra de HP inimigo sem valor numérico antes do Scan.
- Água Bruta, Purificador e Água Pura.
- Rematch virtual de bosses sob condições favoráveis mediante Carga de Simulação.

## Regras de informação

- O jogador não vê atributos técnicos dos inimigos durante o combate antes do Scan.
- O jogador vê a barra de HP do inimigo, mas não o número, antes do Scan.
- Atributos do próprio personagem ficam no Status.
- Respawns, contagem global de criaturas, coletáveis e outros detalhes de debug não ficam expostos permanentemente na HUD.
- A Manopla usa um painel digital diegético para mensagens temporárias.

## Regras de progressão

### Cartas
- **Comum:** fauna recorrente e simples.
- **Incomum:** fauna mais perigosa ou relevante.
- **Rara:** bosses de mundo/missão.
- **Mítica:** criaturas sem respawn / encontros excepcionais.
- **Lendária:** figuras importantes da história.
- **Única:** exclusivas do slot especial futuro.

Recompensas da coleção integral:
- todas as cartas normais → **ATQ +10**;
- todas as cartas + → **Dano Crítico +6%**;
- todas as cartas ++ → **AMP +5%** + futura Carta Única.

### NEXUS
- Atualização única da Manopla.
- 1 ponto de dano causado = 1 XP.
- 20 níveis nesta fase.
- 25.000.000 XP acumulados para o nível máximo.
- Ganhos pequenos e somente ofensivos.
- Nenhum nó defensivo.

### Equipamentos
- Peitoral e Manopla não seguem a mesma lógica de progressão.
- Peitoral, Elmo e Módulo de Locomoção terão Tiers tecnológicos.
- Manopla evolui pela senciência do NEXUS.
- A aparência equipada deve refletir visualmente cada peça.

## 0.4.6 — CONCLUÍDA: Kuvaar e combate tático

### Combate tático
- Seleção explícita do alvo.
- Corpo único em inimigos comuns como primeira implementação.
- Bosses podem possuir múltiplas zonas selecionáveis.
- Cartas já carregam `target_mode` para permitir multitarget real quando surgirem combates com vários alvos.

### Kuvaar
- Conceito: criatura colossal da Bacia Seca de Veyra, com Couraça de Sal.
- Rastro verdadeiro e falso em três setores.
- Rastros falsos consomem tempo, podem consumir recurso de campo e removem a proteção de graça, simulando atração de fauna.
- Três camadas de Couraça de Sal.
- Defesa da couraça cai de 30 → 24 → 17 → 7 conforme as camadas são dissolvidas.
- Água Pura expõe temporariamente a Fenda Ventral.
- Fenda Ventral: DEF 10, multiplicador de dano 1,25x.
- Vitória marca o boss como derrotado e libera o Simulador.

### A Sede de Qaresh
- Continuação natural da crise de abastecimento.
- Etapa de investigação com rastros.
- Preparação de Água Pura por três caminhos:
  - empréstimo aos Avarin;
  - produção própria;
  - desvio do reservatório.
- O desvio cria Incidente e altera Renome.

### Simulador de Combate
- Construído na nave após a primeira vitória de boss.
- Usa Carga de Simulação.
- Rematch não consome Água Pura real.
- Estado virtual começa com HP máximo, memória máxima e 5 cargas virtuais de Água Pura para Kuvaar.
- Permite repetir bosses derrotados para obter novamente seus drops e receitas.

## Próxima etapa recomendada — 0.4.7

A ordem abaixo é uma referência, não uma obrigação. As prioridades podem ser alteradas conforme a evolução do protótipo.

### Renome por facção
- Renome separado por facção/assentamento/região.
- Barra visual no Status.
- Faixas qualitativas de relação.
- Diálogos, preços, acesso e missões podem responder ao estado social.

### Notoriedade
- Uma ação pode ser conhecida ou permanecer oculta.
- Testemunhas, sensores e transmissões determinam quanto uma ação circula.
- Diferenciar estado real do mundo de aquilo que a população acredita ter acontecido.

### Incidentes persistentes
Registrar:
- ação;
- local;
- envolvidos;
- testemunhas;
- sensores/registro;
- transmissão;
- consequência aplicada.

O sistema nunca deve duplicar consequência após recarga de save.

## 0.4.8 — expansão das resoluções e Hack 1.0

- Furtividade física.
- Roubo estruturado.
- Negociação.
- Alarmes e vigilância.
- Hack com progressão própria da Manopla.
- Terminais, portas, redes, drones e instalações.
- Consequências ligadas a incidentes e notoriedade.



## 0.4.9 — consolidação antes da 0.5

- Capitalização padronizada dos nomes das cartas.
- Álbum completo acessível pelo Menu e pela Manopla, com custos de fabricação e quantidades possuídas.
- Cartas fabricadas permanecem no Álbum até equipagem manual.
- Bônus de ATQ das cartas em percentual, preservando escalabilidade durante toda a campanha.
- Ataques de cartas tipados, com matriz de vantagens de +50% e resistência de -25%.
- Golpe da Manopla permanece sem tipo.
- Efeitos de ataque temporários não acumulam e terminam com o combate.
- NEXUS: Calibração de Impacto passa a conceder +1 ATQ nos níveis 2, 3, 9 e 17.
- Nave permanece em fase de concepção para a etapa seguinte; nenhuma restauração ou alteração da Rota Estelar foi implementada nesta versão.

## 0.5.0 — navegação, Peitoral, Renome e Bestiário

### Cockpit / Rota Estelar
- Destinos selecionáveis por clique.
- Planetas ainda não descobertos aparecem como `???`.
- A descoberta nominal de um planeta depende de exploração ou revelação narrativa futura.

### Peitoral / AURORA
- Tela própria para o Peitoral.
- Quatro slots de memória exibidos como vazio, ocupado ou bloqueado.
- Bloqueios de memória vinculados ao Tier do Peitoral.
- AURORA Plus, Nova e Ultimate com bônus substitutivos, não cumulativos.
- AURORA Plus utiliza somente materiais disponíveis em Veyra.

### Renome
- Reputação separada por facção, planeta e galáxia.
- Conclusão de missões registra Renome para a facção beneficiada.
- Milestones de facção, planeta e galáxia com recompensa resgatável.

### Bestiário / Scan
- Criaturas conhecidas registram tipo e mapas de ocorrência.
- Após o Scan, o Bestiário passa a registrar dados técnicos e HP conhecidos.
- Criaturas no mapa exibem nome; após o Scan passam a exibir também um nível calculado a partir de seus atributos.

## 0.5.x — Módulo de Locomoção

- Dash.
- Extensão de memória operacional.
- Melhorias progressivas de mobilidade.
- Interação com terrenos e obstáculos.
- Visual próprio no personagem.
- Progressão independente do NEXUS e do Elmo.

## Nave e expansão galáctica

### Restauração da nave
Sistemas:
- Casco;
- Distribuição de Energia;
- Propulsão;
- Navegação;
- Comunicação;
- Dobra.

### Primeiro voo
- Cockpit operacional.
- Seleção de destino.
- Consumo de recurso de viagem.
- Viagem entre planetas da mesma galáxia.
- Estados individuais por planeta/setor.

### Expansão intergaláctica
- Motor/núcleo de dobra.
- Recurso raro de salto.
- Viagem entre galáxias.
- Retorno à galáxia natal.

## Estrutura de planetas

Não adotar fórmula fixa de “um planeta elemental por galáxia”. Cada planeta deve resultar da combinação de:
- composição;
- atmosfera;
- gravidade;
- superfície;
- clima;
- biosfera;
- fenômenos naturais;
- anomalias;
- ruínas;
- civilização;
- tecnologia;
- recursos;
- ameaças;
- importância narrativa.

Mundos extremos, como um planeta praticamente tomado por fogo, devem ser raros e memoráveis.

## Civilizações e idiomas

Cada civilização deve ter identidade própria em:
- arquitetura;
- vestuário;
- tecnologia;
- organização social;
- economia;
- relação com o ambiente;
- idioma;
- crenças e valores quando relevantes.

Base atual:
- planeta: **Veyra**;
- povo: **Avarin**;
- idioma: **Avari**;
- assentamento inicial: **Qaresh**.

## Pedras especiais — nome ainda em aberto

Termos provisórios:
- Núcleo de Éon;
- Relíquia de Singularidade;
- Fragmento de Ascensão;
- Prisma Arcaico.

Devem ser extremamente raros, ligados a missões difíceis e capazes de conceder bônus excepcionais.

## Princípios permanentes

1. Informação técnica deve ser descoberta progressivamente.
2. O poder permanente deve ser caro, demorado ou raro.
3. O início do jogo não deve permitir acúmulo rápido de atributos.
4. Cada nova mecânica deve ter função no mundo.
5. NPCs possuem física própria.
6. WASD/Setas ficam reservados para movimentação.
7. Saves devem migrar sem duplicar bônus ou consequências.
8. Materiais importantes não devem aparecer todos no primeiro planeta.
9. Planetas devem variar por combinação de características, não por elemento isolado.
10. Os números existem para sustentar o sistema, mas não devem ser todos exibidos ao jogador desde o início.
11. O visual definitivo do jogo será reformulado futuramente; a lógica deve permanecer desacoplada da apresentação atual.


### Revisão 0.4.6 — Combate e boss
- Bosses agora usam seleção explícita de alvo e podem possuir múltiplas zonas.
- Kuvaar é visualmente destacado no mapa e a entrada da Bacia Seca dispara alerta de perigo na Manopla.
- O Simulador de Combate só fica disponível como projeto de craft após a primeira vitória real contra o boss; a máquina não é desbloqueada automaticamente.
- Layout de combate reorganizado para evitar sobreposição entre LED, alvo, inimigo e ações.


## 0.4.6 — Revisão final de combate
- Seleção explícita de partes do corpo para todos os inimigos.
- Precisão do atacante e dos inimigos; chance de acerto por zona.
- Defesa e multiplicador próprios por zona.
- Interface de combate reservando espaço à seleção de alvo.
- Interação robusta com marcos de chão.


## 0.4.7 — Flora, Tipagem e Recompensas
Implementado: direções do protagonista, tipos de criatura/carta, inventário por posse, resgate manual de conquistas, gating visual de Tiers sucessores, catálogo de recursos, flora bloqueada por Scan e Slot Único da Manopla.
- Revisão seguinte da 0.4.7: perfis laterais refinados, caminhada visual, glow frontal do Peitoral, Recursos dentro de Projetos Tecnológicos, zonas vitais das criaturas e mapa sem grid.
- Revisão final: vitória com protagonista de frente, glow do Peitoral removido, Kuvaar acessível a qualquer momento e dificuldade dinâmica conforme os preparativos anteriores concluídos.


## 0.4.8 — Conflito de facções e linguagem visual de cartas

### A Dívida da Fenda
- Nova linha de missão envolvendo os **Guardiões dos Reservatórios** e os **Filhos da Fenda**.
- Líderes: **Iria** e **Tarek**.
- O jogador pode comprometer a comunicação dos Guardiões para favorecer uma emboscada ou alertar Iria antes do confronto.
- O líder derrotado concede sua Carta Mítica como consequência do desfecho.

### Cartas de líderes
- **Sentença Litônica** — Terra — Mítica — Iria.
- **Ruptura da Fenda** — Terra — Mítica — Tarek.
- Ambas são ofensivas e não concedem DEF.
- A carta do líder vencedor pode ser fabricada depois do desfecho e exige **Núcleo de Kuvaar**.

### Efeitos visuais
- Cartas passam a disparar projéteis/effects procedurais pela Manopla.
- Cada carta utiliza uma linguagem visual coerente com sua habilidade: poeira, eletricidade, cristal, ondas, sal, ruptura e impacto lítico.

### 0.5.0 HOTFIX 3 — Cockpit
- Galáxia inicial definida como **Galáxia Nárion**.
- Padrão futuro: média de 4–5 planetas visitáveis por galáxia, com exceções planejadas para sistemas focados em luas.
- Cockpit apresenta nome da galáxia e informações compactas do destino selecionado.
- Nomes desconhecidos permanecem `???` até descoberta; civilizações conhecidas por planeta são estado dinâmico persistente.


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


## 0.5.2 — Exploração interestelar inicial

- Após os seis sistemas da nave chegarem a 100%, a nave pode viajar entre os cinco mundos catalogados da Galáxia Nárion.
- Missão principal **Explore a Galáxia**, mantida aberta até que novas galáxias existam; nesse momento o título passa a **Explore o Universo**.
- Cada viagem é antecedida por uma cena de navegação espacial.
- Veyra permanece como ponto de retorno e cada planeta novo possui um ponto fixo de pouso.
- Orionis, Kael, Nahr e Elyra possuem quatro mapas cada, fauna própria, recursos e flora diferenciada.
- Plantas continuam bloqueadas até Scan e recursos minerais permanecem dependentes das tecnologias futuras.
- Novas cartas e criaturas seguem os tipos já existentes e uma progressão gradual de atributos.
- O Elmo G1 é equipado automaticamente no craft. Três designs de Elmo já possuem identidade visual e suporte de sprite nas quatro direções, ficando os dois designs futuros bloqueados.
- A aparência do detalhe energético do Peitoral acompanha os quatro níveis do AURORA: ciano, vermelho, amarelo e azul.
- Para telas de pular/continuar/aceitar, o padrão de entrada é Espaço.


## 0.5.3 — Mana das criaturas, raridades e escala de conteúdo

- Todas as criaturas atuais usam dois ataques: ataque básico já existente e a técnica da carta correspondente.
- Reserva de Mana própria por criatura; ocultada normalmente e revelada pelo Scan do Elmo.
- Frequência de técnica especial: 20% Comum, 40% Incomum e 60% Boss/Rara.
- Raridades atuais: maioria Comum, minoria Incomum, Rara somente para boss, Mítica para missões/combates difíceis, Lendária para super bosses em momentos críticos e Única apenas pelo sistema futuro de craft.
- Efeitos táticos passam a complementar certas cartas: Atordoamento em Elétrico, redução de ATQ em Metal, Afogamento em Água e DoT em Fogo. Terra mantém identidade defensiva; Planta, Luz e Trevas ainda aguardam definições específicas.
- Inventário e Renome preparados para listas extensas com rolagem e sem crescimento vertical desnecessário.
- Uma arena de boss fica reservada em cada planeta atual; mecânicas e bosses serão definidos posteriormente.
- Compatibilidade de save passa a preservar conteúdo desconhecido de versões futuras em setores, criaturas, cartas, planetas e estatísticas.

## 0.5.7 — CONCLUÍDA: Primeira expansão de bosses da Galáxia Nárion

### Orionis — Fagor
- Arena: Caverna Ígnea de Fagor, com terreno vulcânico e escala visual ampliada.
- Boss de Fogo com corpo de pedra, duas pernas e Núcleo de Magma.
- Pernas possuem HP próprio e não transferem dano diretamente ao HP principal.
- Núcleo de Magma só fica disponível depois que ambas as pernas chegam a 0 HP.
- Núcleo possui vulnerabilidade elevada (multiplicador de dano 1,80×).
- Carta Rara de Fogo com dano alto e sem efeito condicional adicional.

### Kael
- Arena: Clareira de Kael, com mata densa.
- Boss de Planta com Copa e Tronco como alvos independentes.
- A vida da Copa modula o ATQ de Kael; com Copa destruída, ATQ chega a 1.
- Carta Rara de Planta usa 10% do HP atual do jogador como dano adicional e como valor de redução do próximo ataque inimigo.

### Elyra — Ounull
- Arena: Ilhota de Ounull, cercada por água.
- A entrada na área é livre pela faixa de terra; o Módulo de Locomoção é necessário apenas para atravessar a água até a ilha central.
- Boss de Água possui técnica especial Maré de Ounull, que causa Afogamento.
- Ataques do jogador que consomem Memória restauram HP do boss; enquanto o jogador estiver sob Afogamento, a recuperação é duplicada.
- Carta Rara de Água recupera 1% do dano causado em Vida.

### Rotas e informação
- Todos os mapas anteriores às arenas dos bosses atuais possuem indicador de aproximação da área do boss.
- Arenas e portões usam o padrão visual discreto de Zona de Boss já consolidado.
- Nahr permanece sem boss nesta etapa.

### Cartas — interface
- Caixas de efeito do álbum e da fabricação usam rolagem independente para textos longos.
- O texto completo permanece legível sem atravessar o layout.

## 0.5.8 — CONCLUÍDA: RY, civilização de Nahr e primeira Carta Lendária

### Nahr e a investigação de RY
- Nahr passa a possuir cinco áreas, com o **Vazio de RY** reservado como área de boss.
- O Vazio de RY começa totalmente vazio: sem criaturas, nós ou rochas; somente o local central permanece preparado para a futura manifestação do boss.
- Os quatro mapas anteriores de Nahr exibem indicadores de rota apontando para a área de RY.
- Com a viagem interplanetária operacional, surge a missão **Investigue Vazio de RY**.
- A missão mantém quatro flags persistentes: derrotar Kuvaar, Trembe, Ounull e Fagor.
- Após a quarta derrota, o título passa a **Investigue a história do Vazio de RY**.

### Civilização das Sombras de Nahr
- Criada a civilização **Sombras de Nahr**, diferente da sociedade Avarin de Veyra.
- Seus habitantes são pequenas sombras escuras e flutuantes, organizadas no assentamento Refúgio da Penumbra.
- Idioma: **Nahrim**.
- O aprendizado do idioma segue a mesma métrica de Veyra: Elmo Tier 1 equipado + investigação de três fontes culturais espalhadas por Nahr.
- Depois de compreender o idioma e conversar com o povo, o jogador descobre que RY é tratado como a personificação da morte e como um bicho-papão que executa quem desejar.

### RY — primeiro boss Lendário
- RY é o primeiro boss **Lendário**, do tipo **Luz**.
- Forma visual: esfera de luz disforme e translúcida.
- Possui uma única barra de HP robusta.
- Ataque básico e ataque especial vinculado à sua própria carta técnica.
- Reações elementais: Fogo causa Queimadura; Água causa Afogamento; Terra concede escudo; Metal prepara um crítico; Planta recupera HP; Elétrico concede +50% de ATQ ao próximo ataque.
- O boss só pode surgir e ser enfrentado depois que a investigação da história for concluída com o povo de Nahr.

### Fulgor de RY — primeira Carta Lendária
- **Fulgor de RY** inaugura a raridade Lendária e é uma carta do tipo **Luz**.
- Ataque: 30-40 de Ataque da Skill.
- Cada uso concede **+1 ATQ** até o final do combate, com acúmulo entre usos.
- Primeira habilidade exclusiva de Carta Lendária: **Auxílio Iluminado - Se a Memória chegar a 0 enquanto esta carta estiver equipada na Manopla, você perde 1 ponto de Vida e recupera 50% do total da sua Memória.**
- A descrição da habilidade aparece no efeito da carta seguindo o padrão reservado às futuras Cartas Lendárias.
- A derrota de RY entrega seu drop, a carta lendária e 100 de Renome com as Sombras de Nahr.
- Após a derrota, os habitantes de Nahr passam a celebrar a destruição do mal que habitava o vazio e afirmam que seu povo poderá seguir a vida em paz.

### Compatibilidade e documentação
- Save atualizado para schema 59, preservando os IDs internos existentes e os novos estados de Nahr/Ry.
- Codex de Inimigos e Codex de Cartas foram regenerados para a 0.5.8.


## 0.6.1 — Hotfix
- Rota Estelar com seleção hierárquica de galáxias/planetas no padrão visual do Renome.
- Missão simples de instalação do Núcleo de Dobra após a vitória real contra RY, com confirmação no Cockpit.
