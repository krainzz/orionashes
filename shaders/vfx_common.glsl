// ============================================================================
// vfx_common.glsl — Cinzas de Órion | Sistema de VFX (pygame + ModernGL)
// Biblioteca compartilhada GLSL 330 core: ruído Perlin, fbm e utilitários.
// Usada pelos passes de partículas, distorção e bloom.
// ============================================================================
#ifndef VFX_COMMON_GLSL
#define VFX_COMMON_GLSL

#version 330 core

// --- Ruído de gradiente 2D (Perlin clássico, sem tabelas fora da shader) ----
vec2 vfx_grad(vec2 p) {
    // rotação irracional -> ângulos pseudo-aleatórios por célula
    float a = dot(p, vec2(127.1, 311.7));
    float s = sin(a) * 43758.5453123;
    return vec2(cos(s), sin(s)) * 6.2831853;
}

float vfx_perlin(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    // curva de suavização quintica (6t^5 - 15t^4 + 10t^3)
    vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float n00 = dot(vfx_grad(i + vec2(0.0, 0.0)), f - vec2(0.0, 0.0));
    float n10 = dot(vfx_grad(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0));
    float n01 = dot(vfx_grad(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0));
    float n11 = dot(vfx_grad(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0));
    return mix(mix(n00, n10, u.x), mix(n01, n11, u.x), u.y);
}

// --- fbm (fractal brownian motion): lava, água, fogo em movimento contínuo --
float vfx_fbm(vec2 p, float t, int octaves) {
    float amp = 0.5;
    float sum = 0.0;
    for (int i = 0; i < 5; ++i) {
        if (i >= octaves) break;
        // domínio rotacionado/escalado entre oitavas quebra a regularidade
        mat2 rot = mat2(0.80, 0.60, -0.60, 0.80);
        p = rot * p * 2.02 + vec2(13.5 + t * 0.7, 9.2 - t * 0.5);
        sum += amp * vfx_perlin(p);
        amp *= 0.5;
    }
    return sum;
}

// --- utilitários de cor ------------------------------------------------------
float vfx_luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

vec3 vfx_tonemap(vec3 c) {
    // Reinhard estendido: comprime HDR do bloom sem clipping duro
    float l = max(vfx_luma(c), 1e-5);
    return c * (1.0 + l / 2.0) / (1.0 + l);
}
#endif // VFX_COMMON_GLSL
