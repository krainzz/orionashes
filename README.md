0.7.2


# Cinzas de Órion — 0.7.2

Atualização focada na evolução da nave, com o **Emissor Laser**, encontros de asteroides em travessias intergalácticas e um sistema de dano/reparo persistente sem alterar os seis sistemas originais da nave.


### 0.6.9 HOTFIX 1

- XP de Domínio também é concedido em confrontos do Simulador.
- Dano causado ao inimigo é limitado a 2x o HP máximo por evento, e o valor limitado é o usado para XP do NEXUS.

- Simulador também concede XP de Domínio; drops especiais continuam seguindo suas regras próprias.



### 0.7.2

- Badges elementais pixel-art oficiais aplicadas ao Domínio e às cartas, sem rótulos textuais.

- Projeto de **Emissor Laser** desbloqueado com Avari conhecido + primeiro nível de Renome dos Recuperadores de Qaresh.
- Instalação do Emissor Laser pelo Computador da Nave, usando Sucata, Placa, Liga meteórica e Matriz fotônica.
- Novo encontro aleatório de asteroides em viagens entre galáxias, disponível somente após a instalação do laser.
- Asteroides destruídos concedem Essência; colisões geram Dano de Viagem persistente, separado dos seis sistemas originais da nave.
- Dano de Viagem bloqueia novas viagens até a missão de reparo ser concluída com Sucata proporcional ao dano.
- Diagnóstico da Nave recebe o reparo em interface compacta, mantendo o layout existente.
- Save 0.7.0 continua compatível e ganha migração automática para o schema 72.
- Testes focados da 0.7.2 em `test_071_features.py`.

### 0.7.1 HOTFIX 1

- Visualizações oficiais das quatro peças principais referenciadas em `assets/equips/`: `Manopla.png`, `Elmo.png`, `Peitoral.png` e `Grevas.png`.
- Os arquivos de arte não acompanham o pacote e devem ser adicionados manualmente. Na ausência de algum arquivo, a visualização procedural anterior é usada como fallback.

### 0.7.0 HOTFIX 1

Ajustes de seleção/equipamento da Manopla e conversão dos bônus de ATQ das Cartas Únicas para percentuais.
