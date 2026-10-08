# Cinzas de Órion 0.4.4 — balanceamento, atributos e cartas

Esta revisão permanece dentro da versão 0.4.4 e consolida o novo modelo de combate e coleção.

## Combate

- Introduzidos os atributos **ATQ, DEF e AMP**, sem separar dano físico e mágico.
- O sobrevivente começa com **12 ATQ, 5 DEF e 1% AMP**, sendo o AMP inicial atribuído ao peitoral.
- Taxa Crítica inicial: **5%**.
- Dano Crítico inicial: **1,50x**.
- Ataques usam faixas X–Y para a rolagem do Ataque da Skill.
- Fórmula implementada:
  `[ATQ base + (ATQ base × AMP da Skill %) + ATQ da Skill] - DEF do alvo`.
- Crítico é aplicado sobre o dano normal já calculado.
- Inimigos possuem ATQ, DEF, AMP, Taxa Crítica e Dano Crítico próprios.
- Fauna inicial permanece deliberadamente sem AMP e com perfil crítico baixo.

## Raridade das cartas

- **Comum:** fauna recorrente e ameaças de baixa complexidade.
- **Incomum:** ameaças locais mais relevantes e variantes especiais.
- **Rara:** chefes de mundo e de missão.
- **Mítica:** criaturas sem respawn e encontros excepcionais.
- **Lendária:** figuras importantes da história.
- **Única:** reservada às cartas futuras do slot especial.

Nenhuma criatura do mapa inicial de Veyra fornece carta Rara ou superior.

## Variantes de fabricação

Toda carta fabricável usa três cópias possíveis da mesma origem:

- normal: **95,0%**;
- `+`: **4,5%**;
- `++`: **0,5%**.

As variantes mantêm a mesma raridade da carta de origem e aumentam seus atributos concedidos. O sistema permite que cópias normais, `+` e `++` coexistam no álbum e sejam equipadas individualmente.

## Atributos concedidos pelas cartas

Toda carta possui um conjunto explícito de atributos. As cartas iniciais concedem bônus pequenos, evitando que a coleção seja puramente cosmética e preparando cartas futuras para aumentar ATQ, DEF, Taxa Crítica, Dano Crítico, dano mínimo e — muito mais raramente — AMP.

## Interface

- Botões de ação de combate usam largura padronizada para manter os quatro espaços alinhados.
- O álbum apresenta molduras por raridade.
- O estado das variantes fabricadas é mostrado dentro da própria área da carta, sem texto escapando da moldura.
- O sistema de Núcleo Relíquia permanece reservado para progressão futura.
