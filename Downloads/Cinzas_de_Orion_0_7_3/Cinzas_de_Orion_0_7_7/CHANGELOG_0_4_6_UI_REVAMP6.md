# Cinzas de Órion 0.4.6 — UI REVAMP 6

## NEXUS
- Progressão automática, sem pontos de habilidade.
- 20 níveis / 25.000.000 XP no nível máximo.
- Regra mantida: 1 ponto de dano causado = 1 XP.
- Quatro níveis são marcos cognitivos sem bônus direto.
- Níveis 5, 10 e 15 reservados a protocolos de hack.
- Recompensas ofensivas pequenas; nenhum bônus de defesa.
- XP excedente é limitado ao teto de 25.000.000.
- Revisão de progressão atualizada para a revisão 4, com migração de saves anteriores.

## Diário
- Corrigida a ausência do helper `_mission_status_label`, que fazia a abertura do Diário encerrar o jogo com `AttributeError`.
- Catálogo e estados de missão continuam disponíveis na interface.

## Validação
- 113 testes automatizados aprovados.
- Compilação dos módulos principais aprovada.
- Auditoria estática: `_mission_status_label` existe na classe `App` e é declarado antes de `journal`.
