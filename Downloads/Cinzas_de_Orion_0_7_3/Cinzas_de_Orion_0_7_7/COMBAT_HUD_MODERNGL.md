# Combat HUD — ModernGL / GLSL

A release 0.7.3 desenha o HUD de combate numa `pygame.Surface` transparente separada da arena. `CombatHUDRenderer` envia somente essa camada para um FBO ModernGL, aplica barrel distortion sutil e bloom, lê o resultado mantendo o canal alfa e compõe a interface sobre a cena já renderizada. Portanto, a lente não deforma os sprites nem a arena.

## Arquivos

- `combat_hud.py` — carregamento seguro do contexto, FBO, upload/composição e fallback.
- `assets/shaders/combat_hud.vert.glsl` — triângulo de tela cheia.
- `assets/shaders/combat_hud.frag.glsl` — mapeamento de lente e extração de brilho para bloom.
- `main.py` — desenho da interface, estados visuais, layout, cartões e indicador de chance de acerto.

## Parâmetros expostos

`CombatHUDRenderer.apply(surface, time=0.0, curvature=0.008, glow=0.48)`:

- `curvature`: intensidade da curvatura radial; faixa interna limitada a `0.0–0.04`.
- `glow`: intensidade de bloom; faixa limitada a `0.0–1.5`.
- `time`: anima a respiração luminosa sem atualizar estados do jogo.

Em `main.py`, `_draw_combat_hud_ambient()` controla densidade/cor da grade e a oscilação das barras técnicas. `_draw_combat_hud_button()` controla cores, pulso, linha de varredura e mira dos botões. Os desenhos continuam funcionais em Pygame puro se ModernGL não inicializar.

## Compatibilidade

- Reutiliza as hitboxes e callbacks existentes em `self.buttons`; o efeito visual não altera a seleção ou as ações.
- O template da carta continua mostrando raridade, arte, custo, dano e tooltip interativo.
- `TARGET_LOCK` lê `State.target_hit_chance()` para o alvo corporal selecionado; o sistema não modifica a chance.
- O framebuffer de efeitos de ataque é processado antes do framebuffer de HUD, para que a distorção da lente fique restrita à UI.
