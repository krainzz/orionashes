# Cinzas de Órion — 0.5.2

## HOTFIXES

- O comando padrão para **pular, aceitar ou continuar** telas que antes pediam Enter passa a usar **Espaço**.
- O hack da Manopla, aceitação de missões, conclusão do combate e tela de vitória foram ajustados para Espaço.
- O hotfix mantém as setas/WASD reservados para movimentação e seleção quando aplicável.

## NAVEGAÇÃO ENTRE PLANETAS

- Após os seis sistemas da nave chegarem a 100%, o voo interestelar é liberado.
- A missão principal **Explore a Galáxia** é ativada nesse momento.
- Enquanto existir apenas a Galáxia Nárion, a missão permanece com esse título e aberta; a progressão futura será preparada para trocar para **Explore o Universo** quando novas galáxias forem adicionadas.
- A comunicação restaurada identifica os cinco mundos catalogados desta galáxia e permite selecionar seus destinos no Cockpit.
- Toda viagem para outro planeta passa primeiro por uma cena de navegação espacial, com a nave atravessando o espaço até o destino.
- O pouso de cada planeta ocorre sempre no mesmo ponto fixo da sua área de aterrissagem.
- É possível retornar para Veyra pelo Cockpit.

## NOVOS PLANETAS

Foram adicionados quatro mundos além de Veyra, cada um com quatro mapas:

- **Orionis:** calor químico, escória e formações ferrídeas.
- **Kael:** gelo, vento e florestas cristalinas.
- **Nahr:** basalto, sal profundo e flora agressiva.
- **Elyra:** pântanos densos, bioluminescência e áreas umbrías.

Cada mundo possui fauna própria, novos recursos, flora específica e mapas sem missões narrativas nesta etapa. Algumas plantas podem se repetir entre mapas do mesmo planeta, enquanto a flora entre planetas foi diferenciada visualmente.

As plantas novas continuam condicionadas ao Scan e as rochas permanecem inacessíveis para coleta até que as tecnologias correspondentes existam, seguindo a lógica de Veyra.

## FAUNA E CARTAS

- 12 criaturas novas foram adicionadas, distribuídas pelos quatro planetas.
- Os novos inimigos respeitam os tipos já existentes e apresentam uma progressão de atributos do primeiro ao quarto mundo.
- Cada nova criatura possui carta correspondente, ataque próprio e receita de fabricação.
- As cartas novas usam raridade **Incomum** e bônus percentuais de Ataque compatíveis com a escala já estabelecida.
- A matriz de vantagens de tipos existente foi preservada.

## AURORA

- O detalhe energético do Peitoral acompanha visualmente o Tier do AURORA:
  - inicial: ciano;
  - AURORA Plus: vermelho;
  - AURORA Nova: amarelo;
  - AURORA Ultimate: azul.
- O mesmo detalhe aparece dinamicamente no sprite do personagem e na prévia do Equipamento.

## ELMO

- O craft do **Elmo G1** passa a equipá-lo automaticamente.
- O botão de equipar/retirar Elmo foi removido da tela de Equipamento.
- Foram preparados três designs de Elmo, tanto para a prévia do menu quanto para os sprites do personagem:
  - **Elmo Tático** — design atual e funcional;
  - **Elmo de Reconhecimento** — preparado para futura liberação;
  - **Elmo de Combate** — preparado para futura liberação.
- Cada design possui suporte visual para frente, direita, costas e esquerda.
- As identidades e descrições de habilidade dos três designs já estão catalogadas; os dois designs futuros permanecem bloqueados até que seus sistemas de progressão sejam implementados.

## COMPATIBILIDADE DE SAVE

- O formato persistente continua sendo `%LOCALAPPDATA%\Cinzas de Órion\save.json`.
- O arquivo anterior é preservado como `%LOCALAPPDATA%\Cinzas de Órion\bkp.json` antes de uma sobrescrita.
- Saves antigos continuam sendo migrados para a estrutura 0.5.2 sem perder o progresso existente.
