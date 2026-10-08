# Cinzas de Órion — CHANGELOG 0.7.1

## Projeto: Emissor Laser
- Novo projeto tecnológico dos Recuperadores de Qaresh.
- Desbloqueio após idioma Avari + 25 pontos de Renome com a facção.
- Entrega por Mira nas Oficinas de Sifra.
- Instalação exclusiva no Computador da Nave.
- Receita: 30 Sucatas, 10 Placas, 4 Ligas meteóricas e 2 Matrizes fotônicas.

## Encontro: Asteroides
- Ativado somente após a instalação do Emissor Laser.
- Ocorre apenas em viagens entre galáxias, com 30% de chance e no máximo um encontro por viagem.
- Setas direcionais movimentam a nave; ESPAÇO dispara o laser.
- Cada asteroide destruído concede 1 Essência.
- Cada colisão adiciona 1 Dano de Viagem, limitado a 6 por encontro.

## Reparo da Nave
- Dano de Viagem é separado dos seis sistemas de restauração originais.
- Após o pouso, o dano é persistido e ativa a missão **Reparo de Emergência**.
- Cada ponto de dano exige 1 Sucata.
- Novas viagens ficam bloqueadas até o reparo.
- O reparo é realizado pelo Diagnóstico da Nave e consome a Sucata somente na conclusão.

## Compatibilidade
- Saves anteriores ao schema 71 recebem os novos campos com valores seguros.
- A viagem entre planetas continua inalterada quando a rota não cruza galáxias.
- O encontro espacial foi isolado como um tipo de evento de viagem para permitir futuros encontros sem refazer o sistema.

## Validação
- `content.py`, `core.py`, `main.py` e testes 0.7.1 compilam sem erros.
- `test_071_features.py`: cobertura de gate de Renome/idioma, projeto, instalação, encontro, recompensa, dano, bloqueio, reparo e save/load.
- A máquina de validação não possui Pygame instalado e não tem acesso à rede para instalação da dependência; por isso a execução visual do cliente Pygame não foi possível neste ambiente.

## Badges Elementais
- Substituição dos símbolos elementais procedurais pelas badges pixel-art oficiais, sem texto.
- As oito badges são reutilizadas no Domínio, Cartas Únicas e miniaturas discretas das cartas por raridade.
- Escala com nearest-neighbor para preservar o estilo pixel-art e fallback procedural mantido para segurança.
