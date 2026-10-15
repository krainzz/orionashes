# Cinzas de Órion — 0.7.2 HOTFIX 2

## Sistema de Efeitos de Combate (ModernGL/GLSL)

- Adicionada camada de renderização off-screen baseada em ModernGL, sem alterar regras de turno, fórmulas de atributos, dano, mana ou save.
- Técnicas de jogador e ataques inimigos acionam presets de iluminação dinâmica por atenuação de distância.
- Adicionado sistema de partículas instanciadas em GPU via `gl_InstanceID`, com presets para Fogo, Escudo, Cura e os oito elementos.
- Críticos e técnicas Míticas/Lendárias/Únicas acionam pós-processamento FBO com refração radial e aberração cromática.
- Configurações de duração, cor, intensidade, alcance de luz, contagem de partículas e intensidade da onda ficam expostas em `combat_fx.py`.
- O pipeline Pygame existente é preservado; se ModernGL/contexto GL 3.3 não estiver disponível, os efeitos GPU são desativados e os efeitos de combate atuais continuam funcionando.
- Shaders e documentação adicionados em `assets/shaders/` e `COMBAT_FX_MODERNGL.md`.
