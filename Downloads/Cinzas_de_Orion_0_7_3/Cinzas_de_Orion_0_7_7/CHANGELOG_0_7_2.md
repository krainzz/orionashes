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


## Ajustes visuais adicionais
- Sprites externos do protagonista são esticados para um canvas comum de 44×85 px, incluindo o frame alternativo de caminhada.
- O menu **Equipamento** e o retrato da tela de vitória usam a arte externa frontal (`assets/player/baixo.png`) quando disponível.
- O retrato usa as camadas transparentes do equipamento atual, na ordem Grevas → Peitoral → Elmo → Manopla. Elmo e Grevas só são desenhados quando equipados.
- A pose procedural de combate permanece no combate normal; o retrato de vitória é consistente com a aparência externa usada no mundo.
- Documentação de nomes, tamanhos e organização incluída em `assets/player/README.md` e `assets/player/equips/README.md`.
