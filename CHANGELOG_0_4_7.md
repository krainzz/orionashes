# Changelog 0.4.8

- Quatro direções do protagonista no mapa: cima, baixo, esquerda e direita.
- Tipos de criaturas e cartas, sem exposição do tipo da criatura no combate; o tipo da carta só é revelado quando a carta é analisada.
- Inventário mostra apenas itens possuídos, em ordem alfabética.
- Conquistas desbloqueiam sem entregar recompensa automaticamente; exigem resgate manual.
- Alertas de desbloqueio e recebimento de recompensa.
- Projetos de Tier sucessor ocultos até o Tier anterior ser alcançado.
- Catálogo de Recursos com origem e local, incluindo indicação de boss.
- Flora de Veyra com quatro ervas e bloqueio por Scan.
- Terminologia de equipamentos alterada de Geração para Tier.
- Slot especial da Manopla renomeado para Slot Único da Manopla.
- Descrição do NEXUS da Oficina definida como "Habilita a senciência da manopla".
- Save atualizado para save_v047.json.
## Revisão 0.4.7 — ajuste gráfico e combate preparado
- Perfis laterais do protagonista redesenhados: silhueta mais estreita e vertical, uma única perna legível em perfil e Manopla visível apenas quando o perfil corresponde ao braço direito.
- Animação de caminhada refinada para tornar a passada das pernas perceptível.
- Glow suave e pulsante do núcleo do Peitoral somente na visão frontal durante a exploração.
- Botão RECURSOS removido do Menu global e reposicionado no rodapé de Projetos Tecnológicos.
- Toda criatura comum recebeu uma `vital_zone` explícita; o ponto vital fica disponível para a futura mecânica de crítico, sem alterar o cálculo de dano nesta revisão.
- Kuvaar recebeu `vital_zone='ventral'`, mantendo a regra atual de dano e sem insta-kill.
- Linhas de contorno de cada quadrado do terreno removidas para testar o mapa sem grid; limites naturais do terreno foram preservados.
## Revisão final 0.4.7 — ajustes de encerramento
- A tela de vitória força a apresentação frontal do protagonista, independentemente da direção usada antes do fim da batalha.
- O efeito de glow frontal do Peitoral foi removido.
- Kuvaar agora pode ser iniciado assim que o jogador alcança a Bacia de Kuvaar, sem exigir a conclusão prévia da missão.
- A dificuldade da batalha real de Kuvaar aumenta conforme os três preparativos narrativos ainda não concluídos (abastecimento, rastreamento e preparação de água). A conclusão dos três mantém as condições-base planejadas.
- A Água Pura continua sendo uma ferramenta tática; sem preparação prévia, o jogador pode entrar no confronto sem reserva e perde a ferramenta de exposição da Couraça, tornando a luta naturalmente mais severa.

