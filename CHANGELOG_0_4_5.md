# Cinzas de Órion 0.4.5 — Sociedade, Nave e Primeiro Arco

## Combate
- Barra de HP do inimigo restaurada sem valor numérico.
- Atributos técnicos dos inimigos permanecem ocultos até futuras funções de Scan.
- HP dos encontros de Veyra foi aumentado para alongar os combates sem elevar artificialmente o dano básico da fauna.
- Mantidos dano variável, críticos, AMP da Skill e atributos ATQ/DEF/AMP/CRIT/DCRIT.

## Nave
- Entrada física na nave.
- Mapa interno com cockpit, computador de bordo, painel de status e airlock.
- Diagnóstico dos seis sistemas com integridade e requisitos de reparo.

## Elmo
- Craft do Elmo G1 habilitado.
- Núcleo de decodificação e Célula de energia instável como componentes intermediários.
- Elmo equipado habilita análise cultural e progresso linguístico.

## Sociedade e missão
- Novos setores com assentamentos e NPCs Avarin.
- NPCs sólidos e bloqueio de passagem.
- Missão Água para Qaresh.
- Resolução por reparo, confronto ou hack.
- Hack iniciado pela Manopla em terminais compatíveis.
- Renome disponível no Status como barra visual; valores de consequência reservados para a 0.4.6.

## Conquistas
- Estatísticas de combate, coletas, missões e fabricação.
- Log de conquistas paginado.
- Recompensas futuras preparadas para coleção completa de cartas normais, + e ++.

## Cartas
- Raridade associada à força/importância dos encontros.
- Variantes normal/+ /++ com 95% / 4,5% / 0,5%.
- Atributos da carta exibidos somente quando concedem bônus.

## Inicialização
- Launcher sem `venv` persistente.
- Pygame compartilhado em `%LOCALAPPDATA%\CinzasDeOrion\deps` para reutilização entre versões.

## Save
- Arquivo atual: `save_v045.json`.
- Migração preservada para saves 0.2, 0.3, 0.4, 0.4.1, 0.4.2, 0.4.3 e 0.4.4.

## Revisão adicional — feedback de validação

- Recompensas de conquistas comuns foram reduzidas a pequenos lotes de materiais de farm.
- Apenas os três marcos de coleção integral de cartas permanecem com recompensas permanentes de atributo; o marco de cartas ++ também prepara a futura Carta Única.
- WASD permanece reservado exclusivamente à movimentação; atalhos de função usam outras teclas e o hack usa setas/Enter.
- Corrigida a interação `E` dentro da nave para não retornar à escotilha por engano.
- **NEXUS** tornou-se o aprimoramento especial da Manopla: XP por dano causado, níveis e árvore de evolução própria.
- **Removedor de Aprimoramento** é consumível craftável e necessário para retirar cartas equipadas dos slots.


### Revisão de balanceamento — coleção e NEXUS
- Conquistas de coleção: cartas normais = ATQ +10; cartas + = Dano Crítico +6%; cartas ++ = AMP +5%.
- A AMP do personagem passou a somar à AMP específica da Skill no cálculo do dano.
- NEXUS ampliado para 20 níveis e 165.000 XP acumulados no máximo; somente modificadores ofensivos e em incrementos pequenos.
- Fauna inicial rebalanceada para combates mais longos e menos letais: HP maior, dano inimigo menor e crítica inicial mantida baixa.

### Revisão do NEXUS — progressão alongada
- curva recalibrada para 20 níveis e 25.000.000 XP no nível máximo;
- 1 ponto de dano causado = 1 XP permanece;
- recompensas continuam pequenas e exclusivamente ofensivas;
- saves antigos têm o nível recalculado a partir do XP real acumulado, evitando manter níveis obtidos com a curva anterior.

## Hotfix 0.4.5 — acesso ao NEXUS
- A tecla `X` agora abre a tela do NEXUS diretamente durante a exploração, mesmo antes da instalação, permitindo consultar a tela e os requisitos.
- O item NEXUS no Menu deixou de ficar desabilitado quando não instalado; a tela informa como obtê-lo.
- `X` mantém o retorno correto para a origem da tela ao usar ESC.
