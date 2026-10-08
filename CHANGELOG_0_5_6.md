# Cinzas de Órion — 0.5.6

## Hotfixes
- Implementado o Escudo Stasis vinculado ao Elmo Tier 2 para ataques fatais: ataques marcados como fatais podem abrir um QTE de tecla + sincronização temporal; a janela padrão é de 10 segundos e cai para 5 segundos em ameaças de alto nível.
- Sem Elmo Tier 2 equipado, um ataque fatal encerra imediatamente o combate.
- A morte passa a obedecer ao Tanque de Renascimento: sem o Tanque, a campanha termina em Game Over; com o Tanque, o personagem retorna ao interior da nave e perde 10% das Essências mantidas no inventário.
- O Armazenador de Essências protege Essências já depositadas da penalidade de morte.
- A missão de reconstrução do Tanque é adquirida na abertura de uma campanha nova e recebe alerta visual.
- Missões que entram efetivamente em andamento emitem alerta de aquisição sem gerar alertas duplicados ao apenas reabrir uma atividade.
- A missão de reparo da propulsão da nave preserva o cursor da sequência e pode ser reaberta pelo Diagnóstico da Nave para continuar de onde parou.
- A interface do Tanque de Renascimento e do Armazenador foi integrada fisicamente ao interior da nave.

## Introdução e persistência
- Uma campanha nova começa dentro da nave com uma breve conversa do protagonista sobre a fuga e a necessidade de reconstruir o Tanque de Renascimento.
- O diálogo de abertura não reaparece ao carregar um save existente.
- Saves anteriores são migrados para o novo formato sem reabrir a introdução.


## Hotfix 1 — Interface da nave
- Reparos em andamento ficam explicitamente identificados no Status da Nave.
- O acesso ao Tanque de Renascimento abre um popup de insuficiência ou confirmação antes da instalação.
- O Armazenador de Essências abre um popup com saldo protegido e botão de depósito desabilitado quando o inventário está zerado.
- A sombra elíptica da nave foi removida somente na cena de viagem entre planetas, preservando as demais cenas.

## Hotfix 2 — Essência e desbloqueio de viagem
- Ao concluir todos os sistemas necessários para o voo interplanetário, a Manopla agora exibe um alerta específico informando que a viagem para outros planetas está autorizada.
- A listagem de fabricação de cartas passou a usar a mesma identidade visual de raridade do menu Cartas: Comum neutra, Incomum verde, Rara azul, Mítica roxa e Lendária amarela.
- Todo craft com requisito de Essência consulta o saldo consolidado do inventário + Armazenador e consome primeiro o inventário, usando o armazenamento apenas para completar o custo quando necessário.
