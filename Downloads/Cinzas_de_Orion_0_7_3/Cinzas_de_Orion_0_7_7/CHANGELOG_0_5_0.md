# Cinzas de Órion — CHANGELOG 0.5.0

## HOTFIXES E INTERFACE
- Menu principal reorganizado em três grupos para distribuir melhor os comandos.
- Computador de bordo reorganizado sem sobreposição entre Oficina/Craft e Diagnóstico da Nave.

## COCKPIT / ROTA ESTELAR
- Rota Estelar acessível somente pelo Cockpit físico.
- Pontos de planeta clicáveis.
- Destinos ainda não conhecidos são exibidos como `???`.
- Estado do destino selecionado é persistido no save.

## PEITORAL / AURORA
- Nova tela dedicada ao Peitoral.
- Slots de memória exibem `VAZIO`, `OCUPADO` ou `BLOQUEADO`.
- Slots avançados são liberados conforme o Tier do Peitoral.
- AURORA Plus: +20 HP, +2 ATQ, +2% Dano Crítico.
- AURORA Nova: +40 HP, +4 ATQ, +1% Taxa Crítica, +4% Dano Crítico.
- AURORA Ultimate: +100 HP, +10 ATQ, +4% Taxa Crítica, +10% Dano Crítico.
- Bônus dos aprimoramentos do AURORA são substitutivos, não cumulativos.
- AURORA Plus utiliza somente drops disponíveis em Veyra; Nova e Ultimate permanecem bloqueados para tecnologia futura.

## RENOME
- Novo menu de Renome acessível pelo Menu.
- Renome separado por facção e agregado por planeta e galáxia.
- Conclusões de missão atribuem Renome à facção beneficiada.
- Milestones de facção, planeta e galáxia geram recompensas resgatáveis.
- A antiga barra de Renome foi removida do Status.

## BESTIÁRIO / CRIATURAS
- Novo menu de Bestiário.
- Antes do Scan: somente tipo e mapas conhecidos.
- Após o Scan e novo encontro: atributos e HP passam a ser registrados.
- Criaturas no mapa exibem uma faixa preta com nome.
- O nível calculado da criatura aparece na faixa somente após o Scan.

## PERSISTÊNCIA
- Save continua sendo armazenado em `%LOCALAPPDATA%\Cinzas de Órion\save.json`.
- Novos estados de AURORA, slots, Renome e descobertas estelares foram incorporados à persistência e à migração de saves anteriores.

## FORA DO ESCOPO
- A restauração da nave e as missões necessárias para elevar os seis sistemas a 100% continuam em planejamento e não foram implementadas nesta versão.
