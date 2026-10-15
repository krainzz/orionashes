# Cinzas de Órion 0.6.5 — HOTFIX 2

## Oficina de Cartas
- Corrigido o fluxo de clique dos botões de fabricação para usar um handler dedicado da UI.
- Fabricação continua restrita à nave e agora informa visualmente quando o jogador está fora dela.
- Validação visual e de estado usam as mesmas condições: nave, materiais e desbloqueio da receita.
- O craft bem-sucedido continua consumindo os materiais e adicionando a nova instância à Pool.

## Cartas Únicas
- Revisado o fluxo de seleção da carta-fonte e fabricação da Carta Única.
- O craft só executa com carta sobressalente válida, Essências suficientes e jogador na nave.
- O popup da Carta Única agora exibe a própria carta fabricada, com símbolo elemental em destaque, variante e efeitos.

## Feedback
- Tentativas inválidas não ficam silenciosas: um aviso temporário da Oficina é exibido na interface.
