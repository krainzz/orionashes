// ============================================================================
// composite.frag — passe final: cena HDR + bloom aditivo + hit flash.
// O resultado é amostrado pelo pygame via read_pixels (ou exibido direto se
// houver janela GL). Inclui vignette leve e grade de pixels sutil para
// manter a identidade pixel-art do jogo.
// ============================================================================
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D u_scene;   // HDR pós-distorção
uniform sampler2D u_bloom;   // blur do brilho extraído
uniform float u_time;
uniform vec4  u_flash;       // rgba: cor do hit flash × intensidade (1-3 frames)
uniform float u_bloom_strength;

vec3 tonemap(vec3 c) {
    float l = max(max(c.r, c.g), c.b);
    return c * (1.0 + l * 0.6) / (1.0 + l);
}

void main() {
    vec3 scene = texture(u_scene, v_uv).rgb;
    vec3 bloom = texture(u_bloom, v_uv).rgb;
    vec3 col = scene + bloom * u_bloom_strength;

    // hit flash: branco/colorido, 1-3 frames, aplicado sobre tudo
    col += u_flash.rgb * u_flash.a;

    col = tonemap(col);

    // vignette discreta foca o centro da arena
    vec2 q = v_uv - 0.5;
    col *= 1.0 - dot(q, q) * 0.35;

    // grain temporal mínimo (evita banding em áreas escuras)
    float g = fract(sin(dot(v_uv * 511.0 + u_time, vec2(12.9898, 78.233))) * 43758.5453);
    col += (g - 0.5) * 0.012;

    fragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
