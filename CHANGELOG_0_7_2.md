# Cinzas de Órion — CHANGELOG 0.7.2

## Artes e apresentação
- Integração definitiva dos quatro assets oficiais de equipamento em `assets/equips/`: `Elmo.png`, `Peitoral.png`, `Grevas.png` e `Manopla.png`.
- Os arquivos foram incorporados à distribuição e continuam sendo utilizados como arte principal dos menus de equipamento.
- Piso da cena de combate refeito com geometria horizontal e simétrica para eliminar a sensação de chão torto/inclinado no início da batalha.

## Sprites do protagonista
- Adicionado carregamento opcional de sprites-base externos nas quatro direções de movimento:
  - `assets/player/baixo.png`
  - `assets/player/cima.png`
  - `assets/player/esquerda.png`
  - `assets/player/direita.png`
- Segundo frame opcional por direção com `_1.png` (`baixo_1.png`, etc.). Sem ele, o frame principal é reutilizado.
- O carregamento é sob demanda, permitindo substituir/adicionar os PNGs sem alterar o código.
- O sprite de combate continua independente da arte direcional do mundo.

## Compatibilidade
- Save schema atualizado de 71 para 72.
- Nenhum estado de gameplay novo foi exigido para a atualização visual.
