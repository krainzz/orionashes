# Cinzas de Órion 0.4.4 — revisão de interface de combate e cartas

Esta revisão mantém o save 0.4.4 e ajusta apenas apresentação e descoberta de informação.

## Combate

- ATQ, DEF, AMP, Taxa Crítica e Dano Crítico do sobrevivente não são exibidos durante a batalha.
- Esses atributos continuam disponíveis em **STATUS / SISTEMAS** e são usados normalmente no cálculo interno.
- O inimigo não exibe HP numérico, barra de HP ou atributos antes do sistema futuro de **SCAN**.
- Durante a batalha o alvo mostra apenas sua identificação e que a leitura biométrica/scan ainda não está disponível.
- Removidas da tela de combate as linhas de depuração com rolagem, defesa, fórmula e valores técnicos.
- HP e memória do sobrevivente permanecem visíveis para o jogador controlar seu estado atual.

## Álbum

- As cartas exibem somente atributos que realmente concedem bônus.
- Atributos zerados não aparecem.
- A leitura de custos e faixa da técnica foi mantida por serem informações próprias da carta.
- O botão de fabricação continua na **Oficina / Craft**, onde a receita e os materiais são apresentados; ele fica desabilitado quando os materiais ou pré-requisitos não estão disponíveis.
- As variantes normal, + e ++ continuam sendo cópias da mesma carta e preservam sua raridade de origem.

## Compatibilidade

- Nenhuma alteração de formato de save.
- O arquivo continua usando `save_v044.json`.
