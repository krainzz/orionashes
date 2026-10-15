#version 330 core
uniform sampler2D u_card;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec3 u_rarity_color;
uniform vec4 u_name_bar_uv;

in vec2 v_uv;
out vec4 fragColor;

float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

void main() {
    vec4 base = texture(u_card, v_uv);

    vec2 bar_min = u_name_bar_uv.xy * u_resolution;
    vec2 bar_max = u_name_bar_uv.zw * u_resolution;
    vec2 bar_center = 0.5 * (bar_min + bar_max);
    vec2 bar_half = 0.5 * max(vec2(2.0), bar_max - bar_min);
    vec2 p_px = v_uv * u_resolution;

    float dist_px = sdBox(p_px - bar_center, bar_half);
    float pulse = 0.82 + 0.18 * sin(u_time * 3.6);

    float border_tube = exp(-abs(dist_px) * 0.65) * 0.72 * pulse;
    float outer_halo = exp(-max(0.0, dist_px) * 0.16) * 0.42 * pulse;
    float inner_sheen = (dist_px < 0.0) ? exp(dist_px * 0.25) * 0.20 * pulse : 0.0;

    float edge_dist = min(min(p_px.x, u_resolution.x - p_px.x), min(p_px.y, u_resolution.y - p_px.y));
    float frame_glow = exp(-edge_dist * 0.32) * 0.22 * pulse;

    vec3 neon = u_rarity_color * (border_tube + outer_halo + inner_sheen + frame_glow);
    vec3 final_rgb = clamp(base.rgb + neon * max(base.a, 0.65), 0.0, 1.0);
    float final_alpha = clamp(base.a + (border_tube + outer_halo) * 0.45, 0.0, 1.0);

    fragColor = vec4(final_rgb, final_alpha);
}
