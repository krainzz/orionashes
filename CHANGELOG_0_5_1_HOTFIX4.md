# Cinzas de Órion — 0.5.1 HOTFIX4

- Compatibilidade com saves 0.4.9 / `version: 49`, incluindo a criação retroativa do setor `comms_ridge` quando ausente.
- Save persistente em `%LOCALAPPDATA%\Cinzas de Órion\save.json`.
- Backup automático do save anterior em `bkp.json` antes de cada sobrescrita.
- Fallback automático para `bkp.json` quando o save principal estiver corrompido ou incompatível.
- Mantida a migração sem perda do progresso existente.

## HOTFIX5 — Bestiário / spawns híbridos
- Corrigido o erro `ValueError: too many values to unpack` ao abrir o Bestiário.
- O Bestiário e o catálogo de Recursos agora aceitam setores cujos `spawns` podem ser tuplas simples ou registros em dicionário com `species`/`pos`.
- A correção preserva o formato de save e não altera o conteúdo das criaturas.
