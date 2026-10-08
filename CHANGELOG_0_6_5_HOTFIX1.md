# Cinzas de Órion — v0.6.5 HOTFIX 1

## Oficina / Fabricação de Cartas
- Corrigido o fluxo de fabricação das cartas para usar a mesma regra de disponibilidade exibida pela Oficina.
- Essência agora é validada e consumida pelo total combinado entre inventário e Armazenador da nave, evitando divergência entre botão habilitado e ação recusada.
- O botão FABRICAR da tela de Cartas passa a encaminhar explicitamente o resultado para o fluxo de recompensa.
- Após uma fabricação bem-sucedida, a nova instância N / + / ++ é identificada e exibida imediatamente em um popup.
- O popup mostra a carta criada, raridade, tipo, variante, custo de Memória, dano, bônus e descrição.
- A carta continua sendo adicionada normalmente à Pool de cartas.
- Nenhuma regra de desbloqueio foi alterada: a receita só aparece após a descoberta da carta, com as exceções de aquisição já estabelecidas para cartas de missão.

## Regressão
- Adicionados testes cobrindo fabricação de carta, consumo de Essência armazenada e existência do popup de recompensa.
