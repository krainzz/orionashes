# Cinzas de Órion — 0.4.6 Visual Pixel v2 — Correção de transição de mapa

## Correção
- Corrigida a renderização de landmarks durante a entrada em setores diferentes.
- Landmarks agora são mantidos como dicionários completos durante a ordenação/renderização, preservando `pos` e metadados como `mission_site`, `hack_site` e `boss_route_marker`.
- O renderer não tenta mais expandir dicionários como argumentos de `project(x, y)`.
- O tratamento de `landmark` e `boss_actor` foi separado do caminho genérico de entidades.

## Validação
- AST de `main.py`: OK.
- Posições de pedras, coletáveis, landmarks, spawns e nave em todos os setores: válidas como coordenadas de 2 dimensões.
- Projeto empacotado sem arquivos temporários de Python.
