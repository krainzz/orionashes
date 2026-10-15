#version 330 core
uniform sampler2D u_sprite;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_crystal_uv;
uniform vec3 u_glow_color;
uniform int direction;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 base = texture(u_sprite, v_uv);

    if (direction == 1) {
        fragColor = base;
        return;
    }

    vec2 aspect = vec2(u_resolution.x / max(1.0, u_resolution.y), 1.0);
    vec2 delta = (v_uv - u_crystal_uv) * aspect;
    float diamond_dist = abs(delta.x) * 1.15 + abs(delta.y) * 0.95;

    float pulse = 0.5 + 0.5 * sin(u_time * 3.1);
    float core_mask = smoothstep(0.065, 0.012, diamond_dist);
    float halo_mask = exp(-diamond_dist * 22.0) * (0.18 + 0.15 * pulse);

    float is_cyan = step(0.55, base.g) * step(0.60, base.b) * (1.0 - step(0.55, base.r)) * base.a;
    float crystal_boost = is_cyan * (0.20 + 0.24 * pulse);

    vec3 emissive = u_glow_color * (core_mask * (0.22 + 0.18 * pulse) + halo_mask + crystal_boost);
    vec3 out_rgb = clamp(base.rgb + emissive * max(base.a, 0.35), 0.0, 1.0);
    float out_alpha = clamp(base.a + halo_mask * 0.32, 0.0, 1.0);
    fragColor = vec4(out_rgb, out_alpha);
}
