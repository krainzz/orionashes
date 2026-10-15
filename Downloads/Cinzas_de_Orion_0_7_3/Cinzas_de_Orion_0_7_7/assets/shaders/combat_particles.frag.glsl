#version 330 core
in vec2 v_local;
in vec4 v_color;
in float v_alpha;
out vec4 fragColor;
void main() {
    float r = length(v_local);
    if (r > 1.0 || v_alpha <= 0.001) discard;
    float core = 1.0 - smoothstep(0.08, 0.72, r);
    float glow = exp(-r * r * 4.4) * 0.52;
    float alpha = clamp((core * 0.75 + glow) * v_alpha, 0.0, 1.0);
    vec3 rgb = mix(v_color.rgb, vec3(1.0), core * 0.72);
    fragColor = vec4(rgb, alpha);
}
