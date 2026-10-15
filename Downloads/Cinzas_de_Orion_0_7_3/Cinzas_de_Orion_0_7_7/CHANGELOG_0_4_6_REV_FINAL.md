# Cinzas de Órion 0.4.6 — Revisão Final de Combate

- Interação com pontos de interesse no chão prioriza o marco mais próximo e não exige encostá-lo em uma parede.
- Todos os inimigos possuem zonas corporais com defesa, evasão e multiplicador próprios.
- Precisão do protagonista adicionada ao Status; cartas podem concedê-la no futuro.
- Precisão dos inimigos adicionada aos dados internos e usada no acerto dos ataques inimigos.
- A seleção de alvo mostra parte do corpo e chance de acerto.
- O dano normal usa a defesa e o multiplicador específicos da zona selecionada.
- A barra de HP inimiga permanece visível sem valor numérico.
- O espaço de seleção de alvo não exibe mais o texto redundante de “alvo atual”.
- NEXUS possui dois nós ofensivos de Precisão (+1 nos níveis 5 e 13), mantendo ganhos pequenos.


## Revisão final — interação e layout de combate

- Pontos de interesse no chão passam a usar uma lista de hotspots ordenada por distância/prioridade, tornando estações, terminais, válvulas e outros marcos diretamente interagíveis ao ocupar ou encostar no ponto.
- O painel de combate foi separado em duas áreas: seleção de ponto de impacto e integridade do inimigo.
- Removido o subtítulo redundante de “selecionado” dos botões de alvo.
- Toda a fauna e personagens combativos mantêm zonas corporais com Precisão/Evasão, Defesa e multiplicador de dano próprios.
- Precisão do sobrevivente e dos inimigos continua sendo usada no cálculo de acerto; a chance permanece visível apenas como parte do botão de seleção.


### Revisão de dano por zona (0.4.6)
Precisão/Evasão determina somente a chance de acerto. Depois do acerto, a zona corporal altera apenas a Defesa local. Não existe multiplicador de dano escondido por zona; o dano segue exclusivamente a fórmula central.
