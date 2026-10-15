# Cinzas de Órion — 0.6.9

## Domínio

- Inclusão do sistema **Domínio**, individual para Água, Elétrico, Fogo, Luz, Metal, Planta, Terra e Trevas.
- Cada elemento possui progressão independente de **0 a 40**.
- O nível 1 exige 2.000 XP; os requisitos seguintes usam progressão exponencial de 30%, chegando a 55.567.484 XP no nível 40.
- XP por vitória:
  - Comum: 20 XP
  - Incomum: 40 XP
  - Rara: 100 XP
  - Mítica: 200 XP
  - Lendária: 500 XP
- Confrontos no Simulador também concedem XP de Domínio normalmente.
- O XP é aplicado ao Domínio correspondente ao elemento da criatura.

## Bônus

- Os 40 níveis seguem a tabela definida para a 0.6.9, repetindo o ciclo de 10 níveis quatro vezes.
- Bônus ofensivos de Domínio só entram no cálculo quando o jogador usa uma **técnica de carta do mesmo elemento**.
- Bônus defensivos só entram quando o jogador recebe um ataque do elemento correspondente.
- `Defesa +3%` é tratado como aumento percentual da Defesa, e `Dano Recebido -1%` reduz o dano final recebido daquele elemento.
- AMP +1% representa +1 ponto percentual de AMP.

## Interface

- Nova tela **DOMÍNIO**, acessível diretamente pela Manopla.
- Seleção de elementos à direita em ordem alfabética.
- Painel de progressão maior à esquerda, com símbolo elemental, nível, XP, barra de progresso e lista rolável dos 40 bônus.
- A seleção de elemento não altera nem mistura os Domínios dos outros elementos.

## Save

- Schema persistente atualizado para **65**.
- Saves anteriores recebem os oito Domínios com 0 XP / nível 0, preservando todo o restante do progresso.
