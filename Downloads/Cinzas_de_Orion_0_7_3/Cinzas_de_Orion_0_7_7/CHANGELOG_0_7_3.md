# Cinzas de Órion — 0.7.3

## HUD futurista de combate

- Interface de combate redesenhada como visor de alta tecnologia com acentos neon ciano.
- Botões de ação e seleção de alvo agora têm moldura vetorial, brilho, indicador lateral, mira nos cantos e pulso ao passar o cursor/selecionar.
- Os cartões de habilidade preservam arte, raridade, custo, dano, estado habilitado e tooltip interativo.
- Adicionada telemetria discreta de HUD (`SYS_STATUS`, `HUD LINK`) e grade técnica limitada aos espaços da interface.
- `TARGET_LOCK` reflete a chance de acerto da parte corporal selecionada.
- Criada camada alfa de interface processada num FBO ModernGL próprio. Shaders separados realizam uma curvatura de lente sutil e bloom de baixa intensidade.
- O framebuffer de HUD é composto depois dos efeitos de ataque, mantendo os sprites de aliados e inimigos fora da distorção da lente.
- ModernGL permanece opcional; a interface Pygame continua sendo fallback se o driver/contexto não estiver disponível.
- Não foram alterados os cálculos de combate, estados, atributos, turnos, saves ou regras de jogo.
