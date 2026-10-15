# Cinzas de Órion — 0.4.1

## Ecos do deserto

A 0.4.1 é uma atualização de fundação da campanha. Ela não adiciona ainda NPCs, diálogos, hack, renome, elmo, módulo de locomoção ou viagens espaciais. O objetivo é preparar o estado persistente que sustentará essas features nas próximas versões.

### Incluído

- **Correção de manutenção (0.4.1 corrigida):** fontes de 12 e 13 pontos adicionadas à tabela da interface, eliminando o `KeyError` ao abrir o Diário.
- **Menu principal de navegação:** a barra inferior de atalhos da exploração foi removida; as telas de sistema agora ficam concentradas em um Menu acessível por `ESC` ou pelo botão `MENU`.
- Os atalhos de teclado continuam disponíveis para acesso rápido.

- Diário acessível pela tecla **J**.
- Objetivos persistentes com estados **ativo**, **concluído** e **bloqueado**.
- Objetivos autônomos: estabelecer um ponto seguro, reconhecer o planeta, investigar os vestígios e catalogar fragmentos.
- Registro de descobertas narrativas ligado a eventos já existentes.
- Progresso de exploração baseado nos setores efetivamente visitados.
- Progresso dos fragmentos históricos integrado ao diário sem remover a mecânica existente.
- Migração automática de `save_v04.json` para `save_v041.json`.
- Migração continua compatível com `save_v03.json` e `save_v02.json`.
- O save antigo não é sobrescrito durante a migração.
- 4 novos testes de regressão; suíte total: 28 testes.
- Compilação de `main.py`, `core.py`, `world.py`, `content.py` e `test_core.py` validada.

### Decisões preservadas

O jogo continua começando apenas com **manopla + peitoral**. O elmo e o **Módulo de Locomoção** permanecem como conquistas posteriores. A linguagem continua inacessível nesta versão; os registros podem ser coletados e catalogados, mas a tradução continua dependendo do elmo.

### Próxima fundação

A próxima camada prevista é **sociedade e persistência**: assentamentos, NPCs, estados de missão e incidentes. Isso permitirá que roubo, hack, combate contra civis e renome tenham consequências persistentes em vez de serem sistemas isolados.

## Correção pós-lançamento — Menu (28/09/2026)
- Corrigido o fluxo `ESC` entre telas secundárias e o Menu: ao fechar o Menu, a campanha retorna diretamente ao mundo.
- O botão `CONTINUAR EXPLORAÇÃO` também retorna diretamente ao mundo quando o Menu foi aberto a partir de Diário, Inventário, Rotas, Álbum, Equipamento ou Craft.
- Mantidos os atalhos de teclado existentes.
