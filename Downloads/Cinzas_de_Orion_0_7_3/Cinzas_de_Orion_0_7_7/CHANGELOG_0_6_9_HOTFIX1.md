# Cinzas de Órion — 0.6.9 HOTFIX 1

## XP de Domínio no Simulador

- Corrigida a regra indevidamente aplicada na 0.6.9 que bloqueava XP de Domínio em confrontos virtuais.
- Derrotas no Simulador agora concedem o mesmo XP de Domínio da criatura correspondente.
- Regras específicas de drops únicos, como o Núcleo de Dobra de RY, permanecem inalteradas.

## Limite de dano por evento

- Um único evento de dano causado ao inimigo é limitado a **2x o HP máximo da criatura**.
- O limite usa o HP máximo, não o HP restante. Ex.: inimigo com 20 HP máximos e 2 HP restantes pode receber no máximo 40 de dano nesse último golpe.
- O dano efetivamente limitado é também o valor utilizado para o XP do NEXUS, evitando ganhos desproporcionais contra criaturas de início de jogo.
