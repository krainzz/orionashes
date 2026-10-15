// ============================================================================
// particle.frag — GLSL 330 core | ModernGL
// Fragmento único para TODOS os tipos de partícula (one draw call por frame).
// Cada "kind" escolhe um sprite procedural: faísca, brasa com fbm de fogo,
// gota d'água refrativa, folha, lasca de metal, rocha, raio elétrico,
// partícula de luz, sombra, fumaça volumétrica, anel de choque, rachadura,
// cruz de cura e hexágono de escudo. Cor interpola life_a -> life_b.
// Escreve em buffer HDR (RGBA16F) — o brilho acima de 1.0 alimenta o bloom.
// ============================================================================
#version 330 core

in vec2  v_local;
in float v_life;
in float v_kind;
in vec4  v_color_a;
in vec4  v_color_b;
in float v_seed;
in float v_time;

out vec4 fragColor;

// ---- ruído Perlin + fbm (mesma implementação do vfx_common.glsl) ------------
vec2 grad(vec2 p) {
    float a = dot(p, vec2(127.1, 311.7));
    float s = sin(a) * 43758.5453123;
    return vec2(cos(s), sin(s)) * 6.2831853;
}
float perlin(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float n00 = dot(grad(i), f);
    float n10 = dot(grad(i + vec2(1, 0)), f - vec2(1, 0));
    float n01 = dot(grad(i + vec2(0, 1)), f - vec2(0, 1));
    float n11 = dot(grad(i + vec2(1, 1)), f - vec2(1, 1));
    return mix(mix(n00, n10, u.x), mix(n01, n11, u.x), u.y);
}
float fbm(vec2 p, float t) {
    float amp = 0.5, sum = 0.0;
    for (int i = 0; i < 4; ++i) {
        mat2 rot = mat2(0.80, 0.60, -0.60, 0.80);
        p = rot * p * 2.02 + vec2(13.5 + t * 0.9, 9.2 - t * 0.6);
        sum += amp * perlin(p);
        amp *= 0.5;
    }
    return sum;
}

