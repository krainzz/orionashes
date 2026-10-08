# Balanceamento de Combate — 0.4.5

## Sobrevivente inicial

- ATQ: 12
- DEF: 5
- AMP: 1%
- Taxa Crítica: 5%
- Dano Crítico: 1,50x
- Dano básico: 3–5 antes de ATQ/DEF
- AMP efetivo da skill = AMP do personagem + AMP específico da carta

## Fauna de Veyra — revisão de resistência

| Espécie | HP | ATQ | DEF | AMP | CRIT | DCRIT |
|---|---:|---:|---:|---:|---:|---:|
| Escaravelho de sílica | 90 | 4–5 | 4 | 0% | 2% | 1,30x |
| Lagarto das dunas | 108 | 5–6 | 5 | 0% | 3% | 1,35x |
| Sentinela avariada | 120 | 5–7 | 6 | 0% | 4% | 1,40x |
| Cão de sílica | 118 | 5–7 | 6 | 0% | 3% | 1,35x |
| Escavador vítreo | 145 | 6–8 | 8 | 0% | 4% | 1,40x |
| Guardião Avarin | 155 | 6–8 | 7 | 0% | 4% | 1,40x |
| Manta de poeira | 155 | 6–8 | 8 | 0% | 4% | 1,40x |
| Predador prismático | 185 | 7–9 | 9 | 0% | 4% | 1,40x |

A resistência foi aumentada principalmente via HP, enquanto o dano recebido pelo protagonista foi reduzido. O objetivo é dar aos combates mais duração sem transformar a fauna inicial em uma fonte de mortes inevitáveis. A defesa do protagonista permanece baixa e continua sendo um recurso estratégico futuro de cartas defensivas.

## Fórmula

`[ATQ base + (ATQ base × AMP da Skill %) + ATQ da Skill] - DEF do oponente`

O resultado é limitado a pelo menos 1 de dano. O crítico aplica o multiplicador de Dano Crítico sobre o dano já calculado.

## NEXUS — revisão de progressão

- 20 níveis.
- XP acumulado por dano causado, 1 ponto de dano = 1 XP.
- Próximo nível final: 165.000 XP acumulados.
- Cada nível concede 1 ponto NEXUS; os nós de evolução são deliberadamente pequenos.
- Nenhum nó concede DEF.
- Árvore atual: +ATQ, +Taxa Crítica, +Dano Mínimo, +Dano Crítico e +AMP em incrementos mínimos.

## Diretriz de progressão

AMP global deve continuar sendo um atributo muito raro. As Skills iniciais usam AMP muito baixo; cartas futuras Míticas, Lendárias e Únicas serão o principal espaço para Skills mais complexas e fortes.
