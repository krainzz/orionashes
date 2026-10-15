# Cinzas de Órion — 0.5.3

## HOTFIX / COMBATE

- Todas as criaturas atuais possuem dois ataques: o ataque básico existente e a técnica especial vinculada à carta da própria criatura.
- Cada criatura inicia o combate com uma reserva de Mana própria. A Mana é consumida apenas quando a técnica especial é usada.
- Reservas atuais: Comuns 8 Mana / custo 2 (até 4 técnicas), Incomuns 9 / custo 3 (até 3 técnicas) e Bosses/Raras 20 / custo 4 (até 5 técnicas).
- Frequência da técnica: 20% para Comuns, 40% para Incomuns e 60% para Bosses/Raras, limitada pela Mana disponível.
- A Mana não aparece naturalmente na HUD. O dado é revelado pelo Scan do Elmo e pode então ser exibido durante o combate e no Bestiário.
- Corrigida a transição de vitória após efeitos persistentes derrotarem um inimigo, evitando um avanço indevido para o turno adversário.

## CARTAS

- O catálogo atual foi redistribuído para uma maioria de cartas Comuns e uma minoria de Incomuns.
- A única carta Rara atual é a de Kuvaar.
- As cartas Míticas permanecem vinculadas às resoluções de facção atualmente implementadas.
- Não há cartas Lendárias ou Únicas implementadas nesta etapa.
- Cartas Únicas continuam reservadas ao futuro sistema de fabricação.
- Algumas Incomuns ganharam efeitos táticos adicionais coerentes com o tipo: Atordoamento Elétrico, redução de ATQ em ataques de Metal, Afogamento em ataques de Água e DoT em ataques de Fogo; os demais tipos ainda não recebem efeito tático específico.

## INVENTÁRIO E RENOME

- A área de detalhes do Inventário possui barra de rolagem independente para listas longas de receitas.
- O menu de Renome usa uma estrutura escalável por galáxia e planeta visitados, com lista rolável e painel amplo do planeta selecionado.
- Estatísticas permanecem agregadas: criaturas individuais continuam sendo responsabilidade do Bestiário, enquanto Planetas e Missões não são enumerados no painel estatístico.

## COMPATIBILIDADE DE SAVE

- A versão persistente é 53.
- O loader aceita versões antigas e futuras e preserva IDs desconhecidos de cartas, criaturas, planetas, setores e estatísticas em vez de descartá-los silenciosamente.
- Setores atuais ausentes são recriados com seus inimigos iniciais, enquanto setores desconhecidos de uma versão futura continuam armazenados no save.
- `save.json` e `bkp.json` permanecem no diretório persistente do AppData.

## ESTRUTURA PARA BOSSES FUTUROS

- Uma arena foi reservada em cada planeta atual.
- Nenhum boss novo, atributo ou mecânica de boss foi inventado nesta versão; essas definições ficam para a próxima etapa.

### Compatibilidade final de save
- O carregamento de versões futuras preserva também chaves de estatísticas de criaturas que ainda não existem na build atual.
- O save enviado pelo usuário (formato legado v49) foi validado novamente na 0.5.3 e convertido sem bloqueio.
