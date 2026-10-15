# Cinzas de Órion — Versão 0.6.0

## Expansão intergaláctica
- O Núcleo de Dobra, obtido como drop especial garantido na derrota real de RY, pode ser instalado no motor da nave.
- A instalação libera viagens para duas novas galáxias: **Vharos** e **Meridion**.
- Cada nova galáxia possui quatro planetas conectados por sua própria malha de rotas.
- A Rota Estelar passa a distinguir a seleção de galáxia e mantém as novas viagens bloqueadas até a instalação do núcleo.

## Galáxia Vharos
- **Dornak:** mundo metálico e de forjas, com Mekron como boss raro.
- **Nyxara:** mundo crepuscular e subterrâneo, com Nocther como boss raro.
- **Zereth:** mundo iônico e tempestuoso, com Voltrik como boss raro.
- **Pyraxis:** mundo vulcânico, culminando na caldeira de **Alphor, o Balrog**.
- Alphor permanece bloqueado até a derrota dos três bosses raros de Vharos.
- A técnica de Alphor e sua carta lendária usam **Bola de Fogo** e são configuradas para múltiplos alvos.
- A parte vital de Alphor, o **Núcleo Ígneo**, só fica disponível após os dois chifres serem destruídos.

## Galáxia Meridion
- **Thalassene:** mundo úmido de recifes, com Moryss como boss raro.
- **Mycelon:** mundo de florestas e estruturas esporais, com Verdak como boss raro.
- **Tethra:** mundo de cânions e correntes de vento, com Gravorn como boss raro.
- **Nerissa:** mundo urbano com cidade multicivilizacional espalhada por vários mapas; a torre central abriga **Broom, o Samurai Celeste**.
- Broom permanece bloqueado até a derrota dos três bosses raros de Meridion.
- A técnica e a carta lendária de Broom são de alvo único e usam **Raio**.
- O ataque especial de Broom usa a mecânica de ataque fatal/QTE existente, com janela de **Escudo Stasis** para bloqueio.
- A carta permite execução imediata do alvo vital quando ele entra na faixa de 25% da Vida.

## Nerissa e idiomas
- Habitantes de Avarin e Nahr continuam conversando normalmente quando essas línguas já são conhecidas.
- Se o jogador conversar com uma civilização ainda desconhecida, a Manopla/Elmo inicia uma **Calibração Linguística** por QTE.
- Ao passar no QTE, o idioma é aprendido e os próximos contatos com aquela civilização deixam de exigir calibração.
- Novas civilizações usadas na cidade incluem Draan, Nyxen, Velkari, Mycelari e Tethran, além de habitantes já conhecidos.

## Fauna e cartas
- Vharos e Meridion receberam fauna própria distribuída pelos novos mapas.
- Os novos cards seguem a regra existente de uma única bonificação permanente por raridade e não concedem DEF.
- Os atributos permanentes continuam respeitando os valores definidos para Comum, Incomum, Rara, Mítica e Lendária.
- Cada criatura continua seguindo a estrutura de dois ataques da criatura: básico + técnica vinculada à carta.

## Compatibilidade e persistência
- Saves anteriores continuam sendo migrados pela rotina existente.
- Estado do Núcleo de Dobra, seleção de galáxia e idiomas aprendidos é persistido no save.
- Os comportamentos especiais de RY e do Simulador foram preservados.

## Validação
- Suíte completa: **303 testes passando**.
- **3 testes pulados** por ausência do Pygame no ambiente de validação.
- Todos os arquivos Python compilam sem erro.
