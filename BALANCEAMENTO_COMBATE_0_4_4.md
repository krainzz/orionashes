# Cinzas de Órion — Balanceamento de combate 0.4.4

## Sobrevivente inicial

| Atributo | Valor | Observação |
| --- | ---: | --- |
| HP | 36 | Reserva total inicial |
| ATQ | 12 | Ataque base do personagem |
| DEF | 5 | Defesa base |
| AMP | 1,00% | Vem do peitoral; atributo deliberadamente raro |
| Taxa Crítica | 5,00% | Chance por golpe |
| Dano Crítico | 1,50x | Multiplicador sobre o dano normal |
| Faixa básica | 3–5 | Ataque da Skill rolado por golpe |

## Fauna de Veyra

| Criatura | HP | ATQ | DEF | AMP | CRIT | DCRIT | Respawn | Carta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Escaravelho de sílica | 20 | 7–8 | 3 | 0,00% | 2% | 1,30x | 60 s | Comum |
| Lagarto das dunas | 24 | 8–10 | 5 | 0,00% | 3% | 1,35x | 120 s | Incomum |
| Sentinela avariada | 28 | 9–11 | 6 | 0,00% | 4% | 1,40x | 240 s | Incomum |

Esses valores mantêm os inimigos iniciais abaixo do perfil de crítico e AMP que será reservado para desafios futuros. A Sentinela não é uma carta Rara: raridade Rara começa com chefes de mundo/missão.

## Cartas iniciais

| Carta | Raridade | Custo | Skill | Atributos |
| --- | --- | ---: | --- | --- |
| Impacto de sílica | Comum | 2 | 4–6, Skill AMP 0,20% | +1 ATQ, +1 DEF |
| Mordida de areia | Incomum | 3 | 6–8, Skill AMP 0,35% | +2 ATQ, +0,50% CRIT |
| Faísca residual | Incomum | 3 | 5–7, Skill AMP 0,30% | +1 DEF, +1,00% CRIT |

## Variantes de carta

Toda carta fabricável usa a mesma distribuição:

- normal: 95,0%; multiplicador de atributos 1,00x;
- `+`: 4,5%; multiplicador de atributos 1,50x;
- `++`: 0,5%; multiplicador de atributos 2,00x.

As variantes não sobem a raridade da origem. Uma carta Comum `++` continua sendo Comum; ela é apenas uma cópia excepcionalmente eficiente daquela carta.

## Fórmula

`Dano = [ATQ base + (ATQ base × AMP da Skill %) + ATQ da Skill] − DEF`.

O ATQ da Skill vem da faixa X–Y da técnica. O resultado é limitado a pelo menos 1 e arredondado para inteiro antes do multiplicador crítico.

Crítico:

`Dano Crítico = Dano Normal × Dano Crítico`.

A taxa crítica efetiva do inimigo pode ser reduzida pelo modificador `enemy_crit_rate_reduction`, e seu multiplicador pode ser reduzido por `enemy_crit_damage_reduction`.

## Diretrizes futuras

AMP do personagem não deve aparecer como bônus frequente em cartas comuns/incomuns. Cartas de maior raridade podem introduzir Skill AMP superior e, somente em conteúdo tardio, efeitos capazes de aumentar o AMP do personagem. A intenção é preservar o AMP como atributo de alto valor e impedir que ele seja a fonte padrão de crescimento de dano.
