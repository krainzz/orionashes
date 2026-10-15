// ============================================================================
// distortion.frag — screen-space distortion de calor/impacto.
// Desloca a amostra da cena usando um campo de ruído animado, mascarado por
// "ondas de choque" circulares emitidas pelos impactos (u_impacts).
// u_impacts: [x, y, t_norm, strength] repetido até 8 fontes.
// ============================================================================
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D u_scene;      // buffer HDR da cena (pygame já blitado)
uniform vec2  u_viewport;       // (W,H) em px
uniform float u_time;
uniform int   u_impact_count;
uniform vec4  u_impacts[8];     // xy = centro em px, z = progresso 0..1, w = força

vec2 grad2(vec2 p) {
    float a = dot(p, vec2(127.1, 311.7));
    float s = sin(a) * 43758.5453123;
    return vec2(cos(s), sin(s)) * 6.2831853;
}
float noise2(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(dot(grad2(i), f), dot(grad2(i + vec2(1,0)), f - vec2(1,0)), u.x),
               mix(dot(grad2(i + vec2(0,1)), f - vec2(0,1)),
                   dot(grad2(i + vec2(1,1)), f - vec2(1,1)), u.x), u.y);
}

void main() {
    vec2 uv = v_uv;
    vec2 px = uv * u_viewport;
    vec2 offset = vec2(0.0);

    for (int i = 0; i < 8; ++i) {
        if (i >= u_impact_count) break;
        vec4 imp = u_impacts[i];
        float prog = imp.z;                       // 0..1 ao longo do efeito
        float dist = length(px - imp.xy);
        // frente de onda que se expande ~ 520px no pico
        float wave_r = 40.0 + prog * 480.0;
        float band = exp(-pow((dist - wave_r) * 0.018, 2.0));
        // heat-haze persistente dentro do raio, com scroll de ruído
        float haze = noise2(px * 0.02 + vec2(u_time * 1.7, -u_time * 1.1)) * 0.5 + 0.5;
        float inside = smoothstep(wave_r + 90.0, wave_r * 0.25, dist);
        float amt = imp.w * (band * 14.0 + inside * haze * 5.0) * (1.0 - prog);
        offset += normalize(px - imp.xy + vec2(0.31)) * amt;
    }

    vec2 shifted = uv + offset / u_viewport;
    // clamp suave para não amostrar fora da tela
    shifted = clamp(shifted, vec2(0.0005), vec2(0.9995));
    fragColor = texture(u_scene, shifted);
}
