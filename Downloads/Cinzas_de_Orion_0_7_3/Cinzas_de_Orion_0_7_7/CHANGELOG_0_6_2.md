# Cinzas de Órion — Versão 0.6.2

## Revisão de cartas e criaturas

- Revisadas as 16 criaturas comuns/incomuns adicionadas na 0.6.0 e suas respectivas cartas.
- Mantido o contrato de dois ataques por criatura: ataque básico + técnica da própria carta.
- Efeitos foram mantidos dentro das dinâmicas elementais existentes: Metal reduz ATQ, Elétrico pode Atordoar, Fogo pode causar Queimadura, Água aplica Afogamento, Planta prepara dano do próximo ataque do tipo e os demais efeitos seguem funções de combate já presentes.
- Nenhuma carta nova concede DEF como atributo permanente.
- Os bônus permanentes continuam respeitando o teto de uma única bonificação por raridade.
- Faixa de dano/AMP das cartas novas foi mantida compatível com os intervalos das cartas anteriores da mesma raridade.

## Desbloqueio de cartas

- Cartas de criatura com receita só ficam disponíveis para Fabricação depois da primeira derrota da respectiva espécie.
- A primeira derrota adiciona a criatura ao Bestiário e registra a carta conhecida.
- Cartas de missão continuam condicionadas à conclusão da missão.
- Cartas de boss só aparecem na Fabricação após a respectiva derrota real; a vitória não entrega uma cópia automática.

## Hotfixes

### HOTFIX — desbloqueio e alertas de cartas

- Cartas de boss agora possuem receita de Fabricação e só ficam disponíveis após a respectiva derrota real.
- A vitória contra um boss não fabrica mais uma cópia automática da carta.
- O desbloqueio de qualquer carta elegível exibe o popup **NOVA CARTA DESBLOQUEADA PARA CRIAÇÃO!** com prévia ilustrada da carta.
- Corrigida a identificação de bosses cuja carta possui ID diferente do boss, como `alphor_fireball` e `broom_lightning`.
- Corrigido o `AttributeError` do menu ESC por meio de `App.has_unclaimed_achievements()`.

- Corrigido `NameError: CHEST_MEMORY_SLOTS` na Oficina da Nave.
- Contato com facções de Veyra bloqueado até Elmo Tier 1 + idioma Avari.
- A investigação do Vazio de RY aguarda a primeira viagem real para fora de Veyra.
- Alertas visuais unificados para aquisição, atualização e conclusão de missões, sem duplicar alertas equivalentes.
- Requisitos de AURORA padronizados com azul-claro para quantidades disponíveis e vermelho para faltantes.
- O catálogo do Mapa mostra apenas setores visitados.
- Conquistas com recompensa pendente recebem somente um marcador visual discreto no botão.
- Bestiário revamp com lista rolável de criaturas derrotadas, imagem ampliada e caixa de dados rolável.
- A ficha do Bestiário não expõe mapas não visitados.

## Compatibilidade

- Save permanece em formato `version = 62`.
- Saves anteriores continuam passando pela rotina de migração existente.
