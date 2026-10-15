#version 330 core
uniform sampler2D u_scene;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_tank_uv;
uniform vec2 u_status_uv;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 base = texture(u_scene, v_uv);
    vec2 aspect = vec2(u_resolution.x / max(1.0, u_resolution.y), 1.0);

    float pulse = 0.5 + 0.5 * sin(u_time * 2.8);
    vec2 d_tank = (v_uv - u_tank_uv) * aspect;
    float dist_tank = length(d_tank);
    float tank_halo = exp(-dist_tank * 9.5) * (0.22 + 0.12 * pulse);
    vec3 tank_col = vec3(0.10, 1.00, 0.72) * tank_halo;

    vec2 d_status = (v_uv - u_status_uv) * aspect;
    float dist_status = length(d_status);
    float status_halo = exp(-dist_status * 11.0) * (0.14 + 0.06 * sin(u_time * 4.2));
    vec3 status_col = vec3(0.18, 0.88, 1.00) * status_halo;

    vec2 texel = 1.0 / u_resolution;
    vec3 bloom = vec3(0.0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            vec3 s = texture(u_scene, v_uv + vec2(float(x), float(y)) * texel * 2.0).rgb;
            float bright = max(s.g, s.b) * step(0.65, max(s.g, s.b));
            bloom += s * bright;
        }
    }
    bloom /= 9.0;

    vec3 final_rgb = clamp(base.rgb + tank_col + status_col + bloom * 0.18, 0.0, 1.0);
    fragColor = vec4(final_rgb, 1.0);
}
