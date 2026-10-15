# Cinzas de Órion — 0.7.3

Release visual focado exclusivamente no HUD de combate. A lógica de turnos, atributos, dano, memória, cartas, saves e progressão permanece intacta.

### 0.7.3 — HUD futurista de combate

- Botões neon ciano com brilho, indicadores de mira e pulso visual em hover/seleção.
- Molduras técnicas, grades discretas e telemetria decorativa atrás da interface.
- `TARGET_LOCK` reflete a chance de acerto real do ponto corporal selecionado.
- FBO ModernGL separado aplica curvatura de lente/Bloom apenas à camada de interface, sem deformar aliados ou inimigos.
- Fallback Pygame se ModernGL ou o contexto OpenGL não estiver disponível.
- Preservados os desenhos, efeitos, raridades e tooltips das cartas e a disposição dos combatentes.



### 0.6.9 HOTFIX 1

- XP de Domínio também é concedido em confrontos do Simulador.
- Dano causado ao inimigo é limitado a 2x o HP máximo por evento, e o valor limitado é o usado para XP do NEXUS.

- Simulador também concede XP de Domínio; drops especiais continuam seguindo suas regras próprias.



### 0.7.2

- Badges elementais pixel-art oficiais aplicadas ao Domínio e às cartas, sem rótulos textuais.

- Projeto de **Emissor Laser** desbloqueado com Avari conhecido + primeiro nível de Renome dos Recuperadores de Qaresh.
- Instalação do Emissor Laser pelo Computador da Nave, usando Sucata, Placa, Liga meteórica e Matriz fotônica.
- Novo encontro aleatório de asteroides em viagens entre galáxias, disponível somente após a instalação do laser.
- Asteroides destruídos concedem Essência; colisões geram Dano de Viagem persistente, separado dos seis sistemas originais da nave.
- Dano de Viagem bloqueia novas viagens até a missão de reparo ser concluída com Sucata proporcional ao dano.
- Diagnóstico da Nave recebe o reparo em interface compacta, mantendo o layout existente.
- Save 0.7.0 continua compatível e ganha migração automática para o schema 72.
- Testes focados da 0.7.2 em `test_071_features.py`.

### 0.7.1 HOTFIX 1

- Visualizações oficiais das quatro peças principais referenciadas em `assets/equips/`: `Manopla.png`, `Elmo.png`, `Peitoral.png` e `Grevas.png`.
- Os arquivos de arte não acompanham o pacote e devem ser adicionados manualmente. Na ausência de algum arquivo, a visualização procedural anterior é usada como fallback.

### 0.7.0 HOTFIX 1

Ajustes de seleção/equipamento da Manopla e conversão dos bônus de ATQ das Cartas Únicas para percentuais.


### Sprites externos do protagonista

- Os PNGs-base direcionais ficam em `assets/player/` e são esticados para 44×85 px.
- Equipamentos visuais opcionais usam camadas transparentes por peça/direção em `assets/player/equips/<peça>/`.
- O menu Equipamento e o retrato de vitória usam a mesma composição frontal dinâmica. As instruções detalhadas de nomes estão nos arquivos `assets/player/README.md` e `assets/player/equips/README.md`.


### Sistema de Efeitos de Combate (ModernGL)

A camada visual de combate usa shaders GLSL para luzes dinâmicas, partículas instanciadas e ondas de choque de críticos/supremas. Consulte `COMBAT_FX_MODERNGL.md` para presets, variáveis configuráveis e estrutura dos shaders. A camada é renderização-only e retorna ao Pygame se o contexto GPU não estiver disponível.
