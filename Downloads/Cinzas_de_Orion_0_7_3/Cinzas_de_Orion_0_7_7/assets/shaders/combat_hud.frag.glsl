#version 330 core
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_hud;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_curvature;
uniform float u_glow;

vec4 sampleHud(vec2 uv) {
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) return vec4(0.0);
    return texture(u_hud, uv);
}
float emission(vec4 c) {
    float lum = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722));
    // Dark panel fills are not emissive; bright cyan/gold strokes and text are.
    return smoothstep(0.22, 0.72, lum) * c.a;
}
void main() {
    vec2 centered = (v_uv - 0.5) * 2.0;
    float aspect = u_resolution.x / max(u_resolution.y, 1.0);
    vec2 lens = centered * vec2(aspect, 1.0);
    float r2 = dot(lens, lens);
    lens *= 1.0 + u_curvature * r2;
    vec2 warpedUV = lens / vec2(aspect, 1.0) * 0.5 + 0.5;

    vec4 base = sampleHud(warpedUV);
    vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec3 glowRGB = vec3(0.0);
    float glowAlpha = 0.0;
    const vec2 offsets[8] = vec2[8](
        vec2( 1.0, 0.0), vec2(-1.0, 0.0), vec2(0.0, 1.0), vec2(0.0,-1.0),
        vec2( 1.0, 1.0), vec2(-1.0, 1.0), vec2(1.0,-1.0), vec2(-1.0,-1.0)
    );
    for (int i = 0; i < 8; ++i) {
        vec4 neighbor = sampleHud(warpedUV + offsets[i] * px * 2.25);
        float e = emission(neighbor);
        glowRGB = max(glowRGB, neighbor.rgb * e);
        glowAlpha = max(glowAlpha, e);
    }
    float breathing = 0.94 + 0.06 * sin(u_time * 3.5);
    vec3 rgb = clamp(base.rgb + glowRGB * u_glow * 0.42 * breathing, 0.0, 1.0);
    float alpha = clamp(base.a + glowAlpha * u_glow * 0.17 * breathing, 0.0, 1.0);
    // Alpha remains independent of scene color: only the HUD layer is warped.
    fragColor = vec4(rgb, alpha);
}
