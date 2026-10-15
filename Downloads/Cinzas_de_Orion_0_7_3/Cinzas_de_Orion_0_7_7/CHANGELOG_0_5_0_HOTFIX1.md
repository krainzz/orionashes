# CINZAS DE ÓRION — 0.5.0 HOTFIX 1

## Correção de inicialização
- Corrigida uma `f-string` em `core.py` que usava aspas simples aninhadas na mesma expressão.
- A construção agora é compatível com versões do Python anteriores a 3.12, evitando `SyntaxError: f-string: unmatched '['` na inicialização do jogo.
- Nenhuma regra de gameplay, interface ou conteúdo da 0.5.0 foi alterada neste hotfix.
