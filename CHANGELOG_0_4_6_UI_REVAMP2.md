# Cinzas de Órion 0.4.6 — Revisão de UI / Navegação

## Menu e cabeçalhos
- Cabeçalhos de todas as telas passaram a usar apenas um nome principal, coerente com o botão de acesso.
- Removido o botão `NAVE` do Menu principal; a entrada na nave continua sendo uma interação feita no mapa, perto da nave.
- Removidos atalhos cruzados entre telas de painel para impedir que hotkeys criem históricos de navegação confusos.
- ESC agora retorna pela origem da tela aberta, sem saltar para telas intermediárias criadas por atalhos de outro painel.

## Diário
- Refeito como catálogo de missões.
- Missões em andamento e concluídas aparecem em grupos separados.
- Cada missão pode ser selecionada para expandir seus detalhes.
- Status exibido como `NOME - EM ANDAMENTO` ou `NOME - CONCLUÍDA`.
- Criada área de detalhes com rolagem em estilo de interface de jogo, sem widgets nativos do Windows.

## Status
- Textos reorganizados em dois painéis independentes com áreas roláveis.
- Barra de rolagem estilizada integrada ao visual sci-fi do jogo.
- Instrução de rolagem aparece na própria tela.

## Álbum
- Removida a área incorreta de seis slots/referência às pedras.
- Removido `REMOVER CARTA` do Álbum; a remoção fica exclusivamente na configuração da Manopla.
- Raridade passou a ser exibida como selo compacto, evitando atravessar a área de navegação.

## Manopla
- A tela específica mantém três slots normais e um quarto slot especial reservado a cartas ÚNICAS.
- `REMOVER CARTA` foi colocado na configuração da Manopla, usando o Removedor de Aprimoramento disponível.
