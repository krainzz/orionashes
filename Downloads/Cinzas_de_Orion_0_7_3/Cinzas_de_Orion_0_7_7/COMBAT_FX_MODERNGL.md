# Sistema de Efeitos de Combate — ModernGL/GLSL

O sistema é exclusivamente visual. Ele não lê nem modifica dano, atributos, mana, turnos, drops ou saves. A arena continua sendo desenhada pelo Pygame existente; durante fases de ataque, a imagem pronta passa por um framebuffer ModernGL, que acrescenta luz, distorção e partículas GPU. Se ModernGL ou o contexto GL 3.3 falhar, a camada retorna ao renderizador Pygame sem interromper o combate.

## Arquivos

- `combat_fx.py` — API de presets, temporização de eventos, contexto off-screen, framebuffer e renderização instanciada.
- `assets/shaders/combat_post.vert.glsl` e `combat_post.frag.glsl` — composição da cena, pontos de luz, refração e aberração cromática.
- `assets/shaders/combat_particles.vert.glsl` e `combat_particles.frag.glsl` — geração de partículas por `gl_InstanceID` e renderização aditiva das partículas.

## Dependências

Instale com `pip install -r requirements.txt`. O ModernGL usa um contexto off-screen próprio para não exigir que a janela Pygame seja convertida para `OPENGL`; isso preserva o pipeline de UI e a escala de janela atuais.

## Presets configuráveis

Em `combat_fx.py`, edite `FX_PRESETS`. Cada preset expõe `duration` (segundos), `color` (RGB 0–255), `intensity`, `light_radius` (pixels), `particles`, `shockwave` e `shock_intensity`. Também é possível alterar presets em runtime:

```python
app.combat_fx_renderer.configure(
    "fire",
    duration=1.15,
    color=(255, 110, 35),
    intensity=1.2,
    light_radius=300,
    particles=90,
)
```

Presets disponíveis: `physical`, `fire`, `water`, `plant`, `earth`, `metal`, `electric`, `light`, `dark`, `shield` e `heal`. Os elementos compartilham o mesmo shader de partículas instanciadas, mas têm paleta, intensidade e contagem configuráveis. Fogo sobe e muda de vermelho para amarelo; Escudo forma uma elipse cinética; Cura sobe em espiral; os demais elementos se expandem do ponto de impacto em sua cor.

## Ondas de choque

O resultado `critical` ativa `CRITICAL_SHOCKWAVE`; cartas Míticas, Lendárias e Únicas são tratadas visualmente como técnicas supremas e usam `SUPREME_SHOCKWAVE`. Ajuste `duration`, `intensity` e `chromatic` nesses dois dicionários. Nenhum deles participa do cálculo de crítico ou de dano.

## Extensão

Para adicionar outro preset, inclua os parâmetros em `FX_PRESETS`, associe o elemento em `ELEMENT_PRESETS` se aplicável, e adicione seu ID em `preset_ids` dentro de `_render`. Comportamentos exclusivos adicionais podem ser acrescentados na ramificação de `u_preset` de `combat_particles.vert.glsl`.
