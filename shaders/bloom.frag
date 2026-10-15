// ============================================================================
// bloom.frag — extração de brilho (threshold) + blur gaussiano separável.
// O mesmo shader serve para H e V; u_dir escolhe o eixo. Também é usado na
// segunda passada (downsample/blur forte) do ping-pong de 3 níveis.
// ============================================================================
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D u_tex;
uniform vec2  u_texel;     // 1/tamanho do buffer atual
uniform vec2  u_dir;       // (1,0) horizontal | (0,1) vertical
uniform float u_threshold; // corte de luminância (extração) ou 0 (só blur)
uniform float u_radius;    // raio do kernel em texels

void main() {
    vec3 c = texture(u_tex, v_uv).rgb;
    if (u_threshold > 0.0) {
        // soft-knee: evita bordas duras no threshold
        float l = max(c.r, max(c.g, c.b));
        float k = clamp((l - u_threshold) / max(u_threshold, 1e-4), 0.0, 1.0);
        c *= k * k;
    }
    // gaussian 9-tap normalizado (pesos somam 1.0)
    vec3 sum = c * 0.227027;
    for (int i = 1; i <= 4; ++i) {
        float w = (i == 1) ? 0.1945946 : (i == 2) ? 0.12162162 : (i == 3) ? 0.054054054 : 0.016216216;
        vec2 o = u_dir * u_texel * (float(i) * u_radius);
        sum += texture(u_tex, v_uv + o).rgb * w;
        sum += texture(u_tex, v_uv - o).rgb * w;
    }
    fragColor = vec4(sum, 1.0);
}
