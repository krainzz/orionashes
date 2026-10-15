# Cinzas de Órion — 0.4.3

## Manopla / interface
- Mensagens de interação e informação passaram a aparecer em uma caixa suspensa simulando o display digital da Manopla.
- O log ocupa um espaço flutuante no canto superior esquerdo e substitui a antiga linha solta de mensagens.
- O visual é deliberadamente simples nesta fase, para servir de base à futura direção artística.

## Progressão futura
- Criada a base de projetos futuros para Manopla, Peitoral, Elmo, Módulo de Locomoção, circuitos de memória e canal especial.
- Custos futuros incluem materiais que não existem no inventário de Veyra, evitando que toda a progressão possa ser farmada no planeta inicial.
- Criado painel `T` de Projetos Tecnológicos, somente consulta nesta fase.

## Armadura visual
- Adicionada camada modular para representar visualmente o elmo quando estiver equipado.
- O save já carrega `helmet_generation`, `gauntlet_generation` e `locomotion_generation` para suportar futuras peças e evoluções sem reestruturar o personagem.

## Inicialização
- `iniciar.bat` passa a usar marcador local `.deps\\.pygame_ready` e só instala Pygame quando realmente necessário.
- A cópia local é reutilizada entre as aberturas do jogo.

## Compatibilidade
- Migração automática: 0.4 / 0.4.1 / 0.4.2 → 0.4.3.
- O save atual passa a ser `save_v043.json`.
- Saves antigos não são sobrescritos.


## Revisão de interface — 0.4.3

- O log da Manopla deixou o rodapé e agora aparece como **popup digital temporário no canto superior esquerdo**, abaixo da identificação do mapa.
- A janela desaparece automaticamente após alguns segundos, com fade curto, para não ocupar a HUD durante a exploração.
- A HUD lateral foi reorganizada: o Menu passou para o cabeçalho e as informações de criaturas/assentamento ganharam espaçamento.
- `ESC` no cabeçalho de qualquer painel agora respeita a origem: hotkey/E retorna ao mundo; Menu retorna ao Menu.
- Adicionado **diagnóstico técnico da nave**, com leitura persistente de casco, energia, propulsão, navegação, comunicação e dobra.
- `N` abre o diagnóstico enquanto o personagem está junto da nave; `E` continua abrindo a bancada/craft. O Menu também possui a opção de diagnóstico quando estiver na nave.
- A inicialização agora verifica primeiro o Pygame no Python do sistema e só instala quando ele realmente não estiver disponível; `.deps` permanece como fallback.


## Correção final da revisão 0.4.3
- Corrigido `KeyError` ao renderizar o display da Manopla com os tamanhos 10 e 11.
- `label()` e `wrap()` agora obtêm fontes sob demanda, evitando novos erros do mesmo tipo caso uma futura tela utilize outro tamanho.


### Revisão posterior — interface e mundo
- Display da Manopla menor e no canto superior direito.
- HUD lateral do mundo removida; informações exploratórias passam a ser descobertas durante o jogo.
- Novo painel de Status/Sistemas para consulta intencional.
- NPCs físicos e não atravessáveis; coletável de Qaresh reposicionado.
- Inicialização preparada para ambiente persistente de dependências.