// ---- helpers de shape --------------------------------------------------------
float sd_circle(vec2 p)  { return length(p) - 1.0; }
float sd_box(vec2 p, vec2 b) { vec2 d = abs(p) - b; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
// segmento (para raios/lasca/folha): p local, a->b no espaço unitário
float sd_seg(vec2 p, vec2 a, vec2 b, float r) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

void main() {
    vec2 p = v_local;
    float life = clamp(v_life, 0.0, 1.0);
    float d;          // distância assinada do shape (negativo = dentro)
    float glow = 0.0; // energia extra >1.0 p/ alimentar o bloom
    float alpha = 1.0;

    int kind = int(v_kind + 0.5);

    if (kind == 0) {                       // SPARK: lasca alongada quente
        d = sd_seg(p, vec2(-0.9, 0.0), vec2(0.9, 0.0), 0.12);
        glow = exp(-max(d, 0.0) * 6.0) * 2.2;
    } else if (kind == 1)                  // EMBER/FIRE: brasa com fbm de fogo
        || (kind == 2)                     // LAVA: idem, mais densa
    {
        float n = fbm(p * 2.4 + v_seed, v_time * 1.6 + v_seed);
        float disc = length(p) - (1.0 - 0.25 * smoothstep(0.0, 1.0, life));
        d = disc - 0.35 * n;
        glow = smoothstep(0.15, -0.45, d) * (kind == 2 ? 2.6 : 1.8);
        // língua de fogo: estica a cauda para cima conforme envelhece
        float flame = exp(-abs(p.x) * 4.0) * smoothstep(-1.0, 1.0, -p.y);
        glow += flame * (kind == 2 ? 1.4 : 0.9) * (1.0 - life);
    } else if (kind == 3) {                // WATER: gota com refração fake
        d = sd_circle(p) ;
        float rim = smoothstep(-0.05, 0.25, d);           // borda iluminada
        float ripple = 0.12 * sin(length(p) * 18.0 - v_time * 9.0 + v_seed);
        d += ripple;
        glow = rim * 1.1 + smoothstep(0.2, -0.4, d) * 0.7;
    } else if (kind == 4) {                // LEAF/PLANTA: elipse com nervura
        vec2 q = vec2(p.x * 1.7, p.y * 1.0);
        d = sd_circle(q) ;
        float vein = exp(-abs(p.x * 3.0) * 8.0) * step(abs(p.y), 0.9);
        glow = vein * 0.8;
    } else if (kind == 5) {                // METAL: losango/estilhaço brilhante
        d = sd_box(vec2(p.x * 0.707 + p.y * 0.707,
                        -p.x * 0.707 + p.y * 0.707), vec2(0.75, 0.22));
        float sheen = exp(-abs(p.y * 2.2 - p.x * 0.6) * 5.0);
        glow = sheen * 1.9;
    } else if (kind == 6) {                // ROCK/DEBRIS: bloco irregular
        float n = perlin(p * 3.0 + v_seed) * 0.25;
        d = sd_box(p, vec2(0.8, 0.6)) + n;
        glow = 0.0;
    } else if (kind == 7) {                // ELECTRIC: zigue-zague de raio
        float zig = 0.30 * sin(p.y * 14.0 + v_time * 30.0 + v_seed * 6.28);
        d = abs(p.x - zig) - 0.09;
        d = max(d, abs(p.y) - 1.0);
        glow = exp(-max(abs(p.x - zig), 0.0) * 9.0) * 3.0;
    } else if (kind == 8) {                // LIGHT: estrela de 4 pontas
        float ray = exp(-abs(p.x) * 7.0) + exp(-abs(p.y) * 7.0);
        d = length(p) - 0.35;
        glow = ray * 1.6 + smoothstep(0.1, -0.3, d) * 2.4;
    } else if (kind == 9) {                // SHADOW: mancha que corrói a luz
        float n = fbm(p * 2.0, v_time * 0.7 + v_seed);
        d = length(p) - (0.9 + 0.2 * n);
        glow = 0.0;                          // Trevas não emitem bloom
        alpha = smoothstep(0.2, -0.4, d);
    } else if (kind == 10) {               // SMOKE: nuvem volumétrica fake
        float n = fbm(p * 1.6 + v_seed, v_time * 0.35);
        d = length(p) - 1.0;
        alpha = smoothstep(0.15, -0.85, d + 0.55 * n) * 0.55;
        glow = 0.0;
    } else if (kind == 11) {               // SHOCK RING: anel de impacto
        float r = length(p);
        float w = 0.10 + 0.25 * life;
        d = abs(r - 0.85) - w;
        glow = exp(-max(d, 0.0) * 10.0) * 2.8;
        alpha = smoothstep(0.0, 0.35, 1.0 - life);
    } else if (kind == 12) {               // GROUND CRACK: linha ramificada
        float jag = 0.22 * perlin(vec2(p.x * 4.0, v_seed * 9.0));
        d = abs(p.y - jag) - 0.05;
        d = max(d, abs(p.x) - 1.0);
        glow = exp(-max(d, 0.0) * 14.0) * 2.0;   // energia saindo da fissura
    } else if (kind == 13) {               // HEAL: cruz ascendente suave
        d = min(sd_box(p, vec2(0.28, 0.85)), sd_box(p, vec2(0.85, 0.28)));
        glow = exp(-max(d, 0.0) * 5.0) * 1.6;
    } else if (kind == 14) {               // SHIELD HEX: malha geométrica
        vec2 a = abs(p);
        float hex = max(dot(a, normalize(vec2(1.0, 1.73))), a.x);
        d = hex - 0.9;
        float edge = smoothstep(-0.12, 0.0, d);   // só a moldura
        glow = edge * 1.5;
        alpha = edge * 0.9 + smoothstep(0.0, -0.9, d) * 0.12; // face translúcida
    } else {                               // ORB padrão
        d = length(p) - 1.0;
        glow = exp(-max(d, 0.0) * 4.0) * 1.5;
    }

    // curva de vida: cor interpola A -> B; fade-out suave nos dois extremos
    vec4 col = mix(v_color_a, v_color_b, smoothstep(0.0, 1.0, life));
    float body = smoothstep(0.08, -0.08, d);            // interior do shape
    float halo = exp(-max(d, 0.0) * 5.0);               // brilho externo macio
    float appear = smoothstep(0.0, 0.08, life);         // pop-in rápido
    float fade   = 1.0 - smoothstep(0.55, 1.0, life);   // fade-out suave
    float a = clamp((body + halo * 0.6) * alpha, 0.0, 1.0) * col.a * appear * fade;

    vec3 emission = col.rgb * (1.0 + glow * col.a);     // HDR p/ bloom
    fragColor = vec4(emission * a, a);                  // pré-multiplicado
    if (fragColor.a < 0.003) discard;
}
