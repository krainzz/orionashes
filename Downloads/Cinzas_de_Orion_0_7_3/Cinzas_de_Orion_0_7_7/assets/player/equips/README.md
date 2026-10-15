# Camadas de equipamento do protagonista

Para que as peças apareçam sobre o personagem, coloque PNGs transparentes alinhados ao mesmo canvas do sprite-base (44 × 85 px) nestas pastas:

- `peitoral/baixo.png`, `cima.png`, `esquerda.png`, `direita.png`
- `manopla/baixo.png`, `cima.png`, `esquerda.png`, `direita.png`
- `elmo/baixo.png`, `cima.png`, `esquerda.png`, `direita.png`
- `grevas/baixo.png`, `cima.png`, `esquerda.png`, `direita.png`

Opcionalmente, cada direção pode ter o segundo frame da caminhada com sufixo `_1.png` (por exemplo `peitoral/baixo_1.png`). Sem ele, a camada do frame normal é reutilizada.

O jogo compõe as camadas nesta ordem: grevas, peitoral, elmo e manopla. A Manopla e o Peitoral fazem parte da aparência inicial; Elmo e Grevas só são aplicados quando estão equipados. Uma camada ausente é ignorada; o jogo continua funcionando.
